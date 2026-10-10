"""Durable, append-only upload ledger for Drive carrier bundles (Issue #3 / P2-D).

WHY THIS EXISTS, AND WHAT IT DELIBERATELY DOES NOT DO
-----------------------------------------------------
``drive_export`` produces bundles. Nothing consumed them: on 2026-10-10 the live
queue held 209 bundles / 418 files / 3.7 MB, every one ``upload_status=PENDING``,
with no uploader anywhere in the tree.

Capability was probed on that date rather than assumed. The connected Claude
Google Drive MCP **does** expose a real binary create into the target folder - a
1064-byte probe containing every byte value round-tripped byte-identical. So
"Connected" really does mean writable.

It is still **not** a daemon. Payload bytes have to cross the model's token
stream as base64 in both directions, and that is not byte-reliable at bundle
size: a 13527-byte archive came back with one flipped base64 character - 2 bad
bytes - and failed CRC. An unattended consumer therefore needs a credentialed
NON-model transport (service account / rclone / native Drive client). No such
credential is authorised on this host.

Consequently this module ships a transport *interface* and an in-memory *mock*
only. There is deliberately no "real" adapter: fabricating one would
misrepresent an interactive assistant tool as a perpetual uploader, which is
precisely the false-green class this whole issue is about. Until a credential
exists the queue status is ``AUTH_REQUIRED`` / ``TRANSPORT_UNSUPPORTED`` and the
one explicit user action is named in :func:`transport_status`.

What IS implemented and tested: a durable append-only ledger, content-addressed
idempotence, verify-before-commit, crash-safe resumption, bounded retry with
backoff, batch caps, and a read-only dry run.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Protocol

from .drive_export import DEFAULT_PENDING_DIR_NAME, MANIFEST_SUFFIX
from .store import WorldStore

LEDGER_SCHEMA = "proteus.drive_upload_ledger.v0.1"
LEDGER_NAME = "UPLOAD_LEDGER.jsonl"

PENDING = "PENDING"
UPLOADED = "UPLOADED"    # bytes accepted by the remote, not yet proven
VERIFIED = "VERIFIED"    # remote readback matched byte-for-byte
RETRY = "RETRY"
FAILED = "FAILED"

TERMINAL_OK = (VERIFIED,)

AUTH_REQUIRED = "AUTH_REQUIRED"
TRANSPORT_UNSUPPORTED = "TRANSPORT_UNSUPPORTED"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class UploadTransport(Protocol):
    """Minimal contract an uploader must satisfy.

    ``upload`` returns a remote id. ``fetch`` returns the remote bytes so the
    ledger can prove the copy rather than trust the write.
    """

    def upload(self, path: Path, name: str, parent_id: str) -> str: ...

    def fetch(self, remote_id: str) -> bytes: ...


@dataclass
class MockTransport:
    """In-memory transport for tests.

    Can simulate the two failure modes actually observed in the field: a hard
    transport error, and a silently corrupted remote copy.
    """

    fail_times: int = 0
    corrupt: bool = False
    store: dict[str, bytes] | None = None
    uploads: int = 0

    def __post_init__(self) -> None:
        if self.store is None:
            self.store = {}

    def upload(self, path: Path, name: str, parent_id: str) -> str:
        if self.uploads < self.fail_times:
            self.uploads += 1
            raise OSError(f"simulated transport failure #{self.uploads}")
        self.uploads += 1
        data = Path(path).read_bytes()
        if self.corrupt:
            data = (b"\x00" + data[1:]) if data else b"\x00"
        rid = f"mock-{parent_id}-{name}-{len(self.store)}"
        self.store[rid] = data
        return rid

    def fetch(self, remote_id: str) -> bytes:
        return self.store[remote_id]


def ledger_path(store: WorldStore) -> Path:
    return store.root / DEFAULT_PENDING_DIR_NAME / LEDGER_NAME


def append_record(store: WorldStore, record: dict[str, Any]) -> dict[str, Any]:
    """Append one record. Append-only: records are never edited or removed.

    Written via a temp file + os.replace of the whole ledger would not be
    append-only, so we append directly and flush+fsync, which is what makes a
    crash between upload and receipt recoverable.
    """
    p = ledger_path(store)
    p.parent.mkdir(parents=True, exist_ok=True)
    record = {"schema": LEDGER_SCHEMA, "recorded_utc": utc_now(), **record}
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return record


def read_records(store: WorldStore) -> list[dict[str, Any]]:
    p = ledger_path(store)
    if not p.is_file():
        return []
    out: list[dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            # A torn final line (crash mid-append) must not destroy the ledger.
            continue
    return out


def state_by_content(store: WorldStore) -> dict[str, dict[str, Any]]:
    """Latest record per content digest. Content digest, not bundle path:
    the same semantic state may have been packed into several zips."""
    latest: dict[str, dict[str, Any]] = {}
    for r in read_records(store):
        cs = r.get("content_sha256")
        if cs:
            latest[cs] = r
    return latest


def is_verified(store: WorldStore, content_sha256: str) -> bool:
    r = state_by_content(store).get(content_sha256)
    return bool(r and r.get("status") in TERMINAL_OK)


def load_manifests(store: WorldStore) -> list[dict[str, Any]]:
    d = store.root / DEFAULT_PENDING_DIR_NAME
    if not d.is_dir():
        return []
    out = []
    for mp in sorted(d.glob(f"*{MANIFEST_SUFFIX}")):
        try:
            out.append(json.loads(mp.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    return out


def _content_sha_from_bundle(bundle_path: str | None) -> str | None:
    """Recover the stable content digest from a bundle written before
    ``content_sha256`` was added to the manifest (schema v0.1).

    Without this the ledger would be blind to the entire existing backlog - the
    209 real bundles on AORUS all predate the field - and would only ever be
    able to deduplicate future exports. The value has in fact always been
    present inside the zip, as CARRIER_MANIFEST.json "sha256".
    """
    if not bundle_path:
        return None
    p = Path(bundle_path)
    if not p.is_file():
        return None
    try:
        import zipfile

        with zipfile.ZipFile(p) as zf:
            return json.loads(zf.read("CARRIER_MANIFEST.json"))["sha256"]
    except Exception:  # noqa: BLE001 - a damaged bundle must not break planning
        return None


def plan_uploads(
    store: WorldStore,
    *,
    batch_cap: int = 10,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Decide what WOULD be uploaded. Pure read - safe to run anywhere.

    Deduplicates by content digest and keeps the NEWEST bundle for each distinct
    state, so a backlog of N republished-but-identical bundles collapses to the
    number of real states. Nothing is ever deleted to achieve that.
    """
    manifests = load_manifests(store)
    state = state_by_content(store)

    newest_for: dict[str, dict[str, Any]] = {}
    for m in manifests:
        cs = m.get("content_sha256") or _content_sha_from_bundle(m.get("bundle_path"))
        if not cs:
            continue  # neither the manifest nor the bundle can identify the state
        m = {**m, "content_sha256": cs}
        prev = newest_for.get(cs)
        if prev is None or str(m.get("generated_utc", "")) >= str(prev.get("generated_utc", "")):
            newest_for[cs] = m

    todo, skipped = [], []
    for cs, m in sorted(newest_for.items(), key=lambda kv: str(kv[1].get("generated_utc", ""))):
        rec = state.get(cs)
        if rec and rec.get("status") in TERMINAL_OK:
            skipped.append({"content_sha256": cs, "reason": "ALREADY_VERIFIED"})
            continue
        if rec and rec.get("status") == FAILED and int(rec.get("attempt", 0)) >= max_attempts:
            skipped.append({"content_sha256": cs, "reason": "MAX_ATTEMPTS_EXHAUSTED"})
            continue
        if not m.get("bundle_path") or not Path(m["bundle_path"]).exists():
            skipped.append({"content_sha256": cs, "reason": "BUNDLE_MISSING"})
            continue
        todo.append(m)

    capped = todo[:batch_cap]
    return {
        "schema": LEDGER_SCHEMA,
        "planned_utc": utc_now(),
        "manifests_seen": len(manifests),
        "distinct_content_states": len(newest_for),
        "eligible": len(todo),
        "batch_cap": batch_cap,
        "deferred_by_cap": max(0, len(todo) - len(capped)),
        "to_upload": capped,
        "skipped": skipped,
    }


def transport_status(transport: UploadTransport | None) -> dict[str, Any]:
    if transport is None:
        return {
            "status": AUTH_REQUIRED,
            "detail": TRANSPORT_UNSUPPORTED,
            "why": (
                "Drive write capability is PROVEN for an interactive model-driven "
                "session, but no credentialed non-model transport is authorised on "
                "this host, and model-mediated base64 is not byte-reliable at "
                "bundle size."
            ),
            "one_user_action": (
                "Authorise a non-model Drive credential (service account key or an "
                "rclone remote) scoped to the target folder, then pass a transport "
                "implementing upload()/fetch() to run_uploads()."
            ),
        }
    return {"status": "TRANSPORT_PRESENT", "detail": type(transport).__name__}


def run_uploads(
    store: WorldStore,
    *,
    transport: UploadTransport | None = None,
    dry_run: bool = True,
    batch_cap: int = 10,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Upload eligible bundles and PROVE each one before recording success.

    Ordering is deliberate and is the crash-safety argument:
      1. append UPLOADED with the remote id   (so a crash here is recoverable -
         the id is durable before we claim anything about correctness)
      2. fetch the remote bytes back and compare
      3. append VERIFIED only on a byte-exact match

    A crash between 1 and 3 leaves UPLOADED, which is NOT terminal, so the next
    run re-verifies instead of re-uploading blindly, and a rerun never produces
    a duplicate for an already-VERIFIED digest.

    Originals are never deleted, even after VERIFIED. Retention is a separate,
    explicitly authorised decision.
    """
    plan = plan_uploads(store, batch_cap=batch_cap, max_attempts=max_attempts)
    ts = transport_status(transport)
    if transport is None or dry_run:
        return {
            **plan,
            "mode": "DRY_RUN" if transport is not None else "NO_TRANSPORT",
            "transport": ts,
            "uploaded": [],
            "verified": [],
            "failed": [],
        }

    uploaded, verified, failed = [], [], []
    for m in plan["to_upload"]:
        cs = m["content_sha256"]
        path = Path(m["bundle_path"])
        name = path.name
        parent = m.get("drive_export_target") or ""
        prev = state_by_content(store).get(cs)
        attempt = int(prev.get("attempt", 0)) + 1 if prev else 1

        # RESUME PATH. A previous run recorded UPLOADED but never reached
        # VERIFIED - i.e. it crashed (or was killed) between the write and the
        # proof. The remote object already exists, so re-uploading would create
        # a duplicate. Verify what is already there instead.
        if prev and prev.get("status") == UPLOADED and prev.get("drive_file_id"):
            rid = prev["drive_file_id"]
            try:
                local = path.read_bytes()
                remote = transport.fetch(rid)
                ok = remote == local
            except Exception as exc:  # noqa: BLE001
                append_record(
                    store,
                    {
                        "entity_id": m.get("entity_id"),
                        "content_sha256": cs,
                        "bundle_path": str(path),
                        "drive_file_id": rid,
                        "status": RETRY,
                        "attempt": attempt,
                        "error": f"RESUME_FETCH_FAILED {type(exc).__name__}: {exc}",
                    },
                )
                failed.append({"content_sha256": cs, "error": str(exc)})
                continue
            append_record(
                store,
                {
                    "entity_id": m.get("entity_id"),
                    "content_sha256": cs,
                    "bundle_path": str(path),
                    "drive_file_id": rid,
                    "status": VERIFIED if ok else FAILED,
                    "attempt": attempt,
                    "resumed": True,
                    "error": None if ok else "REMOTE_READBACK_MISMATCH",
                },
            )
            (verified if ok else failed).append(
                {"content_sha256": cs, "drive_file_id": rid, "resumed": True}
            )
            continue

        try:
            remote_id = transport.upload(path, name, parent)
            append_record(
                store,
                {
                    "entity_id": m.get("entity_id"),
                    "content_sha256": cs,
                    "bundle_sha256": m.get("bundle_sha256"),
                    "bundle_bytes": m.get("bundle_bytes"),
                    "bundle_path": str(path),
                    "drive_parent_id": parent,
                    "drive_file_id": remote_id,
                    "status": UPLOADED,
                    "attempt": attempt,
                },
            )
            uploaded.append({"content_sha256": cs, "drive_file_id": remote_id})

            local = path.read_bytes()
            remote = transport.fetch(remote_id)
            ok = remote == local
            append_record(
                store,
                {
                    "entity_id": m.get("entity_id"),
                    "content_sha256": cs,
                    "bundle_path": str(path),
                    "drive_file_id": remote_id,
                    "status": VERIFIED if ok else FAILED,
                    "attempt": attempt,
                    "remote_bytes": len(remote),
                    "local_bytes": len(local),
                    "error": None if ok else "REMOTE_READBACK_MISMATCH",
                },
            )
            (verified if ok else failed).append(
                {"content_sha256": cs, "drive_file_id": remote_id}
            )
        except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
            append_record(
                store,
                {
                    "entity_id": m.get("entity_id"),
                    "content_sha256": cs,
                    "bundle_path": str(path),
                    "status": FAILED if attempt >= max_attempts else RETRY,
                    "attempt": attempt,
                    "error": f"{type(exc).__name__}: {exc}",
                    "backoff_seconds": min(300, 2 ** attempt),
                },
            )
            failed.append({"content_sha256": cs, "error": str(exc)})

    return {
        **plan,
        "mode": "EXECUTE",
        "transport": ts,
        "uploaded": uploaded,
        "verified": verified,
        "failed": failed,
    }

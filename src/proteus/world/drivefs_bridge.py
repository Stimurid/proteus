r"""Unattended DriveFS delivery adapter for Proteus carrier bundles.

WHAT CHANGED, AND WHY THIS MODULE CAN EXIST AT ALL
--------------------------------------------------
``drive_upload_ledger`` shipped with no real transport on purpose: the only
Drive write path then available was an interactive model-mediated tool whose
base64 round trip corrupted a 13.5 KB archive (one flipped character, 2 bad
bytes, CRC failure). Presenting that as a daemon would have been a false green.

That constraint is gone. AORUS runs Google Drive for Desktop as the logged-in
user, mounting the SAME Drive corpus at ``G:\``. Bytes written there are plain
filesystem bytes - no token stream, no base64 - and on 2026-10-10 a 17864-byte
real Proteus carrier staged through ``G:`` was downloaded back out of the cloud
through an independent provider path with a byte-identical sha256 and a clean
ZIP CRC (``REAL_CARRIER_CLOUD_VERIFY.json``). So DriveFS is a genuine transport
and needs no new OAuth, no service account and no token handling.

THE ONE THING THIS MODULE REFUSES TO CONFLATE
---------------------------------------------
Copying a file into ``G:\`` and reading it back proves only that the local
DriveFS cache accepted it. It does NOT prove the bytes reached Google. Those are
two different facts and they get two different statuses:

``STAGED_LOCAL``
    Written into the DriveFS target and read back byte-identical *from G:*.
``CLOUD_PRESENT``
    The provider, asked through a path that is not this host's mount, reports
    an object with the expected name, parent folder and exact byte length.
    This proves the upload left the machine. It does NOT prove byte identity:
    the Drive connector available here exposes no checksum field, and its
    binary download path is the base64 route that previously returned a 13527
    byte archive with 2 corrupted bytes.
``CLOUD_VERIFIED``
    An independent provider-side readback returned the same sha256 and byte
    length. Strictly stronger than ``CLOUD_PRESENT``.

Only an imported cloud receipt can produce ``CLOUD_VERIFIED``. There is no code
path in which a local copy, or a presence observation, promotes itself.
:func:`cloud_verify_queue` publishes the exact handshake record a cloud verifier
needs, and :func:`import_cloud_receipt` is the only door back in - a
``CLOUD_PRESENT`` record leaves the item on that queue.

SAFETY INVARIANTS
-----------------
* The target is validated by *content markers*, not just by path. A ``G:`` that
  is some other Drive account, or a path that exists but is the wrong folder,
  is rejected rather than written to.
* Destination filenames are content-addressed and deterministic, so the same
  payload always maps to the same name and a rerun is a no-op.
* A destination that already exists is compared, never overwritten. If the name
  matches but the bytes differ, that is a hard failure, not a replace.
* Staging is temp-write + ``os.rename`` **inside the same target directory**.
  On Windows ``os.rename`` fails when the destination exists, which is exactly
  the non-clobbering semantics wanted here.
* Zero-length and CRC-broken bundles are refused before they are copied.
* Nothing is ever deleted from the corpus. Originals in the pending queue are
  never removed; historical manifests are never rewritten.
* The ledger lives OUTSIDE the world git repo (``~/.aiye/drivefs_bridge``) so
  delivery bookkeeping can never masquerade as world substrate.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import socket
import subprocess
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from ..paths import aiye_home
from .drive_upload_ledger import (
    _content_sha_from_bundle,
    load_manifests,
)
from .store import WorldStore

BRIDGE_SCHEMA = "proteus.drivefs_bridge.v0.1"
RECEIPT_SCHEMA = "proteus.drivefs_cloud_verification.v0.1"
PRESENCE_SCHEMA = "proteus.drivefs_cloud_presence.v0.1"
STAGE_RECEIPT_SCHEMA = "proteus.drivefs_stage_receipt.v0.1"

LEDGER_NAME = "DRIVEFS_LEDGER.jsonl"
QUEUE_NAME = "CLOUD_VERIFY_QUEUE.jsonl"
SUMMARY_NAME = "DRIVEFS_SUMMARY.md"
LOCK_NAME = "drivefs_bridge.lock"

# --- delivery statuses -------------------------------------------------------
STAGED_LOCAL = "STAGED_LOCAL"          # on G:, read back from G: - NOT a cloud proof
CLOUD_PRESENT = "CLOUD_PRESENT"        # provider sees name+parent+length - NOT byte identity
CLOUD_VERIFIED = "CLOUD_VERIFIED"      # independent provider readback matched sha256
SKIPPED_IDENTICAL = "SKIPPED_IDENTICAL"
STAGE_RETRY = "STAGE_RETRY"
STAGE_FAILED = "STAGE_FAILED"
FOREIGN_UNVERIFIED = "FOREIGN_UNVERIFIED"  # pre-existing artifact we did not stage

TERMINAL_DELIVERED = (STAGED_LOCAL, SKIPPED_IDENTICAL, CLOUD_PRESENT, CLOUD_VERIFIED)

# Evidence strength. A later, weaker observation must never overwrite a stronger
# one: a routine STAGED_LOCAL re-record cannot un-verify something the cloud has
# already confirmed.
STATUS_RANK = {
    STAGE_FAILED: 0,
    STAGE_RETRY: 0,
    SKIPPED_IDENTICAL: 1,
    STAGED_LOCAL: 1,
    CLOUD_PRESENT: 2,
    CLOUD_VERIFIED: 3,
}

# --- target verdicts ---------------------------------------------------------
TARGET_OK = "TARGET_OK"
DRIVEFS_UNAVAILABLE = "DRIVEFS_UNAVAILABLE"
TARGET_MISSING = "TARGET_MISSING"
MARKER_MISSING = "MARKER_MISSING"

# --- per-item failure reasons ------------------------------------------------
BUNDLE_MISSING = "BUNDLE_MISSING"
BUNDLE_EMPTY = "BUNDLE_EMPTY"
LOCAL_DIGEST_MISMATCH = "LOCAL_DIGEST_MISMATCH"
MANIFEST_TARGET_MISMATCH = "MANIFEST_TARGET_MISMATCH"
ZIP_CORRUPT = "ZIP_CORRUPT"
NAME_COLLISION_DIFFERENT_PAYLOAD = "NAME_COLLISION_DIFFERENT_PAYLOAD"
READBACK_MISMATCH = "READBACK_MISMATCH"
COPY_FAILED = "COPY_FAILED"

# Markers that identify THIS folder (AORUS/results) and no other. Chosen because
# they are long-lived, distinctively named, and were not created by this tool.
DEFAULT_MARKERS = (
    "AORUS_00_ENTRYPOINT_v03.md",
    "AIYE_DOT_MOUNT_RECEIPT_aiye.dot.20261004T004605Z.json",
    "BOOTSTRAP_MANIFEST_v03.md",
    "ARCHIVARIUS_MVP_v03.md",
)

TEMP_PREFIX = ".proteus-drivefs-tmp-"
# Deterministic destination name. Name identity implies byte identity: the name
# carries the bundle digest, so two files that share a name share their bytes.
NAME_RE = re.compile(r"^proteus-carrier\.(?P<entity>.+)\.c(?P<c>[0-9a-f]{16})\.b(?P<b>[0-9a-f]{16})\.zip$")

CHUNK = 1 << 20


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: str | os.PathLike[str]) -> tuple[str, int]:
    """Streaming digest. Returns (hexdigest, byte_count)."""
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as fh:
        while True:
            b = fh.read(CHUNK)
            if not b:
                break
            h.update(b)
            n += len(b)
    return h.hexdigest(), n


# ---------------------------------------------------------------------------
# Target
# ---------------------------------------------------------------------------


def _drivefs_process_running() -> bool:
    """True when GoogleDriveFS.exe is alive.

    ``G:`` only exists while the client runs, so a mount check alone could in
    principle pass against a stale or unrelated letter. This is a cheap second
    opinion, not a credential read - nothing about the client's tokens, profile
    or config is touched.
    """
    if os.name != "nt":
        return False
    try:
        # BYTES, not text. tasklist writes in the console OEM codepage (cp866 on
        # a Russian Windows), and text=True decodes as UTF-8 inside a reader
        # thread, where the UnicodeDecodeError is swallowed and stdout silently
        # comes back as None. The image name is ASCII, so matching raw bytes is
        # both correct and codepage-independent.
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq GoogleDriveFS.exe", "/NH"],
            capture_output=True,
            timeout=20,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return b"GoogleDriveFS.exe" in (out or b"")


@dataclass(frozen=True)
class DriveFsTarget:
    """A validated destination inside the DriveFS mount.

    ``folder_id`` is the Google Drive id of ``target_dir``. It cannot be read
    off the filesystem, so it is declared here and cross-checked against each
    manifest's ``drive_export_target``; the *marker* check is what actually
    proves we are standing in the right folder.
    """

    drivefs_root: Path
    target_dir: Path
    folder_id: str
    markers: tuple[str, ...] = DEFAULT_MARKERS
    min_markers: int = 2

    @staticmethod
    def from_config(path: str | os.PathLike[str]) -> "DriveFsTarget":
        cfg = json.loads(Path(path).read_text(encoding="utf-8"))
        return DriveFsTarget(
            drivefs_root=Path(cfg["drivefs_root"]),
            target_dir=Path(cfg["target_dir"]),
            folder_id=cfg["target_folder_id"],
            markers=tuple(cfg.get("markers") or DEFAULT_MARKERS),
            min_markers=int(cfg.get("min_markers", 2)),
        )


def validate_target(
    target: DriveFsTarget,
    *,
    process_probe: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    """Prove the destination is the intended folder before writing anything.

    Deliberately read-only. An earlier draft probed writability by creating and
    deleting a scratch file; that is wrong here, because a create+delete inside
    a synced Drive folder produces a real cloud object and then a real trashed
    object on every run. Write capability is instead established by the staging
    copy itself, which fails loudly.
    """
    probe = process_probe if process_probe is not None else _drivefs_process_running
    checks: dict[str, Any] = {}

    checks["drivefs_root"] = str(target.drivefs_root)
    checks["root_present"] = target.drivefs_root.is_dir()
    if not checks["root_present"]:
        return {"status": DRIVEFS_UNAVAILABLE, "reason": "MOUNT_ROOT_ABSENT", "checks": checks}

    checks["drivefs_process_running"] = bool(probe())
    if not checks["drivefs_process_running"]:
        return {
            "status": DRIVEFS_UNAVAILABLE,
            "reason": "GOOGLEDRIVEFS_NOT_RUNNING",
            "checks": checks,
        }

    checks["target_dir"] = str(target.target_dir)
    checks["target_present"] = target.target_dir.is_dir()
    if not checks["target_present"]:
        return {"status": TARGET_MISSING, "reason": "TARGET_DIR_ABSENT", "checks": checks}

    found = [m for m in target.markers if (target.target_dir / m).exists()]
    checks["markers_required"] = list(target.markers)
    checks["markers_found"] = found
    checks["min_markers"] = target.min_markers
    if len(found) < target.min_markers:
        return {
            "status": MARKER_MISSING,
            "reason": "TARGET_IDENTITY_NOT_PROVEN",
            "detail": (
                "The path exists but does not contain the expected AORUS/results "
                "markers. Refusing to write: this may be a different Drive "
                "account, a different folder, or a re-used drive letter."
            ),
            "checks": checks,
        }

    checks["folder_id"] = target.folder_id
    return {"status": TARGET_OK, "reason": None, "checks": checks}


# ---------------------------------------------------------------------------
# Ledger (outside the world repo)
# ---------------------------------------------------------------------------


def default_ledger_dir() -> Path:
    return aiye_home() / "drivefs_bridge"


def _append_jsonl(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return record


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # a torn final line from a crash must not destroy the ledger
    return out


def ledger_path(ledger_dir: Path) -> Path:
    return Path(ledger_dir) / LEDGER_NAME


def queue_path(ledger_dir: Path) -> Path:
    return Path(ledger_dir) / QUEUE_NAME


def append_ledger(ledger_dir: Path, record: dict[str, Any]) -> dict[str, Any]:
    rec = {"schema": BRIDGE_SCHEMA, "recorded_utc": utc_now(), **record}
    return _append_jsonl(ledger_path(ledger_dir), rec)


def read_ledger(ledger_dir: Path) -> list[dict[str, Any]]:
    return _read_jsonl(ledger_path(ledger_dir))


def state_by_bundle(ledger_dir: Path) -> dict[str, dict[str, Any]]:
    """Latest record per *bundle* digest - the unit actually copied."""
    latest: dict[str, dict[str, Any]] = {}
    for r in read_ledger(ledger_dir):
        k = r.get("bundle_sha256")
        if k:
            latest[k] = r
    return latest


def state_by_content(ledger_dir: Path) -> dict[str, dict[str, Any]]:
    """Latest record per *content* state - the unit of semantic delivery.

    A content state delivered once is delivered, regardless of how many
    temporal snapshots of it the producer emitted. Records are kept by evidence
    strength, not by arrival order, so a later weaker observation never demotes
    a stronger one.
    """
    latest: dict[str, dict[str, Any]] = {}
    for r in read_ledger(ledger_dir):
        k = r.get("content_sha256")
        if not k:
            continue
        prev = latest.get(k)
        if prev is not None and STATUS_RANK.get(r.get("status"), -1) < STATUS_RANK.get(prev.get("status"), -1):
            continue
        latest[k] = r
    return latest


# ---------------------------------------------------------------------------
# Lock - scoped to THIS uploader only
# ---------------------------------------------------------------------------


class BridgeLockBusy(RuntimeError):
    pass


@dataclass
class BridgeLock:
    """Exclusive lock for the DriveFS bridge alone.

    It guards this uploader against itself (a scheduled run overlapping a manual
    one). It intentionally does NOT guard the world sync, the exporter or the
    gateway - taking a lock those components do not know about would be a race
    dressed as safety.
    """

    path: Path
    stale_seconds: int = 1800
    _held: bool = field(default=False, init=False)
    broke_stale: dict[str, Any] | None = field(default=None, init=False)

    def acquire(self) -> "BridgeLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {
                "pid": os.getpid(),
                "host": socket.gethostname(),
                "acquired_utc": utc_now(),
                "acquired_monotonic_epoch": time.time(),
            }
        )
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            age = time.time() - self.path.stat().st_mtime
            if age < self.stale_seconds:
                try:
                    holder = json.loads(self.path.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    holder = {}
                raise BridgeLockBusy(
                    f"another drivefs bridge run holds {self.path} "
                    f"(age {age:.0f}s < {self.stale_seconds}s): {holder}"
                )
            self.broke_stale = {"age_seconds": round(age, 1), "path": str(self.path)}
            self.path.unlink(missing_ok=True)
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(payload)
        self._held = True
        return self

    def release(self) -> None:
        if self._held:
            self.path.unlink(missing_ok=True)
            self._held = False

    def __enter__(self) -> "BridgeLock":
        return self.acquire()

    def __exit__(self, *exc: Any) -> None:
        self.release()


# ---------------------------------------------------------------------------
# Naming + staging
# ---------------------------------------------------------------------------


def deterministic_name(entity_id: str, content_sha256: str, bundle_sha256: str) -> str:
    """Stable destination name for a payload.

    Carries both digests on purpose. ``c<content>`` makes a human able to see
    which semantic state a file is; ``b<bundle>`` makes the name a claim about
    the bytes, so "the destination already exists" can be settled by comparison
    instead of by trust.
    """
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", entity_id).strip("-") or "entity"
    return f"proteus-carrier.{safe}.c{content_sha256[:16]}.b{bundle_sha256[:16]}.zip"


def verify_bundle_local(bundle: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Refuse to copy anything we have not first proven locally."""
    if not bundle.is_file():
        return {"ok": False, "reason": BUNDLE_MISSING}
    sha, size = sha256_file(bundle)
    if size == 0:
        return {"ok": False, "reason": BUNDLE_EMPTY, "bundle_sha256": sha, "bundle_bytes": 0}
    declared = manifest.get("bundle_sha256")
    if declared and declared != sha:
        return {
            "ok": False,
            "reason": LOCAL_DIGEST_MISMATCH,
            "bundle_sha256": sha,
            "declared_sha256": declared,
            "bundle_bytes": size,
        }
    declared_bytes = manifest.get("bundle_bytes")
    if declared_bytes is not None and int(declared_bytes) != size:
        return {
            "ok": False,
            "reason": LOCAL_DIGEST_MISMATCH,
            "bundle_sha256": sha,
            "bundle_bytes": size,
            "declared_bytes": declared_bytes,
        }
    try:
        with zipfile.ZipFile(bundle) as zf:
            bad = zf.testzip()
            if bad is not None:
                return {"ok": False, "reason": ZIP_CORRUPT, "bad_member": bad, "bundle_sha256": sha}
            # A valid archive is not yet a carrier. Requiring the manifest member
            # keeps an unrelated zip (or a truncated-then-repaired one) out of the
            # corpus, and is the only structural claim this module makes about
            # bundle contents.
            json.loads(zf.read("CARRIER_MANIFEST.json"))
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
        return {
            "ok": False,
            "reason": ZIP_CORRUPT,
            "error": f"{type(exc).__name__}: {exc}",
            "bundle_sha256": sha,
        }
    return {"ok": True, "bundle_sha256": sha, "bundle_bytes": size}


def _cleanup_own_temps(target_dir: Path, *, older_than_seconds: int = 3600) -> list[str]:
    """Remove ONLY our own abandoned temp files. Never touches anything else."""
    removed: list[str] = []
    try:
        entries = list(target_dir.iterdir())
    except OSError:
        return removed
    now = time.time()
    for p in entries:
        if not p.name.startswith(TEMP_PREFIX):
            continue
        try:
            if now - p.stat().st_mtime < older_than_seconds:
                continue
            p.unlink()
            removed.append(p.name)
        except OSError:
            continue
    return removed


def stage_one(
    target: DriveFsTarget,
    manifest: dict[str, Any],
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Place one bundle into the DriveFS target. Local proof only.

    A successful return is ``STAGED_LOCAL``: written, renamed into place, and
    read back byte-identical *through G:*. That is a local-cache fact. The
    cloud fact is a separate status reached only via :func:`import_cloud_receipt`.
    """
    entity_id = manifest.get("entity_id") or "unknown.entity"
    content_sha = manifest.get("content_sha256")
    bundle_path = Path(manifest.get("bundle_path") or "")

    base = {
        "entity_id": entity_id,
        "content_sha256": content_sha,
        "source_bundle_path": str(bundle_path),
        "manifest_path": manifest.get("_manifest_path"),
        "cloud_folder_id": target.folder_id,
    }

    declared_target = manifest.get("drive_export_target")
    if declared_target and declared_target != target.folder_id:
        return {
            **base,
            "status": STAGE_FAILED,
            "reason": MANIFEST_TARGET_MISMATCH,
            "detail": f"manifest targets {declared_target!r}, adapter targets {target.folder_id!r}",
        }

    local = verify_bundle_local(bundle_path, manifest)
    if not local["ok"]:
        return {**base, "status": STAGE_FAILED, **{k: v for k, v in local.items() if k != "ok"}}

    bundle_sha = local["bundle_sha256"]
    size = local["bundle_bytes"]
    name = deterministic_name(entity_id, content_sha or bundle_sha, bundle_sha)
    dest = target.target_dir / name
    base.update({"bundle_sha256": bundle_sha, "bundle_bytes": size, "dest_name": name,
                 "dest_path": str(dest)})

    if dry_run:
        return {**base, "status": "DRY_RUN", "dest_exists": dest.exists()}

    # Destination already present: compare, never clobber.
    if dest.exists():
        try:
            dsha, dsize = sha256_file(dest)
        except OSError as exc:
            return {**base, "status": STAGE_RETRY, "reason": COPY_FAILED, "error": str(exc)}
        if dsha == bundle_sha:
            return {**base, "status": SKIPPED_IDENTICAL, "dest_sha256": dsha, "dest_bytes": dsize}
        return {
            **base,
            "status": STAGE_FAILED,
            "reason": NAME_COLLISION_DIFFERENT_PAYLOAD,
            "dest_sha256": dsha,
            "dest_bytes": dsize,
            "detail": "same deterministic name, different bytes - refusing to overwrite",
        }

    tmp = target.target_dir / f"{TEMP_PREFIX}{os.getpid()}-{random.randrange(1 << 30):08x}"
    try:
        with open(bundle_path, "rb") as src, open(tmp, "wb") as dst:
            while True:
                chunk = src.read(CHUNK)
                if not chunk:
                    break
                dst.write(chunk)
            dst.flush()
            os.fsync(dst.fileno())
        # os.rename, not os.replace: on Windows it FAILS if the destination
        # exists. Losing the race is then an error we can inspect, not a silent
        # overwrite of somebody else's payload.
        try:
            os.rename(tmp, dest)
        except FileExistsError:
            tmp.unlink(missing_ok=True)
            dsha, dsize = sha256_file(dest)
            if dsha == bundle_sha:
                return {**base, "status": SKIPPED_IDENTICAL, "dest_sha256": dsha,
                        "dest_bytes": dsize, "raced": True}
            return {
                **base,
                "status": STAGE_FAILED,
                "reason": NAME_COLLISION_DIFFERENT_PAYLOAD,
                "dest_sha256": dsha,
                "raced": True,
            }
    except OSError as exc:
        tmp.unlink(missing_ok=True)
        return {**base, "status": STAGE_RETRY, "reason": COPY_FAILED, "error": f"{type(exc).__name__}: {exc}"}

    # Read back THROUGH the mount. Proves the write landed; proves nothing about
    # the cloud.
    try:
        rsha, rsize = sha256_file(dest)
    except OSError as exc:
        return {**base, "status": STAGE_RETRY, "reason": COPY_FAILED, "error": str(exc)}
    if rsha != bundle_sha or rsize != size:
        # We created this file in this call, so removing it is safe and leaves
        # the corpus exactly as we found it.
        try:
            dest.unlink()
            removed = True
        except OSError:
            removed = False
        return {
            **base,
            "status": STAGE_FAILED,
            "reason": READBACK_MISMATCH,
            "readback_sha256": rsha,
            "readback_bytes": rsize,
            "bad_copy_removed": removed,
        }

    return {
        **base,
        "status": STAGED_LOCAL,
        "readback_sha256": rsha,
        "readback_bytes": rsize,
        "readback_via": "DriveFS mount (G:) - LOCAL CACHE ONLY, not a cloud proof",
    }


# ---------------------------------------------------------------------------
# Queue reconciliation
# ---------------------------------------------------------------------------


def plan_stage(
    store: WorldStore,
    ledger_dir: Path,
    *,
    batch_cap: int = 8,
    max_bytes: int = 64 * 1024 * 1024,
) -> dict[str, Any]:
    """Collapse the manifest backlog to distinct content states and pick a batch.

    The producer republishes an unchanged state on every cycle, so the queue is
    mostly temporal duplicates of the same semantics: on 2026-10-10 that was 209
    manifests covering 125 states. Delivery is per *state*. Nothing is deleted
    to achieve the collapse - the historical manifests stay exactly where they
    are, and this is a pure read.

    Newest state first, then a bounded backfill of older ones, so the live
    frontier is never starved by history and history still drains.
    """
    manifests = load_manifests(store)
    pending_dir = store.root / "pending_drive_uploads"
    # load_manifests drops the source path, which the handoff record needs.
    by_bundle = {}
    for mp in sorted(pending_dir.glob("*.PENDING_DRIVE_UPLOAD.json")) if pending_dir.is_dir() else []:
        try:
            by_bundle[json.loads(mp.read_text(encoding="utf-8")).get("bundle_path")] = str(mp)
        except (OSError, ValueError):
            continue

    newest_for: dict[str, dict[str, Any]] = {}
    unidentifiable = 0
    for m in manifests:
        cs = m.get("content_sha256") or _content_sha_from_bundle(m.get("bundle_path"))
        if not cs:
            unidentifiable += 1
            continue
        m = {**m, "content_sha256": cs, "_manifest_path": by_bundle.get(m.get("bundle_path"))}
        prev = newest_for.get(cs)
        if prev is None or str(m.get("generated_utc", "")) >= str(prev.get("generated_utc", "")):
            newest_for[cs] = m

    delivered = state_by_content(ledger_dir)
    todo: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for cs, m in newest_for.items():
        rec = delivered.get(cs)
        if rec and rec.get("status") in TERMINAL_DELIVERED:
            skipped.append({"content_sha256": cs, "reason": f"ALREADY_{rec['status']}"})
            continue
        bp = m.get("bundle_path")
        if not bp or not Path(bp).exists():
            skipped.append({"content_sha256": cs, "reason": BUNDLE_MISSING})
            continue
        todo.append(m)

    # Newest first.
    todo.sort(key=lambda m: str(m.get("generated_utc", "")), reverse=True)

    batch: list[dict[str, Any]] = []
    budget = max_bytes
    for m in todo:
        if len(batch) >= batch_cap:
            break
        size = int(m.get("bundle_bytes") or 0)
        if batch and size > budget:
            break
        budget -= size
        batch.append(m)

    cloud_verified = sum(1 for r in delivered.values() if r.get("status") == CLOUD_VERIFIED)
    staged = sum(1 for r in delivered.values() if r.get("status") in (STAGED_LOCAL, SKIPPED_IDENTICAL))
    return {
        "schema": BRIDGE_SCHEMA,
        "planned_utc": utc_now(),
        "manifests_seen": len(manifests),
        "manifests_unidentifiable": unidentifiable,
        "distinct_content_states": len(newest_for),
        "already_staged_local": staged,
        "already_cloud_verified": cloud_verified,
        "eligible": len(todo),
        "batch_cap": batch_cap,
        "max_bytes": max_bytes,
        "deferred_by_cap": max(0, len(todo) - len(batch)),
        "to_stage": batch,
        "skipped": skipped,
    }


# ---------------------------------------------------------------------------
# Cloud verification handoff
# ---------------------------------------------------------------------------


def cloud_verify_queue(ledger_dir: Path) -> list[dict[str, Any]]:
    """Open handshake records: staged locally, awaiting an independent readback."""
    verified = {
        r.get("bundle_sha256")
        for r in read_ledger(ledger_dir)
        if r.get("status") == CLOUD_VERIFIED
    }
    out = []
    seen: set[str] = set()
    for r in _read_jsonl(queue_path(ledger_dir)):
        k = r.get("bundle_sha256")
        if not k or k in verified or k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def _queue_record(staged: dict[str, Any]) -> dict[str, Any]:
    """The exact contract a cloud verifier needs - and nothing more.

    No path on the local disk is required to do the work: a verifier searches
    ``cloud_folder_id`` for ``dest_name``, downloads it by file id, and compares
    ``expect_sha256`` / ``expect_bytes``.
    """
    return {
        "schema": STAGE_RECEIPT_SCHEMA,
        "queued_utc": utc_now(),
        "status": "PENDING_CLOUD_VERIFY",
        "entity_id": staged.get("entity_id"),
        "content_sha256": staged.get("content_sha256"),
        "bundle_sha256": staged.get("bundle_sha256"),
        "expect_sha256": staged.get("bundle_sha256"),
        "expect_bytes": staged.get("bundle_bytes"),
        "dest_name": staged.get("dest_name"),
        "cloud_folder_id": staged.get("cloud_folder_id"),
        "manifest_path": staged.get("manifest_path"),
        "source_bundle_path": staged.get("source_bundle_path"),
        "verifier_instructions": (
            "Locate dest_name inside Google Drive folder cloud_folder_id, download "
            "the raw bytes by file id through a provider path that is NOT this "
            "host's G: mount, and confirm sha256 == expect_sha256 and length == "
            "expect_bytes and `unzip -t` reports no CRC error. Then return a "
            f"{RECEIPT_SCHEMA} receipt and import it with import_cloud_receipt()."
        ),
    }


def import_cloud_receipt(
    ledger_dir: Path,
    receipt: dict[str, Any],
) -> dict[str, Any]:
    """Promote STAGED_LOCAL -> CLOUD_VERIFIED on independent evidence only.

    Every field is checked against what we actually staged. A receipt that does
    not match the staged bytes is recorded as a mismatch and promotes nothing;
    a receipt for something we never staged is rejected rather than trusted.
    """
    sha = receipt.get("cloud_download_sha256") or receipt.get("source_sha256")
    staged = {
        r.get("bundle_sha256"): r
        for r in read_ledger(ledger_dir)
        if r.get("status") in (STAGED_LOCAL, SKIPPED_IDENTICAL)
    }
    rec = staged.get(sha)
    problems: list[str] = []

    if receipt.get("schema") != RECEIPT_SCHEMA:
        problems.append(f"WRONG_SCHEMA:{receipt.get('schema')!r}")
    if not sha:
        problems.append("NO_DIGEST_IN_RECEIPT")
    if rec is None:
        problems.append("NO_MATCHING_STAGED_RECORD")
    else:
        dl = receipt.get("cloud_download_sha256")
        src = receipt.get("source_sha256")
        if dl and src and dl != src:
            problems.append("RECEIPT_SELF_INCONSISTENT")
        if dl and dl != rec.get("bundle_sha256"):
            problems.append("CLOUD_DIGEST_MISMATCH")
        n = receipt.get("source_length_bytes")
        if n is not None and int(n) != int(rec.get("bundle_bytes") or -1):
            problems.append("BYTE_LENGTH_MISMATCH")
        pid = receipt.get("cloud_parent_id")
        if pid and pid != rec.get("cloud_folder_id"):
            problems.append("PARENT_FOLDER_MISMATCH")
    if not receipt.get("cloud_file_id"):
        problems.append("NO_CLOUD_FILE_ID")

    if problems:
        out = append_ledger(
            ledger_dir,
            {
                "status": "CLOUD_VERIFY_MISMATCH",
                "bundle_sha256": sha,
                "content_sha256": (rec or {}).get("content_sha256"),
                "entity_id": (rec or {}).get("entity_id"),
                "problems": problems,
                "receipt": receipt,
            },
        )
        return {"ok": False, "problems": problems, "record": out}

    out = append_ledger(
        ledger_dir,
        {
            "status": CLOUD_VERIFIED,
            "entity_id": rec.get("entity_id"),
            "content_sha256": rec.get("content_sha256"),
            "bundle_sha256": rec.get("bundle_sha256"),
            "bundle_bytes": rec.get("bundle_bytes"),
            "dest_name": rec.get("dest_name"),
            "cloud_folder_id": rec.get("cloud_folder_id"),
            "cloud_file_id": receipt.get("cloud_file_id"),
            "cloud_url": receipt.get("cloud_url"),
            "cloud_zip_integrity": receipt.get("cloud_zip_integrity"),
            "cloud_readback_via": receipt.get("cloud_readback_via"),
            "verified_by": receipt.get("verified_by") or receipt.get("cloud_readback_via"),
            "receipt_verified_at_utc": receipt.get("verified_at_utc"),
        },
    )
    return {"ok": True, "problems": [], "record": out}


def import_cloud_presence(
    ledger_dir: Path,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Record that the provider can see the staged object. NOT byte identity.

    The evidence available from a metadata query is: the object exists, in the
    expected parent folder, under the expected name, with the expected byte
    length. That is enough to prove the bytes left this machine and enough to
    catch a truncated or zero-length upload - and it is not enough to catch the
    2-byte corruption class, because no checksum is exposed.

    So this deliberately cannot promote anything. The item stays on the cloud
    verification queue until a real digest arrives.
    """
    name = evidence.get("cloud_file_name") or evidence.get("dest_name")
    staged = {
        r.get("dest_name"): r
        for r in read_ledger(ledger_dir)
        if r.get("status") in (STAGED_LOCAL, SKIPPED_IDENTICAL) and r.get("dest_name")
    }
    rec = staged.get(name)
    problems: list[str] = []

    if evidence.get("schema") != PRESENCE_SCHEMA:
        problems.append(f"WRONG_SCHEMA:{evidence.get('schema')!r}")
    if rec is None:
        problems.append("NO_MATCHING_STAGED_RECORD")
    else:
        n = evidence.get("cloud_file_size_bytes")
        if n is None:
            problems.append("NO_BYTE_LENGTH")
        elif int(n) != int(rec.get("bundle_bytes") or -1):
            problems.append("BYTE_LENGTH_MISMATCH")
        pid = evidence.get("cloud_parent_id")
        if not pid:
            problems.append("NO_PARENT_ID")
        elif pid != rec.get("cloud_folder_id"):
            problems.append("PARENT_FOLDER_MISMATCH")
    if not evidence.get("cloud_file_id"):
        problems.append("NO_CLOUD_FILE_ID")

    if problems:
        out = append_ledger(
            ledger_dir,
            {
                "status": "CLOUD_PRESENCE_MISMATCH",
                "dest_name": name,
                "problems": problems,
                "evidence": evidence,
            },
        )
        return {"ok": False, "problems": problems, "record": out}

    out = append_ledger(
        ledger_dir,
        {
            "status": CLOUD_PRESENT,
            "entity_id": rec.get("entity_id"),
            "content_sha256": rec.get("content_sha256"),
            "bundle_sha256": rec.get("bundle_sha256"),
            "bundle_bytes": rec.get("bundle_bytes"),
            "dest_name": rec.get("dest_name"),
            "cloud_folder_id": rec.get("cloud_folder_id"),
            "cloud_file_id": evidence.get("cloud_file_id"),
            "cloud_file_size_bytes": evidence.get("cloud_file_size_bytes"),
            "cloud_url": evidence.get("cloud_url"),
            "observed_via": evidence.get("observed_via"),
            "observed_at_utc": evidence.get("observed_at_utc"),
            "still_pending_byte_verification": True,
            "limitation": (
                "Provider metadata exposes no checksum. Name, parent and exact "
                "byte length agree; byte identity is NOT established."
            ),
        },
    )
    return {"ok": True, "problems": [], "record": out}


def scan_foreign_artifacts(target: DriveFsTarget, ledger_dir: Path) -> list[dict[str, Any]]:
    """Carrier-looking files in the target that this adapter did NOT stage.

    Chiefly the 13527-byte archive the earlier model-mediated base64 route
    delivered with 2 corrupted bytes. It must stay visible and must never be
    counted as a delivery. We do not touch it - classifying is not deleting.
    """
    if not target.target_dir.is_dir():
        return []
    ours = {r.get("dest_name") for r in read_ledger(ledger_dir) if r.get("dest_name")}
    out = []
    for p in sorted(target.target_dir.glob("*carrier*.zip")):
        if p.name in ours or NAME_RE.match(p.name):
            continue
        try:
            st = p.stat()
        except OSError:
            continue
        out.append(
            {
                "name": p.name,
                "bytes": st.st_size,
                "status": FOREIGN_UNVERIFIED,
                "note": "not staged by drivefs_bridge; provenance and integrity unverified",
            }
        )
    return out


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------


def run_stage(
    *,
    target: DriveFsTarget,
    store: WorldStore | None = None,
    ledger_dir: Path | None = None,
    batch_cap: int = 8,
    max_bytes: int = 64 * 1024 * 1024,
    max_seconds: int = 300,
    dry_run: bool = False,
    process_probe: Callable[[], bool] | None = None,
    lock_stale_seconds: int = 1800,
) -> dict[str, Any]:
    """One bounded delivery pass. Never raises on an expected failure; reports it.

    Returns a summary whose ``exit_code`` is what a scheduler should propagate.
    """
    store = store or WorldStore()
    ledger_dir = Path(ledger_dir) if ledger_dir else default_ledger_dir()
    ledger_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()

    summary: dict[str, Any] = {
        "schema": BRIDGE_SCHEMA,
        "started_utc": utc_now(),
        "host": socket.gethostname(),
        "dry_run": dry_run,
        "ledger_dir": str(ledger_dir),
    }

    validation = validate_target(target, process_probe=process_probe)
    summary["target"] = validation
    if validation["status"] != TARGET_OK:
        summary.update(
            {
                "status": validation["status"],
                "staged": [], "skipped_identical": [], "failed": [],
                "finished_utc": utc_now(),
                "exit_code": 2,
            }
        )
        append_ledger(ledger_dir, {"status": validation["status"], "reason": validation.get("reason"),
                                   "checks": validation.get("checks")})
        write_summary(ledger_dir, summary)
        return summary

    try:
        lock = BridgeLock(Path(ledger_dir) / LOCK_NAME, stale_seconds=lock_stale_seconds).acquire()
    except BridgeLockBusy as exc:
        summary.update({"status": "LOCK_BUSY", "detail": str(exc), "staged": [],
                        "skipped_identical": [], "failed": [], "finished_utc": utc_now(),
                        "exit_code": 0})
        return summary

    try:
        if lock.broke_stale:
            append_ledger(ledger_dir, {"status": "STALE_LOCK_BROKEN", **lock.broke_stale})
        summary["stale_lock_broken"] = lock.broke_stale

        if not dry_run:
            removed = _cleanup_own_temps(target.target_dir)
            summary["abandoned_temps_removed"] = removed
            if removed:
                append_ledger(ledger_dir, {"status": "TEMP_CLEANUP", "removed": removed})

        plan = plan_stage(store, ledger_dir, batch_cap=batch_cap, max_bytes=max_bytes)
        summary["plan"] = {k: v for k, v in plan.items() if k != "to_stage"}
        summary["plan"]["batch_size"] = len(plan["to_stage"])

        staged, identical, failed = [], [], []
        timed_out = False
        for m in plan["to_stage"]:
            if time.monotonic() - started > max_seconds:
                timed_out = True
                break
            res = stage_one(target, m, dry_run=dry_run)
            if dry_run:
                staged.append(res)
                continue
            append_ledger(ledger_dir, res)
            if res["status"] == STAGED_LOCAL:
                _append_jsonl(queue_path(ledger_dir), _queue_record(res))
                staged.append(res)
            elif res["status"] == SKIPPED_IDENTICAL:
                _append_jsonl(queue_path(ledger_dir), _queue_record(res))
                identical.append(res)
            else:
                failed.append(res)

        summary.update(
            {
                "staged": staged,
                "skipped_identical": identical,
                "failed": failed,
                "timed_out": timed_out,
                "max_seconds": max_seconds,
                "foreign_artifacts": scan_foreign_artifacts(target, ledger_dir),
                "cloud_verify_pending": len(cloud_verify_queue(ledger_dir)),
                "finished_utc": utc_now(),
                "elapsed_seconds": round(time.monotonic() - started, 2),
            }
        )
        hard = [f for f in failed if f["status"] == STAGE_FAILED]
        summary["status"] = "STAGED_UNVERIFIED" if not hard else "PARTIAL_FAILURE"
        if dry_run:
            summary["status"] = "DRY_RUN"
        summary["exit_code"] = 1 if hard else 0
        if not dry_run:
            write_summary(ledger_dir, summary)
        return summary
    finally:
        lock.release()


def write_summary(ledger_dir: Path, summary: dict[str, Any]) -> Path:
    """Human-readable state. Derived, rewritable - the JSONL stays authoritative."""
    ledger_dir = Path(ledger_dir)
    records = read_ledger(ledger_dir)
    by_state = state_by_content(ledger_dir)
    verified = [r for r in by_state.values() if r.get("status") == CLOUD_VERIFIED]
    present = [r for r in by_state.values() if r.get("status") == CLOUD_PRESENT]
    staged = [r for r in by_state.values() if r.get("status") in TERMINAL_DELIVERED]
    pending = cloud_verify_queue(ledger_dir)
    plan = summary.get("plan", {})

    lines = [
        "# DriveFS delivery summary",
        "",
        f"- generated: `{utc_now()}`",
        f"- host: `{summary.get('host')}`",
        f"- last run status: **{summary.get('status')}** (exit {summary.get('exit_code')})",
        f"- target folder id: `{summary.get('target', {}).get('checks', {}).get('folder_id')}`",
        "",
        "## Counts",
        "",
        "| metric | value |",
        "|---|---|",
        f"| manifests seen | {plan.get('manifests_seen', '?')} |",
        f"| distinct content states | {plan.get('distinct_content_states', '?')} |",
        f"| DRIVEFS_STAGED (states) | {len(staged)} |",
        f"| CLOUD_PRESENT, length only (states) | {len(present)} |",
        f"| PROVIDER_BYTE_VERIFIED (states) | {len(verified)} |",
        f"| pending cloud verification | {len(pending)} |",
        f"| still eligible to stage | {plan.get('eligible', '?')} |",
        f"| ledger records | {len(records)} |",
        "",
        "## Pending cloud verification (handoff queue)",
        "",
    ]
    if pending:
        lines += ["| dest_name | sha256 | bytes | folder |", "|---|---|---|---|"]
        for q in pending[:50]:
            lines.append(
                f"| `{q.get('dest_name')}` | `{q.get('expect_sha256')}` | "
                f"{q.get('expect_bytes')} | `{q.get('cloud_folder_id')}` |"
            )
    else:
        lines.append("_none_")
    lines += [
        "",
        "## Honesty note",
        "",
        "`STAGED_LOCAL` means the bytes were written into the DriveFS mount and read",
        "back identically **through that same mount**. It is not evidence the bytes",
        "reached Google.",
        "",
        "`CLOUD_PRESENT` means the provider reports the object under the expected name,",
        "parent and exact byte length. That proves the upload left this machine. It is",
        "**not** byte identity - no checksum is exposed by that path.",
        "",
        "Only an imported",
        f"`{RECEIPT_SCHEMA}` receipt from an independent provider-side download",
        "produces `CLOUD_VERIFIED`.",
        "",
    ]
    foreign = summary.get("foreign_artifacts") or []
    if foreign:
        lines += ["## Foreign artifacts in target (not staged by this adapter)", ""]
        for f in foreign:
            lines.append(f"- `{f['name']}` ({f['bytes']} bytes) - {f['note']}")
        lines.append("")

    p = ledger_dir / SUMMARY_NAME
    p.write_text("\n".join(lines), encoding="utf-8")
    return p

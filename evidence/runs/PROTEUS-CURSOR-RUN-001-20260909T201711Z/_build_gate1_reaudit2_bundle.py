"""Build isolated Gate1 REAUDIT-002 bundle from frozen commit (no origin worktree)."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SRC = Path(r"C:\projects\Proteus")
COMMIT = "94e6f09d29c9c58bfaf01fac2917a0263cf54311"
AUDIT = Path(r"C:\Projects\Proteus-GATE1-REAUDIT-002")
ZIP = Path(r"C:\Projects\_proteus_gate1_reaudit2_94e6f09.zip")
EP = SRC / "evidence" / "runs" / "PROTEUS-CURSOR-RUN-001-20260909T201711Z"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(rel: str) -> str:
    r = rel.replace("\\", "/")
    if r.startswith(("REAUDIT_2_", "OPEN_BOUNDARIES_FOR_REAUDIT_2", "GATE1_REAUDIT_2_")):
        return "reaudit_bundle_generated"
    if r.startswith("evidence/"):
        return "git_tracked_evidence"
    if r.startswith("_BOOTSTRAP/"):
        return "git_tracked_authority"
    if r.startswith("state/"):
        return "git_tracked_state"
    if r.startswith(("src/", "hosts/", "tests/")):
        return "git_tracked_implementation"
    return "git_tracked_other"


def relation(rel: str) -> str:
    r = rel.replace("\\", "/")
    if "FINAL_THREE" in r or "CURSOR_NATIVE" in r or "SHARED_FRONTIER" in r:
        return "final_three_closure"
    if "GATE1_INDEPENDENT" in r or "GATE1_AUDITOR" in r or "GATE1_REAUDIT" in r:
        return "prior_gate_audit"
    if "GATE1_BLOCKER" in r or r.endswith(
        (
            "T04_RESULT.md",
            "T05_RESULT.md",
            "T09_RESULT.md",
            "T11_CURRENT_SATISFACTION_CROSSWALK.md",
            "PROCESS_DEATH_RESULT.md",
            "T13_L6_POST_INSTALL_SECOND_CYCLE.md",
        )
    ):
        return "first_blocker_closure"
    if r.startswith("src/proteus/frontier_reconcile"):
        return "d012_implementation"
    return "baseline_or_authority"


READING_ORDER = """# REAUDIT_2_READING_ORDER

Independent Gate 1 re-audit #2. You are not Proteus / BUILDER-01.

1. `REAUDIT_2_FREEZE.json` — audited tip, hashes, exclusions
2. `_BOOTSTRAP/BLIND_START/50_GATE1_EVAL.md` + `60_CURRENT_PROTEUS_STATUS.md`
3. `state/CURRENT.md`, `state/FRONTIER.md`, `state/UNRESOLVED.md`, `state/DECISIONS.md` (D-001–D-012)
4. Prior audits: `GATE1_INDEPENDENT_AUDIT.md`, `GATE1_INDEPENDENT_REAUDIT.md` (+ raw)
5. First blocker closure matrix/map (historical claims)
6. Final-three map/matrix/closure + T02 native / T09 reconcile / T13 Cursor-path evidence + raws
7. D-012 source: `src/proteus/frontier_reconcile.py` + CLI wiring + tests
8. Whole-Gate capability sanity against primary evidence, not origin PASS labels alone

Do not use live `C:\\Projects\\Proteus` or `C:\\projects\\Proteus`.
Do not activate Proteus.
"""

OPEN_BOUNDARIES = """# OPEN_BOUNDARIES_FOR_REAUDIT_2

Known candidates for classification by the auditor (not pre-judged as Gate blockers):

- LIVE_ARCHIVARIUS_RECONCILIATION = BLOCKED
- AW1000_REAL_SECRET = UNAVAILABLE
- Drive Desktop observatory transport FAILED_TRANSPORT (MCP path exists)
- Tyumen University source access blocked
- Claude / OpenClaw foreign carriers not yet supported
- Multi-machine sync not claimed
- Python/runtime prerequisites for portable reconstruct
- Packaging / marketplace / UX / field deployment (post-Gate candidates)

Auditor must classify each as GATE_BLOCKER | ACCEPTED_OPEN_BOUNDARY | POST_GATE under Gate authority.
"""


def main() -> None:
    head = subprocess.check_output(["git", "-C", str(SRC), "rev-parse", "HEAD"], text=True).strip()
    if head != COMMIT:
        raise SystemExit(f"HEAD {head} != expected {COMMIT}")

    if AUDIT.exists():
        shutil.rmtree(AUDIT)
    AUDIT.mkdir(parents=True)
    if ZIP.exists():
        ZIP.unlink()

    subprocess.check_call(["git", "-C", str(SRC), "archive", "--format=zip", "-o", str(ZIP), COMMIT])
    with zipfile.ZipFile(ZIP, "r") as zf:
        zf.extractall(AUDIT)

    freeze = {
        "schema": "proteus.gate1_reaudit2_freeze.v0.1",
        "audited_commit": COMMIT,
        "origin_head_at_freeze": head,
        "created_utc": utc_now(),
        "method": "git archive --format=zip -o ZIP <commit>; Expand into isolated AUDIT dir",
        "bundle_root": str(AUDIT),
        "archive_zip": str(ZIP),
        "working_tree_note": (
            "origin tree clean for tracked files; untracked isolated Cursor userdata dirs "
            "excluded by git archive (not part of subject)"
        ),
        "excluded_untracked": [
            "evidence/runs/.../gate1_final3_isolated_cursor_userdata/",
            "evidence/runs/.../gate1_isolated_cursor_userdata/",
            "evidence/runs/.../gate1_isolated_cursor_userdata2/",
        ],
        "first_audit_subject_commit": "94e3d60c9785789f1b7e812a865a325fcb23475f",
        "second_reaudit_subject_commit": "4b1f8d39a6731a994dc67c66aa8f5c059bda78d8",
        "prior_verdicts": {
            "first_audit": "NOT_ACCEPTED",
            "second_reaudit": "NOT_ACCEPTED",
        },
        "origin_claims_to_audit_not_accept": [
            "Cursor-native T02 current PASS",
            "T09 reconciliation PASS",
            "Cursor-path T13 PASS",
            "L6 PASS",
            "D-012 accepted",
            "no remaining Gate-critical blockers from second auditor minimum set",
        ],
        "note": "Isolated extract; auditor must not use live Proteus origin tree.",
    }
    (AUDIT / "REAUDIT_2_FREEZE.json").write_text(
        json.dumps(freeze, indent=2) + "\n", encoding="utf-8"
    )
    (AUDIT / "REAUDIT_2_READING_ORDER.md").write_text(READING_ORDER, encoding="utf-8")
    (AUDIT / "OPEN_BOUNDARIES_FOR_REAUDIT_2.md").write_text(OPEN_BOUNDARIES, encoding="utf-8")

    # Manifest over all files except the manifest itself
    files = []
    for path in sorted(AUDIT.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(AUDIT)).replace("\\", "/")
        if rel in ("GATE1_REAUDIT_2_MANIFEST.json", "GATE1_REAUDIT_2_CONTENT_ADDRESS.txt"):
            continue
        digest = sha256_file(path)
        files.append(
            {
                "path": rel,
                "sha256": digest,
                "bytes": path.stat().st_size,
                "provenance": classify(rel),
                "status": "git_tracked" if not classify(rel).endswith("generated") else "generated",
                "audited_commit": COMMIT,
                "relation": relation(rel),
            }
        )

    # Content-address: sorted path + sha256 lines
    ca = hashlib.sha256()
    for e in files:
        ca.update(f"{e['path']}\0{e['sha256']}\n".encode("utf-8"))
    content_address = ca.hexdigest()
    (AUDIT / "GATE1_REAUDIT_2_CONTENT_ADDRESS.txt").write_text(
        content_address + "\n", encoding="utf-8"
    )

    # Include content-address file in manifest after hashing it
    ca_path = "GATE1_REAUDIT_2_CONTENT_ADDRESS.txt"
    files.append(
        {
            "path": ca_path,
            "sha256": sha256_file(AUDIT / ca_path),
            "bytes": (AUDIT / ca_path).stat().st_size,
            "provenance": "reaudit_bundle_generated",
            "status": "generated",
            "audited_commit": COMMIT,
            "relation": "bundle_integrity",
        }
    )
    files.sort(key=lambda e: e["path"])

    archive_sha = sha256_file(ZIP)
    manifest = {
        "schema": "proteus.gate1_reaudit2_manifest.v0.1",
        "audited_commit": COMMIT,
        "bundle_root": str(AUDIT),
        "created_utc": utc_now(),
        "file_count": len(files),
        "content_address_sha256": content_address,
        "archive_zip": str(ZIP),
        "archive_zip_sha256": archive_sha,
        "first_audit_subject_commit": "94e3d60c9785789f1b7e812a865a325fcb23475f",
        "second_reaudit_subject_commit": "4b1f8d39a6731a994dc67c66aa8f5c059bda78d8",
        "files": files,
    }
    man_path = AUDIT / "GATE1_REAUDIT_2_MANIFEST.json"
    man_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    man_sha = sha256_file(man_path)

    # Copy freeze/manifest summaries into origin evidence for later recording
    EP.mkdir(parents=True, exist_ok=True)
    shutil.copy(man_path, EP / "GATE1_REAUDIT_2_MANIFEST.json")
    shutil.copy(AUDIT / "REAUDIT_2_FREEZE.json", EP / "GATE1_REAUDIT_2_FREEZE.json")
    (EP / "GATE1_REAUDIT_2_CONTENT_ADDRESS.txt").write_text(content_address + "\n", encoding="utf-8")
    (EP / "GATE1_REAUDIT_2_ARCHIVE_SHA256.txt").write_text(archive_sha + "\n", encoding="utf-8")
    (EP / "GATE1_REAUDIT_2_MANIFEST_SHA256.txt").write_text(man_sha + "\n", encoding="utf-8")

    summary = {
        "audited_commit": COMMIT,
        "bundle": str(AUDIT),
        "file_count": len(files),
        "content_address_sha256": content_address,
        "archive_zip_sha256": archive_sha,
        "manifest_sha256": man_sha,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

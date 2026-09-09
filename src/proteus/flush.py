from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .paths import observatory_local, proteus_home, spool_path
from .events import day_stamp


DRIVE_OBSERVATORY_ID = "1Cg0X2__jRf-LtMstPfLTDTPTKK33-bhx"


def flush() -> dict:
    day = day_stamp()
    src = spool_path(day)
    dest_dir = observatory_local() / "10_CURSOR" / day
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = None
    if src.exists():
        copied = dest_dir / src.name
        shutil.copy2(src, copied)
    status = {
        "flushed_at": datetime.now(timezone.utc).isoformat(),
        "local_spool": str(src),
        "local_observatory": str(copied) if copied else None,
        "drive_folder_id": DRIVE_OBSERVATORY_ID,
        "drive_sync": "FAILED_TRANSPORT",
        "reason": (
            "Google Drive Desktop My Drive is empty/not mirrored; Drive MCP not connected. "
            "Local observatory is the durable fallback. Do not invent cloud writes."
        ),
    }
    (observatory_local() / "90_SUMMARIES_AND_ANALYSIS" / "last_flush.json").parent.mkdir(
        parents=True, exist_ok=True
    )
    (observatory_local() / "90_SUMMARIES_AND_ANALYSIS" / "last_flush.json").write_text(
        json.dumps(status, indent=2), encoding="utf-8"
    )
    marker = proteus_home() / "observatory" / "DRIVE_SYNC_BLOCKED.md"
    marker.write_text(
        "# Drive Runtime Observatory flush blocked\n\n"
        f"Target folder ID: `{DRIVE_OBSERVATORY_ID}`\n\n"
        f"{status['reason']}\n",
        encoding="utf-8",
    )
    return status


if __name__ == "__main__":
    print(json.dumps(flush(), indent=2))

import hashlib
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_reentry_ping_reports_non_empty_frontier() -> None:
    frontier_path = PROJECT_ROOT / "state" / "FRONTIER.md"
    frontier = frontier_path.read_text(encoding="utf-8").strip()
    result = subprocess.run(
        [sys.executable, "tools/reentry_ping.py"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert frontier
    assert "frontier:" in result.stdout

    receipt = json.loads(
        (PROJECT_ROOT / "evidence" / "CYCLE2_PING_RECEIPT.json").read_text(encoding="utf-8")
    )
    assert receipt == {
        "frontier_sha16": hashlib.sha256(
            frontier_path.read_text(encoding="utf-8-sig").encode("utf-8")
        ).hexdigest()[:16],
        "current_nonempty": True,
        "cycle": "2",
    }

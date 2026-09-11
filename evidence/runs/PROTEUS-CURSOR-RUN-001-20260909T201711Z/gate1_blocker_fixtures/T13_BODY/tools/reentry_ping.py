"""Print a compact reentry summary and persist its cycle-2 receipt."""

import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def first_content_line(path: Path) -> str:
    """Return the first non-heading, non-empty line in a Markdown file."""
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        content = line.strip()
        if content and not content.startswith("#"):
            return content
    return "(no content)"


def write_cycle2_receipt(frontier_path: Path, current: str) -> None:
    """Record the continuity inputs observed by this ping."""
    frontier_text = frontier_path.read_text(encoding="utf-8-sig")
    receipt = {
        "frontier_sha16": hashlib.sha256(frontier_text.encode("utf-8")).hexdigest()[:16],
        "current_nonempty": current != "(no content)",
        "cycle": "2",
    }
    receipt_path = PROJECT_ROOT / "evidence" / "CYCLE2_PING_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    current = first_content_line(PROJECT_ROOT / "state" / "CURRENT.md")
    frontier_path = PROJECT_ROOT / "state" / "FRONTIER.md"
    frontier = first_content_line(frontier_path)
    write_cycle2_receipt(frontier_path, current)
    print(f"reentry ping | current: {current} | frontier: {frontier}")


if __name__ == "__main__":
    main()

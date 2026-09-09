"""Write a checkpoint/handoff from durable project files."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--done", default="")
    p.add_argument("--next", required=True)
    p.add_argument("--unresolved", default="")
    args = p.parse_args()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = ROOT / "evidence" / "checkpoints" / f"CHECKPOINT-{ts}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    current = (ROOT / "CURRENT.md").read_text(encoding="utf-8") if (ROOT / "CURRENT.md").exists() else ""
    body = f"""# CHECKPOINT {ts}

DONE:
{args.done}

NEXT:
{args.next}

UNRESOLVED:
{args.unresolved}

CURRENT.md snapshot:
---
{current}
"""
    dest.write_text(body, encoding="utf-8")
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

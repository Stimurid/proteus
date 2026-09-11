"""List files under data/ and write a short inventory summary."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "out"
SUMMARY_PATH = OUT_DIR / "inventory_summary.txt"


def list_data_entries(data_dir: Path = DATA_DIR) -> list[tuple[str, int]]:
    """Return sorted (name, size_bytes) for non-directory files under data_dir."""
    if not data_dir.is_dir():
        return []
    entries: list[tuple[str, int]] = []
    for path in data_dir.iterdir():
        if path.is_file():
            entries.append((path.name, path.stat().st_size))
    return sorted(entries, key=lambda item: item[0])


def list_data_files(data_dir: Path = DATA_DIR) -> list[str]:
    """Return sorted names of non-directory files directly under data_dir."""
    return [name for name, _ in list_data_entries(data_dir)]


def build_summary(entries: list[tuple[str, int]]) -> str:
    """Build a short human-readable inventory summary with per-file sizes."""
    if not entries:
        return "Inventory: no files found under data/.\n"
    total = sum(size for _, size in entries)
    lines = [
        "Inventory summary",
        f"Files under data/: {len(entries)}",
        f"Total bytes: {total}",
        "",
    ]
    for name, size in entries:
        lines.append(f"- {name} ({size} bytes)")
    lines.append("")
    return "\n".join(lines)


def write_summary(
    data_dir: Path = DATA_DIR,
    summary_path: Path = SUMMARY_PATH,
) -> Path:
    """List data files and write the summary; create out/ if needed."""
    entries = list_data_entries(data_dir)
    text = build_summary(entries)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(text, encoding="utf-8")
    return summary_path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()

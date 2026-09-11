"""Minimal tests for the inventory helper."""

from pathlib import Path

from tools.inventory import build_summary, write_summary

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "out"
SUMMARY_PATH = OUT_DIR / "inventory_summary.txt"


def test_summary_mentions_seeded_data_files(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    seeded = ["alpha.txt", "beta.txt"]
    for name in seeded:
        (data / name).write_text(f"{name} sample\n", encoding="utf-8")

    out = tmp_path / "out" / "inventory_summary.txt"
    write_summary(data_dir=data, summary_path=out)

    text = out.read_text(encoding="utf-8")
    for name in seeded:
        assert name in text


def test_summary_includes_sizes_and_total(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "a.txt").write_bytes(b"aaa")
    (data / "b.txt").write_bytes(b"bbbb")

    out = tmp_path / "out" / "inventory_summary.txt"
    write_summary(data_dir=data, summary_path=out)
    text = out.read_text(encoding="utf-8")

    assert "a.txt (3 bytes)" in text
    assert "b.txt (4 bytes)" in text
    assert "Total bytes: 7" in text


def test_build_summary_empty() -> None:
    assert "no files found" in build_summary([])


def test_project_data_files_appear_in_summary() -> None:
    """Assert summary mentions each seeded file under the project data/."""
    seeded = sorted(p.name for p in DATA_DIR.iterdir() if p.is_file())
    assert seeded, "expected seeded files under data/"

    write_summary(data_dir=DATA_DIR, summary_path=SUMMARY_PATH)
    text = SUMMARY_PATH.read_text(encoding="utf-8")
    for name in seeded:
        assert name in text
    assert "Total bytes:" in text

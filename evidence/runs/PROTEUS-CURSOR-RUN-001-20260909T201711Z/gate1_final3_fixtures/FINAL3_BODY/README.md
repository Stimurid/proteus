# Inventory Helper

Small local tool project. Goal: list files under `data/` and emit a short summary.
Keep the implementation simple and testable.

Usage: from the project root, run `python -m tools.inventory` (or `python tools/inventory.py`) to list non-recursive files under `data/` and write a short human-readable summary (names, per-file byte sizes, and total bytes) to `out/inventory_summary.txt` (the `out/` directory is created if needed). Install test deps with `pip install -r requirements.txt`, then run `pytest`.

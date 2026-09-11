"""Prepare FINAL3_BODY disposable project + activate Proteus (Cursor path)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

EP = Path(r"C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z")
BODY = EP / "gate1_final3_fixtures" / "FINAL3_BODY"
SRC = Path(r"C:\projects\Proteus")


def main() -> None:
    if BODY.exists():
        import shutil

        shutil.rmtree(BODY)
    BODY.mkdir(parents=True)
    (BODY / "data").mkdir()
    (BODY / "data" / "alpha.txt").write_text("alpha sample\n", encoding="utf-8")
    (BODY / "data" / "beta.txt").write_text("beta sample\n", encoding="utf-8")
    (BODY / "README.md").write_text(
        "# Inventory Helper\n\n"
        "Small local tool project. Goal: list files under `data/` and emit a short summary.\n"
        "Keep the implementation simple and testable.\n",
        encoding="utf-8",
    )
    (BODY / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=BODY, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=BODY, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "seed inventory helper"],
        cwd=BODY,
        check=True,
        capture_output=True,
    )

    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    env["PYTHONPATH"] = str(SRC / "src")
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "proteus.activate",
            "--project",
            str(BODY),
            "--run-id",
            "PROTEUS-CURSOR-RUN-001-20260909T201711Z",
        ],
        cwd=SRC,
        env=env,
        capture_output=True,
        text=True,
    )
    print(r.stdout)
    print(r.stderr)
    if r.returncode != 0:
        raise SystemExit(r.returncode)
    act = json.loads((BODY / ".proteus" / "activation.json").read_text(encoding="utf-8"))
    print("ACTIVATED", act.get("activation_id"))
    print("BODY", BODY)


if __name__ == "__main__":
    main()

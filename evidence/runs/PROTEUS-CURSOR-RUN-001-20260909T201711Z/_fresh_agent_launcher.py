#!/usr/bin/env python3
"""Origin-side launcher for an independent Cursor Agent CLI session.

Reads IDE cursorAuth/accessToken into CURSOR_AUTH_TOKEN for this child only.
Does not print secrets. Does not pass origin conversation content.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_ide_access_token() -> str:
    db = Path(os.environ["APPDATA"]) / "Cursor" / "User" / "globalStorage" / "state.vscdb"
    con = sqlite3.connect(str(db))
    try:
        row = con.execute(
            "select value from ItemTable where key=?",
            ("cursorAuth/accessToken",),
        ).fetchone()
    finally:
        con.close()
    if not row or not row[0]:
        raise SystemExit("IDE cursorAuth/accessToken missing")
    value = row[0]
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    return value


def scrub(text: str) -> str:
    text = re.sub(
        r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}",
        "<JWT_REDACTED>",
        text,
    )
    text = re.sub(r"key_[A-Za-z0-9]{8,}", "<KEY_REDACTED>", text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--prompt", default=None, help="prompt text (avoid for long multiline)")
    parser.add_argument(
        "--prompt-file",
        default=None,
        help="read prompt from UTF-8 file (preferred for long prompts)",
    )
    parser.add_argument("--out", required=True, help="stdout capture path")
    parser.add_argument("--err", required=True, help="stderr capture path")
    parser.add_argument("--meta", required=True, help="json metadata path")
    parser.add_argument("--timeout-sec", type=int, default=0, help="0 = no timeout")
    parser.add_argument(
        "--force",
        action="store_true",
        help="pass --force to allow commands unless denied",
    )
    args = parser.parse_args()
    if bool(args.prompt) == bool(args.prompt_file):
        raise SystemExit("Provide exactly one of --prompt or --prompt-file")
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    else:
        prompt = args.prompt

    localapp = Path(os.environ["LOCALAPPDATA"])
    versions_root = localapp / "cursor-agent" / "versions"
    version_dirs = sorted(
        [p for p in versions_root.iterdir() if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )
    version_dir = next((p for p in version_dirs if (p / "node.exe").is_file()), None)
    if version_dir is None:
        raise SystemExit(f"No Agent CLI version with node.exe under {versions_root}")
    node = version_dir / "node.exe"
    index = version_dir / "index.js"
    if not index.is_file():
        raise SystemExit(f"Agent CLI index.js missing under {version_dir}")

    token = load_ide_access_token()
    env = os.environ.copy()
    env["CURSOR_AUTH_TOKEN"] = token
    # Avoid accidental resume semantics from ambient shell state.
    for k in ("CURSOR_CONVERSATION_ID", "CURSOR_AGENT_PERSIST_SESSION"):
        env.pop(k, None)

    cmd = [
        str(node),
        str(index),
        "-p",
        "--output-format",
        "text",
        "--trust",
        "--workspace",
        args.workspace,
    ]
    if args.force:
        cmd.append("--force")
    cmd.append(prompt)

    out_path = Path(args.out)
    err_path = Path(args.err)
    meta_path = Path(args.meta)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    started = utc_now()
    t0 = time.time()
    with out_path.open("w", encoding="utf-8", errors="replace") as out_f, err_path.open(
        "w", encoding="utf-8", errors="replace"
    ) as err_f:
        proc = subprocess.Popen(
            cmd,
            cwd=args.workspace,
            env=env,
            stdout=out_f,
            stderr=err_f,
            stdin=subprocess.DEVNULL,
        )
        try:
            if args.timeout_sec and args.timeout_sec > 0:
                exit_code = proc.wait(timeout=args.timeout_sec)
                timed_out = False
            else:
                exit_code = proc.wait()
                timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            try:
                exit_code = proc.wait(timeout=10)
            except Exception:
                exit_code = -9

    ended = utc_now()
    raw_out = out_path.read_text(encoding="utf-8", errors="replace")
    raw_err = err_path.read_text(encoding="utf-8", errors="replace")
    # Rewrite captures scrubbed so evidence never stores leaked JWTs.
    out_path.write_text(scrub(raw_out), encoding="utf-8")
    err_path.write_text(scrub(raw_err), encoding="utf-8")

    meta = {
        "started_utc": started,
        "ended_utc": ended,
        "elapsed_sec": round(time.time() - t0, 3),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "pid": proc.pid,
        "node": str(node),
        "index": str(index),
        "workspace": args.workspace,
        "argv_without_prompt": cmd[:-1],
        "prompt_len": len(prompt),
        "prompt_sha256": __import__("hashlib").sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt_sha256_prefix": __import__("hashlib")
        .sha256(prompt.encode("utf-8"))
        .hexdigest()[:16],
        "prompt_source": str(args.prompt_file) if args.prompt_file else "argv",
        "used_continue": False,
        "used_resume": False,
        "auth": "CURSOR_AUTH_TOKEN from IDE cursorAuth/accessToken (value not recorded)",
        "stdout_bytes": out_path.stat().st_size,
        "stderr_bytes": err_path.stat().st_size,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": exit_code == 0 and not timed_out, **meta}, indent=2))
    return 0 if exit_code == 0 and not timed_out else 1


if __name__ == "__main__":
    sys.exit(main())

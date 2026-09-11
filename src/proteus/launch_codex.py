#!/usr/bin/env python3
"""Origin-side launcher for an independent Codex non-interactive session.

Does not resume/fork. Does not print auth tokens. Prefer --prompt-file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def scrub(text: str) -> str:
    text = re.sub(
        r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}",
        "<JWT_REDACTED>",
        text,
    )
    text = re.sub(
        r"(sk-|key_)[A-Za-z0-9_\-]{8,}",
        "<KEY_REDACTED>",
        text,
        flags=re.IGNORECASE,
    )
    return text


def find_codex() -> Path:
    env = os.environ.get("CODEX_CLI")
    if env and Path(env).is_file():
        return Path(env)
    local_bin = Path(os.environ.get("LOCALAPPDATA", "")) / "OpenAI" / "Codex" / "bin"
    # Prefer versioned subdirectory CLIs when newer than the top-level shim.
    candidates: list[Path] = []
    if local_bin.is_dir():
        for p in local_bin.iterdir():
            if p.is_dir():
                exe = p / "codex.exe"
                if exe.is_file():
                    candidates.append(exe)
        top = local_bin / "codex.exe"
        if top.is_file():
            candidates.append(top)
    which = None
    try:
        import shutil

        which = shutil.which("codex")
    except Exception:
        which = None
    if which:
        candidates.append(Path(which))

    def ver_key(path: Path) -> tuple:
        try:
            out = subprocess.check_output([str(path), "--version"], text=True, errors="replace", timeout=20)
        except Exception:
            return (0, 0, 0, str(path))
        # e.g. "codex-cli 0.153.4" or "codex-cli 0.130.0-alpha.5"
        import re

        m = re.search(r"(\d+)\.(\d+)\.(\d+)", out)
        if not m:
            return (0, 0, 0, str(path))
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)), str(path))

    if not candidates:
        raise SystemExit("codex executable not found; set CODEX_CLI")
    best = max(candidates, key=ver_key)
    return best


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--prompt-file", default=None)
    parser.add_argument("--out", required=True)
    parser.add_argument("--err", required=True)
    parser.add_argument("--meta", required=True)
    parser.add_argument("--last-message", required=True, help="codex -o last message path")
    parser.add_argument("--timeout-sec", type=int, default=0)
    parser.add_argument("--sandbox", default="danger-full-access")
    parser.add_argument("--model", default=None, help="optional -m model override")
    parser.add_argument("--ephemeral", action="store_true", default=True)
    parser.add_argument("--no-ephemeral", action="store_true")
    parser.add_argument("--add-dir", action="append", default=[])
    args = parser.parse_args()
    if bool(args.prompt) == bool(args.prompt_file):
        raise SystemExit("Provide exactly one of --prompt or --prompt-file")
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    else:
        prompt = args.prompt

    codex = find_codex()
    version = subprocess.check_output([str(codex), "--version"], text=True, errors="replace").strip()

    ephemeral = not args.no_ephemeral
    cmd = [
        str(codex),
        "exec",
        "-C",
        str(Path(args.workspace).resolve()),
        "--skip-git-repo-check",
        "-s",
        args.sandbox,
        "--dangerously-bypass-approvals-and-sandbox",
        "-c",
        "shell_environment_policy.inherit=all",
        "-o",
        str(Path(args.last_message).resolve()),
    ]
    if ephemeral:
        cmd.append("--ephemeral")
    if args.model:
        cmd.extend(["-m", args.model])
    for d in args.add_dir:
        cmd.extend(["--add-dir", d])
    # Prompt via stdin so multiline / UTF-8 is reliable; also pass `-` explicitly.
    cmd.append("-")

    env = os.environ.copy()
    # Independence: do not carry resume session ids if any ambient vars exist.
    for k in list(env):
        if "CODEX_SESSION" in k.upper() or k.upper().endswith("_RESUME"):
            env.pop(k, None)

    out_path = Path(args.out)
    err_path = Path(args.err)
    meta_path = Path(args.meta)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    started = utc_now()
    t0 = time.time()
    proc = subprocess.Popen(
        cmd,
        cwd=str(Path(args.workspace).resolve()),
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = proc.communicate(
            input=prompt.encode("utf-8"),
            timeout=args.timeout_sec or None,
        )
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout_b, stderr_b = proc.communicate()
        timed_out = True
    else:
        timed_out = False
    elapsed = time.time() - t0
    stdout = scrub(stdout_b.decode("utf-8", errors="replace"))
    stderr = scrub(stderr_b.decode("utf-8", errors="replace"))
    out_path.write_text(stdout, encoding="utf-8")
    err_path.write_text(stderr, encoding="utf-8")

    meta = {
        "schema": "proteus.codex_launch.v0.1",
        "started_utc": started,
        "finished_utc": utc_now(),
        "elapsed_sec": elapsed,
        "timed_out": timed_out,
        "exit_code": proc.returncode,
        "pid": proc.pid,
        "codex_path": str(codex),
        "codex_version": version,
        "workspace": str(Path(args.workspace).resolve()),
        "invocation": cmd[:-1] + ["<stdin-prompt>"],
        "used_resume": False,
        "used_fork": False,
        "used_continue": False,
        "ephemeral": ephemeral,
        "sandbox": args.sandbox,
        "prompt_sha256": prompt_hash,
        "prompt_char_count": len(prompt),
        "stdout_path": str(out_path),
        "stderr_path": str(err_path),
        "last_message_path": str(Path(args.last_message).resolve()),
        "env_keys_set_for_world": sorted(
            k
            for k in ("AIYE_HOME", "PROTEUS_WORLD_ROOT", "PYTHONPATH", "PROTEUS_SOURCE_ROOT")
            if env.get(k)
        ),
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"exit_code": proc.returncode, "meta": str(meta_path), "prompt_sha256": prompt_hash}, indent=2))
    return int(proc.returncode or 0)


if __name__ == "__main__":
    raise SystemExit(main())

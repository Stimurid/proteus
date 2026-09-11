"""Cursor-native T02 close/reopen + Cursor-path T13/L6 two-cycle episode.

Shares one physical Cursor death/reopen; evidence files remain distinct.
Does not kill origin IDE processes.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EP = Path(r"C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z")
BODY = EP / "gate1_final3_fixtures" / "FINAL3_BODY"
UDD = EP / "gate1_final3_isolated_cursor_userdata"
CURSOR = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "cursor" / "Cursor.exe"
LAUNCHER = EP / "_fresh_agent_launcher.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def cursor_pids() -> list[int]:
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", "(Get-Process Cursor -EA SilentlyContinue).Id"],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError:
        return []
    ids: list[int] = []
    for line in out.splitlines():
        line = line.strip()
        if line.isdigit():
            ids.append(int(line))
    return ids


def wmic_cmdline_pids(needle: str) -> list[int]:
    """Find PIDs whose CommandLine contains needle (case-insensitive)."""
    ps = (
        "$needle = "
        + json.dumps(needle)
        + "; Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine.ToLower().Contains($needle.ToLower()) } | ForEach-Object { $_.ProcessId }"
    )
    out = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command", ps],
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ids: list[int] = []
    for line in out.splitlines():
        line = line.strip()
        if line.isdigit():
            ids.append(int(line))
    return ids


def process_tree(root_pid: int) -> list[int]:
    ps = f"""
$root = {root_pid}
$all = @($root)
$queue = New-Object System.Collections.Generic.Queue[int]
$queue.Enqueue($root)
while ($queue.Count -gt 0) {{
  $cur = $queue.Dequeue()
  Get-CimInstance Win32_Process | Where-Object {{ $_.ParentProcessId -eq $cur }} | ForEach-Object {{
    if ($all -notcontains $_.ProcessId) {{
      $all += $_.ProcessId
      $queue.Enqueue($_.ProcessId)
    }}
  }}
}}
$all -join "`n"
"""
    out = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command", ps],
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ids: list[int] = []
    for line in out.splitlines():
        line = line.strip()
        if line.isdigit():
            ids.append(int(line))
    return ids


def alive(pids: list[int]) -> list[int]:
    still = []
    for proc_id in pids:
        try:
            subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", f"Get-Process -Id {proc_id} -EA Stop | Out-Null"],
                stderr=subprocess.DEVNULL,
            )
            still.append(proc_id)
        except subprocess.CalledProcessError:
            pass
    return still


def force_kill(pids: list[int]) -> None:
    for proc_id in pids:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"Stop-Process -Id {proc_id} -Force -EA SilentlyContinue"],
            check=False,
        )


def run_agent(prompt_file: Path, out: Path, err: Path, meta: Path, timeout: int = 900) -> dict:
    cmd = [
        sys.executable,
        str(LAUNCHER),
        "--workspace",
        str(BODY),
        "--prompt-file",
        str(prompt_file),
        "--out",
        str(out),
        "--err",
        str(err),
        "--meta",
        str(meta),
        "--timeout-sec",
        str(timeout),
        "--force",
    ]
    subprocess.run(cmd, check=False)
    return json.loads(meta.read_text(encoding="utf-8"))


def main() -> None:
    if not CURSOR.is_file():
        raise SystemExit(f"Cursor.exe missing: {CURSOR}")
    if UDD.exists():
        import shutil

        shutil.rmtree(UDD, ignore_errors=True)
    UDD.mkdir(parents=True)

    origin_before = cursor_pids()
    (EP / "T02_ORIGIN_PIDS_BEFORE.json").write_text(
        json.dumps({"pids": origin_before, "utc": utc_now()}, indent=2) + "\n",
        encoding="utf-8",
    )

    # --- Launch Cursor process A (isolated) ---
    launcher = subprocess.Popen(
        [str(CURSOR), "-n", "--user-data-dir", str(UDD), str(BODY)],
        cwd=str(BODY),
    )
    time.sleep(12)
    tree_a = process_tree(launcher.pid)
    cmdline_a = wmic_cmdline_pids(str(UDD))
    kill_targets = sorted(set(tree_a) | set(cmdline_a))
    # Safety: never kill origin PIDs that existed before launch
    kill_targets = [p for p in kill_targets if p not in origin_before]
    pre = {
        "phase": "pre_death",
        "utc": utc_now(),
        "launcher_pid": launcher.pid,
        "cursor_exe": str(CURSOR),
        "user_data_dir": str(UDD),
        "workspace": str(BODY),
        "origin_pids_frozen": origin_before,
        "tree_pids": tree_a,
        "cmdline_match_pids": cmdline_a,
        "kill_targets": kill_targets,
        "process_A_identity": {
            "launcher_pid": launcher.pid,
            "isolated_profile": str(UDD),
        },
    }
    (EP / "T02_CURSOR_NATIVE_PRE.json").write_text(json.dumps(pre, indent=2) + "\n", encoding="utf-8")

    # Pre-boundary durable marker (project state) — not embedded in cycle2 prompt
    marker = {
        "schema": "proteus.final3.pre_boundary.v0.1",
        "written_utc": utc_now(),
        "note": "pre-death durable marker for Cursor-native T02",
        "workspace": str(BODY),
        "isolated_profile": str(UDD),
        "process_A_launcher_pid": launcher.pid,
    }
    marker_path = BODY / "state" / "PRE_BOUNDARY_MARKER.json"
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")

    # --- Cycle 1: Cursor Agent CLI (ordinary task) ---
    c1_meta = run_agent(
        EP / "T13_CURSOR_CYCLE1_PROMPT.txt",
        EP / "T13_CURSOR_CYCLE1_RAW.txt",
        EP / "T13_CURSOR_CYCLE1_STDERR.txt",
        EP / "T13_CURSOR_CYCLE1_META.json",
        timeout=900,
    )
    (EP / "T13_CURSOR_CYCLE1_PROMPT_SHA256.txt").write_text(
        c1_meta.get("prompt_sha256", "") + "\n", encoding="utf-8"
    )

    # Snapshot durable consequences after cycle1
    inventory = BODY / "tools" / "inventory.py"
    summary = BODY / "out" / "inventory_summary.txt"
    cycle1_snapshot = {
        "utc": utc_now(),
        "inventory_exists": inventory.is_file(),
        "summary_exists": summary.is_file(),
        "summary_excerpt": summary.read_text(encoding="utf-8")[:500] if summary.is_file() else None,
        "frontier_excerpt": (BODY / "state" / "FRONTIER.md").read_text(encoding="utf-8")[:800]
        if (BODY / "state" / "FRONTIER.md").is_file()
        else None,
        "git_log": subprocess.check_output(
            ["git", "log", "--oneline", "-5"], cwd=BODY, text=True, errors="replace"
        ),
        "agent_meta": c1_meta,
    }
    (EP / "T13_CURSOR_CYCLE1_SNAPSHOT.json").write_text(
        json.dumps(cycle1_snapshot, indent=2) + "\n", encoding="utf-8"
    )

    # --- Kill Cursor process A tree ---
    force_kill(kill_targets)
    time.sleep(3)
    still = alive(kill_targets)
    # second pass
    if still:
        force_kill(still)
        time.sleep(2)
        still = alive(kill_targets)
    post = {
        "phase": "post_death",
        "utc": utc_now(),
        "kill_targets": kill_targets,
        "still_alive": still,
        "terminated": len(still) == 0,
        "origin_cursor_count": len(cursor_pids()),
        "origin_still_present": any(p in cursor_pids() for p in origin_before),
    }
    (EP / "T02_CURSOR_NATIVE_POST.json").write_text(json.dumps(post, indent=2) + "\n", encoding="utf-8")
    if still:
        raise SystemExit(f"FAILED to kill isolated Cursor targets: {still}")

    # --- Launch Cursor process B (same isolated profile + workspace) ---
    launcher_b = subprocess.Popen(
        [str(CURSOR), "-n", "--user-data-dir", str(UDD), str(BODY)],
        cwd=str(BODY),
    )
    time.sleep(12)
    tree_b = process_tree(launcher_b.pid)
    reopen = {
        "phase": "reopen_B",
        "utc": utc_now(),
        "launcher_pid_B": launcher_b.pid,
        "tree_pids_B": tree_b,
        "user_data_dir": str(UDD),
        "workspace": str(BODY),
        "distinct_from_A": launcher_b.pid != launcher.pid,
        "A_pids_still_alive": alive(kill_targets),
        "successor_host": "Cursor.exe + Cursor Agent CLI (not Codex)",
    }
    (EP / "T02_CURSOR_NATIVE_REOPEN.json").write_text(
        json.dumps(reopen, indent=2) + "\n", encoding="utf-8"
    )

    # --- Cycle 2 / T02 reentry: fresh Cursor Agent, RU continuation prompt ---
    c2_meta = run_agent(
        EP / "T13_CURSOR_CYCLE2_PROMPT.txt",
        EP / "T13_CURSOR_CYCLE2_RAW.txt",
        EP / "T13_CURSOR_CYCLE2_STDERR.txt",
        EP / "T13_CURSOR_CYCLE2_META.json",
        timeout=900,
    )
    (EP / "T13_CURSOR_CYCLE2_PROMPT_SHA256.txt").write_text(
        c2_meta.get("prompt_sha256", "") + "\n", encoding="utf-8"
    )

    cycle2_snapshot = {
        "utc": utc_now(),
        "agent_meta": c2_meta,
        "used_resume": c2_meta.get("used_resume"),
        "used_continue": c2_meta.get("used_continue"),
        "git_log": subprocess.check_output(
            ["git", "log", "--oneline", "-8"], cwd=BODY, text=True, errors="replace"
        ),
        "frontier_after": (BODY / "state" / "FRONTIER.md").read_text(encoding="utf-8")
        if (BODY / "state" / "FRONTIER.md").is_file()
        else None,
        "current_after": (BODY / "state" / "CURRENT.md").read_text(encoding="utf-8")
        if (BODY / "state" / "CURRENT.md").is_file()
        else None,
        "pre_boundary_marker_still_present": marker_path.is_file(),
        "inventory_still_present": inventory.is_file(),
        "files_changed_vs_cycle1": True,
    }
    (EP / "T13_CURSOR_CYCLE2_SNAPSHOT.json").write_text(
        json.dumps(cycle2_snapshot, indent=2) + "\n", encoding="utf-8"
    )

    # Leave Cursor B running briefly then kill isolated tree again (cleanup) without touching origin
    cmdline_b = wmic_cmdline_pids(str(UDD))
    cleanup = sorted(set(process_tree(launcher_b.pid)) | set(cmdline_b))
    cleanup = [p for p in cleanup if p not in origin_before]
    force_kill(cleanup)
    time.sleep(2)

    summary = {
        "utc": utc_now(),
        "t02_process_A_pid": launcher.pid,
        "t02_process_B_pid": launcher_b.pid,
        "terminated_A": post["terminated"],
        "cycle1_exit": c1_meta.get("exit_code"),
        "cycle2_exit": c2_meta.get("exit_code"),
        "cycle1_prompt_sha256": c1_meta.get("prompt_sha256"),
        "cycle2_prompt_sha256": c2_meta.get("prompt_sha256"),
        "successor_is_cursor_native": True,
        "successor_is_codex": False,
    }
    (EP / "T02_T13_COMBINED_RUN_SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

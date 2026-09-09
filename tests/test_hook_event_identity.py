from __future__ import annotations

import io
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteus.hook import main as hook_main  # noqa: E402
from proteus.hook_identity import resolve_event_identity  # noqa: E402
from proteus.install_cursor import hook_command, user_hook_entries  # noqa: E402
from proteus.t02_classify import counts_as_named_restart_fire  # noqa: E402


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _run_hook(home: Path, *, stdin: bytes, argv: list[str]) -> tuple[int, dict]:
    os.environ["PROTEUS_HOME"] = str(home)
    os.environ["PROTEUS_EVIDENCE_CLASS"] = "test"
    os.environ["CURSOR_PROJECT_DIR"] = str(ROOT)
    old_in, old_out = sys.stdin, sys.stdout
    sys.stdin = io.BytesIO(stdin)  # type: ignore[assignment]
    buf = io.StringIO()
    sys.stdout = buf
    try:
        rc = hook_main(argv=argv)
    finally:
        sys.stdin, sys.stdout = old_in, old_out
    spool_dir = home / "telemetry" / "cursor"
    events = []
    for p in spool_dir.rglob("events.jsonl"):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
    assert_true(len(events) == 1, "exactly one test spool event")
    return rc, events[0]


def test_empty_stdin_explicit_argv_names_event() -> None:
    with tempfile.TemporaryDirectory() as td:
        rc, ev = _run_hook(Path(td), stdin=b"", argv=["--hook-event", "sessionStart"])
        assert_true(rc == 0, "rc")
        assert_true(ev["hook_event_name"] == "sessionStart", "named from argv")
        assert_true(ev["event_name_source"] == "argv", "source argv")
        assert_true(ev["event_name_argv"] == "sessionStart", "argv recorded")
        assert_true(ev["event_name_stdin"] is None, "no stdin name")
        assert_true(ev.get("event_name_conflict") is not True, "no conflict")
        assert_true(ev["evidence_class"] == "test", "tagged test")
        assert_true(ev["stdin_byte_count"] == 0, "empty stdin counted")


def test_valid_stdin_still_names_event() -> None:
    payload = json.dumps({"hook_event_name": "workspaceOpen", "workspace_roots": ["C:\\x"]})
    with tempfile.TemporaryDirectory() as td:
        rc, ev = _run_hook(Path(td), stdin=payload.encode(), argv=[])
        assert_true(rc == 0, "rc")
        assert_true(ev["hook_event_name"] == "workspaceOpen", "named from stdin")
        assert_true(ev["event_name_source"] == "stdin", "source stdin")
        assert_true(ev["workspace_roots"] == ["C:\\x"], "payload fields kept")


def test_stdin_and_argv_agree() -> None:
    payload = json.dumps({"hook_event_name": "stop"})
    with tempfile.TemporaryDirectory() as td:
        _, ev = _run_hook(Path(td), stdin=payload.encode(), argv=["--hook-event", "stop"])
        assert_true(ev["hook_event_name"] == "stop", "agreed name")
        assert_true(ev["event_name_source"] == "stdin+argv", "both")


def test_contradictory_sources_are_visible() -> None:
    payload = json.dumps({"hook_event_name": "sessionStart"})
    ident = resolve_event_identity(json.loads(payload), ["--hook-event", "stop"])
    assert_true(ident["conflict"] is True, "identity conflict")
    assert_true(ident["hook_event_name"] == "unknown", "no silent winner")
    with tempfile.TemporaryDirectory() as td:
        _, ev = _run_hook(
            Path(td),
            stdin=payload.encode(),
            argv=["--hook-event", "stop"],
        )
        assert_true(ev["hook_event_name"] == "unknown", "event unnamed")
        assert_true(ev["event_name_source"] == "conflict", "source conflict")
        assert_true(ev["event_name_conflict"] is True, "flag")
        assert_true(ev["event_name_conflict_detail"]["stdin"] == "sessionStart", "stdin side")
        assert_true(ev["event_name_conflict_detail"]["argv"] == "stop", "argv side")
        assert_true(ev["status"] == "CONFLICT", "status")


def test_missing_identity_remains_unknown() -> None:
    with tempfile.TemporaryDirectory() as td:
        _, ev = _run_hook(Path(td), stdin=b"", argv=[])
        assert_true(ev["hook_event_name"] == "unknown", "unnamed")
        assert_true(ev["event_name_source"] == "none", "none")
        assert_true(ev["status"] == "UNKNOWN", "unknown status")


def test_old_simulated_rows_cannot_satisfy_t02() -> None:
    baseline_path = (
        ROOT
        / "evidence"
        / "runs"
        / "PROTEUS-CURSOR-RUN-001-20260909T201711Z"
        / "T02_BASELINE.json"
    )
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    simulated = {
        "event_id": "24660483-6ca8-4480-bf9f-ee424801e621",
        "hook_event_name": "workspaceOpen",
        "timestamp_utc": "2026-09-09T20:23:50.251285+00:00",
        "session_id": None,
    }
    later_unknown = {
        "event_id": "80a7c740-c9fc-448c-841c-f02e69d5de0c",
        "hook_event_name": "unknown",
        "timestamp_utc": "2026-09-09T21:58:05.702504+00:00",
        "event_name_source": "none",
    }
    test_named = {
        "event_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "hook_event_name": "sessionStart",
        "timestamp_utc": "2026-09-10T00:00:00+00:00",
        "event_name_source": "argv",
        "evidence_class": "test",
    }
    assert_true(not counts_as_named_restart_fire(simulated, baseline), "sim workspaceOpen")
    assert_true(not counts_as_named_restart_fire(later_unknown, baseline), "unknown post-cutoff")
    assert_true(not counts_as_named_restart_fire(test_named, baseline), "test class")
    sim_session = {
        "event_id": "26bd7500-6353-4cf3-b1a1-dead1b0c3584",
        "hook_event_name": "sessionStart",
        "timestamp_utc": "2026-09-09T20:23:32.551686+00:00",
        "session_id": "sim-001",
    }
    assert_true(not counts_as_named_restart_fire(sim_session, baseline), "sim-001")


def test_installer_registers_explicit_hook_event_argv() -> None:
    entries = user_hook_entries()
    for name in (
        "sessionStart",
        "workspaceOpen",
        "stop",
        "sessionEnd",
        "preCompact",
        "afterFileEdit",
        "postToolUseFailure",
    ):
        cmd = entries[name][0]["command"]
        assert_true(cmd == hook_command(name), "command helper")
        assert_true(f"--hook-event {name}" in cmd, name)


def main() -> None:
    test_empty_stdin_explicit_argv_names_event()
    test_valid_stdin_still_names_event()
    test_stdin_and_argv_agree()
    test_contradictory_sources_are_visible()
    test_missing_identity_remains_unknown()
    test_old_simulated_rows_cannot_satisfy_t02()
    test_installer_registers_explicit_hook_event_argv()
    print("PASS hook identity / T02 exclusion smokes")


if __name__ == "__main__":
    main()

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proteus.control import enqueue, maybe_followup  # noqa: E402
from proteus.events import load_project_orientation  # noqa: E402
from proteus.hook import main as hook_main  # noqa: E402
from proteus.redact import redact  # noqa: E402


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def test_redact_secrets() -> None:
    obj = {"api_key": "secret-value", "ok": "hello", "note": "sk-abcdefghijklmnopqrstuvwxyz"}
    out = redact(obj)
    assert_true(out["api_key"] == "[redacted]", "key redact")
    assert_true("[redacted]" in out["note"], "value redact")
    assert_true(out["ok"] == "hello", "keep")


def test_orientation_loads_state() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        state = root / "state"
        state.mkdir()
        (state / "CURRENT.md").write_text("frontier-test-marker", encoding="utf-8")
        (state / "FRONTIER.md").write_text("next", encoding="utf-8")
        (state / "DECISIONS.md").write_text("decision-marker", encoding="utf-8")
        text = load_project_orientation(root)
        assert_true("frontier-test-marker" in text, "current loaded")
        assert_true("decision-marker" in text, "decisions loaded after second cycle")


def test_stop_followup_from_queue() -> None:
    with tempfile.TemporaryDirectory() as td:
        os.environ["PROTEUS_HOME"] = str(Path(td) / "ph")
        path = enqueue("TEST_STEER", "Record ACK and do not start new product work.", mode="SAME_SESSION")
        assert_true(path.exists(), "queued")
        msg = maybe_followup({"status": "completed", "loop_count": 0})
        assert_true(bool(msg) and "PROTEUS EXTERNAL COMMAND" in msg, "followup")
        msg2 = maybe_followup({"status": "completed", "loop_count": 0})
        assert_true(msg2 is None, "no double claim")


def test_hook_session_start_stdout() -> None:
    with tempfile.TemporaryDirectory() as td:
        os.environ["PROTEUS_HOME"] = str(Path(td) / "ph")
        os.environ["CURSOR_PROJECT_DIR"] = str(ROOT)
        payload = json.dumps({"hook_event_name": "sessionStart", "session_id": "t1"})
        sys.stdin = io.BytesIO(payload.encode())  # type: ignore
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = hook_main()
        finally:
            sys.stdout = old
        assert_true(rc == 0, "hook rc")
        out = json.loads(buf.getvalue() or "{}")
        assert_true("additional_context" in out, "context")
        assert_true("CURRENT.md" in out["additional_context"], "current in context")


def main() -> None:
    test_redact_secrets()
    test_orientation_loads_state()
    test_stop_followup_from_queue()
    test_hook_session_start_stdout()
    print("PASS all unit smokes")


if __name__ == "__main__":
    main()

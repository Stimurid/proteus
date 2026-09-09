from __future__ import annotations

import re
from typing import Any

SECRET_KEY = re.compile(
    r"(password|secret|token|api[_-]?key|authorization|cookie|credential|private[_-]?key)",
    re.I,
)
SECRET_VALUE = re.compile(
    r"(?i)(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|Bearer\s+\S+)"
)


def redact(obj: Any, depth: int = 0) -> Any:
    if depth > 8:
        return "[truncated]"
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if SECRET_KEY.search(str(k)):
                out[k] = "[redacted]"
            else:
                out[k] = redact(v, depth + 1)
        return out
    if isinstance(obj, list):
        return [redact(x, depth + 1) for x in obj[:40]]
    if isinstance(obj, str):
        if len(obj) > 4000:
            obj = obj[:4000] + "…"
        return SECRET_VALUE.sub("[redacted]", obj)
    return obj

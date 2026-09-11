"""Protected secret broker — Windows Credential Manager provider.

Semantic memory stores only opaque secret:// URIs. Plaintext never enters
entity files, Drive carriers, evidence dumps, or CLI stdout by default.
"""

from __future__ import annotations

import ctypes
import json
import re
import sys
from ctypes import wintypes
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..paths import proteus_home

PROVIDER_ID = "windows_credential_manager"
TARGET_PREFIX = "Proteus/secret/"
REDACTED = "<REDACTED>"

CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2


class SecretBrokerError(RuntimeError):
    pass


class SecretNotFoundError(LookupError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _index_path() -> Path:
    d = proteus_home() / "secrets"
    d.mkdir(parents=True, exist_ok=True)
    return d / "index.json"


def _load_index() -> dict[str, Any]:
    path = _index_path()
    if not path.is_file():
        return {"schema": "proteus.secret_broker.index.v0.1", "refs": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_index(data: dict[str, Any]) -> None:
    path = _index_path()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def secret_uri_to_target(secret_uri: str) -> str:
    if not secret_uri.startswith("secret://"):
        raise ValueError("secret_uri must start with secret://")
    body = secret_uri[len("secret://") :].strip()
    if not body or any(c in body for c in " \\\n\r\t"):
        raise ValueError("invalid secret_uri body")
    return TARGET_PREFIX + body


def redact(text: str, secrets: list[str] | None = None) -> str:
    out = text
    for s in secrets or []:
        if s and s in out:
            out = out.replace(s, REDACTED)
    # never leave obvious password= patterns from accidental dumps
    out = re.sub(r"(password|passwd|secret|token)\s*[:=]\s*\S+", r"\1=<REDACTED>", out, flags=re.I)
    return out


@dataclass
class SecretMeta:
    secret_uri: str
    provider: str
    target: str
    label: str | None = None
    recorded_utc: str | None = None

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "secret_uri": self.secret_uri,
            "provider": self.provider,
            "target": self.target,
            "label": self.label,
            "recorded_utc": self.recorded_utc,
            "plaintext": None,
        }


class WindowsCredentialManagerBroker:
    """Narrow Windows CredWrite/CredRead/CredDelete wrapper."""

    provider = PROVIDER_ID

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise SecretBrokerError("WindowsCredentialManagerBroker requires win32")
        self._advapi = ctypes.WinDLL("advapi32", use_last_error=True)

    def put(self, secret_uri: str, plaintext: str, *, label: str | None = None) -> SecretMeta:
        if not plaintext:
            raise SecretBrokerError("empty plaintext refused")
        target = secret_uri_to_target(secret_uri)
        blob = plaintext.encode("utf-16-le")
        class CREDENTIAL(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD),
                ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME),
                ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_char)),
                ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD),
                ("Attributes", wintypes.LPVOID),
                ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR),
            ]

        cred = CREDENTIAL()
        cred.Flags = 0
        cred.Type = CRED_TYPE_GENERIC
        cred.TargetName = target
        cred.Comment = (label or "Proteus secret_ref")[:256]
        cred.CredentialBlobSize = len(blob)
        cred.CredentialBlob = ctypes.cast(
            ctypes.create_string_buffer(blob, len(blob)),
            ctypes.POINTER(ctypes.c_char),
        )
        cred.Persist = CRED_PERSIST_LOCAL_MACHINE
        cred.AttributeCount = 0
        cred.Attributes = None
        cred.TargetAlias = None
        cred.UserName = "proteus"
        ok = self._advapi.CredWriteW(ctypes.byref(cred), 0)
        if not ok:
            raise SecretBrokerError(f"CredWrite failed err={ctypes.get_last_error()}")
        meta = SecretMeta(
            secret_uri=secret_uri,
            provider=self.provider,
            target=target,
            label=label,
            recorded_utc=utc_now(),
        )
        idx = _load_index()
        idx.setdefault("refs", {})[secret_uri] = meta.to_public_dict()
        _save_index(idx)
        return meta

    def get(self, secret_uri: str) -> str:
        target = secret_uri_to_target(secret_uri)
        pcred = wintypes.LPVOID()
        ok = self._advapi.CredReadW(target, CRED_TYPE_GENERIC, 0, ctypes.byref(pcred))
        if not ok:
            err = ctypes.get_last_error()
            raise SecretNotFoundError(f"CredRead failed for {secret_uri} err={err}")
        try:
            class CREDENTIAL(ctypes.Structure):
                _fields_ = [
                    ("Flags", wintypes.DWORD),
                    ("Type", wintypes.DWORD),
                    ("TargetName", wintypes.LPWSTR),
                    ("Comment", wintypes.LPWSTR),
                    ("LastWritten", wintypes.FILETIME),
                    ("CredentialBlobSize", wintypes.DWORD),
                    ("CredentialBlob", ctypes.POINTER(ctypes.c_char)),
                    ("Persist", wintypes.DWORD),
                    ("AttributeCount", wintypes.DWORD),
                    ("Attributes", wintypes.LPVOID),
                    ("TargetAlias", wintypes.LPWSTR),
                    ("UserName", wintypes.LPWSTR),
                ]

            cred = ctypes.cast(pcred, ctypes.POINTER(CREDENTIAL)).contents
            size = cred.CredentialBlobSize
            raw = ctypes.string_at(cred.CredentialBlob, size)
            return raw.decode("utf-16-le")
        finally:
            self._advapi.CredFree(pcred)

    def delete(self, secret_uri: str) -> bool:
        target = secret_uri_to_target(secret_uri)
        ok = self._advapi.CredDeleteW(target, CRED_TYPE_GENERIC, 0)
        idx = _load_index()
        idx.get("refs", {}).pop(secret_uri, None)
        _save_index(idx)
        if not ok:
            err = ctypes.get_last_error()
            if err in (1168, 0x490):  # ERROR_NOT_FOUND
                return False
            raise SecretBrokerError(f"CredDelete failed err={err}")
        return True

    def meta(self, secret_uri: str) -> dict[str, Any] | None:
        return _load_index().get("refs", {}).get(secret_uri)


def get_broker() -> WindowsCredentialManagerBroker:
    return WindowsCredentialManagerBroker()


def put_secret(secret_uri: str, plaintext: str, *, label: str | None = None) -> dict[str, Any]:
    return get_broker().put(secret_uri, plaintext, label=label).to_public_dict()


def get_secret(secret_uri: str) -> str:
    """Explicit retrieval only. Callers must not print/log the return value."""
    return get_broker().get(secret_uri)


def delete_secret(secret_uri: str) -> bool:
    return get_broker().delete(secret_uri)


def describe_secret(secret_uri: str) -> dict[str, Any]:
    meta = get_broker().meta(secret_uri) or {
        "secret_uri": secret_uri,
        "provider": PROVIDER_ID,
        "plaintext": None,
        "status": "index_miss",
    }
    meta["plaintext"] = None
    return meta

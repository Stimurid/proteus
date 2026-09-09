"""Best-effort Cursor host process marker for restart discrimination.

Does not claim an OS-level quit. If the walker cannot name a Cursor ancestor,
fields stay UNKNOWN rather than inferred from hook timing.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any


def cursor_host_process_marker() -> dict[str, Any]:
    out: dict[str, Any] = {
        "hook_pid": os.getpid(),
        "parent_pid": os.getppid(),
        "cursor_pid": None,
        "cursor_image": None,
        "cursor_create_time_utc": None,
        "ancestor_images": [],
        "marker_status": "UNKNOWN",
        "marker_note": "Cursor host process not identified",
    }
    if os.name != "nt":
        out["marker_note"] = "non-Windows process walker not implemented"
        return out
    try:
        chain = _windows_ancestors(limit=12)
        out["ancestor_images"] = [
            {"pid": pid, "image": image} for pid, image, _ctime in chain
        ]
        for pid, image, ctime in chain:
            if image and "cursor" in image.lower():
                out["cursor_pid"] = pid
                out["cursor_image"] = image
                out["cursor_create_time_utc"] = ctime
                out["marker_status"] = "identified"
                out["marker_note"] = (
                    "best-effort Toolhelp ancestor whose image name contains 'cursor'; "
                    "a later change of cursor_create_time_utc is compatible with a process "
                    "restart but is not by itself a quit witness"
                )
                break
    except Exception as exc:
        out["marker_note"] = f"walker failed: {type(exc).__name__}"
        out["marker_status"] = "UNKNOWN"
    return out


def _filetime_to_utc_iso(dw_low: int, dw_high: int) -> str | None:
    ticks = (dw_high << 32) | dw_low
    if ticks == 0:
        return None
    # Windows FILETIME: 100ns since 1601-01-01 UTC
    unix = ticks / 10_000_000 - 11_644_473_600
    return datetime.fromtimestamp(unix, tz=timezone.utc).isoformat()


def _windows_ancestors(limit: int) -> list[tuple[int, str | None, str | None]]:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    TH32CS_SNAPPROCESS = 0x00000002
    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * 260),
        ]

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

    CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
    CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    Process32FirstW = kernel32.Process32FirstW
    Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    Process32FirstW.restype = wintypes.BOOL
    Process32NextW = kernel32.Process32NextW
    Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    Process32NextW.restype = wintypes.BOOL
    OpenProcess = kernel32.OpenProcess
    OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    OpenProcess.restype = wintypes.HANDLE
    GetProcessTimes = kernel32.GetProcessTimes
    GetProcessTimes.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME),
        ctypes.POINTER(FILETIME),
    ]
    GetProcessTimes.restype = wintypes.BOOL
    CloseHandle = kernel32.CloseHandle

    snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == INVALID_HANDLE_VALUE or not snap:
        return []
    parent_of: dict[int, int] = {}
    image_of: dict[int, str] = {}
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        ok = Process32FirstW(snap, ctypes.byref(entry))
        while ok:
            pid = int(entry.th32ProcessID)
            parent_of[pid] = int(entry.th32ParentProcessID)
            image_of[pid] = str(entry.szExeFile)
            ok = Process32NextW(snap, ctypes.byref(entry))
    finally:
        CloseHandle(snap)

    def create_time(pid: int) -> str | None:
        handle = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return None
        try:
            ctime = FILETIME()
            xtime = FILETIME()
            ktime = FILETIME()
            utime = FILETIME()
            if not GetProcessTimes(
                handle,
                ctypes.byref(ctime),
                ctypes.byref(xtime),
                ctypes.byref(ktime),
                ctypes.byref(utime),
            ):
                return None
            return _filetime_to_utc_iso(ctime.dwLowDateTime, ctime.dwHighDateTime)
        finally:
            CloseHandle(handle)

    chain: list[tuple[int, str | None, str | None]] = []
    pid = os.getpid()
    seen: set[int] = set()
    for _ in range(limit):
        if pid in seen or pid == 0:
            break
        seen.add(pid)
        chain.append((pid, image_of.get(pid), create_time(pid)))
        nxt = parent_of.get(pid)
        if nxt is None:
            break
        pid = nxt
    return chain

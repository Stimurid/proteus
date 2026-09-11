# T02_CURSOR_NATIVE_CLOSE_REOPEN

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
Contract: `50_GATE1_EVAL.md` T02 FULL RESTART — continuity after closing/reopening Cursor.  
Re-auditor gap: isolated Cursor kill + **Codex** successor CONTRADICTED Cursor-native reopen.

Historical: `T02_RESULT.md` / hooks T02 remain **PARTIAL** (unchanged).  
This file is **current satisfaction** evidence only.

## Causal shape

`Cursor process A (isolated --user-data-dir)`  
→ durable pre-boundary state (`state/PRE_BOUNDARY_MARKER.json` + Cycle1 inventory artifacts)  
→ force-terminate isolated tree (`T02_CURSOR_NATIVE_POST.json` terminated=true, still_alive=[])  
→ `Cursor process B` same profile/workspace (`T02_CURSOR_NATIVE_REOPEN.json`)  
→ Cursor Agent CLI reentry (not Codex; `used_resume=false`)  
→ recovered/used pre-death durable project state (Cycle2 raw + snapshots)

Shared physical boundary with Cursor-path T13/L6; observations below are T02-specific.

## Process identity

| Field | Value |
| --- | --- |
| Cursor.exe | `%LOCALAPPDATA%\Programs\cursor\Cursor.exe` |
| Isolated profile | `gate1_final3_isolated_cursor_userdata` |
| Workspace | `gate1_final3_fixtures/FINAL3_BODY` |
| Process A launcher PID | 16296 |
| Kill targets | see `T02_CURSOR_NATIVE_PRE.json` |
| A terminated | **true** (`T02_CURSOR_NATIVE_POST.json`) |
| Process B launcher PID | 4532 (distinct) |
| Origin IDE preserved | origin_still_present=true |
| Successor host | Cursor.exe + Cursor Agent CLI — **not Codex** |

Note: after B launch, PID `25680` appears in B’s tree while also having been an A kill-target number. Immediate post-kill `still_alive=[]`; this is Windows **PID reuse**, not A survival.

## Continuity vs discontinuity

- **Discontinuous:** OS process identity A≠B; no resume/continue on Agent sessions.
- **Continuous:** activated Proteus mount + Cycle1 durable inventory + pre-boundary marker available to B/Cycle2.

## Status

**T02 Cursor-native current satisfaction = PASS**

Historical T02 PARTIAL preserved.

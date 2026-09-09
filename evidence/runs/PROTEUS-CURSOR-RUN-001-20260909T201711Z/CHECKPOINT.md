# CHECKPOINT 2026-09-09T21:56Z

RUN_ID: PROTEUS-CURSOR-RUN-001-20260909T201711Z

## Done

- T01 CLEAN_REENTRY closed as PASS (externally witnessed). Prompt-only fresh chat; RUN-001 transcript not used. Contamination absence is not internally provable (`T01_CLEAN_REENTRY.md`).
- FRONTIER no longer asks for clean reentry.
- T02 prepared: `T02_PRE_RESTART.md`, `T02_BASELINE.json`, `T02_POST_RESTART_PROMPT.md`. T02 remains NOT_RUN.

## Changed

- `state/CURRENT.md`, `state/FRONTIER.md`, `state/UNRESOLVED.md`
- `RUN_RECEIPT.md` test matrix + CLEAN_REENTRY = PASS
- `CLEAN_REENTRY_PROMPT.md` marked CLOSED

## Decisions

None new. D-001 / D-002 unchanged.

## Unresolved

See `state/UNRESOLVED.md`. T02 hooks-after-restart still UNKNOWN. Drive transport still FAILED_TRANSPORT.

## Next frontier

T02: human quits/reopens Cursor; new chat runs `T02_POST_RESTART_PROMPT.md`. Do not claim T02 PASS before that.

## Tests

T01 PASS (external). T02 NOT_RUN. Unit smokes not re-run this checkpoint.

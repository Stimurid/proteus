# PRODUCT_ACTIVATION_CHILD_EPISODE

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: origin-side wrapper for an independent Agent CLI product-work session (Cursor project-mount activation)
When: 2026-09-10
Origin role: BUILDER-01 (launcher / evidence wrapper only). Child owns the product design/implementation.

## Separation of records

| Layer | Location | Rule |
| --- | --- | --- |
| CHILD_RAW_RESULT | `PRODUCT_ACTIVATION_CHILD_STDOUT.txt` | Verbatim final child response. Do not rewrite. |
| Child session meta | `PRODUCT_ACTIVATION_CHILD_META.json` | PID, argv, prompt hash, exit, timing |
| Child prompt | `PRODUCT_ACTIVATION_CHILD_PROMPT.txt` | Exact substantive prompt; sha256 `33d7651da571078d1999f3042080946abde3c821cc149363d4ab12736b59fd06` |
| Child product evidence | `PRODUCT_ACTIVATION.md` (+ fixtures, D-006, commit `0c64143`) | Written by the child inside the worktree |
| Origin interpretation | this file, after the raw block | Observable deltas only; no retrospective “cleaner” product answer |

## Session evidence (new, not resume)

| Field | Value |
| --- | --- |
| Attempt 1 | FAIL (launcher) — see `PRODUCT_ACTIVATION_CHILD_LAUNCH_ATTEMPT_1.md` |
| Attempt 2 | PASS — `--prompt-file`; node PID **27804** |
| Workspace | `C:\Projects\Proteus` |
| Flags | `-p --output-format text --trust --force` |
| continue/resume | false / false |
| Started (UTC) | `2026-09-10T16:29:10.245522+00:00` |
| Ended (UTC) | `2026-09-10T16:39:56.430441+00:00` |
| Elapsed | ~646 s |
| Exit | **0** |
| Stderr | empty |

Launcher technical repair between attempts: `_fresh_agent_launcher.py` gained `--prompt-file` (multiline argv delivery). Prompt text unchanged.

## Observable repository / test deltas (post-completion inspection)

- Implementation commit: `0c6414375b3abbff0c39f02c9349217e26f9a2ae` — *Add one-command Cursor project-mount activation for existing repos.*
- Command present: `python -m proteus.activate --project <path> [--dry-run] [--remove]`
- Modules: `src/proteus/activate.py`, `src/proteus/cli.py` subcommand, `hosts/cursor/templates/activate/**`, `tests/test_activate.py`
- Decision D-006 present in `state/DECISIONS.md`
- Child evidence: `PRODUCT_ACTIVATION.md`; fixtures under `activation_fixtures/`
- Origin re-check: `python -m pytest tests/test_activate.py -q` → **10 passed** (2026-09-10 post-child)
- Gate 1 / T01 / T02 / T02b / T03 / PROCESS_DEATH: not upgraded by this wrapper inspection

## Origin interpretation (thin)

The independent child completed the requested ordinary product task and committed a bounded Cursor project-mount activation path with coexistence policy D-006. This wrapper does not re-decide coexistence, template content, or product scope. Gate 1 remains NOT_YET. Spontaneous organ-behavior testing was not part of the child prompt and is not claimed here.

## CHILD_RAW_RESULT

See verbatim file `PRODUCT_ACTIVATION_CHILD_STDOUT.txt` (also reproduced in the human-facing final response for this episode).

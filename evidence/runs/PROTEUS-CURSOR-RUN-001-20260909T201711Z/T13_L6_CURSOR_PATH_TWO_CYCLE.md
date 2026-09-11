# T13_L6_CURSOR_PATH_TWO_CYCLE

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`  
Contracts: `50_GATE1_EVAL.md` T13 + L6.  
Re-auditor gap: prior episode Codex-led / prompt-directed; attribution to installed Cursor Proteus ambiguous.

Historical prior T13/L6 origin claim remains historical; this is **current Cursor-path** evidence.

## Setup

- Disposable project: `gate1_final3_fixtures/FINAL3_BODY`
- Activated via supported Cursor path: `python -m proteus.activate`
- Activation id: `PROTEUS-CURSOR-RUN-001-20260909T201711Z-ACT-20260911T214017Z`
- Surfaces present: `.proteus/ENTRY.md`, `AGENTS.md`, `state/*`, proteus-* rules/skills

## Cycle 1 (ordinary product work)

- Host: **Cursor Agent CLI** (Cursor-native; not Codex)
- Prompt: `T13_CURSOR_CYCLE1_PROMPT.txt` — inventory helper only; **no** cycle/L6/token/persistence coaching
- SHA-256: `53004c19b70e9dbed857abf898b0242cf8b9e3d4ad81ac4377d19e6da703db6a`
- Meta: `T13_CURSOR_CYCLE1_META.json` — used_resume=false, used_continue=false, exit 0, PID 28880
- Raw: `T13_CURSOR_CYCLE1_RAW.txt`
- Durable consequence: `tools/inventory.py`, tests, `out/inventory_summary.txt` (names only), commits `6d1a9a8`…

## Hard boundary

Isolated Cursor process A terminated; Process B reopened — see `T02_CURSOR_NATIVE_*` (shared physical episode; distinct artifacts).

## Cycle 2 (continuation without restatement)

- Host: **new Cursor Agent CLI** session after Cursor B reopen
- Prompt: `T13_CURSOR_CYCLE2_PROMPT.txt` (RU reentry/continue; does not describe Cycle1 work)
- SHA-256: `5682f67380a549efc2195b12f326eb081bdc2945d285069ccd3f9142a6b4816b`
- Meta: `T13_CURSOR_CYCLE2_META.json` — used_resume=false, used_continue=false, exit 0, PID 15800 (≠ Cycle1)
- Raw: `T13_CURSOR_CYCLE2_RAW.txt`

### What Cycle 2 recovered / did

- Entered via installed Proteus mount (activation id, ENTRY/state cited in raw)
- Reconstructed Cycle1 inventory helper from durable tree
- Extended Cycle1 consequence: summary now includes per-file/total **bytes** (`tools/inventory.py`); tests 4 passed
- Updated `state/CURRENT.md`, `state/FRONTIER.md`, local decision, checkpoint under project evidence

## Causal dependency (required)

`Cycle1 inventory module+summary → durable installed project state → Cursor process death → Cursor B + new Agent → Cycle2 recovers inventory and extends it with sizes`

Not: `prompt A says do X → prompt B says now do Y` (Cycle2 prompt does not mention inventory/sizes).

## Status

**T13 Cursor-path current = PASS**  
**L6 current = PASS** (installed capabilities participated in subsequent product-development change after hard boundary)

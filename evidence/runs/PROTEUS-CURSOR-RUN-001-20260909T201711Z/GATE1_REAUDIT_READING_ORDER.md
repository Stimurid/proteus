# Re-audit reading order

1. REAUDIT_FREEZE.json
2. OPEN_BOUNDARIES_FOR_REAUDIT.md
3. _BOOTSTRAP/BLIND_START/50_GATE1_EVAL.md
4. _BOOTSTRAP/BLIND_START/60_CURRENT_PROTEUS_STATUS.md
5. state/IDENTITY.md, CURRENT.md, FRONTIER.md, DECISIONS.md, UNRESOLVED.md
6. First audit: evidence/.../GATE1_INDEPENDENT_AUDIT.md + GATE1_AUDITOR_RAW_RESULT.txt
7. Full RUN_RECEIPT.md and earlier episode evidence (T01–T03, F01, handoff, activation, world, AW1000, F04–F06)
8. Post-first-audit closure artifacts (GATE1_BLOCKER_*, T04/T05/T09/T11/PROCESS_DEATH/T13/L4-L6) as **evidence to examine**, not as binding truth
9. Implementation under src/, hosts/, tests/ as needed to verify correspondence

Hard constraints:
- Do not use the live origin tree.
- Do not install/activate Proteus.
- Do not patch code or rewrite evidence.
- Do not assume blocker closure claims are correct; judge against Gate contracts.

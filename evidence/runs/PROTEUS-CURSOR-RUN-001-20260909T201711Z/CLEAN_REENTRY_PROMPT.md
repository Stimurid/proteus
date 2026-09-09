# CLEAN_REENTRY_PROMPT

Use in a **new** Cursor Agent chat on workspace `C:\Projects\Proteus`. Do not paste RUN-001 transcript.

```
You are BUILDER-01 in the Proteus Cursor incarnation. Do not wait for a pasted old chat.

1. Read AGENTS.md, then state/IDENTITY.md, state/CURRENT.md, state/FRONTIER.md, state/DECISIONS.md, state/UNRESOLVED.md.
2. Read evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T201711Z/RUN_RECEIPT.md.
3. Answer, citing file paths:
   - Who is acting?
   - What project/workspace is this?
   - What is the current frontier?
   - What is one last accepted decision and its provenance?
   - What is one explicit UNKNOWN?
   - What is test state (PASS/FAIL/NOT_RUN)?
   - What is the exact next step?
4. Do not invent operator-layer claims. If something is not in durable state, say UNKNOWN.
```

## Expected postconditions

- Names BUILDER-01 / Proteus / Cursor.
- Frontier mentions independent reentry and Drive observatory transport, not “design architecture from scratch”.
- UNKNOWN includes Agent CLI missing and/or Drive flush blocked and/or hooks not proven after full restart.
- Does not ask the user to paste the previous conversation.

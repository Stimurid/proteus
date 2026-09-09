PROTEUS — EXTERNAL CONTROL OF CURSOR v0.1

PURPOSE  
Provide reliable ways to start, continue and steer Cursor work from outside the visible IDE chat so Proteus can later be monitored/commanded from a cockpit, Google Drive command queue, another agent or automation.

1\. VERIFIED EXTERNAL SURFACES AS OF 2026-09-09  
A. Cursor Agent CLI  
Cursor supplies a native Agent CLI. It can run interactively or headless/non-interactively, accepts an explicit workspace path, supports the same rules system as the editor, reads .cursor/rules plus AGENTS.md and CLAUDE.md, and uses the same MCP configuration.

Useful capabilities include:  
\- agent \--workspace \<path\> ...  
\- non-interactive/print mode for scripts/CI;  
\- structured output formats;  
\- agent \--continue / agent resume for the most recent CLI conversation;  
\- agent \--resume \<thread-id\> and agent ls for CLI conversation history;  
\- worktree mode for isolated parallel runs.

B. ACP  
\`agent acp\` exposes Cursor Agent over stdio using JSON-RPC 2.0. A custom controller can initialize/authenticate, create or load a session, submit prompts, receive streaming session/update notifications and handle permission requests. This is the strongest candidate for a persistent local Proteus controller because it avoids UI automation.

C. Cursor hooks  
The \`stop\` hook can return \`followup\_message\`; Cursor automatically submits it as the next user message in that conversation. This supports “continue according to plan” loops. The hook receives a loop\_count; Cursor documents configurable loop limits.

D. Cloud Agents API  
Cursor Cloud Agents API v1 is public beta. It can programmatically create durable cloud agents, inspect agent/run status and send a follow-up run to an existing agent. This is direct REST control for cloud agents.

2\. IMPORTANT LIMITATION  
Do not assume that the public CLI can resume an arbitrary currently-open local IDE Composer conversation. The verified docs establish CLI session resume and IDE stop-hook continuation, but not a general REST endpoint for injecting an arbitrary prompt into any idle local editor thread.

Therefore Proteus must use the right control path for the right state rather than inventing one universal API.

3\. CONTROL MODES  
MODE 1 — SAME IDE CONVERSATION / STOP-BOUNDARY CONTINUATION  
At \`stop\`, the global/project hook checks whether a trusted command is queued for this conversation/RUN. If yes, it may return that instruction as \`followup\_message\`, continuing the same IDE conversation automatically.

Use for:  
\- “продолжай по плану”;  
\- retry/repair after bounded test failure;  
\- continue next pass;  
\- checkpoint then proceed;  
\- do not stop until listed postconditions are met.

Do not create endless unbounded loops by default. Record every injected follow-up as an external command event.

MODE 2 — LOCAL HEADLESS NEW/CLI RUN  
A controller invokes Cursor Agent CLI against a workspace:  
agent \--workspace \<project-path\> \-p "\<command\>" ...

Use when no suitable live IDE conversation exists or automation should operate independently of the GUI.

MODE 3 — PERSISTENT LOCAL ACP SESSION  
Proteus controller owns \`agent acp\`, maintains explicit session IDs and routes commands through JSON-RPC. This is the preferred route for a future reliable local command plane because the controller can observe streaming state and preserve its own mapping between project/run/session and external command IDs.

MODE 4 — CLOUD AGENT API  
For cloud-hosted Cursor agents, use the official Cloud Agents API to create the agent, poll/get run status and submit follow-up runs. Do not screen-scrape cursor.com for control when API access is available.

4\. DRIVE COMMAND QUEUE  
Canonical candidate queue:  
Proteus Runtime Observatory / 95\_COMMAND\_QUEUE  
Drive folder ID: 1QdEloB\_kt-xJVbedRuCadhIMnKAbh1rK

A command record should include:  
\- command\_id;  
\- created\_at;  
\- issuer \+ provenance;  
\- target\_host;  
\- target\_machine when relevant;  
\- target\_project/workspace;  
\- target RUN\_ID;  
\- target conversation/session/agent ID where known;  
\- requested action/instruction;  
\- mode preference: SAME\_SESSION / CLI / ACP / CLOUD\_API / AUTO;  
\- priority;  
\- expiry/deadline if relevant;  
\- safety/permission class;  
\- expected acknowledgement;  
\- status: QUEUED / CLAIMED / SENT / ACKNOWLEDGED / COMPLETED / FAILED / EXPIRED;  
\- result/receipt pointer.

5\. LOCAL CONTROLLER / POLLER  
A lightweight always-on process may:  
\- watch/sync the Drive command queue;  
\- read local active-run registry;  
\- decide which verified control channel is available;  
\- claim a command atomically enough to avoid duplicate execution;  
\- dispatch it;  
\- record acknowledgement and result;  
\- never expose API keys or secrets in Drive command records.

If Google Drive Desktop is present, the queue can initially be represented by files in a synced local folder. Otherwise an API adapter polls at a sensible interval.

6\. SAME-SESSION COMMAND INJECTION VIA STOP HOOK  
At stop:  
1\) identify RUN/conversation/workspace;  
2\) flush telemetry/current card;  
3\) inspect trusted local command cache/queue;  
4\) if exactly one valid SAME\_SESSION command targets this run and permissions allow it, mark CLAIMED;  
5\) return it as followup\_message;  
6\) log SENT;  
7\) next agent turn records ACKNOWLEDGED.

A default policy can also auto-continue on an internal condition such as “plan has unfinished accepted tasks and stop reason is completed”, but the first version should be conservative and visible in telemetry.

7\. PROTEUS COMMAND EXAMPLES  
\- CONTINUE: Continue from current frontier until next explicit checkpoint.  
\- EXECUTE\_NEXT: Execute the next accepted backlog item, verify, checkpoint.  
\- RUN\_TEST: Run named Gate/eval and record evidence only.  
\- CHECKPOINT: Save state and stop.  
\- MOUNT\_PROJECT: Mount specified project and produce reentry report.  
\- REPAIR: Address current failed postcondition, rerun test, rollback if still failing.  
\- PAUSE\_AFTER: Finish current bounded operation, checkpoint, do not start next item.  
\- STATUS\_ONLY: Analyze current local/run state without modifying source.

These are semantic command classes, not hard-coded keyword routing for agent cognition. The command payload may carry natural-language instruction and context.

8\. REMOTE MONITOR → STEER LOOP  
Runtime Observatory receives telemetry.  
A human/LLM monitor sees:  
project P / host Cursor / RUN R / stage TESTING / blocker X / last event Y.  
It may create a command in the queue:  
“Repair X according to existing plan; rerun tests A/B; if both pass continue to checkpoint, otherwise stop with evidence.”  
Local controller dispatches via same-session hook, CLI or ACP.  
Outcome returns to telemetry/receipt.

This makes Drive a provisional cross-agent control surface before a richer cockpit exists.

9\. SECURITY / AUTHORITY  
\- Commands require issuer provenance.  
\- No secret values in Drive queue.  
\- High-risk destructive commands cannot be silently auto-executed merely because a file appeared in the queue.  
\- User explicit commands outrank monitor suggestions.  
\- Expired or ambiguous target commands are not guessed into another run.  
\- Every dispatched command is logged with channel and target identifiers.

10\. FIRST CURSOR P0 ACCEPTANCE  
External-control P0 passes when:  
\- Cursor Agent CLI is installed/authenticated or an explicit documented blocker exists;  
\- Proteus can start a headless agent in a specified workspace;  
\- one controlled \`stop\`-hook follow-up can continue a bounded IDE run and is logged;  
\- command queue schema/current folder exists;  
\- a local controller can consume at least one test command and acknowledge it;  
\- no claim is made that an arbitrary idle editor chat can be resumed externally unless actual host testing proves a supported path.

11\. FUTURE  
Once Cursor control works, write adapters for Claude Code and Codex to the same command envelope while preserving their native capabilities. Then an upper controller can route work across bodies without UI-specific manual chat copy/paste.  

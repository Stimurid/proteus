PROTEUS — GLOBAL WORKLOG AND TELEMETRY v0.1

PURPOSE  
Make Cursor work observable across every project without manual chat copying. Proteus should continuously leave machine-readable work evidence locally and synchronize useful event streams/summaries into Google Drive so another agent or human can see who is working, where, with which model, on what project/run, what stage it is in, what changed, what is blocked and what should happen next.

1\. SCOPE  
This is a GLOBAL Cursor capability, not a per-project convenience. Once installed, it should activate regardless of which workspace Cursor opens. Project-local hooks may add richer project evidence, but base telemetry belongs at user/global scope.

2\. VERIFIED CURSOR SURFACES AVAILABLE AS OF 2026-09-09  
Cursor supports user-level hooks in \~/.cursor/hooks.json and project hooks in \<project\>/.cursor/hooks.json. Relevant events include workspaceOpen, sessionStart, sessionEnd, beforeSubmitPrompt, preToolUse/postToolUse/postToolUseFailure, before/after shell and MCP calls, beforeReadFile, afterFileEdit, preCompact, afterAgentResponse, afterAgentThought and stop.

Hook input exposes useful identifiers and environment including Cursor version, workspace roots, authenticated user email when available, conversation/session/generation/model metadata where applicable, and transcript\_path when transcripts are enabled. CURSOR\_PROJECT\_DIR, CURSOR\_VERSION and CURSOR\_TRANSCRIPT\_PATH are also exposed as environment variables where applicable.

These surfaces should be discovered/verified by the first run against the actual installed Cursor version before installation.

3\. TWO-LAYER LOGGING  
Do not make the agent loop depend on a network write for every event.

Layer A — LOCAL APPEND-ONLY EVENT STREAM  
Global hooks write compact JSONL events to a local Proteus telemetry spool, for example:  
%USERPROFILE%\\.proteus\\telemetry\\cursor\\YYYY-MM-DD\\...

Layer B — DRIVE COLLECTOR / FLUSH  
A collector periodically batches, enriches and syncs events to the Proteus Runtime Observatory in Google Drive. Flush also occurs on meaningful boundaries such as sessionEnd, preCompact, stop, error or explicit checkpoint where practical.

If Google Drive for Desktop provides a reliable synced local path, the collector may write directly to that synced tree. Otherwise use an authenticated Drive/API adapter. The exact transport is an implementation choice learned from the host.

4\. DRIVE DESTINATION  
Proteus Runtime Observatory:  
Drive folder ID: 1Cg0X2\_\_jRf-LtMstPfLTDTPTKK33-bhx

Subspaces:  
00\_ACTIVE\_RUNS — compact current status of active/recent runs.  
10\_CURSOR — Cursor raw/batched worklogs and receipts.  
20\_CLAUDE\_CODE — future Claude Code adapter logs.  
30\_CODEX — future Codex adapter logs.  
90\_SUMMARIES\_AND\_ANALYSIS — semantic rollups, cross-run analysis, project/host summaries.  
95\_COMMAND\_QUEUE — external steering commands and acknowledgements.

5\. EVENT MINIMUM  
Each event should carry when available:  
\- schema\_version;  
\- event\_id;  
\- timestamp UTC \+ local;  
\- host \= cursor;  
\- machine\_id pseudonymous/stable;  
\- cursor\_version;  
\- user identity only to the degree necessary for routing;  
\- workspace\_roots;  
\- project\_id/project\_name if resolved;  
\- RUN\_ID;  
\- conversation\_id/session\_id/generation\_id where exposed;  
\- model;  
\- hook\_event\_name;  
\- stage/status;  
\- tool/file/shell/MCP metadata appropriate to event;  
\- source revision / git branch / dirty state when useful;  
\- error/failure state;  
\- provenance pointer;  
\- transcript pointer when available, not necessarily transcript duplication.

6\. PRIVACY / SECRETS  
Never upload secret values, access tokens, credentials, cookies, private keys or raw environment dumps. Redact tool inputs/outputs before cloud sync when they may contain secrets. Prefer paths, hashes, counts, event types and bounded summaries over indiscriminate raw dumps.

7\. CHAT / TRANSCRIPT CAPTURE  
Goal: eliminate manual copying of Cursor chats.

If Cursor provides CURSOR\_TRANSCRIPT\_PATH / transcript\_path and transcripts are enabled, retain a durable pointer and, where permitted, periodically copy/export the transcript into the run evidence or Drive log after redaction. Do not rely exclusively on transcript availability; structured hook events and receipts must still make the run understandable.

If transcript format is internal/unstable, preserve raw source plus version metadata and produce a normalized derived summary instead of treating parsed structure as permanent canon.

8\. STAGE MODEL  
Two levels:

DETERMINISTIC STATUS — derived cheaply from events:  
WORKSPACE\_OPEN  
SESSION\_ACTIVE  
TOOL\_ACTIVE  
COMPACTION  
STOPPED  
COMPLETED  
ERROR  
ABORTED  
WAITING/IDLE where actually inferable.

SEMANTIC STAGE — periodically inferred by an LLM from a bounded recent window plus project frontier, e.g.:  
DISCOVERY / BASELINE / DESIGN / IMPLEMENTATION / TESTING / REPAIR / REENTRY\_TEST / PROJECT\_MOUNT / BLOCKED / COMPLETE-CANDIDATE.

Semantic stage is an analysis claim with timestamp/model/evidence window, not raw fact.

9\. ACTIVE RUN CARD  
For each active/recent run maintain a compact generated card:  
\- host;  
\- project/workspace;  
\- RUN\_ID;  
\- conversation/session ID;  
\- model;  
\- started/last event;  
\- current deterministic status;  
\- semantic stage \+ confidence;  
\- current objective;  
\- last meaningful action;  
\- files/branch changed summary;  
\- test state;  
\- blocker;  
\- next expected action;  
\- command queue state.

This is the primary monitoring surface for humans/other agents; raw event logs remain evidence.

10\. PERIODIC LLM ANALYSIS  
A low-frequency semantic analyzer can consume only deltas since its last checkpoint and generate:  
\- run status summary;  
\- stage classification;  
\- likely blocker;  
\- drift from plan;  
\- important decisions/corrections;  
\- whether the agent stopped prematurely;  
\- whether external steering is warranted;  
\- cross-host/project duplicate work or conflicts.

The analyzer must cite event/run IDs and preserve uncertainty. It does not rewrite the underlying worklog.

11\. CROSS-HOST FUTURE  
Claude Code and Codex should eventually emit the same normalized worklog schema through host-specific adapters. The schema must keep HOST and native session identifiers so differences are preserved rather than pretending all systems expose the same lifecycle.

12\. FIRST CURSOR ACCEPTANCE  
P0 observability passes when:  
\- open any Cursor workspace and a global hook emits a workspace event;  
\- start an agent session and a RUN/session record appears;  
\- model/workspace/session identifiers are captured where Cursor exposes them;  
\- afterFileEdit/tool/stop boundaries are logged without blocking normal work;  
\- session end or stop flushes a coherent batch/current card into Drive or the Drive-synced target;  
\- no secrets are present in uploaded evidence;  
\- another agent with Drive access can answer: who/which host is working, on which project, in which run, what stage, what changed, whether blocked, and what next;  
\- no manual transcript copy is required for that answer.

13\. FAILURE PRINCIPLE  
If direct Drive sync fails, local logging MUST continue. Telemetry transport failure must never erase local evidence or block coding work. Collector retries later and records its own sync status.  

PROTEUS — LOCAL LAYOUT AND SYNCHRONIZATION v0.1

PURPOSE  
Define what must exist where before the first Cursor run, how cloud descriptions differ from executable source and host incarnation, and which synchronization loops should exist immediately versus later.

1\. CLOUD HOME — DEVELOPMENT / EVIDENCE  
Google Drive Proteus root:  
https://drive.google.com/drive/folders/1qFAvPLQHPYUOt8iBuAouJ-8nU6AWpF6b

This cloud home currently carries:  
\- current status/function/boundaries;  
\- development program and user-request deltas;  
\- primary sources;  
\- donor lines;  
\- plugin recovery mirror;  
\- genealogy and negative corpus;  
\- ideal-body model documents;  
\- incarnation contracts;  
\- benchmark/eval material;  
\- bootstrap packet.

Google Drive is currently authoritative for developmental meaning and evidence. It is not automatically the runtime filesystem of Proteus.

2\. LOCAL FIRST-HOST ROOT  
Default target for first run:  
C:\\Projects\\Proteus\\

The directory should begin as a clean project root. The bootstrap packet is copied/exported into it before or at the beginning of the first run.

Recommended initial carrier layout only for the bootstrap stage:  
C:\\Projects\\Proteus\\  
  \_BOOTSTRAP\\  
    00\_CONTROL\\  
    10\_AGENT\\  
    15\_OBSERVABILITY\_AND\_CONTROL\\  
    20\_PRODUCT\\  
    30\_CORPUS\_MAP\\  
    40\_FIRST\_RUN\\  
    50\_EVALS\_AND\_RECEIPTS\\

Cursor is NOT required to preserve this layout as the final Proteus repository structure. It must first inspect the host and then design the smallest executable source layout that satisfies the requirements.

3\. EXECUTABLE IDEAL BODY  
During the first run Cursor creates or evolves the local Git repository into the executable ideal body: the versioned source that can generate/install/repair host incarnations.

Required properties, regardless of eventual folder names:  
\- host-independent core behavior or contracts where possible;  
\- Cursor-specific adapter/installer logic;  
\- project-bootstrap/mount logic;  
\- reentry/checkpoint/handoff capability;  
\- rule/skill/hook or equivalent generation where supported;  
\- provenance/receipt and rollback machinery;  
\- tests for Gate 1;  
\- a clear boundary between generated host state and source.

The Git repository becomes the executable authority only after it can reproduce and verify the installed Cursor embodiment.

4\. CURSOR INCARNATION  
The first embodied body consists of the actual Cursor and project surfaces generated or modified from the ideal body. Candidate surfaces include, subject to real inspection of the installed Cursor version:  
\- project-level .cursor rules/config;  
\- AGENTS.md and/or CLAUDE.md compatibility files where useful;  
\- skills;  
\- hooks;  
\- commands;  
\- agents;  
\- MCP configuration;  
\- local runtime/checkpoint state;  
\- project-scoped marker/current/backlog/goal pointers.

Do not assume every listed surface exists or should be used. The first run must detect actual supported mechanisms.

5\. PROJECT-SCOPED MOUNTS  
When the embodied agent is later told to work with Paideia, Hermes, Tinkuy or another project, it creates a project relationship/mount rather than copying the whole Proteus body into that project.

A mount may:  
\- identify the project and authoritative cloud/repo carriers;  
\- create/update host-readable project instructions;  
\- maintain current goal/frontier/backlog/decision pointers;  
\- record a Proteus mount marker and version;  
\- synchronize bounded project state;  
\- install project-scoped skills/rules only when justified;  
\- checkpoint/handoff at session boundaries;  
\- leave a reconciliation receipt.

6\. SYNC LOOP A — CLOUD DEVELOPMENT ↔ LOCAL DEVELOPMENT  
Purpose: keep user intent, product requirements, backlog, eval evidence and unresolved findings aligned.

First-run mode: deliberate/manual checkpoint. The local run consumes cloud bootstrap copies and writes local receipts. Material findings are later promoted to Drive deliberately.

Future mode: gateway-assisted reconciliation with stable IDs, provenance and conflicts.

Never implement last-write-wins semantic sync between Drive descriptions and local source.

7\. SYNC LOOP B — IDEAL BODY → CURSOR INCARNATION  
This should be automated from the first embodiment.

Source change  
→ run relevant tests  
→ compute intended host mutation  
→ snapshot current incarnation  
→ install/update  
→ verify postconditions  
→ write receipt  
→ rollback on failed verification.

Host files are generated/managed embodiment state. They must not become an accidental second source tree.

8\. SYNC LOOP C — INCARNATION EXPERIENCE → IDEAL BODY  
During real Cursor work, new failures and useful adaptations are captured as evidence.

Experience  
→ classify as episode / bug / capability deficit / possible rule / possible skill / infrastructure need / unresolved  
→ test whether it generalizes  
→ change ideal-body source if warranted  
→ test  
→ reinstall  
→ verify.

No direct automatic promotion into deep identity/core on one observation.

9\. SYNC LOOP D — PROJECT MOUNTS ↔ PROJECT AUTHORITIES  
Each mounted project has its own local/cloud/repository truth boundaries. Proteus must learn those from the project's own authority map rather than imposing one universal schema.

Typical flow:  
identify project → locate authoritative carriers → compare with local state → install/update project-facing instructions/markers → work → checkpoint → reconcile evidence/decisions/code through the project's allowed channels.

9.5. GLOBAL WORKLOG / CONTROL SYNC  
Cursor global hooks emit local append-only telemetry regardless of the mounted project. A collector flushes batches/current run cards to Proteus Runtime Observatory (Drive ID 1Cg0X2\_\_jRf-LtMstPfLTDTPTKK33-bhx). External commands use the 95\_COMMAND\_QUEUE carrier (Drive ID 1QdEloB\_kt-xJVbedRuCadhIMnKAbh1rK) plus a local controller that dispatches through verified Cursor stop-hook / CLI / ACP surfaces. Telemetry transport failure must not block work; commands require target+issuer provenance and acknowledgement.

10\. WHAT IS NOT SYNCHRONIZED BLINDLY  
\- historical corpus into system prompt;  
\- Drive documents directly into generated Cursor rules without transformation;  
\- Cursor host drift directly back into product canon;  
\- every project backlog into global agent identity;  
\- every correction into global rule;  
\- conflicting claims by timestamp alone.

11\. GATEWAY STATUS  
A Google Drive↔system gateway is a candidate infrastructure organ. Run 1 must record concrete friction:  
\- Can Cursor reliably obtain the bootstrap packet?  
\- Can it locate cloud authorities when needed?  
\- Is manual export sufficient for development?  
\- Which updates are frequent enough to justify automation?  
\- Do stable Drive IDs survive the desired workflow?

Only this evidence should determine whether the gateway is a tiny sync utility, an MCP server, a daemon, an Archivarius-facing reconciler, or something larger.

12\. START CONDITION  
The first Cursor run can begin as soon as:  
\- C:\\Projects\\Proteus exists;  
\- the bootstrap packet is locally readable;  
\- Git/rollback can be established;  
\- Cursor can inspect its own supported project/config surfaces.  
No separate final architecture is required.  

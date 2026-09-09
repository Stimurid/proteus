PROTEUS BOOTSTRAP — READ FIRST

STATUS  
Authoritative control note for the first Cursor embodiment packet.

1\. PURPOSE  
This packet exists to let a fresh Cursor project begin building the first working Proteus embodiment without first constructing a complete memory platform, gateway, multi-host spine or final architecture.

2\. READ ORDER  
Read in this order before modifying host or project state:  
1\) 10\_AGENT\_SPEC.md — who the working agent is and how it must operate.  
2\) 11\_AGENT\_CAPABILITY\_BACKLOG.md — which agent capabilities are P0/P1/later.  
3\) 20\_PRODUCT\_SPEC.md — what product must be built and what capabilities it must exhibit.  
4\) 21\_PRODUCT\_BACKLOG.md — Gate 1 product build order and deferred branches.  
5\) 15\_WORKLOG\_AND\_TELEMETRY.md \+ 16\_EXTERNAL\_CONTROL.md — global observability and steering.  
6\) 30\_CORPUS\_MAP.md — where evidence, history, donor lines and governing source material live.  
7\) 01\_LOCAL\_LAYOUT\_AND\_SYNC.md — cloud/local/source/incarnation boundaries and sync rules.  
8\) 40\_FIRST\_RUN\_PROMPT.md \+ 41\_MUTATION\_PROTOCOL.md.  
9\) 50\_GATE1\_EVAL.md \+ 51\_RUN\_RECEIPT\_TEMPLATE.md.  
10\) 60\_CURRENT\_PROTEUS\_STATUS.md.  
11\) 70\_PLUGIN\_SOURCE\_MAP.md \+ 71\_PLUGIN\_RECOVERY\_LEDGER.md; open 72\_PRIMARY\_SOURCE\_PLUGIN\_LAUNCH.md when genealogy/anti-reduction meaning matters.

3\. AUTHORITY  
The bootstrap packet is a local working carrier derived from the Proteus Drive corpus. It does not erase the provenance or status of its sources.

Authority classes:  
A. USER-GOVERNING REQUESTS — explicit user instructions and corrections; highest authority for current intent.  
B. CURRENT BLIND-RUN DOCUMENTS — current status, AGENT\_SPEC, PRODUCT\_SPEC, observability/control, local layout/sync and eval program.  
B2. POST-BLIND / OPERATOR-ONLY DOCUMENTS — five withheld operator documents A–E. Their titles and interpretations are intentionally hidden until BLIND\_OBSERVATION.md is written after first embodiment \+ smoke tests.  
C. PRIMARY SOURCES / HISTORICAL CORPUS — evidence of genealogy and earlier commitments; authoritative for what was historically said, not automatically current design law.  
D. DONOR LINES / ANALOGUES — evidence and design resources; never silently promoted into Proteus.  
E. INFERENCE / IMPLEMENTATION CHOICE — must be labeled as such and tested.

Folder names alone do not confer authority. Stable Drive IDs and provenance do.

4\. REQUIRED CONDUCT  
\- Preserve explicit UNKNOWN and unresolved conflicts.  
\- Do not convert ambiguous semantic claims into permanent rules merely to simplify implementation.  
\- Do not silently replace LLM-native behavior with keyword routing, canned logic, state machines or deterministic graph traversal.  
\- Prefer the smallest implementation that can actually be tested, but do not equate smallness with shallowness.  
\- Before changing Cursor/user/project configuration, capture a baseline and rollback path.  
\- Every consequential mutation must be attributable, diffable, testable and reversible.  
\- Treat the historical corpus as evidence, not as a bag of instructions to concatenate into system context.  
\- When a capability can remain host-native, test that route before inventing infrastructure.

5\. FIRST-RUN BOUNDARY  
The first run is allowed to:  
\- create C:\\Projects\\Proteus and initialize/adopt a Git repository;  
\- copy/export the bootstrap packet locally;  
\- inspect Cursor system/project configuration and capabilities;  
\- create project-local rules, skills, hooks, commands, agent files, MCP configuration or supporting code where the actual Cursor installation supports them;  
\- create a minimal portable Proteus source body and a Cursor host adapter;  
\- install/update the first Cursor embodiment;  
\- run Gate 1 smoke tests;  
\- use the installed embodiment for one bounded further Proteus-development action;  
\- write receipts, checkpoints and next frontier.

The first run is not authorized to:  
\- destroy or overwrite unrelated user configuration without backup;  
\- delete uncertain/high-value data;  
\- claim final architecture;  
\- silently promote inference into cloud canon;  
\- build large infrastructure merely because it may be useful later.

6\. STOP / ESCALATE CONDITIONS  
Stop destructive mutation and record the issue when:  
\- authority conflicts cannot be resolved from sources;  
\- required host paths/capabilities are uncertain and mutation could damage unrelated settings;  
\- rollback cannot be established;  
\- the requested behavior appears impossible with available Cursor surfaces and requires a new infrastructure organ;  
\- tests show that a proposed implementation destroys the semantic/LLM-native behavior it is meant to preserve.

7\. SUCCESS OF BOOTSTRAP  
Bootstrap succeeds when a fresh Cursor project can locate the governing packet, establish baseline+rollback, construct and install a minimal embodiment, verify it, and then continue one bounded Proteus-development action through the newly installed capabilities. Creating files alone is not success.  

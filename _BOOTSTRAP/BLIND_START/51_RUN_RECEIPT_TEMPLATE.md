PROTEUS / CURSOR GATE 1 — RUN RECEIPT TEMPLATE

RUN\_ID:  
HOST:  
MACHINE\_ID:  
PROJECT / WORKSPACE:  
CURSOR VERSION:  
MODEL(S):  
SESSION / CONVERSATION IDs:  
START / END:  
SOURCE REVISION:

1\. AUTHORITY READ  
For every governing source used: title, local carrier, Drive ID, status, revision/modified timestamp if available.

2\. BASELINE  
Git branch/revision/status; relevant host/config files; supported surfaces discovered; CLI/ACP/hooks/transcript availability; backups.

3\. OBJECTIVE / FRONTIER  
Exact intended outcome and bounded scope for this run.

4\. DESIGN CHOICES  
Chosen host-native mechanisms, alternatives rejected/deferred, evidence/reason.

5\. SOURCE CHANGES  
Files created/changed in ideal-body repository; commits/diffs.

6\. HOST / INCARNATION CHANGES  
Every Cursor/user/project file changed; before/after evidence; generated-from source pointer.

7\. OBSERVABILITY  
Telemetry local spool path; Runtime Observatory destination; first/last event IDs; active-run card; transcript pointer/copy status; redaction check; sync status.

8\. EXTERNAL CONTROL  
Command ID; ingress channel STOP\_HOOK / CLI / ACP / CLOUD\_API; target run/session; acknowledgement; result; any limitation discovered.

9\. TEST MATRIX  
For each test: PASS / FAIL / PARTIAL / NOT\_RUN; exact evidence pointer. File existence never substitutes for behavioral verification.

10\. SELF-UPDATE / SECOND MUTATION  
Deficit observed; source change; second install/update delta; verification; receipt pointer.

11\. FAILURES / UNKNOWN / CONFLICTS  
Preserve unresolved items explicitly with provenance and required next evidence.

12\. ROLLBACK  
Exact restore path/commands and whether rollback was actually tested.

13\. INFRASTRUCTURE EVIDENCE  
What first-run experience says about need for gateway, MCP/memory, shared substrate, control daemon, transcript handling or other candidate organs.

14\. NEXT FRONTIER  
One exact next executable step plus prerequisites.

FINAL STATUS:  
FIRST\_INCARNATION \= PASS/FAIL/PARTIAL  
OBSERVABILITY \= PASS/FAIL/PARTIAL  
EXTERNAL\_CONTROL \= PASS/FAIL/PARTIAL  
CLEAN\_REENTRY \= PASS/FAIL/NOT\_RUN  
GATE\_1 \= NOT\_YET / CONDITIONAL / PASS  

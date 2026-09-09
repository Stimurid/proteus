# DECISIONS

## D-001 — Local observatory fallback
Source: HOST_CONSTRAINT (Drive MCP error; empty Drive Desktop).
Decision: write Runtime Observatory cards under `%USERPROFILE%\.proteus\observatory\` and keep Drive folder IDs as intended destinations without pretending a successful cloud write.
Status: accepted for v0.1

## D-002 — Host-native hooks before new daemon
Source: CURRENT_PRODUCT_REQUIREMENT.
Decision: global `~/.cursor/hooks.json` + copied hook scripts; no always-on controller process in Gate 1.
Status: accepted for v0.1

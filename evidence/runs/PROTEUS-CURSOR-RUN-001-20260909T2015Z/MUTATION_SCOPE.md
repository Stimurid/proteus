# MUTATION_SCOPE — PROTEUS-CURSOR-RUN-001-20260909T2015Z

CLASS P (allowed): `C:\Projects\Proteus\**` except secrets.

CLASS H (allowed, bounded):
- Create `%USERPROFILE%\.cursor\hooks.json` if absent; merge only Proteus hook entries.
- Create `%USERPROFILE%\.cursor\hooks\proteus\` copies of hook scripts.
- Create `%USERPROFILE%\.proteus\` runtime/telemetry (not a git repo).

CLASS H forbidden this run:
- `cli-config.json`, `mcp.json`, `argv.json`
- wholesale user rules overwrite
- Happ/Amnezia/VPN
- unrelated projects

CLASS C: no Drive document promotion.

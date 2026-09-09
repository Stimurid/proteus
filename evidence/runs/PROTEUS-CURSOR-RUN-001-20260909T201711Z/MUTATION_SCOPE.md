# MUTATION_SCOPE

RUN_ID: PROTEUS-CURSOR-RUN-001-20260909T201711Z

## CLASS P — allowed

- `C:\Projects\Proteus\**` except secrets
- `_BOOTSTRAP` copies of the blind packet (read/copy only; do not rewrite packet sources)

## CLASS H — allowed

- Create `~/.cursor/hooks.json` if absent, or merge only `proteus_hook` entries if present
- Create `~/.cursor/hooks/proteus_hook.cmd`
- Create `%USERPROFILE%\.proteus\**` (telemetry, control queue, host copy, receipts, backups)

## CLASS H — forbidden this run

- `~/.cursor/mcp.json`
- `~/.cursor/cli-config.json`
- `~/.cursor/argv.json`
- Other projects' `.cursor`
- VPN / Happ / Amnezia

## CLASS C

- No Drive document promotion this run (transport blocked)

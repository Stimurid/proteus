# ROLLBACK

Project: `git` restore in `C:\Projects\Proteus`.

Host:

```
python src/proteus/install.py rollback --evidence evidence/runs/PROTEUS-CURSOR-RUN-001-20260909T2015Z
```

This restores the pre-install `hooks.json` snapshot from `host-backups/` and removes `~/.cursor/hooks/proteus`.

`%USERPROFILE%\.proteus` telemetry may be kept as evidence; delete only if explicitly desired.

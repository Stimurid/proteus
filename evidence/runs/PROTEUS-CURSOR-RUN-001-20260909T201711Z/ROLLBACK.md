# ROLLBACK

## Source

Git repository `C:\Projects\Proteus`. After baseline commit, `git status` / restore files from git.

## Host

Backups: `C:\Projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z\host-backups\`
Also installer snapshots under `%USERPROFILE%\.proteus\backups\`.

User hooks uninstall:

```
set PYTHONPATH=C:\Projects\Proteus\src
python -m proteus.install_cursor --run-id PROTEUS-CURSOR-RUN-001-20260909T201711Z --backup-dir C:\Projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z\host-backups --uninstall
```

If `hooks.json` did not exist before install, delete `~/.cursor/hooks.json` and `~/.cursor/hooks/proteus_hook.cmd` after uninstall if they only contain Proteus entries.

Do not delete `%USERPROFILE%\.proteus` telemetry unless the user asks; it is evidence.

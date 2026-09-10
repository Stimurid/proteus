# Proteus portable handoff

This directory is the **distribution / bootstrap location**. It is not run evidence and not historical source.

The user-carried artifact is:

`distribution/proteus-portable-handoff.zip`

Regenerate it from the repository root:

```
python -m proteus.handoff pack
```

(`PYTHONPATH=src` if the package is not installed.)

Clean-room reconstruction test (fresh temp directory, zip only):

```
python -m proteus.handoff cleanroom
```

Usage of the zip is inside the archive: `proteus-handoff/READ_ME_FIRST.md` and `bootstrap.cmd`.

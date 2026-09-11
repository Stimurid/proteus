# AW1000_REAL_ENTITY_EPISODE

RUN_ID: `PROTEUS-CURSOR-RUN-001-20260909T201711Z`
Episode: real world-memory hardening for Arcadyan/Arcadian AW1000
When: 2026-09-11
Acting role: BUILDER-01 (not Proteus)
Prior slice: D-007 / commit `51e051e` (not rebuilt)

## Authority inputs

- User task: REAL WORLD MEMORY HARDENING (this episode)
- Working architecture Drive `1MIaOF2uyozecgePkkowfblwGtOBG7tQrjUdVyLav1fw` (already provenance-recorded)
- Drive handoff: `HANDOFF — Arcadyan AW1000 / OpenWrt…` ID `1lM9BTn1vecgVlWbtN1K14acgzS0nEjn_vZceaQSiLyQ`
- Local: `C:\projects\.cursor\rules\aw1000-network.mdc`, `C:\projects\aw1000-audit\SSH-HANDOFF.md`, `STATUS.md`, `MIGRATION-STATUS.md`
- Live SSH: `AW1000_READONLY_SSH.txt` (read-only; no config mutation)

## Stable entity

- entity_id: `entity.router.aw1000.home` (single entity; aliases extended, not duplicated)
- aliases: AW1000, our router, Arcadian AW1000, Arcadyan AW1000, QWRT, home router, наш роутер
- local HOME: `world_memory_home/world/entities/entity.router.aw1000.home`
- Drive BACKUP carrier: `proteus-entity-router-aw1000-home-carrier-v0.1.zip`
  - provider_id: `1IYbaIRyC3ScnppX1iNdlVgo688jwE48r`
  - parent: `18Bz8HiyOVsLfcEWJ1KKQ2Qvplh8LfJzt`
  - readback + `DRIVE_RECONCILE.json`; no LWW
  - post-cloud local-only delta claim retained (`only_local` demonstrated)

## Facts imported / observed (provenance-bearing)

Categories: device/firmware (historical + live revalidation), Quectel/wwan0, eth4/WAN_ETH historical mapping, SSH mgmt path, AmneziaWG migration status, live interface snapshot 2026-09-11, LAN topology constraint, cloud marker episode.

Conflicts retained:
- historical LAN `192.168.2.1` vs management on `192.168.3.1` (do not collapse)

Unknowns retained:
- logical upstream-failure failover acceptance (mwan3) still UNKNOWN from docs
- green mobile LED meaning UNKNOWN

## Secret broker

- Provider: Windows Credential Manager (`proteus.secrets`, D-008)
- Synthetic put/get/delete PASS (`secret://router.aw1000.home.synthetic_test`)
- Real router password: `AW1000_REAL_SECRET = UNAVAILABLE` (askpass.cmd not read)
- SSH key: path capability only (`secret://router.aw1000.home.ssh_key`); key material not ingested
- Entity/Drive/git/stdout scan: no non-null plaintext secrets

## Router validation

- `REACHABILITY = PASS` via `ssh-aw1000.cmd` to `root@192.168.3.1`
- Read-only: os-release, interfaces, routes, ubus board
- No reboot/reset/config change this episode

## Cross-project recall

| Session | Raw | Result |
| --- | --- | --- |
| PROJECT_R1 | `AW1000_PROJECT_R1_STDOUT.txt` | PASS — facts + unresolved + opaque secret_refs |
| PROJECT_R2 | `AW1000_PROJECT_R2_STDOUT.txt` | PASS — alias `наш роутер` → same id; provenance + conflict; no prompt tech dump |

PROJECT_R1 decision does not appear as entity truth.

## Cloud recovery

- Fresh world root: `aw1000_cloud_recovery_world/`
- Recovered identity/claims/secret_refs from Drive carrier zip
- Local-only post-cloud delta **not** present in recovery (expected)
- Not a claim that cloud equals full local authority forever

## Archivarius

- Adapter reconcile: `ARCHIVARIUS_RECONCILE.json` written
- `LIVE_ARCHIVARIUS_RECONCILIATION = BLOCKED` (no live Archivarius process on host)

## Host-neutral contract

- `proteus.world.api` — resolve/mount/retrieve/route/secret_ref ops listed in CONTRACT

## Tests

Full `pytest tests`: **42 PASS** (includes secret broker + world + activate + prior)

## Not claimed

Full bidirectional sync; all facts current forever; real secret availability; live Archivarius; Codex/Claude portability; natural recruitment; Gate 1.

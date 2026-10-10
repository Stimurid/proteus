# DriveFS delivery bridge

Unattended local-source → Google Drive return for Proteus carrier bundles, using
the Google Drive for Desktop mount (`G:`) as the transport.

## Why this replaces `AUTH_REQUIRED`

`drive_upload_ledger` shipped without a real transport, on purpose. The only
Drive write path then available was model-mediated: payload bytes crossed the
token stream as base64 in both directions, and at bundle size that was not
byte-reliable — a 13527-byte archive came back with one flipped base64
character, 2 bad bytes, failing CRC. The honest status was `AUTH_REQUIRED` /
`TRANSPORT_UNSUPPORTED`, and the named user action was "authorise a service
account or rclone remote".

**That user action is no longer needed.** AORUS already runs Google Drive for
Desktop as the logged-in user, mounting the same Drive corpus at `G:`. Writing
there is an ordinary filesystem write. No new OAuth, no service-account key, no
token is read, copied or stored by any code in this module.

## The three statuses, and why they are three

| status | what it proves | what it does not prove |
|---|---|---|
| `STAGED_LOCAL` | bytes written into the DriveFS target and read back byte-identical **through `G:`** | nothing about Google — this is the local DriveFS cache |
| `CLOUD_PRESENT` | the provider, queried **outside** this host's mount, reports the object under the expected name, in the expected parent folder, at the exact expected byte length | byte identity — this connector exposes no checksum field |
| `CLOUD_VERIFIED` | an independent provider-side download returned the same sha256 and byte length | — |

Only `import_cloud_receipt()` can produce `CLOUD_VERIFIED`. No local copy and no
presence observation promotes itself, and a `CLOUD_PRESENT` record leaves the
item on the cloud verification queue. Ledger records are kept by evidence
strength (`STATUS_RANK`), so a routine re-stage can never un-verify something
the cloud already confirmed.

Observed in practice: staging to `G:` and the object appearing in Drive are
seconds-to-minutes apart. That latency is exactly why `STAGED_LOCAL` must not be
read as delivery.

## Safety properties

* **Target identity is proven by content, not by path.** `validate_target()`
  requires N of a set of long-lived marker files that exist only in
  AORUS/results. A `G:` belonging to a different account, or a correct-looking
  path that is the wrong folder, returns `MARKER_MISSING` and nothing is
  written. Pointing the config at `G:\` itself is refused (verified: exit 2).
* **Validation is read-only.** It deliberately does not probe writability by
  creating a scratch file: a create+delete inside a synced Drive folder produces
  a real cloud object and then a real trashed object on every run.
* **Deterministic, content-addressed names.** `proteus-carrier.<entity>.c<content16>.b<bundle16>.zip`.
  Name identity implies byte identity, so "the destination already exists" is
  settled by comparison rather than by trust.
* **Never overwrites.** Staging is temp-write + `os.rename` *inside the same
  target directory*. On Windows `os.rename` fails when the destination exists,
  which is the non-clobbering semantics wanted here. Same name + different bytes
  is a hard failure, never a replace.
* **Refuses bad payloads before copying**: zero-length, CRC-broken (`testzip()`),
  an archive with no `CARRIER_MANIFEST.json`, a digest disagreeing with the
  manifest, or a manifest targeting a different Drive folder.
* **Nothing is deleted.** Pending bundles and historical manifests stay put.
  Foreign carrier-shaped files in the target — notably the corrupted 13527-byte
  artifact from the old base64 route — are listed as `FOREIGN_UNVERIFIED` and
  left alone.
* **Bounded.** `--batch-cap`, `--max-bytes`, `--max-seconds`. Newest content
  state first, then backfill, so the live frontier is never starved and history
  still drains.
* **Lock scoped to this uploader only.** It guards the bridge against itself;
  it does not take a lock the world sync or the exporter know nothing about.
  Stale locks are broken and recorded.
* **Ledger lives outside the world git repo** (`~/.aiye/drivefs_bridge/`), so
  delivery bookkeeping can never masquerade as world substrate. Append-only
  JSONL; a torn final line from a crash is skipped, not fatal.

## Usage

```powershell
# validate the target, write nothing
.\scripts\drivefs-bridge.ps1 -Command status

# what WOULD be staged (pure read)
.\scripts\drivefs-bridge.ps1 -Command plan -BatchCap 8

# stage one bounded batch
.\scripts\drivefs-bridge.ps1 -Command stage -BatchCap 8 -MaxSeconds 300

# what is waiting for an independent cloud check
.\scripts\drivefs-bridge.ps1 -Command queue
```

Exit codes (the scheduler contract): `0` ok / nothing to do, `1` hard delivery
failure, `2` target unusable (mount gone, client stopped, wrong folder), `3`
usage or configuration error.

### Encoding rule — do not break this

Every `.ps1` here is **pure ASCII**. `powershell.exe` 5.1 — the Task Scheduler
interpreter — reads a BOM-less `.ps1` as ANSI, so a Cyrillic path written as a
literal arrives mangled and `Test-Path` fails silently. The target path lives in
a UTF-8 JSON config that only Python reads. Verified working end-to-end under
5.1 with the real Cyrillic target.

## Cloud verification handshake

`CLOUD_VERIFY_QUEUE.jsonl` publishes a self-sufficient record per staged state:

```json
{
  "schema": "proteus.drivefs_stage_receipt.v0.1",
  "status": "PENDING_CLOUD_VERIFY",
  "dest_name": "proteus-carrier.<entity>.c<...>.b<...>.zip",
  "expect_sha256": "<sha256 of the bundle>",
  "expect_bytes": 13526,
  "cloud_folder_id": "1eMS-Q5kB8-ijPDLFW9qcNBjWVVTDYdR0",
  "content_sha256": "...", "entity_id": "...", "manifest_path": "..."
}
```

A verifier needs no local path: locate `dest_name` in `cloud_folder_id`,
download the raw bytes **by file id through a path that is not this host's `G:`
mount**, confirm `sha256 == expect_sha256`, `length == expect_bytes`, and
`unzip -t` reports no CRC error. Then return:

```json
{
  "schema": "proteus.drivefs_cloud_verification.v0.1",
  "source_sha256": "...", "source_length_bytes": 13526,
  "cloud_file_id": "...", "cloud_parent_id": "1eMS-...",
  "cloud_download_sha256": "...", "cloud_zip_integrity": "PASS",
  "verified_at_utc": "..."
}
```

and import it:

```powershell
python -m proteus.world.drivefs_bridge_cli --config config\drivefs_target.json `
    import-receipt path\to\receipt.json
```

Every field is cross-checked against what was actually staged. A receipt for
something never staged, with a mismatched digest, length or parent folder, or
that contradicts itself, is recorded as `CLOUD_VERIFY_MISMATCH` and promotes
nothing.

A weaker metadata-only observation uses `proteus.drivefs_cloud_presence.v0.1`
and `import-presence`. It records `CLOUD_PRESENT` and **cannot** promote.

## Scheduling: interactive logon only

`G:` is owned by the interactive logon session. Measured on AORUSTIM 2026-10-10
with throwaway probe tasks:

| principal | result |
|---|---|
| `-LogonType Interactive` | session 1, target enumerated (97 entries), task exit 0 — **G: visible** |
| `-LogonType S4U` ("run whether user is logged on or not") | could not be registered without elevation; not usable here |

So the uploader must be registered **interactive**, matching the existing
`AiyeWorldSync` task (`User=Homee, LogonType=Interactive, RunLevel=Limited`).
If the user is logged off the task does not run and the queue waits — which is
correct, and is not the same as claiming delivery happened.

### Operator step: register the task

> This is deliberately a documented operator action rather than a script this
> repo runs for you. Review it, then run it yourself.

```powershell
$Script  = 'C:\projects\Proteus\scripts\drivefs-bridge.ps1'
$Config  = 'C:\projects\Proteus\config\drivefs_target.json'
$Task    = 'ProteusDriveFsBridge'
$Minutes = 20

# 1. PRE-FLIGHT. Never install a scheduler that cannot reach the target.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Script -Config $Config -Command status
if ($LASTEXITCODE -ne 0) { throw "Pre-flight failed ($LASTEXITCODE). Start Google Drive for Desktop, confirm G:, retry." }

# 2. SINGLE OWNER. Refuse to add a second uploader.
$leaf   = Split-Path -Leaf $Script
$others = @(Get-ScheduledTask | Where-Object {
    $_.TaskName -ne $Task -and ($_.Actions | Where-Object { $_.Arguments -and $_.Arguments -match [regex]::Escape($leaf) }) })
if ($others.Count -gt 0) { throw "Already scheduled by: $(($others | % TaskName) -join ', '). Disable those first." }

# 3. Register. Interactive logon; at-logon trigger delayed so DriveFS can mount G:.
$action  = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Script`" -Config `"$Config`" -Command stage -BatchCap 8"
$tLogon  = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$tLogon.Delay = 'PT3M'
$tRepeat = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $Minutes)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $Task -Action $action -Trigger @($tLogon,$tRepeat) `
    -Settings $settings -Principal $principal `
    -Description 'Proteus DriveFS delivery. Interactive logon only - G: does not exist without the user session. STAGED_LOCAL is not a cloud proof.'
```

To remove: `Unregister-ScheduledTask -TaskName 'ProteusDriveFsBridge' -Confirm:$false`.

`-MultipleInstances IgnoreNew` plus the bridge's own lock means an overlapping
tick is a no-op (`LOCK_BUSY`, exit 0), not a double-stage.

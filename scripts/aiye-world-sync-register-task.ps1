# aiye-world-sync-register-task.ps1 — register the 15-min Scheduled Task.
#
# Run once per host (per plan §5.5.A step 6). Idempotent: deletes and recreates.
# Does NOT require admin — registers under current user context.

[CmdletBinding()]
param(
    [string]$TaskName = "AiyeWorldSync",
    [string]$Script   = "C:\projects\Proteus\scripts\aiye-world-sync.ps1",
    [int]$Minutes     = 15
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Script)) { throw "Script not found: $Script" }

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Script`""

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes $Minutes)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

try { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Phase 5.5.A — sync ~/.aiye/world every $Minutes min via Proteus NO_LAST_WRITE_WINS reconcile." | Out-Null

Write-Host "Registered Scheduled Task: $TaskName (every $Minutes min, interactive user $env:USERNAME)"

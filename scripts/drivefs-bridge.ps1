# drivefs-bridge.ps1 - run one bounded DriveFS delivery pass.
#
# PURE ASCII ON PURPOSE. powershell.exe 5.1 reads a BOM-less .ps1 as ANSI, so a
# Cyrillic path written as a literal here would arrive mangled and Test-Path
# would silently fail. The target path therefore lives in a UTF-8 JSON config
# that only Python reads. Do not put non-ASCII characters in this file.
#
# Exit codes are passed through from the Python CLI and are the Task Scheduler
# contract:
#   0  nothing to do, or the pass succeeded
#   1  at least one hard delivery failure
#   2  DriveFS target not usable (G: absent, client stopped, wrong folder)
#   3  usage / configuration error
#
# G: IS visible to a Task Scheduler process registered with
# -LogonType Interactive (measured on AORUSTIM 2026-10-10: session 1, the target
# folder enumerated, exit 0). It is NOT safe to assume the same for a task set
# to "run whether user is logged on or not" - see drivefs-bridge-register-task.ps1.

[CmdletBinding()]
param(
    [string]$Config,
    [string]$RepoRoot,
    [string]$LedgerDir,
    [string]$Python,
    [int]$BatchCap = 8,
    [int]$MaxSeconds = 300,
    [switch]$DryRun,
    [ValidateSet('status', 'plan', 'stage', 'queue')]
    [string]$Command = 'stage'
)

$ErrorActionPreference = 'Stop'

if (-not $RepoRoot) { $RepoRoot = Split-Path -Parent $PSScriptRoot }
if (-not $Config) { $Config = Join-Path $RepoRoot 'config\drivefs_target.json' }
if (-not $LedgerDir) { $LedgerDir = Join-Path $env:USERPROFILE '.aiye\drivefs_bridge' }
if (-not $Python) {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    )
    $Python = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $Python) { $Python = (Get-Command python -ErrorAction SilentlyContinue).Source }
}

# NOT Write-Error: $ErrorActionPreference='Stop' turns it into a terminating
# error, the script dies with exit 1, and the documented usage-error code 3
# never reaches the scheduler.
function Fail-Usage([string]$msg) {
    [Console]::Error.WriteLine($msg)
    exit 3
}
if (-not $Python) { Fail-Usage 'No python interpreter found' }
if (-not (Test-Path -LiteralPath $Config)) { Fail-Usage "Config not found: $Config" }

New-Item -ItemType Directory -Force -Path $LedgerDir | Out-Null
$log = Join-Path $LedgerDir 'drivefs-bridge.log'

$argsList = @(
    '-m', 'proteus.world.drivefs_bridge_cli',
    '--config', $Config,
    '--ledger-dir', $LedgerDir,
    $Command
)
if ($Command -eq 'stage') {
    $argsList += @('--batch-cap', $BatchCap, '--max-seconds', $MaxSeconds)
    if ($DryRun) { $argsList += '--dry-run' }
}
elseif ($Command -eq 'plan') {
    $argsList += @('--batch-cap', $BatchCap)
}

$env:PYTHONPATH = Join-Path $RepoRoot 'src'
$env:PYTHONUTF8 = '1'

$stamp = (Get-Date).ToUniversalTime().ToString('o')
Add-Content -LiteralPath $log -Value "=== $stamp drivefs-bridge $Command (pid $PID, ps $($PSVersionTable.PSVersion)) ===" -Encoding UTF8

$out = & $Python @argsList 2>&1
$code = $LASTEXITCODE

Add-Content -LiteralPath $log -Value ($out | Out-String) -Encoding UTF8
Add-Content -LiteralPath $log -Value "exit_code=$code" -Encoding UTF8
$out | Write-Output

exit $code

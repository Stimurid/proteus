# aiye-world-sync.ps1 — Phase 5.5.A git-sync for ~/.aiye/world
#
# Fetch origin, merge origin/main into local host branch, detect & route
# conflicts through Proteus `conflicts_with` (NOT last-write-wins), rebuild
# index, commit, push. Designed for a 15-minute Scheduled Task on AORUS.
#
# Exit codes:
#   0 — sync succeeded (clean or merged)
#   2 — merge conflict in a non-claims file; left for operator
#   3 — git fetch/push failed (network/auth)
#   4 — Proteus rebuild-index failed
#   5 — publication-readback failed (local HEAD != remote HEAD after push)
#   7 — unhandled runtime exception (caught by outer try/catch)
#
# Logs: appended to C:\Users\Homee\.aiye\world\.sync.log

[CmdletBinding()]
param(
    [string]$WorldRoot = "$env:USERPROFILE\.aiye\world",
    [string]$Branch    = "host/aorus",
    [string]$PythonExe = "C:\Users\Homee\AppData\Local\Programs\Python\Python314\python.exe",
    [string]$ProteusSrc = "C:\projects\Proteus\src",
    [switch]$DryRun
)

# Note: deliberately NOT setting $ErrorActionPreference='Stop' globally. The old
# combination of 2>&1 pipes from native tools (git, python) + Stop converts any
# stderr line into a terminating ErrorRecord and silently exits the script with
# code 1 before the next statement. Native-command stderr must be treated as
# log data, not as PowerShell errors.
$ErrorActionPreference = 'Continue'

function Now { (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ") }
$log = Join-Path $WorldRoot ".sync.log"
function Write-Log([string]$msg) {
    $line = "[$(Now)] $msg"
    Write-Host $line
    try { Add-Content -Path $log -Value $line -Encoding utf8 -ErrorAction SilentlyContinue } catch {}
}

function Invoke-Native {
    param([string]$Label, [scriptblock]$Block)
    $out = & $Block 2>&1
    $exit = $LASTEXITCODE
    foreach ($line in $out) { Write-Log "${Label}: $line" }
    return $exit
}

try {
    if (-not (Test-Path $WorldRoot)) { Write-Log "ABORT: $WorldRoot missing"; exit 1 }
    Set-Location $WorldRoot

    # Python Unicode-safe stdio for Scheduled Task context (non-interactive cp-locale)
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONUTF8 = '1'
    $env:GIT_TERMINAL_PROMPT = '0'

    Write-Log "sync start branch=$Branch dry_run=$DryRun pid=$PID host=$env:COMPUTERNAME user=$env:USERNAME"

    # --- fetch ---
    $exit = Invoke-Native "fetch" { git fetch origin }
    if ($exit -ne 0) { Write-Log "FETCH_FAIL exit=$exit"; exit 3 }

    # --- merge origin/main ---
    $exit = Invoke-Native "merge" { git merge --no-edit --no-ff origin/main }
    if ($exit -ne 0) {
        $conflicted = @(& git diff --name-only --diff-filter=U 2>$null)
        $nonClaims = $conflicted | Where-Object { $_ -notmatch 'claims\.jsonl$' }
        if ($nonClaims) {
            Write-Log "NON_CLAIM_CONFLICT files=$($nonClaims -join ',')"
            Invoke-Native "abort" { git merge --abort } | Out-Null
            exit 2
        }
        foreach ($f in $conflicted) {
            Invoke-Native "readd" { git add -- $f } | Out-Null
        }
        Invoke-Native "commit_merge" { git commit --no-edit -m "sync merge $(Now)" } | Out-Null
    }

    # --- reconcile entities that received new claims from the merge ---
    $changedEntities = @()
    $diff = @(& git diff --name-only "HEAD@{1}" HEAD 2>$null)
    foreach ($p in $diff) {
        if ($p -match '^entities/([^/]+)/') { $changedEntities += $Matches[1] }
    }
    $changedEntities = @($changedEntities | Sort-Object -Unique)

    $env:PYTHONPATH = $ProteusSrc
    foreach ($eid in $changedEntities) {
        Write-Log "reconcile entity=$eid"
        $exit = Invoke-Native "reconcile" { & $PythonExe -m proteus world reconcile --entity-id $eid }
        if ($exit -ne 0) { Write-Log "RECONCILE_WARN entity=$eid exit=$exit (continuing)" }
    }

    # --- rebuild local VIEW index (not pushed) ---
    $exit = Invoke-Native "rebuild" { & $PythonExe -m proteus world rebuild-index }
    if ($exit -ne 0) { Write-Log "REBUILD_FAIL exit=$exit"; exit 4 }

    # --- commit local changes (reconcile may have rewritten claim statuses) ---
    $status = (& git status --porcelain) -join "`n"
    if ($status) {
        Invoke-Native "add" { git add -A } | Out-Null
        Invoke-Native "commit" { git commit -m "sync $(Now) reconcile" } | Out-Null
    }

    if ($DryRun) { Write-Log "DRY_RUN end; no push"; exit 0 }

    # --- push host branch ---
    $exit = Invoke-Native "push" { git push origin $Branch }
    if ($exit -ne 0) { Write-Log "PUSH_FAIL exit=$exit"; exit 3 }

    # --- publication readback: fast-forward main and verify ---
    $exit = Invoke-Native "push_main" { git push origin "$($Branch):main" }
    # Non-fatal push_main; verify instead.

    $localHead = (& git rev-parse $Branch).Trim()
    $remoteHostHead = (& git ls-remote --heads origin $Branch | ForEach-Object { ($_ -split "\s+")[0] })
    $remoteMainHead = (& git ls-remote --heads origin main | ForEach-Object { ($_ -split "\s+")[0] })
    Write-Log "readback local=$localHead remote_host=$remoteHostHead remote_main=$remoteMainHead"
    if ($localHead -ne $remoteHostHead) {
        Write-Log "READBACK_FAIL remote $Branch not updated"; exit 5
    }
    if ($localHead -ne $remoteMainHead) {
        Write-Log "READBACK_WARN remote main ($remoteMainHead) != local HEAD ($localHead); push_main exit=$exit"
    }

    Write-Log "sync end OK local=$localHead"
    exit 0

} catch {
    Write-Log "UNHANDLED_EXCEPTION: $($_ | Out-String)"
    exit 7
}

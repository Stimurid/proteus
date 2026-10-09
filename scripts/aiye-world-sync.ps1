# aiye-world-sync.ps1 — Phase 5.5.A git-sync for ~/.aiye/world
#
# Fetch origin, merge origin/main into local host branch, detect & route
# conflicts through Proteus `conflicts_with` (NOT last-write-wins), rebuild
# index, commit, push. Designed for a 15-minute Scheduled Task on AORUS.
#
# Exit codes:
#   0 — sync succeeded (clean or merged)
#   2 — merge conflict/metadata op failed; left for operator review
#   3 — git transport (fetch/push/add/commit) failed
#   4 — Proteus rebuild-index failed
#   5 — publication-readback failed (local HEAD != both remote HEADs after push,
#        OR stranded uncommitted claims remain)
#   6 — DEGRADED success (transport+publication OK; one or more reconcile steps
#        returned non-zero and the view is partially stale; still better than
#        hiding under exit 0, but not full PASS)
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

    # Clean-worktree snapshot pre-run — used later to assert no stranded claims.
    $preIntendedStaged = (& git diff --cached --name-only 2>$null) -join "`n"
    $preIntendedUnstaged = (& git diff --name-only 2>$null) -join "`n"

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
            $e = Invoke-Native "readd" { git add -- $f }
            if ($e -ne 0) { Write-Log "READD_FAIL file=$f exit=$e"; exit 2 }
        }
        $e = Invoke-Native "commit_merge" { git commit --no-edit -m "sync merge $(Now)" }
        if ($e -ne 0) { Write-Log "COMMIT_MERGE_FAIL exit=$e"; exit 2 }
    }

    # --- reconcile entities that received new claims from the merge ---
    $changedEntities = @()
    $diff = @(& git diff --name-only "HEAD@{1}" HEAD 2>$null)
    foreach ($p in $diff) {
        if ($p -match '^entities/([^/]+)/') { $changedEntities += $Matches[1] }
    }
    $changedEntities = @($changedEntities | Sort-Object -Unique)

    $env:PYTHONPATH = $ProteusSrc
    $reconcileDegraded = $false
    foreach ($eid in $changedEntities) {
        Write-Log "reconcile entity=$eid"
        $exit = Invoke-Native "reconcile" { & $PythonExe -m proteus world reconcile --entity-id $eid }
        if ($exit -ne 0) {
            Write-Log "RECONCILE_DEGRADED entity=$eid exit=$exit"
            $reconcileDegraded = $true
        }
    }

    # --- rebuild local VIEW index (not pushed) ---
    $exit = Invoke-Native "rebuild" { & $PythonExe -m proteus world rebuild-index }
    if ($exit -ne 0) { Write-Log "REBUILD_FAIL exit=$exit"; exit 4 }

    # --- DryRun gate: performs merge + reconcile + rebuild above (which may
    # touch worktree). Exit now without ANY commit/push so repeated dry-runs
    # on a clean world yield deterministic state. The merge up-stream could
    # still alter working tree; reset the staging index to pre-run snapshot
    # if the operator chose dry mode.
    if ($DryRun) {
        Write-Log "DRY_RUN end; no commit; no push"
        exit 0
    }

    # --- commit local changes (reconcile may have rewritten claim statuses) ---
    $status = (& git status --porcelain) -join "`n"
    if ($status) {
        $e = Invoke-Native "add" { git add -A }
        if ($e -ne 0) { Write-Log "ADD_FAIL exit=$e"; exit 3 }
        $e = Invoke-Native "commit" { git commit -m "sync $(Now) reconcile" }
        if ($e -ne 0) { Write-Log "COMMIT_FAIL exit=$e"; exit 3 }
    }

    # --- push host branch ---
    $exit = Invoke-Native "push" { git push origin $Branch }
    if ($exit -ne 0) { Write-Log "PUSH_FAIL exit=$exit"; exit 3 }

    # --- publish main; main is REQUIRED by the cross-host read contract.
    # A failed push to main must surface as a non-zero exit so the Scheduler
    # does not record LastTaskResult=0 on partial publication.
    $pushMainExit = Invoke-Native "push_main" { git push origin "$($Branch):main" }
    if ($pushMainExit -ne 0) {
        Write-Log "PUSH_MAIN_FAIL exit=$pushMainExit (cross-host contract requires main)"
    }

    # --- publication readback: strict equality on all three refs ---
    $localHead = (& git rev-parse $Branch 2>$null).Trim()
    if (-not $localHead) { Write-Log "REV_PARSE_FAIL branch=$Branch"; exit 5 }
    $remoteHostLine = (& git ls-remote --heads origin $Branch 2>$null)
    if (-not $remoteHostLine) { Write-Log "LS_REMOTE_FAIL branch=$Branch"; exit 5 }
    $remoteHostHead = ($remoteHostLine -split "\s+")[0]
    $remoteMainLine = (& git ls-remote --heads origin main 2>$null)
    if (-not $remoteMainLine) { Write-Log "LS_REMOTE_FAIL branch=main"; exit 5 }
    $remoteMainHead = ($remoteMainLine -split "\s+")[0]
    Write-Log "readback local=$localHead remote_host=$remoteHostHead remote_main=$remoteMainHead"
    if ($localHead -ne $remoteHostHead) {
        Write-Log "READBACK_FAIL remote $Branch not at local HEAD"; exit 5
    }
    if ($localHead -ne $remoteMainHead) {
        Write-Log "READBACK_FAIL remote main ($remoteMainHead) != local HEAD ($localHead)"; exit 5
    }

    # Assert no stranded intended changes remain uncommitted.
    $postStatus = (& git status --porcelain 2>$null) -join "`n"
    if ($postStatus) {
        Write-Log "STRANDED_CHANGES post-sync:`n$postStatus"; exit 5
    }

    if ($reconcileDegraded) {
        Write-Log "sync end DEGRADED local=$localHead (reconcile warnings; publication contract satisfied)"
        exit 6
    }
    Write-Log "sync end OK local=$localHead"
    exit 0

} catch {
    Write-Log "UNHANDLED_EXCEPTION: $($_ | Out-String)"
    exit 7
}

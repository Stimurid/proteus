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

$ErrorActionPreference = 'Stop'
$ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$log = Join-Path $WorldRoot ".sync.log"
function Write-Log([string]$msg) {
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $log -Value $line -Encoding utf8
}

if (-not (Test-Path $WorldRoot)) { Write-Log "ABORT: $WorldRoot missing"; exit 1 }
Set-Location $WorldRoot

Write-Log "sync start branch=$Branch dry_run=$DryRun"

# --- fetch ---
try {
    $env:GIT_TERMINAL_PROMPT = '0'
    git fetch origin 2>&1 | ForEach-Object { Write-Log "fetch: $_" }
    if ($LASTEXITCODE -ne 0) { Write-Log "FETCH_FAIL exit=$LASTEXITCODE"; exit 3 }
} catch {
    Write-Log "FETCH_EXCEPTION: $_"; exit 3
}

# --- merge origin/main ---
$mergeOut = git merge --no-edit --no-ff origin/main 2>&1
$mergeExit = $LASTEXITCODE
$mergeOut | ForEach-Object { Write-Log "merge: $_" }

$conflicted = @()
if ($mergeExit -ne 0) {
    $conflicted = git diff --name-only --diff-filter=U
    $nonClaims = $conflicted | Where-Object { $_ -notmatch 'claims\.jsonl$' }
    if ($nonClaims) {
        Write-Log "NON_CLAIM_CONFLICT files=$($nonClaims -join ',')"
        Write-Log "operator action required; aborting merge"
        git merge --abort 2>&1 | ForEach-Object { Write-Log "abort: $_" }
        exit 2
    }
    # claims.jsonl should already have been union-merged by .gitattributes.
    # If git still reports them unresolved, re-add is safe.
    foreach ($f in $conflicted) {
        git add -- $f 2>&1 | ForEach-Object { Write-Log "readd: $_" }
    }
    git commit --no-edit -m "sync merge $ts" 2>&1 | ForEach-Object { Write-Log "commit: $_" }
}

# --- reconcile entities that received new claims from the merge ---
$changedEntities = @()
try {
    $diff = git diff --name-only "HEAD@{1}" HEAD 2>$null
    foreach ($p in $diff) {
        if ($p -match '^entities/([^/]+)/') {
            $changedEntities += $Matches[1]
        }
    }
    $changedEntities = $changedEntities | Sort-Object -Unique
} catch {
    Write-Log "DIFF_SKIP (no prior HEAD): $_"
}

$env:PYTHONPATH = $ProteusSrc
foreach ($eid in $changedEntities) {
    Write-Log "reconcile entity=$eid"
    & $PythonExe -m proteus world reconcile --entity-id $eid 2>&1 | ForEach-Object { Write-Log "reconcile: $_" }
}

# --- rebuild local VIEW index (not pushed) ---
& $PythonExe -m proteus world rebuild-index 2>&1 | ForEach-Object { Write-Log "rebuild: $_" }
if ($LASTEXITCODE -ne 0) { Write-Log "REBUILD_FAIL exit=$LASTEXITCODE"; exit 4 }

# --- commit local changes (reconcile may have rewritten claim statuses) ---
$status = git status --porcelain
if ($status) {
    git add -A 2>&1 | ForEach-Object { Write-Log "add: $_" }
    git commit -m "sync $ts reconcile" 2>&1 | ForEach-Object { Write-Log "commit: $_" }
}

if ($DryRun) { Write-Log "DRY_RUN end; no push"; exit 0 }

# --- push both branch and (fast-forward) main ---
git push origin $Branch 2>&1 | ForEach-Object { Write-Log "push: $_" }
if ($LASTEXITCODE -ne 0) { Write-Log "PUSH_FAIL exit=$LASTEXITCODE"; exit 3 }

# Attempt fast-forward main; failure is non-fatal (owner may want manual PR).
git push origin "$($Branch):main" 2>&1 | ForEach-Object { Write-Log "push_main: $_" }

Write-Log "sync end OK"
exit 0

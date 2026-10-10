# aiye-world-sync.ps1 - Phase 5.5.A git-sync for ~/.aiye/world
#
# Fetch origin, merge origin/main into local host branch, resolve claims.jsonl
# divergence as APPEND-ONLY RECORDS (never text hunks, never last-write-wins),
# validate ledger integrity, rebuild index, commit, push.
# Designed for a 15-minute Scheduled Task on AORUS.
#
# Exit codes:
#   0 - sync succeeded (clean or merged)
#   2 - merge conflict/metadata op failed; left for operator review
#   3 - git transport (fetch/push/add/commit) failed
#   4 - Proteus rebuild-index failed
#   5 - publication-readback failed (local HEAD != both remote HEADs after push,
#        OR stranded uncommitted claims remain)
#   6 - DEGRADED success (transport+publication OK; one or more reconcile steps
#        returned non-zero and the view is partially stale; still better than
#        hiding under exit 0, but not full PASS)
#   7 - unhandled runtime exception (caught by outer try/catch)
#   8 - claims ledger integrity failure (conflict markers, invalid JSON, or a
#        missing trailing newline that merge=union would corrupt). Publication
#        is refused; the ledger is left for operator review.
#   9 - NO DURABLE RECEIPT: not one log line reached disk, so the run left no
#        evidence. Refuses to report any other code as success.
#
# Modes (Issue #1 round 3 - the old -DryRun was NOT read-only):
#   (default)   full pipeline, commits and publishes.
#   -NoPublish  LOCAL-MUTATING. Runs fetch/merge/reconcile/rebuild/commit against
#               the real world, then stops before push. This DOES change local
#               git state. It is not a preview and must never be described as one.
#   -Preview    Genuinely read-only w.r.t. the real world. Clones $WorldRoot to a
#               temporary directory, repoints origin at the real remote, runs the
#               pipeline there under -NoPublish, reports what WOULD change, and
#               deletes the clone. $WorldRoot is never written.
#   -DryRun     DEPRECATED alias for -Preview, kept so existing callers do not
#               break. Prior versions ran fetch+merge+reconcile+rebuild against
#               the real world BEFORE their "dry" gate, so -DryRun was silently
#               local-mutating, and the staging-reset its own comment promised
#               was never implemented (the captured pre-run snapshot was dead
#               code: $preIntendedStaged / $preIntendedUnstaged were never read).
#
# Logs: appended to C:\Users\Homee\.aiye\world\.sync.log

[CmdletBinding()]
param(
    [string]$WorldRoot = "$env:USERPROFILE\.aiye\world",
    [string]$Branch    = "host/aorus",
    [string]$PythonExe = "C:\Users\Homee\AppData\Local\Programs\Python\Python314\python.exe",
    [string]$ProteusSrc = "C:\projects\Proteus\src",
    [switch]$NoPublish,
    [switch]$Preview,
    [switch]$DryRun,
    [int]$PushRetries = 3
)

# Note: deliberately NOT setting $ErrorActionPreference='Stop' globally. The old
# combination of 2>&1 pipes from native tools (git, python) + Stop converts any
# stderr line into a terminating ErrorRecord and silently exits the script with
# code 1 before the next statement. Native-command stderr must be treated as
# log data, not as PowerShell errors.
$ErrorActionPreference = 'Continue'

function Now { (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ") }
$log = Join-Path $WorldRoot ".sync.log"

# Durable-receipt accounting. The previous Write-Log swallowed every append
# failure (-ErrorAction SilentlyContinue inside try{}catch{}), so if the log
# was briefly unavailable - another process holding a handle, e.g. a `tail -F`
# watcher, which is exactly how this was found - the whole run proceeded and
# exited 0 while leaving NO durable record, and Task Scheduler recorded
# LastTaskResult=0. Success with zero evidence is the same false-SUCCESS class
# as the rest of Issue #1. A transient lock must not be fatal, but total
# blindness must not be reported as success.
$script:LogWritesOk = 0
$script:LogWritesFailed = 0

function Write-Log([string]$msg) {
    $line = "[$(Now)] $msg"
    Write-Host $line
    for ($i = 1; $i -le 3; $i++) {
        try {
            Add-Content -Path $log -Value $line -Encoding utf8 -ErrorAction Stop
            $script:LogWritesOk++
            return
        } catch {
            if ($i -eq 3) {
                $script:LogWritesFailed++
                # stderr, so a lost log line is still visible to the caller
                # and to Task Scheduler's captured output.
                [Console]::Error.WriteLine("LOG_WRITE_FAILED after $i attempts: $line")
                return
            }
            Start-Sleep -Milliseconds (200 * $i)
        }
    }
}

# Exit wrapper: refuses to report success when nothing could be recorded.
function Exit-Sync([int]$Code) {
    if ($script:LogWritesFailed -gt 0) {
        [Console]::Error.WriteLine("LOG_DEGRADED ok=$($script:LogWritesOk) failed=$($script:LogWritesFailed) log=$log")
    }
    if ($script:LogWritesOk -eq 0) {
        # Not one line reached disk: there is no durable receipt for this run.
        [Console]::Error.WriteLine("NO_DURABLE_RECEIPT: no log line could be written to $log; refusing to report exit=$Code as success")
        exit 9
    }
    exit $Code
}

function Invoke-Native {
    param([string]$Label, [scriptblock]$Block)
    $out = & $Block 2>&1
    $exit = $LASTEXITCODE
    foreach ($line in $out) { Write-Log "${Label}: $line" }
    return $exit
}

$script:ClaimsTool = Join-Path $PSScriptRoot "claims_jsonl.py"

# Write JSONL as UTF-8 with NO byte-order mark, and always end with a newline.
#
# Windows PowerShell 5.1 - which is what the Scheduled Task actually runs - emits
# a BOM (EF BB BF) for `Set-Content -Encoding utf8`, and 5.1 has no utf8NoBOM
# option. The three git merge-stage files below are fed straight to
# claims_jsonl.py, and a BOM makes the first line unparseable JSON. The resolver
# then returned 3, Invoke-MergeRef returned 8, and publication was refused.
#
# That meant the append-only claims merge path - the centrepiece of Issue #1 -
# could never have completed under the real scheduler. It passed CI only because
# the suites were run under pwsh 7, where `-Encoding utf8` is BOM-less. Verified
# 2026-10-10: PS5.1 first bytes "EF BB BF 7B" vs pwsh7 "7B 22 61 22".
#
# ASCII would also dodge the BOM but would corrupt non-ASCII claim bodies (the
# live world carries Russian text), so UTF8Encoding($false) is the correct fix.
$script:Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
function Write-JsonlNoBom([string]$Path, $Lines) {
    $arr = [string[]]@(@($Lines) | ForEach-Object { [string]$_ })
    [System.IO.File]::WriteAllLines($Path, $arr, $script:Utf8NoBom)
}

# Validate every tracked claims ledger. Corruption (markers / invalid JSON /
# missing trailing newline) returns 3 from the tool and blocks publication.
# Divergent claim_ids are warnings and deliberately do NOT block: the live world
# legitimately carries append-only supersede records.
function Test-ClaimsIntegrity {
    param([string]$Label)
    $entitiesDir = Join-Path $WorldRoot "entities"
    if (-not (Test-Path $entitiesDir)) { Write-Log "claims_integrity ${Label}: no entities dir"; return 0 }
    $files = @(Get-ChildItem -Path $entitiesDir -Recurse -Filter "claims.jsonl" -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
    if ($files.Count -eq 0) { Write-Log "claims_integrity ${Label}: no ledgers found"; return 0 }
    $exit = Invoke-Native "claims_integrity_$Label" { & $PythonExe $script:ClaimsTool validate @files }
    return $exit
}

# Merge ONE named remote ref. claims.jsonl divergence is resolved from git's three
# merge stages as records; anything else is left for the operator.
#
# Issue #3: this function used to be hard-wired to origin/main. That is the whole
# bug. When another host published to origin/<branch> but NOT to origin/main,
# `git merge origin/main` reported "Already up to date", the local tip stayed behind
# origin/<branch>, and `git push` was rejected non-fast-forward. The retry loop then
# re-ran the SAME main-only merge, so every retry was guaranteed to fail identically
# (observed live 2026-10-10T07:37Z: 3x "Already up to date" between 3x rejected
# pushes, Scheduled Task LastTaskResult=3).
function Invoke-MergeRef {
    param([Parameter(Mandatory = $true)][string]$Ref)
    $exit = Invoke-Native "merge[$Ref]" { git merge --no-edit --no-ff $Ref }
    if ($exit -eq 0) { return 0 }

    $conflicted = @(& git diff --name-only --diff-filter=U 2>$null)
    $nonClaims = @($conflicted | Where-Object { $_ -notmatch 'claims\.jsonl$' })
    if ($nonClaims.Count -gt 0) {
        Write-Log "NON_CLAIM_CONFLICT ref=$Ref files=$($nonClaims -join ',')"
        Invoke-Native "abort" { git merge --abort } | Out-Null
        return 2
    }

    $tmp = Join-Path $env:TEMP "aiye-claims-merge-$(Get-Random)"
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    try {
        foreach ($f in $conflicted) {
            $base   = Join-Path $tmp "base.jsonl"
            $ours   = Join-Path $tmp "ours.jsonl"
            $theirs = Join-Path $tmp "theirs.jsonl"
            $out    = Join-Path $tmp "merged.jsonl"

            # Stage 1 (common ancestor) is absent for add/add conflicts.
            $b = (& git show ":1:$f" 2>$null)
            if ($LASTEXITCODE -ne 0) { $b = @() }
            Write-JsonlNoBom $base $b

            $o = (& git show ":2:$f" 2>$null)
            if ($LASTEXITCODE -ne 0) { Write-Log "STAGE2_MISSING file=$f"; return 2 }
            Write-JsonlNoBom $ours $o

            $t = (& git show ":3:$f" 2>$null)
            if ($LASTEXITCODE -ne 0) { Write-Log "STAGE3_MISSING file=$f"; return 2 }
            Write-JsonlNoBom $theirs $t

            $e = Invoke-Native "claims_resolve" { & $PythonExe $script:ClaimsTool resolve --base $base --ours $ours --theirs $theirs --out $out }
            if ($e -ne 0) { Write-Log "CLAIMS_RESOLVE_FAIL file=$f exit=$e"; return 8 }

            $target = Join-Path $WorldRoot $f
            Copy-Item -Path $out -Destination $target -Force
            $e = Invoke-Native "claims_validate_resolved" { & $PythonExe $script:ClaimsTool validate $target }
            if ($e -ne 0) { Write-Log "CLAIMS_RESOLVED_INVALID file=$f exit=$e"; return 8 }

            $e = Invoke-Native "readd" { git add -- $f }
            if ($e -ne 0) { Write-Log "READD_FAIL file=$f exit=$e"; return 2 }
        }
    } finally {
        Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    }

    # No conflicted path may survive into the commit.
    $stillConflicted = @(& git diff --name-only --diff-filter=U 2>$null)
    if ($stillConflicted.Count -gt 0) {
        Write-Log "UNRESOLVED_AFTER_MERGE files=$($stillConflicted -join ',')"
        return 2
    }
    $e = Invoke-Native "commit_merge" { git commit --no-edit -m "sync merge $Ref $(Now)" }
    if ($e -ne 0) { Write-Log "COMMIT_MERGE_FAIL ref=$Ref exit=$e"; return 2 }
    return 0
}

# Integrate EVERY remote ref this host is contractually bound to, not just main.
#
# Order matters: origin/$Branch FIRST. That is the ref we are about to push to, so
# it is the one that can reject us; incorporating it is what turns the push into a
# fast-forward. origin/main second, because the cross-host read contract also
# requires main and another host may have advanced it independently.
#
# A ref absent on the remote (first publication of a host branch) is SKIPPED, not
# an error. A ref already an ancestor costs one cheap "Already up to date".
#
# Returns 0 on success, else the first non-zero merge result (2 = operator review,
# 8 = claims-ledger integrity). Never force-pushes, never drops a remote commit.
function Invoke-MergeRemotes {
    param([Parameter(Mandatory = $true)][string]$Branch)
    foreach ($ref in @("origin/$Branch", "origin/main")) {
        & git rev-parse --verify --quiet "$ref^{commit}" > $null 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "merge_skip ref=$ref (absent on remote)"
            continue
        }
        $e = Invoke-MergeRef -Ref $ref
        if ($e -ne 0) { Write-Log "MERGE_REF_FAIL ref=$ref exit=$e"; return $e }
    }
    return 0
}

try {
    if (-not (Test-Path $WorldRoot)) { Write-Log "ABORT: $WorldRoot missing"; Exit-Sync 1 }

    # --- -DryRun is a deprecated alias; -Preview is the honest name. ---
    if ($DryRun -and -not $Preview) {
        Write-Log "DRYRUN_DEPRECATED: -DryRun was local-mutating in prior versions; routing to -Preview (isolated clone). Use -Preview for read-only, -NoPublish for local-mutating."
        $Preview = $true
    }

    if ($Preview) {
        # Genuine isolation: the real world is only ever read, by `git clone`.
        $clone = Join-Path $env:TEMP "aiye-world-preview-$(Get-Random)"
        Write-Log "PREVIEW start clone=$clone source=$WorldRoot (source is READ-ONLY in this mode)"
        $e = Invoke-Native "preview_clone" { git clone --no-hardlinks --branch $Branch -- $WorldRoot $clone }
        if ($e -ne 0) { Write-Log "PREVIEW_CLONE_FAIL exit=$e"; Exit-Sync 3 }

        $realOrigin = (& git -C $WorldRoot remote get-url origin 2>$null)
        if ($LASTEXITCODE -ne 0 -or -not $realOrigin) {
            Write-Log "PREVIEW_ORIGIN_UNRESOLVED"
            Remove-Item -Recurse -Force $clone -ErrorAction SilentlyContinue
            Exit-Sync 3
        }
        Invoke-Native "preview_origin"    { git -C $clone remote set-url origin $realOrigin.Trim() } | Out-Null
        Invoke-Native "preview_identity"  { git -C $clone config user.email "preview@line-a.local" } | Out-Null
        Invoke-Native "preview_identity2" { git -C $clone config user.name "aiye-world-sync preview" } | Out-Null

        $before = (& git -C $clone rev-parse HEAD 2>$null)
        & $PSCommandPath -WorldRoot $clone -Branch $Branch -PythonExe $PythonExe -ProteusSrc $ProteusSrc -NoPublish
        $code = $LASTEXITCODE
        $after = (& git -C $clone rev-parse HEAD 2>$null)
        $shortlog = ((& git -C $clone log --oneline "$before..$after" 2>$null) -join "; ")
        Write-Log "PREVIEW result exit=$code head_before=$before head_after=$after would_commit=[$shortlog]"
        Write-Log "PREVIEW end; real world at $WorldRoot untouched; clone discarded"
        Remove-Item -Recurse -Force $clone -ErrorAction SilentlyContinue
        Exit-Sync $code
    }

    Set-Location $WorldRoot

    # Python Unicode-safe stdio for Scheduled Task context (non-interactive cp-locale)
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONUTF8 = '1'
    $env:GIT_TERMINAL_PROMPT = '0'

    # Bind the Proteus substrate to the world we were actually pointed at.
    # proteus.paths.world_root() resolves PROTEUS_WORLD_ROOT, else
    # $USERPROFILE\.aiye\world - it does NOT follow the process cwd. Without
    # this line every `proteus world reconcile` / `rebuild-index` below ran
    # against the DEFAULT world no matter what -WorldRoot said, which meant
    # (a) -Preview's isolated clone was a lie for the Python half of the
    # pipeline, and (b) the test harnesses rewrote the live index/ while
    # believing they were sandboxed. Source-of-truth entities/ escaped damage
    # only because reconcile exits non-zero on an absent entity id and the
    # Issue #2 semantic-change guard suppresses no-op writes.
    $env:PROTEUS_WORLD_ROOT = $WorldRoot

    Write-Log "sync start branch=$Branch no_publish=$NoPublish pid=$PID host=$env:COMPUTERNAME user=$env:USERNAME"

    # --- pre-flight ledger integrity: never merge on top of an already-corrupt ledger ---
    $e = Test-ClaimsIntegrity "pre"
    if ($e -ne 0) { Write-Log "CLAIMS_PREFLIGHT_FAIL exit=$e"; Exit-Sync 8 }

    # --- fetch ---
    $exit = Invoke-Native "fetch" { git fetch origin }
    if ($exit -ne 0) { Write-Log "FETCH_FAIL exit=$exit"; Exit-Sync 3 }

    # --- merge ALL remote refs (claims resolved as append-only records) ---
    # Capture the pre-merge tip so the reconcile diff below covers every merge we
    # just performed. The old code diffed HEAD@{1}..HEAD, which only ever saw the
    # LAST merge commit and silently skipped entities whose claims arrived in an
    # earlier merge of the same cycle.
    $preMergeHead = (& git rev-parse HEAD 2>$null)
    $exit = Invoke-MergeRemotes -Branch $Branch
    if ($exit -ne 0) { Write-Log "MERGE_STAGE_FAIL exit=$exit"; Exit-Sync $exit }

    # --- post-merge ledger integrity. This is the gate that catches the
    # merge=union trailing-newline corruption, which raises NO git conflict. ---
    $e = Test-ClaimsIntegrity "post_merge"
    if ($e -ne 0) { Write-Log "CLAIMS_POSTMERGE_FAIL exit=$e (publication refused)"; Exit-Sync 8 }

    # --- reconcile entities that received new claims from the merge ---
    $changedEntities = @()
    if (-not $preMergeHead) { $preMergeHead = "HEAD@{1}" }
    $diff = @(& git diff --name-only $preMergeHead HEAD 2>$null)
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
    if ($exit -ne 0) { Write-Log "REBUILD_FAIL exit=$exit"; Exit-Sync 4 }

    # --- commit local changes (reconcile may have rewritten claim statuses) ---
    $status = (& git status --porcelain) -join "`n"
    if ($status) {
        $e = Invoke-Native "add" { git add -A }
        if ($e -ne 0) { Write-Log "ADD_FAIL exit=$e"; Exit-Sync 3 }
        $e = Invoke-Native "commit" { git commit -m "sync $(Now) reconcile" }
        if ($e -ne 0) { Write-Log "COMMIT_FAIL exit=$e"; Exit-Sync 3 }
    }

    if ($NoPublish) {
        # LOCAL-MUTATING stop point. Local git state HAS changed above.
        Write-Log "NO_PUBLISH end; local state mutated (merge/reconcile/commit applied); no push performed"
        if ($reconcileDegraded) { Exit-Sync 6 }
        Exit-Sync 0
    }

    # --- push host branch, with bounded retry against a concurrent remote writer.
    # A non-fast-forward rejection means another host published between our fetch
    # and our push. Re-fetch, re-merge (append-only), re-validate, retry. No
    # force-push: a lost commit is worse than a failed cycle. ---
    $pushed = $false
    $maxAttempts = [Math]::Max(1, $PushRetries)
    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        $exit = Invoke-Native "push" { git push origin $Branch }
        if ($exit -eq 0) { $pushed = $true; break }
        Write-Log "PUSH_REJECTED attempt=$attempt/$maxAttempts exit=$exit (likely non-fast-forward: concurrent remote writer)"
        if ($attempt -ge $maxAttempts) { break }

        $e = Invoke-Native "refetch" { git fetch origin }
        if ($e -ne 0) { Write-Log "REFETCH_FAIL exit=$e"; Exit-Sync 3 }
        $e = Invoke-MergeRemotes -Branch $Branch
        if ($e -ne 0) { Write-Log "REMERGE_FAIL exit=$e"; Exit-Sync $e }
        $e = Test-ClaimsIntegrity "post_remerge"
        if ($e -ne 0) { Write-Log "CLAIMS_POSTREMERGE_FAIL exit=$e"; Exit-Sync 8 }

        $st = (& git status --porcelain) -join "`n"
        if ($st) {
            $e = Invoke-Native "readd_retry" { git add -A }
            if ($e -ne 0) { Write-Log "ADD_FAIL exit=$e"; Exit-Sync 3 }
            $e = Invoke-Native "commit_retry" { git commit -m "sync $(Now) remerge" }
            if ($e -ne 0) { Write-Log "COMMIT_FAIL exit=$e"; Exit-Sync 3 }
        }
    }
    if (-not $pushed) { Write-Log "PUSH_FAIL exhausted attempts=$maxAttempts"; Exit-Sync 3 }

    # --- publish main; main is REQUIRED by the cross-host read contract.
    # A failed push to main must surface as a non-zero exit so the Scheduler
    # does not record LastTaskResult=0 on partial publication.
    $pushMainExit = Invoke-Native "push_main" { git push origin "$($Branch):main" }
    if ($pushMainExit -ne 0) {
        Write-Log "PUSH_MAIN_FAIL exit=$pushMainExit (cross-host contract requires main)"
    }

    # --- publication readback: strict equality on all three refs ---
    $localHead = (& git rev-parse $Branch 2>$null).Trim()
    if (-not $localHead) { Write-Log "REV_PARSE_FAIL branch=$Branch"; Exit-Sync 5 }
    $remoteHostLine = (& git ls-remote --heads origin $Branch 2>$null)
    if (-not $remoteHostLine) { Write-Log "LS_REMOTE_FAIL branch=$Branch"; Exit-Sync 5 }
    $remoteHostHead = ($remoteHostLine -split "\s+")[0]
    $remoteMainLine = (& git ls-remote --heads origin main 2>$null)
    if (-not $remoteMainLine) { Write-Log "LS_REMOTE_FAIL branch=main"; Exit-Sync 5 }
    $remoteMainHead = ($remoteMainLine -split "\s+")[0]
    Write-Log "readback local=$localHead remote_host=$remoteHostHead remote_main=$remoteMainHead"
    if ($localHead -ne $remoteHostHead) {
        Write-Log "READBACK_FAIL remote $Branch not at local HEAD"; Exit-Sync 5
    }
    if ($localHead -ne $remoteMainHead) {
        Write-Log "READBACK_FAIL remote main ($remoteMainHead) != local HEAD ($localHead)"; Exit-Sync 5
    }

    # Assert no stranded intended changes remain uncommitted.
    $postStatus = (& git status --porcelain 2>$null) -join "`n"
    if ($postStatus) {
        Write-Log "STRANDED_CHANGES post-sync:`n$postStatus"; Exit-Sync 5
    }

    if ($reconcileDegraded) {
        Write-Log "sync end DEGRADED local=$localHead (reconcile warnings; publication contract satisfied)"
        Exit-Sync 6
    }
    Write-Log "sync end OK local=$localHead"
    Exit-Sync 0

} catch {
    Write-Log "UNHANDLED_EXCEPTION: $($_ | Out-String)"
    Exit-Sync 7
}

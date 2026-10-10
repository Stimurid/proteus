# test_dualref_sync.ps1 - Issue #3 regression suite for aiye-world-sync.ps1
#
# Reproduces the 2026-10-10T07:06Z production failure in isolation, using a real
# bare origin and TWO independent writer repos, then asserts the repaired
# behaviour. Run against the OLD script and it MUST fail S1/S2/S3; run against the
# repaired script and every scenario MUST pass.
#
#   pwsh/powershell -File tests\test_dualref_sync.ps1 [-SyncScript <path>]
#
# Nothing here touches the production world: every scenario builds its own
# throwaway world under $env:TEMP and the script under test binds
# PROTEUS_WORLD_ROOT to it. S7 proves that explicitly.

[CmdletBinding()]
param(
    [string]$SyncScript = (Join-Path $PSScriptRoot "..\scripts\aiye-world-sync.ps1"),
    [string]$PythonExe  = "C:\Users\Homee\AppData\Local\Programs\Python\Python314\python.exe",
    [string]$ProteusSrc = (Join-Path $PSScriptRoot "..\src"),
    [string]$Branch     = "host/aorus",
    [switch]$ExpectLegacy   # invert S1/S2/S3 expectations: assert the OLD bug is present
)

$ErrorActionPreference = 'Continue'
$SyncScript = (Resolve-Path $SyncScript).Path
$ProteusSrc = (Resolve-Path $ProteusSrc).Path
$script:Pass = 0
$script:Fail = 0
$script:Failures = @()

function Ok($name, $detail)   { $script:Pass++; Write-Host "  PASS  $name  $detail" }
function Bad($name, $detail)  { $script:Fail++; $script:Failures += "$name :: $detail"; Write-Host "  FAIL  $name  $detail" }
function Assert($cond, $name, $detail) { if ($cond) { Ok $name $detail } else { Bad $name $detail } }

# Deliberately a SIMPLE function (no [Parameter()] attribute). Adding one makes it
# an advanced function, which silently gains the common parameters - and then a git
# flag like `-d` binds to `-Debug` instead of being passed through to git. That bug
# made `update-ref -d` a no-op here and quietly weakened S5.
# Also note the name is RunGit, not Git: PowerShell is case-insensitive, so a
# function named `Git` shadows git.exe and `& git ...` inside it recurses forever.
function RunGit {
    param([string]$Repo)
    $out = & git.exe -C $Repo @args 2>&1
    $script:GitExit = $LASTEXITCODE
    return ($out -join "`n")
}
function IsAncestor { param([string]$Repo, [string]$Anc, [string]$Desc)
    & git.exe -C $Repo merge-base --is-ancestor $Anc $Desc 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0) }
function BareSha { param([string]$Origin, [string]$Ref)
    $v = & git.exe --git-dir=$Origin rev-parse --verify --quiet $Ref 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }; return "$v".Trim() }

function Claim([string]$id, [string]$body) {
    (@{ claim_id = $id; subject = "entity.test.widget"; body = $body;
        status = "current"; recorded_utc = (Get-Date).ToUniversalTime().ToString("o") } |
        ConvertTo-Json -Compress)
}

# Build: bare origin + hostA (under test) + hostB (concurrent writer).
function New-Env {
    $root   = Join-Path $env:TEMP ("dualref-" + [guid]::NewGuid().ToString("N").Substring(0, 10))
    $origin = Join-Path $root "origin.git"
    $A      = Join-Path $root "hostA"
    $B      = Join-Path $root "hostB"
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    & git.exe init --bare -q $origin 2>&1 | Out-Null

    New-Item -ItemType Directory -Force -Path (Join-Path $A "entities\entity.test.widget") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $A "index") | Out-Null
    Set-Content -Path (Join-Path $A "config.json") -Value '{"schema":"proteus.entity.v0.1"}' -Encoding ascii
    # store.mount() hard-requires carriers.json / projects.json / secret_refs.json.
    # Without them `proteus world reconcile` raises FileNotFoundError, the sync
    # reports DEGRADED (exit 6) and the suite cannot distinguish that from a real
    # reconcile regression.
    $ed = Join-Path $A "entities\entity.test.widget"
    Set-Content -Path (Join-Path $ed "identity.json") `
        -Value '{"entity_id":"entity.test.widget","name":"widget","aliases":["widget"]}' -Encoding ascii
    Set-Content -Path (Join-Path $ed "carriers.json") `
        -Value '{"schema":"proteus.entity.v0.1","entity_id":"entity.test.widget","carriers":[]}' -Encoding ascii
    Set-Content -Path (Join-Path $ed "projects.json") `
        -Value '{"schema":"proteus.entity.v0.1","entity_id":"entity.test.widget","projects":[]}' -Encoding ascii
    Set-Content -Path (Join-Path $ed "secret_refs.json") `
        -Value '{"schema":"proteus.entity.v0.1","entity_id":"entity.test.widget","secret_refs":[]}' -Encoding ascii
    Set-Content -Path (Join-Path $ed "ENTITY.md")     -Value "# widget"     -Encoding ascii
    Set-Content -Path (Join-Path $ed "unresolved.md") -Value "# unresolved" -Encoding ascii
    # merge=union + trailing newline are what keep claims append-only under git
    Set-Content -Path (Join-Path $A ".gitattributes") -Value "*.jsonl merge=union" -Encoding ascii
    # Mirror the production world's ignore scope. Without this the script's own
    # .sync.log lands untracked in the world root and the final "no stranded
    # changes" assertion trips with exit 5 - a fixture artefact, not a defect.
    Set-Content -Path (Join-Path $A ".gitignore") `
        -Value @("config.json", "index/", "pending_drive_uploads/", "_drive_staging/", ".sync.log") `
        -Encoding ascii
    Set-Content -Path (Join-Path $A "entities\entity.test.widget\claims.jsonl") `
        -Value (Claim "claim.seed" "seed claim") -Encoding ascii

    & git.exe init -q -b $Branch $A 2>&1 | Out-Null
    RunGit $A config user.email "test@line-a.local" | Out-Null
    RunGit $A config user.name  "dualref test"      | Out-Null
    RunGit $A remote add origin $origin             | Out-Null
    RunGit $A add -A                                | Out-Null
    RunGit $A commit -q -m "seed"                   | Out-Null
    RunGit $A push -q origin "$Branch"              | Out-Null
    RunGit $A push -q origin "$($Branch):main"      | Out-Null

    & git.exe clone -q --branch $Branch $origin $B 2>&1 | Out-Null
    RunGit $B config user.email "hostb@line-a.local" | Out-Null
    RunGit $B config user.name  "host B"             | Out-Null
    return @{ Root = $root; Origin = $origin; A = $A; B = $B }
}

# hostB publishes to the HOST branch only - main deliberately left behind.
# This is the exact production shape: remote host/aorus=3b3da59 ahead,
# remote main=a6418d5 equal to local.
function Advance-HostBranchOnly {
    param($E, [string]$File = "entities\entity.test.widget\hostb-artifact.txt", [string]$Text = "hostB human artifact")
    $p = Join-Path $E.B $File
    New-Item -ItemType Directory -Force -Path (Split-Path $p) | Out-Null
    Set-Content -Path $p -Value $Text -Encoding ascii
    RunGit $E.B add -A | Out-Null
    RunGit $E.B commit -q -m "hostB: $Text" | Out-Null
    RunGit $E.B push -q origin "$Branch" | Out-Null
    return (RunGit $E.B rev-parse HEAD).Trim()
}

function Invoke-Sync {
    param($E, [string[]]$Extra = @())
    $out = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $SyncScript `
        -WorldRoot $E.A -Branch $Branch -PythonExe $PythonExe -ProteusSrc $ProteusSrc @Extra 2>&1
    return @{ Exit = $LASTEXITCODE; Out = ($out -join "`n") }
}

# NOTE: deliberately NOT Remove-Item -Recurse -Force. On Windows that can spin for
# minutes on a git object store (read-only loose objects + deep nesting). The .NET
# call is both fast and predictable.
function Cleanup($E) {
    if (-not $E -or -not $E.Root) { return }
    try { [System.IO.Directory]::Delete($E.Root, $true) } catch { }
}

Write-Host ""
Write-Host "=== dual-ref sync suite ==="
Write-Host "script under test: $SyncScript"
Write-Host "legacy-expectation mode: $ExpectLegacy"
Write-Host ""

# ---------------------------------------------------------------- S1
# Remote host branch ahead, remote main stale. The production failure.
Write-Host "S1 REMOTE_HOST_AHEAD (the live 07:06Z failure)"
$E = New-Env
$bSha = Advance-HostBranchOnly $E
$localBefore = (RunGit $E.A rev-parse HEAD).Trim()
Assert ((BareSha $E.Origin "refs/heads/$Branch") -eq $bSha) "S1.setup.remote_host_ahead" "remote host=$bSha"
Assert ((BareSha $E.Origin "refs/heads/main") -eq $localBefore) "S1.setup.remote_main_stale" "remote main=$localBefore"

$r = Invoke-Sync $E
if ($ExpectLegacy) {
    Assert ($r.Exit -eq 3) "S1.legacy.exit3" "exit=$($r.Exit) (old main-only merge cannot converge)"
    Assert ($r.Out -match "PUSH_FAIL exhausted") "S1.legacy.push_exhausted" "retries all rejected"
    Assert (($r.Out | Select-String -AllMatches "Already up to date").Matches.Count -ge 2) `
        "S1.legacy.noop_remerge" "retry re-merged origin/main only"
} else {
    Assert ($r.Exit -eq 0) "S1.exit0" "exit=$($r.Exit)"
    $lo = (RunGit $E.A rev-parse HEAD).Trim()
    $rh = BareSha $E.Origin "refs/heads/$Branch"
    $rm = BareSha $E.Origin "refs/heads/main"
    Assert ($lo -eq $rh -and $lo -eq $rm) "S1.three_refs_equal" "local=$lo host=$rh main=$rm"
    Assert (Test-Path (Join-Path $E.A "entities\entity.test.widget\hostb-artifact.txt")) `
        "S1.remote_commit_preserved" "hostB artifact survived (no force-push)"
    Assert (IsAncestor $E.A $bSha "HEAD") `
        "S1.remote_sha_is_ancestor" "$bSha reachable from new tip"
    Assert (IsAncestor $E.A $localBefore "HEAD") `
        "S1.local_sha_is_ancestor" "local history not rewritten"
}
Cleanup $E

# ---------------------------------------------------------------- S2
# Append-only claims: both hosts add a DIFFERENT claim. Both must survive.
Write-Host "S2 APPEND_ONLY_CLAIMS (NO_LAST_WRITE_WINS)"
$E = New-Env
$cf = "entities\entity.test.widget\claims.jsonl"
$bp = Join-Path $E.B $cf
Set-Content -Path $bp -Value ((Claim "claim.seed" "seed claim"), (Claim "claim.fromB" "hostB claim")) -Encoding ascii
RunGit $E.B add -A | Out-Null; RunGit $E.B commit -q -m "hostB claim" | Out-Null; RunGit $E.B push -q origin "$Branch" | Out-Null
$ap = Join-Path $E.A $cf
Set-Content -Path $ap -Value ((Claim "claim.seed" "seed claim"), (Claim "claim.fromA" "hostA claim")) -Encoding ascii
RunGit $E.A add -A | Out-Null; RunGit $E.A commit -q -m "hostA claim" | Out-Null

$r = Invoke-Sync $E
if ($ExpectLegacy) {
    Assert ($r.Exit -ne 0) "S2.legacy.nonzero" "exit=$($r.Exit) (cannot publish)"
} else {
    Assert ($r.Exit -eq 0) "S2.exit0" "exit=$($r.Exit)"
    $txt = Get-Content $ap -Raw
    Assert ($txt -match "claim\.fromA") "S2.local_claim_survived" "claim.fromA present"
    Assert ($txt -match "claim\.fromB") "S2.remote_claim_survived" "claim.fromB present"
    Assert ($txt -match "claim\.seed")  "S2.seed_claim_survived"   "claim.seed present"
    Assert ($txt.EndsWith("`n") -or $txt.EndsWith("`r`n")) "S2.trailing_newline" "ledger ends with newline"
}
Cleanup $E

# ---------------------------------------------------------------- S3
# Race: hostB publishes BETWEEN our fetch and our push (pre-push hook).
Write-Host "S3 PUSH_RACE (writer lands between fetch and push)"
$E = New-Env
$flag = (Join-Path $E.Root "raced.flag") -replace '\\', '/'
$bfwd = ($E.B) -replace '\\', '/'
$hook = Join-Path $E.A ".git\hooks\pre-push"
@"
#!/bin/sh
if [ ! -f "$flag" ]; then
  touch "$flag"
  printf 'raced\n' > "$bfwd/entities/entity.test.widget/race.txt"
  git -C "$bfwd" add -A >/dev/null 2>&1
  git -C "$bfwd" commit -q -m "hostB race commit" >/dev/null 2>&1
  git -C "$bfwd" push -q origin $Branch >/dev/null 2>&1
fi
exit 0
"@ | Set-Content -Path $hook -Encoding ascii
$p = Join-Path $E.A "entities\entity.test.widget\localwork.txt"
Set-Content -Path $p -Value "hostA work" -Encoding ascii
RunGit $E.A add -A | Out-Null; RunGit $E.A commit -q -m "hostA work" | Out-Null

$r = Invoke-Sync $E
if ($ExpectLegacy) {
    Assert ($r.Exit -ne 0) "S3.legacy.nonzero" "exit=$($r.Exit)"
} else {
    Assert ($r.Exit -eq 0) "S3.exit0" "exit=$($r.Exit) (converged after race)"
    Assert ($r.Out -match "PUSH_REJECTED") "S3.race_actually_happened" "a push was really rejected"
    $lo = (RunGit $E.A rev-parse HEAD).Trim()
    Assert ($lo -eq (BareSha $E.Origin "refs/heads/$Branch")) "S3.host_ref_converged" "local==remote host"
    Assert ($lo -eq (BareSha $E.Origin "refs/heads/main"))    "S3.main_ref_converged" "local==remote main"
    Assert (Test-Path (Join-Path $E.A "entities\entity.test.widget\race.txt"))      "S3.racer_commit_kept" "race.txt merged in"
    Assert (Test-Path (Join-Path $E.A "entities\entity.test.widget\localwork.txt")) "S3.local_work_kept"   "localwork.txt kept"
}
Cleanup $E

# ---------------------------------------------------------------- S4
# A genuine non-claims conflict must NOT be auto-resolved and must NOT publish.
Write-Host "S4 NON_CLAIM_CONFLICT (refuse, do not guess)"
$E = New-Env
$rel = "entities\entity.test.widget\identity.json"
Set-Content -Path (Join-Path $E.B $rel) -Value '{"entity_id":"entity.test.widget","name":"widget-B"}' -Encoding ascii
RunGit $E.B add -A | Out-Null; RunGit $E.B commit -q -m "B identity" | Out-Null; RunGit $E.B push -q origin "$Branch" | Out-Null
Set-Content -Path (Join-Path $E.A $rel) -Value '{"entity_id":"entity.test.widget","name":"widget-A"}' -Encoding ascii
RunGit $E.A add -A | Out-Null; RunGit $E.A commit -q -m "A identity" | Out-Null
$remoteBefore = BareSha $E.Origin "refs/heads/$Branch"

$r = Invoke-Sync $E
if ($ExpectLegacy) {
    # The legacy script never even SEES this conflict: it merges only origin/main,
    # so it dies earlier at the rejected push (exit 3). The invariant that must
    # hold either way is "no false green" + "remote not corrupted".
    Assert ($r.Exit -ne 0) "S4.legacy.no_false_green" "exit=$($r.Exit) (fails before reaching the conflict)"
} else {
    Assert ($r.Exit -eq 2) "S4.exit2_operator_review" "exit=$($r.Exit)"
    Assert ($r.Out -match "NON_CLAIM_CONFLICT") "S4.logged" "conflict surfaced in log"
}
Assert ((BareSha $E.Origin "refs/heads/$Branch") -eq $remoteBefore) "S4.remote_untouched" "no partial publication"
Assert ((RunGit $E.A status --porcelain) -notmatch "^UU") "S4.merge_aborted" "working tree left clean of conflict stages"
Cleanup $E

# ---------------------------------------------------------------- S5
# Host branch absent on remote (first publication) must be skipped, not fatal.
Write-Host "S5 ABSENT_REMOTE_HOST_REF (first publication)"
$E = New-Env
# The bare repo's HEAD symrefs to the host branch (first push set it), and git
# will not delete the branch HEAD points at. Repoint HEAD at main first.
& git.exe --git-dir=$($E.Origin) symbolic-ref HEAD refs/heads/main 2>&1 | Out-Null
& git.exe --git-dir=$($E.Origin) update-ref -d "refs/heads/$Branch" 2>&1 | Out-Null
RunGit $E.A update-ref -d "refs/remotes/origin/$Branch" | Out-Null
# Self-check: if the setup did not actually remove the ref, the scenario would
# silently degenerate into "ordinary fast-forward push" and prove nothing.
Assert ($null -eq (BareSha $E.Origin "refs/heads/$Branch")) "S5.setup.host_ref_deleted" "remote host branch really gone"
$p = Join-Path $E.A "entities\entity.test.widget\first.txt"
Set-Content -Path $p -Value "first publication" -Encoding ascii
RunGit $E.A add -A | Out-Null; RunGit $E.A commit -q -m "first" | Out-Null

$r = Invoke-Sync $E
if ($ExpectLegacy) {
    # Legacy is not required to handle this case well; it is only required never to
    # claim success while the refs disagree.
    $lo = (RunGit $E.A rev-parse HEAD).Trim()
    $conv = ($lo -eq (BareSha $E.Origin "refs/heads/$Branch")) -and ($lo -eq (BareSha $E.Origin "refs/heads/main"))
    Assert ($r.Exit -ne 0 -or $conv) "S5.legacy.no_false_green" "exit=$($r.Exit) converged=$conv"
} else {
    Assert ($r.Exit -eq 0) "S5.exit0" "exit=$($r.Exit)"
    $mergeLines = @($r.Out -split "`n" | Where-Object { $_ -match "merge" })
    foreach ($ml in $mergeLines) { Write-Host "    [S5 merge log] $ml" }
    Assert ($r.Out -match "merge_skip ref=origin/$([regex]::Escape($Branch))") "S5.skipped_absent_ref" "absent ref skipped not failed"
    $lo = (RunGit $E.A rev-parse HEAD).Trim()
    Assert ($lo -eq (BareSha $E.Origin "refs/heads/$Branch")) "S5.host_published" "host branch created"
    Assert ($lo -eq (BareSha $E.Origin "refs/heads/main"))    "S5.main_published" "main published"
}
Cleanup $E

# ---------------------------------------------------------------- S6
# Corrupt ledger (missing trailing newline - the merge=union hazard) must block
# publication with exit 8 BEFORE anything reaches the remote.
Write-Host "S6 LEDGER_INTEGRITY_GATE (exit 8, refuse to publish)"
$E = New-Env
$ap = Join-Path $E.A "entities\entity.test.widget\claims.jsonl"
[System.IO.File]::WriteAllText($ap, (Claim "claim.seed" "seed claim"))  # no trailing newline
RunGit $E.A add -A | Out-Null; RunGit $E.A commit -q -m "corrupt ledger" | Out-Null
$remoteBefore = BareSha $E.Origin "refs/heads/$Branch"

$r = Invoke-Sync $E
Assert ($r.Exit -eq 8) "S6.exit8" "exit=$($r.Exit)"
Assert ((BareSha $E.Origin "refs/heads/$Branch") -eq $remoteBefore) "S6.remote_untouched" "publication refused"
Cleanup $E

# ---------------------------------------------------------------- S7
# The suite must not have written to the REAL production world index.
Write-Host "S7 PRODUCTION_WORLD_UNTOUCHED"
$realIdx = Join-Path $env:USERPROFILE ".aiye\world\index\INDEX_RECEIPT.json"
if (Test-Path $realIdx) {
    $age = ((Get-Date).ToUniversalTime() - (Get-Item $realIdx).LastWriteTimeUtc).TotalSeconds
    Assert ($age -gt 5) "S7.real_index_not_rewritten" "real INDEX_RECEIPT.json last written ${age}s ago"
} else {
    Ok "S7.real_index_absent" "no production index present to damage"
}

Write-Host ""
Write-Host "=== RESULT: pass=$script:Pass fail=$script:Fail ==="
if ($script:Fail -gt 0) { $script:Failures | ForEach-Object { Write-Host "  - $_" }; exit 1 }
exit 0

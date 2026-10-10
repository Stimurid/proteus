# test_sync_failure_matrix.ps1 — isolated failure injection for aiye-world-sync.ps1
#
# Builds a disposable local git world (bare remote + working clone) with
# fixture entities, runs the real sync script against it under each failure
# scenario, and asserts the expected exit code + log signature.
#
# NO changes to the production ~/.aiye/world or Stimurid/aiye-world.
#
# Run:
#   powershell -NoProfile -ExecutionPolicy Bypass -File tests\test_sync_failure_matrix.ps1

[CmdletBinding()]
param()

# Test harness itself must NOT use Stop: native git stderr (CRLF/warnings) is
# data, not errors. Keeping the harness non-strict mirrors our production fix.
$ErrorActionPreference = 'Continue'
$script:ProteusRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$script:Script = Join-Path $script:ProteusRoot 'scripts\aiye-world-sync.ps1'
$script:PythonExe = "C:\Users\Homee\AppData\Local\Programs\Python\Python314\python.exe"
$script:ProteusSrc = Join-Path $script:ProteusRoot 'src'

$results = @()
function Assert-Case {
    param([string]$Name, [int]$ExpectedExit, [int]$ActualExit, [string]$LogTail, [string]$Expect)
    $pass = ($ExpectedExit -eq $ActualExit) -and ($Expect -eq "" -or $LogTail -match $Expect)
    $script:results += [pscustomobject]@{
        Case     = $Name
        Expected = $ExpectedExit
        Actual   = $ActualExit
        Pattern  = $Expect
        Status   = $(if ($pass) { "PASS" } else { "FAIL" })
    }
    Write-Host ("[$($script:results[-1].Status)] $Name expected=$ExpectedExit actual=$ActualExit")
    if (-not $pass) {
        Write-Host "  log tail: $LogTail"
    }
}

function New-TestWorld {
    param([string]$Suffix)
    $base = Join-Path $env:TEMP "aiye-sync-test-$Suffix-$(Get-Random)"
    New-Item -ItemType Directory -Force -Path "$base\remote" | Out-Null
    New-Item -ItemType Directory -Force -Path "$base\world" | Out-Null
    git -C "$base\remote" init --bare -b main 2>&1 | Out-Null
    git -C "$base\world" init -b host/aorus 2>&1 | Out-Null
    git -C "$base\world" config user.email "test@line-a.local" 2>&1 | Out-Null
    git -C "$base\world" config user.name "Line A Test" 2>&1 | Out-Null
    git -C "$base\world" remote add origin "$base\remote" 2>&1 | Out-Null
    New-Item -ItemType Directory -Force -Path "$base\world\entities\entity.test\" | Out-Null
    @'
{"schema":"proteus.entity.v0.1","entity_id":"entity.test","display_name":"Test Entity","aliases":["test"],"relations":[],"created_utc":"2026-10-10T00:00:00Z","note":"fixture"}
'@ | Out-File "$base\world\entities\entity.test\identity.json" -Encoding ascii
    '{"claim_id":"claim.test.seed","entity_id":"entity.test","scope":"ENTITY","topic":"seed","text":"seed","status":"current","conflicts_with":[],"provenance":{"observer":"test","kind":"fact","confidence":"high"},"recorded_utc":"2026-10-10T00:00:00Z"}' |
        Out-File "$base\world\entities\entity.test\claims.jsonl" -Encoding ascii
    '{"schema":"proteus.entity.v0.1","entity_id":"entity.test","carriers":[]}' | Out-File "$base\world\entities\entity.test\carriers.json" -Encoding ascii
    '{"schema":"proteus.entity.v0.1","entity_id":"entity.test","projects":[]}' | Out-File "$base\world\entities\entity.test\projects.json" -Encoding ascii
    '{"schema":"proteus.entity.v0.1","entity_id":"entity.test","secret_refs":[]}' | Out-File "$base\world\entities\entity.test\secret_refs.json" -Encoding ascii
    '# Test entity' | Out-File "$base\world\entities\entity.test\ENTITY.md" -Encoding ascii
    '# Unresolved' | Out-File "$base\world\entities\entity.test\unresolved.md" -Encoding ascii
    "*.log`nindex/`npending_drive_uploads/`n" | Out-File "$base\world\.gitignore" -Encoding ascii
    git -C "$base\world" add -A 2>&1 | Out-Null
    git -C "$base\world" commit -m "seed" 2>&1 | Out-Null
    git -C "$base\world" push -u origin host/aorus 2>&1 | Out-Null
    git -C "$base\world" push origin "host/aorus:main" 2>&1 | Out-Null
    return $base
}

function Invoke-SyncOnWorld {
    param([string]$WorldRoot, [switch]$DryRun)
    $args = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $script:Script,
              '-WorldRoot', $WorldRoot,
              '-PythonExe', $script:PythonExe,
              '-ProteusSrc', $script:ProteusSrc)
    if ($DryRun) { $args += '-DryRun' }
    $p = Start-Process -FilePath 'powershell.exe' -ArgumentList $args -Wait -PassThru -NoNewWindow
    $log = Join-Path $WorldRoot ".sync.log"
    $tail = ""
    if (Test-Path $log) { $tail = (Get-Content $log -Tail 30) -join "`n" }
    return @{ Exit = $p.ExitCode; LogTail = $tail }
}

# --- CASE: clean happy path ---
$base = New-TestWorld "happy"
try {
    $r = Invoke-SyncOnWorld "$base\world"
    Assert-Case "happy-path" 0 $r.Exit $r.LogTail "sync end OK"
} finally { Remove-Item -Recurse -Force $base -ErrorAction SilentlyContinue }

# --- CASE: -DryRun is now a deprecated alias for -Preview (Issue #1 round 3).
# It must still not commit or push, and it must announce the rename rather
# than emitting the old DRY_RUN signature, because the old mode silently
# ran fetch+merge+reconcile+rebuild against the real world before its gate. ---
$base = New-TestWorld "dryrun"
try {
    $claimLine = '{"claim_id":"claim.test.dry","entity_id":"entity.test","scope":"ENTITY","topic":"dry","text":"dry","status":"current","conflicts_with":[],"provenance":{"observer":"test","kind":"fact","confidence":"high"},"recorded_utc":"2026-10-10T00:00:00Z"}'
    Add-Content "$base\world\entities\entity.test\claims.jsonl" -Value $claimLine
    $headBefore = (git -C "$base\world" rev-parse HEAD).Trim()
    $r = Invoke-SyncOnWorld "$base\world" -DryRun
    $headAfter = (git -C "$base\world" rev-parse HEAD).Trim()
    Assert-Case "dryrun-no-push" 0 $r.Exit $r.LogTail "DRYRUN_DEPRECATED"
    if ($headBefore -ne $headAfter) {
        $script:results += [pscustomobject]@{ Case="dryrun-head-unchanged"; Expected="eq"; Actual="diff"; Pattern=""; Status="FAIL" }
        Write-Host "[FAIL] dryrun-head-unchanged: HEAD moved $headBefore -> $headAfter"
    } else {
        $script:results += [pscustomobject]@{ Case="dryrun-head-unchanged"; Expected="eq"; Actual="eq"; Pattern=""; Status="PASS" }
        Write-Host "[PASS] dryrun-head-unchanged"
    }
} finally { Remove-Item -Recurse -Force $base -ErrorAction SilentlyContinue }

# --- CASE: push to main rejected (bare repo refuses main writes via hook) ---
$base = New-TestWorld "pushmain-reject"
try {
    # Install a pre-receive hook on the bare remote that rejects any push to main.
    # This models a protected-branch policy (main requires PR / signed / etc.)
    # without requiring GitHub config.
    $hookPath = "$base\remote\hooks\pre-receive"
    @"
#!/bin/sh
while read oldrev newrev refname; do
    if [ "`$refname" = "refs/heads/main" ]; then
        echo "pre-receive: main is protected" >&2
        exit 1
    fi
done
"@ | Out-File $hookPath -Encoding ascii -NoNewline
    # Make hook executable (git for Windows uses msys permissions bits)
    git -C "$base\remote" update-server-info 2>&1 | Out-Null
    # Add a claim so sync has something to push
    $claimLine = '{"claim_id":"claim.test.pushreject","entity_id":"entity.test","scope":"ENTITY","topic":"r","text":"r","status":"current","conflicts_with":[],"provenance":{"observer":"test","kind":"fact","confidence":"high"},"recorded_utc":"2026-10-10T00:00:00Z"}'
    Add-Content "$base\world\entities\entity.test\claims.jsonl" -Value $claimLine
    $r = Invoke-SyncOnWorld "$base\world"
    # Expected: push to host/aorus OK; push_main fails via hook; readback
    # detects remote main != local HEAD; exits 5.
    Assert-Case "push-main-rejected" 5 $r.Exit $r.LogTail "READBACK_FAIL remote main"
} finally { Remove-Item -Recurse -Force $base -ErrorAction SilentlyContinue }

# --- CASE: idempotence — identical input twice produces no new semantic diff ---
$base = New-TestWorld "idempotent"
try {
    # first sync establishes baseline
    $r1 = Invoke-SyncOnWorld "$base\world"
    $head1 = (git -C "$base\world" rev-parse HEAD).Trim()
    # second sync without any new claims — should NOT create new semantic commit
    $r2 = Invoke-SyncOnWorld "$base\world"
    $head2 = (git -C "$base\world" rev-parse HEAD).Trim()
    Assert-Case "idempotent-exit" 0 $r2.Exit $r2.LogTail "sync end OK"
    if ($head1 -eq $head2) {
        $script:results += [pscustomobject]@{ Case="idempotent-head"; Expected="eq"; Actual="eq"; Pattern=""; Status="PASS" }
        Write-Host "[PASS] idempotent-head (no churn commit)"
    } else {
        $script:results += [pscustomobject]@{ Case="idempotent-head"; Expected="eq"; Actual="diff"; Pattern=""; Status="FAIL" }
        Write-Host "[FAIL] idempotent-head: $head1 -> $head2 (churn commit created)"
    }
} finally { Remove-Item -Recurse -Force $base -ErrorAction SilentlyContinue }

# --- CASE: new claim produces exactly one new semantic commit ---
$base = New-TestWorld "newclaim"
try {
    $r1 = Invoke-SyncOnWorld "$base\world"
    $head1 = (git -C "$base\world" rev-parse HEAD).Trim()
    $claimLine = '{"claim_id":"claim.test.new","entity_id":"entity.test","scope":"ENTITY","topic":"n","text":"new","status":"current","conflicts_with":[],"provenance":{"observer":"test","kind":"fact","confidence":"high"},"recorded_utc":"2026-10-10T00:00:00Z"}'
    Add-Content "$base\world\entities\entity.test\claims.jsonl" -Value $claimLine
    $r2 = Invoke-SyncOnWorld "$base\world"
    $head2 = (git -C "$base\world" rev-parse HEAD).Trim()
    Assert-Case "newclaim-exit" 0 $r2.Exit $r2.LogTail "sync end OK"
    if ($head1 -ne $head2) {
        $script:results += [pscustomobject]@{ Case="newclaim-advances-head"; Expected="diff"; Actual="diff"; Pattern=""; Status="PASS" }
        Write-Host "[PASS] newclaim-advances-head"
    } else {
        $script:results += [pscustomobject]@{ Case="newclaim-advances-head"; Expected="diff"; Actual="eq"; Pattern=""; Status="FAIL" }
        Write-Host "[FAIL] newclaim-advances-head: HEAD did not move"
    }
} finally { Remove-Item -Recurse -Force $base -ErrorAction SilentlyContinue }

# --- SUMMARY ---
Write-Host ""
Write-Host "========== RESULT MATRIX =========="
$results | Format-Table -AutoSize
$fails = @($results | Where-Object { $_.Status -eq "FAIL" })
if ($fails.Count -gt 0) {
    Write-Host "`n$($fails.Count) FAIL(s)"
    exit 1
}
Write-Host "`nALL PASS"
exit 0

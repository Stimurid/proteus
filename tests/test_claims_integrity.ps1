# test_claims_integrity.ps1 - Issue #1 round 3 negative tests.
#
# Covers the two false-SUCCESS paths that round 2 left open, plus the new
# modes and the push-retry path. Every case builds a disposable local bare
# remote + working clone under $env:TEMP.
#
# NO changes to the production ~/.aiye/world or to Stimurid/aiye-world.
#
# Run:
#   powershell -NoProfile -ExecutionPolicy Bypass -File tests\test_claims_integrity.ps1

[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'
$script:ProteusRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$script:Script      = Join-Path $script:ProteusRoot 'scripts\aiye-world-sync.ps1'
$script:ClaimsTool  = Join-Path $script:ProteusRoot 'scripts\claims_jsonl.py'
$script:PythonExe   = "C:\Users\Homee\AppData\Local\Programs\Python\Python314\python.exe"
$script:ProteusSrc  = Join-Path $script:ProteusRoot 'src'

$script:results = @()
function Assert-Case {
    param([string]$Name, $Expected, $Actual, [string]$Note = "")
    $pass = ("$Expected" -eq "$Actual")
    $script:results += [pscustomobject]@{
        Case = $Name; Expected = $Expected; Actual = $Actual; Status = $(if ($pass) { "PASS" } else { "FAIL" })
    }
    Write-Host ("[{0}] {1} expected={2} actual={3} {4}" -f $script:results[-1].Status, $Name, $Expected, $Actual, $Note)
}

function New-World {
    param([string]$Suffix, [switch]$WithUnionAttr)
    $base = Join-Path $env:TEMP "claims-test-$Suffix-$(Get-Random)"
    New-Item -ItemType Directory -Force -Path "$base\remote" | Out-Null
    New-Item -ItemType Directory -Force -Path "$base\world\entities\entity.test" | Out-Null
    git -C "$base\remote" init --bare -b main 2>&1 | Out-Null
    git -C "$base\world" init -b host/aorus 2>&1 | Out-Null
    git -C "$base\world" config user.email "test@line-a.local" 2>&1 | Out-Null
    git -C "$base\world" config user.name  "Line A Test"       2>&1 | Out-Null
    git -C "$base\world" config core.autocrlf false            2>&1 | Out-Null
    git -C "$base\world" remote add origin "$base\remote"      2>&1 | Out-Null
    if ($WithUnionAttr) {
        Set-Content -Path "$base\world\.gitattributes" -Value "entities/**/claims.jsonl merge=union" -Encoding ascii -NoNewline:$false
    }
    # Mirror the production world's .gitignore. Without it the script's own
    # .sync.log (written inside WorldRoot) shows up as an untracked file and
    # trips the post-sync STRANDED_CHANGES assertion.
    Set-Content -Path "$base\world\.gitignore" -Value @(".sync.log", "index/", "_drive_staging/", "pending_drive_uploads/") -Encoding ascii
    '{"schema":"proteus.entity.v0.1","entity_id":"entity.test","display_name":"Test Entity","aliases":["test"],"relations":[],"created_utc":"2026-10-10T00:00:00Z"}' |
        Set-Content "$base\world\entities\entity.test\identity.json" -Encoding utf8
    # Full entity file set, so `proteus world reconcile` succeeds and the run
    # is a clean 0 rather than DEGRADED 6 for an unrelated fixture reason.
    '{"schema":"proteus.entity.v0.1","entity_id":"entity.test","carriers":[]}'    | Set-Content "$base\world\entities\entity.test\carriers.json"    -Encoding utf8
    '{"schema":"proteus.entity.v0.1","entity_id":"entity.test","projects":[]}'    | Set-Content "$base\world\entities\entity.test\projects.json"    -Encoding utf8
    '{"schema":"proteus.entity.v0.1","entity_id":"entity.test","secret_refs":[]}' | Set-Content "$base\world\entities\entity.test\secret_refs.json" -Encoding utf8
    '# Test entity' | Set-Content "$base\world\entities\entity.test\ENTITY.md"     -Encoding utf8
    '# Unresolved'  | Set-Content "$base\world\entities\entity.test\unresolved.md" -Encoding utf8
    return $base
}

function Add-Claim {
    param([string]$Path, [string]$Id, [string]$Text, [switch]$NoTrailingNewline)
    $line = '{"claim_id":"' + $Id + '","entity_id":"entity.test","text":"' + $Text + '","status":"current","recorded_utc":"2026-10-10T00:00:00Z"}'
    if ($NoTrailingNewline) {
        $existing = ""
        if (Test-Path $Path) { $existing = [IO.File]::ReadAllText($Path) }
        [IO.File]::WriteAllText($Path, $existing + $line)
    } else {
        Add-Content -Path $Path -Value $line -Encoding utf8
    }
}

Write-Host "=== Issue #1 round 3: claims ledger integrity ===`n"

# ---------------------------------------------------------------- C1 + C2
# Concurrent writers with DISTINCT append-only claims. The merge must keep
# BOTH claims and must never publish conflict markers.
$b = New-World "concurrent"
$cl = "$b\world\entities\entity.test\claims.jsonl"
Add-Claim $cl "claim.seed" "seed"
git -C "$b\world" add -A -f 2>&1 | Out-Null
git -C "$b\world" commit -q -m seed 2>&1 | Out-Null
git -C "$b\world" push -q origin host/aorus:main 2>&1 | Out-Null

git clone -q "$b\remote" "$b\w2" 2>&1 | Out-Null
git -C "$b\w2" config user.email "t2@l.local" 2>&1 | Out-Null
git -C "$b\w2" config user.name  "T2"         2>&1 | Out-Null
Add-Claim "$b\w2\entities\entity.test\claims.jsonl" "claim.WRITER2" "from writer2"
git -C "$b\w2" add -A 2>&1 | Out-Null
git -C "$b\w2" commit -q -m w2 2>&1 | Out-Null
git -C "$b\w2" push -q origin HEAD:main 2>&1 | Out-Null

Add-Claim $cl "claim.WRITER1" "from writer1"
git -C "$b\world" add -A 2>&1 | Out-Null
git -C "$b\world" commit -q -m w1 2>&1 | Out-Null

& $script:Script -WorldRoot "$b\world" -Branch "host/aorus" -PythonExe $script:PythonExe -ProteusSrc $script:ProteusSrc 2>&1 | Out-Null
$syncExit = $LASTEXITCODE
Assert-Case "C1 concurrent distinct claims: sync succeeds" 0 $syncExit

$published = (& git -C "$b\world" show "HEAD:entities/entity.test/claims.jsonl" 2>$null) -join "`n"
$hasMarkers = [bool]($published -match '^<<<<<<<|^=======|^>>>>>>>')
$hasW1 = [bool]($published -match 'claim\.WRITER1')
$hasW2 = [bool]($published -match 'claim\.WRITER2')
Assert-Case "C2a published ledger has NO conflict markers" $false $hasMarkers
Assert-Case "C2b writer1 claim survived (NO_LAST_WRITE_WINS)" $true $hasW1
Assert-Case "C2c writer2 claim survived (NO_LAST_WRITE_WINS)" $true $hasW2

& $script:PythonExe $script:ClaimsTool validate $cl 2>&1 | Out-Null
Assert-Case "C2d published ledger is valid JSONL" 0 $LASTEXITCODE

# ---------------------------------------------------------------- C3
# merge=union + missing trailing newline silently concatenates records and
# raises NO git conflict. The post-merge gate must refuse publication (8).
$b3 = New-World "union" -WithUnionAttr
$cl3 = "$b3\world\entities\entity.test\claims.jsonl"
Add-Claim $cl3 "claim.seed" "seed" -NoTrailingNewline
git -C "$b3\world" add -A -f 2>&1 | Out-Null
git -C "$b3\world" commit -q -m seed 2>&1 | Out-Null
git -C "$b3\world" push -q origin host/aorus:main 2>&1 | Out-Null

git clone -q "$b3\remote" "$b3\w2" 2>&1 | Out-Null
git -C "$b3\w2" config user.email "t2@l.local" 2>&1 | Out-Null
git -C "$b3\w2" config user.name  "T2"         2>&1 | Out-Null
git -C "$b3\w2" config core.autocrlf false     2>&1 | Out-Null
Add-Claim "$b3\w2\entities\entity.test\claims.jsonl" "claim.WRITER2" "from writer2" -NoTrailingNewline
git -C "$b3\w2" add -A 2>&1 | Out-Null
git -C "$b3\w2" commit -q -m w2 2>&1 | Out-Null
git -C "$b3\w2" push -q origin HEAD:main 2>&1 | Out-Null

Add-Claim $cl3 "claim.WRITER1" "from writer1" -NoTrailingNewline
git -C "$b3\world" add -A 2>&1 | Out-Null
git -C "$b3\world" commit -q -m w1 2>&1 | Out-Null

& $script:Script -WorldRoot "$b3\world" -Branch "host/aorus" -PythonExe $script:PythonExe -ProteusSrc $script:ProteusSrc 2>&1 | Out-Null
Assert-Case "C3 union+no-trailing-newline corruption refused" 8 $LASTEXITCODE "(pre-flight or post-merge gate)"

# ---------------------------------------------------------------- C4
# A ledger already containing conflict markers must never be published.
$b4 = New-World "markers"
$cl4 = "$b4\world\entities\entity.test\claims.jsonl"
Add-Claim $cl4 "claim.seed" "seed"
Add-Content -Path $cl4 -Value "<<<<<<< HEAD" -Encoding utf8
git -C "$b4\world" add -A -f 2>&1 | Out-Null
git -C "$b4\world" commit -q -m seed 2>&1 | Out-Null
git -C "$b4\world" push -q origin host/aorus:main 2>&1 | Out-Null
& $script:Script -WorldRoot "$b4\world" -Branch "host/aorus" -PythonExe $script:PythonExe -ProteusSrc $script:ProteusSrc 2>&1 | Out-Null
Assert-Case "C4 pre-existing conflict marker refused" 8 $LASTEXITCODE

# ---------------------------------------------------------------- C5
# -Preview must not mutate the real world at all.
$b5 = New-World "preview"
$cl5 = "$b5\world\entities\entity.test\claims.jsonl"
Add-Claim $cl5 "claim.seed" "seed"
git -C "$b5\world" add -A -f 2>&1 | Out-Null
git -C "$b5\world" commit -q -m seed 2>&1 | Out-Null
git -C "$b5\world" push -q origin host/aorus:main 2>&1 | Out-Null

git clone -q "$b5\remote" "$b5\w2" 2>&1 | Out-Null
git -C "$b5\w2" config user.email "t2@l.local" 2>&1 | Out-Null
git -C "$b5\w2" config user.name  "T2"         2>&1 | Out-Null
Add-Claim "$b5\w2\entities\entity.test\claims.jsonl" "claim.REMOTE" "remote only"
git -C "$b5\w2" add -A 2>&1 | Out-Null
git -C "$b5\w2" commit -q -m w2 2>&1 | Out-Null
git -C "$b5\w2" push -q origin HEAD:main 2>&1 | Out-Null

$headBefore   = (& git -C "$b5\world" rev-parse HEAD 2>$null)
$statusBefore = ((& git -C "$b5\world" status --porcelain 2>$null) -join "|")
$remoteBefore = (& git -C "$b5\world" rev-parse refs/remotes/origin/main 2>$null)

& $script:Script -WorldRoot "$b5\world" -Branch "host/aorus" -PythonExe $script:PythonExe -ProteusSrc $script:ProteusSrc -Preview 2>&1 | Out-Null
$previewExit = $LASTEXITCODE

$headAfter   = (& git -C "$b5\world" rev-parse HEAD 2>$null)
$statusAfter = ((& git -C "$b5\world" status --porcelain 2>$null) -join "|")
$remoteAfter = (& git -C "$b5\world" rev-parse refs/remotes/origin/main 2>$null)

Assert-Case "C5a -Preview leaves HEAD unchanged"            $headBefore   $headAfter
Assert-Case "C5b -Preview leaves worktree unchanged"        $statusBefore $statusAfter
Assert-Case "C5c -Preview does not even move origin/main"   $remoteBefore $remoteAfter
Assert-Case "C5d -Preview reports the would-be exit code"   0            $previewExit

# ---------------------------------------------------------------- C6
# -NoPublish is local-mutating by contract, and must NOT publish.
$b6 = New-World "nopublish"
$cl6 = "$b6\world\entities\entity.test\claims.jsonl"
Add-Claim $cl6 "claim.seed" "seed"
git -C "$b6\world" add -A -f 2>&1 | Out-Null
git -C "$b6\world" commit -q -m seed 2>&1 | Out-Null
git -C "$b6\world" push -q origin host/aorus:main 2>&1 | Out-Null
$remoteHeadBefore = (& git -C "$b6\remote" rev-parse main 2>$null)

Add-Claim $cl6 "claim.LOCAL" "local only"
& $script:Script -WorldRoot "$b6\world" -Branch "host/aorus" -PythonExe $script:PythonExe -ProteusSrc $script:ProteusSrc -NoPublish 2>&1 | Out-Null
$npExit = $LASTEXITCODE
$remoteHeadAfter = (& git -C "$b6\remote" rev-parse main 2>$null)
$localStatus = ((& git -C "$b6\world" status --porcelain 2>$null) -join "|")

Assert-Case "C6a -NoPublish succeeds"                   0 $npExit
Assert-Case "C6b -NoPublish did NOT advance the remote" $remoteHeadBefore $remoteHeadAfter
Assert-Case "C6c -NoPublish committed locally"          "" $localStatus

# ---------------------------------------------------------------- C7
# Concurrent remote writer appearing between fetch and push: the bounded
# retry must re-merge and still publish, losing no commit.
$b7 = New-World "nonff"
$cl7 = "$b7\world\entities\entity.test\claims.jsonl"
Add-Claim $cl7 "claim.seed" "seed"
git -C "$b7\world" add -A -f 2>&1 | Out-Null
git -C "$b7\world" commit -q -m seed 2>&1 | Out-Null
git -C "$b7\world" push -q origin host/aorus 2>&1 | Out-Null
git -C "$b7\world" push -q origin host/aorus:main 2>&1 | Out-Null

# Remote host-branch advances behind our back -> our push is non-fast-forward.
git clone -q --branch host/aorus "$b7\remote" "$b7\w2" 2>&1 | Out-Null
git -C "$b7\w2" config user.email "t2@l.local" 2>&1 | Out-Null
git -C "$b7\w2" config user.name  "T2"         2>&1 | Out-Null
Add-Claim "$b7\w2\entities\entity.test\claims.jsonl" "claim.RACER" "racer"
git -C "$b7\w2" add -A 2>&1 | Out-Null
git -C "$b7\w2" commit -q -m racer 2>&1 | Out-Null
git -C "$b7\w2" push -q origin HEAD:host/aorus 2>&1 | Out-Null
git -C "$b7\w2" push -q origin HEAD:main 2>&1 | Out-Null

# Our claim is COMMITTED before the sync run. (An *uncommitted* local claim is a
# separate, pre-existing defect: the script merges before it commits, so git
# refuses the merge with "Please commit your changes or stash them". Tracked
# separately; not exercised here.)
Add-Claim $cl7 "claim.MINE" "mine"
git -C "$b7\world" add -A 2>&1 | Out-Null
git -C "$b7\world" commit -q -m mine 2>&1 | Out-Null
& $script:Script -WorldRoot "$b7\world" -Branch "host/aorus" -PythonExe $script:PythonExe -ProteusSrc $script:ProteusSrc 2>&1 | Out-Null
$nonffExit = $LASTEXITCODE
$finalLedger = (& git -C "$b7\world" show "HEAD:entities/entity.test/claims.jsonl" 2>$null) -join "`n"
Assert-Case "C7a non-fast-forward resolved by bounded retry" 0 $nonffExit
Assert-Case "C7b racer's claim survived"  $true ([bool]($finalLedger -match 'claim\.RACER'))
Assert-Case "C7c our claim survived"      $true ([bool]($finalLedger -match 'claim\.MINE'))

# ---------------------------------------------------------------- summary
Write-Host "`n=== SUMMARY ==="
$script:results | Format-Table -AutoSize | Out-String | Write-Host
$failed = @($script:results | Where-Object { $_.Status -ne "PASS" })
Write-Host ("total={0} pass={1} fail={2}" -f $script:results.Count, ($script:results.Count - $failed.Count), $failed.Count)
if ($failed.Count -gt 0) { exit 1 }
exit 0

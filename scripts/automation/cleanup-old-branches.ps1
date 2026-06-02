# PowerShell script to clean up old branches
# Run weekly via CI/CD to keep repositories clean

param(
    [int]$DaysOld = 30,
    [switch]$DryRun,
    [string[]]$ProtectedBranches = @("main", "gh-pages", "master", "develop")
)

Write-Host "🔍 Starting branch cleanup..." -ForegroundColor Cyan

function Test-ProtectedBranch {
    param([string]$Branch)
    return $ProtectedBranches -contains $Branch
}

function Get-BranchAge {
    param([string]$BranchRef)

    try {
        $commitInfo = git log -1 --format="%cd" --date=short $BranchRef 2>$null
        if (-not $commitInfo) { return 9999 }

        $commitDate = [DateTime]::Parse($commitInfo)
        $ageDays = [Math]::Floor(([DateTime]::Now - $commitDate).TotalDays)
        return $ageDays
    }
    catch {
        return 9999
    }
}

function Remove-RemoteBranch {
    param([string]$Remote, [string]$Branch)

    if ($DryRun) {
        Write-Host "📝 [DRY RUN] Would delete: $Remote/$Branch" -ForegroundColor Yellow
        return
    }

    Write-Host "🗑️  Deleting: $Remote/$Branch" -ForegroundColor Red
    git push $Remote --delete $Branch 2>$null
}

function Cleanup-Remote {
    param([string]$Remote)

    Write-Host "📡 Checking remote: $Remote" -ForegroundColor Cyan

    # Fetch all branches from remote
    git fetch $Remote --prune 2>$null

    # Get list of remote branches
    $remoteBranches = git branch -r |
        Where-Object { $_ -match "^  $Remote/" } |
        ForEach-Object { $_ -replace "^  $Remote/", "" } |
        Where-Object { $_ -notmatch "HEAD" }

    foreach ($branch in $remoteBranches) {
        # Skip protected branches
        if (Test-ProtectedBranch $branch) {
            Write-Host "🛡️  Skipping protected branch: $branch" -ForegroundColor Green
            continue
        }

        # Check if branch is merged into main
        $mergeBase = git merge-base "$Remote/$branch" "$Remote/main" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $isAncestor = git merge-base --is-ancestor "$Remote/$branch" "$Remote/main" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Merged branch: $branch (already in main)" -ForegroundColor Green
                Remove-RemoteBranch $Remote $branch
                continue
            }
        }

        # Check branch age
        $age = Get-BranchAge "$Remote/$branch"
        if ($age -gt $DaysOld) {
            Write-Host "⏳ Old branch ($age days): $branch" -ForegroundColor Yellow
            Remove-RemoteBranch $Remote $branch
            continue
        }

        Write-Host "📌 Active branch ($age days): $branch - keeping" -ForegroundColor Gray
    }
}

# Main execution
try {
    # Run cleanup for configured remotes
    $remotes = @("origin", "github")

    foreach ($remote in $remotes) {
        $remoteExists = git remote | Where-Object { $_ -eq $remote }
        if ($remoteExists) {
            Cleanup-Remote $remote
        }
        else {
            Write-Host "⚠️  Remote '$remote' not found, skipping" -ForegroundColor Yellow
        }
    }

    Write-Host "✨ Branch cleanup completed!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error during cleanup: $_" -ForegroundColor Red
    exit 1
}

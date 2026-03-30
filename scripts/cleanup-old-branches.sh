#!/bin/bash
# Script to clean up old branches that have been merged or are stale
# Run this weekly via CI/CD to keep repositories clean

set -e

echo "🔍 Starting branch cleanup..."

# Configuration
DAYS_OLD=30  # Delete branches older than 30 days
PROTECTED_BRANCHES="main|gh-pages|master|develop"
DRY_RUN=${DRY_RUN:-false}

# Function to check if branch is protected
is_protected() {
    local branch="$1"
    if echo "$branch" | grep -qE "^($PROTECTED_BRANCHES)$"; then
        return 0
    fi
    return 1
}

# Function to get branch age in days
get_branch_age() {
    local branch="$1"
    local last_commit_date=$(git log -1 --format="%cd" --date=short "$branch" 2>/dev/null || echo "")
    if [ -z "$last_commit_date" ]; then
        echo "9999"  # Very old if can't get date
        return
    fi
    
    local last_commit_ts=$(date -d "$last_commit_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$last_commit_date" +%s)
    local now_ts=$(date +%s)
    local age_days=$(( (now_ts - last_commit_ts) / 86400 ))
    echo "$age_days"
}

# Function to delete remote branch
delete_remote_branch() {
    local remote="$1"
    local branch="$2"
    
    if [ "$DRY_RUN" = "true" ]; then
        echo "📝 [DRY RUN] Would delete: $remote/$branch"
        return
    fi
    
    echo "🗑️  Deleting: $remote/$branch"
    git push "$remote" --delete "$branch" 2>/dev/null || true
}

# Main cleanup logic
cleanup_remote() {
    local remote="$1"
    
    echo "📡 Checking remote: $remote"
    
    # Fetch all branches from remote
    git fetch "$remote" --prune
    
    # Get list of remote branches
    local remote_branches=$(git branch -r | grep "^  $remote/" | sed "s|^  $remote/||" | grep -v "HEAD")
    
    for branch in $remote_branches; do
        # Skip protected branches
        if is_protected "$branch"; then
            echo "🛡️  Skipping protected branch: $branch"
            continue
        fi
        
        # Check if branch is merged into main
        if git merge-base --is-ancestor "$remote/$branch" "$remote/main" 2>/dev/null; then
            echo "✅ Merged branch: $branch (already in main)"
            delete_remote_branch "$remote" "$branch"
            continue
        fi
        
        # Check branch age
        local age=$(get_branch_age "$remote/$branch")
        if [ "$age" -gt "$DAYS_OLD" ]; then
            echo "⏳ Old branch ($age days): $branch"
            delete_remote_branch "$remote" "$branch"
            continue
        fi
        
        echo "📌 Active branch ($age days): $branch - keeping"
    done
}

# Run cleanup for configured remotes
for remote in origin github; do
    if git remote | grep -q "^$remote$"; then
        cleanup_remote "$remote"
    else
        echo "⚠️  Remote '$remote' not found, skipping"
    fi
done

echo "✨ Branch cleanup completed!"
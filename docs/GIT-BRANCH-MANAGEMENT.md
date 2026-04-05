# Git Branch Management & Cleanup Process

## 📋 Overview

This document defines the branch management strategy for the Portfolio System Architect project. It ensures clean repositories, prevents accumulation of technical debt, and establishes clear workflows for collaboration.

## 🎯 Branch Naming Convention

### Prefixes & Purpose
| Prefix | Purpose | Example | Auto-cleanup |
|--------|---------|---------|--------------|
| `feature/` | New functionality | `feature/audience-docs` | 30 days after merge |
| `fix/` | Bug fixes | `fix/docs-time-intervals` | 30 days after merge |
| `docs/` | Documentation only | `docs/readme-update` | 30 days after merge |
| `enhance/` | Improvements (non-breaking) | `enhance/ci-performance` | 30 days after merge |
| `security/` | Security fixes | `security/sql-injection` | Keep until audit |
| `experiment/` | Proof of concepts | `experiment/new-llm-integration` | 14 days |

### Rules
1. Use kebab-case: `feature/my-feature-name`
2. Be descriptive but concise
3. Include ticket/issue number if applicable: `feature/123-add-auth`

## 🔄 Workflow Process

### 1. Creating a Branch
```bash
# Always start from main
git checkout main
git pull origin main

# Create new branch
git checkout -b feature/descriptive-name
```

### 2. Making Changes
- Commit frequently with clear messages
- Follow conventional commits: `feat:`, `fix:`, `docs:`, etc.
- Keep changes focused on the branch's purpose

### 3. Creating a Pull Request
1. Push branch to remote: `git push origin feature/descriptive-name`
2. Create PR on **SourceCraft** (not GitHub)
3. Add description, link issues, assign reviewers
4. Wait for CI checks to pass

### 4. After PR Merge
```bash
# Delete remote branch (automatically via CI or manually)
git push origin --delete feature/descriptive-name

# Delete local branch
git branch -d feature/descriptive-name

# Update local main
git checkout main
git pull origin main
```

## 🧹 Automated Cleanup

### CI/CD Scheduled Cleanup
- **Frequency**: Every Sunday at 03:00 UTC
- **Script**: `scripts/cleanup-old-branches.sh`
- **Criteria**:
  - Branches merged into main (any age)
  - Branches older than 30 days (not merged)
  - Dependabot branches older than 14 days

### Protected Branches (Never deleted)
- `main`
- `gh-pages`
- `master`
- `develop`

### Manual Cleanup Commands
```bash
# Dry run (see what would be deleted)
DRY_RUN=true ./scripts/cleanup-old-branches.sh

# Force cleanup (immediate)
./scripts/cleanup-old-branches.sh

# PowerShell version
pwsh scripts/cleanup-old-branches.ps1 -DryRun
```

## 📊 Branch Health Metrics

### Monitoring
- **Active branches**: `git branch -r --no-merged origin/main`
- **Stale branches**: `git branch -r --merged origin/main`
- **Branch age**: Script calculates days since last commit

### Reports
Weekly CI job generates:
1. List of branches deleted
2. Current branch count
3. Age distribution of active branches

## 🚨 Exception Handling

### Branches to Keep Longer
| Scenario | Retention | Process |
|----------|-----------|---------|
| Security fixes | 90 days | Manual review before deletion |
| Grant-related work | Until grant decision | Tag with `grant-2025` |
| Production hotfixes | 60 days | Linked to incident report |

### Restoring Deleted Branches
```bash
# Find commit hash
git reflog | grep "feature/deleted-branch"

# Restore from commit
git checkout -b feature/restored-branch <commit-hash>
```

## 🔧 Configuration Files

### 1. CI Configuration (`.sourcecraft/ci.yaml`)
- Defines scheduled cleanup job
- Sets DRY_RUN=false for production
- Configures email notifications

### 2. Cleanup Scripts
- `scripts/cleanup-old-branches.sh` - Linux/macOS
- `scripts/cleanup-old-branches.ps1` - Windows/PowerShell

### 3. Git Hooks (Optional)
- Pre-commit: Check branch naming
- Pre-push: Warn about stale branches

## 📝 Best Practices

### Do's
- ✅ Delete branches immediately after merge
- ✅ Use descriptive names
- ✅ Keep branches focused (single responsibility)
- ✅ Regular cleanup (weekly)
- ✅ Document long-running branches

### Don'ts
- ❌ Use generic names (`test`, `update`, `fix`)
- ❌ Keep branches after merge
- ❌ Work directly on `main`
- ❌ Ignore CI cleanup failures

## 🔗 Related Documentation

- [GitHub Mirror Instructions](GITHUB-MIRROR-INSTRUCTIONS.md)
- [CI/CD Configuration](../.sourcecraft/ci.yaml)
- [Contributing Guidelines](../CONTRIBUTING.md)

## 📞 Support

### Issues with Cleanup
1. Check CI logs for errors
2. Verify git permissions
3. Run manual dry run

### Process Questions
- Open issue with label `git-process`
- Contact maintainers on SourceCraft
- Review this document for updates

---

*Last updated: $(date +%Y-%m-%d)*  
*Auto-cleanup status: ✅ Active*  
*Next cleanup: Sunday 03:00 UTC*

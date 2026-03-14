# Git Push & Sync TODO

## Approved Plan Steps (Step-by-step execution)

### Step 1: Add GitHub remote
- [ ] `git remote add github git@github.com:leadarchitect-ai/portfolio-system-architect.git`
- Verify: `git remote -v`

### Step 2: Stage and commit local changes
- [ ] `git add -A`
- [ ] `git commit -m "chore: apply Docker fixes, deprecate legacy TODO files, update pytest-cov to 7.0.0"`

### Step 3: Push current branch to origin (SourceCraft)
- [ ] `git push origin blackboxai/todo-unify-mirroring`

### Step 4: Switch to main, pull, merge current branch
- [ ] `git checkout main`
- [ ] `git pull origin main`
- [ ] `git merge blackboxai/todo-unify-mirroring`

### Step 5: Push main to both remotes
- [ ] `git push origin main`
- [ ] `git push github main`

### Step 6: Push current branch to GitHub for PR
- [ ] `git checkout blackboxai/todo-unify-mirroring`
- [ ] `git push github blackboxai/todo-unify-mirroring`

### Step 7: Create PR (if gh CLI ready)
- [ ] Check `gh` installed: `gh --version`
- [ ] `gh pr create --base main --head blackboxai/todo-unify-mirroring --title "Docker fixes and TODO cleanup" --body "Apply Docker fixes, deprecate legacy TODO files, update pytest-cov to 7.0.0"`

### Step 8: Verify sync
- [ ] `git fetch --all`
- [ ] `git diff origin/main github/main` (should be empty)

### Followup (manual)
- Add GH_TOKEN secret in GitHub repo settings.
- Enable SourceCraft UI mirroring.
- Test workflow: `gh workflow run mirror-sourcecraft.yml`
- Mark this TODO complete and commit to main.

**Status:** Ready to execute Step 1.
**Last update:** $(date)

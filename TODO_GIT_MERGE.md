# TODO: Git Branches Merge Plan (Approved: 2026)

## Status: Pending

### 1. [ ] Checkout main
`git checkout main`

### 2. [ ] Pull all remotes
`git pull --all`

### 3. [ ] Merge refactor
`git merge refactor/structure-resume-v1`

### 4. [ ] Create post-grant tag
`git tag -a grant-refactor-v1 -m \"Post-grant refactor complete (TODO_REFRACTOR done)\"`

### 5. [ ] Push all + tags
`git push --all --tags`

### 6. [ ] Create PR (if gh CLI)
`gh pr create --title \"Merge structure refactor\" --body \"Safe: grant tags preserved\"`

### 7. [ ] Cleanup
- `git branch -D backup/main-before-grant-merge`
- `git branch -D blackboxai/feat-ci-cd blackboxai/grant-readiness` (after review)

### Notes
- Grant tags safe.
- Update after each step.
- `git status` clean expected.

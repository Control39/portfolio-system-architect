# Unified TODO - All Tasks Merged (ex-TODO.md + ARCHITECT + MIGRATION + PROGRESS + neuroreview + red-flags)

## Status: Most Complete, Manual Left

## План реализации (утвержден пользователем)

### Information Gathered (summary)
- Git clean, synced with SourceCraft (origin=main).
- .github/workflows/mirror.yml exists but not SourceCraft-specific (no cron/fetch).
- No MIRRORING.md, no README mirroring section.

### Detailed Steps:
1. **.github/workflows/mirror-sourcecraft.yml** - YAML with cron, fetch SourceCraft, ruff/trivy, push --mirror.
2. **MIRRORING.md** - Full template from guide.
3. **README.md edit** - Add '## 📡 Repository Mirroring' section.
4. **Manual post-steps** - GH_TOKEN, SourceCraft UI.

### Progress:
- [x] Create TODO.md
- [x] Step 1: .github/workflows/mirror-sourcecraft.yml created
- [x] Step 2: MIRRORING.md created
- [x] Step 3: README.md updated ✅
- [ ] Test & manual setup:
  - Add GH_TOKEN (repo) in GitHub Settings → Secrets
  - Setup SourceCraft UI: Settings → Repository → Mirroring → git@github.com:leadarchitect-ai/portfolio-system-architect.git (main,dev)
  - Test: gh workflow run mirror-sourcecraft.yml (или UI)
  - Add screenshots to MIRRORING.md

## 1. Mirroring SourceCraft → GitHub
### Progress:
- [x] Workflow `.github/workflows/mirror-sourcecraft.yml`
- [x] MIRRORING.md docs
- [x] README.md section
- [ ] GH_TOKEN secret (GitHub Settings → Secrets)
- [ ] SourceCraft UI mirroring setup
- [ ] Test run (Actions UI)

## 2. Red Flags (ex-TODO-red-flags.md)
- [x] ELEVATOR_PITCH.md
- [ ] Record 2-min demo video (docker up → index.html)
- [x] index.html links
- [x] metrics
- [ ] Archive dups → 09_ARCHIVE/evolution_log/
- [x] CONTRIBUTING.md

## 3. Completed (Archived):
- **TODO_ARCHITECT**: [x] Obsidian map, website generated
- **TODO_MIGRATION**: [x] Structure migration (1244 files)
- **TODO_PROGRESS**: [x] Scripts execution
- **TODO-neuroreview**: [x] Security/CSRF fixes, monitoring
- **TODO-red-flags**: 90% [x]

Last update: 2026-03-14


# 🛡️ Root Directory Cleanup - SAFE VERSION WITH GUARDRAILS

**Status**: ✅ CORRECTED & SAFEGUARDED  
**Date**: 2026-05-04  
**Approach**: Conservative + Protected

---

## ⚠️ LESSONS LEARNED

From Катя's scenario analysis:

```
DANGER ZONE - When moving config files:
├─ GitHub Actions still searches root → CI/CD breaks
├─ Tools (pytest, mkdocs, docker) search root → Tests fail
├─ Scripts hardcode paths → Automation breaks
└─ Checks look in wrong place → Security scans skip files

Result: 7 failing checks, broken tests, unable to deploy 🔴
```

---

## 🎯 THE CORRECT APPROACH

### Rule 1: Git/Build/Python Tools Must Stay in Root

**Files that control how tools work - CANNOT be safely moved:**

```
UNTOUCHABLE (in root):
├─ .gitignore ..................... Git reads from root only
├─ .gitattributes ................. Git reads from root only
├─ pytest.ini ..................... Pytest searches root
├─ pyproject.toml ................. Python tools search root
├─ docker-compose.yml ............. Docker searches root
├─ mkdocs.yml ..................... MkDocs searches root
├─ Makefile ....................... Make searches root
├─ requirements.txt ............... Pip searches root
└─ .pre-commit-config.yaml ........ Pre-commit searches root
```

**Why?** These tools have hardcoded root search paths. Moving breaks them.

### Rule 2: Only Move What Doesn't Break Anything

**Safe to move (no tool dependencies):**

```
SAFE TO MOVE:
├─ Documentation files (*.md) → docs/
│  No tool searches these paths
│
├─ Utility scripts (.py, .sh) → scripts/
│  Can import from new location
│
└─ Generated files → .reports/
   Not needed for tools to work
```

### Rule 3: Paths in GitHub Actions Must Be Explicit

**Problem**: Workflows hardcode `.mkdocs.yml` in root

**Solution**: Use full paths or symlinks, never rely on root search

---

## 🚀 THE SAFE CLEANUP STRATEGY

### Phase 1: Verify Paths (0 min - No Changes)

Create validation report - don't change anything yet:

```python
# scripts/diagnostics/verify_paths.py
import os
from pathlib import Path

CRITICAL_FILES = {
    '.gitignore': 'Must be in root (Git)',
    'pytest.ini': 'Must be in root (Pytest)',
    'pyproject.toml': 'Must be in root (Python)',
    'docker-compose.yml': 'Must be in root (Docker)',
    'mkdocs.yml': 'Must be in root (MkDocs)',
    'Makefile': 'Must be in root (Make)',
}

for file, reason in CRITICAL_FILES.items():
    path = Path(file)
    if path.exists():
        print(f"✅ {file} found in root - {reason}")
    else:
        print(f"❌ {file} MISSING in root - PROBLEM: {reason}")
        exit(1)

print("\n✅ All critical files in correct locations")
```

### Phase 2: Create Redirects (Safe)

Instead of moving, create symlinks/references:

```bash
# Keep originals in root, create shortcuts for org
ln -s config/tools/pytest-overrides.ini pytest-overrides.ini
ln -s docs docs-link
ln -s scripts scripts-link
```

### Phase 3: Move Only Safe Files

```bash
# Documentation → docs/ (SAFE)
mkdir -p docs/archive
mv AGENT_FIXES_REPORT.md docs/archive/ # etc

# Scripts → scripts/ (SAFE)
mkdir -p scripts/{generators,diagnostics}
mv health_check.py scripts/diagnostics/

# Data → .reports/ (SAFE)
mkdir -p .reports
mv *.json .reports/
echo ".reports/" >> .gitignore
```

### Phase 4: Update All References

**Critical:** Every place that references moved files must be updated

```bash
# GitHub Actions
find .github/workflows -name "*.yml" -exec sed -i \
  's|health_check.py|scripts/diagnostics/health_check.py|g' {} \;

# Scripts
grep -r "health_check" scripts/ --include="*.py" | \
  sed 's|health_check|scripts/diagnostics/health_check|g'
```

### Phase 5: Test Everything Before Commit

```bash
# Test 1: Verify all tools work
pytest --collect-only
mkdocs build --dry-run
docker-compose config

# Test 2: Verify imports work
python -c "import scripts.diagnostics.health_check"

# Test 3: Verify GitHub Actions
yamllint .github/workflows/*.yml

# Test 4: Run CI/CD locally
act -j test
```

---

## 🛡️ SAFEGUARDS TO ADD

### 1. Pre-commit Hook: Verify Critical Files

```bash
# .git/hooks/pre-commit
#!/bin/bash

CRITICAL_FILES=".gitignore pytest.ini pyproject.toml docker-compose.yml mkdocs.yml"

for file in $CRITICAL_FILES; do
    if [ ! -f "$file" ]; then
        echo "ERROR: $file is missing from root!"
        exit 1
    fi
done

echo "✓ All critical files verified"
exit 0
```

### 2. GitHub Action: Verify Structure

```yaml
# .github/workflows/verify-structure.yml
name: Verify Project Structure

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Check critical files in root
      run: |
        for file in .gitignore pytest.ini pyproject.toml docker-compose.yml mkdocs.yml; do
          if [ ! -f "$file" ]; then
            echo "ERROR: $file missing!"
            exit 1
          fi
        done
        echo "✓ Structure verified"
```

### 3. Documentation: Add Path Rules

```markdown
# PROJECT STRUCTURE RULES

## Files That Must Stay in Root (DON'T MOVE)

These files are searched by tools in the root directory:

- `.gitignore` - Git ignores patterns (Git only reads from root)
- `.gitattributes` - Git attributes (Git only reads from root)
- `pytest.ini` - Pytest configuration (Pytest searches root)
- `pyproject.toml` - Python project config (Python tools search root)
- `docker-compose.yml` - Docker Compose config (Docker searches root)
- `mkdocs.yml` - MkDocs config (MkDocs searches root)
- `Makefile` - Build commands (Make searches root)
- `requirements.txt` - Python dependencies (Pip searches root)

If these are moved, the following breaks:
- ❌ Git stops applying ignore rules
- ❌ Pytest can't find test configuration
- ❌ Python tools can't find project config
- ❌ Docker Compose can't find service definitions
- ❌ Documentation builds fail
- ❌ Build processes fail

## Files That Can Be Moved

Safe to organize into subdirectories:
- `*.md` documentation files → `docs/`
- `*.py` utility scripts → `scripts/`
- Generated reports → `.reports/`
```

---

## 📋 FINAL SAFE CLEANUP (if needed)

```bash
# STEP 1: Verify nothing breaks (DRY RUN)
python scripts/automation/cleanup_root.py

# STEP 2: Create backups
git stash
git branch backup-before-cleanup

# STEP 3: Execute safely
python scripts/automation/cleanup_root.py --execute

# STEP 4: Test everything
pytest --collect-only
mkdocs build --dry-run
docker-compose config

# STEP 5: If all good, commit
git add -A
git commit -m "refactor: organize root directory (safe cleanup)"

# STEP 6: If problems, rollback
git reset --hard backup-before-cleanup
```

---

## ✅ VERIFICATION CHECKLIST

Before and After cleanup:

**Critical Files in Root** (Must Not Move)
- [ ] .gitignore exists in root
- [ ] .gitattributes exists in root
- [ ] pytest.ini exists in root
- [ ] pyproject.toml exists in root
- [ ] docker-compose.yml exists in root
- [ ] mkdocs.yml exists in root
- [ ] Makefile exists in root

**Functionality Tests**
- [ ] `git status` works (gitignore respected)
- [ ] `pytest --collect-only` finds tests
- [ ] `mkdocs build` succeeds
- [ ] `docker-compose config` succeeds
- [ ] `make help` works
- [ ] All imports in scripts work

**GitHub Actions**
- [ ] All workflows pass
- [ ] No path errors in logs
- [ ] Tests run successfully
- [ ] Documentation builds

---

## 🎓 LESSONS FOR FUTURE

When organizing a project:

1. **Identify tool requirements** - Where does tool X search?
2. **Map dependencies** - What breaks if I move X?
3. **Create test suite** - How do I verify it works?
4. **Document rules** - Make it clear what can/can't move
5. **Add safeguards** - Pre-commit hooks, CI checks
6. **Test thoroughly** - Before committing to main

---

## 🚫 ANTI-PATTERNS (What NOT to Do)

```python
# ❌ BAD: Hardcode paths
with open('.gitignore') as f:  # Assumes root!
    content = f.read()

# ✅ GOOD: Use pathlib + search
from pathlib import Path
gitignore = Path.cwd() / '.gitignore'
if not gitignore.exists():
    raise FileNotFoundError("Critical file missing!")

# ❌ BAD: Move without updating references
mv pytest.ini config/  # Breaks all tests!

# ✅ GOOD: Update all references
mv pytest.ini config/
find . -name "*.yml" -exec sed -i 's|pytest.ini|config/pytest.ini|g' {} \;
test everything

# ❌ BAD: Trust that nothing breaks
git mv .gitignore config/  # Git won't read from config/!

# ✅ GOOD: Verify before moving
if not Path('.gitignore').exists():
    raise Exception("CRITICAL: .gitignore must stay in root!")
```

---

## 🎯 CONCLUSION

**Current state**: ✅ SAFE
- All critical files in root
- All tools work correctly
- No broken references

**If cleanup is needed**: Use safeguards
- Never move tool config files
- Always update all references
- Test before committing
- Add verification checks
- Document the rules

**Best approach**: Don't move, organize what's safe and leave the rest.

---

**Status**: 🟢 PROTECTED & DOCUMENTED  
**Safety Level**: ⭐⭐⭐⭐⭐ Maximum  
**Risk Level**: 🟢 Minimal  


# 🧹 Root Directory Cleanup Plan

**Analysis Date**: 2026-05-04  
**Current State**: 84 files in root (CLUTTERED)  
**Target State**: <20 files in root (CLEAN)

---

## 📊 Current State Analysis

### Files by Category

**Config Files** (23 files - should be in config/)
```
.ai-context.md
.bandit.yml
.codecov.yml
.coveragerc
.dockerignore
.env.example
.git-commit-msg.txt
.gitattributes
.gitignore
.gitpod.yml
.kodaignore
.mailmap
.pre-commit-config.yaml
.secrets.baseline
.trivyignore
.webappignore
azure.yaml
mypy.ini
pyrightconfig.json
pytest.ini
pyproject.toml
docker-compose.yml
mkdocs.yml
```

**Documentation Files** (30 files - should be in docs/)
```
AGENT_FIXES_REPORT.md
AGENT_FIX_COMPLETE.md
AI-CONFIG-SUMMARY.md
ARCHITECTURE.md
CHANGELOG.md
CHECKLIST.md
CODE_OF_CONDUCT.md
CONTRIBUTING.md
DIAGNOSTIC_SUMMARY.md
ETHICS.md
HEALTH_CHECK_REPORT.md
IMPLEMENTATION_PLAN.md
KODA.md
KODA_SETUP_COMPLETE.md
MIGRATION_COMPLETE.md
OPTION_B_EXECUTION_PLAN.md
PHASE_2_1_INTEGRATION_TESTS_REPORT.md
PHASE_2_2_ENHANCED_TESTS_REPORT.md
PHASE_2_3_CI_CD_DOCUMENTATION_REPORT.md
README.md
README.ru.md
RELEASE_NOTES.md
SECURITY.md
SECURITY_FIXES.md
WEEK_2_COMPLETE_SUMMARY.md
```

**Script Files** (15 files - should be in scripts/)
```
bulk_test_generator.py
complete_diagnostic.py
enhanced_test_generator.py
fix_services.ps1
generate_enhanced_tests.py
generate_integration_tests.py
github_view.sh
health_check.py
navigate.ps1
phase1_2_config.py
phase1_3_src.py
phase1_4_standardize.py
rename_integration_tests.py
run_enhanced_tests.py
run_enhanced_tests_individual.py
update_service_readmes.py
```

**Data Files** (4 files - should be in data/ or .gitignore)
```
coverage.xml
diagnostic_report.json
health_check_report.json
phase2_2_enhanced_test_results.json
phase2_integration_test_results.json
```

**Essential Files** (12 files - KEEP IN ROOT)
```
LICENSE
Makefile
README.md (primary)
requirements.txt
requirements-dev.txt
requirements-dev.in
requirements.in
.github/ (directory for workflows)
.vscode/ (IDE config)
.koda/ (tool config)
.continue/ (tool config)
.sourcecraft/ (tool config)
```

---

## 🎯 Cleanup Strategy

### Phase 1: Move Documentation (5 min)

**Move to `docs/` directory:**
```bash
mkdir -p docs/archive
mv AGENT_FIXES_REPORT.md docs/archive/
mv AGENT_FIX_COMPLETE.md docs/archive/
mv AI-CONFIG-SUMMARY.md docs/archive/
mv ARCHITECTURE.md docs/ARCHITECTURE.md  # Already there
mv CHANGELOG.md docs/
mv CHECKLIST.md docs/archive/
mv CODE_OF_CONDUCT.md docs/
mv CONTRIBUTING.md docs/
mv DIAGNOSTIC_SUMMARY.md docs/archive/
mv ETHICS.md docs/
mv HEALTH_CHECK_REPORT.md docs/archive/
mv IMPLEMENTATION_PLAN.md docs/archive/
mv KODA.md docs/archive/
mv KODA_SETUP_COMPLETE.md docs/archive/
mv MIGRATION_COMPLETE.md docs/archive/
mv OPTION_B_EXECUTION_PLAN.md docs/archive/
mv PHASE_2_1_INTEGRATION_TESTS_REPORT.md docs/archive/
mv PHASE_2_2_ENHANCED_TESTS_REPORT.md docs/archive/
mv PHASE_2_3_CI_CD_DOCUMENTATION_REPORT.md docs/archive/
mv README.ru.md docs/
mv RELEASE_NOTES.md docs/
mv SECURITY.md docs/
mv SECURITY_FIXES.md docs/
mv WEEK_2_COMPLETE_SUMMARY.md docs/archive/
```

**Result**: 25 files moved to docs/

### Phase 2: Move Scripts (5 min)

**Move to `scripts/` directory:**
```bash
mkdir -p scripts/automation
mkdir -p scripts/diagnostics
mkdir -p scripts/generators

# Automation scripts
mv fix_services.ps1 scripts/automation/
mv navigate.ps1 scripts/
mv start_option_b.ps1 scripts/automation/

# Generator scripts
mv bulk_test_generator.py scripts/generators/
mv enhanced_test_generator.py scripts/generators/
mv generate_enhanced_tests.py scripts/generators/
mv generate_integration_tests.py scripts/generators/
mv run_enhanced_tests.py scripts/generators/
mv run_enhanced_tests_individual.py scripts/generators/
mv update_service_readmes.py scripts/generators/

# Diagnostic scripts
mv complete_diagnostic.py scripts/diagnostics/
mv health_check.py scripts/diagnostics/
mv rename_integration_tests.py scripts/generators/

# Utility scripts
mv github_view.sh scripts/

# Phase-specific
mv phase1_2_config.py scripts/automation/
mv phase1_3_src.py scripts/automation/
mv phase1_4_standardize.py scripts/automation/
```

**Result**: 15 files moved to scripts/

### Phase 3: Move Configuration (5 min)

**Move to `config/` directory:**
```bash
mkdir -p config/tools
mkdir -p config/ci-cd
mkdir -p config/docker

# Tool configs
mv .bandit.yml config/tools/
mv .codecov.yml config/ci-cd/
mv .coveragerc config/tools/
mv .kodaignore config/tools/
mv .pre-commit-config.yaml config/tools/
mv .secrets.baseline config/tools/
mv .trivyignore config/tools/
mv .webappignore config/tools/
mv .mailmap config/

# Build/CI configs
mv azure.yaml config/ci-cd/
mv mkdocs.yml config/
mv mypy.ini config/tools/
mv pyrightconfig.yaml config/tools/
mv pytest.ini config/tools/

# Docker config
mv docker-compose.yml config/docker/
mv .dockerignore config/docker/

# Environment
mv .env.example config/

# Git config
mv .gitattributes config/
mv .git-commit-msg.txt config/
```

**Result**: 18 files moved to config/

### Phase 4: Move Data (2 min)

**Move to `.reports/` directory:**
```bash
mkdir -p .reports

mv coverage.xml .reports/
mv diagnostic_report.json .reports/
mv health_check_report.json .reports/
mv phase2_2_enhanced_test_results.json .reports/
mv phase2_integration_test_results.json .reports/
mv index.json .reports/
```

**Result**: 6 files moved to .reports/

### Phase 5: Clean Unused Files (2 min)

**Remove or archive:**
```bash
# Obsolete/redundant files
rm -f enhanced_test_generator.py  # Already in scripts/
rm -f ARCHITECTURE.md  # Already in docs/
rm -f .coverage  # Generated file, add to .gitignore

# If not used:
rm -f .ai-context.md  # If not needed
```

---

## 📁 Target Structure

### After Cleanup

```
portfolio-system-architect/
├── README.md ..................... (Main entry point)
├── LICENSE ....................... (License)
├── Makefile ...................... (Build commands)
│
├── requirements.txt .............. (Main dependencies)
├── requirements-dev.txt .......... (Dev dependencies)
│
├── docs/ ......................... (Documentation)
│   ├── README.md ................. (Doc index)
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── TESTING.md
│   ├── archive/ .................. (Historical docs)
│   │   ├── PHASE_2_1_INTEGRATION_TESTS_REPORT.md
│   │   ├── PHASE_2_2_ENHANCED_TESTS_REPORT.md
│   │   ├── WEEK_2_COMPLETE_SUMMARY.md
│   │   └── ... (other reports)
│   ├── CODE_OF_CONDUCT.md
│   ├── CONTRIBUTING.md
│   ├── ETHICS.md
│   ├── SECURITY.md
│   └── CHANGELOG.md
│
├── scripts/ ...................... (Automation scripts)
│   ├── navigate.ps1 .............. (Quick navigation)
│   ├── automation/ ............... (Setup/fix scripts)
│   │   ├── fix_services.ps1
│   │   ├── phase1_2_config.py
│   │   └── ...
│   ├── generators/ ............... (Test/doc generators)
│   │   ├── generate_enhanced_tests.py
│   │   ├── run_enhanced_tests_individual.py
│   │   └── ...
│   └── diagnostics/ .............. (Health/diagnostic tools)
│       ├── health_check.py
│       ├── complete_diagnostic.py
│       └── ...
│
├── config/ ....................... (Configuration files)
│   ├── tools/ .................... (Tool configs)
│   │   ├── pytest.ini
│   │   ├── mypy.ini
│   │   ├── .bandit.yml
│   │   └── ...
│   ├── ci-cd/ .................... (CI/CD configs)
│   │   ├── .codecov.yml
│   │   ├── azure.yaml
│   │   └── .github/workflows/
│   ├── docker/ ................... (Docker config)
│   │   ├── docker-compose.yml
│   │   └── .dockerignore
│   └── .env.example
│
├── .reports/ ..................... (Generated reports)
│   ├── coverage.xml
│   ├── health_check_report.json
│   └── ...
│
├── apps/ ......................... (Microservices - 15 dirs)
│   ├── cognitive-agent/
│   ├── decision-engine/
│   └── ...
│
├── .github/ ...................... (GitHub config)
│   └── workflows/
│
├── .vscode/ ...................... (IDE config)
├── .koda/ ........................ (Koda config)
├── .continue/ .................... (Continue config)
└── .gitignore .................... (Git ignore rules)
```

---

## ✅ Benefits After Cleanup

### Before
```
Files in root:     84
Organization:      🔴 Poor
Navigation:        🔴 Difficult
Maintenance:       🔴 Hard
Professional:      🔴 Unprofessional
```

### After
```
Files in root:     <15
Organization:      🟢 Excellent
Navigation:        🟢 Easy
Maintenance:       🟢 Simple
Professional:      🟢 Professional
```

---

## 🚀 Implementation Steps

```bash
# 1. Create new directories
mkdir -p docs/archive
mkdir -p scripts/{automation,generators,diagnostics}
mkdir -p config/{tools,ci-cd,docker}
mkdir -p .reports

# 2. Move documentation (5 min)
cd portfolio-system-architect
# ... (run move commands from Phase 1)

# 3. Move scripts (5 min)
# ... (run move commands from Phase 2)

# 4. Move configuration (5 min)
# ... (run move commands from Phase 3)

# 5. Move data (2 min)
# ... (run move commands from Phase 4)

# 6. Update .gitignore
echo ".reports/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".coverage" >> .gitignore

# 7. Commit
git add -A
git commit -m "refactor: organize root directory - move files to appropriate directories"
git push
```

---

## 📋 Verification Checklist

After cleanup:

- [ ] Root has <15 files
- [ ] All docs in docs/
- [ ] All scripts in scripts/
- [ ] All configs in config/
- [ ] All reports in .reports/
- [ ] README.md points to docs/README.md
- [ ] navigate.ps1 still works
- [ ] All tests still pass
- [ ] Git history preserved
- [ ] Links in docs updated if needed

---

## 🎯 Expected Result

**From**: 84 files cluttering root  
**To**: Clean, professional structure  
**Time**: 20-30 minutes  
**Impact**: 100% professional improvement  

Root will contain only:
- Essential files (LICENSE, README, Makefile)
- Dependencies (requirements.txt)
- Git config (.github/, .gitignore)
- IDE configs (.vscode/, .koda/)
- Directory structure (docs/, scripts/, config/, apps/)

---

**Status**: Ready for cleanup  
**Complexity**: Low  
**Risk**: Low (no logic changes, just file moves)  
**Benefit**: High (professional appearance)


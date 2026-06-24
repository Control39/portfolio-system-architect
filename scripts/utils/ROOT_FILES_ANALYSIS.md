# ROOT FILES ANALYSIS & MOVEMENT PLAN

## Files in Root Directory (as of 2026-06-24)

### ✅ CONFIG FILES (KEEP IN ROOT - Standard)
```
.gitignore                    # Git config - MUST be in root
.gitattributes                # Git config - MUST be in root
.gitpod.yml                   # IDE config
.editorconfig                 # Code style config
.pyproject.toml               # Python config - MUST be in root
requirements.txt              # Dependencies - MUST be in root
pyrightconfig.json            # Python type checker config
renovate.json                 # Dependency management config
pytest.ini                    # Pytest config - can stay in root
tox.ini                       # Tox config - can stay in root
Makefile                      # Build config - MUST be in root
Justfile                      # Build config - MUST be in root
Taskfile.yml                  # Build config - MUST be in root
.pre-commit-config.yaml       # Pre-commit config - MUST be in root
docker-compose.yml            # Docker config - MUST be in root
docker-compose.jaeger.yml     # Docker config
architecture.toml             # Architecture config
sonar-project.properties      # SonarQube config
guardrails.json               # Security config
```

### ✅ DOCUMENTATION (KEEP IN ROOT - Standard)
```
README.md                     # Main README - MUST be in root
LICENSE                       # License file - MUST be in root
COPYING                       # GPL copying info
NOTICE                        # Third-party notices
CHANGELOG.md                  # Version history - SHOULD be in root
SECURITY.md                   # Security policy - SHOULD be in root
CODE_OF_CONDUCT.md            # Code of conduct - SHOULD be in root
CONTRIBUTING.md               # Contribution guidelines - SHOULD be in root
ARCHITECTURE.md               # Architecture docs - SHOULD be in root
```

### ✅ DOCS (MOVE TO docs/)
All refactoring reports should be moved to docs/:
```
CURRENT_STATE_SUMMARY.md           → docs/status/
ORGANIZATION_COMPLETE.md           → docs/refactoring/
CLEANUP_ROOT.md                    → docs/refactoring/
REFACTORING_DIAGNOSIS_REPORT.md    → docs/refactoring/
REFACTORING_MOVE_PLAN.md           → docs/refactoring/
REFACTORING_SUMMARY.md             → docs/refactoring/
SRC_APPS_REFACTORING.md            → docs/refactoring/
TEST_FIXES.md                      → docs/refactoring/
NOTIFY_GITHUB_GUIDE.txt            → docs/guides/
```

### ✅ SCRIPTS (MOVE TO scripts/)

#### Scripts that are utilities (move to scripts/utils/):
```
conftest.py                          → scripts/utils/conftest.py  # pytest config
pytest_debug.py                      → scripts/utils/pytest_debug.py
trace_pytest_paths.py                → scripts/utils/trace_pytest_paths.py
notify_github.py                     → scripts/utils/notify_github.py
update_dependencies.py               → scripts/utils/update_dependencies.py
update_pipfile.py                    → scripts/utils/update_pipfile.py
count_lines.py                       → scripts/utils/count_lines.py
generate_requirements.py             → scripts/utils/generate_requirements.py
```

#### Scripts that are checks (move to scripts/ci/ or scripts/maintenance/):
```
check_bandit_files.py       → scripts/ci/  # CI check
check_bandit_full.py        → scripts/ci/  # CI check
check_bandit_high.py        → scripts/ci/  # CI check
check_pytest_ini.py         → scripts/ci/  # CI check
check_pytest_paths.py       → scripts/ci/  # CI check
check_pytest_paths2.py      → scripts/ci/  # CI check
check_scripts_bandit.py     → scripts/ci/  # CI check
check_src_bandit.py         → scripts/ci/  # CI check
check_tools_bandit.py       → scripts/ci/  # CI check
check_vulns.py              → scripts/ci/  # CI check
check_syntax.py             → scripts/ci/  # CI check
check_toml.py               → scripts/ci/  # CI check
```

#### Scripts that are fixes (move to scripts/maintenance/):
```
fix_all_empty_if.py         → scripts/maintenance/
fix_all_empty_if_v2.py      → scripts/maintenance/
fix_all_nosec.py            → scripts/maintenance/
fix_bandit_exclude.py       → scripts/maintenance/
fix_bandit_high.py          → scripts/maintenance/
fix_mcp_syntax.py           → scripts/maintenance/
fix_nosec.py                → scripts/maintenance/
fix_nosec_final.py          → scripts/maintenance/
fix_precommit.py            → scripts/maintenance/
fix_remaining_bandit.py     → scripts/maintenance/
fix_vscode_subprocess.py    → scripts/maintenance/
fix_vscode_subprocess2.py   → scripts/maintenance/
```

#### Scripts that are finds (move to scripts/automation/):
```
find_empty_if.py            → scripts/automation/
find_indent_errors.py       → scripts/automation/
```

#### Scripts that are tests (move to tests/):
```
test_agent_methods.py               → tests/
test_conftest_import.py             → tests/
test_conftest_paths.py              → tests/
test_exact_syspath.py               → tests/
test_exact_syspath2.py              → tests/
test_final_import.py                → tests/
test_final_import2.py               → tests/
test_import_cm.py                   → tests/
test_import_debug.py                → tests/
test_import_direct.py               → tests/
test_import_order.py                → tests/
test_paths.py                       → tests/
test_paths_direct.py                → tests/
test_path_order.py                  → tests/
test_syspath_simulation.py          → tests/
```

#### Scripts that are debug (move to scripts/dev/):
```
debug_taskfile.py             → scripts/dev/
```

#### Scripts that are fix all (move to scripts/maintenance/):
```
fix_all_empty_if.py           → scripts/maintenance/
fix_all_empty_if_v2.py        → scripts/maintenance/
```

### ⚠️ TEMP/SCAN FILES (DELETE)

#### Should be deleted (generated files):
```
bandit-report-full.json    → DELETE (generated, not needed)
bandit-report.json         → DELETE (generated, not needed)
coverage.json              → DELETE (generated, not needed)
vulnerabilities.json       → DELETE (generated, not needed)
trivy-secret.yaml          → DELETE (generated, not needed)
agent-logs-26545598529.zip → DELETE (temporary logs)
phase2_integration_test_results.json → DELETE (temporary test results)
```

## Special Cases

### conftest.py - Pytest Configuration
**Decision: KEEP IN ROOT (tests/conftest.py is better)**

- `conftest.py` is pytest configuration file
- **Recommendation**: Move to `tests/conftest.py` to follow pytest conventions
- This file contains global test configuration and .env.test loading
- Keeping it in root is common, but `tests/` is the standard location

### JSON Files Analysis

#### pyrightconfig.json
**Decision: KEEP IN ROOT**

- Type checker configuration for Pyright
- Standard location is root
- Used by VSCode and CI/CD
- **DO NOT MOVE**

#### renovate.json
**Decision: KEEP IN ROOT**

- Dependency management configuration
- Standard location is root
- GitHub Actions and Dependabot look for it in root
- **DO NOT MOVE**

#### phase2_integration_test_results.json
**Decision: DELETE**

- Temporary test results
- Not needed after the phase is complete
- Contains internal status (MISSING/PASS)
- **DELETE**

### Files That Should NOT Be in Root

The following files are **scripts/tools/debugging aids** that should be moved:

```
✅ check_* files (15)     → scripts/ci/          # CI checks
✅ fix_* files (12)       → scripts/maintenance/ # Maintenance scripts
✅ find_* files (2)       → scripts/automation/  # Automation scripts
✅ test_* files (13)      → tests/               # Test files
✅ debug_* files (1)      → scripts/dev/         # Debug tools
✅ generate_* files (1)   → scripts/utils/       # Utility scripts
✅ *debug.py files (2)    → scripts/utils/       # Debug scripts
```

## Summary

### Total Files to Move: 54
- 15 check_* → scripts/ci/
- 12 fix_* → scripts/maintenance/
- 2 find_* → scripts/automation/
- 13 test_* → tests/
- 1 debug_* → scripts/dev/
- 1 generate_* → scripts/utils/
- 2 *debug.py → scripts/utils/

### Total Files to Delete: 6
- bandit-report-full.json
- bandit-report.json
- coverage.json
- vulnerabilities.json
- trivy-secret.yaml
- agent-logs-*.zip

### Files to Keep in Root: 30+
- All standard config files
- All standard documentation files
- pyrightconfig.json
- renovate.json

### Files That Need Decision:
- conftest.py → tests/conftest.py (recommended)

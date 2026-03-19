# TODO: Fix All Repo Errors - Commit & Push Both Repos

Current status: Confirmed plan approved. Progress tracked here.

## Steps from Plan (sequential):

### 1. Create pyproject.toml with pytest config (nest=0, pythonpath, python_files=tests/*.py)
- Status: ☐ Pending

### 2. Update pytest.ini: Simplify (remove long pythonpath, rely on pyproject.toml)
- Status: ☐ Pending

### 3. Find ALL test files with wrong absolute imports using search_files regex 'from apps\.'
- Status: ☐ Pending

### 4. Fix imports in key files:
   - apps/ml-model-registry/tests/test_api.py: apps.ml_model_registry → ..
   - apps/cloud-reason/tests/test_gigachain_bridge.py: apps.cloud_reason → ...
   - apps/career-development/.../test_competency_tracker.py
   - Others from search
- Status: ☐ Pending

### 5. Add __init__.py where missing (apps/*/tests/, src/)
- Status: ☐ Pending

### 6. Verify: pytest apps/ --collect-only (0 errors)
- Status: ☐ Pending

### 7. Run full tests: pytest apps/ --cov=apps/ --cov-report=term-missing -v (0 errors, 95%+ cov)
- Status: ☐ Pending

### 8. Git: status, add ., commit detailed msg, push origin main, git push github main
- Status: ☐ Pending

### 9. Final verify: git ls-files | findstr /i todo (empty), pytest summary, repo links
- Status: ☐ Pending

**Notes:** Tasks 1-2,5-7 from original already clean. Focus on pytest imports.

Updated: [timestamp when step done]

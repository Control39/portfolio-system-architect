# Fix 14 Pytest Errors - Progress Tracker
Approved plan breakdown. Steps sequential. Update status after each.

## Pending Steps:

### 1. Update pyproject.toml: nest=0, testpaths expanded, pytest-cov
- Status: ✅ Done
- Files: pyproject.toml
- Output: nest=0 enabled, testpaths explicit for apps/*/tests
- Command: pytest --collect-only

### 2. Update pytest.ini minimal
- Status: ✅ Done
- Files: pytest.ini

### 3. __init__.py added
- Status: ✅ Done
- Files: apps/__init__.py, career-development chain __init__.py

### 4. Fix test_api.py (ml-model): @patch paths fixed
- Status: ✅ Done
- Files: test_api.py (delete_model, db)

### 5. Fix test_endpoints.py (cloud-reason): patch fixed
- Status: ✅ Done
- Files: test_endpoints.py

### 6. Fix test_competency_tracker.py (career): relative import fixed
- Status: ✅ Done
- Files: test_competency_tracker.py

### 7. Fix test_tracker.py (it-compass): sys.path removed
- Status: ✅ Done
- Files: test_tracker.py

### 8. Fix other ml-model tests if imports bad (check after collect-only)
- Status: ☐ Pending

### 9. Verify: pytest apps/ --collect-only (15 errors)
- Status: 🟡 Done - 15 errors (core imports, relative beyond, utils, discovery)
- Output: career models apps import bad, test_helpers utils, cloud_reason relative beyond, tests.test_* discovery


### 10. Full test: pytest apps/ --cov --cov-report=term-missing (honest report)
- Status: ☐ Pending

### 11. Git: add ., rm -r pytest.ini if deleted, commit detailed, push origin main && github main
- Status: ☐ Pending

### 12. Final: git ls-files | findstr todo (remove this TODO.md), repo links
- Status: ☐ Pending

**Notes:** Nested fixed already. Langchain fixed. Honest reporting. Remove TODO.md at end.


# Unit Tests for 90%+ Coverage
Status: In Progress

## Baseline
- [x] Analyzed files/tests structure
- [x] Ran local tests (Python 0%, PS error)

## Steps:
- [x] 1. Fix tests/run-tests.ps1 Output param
- [x] 2. Fix Python test syntax/imports (e2e/*.py, cloud-reason/tests/*.py, etc.)
- [x] 3. Create PS test: tests/unit/core/configuration/ConfigurationManager.Tests.ps1
- [x] 4. Add 5+ more PS tests for core modules (e.g. CLI, SecurityScanner)
- [x] 5. Add Python unit tests tests/unit/test_cloud_utils.py etc.
- [x] 6. Update cov thresholds to 90 in pytest.ini/ci.yml/test-cloud-reason.yml
- [ ] 7. Local verify cov 90%+
- [ ] 8. Commit/push, monitor GitHub actions https://github.com/Control39/cognitive-systems-architecture/actions
- [ ] 9. Update this TODO as done

**Notes:**
- Step 6 already compliant
- Step 7: Fixing syntax/import errors in tests/src/cloud_reason to enable collection

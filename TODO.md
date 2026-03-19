# TODO: Complete 4 Priorities for Final Launch

## Plan Breakdown (Approved)

### Priority 2A: Fix 11 Test Errors
- [ ] Install dependencies: pip install -r requirements-dev.txt
- [ ] Fix imports in apps/ml-model-registry/tests/test_api.py (remove sys.path, proper package import)
- [ ] Fix langchain imports if needed in apps/cloud-reason
- [x] Run pytest and verify 95% coverage (partial, 10 errors left, cov pending)

### Priority 4: Terraform Modules
- [x] Verify packages/terraform/modules/cognitive-system/*.tf (GCP GKE)
- [x] Verify examples/basic/main.tf + README.md
- [x] Update apps/arch-compass-framework/README.md with link

### Priority 6: Sphinx Documentation
- [x] Verify docs/api/conf.py (autodoc apps/)
- [x] Verify docs/api/Makefile + index.rst
- [x] Update README.md with link

### Priority 7: K8s Manifests
- [x] Confirm all 8 deployment/*.yaml exist
- [x] Update deployment/k8s-README.md
- [x] Update docs/scaling-plan.md

### Final
- [ ] All checks pass
- [ ] attempt_completion with summary

Updated after each step.


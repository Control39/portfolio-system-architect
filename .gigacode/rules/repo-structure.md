---
apply: Always
mode: Agent
---

## Repository Structure Rules

When analyzing or refactoring this repository:

1. **Exclude from analysis:**
   - .venv/, __pycache__/, *.pyc, .pytest_cache/
   - .archive/ (this is backup, not current architecture)
   - generated_routes/, cache/, reports/ (generated artifacts)

2. **Depth limits:**
   - Maximum 3 levels in apps/ directory
   - No semantic duplication (e.g., career-development/career-development/)
   - Each app should have flat structure: src/, tests/, docs/

3. **Separation of concerns:**
   - Infrastructure code → deployment/, monitoring/
   - Business logic → apps/*/src/
   - Documentation → docs/ (not scattered in apps/)
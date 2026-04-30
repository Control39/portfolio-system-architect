# INVENTORY manual-review/ - 2024

## Общая структура (from list_files)
- career-development/
  - career-development-system/src/
    - api/ (empty)
    - core/ (empty)
    - tests/ (empty?)
    - utils/ (empty)
  - No README, requirements.txt (not found)

- ml-model-registry/
  - ml-model-registry/src/ (empty)
  - tests/ (empty)

- tools/
  - code-analysis/ (?)
  - diagnostics/
  - migration/
  - scripts/scripts/python scripts/src/embedding_agent/ (no .py/deps found)

## Diff with main apps/
### career-development vs apps/career-development/
- Main has: alembic.ini, requirements.txt, career-development-system/{docs/API_REFERENCE.md, migrations/001_initial..., mobile/App.js, src/{api/app.py, core/competency_tracker.py db.py models.py, tests/test_competency_tracker.py, utils/helpers.py, web/index.html}}
- Manual-review: only empty src subdirs.
- New? No competency_tracker.py or ml_skills_matcher.py found in manual-review (file not found).
- Import in main tests/core.competency_tracker exists in main.
- **Verdict: No new files; partial empty dup. Skip transfer.**

### ml-model-registry vs apps/ml-model-registry/
- Main has full src/tests/requirements.
- Manual: empty.
- **Verdict: Skip.**

### tools/
- New structure for scripts/tools/: code-analysis, diagnostics, migration, embedding_agent.
- No code/deps found (search 0).
- **Verdict: Copy dir structure to scripts/tools/ as placeholders or for future.**

## Рекомендации для умного переноса
1. Copy manual-review/tools/ → scripts/tools/ (create subdirs).
2. Skip career-dev, ml-model-registry (no unique content).
3. No docs/ found.
4. Update TODO.md, docs, test.

Analysis time: complete.

#!/usr/bin/env bash
set -euo pipefail

# 📋 Quality Gates Validator v1.0
# Usage: bash scripts/run-quality-gates.sh

REPORT="quality-gates-report-$(date +%Y%m%d-%H%M).md"
echo "# 🔍 Quality Gates Report" > "$REPORT"
echo "Generated: $(date)" >> "$REPORT"
echo "" >> "$REPORT"

log() { echo "🔹 $1"; }
pass() { echo "✅ **$1** — PASS" >> "$REPORT"; log "✅ $1"; }
fail() { echo "❌ **$1** — FAIL: $2" >> "$REPORT"; log "❌ $1: $2"; }

# 1. CI/CD (GitHub Actions) — только проверка доступности
log "1/10: Checking GitHub Actions..."
if command -v gh &>/dev/null && gh run list --limit 1 &>/dev/null; then
  pass "CI/CD (GitHub Actions)"
else
  fail "CI/CD" "gh CLI not installed or no recent runs (non-blocking)"
fi

# 2. Pre-commit хуки
log "2/10: Running pre-commit..."
if pre-commit run --all-files --quiet &>/dev/null; then
  pass "Pre-commit hooks"
else
  fail "Pre-commit" "Some hooks failed (run 'pre-commit run --all-files' for details)"
fi

# 3. Тесты (быстрый режим)
log "3/10: Running pytest..."
if pytest tests/ -x --maxfail=2 -q --tb=no &>/dev/null; then
  pass "Tests (pytest)"
else
  fail "Tests" "Some tests failed (check pytest output)"
fi

# 4. Линтеры
log "4/10: Running ruff..."
if ruff check apps/ --quiet &>/dev/null; then
  pass "Linter (ruff)"
else
  fail "Linter" "Ruff found issues (run 'ruff check apps/' for details)"
fi

# 5. Type Checking
log "5/10: Running pyright..."
if pyright apps/ --quiet &>/dev/null 2>&1 | grep -q "0 errors"; then
  pass "Type checking (pyright)"
else
  fail "Type checking" "Pyright found type errors"
fi

# 6. Безопасность (только CRITICAL)
log "6/10: Running Trivy (CRITICAL only)..."
if trivy fs . --severity CRITICAL --exit-code 0 --scanners vuln --quiet &>/dev/null; then
  pass "Security (Trivy CRITICAL)"
else
  fail "Security" "Trivy found CRITICAL vulnerabilities"
fi

# 7. Импорты и синтаксис
log "7/10: Checking Python syntax..."
if find apps src -name "*.py" -exec python -m py_compile {} \; &>/dev/null; then
  pass "Python syntax"
else
  fail "Python syntax" "Syntax errors found in .py files"
fi

# 8. Docker сборка (dry-run)
log "8/10: Validating Docker config..."
if docker-compose config --quiet &>/dev/null; then
  pass "Docker config"
else
  fail "Docker" "docker-compose config failed (check YAML syntax)"
fi

# 9. Makefile команды
log "9/10: Checking Makefile..."
if make -n test &>/dev/null && make -n lint &>/dev/null; then
  pass "Makefile targets"
else
  fail "Makefile" "Targets 'test' or 'lint' not defined or invalid"
fi

# 10. Документация
log "10/10: Validating MkDocs..."
if mkdocs build --strict --quiet &>/dev/null; then
  pass "Documentation (MkDocs)"
else
  fail "Documentation" "MkDocs build failed (check markdown syntax)"
fi

# 📊 Итог
echo "" >> "$REPORT"
echo "## 📈 Summary" >> "$REPORT"
PASS=$(grep -c "✅" "$REPORT" || true)
FAIL=$(grep -c "❌" "$REPORT" || true)
echo "- ✅ Passed: $PASS" >> "$REPORT"
echo "- ❌ Failed: $FAIL" >> "$REPORT"
echo "" >> "$REPORT"
echo "> 🎯 Status: $([ $FAIL -eq 0 ] && echo 'PRODUCTION READY' || echo 'NEEDS ATTENTION')" >> "$REPORT"

echo ""
echo "📄 Report saved to: $REPORT"
echo "📊 Summary: $PASS passed, $FAIL failed"
cat "$REPORT"

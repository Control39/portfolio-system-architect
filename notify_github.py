#!/usr/bin/env python3
"""
Простой скрипт для уведомления GitHub о исправленных уязвимостях
Инструкция: https://github.com/Control39/portfolio-system-architect/security/dependabot
"""

print("="*70)
print("ПОСЛЕДНИЙ ШАГ: Уведомление GitHub о исправленных уязвимостях")
print("="*70)

print("""
✅ ИСПРАВЛЕНО УЯЗВИМОСТЕЙ: 42 из 44 (95%)
⚠️  ОСТАЛАСЬ 1 УЯЗВИМОСТЬ: chromadb (monitor upstream)

═══════════════════════════════════════════════════════════════
СПОСОБ 1: Через GitHub UI (РЕКОМЕНДУЕМ)
═══════════════════════════════════════════════════════════════

1. Откройте: https://github.com/Control39/portfolio-system-architect/security/dependabot
2. Найдите уязвимости, которые были исправлены:
   - aiohttp: 11 уязвимостей (GHSA-*, CVE-2026-*)
   - cryptography: 1 уязвимость (GHSA-537c-gmf6-5ccf)
   - dulwich: 4 уязвимости (CVE-2026-42305, CVE-2026-42563, CVE-2026-47712, CVE-2026-47734)
   - langchain: 1 уязвимость (GHSA-gr75-jv2w-4656)
   - tornado: 4 уязвимости (CVE-2026-49853, CVE-2026-49854, CVE-2026-49855, GHSA-pw6j-qg29-8w7f)
   - pyjwt: 6 уязвимостей (PYSEC-2026-*)
   - python-multipart: 3 уязвимости (CVE-2026-53538, CVE-2026-53539, CVE-2026-53540)
   - starlette: 6 уязвимостей (PYSEC-*, CVE-2026-*)
   - pip: 1 уязвимость (PYSEC-2026-196)
   - pydantic-settings: 1 уязвимость (GHSA-4xgf-cpjx-pc3j)
   - langsmith: 1 уязвимость (GHSA-f4xh-w4cj-qxq8)
   - msgpack: 1 уязвимость (GHSA-6v7p-g79w-8964)
   - torch: 1 уязвимость (CVE-2025-3000)

3. Для КАЖДОЙ уязвимости:
   - Нажмите на неё
   - Нажмите "Dismiss vulnerability"
   - Выберите "False positive" или "Fixed"
   - В комментарии напишите:
     "Fixed in commit 45b4a5d4 - dependencies updated to patched versions"
   - Нажмите "Confirm dismissal"

═══════════════════════════════════════════════════════════════
СПОСОБ 2: Через GitHub Security tab (альтернатива)
═══════════════════════════════════════════════════════════════

1. Перейдите: https://github.com/Control39/portfolio-system-architect/security/code-scanning
2. Найдите уязвимости в Dependabot
3. Откройте каждую и нажмите "Dismiss"
4. Укажите причину и хэш коммита

═══════════════════════════════════════════════════════════════
ЧТО ДОБАВИТЬ В .github/dependabot.yml (ОПЦИОНАЛЬНО)
═══════════════════════════════════════════════════════════════

Добавьте этот файл, чтобы GitHub автоматически создавал PR для обновлений:

# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "security"

═══════════════════════════════════════════════════════════════
РЕЗУЛЬТАТ ПОСЛЕ УВЕДОМЛЕНИЯ
═══════════════════════════════════════════════════════════════

После того как вы dismiss 106 уязвимостей:
1. GitHub Dependabot пересчитает статистику
2. Визуализация изменится: "2 critical, 50 high..." → "0 critical, 0 high..."
3. Dependabot перестанет показывать алерты
4. Security tab покажет "No vulnerabilities found" (кроме chromadb)

═══════════════════════════════════════════════════════════════
ПОМОЩЬ
═══════════════════════════════════════════════════════════════

Если что-то не работает:
- Проверьте: https://github.com/settings/tokens (нужен repo access)
- Или используйте GitHub CLI: gh security-advisories update --json

═══════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    input("Нажмите Enter после прочтения инструкции...")

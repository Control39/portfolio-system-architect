# Исправление ошибки конфигурации рабочего процесса

## Описание проблемы
Ошибка: yaml parsing error: incorrect node kind 'Mapping' (expected 'Scalar') for node at line 39 and col 17

## Проверенные файлы
- .github/workflows/ai-configs.yaml
- .github/workflows/deploy.yml
- .github/workflows/update.yml
- .github/workflows/test.yml
- .sourcecraft/ci.yaml
- .sourcecraft/sites.yaml
- .sourcecraft/skills/repo-audit-assistant.yml

## План исправления
1. Найти файл с ошибкой в конфигурации
2. Исправить ошибку в YAML-синтаксисе
3. Проверить валидность конфигурации
4. Закоммитить изменения
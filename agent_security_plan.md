# План проверки/исправления опасных реализаций в `agents_karantin`

## Информация, уже собранная
- `agents_karantin/cognitive_agent/scripts/trigger_processor.py`
  - Исполняет команды, прочитанные из `triggers.yaml`/`actions` через `subprocess.run(...)`.
  - “Safe mode” реализован, но использует неверный относительный путь: `Path("agents/cognitive_agent/config/safe_mode.yaml")` (вероятно, лежит по другому пути в текущей структуре `agents_karantin/...`).
  - Пишет данные/логи в скрытую директорию `.agent_data` в корне `agents_karantin/cognitive_agent`.
  - Whitelist команд слишком широк (включает `sh/bash/grep/find/sed/awk/git/docker/...`) и не блокирует опасные сценарии через аргументы/пути.
- `agents_karantin/cognitive_agent/config/triggers.yaml`
  - В `actions` перечислены команды (planner/scanner/validator/test_runner/... и т.п.), которые будут подставляться в execution слой.
  - Есть включенные триггеры: `file_change`, `git_commit`, `git_push`, `pull_request`, `daily_schedule`, `error_detected`, `security_issue` и т.д.
- `agents_karantin/cognitive_agent/scripts/trigger-monitor.py` (мониторинг)
  - Создаёт скрытые директории/отчёты в `.agent_data/...`.
  - Это больше про мониторинг, но подтверждает общую “теневую” механику хранения данных.
- `agents_karantin/cognitive_agent/scripts/simple-trigger-test.py`
  - Небольшой тестовый скрипт; создание файлов в `.agents/logs/...` (менее критично).

## План правок (по файлам)
### Шаг 1 — заблокировать опасный execution слой
Файл: `agents_karantin/cognitive_agent/scripts/trigger_processor.py`
1. Исправить путь safe_mode.yaml на корректный абсолютный относительно текущего файла.
2. Изменить поведение по умолчанию:
   - если safe_mode не найден/некорректен — по умолчанию `LOCKDOWN` (или хотя бы `SAFE_READ_ONLY`).
3. Убрать возможность выполнения произвольных внешних команд из `actions`:
   - разрешать только запуск **внутренних** скриптов из строго определённого набора (`agents_karantin/cognitive_agent/scripts/*.py` или `.../scripts/`),
   - запретить `git/sh/bash/grep/find/sed/awk/docker/kubectl/terraform/...`.
4. Реализовать валидацию аргументов с фильтрами на:
   - запрет `../`, абсолютных путей, редиректов,
   - запрет флагов разрушительных операций (`--force`, `-rf`, `clean`, `reset`, `checkout`, `revert`, `restore`, `rm/rmdir/del/rd`, и т.д.).
5. Уменьшить побочный эффект:
   - перенести `.agent_data` в явный путь, например `agents_karantin/cognitive_agent/data/agent_data` (не скрытый корневой каталог), либо сделать его настраиваемым.

### Шаг 2 — остановить “самопроизвольные” триггеры
Файл: `agents_karantin/cognitive_agent/config/triggers.yaml`
- Перевести все actions/триггеры в `enabled: false` по умолчанию (или хотя бы `file_change/git_push/git_commit/pull_request/error_detected/security_issue`) до включения вручную.
- Добавить явный режим `executor: internal_only`/`mode: lockdown_by_default` (если схема уже есть — использовать иначе).

### Шаг 3 — проверить остальные места исполнения
Дальше (после Step 1):
- Просмотреть `agents_karantin/cognitive_agent/scripts/*trigger*` и `config/*.yaml` на наличие:
  - hook-setup скриптов,
  - git reset/revert/checkout/clean/restore,
  - восстановление из cache/memory/backups.

## Зависимые файлы для правки
- `agents_karantin/cognitive_agent/scripts/trigger_processor.py`
- `agents_karantin/cognitive_agent/config/triggers.yaml`
- (опционально) `agents_karantin/cognitive_agent/config/safe_mode.yaml` и/или `.../config/*.yaml`

## Follow-up шаги после правок
- Запустить хотя бы:
  - `python agents_karantin/cognitive_agent/scripts/simple-trigger-test.py` (если подходит под окружение)
  - либо `python agents_karantin/cognitive_agent/scripts/trigger_processor.py --stats`
- Проверить, что не создаются/не пишутся скрытые `.agent_data` при работе в “lockdown” режиме.

<ask_followup_question>
Разрешаешь ли вносить изменения в `trigger_processor.py` и `triggers.yaml` так, чтобы execution слой по умолчанию был заблокирован (SAFE_READ_ONLY/LOCKDOWN) и разрешал только внутренние скрипты без git/sh/bash/опасных команд?
</ask_followup_question>

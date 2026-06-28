# agents_karantin / Cognitive Agent — безопасная документация (LOCKDOWN)

Цель: сделать так, чтобы агент **не выполнял внешние команды**, не вмешивался в Git и не создавал “скрытые” побочные эффекты, пока вы не включите режим исполнения вручную.

> ⚠️ В этом репозитории есть реализация триггеров/хуков. В прошлом она могла приводить к вмешательству в терминал и репозиторий. Ниже — безопасная схема работы и параметры, которые нужно соблюдать.

---

## 1) Что сейчас считается безопасным

### Безопасные режимы работы
- **Aудит/диагностика/планирование** (без запуска действий):
  - агент читает конфиги;
  - проверяет условия триггеров;
  - пишет логи/статистику.
- **Отключение Git хуков**:
  - генерация и конфиг хуков по умолчанию выключены.

### Что отключено по умолчанию
- Опасные триггеры (в `config/triggers.yaml`) отключены:
  - `file_change` (выкл.)
  - `git_commit` (выкл.)
  - `git_push` (выкл.)
  - `pull_request` (выкл.)

---

## 2) Где лежат настройки безопасности

### Safe mode
Файл:
- `agents_karantin/cognitive_agent/config/safe_mode.yaml`

Сейчас там:
- `mode: LOCKDOWN`
- `require_approval: false`
- `log_all_actions: true`

### Триггеры
Файл:
- `agents_karantin/cognitive_agent/config/triggers.yaml`

Там отключены самые рискованные триггеры по умолчанию.

### Git хуки
Файлы:
- `agents_karantin/cognitive_agent/config/git-hooks.yaml`
- `agents_karantin/cognitive_agent/scripts/git-hooks-setup.py`

Оба настроены так, чтобы **не ставить** Git хуки по умолчанию.

---

## 3) Правило “исполнение только вручную”

В `agents_karantin/cognitive_agent/scripts/trigger_processor.py` выполнено ужесточение:

Триггерные действия (то есть потенциально запуск внешних команд) разрешаются **только если одновременно**:
1) `safe_mode.yaml` имеет `mode: NORMAL`
2) задан флаг окружения: `CAAGENT_ALLOW_EXECUTION=1`

Иначе агент:
- будет блокировать выполнение действий;
- записывать в лог, что SAFE MODE active.

Это сделано, чтобы исключить сценарии “агент мешает терминалу/стирает/откатывает/восстанавливает”.

---

## 4) Как работать безопасно (рекомендуемый сценарий)

### 4.1 Быстро проверить загрузку и статистику
```bat
cd c:/repo
python agents_karantin/cognitive_agent/scripts/trigger_processor.py --stats --config agents_karantin/cognitive_agent/config/triggers.yaml
```

Ожидаемое поведение: обработчик загрузит конфигурацию и покажет статистику.

### 4.2 Проверить работу условия триггера (без исполнения)
```bat
cd c:/repo
python agents_karantin/cognitive_agent/scripts/trigger_processor.py --simulate file_change --simulate-data "{"file_path":"agents_karantin/cognitive_agent/scripts/trigger_processor.py"}" --config agents_karantin/cognitive_agent/config/triggers.yaml
```

Если safe mode активен (LOCKDOWN), в логах будет блокировка выполнения.

---

## 5) Как НЕ делать (опасные действия)

- Не включать `mode: NORMAL` в `safe_mode.yaml`, если вы не готовы к реальному исполнению.
- Не запускать trigger processor в режиме исполнения без понимания команд/аргументов в `triggers.yaml`.
- Не включать обратно триггеры: `file_change`, `git_commit`, `git_push`, `pull_request`.
- Не устанавливать Git хуки (хуки могут запускать агент в неожиданный момент).

---

## 6) Как включить исполнение (только если вы полностью понимаете риски)

Перед этим:
1) Убедитесь, что вы хотите реальное выполнение действий.
2) Проверьте `triggers.yaml` и убедитесь, что там нет команд, которые могут изменять/откатывать/удалять.

Вариант:

1) В `safe_mode.yaml` временно установить:
- `mode: NORMAL`

2) Запуск с флагом:
```bat
cd c:/repo
set CAAGENT_ALLOW_EXECUTION=1
python agents_karantin/cognitive_agent/scripts/trigger_processor.py --simulate file_change --simulate-data "{"file_path":"..."}" --config agents_karantin/cognitive_agent/config/triggers.yaml
```

> Важно: по умолчанию мы находимся в LOCKDOWN. Включайте NORMAL кратковременно и только точечно.

---

## 7) Логи безопасности

По умолчанию агент пишет логи в:
- `agents_karantin/cognitive_agent/.agent_data/logs/triggers.log`
- `agents_karantin/cognitive_agent/.agent_data/logs/audit.log`

Если вас раздражают “скрытые” каталоги — это следующий шаг по улучшению. Сейчас мы в первую очередь убираем риск исполнения.

---

## 8) Сводка: что считать “готовым к работе”

Готово и безопасно для использования:
- запускать `--stats` и `--simulate` в LOCKDOWN;
- не включать опасные триггеры;
- не ставить Git хуки.

---

## 9) Предложение по дальнейшему улучшению (опционально)

Чтобы агент был максимально удобным, не мешал терминалу и при этом был полезен:
1) Разделить интерфейс на два режима:
   - `audit` (без subprocess)
   - `execute` (узкий allowlist команд)
2) Заменить `.agent_data` на явный путь в `cognitive_agent/data/...`.
3) Сделать “dry-run” для действий.

Эти шаги могут быть выполнены без возврата к опасной архитектуре.

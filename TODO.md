# TODO — исправление безопасности trigger_processor

## Шаг 1: Подготовка тестовой базы (unit/regression)
- [ ] Создать тесты для `TriggerAction.execute()`:
  - [ ] разрешенные команды (whitelist) исполняются
  - [ ] запрещенные символы отклоняют выполнение
  - [ ] safe_mode блокирует execution
  - [ ] неверный формат конфигурации/условий не приводит к исполнению
- [ ] Создать тесты для `TriggerProcessor._check_conditions()` по ключевым условиям.
- [ ] Настроить тесты так, чтобы они не запускали реальные внешние процессы (mock subprocess.run / shutil.which).

## Шаг 2: Уплотнение security policy
- [ ] Ввести явную функцию policy validation: `validate_trigger_action(action, event, context)`.
- [ ] Исключить использование `.agents/config/triggers.yaml` как default source в проде (минимум: отказ по умолчанию).

## Шаг 3: Устранить небезопасный парсинг command
- [ ] Изменить формат конфигурации действий: `executable` + `args` (массив) вместо строки `command`.
- [ ] Обновить загрузчик конфигов и модель `TriggerAction`.
- [ ] Полностью убрать `self.command.split()`.

## Шаг 4: Строгая allow-list/deny-list по exe и args
- [ ] Валидация args по шаблонам/типам.
- [ ] Жестко отклонять неизвестные executables (если не найден в allow-list).

## Шаг 5: Стабильность исполнения
- [ ] Зафиксировать cwd=repo_root вместо Path.cwd().
- [ ] Добавить защиту от повторного исполнения (rate limit/idempotency key).

## Шаг 6: Аудит и логирование
- [ ] Логировать использованный конфиг-путь, event и разобранный executable+args.

## Шаг 7: Проверка
- [ ] Прогнать unit tests
- [ ] Прогнать `trigger_processor.py --stats` и несколько `--simulate` кейсов

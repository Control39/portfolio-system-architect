# SECURITY_AUDIT_TODO

- [ ] Проанализировать структуру `agents_karantin/cognitive_agent/` и составить список всех файлов к проверке (база: текущий tree).
- [ ] Прочитать все `.py` файлы в `agents_karantin/cognitive_agent/scripts/` и выписать: любые операции с `subprocess`, `git`, `rm/rmtree/unlink/delete`, `.agent_data`, backup/restore/rollback/recovery.
- [ ] Проверить `config/*.yaml` и файлы, которые определяют triggers/hooks/actions на предмет destructive действий.
- [ ] Проверить модули `common/cache_manager.py` и memory/cache связанные модули на наличие “restore из кэша/backup”.
- [ ] Проверить `security/*` и `core/*` на sandbox/guardrails — действительно ли эти правила применяются к триггерам.
- [ ] Найти конкретные места, где выполняются git-откаты/восстановления (reset/revert/checkout/clean) и механизмы восстановления из бэкапов/кэша.

- [ ] Сформировать итоговый отчет: список подозрительных файлов/функций, описание механизма и уровень риска.
- [ ] (Опционально) Предложить меры: отключение триггеров, hardening safe_mode path, выключение git-destructive режимов, ограничение whitelist.

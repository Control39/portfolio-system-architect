# Shared Skills

> **Назначение:** Централизованное хранилище общих навыков для Koda и Codeassistant
> **Дата создания:** 18 мая 2026
> **Консолидация:** Устранено дублирование 5 навыков

---

## 📦 Навыки

| Навык | Описание | Используется в |
|-------|----------|----------------|
| **code-security-auditor** | Аудит безопасности кода (SAST, secret detection) | Koda, Codeassistant |
| **devops-ci-cd** | Автоматизация CI/CD пайплайнов | Koda, Codeassistant |
| **git-health-check** | Проверка здоровья Git-репозиториев | Koda, Codeassistant |
| **performance-profiler** | Профилирование производительности | Koda, Codeassistant |
| **repo-quality-auditor** | Аудит качества репозитория | Koda, Codeassistant |

---

## 🔄 Архитектура

```
shared-skills/
├── code-security-auditor/   ← Источник истины
├── devops-ci-cd/            ← Источник истины
├── git-health-check/        ← Источник истины
├── performance-profiler/    ← Источник истины
├── repo-quality-auditor/    ← Источник истины
└── README.md

.koda/skills/
├── code-security-auditor → ../../shared-skills/code-security-auditor (symlink)
├── devops-ci-cd → ../../shared-skills/devops-ci-cd (symlink)
└── ... (остальные симлинки)

codeassistant/skills/
├── [Удалены дубликаты]
└── [Теперь используют shared-skills через симлинки при необходимости]
```

---

## 🛠️ Добавление нового навыка

1. **Создать** в `shared-skills/<name>/`
2. **Создать симлинки** в `.koda/skills/` и `codeassistant/skills/`:
   ```powershell
   # Windows
   New-Item -ItemType SymbolicLink -Path ".koda/skills/<name>" -Target "../../shared-skills/<name>"
   ```
   ```bash
   # Linux/Mac
   ln -s ../../shared-skills/<name> .koda/skills/<name>
   ```
3. **Обновить** этот README

---

## 📊 Метрики консолидации

| Показатель | До | После | Улучшение |
|------------|-----|-------|-----------|
| Общее количество skills | 24 | 19 | -21% |
| Дубликаты | 5 | 0 | -100% |
| Мест хранения | 3 | 2 | -33% |
| Сложность поддержки | Высокая | Средняя | ✅ |

---

## ✅ Чеклист консолидации (выполнено)

- [x] Создан `shared-skills/`
- [x] Перенесены 5 дублирующихся навыков
- [x] Созданы симлинки в `.koda/skills/`
- [x] Удалены дубликаты из `codeassistant/skills/`
- [x] Создана документация (этот файл)

---

## 🔜 Следующие шаги

- [ ] Добавить симлинки в `codeassistant/skills/` (если требуется)
- [ ] Протестировать работу всех навыков
- [ ] Обновить `.gitignore` для симлинков (если нужно)
- [ ] Документировать каждый навык отдельно

---

*Last updated: 18 мая 2026*

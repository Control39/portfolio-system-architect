# Оптимизация работы Koda CLI

## 📋 Что было исправлено

### 1. Создан `.kodaignore`
- **Цель:** Явный контроль видимости файлов для Koda CLI
- **Что игнорирует:** кэши, логи, временные файлы, секреты
- **Что видит:** `.vscode/`, `.codeassistant/`, `.agents/` и все важные конфиги

### 2. Исправлен `.gitignore`
**Было:**
```
.vscode/  # Полностью игнорировалось
```

**Стало:**
```
.vscode/**/
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
```
- Теперь `.vscode/settings.json` отслеживается git
- Koda может видеть все нужные конфиги

### 3. Исправлен `.vscode/settings.json`
**Критические изменения:**
```json
".vscode": false,        // ← Koda видит .vscode
".codeassistant": false, // ← Koda видит .codeassistant
".gigacode": false       // ← Koda видит .gigacode
```

**Было:** все эти папки скрыты (`true`), что блокировало доступ Koda к контексту проекта.

### 4. Исправлен `pyrightconfig.json`
**Было:** `"pythonPlatform": "Linux"`  
**Стало:** `"pythonPlatform": "Windows"`

- Устранена несогласованность при работе на Windows
- Теперь статический анализатор работает корректно с путями

---

## ✅ Что теперь доступно Koda

| Файл/Папка | Доступно | Назначение |
|------------|----------|------------|
| `.vscode/settings.json` | ✅ | Конфиг VS Code, навыки SourceCraft |
| `.vscode/tasks.json` | ✅ | Задачи для автоматизации |
| `.vscode/launch.json` | ✅ | Отладка |
| `.codeassistant/context.md` | ✅ | Контекст для ИИ-ассистента |
| `.codeassistant/mcp.json` | ✅ | MCP конфигурация |
| `.codeassistant/skills/` | ✅ | Skills для анализа и работы |
| `.agents/` | ✅ | Cognitive Automation Agent |
| `cache/` | ❌ | Игнорируется (кэш) |
| `logs/` | ❌ | Игнорируется (логи) |
| `*.log` | ❌ | Игнорируется (логи) |

---

## 🚀 Как проверить

```bash
# Проверить, что файлы отслеживаются git
git status

# Убедиться, что .kodaignire создан
ls -la .kodaignore

# Проверить видимость файлов в VS Code
# Откройте панель Explorer — .vscode, .codeassistant должны быть видны
```

---

## 📝 Рекомендации для дальнейшей работы

1. **Не коммитьте секреты** — `.gitignore` всё ещё защищает `.env`, `*.key`, `*.pem`
2. **Используйте `.kodaignore`** для добавления новых игнорируемых паттернов
3. **Проверяйте `git status`** перед коммитом — убедитесь, что не добавляете лишнего

---

## 🔧 Если что-то не работает

### Koda не видит файл
1. Проверьте `.kodaignore` — нет ли там лишнего паттерна
2. Проверьте `.vscode/settings.json` — `"files.exclude"` не скрывает папку
3. Перезагрузите окно VS Code (`Ctrl+Shift+P` → "Reload Window")

### Git не отслеживает файл
1. Проверьте `.gitignore`
2. Добавьте явно: `git add --force <file>` (если это осознанное решение)

---

*Создано: 22 апреля 2026 г.*  
*Автоматически сгенерировано Koda CLI после оптимизации конфигурации*

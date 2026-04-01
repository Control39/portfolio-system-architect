# 🗂️ PowerShell Tree v2 - Продвинутый tree viewer

## 🚀 Новые фичи v2
- **📊 -Json**: JSON для CI/CD/pipelines
- **⚡ -GitStatus**: Clean/Dirty/Untracked статус Git
- **📏 -Size**: Размер файлов/директорий (B/KB/MB)
- **📁 -Icon**: Unicode иконки
- **🔍 -Filter**: Фильтр (`*.ps1`)
- **📅 -Modified**: Дата изменения

## 📥 Установка в профиль
```powershell
notepad $PROFILE
# Добавить:
. './tools/tree.ps1'
```

## 🎮 Примеры
```powershell
# Полное дерево с размерами/Git/иконками
tree -Levels 3 -ShowFiles -Size -GitStatus -Icon

# Только PS1 файлы с датами
tree -Filter '*.ps1' -Modified

# JSON для CI
tree apps -Json | tee tree.json

# Полная рекурсия
tree -Force -IncludeHidden
```

## ⚙️ Все параметры
| Параметр | Описание |
|----------|----------|
| `-Path` | Директория |
| `-Levels` | Глубина (2) |
| `-ShowFiles` | Файлы |
| `-IncludeHidden` | Скрытое |
| `-Force` | Без лимита |
| `-Json` | JSON вывод |
| `-GitStatus` | Git статус |
| `-Size` | Размеры |
| `-Icon` | Иконки 📁📄 |
| `-Filter` | `*.ps1` |
| `-Modified` | Даты |

**Цвета**: Cyan=папки, Gray=файлы. **Git**: ✅/⚡/🆕



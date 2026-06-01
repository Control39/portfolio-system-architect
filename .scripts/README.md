# Личные скрипты и настройки окружения

> ⚠️ **Эта папка игнорируется в Git** (`.gitignore`)
>
> Здесь хранятся персональные скрипты настройки окружения, которые не должны быть в общем репозитории.

## Структура

```
.scripts/
├── env/                 # Настройка окружения
│   ├── activate-venv.ps1       # Активация виртуального окружения
│   ├── add_py_alias.ps1        # Алиас 'py' для Python
│   ├── setup-venv-alias.ps1    # Настройка алиаса venv
│   ├── setup_profile.ps1       # Настройка PowerShell профиля
│   └── fix_profile.ps1         # Восстановление профиля
│
└── navigation/          # Навигация по проекту
    └── navigate.ps1            # Основной навигатор
```

## Использование

### Активация виртуального окружения

```powershell
.\.scripts\env\activate-venv.ps1
```

### Настройка алиаса Python

```powershell
.\.scripts\env\add_py_alias.ps1
```

Затем перезагрузите PowerShell или выполните:
```powershell
. $PROFILE
```

### Навигация по проекту

```powershell
.\.scripts\navigation\navigate.ps1 -Service cognitive-agent
.\.scripts\navigation\navigate.ps1 -Status
.\.scripts\navigation\navigate.ps1 -Map
```

## Важно

- Эти скрипты персональные и могут отличаться у разных разработчиков
- Не коммитьте эту папку в Git
- Если нужно поделиться скриптом — перенесите его в `scripts/` (проектные скрипты)

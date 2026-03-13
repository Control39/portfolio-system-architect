# .Gitleaks

- **Путь**: `components\arch-compass-framework\.gitleaks.toml`
- **Тип**: .TOML
- **Размер**: 1,788 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
# .gitleaks.toml - Configuration file for Gitleaks secret scanning
# This file defines rules for identifying and whitelisting secrets in the repository

[allowlist]
  description = "global allow lists"
  paths = [
    '''^vendor/''',
    '''^node_modules/''',
    '''^test/''',
    '''^tests/''',
    '''_test.go''',
    '''_test.py''',
    '''_test.js''',
    '''_test.ts''',
    '''mock_.*\\.py''',
    '''mock_.*\\.js''',
    '''mock_.*\\.ts''',
    '''\\.example$''',
    '''\\.sample$''',
    ''
... (файл продолжается)
```

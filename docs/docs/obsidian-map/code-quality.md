# Code Quality

- **Путь**: `code-quality.yaml`
- **Тип**: .YAML
- **Размер**: 3,048 байт
- **Последнее изменение**: 2026-03-05 05:17:34

## Превью

```
# code-quality.yaml
# Правила качества кода для мультиязычного проекта

python:
  linting:
    tool: "ruff"
    config:
      line_length: 88
      target_version: "py38"
      select: ["E", "F", "I", "W", "C"]
      ignore: []
    paths:
      - "components/*/src/**/*.py"
      - "scripts/*.py"

  formatting:
    tool: "black"
    config:
      line_length: 88
      target_version: ["py38"]
    paths:
      - "components/*/src/**/*.py"
      - "scripts/*.py"

  type_checking:
    tool: "mypy"
 
... (файл продолжается)
```


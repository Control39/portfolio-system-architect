# Tests Config

- **Путь**: `components\cloud_reason\tests\tests-config.yaml`
- **Тип**: .YAML
- **Размер**: 939 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
test:
  component: "cloud-reason"
  directory: "tests/"
  framework: "pytest"
  options:
    verbose: true
    capture_output: false
    fail_fast: false

test_suites:
  - name: "api_tests"
    files: ["tests/test_api.py"]
    description: "Тестирование REST API endpoints"
  - name: "reasoning_tests"
    files: ["tests/test_reasoning.py"]
    description: "Тестирование движка рассуждений"

test_data:
  directory: "tests/data/"
  files:
    - "test_context.json"
    - "test_hypotheses.json"

cove
... (файл продолжается)
```


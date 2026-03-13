# Стандарты тестирования для проекта portfolio-system-architect

## Общие принципы

### 1. Единый подход к тестированию
- **Python компоненты**: используйте `pytest` как основной фреймворк
- **PowerShell компоненты**: используйте `Pester` как основной фреймворк
- **Унифицированная структура тестов**: все тесты должны следовать единой структуре

### 2. Структура тестовых директорий
```
components/
├── component-name/
│   ├── src/           # Исходный код
│   ├── tests/         # Тесты компонента
│   │   ├── unit/      # Модульные тесты
│   │   ├── integration/ # Интеграционные тесты
│   │   ├── fixtures/  # Фикстуры и тестовые данные
│   │   └── conftest.py # Конфигурация pytest (для Python)
│   └── ...
```

### 3. Именование тестовых файлов
- Python: `test_<module_name>.py` или `<module_name>_test.py`
- PowerShell: `<ModuleName>.Tests.ps1`
- Тестовые функции/методы: `test_<function_name>` или `Describe "<FunctionName>"`

## Стандарты для Python компонентов

### 1. Использование pytest
```python
# Хорошо
def test_function_returns_correct_value():
    result = function_under_test()
    assert result == expected_value

# Плохо (старый стиль unittest)
class TestFunction(unittest.TestCase):
    def test_function(self):
        self.assertEqual(function_under_test(), expected_value)
```

### 2. Фикстуры pytest
```python
# conftest.py в корне тестовой директории
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}

# Использование в тестах
def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

### 3. Параметризованные тесты
```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double_function(input_value, expected):
    result = double(input_value)
    assert result == expected
```

### 4. Покрытие кода
- Минимальное покрытие: 70% (настраивается в code-quality.yaml)
- Запуск с покрытием: `pytest --cov=components/component-name/src tests/`

## Стандарты для PowerShell компонентов

### 1. Использование Pester
```powershell
# Module.Tests.ps1
Describe "Get-ArchCompass" {
    It "Возвращает корректный путь" {
        $result = Get-ArchCompass -Environment "test"
        $result | Should -Not -BeNullOrEmpty
    }
    
    It "Проверяет существование пути" {
        $result = Get-ArchCompass -Environment "test"
        Test-Path $result | Should -Be $true
    }
}
```

### 2. Мокирование в Pester
```powershell
BeforeAll {
    Mock Get-Content { return "mock content" }
}

It "Использует мок для Get-Content" {
    $result = Get-FileContent "test.txt"
    $result | Should -Be "mock content"
}
```

## Интеграция с CI/CD

### 1. Запуск всех тестов
```bash
# Python тесты
pytest components/ --cov=components/ --cov-report=html

# PowerShell тесты
Get-ChildItem -Path components/ -Filter *.Tests.ps1 -Recurse | ForEach-Object {
    Invoke-Pester $_.FullName
}
```

### 2. GitHub Actions workflow
Тесты автоматически запускаются:
- При каждом push в ветки
- При создании pull request
- По расписанию (ежедневно)

### 3. Отчеты о покрытии
- HTML отчеты генерируются автоматически
- Отчеты сохраняются как артефакты workflow
- Можно просматривать в браузере

## Миграция существующих тестов

### 1. Из unittest в pytest
```python
# Было (unittest)
import unittest

class TestComponent(unittest.TestCase):
    def test_something(self):
        self.assertEqual(func(), expected)

# Стало (pytest)
def test_something():
    assert func() == expected
```

### 2. Обновление импортов
```python
# Вместо
from unittest.mock import patch

# Используйте
import pytest
from unittest.mock import patch  # можно оставить, совместимо с pytest
```

### 3. Перенос тестовых данных
- Переместите тестовые данные в `tests/fixtures/`
- Используйте фикстуры pytest для загруз

## Р по написанию тестов

### 1. Принципы FIRST
- **F**ast: тесты должны выполняться быстро
- **I**ndependent: тесты не должны зависеть друг от друга
- **R**epeatable: тесты должны давать одинаковый результат в любой среде
- **S**elf-validating: тест должен сам определять, пройден он или нет
- **T**imely: тесты должны писаться вовремя (желательно перед кодом)

### 2. Структура теста AAA
- **Arrange**: подготовка данных и окружения
- **Act**: выполнение тестируемого действия
- **Assert**: проверка результата

### 3. Тестирование граничных случаев
- Минимальные и максимальные значения
- Пустые входные данные
- Некорректные входные данные
- Состояния ошибок и исключения

## Полезные команды

### Запуск тестов конкретного компонента
```bash
# Python компонент
pytest components/component-name/tests/ -v

# PowerShell компонент
Invoke-Pester components/component-name/tests/
```

### Запуск с покрытием
```bash
pytest components/component-name/tests/ --cov=components/component-name/src --cov-report=term-missing
```

### Запуск определенных тестов
```bash
# По имени теста
pytest -k "test_function_name"

# По маркеру
pytest -m "integration"
```

### Генерация отчетов
```bash
# HTML отчет
pytest --cov=components/ --cov-report=html

# XML отчет (для CI)
pytest --cov=components/ --cov-report=xml

# Отчет в консоли
pytest --cov=components/ --cov-report=term-missing
```

## Контакты и поддержка

При возникновении вопросов по тестированию:
1. Обратитесь к документации pytest: https://docs.pytest.org/
2. Обратитесь к документации Pester: https://pester.dev/
3. Создайте issue в репозитории с тегом `testing`
4. Свяжитесь с ответственным за качество кода
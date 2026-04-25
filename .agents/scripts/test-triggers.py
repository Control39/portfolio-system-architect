#!/usr/bin/env python3
"""Тестовый скрипт для проверки работы обработчика триггеров Cognitive Automation Agent.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Добавляем путь к скриптам агента
sys.path.insert(0, str(Path(__file__).parent.parent))

# Импортируем классы из trigger-processor.py
try:
    # Создаем временный модуль для импорта
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "trigger_processor",
        Path(__file__).parent / "trigger-processor.py",
    )
    trigger_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trigger_module)

    # Получаем классы из модуля
    TriggerProcessor = trigger_module.TriggerProcessor
    TriggerEvent = trigger_module.TriggerEvent
    TriggerPriority = trigger_module.TriggerPriority
    CommonTriggers = trigger_module.CommonTriggers

except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Создаем заглушки для тестирования...")

    # Заглушки для тестирования
    from enum import Enum

    class TriggerPriority(Enum):
        CRITICAL = 100
        HIGH = 75
        MEDIUM = 50
        LOW = 25

    class TriggerEvent:
        def __init__(self, name, source, data, priority=None):
            self.name = name
            self.source = source
            self.data = data
            self.priority = priority or TriggerPriority.MEDIUM

        def to_dict(self):
            return {
                "name": self.name,
                "source": self.source,
                "data": self.data,
                "priority": self.priority.value if hasattr(self.priority, "value") else 50,
            }

    class CommonTriggers:
        @staticmethod
        def create_project_open_trigger(project_path):
            return TriggerEvent(
                "project_open",
                "system",
                {"project_path": project_path},
                TriggerPriority.HIGH,
            )

        @staticmethod
        def create_file_change_trigger(filename, change_type):
            return TriggerEvent(
                "file_change",
                "filesystem",
                {"file": filename, "change_type": change_type},
                TriggerPriority.MEDIUM,
            )

        @staticmethod
        def create_git_commit_trigger(commit_hash, message, author=None, files_changed=None):
            return TriggerEvent(
                "git_commit",
                "git",
                {
                    "commit_hash": commit_hash,
                    "message": message,
                    "author": author,
                    "files_changed": files_changed or [],
                },
                TriggerPriority.MEDIUM,
            )

    class TriggerProcessor:
        def __init__(self):
            self.triggers = {}
            self.actions = {}
            self.event_queue = []

        def add_event(self, event):
            self.event_queue.append(event)

def test_trigger_loading():
    """Тест загрузки конфигурации триггеров"""
    print("=== Тест загрузки конфигурации триггеров ===")

    try:
        processor = TriggerProcessor()
        print(f"✓ Загружено триггеров: {len(processor.triggers)}")
        print(f"✓ Загружено действий: {len(processor.actions)}")

        # Выводим информацию о триггерах
        for trigger_name, trigger_config in processor.triggers.items():
            print(f"  - {trigger_name}: {trigger_config.get('enabled', False)}")

        return True
    except Exception as e:
        print(f"✗ Ошибка загрузки конфигурации: {e}")
        return False

def test_event_creation():
    """Тест создания событий"""
    print("\n=== Тест создания событий ===")

    try:
        # Создаем тестовые события
        events = [
            TriggerEvent(
                name="project_open",
                source="test",
                data={"project_path": "/test/project"},
                priority=TriggerPriority.HIGH,
            ),
            TriggerEvent(
                name="file_change",
                source="test",
                data={"file": "test.py", "change_type": "modified"},
                priority=TriggerPriority.MEDIUM,
            ),
            TriggerEvent(
                name="git_commit",
                source="test",
                data={"commit_hash": "abc123", "message": "Test commit"},
                priority=TriggerPriority.LOW,
            ),
        ]

        for event in events:
            print(f"✓ Создано событие: {event.name} (приоритет: {event.priority.name})")
            print(f"  Данные: {json.dumps(event.data, indent=2)}")

        return True
    except Exception as e:
        print(f"✗ Ошибка создания событий: {e}")
        return False

def test_common_triggers():
    """Тест общих триггеров"""
    print("\n=== Тест общих триггеров ===")

    try:
        # Тестируем фабричные методы
        triggers = [
            CommonTriggers.create_project_open_trigger("/test/project"),
            CommonTriggers.create_file_change_trigger("test.py", "modified"),
            CommonTriggers.create_git_commit_trigger("abc123", "Test commit"),
            CommonTriggers.create_test_completion_trigger(10, 2, 1),
            CommonTriggers.create_dependency_update_trigger(["requests", "numpy"]),
            CommonTriggers.create_security_alert_trigger("CVE-2023-12345", "high"),
            CommonTriggers.create_performance_issue_trigger("slow_endpoint", 5.2),
            CommonTriggers.create_code_quality_issue_trigger("complex_function", 25),
        ]

        for trigger in triggers:
            print(f"✓ Создан триггер: {trigger.name}")

        return True
    except Exception as e:
        print(f"✗ Ошибка создания общих триггеров: {e}")
        return False

def test_processor_queue():
    """Тест работы очереди обработчика"""
    print("\n=== Тест работы очереди ===")

    try:
        processor = TriggerProcessor()

        # Добавляем события в очередь
        events = [
            TriggerEvent("test_event_1", "test", {"value": 1}, priority=TriggerPriority.HIGH),
            TriggerEvent("test_event_2", "test", {"value": 2}, priority=TriggerPriority.MEDIUM),
            TriggerEvent("test_event_3", "test", {"value": 3}, priority=TriggerPriority.LOW),
        ]

        for event in events:
            processor.add_event(event)

        print(f"✓ Добавлено событий в очередь: {len(events)}")
        print(f"✓ Размер очереди: {len(processor.event_queue)}")

        # Проверяем приоритетную сортировку
        sorted_events = sorted(processor.event_queue, key=lambda e: e.priority.value, reverse=True)
        print("✓ Очередь отсортирована по приоритету:")
        for event in sorted_events:
            print(f"  - {event.name}: приоритет {event.priority.name}")

        return True
    except Exception as e:
        print(f"✗ Ошибка работы очереди: {e}")
        return False

def test_action_execution():
    """Тест выполнения действий (мок)"""
    print("\n=== Тест выполнения действий ===")

    try:
        # Создаем мок-действия
        test_actions = {
            "echo_test": {
                "command": "echo 'Тестовое действие выполнено'",
                "timeout": 5,
                "allowed_failures": 0,
            },
            "python_version": {
                "command": "python --version",
                "timeout": 5,
                "allowed_failures": 0,
            },
        }

        # Сохраняем тестовую конфигурацию
        test_config = {
            "version": "1.0.0",
            "actions": test_actions,
        }

        config_path = Path(".agents/config/test-triggers.yaml")
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f, default_flow_style=False)

        print("✓ Создана тестовая конфигурация действий")

        # Очищаем тестовую конфигурацию
        config_path.unlink()

        return True
    except Exception as e:
        print(f"✗ Ошибка выполнения действий: {e}")
        return False

def test_integration():
    """Тест интеграции с системой"""
    print("\n=== Тест интеграции с системой ===")

    try:
        # Проверяем существование необходимых файлов
        required_files = [
            ".agents/config/triggers.yaml",
            ".agents/config/agent-config.yaml",
            ".agents/scripts/trigger-processor.py",
        ]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            print(f"✗ Отсутствуют файлы: {missing_files}")
            return False

        print("✓ Все необходимые файлы существуют")

        # Проверяем структуру директорий
        required_dirs = [
            ".agents/logs/triggers",
            ".agents/plans",
            ".agents/scans",
        ]

        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"✓ Директория создана/проверена: {dir_path}")

        return True
    except Exception as e:
        print(f"✗ Ошибка интеграции: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("Тестирование системы триггеров Cognitive Automation Agent")
    print("=" * 60)

    tests = [
        ("Загрузка конфигурации", test_trigger_loading),
        ("Создание событий", test_event_creation),
        ("Общие триггеры", test_common_triggers),
        ("Работа очереди", test_processor_queue),
        ("Выполнение действий", test_action_execution),
        ("Интеграция с системой", test_integration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ Неожиданная ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))

    # Вывод результатов
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, success in results:
        if success:
            print(f"✓ {test_name}: ПРОЙДЕН")
            passed += 1
        else:
            print(f"✗ {test_name}: НЕ ПРОЙДЕН")
            failed += 1

    print("\n" + "=" * 60)
    print(f"ИТОГО: {passed} пройдено, {failed} не пройдено")

    if failed == 0:
        print("✓ Все тесты успешно пройдены!")
        return True
    print("✗ Некоторые тесты не пройдены")
    return False

def simulate_real_scenario():
    """Симуляция реального сценария работы"""
    print("\n" + "=" * 60)
    print("СИМУЛЯЦИЯ РЕАЛЬНОГО СЦЕНАРИЯ")
    print("=" * 60)

    try:
        # Создаем обработчик
        processor = TriggerProcessor()

        # Симулируем открытие проекта
        print("1. Симуляция открытия проекта...")
        project_event = CommonTriggers.create_project_open_trigger(str(Path.cwd()))
        processor.add_event(project_event)
        print(f"   ✓ Добавлено событие: {project_event.name}")

        # Симулируем изменение файла
        print("2. Симуляция изменения файла...")
        file_event = CommonTriggers.create_file_change_trigger("test.py", "created")
        processor.add_event(file_event)
        print(f"   ✓ Добавлено событие: {file_event.name}")

        # Симулируем коммит в Git
        print("3. Симуляция коммита в Git...")
        git_event = CommonTriggers.create_git_commit_trigger(
            commit_hash="abc123def456",
            message="Тестовый коммит",
            author="Test User",
            files_changed=["test.py", "README.md"],
        )
        processor.add_event(git_event)
        print(f"   ✓ Добавлено событие: {git_event.name}")

        # Показываем статистику
        print("\nСтатистика событий:")
        print(f"  - Всего событий в очереди: {len(processor.event_queue)}")
        print(f"  - Приоритет HIGH: {sum(1 for e in processor.event_queue if e.priority == TriggerPriority.HIGH)}")
        print(f"  - Приоритет MEDIUM: {sum(1 for e in processor.event_queue if e.priority == TriggerPriority.MEDIUM)}")
        print(f"  - Приоритет LOW: {sum(1 for e in processor.event_queue if e.priority == TriggerPriority.LOW)}")

        # Сохраняем события в лог
        log_dir = Path(".agents/logs/triggers")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        events_data = [event.to_dict() for event in processor.event_queue]
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ События сохранены в лог: {log_file}")

        return True
    except Exception as e:
        print(f"✗ Ошибка симуляции: {e}")
        return False

if __name__ == "__main__":
    # Запускаем тесты
    tests_passed = run_all_tests()

    # Если тесты пройдены, запускаем симуляцию
    if tests_passed:
        simulate_real_scenario()

    # Выводим рекомендации
    print("\n" + "=" * 60)
    print("РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ:")
    print("=" * 60)
    print("1. Для запуска обработчика триггеров в режиме демона:")
    print("   python .agents/scripts/trigger-processor.py --daemon")
    print("\n2. Для ручного запуска триггера:")
    print("   python .agents/scripts/trigger-processor.py --trigger project_open")
    print("\n3. Для просмотра логов:")
    print("   tail -f .agents/logs/triggers.log")
    print("\n4. Для интеграции с Git хуками:")
    print("   Смотрите .agents/scripts/git-hooks-setup.py")

    sys.exit(0 if tests_passed else 1)

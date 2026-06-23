"""
Интеллектуальные guardrails с анализом контекста
"""

import re
from pathlib import Path

import yaml  # 移至模块顶层


class IntelligentGuardrails:
    """
    Умные guardrails, которые понимают контекст
    """

    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.allowed_operations = self._build_allowed_operations()
        # 预编译正则表达式模式
        self._compiled_patterns = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """预编译所有需要的正则表达式模式"""
        # 编译配置中的阻塞模式
        blocked_patterns = self.config.get("blocked_patterns", [])
        self._compiled_patterns["blocked"] = [re.compile(pattern, re.IGNORECASE) for pattern in blocked_patterns]

        # 编译允许的路径模式
        allowed_paths = self.config.get("allowed_paths", [])
        self._compiled_patterns["allowed"] = [re.compile(p, re.IGNORECASE) for p in allowed_paths]

    def _build_allowed_operations(self) -> dict[str, list[str]]:
        """Построить карту разрешённых операций"""
        return {
            # Где можно читать
            "read": ["apps/", "agents/", "config/", "tests/", "docs/"],
            # Где можно писать (БЕЗ подтверждения)
            "write": [
                "apps/",  # Основной код
                "agents/",  # Агенты
                "tests/",  # Тесты
                "docs/",  # Документация
                "examples/",  # Примеры
            ],
            # Что можно изменять (БЕЗ подтверждения)
            "modify": [
                "*.py",  # Python файлы
                "*.js",  # JS файлы
                "*.ts",  # TS файлы
                "*.md",  # Markdown
                "*.txt",  # Текст
            ],
            # Что требует подтверждения
            "requires_approval": [
                "config/*.yaml",  # Конфиги
                "config/*.yml",  # Конфиги
                "*.json",  # JSON данные
                "requirements.txt",  # Зависимости
                "Dockerfile",  # Докер
                "docker-compose.yml",  # Докер компоуз
            ],
            # Что запрещено
            "blocked": [
                ".env",  # Секреты
                ".pem",  # Ключи
                ".key",  # Ключи
                "*.key",  # Ключи
                "*.pem",  # Ключи
                "*.crt",  # Сертификаты
            ],
        }

    def check_action(self, action: str, path: str, context: dict = None) -> tuple[bool, str]:
        """
        Проверить действие на безопасность с учётом контекста

        Args:
            action: Действие (write, modify, delete и т.д.)
            path: Путь к файлу
            context: Контекст (например, "fix_bug", "add_feature", "refactor")

        Returns:
            (разрешено, сообщение)
        """
        # Валидация входных параметров
        if not isinstance(action, str) or not isinstance(path, str):
            return False, "Неверный тип параметров: action и path должны быть строками"

        action_lower = action.lower()
        path_lower = path.lower()

        # 1. Если action = delete — всегда запрещено (без подтверждения)
        if action_lower == "delete":
            return False, "Удаление файлов запрещено без явного подтверждения"

        # 2. Проверяем заблокированные паттерны
        for pattern in self._compiled_patterns.get("blocked", []):
            if pattern.search(path):
                return False, f"Путь заблокирован: {path}"

        # 3. Проверяем разрешённые пути
        if self.config.get("allowed_paths"):
            allowed = any(p.match(path) for p in self._compiled_patterns.get("allowed", []))
            if not allowed:
                return False, f"Путь не в разрешённом списке: {path}"

        # 4. Проверяем действие
        if action_lower in ["read", "scan", "analyze"]:
            return True, "Разрешено (только чтение)"

        # 5. Модифицирующие действия — проверяем контекст
        if action_lower in ["write", "modify", "refactor", "fix", "optimize"]:
            # Если это тесты — всегда разрешено
            if "tests" in path_lower or "test" in path_lower:
                return True, "Разрешено (тесты)"

            # Если это документация — всегда разрешено
            if path.endswith((".md", ".rst", ".txt")):
                return True, "Разрешено (документация)"

            # Если это быстрая правка бага — разрешено
            if context and context.get("type") in ["bugfix", "hotfix", "typo"]:
                return True, "Разрешено (исправление бага)"

            # Если это рефакторинг — разрешено, но логируем
            if context and context.get("type") == "refactor":
                return True, "Разрешено (рефакторинг с аудитом)"

            # Код-ревью — разрешено
            if context and context.get("type") == "codereview":
                return True, "Разрешено (код-ревью)"

            # По умолчанию — разрешено с логированием
            return True, "Разрешено (с аудитом)"

        return False, f"Действие не распознано: {action}"

    def _load_config(self, config_path: Path) -> dict:
        """Загрузить конфигурацию"""
        try:
            if config_path.exists():
                with open(config_path, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}
        except yaml.YAMLError as e:
            print(f"Ошибка при парсинге YAML файла: {e}")
            return {}
        except Exception as e:
            print(f"Неизвестная ошибка при загрузке конфига: {e}")
            return {}
        return {}

    def get_intelligent_decision(self, action: str, path: str, context: dict = None) -> dict:
        """
        Получить интеллектуальное решение с объяснением

        Returns:
            {
                "allowed": True/False,
                "reason": "Объяснение",
                "requires_approval": True/False,
                "priority": "high/medium/low",
                "suggestion": "Предложение"
            }
        """
        allowed, message = self.check_action(action, path, context)

        # Формируем расширенный ответ
        result = {
            "allowed": allowed,
            "reason": message,
            "requires_approval": False,
            "priority": "medium",
            "suggestion": None,
        }

        # Если не разрешено — предлагаем альтернативу
        if not allowed:
            result["suggestion"] = self._suggest_alternative(action, path)
            result["priority"] = "high"

        # Проверяем, нужно ли подтверждение - исправленная логика
        path_lower = path.lower()
        action_lower = action.lower()

        if (
            "config" in path_lower
            and action_lower in ["write", "modify"]
            and (path_lower.endswith((".yaml", ".yml")) or "config/" in path_lower)
        ):
            result["requires_approval"] = True
            result["priority"] = "high"

        if (
            ("requirements" in path_lower and path_lower.endswith(".txt"))
            or "dockerfile" in path_lower
            or "docker-compose.yml" in path_lower
        ):
            result["requires_approval"] = True
            result["priority"] = "high"

        return result

    def _suggest_alternative(self, action: str, path: str) -> str:
        """Предложить альтернативу для заблокированного действия"""
        if "delete" in action.lower():
            return "Предложите переместить файл в папку .trash вместо удаления"

        if ".env" in path:
            return "Используйте .env.example для сохранения структуры без секретов"

        if path.endswith((".pem", ".key")):
            return "Не изменяйте ключи шифрования напрямую. Используйте переменные окружения."

        return "Попробуйте создать новый файл вместо изменения существующего"

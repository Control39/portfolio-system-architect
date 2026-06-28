"""
Модуль для автоматического запуска генерации тестов при изменении кода

Интегрирует TestGenerator с системой мониторинга изменений файлов.
"""

import asyncio
import time
from pathlib import Path
from typing import Any, Callable

import structlog

from agents.cognitive_agent.src.test_generator import TestGenerator

logger = structlog.get_logger(__name__)


class TestGeneratorWatcher:
    """
    Монитор изменений файлов кода для автоматической генерации тестов

    Следит за изменениями в файлами и запускает генерацию тестов при изменениях.
    """

    def __init__(
        self,
        project_path: str,
        prompts_dir: Path,
        llm_client: Any | None = None,
        polling_interval: int = 60,  # 1 минута по умолчанию
        file_patterns: list[str] | None = None,
        on_change_callback: Callable | None = None,
        root_prompts_dir: Path | None = None,
    ):
        """
        Инициализация Watcher

        Args:
            project_path: Путь к проекту
            prompts_dir: Путь к директории с шаблонами
            llm_client: Клиент LLM для генерации
            polling_interval: Интервал проверки изменений (секунды)
            file_patterns: Паттерны файлов для мониторинга
            on_change_callback: Коллбек при изменении (для интеграции с UI)
            root_prompts_dir: Путь к корневой директории с шаблонами (source of truth)
        """
        self.project_path = Path(project_path)
        self.prompts_dir = prompts_dir
        self.root_prompts_dir = root_prompts_dir or Path("prompts")
        self.llm_client = llm_client
        self.polling_interval = polling_interval
        self.file_patterns = file_patterns or ["*.py", "**/*.py"]
        self.on_change_callback = on_change_callback

        # Инициализация TestGenerator с поддержкой корневых шаблонов
        self.test_generator = TestGenerator(
            project_path=str(project_path),
            prompts_dir=prompts_dir,
            llm_client=llm_client,
            root_prompts_dir=self.root_prompts_dir,
        )

        # Кэш хешей файлов
        self.file_hashes: dict[Path, str] = {}
        self.running = False
        self._task = None

        logger.info(f"✅ TestGeneratorWatcher initialized: {project_path}")

    async def _get_file_hash(self, file_path: Path) -> str:
        """Получить хеш файла (для определения изменений)"""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            return str(hash(content))
        except Exception as e:
            logger.warning(f"Ошибка при чтении файла {file_path}: {e}")
            return ""

    async def _find_changed_files(self) -> list[Path]:
        """Найти изменённые файлы"""
        changed_files = []

        for pattern in self.file_patterns:
            for file_path in self.project_path.glob(pattern):
                if not file_path.is_file():
                    continue

                # Пропускать файлы из venv и __pycache__
                if "venv" in str(file_path) or "__pycache__" in str(file_path):
                    continue

                # Пропускать файлы тестов
                if "test_" in file_path.name.lower() or "_test" in file_path.name.lower():
                    continue

                current_hash = await self._get_file_hash(file_path)
                previous_hash = self.file_hashes.get(file_path)

                if current_hash != previous_hash:
                    changed_files.append(file_path)
                    self.file_hashes[file_path] = current_hash

        return changed_files

    async def _on_file_change(self, file_path: Path) -> None:
        """Обработка изменений в файле"""
        logger.info(f"📁 Изменен файл: {file_path}")

        if self.llm_client is None:
            logger.warning("LLM client не configured, skipping test generation")
            return

        try:
            result = await self.test_generator.generate_test_for_file(
                file_path=file_path,
                llm_client=self.llm_client,
            )

            if result["success"]:
                logger.info(f"✅ Генерация тестов завершена: {file_path}")

                # Вызвать коллбек
                if self.on_change_callback:
                    await self.on_change_callback(result)

                # Сохранить результат (можно добавить в файл)
                output_dir = file_path.parent / "generated_tests"
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / f"test_{file_path.stem}.py"

                self.test_generator.apply_generated_tests(
                    test_code=result["output"],
                    output_file=output_file,
                    mode="overwrite",
                )

                logger.info(f"💾 Тесты сохранены: {output_file}")
            else:
                logger.error(f"❌ Генерация тестов не удалась: {file_path}")
                logger.error(f"   Error: {result.get('error', 'Unknown')}")

        except Exception as e:
            logger.error(f"Ошибка при генерации тестов для {file_path}: {e}")

    async def start(self) -> None:
        """Запустить мониторинг"""
        if self.running:
            logger.warning("Watcher already running")
            return

        self.running = True
        logger.info("🚀 Starting TestGeneratorWatcher")

        # Инициализировать хешы всех файлов
        for pattern in self.file_patterns:
            for file_path in self.project_path.glob(pattern):
                if file_path.is_file():
                    hash_value = await self._get_file_hash(file_path)
                    self.file_hashes[file_path] = hash_value

        logger.info(f"📋 Found {len(self.file_hashes)} Python files to monitor")

        # Запустить цикл мониторинга
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> None:
        """Остановить мониторинг"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 TestGeneratorWatcher stopped")

    async def _monitor_loop(self) -> None:
        """Основной цикл мониторинга"""
        while self.running:
            try:
                changed_files = await self._find_changed_files()

                if changed_files:
                    logger.info(f"🔄 Detected {len(changed_files)} file changes")

                    for file_path in changed_files:
                        await self._on_file_change(file_path)

                # Ждать следующей проверки
                await asyncio.sleep(self.polling_interval)

            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(self.polling_interval)

    async def check_once(self) -> list[Path]:
        """Проверить изменения один раз (для ручного запуска)"""
        return await self._find_changed_files()


class TestGeneratorTrigger:
    """
    Триггер для ручного запуска генерации тестов

    Используется для запуска генерации по команде (например, из CLI или UI).
    """

    def __init__(self, test_generator: TestGenerator, llm_client: Any):
        """
        Инициализация Trigger

        Args:
            test_generator: Экземпляр TestGenerator
            llm_client: Клиент LLM
        """
        self.test_generator = test_generator
        self.llm_client = llm_client

    async def trigger_file(self, file_path: str | Path) -> dict[str, Any]:
        """
        Запустить ��енерацию для одного файла

        Args:
            file_path: Путь к файлу

        Returns:
            Результат генерации
        """
        return await self.test_generator.generate_test_for_file(
            file_path=file_path,
            llm_client=self.llm_client,
        )

    async def trigger_directory(self, directory: str | Path) -> list[dict[str, Any]]:
        """
        Запустить генерацию для директории

        Args:
            directory: Путь к директории

        Returns:
            Список результатов генерации
        """
        return await self.test_generator.generate_tests_for_directory(
            directory=directory,
            llm_client=self.llm_client,
        )

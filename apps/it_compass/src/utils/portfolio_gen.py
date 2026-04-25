"""
Генератор портфолио для IT Compass.
Методология "Объективные маркеры компетенций"
© 2025 Ekaterina Kudelya. CC BY-ND 4.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PortfolioGenerator:
    def __init__(
        self,
        markers_dir: str = "src/data/markers",
        progress_file: str = "src/data/user_progress.json",
        output_file: str = "docs/my_portfolio.md",
    ):
        self.markers_dir = Path(markers_dir)
        self.progress_file = Path(progress_file)
        self.output_file = Path(output_file)
        self._markers_cache: Optional[Dict[str, Dict]] = None

    def generate_portfolio(self) -> bool:
        try:
            progress = self._load_progress()
            if not progress:
                return False

            completed_markers = self._load_all_markers()
            completed_markers_list = [
                marker
                for marker_id, marker in completed_markers.items()
                if marker_id in progress.get("completed_markers", [])
            ]

            if not completed_markers_list:
                print("ℹ️ Нет выполненных маркеров.")
                return False

            portfolio_content = self._create_portfolio_content(completed_markers_list)
            return self._save_portfolio(portfolio_content)

        except Exception as e:
            logger.error(f"Ошибка при генерации портфолио: {e}")
            print(f"⚠️ Ошибка генерации: {e}")
            return False

    def _load_progress(self) -> Optional[Dict]:
        if not self.progress_file.exists():
            print("⚠️ Файл прогресса отсутствует.")
            return None

        try:
            with open(self.progress_file, "r", encoding="utf-8") as f:
                progress = json.load(f)

            if not isinstance(progress, dict):
                logger.error("Некорректная структура файла прогресса")
                return None

            return progress
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга файла прогресса: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке прогресса: {e}")
            return None

    def _load_all_markers(self) -> Dict[str, Dict]:
        if self._markers_cache is not None:
            return self._markers_cache

        markers = {}

        if not self.markers_dir.exists():
            logger.warning(f"Директория маркеров не найдена: {self.markers_dir}")
            return markers

        try:
            for json_path in self.markers_dir.glob("*.json"):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        skill_data = json.load(f)

                    skill_name = skill_data.get(
                        "skill_name", json_path.stem.capitalize()
                    )

                    for level_data in skill_data.get("levels", {}).values():
                        for marker in level_data:
                            marker_copy = marker.copy()
                            marker_copy["skill_name"] = skill_name
                            markers[marker["id"]] = marker_copy

                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка парсинга файла {json_path}: {e}")
                except Exception as e:
                    logger.error(f"Неожиданная ошибка при загрузке {json_path}: {e}")

        except Exception as e:
            logger.error(f"Критическая ошибка при загрузке маркеров: {e}")

        self._markers_cache = markers
        return markers

    def _create_portfolio_content(self, completed_markers: List[Dict]) -> List[str]:
        by_skill = self._group_markers_by_skill(completed_markers)

        lines = [
            "# 🎯 Моё IT-портфолио",
            "",
            f"> Сформировано автоматически через [IT Compass](https://github.com/Control39/it-compass) "
            f"({datetime.now().strftime('%d.%m.%Y')})",
            "",
            "> **Методология:** © 2025 Ekaterina Kudelya, [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/)",
            "",
            "## ✅ Подтверждённые навыки",
            "",
        ]

        for skill_name in sorted(by_skill.keys()):
            lines.append(f"### {skill_name}")
            for marker in by_skill[skill_name]:
                lines.append(f"- ✅ **{marker['marker']}**")
                if marker.get("validation"):
                    lines.append(f" > 🔍 Валидация: {marker['validation']}")

                if marker.get("priority") == "high":
                    lines.append(" > ⭐ Высокий приоритет для трудоустройства")

                methodology_author = marker.get(
                    "methodology_author", "Ekaterina Kudelya"
                )
                methodology_license = marker.get("methodology_license", "CC BY-ND 4.0")
                lines.append(
                    f" > 📋 Методология: © {methodology_author}, {methodology_license}"
                )
            lines.append("")

        lines.extend(
            [
                "## 💡 Рекомендации по использованию",
                "",
                "- Прикладывайте скриншоты выполненных проектов",
                "- Указывайте ссылки на GitHub репозитории",
                "- Используйте это портфолио при откликах на вакансии",
                "",
                "> 🚀 **Следующий шаг:** Продолжайте отмечать выполненные маркеры!",
            ]
        )

        return lines

    def _group_markers_by_skill(self, markers: List[Dict]) -> Dict[str, List[Dict]]:
        grouped = {}
        for marker in markers:
            skill = marker.get("skill_name", "Other")
            grouped.setdefault(skill, []).append(marker)
        return grouped

    def _save_portfolio(self, content: List[str]) -> bool:
        try:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            portfolio_text = "\n".join(content)

            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(portfolio_text)

            print(f"✅ Портфолио сохранено: {self.output_file.absolute()}")
            logger.info(f"Портфолио успешно создано: {self.output_file}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении портфолио: {e}")
            print(f"⚠️ Ошибка записи: {e}")
            return False


def generate_portfolio():
    generator = PortfolioGenerator()
    return generator.generate_portfolio()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = generate_portfolio()

    if success:
        print("\n🎉 Портфолио готово! Файл: docs/my_portfolio.md")
    else:
        print("\n❌ Не удалось создать портфолио.")


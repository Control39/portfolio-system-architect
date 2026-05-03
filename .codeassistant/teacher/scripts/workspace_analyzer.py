#!/usr/bin/env python3
"""
Анализатор рабочего пространства для когнитивного архитектора
Анализирует файлы на рабочем столе и предлагает классификацию
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class WorkspaceAnalyzer:
    def __init__(self, desktop_path: str = None):
        if desktop_path is None:
            # Стандартные пути для Windows
            possible_paths = [
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Рабочий стол"),
                "C:/Users/Z/Desktop",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    desktop_path = path
                    break

        self.desktop_path = Path(desktop_path)
        self.analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "total_size_gb": 0,
            "categories": {},
            "recommendations": [],
        }

    def analyze(self) -> Dict:
        """Анализировать рабочее пространство"""
        print(f"Анализируем: {self.desktop_path}")

        categories = self._categorize_files()
        duplicates = self._find_duplicates()
        old_files = self._find_old_files()

        self.analysis.update(
            {
                "categories": categories,
                "duplicates_count": len(duplicates),
                "old_files_count": len(old_files),
                "duplicates": duplicates[:20],  # Ограничим вывод
                "old_files": old_files[:20],
            }
        )

        self._generate_recommendations()
        return self.analysis

    def _categorize_files(self) -> Dict[str, List]:
        """Классифицировать файлы по категориям"""
        categories = {
            "documents": [],
            "images": [],
            "archives": [],
            "executables": [],
            "configs": [],
            "backups": [],
            "temporary": [],
            "projects": [],
            "unknown": [],
        }

        doc_extensions = {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"}
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"}
        archive_extensions = {".zip", ".rar", ".7z", ".tar", ".gz"}
        exec_extensions = {".exe", ".msi", ".bat", ".ps1", ".sh", ".jar"}
        config_extensions = {".json", ".yaml", ".yml", ".ini", ".cfg", ".properties"}

        total_size = 0

        for item in self.desktop_path.iterdir():
            if item.is_file():
                self.analysis["total_files"] += 1
                file_size = item.stat().st_size
                total_size += file_size

                ext = item.suffix.lower()
                file_info = {
                    "name": item.name,
                    "path": str(item),
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                }

                # Классификация
                if ext in doc_extensions:
                    categories["documents"].append(file_info)
                elif ext in image_extensions:
                    categories["images"].append(file_info)
                elif ext in archive_extensions:
                    categories["archives"].append(file_info)
                elif ext in exec_extensions:
                    categories["executables"].append(file_info)
                elif ext in config_extensions:
                    categories["configs"].append(file_info)
                elif "backup" in item.name.lower() or item.name.endswith(".bak"):
                    categories["backups"].append(file_info)
                elif "temp" in item.name.lower() or item.name.startswith("~"):
                    categories["temporary"].append(file_info)
                elif item.is_dir() and any(
                    x in item.name.lower() for x in ["project", "repo", "app"]
                ):
                    categories["projects"].append(file_info)
                else:
                    categories["unknown"].append(file_info)

        self.analysis["total_size_gb"] = round(total_size / (1024**3), 2)

        # Подсчет файлов в каждой категории
        for category, files in categories.items():
            categories[category] = {
                "count": len(files),
                "total_size_mb": round(sum(f["size_mb"] for f in files), 2),
                "files": files[:10],  # Ограничим вывод
            }

        return categories

    def _find_duplicates(self) -> List[Tuple[str, List[str]]]:
        """Найти дубликаты файлов по хешу"""
        hashes = {}
        duplicates = []

        for item in self.desktop_path.iterdir():
            if item.is_file():
                try:
                    file_hash = self._calculate_hash(item)
                    if file_hash in hashes:
                        hashes[file_hash].append(str(item))
                    else:
                        hashes[file_hash] = [str(item)]
                except Exception:
                    continue

        # Фильтруем только дубликаты
        for file_hash, paths in hashes.items():
            if len(paths) > 1:
                duplicates.append((file_hash[:16], paths))

        return duplicates

    def _find_old_files(self, days_old: int = 90) -> List[Dict]:
        """Найти старые файлы"""
        old_files = []
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)

        for item in self.desktop_path.iterdir():
            if item.is_file():
                if item.stat().st_mtime < cutoff_time:
                    old_files.append(
                        {
                            "name": item.name,
                            "path": str(item),
                            "days_old": int(
                                (datetime.now().timestamp() - item.stat().st_mtime) / (24 * 3600)
                            ),
                            "size_mb": round(item.stat().st_size / (1024 * 1024), 2),
                        }
                    )

        return sorted(old_files, key=lambda x: x["days_old"], reverse=True)

    def _calculate_hash(self, filepath: Path, chunk_size: int = 8192) -> str:
        """Рассчитать хеш файла"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _generate_recommendations(self) -> None:
        """Сгенерировать рекомендации по очистке"""
        recs = []

        # Рекомендации по категориям
        cats = self.analysis["categories"]

        if cats["temporary"]["count"] > 0:
            count = cats["temporary"]["count"]
            size = cats["temporary"]["total_size_mb"]
            recs.append(
                {
                    "action": "delete",
                    "category": "temporary",
                    "files": count,
                    "size_mb": size,
                    "reason": "Временные файлы можно безопасно удалить",
                }
            )

        if cats["backups"]["count"] > 5:
            msg = f"Много backup файлов ({cats['backups']['count']}), можно заархивировать"
            recs.append(
                {
                    "action": "archive",
                    "category": "backups",
                    "files": cats["backups"]["count"],
                    "size_mb": cats["backups"]["total_size_mb"],
                    "reason": msg,
                }
            )

        if cats["archives"]["count"] > 10:
            msg = f"Много архивов ({cats['archives']['count']}), переместить в отдельную папку"
            recs.append(
                {
                    "action": "move",
                    "category": "archives",
                    "files": cats["archives"]["count"],
                    "size_mb": cats["archives"]["total_size_mb"],
                    "reason": msg,
                }
            )

        if self.analysis["duplicates_count"] > 0:
            recs.append(
                {
                    "action": "deduplicate",
                    "category": "duplicates",
                    "files": self.analysis["duplicates_count"],
                    "reason": f"Найдено {self.analysis['duplicates_count']} дубликатов",
                }
            )

        if self.analysis["old_files_count"] > 20:
            count = self.analysis["old_files_count"]
            msg = f"Много старых файлов ({count}+), нужна проверка"
            recs.append(
                {
                    "action": "review",
                    "category": "old_files",
                    "files": self.analysis["old_files_count"],
                    "reason": msg,
                }
            )

        # Общие рекомендации
        if self.analysis["total_files"] > 50:
            count = self.analysis["total_files"]
            msg = f"На рабочем столе {count} файлов, нужна организация"
            recs.append(
                {
                    "action": "organize",
                    "category": "general",
                    "reason": msg,
                }
            )

        self.analysis["recommendations"] = recs

    def generate_report(self) -> str:
        """Сгенерировать текстовый отчет"""
        report = []
        report.append("=" * 60)
        report.append("АНАЛИЗ РАБОЧЕГО ПРОСТРАНСТВА")
        report.append("=" * 60)
        report.append(f"Время анализа: {self.analysis['timestamp']}")
        report.append(f"Всего файлов: {self.analysis['total_files']}")
        report.append(f"Общий размер: {self.analysis['total_size_gb']} GB")
        report.append("")

        # Категории
        report.append("КАТЕГОРИИ ФАЙЛОВ:")
        for cat_name, cat_data in self.analysis["categories"].items():
            if cat_data["count"] > 0:
                count = cat_data["count"]
                size = cat_data["total_size_mb"]
                report.append(f"  {cat_name}: {count} файлов ({size} MB)")

        report.append("")

        # Рекомендации
        report.append("РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(self.analysis["recommendations"], 1):
            action = rec["action"].upper()
            reason = rec["reason"]
            report.append(f"{i}. {action} - {reason}")
            if "files" in rec:
                files = rec["files"]
                size = rec.get("size_mb", "N/A")
                report.append(f"   Файлов: {files}, Размер: {size} MB")

        report.append("")

        # План действий
        report.append("ПЛАН ДЕЙСТВИЙ:")
        report.append("1. Удалить временные файлы (.tmp, ~)")
        report.append("2. Переместить архивы в папку Archives/")
        report.append("3. Удалить дубликаты")
        report.append("4. Проверить старые файлы (>90 дней)")
        report.append("5. Организовать по проектам")

        return "\n".join(report)

    def create_organization_plan(self) -> Dict:
        """Создать план организации"""
        plan = {
            "folders_to_create": [
                "Documents",
                "Projects",
                "Archives",
                "Installers",
                "Images",
                "Backups",
                "Temporary",
            ],
            "actions": [],
        }

        # Добавить действия на основе анализа
        for rec in self.analysis["recommendations"]:
            if rec["action"] == "delete":
                plan["actions"].append(
                    {
                        "type": "delete",
                        "target": rec["category"],
                        "description": f"Удалить {rec['files']} временных файлов",
                    }
                )
            elif rec["action"] == "move":
                plan["actions"].append(
                    {
                        "type": "move",
                        "target": rec["category"],
                        "destination": f"Archives/{rec['category']}",
                        "description": f"Переместить {rec['files']} файлов",
                    }
                )

        return plan


def main():
    """Точка входа"""
    analyzer = WorkspaceAnalyzer()
    analysis = analyzer.analyze()

    # Сохранить отчет
    report = analyzer.generate_report()
    print(report)

    # Сохранить в файл
    report_path = Path(".codeassistant/teacher/reports/workspace_analysis.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nОтчет сохранен: {report_path}")

    # Сохранить JSON для дальнейшего использования
    json_path = report_path.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(f"Данные сохранены: {json_path}")


if __name__ == "__main__":
    main()

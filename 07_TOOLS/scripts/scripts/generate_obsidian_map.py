"""
Генерирует Obsidian-карту знаний из структуры репозитория portfolio-system-architect.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Set

# Пути
REPO_ROOT: Path = Path(__file__).parent.parent.resolve()
OUTPUT_DIR: Path = REPO_ROOT / "docs" / "obsidian-map"
README_PATH: Path = REPO_ROOT / "README.md"

# Игнорируемые директории (точное совпадение через set intersection)
IGNORED_DIRS: Set[str] = {
    ".git", "__pycache__", "node_modules", "venv", "env", 
    ".vscode", ".idea", ".gigaide", "backups", ".backup",
    "Lib", ".sourcecraft", ".github", ".vscode-settings", 
    ".vscode-settings-backup", ".continue", ".codeassistant",
    ".gigaide", ".codeassistant", "data/embeddings"
}

# Расширения файлов для включения
INCLUDE_EXTENSIONS: Set[str] = {".md", ".py", ".ps1", ".sh", ".yaml", ".yml", ".json", ".toml"}


def get_all_files(root: Path) -> List[Path]:
    """Получает все файлы в директории рекурсивно, исключая игнорируемые."""
    files: List[Path] = []
    for item in root.rglob("*"):
        if item.is_file():
            # Проверяем через пересечение множеств
            parts_set = set(item.parts)
            if not parts_set.intersection(IGNORED_DIRS):
                if item.suffix.lower() in INCLUDE_EXTENSIONS:
                    files.append(item)
    return files


def generate_note_content(file_path: Path) -> str:
    """Генерирует содержимое заметки для файла."""
    relative_path: Path = file_path.relative_to(REPO_ROOT)
    suffix: str = file_path.suffix.lower()
    
    # Заголовок
    title: str = relative_path.stem.replace("-", " ").replace("_", " ").title()
    
    # Метаданные
    stat = file_path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    
    content: str = f"# {title}\n\n"
    content += f"- **Путь**: `{relative_path}`\n"
    content += f"- **Тип**: {suffix.upper() if suffix else 'Нет'}\n"
    content += f"- **Размер**: {stat.st_size:,} байт\n"
    content += f"- **Последнее изменение**: {mtime}\n\n"
    
    # Добавляем превью содержимого для текстовых файлов
    if suffix in {".md", ".py", ".ps1", ".sh", ".yaml", ".yml", ".json", ".toml"}:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content: str = f.read()
            content += "## Превью\n\n"
            content += "```\n"
            preview: str = file_content[:500]
            content += preview
            if len(file_content) > 500:
                content += "\n... (файл продолжается)"
            content += "\n```\n"
        except Exception as e:
            content += f"## Ошибка\n\nНе удалось прочитать файл: {e}\n"
    
    return content


def sanitize_filename(name: str) -> str:
    """Санитизирует имя файла для Windows."""
    # Заменяем недопустимые символы
    invalid = '<>:"/\\|?*'
    for char in invalid:
        name = name.replace(char, "_")
    # Обрезаем слишком длинные имена
    if len(name) > 200:
        name = name[:200]
    return name


def main() -> None:
    """Основная функция генерации Obsidian-карты."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    files: List[Path] = get_all_files(REPO_ROOT)
    
    for file in files:
        try:
            # Формируем относительный путь
            relative = file.relative_to(REPO_ROOT)
            # Имя заметки: путь без расширения
            note_name = str(relative.with_suffix('')).replace("/", "_").replace("\\", "_")
            note_name = sanitize_filename(note_name)
            note_path: Path = OUTPUT_DIR / f"{note_name}.md"
            
            content: str = generate_note_content(file)
            with open(note_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"[OK] {note_name}.md")
        except Exception as e:
            print(f"[X] Ошибка: {file} - {e}")
    
    # Копируем README в корень
    try:
        if README_PATH.exists():
            with open(README_PATH, "r", encoding="utf-8") as f:
                readme_content: str = f.read()
            
            main_note_path: Path = OUTPUT_DIR / "README.md"
            with open(main_note_path, "w", encoding="utf-8") as f:
                f.write("# Карта\n\n")
                f.write(readme_content)
            
            print("[OK] README.md")
    except Exception as e:
        print(f"[X] Ошибка README: {e}")
    
    print(f"\n[V] Obsidian-карта: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
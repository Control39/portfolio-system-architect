# Исправление #123: нормализация путей для предотвращения дубликатов

"""Генерирует профессиональный сайт-портфолио с поддержкой Mermaid и Git-статуса.
"""

import subprocess
from pathlib import Path

import markdown as md

# Пути
REPO_ROOT: Path = Path(__file__).parent.parent.resolve()
OUTPUT_DIR: Path = REPO_ROOT / "docs" / "website"
LOGO_PATH: str = REPO_ROOT / "assets" / "logo.svg"

# Игнорируемые директории
IGNORED_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    "env",
    ".vscode",
    ".idea",
    "docs/website",
    "Lib",
    "data/embeddings",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{title} — portfolio-system-architect</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    <style>
        :root {{ --primary: #1a73e8; }}
        body {{ background: #f8f9fa; color: #212529; font-family: 'Segoe UI', sans-serif; }}
        .sidebar {{
            background: linear-gradient(to bottom, var(--primary), #0d47a1);
            height: 100vh;
            position: fixed;
            color: white;
        }}
        .sidebar h5, .sidebar a {{ color: white; }}
        .sidebar a:hover {{ background: rgba(255,255,255,0.2); border-radius: 8px; }}
        .content {{ margin-left: 240px; padding: 2rem; }}
        pre {{ background: #f1f3f5; border-radius: 8px; padding: 1rem; overflow: auto; }}
        code {{ background: #e9ecef; padding: 0.2em 0.4em; border-radius: 4px; }}
        h1, h2, h3 {{ color: var(--primary); }}
        .mermaid {{ margin: 2rem 0; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-3 col-lg-2 d-md-block sidebar">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-4">
                        <img src="{logo}" alt="Logo" width="40" class="rounded">
                        <h6 class="mt-2">Portfolio Architect</h6>
                    </div>
                    <hr>
                    <ul class="nav flex-column">
{navigation}
                    </ul>
                </div>
            </nav>
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 content">
                <div class="d-flex justify-content-between flex-wrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1>{title}</h1>
                    <a href="index.html" class="btn btn-outline-primary btn-sm"><i class="bi bi-house"></i> Home</a>
                </div>
                {content}
                <footer class="footer">
                    <p>Сгенерировано автоматически • <code>portfolio-system-architect</code></p>
                </footer>
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


def generate_nav_links(pages_keys: list[str]) -> str:
    """Генерирует навигацию на основе реальных страниц."""
    links = []
    # Всегда добавляем главную
    links.append(
        '                        <li><a class="nav-link" href="index.html">[+] Главная</a></li>'
    )

    # Добавляем страницы, которые существуют
    for key in sorted(set(pages_keys)):
        if key == "index":
            continue
        display = key.replace("-", " ").replace("_", " ").title()
        links.append(
            f'                        <li><a class="nav-link" href="{key}.html">[{key[0].upper()}] {display}</a></li>'
        )

    return "\n".join(links)


def md_to_html(content: str) -> str:
    """Конвертирует Markdown в HTML."""
    try:
        return md.markdown(
            content.replace("]]", "").replace("[[", ""),
            extensions=["fenced_code", "codehilite", "tables"],
        )
    except Exception as e:
        return f"<p>Ошибка парсинга: {e}</p>"


def sanitize_filename(name: str) -> str:
    """Санитизирует имя файла."""
    invalid = '<>:"/\\|?*'
    for char in invalid:
        name = name.replace(char, "_")
    if len(name) > 200:
        name = name[:200]
    return name


def convert() -> None:
    """Основная функция генерации сайта."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logo = str(LOGO_PATH) if LOGO_PATH.exists() else "https://via.placeholder.com/40"

    # Индексная страница
    index_content = """# Добро пожаловать

> Я — **архитектор когнитивных систем**, создаю новые роли в IT.

## Что здесь?

- Структура проекта
- Автоматизированное документирование
- Компоненты системы
"""

    # Git статус
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h %s (%cr)"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            index_content += f"\n- **Последний коммит**: `{result.stdout.strip()}`\n"
    except Exception:
        pass

    pages: dict[str, tuple[str, str]] = {"index": ("Главная", index_content)}

    # Сканируем репозиторий напрямую
    md_files = []
    for ext in ["*.md", "*.py", "*.yaml", "*.yml"]:
        for f in REPO_ROOT.rglob(ext):
            # Проверяем игнорируемые директории
            parts_set = set(f.parts)
            if parts_set.intersection(IGNORED_DIRS):
                continue
            md_files.append(f)

    for md_file in md_files:
        try:
            relative = md_file.relative_to(REPO_ROOT)

            # Нормализация путей: 03_CASES → cases
            normalized_parts = []
            for part in relative.parts:
                if part == "03_CASES":
                    normalized_parts.append("cases")
                else:
                    normalized_parts.append(part)
            relative = Path(*normalized_parts)

            # Имя страницы: путь без расширения
            filename = (
                str(relative.with_suffix("")).replace("/", "_").replace("\\", "_")
            )
            filename = sanitize_filename(filename)

            with open(md_file, encoding="utf-8") as f:
                content = f.read()

            title = filename.replace("-", " ").replace("_", " ").title()
            pages[filename] = (title, content)

        except Exception as e:
            print(f"[!] {md_file.name}: {e}")

    # Генерируем навигацию
    nav = generate_nav_links(list(pages.keys()))

    # Генерируем HTML
    for stem, (title, content_md) in pages.items():
        html_content = md_to_html(content_md)
        html = HTML_TEMPLATE.format(
            title=title,
            navigation=nav,
            content=html_content,
            logo=logo,
        )
        output_path = OUTPUT_DIR / f"{stem}.html"
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            print(f"[X] Запись {stem}: {e}")

    print(f"[V] Сайт: {OUTPUT_DIR / 'index.html'}")


if __name__ == "__main__":
    convert()

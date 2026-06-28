#!/usr/bin/env python3
"""
Analyze documentation in a directory and generate a structured report.

Usage:
    python analyze_docs.py --path ./docs --output report.md
    python analyze_docs.py --path ./docs --verbose
    python analyze_docs.py --path ./docs --find-duplicates
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def get_file_metadata(filepath: Path) -> Dict:
    """Get file metadata (size, dates, lines)."""
    stat = filepath.stat()
    return {
        "path": str(filepath),
        "relative_path": str(filepath),
        "size_kb": round(stat.st_size / 1024, 2),
        "size_bytes": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d"),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
        "lines": len(filepath.read_text(encoding="utf-8", errors="ignore").splitlines()),
    }


def extract_headers(content: str) -> List[str]:
    """Extract all markdown headers (#, ##, ###, ####)."""
    headers = []
    for line in content.split("\n"):
        match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if match:
            headers.append(match.group(2).strip())
    return headers


def has_frontmatter(content: str) -> bool:
    """Check if file has frontmatter (--- at the beginning)."""
    return content.strip().startswith("---")


def count_links(content: str) -> int:
    """Count internal links to other documents."""
    # Markdown links: [text](path) or [text](path#anchor)
    link_pattern = r"\[([^\]]*)\]\(([^)]+)\)"
    links = re.findall(link_pattern, content)

    # Filter for relative links to .md files
    md_links = [link for link in links if ".md" in link[1] or ".md#" in link[1]]
    return len(md_links)


def has_changelog_section(content: str) -> bool:
    """Check if content has a changelog/history section."""
    changelog_patterns = [
        r"^[#]{2,}\s*(История|История\s+изменений|Changelog|History|Changes|Version\s+History)",
        r"^[#]{2,}\s*(Changes\s+\(|Changelog\s+\()",
    ]

    for pattern in changelog_patterns:
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            return True
    return False


def get_git_date(filepath: Path) -> Optional[str]:
    """Get file modification date from git history."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(filepath)],
            capture_output=True,
            text=True,
            cwd=filepath.parent,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


class TopicClassifier:
    """Classify documents into topics based on filename, path, and headers."""

    TOPICS = {
        "architecture": [
            "architecture",
            "arch",
            "design",
            "system",
            "layers",
            "component",
            "module",
            "structure",
            "pattern",
            "decision",
            "adr",
        ],
        "guides": ["guide", "tutorial", "how-to", "getting-started", "setup", "quickstart", "start", "walkthrough"],
        "api": ["api", "endpoint", "rest", "graphql", "websocket", "client", "integration", "sdk"],
        "operations": [
            "deploy",
            "monitoring",
            "logging",
            "ops",
            "troubleshoot",
            "maintenance",
            "admin",
            "configuration",
            "config",
        ],
        "user-guides": ["user", "usage", "configuration", "settings", "workflow", "workflow", "task", "feature"],
        "meta": ["meta", "changelog", "contributing", "style-guide", "template", "readme", "overview", "index"],
        "testing": ["test", "testing", "pytest", "coverage", "qa", "quality"],
        "security": ["security", "secure", "auth", "authentication", "authorization", "permission", "rbac"],
        "examples": ["example", "demo", "sample", "showcase", "scenario"],
        "cases": ["case", "scenario", "use-case", "problem", "solution"],
    }

    @classmethod
    def classify(cls, filepath: Path, headers: List[str]) -> str:
        """Classify document into a topic."""
        all_text = " ".join([str(filepath)] + headers).lower()

        for topic, keywords in cls.TOPICS.items():
            for keyword in keywords:
                if keyword in all_text:
                    return topic

        return "uncategorized"


def find_duplicates(docs: List[Dict]) -> List[Tuple[Dict, Dict, float]]:
    """Find potential duplicate documents based on similarity."""
    duplicates = []
    n = len(docs)

    for i in range(n):
        for j in range(i + 1, n):
            doc1, doc2 = docs[i], docs[j]

            # Calculate similarity score
            score = 0
            reasons = []

            # Similar filename
            if doc1["filename"] == doc2["filename"]:
                score += 40
                reasons.append("same filename")

            # Similar headers
            common_headers = set(doc1["headers"]) & set(doc2["headers"])
            if len(common_headers) > 0:
                score += min(30, len(common_headers) * 10)
                reasons.append(f"common headers: {list(common_headers)[:2]}")

            # Similar topic
            if doc1["topic"] == doc2["topic"]:
                score += 20
                reasons.append("same topic")

            if score >= 50:
                duplicates.append((doc1, doc2, score, reasons))

    # Sort by score descending
    duplicates.sort(key=lambda x: x[2], reverse=True)
    return duplicates


def generate_file_tree(docs: List[Dict], max_depth: int = 4) -> str:
    """Generate a visual file tree structure."""
    tree = "```\ndocs/\n"

    # Group by first-level directory
    first_level = {}
    for doc in docs:
        parts = doc["relative_path"].split("/")
        if len(parts) > 1:
            dir_name = parts[0]
            if dir_name not in first_level:
                first_level[dir_name] = []
            first_level[dir_name].append(doc)

    # Sort directories
    for dir_name in sorted(first_level.keys()):
        docs_in_dir = first_level[dir_name]
        tree += f"├── {dir_name}/\n"

        # Group by second-level directory if exists
        if any(len(d["relative_path"].split("/")) > 2 for d in docs_in_dir):
            second_level = {}
            for doc in docs_in_dir:
                parts = doc["relative_path"].split("/")
                if len(parts) > 2:
                    sub_dir = parts[1]
                    if sub_dir not in second_level:
                        second_level[sub_dir] = []
                    second_level[sub_dir].append(doc)

            for sub_dir in sorted(second_level.keys()):
                tree += f"│   ├── {sub_dir}/\n"
                for doc in sorted(second_level[sub_dir], key=lambda x: x["filename"]):
                    today = " ⭐ СЕГОДНЯ" if doc["modified"] == datetime.now().strftime("%Y-%m-%d") else ""
                    tree += f"│   │   ├── {doc['filename']} ({doc['size_kb']} KB, обновлен {doc['modified']}){today}\n"
        else:
            for doc in sorted(docs_in_dir, key=lambda x: x["filename"]):
                today = " ⭐ СЕГОДНЯ" if doc["modified"] == datetime.now().strftime("%Y-%m-%d") else ""
                tree += f"│   ├── {doc['filename']} ({doc['size_kb']} KB, обновлен {doc['modified']}){today}\n"

    tree += "```"
    return tree


def generate_report(docs: List[Dict], find_duplicates_flag: bool = False, verbose: bool = False) -> str:
    """Generate the analysis report in markdown format."""

    # Calculate statistics
    total_files = len(docs)
    total_size = sum(d["size_bytes"] for d in docs)
    avg_lines = sum(d["lines"] for d in docs) // total_files if total_files > 0 else 0
    oldest = min(d["modified"] for d in docs) if docs else "N/A"
    newest = max(d["modified"] for d in docs) if docs else "N/A"

    # Group by topic
    topic_groups: Dict[str, List[Dict]] = {}
    for doc in docs:
        topic = doc["topic"]
        if topic not in topic_groups:
            topic_groups[topic] = []
        topic_groups[topic].append(doc)

    # Find duplicates
    duplicates = find_duplicates(docs) if find_duplicates_flag else []

    # Build report
    report = []
    report.append("# 📊 Анализ документации")
    report.append(f"\n*Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    report.append("")

    # Statistics
    report.append("## 📈 Статистика")
    report.append(f"- Всего файлов: **{total_files}**")
    report.append(f"- Общий размер: **{total_size / 1024:.2f} KB**")
    report.append(f"- Средняя длина: **{avg_lines}** строк")
    report.append(f"- Самый старый документ: **{oldest}**")
    report.append(f"- Самый новый документ: **{newest}**")
    report.append("")

    # File tree
    report.append("## 📁 Структура")
    report.append(generate_file_tree(docs))
    report.append("")

    # Topic grouping
    report.append("## 🏷️ Группировка по темам")

    topic_names = {
        "uncategorized": "📋 Без категории",
        "architecture": "🏗️ Архитектура",
        "guides": "📖 Руководства",
        "api": "🔌 API",
        "operations": "⚙️ Операции",
        "user-guides": "👤 Руководства пользователя",
        "meta": "📝 Мета-документы",
        "testing": "🧪 Тестирование",
        "security": "🛡️ Безопасность",
        "examples": "💡 Примеры",
        "cases": "📌 Кейсы",
    }

    for topic in sorted(topic_groups.keys()):
        docs_in_topic = topic_groups[topic]
        report.append(f"### {topic_names.get(topic, topic.capitalize())} ({len(docs_in_topic)} файлов)")

        for doc in sorted(docs_in_topic, key=lambda x: x["filename"]):
            headers_preview = ", ".join(doc["headers"][:2]) if doc["headers"] else "без заголовка"
            report.append(f"- `{doc['relative_path']}` - {headers_preview}")

        report.append("")

    # Duplicates
    if find_duplicates_flag and duplicates:
        report.append("## 🔄 Потенциальные дубликаты")
        report.append("")

        for doc1, doc2, score, reasons in duplicates[:10]:  # Top 10
            report.append(f"⚠️ **Сходство: {score}%**")
            report.append(f"1. `{doc1['relative_path']}`")
            report.append(f"2. `{doc2['relative_path']}`")
            report.append(f"   - {', '.join(reasons)}")
            report.append("")

    # Recommendations
    report.append("## 📝 Рекомендации")

    # Find outdated documents
    old_docs = [d for d in docs if d["modified"] < "2024-01-01"]
    if old_docs:
        report.append("### Что обновить (устаревшее)")
        for doc in sorted(old_docs, key=lambda x: x["modified"])[:5]:
            report.append(f"- `{doc['relative_path']}` - не обновлялся с {doc['modified']}")
        report.append("")

    # Find empty/small files
    small_docs = [d for d in docs if d["size_kb"] < 1]
    if small_docs:
        report.append("### Что проверить (маленькие файлы)")
        for doc in sorted(small_docs, key=lambda x: x["size_kb"])[:5]:
            report.append(f"- `{doc['relative_path']}` - {doc['size_kb']} KB")
        report.append("")

    # Summary
    report.append("### Общая сводка")
    report.append(f"- Всего документов: **{total_files}**")
    report.append(f"- Уникальных тем: **{len(topic_groups)}**")
    if find_duplicates_flag:
        report.append(f"- Потенциальных дубликатов: **{len(duplicates)}**")
    report.append("")

    return "\n".join(report)


def analyze_docs(
    docs_path: str, output_path: Optional[str] = None, find_duplicates: bool = False, verbose: bool = False
) -> None:
    """Main function to analyze documentation."""

    docs_dir = Path(docs_path)

    if not docs_dir.exists():
        print(f"❌ Путь не найден: {docs_path}")
        sys.exit(1)

    if not docs_dir.is_dir():
        print(f"❌ Не директория: {docs_path}")
        sys.exit(1)

    print(f"🔍 Анализ документации в: {docs_path}")

    # Collect all markdown files
    md_files = []
    for root, dirs, files in os.walk(docs_dir):
        # Ignore hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".md"):
                filepath = Path(root) / file
                md_files.append(filepath)

    print(f"📝 Найдено {len(md_files)} markdown файлов")

    # Analyze each file
    docs = []
    for filepath in md_files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")

            # Get relative path from docs_dir
            relative_path = str(filepath.relative_to(docs_dir))

            doc = {
                "filepath": filepath,
                "filename": filepath.name,
                "relative_path": relative_path,
                "headers": extract_headers(content),
                "has_frontmatter": has_frontmatter(content),
                "link_count": count_links(content),
                "has_changelog": has_changelog_section(content),
                "topic": TopicClassifier.classify(filepath, extract_headers(content)),
            }

            # Merge with metadata
            metadata = get_file_metadata(filepath)
            doc.update(metadata)

            docs.append(doc)

            if verbose:
                print(f"   ✓ {relative_path} ({doc['size_kb']} KB, {doc['lines']} строк)")

        except Exception as e:
            print(f"   ✗ Ошибка при обработке {filepath}: {e}")

    print(f"✅ Проанализировано {len(docs)} файлов")

    # Find duplicates
    duplicates = find_duplicates(docs) if find_duplicates_flag else []

    # Generate report
    report = generate_report(docs, find_duplicates_flag=find_duplicates_flag, verbose=verbose)

    # Output report
    if output_path:
        output_file = Path(output_path)
        output_file.write_text(report, encoding="utf-8")
        print(f"📄 Отчет сохранен: {output_path}")
    else:
        print("\n" + "=" * 80)
        print("📊 ОТЧЕТ:")
        print("=" * 80)
        print(report)
        print("=" * 80)


def main():
    """Parse arguments and run analysis."""
    parser = argparse.ArgumentParser(description="Analyze documentation and generate a structured report.")
    parser.add_argument("--path", "-p", default="./docs", help="Path to documentation directory (default: ./docs)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (default: print to stdout)")
    parser.add_argument("--find-duplicates", "-d", action="store_true", help="Find potential duplicate documents")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed progress")

    args = parser.parse_args()

    analyze_docs(
        docs_path=args.path, output_path=args.output, find_duplicates=args.find_duplicates, verbose=args.verbose
    )


if __name__ == "__main__":
    main()

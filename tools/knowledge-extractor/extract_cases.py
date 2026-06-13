import json
from datetime import datetime
from pathlib import Path

# === КОНФИГУРАЦИЯ ===
INPUT_FILE = Path("chat-export-1780232041594.json")
OUTPUT_FILE = Path("tools/knowledge-extractor/extracted_cases.md")

# Ключевые слова для поиска кейсов (в нижнем регистре)
KEYWORDS = [
    "кейс",
    "портфолио",
    "star",
    "инфраструктур",
    "shift-left",
    "devsecops",
    "fallback",
    "sanitiz",
    "собеседовани",
    "резюме",
    "cv",
]


def extract_text_from_message(msg: dict) -> str:
    """Извлекает текст из сообщения, учитывая content_list с фазами."""
    # Если есть content_list — склеиваем все фазы
    if "content_list" in msg and msg["content_list"]:
        parts = []
        for item in msg["content_list"]:
            if isinstance(item, dict) and "content" in item:
                parts.append(str(item["content"]))
        return "\n".join(parts)
    # Иначе берём обычное поле content
    return str(msg.get("content", "") or "")


def is_case_related(text: str) -> bool:
    """Проверяет, содержит ли текст ключевые слова."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in KEYWORDS)


def main():
    print(f"📂 Загружаю {INPUT_FILE}...")
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    chats = data.get("data", [])
    print(f"✅ Найдено чатов: {len(chats)}")

    found_cases = []  # Список кортежей (title, role, snippet)

    for chat in chats:
        title = chat.get("title", "Без названия")
        messages_dict = chat.get("chat", {}).get("history", {}).get("messages", {})

        # Итерируемся по значениям словаря (сами сообщения)
        for msg in messages_dict.values():
            if not isinstance(msg, dict):
                continue
            text = extract_text_from_message(msg)
            if is_case_related(text):
                found_cases.append(
                    {
                        "title": title,
                        "role": msg.get("role", "unknown"),
                        "snippet": text[:800],  # первые 800 символов
                        "timestamp": msg.get("timestamp"),
                    }
                )

    # Сохраняем результат
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# 📚 Извлечённые кейсы из диалогов\n\n")
        f.write(f"**Дата выгрузки:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**Найдено релевантных сообщений:** {len(found_cases)}\n\n")
        f.write("---\n\n")

        # Группируем по заголовкам чатов
        by_title = {}
        for case in found_cases:
            by_title.setdefault(case["title"], []).append(case)

        for title, cases in by_title.items():
            f.write(f"## 💬 {title}\n\n")
            for i, case in enumerate(cases, 1):
                role_emoji = "👤" if case["role"] == "user" else "🤖"
                f.write(f"### Фрагмент {i} {role_emoji} ({case['role']})\n\n")
                f.write(f"```\n{case['snippet']}\n```\n\n")
            f.write("---\n\n")

    print(f"✅ Результат сохранён: {OUTPUT_FILE}")
    print(f"📊 Уникальных чатов с кейсами: {len(by_title)}")


if __name__ == "__main__":
    main()

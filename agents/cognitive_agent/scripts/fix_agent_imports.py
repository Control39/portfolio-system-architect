#!/usr/bin/env python3
"""
Применяет все правки к autonomous_agent.py:
- Убирает сломанные импорты
- Добавляет заглушки для AI провайдера
- Правит пути к логам и сканам
"""

import re
from pathlib import Path

AGENT_FILE = Path("C:/repo/agents/cognitive_agent/autonomous_agent.py")
BACKUP_FILE = AGENT_FILE.with_suffix(".py.before_fix")


def apply_fixes():
    print(f"🔧 Fixing {AGENT_FILE}")

    # Создаём бэкап
    if not BACKUP_FILE.exists():
        backup = AGENT_FILE.read_text(encoding="utf-8")
        BACKUP_FILE.write_text(backup, encoding="utf-8")
        print(f"✅ Backup created: {BACKUP_FILE}")

    content = AGENT_FILE.read_text(encoding="utf-8")

    # 1. Заменяем импорты на заглушки
    content = re.sub(
        r"from apps\.ai_config_manager\.src\.ai_config_manager\.config_manager import ConfigManager",
        "# [FIXED] ConfigManager import removed — using yaml directly",
        content,
    )

    content = re.sub(
        r"from apps\.ai_provider_manager\.src\.ai_provider_manager import \([\s\n]*chat_with_fallback,[\s\n]*get_provider_manager,[\s\n]*\)",
        '''# [FIXED] AI Provider Manager not available — using stubs
def chat_with_fallback(messages, **kwargs):
    """Stub for AI provider — returns None"""
    import logging
    logging.getLogger(__name__).warning("AI provider not configured — returning None")
    return None

def get_provider_manager():
    """Stub for AI provider manager"""
    return None''',
        content,
    )

    content = re.sub(
        r"from apps\.it_compass\.src\.it_compass_scanner import get_scanner",
        "# [FIXED] IT Compass scanner not available — disabled",
        content,
    )

    # 2. Добавляем import yaml (если нет)
    if "import yaml" not in content:
        content = content.replace("import yaml", "import yaml  # Added by fix script")
        # Если yaml вообще не импортировался
        if "import yaml" not in content:
            # Найти блок импортов и добавить
            lines = content.split("\n")
            new_lines = []
            inserted = False
            for i, line in enumerate(lines):
                new_lines.append(line)
                if not inserted and line.startswith("import ") and "structlog" in line:
                    new_lines.insert(i + 1, "import yaml")
                    inserted = True
            if not inserted:
                new_lines.insert(10, "import yaml")
            content = "\n".join(new_lines)

    # 3. Заменяем ConfigManager на yaml.load
    content = re.sub(
        r"self\.config = ConfigManager\(str\(config_path\)\) if config_path\.exists\(\) else None",
        'self.config = yaml.safe_load(config_path.read_text(encoding="utf-8")) if config_path.exists() else None',
        content,
    )

    # 4. Заменяем self.ai_manager = get_provider_manager()
    content = re.sub(
        r"self\.ai_manager = get_provider_manager\(\)",
        "self.ai_manager = None  # [FIXED] AI provider disabled",
        content,
    )

    # 5. Заменяем _run_compass_scan
    compass_scan_pattern = r"def _run_compass_scan\(self\):.*?return compass_scanner\.scan_project\(\)"
    compass_replacement = '''def _run_compass_scan(self):
        """IT Compass scan — temporarily disabled"""
        import logging
        logging.getLogger(__name__).info("IT Compass scan disabled — module not found")
        return {"markers_detected": 0, "markers_total": 0, "status": "disabled"}'''

    # Используем re.DOTALL для многострочной замены
    content = re.sub(compass_scan_pattern, compass_replacement, content, flags=re.DOTALL)

    # 6. Правим путь к сохранению сканов
    content = re.sub(
        r'output_dir = self\.project_path / "cognitive_agent" / "scans"',
        'output_dir = self.project_path / "agents" / "cognitive_agent" / "scans"',
        content,
    )

    # 7. Правим путь к логам (уже есть REPO_ROOT / "logs", но проверим)
    # Уже правильно — оставляем как есть

    # Сохраняем
    AGENT_FILE.write_text(content, encoding="utf-8")

    print("✅ Fixes applied successfully!")
    print("\n📝 Изменения:")
    print("   - Убраны импорты из apps/ai_config_manager, apps/ai_provider_manager, apps/it_compass")
    print("   - Добавлены заглушки для AI функций")
    print("   - Путь к сканам исправлен на agents/cognitive_agent/scans")
    print("   - ConfigManager заменён на yaml.safe_load")

    print("\n⚠️ ВАЖНО: После правки агент будет работать в режиме 'только анализ'")
    print("   (AI-вызовы будут возвращать None)")


if __name__ == "__main__":
    apply_fixes()

#!/usr/bin/env python3
"""
Простой тест для проверки аудита документации
"""
import sys
from pathlib import Path

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

def simple_audit_test():
    """Простой тест аудита документации без полной инициализации агента"""
    import re
    from pathlib import Path
    
    print("🔍 Простой тест аудита документации")
    
    # Проверим README файлы на наличие несоответствий
    readme_paths = [
        REPO_ROOT / "agents" / "cognitive_agent" / "README.md",
        REPO_ROOT / "README.md",
    ]
    
    discrepancies = []
    
    for readme_path in readme_paths:
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            # Проверяем упоминания функций как "в разработке" без "уже реализована" рядом
            implemented_features = [
                "интеграция с маркерами IT-Compass",
                "интеграция с Job Automation Agent", 
                "ollama fallback",
                "e2e-тесты",
                "docker compose",
                "анализ качества кода",
                "анализ документации",
                "анализ тестов"
            ]
            
            for feature_keyword in implemented_features:
                # Ищем упоминание функции рядом со статусом "в разработке"
                pattern = rf'({re.escape(feature_keyword)}.*?(?:в разработке|🟡|в работе).*?)(?!\s*\(уже реализована|\s*✅)'
                
                matches = re.finditer(pattern, readme_content, re.IGNORECASE)
                
                for match in matches:
                    match_text = match.group(0)
                    # Проверяем, есть ли "уже реализована" или "✅" в этом же абзаце
                    if "уже реализована" not in match_text.lower() and "✅" not in match_text:
                        discrepancies.append({
                            "feature": feature_keyword,
                            "file": str(readme_path),
                            "context": match_text[:100] + "..."
                        })
    
    print(f"Найдено потенциальных несоответствий: {len(discrepancies)}")
    
    if discrepancies:
        for i, disc in enumerate(discrepancies, 1):
            print(f"  {i}. Функция: {disc['feature']}")
            print(f"     Файл: {disc['file']}")
            print(f"     Контекст: {disc['context']}")
            print()
    else:
        print("✅ Все найденные упоминания соответствуют реальному статусу")
    
    return len(discrepancies)

if __name__ == "__main__":
    simple_audit_test()
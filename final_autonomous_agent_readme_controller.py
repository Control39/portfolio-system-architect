#!/usr/bin/env python3
"""
Финальный скрипт автономного когнитивного агента для управления README файлами
в директории apps. Агент обновляет README для каждого сервиса и создает общий
README для всей директории apps, собирая информацию из README каждого сервиса.
"""
from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent
import sys
from pathlib import Path
import json
import re
from datetime import datetime

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))


def main():
    """Основная функция автономного управления README файлами"""

    print("🚀 Запуск автономного когнитивного агента для управления README файлами...")

    # Создаем агента
    agent = AutonomousCognitiveAgent(project_path=str(REPO_ROOT))

    print("🤖 Агент инициализирован, начинаю сканирование директории apps...")

    # Получаем все сервисы в директории apps
    apps_dir = REPO_ROOT / "apps"
    if not apps_dir.exists():
        print(f"❌ Директория apps не найдена: {apps_dir}")
        return

    # Найти все поддиректории в apps (это и есть наши сервисы)
    service_dirs = [d for d in apps_dir.iterdir() if d.is_dir(
    ) and not d.name.startswith('.') and not d.name.startswith('__')]

    print(f"🔍 Найдено {len(service_dirs)} сервисов для обновления README:")
    for i, service_dir in enumerate(service_dirs, 1):
        print(f"  {i}. {service_dir.name}")

    # Обновляем README для каждого сервиса
    results = process_all_services(agent, service_dirs)

    # Создаем общий README для директории apps
    apps_readme_result = create_apps_directory_readme(agent, service_dirs)

    results["apps_readme"] = apps_readme_result

    # Выводим финальные результаты
    print_final_report(results)

    print("\n✅ Автономный агент завершил управление README файлами")


def process_all_services(agent, service_dirs):
    """Обрабатывает все сервисы, обновляя их README файлы"""
    results = {
        "successful": [],
        "failed": [],
        "total": len(service_dirs)
    }

    for i, service_dir in enumerate(service_dirs, 1):
        print(
            f"\n🔄 [{i}/{len(service_dirs)}] Обработка сервиса: {service_dir.name}")

        # Создаем профиль сервиса
        class ServiceProfile:
            def __init__(self, name, path):
                self.name = name
                self.path = path

        service_profile = ServiceProfile(
            name=service_dir.name,
            path=str(service_dir)
        )

        # Обновляем README для этого сервиса
        result = agent.update_readme_for_service(service_profile)

        if result["status"] == "success":
            results["successful"].append({
                "service": service_profile.name,
                "message": result["message"]
            })
            print(f"  ✅ {service_profile.name}: {result['message']}")
        else:
            results["failed"].append({
                "service": service_profile.name,
                "message": result["message"]
            })
            print(f"  ❌ {service_profile.name}: {result['message']}")

    print(f"\n📊 Результаты обновления README:")
    print(f"  Успешно: {len(results['successful'])}")
    print(f"  Неудачно: {len(results['failed'])}")
    print(f"  Всего: {results['total']}")

    return results


def create_apps_directory_readme(agent, service_dirs):
    """Создает общий README для директории apps, собирая информацию из README каждого сервиса"""
    print(f"\n🔄 Создание общего README для директории apps...")

    apps_dir = Path(agent.project_path) / "apps"

    # Собрать информацию из README каждого сервиса
    services_info = []

    for service_dir in service_dirs:
        readme_path = service_dir / "README.md"

        if readme_path.exists():
            # Попробуем извлечь информацию из README
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Извлечение информации через простой парсинг
                service_info = parse_service_readme(content, service_dir.name)
                services_info.append(service_info)
            except Exception as e:
                print(
                    f"  ⚠️ Не удалось прочитать README для {service_dir.name}: {e}")
                # Если не удалось прочитать существующий README, создаем минимальный
                services_info.append({
                    "name": service_dir.name,
                    "purpose": "Информация недоступна",
                    "framework": "Неизвестно",
                    "language": "Python",
                    "readiness_level": "Неизвестно",
                    "test_coverage": 0,
                    "capabilities": ["Информация из README недоступна"]
                })
        else:
            # Если README не существует, анализируем код
            try:
                class ServiceProfile:
                    def __init__(self, name, path):
                        self.name = name
                        self.path = path

                service_profile = ServiceProfile(
                    name=service_dir.name,
                    path=str(service_dir)
                )

                analysis_report = agent._analyze_service_code(service_profile)

                services_info.append({
                    "name": service_dir.name,
                    "purpose": analysis_report.get('purpose', 'Информация недоступна'),
                    "framework": analysis_report.get('framework', 'Неизвестно'),
                    "language": analysis_report.get('language', 'Python'),
                    "readiness_level": analysis_report.get('readiness_level', 'Неизвестно'),
                    "test_coverage": analysis_report.get('test_coverage', 0),
                    "capabilities": analysis_report.get('capabilities', ["Нет информации"])
                })
            except Exception as e:
                print(
                    f"  ⚠️ Не удалось проанализировать код для {service_dir.name}: {e}")
                services_info.append({
                    "name": service_dir.name,
                    "purpose": "Информация недоступна",
                    "framework": "Неизвестно",
                    "language": "Python",
                    "readiness_level": "Неизвестно",
                    "test_coverage": 0,
                    "capabilities": ["Не удалось проанализировать код"]
                })

    # Сортировка сервисов по имени для согласованности
    services_info.sort(key=lambda x: x["name"])

    # Генерация общего README
    template_str = """# 🗂️ Директория приложений (apps)

Этот каталог содержит набор микросервисов, каждый из которых реализует отдельную бизнес-функцию. Все сервисы объединены общей архитектурой и могут работать как независимо, так и в составе единой системы.

**Дата генерации:** {{ timestamp }}

## 📋 Список сервисов

{% for service in services %}
### [{{ service.name }}](./{{ service.name }}/README.md)

**Назначение:** {{ service.purpose }}

**Технологии:** {{ service.framework }}, {{ service.language }}

**Статус готовности:** {{ service.readiness_level }}

**Покрытие тестами:** {{ service.test_coverage }}%

**Ключевые возможности:**
{% for capability in service.capabilities[:3] %}
*   {{ capability }}
{% endfor %}

[Подробнее](./{{ service.name }}/README.md)

---

{% endfor %}

## 🔄 Архитектурные принципы

*   **Микросервисная архитектура** - каждый сервис решает одну конкретную задачу
*   **Независимое масштабирование** - каждый сервис может масштабироваться отдельно
*   **Единые точки интеграции** - стандартные интерфейсы взаимодействия между сервисами
*   **Автоматическая документация** - README файлы генерируются автоматически на основе анализа кода

> *Этот файл автоматически генерируется автономным когнитивным агентом на основе анализа исходного кода всех сервисов в директории. Ручные изменения будут перезаписаны.*
"""

    # Подготовка контекста для шаблона
    context = {
        "services": services_info,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Рендеринг шаблона
    import jinja2
    template = jinja2.Template(template_str)
    apps_readme_content = template.render(context)

    # Путь к общему README
    apps_readme_path = apps_dir / "README.md"

    # Проверка guardrails перед записью
    relative_path = agent._make_relative_path(apps_readme_path)
    access_granted, access_msg = agent._check_file_access(
        str(relative_path), "write")
    if not access_granted:
        print(
            f"  ❌ Доступ к записи общего файла README для apps запрещен: {access_msg}")
        return {"status": "error", "message": access_msg}

    # Запись файла
    try:
        with open(apps_readme_path, 'w', encoding='utf-8') as f:
            f.write(apps_readme_content)

        agent.audit_logger.log_action(
            "apps_readme_updated",
            {"path": str(apps_readme_path),
             "services_count": len(services_info)},
            status="success"
        )
        print(
            f"  ✅ Общий README для директории apps успешно создан. Сервисов: {len(services_info)}")

        return {
            "status": "success",
            "message": f"Общий README для apps создан, включает {len(services_info)} сервисов",
            "services_count": len(services_info)
        }
    except Exception as e:
        print(f"  ❌ Ошибка при записи общего README для apps: {e}")
        agent.audit_logger.log_action("apps_readme_update_failed", {
                                      "error": str(e)}, status="failed")
        return {"status": "error", "message": str(e)}


def parse_service_readme(content, service_name):
    """
    Простой парсер для извлечения информации из README сервиса
    """
    # Извлечение назначения сервиса
    purpose_match = re.search(
        r'(?:##\s*🎯\s*Назначение сервиса|##\s*Назначение сервиса)[\s\S]*?\n(.+?)(?=\n##|$)', content)
    purpose = purpose_match.group(1).strip(
    ) if purpose_match else "Назначение не указано"

    # Извлечение фреймворка
    framework_match = re.search(r'Фреймворк:[\s*]\s*(.+?)(?:\n|\*)', content)
    framework = framework_match.group(
        1).strip() if framework_match else "Не указан"

    # Извлечение языка
    language_match = re.search(r'Язык:[\s*]\s*(.+?)(?:\n|\*)', content)
    language = language_match.group(1).strip() if language_match else "Python"

    # Извлечение уровня готовности
    readiness_match = re.search(
        r'Уровень готовности:[\s*]\s*(.+?)(?:\n|\*)', content)
    readiness_level = readiness_match.group(
        1).strip() if readiness_match else "Неизвестно"

    # Извлечение покрытия тестами
    coverage_match = re.search(r'Покрытие тестами:[\s*]\s*(\d+)%', content)
    test_coverage = int(coverage_match.group(1)) if coverage_match else 0

    # Извлечение возможностей
    capabilities = []
    capabilities_section = re.search(
        r'(?:##\s*🚀\s*Ключевые возможности|##\s*Ключевые возможности)[\s\S]*?\n((?:\*[^\n]*\n?)*)', content)
    if capabilities_section:
        cap_lines = capabilities_section.group(1).split('\n')
        for line in cap_lines:
            line = line.strip()
            if line.startswith('*') and len(line) > 2:
                cap = line[1:].strip().strip('-').strip()
                if cap:
                    capabilities.append(cap)

    # Если не удалось извлечь возможности, используем заглушку
    if not capabilities:
        capabilities = ["Информация недоступна в README"]

    return {
        "name": service_name,
        "purpose": purpose,
        "framework": framework,
        "language": language,
        "readiness_level": readiness_level,
        "test_coverage": test_coverage,
        "capabilities": capabilities
    }


def print_final_report(results):
    """Выводит финальный отчет о выполненной работе"""
    print(f"\n🎯 ФИНАЛЬНЫЙ ОТЧЕТ:")
    print(f"  Всего сервисов обработано: {results['total']}")
    print(f"  Успешно обновлено: {len(results['successful'])}")
    print(f"  Ошибок: {len(results['failed'])}")

    if results['apps_readme']['status'] == 'success':
        print(f"  Общий README для apps: ✅ Успешно создан")
    else:
        print(
            f"  Общий README для apps: ❌ Ошибка - {results['apps_readme']['message']}")

    if results['failed']:
        print(f"\n❌ ПОДРОБНОСТИ ОШИБОК:")
        for failure in results['failed']:
            print(f"  - {failure['service']}: {failure['message']}")

    print(f"\n📈 ДЕТАЛИ УСПЕШНЫХ ОПЕРАЦИЙ:")
    for success in results['successful']:
        print(f"  - {success['service']}: {success['message']}")

    # Общая статистика
    success_rate = len(results['successful']) / \
        results['total'] * 100 if results['total'] > 0 else 0
    print(
        f"\n📊 Эффективность: {success_rate:.1f}% ({len(results['successful'])}/{results['total']})")


if __name__ == "__main__":
    main()

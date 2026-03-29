#!/usr/bin/env python3
"""
Скрипт для мониторинга актуальности бейджей в проекте.
Проверяет, что бейджи отражают реальное состояние проекта.
"""

import re
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import sys

def check_static_badges(readme_content: str) -> dict:
    """Проверить статические бейджи на актуальность."""
    issues = []
    
    # Проверка Python версии
    python_match = re.search(r'Python-(\d+\.\d+(?:\.\d+)?)', readme_content)
    if python_match:
        python_version = python_match.group(1)
        # Можно добавить проверку актуальности версии
        issues.append(f"Python version badge: {python_version}")
    
    # Проверка coverage бейджа
    coverage_match = re.search(r'Coverage-(\d+(?:\.\d+)?)%25', readme_content)
    if coverage_match:
        coverage_value = float(coverage_match.group(1))
        if coverage_value < 80:
            issues.append(f"Coverage is low: {coverage_value}% (target: 80%+)")
    
    # Проверка security бейджей
    security_badges = re.findall(r'Security-[^"]+', readme_content)
    if not security_badges:
        issues.append("Missing security badges")
    else:
        issues.append(f"Security badges found: {len(security_badges)}")
    
    return {
        "static_badges_checked": True,
        "issues": issues,
        "python_version": python_match.group(1) if python_match else "unknown",
        "coverage_value": coverage_match.group(1) if coverage_match else "unknown"
    }

def check_dynamic_badges(readme_content: str) -> dict:
    """Проверить динамические бейджи (ссылки)."""
    issues = []
    working_badges = 0
    broken_badges = 0
    
    # Найти все URL бейджей
    badge_urls = re.findall(r'https://[^"\s]+badge[^"\s]+', readme_content)
    
    for url in badge_urls[:5]:  # Проверяем только первые 5 чтобы не перегружать
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                working_badges += 1
            else:
                broken_badges += 1
                issues.append(f"Broken badge: {url} (HTTP {response.status_code})")
        except Exception as e:
            broken_badges += 1
            issues.append(f"Error checking badge {url}: {e}")
    
    return {
        "dynamic_badges_checked": True,
        "total_badges_found": len(badge_urls),
        "working_badges": working_badges,
        "broken_badges": broken_badges,
        "issues": issues
    }

def check_badge_freshness() -> dict:
    """Проверить свежесть бейджей (когда обновлялись последний раз)."""
    issues = []
    
    # Проверить файл с метриками
    metrics_file = Path("badges/metrics.json")
    if metrics_file.exists():
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            
            updated_at = datetime.fromisoformat(metrics.get('updated_at', '2000-01-01'))
            days_old = (datetime.now() - updated_at).days
            
            if days_old > 7:
                issues.append(f"Badges are {days_old} days old (should update weekly)")
            else:
                issues.append(f"Badges are fresh: {days_old} days old")
                
            return {
                "freshness_checked": True,
                "last_updated": metrics.get('updated_at'),
                "days_old": days_old,
                "coverage": metrics.get('coverage'),
                "issues": issues
            }
        except Exception as e:
            issues.append(f"Error reading metrics: {e}")
    
    return {
        "freshness_checked": False,
        "issues": ["No metrics file found"]
    }

def generate_health_report() -> dict:
    """Сгенерировать полный отчет о здоровье бейджей."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        return {"error": "README.md not found"}
    
    readme_content = readme_path.read_text(encoding='utf-8')
    
    static_report = check_static_badges(readme_content)
    dynamic_report = check_dynamic_badges(readme_content)
    freshness_report = check_badge_freshness()
    
    # Общая оценка здоровья
    total_issues = (
        len(static_report.get('issues', [])) +
        len(dynamic_report.get('issues', [])) +
        len(freshness_report.get('issues', []))
    )
    
    health_score = 100 - min(total_issues * 10, 100)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "health_score": health_score,
        "summary": {
            "static_badges": static_report,
            "dynamic_badges": dynamic_report,
            "freshness": freshness_report
        },
        "recommendations": generate_recommendations(
            static_report, dynamic_report, freshness_report
        )
    }

def generate_recommendations(static: dict, dynamic: dict, freshness: dict) -> list:
    """Сгенерировать рекомендации по улучшению бейджей."""
    recommendations = []
    
    # Рекомендации по статическим бейджам
    if static.get('coverage_value', 'unknown') != 'unknown':
        coverage = float(static['coverage_value'])
        if coverage < 80:
            recommendations.append(f"Увеличить покрытие тестами с {coverage}% до 80%+")
    
    # Рекомендации по динамическим бейджам
    if dynamic.get('broken_badges', 0) > 0:
        recommendations.append(f"Исправить {dynamic['broken_badges']} сломанных бейджей")
    
    # Рекомендации по свежести
    if freshness.get('days_old', 0) > 7:
        recommendations.append("Обновить бейджи (прошло больше недели)")
    
    # Общие рекомендации
    if not recommendations:
        recommendations.append("Бейджи в хорошем состоянии. Продолжайте поддерживать актуальность.")
    
    return recommendations

def main():
    """Основная функция."""
    print("Checking badge health...")
    print("=" * 60)
    
    report = generate_health_report()
    
    if 'error' in report:
        print(f"Error: {report['error']}")
        sys.exit(1)
    
    # Вывод отчета
    print(f"Health Score: {report['health_score']}/100")
    print(f"Timestamp: {report['timestamp']}")
    print()
    
    # Статические бейджи
    static = report['summary']['static_badges']
    print("Static Badges:")
    print(f"  Python: {static.get('python_version', 'unknown')}")
    print(f"  Coverage: {static.get('coverage_value', 'unknown')}%")
    if static.get('issues'):
        for issue in static['issues']:
            print(f"  ⚠️  {issue}")
    
    # Динамические бейджи
    dynamic = report['summary']['dynamic_badges']
    print(f"\nDynamic Badges: {dynamic.get('working_badges', 0)} working, "
          f"{dynamic.get('broken_badges', 0)} broken")
    if dynamic.get('issues'):
        for issue in dynamic['issues'][:3]:  # Показываем только первые 3
            print(f"  ⚠️  {issue}")
    
    # Свежесть
    freshness = report['summary']['freshness']
    if freshness.get('days_old') is not None:
        print(f"\nFreshness: {freshness['days_old']} days old")
    
    # Рекомендации
    print(f"\nRecommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print("=" * 60)
    
    # Сохраняем отчет
    report_path = Path("badges/health-report.json")
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Report saved to {report_path}")
    
    # Возвращаем код выхода в зависимости от здоровья
    if report['health_score'] < 70:
        print("Warning: Badge health is poor")
        sys.exit(1)
    elif report['health_score'] < 90:
        print("Warning: Badge health needs improvement")
        sys.exit(0)
    else:
        print("Success: Badge health is good")
        sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Анализ текущих бейджей в проекте
"""

import re
import json
from collections import defaultdict

def analyze_badges(readme_content):
    """Проанализировать бейджи в README"""
    
    # Ищем все img src
    img_pattern = r'<img\s+src="([^"]+)"\s+alt="([^"]*)"'
    matches = re.findall(img_pattern, readme_content)
    
    categories = defaultdict(list)
    shield_io_count = 0
    native_count = 0
    other_count = 0
    
    for url, alt in matches:
        badge_info = {
            'url': url,
            'alt': alt,
            'type': 'unknown'
        }
        
        # Определяем тип бейджа
        if 'img.shields.io' in url:
            badge_info['type'] = 'shields.io'
            shield_io_count += 1
            
            # Анализируем shields.io бейдж
            if 'badge/' in url:
                badge_info['subtype'] = 'static'
            elif 'github/actions' in url:
                badge_info['subtype'] = 'github-actions'
            elif 'github/last-commit' in url:
                badge_info['subtype'] = 'last-commit'
            elif 'github/stars' in url:
                badge_info['subtype'] = 'stars'
            elif 'github/forks' in url:
                badge_info['subtype'] = 'forks'
            elif 'docker/pulls' in url:
                badge_info['subtype'] = 'docker-pulls'
            else:
                badge_info['subtype'] = 'other-shields'
                
        elif 'github.com' in url and 'badge.svg' in url:
            badge_info['type'] = 'github-native'
            native_count += 1
        elif 'codecov.io' in url:
            badge_info['type'] = 'codecov'
            other_count += 1
        elif 'snyk.io' in url:
            badge_info['type'] = 'snyk'
            other_count += 1
        else:
            badge_info['type'] = 'other'
            other_count += 1
        
        # Определяем категорию по alt тексту
        alt_lower = alt.lower()
        if 'ci' in alt_lower or 'test' in alt_lower:
            categories['ci'].append(badge_info)
        elif 'coverage' in alt_lower:
            categories['coverage'].append(badge_info)
        elif 'security' in alt_lower or 'trivy' in alt_lower or 'bandit' in alt_lower or 'snyk' in alt_lower:
            categories['security'].append(badge_info)
        elif 'license' in alt_lower:
            categories['license'].append(badge_info)
        elif 'python' in alt_lower:
            categories['language'].append(badge_info)
        elif 'docker' in alt_lower or 'kubernetes' in alt_lower or 'prometheus' in alt_lower:
            categories['tech-stack'].append(badge_info)
        elif 'production' in alt_lower or 'gitops' in alt_lower or 'observability' in alt_lower:
            categories['architecture'].append(badge_info)
        else:
            categories['other'].append(badge_info)
    
    return {
        'total': len(matches),
        'by_type': {
            'shields.io': shield_io_count,
            'github-native': native_count,
            'other': other_count
        },
        'categories': dict(categories),
        'badges': matches
    }

def main():
    # Читаем README.md
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = analyze_badges(content)
    
    print("=" * 80)
    print("АНАЛИЗ БЕЙДЖЕЙ В README.md")
    print("=" * 80)
    
    print(f"\n📊 Всего бейджей: {analysis['total']}")
    print(f"\n📈 Распределение по типам:")
    for type_name, count in analysis['by_type'].items():
        if analysis['total'] > 0:
            percentage = (count / analysis['total']) * 100
            print(f"  • {type_name}: {count} ({percentage:.1f}%)")
        else:
            print(f"  • {type_name}: {count} (0%)")
    
    print(f"\n🏷️  Распределение по категориям:")
    for category, badges in analysis['categories'].items():
        print(f"  • {category}: {len(badges)} бейджей")
    
    print(f"\n🔍 Рекомендации по анализу:")
    
    # Проверяем shields.io использование
    if analysis['total'] > 0:
        shield_percentage = (analysis['by_type']['shields.io'] / analysis['total']) * 100
        if shield_percentage < 90:
            print(f"  ⚠️  Только {shield_percentage:.1f}% бейджей используют shields.io")
            print("     Рекомендация: Перевести все бейджи на shields.io для надежности")
        else:
            print(f"  ✅ {shield_percentage:.1f}% бейджей используют shields.io - отлично!")
    else:
        shield_percentage = 0
        print("  ⚠️  No badges found in README.md")
    
    # Проверяем наличие динамических бейджей
    dynamic_count = 0
    for category, badges in analysis['categories'].items():
        for badge in badges:
            if badge['type'] == 'shields.io' and badge.get('subtype') in ['github-actions', 'last-commit', 'stars', 'forks', 'docker-pulls']:
                dynamic_count += 1
    
    if analysis['total'] > 0:
        dynamic_percentage = (dynamic_count / analysis['total']) * 100
        print(f"\n  🔄 Динамических бейджей: {dynamic_count} ({dynamic_percentage:.1f}%)")
        
        if dynamic_percentage < 40:
            print("     Рекомендация: Увеличить количество динамических бейджей")
        else:
            print("     ✅ Хороший уровень динамических бейджей")
    else:
        dynamic_percentage = 0
        print(f"\n  🔄 Динамических бейджей: {dynamic_count} (0%)")
        print("     ⚠️  No badges found in README.md")
    
    # Проверяем ссылки на детальные отчеты
    print(f"\n  🔗 Проверьте, что бейджи ведут на детальные отчеты:")
    print("     • CI бейдж → GitHub Actions workflow")
    print("     • Coverage бейдж → Codecov отчет")
    print("     • Security бейдж → отчеты сканирования")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
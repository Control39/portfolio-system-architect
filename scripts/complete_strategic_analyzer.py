#!/usr/bin/env python3
"""
Полный стратегический анализатор экосистемы.
Объединяет метрики проекта, анализ сервисов и веб-поиск.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


class CompleteStrategicAnalyzer:
    def __init__(self, repo_path: str, metrics_file: str | None = None):
        self.repo_path = Path(repo_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project_metrics": {},
            "services": [],
            "web_research": {},
            "uniqueness_analysis": {},
            "market_analysis": {},
            "recommendations": [],
            "summary": {},
        }
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

        # Загружаем метрики
        if metrics_file:
            self._load_metrics(metrics_file)
        else:
            # Используем значения по умолчанию (из твоего файла)
            self._load_default_metrics()

        print("🧠 Инициализация полного стратегического анализатора...")

    def _load_metrics(self, metrics_file: str):
        """Загрузка метрик из файла"""
        try:
            with open(metrics_file, encoding="utf-8") as f:
                content = f.read()

            # Парсим ключ-значение
            metrics = {}
            for line in content.split("\n"):
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Пробуем преобразовать в число
                    try:
                        if "." in value:
                            value = float(value)
                        elif value.isdigit():
                            value = int(value)
                    except:
                        pass

                    metrics[key] = value

            self.results["project_metrics"] = metrics
            print(f"✅ Загружено {len(metrics)} метрик")

        except Exception as e:
            print(f"⚠️ Ошибка загрузки метрик: {e}")
            self._load_default_metrics()

    def _load_default_metrics(self):
        """Загрузка метрик по умолчанию (из твоего файла)"""
        self.results["project_metrics"] = {
            "Размер команды": 5,
            "Бюджет ($)": 100000,
            "Срок реализации (месяцы)": 12,
            "Технологический стек": "python, react, docker, kubernetes",
            "Рыночный спрос (0-1)": 0.7,
            "Уровень инноваций (0-1)": 0.6,
            "Масштабируемость (0-1)": 0.7,
            "Уровень конкуренции (0-1)": 0.5,
            "Фактор риска (0-1)": 0.3,
            "Экспертиза команды (0-1)": 0.7,
            "Тип проекта": "Стартап",
            "Зависимости": "django, requests, numpy",
            "Целевая аудитория (кол-во)": 10000,
            "Потенциал выручки ($)": 500000,
        }
        print("✅ Загружены метрики по умолчанию")

    def analyze(self) -> dict[str, Any]:
        """Запуск полного анализа"""
        print("\n" + "=" * 70)
        print("🧠  ПОЛНЫЙ СТРАТЕГИЧЕСКИЙ АНАЛИЗ ЭКОСИСТЕМЫ")
        print("=" * 70)

        # 1. Анализ метрик проекта
        self._analyze_metrics()

        # 2. Анализ сервисов
        self._analyze_services()

        # 3. Веб-исследование
        self._research_web()

        # 4. Оценка уникальности
        self._assess_uniqueness()

        # 5. Рыночный анализ
        self._analyze_market()

        # 6. Генерация рекомендаций
        self._generate_recommendations()

        # 7. Создание сводки
        self._create_summary()

        # 8. Сохранение отчёта
        self._save_report()

        print("\n✅ Полный стратегический анализ завершён!")
        return self.results

    def _analyze_metrics(self):
        """Анализ метрик проекта"""
        print("\n📊 Анализ метрик проекта...")

        metrics = self.results["project_metrics"]

        # Оценка жизнеспособности
        viability_score = 0

        # Команда и бюджет
        if metrics.get("Размер команды", 0) >= 3:
            viability_score += 1
        if metrics.get("Бюджет ($)", 0) >= 50000:
            viability_score += 1

        # Рыночный спрос
        if metrics.get("Рыночный спрос (0-1)", 0) >= 0.5:
            viability_score += 1

        # Инновации
        if metrics.get("Уровень инноваций (0-1)", 0) >= 0.5:
            viability_score += 1

        # Экспертиза
        if metrics.get("Экспертиза команды (0-1)", 0) >= 0.5:
            viability_score += 1

        # Риск
        if metrics.get("Фактор риска (0-1)", 0) <= 0.5:
            viability_score += 1

        # Конкуренция
        if metrics.get("Уровень конкуренции (0-1)", 0) <= 0.6:
            viability_score += 1

        # ROI
        budget = metrics.get("Бюджет ($)", 100000)
        revenue = metrics.get("Потенциал выручки ($)", 500000)
        roi = (revenue - budget) / budget if budget > 0 else 0

        viability = {
            "score": viability_score,
            "max_score": 7,
            "percentage": (viability_score / 7) * 100,
            "level": "Высокая" if viability_score >= 5 else "Средняя" if viability_score >= 3 else "Низкая",
            "roi": roi,
            "roi_percentage": roi * 100,
        }

        self.results["project_metrics_analysis"] = viability

        print(f"  • Жизнеспособность: {viability['percentage']:.0f}% ({viability['level']})")
        print(f"  • ROI: {viability['roi_percentage']:.0f}%")
        print(f"  • Команда: {metrics.get('Размер команды', 0)} чел.")
        print(f"  • Бюджет: ${metrics.get('Бюджет ($)', 0):,}")

    def _analyze_services(self):
        """Анализ сервисов из репозитория"""
        print("\n📁 Анализ сервисов...")

        # Анализируем как apps/, так и agents/ директории
        service_dirs = []

        apps_dir = self.repo_path / "apps"
        if apps_dir.exists():
            service_dirs.extend([d for d in apps_dir.iterdir() if d.is_dir()])

        agents_dir = self.repo_path / "agents"
        if agents_dir.exists():
            service_dirs.extend([d for d in agents_dir.iterdir() if d.is_dir()])

        for service_dir in service_dirs:
            readme_path = service_dir / "README.md"
            if not readme_path.exists():
                continue

            content = readme_path.read_text(encoding="utf-8", errors="ignore")

            service_info = {
                "name": service_dir.name,
                "path": str(service_dir.relative_to(self.repo_path)),
                "purpose": self._extract_purpose(content),
                "features": self._extract_features(content),
                "status": self._extract_status(content),
                "unique_score": self._assess_unique(content),
                "market_score": self._assess_market(content),
                "python_files": self._count_python_files(service_dir),
                "has_src": self._has_src_directory(service_dir),
                "has_tests": self._has_tests_directory(service_dir),
            }

            self.results["services"].append(service_info)

            status_icon = self._get_status_icon(service_info["status"])
            print(
                f"  • {service_info['path']}: {status_icon} {service_info['status']}, Уникальность={service_info['unique_score']}/10, Python файлов: {service_info['python_files']}"
            )

    def _count_python_files(self, service_dir: Path) -> int:
        """Подсчет Python файлов в сервисе"""
        python_files = list(service_dir.rglob("*.py"))
        return len(python_files)

    def _has_src_directory(self, service_dir: Path) -> bool:
        """Проверка наличия src директории"""
        return (service_dir / "src").exists()

    def _has_tests_directory(self, service_dir: Path) -> bool:
        """Проверка наличия tests директории"""
        return (service_dir / "tests").exists()

    def _get_status_icon(self, status: str) -> str:
        """Возвращает иконку для статуса"""
        icons = {"Production Ready": "🟢", "MVP": "🟡", "WIP": "🔴", "Active": "🔵"}
        return icons.get(status, "⚪")

    def _extract_purpose(self, content: str) -> str:
        """Извлечение назначения"""
        patterns = [
            r"## 🎯 Назначение\s*\n(.*?)(?=\n##|\Z)",
            r"## Purpose\s*\n(.*?)(?=\n##|\Z)",
            r"## Описание\s*\n(.*?)(?=\n##|\Z)",
            r"#.*?(?:назначение|purpose|описание).*?\n(.*?)(?=\n#|\Z)",
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                text = match.group(1).strip()
                text = re.sub(r"[*-]\s+", "", text)
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                return " ".join(lines[:2]) if lines else text[:150]
        return "Назначение не указано"

    def _extract_features(self, content: str) -> list[str]:
        """Извлечение ключевых возможностей"""
        features = []
        patterns = [
            r"(?:Ключевые возможности|Features|Возможности)[:\s]*(.*?)(?=\n##|\Z)",
            r"(?:ключевые особенности|функции)[:\s]*(.*?)(?=\n##|\Z)",
        ]
        for pattern in patterns:
            section = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if section:
                text = section.group(1)
                items = re.findall(r"[*-]\s*\[[x ]\]\s*(.*?)(?=\n|$)", text)
                if not items:
                    items = re.findall(r"[*-]\s*(.*?)(?=\n|$)", text)
                features.extend([item.strip() for item in items if item.strip()])
        return features[:5]

    def _extract_status(self, content: str) -> str:
        """Извлечение статуса"""
        content_lower = content.lower()
        if "production ready" in content_lower or "production-ready" in content_lower or "🟢" in content:
            return "Production Ready"
        elif "mvp" in content_lower or "minimum viable product" in content_lower or "🟡" in content:
            return "MVP"
        elif (
            "wip" in content_lower
            or "work in progress" in content_lower
            or "under development" in content_lower
            or "🔴" in content
        ):
            return "WIP"
        elif (
            "alpha" in content_lower
            or "beta" in content_lower
            or "development" in content_lower
            or "active" in content_lower
            or "dev" in content_lower
        ):
            return "Active"
        return "Active"  # По умолчанию считаем активным

    def _assess_unique(self, content: str) -> int:
        """Оценка уникальности"""
        score = 5
        content_lower = content.lower()

        # Проверяем содержимое файла для оценки уникальности
        if "уникаль" in content_lower or "unique" in content_lower:
            score += 2
        if "ai" in content or "агент" in content_lower or "agent" in content_lower:
            score += 1
        if "ddd" in content_lower or "архитектур" in content_lower or "architecture" in content_lower:
            score += 1
        if "интеграц" in content_lower or "integration" in content_lower:
            score += 1
        if "cognitive" in content_lower or "когнитивн" in content_lower:
            score += 2
        if "autonomous" in content_lower or "автономн" in content_lower:
            score += 2
        if "multi-agent" in content_lower or "multiagent" in content_lower or "многоагентн" in content_lower:
            score += 2

        return min(score, 10)

    def _assess_market(self, content: str) -> int:
        """Оценка рыночного спроса"""
        score = 5
        content_lower = content.lower()
        keywords = [
            "AI",
            "ML",
            "cloud",
            "автоматизац",
            "агент",
            "RAG",
            "cognitive",
            "multi-agent",
            "orchestrator",
            "framework",
        ]
        for kw in keywords:
            if kw.lower() in content_lower:
                score += 0.5
        return min(int(score), 10)

    def _research_web(self):
        """Веб-исследование"""
        print("\n🌐 Исследование рынка через интернет...")

        # Ищем аналоги для ключевых сервисов
        key_services = ["cognitive_agent", "it_compass", "decision_engine"]

        for service_name in key_services:
            # Проверяем, есть ли такой сервис
            service = next((s for s in self.results["services"] if s["name"] == service_name), None)
            if service:
                print(f"  • Ищем аналоги для {service_name}...")
                analogs = self._search_web(f"alternatives to {service_name} software")
                service["web_analogs"] = analogs[:3]

        # Ищем общие тренды
        print("  • Ищем тренды в AI-инженерии...")
        trends = self._search_web("AI agent software engineering trends 2026")
        self.results["web_research"]["trends"] = trends[:5]

        # Ищем вакансии
        print("  • Ищем вакансии для Cognitive Architect...")
        jobs = self._search_web("cognitive architect job requirements")
        self.results["web_research"]["jobs"] = jobs[:5]

    def _search_web(self, query: str) -> list[str]:
        """Поиск через DuckDuckGo"""
        results = []
        try:
            encoded = quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                snippets = soup.select(".result__snippet")
                for snippet in snippets[:5]:
                    text = snippet.get_text(strip=True)
                    if text and len(text) > 20:
                        results.append(text[:200])
        except Exception as e:
            print(f"    ⚠️ Ошибка поиска: {e}")

        return results if results else ["Информация временно недоступна"]

    def _assess_uniqueness(self):
        """Оценка уникальности экосистемы"""
        print("\n💎 Оценка уникальности...")

        # Считаем уникальные сервисы
        unique_services = [s for s in self.results["services"] if s.get("unique_score", 0) >= 7]

        # Сравниваем с рыночными трендами
        market_match = 0
        trends = self.results["web_research"].get("trends", [])
        for trend in trends:
            if "AI" in trend or "агент" in trend or "автоматизация" in trend:
                market_match += 1

        uniqueness = {
            "unique_services_count": len(unique_services),
            "total_services": len(self.results["services"]),
            "uniqueness_percentage": (len(unique_services) / max(len(self.results["services"]), 1)) * 100,
            "market_alignment": market_match / max(len(trends), 1) * 100 if trends else 50,
            "unique_services_names": [s["name"] for s in unique_services],
            "services_with_src": sum(1 for s in self.results["services"] if s.get("has_src", False)),
            "services_with_tests": sum(1 for s in self.results["services"] if s.get("has_tests", False)),
            "total_python_files": sum(s.get("python_files", 0) for s in self.results["services"]),
        }

        self.results["uniqueness_analysis"] = uniqueness

        print(f"  • Уникальных сервисов: {uniqueness['unique_services_count']}/{uniqueness['total_services']}")
        print(f"  • Уникальность: {uniqueness['uniqueness_percentage']:.0f}%")
        print(f"  • Сервисов с src/: {uniqueness['services_with_src']}/{uniqueness['total_services']}")
        print(f"  • Сервисов с tests/: {uniqueness['services_with_tests']}/{uniqueness['total_services']}")
        print(f"  • Всего Python файлов: {uniqueness['total_python_files']}")
        print(f"  • Соответствие трендам: {uniqueness['market_alignment']:.0f}%")

    def _analyze_market(self):
        """Рыночный анализ"""
        print("\n📈 Рыночный анализ...")

        metrics = self.results["project_metrics"]
        services = self.results["services"]

        # Средняя уникальность сервисов
        avg_unique = sum(s.get("unique_score", 5) for s in services) / max(len(services), 1)

        # Средний рыночный спрос
        avg_market = sum(s.get("market_score", 5) for s in services) / max(len(services), 1)

        # Конкурентное преимущество
        competitive_advantage = (
            (metrics.get("Рыночный спрос (0-1)", 0.5) * 100)
            + (avg_unique * 10)
            + (metrics.get("Уровень инноваций (0-1)", 0.5) * 100)
        ) / 3

        market_analysis = {
            "avg_uniqueness": avg_unique,
            "avg_market_demand": avg_market,
            "competitive_advantage": competitive_advantage,
            "market_attractiveness": metrics.get("Рыночный спрос (0-1)", 0.5) * 100,
            "innovation_level": metrics.get("Уровень инноваций (0-1)", 0.5) * 100,
            "scalability": metrics.get("Масштабируемость (0-1)", 0.5) * 100,
            "risk_level": metrics.get("Фактор риска (0-1)", 0.5) * 100,
            "team_expertise": metrics.get("Экспертиза команды (0-1)", 0.5) * 100,
        }

        self.results["market_analysis"] = market_analysis

        print(f"  • Средняя уникальность: {avg_unique:.1f}/10")
        print(f"  • Конкурентное преимущество: {competitive_advantage:.0f}%")
        print(f"  • Привлекательность рынка: {market_analysis['market_attractiveness']:.0f}%")
        print(f"  • Уровень инноваций: {market_analysis['innovation_level']:.0f}%")
        print(f"  • Масштабируемость: {market_analysis['scalability']:.0f}%")

    def _generate_recommendations(self):
        """Генерация рекомендаций"""
        print("\n💡 Генерация рекомендаций...")

        recommendations = []
        metrics = self.results["project_metrics"]
        uniqueness = self.results.get("uniqueness_analysis", {})
        market = self.results.get("market_analysis", {})
        services = self.results.get("services", [])

        # 1. Стратегия позиционирования
        if uniqueness.get("uniqueness_percentage", 0) > 50:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "strategy",
                    "title": "Позиционируйтесь как Cognitive Systems Architect",
                    "description": "Ваша экосистема уникальна — используйте это",
                    "action": "Обновите LinkedIn, резюме, GitHub с этим позиционированием",
                }
            )

        # 2. Демонстрация
        recommendations.append(
            {
                "priority": "high",
                "category": "marketing",
                "title": "Создайте публичную демонстрацию",
                "description": "Покажите агента в действии на видео",
                "action": "Запишите 5-минутную демонстрацию работы Cognitive Agent",
            }
        )

        # 3. Монетизация
        if metrics.get("Потенциал выручки ($)", 0) > 100000:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "monetization",
                    "title": "Рассмотрите варианты монетизации",
                    "description": "Ваш проект имеет коммерческий потенциал",
                    "action": "Изучите: Open Core, SaaS, Consulting",
                }
            )

        # 4. Команда
        if metrics.get("Размер команды", 0) < 3:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "team",
                    "title": "Увеличьте команду",
                    "description": "5 человек — мало для такой экосистемы",
                    "action": "Найдите: AI Engineer, DevOps, Frontend",
                }
            )

        # 5. Технологии
        tech_stack = metrics.get("Технологический стек", "")
        if "kubernetes" in tech_stack.lower():
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "tech",
                    "title": "Инвестируйте в DevOps",
                    "description": "Kubernetes требует квалифицированной поддержки",
                    "action": "Наймите DevOps-инженера с опытом K8s",
                }
            )

        # 6. Гранты
        if metrics.get("Уровень инноваций (0-1)", 0) > 0.5:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "funding",
                    "title": "Подайте заявки на гранты",
                    "description": "Ваш проект инновационный и может получить финансирование",
                    "action": "SourceCraft, Yandex Open Source, AI Grants",
                }
            )

        # 7. Улучшение архитектуры
        services_without_src = [s["name"] for s in services if not s.get("has_src", False)]
        if services_without_src:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "architecture",
                    "title": "Стандартизируйте структуру сервисов",
                    "description": "Некоторые сервисы не соответствуют архитектурным стандартам",
                    "action": f"Добавьте src/ директории для: {', '.join(services_without_src[:3])}",
                }
            )

        # 8. Покрытие тестами
        services_without_tests = [s["name"] for s in services if not s.get("has_tests", False)]
        if services_without_tests:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "quality",
                    "title": "Добавьте тесты для сервисов",
                    "description": "Некоторые сервисы не имеют тестов",
                    "action": f"Создайте тесты для: {', '.join(services_without_tests[:5])}",
                }
            )

        self.results["recommendations"] = recommendations

        for rec in recommendations:
            priority = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            print(f"  {priority} {rec['title']}")

    def _create_summary(self):
        """Создание сводки"""
        metrics = self.results["project_metrics"]
        market = self.results.get("market_analysis", {})
        uniqueness = self.results.get("uniqueness_analysis", {})
        services = self.results.get("services", [])

        # Оценка готовности (реалистичная)
        readiness = 0
        if market.get("competitive_advantage", 0) > 50:
            readiness += 1
        if uniqueness.get("uniqueness_percentage", 0) > 50:
            readiness += 1
        if metrics.get("Рыночный спрос (0-1)", 0) > 0.5:
            readiness += 1
        if metrics.get("Экспертиза команды (0-1)", 0) > 0.5:
            readiness += 1
        if metrics.get("Фактор риска (0-1)", 0) < 0.4:
            readiness += 1

        summary = {
            "project_readiness": (readiness / 5) * 100,
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
        }

        # Сильные стороны
        if uniqueness.get("uniqueness_percentage", 0) > 50:
            summary["strengths"].append("Высокая уникальность экосистемы")
        if market.get("competitive_advantage", 0) > 50:
            summary["strengths"].append("Сильное конкурентное преимущество")
        if metrics.get("Рыночный спрос (0-1)", 0) > 0.6:
            summary["strengths"].append("Высокий рыночный спрос")
        if uniqueness.get("total_python_files", 0) > 1000:
            summary["strengths"].append(f"Большой объем кода: {uniqueness['total_python_files']} Python файлов")
        if uniqueness.get("services_with_tests", 0) > 5:
            summary["strengths"].append(f"Наличие тестов: {uniqueness['services_with_tests']} сервисов протестировано")

        # Слабые стороны
        if metrics.get("Размер команды", 0) < 3:
            summary["weaknesses"].append("Малая команда для такого масштаба")
        if uniqueness.get("services_with_src", 0) < len(services) * 0.5:
            summary["weaknesses"].append(
                f"Мало сервисов с src/ директорией: {uniqueness['services_with_src']}/{len(services)}"
            )
        if uniqueness.get("services_with_tests", 0) < len(services) * 0.5:
            summary["weaknesses"].append(
                f"Недостаточное тестирование: {uniqueness['services_with_tests']}/{len(services)} сервисов с тестами"
            )

        # Возможности
        if metrics.get("Потенциал выручки ($)", 0) > 200000:
            summary["opportunities"].append("Высокий потенциал выручки")
        if metrics.get("Целевая аудитория (кол-во)", 0) > 5000:
            summary["opportunities"].append("Широкая целевая аудитория")
        if uniqueness.get("unique_services_count", 0) > 10:
            summary["opportunities"].append(f"Много уникальных сервисов: {uniqueness['unique_services_count']} шт.")

        # Реальные угрозы
        if metrics.get("Уровень конкуренции (0-1)", 0) > 0.6:
            summary["threats"].append("Высокая конкуренция")
        if metrics.get("Фактор риска (0-1)", 0) > 0.5:
            summary["threats"].append("Высокий фактор риска")
        if uniqueness.get("services_with_tests", 0) < 5:
            summary["threats"].append("Недостаточное тестирование может вызвать проблемы с надежностью")

        self.results["summary"] = summary

        print("\n📊 ИТОГОВАЯ СВОДКА:")
        print(f"  • Готовность проекта: {summary['project_readiness']:.0f}%")
        print(f"  • Сильные стороны: {len(summary['strengths'])}")
        print(f"  • Возможности: {len(summary['opportunities'])}")
        print(f"  • Угрозы: {len(summary['threats'])}")

    def _save_report(self):
        """Сохранение отчёта"""
        print("\n💾 Сохранение отчёта...")

        # JSON
        json_path = self.repo_path / "complete_strategic_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        # Текстовый отчёт
        txt_path = self.repo_path / "complete_strategic_report.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("🧠  ПОЛНЫЙ СТРАТЕГИЧЕСКИЙ ОТЧЁТ\n")
            f.write("=" * 70 + "\n\n")

            f.write("📊 МЕТРИКИ ПРОЕКТА:\n")
            for key, value in self.results["project_metrics"].items():
                f.write(f"  • {key}: {value}\n")

            f.write("\n📈 АНАЛИЗ ЖИЗНЕСПОСОБНОСТИ:\n")
            viability = self.results.get("project_metrics_analysis", {})
            f.write(f"  • Оценка: {viability.get('percentage', 0):.0f}%\n")
            f.write(f"  • Уровень: {viability.get('level', 'unknown')}\n")
            f.write(f"  • ROI: {viability.get('roi_percentage', 0):.0f}%\n")

            f.write("\n💎 УНИКАЛЬНОСТЬ:\n")
            uniqueness = self.results.get("uniqueness_analysis", {})
            f.write(
                f"  • Уникальных сервисов: {uniqueness.get('unique_services_count', 0)}/{uniqueness.get('total_services', 0)}\n"
            )
            f.write(f"  • Процент уникальности: {uniqueness.get('uniqueness_percentage', 0):.0f}%\n")
            f.write(f"  • Всего Python файлов: {uniqueness.get('total_python_files', 0)}\n")
            f.write(f"  • Сервисов с src/: {uniqueness.get('services_with_src', 0)}\n")
            f.write(f"  • Сервисов с tests/: {uniqueness.get('services_with_tests', 0)}\n")
            if uniqueness.get("unique_services_names"):
                f.write(f"  • Сервисы: {', '.join(uniqueness['unique_services_names'])}\n")

            f.write("\n📈 РЫНОЧНЫЙ АНАЛИЗ:\n")
            market = self.results.get("market_analysis", {})
            f.write(f"  • Конкурентное преимущество: {market.get('competitive_advantage', 0):.0f}%\n")
            f.write(f"  • Привлекательность рынка: {market.get('market_attractiveness', 0):.0f}%\n")
            f.write(f"  • Уровень инноваций: {market.get('innovation_level', 0):.0f}%\n")
            f.write(f"  • Масштабируемость: {market.get('scalability', 0):.0f}%\n")

            f.write("\n🌐 ИССЛЕДОВАНИЕ РЫНКА:\n")
            web = self.results.get("web_research", {})
            if web.get("trends"):
                f.write("  • Тренды:\n")
                for trend in web["trends"][:3]:
                    f.write(f"    - {trend[:100]}...\n")

            f.write("\n💡 РЕКОМЕНДАЦИИ:\n")
            for rec in self.results.get("recommendations", []):
                f.write(f"\n  [{rec['priority'].upper()}] {rec['title']}")
                f.write(f"\n    • {rec['description']}")
                f.write(f"\n    • Действие: {rec['action']}\n")

            f.write("\n📊 ИТОГОВАЯ СВОДКА:\n")
            summary = self.results.get("summary", {})
            f.write(f"  • Готовность проекта: {summary.get('project_readiness', 0):.0f}%\n")
            f.write(f"  • Сильные стороны: {', '.join(summary.get('strengths', ['нет']))}\n")
            f.write(f"  • Возможности: {', '.join(summary.get('opportunities', ['нет']))}\n")
            f.write(f"  • Слабые стороны: {', '.join(summary.get('weaknesses', ['нет']))}\n")
            f.write(f"  • Угрозы: {', '.join(summary.get('threats', ['нет']))}\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("✅ АНАЛИЗ ЗАВЕРШЁН\n")
            f.write("=" * 70 + "\n")

        print(f"  ✅ JSON: {json_path}")
        print(f"  ✅ TXT: {txt_path}")


def main():
    import sys

    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    metrics_file = sys.argv[2] if len(sys.argv) > 2 else None

    analyzer = CompleteStrategicAnalyzer(repo_path, metrics_file)
    results = analyzer.analyze()

    print("\n" + "=" * 70)
    print("📊 ИТОГОВАЯ ОЦЕНКА ЭКОСИСТЕМЫ")
    print("=" * 70)

    summary = results.get("summary", {})
    print(f"\n🎯 Готовность проекта: {summary.get('project_readiness', 0):.0f}%")
    print("\n💪 Сильные стороны:")
    for s in summary.get("strengths", ["Не определены"]):
        print(f"  • {s}")
    print("\n🚀 Возможности:")
    for o in summary.get("opportunities", ["Не определены"]):
        print(f"  • {o}")
    print("\n⚠️ Слабые стороны:")
    for w in summary.get("weaknesses", ["Не определены"]):
        print(f"  • {w}")
    print("\n🚨 Угрозы:")
    for t in summary.get("threats", ["Не определены"]):
        print(f"  • {t}")

    print("\n" + "=" * 70)
    print("✅ Отчёт сохранён в:")
    print("  • complete_strategic_report.json")
    print("  • complete_strategic_report.txt")
    print("=" * 70)


if __name__ == "__main__":
    main()

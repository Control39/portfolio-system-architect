#!/usr/bin/env python3
"""
Полный стратегический анализатор с автоматическим сбором данных из репозитория
"""

import logging
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template_string

# Настройка
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


class ProjectType(Enum):
    STARTUP = "startup"
    ENTERPRISE = "enterprise"
    OPEN_SOURCE = "open_source"
    RESEARCH = "research"
    COMMERCIAL = "commercial"


@dataclass
class ServiceMetrics:
    """Метрики сервиса из репозитория"""

    name: str
    path: str
    status: str  # Production Ready, MVP, WIP, Active
    has_tests: bool
    test_count: int = 0
    has_readme: bool
    readme_size_kb: float = 0
    has_dockerfile: bool
    has_requirements: bool
    lines_of_code: int = 0
    python_files: int = 0
    tech_stack: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    description: str = ""
    features: list[str] = field(default_factory=list)


@dataclass
class ProjectMetrics:
    """Метрики всего проекта"""

    name: str
    description: str
    team_size: int
    budget: float
    timeline_months: int
    tech_stack: list[str]
    market_demand: float
    innovation_level: float
    scalability: float
    competition_level: float
    risk_factor: float
    team_expertise: float
    project_type: ProjectType
    dependencies: list[str]
    target_users: int
    revenue_potential: float
    services: list[ServiceMetrics] = field(default_factory=list)


@dataclass
class StrategicValueResult:
    project_name: str
    overall_score: float
    technology_score: float
    market_score: float
    team_score: float
    innovation_score: float
    scalability_score: float
    risk_assessment: float
    recommendations: list[str]
    strengths: list[str]
    weaknesses: list[str]
    confidence_level: float
    analysis_timestamp: str
    detailed_breakdown: dict[str, float]
    services_analysis: list[dict[str, Any]] = field(default_factory=list)


class RepoScanner:
    """Сканер репозитория для сбора метрик"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.services = []

    def scan(self) -> list[ServiceMetrics]:
        """Сканирование всех сервисов в apps/"""
        logger.info("🔍 Сканирование репозитория...")

        apps_dir = self.repo_path / "apps"
        if not apps_dir.exists():
            logger.warning("⚠️ Директория apps/ не найдена")
            return []

        for service_dir in apps_dir.iterdir():
            if not service_dir.is_dir():
                continue

            metrics = self._analyze_service(service_dir)
            if metrics:
                self.services.append(metrics)
                logger.info(f"  • {metrics.name}: {metrics.status}, {metrics.lines_of_code} строк")

        return self.services

    def _analyze_service(self, service_dir: Path) -> ServiceMetrics | None:
        """Анализ отдельного сервиса"""
        name = service_dir.name

        # README
        readme_path = service_dir / "README.md"
        has_readme = readme_path.exists()
        readme_size = 0
        description = ""
        features = []
        status = "Unknown"

        if has_readme:
            content = readme_path.read_text(encoding="utf-8", errors="ignore")
            readme_size = len(content) / 1024

            # Извлечение статуса
            if "Production Ready" in content or "🟢" in content:
                status = "Production Ready"
            elif "MVP" in content or "🟡" in content:
                status = "MVP"
            elif "WIP" in content or "🔴" in content:
                status = "WIP"
            elif "Active" in content:
                status = "Active"

            # Извлечение описания
            import re

            desc_match = re.search(r"## 🎯 Назначение\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
            if desc_match:
                description = desc_match.group(1).strip()[:200]

            # Извлечение фич
            features_match = re.search(r"Ключевые возможности[:\s]*(.*?)(?=\n##|\Z)", content, re.DOTALL)
            if features_match:
                items = re.findall(r"[*-]\s*\[[x ]\]\s*(.*?)(?=\n|$)", features_match.group(1))
                features = [f.strip() for f in items[:5]]

        # Тесты
        tests_dir = service_dir / "tests"
        has_tests = tests_dir.exists()
        test_count = 0
        if has_tests:
            test_files = list(tests_dir.rglob("test_*.py"))
            test_count = len(test_files)

        # Файлы
        python_files = list(service_dir.rglob("*.py"))
        python_count = len(python_files)
        lines = 0
        for py_file in python_files:
            try:
                lines += len(py_file.read_text(encoding="utf-8", errors="ignore").split("\n"))
            except:
                pass

        # Технологии из README
        tech_stack = []
        if has_readme:
            content = readme_path.read_text(encoding="utf-8", errors="ignore")
            tech_keywords = [
                "Python",
                "FastAPI",
                "Django",
                "Flask",
                "React",
                "Vue",
                "Angular",
                "Docker",
                "Kubernetes",
                "PostgreSQL",
                "ChromaDB",
                "Redis",
                "Nginx",
            ]
            for tech in tech_keywords:
                if tech.lower() in content.lower():
                    tech_stack.append(tech)

        # Зависимости из requirements.txt
        dependencies = []
        req_path = service_dir / "requirements.txt"
        if req_path.exists():
            content = req_path.read_text(encoding="utf-8", errors="ignore")
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split("[")[0].strip()
                    if pkg:
                        dependencies.append(pkg)

        return ServiceMetrics(
            name=name,
            path=str(service_dir.relative_to(self.repo_path)),
            status=status,
            has_tests=has_tests,
            test_count=test_count,
            has_readme=has_readme,
            readme_size_kb=readme_size,
            has_dockerfile=(service_dir / "Dockerfile").exists(),
            has_requirements=req_path.exists(),
            lines_of_code=lines,
            python_files=python_count,
            tech_stack=tech_stack[:5],
            dependencies=dependencies[:10],
            description=description,
            features=features,
        )


class StrategicValueAnalyzer:
    """Анализатор стратегической ценности"""

    def __init__(self):
        self.weights = {
            "technology": 0.15,
            "market": 0.25,
            "team": 0.20,
            "innovation": 0.15,
            "scalability": 0.15,
            "risk": 0.10,
        }

    def analyze(self, metrics: ProjectMetrics) -> StrategicValueResult:
        """Полный анализ проекта"""

        # 1. Анализ технологий
        tech_score = self._analyze_technology(metrics)

        # 2. Анализ рынка
        market_score = self._analyze_market(metrics)

        # 3. Анализ команды
        team_score = self._analyze_team(metrics)

        # 4. Анализ инноваций
        innovation_score = self._analyze_innovation(metrics)

        # 5. Анализ масштабируемости
        scalability_score = self._analyze_scalability(metrics)

        # 6. Анализ рисков
        risk_score = self._analyze_risk(metrics)

        scores = {
            "technology": tech_score,
            "market": market_score,
            "team": team_score,
            "innovation": innovation_score,
            "scalability": scalability_score,
            "risk": risk_score,
        }

        # Общая оценка
        overall = sum(scores[k] * self.weights[k] for k in scores)

        # Рекомендации
        recommendations = self._generate_recommendations(metrics, scores)

        # Сильные и слабые стороны
        strengths, weaknesses = self._get_strengths_weaknesses(metrics, scores)

        # Анализ сервисов
        services_analysis = self._analyze_services(metrics.services)

        return StrategicValueResult(
            project_name=metrics.name,
            overall_score=round(overall, 2),
            technology_score=round(tech_score, 2),
            market_score=round(market_score, 2),
            team_score=round(team_score, 2),
            innovation_score=round(innovation_score, 2),
            scalability_score=round(scalability_score, 2),
            risk_assessment=round(risk_score, 2),
            recommendations=recommendations,
            strengths=strengths,
            weaknesses=weaknesses,
            confidence_level=0.85,
            analysis_timestamp=datetime.now().isoformat(),
            detailed_breakdown=scores,
            services_analysis=services_analysis,
        )

    def _analyze_technology(self, metrics: ProjectMetrics) -> float:
        score = 0

        # Количество технологий
        tech_count = len(metrics.tech_stack)
        if tech_count > 5:
            score += 25
        elif tech_count > 3:
            score += 18
        else:
            score += 10

        # Современность технологий
        modern = ["python", "react", "vue", "angular", "typescript", "kubernetes", "docker", "ai", "ml", "fastapi"]
        modern_count = sum(1 for t in metrics.tech_stack if any(m in t.lower() for m in modern))
        score += min(modern_count * 4, 25)

        # Наличие Docker/Kubernetes
        if any("docker" in t.lower() or "kubernetes" in t.lower() for t in metrics.tech_stack):
            score += 15

        # Наличие тестов в сервисах
        services_with_tests = sum(1 for s in metrics.services if s.has_tests)
        if services_with_tests > 0:
            score += min(services_with_tests * 5, 20)

        # Качество документации
        services_with_readme = sum(1 for s in metrics.services if s.has_readme)
        if services_with_readme > 0:
            score += min(services_with_readme * 3, 15)

        return min(score, 100)

    def _analyze_market(self, metrics: ProjectMetrics) -> float:
        score = 0

        # Спрос
        score += metrics.market_demand * 35

        # Потенциал выручки
        if metrics.revenue_potential > 1000000:
            score += 25
        elif metrics.revenue_potential > 100000:
            score += 20
        elif metrics.revenue_potential > 50000:
            score += 15
        else:
            score += 5

        # Конкуренция (чем ниже, тем лучше)
        score += (1 - metrics.competition_level) * 25

        # Целевая аудитория
        if metrics.target_users > 1000000:
            score += 15
        elif metrics.target_users > 100000:
            score += 12
        elif metrics.target_users > 10000:
            score += 8
        else:
            score += 3

        return min(score, 100)

    def _analyze_team(self, metrics: ProjectMetrics) -> float:
        score = 0

        # Размер команды
        if 3 <= metrics.team_size <= 10:
            score += 30
        elif 11 <= metrics.team_size <= 20:
            score += 25
        elif metrics.team_size > 20:
            score += 20
        else:
            score += 10

        # Экспертиза
        score += metrics.team_expertise * 40

        # Бюджет
        if metrics.budget > 1000000:
            score += 20
        elif metrics.budget > 100000:
            score += 15
        else:
            score += 10

        return min(score, 100)

    def _analyze_innovation(self, metrics: ProjectMetrics) -> float:
        score = metrics.innovation_level * 100

        # Бонус за исследовательский тип
        if metrics.project_type == ProjectType.RESEARCH:
            score *= 1.2
        elif metrics.project_type == ProjectType.OPEN_SOURCE:
            score *= 1.1

        # Бонус за количество сервисов
        if len(metrics.services) > 10:
            score *= 1.1

        return min(score, 100)

    def _analyze_scalability(self, metrics: ProjectMetrics) -> float:
        score = metrics.scalability * 100

        # Короткий срок — хорошо для масштабирования
        if metrics.timeline_months <= 6:
            score *= 1.1

        # Большая аудитория — требует масштабируемости
        if metrics.target_users > 1000000:
            score *= 1.15
        elif metrics.target_users > 100000:
            score *= 1.05

        # Наличие Docker/Kubernetes помогает масштабированию
        if any("kubernetes" in t.lower() or "docker" in t.lower() for t in metrics.tech_stack):
            score *= 1.1

        return min(score, 100)

    def _analyze_risk(self, metrics: ProjectMetrics) -> float:
        risk_score = 100 - (metrics.risk_factor * 100)

        # Бюджет снижает риск
        if metrics.budget > 500000:
            risk_score += 15
        elif metrics.budget > 100000:
            risk_score += 10

        # Большая команда снижает риск
        if metrics.team_size >= 5:
            risk_score += 10

        # Высокая экспертиза снижает риск
        risk_score += metrics.team_expertise * 20

        # Наличие тестов снижает риск
        services_with_tests = sum(1 for s in metrics.services if s.has_tests)
        if services_with_tests > 0:
            risk_score += min(services_with_tests * 2, 10)

        return min(max(risk_score, 0), 100)

    def _generate_recommendations(self, metrics: ProjectMetrics, scores: dict[str, float]) -> list[str]:
        recs = []

        if scores["technology"] < 60:
            recs.append("Обновите технологический стек, добавьте современные инструменты")

        if scores["market"] < 70:
            if metrics.competition_level > 0.7:
                recs.append("Высокая конкуренция — сфокусируйтесь на уникальном преимуществе")
            if metrics.market_demand < 0.5:
                recs.append("Рыночный спрос низкий — пересмотрите ценностное предложение")

        if scores["team"] < 65:
            if metrics.team_size < 3:
                recs.append("Увеличьте команду до 5+ человек")
            if metrics.team_expertise < 0.6:
                recs.append("Инвестируйте в обучение и развитие команды")

        if scores["innovation"] < 70:
            recs.append("Повысьте инновационность через R&D и эксперименты")

        if scores["scalability"] < 65:
            recs.append("Оптимизируйте архитектуру для горизонтального масштабирования")

        if scores["risk"] < 75:
            recs.append("Разработайте стратегию управления рисками")

        # Анализ сервисов
        services_without_tests = [s.name for s in metrics.services if not s.has_tests]
        if services_without_tests:
            recs.append(f"Добавьте тесты для сервисов: {', '.join(services_without_tests[:3])}")

        services_without_readme = [s.name for s in metrics.services if not s.has_readme]
        if services_without_readme:
            recs.append(f"Добавьте README для: {', '.join(services_without_readme[:3])}")

        return recs[:10]

    def _get_strengths_weaknesses(self, metrics: ProjectMetrics, scores: dict[str, float]) -> tuple:
        strengths, weaknesses = [], []

        if scores["technology"] >= 80:
            strengths.append("Современный технологический стек")
        elif scores["technology"] < 60:
            weaknesses.append("Технологический стек требует обновления")

        if scores["market"] >= 80:
            strengths.append("Высокий рыночный потенциал")
        elif scores["market"] < 60:
            weaknesses.append("Низкий рыночный спрос или высокая конкуренция")

        if scores["team"] >= 80:
            strengths.append("Сильная и опытная команда")
        elif scores["team"] < 60:
            weaknesses.append("Команда требует усиления")

        if scores["innovation"] >= 80:
            strengths.append("Высокий уровень инноваций")
        elif scores["innovation"] < 70:
            weaknesses.append("Недостаточный уровень инноваций")

        if scores["scalability"] >= 80:
            strengths.append("Хорошая масштабируемость архитектуры")
        elif scores["scalability"] < 60:
            weaknesses.append("Проблемы с масштабируемостью")

        if scores["risk"] >= 85:
            strengths.append("Низкий уровень рисков")
        elif scores["risk"] < 75:
            weaknesses.append("Высокий уровень рисков")

        # Дополнительные сильные стороны из сервисов
        prod_services = [s.name for s in metrics.services if s.status == "Production Ready"]
        if len(prod_services) >= 3:
            strengths.append(f"Есть production-ready сервисы: {', '.join(prod_services[:3])}")

        services_with_tests = [s.name for s in metrics.services if s.has_tests]
        if services_with_tests:
            strengths.append(f"Есть тесты для: {', '.join(services_with_tests[:3])}")

        return strengths[:5], weaknesses[:5]

    def _analyze_services(self, services: list[ServiceMetrics]) -> list[dict[str, Any]]:
        """Анализ каждого сервиса"""
        result = []
        for s in services:
            # Оценка готовности сервиса
            readiness = 0
            if s.status == "Production Ready":
                readiness = 90
            elif s.status == "MVP":
                readiness = 60
            elif s.status == "Active":
                readiness = 50
            else:
                readiness = 30

            # Бонус за тесты
            if s.has_tests:
                readiness += 10

            result.append(
                {
                    "name": s.name,
                    "status": s.status,
                    "has_tests": s.has_tests,
                    "test_count": s.test_count,
                    "lines_of_code": s.lines_of_code,
                    "python_files": s.python_files,
                    "readme_size_kb": round(s.readme_size_kb, 1),
                    "readiness_score": min(readiness, 100),
                    "tech_stack": s.tech_stack[:3],
                    "description": s.description[:100] if s.description else "",
                }
            )

        return sorted(result, key=lambda x: x["readiness_score"], reverse=True)


# Flask приложение
app = Flask(__name__)

# Глобальный анализатор и данные
analyzer = StrategicValueAnalyzer()
scanner = RepoScanner(REPO_ROOT)
scanned_services = scanner.scan()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Strategic Value Analyzer</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0a0e17;
            color: #e0e0e0;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid #1a2332;
        }
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #4a6cf7, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }
        .header p {
            color: #8892b0;
            font-size: 1.1em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }
        .stat-card {
            background: #141b2b;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #1a2332;
            text-align: center;
        }
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #4a6cf7;
        }
        .stat-card .label {
            color: #8892b0;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 30px 0;
        }
        @media (max-width: 768px) {
            .main-grid { grid-template-columns: 1fr; }
        }
        .card {
            background: #141b2b;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #1a2332;
        }
        .card h3 {
            margin-top: 0;
            color: #4a6cf7;
            border-bottom: 1px solid #1a2332;
            padding-bottom: 10px;
        }
        .score-circle {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 70px;
            height: 70px;
            border-radius: 50%;
            font-size: 1.5em;
            font-weight: bold;
            margin: 5px;
        }
        .score-high { background: #10b981; color: white; }
        .score-mid { background: #f59e0b; color: white; }
        .score-low { background: #ef4444; color: white; }
        .service-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #1a2332;
        }
        .service-item .name { color: #e0e0e0; }
        .service-item .status { font-size: 0.85em; padding: 2px 10px; border-radius: 12px; }
        .status-ready { background: #10b981; color: white; }
        .status-mvp { background: #f59e0b; color: white; }
        .status-wip { background: #ef4444; color: white; }
        .status-active { background: #4a6cf7; color: white; }
        .recommendations-list { list-style: none; padding: 0; }
        .recommendations-list li {
            padding: 8px 12px;
            margin: 5px 0;
            background: #1a2332;
            border-radius: 6px;
            border-left: 3px solid #4a6cf7;
        }
        .btn {
            background: #4a6cf7;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #3a5bd9;
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #1a2332;
            border: 1px solid #4a6cf7;
        }
        .btn-secondary:hover {
            background: #2a3a52;
        }
        .flex { display: flex; gap: 10px; flex-wrap: wrap; }
        .mt-20 { margin-top: 20px; }
        .text-center { text-align: center; }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.75em;
            background: #1a2332;
        }
        .hidden { display: none; }
        .loading {
            text-align: center;
            padding: 40px;
            color: #8892b0;
        }
        .spinner {
            border: 3px solid #1a2332;
            border-top: 3px solid #4a6cf7;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .tab-bar {
            display: flex;
            gap: 5px;
            margin-bottom: 15px;
            border-bottom: 1px solid #1a2332;
            padding-bottom: 10px;
        }
        .tab {
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 6px;
            background: transparent;
            color: #8892b0;
            border: none;
        }
        .tab.active {
            background: #1a2332;
            color: #4a6cf7;
        }
        .tab:hover { background: #1a2332; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🧠 Strategic Value Analyzer</h1>
        <p>Автоматический анализ стратегической ценности вашего проекта</p>
        <div class="flex" style="justify-content:center;margin-top:15px;">
            <button class="btn" onclick="runAnalysis()">🔄 Анализировать заново</button>
            <button class="btn btn-secondary" onclick="exportReport()">📥 Экспорт отчёта</button>
        </div>
    </div>

    <div id="loading" class="loading">
        <div class="spinner"></div>
        <p>Анализ выполняется...</p>
    </div>

    <div id="content" class="hidden">
        <div class="stats-grid" id="statsGrid"></div>

        <div class="tab-bar">
            <button class="tab active" onclick="showTab('overview')">📊 Обзор</button>
            <button class="tab" onclick="showTab('services')">📁 Сервисы</button>
            <button class="tab" onclick="showTab('recommendations')">💡 Рекомендации</button>
        </div>

        <div id="tab-overview" class="main-grid"></div>
        <div id="tab-services" class="hidden"></div>
        <div id="tab-recommendations" class="hidden"></div>
    </div>
</div>

<script>
let currentData = null;

async function runAnalysis() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('content').classList.add('hidden');

    try {
        const res = await fetch('/analyze', { method: 'POST' });
        const data = await res.json();
        currentData = data;
        displayResults(data);
    } catch(e) {
        alert('Ошибка: ' + e.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('content').classList.remove('hidden');
    }
}

function displayResults(data) {
    // Статистика
    document.getElementById('statsGrid').innerHTML = `
        <div class="stat-card"><div class="value">${data.overall_score}</div><div class="label">Общая оценка</div></div>
        <div class="stat-card"><div class="value">${data.services_analysis?.length || 0}</div><div class="label">Сервисов</div></div>
        <div class="stat-card"><div class="value">${data.strengths?.length || 0}</div><div class="label">Сильных сторон</div></div>
        <div class="stat-card"><div class="value">${data.recommendations?.length || 0}</div><div class="label">Рекомендаций</div></div>
    `;

    // Обзор
    const overview = document.getElementById('tab-overview');
    overview.innerHTML = `
        <div class="card">
            <h3>📊 Оценки по категориям</h3>
            ${renderScores(data)}
            <p style="margin-top:15px;color:#8892b0;">Уверенность: ${(data.confidence_level * 100).toFixed(0)}%</p>
            <p style="color:#8892b0;">Дата: ${new Date(data.analysis_timestamp).toLocaleString()}</p>
        </div>
        <div class="card">
            <h3>💪 Сильные стороны</h3>
            ${data.strengths?.length ? '<ul>' + data.strengths.map(s => `<li>${s}</li>`).join('') + '</ul>' : '<p style="color:#8892b0;">Нет данных</p>'}
            <h3 style="margin-top:15px;">⚠️ Слабые стороны</h3>
            ${data.weaknesses?.length ? '<ul>' + data.weaknesses.map(s => `<li>${s}</li>`).join('') + '</ul>' : '<p style="color:#8892b0;">Нет данных</p>'}
        </div>
    `;

    // Сервисы
    const servicesDiv = document.getElementById('tab-services');
    if (data.services_analysis?.length) {
        servicesDiv.innerHTML = `
            <div class="card">
                <h3>📁 Сервисы (${data.services_analysis.length})</h3>
                ${data.services_analysis.map(s => `
                    <div class="service-item">
                        <span class="name">${s.name}</span>
                        <span>
                            <span class="status status-${s.status?.toLowerCase?.()?.replace(' ', '-') || 'active'}">${s.status || 'Unknown'}</span>
                            <span class="badge">${s.readiness_score}%</span>
                            ${s.has_tests ? '<span class="badge">✅ тесты</span>' : ''}
                        </span>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        servicesDiv.innerHTML = `<div class="card"><p style="color:#8892b0;">Сервисы не найдены</p></div>`;
    }

    // Рекомендации
    const recDiv = document.getElementById('tab-recommendations');
    if (data.recommendations?.length) {
        recDiv.innerHTML = `
            <div class="card">
                <h3>💡 Рекомендации</h3>
                <ul class="recommendations-list">
                    ${data.recommendations.map(r => `<li>${r}</li>`).join('')}
                </ul>
            </div>
        `;
    } else {
        recDiv.innerHTML = `<div class="card"><p style="color:#8892b0;">Рекомендаций нет</p></div>`;
    }
}

function renderScores(data) {
    const items = [
        { key: 'technology_score', label: 'Технологии' },
        { key: 'market_score', label: 'Рынок' },
        { key: 'team_score', label: 'Команда' },
        { key: 'innovation_score', label: 'Инновации' },
        { key: 'scalability_score', label: 'Масштаб' },
        { key: 'risk_assessment', label: 'Риски' }
    ];
    return items.map(({key, label}) => {
        const val = data[key] || 0;
        const cls = val >= 75 ? 'score-high' : val >= 50 ? 'score-mid' : 'score-low';
        return `<div><span class="score-circle ${cls}">${val}</span> ${label}</div>`;
    }).join('');
}

function showTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('[id^="tab-"]').forEach(t => t.classList.add('hidden'));

    document.querySelector(`.tab[onclick*="${tab}"]`).classList.add('active');
    document.getElementById(`tab-${tab}`).classList.remove('hidden');
}

function exportReport() {
    if (!currentData) return;
    const dataStr = JSON.stringify(currentData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `strategic_report_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Запуск при загрузке
document.addEventListener('DOMContentLoaded', runAnalysis);
</script>
</body>
</html>
"""


@app.route("/")
def index():
    """Главная страница с автоматическим анализом"""
    return render_template_string(HTML_TEMPLATE)


@app.route("/analyze", methods=["POST"])
def analyze():
    """Запуск полного анализа"""
    try:
        # Сканируем сервисы заново
        scanner = RepoScanner(REPO_ROOT)
        services = scanner.scan()

        # Собираем метрики из сканирования
        tech_stack = set()
        dependencies = set()
        for s in services:
            tech_stack.update(s.tech_stack)
            dependencies.update(s.dependencies)

        # Формируем метрики проекта
        metrics = ProjectMetrics(
            name="Portfolio System Architect",
            description="Экосистема из 20+ сервисов с когнитивным агентом",
            team_size=5,
            budget=100000,
            timeline_months=12,
            tech_stack=list(tech_stack)[:10] or ["python", "react", "docker", "kubernetes"],
            market_demand=0.7,
            innovation_level=0.6,
            scalability=0.7,
            competition_level=0.5,
            risk_factor=0.3,
            team_expertise=0.7,
            project_type=ProjectType.STARTUP,
            dependencies=list(dependencies)[:15],
            target_users=10000,
            revenue_potential=500000,
            services=services,
        )

        # Анализ
        result = analyzer.analyze(metrics)
        return jsonify(asdict(result))

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/services", methods=["GET"])
def get_services():
    """Получение списка сервисов"""
    scanner = RepoScanner(REPO_ROOT)
    services = scanner.scan()
    return jsonify([asdict(s) for s in services])


def main():
    print("=" * 60)
    print("🧠  STRATEGIC VALUE ANALYZER")
    print("=" * 60)
    print(f"📁 Репозиторий: {REPO_ROOT}")
    print(f"📊 Найдено сервисов: {len(scanned_services)}")
    print("")
    print("🌐 Открой в браузере: http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()

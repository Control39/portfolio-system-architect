#!/usr/bin/env python3
"""
Strategic Value Analyzer Web Interface - Enterprise Version
"""

import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Добавляем корень репозитория в путь для правильного импорта
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Импортируем enterprise версию агента из правильного места
from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Типы проектов
class ProjectType(Enum):
    STARTUP = "startup"
    ENTERPRISE = "enterprise"
    OPEN_SOURCE = "open_source"
    RESEARCH = "research"
    COMMERCIAL = "commercial"


@dataclass
class ProjectMetrics:
    """Метрики проекта для анализа стратегической ценности"""

    name: str
    description: str
    team_size: int
    budget: float
    timeline_months: int
    tech_stack: list[str]
    market_demand: float  # 0-1
    innovation_level: float  # 0-1
    scalability: float  # 0-1
    competition_level: float  # 0-1
    risk_factor: float  # 0-1
    team_expertise: float  # 0-1
    project_type: ProjectType
    dependencies: list[str]
    target_users: int
    revenue_potential: float


@dataclass
class StrategicValueResult:
    """Результат анализа стратегической ценности"""

    project_name: str
    overall_score: float  # 0-100
    technology_score: float
    market_score: float
    team_score: float
    innovation_score: float
    scalability_score: float
    risk_assessment: float
    recommendations: list[str]
    strengths: list[str]
    weaknesses: list[str]
    confidence_level: float  # 0-1
    analysis_timestamp: str
    detailed_breakdown: dict[str, float]


class StrategicValueAnalyzer:
    """Анализатор стратегической ценности проектов"""

    def __init__(self):
        self.weights = {
            "technology": 0.15,
            "market": 0.25,
            "team": 0.20,
            "innovation": 0.15,
            "scalability": 0.15,
            "risk": 0.10,
        }
        self.agents_used = []

    def analyze_technology(self, metrics: ProjectMetrics) -> float:
        """Анализ технологической составляющей (0-100)"""
        score = 0

        # Оценка технологического стека
        if len(metrics.tech_stack) > 5:
            score += 20
        elif len(metrics.tech_stack) > 3:
            score += 15
        else:
            score += 10

        # Современность технологий (упрощенная оценка)
        modern_tech = [
            "react",
            "vue",
            "angular",
            "python",
            "typescript",
            "kubernetes",
            "docker",
            "ai",
            "ml",
            "blockchain",
        ]
        modern_score = sum(1 for tech in metrics.tech_stack if any(
            mod in tech.lower() for mod in modern_tech))
        score += min(modern_score * 3, 20)

        # Зависимости
        if len(metrics.dependencies) < 10:
            score += 15
        elif len(metrics.dependencies) < 20:
            score += 10
        else:
            score += 5

        return min(score, 100)

    def analyze_market(self, metrics: ProjectMetrics) -> float:
        """Анализ рыночной составляющей (0-100)"""
        score = 0

        # Спрос на рынке
        demand_score = metrics.market_demand * 40
        score += demand_score

        # Потенциал выручки
        if metrics.revenue_potential > 1000000:
            score += 25
        elif metrics.revenue_potential > 100000:
            score += 20
        elif metrics.revenue_potential > 10000:
            score += 15
        else:
            score += 5

        # Конкуренция (меньше конкуренции - выше балл)
        competition_impact = (1 - metrics.competition_level) * 35
        score += competition_impact

        # Целевые пользователи
        if metrics.target_users > 1000000:
            score += 20
        elif metrics.target_users > 100000:
            score += 15
        elif metrics.target_users > 10000:
            score += 10
        else:
            score += 5

        return min(score, 100)

    def analyze_team(self, metrics: ProjectMetrics) -> float:
        """Анализ командной составляющей (0-100)"""
        score = 0

        # Размер команды
        if 3 <= metrics.team_size <= 10:
            score += 25
        elif 11 <= metrics.team_size <= 20:
            score += 20
        elif metrics.team_size > 20:
            score += 15
        else:
            score += 10

        # Экспертиза команды
        expertise_score = metrics.team_expertise * 40
        score += expertise_score

        # Бюджет (для найма и развития)
        if metrics.budget > 1000000:
            score += 20
        elif metrics.budget > 100000:
            score += 15
        elif metrics.budget > 10000:
            score += 10
        else:
            score += 5

        return min(score, 100)

    def analyze_innovation(self, metrics: ProjectMetrics) -> float:
        """Анализ инновационности (0-100)"""
        score = metrics.innovation_level * 100

        # Учет типа проекта
        if metrics.project_type == ProjectType.RESEARCH:
            score *= 1.2  # Исследовательские проекты более инновационны
        elif metrics.project_type == ProjectType.OPEN_SOURCE:
            score *= 1.1  # Открытый исходный код способствует инновациям

        return min(score, 100)

    def analyze_scalability(self, metrics: ProjectMetrics) -> float:
        """Анализ масштабируемости (0-100)"""
        score = metrics.scalability * 100

        # Влияние продолжительности проекта
        if metrics.timeline_months <= 6:
            score *= 1.1  # Короткие проекты могут быть более масштабируемыми
        elif metrics.timeline_months > 24:
            score *= 0.9  # Долгосрочные проекты сложнее масштабировать

        # Влияние размера целевой аудитории
        if metrics.target_users > 1000000:
            score *= 1.2
        elif metrics.target_users > 100000:
            score *= 1.1
        elif metrics.target_users > 10000:
            score *= 1.05

        return min(score, 100)

    def analyze_risk(self, metrics: ProjectMetrics) -> float:
        """Анализ рисков (0-100, где 100 = минимальный риск)"""
        base_risk = metrics.risk_factor * 100
        risk_score = 100 - base_risk  # Чем выше риск фактор, тем ниже оценка

        # Учет бюджета как фактора снижения риска
        if metrics.budget > 500000:
            risk_score += 15
        elif metrics.budget > 100000:
            risk_score += 10
        elif metrics.budget > 10000:
            risk_score += 5

        # Учет команды как фактора снижения риска
        if metrics.team_size >= 5:
            risk_score += 10
        elif metrics.team_size >= 3:
            risk_score += 5

        # Учет экспертизы команды
        risk_score += metrics.team_expertise * 20

        return min(max(risk_score, 0), 100)  # Ограничиваем от 0 до 100

    def generate_recommendations(self, metrics: ProjectMetrics, scores: dict[str, float]) -> list[str]:
        """Генерация рекомендаций на основе анализа"""
        recommendations = []

        # Рекомендации по технологиям
        if scores["technology"] < 60:
            recommendations.append(
                "Рассмотрите обновление технологического стека для повышения конкурентоспособности")

        # Рекомендации по рынку
        if scores["market"] < 70:
            if metrics.competition_level > 0.7:
                recommendations.append(
                    "Высокий уровень конкуренции - рассмотрите дифференциацию продукта")
            if metrics.market_demand < 0.5:
                recommendations.append(
                    "Низкий спрос на рынке - пересмотрите ценность предложения")

        # Рекомендации по команде
        if scores["team"] < 65:
            if metrics.team_size < 3:
                recommendations.append(
                    "Увеличьте размер команды для повышения эффективности")
            if metrics.team_expertise < 0.6:
                recommendations.append(
                    "Инвестируйте в развитие экспертизы команды")

        # Рекомендации по инновациям
        if scores["innovation"] < 70:
            recommendations.append(
                "Повысьте уровень инноваций через исследования и внедрение новых технологий")

        # Рекомендации по масштабируемости
        if scores["scalability"] < 65:
            recommendations.append(
                "Оптимизируйте архитектуру для лучшей масштабируемости")

        # Рекомендации по рискам
        if scores["risk"] < 75:
            recommendations.append("Разработайте стратегию управления рисками")

        # Общие рекомендации
        if metrics.budget < 50000:
            recommendations.append(
                "Рассмотрите привлечение дополнительного финансирования")

        if metrics.timeline_months > 12:
            recommendations.append(
                "Оптимизируйте план реализации для сокращения сроков")

        return recommendations

    def analyze_project(self, metrics: ProjectMetrics) -> StrategicValueResult:
        """Провести полный анализ стратегической ценности проекта"""
        logger.info(f"Analyzing strategic value for project: {metrics.name}")

        # Расчет частичных оценок
        scores = {
            "technology": self.analyze_technology(metrics),
            "market": self.analyze_market(metrics),
            "team": self.analyze_team(metrics),
            "innovation": self.analyze_innovation(metrics),
            "scalability": self.analyze_scalability(metrics),
            "risk": self.analyze_risk(metrics),
        }

        # Расчет общей оценки
        weighted_sum = sum(
            scores[key] * self.weights[key.replace("_", "")] for key in scores)
        overall_score = weighted_sum

        # Генерация рекомендаций
        recommendations = self.generate_recommendations(metrics, scores)

        # Определение сильных и слабых сторон
        strengths = []
        weaknesses = []

        if scores["technology"] >= 80:
            strengths.append("Высокий уровень технологического совершенства")
        elif scores["technology"] < 60:
            weaknesses.append("Необходимо обновить технологический стек")

        if scores["market"] >= 80:
            strengths.append("Высокий рыночный потенциал")
        elif scores["market"] < 60:
            weaknesses.append("Низкий рыночный спрос или высокая конкуренция")

        if scores["team"] >= 80:
            strengths.append("Сильная и компетентная команда")
        elif scores["team"] < 60:
            weaknesses.append(
                "Необходимо усилить команду или повысить квалификацию")

        if scores["innovation"] >= 80:
            strengths.append("Высокий уровень инноваций")
        elif scores["innovation"] < 70:
            weaknesses.append("Нужно повысить уровень инноваций")

        if scores["scalability"] >= 80:
            strengths.append("Хорошая масштабируемость")
        elif scores["scalability"] < 60:
            weaknesses.append("Проблемы с масштабируемостью")

        if scores["risk"] >= 85:
            strengths.append("Низкий уровень рисков")
        elif scores["risk"] < 75:
            weaknesses.append("Высокий уровень рисков")

        # Определение уровня уверенности (на основе полноты данных)
        data_completeness = sum(
            1 for value in asdict(metrics).values() if value is not None and value != [] and value != "" and value != 0
        ) / len(asdict(metrics))
        # Максимум 95% из-за неопределенности
        confidence_level = min(data_completeness, 0.95)

        result = StrategicValueResult(
            project_name=metrics.name,
            overall_score=round(overall_score, 2),
            technology_score=round(scores["technology"], 2),
            market_score=round(scores["market"], 2),
            team_score=round(scores["team"], 2),
            innovation_score=round(scores["innovation"], 2),
            scalability_score=round(scores["scalability"], 2),
            risk_assessment=round(scores["risk"], 2),
            recommendations=recommendations,
            strengths=strengths,
            weaknesses=weaknesses,
            confidence_level=round(confidence_level, 2),
            analysis_timestamp=datetime.now().isoformat(),
            detailed_breakdown=scores,
        )

        logger.info(
            f"Analysis completed for {metrics.name}. Overall score: {result.overall_score}")
        return result


# HTML шаблон для главной страницы
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strategic Value Analyzer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select, textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Strategic Value Analyzer</h1>
        <form id="analysisForm">
            <div class="form-group">
                <label for="name">Название проекта:</label>
                <input type="text" id="name" name="name" required>
            </div>

            <div class="form-group">
                <label for="description">Описание проекта:</label>
                <textarea id="description" name="description"></textarea>
            </div>

            <div class="form-group">
                <label for="team_size">Размер команды:</label>
                <input type="number" id="team_size" name="team_size" min="1" required>
            </div>

            <div class="form-group">
                <label for="budget">Бюджет ($):</label>
                <input type="number" id="budget" name="budget" min="0" step="1000" required>
            </div>

            <div class="form-group">
                <label for="timeline_months">Срок реализации (месяцы):</label>
                <input type="number" id="timeline_months" name="timeline_months" min="1" required>
            </div>

            <div class="form-group">
                <label for="tech_stack">Технологический стек (через запятую):</label>
                <input type="text" id="tech_stack" name="tech_stack">
            </div>

            <div class="form-group">
                <label for="market_demand">Рыночный спрос (0-1):</label>
                <input type="number" id="market_demand" name="market_demand" min="0" max="1" step="0.01" required>
            </div>

            <div class="form-group">
                <label for="innovation_level">Уровень инноваций (0-1):</label>
                <input type="number" id="innovation_level" name="innovation_level" min="0" max="1" step="0.01" required>
            </div>

            <div class="form-group">
                <label for="scalability">Масштабируемость (0-1):</label>
                <input type="number" id="scalability" name="scalability" min="0" max="1" step="0.01" required>
            </div>

            <div class="form-group">
                <label for="competition_level">Уровень конкуренции (0-1):</label>
                <input type="number" id="competition_level" name="competition_level" min="0" max="1" step="0.01" required>
            </div>

            <div class="form-group">
                <label for="risk_factor">Фактор риска (0-1):</label>
                <input type="number" id="risk_factor" name="risk_factor" min="0" max="1" step="0.01" required>
            </div>

            <div class="form-group">
                <label for="team_expertise">Экспертиза команды (0-1):</label>
                <input type="number" id="team_expertise" name="team_expertise" min="0" max="1" step="0.01" required>
            </div>

            <div class="form-group">
                <label for="project_type">Тип проекта:</label>
                <select id="project_type" name="project_type" required>
                    <option value="startup">Стартап</option>
                    <option value="enterprise">Корпоративный</option>
                    <option value="open_source">Open Source</option>
                    <option value="research">Исследовательский</option>
                    <option value="commercial">Коммерческий</option>
                </select>
            </div>

            <div class="form-group">
                <label for="dependencies">Зависимости (через запятую):</label>
                <input type="text" id="dependencies" name="dependencies">
            </div>

            <div class="form-group">
                <label for="target_users">Целевая аудитория (кол-во пользователей):</label>
                <input type="number" id="target_users" name="target_users" min="0" required>
            </div>

            <div class="form-group">
                <label for="revenue_potential">Потенциал выручки ($):</label>
                <input type="number" id="revenue_potential" name="revenue_potential" min="0" step="1000" required>
            </div>

            <button type="submit">Анализировать проект</button>
        </form>

        <div id="results" class="results" style="display:none;"></div>
    </div>

    <script>
        document.getElementById('analysisForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            // Преобразование числовых значений
            data.team_size = parseInt(data.team_size);
            data.budget = parseFloat(data.budget);
            data.timeline_months = parseInt(data.timeline_months);
            data.market_demand = parseFloat(data.market_demand);
            data.innovation_level = parseFloat(data.innovation_level);
            data.scalability = parseFloat(data.scalability);
            data.competition_level = parseFloat(data.competition_level);
            data.risk_factor = parseFloat(data.risk_factor);
            data.team_expertise = parseFloat(data.team_expertise);
            data.target_users = parseInt(data.target_users);
            data.revenue_potential = parseFloat(data.revenue_potential);

            // Преобразование массивов
            if(data.tech_stack) data.tech_stack = data.tech_stack.split(',').map(s => s.trim());
            if(data.dependencies) data.dependencies = data.dependencies.split(',').map(s => s.trim());

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if(response.ok) {
                    displayResults(result);
                } else {
                    alert('Ошибка: ' + result.error);
                }
            } catch (error) {
                alert('Произошла ошибка: ' + error.message);
            }
        });

        function displayResults(result) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <h2>Результаты анализа: ${result.project_name}</h2>
                <p><strong>Общий балл:</strong> ${result.overall_score}/100</p>
                <p><strong>Уверенность:</strong> ${(result.confidence_level * 100).toFixed(1)}%</p>

                <h3>Детализация:</h3>
                <ul>
                    <li>Технологии: ${result.technology_score}/100</li>
                    <li>Рынок: ${result.market_score}/100</li>
                    <li>Команда: ${result.team_score}/100</li>
                    <li>Инновации: ${result.innovation_score}/100</li>
                    <li>Масштабируемость: ${result.scalability_score}/100</li>
                    <li>Риски: ${result.risk_assessment}/100</li>
                </ul>

                <h3>Сильные стороны:</h3>
                <ul>
                    ${result.strengths.map(s => '<li>' + s + '</li>').join('')}
                </ul>

                <h3>Слабые стороны:</h3>
                <ul>
                    ${result.weaknesses.map(w => '<li>' + w + '</li>').join('')}
                </ul>

                <h3>Рекомендации:</h3>
                <ul>
                    ${result.recommendations.map(r => '<li>' + r + '</li>').join('')}
                </ul>
            `;
            resultsDiv.style.display = 'block';
        }
    </script>
</body>
</html>
"""


# FastAPI приложение
app = FastAPI(title="Strategic Value Analyzer", version="2.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальная переменная для агента
agent: AutonomousCognitiveAgent | None = None


@app.on_event("startup")
async def startup_event():
    """Инициализация агента при запуске приложения"""
    global agent
    logger.info("🚀 Запуск Strategic Value Analyzer...")

    # Создаем экземпляр enterprise агента
    agent = AutonomousCognitiveAgent()

    # Запускаем агента в фоновом режиме
    agent.start(background=True)

    logger.info("✅ Strategic Value Analyzer запущен")


@app.on_event("shutdown")
async def shutdown_event():
    """Остановка агента при выключении приложения"""
    global agent
    if agent:
        agent.stop()
        logger.info("🛑 Strategic Value Analyzer остановлен")


class TaskRequest(BaseModel):
    """Модель запроса задачи"""
    task: str
    auto_approve: bool = False


class ScanRequest(BaseModel):
    """Модель запроса сканирования"""
    mode: str = "auto"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница"""
    from fastapi.responses import HTMLResponse

    # Since we're using a string template, we'll return the HTML directly
    return HTMLResponse(content=HTML_TEMPLATE)


@app.post("/analyze")
async def analyze(request: Request):
    """Анализ проекта"""
    try:
        data = await request.json()

        # Валидация данных
        required_fields = [
            "name",
            "team_size",
            "budget",
            "timeline_months",
            "market_demand",
            "innovation_level",
            "scalability",
            "competition_level",
            "risk_factor",
            "team_expertise",
            "project_type",
            "target_users",
            "revenue_potential",
        ]

        for field in required_fields:
            if field not in data:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Поле {field} обязательно"}
                )

        # Создание объекта метрик
        metrics = ProjectMetrics(
            name=data["name"],
            description=data.get("description", ""),
            team_size=data["team_size"],
            budget=data["budget"],
            timeline_months=data["timeline_months"],
            tech_stack=data.get("tech_stack", []),
            market_demand=data["market_demand"],
            innovation_level=data["innovation_level"],
            scalability=data["scalability"],
            competition_level=data["competition_level"],
            risk_factor=data["risk_factor"],
            team_expertise=data["team_expertise"],
            project_type=ProjectType(data["project_type"]),
            dependencies=data.get("dependencies", []),
            target_users=data["target_users"],
            revenue_potential=data["revenue_potential"],
        )

        # Создание анализатора и выполнение анализа
        analyzer = StrategicValueAnalyzer()
        result = analyzer.analyze_project(metrics)

        return JSONResponse(content=asdict(result))

    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Запуск сервера"""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    # Запускаем сервер
    print("🚀 Запуск Strategic Value Analyzer Web Interface...")
    print("🌐 Сервер будет доступен по адресу: http://localhost:8000")
    print("📊 API документация: http://localhost:8000/docs")
    print("-" * 50)

    run_server()

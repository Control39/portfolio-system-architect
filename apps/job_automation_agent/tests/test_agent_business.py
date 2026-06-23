"""
Тесты для бизнес-логики Job Automation Agent.

Test Coverage:
- Job search operations
- Resume parsing and matching
- Application tracking
- Agent orchestration
- Edge cases and validation
"""

import sys
from pathlib import Path


# Добавляем корень проекта и apps в путь
ROOT_DIR = Path(__file__).parent.parent.parent
SRC_DIR = ROOT_DIR / "apps" / "job-automation-agent"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.analysis import JobAnalyzer, MatchScore  # noqa: E402
from src.resume import ResumeParser  # noqa: E402


class TestResumeParser:
    """Тесты парсинга резюме."""

    def test_parse_resume_text(self):
        """Тест парсинга текста резюме."""
        parser = ResumeParser()

        resume_text = """
        Иван Иванов
        Senior Python Developer

        Опыт работы:
        - Company A, 2020-2024: Python разработчик
        - Company B, 2018-2020: Junior Developer

        Навыки: Python, FastAPI, Docker, PostgreSQL
        """

        result = parser.parse(resume_text)

        assert result.name == "Иван Иванов"
        assert result.position == "Senior Python Developer"
        assert len(result.skills) > 0
        assert "Python" in result.skills

    def test_parse_empty_resume(self):
        """Тест парсинга пустого резюме."""
        parser = ResumeParser()
        result = parser.parse("")

        assert result.name is None
        assert result.position is None
        assert result.skills is not None
        assert len(result.skills) == 0

    def test_extract_skills(self):
        """Тест извлечения навыков."""
        parser = ResumeParser()

        text = "Python, FastAPI, Docker, Kubernetes, PostgreSQL"
        skills = parser.extract_skills(text)

        assert "Python" in skills
        assert "FastAPI" in skills
        assert "Docker" in skills

    def test_extract_skills_from_list(self):
        """Тест извлечения навыков из списка."""
        parser = ResumeParser()

        skills_list = ["Python", "JavaScript", "Go"]
        result = parser.extract_skills_from_list(skills_list)

        assert len(result) == 3
        assert "Python" in result


class TestJobAnalyzer:
    """Тесты анализа вакансий."""

    def test_analyze_single_job(self):
        """Тест анализа одной вакансии."""
        analyzer = JobAnalyzer()

        job = {
            "id": "123",
            "name": "Senior Python Developer",
            "employer": "Tech Company",
            "salary": {"from": 200000, "to": 300000},
            "url": "https://example.com",
        }

        analysis = analyzer.analyze_job(job)

        assert analysis.job_id == "123"
        assert analysis.position == "Senior Python Developer"
        assert analysis.employer == "Tech Company"

    def test_analyze_empty_job(self):
        """Тест анализа пустой вакансии."""
        analyzer = JobAnalyzer()
        analysis = analyzer.analyze_job({})

        assert analysis.job_id is None
        assert analysis.position is None

    def test_match_resume_to_job(self):
        """Тест подбора резюме к вакансии."""
        analyzer = JobAnalyzer()

        resume = {
            "skills": ["Python", "FastAPI", "Docker"],
            "experience_years": 5,
        }

        job = {
            "id": "job-1",
            "name": "Python Developer",
            "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        }

        score = analyzer.match_resume_to_job(resume, job)

        assert isinstance(score, MatchScore)
        assert score.match_percentage >= 0
        assert score.match_percentage <= 100

    def test_match_percentage_calculation(self):
        """Тест расчёта процента совпадения."""
        analyzer = JobAnalyzer()

        # Полное совпадение
        resume = {"skills": ["Python", "FastAPI"]}
        job = {"id": "1", "name": "Dev", "required_skills": ["Python", "FastAPI"]}

        score = analyzer.match_resume_to_job(resume, job)
        assert score.match_percentage == 100

    def test_search_all_jobs_mock(self):
        """Тест поиска всех вакансий (mock)."""

        # Тест с заглушками
        async def mock_search():
            return [
                {"id": "1", "name": "Job 1", "employer": "Company A"},
                {"id": "2", "name": "Job 2", "employer": "Company B"},
            ]

        # Результат должен быть списком
        result = asyncio_mock_wrapper(mock_search)
        assert isinstance(result, list)
        assert len(result) == 2


class TestAgentOrchestration:
    """Тесты оркестрации агента."""

    def test_create_agent_instance(self):
        """Тест создания экземпляра агента."""
        from src.core.orchestrator import JobAgentOrchestrator

        orchestrator = JobAgentOrchestrator()

        assert orchestrator is not None
        assert orchestrator.is_running is False

    def test_start_agent(self):
        """Тест запуска агента."""
        from src.core.orchestrator import JobAgentOrchestrator

        orchestrator = JobAgentOrchestrator()
        orchestrator.start()

        assert orchestrator.is_running is True

    def test_stop_agent(self):
        """Тест остановки агента."""
        from src.core.orchestrator import JobAgentOrchestrator

        orchestrator = JobAgentOrchestrator()
        orchestrator.start()
        orchestrator.stop()

        assert orchestrator.is_running is False

    def test_agent_search_workflow(self):
        """Тест рабочего процесса поиска."""
        from src.core.orchestrator import JobAgentOrchestrator

        orchestrator = JobAgentOrchestrator()

        # Эмуляция рабочего процесса
        results = orchestrator.search_jobs(query="Python")

        assert isinstance(results, list)


class TestAnalysisModule:
    """Тесты модуля анализа."""

    def test_compute_match_score(self):
        """Тест вычисления балла совпадения."""
        from src.analysis import compute_match_score

        resume_skills = {"Python", "FastAPI", "Docker"}
        required_skills = {"Python", "FastAPI", "PostgreSQL"}

        score = compute_match_score(resume_skills, required_skills)

        assert 0 <= score <= 100

    def test_compute_match_score_empty(self):
        """Тест вычисления балла для пустых наборов."""
        from src.analysis import compute_match_score

        # Пустое резюме
        score1 = compute_match_score(set(), {"Python"})
        assert score1 == 0

        # Пустые требования
        score2 = compute_match_score({"Python"}, set())
        assert score2 == 100  # Все требуемые (пустые) совпадают

    def test_analyze_market_trends(self):
        """Тест анализа рыночных трендов."""
        analyzer = JobAnalyzer()

        jobs = [
            {"id": "1", "name": "Python Developer", "salary": {"from": 150000}},
            {"id": "2", "name": "Python Developer", "salary": {"from": 200000}},
            {"id": "3", "name": "Python Developer", "salary": {"from": 180000}},
        ]

        trends = analyzer.analyze_market_trends(jobs)

        assert trends is not None
        assert trends["average_salary"] is not None


class TestEdgeCases:
    """Тесты граничных случаев."""

    def test_resume_with_no_skills(self):
        """Тест резюме без навыков."""
        parser = ResumeParser()
        result = parser.parse("Иван Иванов\nDeveloper")

        assert result.name == "Иван Иванов"
        assert len(result.skills) == 0

    def test_job_with_no_salary(self):
        """Тест вакансии без зарплаты."""
        analyzer = JobAnalyzer()

        job = {
            "id": "123",
            "name": "Developer",
            "salary": None,
        }

        analysis = analyzer.analyze_job(job)

        assert analysis.job_id == "123"
        assert analysis.salary_from is None

    def test_unicode_in_resume(self):
        """Тест Unicode символов в резюме."""
        parser = ResumeParser()

        resume_text = """
        Иван Иванов
        Разработчик 🚀

        Навыки: Python, JavaScript, Go
        """

        result = parser.parse(resume_text)

        assert "Иван" in result.name
        assert "Python" in result.skills

    def test_special_characters_in_job_name(self):
        """Тест специальных символов в названии вакансии."""
        analyzer = JobAnalyzer()

        job = {
            "id": "123",
            "name": "Python Developer (Senior) - $150k+",
            "employer": "Tech & Co.",
        }

        analysis = analyzer.analyze_job(job)

        assert "Python" in analysis.position

    def test_large_job_list(self):
        """Тест большого списка вакансий."""
        analyzer = JobAnalyzer()

        jobs = [{"id": str(i), "name": f"Job {i}"} for i in range(1000)]

        results = [analyzer.analyze_job(job) for job in jobs]

        assert len(results) == 1000


def asyncio_mock_wrapper(async_func):
    """Вспомогательная функция для тестирования async."""
    import asyncio

    return asyncio.run(async_func())

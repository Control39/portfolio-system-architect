"""
Reporter for generating analysis reports.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Any

from .maturity_scoring import MaturityScorer

logger = logging.getLogger(__name__)


class ReporterError(Exception):
    """Custom exception for Reporter errors."""

    pass


class Reporter:
    """Generates reports from analysis results."""

    # HTML template as a constant
    _HTML_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assistant Orchestrator Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #f5f7fa; color: #333; line-height: 1.6; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .subtitle { font-size: 1.2rem; opacity: 0.9; }
        .timestamp { margin-top: 1rem; font-size: 0.9rem; opacity: 0.8; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 2rem; }
        .card { background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .card h2 { color: #4a5568; margin-bottom: 1rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 0.8rem; }
        .metric-label { color: #718096; }
        .metric-value { font-weight: bold; color: #2d3748; }
        .score-container { text-align: center; padding: 2rem; }
        .score-circle { width: 150px; height: 150px; border-radius: 50%; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center; background: conic-gradient(#10b981 ${percentage}%, #e2e8f0 0%); }
        .score-value { font-size: 3rem; color: white; font-weight: bold; }
        .score-label { font-size: 1.2rem; color: #4a5568; }
        .recommendations { margin-top: 2rem; }
        .recommendation { background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin-bottom: 1rem; border-radius: 0 5px 5px 0; }
        .recommendation h3 { color: #856404; margin-bottom: 0.5rem; }
        .recommendation p { color: #856404; }
        footer { margin-top: 3rem; text-align: center; color: #718096; font-size: 0.9rem; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-info { background: #dbeafe; color: #1e40af; }
        .badge-danger { background: #fee2e2; color: #991b1b; }
        @media (max-width: 768px) {
            .dashboard { grid-template-columns: 1fr; }
            header { padding: 1rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Assistant Orchestrator Dashboard</h1>
            <div class="subtitle">Анализ зрелости архитектуры проекта</div>
            <div class="timestamp">Отчёт сгенерирован: ${timestamp}</div>
        </header>

        <div class="dashboard">
            <div class="card">
                <h2>🏗️ Микросервисы</h2>
                <div class="metric">
                    <span class="metric-label">Всего сервисов</span>
                    <span class="metric-value">${total_services}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Production-ready</span>
                    <span class="metric-value">${prod_ready_services}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">С тестами</span>
                    <span class="metric-value">${services_with_tests}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">С Docker</span>
                    <span class="metric-value">${services_with_docker}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Docker Compose</span>
                    <span class="metric-value">${has_docker_compose}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Kubernetes</span>
                    <span class="metric-value">${has_kubernetes}</span>
                </div>
            </div>

            <div class="card">
                <h2>🎯 Навыки</h2>
                <div class="metric">
                    <span class="metric-label">Маркеров</span>
                    <span class="metric-value">${skill_markers_count}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Категорий</span>
                    <span class="metric-value">${skill_categories_count}</span>
                </div>
            </div>

            <div class="card">
                <h2>📈 Активность</h2>
                <div class="metric">
                    <span class="metric-label">Всего коммитов</span>
                    <span class="metric-value">${total_commits}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Контрибьюторов</span>
                    <span class="metric-value">${contributors_count}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Активность (30 дней)</span>
                    <span class="metric-value">${recent_activity} коммитов</span>
                </div>
            </div>

            <div class="card">
                <h2>📚 Документация</h2>
                <div class="metric">
                    <span class="metric-label">Архитектурных документов</span>
                    <span class="metric-value">${architecture_docs_count}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Зависимостей</span>
                    <span class="metric-value">${dependencies_count}</span>
                </div>
            </div>

            <div class="card score-container">
                <h2>🎯 Уровень зрелости</h2>
                <div class="score-circle" style="background: conic-gradient(#10b981 ${percentage}%, #e2e8f0 0%);">
                    <div class="score-value">${maturity_score}</div>
                </div>
                <div class="score-label">из 5.0</div>
                <div style="margin-top: 1rem;">
                    ${maturity_badge}
                </div>
            </div>
        </div>

        <div class="card">
            <h2>💡 Рекомендации</h2>
            <div class="recommendations">
                ${recommendations_html}
            </div>
        </div>

        <footer>
            <p>Сгенерировано Assistant Orchestrator v1.0.0</p>
            <p>Для подробного анализа запустите: <code>python -m assistant_orchestrator --format json</code></p>
        </footer>
    </div>
</body>
</html>
""")

    def __init__(self, analysis_result: Any):
        """
        Initialize reporter with analysis result.

        Args:
            analysis_result: Analysis result object or dict

        Raises:
            ReporterError: If analysis_result is invalid
        """
        self.result = analysis_result

        # Extract data safely
        try:
            data = self._extract_dict(analysis_result)
            self.scorer = MaturityScorer(data)
        except Exception as e:
            logger.error(f"Failed to initialize MaturityScorer: {e}")
            raise ReporterError(f"Invalid analysis result: {e}")

    def _extract_dict(self, obj: Any) -> dict[str, Any]:
        """Safely extract dictionary from object."""
        if hasattr(obj, "dict"):
            try:
                return obj.dict()
            except Exception as e:
                logger.warning(f"Failed to call dict(): {e}")

        if isinstance(obj, dict):
            return obj

        if hasattr(obj, "__dict__"):
            return obj.__dict__

        raise ReporterError(f"Cannot convert {type(obj)} to dict")

    def _safe_get(self, path: str, default: Any = None) -> Any:
        """
        Safely get value from nested structure using dot notation.

        Args:
            path: Dot-separated path (e.g., 'microservices.services')
            default: Default value if path not found

        Returns:
            Value at path or default
        """
        try:
            current = self.result

            # If result has dict method, use it for consistent access
            if hasattr(current, "dict"):
                current = current.dict()

            for key in path.split("."):
                if isinstance(current, dict):
                    current = current.get(key, default)
                elif hasattr(current, key):
                    current = getattr(current, key)
                else:
                    return default

                if current is None:
                    return default

            return current
        except Exception as e:
            logger.debug(f"Error accessing {path}: {e}")
            return default

    def save(self, path: Path) -> None:
        """
        Save report to file in appropriate format.

        Args:
            path: Path to save report

        Raises:
            ReporterError: If saving fails
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            if path.suffix == ".json":
                self._save_json(path)
            elif path.suffix == ".txt":
                self._save_text(path)
            elif path.suffix == ".html":
                self._save_html(path)
            else:
                # Default to JSON with warning
                json_path = path.with_suffix(".json")
                self._save_json(json_path)
                logger.warning(f"Unknown format {path.suffix}, saved as JSON to {json_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise ReporterError(f"Cannot save report to {path}: {e}")

    def _save_json(self, path: Path) -> None:
        """Save as JSON file."""
        try:
            data = self._extract_dict(self.result)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_serializer)

            logger.info(f"JSON report saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save JSON report: {e}")
            raise ReporterError(f"JSON save failed: {e}")

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """Custom JSON serializer for non-serializable objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        if hasattr(obj, "dict"):
            return obj.dict()
        try:
            return str(obj)
        except Exception:
            return f"<non-serializable: {type(obj).__name__}>"

    def _save_text(self, path: Path) -> None:
        """Save as text report."""
        try:
            report_content = self._generate_text_report()
            with open(path, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"Text report saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save text report: {e}")
            raise ReporterError(f"Text save failed: {e}")

    def _save_html(self, path: Path) -> None:
        """Save as HTML dashboard."""
        try:
            html_content = self._generate_html_report()
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML report saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save HTML report: {e}")
            logger.warning("Falling back to text report")
            self._save_text(path.with_suffix(".txt"))
            raise ReporterError(f"HTML save failed, fallback to text: {e}")

    def _generate_text_report(self) -> str:
        """Generate human-readable text report."""
        try:
            maturity_score = self.scorer.calculate_score()
            recommendations = self.scorer.get_recommendations()
        except Exception as e:
            logger.error(f"Error calculating maturity: {e}")
            maturity_score = 0.0
            recommendations = []

        # Safe data extraction
        services = self._safe_get("microservices.services", [])
        total_services = len(services) if isinstance(services, list) else 0

        prod_ready = sum(1 for s in services if isinstance(s, dict) and s.get("is_production_ready"))
        services_with_tests = sum(1 for s in services if isinstance(s, dict) and s.get("has_tests"))
        services_with_docker = sum(1 for s in services if isinstance(s, dict) and s.get("has_docker"))

        skill_categories = self._safe_get("skill_markers.categories", [])
        skill_categories_count = len(skill_categories) if isinstance(skill_categories, list) else 0

        skill_total = self._safe_get("skill_markers.total_count", 0)
        arch_docs = self._safe_get("architecture_docs", [])
        arch_docs_count = len(arch_docs) if isinstance(arch_docs, list) else 0

        total_commits = self._safe_get("git_stats.total_commits", 0)
        recent_activity = self._safe_get("git_stats.recent_activity_days", 0)
        contributors = self._safe_get("git_stats.contributors", [])
        contributors_count = len(contributors) if isinstance(contributors, list) else 0

        dependencies = self._safe_get("dependencies", [])
        dependencies_count = len(dependencies) if isinstance(dependencies, list) else 0

        has_docker_compose = "Да" if self._safe_get("microservices.has_docker_compose", False) else "Нет"
        has_kubernetes = "Да" if self._safe_get("microservices.has_kubernetes", False) else "Нет"

        timestamp = self._safe_get("timestamp", datetime.now().isoformat())

        lines = [
            "=" * 60,
            "📊 ОТЧЕТ АНАЛИЗА ЭКОСИСТЕМЫ",
            "=" * 60,
            f"Время: {timestamp}",
            "",
            "🏗️ Микросервисы",
            f"  • Всего: {total_services}",
            f"  • Production-ready: {prod_ready}",
            f"  • С тестами: {services_with_tests}",
            f"  • С Docker: {services_with_docker}",
            "",
            "🎯 Навыки",
            f"  • Категорий: {skill_categories_count}",
            f"  • Маркеров: {skill_total}",
            "",
            "📚 Документация",
            f"  • Архитектурных документов: {arch_docs_count}",
            "",
            "📈 Git статистика",
            f"  • Коммитов: {total_commits}",
            f"  • Активность (последние 30 дней): {recent_activity} коммитов",
            f"  • Контрибьюторов: {contributors_count}",
            "",
            "🔗 Зависимости",
            f"  • Сервисов: {dependencies_count}",
            f"  • Docker Compose: {has_docker_compose}",
            f"  • Kubernetes: {has_kubernetes}",
        ]

        # Maturity score
        lines.extend(
            [
                "",
                "=" * 60,
                "🎯 ОЦЕНКА ЗРЕЛОСТИ АРХИТЕКТУРЫ",
                "=" * 60,
                f"Уровень зрелости: {maturity_score:.1f} / 5.0",
            ]
        )

        # Score interpretation
        if maturity_score >= 4.0:
            lines.append("✅ Высокий уровень зрелости — архитектура соответствует лучшим практикам")
        elif maturity_score >= 3.0:
            lines.append("⚠️  Средний уровень зрелости — есть потенциал для улучшений")
        elif maturity_score >= 2.0:
            lines.append("📉 Базовый уровень — требуется работа над архитектурой")
        else:
            lines.append("🚨 Начальный уровень — необходимы значительные улучшения")

        # Recommendations
        if recommendations and isinstance(recommendations, list):
            lines.extend(["", "💡 РЕКОМЕНДАЦИИ ДЛЯ УЛУЧШЕНИЯ:"])
            for i, rec in enumerate(recommendations[:5], 1):
                if isinstance(rec, dict):
                    lines.append(f"  {i}. {rec.get('title', 'Нет заголовка')}")
                    lines.append(f"     📝 {rec.get('description', 'Нет описания')}")
                    lines.append(f"     🎯 Потенциальный рост: +{rec.get('potential_gain', 0)} баллов")
                    lines.append(f"     🛠️  Действие: {rec.get('action', 'Нет действия')}")
                    lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _generate_html_report(self) -> str:
        """Generate HTML dashboard report."""
        try:
            maturity_score = self.scorer.calculate_score()
            recommendations = self.scorer.get_recommendations()
        except Exception as e:
            logger.error(f"Error calculating maturity: {e}")
            maturity_score = 0.0
            recommendations = []

        # Calculate percentage for circle
        percentage = (maturity_score / 5.0) * 100

        # Determine badge
        if maturity_score >= 4.0:
            maturity_badge = "<span class='badge badge-success'>Высокий уровень</span>"
        elif maturity_score >= 3.0:
            maturity_badge = "<span class='badge badge-warning'>Средний уровень</span>"
        elif maturity_score >= 2.0:
            maturity_badge = "<span class='badge badge-info'>Базовый уровень</span>"
        else:
            maturity_badge = "<span class='badge badge-danger'>Начальный уровень</span>"

        # Safe data extraction
        services = self._safe_get("microservices.services", [])
        total_services = len(services) if isinstance(services, list) else 0

        prod_ready = sum(1 for s in services if isinstance(s, dict) and s.get("is_production_ready"))
        services_with_tests = sum(1 for s in services if isinstance(s, dict) and s.get("has_tests"))
        services_with_docker = sum(1 for s in services if isinstance(s, dict) and s.get("has_docker"))

        skill_categories = self._safe_get("skill_markers.categories", [])
        skill_categories_count = len(skill_categories) if isinstance(skill_categories, list) else 0
        skill_markers_count = self._safe_get("skill_markers.total_count", 0)

        arch_docs = self._safe_get("architecture_docs", [])
        arch_docs_count = len(arch_docs) if isinstance(arch_docs, list) else 0

        total_commits = self._safe_get("git_stats.total_commits", 0)
        recent_activity = self._safe_get("git_stats.recent_activity_days", 0)
        contributors = self._safe_get("git_stats.contributors", [])
        contributors_count = len(contributors) if isinstance(contributors, list) else 0

        dependencies = self._safe_get("dependencies", [])
        dependencies_count = len(dependencies) if isinstance(dependencies, list) else 0

        has_docker_compose = "Да" if self._safe_get("microservices.has_docker_compose", False) else "Нет"
        has_kubernetes = "Да" if self._safe_get("microservices.has_kubernetes", False) else "Нет"

        timestamp = self._safe_get("timestamp", datetime.now().isoformat())

        # Generate recommendations HTML
        recommendations_html = ""
        if recommendations and isinstance(recommendations, list):
            for rec in recommendations[:5]:
                if isinstance(rec, dict):
                    recommendations_html += f"""
                <div class="recommendation">
                    <h3>{self._escape_html(rec.get("title", "Нет заголовка"))}</h3>
                    <p>{self._escape_html(rec.get("description", "Нет описания"))}</p>
                    <p><strong>Потенциальный рост:</strong> +{rec.get("potential_gain", 0)} баллов</p>
                    <p><strong>Действие:</strong> {self._escape_html(rec.get("action", "Нет действия"))}</p>
                </div>
"""
        else:
            recommendations_html = """
                <div class="recommendation">
                    <h3>Отличная работа!</h3>
                    <p>Проект демонстрирует высокую зрелость архитектуры. Продолжайте в том же духе!</p>
                </div>
"""

        # Fill template
        return self._HTML_TEMPLATE.substitute(
            percentage=f"{percentage:.1f}",
            maturity_score=f"{maturity_score:.1f}",
            maturity_badge=maturity_badge,
            timestamp=self._escape_html(timestamp),
            total_services=total_services,
            prod_ready_services=prod_ready,
            services_with_tests=services_with_tests,
            services_with_docker=services_with_docker,
            has_docker_compose=has_docker_compose,
            has_kubernetes=has_kubernetes,
            skill_markers_count=skill_markers_count,
            skill_categories_count=skill_categories_count,
            total_commits=total_commits,
            contributors_count=contributors_count,
            recent_activity=recent_activity,
            architecture_docs_count=arch_docs_count,
            dependencies_count=dependencies_count,
            recommendations_html=recommendations_html,
        )

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        if not isinstance(text, str):
            text = str(text)

        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
        }
        return "".join(html_escape_table.get(c, c) for c in text)


# Convenience function for quick reporting
def generate_report(analysis_result: Any, output_path: Path, format: str = "html") -> None:
    """
    Generate report from analysis result.

    Args:
        analysis_result: Analysis result object
        output_path: Path to save report
        format: Report format ('json', 'txt', 'html')

    Raises:
        ReporterError: If report generation fails
    """
    reporter = Reporter(analysis_result)

    # Ensure correct extension
    if not output_path.suffix:
        output_path = output_path.with_suffix(f".{format}")

    reporter.save(output_path)

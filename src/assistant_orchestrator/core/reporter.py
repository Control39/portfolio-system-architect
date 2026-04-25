"""Reporter for generating analysis reports.
"""
import json
import logging
from pathlib import Path
from typing import Any

from .maturity_scoring import MaturityScorer

logger = logging.getLogger(__name__)


class Reporter:
    """Generates reports from analysis results."""

    def __init__(self, analysis_result: Any):
        self.result = analysis_result
        self.scorer = MaturityScorer(analysis_result.dict())

    def save(self, path: Path):
        """Save report to file in appropriate format."""
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.suffix == ".json":
            self._save_json(path)
        elif path.suffix == ".txt":
            self._save_text(path)
        elif path.suffix == ".html":
            self._save_html(path)
        else:
            # Default to JSON
            self._save_json(path.with_suffix(".json"))
            logger.warning(f"Unknown format {path.suffix}, saved as JSON")

    def _save_json(self, path: Path):
        """Save as JSON file."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.result.dict(), f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"JSON report saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save JSON report: {e}")
            raise

    def _save_text(self, path: Path):
        """Save as text report."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._generate_text_report())
            logger.info(f"Text report saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save text report: {e}")
            raise

    def _save_html(self, path: Path):
        """Save as HTML dashboard."""
        try:
            html_content = self._generate_html_report()
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML report saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save HTML report: {e}")
            # Fallback to text
            self._save_text(path.with_suffix(".txt"))

    def _generate_text_report(self) -> str:
        """Generate human-readable text report."""
        maturity_score = self.scorer.calculate_score()
        recommendations = self.scorer.get_recommendations()

        lines = [
            "=" * 60,
            "📊 ОТЧЕТ АНАЛИЗА ЭКОСИСТЕМЫ",
            "=" * 60,
            f"Время: {self.result.timestamp}",
            "",
            "🏗️ Микросервисы",
            f"  • Всего: {len(self.result.microservices.get('services', []))}",
            f"  • Production-ready: {len([s for s in self.result.microservices.get('services', []) if s.get('is_production_ready')])}",
            f"  • С тестами: {sum(1 for s in self.result.microservices.get('services', []) if s.get('has_tests'))}",
            f"  • С Docker: {sum(1 for s in self.result.microservices.get('services', []) if s.get('has_docker'))}",
            "",
            "🎯 Навыки",
            f"  • Категорий: {len(self.result.skill_markers.get('categories', []))}",
            f"  • Маркеров: {self.result.skill_markers.get('total_count', 0)}",
            "",
            "📚 Документация",
            f"  • Архитектурных документов: {len(self.result.architecture_docs)}",
            "",
            "📈 Git статистика",
            f"  • Коммитов: {self.result.git_stats.get('total_commits', 0)}",
            f"  • Активность (последние 30 дней): {self.result.git_stats.get('recent_activity_days', 0)} коммитов",
            f"  • Контрибьюторов: {len(self.result.git_stats.get('contributors', []))}",
            "",
            "🔗 Зависимости",
            f"  • Сервисов: {len(self.result.dependencies)}",
            f"  • Docker Compose: {'Да' if self.result.microservices.get('has_docker_compose') else 'Нет'}",
            f"  • Kubernetes: {'Да' if self.result.microservices.get('has_kubernetes') else 'Нет'}",
        ]

        # Maturity score
        lines.extend([
            "",
            "=" * 60,
            "🎯 ОЦЕНКА ЗРЕЛОСТИ АРХИТЕКТУРЫ",
            "=" * 60,
            f"Уровень зрелости: {maturity_score:.1f} / 5.0",
        ])

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
        if recommendations:
            lines.extend([
                "",
                "💡 РЕКОМЕНДАЦИИ ДЛЯ УЛУЧШЕНИЯ:",
            ])
            for i, rec in enumerate(recommendations[:5], 1):
                lines.append(f"  {i}. {rec['title']}")
                lines.append(f"     📝 {rec['description']}")
                lines.append(f"     🎯 Потенциальный рост: +{rec['potential_gain']} баллов")
                lines.append(f"     🛠️  Действие: {rec['action']}")
                lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _generate_html_report(self) -> str:
        """Generate HTML dashboard report."""
        maturity_score = self.scorer.calculate_score()
        recommendations = self.scorer.get_recommendations()

        # Simple HTML template with inline CSS
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assistant Orchestrator Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        body {{ background: #f5f7fa; color: #333; line-height: 1.6; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .subtitle {{ font-size: 1.2rem; opacity: 0.9; }}
        .timestamp {{ margin-top: 1rem; font-size: 0.9rem; opacity: 0.8; }}
        .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 2rem; }}
        .card {{ background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .card h2 {{ color: #4a5568; margin-bottom: 1rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; }}
        .metric {{ display: flex; justify-content: space-between; margin-bottom: 0.8rem; }}
        .metric-label {{ color: #718096; }}
        .metric-value {{ font-weight: bold; color: #2d3748; }}
        .score-container {{ text-align: center; padding: 2rem; }}
        .score-circle {{ width: 150px; height: 150px; border-radius: 50%; background: conic-gradient(#10b981 {maturity_score/5*100}%, #e2e8f0 0%); margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center; }}
        .score-value {{ font-size: 3rem; color: white; font-weight: bold; }}
        .score-label {{ font-size: 1.2rem; color: #4a5568; }}
        .recommendations {{ margin-top: 2rem; }}
        .recommendation {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin-bottom: 1rem; border-radius: 0 5px 5px 0; }}
        .recommendation h3 {{ color: #856404; margin-bottom: 0.5rem; }}
        .recommendation p {{ color: #856404; }}
        footer {{ margin-top: 3rem; text-align: center; color: #718096; font-size: 0.9rem; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }}
        .badge-success {{ background: #d1fae5; color: #065f46; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .badge-info {{ background: #dbeafe; color: #1e40af; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Assistant Orchestrator Dashboard</h1>
            <div class="subtitle">Анализ зрелости архитектуры проекта</div>
            <div class="timestamp">Отчёт сгенерирован: {self.result.timestamp}</div>
        </header>

        <div class="dashboard">
            <div class="card">
                <h2>🏗️ Микросервисы</h2>
                <div class="metric">
                    <span class="metric-label">Всего сервисов</span>
                    <span class="metric-value">{len(self.result.microservices.get('services', []))}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Production-ready</span>
                    <span class="metric-value">{len([s for s in self.result.microservices.get('services', []) if s.get('is_production_ready')])}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">С тестами</span>
                    <span class="metric-value">{sum(1 for s in self.result.microservices.get('services', []) if s.get('has_tests'))}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">С Docker</span>
                    <span class="metric-value">{sum(1 for s in self.result.microservices.get('services', []) if s.get('has_docker'))}</span>
                </div>
            </div>

            <div class="card">
                <h2>🎯 Навыки</h2>
                <div class="metric">
                    <span class="metric-label">Маркеров</span>
                    <span class="metric-value">{self.result.skill_markers.get('total_count', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Категорий</span>
                    <span class="metric-value">{len(self.result.skill_markers.get('categories', []))}</span>
                </div>
            </div>

            <div class="card">
                <h2>📈 Активность</h2>
                <div class="metric">
                    <span class="metric-label">Всего коммитов</span>
                    <span class="metric-value">{self.result.git_stats.get('total_commits', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Контрибьюторов</span>
                    <span class="metric-value">{len(self.result.git_stats.get('contributors', []))}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Активность (30 дней)</span>
                    <span class="metric-value">{self.result.git_stats.get('recent_activity_days', 0)} коммитов</span>
                </div>
            </div>

            <div class="card score-container">
                <h2>🎯 Уровень зрелости</h2>
                <div class="score-circle">
                    <div class="score-value">{maturity_score:.1f}</div>
                </div>
                <div class="score-label">из 5.0</div>
                <div style="margin-top: 1rem;">
                    {"<span class='badge badge-success'>Высокий уровень</span>" if maturity_score >= 4.0 else
                     "<span class='badge badge-warning'>Средний уровень</span>" if maturity_score >= 3.0 else
                     "<span class='badge badge-info'>Базовый уровень</span>"}
                </div>
            </div>
        </div>

        <div class="card">
            <h2>💡 Рекомендации</h2>
            <div class="recommendations">
"""

        if recommendations:
            for rec in recommendations[:5]:
                html += f"""
                <div class="recommendation">
                    <h3>{rec['title']}</h3>
                    <p>{rec['description']}</p>
                    <p><strong>Потенциальный рост:</strong> +{rec['potential_gain']} баллов</p>
                    <p><strong>Действие:</strong> {rec['action']}</p>
                </div>
"""
        else:
            html += """
                <div class="recommendation">
                    <h3>Отличная работа!</h3>
                    <p>Проект демонстрирует высокую зрелость архитектуры. Продолжайте в том же духе!</p>
                </div>
"""

        html += """
            </div>
        </div>

        <footer>
            <p>Сгенерировано Assistant Orchestrator v0.1.0</p>
            <p>Для подробного анализа запустите: <code>python -m assistant_orchestrator --format json</code></p>
        </footer>
    </div>
</body>
</html>"""

        return html


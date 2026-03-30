"""
Maturity scoring for architecture assessment.
"""
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MaturityScorer:
    """Calculate architecture maturity score (0-5)."""
    
    def __init__(self, analysis_result: Dict[str, Any]):
        self.analysis = analysis_result
    
    def calculate_score(self) -> float:
        """Calculate overall maturity score (0-5)."""
        score = 0.0
        
        # 1. Microservices maturity
        score += self._score_microservices()
        
        # 2. Skills maturity
        score += self._score_skills()
        
        # 3. Documentation maturity
        score += self._score_documentation()
        
        # 4. Git activity maturity
        score += self._score_git_activity()
        
        # 5. Dependencies maturity
        score += self._score_dependencies()
        
        # 6. Production readiness
        score += self._score_production_readiness()
        
        # Cap at 5.0
        return min(score, 5.0)
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for improving maturity score."""
        recommendations = []
        current_score = self.calculate_score()
        
        # Check microservices
        services = self.analysis.get('microservices', {}).get('services', [])
        prod_ready = sum(1 for s in services if s.get('is_production_ready', False))
        
        if prod_ready < len(services) * 0.8:  # Less than 80% production ready
            recommendations.append({
                'category': 'microservices',
                'title': 'Увеличить количество production-ready сервисов',
                'description': f'Только {prod_ready} из {len(services)} сервисов готовы к продакшену',
                'potential_gain': 0.3,
                'action': 'Добавить тесты, Dockerfile и health checks для оставшихся сервисов'
            })
        
        # Check Kubernetes
        has_k8s = self.analysis.get('microservices', {}).get('has_kubernetes', False)
        if not has_k8s:
            recommendations.append({
                'category': 'deployment',
                'title': 'Добавить Kubernetes manifests',
                'description': 'Отсутствуют конфигурации Kubernetes для оркестрации',
                'potential_gain': 0.3,
                'action': 'Создать k8s/ директорию с манифестами для каждого сервиса'
            })
        
        # Check architecture decision records
        docs = self.analysis.get('architecture_docs', [])
        has_adr = any('adr' in doc.lower() or 'decision' in doc.lower() for doc in docs)
        if not has_adr:
            recommendations.append({
                'category': 'documentation',
                'title': 'Начать вести Architecture Decision Records (ADR)',
                'description': 'Отсутствуют документированные архитектурные решения',
                'potential_gain': 0.5,
                'action': 'Создать docs/adr/ и добавить первый ADR'
            })
        
        # Check test coverage
        services_with_tests = sum(1 for s in services if s.get('has_tests', False))
        if services_with_tests < len(services):
            recommendations.append({
                'category': 'testing',
                'title': 'Улучшить покрытие тестами',
                'description': f'{services_with_tests} из {len(services)} сервисов имеют тесты',
                'potential_gain': 0.2,
                'action': 'Добавить unit-тесты для сервисов без тестов'
            })
        
        # Check recent activity
        recent_commits = self.analysis.get('git_stats', {}).get('recent_activity_days', 0)
        if recent_commits < 10:
            recommendations.append({
                'category': 'activity',
                'title': 'Увеличить активность разработки',
                'description': f'Только {recent_commits} коммитов за последние 30 дней',
                'potential_gain': 0.2,
                'action': 'Планировать регулярные коммиты и code reviews'
            })
        
        return recommendations
    
    def _score_microservices(self) -> float:
        """Score based on microservices architecture."""
        services = self.analysis.get('microservices', {}).get('services', [])
        if not services:
            return 0.0
        
        score = 0.0
        
        # Base score for having microservices
        if len(services) >= 1:
            score += 0.5
        
        # Production ready services
        prod_ready = sum(1 for s in services if s.get('is_production_ready', False))
        if prod_ready > 0:
            score += 0.5 * (prod_ready / len(services))
        
        # Services with tests
        with_tests = sum(1 for s in services if s.get('has_tests', False))
        if with_tests > 0:
            score += 0.3 * (with_tests / len(services))
        
        # Docker support
        with_docker = sum(1 for s in services if s.get('has_docker', False))
        if with_docker > 0:
            score += 0.2 * (with_docker / len(services))
        
        return min(score, 1.0)
    
    def _score_skills(self) -> float:
        """Score based on IT-Compass skill markers."""
        skill_count = self.analysis.get('skill_markers', {}).get('total_count', 0)
        categories = len(self.analysis.get('skill_markers', {}).get('categories', []))
        
        if skill_count == 0:
            return 0.0
        
        score = 0.0
        
        if skill_count >= 20:
            score += 0.5
        if skill_count >= 50:
            score += 0.3
        if skill_count >= 100:
            score += 0.2
        
        if categories >= 10:
            score += 0.3
        if categories >= 20:
            score += 0.2
        
        return min(score, 1.0)
    
    def _score_documentation(self) -> float:
        """Score based on architecture documentation."""
        docs = self.analysis.get('architecture_docs', [])
        
        if not docs:
            return 0.0
        
        score = 0.0
        
        # Base score for having docs
        score += 0.5
        
        # Multiple docs
        if len(docs) >= 3:
            score += 0.3
        if len(docs) >= 10:
            score += 0.2
        
        # Check for specific important docs
        doc_names = [d.lower() for d in docs]
        if any('architecture' in name for name in doc_names):
            score += 0.2
        if any('design' in name for name in doc_names):
            score += 0.2
        if any('adr' in name for name in doc_names):
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_git_activity(self) -> float:
        """Score based on Git repository activity."""
        git_stats = self.analysis.get('git_stats', {})
        total_commits = git_stats.get('total_commits', 0)
        recent_activity = git_stats.get('recent_activity_days', 0)
        contributors = len(git_stats.get('contributors', []))
        
        score = 0.0
        
        # Commit volume
        if total_commits >= 50:
            score += 0.3
        if total_commits >= 200:
            score += 0.2
        if total_commits >= 500:
            score += 0.2
        
        # Recent activity
        if recent_activity >= 10:
            score += 0.2
        if recent_activity >= 30:
            score += 0.3
        
        # Contributors
        if contributors >= 3:
            score += 0.2
        if contributors >= 10:
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_dependencies(self) -> float:
        """Score based on dependencies management."""
        deps = self.analysis.get('dependencies', {})
        has_docker_compose = self.analysis.get('microservices', {}).get('has_docker_compose', False)
        
        score = 0.0
        
        if deps:
            score += 0.5
        
        if has_docker_compose:
            score += 0.3
        
        # Check for multiple services with dependencies
        if len(deps) >= 3:
            score += 0.2
        
        return min(score, 0.5)  # Max 0.5 for dependencies
    
    def _score_production_readiness(self) -> float:
        """Score based on overall production readiness indicators."""
        score = 0.0
        
        # Check for CI/CD indicators
        # (Could be extended to detect .github/workflows, Jenkinsfile, etc.)
        # For now, we'll give a small bonus if we have both Docker and tests
        
        services = self.analysis.get('microservices', {}).get('services', [])
        if services:
            has_docker = any(s.get('has_docker', False) for s in services)
            has_tests = any(s.get('has_tests', False) for s in services)
            
            if has_docker and has_tests:
                score += 0.5
        
        return min(score, 0.5)
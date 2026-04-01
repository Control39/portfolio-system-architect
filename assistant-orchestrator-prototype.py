#!/usr/bin/env python3
"""
Прототип помощника-оркестратора для анализа многоисточниковых доказательств

Анализирует:
1. Структуру проекта - 10 production-ready микросервисов
2. Архитектурные документы - DESIGN.md, automation/README.md
3. Систему маркеров IT-Compass - 18 областей навыков
4. Интеграции между компонентами - system dependencies
5. Git историю (как дополнительный источник)
"""

import os
import json
import yaml
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re

@dataclass
class MicroserviceInfo:
    """Информация о микросервисе"""
    name: str
    path: str
    has_dockerfile: bool
    has_kubernetes: bool
    has_requirements: bool
    has_tests: bool
    language: str
    description: str = ""

@dataclass
class SkillMarker:
    """Маркер навыка из IT-Compass"""
    skill_name: str
    level: str
    marker_id: str
    description: str
    smart_criteria: Dict[str, str]

@dataclass
class ProjectAnalysis:
    """Результат анализа проекта"""
    timestamp: str
    total_microservices: int
    production_ready_count: int
    total_skill_markers: int
    skill_categories: List[str]
    architecture_docs: List[str]
    git_commit_count: int
    dependencies: Dict[str, List[str]]
    summary: Dict[str, Any]

class AssistantOrchestrator:
    """Помощник-оркестратор для анализа экосистемы"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_result = None
        
    def analyze_project_structure(self) -> List[MicroserviceInfo]:
        """Анализирует структуру проекта и микросервисы"""
        apps_dir = self.project_root / "apps"
        microservices = []
        
        if not apps_dir.exists():
            print(f"⚠️ Директория apps не найдена: {apps_dir}")
            return microservices
            
        for item in apps_dir.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                ms_info = self._analyze_microservice(item)
                microservices.append(ms_info)
                
        return microservices
    
    def _analyze_microservice(self, ms_path: Path) -> MicroserviceInfo:
        """Анализирует отдельный микросервис"""
        name = ms_path.name
        
        # Проверяем наличие ключевых файлов
        has_dockerfile = (ms_path / "Dockerfile").exists()
        has_kubernetes = self._check_kubernetes_files(ms_path)
        has_requirements = self._check_requirements_files(ms_path)
        has_tests = self._check_tests_exist(ms_path)
        
        # Определяем язык программирования
        language = self._detect_language(ms_path)
        
        # Получаем описание из README если есть
        description = self._get_description(ms_path)
        
        return MicroserviceInfo(
            name=name,
            path=str(ms_path.relative_to(self.project_root)),
            has_dockerfile=has_dockerfile,
            has_kubernetes=has_kubernetes,
            has_requirements=has_requirements,
            has_tests=has_tests,
            language=language,
            description=description
        )
    
    def _check_kubernetes_files(self, path: Path) -> bool:
        """Проверяет наличие Kubernetes конфигураций"""
        k8s_patterns = ["*.yaml", "*.yml", "deployment", "k8s"]
        for pattern in k8s_patterns:
            if list(path.glob(f"**/{pattern}")):
                return True
        return False
    
    def _check_requirements_files(self, path: Path) -> bool:
        """Проверяет наличие файлов зависимостей"""
        req_files = ["requirements.txt", "pyproject.toml", "package.json", "go.mod"]
        for file in req_files:
            if (path / file).exists():
                return True
        return False
    
    def _check_tests_exist(self, path: Path) -> bool:
        """Проверяет наличие тестов"""
        test_dirs = ["tests", "test", "__tests__"]
        test_files = ["*test*.py", "*spec*.js", "*test*.go"]
        
        # Проверяем тестовые директории
        for test_dir in test_dirs:
            if (path / test_dir).exists():
                return True
        
        # Проверяем тестовые файлы
        for pattern in test_files:
            if list(path.glob(f"**/{pattern}")):
                return True
                
        return False
    
    def _detect_language(self, path: Path) -> str:
        """Определяет язык программирования"""
        # Проверяем по расширениям файлов
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.go': 'Go',
            '.java': 'Java',
            '.rs': 'Rust',
            '.ps1': 'PowerShell',
            '.sh': 'Bash'
        }
        
        for ext, lang in extensions.items():
            if list(path.glob(f"**/*{ext}")):
                return lang
        
        # Проверяем по специфическим файлам
        if (path / "package.json").exists():
            return "JavaScript/TypeScript"
        elif (path / "go.mod").exists():
            return "Go"
        elif (path / "Cargo.toml").exists():
            return "Rust"
        
        return "Unknown"
    
    def _get_description(self, path: Path) -> str:
        """Получает описание из README"""
        readme_files = ["README.md", "README.txt", "README"]
        for readme in readme_files:
            readme_path = path / readme
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8', errors='ignore')
                    # Берем первую строку после заголовка
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith('#') and len(line.strip()) > 10:
                            return line.strip()[:100] + "..."
                except:
                    pass
        return ""
    
    def analyze_it_compass_markers(self) -> List[SkillMarker]:
        """Анализирует маркеры навыков из IT-Compass"""
        markers_dir = self.project_root / "apps" / "it-compass" / "src" / "data" / "markers"
        skill_markers = []
        
        if not markers_dir.exists():
            print(f"⚠️ Директория маркеров не найдена: {markers_dir}")
            return skill_markers
        
        for marker_file in markers_dir.glob("*.json"):
            try:
                with open(marker_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                skill_name = marker_file.stem.replace('_', ' ').title()
                
                # Извлекаем маркеры из структуры
                if 'levels' in data:
                    for level, level_markers in data['levels'].items():
                        for marker in level_markers:
                            marker_id = marker.get('id', f"{skill_name}-{level}-{len(skill_markers)}")
                            description = marker.get('description', '')
                            smart_criteria = marker.get('smart_criteria', {})
                            
                            skill_markers.append(SkillMarker(
                                skill_name=skill_name,
                                level=level,
                                marker_id=marker_id,
                                description=description,
                                smart_criteria=smart_criteria
                            ))
            except Exception as e:
                print(f"⚠️ Ошибка при чтении {marker_file}: {e}")
        
        return skill_markers
    
    def analyze_architecture_docs(self) -> List[str]:
        """Анализирует архитектурные документы"""
        docs_to_analyze = [
            "docs/assistant-orchestrator/DESIGN.md",
            "automation/README.md",
            "PROJECT-DESCRIPTION.md",
            "README.md"
        ]
        
        found_docs = []
        for doc_path in docs_to_analyze:
            full_path = self.project_root / doc_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8', errors='ignore')
                    # Проверяем, что документ не пустой
                    if len(content.strip()) > 100:
                        found_docs.append(doc_path)
                except:
                    pass
        
        return found_docs
    
    def analyze_git_history(self) -> int:
        """Анализирует Git историю (количество коммитов)"""
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return 0
    
    def analyze_dependencies(self) -> Dict[str, List[str]]:
        """Анализирует зависимости между компонентами"""
        dependencies = {}
        
        # Проверяем docker-compose файлы
        compose_files = list(self.project_root.glob("docker-compose*.yml"))
        for compose_file in compose_files:
            try:
                with open(compose_file, 'r') as f:
                    compose_data = yaml.safe_load(f)
                    if compose_data and 'services' in compose_data:
                        for service_name in compose_data['services'].keys():
                            if service_name not in dependencies:
                                dependencies[service_name] = []
                            # Добавляем зависимости из networks, links и т.д.
                            service_config = compose_data['services'][service_name]
                            if 'depends_on' in service_config:
                                dependencies[service_name].extend(service_config['depends_on'])
            except:
                pass
        
        return dependencies
    
    def run_full_analysis(self) -> ProjectAnalysis:
        """Выполняет полный анализ проекта"""
        print("🔍 Запуск анализа экосистемы...")
        
        # 1. Анализ структуры проекта
        microservices = self.analyze_project_structure()
        production_ready = [ms for ms in microservices if ms.has_dockerfile or ms.has_kubernetes]
        
        # 2. Анализ маркеров IT-Compass
        skill_markers = self.analyze_it_compass_markers()
        skill_categories = list(set([m.skill_name for m in skill_markers]))
        
        # 3. Анализ архитектурных документов
        architecture_docs = self.analyze_architecture_docs()
        
        # 4. Анализ Git истории
        git_commit_count = self.analyze_git_history()
        
        # 5. Анализ зависимостей
        dependencies = self.analyze_dependencies()
        
        # Создаем сводку
        summary = {
            "microservices_analysis": {
                "total": len(microservices),
                "production_ready": len(production_ready),
                "languages": list(set([ms.language for ms in microservices])),
                "with_tests": len([ms for ms in microservices if ms.has_tests])
            },
            "skills_analysis": {
                "total_markers": len(skill_markers),
                "categories": skill_categories,
                "levels_distribution": {
                    "1": len([m for m in skill_markers if m.level == "1"]),
                    "2": len([m for m in skill_markers if m.level == "2"]),
                    "3": len([m for m in skill_markers if m.level == "3"])
                }
            },
            "documentation_analysis": {
                "architecture_docs_found": len(architecture_docs),
                "docs_list": architecture_docs
            }
        }
        
        self.analysis_result = ProjectAnalysis(
            timestamp=datetime.now().isoformat(),
            total_microservices=len(microservices),
            production_ready_count=len(production_ready),
            total_skill_markers=len(skill_markers),
            skill_categories=skill_categories,
            architecture_docs=architecture_docs,
            git_commit_count=git_commit_count,
            dependencies=dependencies,
            summary=summary
        )
        
        return self.analysis_result
    
    def generate_report(self, output_format: str = "text") -> str:
        """Генерирует отчет на основе анализа"""
        if not self.analysis_result:
            self.run_full_analysis()
        
        analysis = self.analysis_result
        
        if output_format == "json":
            return json.dumps(asdict(analysis), indent=2, ensure_ascii=False)
        
        # Текстовый отчет
        report = []
        report.append("=" * 60)
        report.append("📊 ОТЧЕТ АНАЛИЗА ЭКОСИСТЕМЫ КОГНИТИВНОЙ АРХИТЕКТУРЫ")
        report.append("=" * 60)
        report.append(f"Время анализа: {analysis.timestamp}")
        report.append("")
        
        # Раздел 1: Микросервисы
        report.append("🏗️  СТРУКТУРА ПРОЕКТА")
        report.append(f"  • Всего компонентов: {analysis.total_microservices}")
        report.append(f"  • Production-ready: {analysis.production_ready_count}")
        report.append("")
        
        # Раздел 2: Навыки
        report.append("🎯 СИСТЕМА НАВЫКОВ IT-COMPASS")
        report.append(f"  • Всего маркеров: {analysis.total_skill_markers}")
        report.append(f"  • Категории навыков: {', '.join(analysis.skill_categories[:5])}...")
        report.append("")
        
        # Раздел 3: Документация
        report.append("📚 АРХИТЕКТУРНАЯ ДОКУМЕНТАЦИЯ")
        report.append(f"  • Найдено документов: {len(analysis.architecture_docs)}")
        for doc in analysis.architecture_docs[:3]:
            report.append(f"    • {doc}")
        report.append("")
        
        # Раздел 4: Git
        report.append("📈 ИСТОРИЯ РАЗРАБОТКИ")
        report.append(f"  • Коммитов в репозитории: {analysis.git_commit_count}")
        report.append("")
        
        # Раздел 5: Сводка
        report.append("📋 СВОДКА ЭКСПЕРТИЗЫ")
        report.append(f"  • Архитектурные навыки: {analysis.production_ready_count} production-ready микросервисов")
        report.append(f"  • Методологические навыки: {analysis.total_skill_markers} структурированных маркеров")
        report.append(f"  • Документационные навыки: {len(analysis.architecture_docs)} архитектурных документов")
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, output_file: str = "ecosystem-analysis-report.json"):
        """Сохраняет отчет в файл"""
        if not self.analysis_result:
            self.run_full_analysis()
        
        report_data = asdict(self.analysis_result)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Отчет сохранен в {output_file}")
        
        # Также создаем текстовую версию
        text_report = self.generate_report("text")
        text_file = output_file.replace('.json', '.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_report)
        print(f"✅ Текстовый отчет сохранен в {text_file}")

def main():
    """Основная функция"""
    print("🚀 Запуск прототипа помощника-оркестратора")
    print("=" * 50)
    
    # Создаем orchestrator
    orchestrator = AssistantOrchestrator()
    
    # Выполняем анализ
    analysis = orchestrator.run_full_analysis()
    
    # Генерируем и выводим отчет
    report = orchestrator.generate_report("text")
    print(report)
    
    # Сохраняем отчет
    orchestrator.save_report()
    
    # Дополнительная информация
    print("\n📁 Файлы отчета:")
    print("  • ecosystem-analysis-report.json - JSON с полными данными")
    print("  • ecosystem-analysis-report.txt - Текстовый отчет")
    print("\n🎯 Использование:")
    print("  • Для автоматизации: python assistant-orchestrator-prototype.py")
    print("  • Для интеграции: импортируйте класс AssistantOrchestrator")
    print("  • Для расширения: добавьте новые методы анализа")

if __name__ == "__main__":
    main()

"""
Генератор портфолио для IT Compass
Утилита для автоматической генерации профессионального портфолио
на основе прогресса пользователя
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader


class PortfolioGenerator:
    """Генератор профессионального портфолио"""
    
    def __init__(self, template_dir: str = "templates", output_dir: str = "portfolio"):
        """
        Инициализация генератора портфолио
        
        Args:
            template_dir: Директория с шаблонами
            output_dir: Директория для выходных файлов
        """
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
        # Создаем директории, если их нет
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "css"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "js"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
    
    def generate_portfolio(self, user_data: Dict = None, 
                         progress_data: Dict = None) -> Dict:
        """
        Генерация портфолио на основе данных пользователя
        
        Args:
            user_data: Данные пользователя
            progress_data: Данные прогресса
            
        Returns:
            Словарь с информацией о сгенерированном портфолио
        """
        # Подготавливаем данные для портфолио
        portfolio_data = self._prepare_portfolio_data(user_data, progress_data)
        
        # Генерируем файлы портфолио
        generated_files = self._generate_portfolio_files(portfolio_data)
        
        return {
            "status": "success",
            "generated_files": generated_files,
            "portfolio_data": portfolio_data,
            "generated_at": datetime.now().isoformat()
        }
    
    def _prepare_portfolio_data(self, user_data: Dict = None, 
                                progress_data: Dict = None) -> Dict:
        """
        Подготовка данных для портфолио
        
        Args:
            user_data: Данные пользователя
            progress_data: Данные прогресса
            
        Returns:
            Словарь с подготовленными данными
        """
        # Базовые данные
        portfolio_data = {
            "title": "Профессиональное портфолио",
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "user": user_data or {
                "name": "Имя Фамилия",
                "title": "IT Специалист",
                "email": "email@example.com",
                "phone": "+7 (XXX) XXX-XXXX",
                "location": "Город, Страна"
            },
            "sections": {}
        }
        
        # Добавляем секцию с навыками
        portfolio_data["sections"]["skills"] = self._generate_skills_section(progress_data)
        
        # Добавляем секцию с проектами
        portfolio_data["sections"]["projects"] = self._generate_projects_section(progress_data)
        
        # Добавляем секцию с достижениями
        portfolio_data["sections"]["achievements"] = self._generate_achievements_section(progress_data)
        
        # Добавляем секцию с графиками (если есть данные)
        portfolio_data["sections"]["charts"] = self._generate_charts_section(progress_data)
        
        return portfolio_data
    
    def _generate_skills_section(self, progress_data: Dict = None) -> Dict:
        """
        Генерация секции с навыками
        
        Args:
            progress_data: Данные прогресса
            
        Returns:
            Словарь с данными о навыках
        """
        if not progress_data:
            return {
                "title": "Навыки",
                "description": "Список профессиональных навыков",
                "skills_list": [
                    {"name": "Python", "level": 80, "category": "Программирование"},
                    {"name": "JavaScript", "level": 70, "category": "Программирование"},
                    {"name": "Docker", "level": 60, "category": "DevOps"},
                    {"name": "AWS", "level": 50, "category": "Облака"}
                ]
            }
        
        # Извлекаем навыки из данных прогресса
        skills_list = []
        directions_stats = progress_data.get("statistics", {}).get("directions", {})
        
        for direction, count in directions_stats.items():
            # Преобразуем направления в навыки
            skill_name = direction.replace("_", " ").title()
            # Уровень на основе количества выполненных маркеров
            level = min(count * 10, 100)
            
            skills_list.append({
                "name": skill_name,
                "level": level,
                "category": "IT Навыки"
            })
        
        return {
            "title": "Навыки",
            "description": "Профессиональные навыки, основанные на прогрессе в IT Compass",
            "skills_list": skills_list
        }
    
    def _generate_projects_section(self, progress_data: Dict = None) -> Dict:
        """
        Генерация секции с проектами
        
        Args:
            progress_data: Данные прогресса
            
        Returns:
            Словарь с данными о проектах
        """
        return {
            "title": "Проекты",
            "description": "Проекты и кейсы",
            "projects_list": [
                {
                    "name": "IT Compass Tracker",
                    "description": "Система отслеживания IT навыков и компетенций",
                    "technologies": ["Python", "Streamlit", "JSON"],
                    "link": "https://github.com/user/it-compass"
                },
                {
                    "name": "Portfolio Generator",
                    "description": "Генератор профессиональных портфолио",
                    "technologies": ["Python", "Jinja2", "HTML/CSS"],
                    "link": "https://github.com/user/portfolio-generator"
                }
            ]
        }
    
    def _generate_achievements_section(self, progress_data: Dict = None) -> Dict:
        """
        Генерация секции с достижениями
        
        Args:
            progress_data: Данные прогресса
            
        Returns:
            Словарь с данными о достижениях
        """
        achievements = []
        
        if progress_data:
            total_completed = progress_data.get("statistics", {}).get("total_completed", 0)
            
            if total_completed >= 50:
                achievements.append({
                    "title": "Мастер навыков",
                    "description": "Выполнил 50+ маркеров навыков",
                    "icon": "🏆"
                })
            
            if total_completed >= 25:
                achievements.append({
                    "title": "Полуфиналист",
                    "description": "Выполнил 25+ маркеров навыков",
                    "icon": "🥈"
                })
            
            # Достижения по направлениям
            directions = progress_data.get("statistics", {}).get("directions", {})
            for direction, count in directions.items():
                if count >= 10:
                    achievements.append({
                        "title": f"Эксперт в {direction}",
                        "description": f"Освоил {count} навыков в направлении {direction}",
                        "icon": "🎓"
                    })
        
        # Добавляем базовые достижения, если нет данных
        if not achievements:
            achievements = [
                {
                    "title": "Начинающий",
                    "description": "Начал путь в IT",
                    "icon": "🚀"
                },
                {
                    "title": "Исследователь",
                    "description": "Изучает новые технологии",
                    "icon": "🔍"
                }
            ]
        
        return {
            "title": "Достижения",
            "description": "Профессиональные достижения",
            "achievements_list": achievements
        }
    
    def _generate_charts_section(self, progress_data: Dict = None) -> Dict:
        """
        Генерация секции с графиками
        
        Args:
            progress_data: Данные прогресса
            
        Returns:
            Словарь с данными о графиках
        """
        return {
            "title": "Статистика",
            "description": "Визуализация прогресса",
            "charts": [
                {
                    "type": "progress",
                    "title": "Общий прогресс",
                    "data": progress_data.get("statistics", {}) if progress_data else {}
                },
                {
                    "type": "directions",
                    "title": "По направлениям",
                    "data": progress_data.get("statistics", {}).get("directions", {}) if progress_data else {}
                }
            ]
        }
    
    def _generate_portfolio_files(self, portfolio_data: Dict) -> List[str]:
        """
        Генерация файлов портфолио
        
        Args:
            portfolio_data: Данные для портфолио
            
        Returns:
            Список сгенерированных файлов
        """
        generated_files = []
        
        # Генерируем README.md
        readme_content = self._generate_readme(portfolio_data)
        readme_path = os.path.join(self.output_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        generated_files.append("README.md")
        
        # Генерируем portfolio.json
        json_path = os.path.join(self.output_dir, "portfolio.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(portfolio_data, f, ensure_ascii=False, indent=2)
        generated_files.append("portfolio.json")
        
        # Генерируем index.html
        html_content = self._generate_html_portfolio(portfolio_data)
        html_path = os.path.join(self.output_dir, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        generated_files.append("index.html")
        
        # Копируем CSS файлы
        css_content = self._generate_css()
        css_path = os.path.join(self.output_dir, "css", "style.css")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
        generated_files.append("css/style.css")
        
        return generated_files
    
    def _generate_readme(self, portfolio_data: Dict) -> str:
        """
        Генерация README.md файла
        
        Args:
            portfolio_data: Данные для портфолио
            
        Returns:
            Строка с содержимым README.md
        """
        readme = f"""# {portfolio_data['user']['name']} - Профессиональное портфолио

## Контактная информация
- Email: {portfolio_data['user']['email']}
- Телефон: {portfolio_data['user']['phone']}
- Местоположение: {portfolio_data['user']['location']}

## Обо мне
Профессионал в области IT, специализирующийся на разработке и архитектуре решений.

## Навыки
"""
        
        # Добавляем навыки
        skills = portfolio_data['sections'].get('skills', {}).get('skills_list', [])
        for skill in skills:
            readme += f"- {skill['name']} ({skill['level']}%)\n"
        
        readme += f"""

## Проекты
"""
        
        # Добавляем проекты
        projects = portfolio_data['sections'].get('projects', {}).get('projects_list', [])
        for project in projects:
            readme += f"- **{project['name']}**: {project['description']}\n"
            if 'technologies' in project:
                readme += f"  Технологии: {', '.join(project['technologies'])}\n"
        
        readme += f"""

## Достижения
"""
        
        # Добавляем достижения
        achievements = portfolio_data['sections'].get('achievements', {}).get('achievements_list', [])
        for achievement in achievements:
            readme += f"- {achievement['icon']} {achievement['title']}: {achievement['description']}\n"
        
        readme += f"""

---
*Сгенерировано автоматически с помощью IT Compass - {portfolio_data['generated_date']}*
"""
        
        return readme
    
    def _generate_html_portfolio(self, portfolio_data: Dict) -> str:
        """
        Генерация HTML портфолио
        
        Args:
            portfolio_data: Данные для портфолио
            
        Returns:
            Строка с HTML содержимым
        """
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{portfolio_data['user']['name']} - Портфолио</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>{portfolio_data['user']['name']}</h1>
        <p>{portfolio_data['user']['title']}</p>
        <p>Email: {portfolio_data['user']['email']} | Телефон: {portfolio_data['user']['phone']}</p>
    </header>
    
    <main>
        <section id="skills">
            <h2>{portfolio_data['sections'].get('skills', {}).get('title', 'Навыки')}</h2>
            <p>{portfolio_data['sections'].get('skills', {}).get('description', '')}</p>
            <div class="skills-grid">
"""
        
        # Добавляем навыки
        skills = portfolio_data['sections'].get('skills', {}).get('skills_list', [])
        for skill in skills:
            html += f"""                <div class="skill">
                    <h3>{skill['name']}</h3>
                    <div class="skill-bar">
                        <div class="skill-level" style="width: {skill['level']}%"></div>
                    </div>
                    <p>{skill['level']}%</p>
                </div>
"""
        
        html += """            </div>
        </section>
        
        <section id="projects">
            <h2>Проекты</h2>
            <div class="projects-grid">
"""
        
        # Добавляем проекты
        projects = portfolio_data['sections'].get('projects', {}).get('projects_list', [])
        for project in projects:
            html += f"""                <div class="project">
                    <h3>{project['name']}</h3>
                    <p>{project['description']}</p>
                    <p><a href="{project.get('link', '#')}">Подробнее</a></p>
                </div>
"""
        
        html += """            </div>
        </section>
        
        <section id="achievements">
            <h2>Достижения</h2>
            <div class="achievements-grid">
"""
        
        # Добавляем достижения
        achievements = portfolio_data['sections'].get('achievements', {}).get('achievements_list', [])
        for achievement in achievements:
            html += f"""                <div class="achievement">
                    <span class="achievement-icon">{achievement['icon']}</span>
                    <h3>{achievement['title']}</h3>
                    <p>{achievement['description']}</p>
                </div>
"""
        
        html += """            </div>
        </section>
    </main>
    
    <footer>
        <p>Сгенерировано с помощью IT Compass - {portfolio_data['generated_date']}</p>
    </footer>
</body>
</html>"""
        
        return html
    
    def _generate_css(self) -> str:
        """
        Генерация CSS стилей
        
        Returns:
            Строка с CSS содержимым
        """
        return """/* Основные стили для портфолио */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
}

header {
    background-color: #333;
    color: white;
    padding: 1rem;
    text-align: center;
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

section {
    margin-bottom: 2rem;
    background-color: white;
    padding: 1.5rem;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

h1, h2, h3 {
    color: #333;
}

.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
}

.skill {
    text-align: center;
}

.skill-bar {
    width: 100%;
    height: 20px;
    background-color: #ddd;
    border-radius: 10px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.skill-level {
    height: 100%;
    background-color: #4CAF50;
    transition: width 0.3s ease;
}

.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
}

.project {
    border: 1px solid #ddd;
    padding: 1rem;
    border-radius: 5px;
}

.achievements-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
}

.achievement {
    text-align: center;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.achievement-icon {
    font-size: 2rem;
    display: block;
    margin-bottom: 0.5rem;
}

footer {
    background-color: #333;
    color: white;
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}

@media (max-width: 768px) {
    .skills-grid, .projects-grid, .achievements-grid {
        grid-template-columns: 1fr;
    }
}
"""
    
    def export_portfolio_template(self) -> Dict:
        """
        Экспорт шаблона портфолио
        
        Returns:
            Словарь с шаблоном портфолио
        """
        return {
            "template_version": "1.0",
            "sections": [
                "skills",
                "projects", 
                "achievements",
                "experience",
                "education",
                "contact"
            ],
            "exported_at": datetime.now().isoformat()
        }


# Пример использования
if __name__ == "__main__":
    # Создаем генератор портфолио
    portfolio_gen = PortfolioGenerator()
    
    # Пример данных прогресса
    sample_progress = {
        "statistics": {
            "total_completed": 35,
            "directions": {
                "backend_development": 12,
                "frontend_development": 8,
                "devops": 6,
                "data_science": 9
            },
            "levels": {
                "basic": 20,
                "advanced": 10,
                "expert": 5
            }
        }
    }
    
    # Генерируем портфолио
    result = portfolio_gen.generate_portfolio(progress_data=sample_progress)
    
    print("Портфолио успешно сгенерировано!")
    print(f"Сгенерированные файлы: {', '.join(result['generated_files'])}")
    print(f"Дата генерации: {result['generated_at']}")
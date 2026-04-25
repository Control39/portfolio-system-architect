# Пример интеграции it-compass и decision-engine
# Демонстрация взаимодействия между системой отслеживания компетенций и движком принятия решений

from typing import Any


class ITCompassDecisionEngineIntegration:
    """Класс для демонстрации интеграции it-compass и decision-engine
    """

    def __init__(self):
        self.user_profile = {}
        self.cloud_solutions = []
        self.recommendations = []

    def load_user_profile(self, profile_data: dict[str, Any]):
        """Загрузка профиля пользователя из it-compass
        """
        self.user_profile = profile_data
        print("Профиль пользователя загружен из it-compass")
        print(f"Компетенции: {', '.join(self.user_profile.get('skills', []))}")

    def load_cloud_solutions(self, solutions_data: list[dict[str, Any]]):
        """Загрузка данных об облачных решениях из decision-engine
        """
        self.cloud_solutions = solutions_data
        print("Данные об облачных решениях загружены из decision-engine")
        print(f"Доступно решений: {len(self.cloud_solutions)}")

    def generate_recommendations(self) -> list[dict[str, Any]]:
        """Генерация рекомендаций на основе профиля пользователя и облачных решений
        """
        user_skills = set(self.user_profile.get("skills", []))
        self.recommendations = []

        for solution in self.cloud_solutions:
            required_skills = set(solution.get("required_skills", []))
            skill_match = (
                len(user_skills.intersection(required_skills)) / len(required_skills)
                if required_skills
                else 0
            )

            if skill_match > 0.5:  # Если совпадение навыков более 50%
                recommendation = {
                    "solution_name": solution.get("name"),
                    "match_score": skill_match,
                    "required_skills": list(required_skills),
                    "missing_skills": list(required_skills - user_skills),
                    "learning_path": self._generate_learning_path(
                        required_skills - user_skills,
                    ),
                }
                self.recommendations.append(recommendation)

        # Сортировка по уровню совпадения
        self.recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return self.recommendations

    def _generate_learning_path(self, missing_skills: set) -> list[str]:
        """Генерация пути обучения для недостающих навыков
        """
        learning_paths = {
            "AWS": "AWS Certified Solutions Architect",
            "Azure": "Microsoft Azure Fundamentals",
            "GCP": "Google Cloud Professional Cloud Architect",
            "Docker": "Docker Certified Associate",
            "Kubernetes": "Certified Kubernetes Administrator",
        }

        return [
            learning_paths.get(skill, f"Изучение {skill}") for skill in missing_skills
        ]

    def display_recommendations(self):
        """Отображение рекомендаций
        """
        print("\n=== РЕКОМЕНДАЦИИ ПО ИНТЕГРАЦИИ IT-COMPASS И DECISION-ENGINE ===")
        if not self.recommendations:
            print("Рекомендации не найдены. Возможно, требуется больше данных.")
            return

        for i, rec in enumerate(self.recommendations, 1):
            print(f"\n{i}. Решение: {rec['solution_name']}")
            print(f"   Уровень совпадения: {rec['match_score']:.2%}")
            print(f"   Требуемые навыки: {', '.join(rec['required_skills'])}")
            if rec["missing_skills"]:
                print(f"   Недостающие навыки: {', '.join(rec['missing_skills'])}")
                print(f"   Путь обучения: {' -> '.join(rec['learning_path'])}")
            else:
                print("   Все необходимые навыки имеются!")


# Демонстрационные данные
SAMPLE_USER_PROFILE = {
    "name": "Алексей Петров",
    "skills": ["Python", "Docker", "AWS", "REST API", "CI/CD"],
    "experience": "3 года",
    "current_role": "DevOps Engineer",
}

SAMPLE_CLOUD_SOLUTIONS = [
    {
        "name": "Микросервисная архитектура на AWS",
        "required_skills": ["AWS", "Docker", "Kubernetes", "Python", "Terraform"],
        "description": "Платформа для развертывания микросервисов",
    },
    {
        "name": "Data Lake на Azure",
        "required_skills": ["Azure", "Python", "Spark", "SQL", "Databricks"],
        "description": "Решение для хранения и анализа больших данных",
    },
    {
        "name": "Serverless API на GCP",
        "required_skills": ["GCP", "Python", "Cloud Functions", "REST API", "Firebase"],
        "description": "Бессерверная архитектура для веб-API",
    },
]


def main():
    """Основная функция демонстрации интеграции
    """
    print("Демонстрация интеграции it-compass и decision-engine")
    print("=" * 50)

    # Создание экземпляра интеграции
    integration = ITCompassDecisionEngineIntegration()

    # Загрузка данных
    integration.load_user_profile(SAMPLE_USER_PROFILE)
    integration.load_cloud_solutions(SAMPLE_CLOUD_SOLUTIONS)

    # Генерация рекомендаций
    integration.generate_recommendations()

    # Отображение результатов
    integration.display_recommendations()

    print("\n=== ЗАКЛЮЧЕНИЕ ===")
    print("Интеграция it-compass и decision-engine позволяет:")
    print("1. Персонализировать рекомендации по облачным решениям")
    print("2. Определять пробелы в навыках пользователя")
    print("3. Предлагать пути обучения для освоения новых технологий")
    print("4. Оптимизировать выбор облачных решений под профиль специалиста")


if __name__ == "__main__":
    main()


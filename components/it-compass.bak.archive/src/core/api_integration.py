"""
Модуль интеграции с внешними API для IT Compass.

Этот модуль предоставляет классы и функции для интеграции с внешними
платформами, такими как GitHub, Coursera, LinkedIn и другими.
"""

import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import os


@dataclass
class UserActivity:
    """
    Активность пользователя на внешней платформе.
    """
    platform: str             # Платформа (github, coursera, linkedin)
    activity_type: str       # Тип активности (commit, course_completed, post)
    timestamp: str           # Время активности (ISO формат)
    description: str         # Описание активности
    url: str = ""            # Ссылка на активность
    metadata: Dict[str, Any] = None  # Дополнительные метаданные


@dataclass
class ExternalResource:
    """
    Внешний ресурс пользователя.
    """
    platform: str             # Платформа (github, coursera, linkedin)
    resource_type: str       # Тип ресурса (repository, course, post)
    title: str              # Название ресурса
    url: str                # Ссылка на ресурс
    created_at: str         # Дата создания (ISO формат)
    description: str = ""    # Описание ресурса
    metadata: Dict[str, Any] = None  # Дополнительные метаданные


class APIIntegration(ABC):
    """
    Абстрактный базовый класс для интеграции с внешними API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация интеграции с API.
        
        Args:
            config (Dict[str, Any]): Конфигурация для интеграции
        """
        self.config = config
        self.base_url = config.get("base_url", "")
        self.api_key = config.get("api_key", "")
        self.timeout = config.get("timeout", 30)
    
    @abstractmethod
    def get_user_activities(self, user_id: str) -> List[UserActivity]:
        """
        Получение активностей пользователя.
        
        Args:
            user_id (str): Идентификатор пользователя
            
        Returns:
            List[UserActivity]: Список активностей пользователя
        """
        pass
    
    @abstractmethod
    def get_user_resources(self, user_id: str) -> List[ExternalResource]:
        """
        Получение ресурсов пользователя.
        
        Args:
            user_id (str): Идентификатор пользователя
            
        Returns:
            List[ExternalResource]: Список ресурсов пользователя
        """
        pass


class GitHubIntegration(APIIntegration):
    """
    Интеграция с GitHub API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация интеграции с GitHub.
        
        Args:
            config (Dict[str, Any]): Конфигурация для интеграции с GitHub
        """
        super().__init__(config)
        self.base_url = "https://api.github.com"
    
    def get_user_activities(self, user_id: str) -> List[UserActivity]:
        """
        Получение активностей пользователя на GitHub.
        
        Args:
            user_id (str): Идентификатор пользователя (логин на GitHub)
            
        Returns:
            List[UserActivity]: Список активностей пользователя
        """
        activities = []
        
        try:
            # Получение событий пользователя
            events_url = f"{self.base_url}/users/{user_id}/events/public"
            headers = {"Authorization": f"token {self.api_key}"} if self.api_key else {}
            
            response = requests.get(
                events_url, 
                headers=headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            events = response.json()
            
            for event in events[:20]:  # Ограничиваем 20 последними событиями
                activity = UserActivity(
                    platform="github",
                    activity_type=event.get("type", "unknown"),
                    timestamp=event.get("created_at", ""),
                    description=self._get_event_description(event),
                    url=event.get("url", ""),
                    metadata={
                        "repo": event.get("repo", {}).get("name", ""),
                        "payload": event.get("payload", {})
                    }
                )
                activities.append(activity)
                
        except Exception as e:
            print(f"Ошибка при получении активностей GitHub: {e}")
        
        return activities
    
    def get_user_resources(self, user_id: str) -> List[ExternalResource]:
        """
        Получение репозиториев пользователя на GitHub.
        
        Args:
            user_id (str): Идентификатор пользователя (логин на GitHub)
            
        Returns:
            List[ExternalResource]: Список репозиториев пользователя
        """
        resources = []
        
        try:
            # Получение репозиториев пользователя
            repos_url = f"{self.base_url}/users/{user_id}/repos"
            headers = {"Authorization": f"token {self.api_key}"} if self.api_key else {}
            params = {"sort": "updated", "direction": "desc"}
            
            response = requests.get(
                repos_url, 
                headers=headers, 
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            repos = response.json()
            
            for repo in repos[:10]:  # Ограничиваем 10 последними репозиториями
                resource = ExternalResource(
                    platform="github",
                    resource_type="repository",
                    title=repo.get("name", ""),
                    url=repo.get("html_url", ""),
                    created_at=repo.get("created_at", ""),
                    description=repo.get("description", ""),
                    metadata={
                        "language": repo.get("language", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "private": repo.get("private", False)
                    }
                )
                resources.append(resource)
                
        except Exception as e:
            print(f"Ошибка при получении репозиториев GitHub: {e}")
        
        return resources
    
    def _get_event_description(self, event: Dict[str, Any]) -> str:
        """
        Получение описания события GitHub.
        
        Args:
            event (Dict[str, Any]): Событие GitHub
            
        Returns:
            str: Описание события
        """
        event_type = event.get("type", "")
        
        if event_type == "PushEvent":
            commits = event.get("payload", {}).get("commits", [])
            return f"Push с {len(commits)} коммитами в {event.get('repo', {}).get('name', '')}"
        elif event_type == "IssuesEvent":
            action = event.get("payload", {}).get("action", "")
            return f"Issue {action}: {event.get('payload', {}).get('issue', {}).get('title', '')}"
        elif event_type == "PullRequestEvent":
            action = event.get("payload", {}).get("action", "")
            return f"Pull Request {action}: {event.get('payload', {}).get('pull_request', {}).get('title', '')}"
        else:
            return f"{event_type} в {event.get('repo', {}).get('name', '')}"


class LearningPlatformIntegration(APIIntegration):
    """
    Интеграция с платформами онлайн-обучения (Coursera, Udemy и др.).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация интеграции с платформой обучения.
        
        Args:
            config (Dict[str, Any]): Конфигурация для интеграции
        """
        super().__init__(config)
        self.platform = config.get("platform", "unknown")
    
    def get_user_activities(self, user_id: str) -> List[UserActivity]:
        """
        Получение активностей пользователя на платформе обучения.
        
        Args:
            user_id (str): Идентификатор пользователя
            
        Returns:
            List[UserActivity]: Список активностей пользователя
        """
        activities = []
        
        try:
            # Получение курсов пользователя
            courses_url = f"{self.base_url}/users/{user_id}/courses"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            
            response = requests.get(
                courses_url, 
                headers=headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            courses = response.json()
            
            for course in courses.get("enrolled_courses", [])[:10]:
                activity = UserActivity(
                    platform=self.platform,
                    activity_type="course_progress",
                    timestamp=course.get("last_accessed", ""),
                    description=f"Прогресс в курсе: {course.get('title', '')}",
                    url=course.get("url", ""),
                    metadata={
                        "course_id": course.get("id", ""),
                        "progress": course.get("progress", 0),
                        "completed": course.get("completed", False)
                    }
                )
                activities.append(activity)
                
        except Exception as e:
            print(f"Ошибка при получении активностей платформы обучения: {e}")
        
        return activities
    
    def get_user_resources(self, user_id: str) -> List[ExternalResource]:
        """
        Получение курсов пользователя на платформе обучения.
        
        Args:
            user_id (str): Идентификатор пользователя
            
        Returns:
            List[ExternalResource]: Список курсов пользователя
        """
        resources = []
        
        try:
            # Получение курсов пользователя
            courses_url = f"{self.base_url}/users/{user_id}/courses"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            
            response = requests.get(
                courses_url, 
                headers=headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            courses = response.json()
            
            for course in courses.get("completed_courses", [])[:10]:
                resource = ExternalResource(
                    platform=self.platform,
                    resource_type="course",
                    title=course.get("title", ""),
                    url=course.get("url", ""),
                    created_at=course.get("completed_at", ""),
                    description=course.get("description", ""),
                    metadata={
                        "course_id": course.get("id", ""),
                        "certificate_url": course.get("certificate_url", ""),
                        "grade": course.get("grade", "")
                    }
                )
                resources.append(resource)
                
        except Exception as e:
            print(f"Ошибка при получении курсов платформы обучения: {e}")
        
        return resources


class LinkedInIntegration(APIIntegration):
    """
    Интеграция с LinkedIn API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация интеграции с LinkedIn.
        
        Args:
            config (Dict[str, Any]): Конфигурация для интеграции с LinkedIn
        """
        super().__init__(config)
        self.base_url = "https://api.linkedin.com/v2"
    
    def get_user_activities(self, user_id: str) -> List[UserActivity]:
        """
        Получение активностей пользователя на LinkedIn.
        
        Args:
            user_id (str): Идентификатор пользователя
            
        Returns:
            List[UserActivity]: Список активностей пользователя
        """
        activities = []
        
        try:
            # Получение публикаций пользователя
            posts_url = f"{self.base_url}/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            params = {
                "author": f"urn:li:person:{user_id}",
                "count": 10
            }
            
            response = requests.get(
                posts_url, 
                headers=headers, 
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            posts = response.json()
            
            for post in posts.get("elements", []):
                activity = UserActivity(
                    platform="linkedin",
                    activity_type="post",
                    timestamp=post.get("created", {}).get("time", ""),
                    description=self._get_post_content(post),
                    url=f"https://www.linkedin.com/feed/update/{post.get('id', '')}",
                    metadata={
                        "post_id": post.get("id", ""),
                        "likes": post.get("likes", {}).get("total", 0),
                        "comments": post.get("comments", {}).get("total", 0)
                    }
                )
                activities.append(activity)
                
        except Exception as e:
            print(f"Ошибка при получении активностей LinkedIn: {e}")
        
        return activities
    
    def get_user_resources(self, user_id: str) -> List[ExternalResource]:
        """
        Получение ресурсов пользователя на LinkedIn.
        
        Args:
            user_id (str): Идентификатор пользователя
            
        Returns:
            List[ExternalResource]: Список ресурсов пользователя
        """
        resources = []
        
        try:
            # Получение профиля пользователя
            profile_url = f"{self.base_url}/me"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(
                profile_url, 
                headers=headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            profile = response.json()
            
            resource = ExternalResource(
                platform="linkedin",
                resource_type="profile",
                title=f"LinkedIn профиль: {profile.get('localizedFirstName', '')} {profile.get('localizedLastName', '')}",
                url=f"https://www.linkedin.com/in/{user_id}",
                created_at="",  # LinkedIn не предоставляет дату создания профиля
                description=profile.get("headline", ""),
                metadata={
                    "first_name": profile.get("localizedFirstName", ""),
                    "last_name": profile.get("localizedLastName", ""),
                    "headline": profile.get("headline", ""),
                    "industry": profile.get("industry", {}).get("localizedInfo", ""),
                    "location": profile.get("location", {}).get("localizedInfo", "")
                }
            )
            resources.append(resource)
                
        except Exception as e:
            print(f"Ошибка при получении ресурсов LinkedIn: {e}")
        
        return resources
    
    def _get_post_content(self, post: Dict[str, Any]) -> str:
        """
        Получение содержимого публикации LinkedIn.
        
        Args:
            post (Dict[str, Any]): Публикация LinkedIn
            
        Returns:
            str: Содержимое публикации
        """
        try:
            # Получение текста публикации
            content_entities = post.get("content", {}).get("contentEntities", [])
            if content_entities:
                return content_entities[0].get("title", "")
            
            # Если нет контента, возвращаем описание
            return post.get("description", {}).get("text", "")[:100] + "..."
        except:
            return "Публикация LinkedIn"


class IntegrationManager:
    """
    Менеджер интеграций с внешними API.
    
    Управляет всеми интеграциями и обеспечивает синхронизацию данных пользователя.
    """
    
    def __init__(self, config_file: str = "./config/api_settings.json"):
        """
        Инициализация менеджера интеграций.
        
        Args:
            config_file (str): Путь к файлу конфигурации
        """
        self.config_file = config_file
        self.integrations = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Загрузка конфигурации интеграций.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Создание интеграций на основе конфигурации
                for integration_name, integration_config in config.items():
                    if integration_name == "github":
                        self.integrations["github"] = GitHubIntegration(integration_config)
                    elif integration_name == "learning_platform":
                        self.integrations["learning_platform"] = LearningPlatformIntegration(integration_config)
                    elif integration_name == "linkedin":
                        self.integrations["linkedin"] = LinkedInIntegration(integration_config)
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации интеграций: {e}")
    
    def sync_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Синхронизация данных пользователя со всеми интеграциями.
        
        Args:
            user_id (str): Идентификатор пользователя
            
        Returns:
            Dict[str, Any]: Синхронизированные данные пользователя
        """
        user_data = {
            "activities": [],
            "resources": [],
            "summary": {}
        }
        
        # Синхронизация с каждой интеграцией
        for name, integration in self.integrations.items():
            try:
                # Получение активностей
                activities = integration.get_user_activities(user_id)
                user_data["activities"].extend(activities)
                
                # Получение ресурсов
                resources = integration.get_user_resources(user_id)
                user_data["resources"].extend(resources)
                
            except Exception as e:
                print(f"Ошибка при синхронизации с {name}: {e}")
        
        # Создание сводки
        user_data["summary"] = self._create_summary(user_data)
        
        return user_data
    
    def _create_summary(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание сводки по данным пользователя.
        
        Args:
            user_data (Dict[str, Any]): Данные пользователя
            
        Returns:
            Dict[str, Any]: Сводка по данным пользователя
        """
        summary = {
            "total_activities": len(user_data["activities"]),
            "total_resources": len(user_data["resources"]),
            "platforms": {},
            "activity_types": {}
        }
        
        # Подсчет активностей по платформам
        for activity in user_data["activities"]:
            platform = activity.platform
            if platform not in summary["platforms"]:
                summary["platforms"][platform] = 0
            summary["platforms"][platform] += 1
            
            # Подсчет типов активностей
            activity_type = activity.activity_type
            if activity_type not in summary["activity_types"]:
                summary["activity_types"][activity_type] = 0
            summary["activity_types"][activity_type] += 1
        
        # Подсчет ресурсов по платформам
        for resource in user_data["resources"]:
            platform = resource.platform
            if platform not in summary["platforms"]:
                summary["platforms"][platform] = 0
            summary["platforms"][platform] += 1
        
        return summary


# Пример использования
if __name__ == "__main__":
    # Создание менеджера интеграций
    manager = IntegrationManager("./config/api_settings.json")
    
    # Синхронизация данных пользователя
    user_data = manager.sync_user_data("example_user")
    
    print(f"Синхронизировано {user_data['summary']['total_activities']} активностей")
    print(f"Синхронизировано {user_data['summary']['total_resources']} ресурсов")
    print(f"Платформы: {list(user_data['summary']['platforms'].keys())}")
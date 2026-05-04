#!/usr/bin/env python3
"""
Скрипты автоматизации Git для когнитивного архитектора
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


class GitAutomation:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).absolute()
        self.git_dir = self.repo_path / ".git"

    def run_git(self, command: str) -> str:
        """Выполнить git команду"""
        try:
            result = subprocess.run(
                f"git {command}",
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"

    def get_status(self) -> Dict:
        """Получить статус репозитория"""
        status = self.run_git("status --porcelain")
        branch = self.run_git("branch --show-current")
        ahead = self.run_git("rev-list --count HEAD..origin/" + branch) if branch else "0"
        behind = self.run_git("rev-list --count origin/" + branch + "..HEAD") if branch else "0"

        return {
            "branch": branch,
            "changes": len(status.splitlines()) if status else 0,
            "ahead": ahead,
            "behind": behind,
            "status": status,
        }

    def auto_commit(self, message: str = None) -> Dict:
        """Автоматический коммит изменений"""
        if message is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            message = f"Auto commit: {timestamp}"

        # Проверяем есть ли изменения
        status = self.get_status()
        if status["changes"] == 0:
            return {"success": False, "message": "Нет изменений для коммита"}

        # Добавляем все изменения
        self.run_git("add .")

        # Создаем коммит
        commit_result = self.run_git(f'commit -m "{message}"')

        return {
            "success": "error" not in commit_result.lower(),
            "message": message,
            "commit_result": commit_result,
            "changes": status["changes"],
        }

    def create_feature_branch(self, feature_name: str) -> Dict:
        """Создать feature ветку"""
        # Переходим на main и обновляем
        self.run_git("checkout main")
        self.run_git("pull origin main")

        # Создаем ветку
        branch_name = f"feature/{feature_name.replace(' ', '-').lower()}"
        branch_result = self.run_git(f"checkout -b {branch_name}")

        return {
            "success": "switched" in branch_result.lower(),
            "branch": branch_name,
            "result": branch_result,
        }

    def finish_feature(self, feature_name: str, squash: bool = True) -> Dict:
        """Завершить feature ветку"""
        branch_name = f"feature/{feature_name.replace(' ', '-').lower()}"

        # Переходим на main
        self.run_git("checkout main")
        self.run_git("pull origin main")

        # Мержим feature ветку
        if squash:
            merge_result = self.run_git(f"merge --squash {branch_name}")
        else:
            merge_result = self.run_git(f"merge {branch_name}")

        # Коммитим
        commit_message = f"Merge feature: {feature_name}"
        self.run_git(f'commit -m "{commit_message}"')

        # Пушим
        push_result = self.run_git("push origin main")

        # Удаляем feature ветку
        self.run_git(f"branch -d {branch_name}")

        return {
            "success": "error" not in merge_result.lower(),
            "feature": feature_name,
            "merge_result": merge_result,
            "push_result": push_result,
        }

    def analyze_repo(self) -> Dict:
        """Анализ репозитория"""
        # Количество коммитов
        commit_count = self.run_git("rev-list --count HEAD")

        # Авторы
        authors = self.run_git("shortlog -sn --all")

        # Последние коммиты
        recent_commits = self.run_git("log --oneline -10")

        # Размер репозитория
        size_result = subprocess.run(
            "du -sh .", shell=True, cwd=self.repo_path, capture_output=True, text=True
        )
        repo_size = size_result.stdout.strip() if size_result.stdout else "Unknown"

        return {
            "commit_count": commit_count,
            "repo_size": repo_size,
            "authors": authors,
            "recent_commits": recent_commits.splitlines() if recent_commits else [],
        }

    def cleanup_branches(self) -> Dict:
        """Очистка старых веток"""
        # Получаем список веток
        branches = self.run_git("branch --list")
        branch_list = [b.strip() for b in branches.splitlines() if b.strip()]

        # Удаляем merged ветки
        deleted = []
        for branch in branch_list:
            if branch not in ["main", "master", "* main", "* master"]:
                # Проверяем merged ли ветка
                is_merged = self.run_git(f"branch --merged main | grep {branch}")
                if branch in is_merged:
                    delete_result = self.run_git(f"branch -d {branch}")
                    if "deleted" in delete_result:
                        deleted.append(branch)

        return {"deleted_count": len(deleted), "deleted_branches": deleted}

    def generate_changelog(self, since_tag: str = None) -> str:
        """Генерация changelog"""
        if since_tag:
            cmd = f"log {since_tag}..HEAD --oneline --pretty=format:'- %s'"
        else:
            cmd = "log --since='1 month ago' --oneline --pretty=format:'- %s'"

        commits = self.run_git(cmd)

        changelog = "# Changelog\n\n"
        changelog += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

        if commits:
            changelog += "## Recent Changes\n\n"
            changelog += commits
        else:
            changelog += "No changes in specified period.\n"

        return changelog


def main():
    """Точка входа"""
    if len(sys.argv) < 2:
        print(
            """
Git Automation для когнитивного архитектора

Использование:
  python git_automation.py <command> [args]

Команды:
  status          - статус репозитория
  auto-commit     - автоматический коммит
  feature <name>  - создать feature ветку
  finish <name>   - завершить feature ветку
  analyze         - анализ репозитория
  cleanup         - очистка веток
  changelog       - генерация changelog
  help            - эта справка
"""
        )
        return

    command = sys.argv[1]
    automation = GitAutomation()

    if command == "status":
        status = automation.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif command == "auto-commit":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        result = automation.auto_commit(message)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "feature":
        if len(sys.argv) < 3:
            print("Укажите название feature")
            return
        feature_name = sys.argv[2]
        result = automation.create_feature_branch(feature_name)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "finish":
        if len(sys.argv) < 3:
            print("Укажите название feature")
            return
        feature_name = sys.argv[2]
        result = automation.finish_feature(feature_name)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "analyze":
        result = automation.analyze_repo()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "cleanup":
        result = automation.cleanup_branches()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "changelog":
        since_tag = sys.argv[2] if len(sys.argv) > 2 else None
        changelog = automation.generate_changelog(since_tag)
        print(changelog)

    elif command == "help":
        print(
            """
Примеры использования:

1. Проверить статус:
   python git_automation.py status

2. Автоматический коммит:
   python git_automation.py auto-commit "Описание изменений"

3. Создать feature ветку:
   python git_automation.py feature "новая-функция"

4. Завершить feature ветку:
   python git_automation.py finish "новая-функция"

5. Анализ репозитория:
   python git_automation.py analyze

6. Очистка веток:
   python git_automation.py cleanup

7. Генерация changelog:
   python git_automation.py changelog v1.0.0
"""
        )

    else:
        print(f"Неизвестная команда: {command}")
        print("Используйте 'help' для справки")


if __name__ == "__main__":
    main()

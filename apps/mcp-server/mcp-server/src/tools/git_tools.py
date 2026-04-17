"""
Инструменты для работы с Git
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta

from fastmcp import FastMCP

mcp = FastMCP("Git Tools")

# Корень проекта
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

@mcp.tool()
def get_git_status_tool() -> Dict[str, Any]:
    """
    Получение статуса Git репозитория
    
    Возвращает:
        Словарь с информацией о статусе Git
    """
    try:
        # Проверяем, что это Git репозиторий
        if not (PROJECT_ROOT / ".git").exists():
            return {
                "success": False,
                "message": "Директория не является Git репозиторием",
                "is_git_repo": False
            }
        
        # Получаем текущую ветку
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        # Получаем статус
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        status_lines = status_result.stdout.strip().split('\n') if status_result.stdout else []
        
        # Анализируем изменения
        changes = {
            "modified": [],
            "added": [],
            "deleted": [],
            "renamed": [],
            "untracked": []
        }
        
        for line in status_lines:
            if not line.strip():
                continue
            
            status = line[:2]
            filename = line[3:].strip()
            
            if status == " M":
                changes["modified"].append(filename)
            elif status == "A " or status == "A ":
                changes["added"].append(filename)
            elif status == "D ":
                changes["deleted"].append(filename)
            elif status.startswith("R"):
                changes["renamed"].append(filename)
            elif status == "??":
                changes["untracked"].append(filename)
        
        # Получаем информацию о remote
        remote_result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        remotes = []
        if remote_result.stdout:
            for line in remote_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        remotes.append({
                            "name": parts[0],
                            "url": parts[1],
                            "type": parts[2] if len(parts) > 2 else ""
                        })
        
        # Получаем количество коммитов
        commit_count_result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        commit_count = int(commit_count_result.stdout.strip()) if commit_count_result.returncode == 0 else 0
        
        return {
            "success": True,
            "message": f"Git статус для ветки '{current_branch}'",
            "is_git_repo": True,
            "current_branch": current_branch,
            "commit_count": commit_count,
            "changes": changes,
            "change_counts": {k: len(v) for k, v in changes.items()},
            "remotes": remotes,
            "total_changes": sum(len(v) for v in changes.values())
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при получении Git статуса: {str(e)}",
            "error": str(e),
            "is_git_repo": False
        }

@mcp.tool()
def scan_last_commits_for_markers_tool(commits_count: int = 10) -> Dict[str, Any]:
    """
    Анализ последних коммитов на наличие маркеров IT-Compass
    
    Аргументы:
        commits_count: Количество последних коммитов для анализа (по умолчанию 10)
    
    Возвращает:
        Словарь с обнаруженными маркерами
    """
    try:
        # Проверяем, что это Git репозиторий
        if not (PROJECT_ROOT / ".git").exists():
            return {
                "success": False,
                "message": "Директория не является Git репозиторием",
                "detected_markers": []
            }
        
        # Получаем последние коммиты
        log_format = '{"hash": "%H", "author": "%an", "email": "%ae", "date": "%ad", "subject": "%s", "body": "%b"}'
        
        log_result = subprocess.run(
            ["git", "log", f"-{commits_count}", f"--pretty=format:{log_format}", "--date=short"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if log_result.returncode != 0:
            return {
                "success": False,
                "message": f"Ошибка при получении лога Git: {log_result.stderr}",
                "detected_markers": []
            }
        
        # Парсим коммиты (каждая строка - JSON объект)
        commits = []
        for line in log_result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    commit_data = json.loads(line)
                    commits.append(commit_data)
                except json.JSONDecodeError:
                    # Пропускаем некорректные строки
                    continue
        
        # Загружаем маркеры IT-Compass
        markers_path = PROJECT_ROOT / "apps" / "it-compass" / "src" / "data" / "markers"
        
        if not markers_path.exists():
            return {
                "success": False,
                "message": f"Путь к маркерам IT-Compass не найден: {markers_path}",
                "detected_markers": []
            }
        
        # Загружаем все маркеры
        all_markers = []
        for marker_file in markers_path.glob("*.json"):
            try:
                with open(marker_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                domain = marker_file.stem
                skill_name = data.get("skill_name", domain)
                levels = data.get("levels", {})
                
                for level_num, level_markers in levels.items():
                    for marker in level_markers:
                        marker_text = marker.get("marker", "")
                        marker_id = marker.get("id", "")
                        
                        if marker_text:
                            all_markers.append({
                                "domain": domain,
                                "skill": skill_name,
                                "level": level_num,
                                "marker": marker_text,
                                "id": marker_id,
                                "keywords": _extract_keywords(marker_text)
                            })
            except (json.JSONDecodeError, IOError):
                continue
        
        # Анализируем коммиты на наличие маркеров
        detected = []
        
        for commit in commits:
            commit_text = f"{commit.get('subject', '')} {commit.get('body', '')}".lower()
            
            for marker in all_markers:
                # Проверяем по ключевым словам
                keywords = marker.get("keywords", [])
                matches = []
                
                for keyword in keywords:
                    if keyword in commit_text:
                        matches.append(keyword)
                
                if matches:
                    detected.append({
                        "commit_hash": commit.get("hash", "")[:8],
                        "commit_subject": commit.get("subject", ""),
                        "commit_date": commit.get("date", ""),
                        "commit_author": commit.get("author", ""),
                        "marker_domain": marker["domain"],
                        "marker_skill": marker["skill"],
                        "marker_level": marker["level"],
                        "marker_text": marker["marker"],
                        "marker_id": marker["id"],
                        "matched_keywords": matches,
                        "confidence": min(len(matches) * 20, 100)  # Простая оценка уверенности
                    })
        
        # Группируем по доменам
        domains = {}
        for detection in detected:
            domain = detection["marker_domain"]
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(detection)
        
        # Сортируем по уверенности
        detected.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "success": True,
            "message": f"Проанализировано {len(commits)} коммитов, обнаружено {len(detected)} маркеров",
            "commits_analyzed": len(commits),
            "markers_available": len(all_markers),
            "detected_markers": detected[:50],  # Ограничиваем вывод
            "domains_summary": {
                domain: len(markers) for domain, markers in domains.items()
            },
            "total_detected": len(detected)
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при анализе коммитов: {str(e)}",
            "error": str(e),
            "detected_markers": []
        }

@mcp.tool()
def get_git_history_tool(days: int = 30) -> Dict[str, Any]:
    """
    Получение истории коммитов за указанный период
    
    Аргументы:
        days: Количество дней для анализа (по умолчанию 30)
    
    Возвращает:
        Словарь с историей коммитов
    """
    try:
        # Проверяем, что это Git репозиторий
        if not (PROJECT_ROOT / ".git").exists():
            return {
                "success": False,
                "message": "Директория не является Git репозиторием",
                "commits": []
            }
        
        # Рассчитываем дату
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Получаем коммиты
        log_format = '{"hash": "%H", "author": "%an", "date": "%ad", "subject": "%s", "files_changed": "%stat"}'
        
        log_result = subprocess.run(
            ["git", "log", f"--since={since_date}", f"--pretty=format:{log_format}", "--date=short", "--stat"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if log_result.returncode != 0:
            return {
                "success": False,
                "message": f"Ошибка при получении истории Git: {log_result.stderr}",
                "commits": []
            }
        
        # Парсим коммиты
        commits = []
        current_commit = None
        
        for line in log_result.stdout.strip().split('\n'):
            if line.strip().startswith('{'):
                # Новый коммит
                if current_commit:
                    commits.append(current_commit)
                
                try:
                    current_commit = json.loads(line)
                    current_commit["files"] = []
                except json.JSONDecodeError:
                    current_commit = None
            elif current_commit and line.strip() and not line.startswith(' '):
                # Информация об измененных файлах
                parts = line.strip().split('|')
                if len(parts) >= 1:
                    file_info = parts[0].strip()
                    if file_info:
                        current_commit["files"].append(file_info)
        
        # Добавляем последний коммит
        if current_commit:
            commits.append(current_commit)
        
        # Анализируем активность
        authors = {}
        for commit in commits:
            author = commit.get("author", "unknown")
            if author not in authors:
                authors[author] = 0
            authors[author] += 1
        
        # Сортируем авторов по активности
        sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)
        
        # Анализируем файлы
        file_changes = {}
        for commit in commits:
            for file in commit.get("files", []):
                if file not in file_changes:
                    file_changes[file] = 0
                file_changes[file] += 1
        
        # Сортируем файлы по изменениям
        sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "success": True,
            "message": f"История коммитов за последние {days} дней",
            "since_date": since_date,
            "total_commits": len(commits),
            "commits": commits[:100],  # Ограничиваем вывод
            "activity_summary": {
                "authors": dict(sorted_authors[:10]),
                "most_active_author": sorted_authors[0][0] if sorted_authors else "none",
                "most_changed_files": dict(sorted_files),
                "commits_per_day": len(commits) / days if days > 0 else 0
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при получении истории Git: {str(e)}",
            "error": str(e),
            "commits": []
        }

def _extract_keywords(text: str) -> List[str]:
    """Извлечение ключевых слов из текста маркера"""
    # Удаляем стоп-слова и извлекаем значимые слова
    stop_words = {"и", "в", "на", "с", "по", "для", "из", "от", "до", "за", "не", "что", "это", "как", "так"}
    
    words = text.lower().split()
    keywords = []
    
    for word in words:
        # Очищаем слово от знаков препинания
        clean_word = ''.join(c for c in word if c.isalnum())
        
        if (clean_word and len(clean_word) > 2 and 
            clean_word not in stop_words and
            not clean_word.isnumeric()):
            keywords.append(clean_word)
    
    return list(set(keywords))  # Удаляем дубликаты

# Экспортируем инструменты для импорта в main.py
__all__ = [
    'get_git_status_tool',
    'scan_last_commits_for_markers_tool',
    'get_git_history_tool'
]
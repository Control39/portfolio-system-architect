"""
Инструменты для работы с файловой системой
"""

import os
from pathlib import Path
from typing import Dict, Any
import fnmatch

from fastmcp import FastMCP

# Создаем экземпляр FastMCP для регистрации инструментов
# В реальности инструменты будут зарегистрированы в main.py
mcp = FastMCP("File Tools")

# Корень проекта (будет установлен при импорте)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

@mcp.tool()
def read_file_tool(path: str) -> str:
    """
    Чтение содержимого файла
    
    Аргументы:
        path: Путь к файлу (относительно корня проекта или абсолютный)
    
    Возвращает:
        Содержимое файла как строку
    """
    try:
        file_path = _resolve_path(path)
        if not file_path.exists():
            return f"Файл не найден: {path}"
        
        if not file_path.is_file():
            return f"Путь не является файлом: {path}"
        
        # Проверяем размер файла (не читаем слишком большие файлы)
        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10 MB
            return f"Файл слишком большой для чтения: {file_path.stat().st_size} байт"
        
        # Определяем кодировку
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Пробуем другие кодировки для бинарных файлов
            with open(file_path, 'rb') as f:
                content = f.read().decode('latin-1')
        
        return content
    
    except PermissionError:
        return f"Нет прав на чтение файла: {path}"
    except Exception as e:
        return f"Ошибка при чтении файла {path}: {str(e)}"

@mcp.tool()
def write_file_tool(path: str, content: str) -> Dict[str, Any]:
    """
    Запись содержимого в файл
    
    Аргументы:
        path: Путь к файлу (относительно корня проекта или абсолютный)
        content: Содержимое для записи
    
    Возвращает:
        Словарь с результатом операции
    """
    try:
        file_path = _resolve_path(path)
        
        # Создаем директории, если их нет
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Записываем файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Получаем информацию о файле
        file_size = file_path.stat().st_size
        
        return {
            "success": True,
            "message": f"Файл успешно записан: {path}",
            "path": str(file_path.relative_to(PROJECT_ROOT)),
            "size_bytes": file_size,
            "size_human": _human_readable_size(file_size)
        }
    
    except PermissionError:
        return {
            "success": False,
            "message": f"Нет прав на запись файла: {path}",
            "error": "PermissionError"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при записи файла {path}: {str(e)}",
            "error": str(e)
        }

@mcp.tool()
def list_files_tool(path: str = ".", recursive: bool = False) -> Dict[str, Any]:
    """
    Получение списка файлов и директорий
    
    Аргументы:
        path: Путь к директории (по умолчанию текущая директория)
        recursive: Рекурсивный обход (по умолчанию False)
    
    Возвращает:
        Словарь с информацией о файлах
    """
    try:
        dir_path = _resolve_path(path)
        
        if not dir_path.exists():
            return {
                "success": False,
                "message": f"Директория не найдена: {path}",
                "files": []
            }
        
        if not dir_path.is_dir():
            return {
                "success": False,
                "message": f"Путь не является директорией: {path}",
                "files": []
            }
        
        files = []
        
        if recursive:
            # Рекурсивный обход
            for root, dirs, filenames in os.walk(dir_path):
                # Пропускаем скрытые директории и виртуальные окружения
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', '.venv', 'venv']]
                
                for filename in filenames:
                    # Пропускаем скрытые файлы
                    if filename.startswith('.'):
                        continue
                    
                    file_path = Path(root) / filename
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    
                    try:
                        stat = file_path.stat()
                        files.append({
                            "name": filename,
                            "path": str(rel_path),
                            "type": "file",
                            "size_bytes": stat.st_size,
                            "size_human": _human_readable_size(stat.st_size),
                            "modified": stat.st_mtime
                        })
                    except (PermissionError, OSError):
                        # Пропускаем файлы без доступа
                        continue
        else:
            # Только текущий уровень
            for item in dir_path.iterdir():
                # Пропускаем скрытые файлы и директории
                if item.name.startswith('.'):
                    continue
                
                rel_path = item.relative_to(PROJECT_ROOT)
                
                try:
                    if item.is_file():
                        stat = item.stat()
                        files.append({
                            "name": item.name,
                            "path": str(rel_path),
                            "type": "file",
                            "size_bytes": stat.st_size,
                            "size_human": _human_readable_size(stat.st_size),
                            "modified": stat.st_mtime
                        })
                    elif item.is_dir():
                        files.append({
                            "name": item.name,
                            "path": str(rel_path),
                            "type": "directory",
                            "size_bytes": 0,
                            "size_human": "0 B",
                            "modified": 0
                        })
                except (PermissionError, OSError):
                    # Пропускаем элементы без доступа
                    continue
        
        # Сортируем: сначала директории, потом файлы, по имени
        files.sort(key=lambda x: (0 if x["type"] == "directory" else 1, x["name"].lower()))
        
        return {
            "success": True,
            "message": f"Найдено {len(files)} элементов в {path}",
            "path": str(dir_path.relative_to(PROJECT_ROOT)),
            "recursive": recursive,
            "count": len(files),
            "files": files[:100]  # Ограничиваем вывод 100 элементами
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при получении списка файлов {path}: {str(e)}",
            "error": str(e),
            "files": []
        }

@mcp.tool()
def search_files_tool(query: str, file_pattern: str = "*.py") -> Dict[str, Any]:
    """
    Поиск файлов по шаблону и содержимому
    
    Аргументы:
        query: Текст для поиска в содержимом файлов (пустая строка для поиска только по имени)
        file_pattern: Шаблон имени файла (например, "*.py", "*.md")
    
    Возвращает:
        Словарь с результатами поиска
    """
    try:
        results = []
        
        # Рекурсивный поиск по всему проекту
        for root, dirs, filenames in os.walk(PROJECT_ROOT):
            # Пропускаем скрытые директории и виртуальные окружения
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', '.venv', 'venv', 'node_modules']]
            
            for filename in filenames:
                # Проверяем шаблон имени файла
                if not fnmatch.fnmatch(filename, file_pattern):
                    continue
                
                file_path = Path(root) / filename
                
                # Пропускаем слишком большие файлы
                try:
                    if file_path.stat().st_size > 5 * 1024 * 1024:  # 5 MB
                        continue
                except (PermissionError, OSError):
                    continue
                
                # Если query пустой, добавляем все файлы по шаблону
                if not query.strip():
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    results.append({
                        "file": str(rel_path),
                        "matches": [],
                        "line_count": 0
                    })
                    continue
                
                # Ищем query в содержимом файла
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    matches = []
                    for i, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            matches.append({
                                "line": i,
                                "content": line.strip()[:100]  # Ограничиваем длину
                            })
                    
                    if matches:
                        rel_path = file_path.relative_to(PROJECT_ROOT)
                        results.append({
                            "file": str(rel_path),
                            "matches": matches[:10],  # Ограничиваем количество совпадений
                            "line_count": len(lines),
                            "match_count": len(matches)
                        })
                
                except (UnicodeDecodeError, PermissionError, OSError):
                    # Пропускаем файлы, которые не можем прочитать
                    continue
        
        return {
            "success": True,
            "message": f"Найдено {len(results)} файлов по запросу '{query}' с шаблоном '{file_pattern}'",
            "query": query,
            "file_pattern": file_pattern,
            "count": len(results),
            "results": results[:50]  # Ограничиваем вывод 50 результатами
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка при поиске файлов: {str(e)}",
            "error": str(e),
            "results": []
        }

def _resolve_path(path: str) -> Path:
    """Преобразование пути в абсолютный Path"""
    path_obj = Path(path)
    
    # Если путь абсолютный, используем как есть
    if path_obj.is_absolute():
        return path_obj
    
    # Если путь начинается с ./ или ../, разрешаем относительно корня проекта
    if path.startswith('./') or path.startswith('../'):
        return (PROJECT_ROOT / path).resolve()
    
    # Иначе считаем, что путь относительно корня проекта
    return (PROJECT_ROOT / path).resolve()

def _human_readable_size(size_bytes: int) -> str:
    """Преобразование размера в читаемый формат"""
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {units[i]}"

# Экспортируем инструменты для импорта в main.py
__all__ = [
    'read_file_tool',
    'write_file_tool',
    'list_files_tool',
    'search_files_tool'
]
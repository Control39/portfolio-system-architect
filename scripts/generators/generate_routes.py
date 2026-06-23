import csv
import json
import os
from datetime import datetime


def load_graph_schema(schema_path: str) -> dict:
    """Загружает базовую схему графа из JSON-файла."""
    with open(schema_path, encoding="utf-8") as file:
        return json.load(file)


def create_route_from_task(task: dict, schema: dict) -> dict:
    """Создает маршрут reasoning на основе задачи и схемы."""
    # Определяем цвет в зависимости от направления
    direction_colors = {
        "Аналитика": "#4285F4",
        "DevOps": "#FBBC05",
        "MLOps": "#34A853",
        "Документирование": "#A142F4",
        "ИИ": "#EA4335",
        "Системное мышление": "#F4B400",
    }
    color = direction_colors.get(task["direction"], "#CCCCCC")  # Серый по умолчанию

    # Создаем копию схемы для модификации
    route = schema.copy()

    # Обновляем узлы данными из задачи
    for node in route["nodes"]:
        if node["id"] == "source":
            node["label"] = task["source"]
        elif node["id"] == "task":
            node["label"] = task["task"]
            node["data"] = {"description": task["task"]}
        elif node["id"] == "tool":
            node["label"] = "Инструменты"
            node["data"] = {"description": task["tool"]}
        elif node["id"] == "direction":
            node["label"] = task["direction"]
            node["style"]["fill"] = color
        elif node["id"] == "confirmation":
            node["label"] = "Подтверждение"
            node["data"] = {"description": "Ожидается подтверждение решения"}
        elif node["id"] == "result":
            node["label"] = "Результат"
            node["data"] = {"description": "Интеграция решения в проект"}

    # Обновляем метаданные
    route["metadata"]["title"] = f"Reasoning-граф: {task['task']}"
    route["metadata"]["description"] = f"Автоматически сгенерированный маршрут для задачи: {task['task']}"
    route["metadata"]["updated"] = datetime.now().strftime("%Y-%m-%d")

    return route


def save_route(route: dict, output_dir: str, task_id: str):
    """Сохраняет сгенерированный маршрут в файл."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"route_{task_id}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(route, file, ensure_ascii=False, indent=2)
    print(f"Маршрут сохранен: {filepath}")


def main():
    # Пути к файлам
    tasks_csv = "tasks.csv"
    schema_json = "diagrams/reasoning/graph-schema.json"
    output_dir = "generated_routes"

    # Проверка существования файлов
    if not os.path.exists(tasks_csv):
        print(f"Ошибка: Файл {tasks_csv} не найден.")
        return
    if not os.path.exists(schema_json):
        print(f"Ошибка: Файл схемы {schema_json} не найден.")
        return

    # Загрузка схемы
    try:
        schema = load_graph_schema(schema_json)
    except Exception as e:
        print(f"Ошибка при загрузке схемы: {e}")
        return

    # Чтение задач и генерация маршрутов
    try:
        with open(tasks_csv, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                route = create_route_from_task(row, schema)
                save_route(route, output_dir, row["id"])
        print("Генерация маршрутов завершена.")
    except Exception as e:
        print(f"Ошибка при обработке CSV: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
check_ports.py - Проверка конфигурации портов и маршрутизации в docker-compose.yml

Цель:
- Обнаружить конфликты портов между сервисами
- Проверить корректность лейблов Traefik
- Убедиться, что каждый сервис имеет уникальный маршрут
- Проверить наличие PYTHONPATH (ADR-020)

Использование:
    python scripts/check_ports.py

Вывод:
    ✅ Если всё корректно
    ❌ Если обнаружены конфликты (exit code 1)
"""

import os
import re
import sys
from typing import Any

import yaml


def check_pythonpath() -> None:
    """
    Проверка наличия PYTHONPATH (ADR-020).

    Завершает работу с кодом 1, если PYTHONPATH не настроен или не содержит /app.
    """
    pythonpath = os.getenv("PYTHONPATH")

    if not pythonpath:
        print("❌ PYTHONPATH не настроен.")
        print("   Установите: export PYTHONPATH=/app:/app/src (Linux/Mac)")
        print("   или: $env:PYTHONPATH = '/app:/app/src' (Windows PowerShell)")
        print("   См. ADR-020: Separation of Architectural Layers")
        sys.exit(1)

    if "/app" not in pythonpath:
        print(f"❌ PYTHONPATH настроен некорректно: {pythonpath}")
        print("   Должен содержать '/app' и '/app/src'")
        print("   Правильный формат: PYTHONPATH=/app:/app/src")
        print("   См. ADR-020: Separation of Architectural Layers")
        sys.exit(1)

    # Проверка наличия /app/src (необязательно, но желательно)
    if "/app/src" not in pythonpath:
        print(f"⚠️  PYTHONPATH не содержит '/app/src': {pythonpath}")
        print("   Некоторые импорты могут не работать")
        print("   Рекомендуемый формат: PYTHONPATH=/app:/app/src")


def load_compose(path: str = "docker-compose.yml") -> dict[str, Any]:
    """Загрузить docker-compose.yml и распарсить YAML."""
    if not os.path.exists(path):
        print(f"❌ Файл {path} не найден")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        try:
            data: dict[str, Any] = yaml.safe_load(f)  # type: ignore[no-any-return]
            return data
        except yaml.YAMLError as e:
            print(f"❌ Ошибка парсинга YAML: {e}")
            sys.exit(1)


def parse_port_mapping(port_mapping: str) -> tuple[str, int]:
    """
    Парсинг формата порта: "host:container" или "port".

    Возвращает: (host_port, container_port)
    """
    if isinstance(port_mapping, int):
        return str(port_mapping), port_mapping

    port_str = str(port_mapping)

    # Учёт форматов: "8001:8000", "8001", "127.0.0.1:8001:8000"
    parts = port_str.split(":")

    if len(parts) == 1:
        # Просто порт: "8000"
        port = int(parts[0])
        return str(port), port
    if len(parts) == 2:
        # "host:container"
        host_port = int(parts[0])
        container_port = int(parts[1])
        return str(host_port), container_port
    if len(parts) == 3:
        # "ip:host:container"
        host_port = int(parts[1])
        container_port = int(parts[2])
        return str(host_port), container_port
    raise ValueError(f"Некорректный формат порта: {port_mapping}")


def check_port_conflicts(compose_data: dict[str, Any]) -> list[tuple[str, str, str]]:
    """
    Проверить конфликты host-портов между сервисами.

    Возвращает: список кортежей (host_port, service1, service2)
    """
    services = compose_data.get("services", {})
    port_map: dict[str, str] = {}
    conflicts: list[tuple[str, str, str]] = []

    for service_name, config in services.items():
        if not config:
            continue

        ports = config.get("ports", [])
        for port_mapping in ports:
            try:
                host_port, _ = parse_port_mapping(port_mapping)

                if host_port in port_map:
                    conflicts.append((host_port, port_map[host_port], service_name))
                else:
                    port_map[host_port] = service_name
            except (ValueError, IndexError) as e:
                print(f"⚠️  Ошибка парсинга порта для {service_name}: {port_mapping} ({e})")

    return conflicts


def extract_traefik_routes(compose_data: dict[str, Any]) -> dict[str, dict[str, str]]:
    """
    Извлечь маршруты Traefik из лейблов сервисов.

    Возвращает: {service_name: {'route': '/path', 'rule': '...'}}
    """
    services = compose_data.get("services", {})
    routes: dict[str, dict[str, str]] = {}

    for service_name, config in services.items():
        if not config:
            continue

        labels = config.get("labels", [])
        if isinstance(labels, list):
            labels = {label.split("=")[0]: "=".join(label.split("=")[1:]) for label in labels if "=" in label}

        # Ищем лейблы вида: traefik.http.routers.<name>.rule=...
        for label_key, label_value in labels.items():
            if "traefik.http.routers" in label_key and ".rule" in label_key:
                # Извлекаем маршрут из правила (например: PathPrefix(`/api/decision`))
                route_match = re.search(r'PathPrefix\([`\'"]([^`\'"]+)[`\'"]\)', label_value)
                if route_match:
                    routes[service_name] = {"route": route_match.group(1), "rule": label_value}
                    break

    return routes


def check_route_conflicts(routes: dict[str, dict[str, str]]) -> list[tuple[str, str, str]]:
    """
    Проверить конфликты маршрутов Traefik.

    Возвращает: список кортежей (route, service1, service2)
    """
    route_map: dict[str, str] = {}
    conflicts: list[tuple[str, str, str]] = []

    for service_name, info in routes.items():
        route = info.get("route", "")
        if not route:
            continue

        if route in route_map:
            conflicts.append((route, route_map[route], service_name))
        else:
            route_map[route] = service_name

    return conflicts


def check_container_port_conflicts(compose_data: dict[str, Any]) -> list[tuple[int, str, str]]:
    """
    Проверить конфликты container-портов (внутри Docker network).

    Возвращает: список кортежей (container_port, service1, service2)
    """
    services = compose_data.get("services", {})
    port_map: dict[int, str] = {}
    conflicts: list[tuple[int, str, str]] = []

    for service_name, config in services.items():
        if not config:
            continue

        ports = config.get("ports", [])
        for port_mapping in ports:
            try:
                _, container_port = parse_port_mapping(port_mapping)
                container_port_int = int(container_port)

                if container_port_int in port_map:
                    conflicts.append((container_port_int, port_map[container_port_int], service_name))
                else:
                    port_map[container_port_int] = service_name
            except (ValueError, IndexError):
                pass

    return conflicts


def check_pythonpath_in_compose(compose_data: dict[str, Any]) -> list[tuple[str, str]]:
    """
    Проверить наличие правильного PYTHONPATH в сервисах.

    Возвращает: список сервисов с неправильным PYTHONPATH
    """
    services = compose_data.get("services", {})
    issues: list[tuple[str, str]] = []

    for service_name, config in services.items():
        if not config:
            continue

        environment = config.get("environment", [])

        # Если environment не список, пробуем преобразовать
        if isinstance(environment, dict):
            pythonpath = environment.get("PYTHONPATH", "")
            if pythonpath and pythonpath != "/app:/app/src":
                issues.append((service_name, pythonpath))
        elif isinstance(environment, list):
            for env_var in environment:
                if isinstance(env_var, str) and env_var.startswith("PYTHONPATH="):
                    pythonpath = env_var.split("=", 1)[1]
                    if pythonpath != "/app:/app/src":
                        issues.append((service_name, pythonpath))
                    break

    return issues


def print_report(
    port_conflicts: list[tuple[str, str, str]],
    route_conflicts: list[tuple[str, str, str]],
    container_port_conflicts: list[tuple[int, str, str]],
    routes: dict[str, dict[str, str]],
    all_services: list[str],
    pythonpath_issues: list[tuple[str, str]],
):
    """Вывести отчёт о проверке."""
    print("\n" + "=" * 70)
    print("🔍 ОТЧЁТ ПРОВЕРКИ КОНФИГУРАЦИИ DOCKER COMPOSE")
    print("=" * 70)
    print(f"📊 Всего сервисов в файле: {len(all_services)}")

    # Предупреждение об именовании
    underscore_services = [s for s in all_services if "_" in s]
    if underscore_services:
        print("\n⚠️  ВНИМАНИЕ: Найдены сервисы с '_' (рекомендуется использовать '-'):")
        for s in underscore_services:
            print(f"   • {s}")

    # PYTHONPATH проверка
    print("\n📊 PYTHONPATH (ADR-020):")
    if pythonpath_issues:
        print("❌ Обнаружены проблемы с PYTHONPATH:")
        for service, current_path in pythonpath_issues:
            print(f"   ⚠️  {service}: {current_path}")
            print("       Должно быть: PYTHONPATH=/app:/app/src")
    else:
        print("✅ Все сервисы имеют правильный PYTHONPATH=/app:/app/src")

    # Host-порты
    print("\n📊 Host-порты (внешний доступ):")
    if port_conflicts:
        print("❌ Обнаружены КОНФЛИКТЫ:")
        for port, svc1, svc2 in port_conflicts:
            print(f"   ⚠️  Порт {port}: {svc1} vs {svc2}")
    else:
        print("✅ Конфликтов host-портов нет")

    # Container-порты
    print("\n📊 Container-порты (внутри Docker):")
    if container_port_conflicts:
        print("❌ Обнаружены КОНФЛИКТЫ:")
        for port, svc1, svc2 in container_port_conflicts:
            print(f"   ⚠️  Порт {port}: {svc1} vs {svc2}")
    else:
        print("✅ Конфликтов container-портов нет")

    # Traefik маршруты
    print("\n📊 Traefik маршруты (только HTTP-сервисы):")
    if route_conflicts:
        print("❌ Обнаружены КОНФЛИКТЫ маршрутов:")
        for route, svc1, svc2 in route_conflicts:
            print(f"   ⚠️  Маршрут {route}: {svc1} vs {svc2}")
    else:
        print("✅ Конфликтов маршрутов нет")

    # Полный список
    print("\n📋 Полное распределение:")
    for service in sorted(all_services):
        route_info = routes.get(service, {})
        route = route_info.get("route", "Нет HTTP-маршрута (внутренний сервис)")
        print(f"   • {service:<25} → {route}")

    print("\n" + "=" * 70)


def main():
    """Основная функция."""
    import argparse

    parser = argparse.ArgumentParser(description="Проверка конфигурации портов")
    parser.add_argument(
        "--skip-pythonpath", action="store_true", help="Пропустить проверку PYTHONPATH (для pre-commit/CI)"
    )
    parser.add_argument("--strict", action="store_true", help="Строгий режим (для CI)")
    args = parser.parse_args()

    print("🔍 Проверка конфигурации Docker Compose...")
    print("📁 Файл: docker-compose.yml")

    # ✅ Проверка PYTHONPATH (ADR-020) — пропускается в pre-commit/CI
    if not args.skip_pythonpath:
        check_pythonpath()
    else:
        print("⏭️  PYTHONPATH проверка пропущена (--skip-pythonpath)")

    # Загрузка
    compose_data = load_compose()

    # Проверки
    port_conflicts = check_port_conflicts(compose_data)
    container_port_conflicts = check_container_port_conflicts(compose_data)
    routes = extract_traefik_routes(compose_data)
    route_conflicts = check_route_conflicts(routes)
    pythonpath_issues = check_pythonpath_in_compose(compose_data)

    # Список всех сервисов
    all_services = list(compose_data.get("services", {}).keys())

    # Отчёт
    print_report(port_conflicts, route_conflicts, container_port_conflicts, routes, all_services, pythonpath_issues)

    # Итог
    has_errors = bool(port_conflicts or route_conflicts or container_port_conflicts or pythonpath_issues)

    if has_errors:
        print("❌ ПРОВЕРКА НЕ УСПЕШНА: обнаружены конфликты")
        sys.exit(1)
    else:
        print("✅ ПРОВЕРКА УСПЕШНА: конфликтов не обнаружено")
        sys.exit(0)


if __name__ == "__main__":
    main()

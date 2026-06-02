#!/usr/bin/env python3
"""
check_ports.py - Проверка конфигурации портов и маршрутизации
в docker-compose*.yml и Kubernetes Ingress

Цель:
- Обнаружить конфликты портов между сервисами
- Проверить корректность лейблов Traefik / Ingress
- Убедиться, что каждый маршрут уникален (даже между Docker и K8s)

Поддерживает:
- docker-compose.yml, docker-compose.dev.yml и др.
- Kubernetes Ingress в deployment/k8s/**/ingress.yaml или *-ingress.yaml

Использование:
    python scripts/check_ports.py [--strict]

Флаги:
    --strict    Возвращать exit 1, если нет ни одного файла (для CI)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set

import yaml


def find_compose_files() -> List[Path]:
    """Найти все файлы docker-compose*.yml в корне проекта."""
    return sorted(Path(".").glob("docker-compose*.yml"))


def find_ingress_files() -> List[Path]:
    """Найти все ingress-файлы в k8s-директориях."""
    patterns = [
        "deployment/k8s/**/*ingress*.yaml",
        "deployment/k8s/**/ingress.yaml",
        "k8s/**/*ingress*.yaml",
        "manifests/**/*ingress*.yaml",
    ]
    files = []
    for pattern in patterns:
        files.extend(Path(".").glob(pattern))
    return sorted(set(files))


def load_yaml(path: Path) -> Dict[str, Any]:
    """Загрузить и распарсить YAML-файл."""
    if not path.exists():
        print(f"❌ Файл не существует: {path}")
        return {}

    try:
        with open(path, encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f) or {}
            return data
    except yaml.YAMLError as e:
        print(f"❌ Ошибка парсинга YAML в {path}: {e}")
        return {}


def parse_port_mapping(port_mapping: str) -> Tuple[str, int]:
    """
    Парсинг формата порта: "host:container" или "port".

    Возвращает: (host_port, container_port)
    """
    if isinstance(port_mapping, int):
        return str(port_mapping), port_mapping

    port_str = str(port_mapping)
    parts = port_str.split(":")

    if len(parts) == 1:
        port = int(parts[0])
        return str(port), port
    if len(parts) == 2:
        host_port = int(parts[0])
        container_port = int(parts[1])
        return str(host_port), container_port
    if len(parts) == 3:
        host_port = int(parts[1])
        container_port = int(parts[2])
        return str(host_port), container_port
    raise ValueError(f"Некорректный формат порта: {port_mapping}")


def check_port_conflicts(
    compose_data: Dict[str, Any], file_name: str
) -> List[Tuple[str, str, str, str]]:
    """Проверить конфликты host-портов."""
    services = compose_data.get("services", {})
    conflicts: List[Tuple[str, str, str, str]] = []
    port_map: Dict[str, Tuple[str, str]] = {}

    for service_name, config in services.items():
        if not config:
            continue
        ports = config.get("ports", [])
        for port_mapping in ports:
            try:
                host_port, _ = parse_port_mapping(port_mapping)
                key = f"{file_name}:{service_name}"
                if host_port in port_map:
                    prev_service, prev_file = port_map[host_port]
                    conflicts.append((host_port, prev_service, prev_file, service_name, file_name))
                else:
                    port_map[host_port] = (service_name, file_name)
            except (ValueError, IndexError) as e:
                print(
                    f"⚠️  Ошибка парсинга порта для {service_name} в {file_name}: {port_mapping} ({e})"
                )
    return conflicts


def extract_traefik_routes(
    compose_data: Dict[str, Any], file_name: str
) -> Dict[str, Dict[str, str]]:
    """Извлечь маршруты Traefik из docker-compose labels."""
    services = compose_data.get("services", {})
    routes: Dict[str, Dict[str, str]] = {}

    for service_name, config in services.items():
        if not config:
            continue
        labels = config.get("labels", [])
        if isinstance(labels, list):
            label_dict = {}
            seen_keys: Set[str] = set()
            for label in labels:
                if "=" not in label:
                    continue
                key, value = label.split("=", 1)
                if key in seen_keys:
                    print(f"⚠️  Дублирование лейбла '{key}' в сервисе {service_name} ({file_name})")
                seen_keys.add(key)
                label_dict[key] = value
            labels = label_dict

        for label_key, label_value in labels.items():
            if "traefik.http.routers" in label_key and ".rule" in label_key:
                route_match = (
                    re.search(r'PathPrefix\([`\'"]([^`\'"]+)[`\'"]\)', label_value)
                    or re.search(r'Path\([`\'"]([^`\'"]+)[`\'"]\)', label_value)
                    or re.search(r'Host\([`\'"]([^`\'"]+)[`\'"]\)', label_value)
                )
                if route_match:
                    route = route_match.group(1)
                    routes[service_name] = {
                        "route": route,
                        "rule": label_value,
                        "file": file_name,
                        "source": "docker-compose",
                    }
                    break
    return routes


def extract_ingress_routes(
    ingress_data: Dict[str, Any], file_name: str
) -> Dict[str, Dict[str, str]]:
    """Извлечь маршруты из Kubernetes Ingress."""
    routes: Dict[str, Dict[str, str]] = {}
    items = ingress_data.get("items", []) if ingress_data.get("kind") == "List" else [ingress_data]

    for item in items:
        if item.get("kind") != "Ingress":
            continue
        metadata = item.get("metadata", {})
        name = metadata.get("name", "unknown-ingress")
        annotations = metadata.get("annotations", {})
        spec = item.get("spec", {})

        rules = spec.get("rules", [])
        for rule in rules:
            host = rule.get("host", "").strip()
            if not host:
                continue
            http = rule.get("http")
            if not http:
                continue
            paths = http.get("paths", [])
            for path_obj in paths:
                path = path_obj.get("path", "/").strip()
                # Пример: host → "api.example.com", path → "/v1"
                full_route = f"https://{host}{path}".rstrip("/")
                routes[f"{name}-{host}"] = {
                    "route": full_route,
                    "rule": f"host={host}, path={path}",
                    "file": file_name,
                    "source": "k8s-ingress",
                }

        # Поддержка simple fanout (без host)
        default_backend = spec.get("defaultBackend")
        if default_backend and not rules:
            path = "/"
            host = annotations.get("nginx.ingress.kubernetes.io/server-alias", "default.local")
            full_route = f"https://{host}{path}".rstrip("/")
            routes[f"{name}-default"] = {
                "route": full_route,
                "rule": f"default → {host}",
                "file": file_name,
                "source": "k8s-ingress",
            }

    return routes


def check_route_conflicts(routes: Dict[str, Dict[str, str]]) -> List[Tuple[str, str, str]]:
    """Проверить конфликты маршрутов (независимо от источника)."""
    route_map: Dict[str, str] = {}
    conflicts: List[Tuple[str, str, str]] = []

    for service, info in routes.items():
        route = info.get("route", "")
        if not route:
            continue
        if route in route_map:
            conflicts.append((route, route_map[route], service))
        else:
            route_map[route] = service

    return conflicts


def check_container_port_conflicts(
    compose_data: Dict[str, Any], file_name: str
) -> List[Tuple[int, str, str, str]]:
    """Проверить конфликты container-портов."""
    services = compose_data.get("services", {})
    conflicts: List[Tuple[int, str, str, str]] = []
    port_map: Dict[int, Tuple[str, str]] = {}

    for service_name, config in services.items():
        if not config:
            continue
        ports = config.get("ports", [])
        for port_mapping in ports:
            try:
                _, container_port = parse_port_mapping(port_mapping)
                if container_port in port_map:
                    prev_service, prev_file = port_map[container_port]
                    conflicts.append(
                        (container_port, prev_service, prev_file, service_name, file_name)
                    )
                else:
                    port_map[container_port] = (service_name, file_name)
            except (ValueError, IndexError):
                pass
    return conflicts


def print_report(
    all_port_conflicts: List[Tuple[str, str, str, str, str]],
    all_route_conflicts: List[Tuple[str, str, str]],
    all_container_conflicts: List[Tuple[int, str, str, str, str]],
    all_routes: Dict[str, Dict[str, str]],
    processed_compose: List[str],
    processed_ingress: List[str],
):
    """Вывести сводный отчёт."""
    print("\n" + "=" * 70)
    print("🔍 СВОДНАЯ ПРОВЕРКА МАРШРУТИЗАЦИИ")
    print("=" * 70)

    total_files = len(processed_compose) + len(processed_ingress)
    if total_files == 0:
        print("❌ Не найдено ни одного docker-compose* или ingress-файла")
        return

    if processed_compose:
        print(f"📁 docker-compose файлы: {len(processed_compose)}")
        for f in processed_compose:
            print(f"   • {f}")

    if processed_ingress:
        print(f"☸️  Ingress файлы: {len(processed_ingress)}")
        for f in processed_ingress:
            print(f"   • {f}")

    # Host-порты
    print("\n📊 Host-порты (Docker):")
    if all_port_conflicts:
        print("❌ КОНФЛИКТЫ НАЙДЕНЫ:")
        for port, svc1, file1, svc2, file2 in all_port_conflicts:
            print(f"   ⚠️  Порт {port}: {svc1} ({file1}) vs {svc2} ({file2})")
    else:
        print("✅ Конфликтов host-портов нет")

    # Container-порты
    print("\n📦 Container-порты (Docker):")
    if all_container_conflicts:
        print("❌ КОНФЛИКТЫ НАЙДЕНЫ:")
        for port, svc1, file1, svc2, file2 in all_container_conflicts:
            print(f"   ⚠️  Порт {port}: {svc1} ({file1}) vs {svc2} ({file2})")
    else:
        print("✅ Конфликтов container-портов нет")

    # Маршруты (Traefik + Ingress)
    print("\n🌐 Маршруты (Traefik + Ingress):")
    if all_route_conflicts:
        print("❌ КОНФЛИКТЫ МАРШРУТОВ:")
        for route, svc1, svc2 in all_route_conflicts:
            print(f"   ⚠️  {route}: {svc1} vs {svc2}")
    else:
        print("✅ Конфликтов маршрутов нет")

    # Все маршруты
    print("\n📋 Все маршруты:")
    if all_routes:
        for service, info in sorted(all_routes.items(), key=lambda x: x[1].get("route", "")):
            src = "🐳" if info["source"] == "docker-compose" else "☸️ "
            file_part = f" ({info['file']})"
            print(f"   {src} {service:25} → {info.get('route', 'N/A')}{file_part}")
    else:
        print("   ⚠️  Маршруты не найдены")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Проверка конфигурации портов и маршрутов")
    parser.add_argument("--strict", action="store_true", help="Падать, если нет файлов")
    args = parser.parse_args()

    # Поиск файлов
    compose_files = find_compose_files()
    ingress_files = find_ingress_files()

    if args.strict and not (compose_files or ingress_files):
        print("❌ Не найдено ни одного docker-compose* или ingress-файла (--strict)")
        sys.exit(1)

    if not compose_files and not ingress_files:
        print("ℹ️  Нет файлов для проверки — пропуск")
        sys.exit(0)

    # Сбор данных
    all_port_conflicts: List[Tuple[str, str, str, str, str]] = []
    all_container_conflicts: List[Tuple[int, str, str, str, str]] = []
    all_routes: Dict[str, Dict[str, str]] = {}

    # Docker Compose
    for file_path in compose_files:
        print(f"🔍 Загрузка docker-compose: {file_path}")
        data = load_yaml(file_path)
        if not data:
            continue
        all_port_conflicts.extend(check_port_conflicts(data, str(file_path)))
        all_container_conflicts.extend(check_container_port_conflicts(data, str(file_path)))
        routes = extract_traefik_routes(data, str(file_path))
        all_routes.update(routes)

    # K8s Ingress
    for file_path in ingress_files:
        print(f"☸️  Загрузка Ingress: {file_path}")
        data = load_yaml(file_path)
        if not data:
            continue
        routes = extract_ingress_routes(data, str(file_path))
        all_routes.update(routes)

    all_route_conflicts = check_route_conflicts(all_routes)

    # Отчёт
    processed_compose = [str(f) for f in compose_files]
    processed_ingress = [str(f) for f in ingress_files]
    print_report(
        all_port_conflicts,
        all_route_conflicts,
        all_container_conflicts,
        all_routes,
        processed_compose,
        processed_ingress,
    )

    # Итог
    has_errors = bool(all_port_conflicts or all_route_conflicts or all_container_conflicts)
    if has_errors:
        print("❌ ПРОВЕРКА НЕ УСПЕШНА: обнаружены конфликты")
        sys.exit(1)
    else:
        print("✅ ПРОВЕРКА УСПЕШНА: всё в порядке")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Скрипт для синхронизации файлов между двумя проектами на основе хэшей.
Сравнивает содержимое файлов и копирует отсутствующие или более новые версии.
"""

import hashlib
import os
import shutil
import sys
import time


def calculate_file_hash(filepath, chunk_size=8192):
    """Вычисляет SHA-256 хэш файла."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"  ⚠️  Ошибка чтения {filepath}: {e}")
        return None


def scan_directory(directory, relative_to=None):
    """Сканирует директорию рекурсивно, возвращает словарь:
    относительный_путь -> (полный_путь, хэш, размер, время_модификации)
    """
    if relative_to is None:
        relative_to = directory
    file_map = {}
    for root, dirs, files in os.walk(directory):
        # Пропускаем скрытые папки
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.startswith("."):
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, relative_to)
            try:
                stat = os.stat(full_path)
                size = stat.st_size
                mtime = stat.st_mtime
                file_hash = calculate_file_hash(full_path)
                if file_hash is None:
                    continue
                file_map[rel_path] = {
                    "full_path": full_path,
                    "hash": file_hash,
                    "size": size,
                    "mtime": mtime,
                }
            except OSError as e:
                print(f"  ⚠️  Ошибка доступа к {full_path}: {e}")
    return file_map


def compare_directories(source_map, target_map):
    """Сравнивает два словаря файлов.
    Возвращает:
      - missing: файлы, которые есть в source, но отсутствуют в target
      - different: файлы с одинаковым путём, но разным хэшем
      - extra: файлы, которые есть в target, но отсутствуют в source (опционально)
    """
    missing = {}
    different = {}
    extra = {}

    # Проверяем файлы из source
    for rel_path, src_info in source_map.items():
        if rel_path not in target_map:
            missing[rel_path] = src_info
        else:
            tgt_info = target_map[rel_path]
            if src_info["hash"] != tgt_info["hash"]:
                different[rel_path] = {
                    "source": src_info,
                    "target": tgt_info,
                }

    # Файлы, которые есть только в target (возможно, устаревшие)
    for rel_path, tgt_info in target_map.items():
        if rel_path not in source_map:
            extra[rel_path] = tgt_info

    return missing, different, extra


def copy_file(src_info, target_dir, dry_run=False, backup=True):
    """Копирует файл из source в target с сохранением структуры папок."""
    rel_path = src_info.get("_rel_path")  # будет установлено вызывающим кодом
    src_path = src_info["full_path"]
    dest_path = os.path.join(target_dir, rel_path)

    if dry_run:
        print(f"  [DRY RUN] Копирование: {rel_path} -> {dest_path}")
        return True

    # Создаём целевую папку, если её нет
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # Если файл уже существует, создаём резервную копию
    if backup and os.path.exists(dest_path):
        backup_path = dest_path + f".backup_{int(time.time())}"
        try:
            shutil.copy2(dest_path, backup_path)
            print(f"  📦 Создан бэкап: {backup_path}")
        except Exception as e:
            print(f"  ⚠️  Не удалось создать бэкап: {e}")

    try:
        shutil.copy2(src_path, dest_path)
        print(f"  ✅ Скопирован: {rel_path}")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка копирования {rel_path}: {e}")
        return False


def sync_component(source_dir, target_dir, component_name, dry_run=False, auto_confirm=False):
    """Синхронизирует один компонент (поддиректорию) из source в target."""
    print(f"\n🔍 Синхронизация компонента: {component_name}")
    print(f"   Источник: {source_dir}")
    print(f"   Цель: {target_dir}")

    if not os.path.exists(source_dir):
        print(f"❌ Источник не существует: {source_dir}")
        return False
    if not os.path.exists(target_dir):
        print(f"⚠️  Целевая директория не существует, создаём: {target_dir}")
        if not dry_run:
            os.makedirs(target_dir, exist_ok=True)

    # Сканируем
    print("📊 Сканирование исходной директории...")
    source_map = scan_directory(source_dir, relative_to=source_dir)
    print(f"   Найдено файлов: {len(source_map)}")

    print("📊 Сканирование целевой директории...")
    target_map = scan_directory(target_dir, relative_to=target_dir)
    print(f"   Найдено файлов: {len(target_map)}")

    # Сравниваем
    missing, different, extra = compare_directories(source_map, target_map)

    print("\n📋 Результаты сравнения:")
    print(f"   Отсутствуют в цели: {len(missing)}")
    print(f"   Различаются по содержимому: {len(different)}")
    print(f"   Лишние в цели (нет в источнике): {len(extra)}")

    # Добавляем относительный путь в информацию для удобства
    for rel_path, info in missing.items():
        info["_rel_path"] = rel_path
    for rel_path, diff in different.items():
        diff["source"]["_rel_path"] = rel_path

    # Показываем детали
    if missing:
        print("\n📁 Файлы для копирования (отсутствуют в цели):")
        for rel_path in list(missing.keys())[:10]:
            print(f"   • {rel_path}")
        if len(missing) > 10:
            print(f"   ... и ещё {len(missing) - 10} файлов")

    if different:
        print("\n🔄 Файлы с различиями (возможно, нужна перезапись):")
        for rel_path in list(different.keys())[:10]:
            src_size = different[rel_path]["source"]["size"]
            tgt_size = different[rel_path]["target"]["size"]
            print(f"   • {rel_path} (размеры: {src_size} vs {tgt_size} байт)")
        if len(different) > 10:
            print(f"   ... и ещё {len(different) - 10} файлов")

    if extra:
        print("\n🗑️  Файлы, которые есть только в цели (возможно, устарели):")
        for rel_path in list(extra.keys())[:10]:
            print(f"   • {rel_path}")
        if len(extra) > 10:
            print(f"   ... и ещё {len(extra) - 10} файлов")

    # Запрашиваем подтверждение, если не dry_run и не auto_confirm
    total_actions = len(missing) + len(different)
    if total_actions == 0:
        print("\n✨ Нет изменений для синхронизации.")
        return True

    if not dry_run and not auto_confirm:
        print(f"\n📦 Будет выполнено действий: {total_actions}")
        response = input("   Продолжить синхронизацию? (y/n): ").lower()
        if response not in ("y", "yes", "д", "да"):
            print("❌ Синхронизация отменена.")
            return False

    # Копируем отсутствующие файлы
    success_count = 0
    if missing:
        print("\n📤 Копирование отсутствующих файлов...")
        for _rel_path, info in missing.items():
            if copy_file(info, target_dir, dry_run=dry_run):
                success_count += 1

    # Перезаписываем различающиеся файлы (опционально)
    if different:
        print("\n🔄 Перезапись файлов с различиями...")
        for _rel_path, diff in different.items():
            src_info = diff["source"]
            if copy_file(src_info, target_dir, dry_run=dry_run):
                success_count += 1

    print(
        f"\n✅ Синхронизация завершена. Успешно обработано файлов: {success_count}/{total_actions}"
    )
    return success_count == total_actions


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Синхронизация проектов по хэшам файлов")
    parser.add_argument("source", help="Исходная директория (my-ecosystem-FINAL)")
    parser.add_argument("target", help="Целевая директория (portfolio-system-architect)")
    parser.add_argument("--component", help="Имя компонента (подпапка) для синхронизации")
    parser.add_argument(
        "--dry-run", action="store_true", help="Показать план без реальных действий"
    )
    parser.add_argument("--all", action="store_true", help="Синхронизировать все компоненты")
    parser.add_argument("--yes", action="store_true", help="Автоматически подтверждать действия")

    args = parser.parse_args()

    source_root = os.path.abspath(args.source)
    target_root = os.path.abspath(args.target)

    if not os.path.exists(source_root):
        print(f"❌ Исходная директория не существует: {source_root}")
        return 1
    if not os.path.exists(target_root):
        print(f"⚠️  Целевая директория не существует: {target_root}")
        if not args.dry_run:
            os.makedirs(target_root, exist_ok=True)

    # Если указан компонент, синхронизируем только его
    if args.component:
        source_dir = os.path.join(source_root, args.component)
        target_dir = os.path.join(target_root, args.component)
        sync_component(
            source_dir,
            target_dir,
            args.component,
            dry_run=args.dry_run,
            auto_confirm=args.yes,
        )
    elif args.all:
        # Находим все поддиректории в source, которые являются компонентами
        components = []
        for item in os.listdir(source_root):
            if os.path.isdir(os.path.join(source_root, item)):
                components.append(item)
        print(f"🔍 Найдено компонентов: {len(components)}")
        for comp in components:
            sync_component(
                os.path.join(source_root, comp),
                os.path.join(target_root, comp),
                comp,
                dry_run=args.dry_run,
                auto_confirm=args.yes,
            )
    else:
        print("❌ Укажите --component или --all")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

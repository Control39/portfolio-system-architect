#!/usr/bin/env python3
"""
Простой анализатор рабочего пространства
"""

import json
from datetime import datetime
from pathlib import Path


def analyze_desktop():
    """Анализировать рабочий стол"""
    desktop_path = Path("C:/Users/Z/Desktop")

    if not desktop_path.exists():
        print("Рабочий стол не найден")
        return

    files = []
    total_size = 0

    for item in desktop_path.iterdir():
        if item.is_file():
            size = item.stat().st_size
            total_size += size

            files.append(
                {
                    "name": item.name,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d"),
                    "extension": item.suffix.lower(),
                }
            )

    # Сортировка по размеру
    files.sort(key=lambda x: x["size_mb"], reverse=True)

    # Анализ по расширениям
    extensions = {}
    for f in files:
        ext = f["extension"] or "no_extension"
        if ext not in extensions:
            extensions[ext] = {"count": 0, "total_size": 0}
        extensions[ext]["count"] += 1
        extensions[ext]["total_size"] += f["size_mb"]

    # Генерация отчета
    report = []
    report.append("=" * 60)
    report.append("АНАЛИЗ РАБОЧЕГО СТОЛА")
    report.append("=" * 60)
    report.append(f"Всего файлов: {len(files)}")
    report.append(f"Общий размер: {round(total_size / (1024**3), 2)} GB")
    report.append("")

    report.append("ТОП-10 самых больших файлов:")
    for i, f in enumerate(files[:10], 1):
        report.append(f"{i:2}. {f['name'][:40]:40} {f['size_mb']:6.1f} MB ({f['modified']})")

    report.append("")
    report.append("РАСПРЕДЕЛЕНИЕ ПО РАСШИРЕНИЯМ:")
    for ext, data in sorted(extensions.items(), key=lambda x: x[1]["total_size"], reverse=True):
        if data["count"] > 0:
            report.append(f"  {ext:10} {data['count']:3} файлов, {data['total_size']:6.1f} MB")

    report.append("")
    report.append("РЕКОМЕНДАЦИИ:")

    # Рекомендации
    if len(files) > 50:
        report.append("1. Слишком много файлов на рабочем столе (>50)")
        report.append("   Рекомендация: переместить в папки по категориям")

    large_files = [f for f in files if f["size_mb"] > 100]
    if large_files:
        report.append("2. Найдены большие файлы (>100 MB):")
        for f in large_files[:3]:
            report.append(f"   - {f['name']} ({f['size_mb']} MB)")
        report.append("   Рекомендация: переместить в папку Large_Files/")

    exe_count = sum(1 for f in files if f["extension"] in [".exe", ".msi"])
    if exe_count > 5:
        report.append(f"3. Много установщиков ({exe_count})")
        report.append("   Рекомендация: переместить в папку Installers/")

    zip_count = sum(1 for f in files if f["extension"] in [".zip", ".rar", ".7z"])
    if zip_count > 3:
        report.append(f"4. Много архивов ({zip_count})")
        report.append("   Рекомендация: распаковать или переместить в Archives/")

    report.append("")
    report.append("ПЛАН ОРГАНИЗАЦИИ:")
    report.append("1. Создать папки: Documents, Projects, Archives, Installers, Images")
    report.append("2. Переместить файлы по категориям")
    report.append("3. Удалить временные файлы (.tmp, ~)")
    report.append("4. Проверить дубликаты")
    report.append("5. Настроить автоматическую сортировку")

    # Сохранить отчет
    report_text = "\n".join(report)
    print(report_text)

    # Сохранить в файл
    output_dir = Path(".codeassistant/teacher/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "desktop_analysis.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"\nОтчет сохранен: {report_path}")

    # Сохранить данные в JSON
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(files),
        "total_size_gb": round(total_size / (1024**3), 2),
        "files": files[:50],  # Ограничим
        "extensions": extensions,
        "recommendations": ["organize_files", "create_folders", "remove_temporaries"],
    }

    json_path = output_dir / "desktop_analysis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Данные сохранены: {json_path}")

    return data


def create_organization_script():
    """Создать скрипт для организации"""
    script = """@echo off
REM Скрипт организации рабочего стола
echo Организация рабочего стола...

REM Создание папок
mkdir "Documents" 2>nul
mkdir "Projects" 2>nul
mkdir "Archives" 2>nul
mkdir "Installers" 2>nul
mkdir "Images" 2>nul
mkdir "Backups" 2>nul
mkdir "Temporary" 2>nul

echo Папки созданы
echo.
echo Перемещение файлов...

REM Перемещение по расширениям (пример)
REM move *.pdf "Documents" 2>nul
REM move *.doc* "Documents" 2>nul
REM move *.txt "Documents" 2>nul
REM move *.md "Documents" 2>nul

REM move *.png "Images" 2>nul
REM move *.jpg "Images" 2>nul
REM move *.jpeg "Images" 2>nul

REM move *.zip "Archives" 2>nul
REM move *.rar "Archives" 2>nul
REM move *.7z "Archives" 2>nul

REM move *.exe "Installers" 2>nul
REM move *.msi "Installers" 2>nul

echo.
echo Очистка временных файлов...
del *.tmp 2>nul
del ~*.* 2>nul

echo.
echo Готово! Рабочий стол организован.
pause
"""

    script_path = Path(".codeassistant/teacher/scripts/organize_desktop.bat")
    with open(script_path, "w", encoding="cp1251") as f:
        f.write(script)

    print(f"Скрипт создан: {script_path}")
    return script_path


def main():
    """Основная функция"""
    print("Анализ рабочего пространства...")
    data = analyze_desktop()

    print("\nСоздание скрипта организации...")
    script_path = create_organization_script()

    print("\n" + "=" * 60)
    print("СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Просмотрите отчет в .codeassistant/teacher/reports/")
    print("2. Запустите скрипт: " + str(script_path))
    print("3. Проверьте результат")
    print("4. Настройте автоматическую организацию")
    print("=" * 60)


if __name__ == "__main__":
    main()

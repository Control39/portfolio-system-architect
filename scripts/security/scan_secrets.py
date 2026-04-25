#!/usr/bin/env python3
"""Сканирование проекта на наличие потенциальных секретов (ключей API, паролей, токенов).
Использует detect-secrets для создания базового файла .secrets.baseline и последующего сравнения.
"""
import os
import subprocess
import sys
from pathlib import Path


def run_detect_secrets_scan() -> int:
    """Запуск detect-secrets scan и вывод результатов."""
    cmd = [
        sys.executable, "-m", "detect_secrets", "scan",
        "--all-files",
        "--exclude-files", "*.secrets.baseline",
        "--exclude-files", "*.pyc",
        "--exclude-files", "*.log",
        "--exclude-files", "node_modules/",
        "--exclude-files", ".git/",
        "--exclude-files", ".venv/",
        "--exclude-files", "__pycache__/",
        "--exclude-files", "coverage_html/",
        "--exclude-files", "*.csv",
        "--exclude-files", "*.json",
        "--exclude-files", "*.yaml",
        "--exclude-files", "*.yml",
        "--exclude-files", "*.txt",
        "--exclude-files", "*.md",
        "--exclude-files", "*.html",
        "--exclude-files", "*.sql",
        "--exclude-files", "*.db",
        "--exclude-files", "*.pem",
        "--exclude-files", "*.key",
        "--exclude-files", "*.cer",
        "--exclude-files", "*.crt",
    ]
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode != 0:
            print("Detect-secrets scan failed:")
            print(result.stderr)
            return result.returncode
        # Вывод результатов
        if result.stdout:
            print("Potential secrets found:")
            print(result.stdout)
        else:
            print("No new secrets found.")
        return 0
    except FileNotFoundError:
        print("Error: detect-secrets not installed. Install via 'pip install detect-secrets'")
        return 1

def create_baseline() -> int:
    """Создание базового файла .secrets.baseline для отслеживания известных секретов."""
    cmd = [sys.executable, "-m", "detect_secrets", "scan", "--all-files", "--update", ".secrets.baseline"]
    try:
        print("Creating/updating .secrets.baseline...")
        subprocess.run(cmd, check=True, cwd=os.getcwd())
        print("Baseline created/updated.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Failed to create baseline: {e}")
        return 1

def audit_baseline() -> int:
    """Аудит существующего baseline файла (ручная проверка)."""
    if not Path(".secrets.baseline").exists():
        print("No .secrets.baseline found. Run with --create-baseline first.")
        return 1
    cmd = [sys.executable, "-m", "detect_secrets", "audit", ".secrets.baseline"]
    try:
        subprocess.run(cmd, check=True, cwd=os.getcwd())
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Audit failed: {e}")
        return 1

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Security secrets scanner")
    parser.add_argument("--scan", action="store_true", help="Run scan for secrets")
    parser.add_argument("--create-baseline", action="store_true", help="Create/update baseline file")
    parser.add_argument("--audit", action="store_true", help="Audit existing baseline")
    args = parser.parse_args()

    if not (args.scan or args.create_baseline or args.audit):
        parser.print_help()
        sys.exit(1)

    exit_code = 0
    if args.create_baseline:
        exit_code = create_baseline()
    if args.audit:
        exit_code = audit_baseline()
    if args.scan:
        exit_code = run_detect_secrets_scan()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()

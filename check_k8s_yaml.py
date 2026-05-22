#!/usr/bin/env python3
"""Проверка синтаксиса YAML файлов K8s манифестов."""
import yaml
import glob
import sys

def check_k8s_manifests():
    """Проверка всех YAML файлов в deployment/k8s/base/"""
    files = glob.glob('deployment/k8s/base/**/*.yaml', recursive=True)
    errors = []
    
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                docs = list(yaml.safe_load_all(f))
                print(f"✓ {filepath} — валидно ({len(docs)} документ(ов))")
        except yaml.YAMLError as e:
            errors.append(f"✗ {filepath}: {e}")
        except Exception as e:
            errors.append(f"✗ {filepath}: {e}")
    
    if errors:
        print("\n❌ Ошибки:")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print(f"\n✅ все {len(files)} YAML файлов валидны!")

if __name__ == '__main__':
    check_k8s_manifests()

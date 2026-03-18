#!/usr/bin/env python3
\"\"\"Safe sync script from my-ecosystem-FINAL to _sync/ with diff previews.
Inspired by my-ecosystem/scripts/analyze_all.py, git_fix_history.py.
Usage: python scripts/sync-from-my-ecosystem.py --source C:/Users/Z/my-ecosystem-FINAL/it-compass/src/data/markers --target _sync/it-compass/markers --preview\"\"\"
import os
import json
import difflib
import argparse
from pathlib import Path

def preview_diff(source_file, target_file):
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source = f.read()
        with open(target_file, 'r', encoding='utf-8') as f:
            target = f.read()
        diff = difflib.unified_diff(
            target.splitlines(keepends=True),
            source.splitlines(keepends=True),
            fromfile=target_file, tofile=source_file
        )
        return ''.join(diff)
    except FileNotFoundError:
        return f'New file: {source_file}'

def sync_file(source, target_dir, preview_only=False):
    target = Path(target_dir) / Path(source).name
    if preview_only:
        print(preview_diff(source, target))
    else:
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        with open(source, 'r', encoding='utf-8') as sf, open(target, 'w', encoding='utf-8') as tf:
            tf.write(sf.read())
        print(f'Synced: {target}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, help='Source dir e.g. C:/Users/Z/my-ecosystem-FINAL/it-compass/src/data/markers/')
    parser.add_argument('--target', default='_sync/it-compass', help='Target _sync subdir')
    parser.add_argument('--preview', action='store_true', help='Preview diffs only')
    args = parser.parse_args()

    for root, _, files in os.walk(args.source):
        for file in files:
            if file.endswith('.json'):
                source_path = os.path.join(root, file)
                sync_file(source_path, args.target, args.preview)
                print('-' * 80)

if __name__ == '__main__':
    main()

# Example: python scripts/sync-from-my-ecosystem.py --source C:/Users/Z/my-ecosystem-FINAL/it-compass/src/data/markers --target _sync/it-compass/markers --preview


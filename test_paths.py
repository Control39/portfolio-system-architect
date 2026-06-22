import sys
from pathlib import Path

# Test what paths would be added
REPO_ROOT = Path('C:/repo').resolve()
SRC_PATH = REPO_ROOT / 'src'
MOLECULE_SRC = REPO_ROOT / 'apps/ai_config_manager/src'

print('REPO_ROOT:', REPO_ROOT)
print('SRC_PATH:', SRC_PATH)
print('MOLECULE_SRC:', MOLECULE_SRC)
print()
print('SRC_PATH exists:', SRC_PATH.exists())
print('MOLECULE_SRC exists:', MOLECULE_SRC.exists())
print()
print('Contents of MOLECULE_SRC:')
if MOLECULE_SRC.exists():
    for f in MOLECULE_SRC.iterdir():
        print(f'  {f.name}')

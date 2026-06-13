import sys
from pathlib import Path

molecule_root = Path(__file__).parent.parent
if str(molecule_root) not in sys.path:

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath('../../'))

project = 'Portfolio System Architect API'
copyright = '2026, Екатерина Куделя'
author = 'Екатерина Куделя'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autodoc_typehints',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

autodoc_typehints = 'description'

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'furo'
html_static_path = ['_static']

# Autodoc members all
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
}

# Add apps to path
for app in ['it-compass', 'cloud-reason', 'career-development', 'ml-model-registry']:
    autodoc_mock_imports = []
    sys.path.append(os.path.abspath(f'../../apps/{app}'))


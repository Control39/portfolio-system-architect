# setup.py
"""
Portfolio System Architect — Compositional Architecture Entry Point

Этот файл позволяет:
- Установить весь код как пакет: `pip install -e .`
- Корректно импортировать Атомы из `src/` в любых сервисах (Молекулах)
- Решить проблемы с `ImportError` (например, `from ai_config_manager import ConfigManager`)
"""

from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="portfolio-system-architect",
    version="0.1.0",
    description="Cognitive Architecture: Systems for Thinking",
    author="Катя (Control39)",
    author_email="leadarchitect@yandex.ru",
    url="https://github.com/Control39/portfolio-system-architect",
    packages=find_packages(where=".", include=["src", "src.*"]),  # Ищем пакеты в корне и src
    package_dir={"": "."},                  # Корень проекта как корень импорта
    python_requires=">=3.12",
    install_requires=[
        # Общие зависимости Атомов (если есть)
        # Раскомментируйте, когда появятся общие библиотеки
        # "pyyaml",
        # "fastapi",
        # "uvicorn",
        # "pydantic",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
            "httpx-respx",
            "flake8",
            "black",
            "isort",
            "mypy",
            "bandit",
            "pre-commit",
            "streamlit",
        ],
        "docker": [
            "docker",
            "python-dotenv",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    zip_safe=False,
    include_package_data=True,  # если будут *.yaml, *.json и т.д.
)
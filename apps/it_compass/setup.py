"""
IT Compass Setup Script
Методология "Объективные маркеры компетенций"
© 2025 Ekaterina Kudelya. CC BY-ND 4.0
"""

from setuptools import find_packages, setup


def read_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        return []


setup(
    name="it-compass",
    version="1.0.0",
    author="Ekaterina Kudelya",
    author_email="leadarchitect@yandex.ru",
    description="Objective IT career growth tracker with verifiable markers",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/Control39/it-compass",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "it-compass=main:main",  # ✅ ИСПРАВЛЕНО
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt", "*.sh"],
    },
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/Control39/it-compass/issues",
        "Source": "https://github.com/Control39/it-compass",
        "Documentation": "https://github.com/Control39/it-compass/tree/main/docs",
        "Funding": "https://github.com/sponsors/Control39",
    },
    keywords="career, growth, it, skills, portfolio, markers, smart",
    platforms="any",
)

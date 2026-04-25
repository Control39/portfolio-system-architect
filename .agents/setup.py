"""Setup configuration for Cognitive Automation Agent package.
"""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cognitive-automation-agent",
    version="1.0.0",
    author="Cognitive Automation Agent Team",
    author_email="agent@example.com",
    description="Autonomous intelligent agent for development automation and project management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cognitive-automation-agent",
    packages=find_packages(include=["agents", "agents.*"]),
    package_dir={"agents": "."},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "monitoring": [
            "prometheus-client>=0.17.0",
            "grafana-api>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cognitive-agent=agents.launch_script:main",
            "agent-scanner=agents.scripts.scanner_main:main",
            "agent-planner=agents.scripts.planner_main:main",
            "agent-learning=agents.scripts.learning_main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agents": [
            "config/*.yaml",
            "config/*.yml",
            "skills/*.py",
            "skills/*.yaml",
        ],
    },
)


from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
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
    packages=find_packages(),  # автоматически найдёт все пакеты
    package_data={
        "": [
            "config/*.yaml",
            "config/*.yml",
            "skills/*.py",
            "skills/*.yaml",
            "scripts/*.py",
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cognitive-agent=launch_script:main",
            "agent-scanner=scripts.scanner_main:main",
            "agent-planner=scripts.planner_main:main",
            "agent-learning=scripts.learning_main:main",
        ],
    },
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
)

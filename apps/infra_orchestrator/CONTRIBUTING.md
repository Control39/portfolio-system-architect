# Contributing to Infra-Orchestrator

This project is part of the [portfolio-system-architect](https://github.com/your-org/portfolio-system-architect) repository. Please refer to the root [CONTRIBUTING.md](../../CONTRIBUTING.md) for general contribution guidelines.

## Project-specific guidelines

### Development setup

1. Ensure you have Python 3.10+ installed.
2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run tests with pytest:
   ```bash
   pytest tests/ -v
   ```

### Pull request process

- All changes must be accompanied by pytest tests.
- Update the CHANGELOG.md with a brief description of your changes.
- Ensure the code follows Python best practices (Black, Ruff, MyPy).
- Request a review from the project maintainers.

### Code style

Follow the Python style guide defined in `pyproject.toml` (Black + isort + Ruff).
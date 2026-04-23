# Contributing to Cloud-Reason

This project is part of the [portfolio-system-architect](https://github.com/your-org/portfolio-system-architect) repository. Please refer to the root [CONTRIBUTING.md](../../CONTRIBUTING.md) for general contribution guidelines.

## Project-specific guidelines

### Development setup

1. Ensure you have Python 3.10+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (see `.env.example` in the root).
4. Run tests:
   ```bash
   pytest tests/
   ```

### Pull request process

- All changes must be accompanied by tests.
- Update the CHANGELOG.md with a brief description of your changes.
- Ensure the code passes linting (`black`, `flake8`).
- Request a review from the project maintainers.

### Code style

Follow the Python style guide defined in the root `pyproject.toml`.

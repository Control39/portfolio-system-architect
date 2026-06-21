# Contributing to Portfolio System Architect

Thank you for your interest in contributing to Portfolio System Architect! This document provides guidelines for contributing to this project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the issue tracker to avoid duplicates. When creating a bug report:

1. Use a clear, descriptive title
2. Describe the exact steps to reproduce the issue
3. Include expected vs actual behavior
4. Provide environment details (OS, Python version, etc.)
5. Include relevant logs or screenshots

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

1. A clear, descriptive title
2. A detailed description of the proposed enhancement
3. Any relevant examples or mockups
4. Explain why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a branch for your feature/bugfix (`git checkout -b feature/amazing-feature`)
3. Make your changes following our coding standards
4. Run tests and ensure they pass
5. Update documentation as needed
6. Commit your changes with clear messages
7. Push your branch and open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Control39/portfolio-system-architect.git
cd portfolio-system-architect

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest apps/*/tests/ -v
```

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed

## Testing

All pull requests must include appropriate tests:

```bash
# Run all tests
pytest apps/*/tests/ -v

# Run with coverage
pytest apps/*/tests/ --cov=apps --cov-report=term-missing

# Run specific test file
pytest apps/service_name/tests/test_example.py -v
```

## Documentation

- Update README.md if adding new features
- Update API documentation
- Add docstrings to all public functions and classes

## PR Review Process

1. Your PR will be reviewed by maintainers
2. Address any feedback or requested changes
3. Once approved, your PR will be merged

## Questions?

Feel free to open an issue or contact us at leadarchitect@yandex.ru

Thank you for contributing! 🚀

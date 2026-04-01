# Contributing to Arch-Compass-Framework

This project is part of the [portfolio-system-architect](https://github.com/your-org/portfolio-system-architect) repository. Please refer to the root [CONTRIBUTING.md](../../CONTRIBUTING.md) for general contribution guidelines.

## Project-specific guidelines

### Development setup

1. Ensure you have PowerShell 7.0+ installed.
2. Import the module:
   ```powershell
   Import-Module ./ArchCompass.psm1 -Force
   ```
3. Run tests with Pester:
   ```powershell
   Invoke-Pester ./tests/
   ```

### Pull request process

- All changes must be accompanied by Pester tests.
- Update the CHANGELOG.md with a brief description of your changes.
- Ensure the code follows PowerShell best practices (PSScriptAnalyzer).
- Request a review from the project maintainers.

### Code style

Follow the PowerShell style guide defined in the repository's `.vscode/settings.json`.

# Scripts Directory Structure

This directory contains utility scripts for development, deployment, and maintenance of the portfolio system. The scripts are organized by platform and purpose to demonstrate cross-platform expertise.

## 🏗️ Structure Rationale

The mixed scripting approach (PowerShell, Bash, Python, Batch) is **intentional** and demonstrates:

1. **Cross-platform expertise** – ability to work in both Windows and Linux environments
2. **Pragmatic tool selection** – using the right tool for each specific task
3. **Enterprise relevance** – many Russian companies use mixed environments
4. **Automation versatility** – scripts for CI/CD, local development, and production

## 📁 Directory Organization

### `windows/` – Windows-specific scripts
- **Purpose**: Scripts that require Windows-specific features or are meant to run in Windows environments
- **Languages**: PowerShell (.ps1), Batch (.bat)
- **Examples**: 
  - `fix_encoding.ps1` – fixes file encoding issues (Windows-specific)
  - `migrate-to-monorepo.bat` – Windows batch script for migration

### `linux/` – Linux/Unix-specific scripts
- **Purpose**: Scripts for Linux containers, CI/CD pipelines, and Unix-like systems
- **Languages**: Bash (.sh), Shell
- **Examples**:
  - `generate-docs.sh` – builds documentation (runs in Docker/Linux CI)
  - `backup-postgres.sh` – PostgreSQL backup (Linux cron job)

### `python/` – Cross-platform Python scripts
- **Purpose**: Platform-independent utilities and complex automation
- **Languages**: Python (.py)
- **Examples**:
  - `healthcheck.py` – health checks for services (cross-platform)
  - `sync-from-my-ecosystem.py` – complex data synchronization

### `general/` – Platform-agnostic or legacy scripts
- **Purpose**: Scripts that haven't been categorized yet or work on any platform
- **Languages**: Mixed
- **Note**: This is a transitional directory; scripts should eventually move to appropriate categories

## 🔄 Current Scripts Mapping

| Script | Current Location | Recommended Location | Reason |
|--------|------------------|----------------------|--------|
| `fix_encoding.ps1` | root | `windows/` | Windows-specific PowerShell script |
| `migrate-to-monorepo.bat` | root | `windows/` | Windows batch script |
| `generate-docs.sh` | root | `linux/` | Runs in Linux CI/CD |
| `generate-index.sh` | root | `linux/` | Linux shell script |
| `generate-site.sh` | root | `linux/` | Linux shell script |
| `backup-postgres.sh` | root | `linux/` | PostgreSQL on Linux |
| `restore-postgres.sh` | root | `linux/` | PostgreSQL on Linux |
| `check-lfs.sh` | root | `linux/` | Git LFS check (Linux) |
| `healthcheck.py` | root | `python/` | Cross-platform Python |
| `migrate-sqlite-to-postgres.py` | root | `python/` | Cross-platform Python |
| `sync-from-my-ecosystem.py` | root | `python/` | Cross-platform Python |
| `test_yandex_gpt_integration.py` | root | `python/` | Cross-platform Python |
| `translate-docs.py` | root | `python/` | Cross-platform Python |

## 🚀 Usage Guidelines

### For New Scripts
1. **Choose the right language**:
   - **Windows administration**: PowerShell
   - **Linux/containers/CI**: Bash
   - **Cross-platform/complex logic**: Python
2. **Place in appropriate directory**:
   - `windows/` for Windows-specific
   - `linux/` for Linux/Unix-specific  
   - `python/` for cross-platform Python
3. **Document dependencies** in script header

### For Existing Scripts
- Scripts in root directory are **legacy** and will be gradually moved
- Update any references in documentation or CI/CD configurations
- Test after moving to ensure nothing breaks

## 🤔 Why Not Unify on One Language?

While Python could handle all tasks, the mixed approach demonstrates:

1. **Real-world enterprise experience** – companies have mixed environments
2. **Specialized tool expertise** – PowerShell for Windows admin, Bash for Linux ops
3. **Portfolio diversity** – shows breadth of skills beyond just Python
4. **Performance/appropriateness** – some tasks are simpler in native shell

## 📚 Related Documentation
- [ADR-007: Technology Stack Justification](../docs/docs/adr/ADR-007-technology-stack-justification.md)
- README.md: Architectural Justification section
- [CI/CD Configuration](../.github/workflows/) – uses these scripts


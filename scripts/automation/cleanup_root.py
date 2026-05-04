#!/usr/bin/env python3
"""
Root Directory Cleanup Script
Organizes scattered files into proper directories
"""

import os
import shutil
from pathlib import Path

class RootCleaner:
    def __init__(self, root_path="."):
        self.root = Path(root_path).resolve()
        self.moves = {}
        self.skips = []
    
    def plan_cleanup(self):
        """Plan all file moves"""
        
        # Essential files to keep in root
        essential = {
            'README.md', 'LICENSE', 'Makefile',
            'requirements.txt', 'requirements-dev.txt',
            'requirements-dev.in', 'requirements.in',
            'pyproject.toml', 'docker-compose.yml'
        }
        
        # Documentation files -> docs/
        docs = {
            'AGENT_FIXES_REPORT.md': 'docs/archive/',
            'AGENT_FIX_COMPLETE.md': 'docs/archive/',
            'AI-CONFIG-SUMMARY.md': 'docs/archive/',
            'CHANGELOG.md': 'docs/',
            'CHECKLIST.md': 'docs/archive/',
            'CODE_OF_CONDUCT.md': 'docs/',
            'CONTRIBUTING.md': 'docs/',
            'DIAGNOSTIC_SUMMARY.md': 'docs/archive/',
            'ETHICS.md': 'docs/',
            'HEALTH_CHECK_REPORT.md': 'docs/archive/',
            'IMPLEMENTATION_PLAN.md': 'docs/archive/',
            'KODA.md': 'docs/archive/',
            'KODA_SETUP_COMPLETE.md': 'docs/archive/',
            'MIGRATION_COMPLETE.md': 'docs/archive/',
            'OPTION_B_EXECUTION_PLAN.md': 'docs/archive/',
            'PHASE_2_1_INTEGRATION_TESTS_REPORT.md': 'docs/archive/',
            'PHASE_2_2_ENHANCED_TESTS_REPORT.md': 'docs/archive/',
            'PHASE_2_3_CI_CD_DOCUMENTATION_REPORT.md': 'docs/archive/',
            'README.ru.md': 'docs/',
            'RELEASE_NOTES.md': 'docs/',
            'SECURITY.md': 'docs/',
            'SECURITY_FIXES.md': 'docs/',
            'WEEK_2_COMPLETE_SUMMARY.md': 'docs/archive/',
        }
        
        # Script files -> scripts/
        scripts = {
            'bulk_test_generator.py': 'scripts/generators/',
            'complete_diagnostic.py': 'scripts/diagnostics/',
            'enhanced_test_generator.py': 'scripts/generators/',
            'generate_enhanced_tests.py': 'scripts/generators/',
            'generate_integration_tests.py': 'scripts/generators/',
            'github_view.sh': 'scripts/',
            'health_check.py': 'scripts/diagnostics/',
            'navigate.ps1': 'scripts/',
            'phase1_2_config.py': 'scripts/automation/',
            'phase1_3_src.py': 'scripts/automation/',
            'phase1_4_standardize.py': 'scripts/automation/',
            'rename_integration_tests.py': 'scripts/generators/',
            'run_enhanced_tests.py': 'scripts/generators/',
            'run_enhanced_tests_individual.py': 'scripts/generators/',
            'update_service_readmes.py': 'scripts/generators/',
        }
        
        # Config files -> config/
        configs = {
            '.bandit.yml': 'config/tools/',
            '.codecov.yml': 'config/ci-cd/',
            '.coveragerc': 'config/tools/',
            '.dockerignore': 'config/docker/',
            '.env.example': 'config/',
            '.gitattributes': 'config/',
            '.git-commit-msg.txt': 'config/',
            '.kodaignore': 'config/tools/',
            '.mailmap': 'config/',
            '.pre-commit-config.yaml': 'config/tools/',
            '.secrets.baseline': 'config/tools/',
            '.trivyignore': 'config/tools/',
            '.webappignore': 'config/tools/',
            'azure.yaml': 'config/ci-cd/',
            'mkdocs.yml': 'config/',
            'mypy.ini': 'config/tools/',
            'pyrightconfig.json': 'config/tools/',
            'pytest.ini': 'config/tools/',
        }
        
        # Data files -> .reports/
        data = {
            'coverage.xml': '.reports/',
            'diagnostic_report.json': '.reports/',
            'health_check_report.json': '.reports/',
            'index.json': '.reports/',
            'phase2_2_enhanced_test_results.json': '.reports/',
            'phase2_integration_test_results.json': '.reports/',
        }
        
        self.moves = {**docs, **scripts, **configs, **data}
        self.essential = essential
        
        return self.moves
    
    def create_directories(self):
        """Create target directories"""
        print("📁 Creating directories...")
        
        dirs = {
            'docs/archive',
            'scripts/automation',
            'scripts/generators',
            'scripts/diagnostics',
            'config/tools',
            'config/ci-cd',
            'config/docker',
            '.reports',
        }
        
        for dir_name in dirs:
            dir_path = self.root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ Created {dir_name}/")
    
    def move_files(self, dry_run=True):
        """Move files to their destinations"""
        print(f"\n{'📋 DRY RUN - ' if dry_run else '✏️  '}Moving files...")
        
        moved = 0
        skipped = 0
        
        for file_name, dest_dir in self.moves.items():
            src = self.root / file_name
            
            if not src.exists():
                skipped += 1
                continue
            
            dest = self.root / dest_dir / file_name
            
            if dry_run:
                print(f"   → {file_name} → {dest_dir}")
            else:
                shutil.move(str(src), str(dest))
                print(f"   ✓ Moved {file_name}")
            
            moved += 1
        
        print(f"\nMoved: {moved}, Skipped: {skipped}")
        return moved, skipped
    
    def update_gitignore(self, dry_run=True):
        """Update .gitignore to ignore generated files"""
        print(f"\n{'📋 ' if dry_run else ''}Updating .gitignore...")
        
        gitignore = self.root / '.gitignore'
        additions = [
            '.reports/',
            '.coverage',
            '*.pyc',
        ]
        
        if gitignore.exists():
            content = gitignore.read_text()
        else:
            content = ""
        
        for addition in additions:
            if addition not in content:
                if not dry_run:
                    with open(gitignore, 'a') as f:
                        f.write(f"{addition}\n")
                print(f"   ✓ Added {addition}")
        
        if not dry_run:
            print("   ✓ .gitignore updated")
    
    def cleanup(self, dry_run=True):
        """Execute cleanup"""
        print("🧹 ROOT DIRECTORY CLEANUP")
        print("=" * 60)
        
        self.plan_cleanup()
        self.create_directories()
        self.move_files(dry_run=dry_run)
        self.update_gitignore(dry_run=dry_run)
        
        print("\n" + "=" * 60)
        if dry_run:
            print("✓ DRY RUN COMPLETE - No files moved")
            print("\nTo execute cleanup, run:")
            print("  python scripts/automation/cleanup_root.py --execute")
        else:
            print("✓ CLEANUP COMPLETE")
        
        self.print_summary()
    
    def print_summary(self):
        """Print cleanup summary"""
        print("\n📊 SUMMARY")
        print("-" * 60)
        
        root_files = [f for f in self.root.iterdir() if f.is_file()]
        root_count = len([f for f in root_files if f.name not in self.essential and not f.name.startswith('.')])
        
        print(f"Files to move: {len(self.moves)}")
        print(f"Directories to create: 8")
        print(f"Final root file count: ~{len(self.essential) + 5} (from {root_count})")
        print("\nResult: Professional, clean root directory ✨")


if __name__ == "__main__":
    import sys
    
    dry_run = "--execute" not in sys.argv
    
    cleaner = RootCleaner()
    cleaner.cleanup(dry_run=dry_run)

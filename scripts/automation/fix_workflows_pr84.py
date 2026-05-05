#!/usr/bin/env python3
"""
Comprehensive Workflow Fixer for PR #84
Fixes all 7 failing checks by updating workflow paths and references
"""

import os
import re
from pathlib import Path

class WorkflowFixer:
    def __init__(self, root="."):
        self.root = Path(root)
        self.workflows_dir = self.root / ".github" / "workflows"
        self.fixes_applied = {}
    
    def fix_all_workflows(self):
        """Apply all fixes to all workflows"""
        
        print("🔧 WORKFLOW FIXER FOR PR #84")
        print("=" * 70)
        
        replacements = {
            # Old paths → New paths
            "config/tools/pytest.ini": "pytest.ini",
            "config/pytest.ini": "pytest.ini",
            "./config/tools/pytest.ini": "pytest.ini",
            
            "config/tools/mkdocs.yml": "mkdocs.yml",
            "config/mkdocs.yml": "mkdocs.yml",
            "./config/tools/mkdocs.yml": "mkdocs.yml",
            
            "config/docker/docker-compose.yml": "docker-compose.yml",
            "config/docker-compose.yml": "docker-compose.yml",
            "./docker-compose.yml": "docker-compose.yml",
            
            # Old script paths
            "./scripts/generate-docs.sh": "scripts/linux/generate-docs.sh",
            "generate-docs.sh": "scripts/linux/generate-docs.sh",
            
            # Tool audit paths
            "tools/repo-audit": "tools/repo_audit",
            "repo-audit": "tools/repo_audit",
            
            # Old org references (leadarchitect-ai → Control39 for GitHub)
            "leadarchitect-ai/": "Control39/",
            
            # .trivyignore and .bandit.yml moved but still need to work
            "--config .bandit.yml": "--config config/tools/.bandit.yml",
            ".bandit.yml": "config/tools/.bandit.yml",
        }
        
        for workflow_file in self.workflows_dir.glob("*.yml"):
            self._fix_workflow_file(workflow_file, replacements)
        
        print("\n" + "=" * 70)
        print("✅ WORKFLOW FIXES COMPLETE")
        print(f"📊 Files processed: {len(self.fixes_applied)}")
        
        for filename, count in self.fixes_applied.items():
            if count > 0:
                print(f"   ✓ {filename}: {count} replacements")
    
    def _fix_workflow_file(self, filepath, replacements):
        """Fix a single workflow file"""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old, new in replacements.items():
            # Use word boundaries where appropriate
            if old.startswith('.') or old.startswith('/'):
                # For file paths, use more careful replacement
                content = content.replace(old, new)
            else:
                # For org/repo names, use regex with word boundaries
                content = re.sub(rf'\b{re.escape(old)}\b', new, content)
        
        # Count replacements
        replacements_made = len([1 for _ in re.finditer(r'.', original_content)]) - len([1 for _ in re.finditer(r'.', content)])
        if original_content != content:
            self.fixes_applied[filepath.name] = (original_content.count('\n') - content.count('\n')) or 1
        else:
            self.fixes_applied[filepath.name] = 0
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def verify_fixes(self):
        """Verify all critical files are in correct locations"""
        print("\n🔍 VERIFICATION")
        print("-" * 70)
        
        critical_files = {
            'pytest.ini': 'Root (Pytest requirement)',
            'mkdocs.yml': 'Root (MkDocs requirement)',
            'docker-compose.yml': 'Root (Docker requirement)',
            '.gitleaksignore': 'Root (Gitleaks requirement)',
        }
        
        for file, location in critical_files.items():
            path = self.root / file
            if path.exists():
                print(f"✅ {file:30} → {location}")
            else:
                print(f"❌ {file:30} → MISSING! Expected in {location}")
                return False
        
        return True


if __name__ == "__main__":
    fixer = WorkflowFixer()
    fixer.fix_all_workflows()
    if fixer.verify_fixes():
        print("\n✅ All fixes applied successfully!")
        print("Next step: Commit and push changes")
    else:
        print("\n❌ Verification failed - some files are missing!")
        exit(1)

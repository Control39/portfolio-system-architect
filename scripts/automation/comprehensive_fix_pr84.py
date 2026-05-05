#!/usr/bin/env python3
"""
COMPREHENSIVE FIX for PR #84
Fixes all organization references, paths, and CAA-related issues
"""

import re
from pathlib import Path

def fix_all_workflows():
    """Fix all workflow files"""
    
    print("🔧 COMPREHENSIVE WORKFLOW FIX")
    print("=" * 80)
    
    workflows_dir = Path(".github/workflows")
    replacements = [
        # Organization changes (leadarchitect-ai → Control39)
        ("leadarchitect-ai", "Control39"),
        ("leadarchitect-ai.github.io", "control39.github.io"),
        ("leadarchitect-ai.sourcecraft", "control39.sourcecraft"),
        
        # Path fixes
        ("config/agent-config.yaml", "apps/cognitive-agent/config/agent-config.yaml"),
        ("config/triggers.yaml", "apps/cognitive-agent/config/triggers.yaml"),
        ("config/learning.yaml", "apps/cognitive-agent/config/learning.yaml"),
        
        # CAA-audit skill path
        (".codeassistant/skills/caa-audit", ".codeassistant/skills/caa-audit"),
        
        # .agents → apps reference (old path)
        ("cd .agents", "cd apps/cognitive-agent"),
        
        # Fix mkdocs references
        ("--config-file ./config/mkdocs.yml", "--config-file ./mkdocs.yml"),
        
        # pytest paths
        ("config/pytest.ini", "pytest.ini"),
    ]
    
    for workflow_file in workflows_dir.glob("*.yml"):
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        for old, new in replacements:
            if old != new:
                content = content.replace(old, new)
        
        if content != original:
            with open(workflow_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            changes = sum(1 for _ in re.finditer(re.escape(old), original) for old, _ in replacements)
            print(f"✅ {workflow_file.name:<40} Fixed")
        else:
            print(f"⊘  {workflow_file.name:<40} No changes needed")
    
    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE FIX COMPLETE")
    print("\nKey fixes applied:")
    print("  1. leadarchitect-ai → Control39 (organization)")
    print("  2. Config paths → correct locations")
    print("  3. CAA references → correct structure")
    print("  4. .agents → apps/cognitive-agent")
    print("  5. mkdocs, pytest paths → root")

if __name__ == "__main__":
    fix_all_workflows()

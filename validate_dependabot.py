#!/usr/bin/env python3
"""Validate Dependabot YAML configuration."""

import yaml
import sys

def main():
    try:
        with open('.github/dependabot.yml', 'r') as f:
            data = yaml.safe_load(f)
        
        print('✅ YAML is valid')
        print(f'Version: {data.get("version")}')
        
        updates = data.get('updates', [])
        print(f'Number of update entries: {len(updates)}')
        
        for i, update in enumerate(updates):
            print(f'  {i+1}. {update.get("package-ecosystem")} - {update.get("directory")}')
        
        # Check for common issues
        if data.get('version') != 2:
            print('⚠️  Warning: Dependabot version should be 2')
        
        if not updates:
            print('❌ Error: No update configurations found')
            sys.exit(1)
            
        print('\n✅ Dependabot configuration looks good!')
        return 0
        
    except yaml.YAMLError as e:
        print(f'❌ YAML Error: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'❌ Error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
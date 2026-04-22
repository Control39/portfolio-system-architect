import toml
from pathlib import Path

def validate_pyproject():
    file_path = "apps/mcp-server/pyproject.toml"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        print(f"✅ {file_path} — valid TOML")
        print(f"Name: {data['project']['name']}")
        print(f"Version: {data['project']['version']}")
        return True
    except Exception as e:
        print(f"❌ Invalid TOML: {e}")
        return False

if __name__ == "__main__":
    validate_pyproject()
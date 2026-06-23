"""Check pytest paths."""

from pathlib import Path

# Check if pytest.ini is being used
pytest_ini = Path("C:/repo/pytest.ini")
print(f"pytest.ini exists: {pytest_ini.exists()}")

# Check what pytest would read from pytest.ini
import configparser

config = configparser.ConfigParser()
config.read(pytest_ini)

print("\npytest.ini pythonpath:")
pythonpath = config.get("pytest", "pythonpath", fallback="").strip().split("\n")
for p in pythonpath:
    p = p.strip()
    if p:
        abs_path = (Path.cwd() / p).resolve()
        print(f"  {p} -> {abs_path}")

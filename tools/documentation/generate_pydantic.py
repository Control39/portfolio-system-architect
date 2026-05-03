#!/usr/bin/env python3
"""Pydantic Schema Generator from YAML definitions
Generates src/shared/pydantic/*.py from src/shared/schemas/*.yaml
"""

import argparse
from pathlib import Path

import yaml

SCHEMAS_DIR = Path("src/shared/schemas")
PYDANTIC_DIR = Path("src/shared/pydantic")
PYDANTIC_DIR.mkdir(exist_ok=True)


def yaml_to_pydantic(schema_path: Path) -> str:
    """Convert YAML schema to Pydantic models"""
    with open(schema_path) as f:
        data = yaml.safe_load(f)

    models = []
    data.get("title", "GeneratedModels")

    # Extract definitions
    definitions = data.get("definitions", [])
    properties = data.get("properties", {})

    for model_name in definitions:
        props = properties.get(model_name, {}).get("properties", {})
        required = properties.get(model_name, {}).get("required", [])

        model_str = f"class {model_name}(BaseModel):\n"
        for prop_name, prop_def in props.items():
            prop_type = _infer_type(prop_def)
            default = " = Field(...) " if prop_name in required else " = Field(None)"
            model_str += f"    {prop_name}: {prop_type}{default}\n"
        models.append(model_str)

    return f'''"""
{schema_path.stem} - Generated Pydantic Models
Source: {schema_path}
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

{chr(10).join(models)}
'''


def _infer_type(prop_def: dict) -> str:
    """Infer Python type from JSON Schema"""
    type_map = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List[Any]",
        "object": "dict[str, Any]",
    }

    prop_type = prop_def.get("type", "string")
    if "format" in prop_def and prop_def["format"] == "date-time":
        return "datetime"

    return type_map.get(prop_type, "Any")


def generate_all():
    """Generate all schemas"""
    for yaml_file in SCHEMAS_DIR.glob("*.yaml"):
        py_content = yaml_to_pydantic(yaml_file)
        py_file = PYDANTIC_DIR / f"{yaml_file.stem}.py"
        with open(py_file, "w") as f:
            f.write(py_content)
        print(f"✅ Generated {py_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("schema", nargs="?", help="Specific schema file")
    args = parser.parse_args()

    if args.schema:
        yaml_path = SCHEMAS_DIR / f"{args.schema}.yaml"
        py_content = yaml_to_pydantic(yaml_path)
        print(py_content)
    else:
        generate_all()

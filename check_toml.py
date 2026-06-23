#!/usr/bin/env python3
import tomllib

with open("architecture.toml", "rb") as f:
    data = tomllib.load(f)

import json

print(json.dumps(data, indent=2, ensure_ascii=False))

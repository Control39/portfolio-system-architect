import re


with open(".kodacli/KODA.md", encoding="utf-8") as f:
    content = f.read()
m = re.search(r"[~]?(\d+\.?\d*)%", content)
print("Found:", m.group(1) if m else "None")

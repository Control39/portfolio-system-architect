import os
from pathlib import Path

docs_dir = Path(r"C:\repo\docs")

# Создаем папки
layouts_dir = docs_dir / "_layouts"
includes_dir = docs_dir / "_includes"
assets_dir = docs_dir / "assets"

for d in [layouts_dir, includes_dir, assets_dir]:
    d.mkdir(exist_ok=True)
    print(f"✅ Created: {d.relative_to(docs_dir)}")

# Создаем базовый layout
layout_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ page.title | default: site.title }}</title>
  <meta name="description" content="{{ page.description | default: site.description }}">
  <link rel="stylesheet" href="{{ '/assets/style.css' | relative_url }}">
</head>
<body>
  <header>
    <nav>
      <a href="{{ '/' | relative_url }}" class="logo">Portfolio System Architect</a>
      <ul>
        <li><a href="{{ '/cases/README.md' | relative_url }}">Cases</a></li>
        <li><a href="{{ '/apps/README.md' | relative_url }}">Services</a></li>
        <li><a href="{{ '/ARCHITECTURE.md' | relative_url }}">Architecture</a></li>
      </ul>
    </nav>
  </header>
  
  <main>
    {{ content }}
  </main>
  
  <footer>
    <p>&copy; 2026 Portfolio System Architect. Built with Jekyll.</p>
  </footer>
</body>
</html>
"""

with open(layouts_dir / "default.html", "w", encoding="utf-8") as f:
    f.write(layout_content)
print("✅ Created: _layouts/default.html")

# Создаем CSS
css_content = """
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: #333;
}

header {
  background: #f5f5f5;
  padding: 20px;
  margin-bottom: 30px;
  border-radius: 8px;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

nav .logo {
  font-size: 1.5em;
  font-weight: bold;
  color: #0366d6;
  text-decoration: none;
}

nav ul {
  list-style: none;
  display: flex;
  gap: 20px;
  margin: 0;
  padding: 0;
}

nav a {
  color: #555;
  text-decoration: none;
  padding: 5px 10px;
  border-radius: 4px;
}

nav a:hover {
  background: #e1e4e8;
}

main {
  min-height: 60vh;
}

footer {
  margin-top: 50px;
  padding-top: 20px;
  border-top: 1px solid #e1e4e8;
  text-align: center;
  color: #666;
  font-size: 0.9em;
}

h1, h2, h3 {
  color: #24292e;
}

a {
  color: #0366d6;
}

code {
  background: #f6f8fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

pre {
  background: #f6f8fa;
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

th, td {
  border: 1px solid #e1e4e8;
  padding: 10px;
  text-align: left;
}

th {
  background: #f6f8fa;
  font-weight: bold;
}
"""

(assets_dir / "style.css").write_text(css_content, encoding="utf-8")
print("✅ Created: assets/style.css")

print("\n✅ Jekyll structure ready!")

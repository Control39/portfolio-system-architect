from pathlib import Path

from scripts.generate_readme import ReadmeGenerator


g = ReadmeGenerator(Path("."))
print("Coverage:", g._get_test_coverage())
print("Root:", g.root)

#!/bin/bash
# Generate/update docs/INDEX.md from template

cd "$(dirname "$0")/../docs"
echo "Updating INDEX.md..."
# Future: grep all MD headers → auto-index
pandoc INDEX.md -o INDEX.pdf
echo "INDEX.pdf created."


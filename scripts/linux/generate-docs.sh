#!/bin/bash
# Generate documentation using MkDocs and deploy to GitHub Pages
# Usage: ./scripts/generate-docs.sh [--deploy]

set -e

cd "$(dirname "$0")/.."

DOCS_DIR="docs"
CONFIG_FILE="./mkdocs.yml"
BUILD_DIR="$DOCS_DIR/site"

# Install dependencies if needed
if ! command -v mkdocs &> /dev/null; then
    echo "MkDocs not found, installing via pip..."
    pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized
fi

# Build docs
echo "Building documentation..."
mkdocs build --site-dir "$BUILD_DIR" --config-file "$CONFIG_FILE"

echo "Documentation built at $BUILD_DIR"

# Deploy to GitHub Pages if --deploy flag provided
if [[ "$1" == "--deploy" ]]; then
    if [[ -z "$GITHUB_TOKEN" ]]; then
        echo "Error: GITHUB_TOKEN environment variable not set."
        exit 1
    fi
    echo "Deploying to GitHub Pages..."
    mkdocs gh-deploy --config-file "$CONFIG_FILE" --force
    echo "Deployment completed."
fi

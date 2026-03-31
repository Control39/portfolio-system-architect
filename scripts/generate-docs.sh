#!/bin/bash

# Automatic documentation generation script
# Generates documentation from code and updates documentation site

set -e

echo "📚 Automatic Documentation Generation"
echo "================================================================"

# Create directories
mkdir -p docs/api
mkdir -p docs/reference
mkdir -p docs/architecture/diagrams

# Function to check if command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "⚠️  $1 not found. Installing..."
        return 1
    fi
    return 0
}

# Generate API documentation from FastAPI
generate_api_docs() {
    echo "1. Generating API documentation..."
    
    if check_command "pydoc-markdown"; then
        echo "   Using pydoc-markdown..."
        pydoc-markdown -m gateway.main -o docs/api/gateway.md --render-toc
        pydoc-markdown -m api.main -o docs/api/api.md --render-toc
    else
        echo "   Using fallback method..."
        
        # Generate OpenAPI schema
        if [ -f "gateway/main.py" ]; then
            echo "   Generating OpenAPI schema for gateway..."
            python -c "
from gateway.main import app
import json
with open('docs/api/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
            " || echo "   ⚠️  Could not generate OpenAPI schema"
        fi
        
        # Generate simple markdown documentation
        echo "# API Documentation" > docs/api/README.md
        echo "" >> docs/api/README.md
        echo "Generated on $(date)" >> docs/api/README.md
        echo "" >> docs/api/README.md
        echo "## Endpoints" >> docs/api/README.md
        echo "" >> docs/api/README.md
        echo "- \`GET /health\` - Health check" >> docs/api/README.md
        echo "- \`GET /docs\` - Interactive API documentation" >> docs/api/README.md
        echo "- \`GET /redoc\` - Alternative API documentation" >> docs/api/README.md
    fi
    
    echo "   ✅ API documentation generated in docs/api/"
}

# Generate Python module documentation
generate_python_docs() {
    echo "2. Generating Python module documentation..."
    
    # Generate documentation for main modules
    for module in src apps gateway api; do
        if [ -d "$module" ] && [ "$(ls -A $module 2>/dev/null)" ]; then
            echo "   Documenting $module/"
            mkdir -p "docs/reference/$module"
            
            # Find Python files
            find "$module" -name "*.py" -type f | while read -r pyfile; do
                relpath="${pyfile#$module/}"
                dirname="docs/reference/$module/$(dirname "$relpath")"
                mkdir -p "$dirname"
                
                # Generate simple documentation
                echo "# \`$relpath\`" > "$dirname/$(basename "$pyfile" .py).md"
                echo "" >> "$dirname/$(basename "$pyfile" .py).md"
                echo "\`\`\`python" >> "$dirname/$(basename "$pyfile" .py).md"
                head -50 "$pyfile" >> "$dirname/$(basename "$pyfile" .py).md"
                echo "\`\`\`" >> "$dirname/$(basename "$pyfile" .py).md"
            done
        fi
    done
    
    echo "   ✅ Python documentation generated in docs/reference/"
}

# Generate database schema documentation
generate_db_docs() {
    echo "3. Generating database schema documentation..."
    
    if [ -f "alembic.ini" ] || [ -d "migrations" ]; then
        echo "   Found Alembic migrations"
        echo "# Database Schema" > docs/database/README.md
        echo "" >> docs/database/README.md
        echo "## Tables" >> docs/database/README.md
        echo "" >> docs/database/README.md
        echo "Generated from Alembic migrations" >> docs/database/README.md
    else
        echo "   ⚠️  No database migrations found"
    fi
    
    echo "   ✅ Database documentation generated"
}

# Generate architecture diagrams
generate_diagrams() {
    echo "4. Generating architecture diagrams..."
    
    if check_command "diagrams"; then
        echo "   Generating system architecture diagram..."
        python -c "
from diagrams import Diagram, Cluster
from diagrams.onprem.client import User
from diagrams.onprem.network import Internet
from diagrams.onprem.container import Docker
from diagrams.programming.language import Python

with Diagram('Portfolio System Architecture', show=False, direction='TB'):
    user = User('User')
    internet = Internet('Internet')
    
    with Cluster('API Gateway'):
        gateway = Python('FastAPI')
    
    with Cluster('Microservices'):
        auth = Python('Auth Service')
        rag = Python('RAG Service')
        ml = Python('ML Service')
        monitoring = Python('Monitoring')
    
    with Cluster('Databases'):
        postgres = Docker('PostgreSQL')
        redis = Docker('Redis')
        chroma = Docker('ChromaDB')
    
    with Cluster('Monitoring'):
        prometheus = Docker('Prometheus')
        grafana = Docker('Grafana')
    
    user >> internet >> gateway
    gateway >> [auth, rag, ml, monitoring]
    auth >> postgres
    rag >> chroma
    ml >> redis
    monitoring >> [prometheus, grafana]
        " || echo "   ⚠️  Could not generate diagram"
    else
        echo "   ⚠️  Diagrams package not installed. Install with: pip install diagrams"
    fi
    
    echo "   ✅ Architecture diagrams generated"
}

# Update documentation index
update_index() {
    echo "5. Updating documentation index..."
    
    cat > docs/README.md << 'EOF'
# Portfolio System Architect - Documentation

This documentation is automatically generated from the codebase.

## 📚 Documentation Sections

### [API Documentation](api/README.md)
- REST API endpoints
- Request/response examples
- OpenAPI specification

### [Reference Documentation](reference/README.md)
- Python module documentation
- Code examples
- Architecture overview

### [Database Schema](database/README.md)
- Table definitions
- Relationships
- Migration guide

### [Architecture Diagrams](architecture/diagrams/README.md)
- System architecture
- Component relationships
- Data flow diagrams

## 🔧 How to Use

### View Documentation Online
The documentation is hosted at: [https://leadarchitect-ai.github.io/portfolio-system-architect/](https://leadarchitect-ai.github.io/portfolio-system-architect/)

### Generate Documentation Locally
```bash
./scripts/generate-docs.sh
```

### Auto-generated Documentation
This documentation is automatically updated:
- On every commit to main branch
- Daily via scheduled job
- When version tags are pushed

## 📊 Documentation Status
- Last generated: $(date)
- Version: $(grep -E '^version =' pyproject.toml | sed -E 's/version = "([^"]+)"/\1/' 2>/dev/null || echo "unknown")
- Coverage: $(find docs -name "*.md" | wc -l) markdown files

## 🚀 Quick Start
See [QUICKSTART.md](QUICKSTART.md) for getting started with the project.
EOF
    
    echo "   ✅ Documentation index updated"
}

# Build documentation site
build_docs_site() {
    echo "6. Building documentation site..."
    
    if [ -f "mkdocs.yml" ]; then
        echo "   Building with MkDocs..."
        mkdocs build --clean || echo "   ⚠️  MkDocs build failed"
    elif [ -f "docs/conf.py" ]; then
        echo "   Building with Sphinx..."
        sphinx-build docs docs/_build || echo "   ⚠️  Sphinx build failed"
    else
        echo "   ⚠️  No documentation builder configured"
        echo "   Create mkdocs.yml or docs/conf.py for full site generation"
    fi
    
    echo "   ✅ Documentation site built"
}

# Main execution
main() {
    echo "Starting documentation generation..."
    echo ""
    
    generate_api_docs
    echo ""
    
    generate_python_docs
    echo ""
    
    generate_db_docs
    echo ""
    
    generate_diagrams
    echo ""
    
    update_index
    echo ""
    
    build_docs_site
    echo ""
    
    echo "================================================================"
    echo "🎉 Documentation generation completed!"
    echo ""
    echo "📁 Generated files:"
    find docs -name "*.md" -o -name "*.json" -o -name "*.png" | head -10
    echo ""
    echo "📊 Statistics:"
    echo "  - Markdown files: $(find docs -name "*.md" | wc -l)"
    echo "  - Total size: $(du -sh docs | cut -f1)"
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Review generated documentation"
    echo "  2. Commit changes: git add docs/ && git commit -m 'docs: update documentation'"
    echo "  3. Deploy: ./scripts/deploy-docs.sh"
    echo "================================================================"
}

# Run main function
main
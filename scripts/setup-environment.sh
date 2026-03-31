#!/bin/bash

# Setup script for portfolio-system-architect
# Automatically sets up virtual environment and installs dependencies

set -e

echo "🚀 Setting up portfolio-system-architect development environment"
echo "================================================================"

# Check Python version
echo "1. Checking Python version..."
python --version || { echo "❌ Python not found. Please install Python 3.10+"; exit 1; }

# Create virtual environment if it doesn't exist
echo "2. Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating new virtual environment..."
    python -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "3. Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
else
    echo "❌ Could not find activate script"
    exit 1
fi

echo "Virtual environment activated: $(which python)"

# Upgrade pip
echo "4. Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "5. Installing dependencies..."
pip install -e .[dev]

# Install pre-commit hooks
echo "6. Setting up pre-commit hooks..."
pre-commit install

# Check if Docker is running
echo "7. Checking Docker..."
if command -v docker &> /dev/null; then
    docker --version
    if docker ps &> /dev/null; then
        echo "✅ Docker is running"
    else
        echo "⚠️  Docker is installed but not running. Start Docker Desktop."
    fi
else
    echo "⚠️  Docker not found. Some features will not work."
fi

# Create .env file if it doesn't exist
echo "8. Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "⚠️  Please edit .env file with your configuration"
    else
        echo "⚠️  No .env.example found. Creating empty .env file"
        touch .env
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "================================================================"
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run './scripts/start-all.sh' to start all services"
echo "3. Run 'pre-commit run --all-files' to check code quality"
echo "4. Run 'pytest tests/' to run tests"
echo ""
echo "Available scripts:"
echo "- ./scripts/start-all.sh      - Start all services"
echo "- ./scripts/stop-all.sh       - Stop all services"
echo "- ./scripts/health-check.sh   - Check service health"
echo "- ./scripts/security-check.sh - Run security checks"
echo "================================================================"
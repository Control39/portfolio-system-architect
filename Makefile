# Makefile для управления Cognitive Agent архитектурой

.PHONY: help chat run-agent scan-project show-status architecture-docs

# === Help Commands ===
help:
	@echo "🤖 Cognitive Agent Management Commands:"
	@echo ""
	@echo "Main Commands:"
	@echo "  make chat              - Start chat interface with Cognitive Agent"
	@echo "  make run-agent         - Run Cognitive Agent API"
	@echo "  make scan-project      - Scan project with Cognitive Agent"
	@echo "  make show-status       - Show agent status"
	@echo ""
	@echo "Architecture Commands:"
	@echo "  make architecture-docs - Show architecture documentation"
	@echo "  make show-structure    - Show project structure"
	@echo "  make check-integrity   - Check system integrity"
	@echo ""
	@echo "Development Commands:"
	@echo "  make test-all          - Run all tests"
	@echo "  make lint              - Run code linting"
	@echo ""

# === Main Commands ===
chat:
	@echo "🚀 Starting Cognitive Agent Chat..."
	python scripts/cognitive_agent_chat.py

run-agent:
	@echo "🚀 Running Cognitive Agent API..."
	python -c "from agents.cognitive_agent.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8008)"

scan-project:
	@echo "🔍 Scanning project with Cognitive Agent..."
	python -c "from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent; agent = AutonomousCognitiveAgent(); result = agent.scan_project(); print('Scan completed:', result.get('files', 0), 'files scanned')"

show-status:
	@echo "📊 Showing Cognitive Agent status..."
	python -c "from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent; agent = AutonomousCognitiveAgent(); status = agent.get_status(); print('Agent Status:'); [print(f'  {k}: {v}') for k,v in status.items()]"

# === Architecture Commands ===
architecture-docs:
	@echo "🏗️ Cognitive Agent Architecture:"
	@echo ""
	@echo "Core Components:"
	@echo "  - agents/cognitive_agent/autonomous_agent.py (main logic)"
	@echo "  - agents/cognitive_agent/autonomous_agent_v.2.py (enhanced)"
	@echo "  - agents/cognitive_agent/orchestrator_v2.py (task orchestration)"
	@echo ""
	@echo "External Services:"
	@echo "  - apps/ai_provider_manager/ (GigaChat, Ollama)"
	@echo "  - apps/ai_config_manager/ (centralized config)"
	@echo "  - apps/it_compass/ (skill markers)"
	@echo "  - apps/auth_service/ (authentication)"
	@echo "  - apps/decision_engine/ (recommendations)"
	@echo "  - apps/knowledge_graph/ (knowledge storage)"
	@echo "  - apps/embedding_agent/ (RAG system)"
	@echo ""
	@echo "Key Features:"
	@echo "  - 25+ specialized skills"
	@echo "  - Enterprise guardrails"
	@echo "  - Role-based authorization"
	@echo "  - Audit trail system"
	@echo "  - Self-learning capability"

show-structure:
	@echo "📁 Project Structure:"
	@echo ""
	@echo "Root:"
	@echo "├── agents/ (autonomous agents)"
	@echo "│   └── cognitive_agent/ (main agent)"
	@echo "│       ├── autonomous_agent.py (main logic)"
	@echo "│       ├── autonomous_agent_v.2.py (enhanced)"
	@echo "│       ├── orchestrator_v2.py (task orchestration)"
	@echo "│       ├── config/ (guardrails, settings)"
	@echo "│       ├── skills/ (25+ specialized skills)"
	@echo "│       ├── src/ (core modules)"
	@echo "│       ├── tests/ (comprehensive tests)"
	@echo "│       └── docs/ (architecture documentation)"
	@echo "├── apps/ (microservices)"
	@echo "├── src/ (shared components)"
	@echo "├── config/ (centralized configuration)"
	@echo "├── docs/ (documentation)"
	@echo "├── scripts/ (automation scripts)"
	@echo "└── tests/ (test suites)"

check-integrity:
	@echo "✅ Checking system integrity..."
	@python -c "import sys; from pathlib import Path; repo_root = Path('.'); print('Python executable:', sys.executable); print('Repo exists:', repo_root.exists()); print('Agent module exists:', (repo_root/'agents'/'cognitive_agent').exists())"

# === Development Commands ===
test-all:
	@echo "🧪 Running all tests..."
	python -m pytest tests/ -v

lint:
	@echo "🧹 Running code linting..."
	python -m flake8 . --exclude .git,__pycache__,.venv --ignore=E501,W503

# === Environment Commands ===
setup-env:
	@echo "🔧 Setting up environment..."
	pip install -r requirements.txt

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

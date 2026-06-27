# tests/test_guardrails.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

from pathlib import Path

import pytest
import yaml

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent


class TestGuardrails:
    @pytest.fixture
    def agent(self, tmp_path: Path):
        # Создаём mock-проект
        config_dir = tmp_path / "agents" / "cognitive_agent" / "config"
        config_dir.mkdir(parents=True)

        # Сохраняем guardrails.yaml
        guardrails_yaml = config_dir / "guardrails.yaml"
        guardrails_yaml.write_text(
            yaml.dump(
                {
                    "allowed_paths": ["^apps/", "^agents/", "^config/"],
                    "blocked_patterns": [".env", ".pem", ".key"],
                    "safe_actions": ["read", "scan"],
                    "rules": [
                        {
                            "pattern": ".*\\.py$",
                            "action_pattern": "(write|create|edit|modify|update|delete|remove)",
                            "action": "requires-approval",
                        },
                        {"pattern": ".*\\.(key|pem|env)$", "action_pattern": ".*", "action": "block"},
                        {"pattern": "config/sensitive.*", "action_pattern": ".*", "action": "block"},
                        {"pattern": ".*", "action_pattern": "read|scan|list|analyze", "action": "allow"},
                    ],
                }
            )
        )

        # Mock self.project_path
        agent = AutonomousCognitiveAgent(str(tmp_path))
        agent.project_path = tmp_path
        agent._load_guardrails(guardrails_yaml)
        return agent

    def test_allowed_path_read(self, agent: AutonomousCognitiveAgent):
        # ✅ Исправлено: без == True
        assert agent._check_guardrail("read", "apps/main.py")
        assert agent._check_guardrail("scan", "agents/cognitive_agent/autonomous_agent.py")
        assert agent._check_guardrail("list", "config/vscode/vscode-extensions.json")

    def test_disallowed_path(self, agent: AutonomousCognitiveAgent):
        # ✅ Исправлено: с not
        assert not agent._check_guardrail("read", "deployments/deploy.sh")
        assert not agent._check_guardrail("read", "/etc/passwd")
        assert not agent._check_guardrail("read", "~/backup.sh")

    def test_blocked_patterns(self, agent: AutonomousCognitiveAgent):
        # ✅ Исправлено: с not
        assert not agent._check_guardrail("read", "config/.env")
        assert not agent._check_guardrail("write", "secrets.pem")
        assert not agent._check_guardrail("update", "private.key")

    def test_requires_approval(self, agent: AutonomousCognitiveAgent):
        # ✅ Исправлено: с not
        assert not agent._check_guardrail("write", "apps/auth_service/main.py")
        assert not agent._check_guardrail("edit", "agents/cognitive_agent/autonomous_agent.py")
        assert not agent._check_guardrail("update", "config/sensitive/secrets.yaml")

    def test_default_deny(self, agent: AutonomousCognitiveAgent):
        # ✅ Исправлено: с not
        assert not agent._check_guardrail("install", "some/package")
        assert not agent._check_guardrail("delete", "logs/test.log")

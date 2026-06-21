#!/usr/bin/env python3
"""
Enterprise Cognitive Agent - Backward Compatibility Wrapper

⚠️  DEPRECATED: This file is kept for backward compatibility only.
All functionality has been merged into autonomous_agent.py.

Please update your imports to use:
    from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent

This module re-exports the main agent class to avoid breaking existing code.
"""

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent

# For backward compatibility with old imports
AutonomousCognitiveAgentEnterprise = AutonomousCognitiveAgent

__all__ = ['AutonomousCognitiveAgent', 'AutonomousCognitiveAgentEnterprise']

#!/usr/bin/env python3
"""Test script for AutonomousCognitiveAgent methods"""

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent

# Test agent instantiation
agent = AutonomousCognitiveAgent()
print(f"Agent created: {agent.agent_id}")

# Test start method
agent.start(background=False)
print("Agent started")

# Test stop method  
agent.stop()
print("Agent stopped")

print("All methods work correctly!")

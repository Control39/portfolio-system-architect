#!/usr/bin/env python3
"""Test prompt engine with root-level prompts integration"""

from pathlib import Path
from agents.cognitive_agent.src.prompt_engine import PromptEngine
from agents.cognitive_agent.integrations.llm_client import create_llm_client


def main():
    prompts_dir = Path("agents/cognitive_agent/prompts")
    root_prompts_dir = Path("prompts")

    print("=== Prompt Engine Integration Test ===\n")
    print(f"Root-level prompts: {root_prompts_dir}")
    print(f"Agent-level prompts: {prompts_dir}\n")

    # Create LLM client
    llm_client = create_llm_client()

    # Initialize prompt engine with both directories
    engine = PromptEngine(
        prompts_dir=prompts_dir,
        llm_client=llm_client,
        root_prompts_dir=root_prompts_dir,
    )

    # List all templates
    templates = engine.list_templates()
    print(f"Total templates: {len(templates)}\n")

    print("Template sources:")
    for name, info in sorted(templates.items()):
        print(f"  - {name}: {info['source']} (v{info['version']})")

    print("\n=== Testing Template Loading ===")

    # Test loading a framework template
    framework_template = "python/fastapi/api"
    print(f"\nLoading template: {framework_template}")
    try:
        template = engine.load_template(framework_template)
        source = engine.get_template_source(framework_template)
        print(f"✓ Loaded from: {source}")
        print(f"  Version: {template.version}")
        print(f"  Description: {template.description}")
        print(f"  Content length: {len(template.content)} chars")
    except ValueError as e:
        print(f"✗ Failed: {e}")

    # Test loading a strategy template
    strategy_template = "test_generation"
    print(f"\nLoading template: {strategy_template}")
    try:
        template = engine.load_template(strategy_template)
        source = engine.get_template_source(strategy_template)
        print(f"✓ Loaded from: {source}")
        print(f"  Version: {template.version}")
        print(f"  Description: {template.description}")
        print(f"  Content length: {len(template.content)} chars")
    except ValueError as e:
        print(f"✗ Failed: {e}")

    print("\n=== Integration Test Complete ===")


if __name__ == "__main__":
    main()

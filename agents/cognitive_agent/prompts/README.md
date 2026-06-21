# Prompt Templates Directory

This directory contains prompt templates for the Cognitive Agent's **Prompt-Driven Architecture**.

## 📚 Architecture Overview

The Cognitive Agent uses a **Hybrid Architecture** with three layers:

```
Layer 1: Orchestrator (Python code)
  ↓ Infrastructure glue, file I/O, API calls, error handling

Layer 2: Strategy Manager (Prompt Engine)
  ↓ Template loading, rendering, LLM execution

Layer 3: Prompt Templates (Text files - THIS DIRECTORY)
  ↓ Business logic, decision rules, analysis strategies
```

## 🎯 Purpose

Instead of hard-coding business logic in Python (if/else statements), we use **prompt templates** that:

- ✅ Are easy to modify without redeploying code
- ✅ Can be edited by QA engineers and domain experts (no Python knowledge needed)
- ✅ Support multiple languages/frameworks via different templates
- ✅ Enable rapid experimentation and A/B testing of strategies

## 📁 Template Structure

Each template is a Markdown file with optional YAML frontmatter:

```markdown
---
name: template_name
version: 1.0
description: What this template does
author: Your Name
date: 2026-06-21
tags: [tag1, tag2]
---

# Template Title

## Context

You are an expert in {domain}. Your task is to...

## Input Variables

- **Variable 1:** {variable_1}
- **Variable 2:** {variable_2}

## Instructions

Detailed instructions for the LLM...

## Output Format

Expected output structure (JSON, markdown, etc.)
```

## 🔧 Available Templates

### 1. `test_coverage_analysis.md`
**Purpose:** Analyze test coverage and recommend improvements
**Variables:** `service_name`, `framework`, `criticality`, `current_coverage`, `target_coverage`, `python_version`
**Use Case:** Automatically assess service test quality and generate actionable recommendations

### More templates coming soon:
- `code_review_python.md` - Code review strategy for Python services
- `documentation_analysis.md` - Documentation quality assessment
- `security_scan.md` - Security vulnerability analysis
- `test_generation_python.md` - Automated test generation strategy

## 💡 How to Use

### In Python Code:

```python
from pathlib import Path
from agents.cognitive_agent.src.prompt_engine import PromptEngine

# Initialize engine
prompts_dir = Path("agents/cognitive_agent/prompts")
engine = PromptEngine(prompts_dir=prompts_dir)

# Render a template
context = {
    "service_name": "auth_service",
    "framework": "FastAPI",
    "criticality": "high",
    "current_coverage": 65,
    "target_coverage": 90,
    "python_version": "3.12"
}

prompt = engine.render("test_coverage_analysis", context)

# Execute via LLM (if client configured)
result = await engine.execute_strategy("test_coverage_analysis", context)
```

### Duel Mode (Code vs Prompt):

```python
# Compare traditional code approach vs prompt-driven approach
comparison = await engine.execute_duel_mode(
    task_description="Analyze test coverage for auth_service",
    code_approach_result=traditional_analysis_result,
    prompt_strategy="test_coverage_analysis",
    context=context,
    evaluation_criteria=["performance", "accuracy", "actionability"]
)
```

## ✏️ Creating New Templates

1. Create a new `.md` file in this directory
2. Add YAML frontmatter with metadata
3. Write your prompt using `{variable_name}` placeholders
4. Test rendering with `PromptEngine.render()`
5. Document in this README

### Best Practices:

- ✅ Be specific about the LLM's role and expertise
- ✅ Clearly define input variables and expected values
- ✅ Specify output format (JSON schema preferred)
- ✅ Include examples when helpful
- ✅ Version your templates for tracking changes
- ❌ Don't hard-code values that should be variables
- ❌ Don't make templates too long (>2000 tokens)
- ❌ Don't mix infrastructure concerns (file I/O, API calls)

## 🔄 Updating Templates

Templates can be updated **without code deployment**:

1. Edit the `.md` file
2. Increment version in frontmatter
3. Commit changes
4. Restart agent (or implement hot-reload)

This enables **rapid iteration** on business logic!

## 📊 Template Performance

Track template effectiveness:

- Execution time
- LLM response quality
- User satisfaction ratings
- Comparison with code-based approaches (duel mode)

## 🔗 Related Documentation

- [Prompt Engine Implementation](../src/prompt_engine.py)
- [Hybrid Architecture Guide](../docs/HYBRID_ARCHITECTURE.md)
- [Cognitive Agent README](../README.md)

---

**Last Updated:** 2026-06-21
**Maintained by:** Cognitive Agent Team

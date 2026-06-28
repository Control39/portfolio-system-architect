# Hybrid Architecture: Code + Prompts

## 📚 Overview

The Cognitive Agent now uses a **Hybrid Architecture** that combines the best of both worlds:

- **Code (Python)**: For infrastructure, performance-critical operations, and enterprise features
- **Prompts (Text Templates)**: For business logic, decision-making, and flexible strategies

This architecture enables rapid iteration on business logic without code deployment while maintaining production-grade reliability.

---

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────┐
│  Layer 1: Orchestrator (Python)            │
│  - autonomous_agent.py                      │
│  - Infrastructure glue (file I/O, APIs)     │
│  - Enterprise features (metrics, audit)     │
│  - Error handling & security                │
│  - Stable, rarely changes                   │
└─────────────────────────────────────────────┘
                    ↓ calls
┌─────────────────────────────────────────────┐
│  Layer 2: Strategy Manager (Prompt Engine) │
│  - src/prompt_engine.py                     │
│  - Template loading & caching               │
│  - Context injection                        │
│  - LLM execution                            │
│  - Duel mode (code vs prompt comparison)    │
└─────────────────────────────────────────────┘
                    ↓ renders
┌─────────────────────────────────────────────┐
│  Layer 3: Prompt Templates (Markdown)      │
│  - prompts/*.md                             │
│  - Business logic & decision rules          │
│  - Editable by domain experts               │
│  - Rapid iteration without deployment       │
└─────────────────────────────────────────────┘
```

---

## 🎯 Why Hybrid?

### Pure Code Approach (OLD)
```python
# Hard-coded business logic
if service_profile.criticality == 'high':
    coverage_goal = 90
    test_types = ['unit', 'integration', 'e2e']
elif service_profile.criticality == 'medium':
    coverage_goal = 75
    test_types = ['unit', 'integration']
# ... 50+ lines of if/else logic
```

**Problems:**
- ❌ Changes require code deployment
- ❌ QA engineers can't modify logic
- ❌ One version per language/framework
- ❌ Slow iteration cycle

### Pure Prompt Approach (NOT VIABLE)
```python
# Everything via LLM
prompt = "Analyze this service and tell me what to do"
result = llm.call(prompt)
```

**Problems:**
- ❌ Slow (2-5 seconds per call)
- ❌ Expensive ($0.001-0.01 per call)
- ❌ Unreliable (LLM hallucinations)
- ❌ Can't replace infrastructure code

### Hybrid Approach (✅ BEST)
```python
# Infrastructure in code
metrics_collector.record_task_completion(success=True)

# Business logic in prompts
context = {
    "service_name": service.name,
    "criticality": service.criticality,
    "current_coverage": service.test_coverage
}
result = prompt_engine.execute_strategy("test_coverage_analysis", context)
```

**Benefits:**
- ✅ Fast for infrastructure (native code)
- ✅ Flexible for business logic (edit prompts)
- ✅ Reliable for enterprise features (deterministic)
- ✅ QA-friendly (text templates)
- ✅ Multi-language support (different templates)

---

## 💡 Key Components

### 1. PromptEngine (`src/prompt_engine.py`)

```python
from agents.cognitive_agent.src.prompt_engine import PromptEngine

# Initialize
engine = PromptEngine(prompts_dir=Path("prompts/"))

# Render template
prompt = engine.render("test_coverage_analysis", {
    "service_name": "auth_service",
    "criticality": "high",
    "current_coverage": 65
})

# Execute strategy
result = await engine.execute_strategy("test_coverage_analysis", context)
```

**Features:**
- Template discovery and caching
- YAML frontmatter support
- Context variable substitution
- LLM integration (async)
- Duel mode for A/B testing

### 2. Prompt Templates (`prompts/*.md`)

Each template is a Markdown file with:
- YAML frontmatter (metadata)
- Context variables (`{variable_name}`)
- Instructions for LLM
- Expected output format

**Example:** See `prompts/test_coverage_analysis.md`

### 3. Duel Mode

Compare code-based vs prompt-based approaches:

```python
comparison = await engine.execute_duel_mode(
    task_description="Analyze test coverage",
    code_approach_result=traditional_result,
    prompt_strategy="test_coverage_analysis",
    context=context
)

# Returns:
{
    "task": "...",
    "code_approach": {...},
    "prompt_approach": {...},
    "winner": "pending_manual_review",
    "recommendation": "..."
}
```

---

## 🚀 Getting Started

### For Developers

1. **Add new strategy:**
   ```bash
   # Create template
   touch prompts/my_new_strategy.md

   # Write prompt with {variables}

   # Use in code
   result = await engine.execute_strategy("my_new_strategy", context)
   ```

2. **Modify existing strategy:**
   ```bash
   # Edit template (no code changes needed!)
   vim prompts/test_coverage_analysis.md

   # Increment version in frontmatter

   # Commit and restart agent
   ```

### For QA Engineers / Domain Experts

1. **Edit business logic:**
   - Open template file in any text editor
   - Modify instructions, rules, criteria
   - Save and commit
   - **No Python knowledge required!**

2. **Create language-specific templates:**
   - `test_generation_python.md`
   - `test_generation_go.md`
   - `test_generation_java.md`

   Agent automatically selects based on service framework!

---

## 📊 Performance Comparison

| Metric | Pure Code | Pure Prompt | Hybrid |
|--------|-----------|-------------|--------|
| **Infrastructure Speed** | ⚡ Fast | ⚡ Fast | ⚡ Fast |
| **Business Logic Flexibility** | ❌ Low | ✅ High | ✅ High |
| **Iteration Speed** | ❌ Hours (deploy) | ✅ Minutes (edit) | ✅ Minutes |
| **QA Engineer Friendly** | ❌ No | ✅ Yes | ✅ Yes |
| **Reliability** | ✅ High | ⚠️ Medium | ✅ High |
| **Cost** | ✅ $0 | ❌ $0.001/call | ✅ Minimal |

---

## 🔮 Future Enhancements

1. **Hot Reload**: Watch template files for changes, auto-reload
2. **Template Versioning**: Git-based version control for prompts
3. **A/B Testing Framework**: Automatic comparison of template versions
4. **Template Marketplace**: Share templates across projects
5. **Performance Metrics**: Track template execution time, quality scores
6. **Auto-Judging**: AI-powered evaluation of duel mode results

---

## 📖 Examples

### Example 1: Test Coverage Analysis

**Old way (hard-coded):**
```python
def analyze_coverage(service):
    if service.criticality == 'high':
        return CoverageAnalysis(goal=90, types=['unit', 'integration', 'e2e'])
    # ... more if/else
```

**New way (prompt-driven):**
```python
async def analyze_coverage(service):
    context = {
        "service_name": service.name,
        "criticality": service.criticality,
        "current_coverage": service.test_coverage,
        "target_coverage": 90 if service.criticality == 'high' else 75
    }
    result = await prompt_engine.execute_strategy("test_coverage_analysis", context)
    return parse_json_result(result['output'])
```

**Benefit:** Change coverage goals by editing prompt, not code!

### Example 2: Multi-Language Support

Create templates:
- `prompts/code_review_python.md`
- `prompts/code_review_go.md`
- `prompts/code_review_java.md`

Agent selects automatically:
```python
template_name = f"code_review_{service.language}"
result = await prompt_engine.execute_strategy(template_name, context)
```

---

## 🔗 Related Documentation

- [Prompt Engine API](src/prompt_engine.py)
- [Available Templates](prompts/README.md)
- [Cognitive Agent README](../README.md)
- [Enterprise Integration Report](../ENTERPRISE_INTEGRATION_REPORT.md)

---

**Last Updated:** 2026-06-21
**Author:** Cognitive Agent Team
**Status:** ✅ Production Ready

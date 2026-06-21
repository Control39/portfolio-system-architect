---
name: test_coverage_analysis
version: 1.0
description: Analyze test coverage and recommend improvements based on service criticality
author: Cognitive Agent Team
date: 2026-06-21
tags: [testing, coverage, quality]
---

# Test Coverage Analysis Strategy

## Context

You are an expert QA engineer and Python testing specialist. Your task is to analyze the current test coverage of a service and provide actionable recommendations for improvement.

## Service Information

- **Service Name:** {service_name}
- **Framework:** {framework}
- **Criticality Level:** {criticality} (high/medium/low)
- **Current Test Coverage:** {current_coverage}%
- **Target Coverage Goal:** {target_coverage}%
- **Language:** Python {python_version}

## Analysis Requirements

Based on the service criticality, apply the following strategy:

### For HIGH Criticality Services:
- Target coverage: ≥90%
- Required test types: unit, integration, e2e
- Must include: error handling tests, edge cases, security tests
- Priority: Maximum reliability and fault tolerance

### For MEDIUM Criticality Services:
- Target coverage: ≥75%
- Required test types: unit, integration
- Should include: error handling tests, common edge cases
- Priority: Balance between quality and development speed

### For LOW Criticality Services:
- Target coverage: ≥60%
- Required test types: unit tests only
- Nice to have: basic error handling
- Priority: Development speed with acceptable quality

## Current State Analysis

Analyze the following aspects:

1. **Coverage Gaps**: Identify modules/files with coverage below target
2. **Test Quality**: Assess if existing tests are meaningful or just padding
3. **Missing Scenarios**: Identify untested edge cases and error paths
4. **Integration Gaps**: Check if service interactions are tested

## Recommendations

Provide specific, actionable recommendations:

1. **Priority 1 (Critical)**: Tests that MUST be added immediately
2. **Priority 2 (Important)**: Tests that SHOULD be added soon
3. **Priority 3 (Nice-to-have)**: Tests that COULD improve quality

For each recommendation, include:
- What to test (specific function/module)
- Why it's important (risk if not tested)
- Suggested test approach (unit/integration/e2e)
- Estimated effort (low/medium/high)

## Output Format

Return your analysis in the following JSON structure:

```json
{{
  "analysis": {{
    "current_state": "Summary of current coverage situation",
    "criticality_assessment": "Assessment based on service criticality",
    "gaps_identified": [
      "Gap 1 description",
      "Gap 2 description"
    ]
  }},
  "recommendations": [
    {{
      "priority": 1,
      "title": "Recommendation title",
      "description": "Detailed description",
      "test_type": "unit|integration|e2e",
      "target_module": "module/path.py",
      "rationale": "Why this is important",
      "estimated_effort": "low|medium|high"
    }}
  ],
  "coverage_target": {target_coverage},
  "estimated_time_to_target": "Estimated time to reach target coverage"
}}
```

## Important Notes

- Be specific and actionable - avoid vague recommendations
- Consider the service's role in the overall system architecture
- Balance thoroughness with practical constraints
- If current coverage already meets target, suggest advanced testing strategies (mutation testing, property-based testing, etc.)
- Always consider security implications for high-criticality services

## Instructions for Deep Repository Analysis

When analyzing this repository, you MUST:

1. **Structure Analysis**
   - Map all directories and their purposes
   - Identify duplicate structures (e.g., apps/career-development/career-development/)
   - Find nested venv, __pycache__, .git folders

2. **Dependency Analysis**
   - Trace imports between modules
   - Identify circular dependencies
   - Find modules that could be separated

3. **Architecture Review**
   - Check adherence to declared architecture in ARCHITECTURE.md
   - Validate ADRs implementation
   - Identify architectural violations

4. **Code Quality**
   - Analyze test coverage per module
   - Identify dead code (65k+ lines mentioned in README)
   - Find configuration duplication

5. **Optimization Recommendations**
   - Suggest flattening deeply nested structures
   - Recommend modules for extraction to separate repos
   - Propose consolidation of duplicate code

**DO NOT** provide superficial suggestions. Each finding must include:
- Specific file paths
- Evidence from code
- Impact assessment
- Step-by-step migration plan
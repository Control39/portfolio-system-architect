# ADR Renumbering Report

**Generated:** 2026-05-23 08:29:25
**Backup:** `legacy\adr-archive\backup_20260523_082924`

## Summary

- **Total ADRs consolidated:** 18
- **Former duplicates skipped:** 6
- **Stubs skipped:** 3

## Renumbering Table

| New ID | Former ID | File | Note |
|--------|-----------|------|------|
| ADR-001 | ADR-001-system-thinking-methodology | `ADR-001-system-thinking-methodology.md` | Methodology |
| ADR-002 | ADR-001 | `ADR-002-consolidated.md` | Stack choice (Python vs Node) |
| ADR-003 | ADR-002-component-integration | `ADR-003-component-integration.md` | Component integration |
| ADR-004 | ADR-010-diagram-format | `ADR-004-diagram-format.md` | Diagram format (Mermaid) — was ADR-010 |
| ADR-005 | ADR-003-ml-model-versioning-system | `ADR-005-ml-model-versioning-system.md` | ML Model Registry |
| ADR-006 | ADR-004-data-storage-format | `ADR-006-data-storage-format.md` | Data storage format |
| ADR-007 | ADR-005-ui-technology-choice | `ADR-007-ui-technology-choice.md` | UI technology |
| ADR-008 | ADR-006-data-validation-approach | `ADR-008-data-validation-approach.md` | Data validation |
| ADR-009 | ADR-007-technology-stack-justification | `ADR-009-technology-stack-justification.md` | Stack justification |
| ADR-010 | ADR-008-service-discovery | `ADR-010-service-discovery.md` | Service discovery |
| ADR-011 | ADR-009-base-docker-images | `ADR-011-base-docker-images.md` | Base Docker images |
| ADR-012 | ADR-010-vscode-settings-separation | `ADR-012-vscode-settings-separation.md` | VSCode settings separation |
| ADR-014 | ADR-015-monorepo-boundary | `ADR-014-monorepo-boundary.md` | src/ vs apps/ boundary — was ADR-015 |
| ADR-015 | ADR-016-standardize-documentation | `ADR-015-standardize-documentation.md` | Documentation standard — was ADR-016 |
| ADR-016 | ADR-017-mcp-server-coverage-decision | `ADR-016-mcp-server-coverage-decision.md` | MCP Server coverage — was ADR-017 |
| ADR-017 | ADR-018-dependency-injection | `ADR-017-dependency-injection.md` | Dependency injection — was ADR-018 |
| ADR-018 | ADR-018-documentation-and-audit-standards | `ADR-018-documentation-and-audit-standards.md` | Documentation & audit — was ADR-018 |
| ADR-019 | ADR-019-local-vs-cloud-llm | `ADR-019-local-vs-cloud-llm.md` | Local vs Cloud LLM |

## Skipped Files

| File | Reason |
|------|--------|
| `adr-template.md` | Stub/template/redirect |
| `ADR-001-system-thinking-methodology.md` | Stub/template/redirect |
| `ADR-002.md` | Stub/template/redirect |
| `docs/adr/ADR-002-component-integration.md` | Duplicate (identical to decisions/) |
| `docs/adr/ADR-009-base-docker-images.md` | Duplicate (identical to decisions/) |
| `docs/adr/ADR-003-ml-model-versioning-system.md` | Duplicate (identical to decisions/) |
| `docs/adr/ADR-005-ui-technology-choice.md` | Duplicate (identical to decisions/) |
| `docs/adr/ADR-007-technology-stack-justification.md` | Duplicate (identical to decisions/) |
| `docs/adr/ADR-006-data-validation-approach.md` | Duplicate (identical to decisions/) |

## Next Steps

1. Update cross-references in README files to use new ADR numbers.
2. Update `README.md` ADR table.
3. Update `CONTRIBUTING.md` ADR examples.
4. Archive `docs/adr/` directory (or remove after verification).

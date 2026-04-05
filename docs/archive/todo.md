> [!NOTE]
> Актуальные задачи перенесены в GitHub Issues:
> - [#15](https://github.com/Control39/cognitive-systems-architecture/issues/15) — Improve Pester reporting in tests/run-tests.ps1
> - [#16](https://github.com/Control39/cognitive-systems-architecture/issues/16) — Add PSScriptInfo metadata to tools/*.ps1 scripts
> - [#17](https://github.com/Control39/cognitive-systems-architecture/issues/17) — Re-validate all PowerShell scripts with Test-ScriptFileInfo
> - [#18](https://github.com/Control39/cognitive-systems-architecture/issues/18) — Runtime test all PowerShell scripts

# PowerShell Error Fixes TODO

## Completed
- [x] Validate syntax with Test-ScriptFileInfo (confirmed parse errors in tests/run-tests.ps1, RAG/*.ps1, examples/*.ps1)

## In Progress
## Completed
- [x] Edit param() comments in tests/run-tests.ps1
- [x] Fix apps/system-proof/system-proof/RAG/process_document.ps1 param block
- [x] Fix apps/system-proof/system-proof/RAG/organize_files.ps1 params
- [x] Fix apps/system-proof/system-proof/RAG/auto_upload_cycle.ps1 param
- [x] Fix docs/integrations/examples/*.ps1 params (param syntax resolved)

## Pending
1. Improve tests/run-tests.ps1 reporting (Pester)
2. Add PSScriptInfo to tools/*.ps1 (optional)
3. Re-validate all with Test-ScriptFileInfo
4. Test runtime: powershell -File *.ps1
5. Commit changes

Updated: $(Get-Date)

Updated: $(Get-Date)


# TODO: Fix SourceCraft Review Issues from PR feature/integrate-reasoning-api to main

Approved plan implementation steps (PowerShell-focused fixes for typos, var decl, hardcoded test secrets):

## 1. Create branch & setup
- [ ] `git checkout -b blackboxai/fix-review-issues`
- [ ] Commit all changes at end

## 2. Fix src/core/security/SecretManager.psm1 (Lees → Leaks)
- [ ] Replace class property `$Lees`
- [ ] Replace `$result.Lees.Add`
- [ ] Replace `$checkResult.Lees.Count`
- [ ] Verify with `Get-Content src/core/security/SecretManager.psm1 | Select-String Leaks`

## 3. Fix src/core/logging/StructuredLogger.psm1 (declare $entry)
- [ ] Add `[LogEntry]$entry = $null` before each TryDequeue while loop (~5 places)
- [ ] Verify syntax

## 4. Fix hardcoded secrets in tests (replace with random gen)
- [ ] `tests/unit/security/SecretManager.Tests.ps1`: sk-*, P@ssw0rd123!, eyJhbGci, my-secret-key-12345
- [ ] `tests/unit/security/SecurityScanner.Tests.ps1`: sk-1234567890, P@ssw0rd!, eyJhbGci, sk-test123456789012345678901234567890, mypassword123
- [ ] `tests/unit/core/logging/StructuredLogger.Tests.ps1`: secret-key-12345
- [ ] `tests/unit/core/validation/InputValidator.Tests.ps1`: "sk-" + ("a"*32)
- [ ] `tests/unit/core/security/SecurityScanner.Tests.ps1`: testSecretValue hardcoded
- [ ] Update OpenAI key gen: random chars after sk-

## 5. Enhance primitive tests
- [ ] SecurityScanner/SecretManager: Add specific assertions (e.g., SuspiciousFiles.Count)

## 6. Test & Verify
- [ ] `Invoke-Pester -Path './tests/unit' -Output Detailed`
- [ ] Manual security scan if available: `Invoke-SecurityScan`
- [ ] Check no gitleaks patterns: `gitleaks detect --source .` (if installed)

## 7. Complete
- [ ] `attempt_completion` with summary
- [ ] Suggest GH CLI PR: `gh pr create --title "Fix review issues" --body "Addresses all SourceCraft comments"`

Progress: Fixed SecretManager.psm1 (Lees→Leaks), 4 test files hardcoded secrets → random gen. StructuredLogger already has $entry decls. Next: remaining tests, Pester verify.


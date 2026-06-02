# Добавьте в класс SecurityScanner (или как отдельную функцию)

function Get-SecurityScore {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$RepoPath
    )

    # Разрешаем путь
    $RepoPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($RepoPath)
    if (-not (Test-Path $RepoPath)) {
        throw "Repository path not found: $RepoPath"
    }

    $score = 100
    $recommendations = [System.Collections.Generic.List[string]]::new()
    $findings = @()

    # --- 1. Проверка на найденные секреты ---
    try {
        $scanResult = Invoke-SecurityScan -TargetPath $RepoPath -ScanForSecrets:$true -RunExternalTools:$false -CheckGitignore:$false
        $secretCount = $scanResult.Findings.Count

        if ($secretCount -gt 0) {
            $penalty = 10 * $secretCount
            $score -= $penalty
            $findings += "Found $secretCount potential secrets"
            $recommendations.Add("Remove hardcoded secrets immediately. Check: $($scanResult.Findings[0].FilePath)")
        }
    }
    catch {
        [StructuredLogger]::Log("Failed to scan for secrets during scoring: $($_.Exception.Message)", "WARN")
        $score -= 20  # Штраф за невозможность проверить
        $recommendations.Add("Security scan failed — ensure scanner is working")
    }

    # --- 2. Проверка .gitignore ---
    $gitignorePath = Join-Path $RepoPath ".gitignore"
    if (-not (Test-Path $gitignorePath)) {
        $score -= 20
        $findings += ".gitignore missing"
        $recommendations.Add("Create .gitignore to prevent accidental commit of secrets/configs")
    } else {
        $content = Get-Content $gitignorePath -Raw
        if ($content -notmatch 'secret|env|key|token|password|private|pfx|p12') {
            $score -= 10  # Мягче, чем полное отсутствие
            $findings += ".gitignore exists but may not cover secrets"
            $recommendations.Add("Improve .gitignore with rules for secrets, .env, *.pfx, etc.")
        }
    }

    # --- 3. Проверка на hardcoded пароли (дополнительно к сканеру) ---
    $dangerousPatterns = @(
        'password\s*=\s*["''][^"''\s]*["'']',
        'pwd\s*=\s*["''][^"''\s]*["'']',
        'pass\s*=\s*["''][^"''\s]*["'']'
    )

    $codeFiles = Get-ChildItem $RepoPath -File -Include @('.ps1','.py','.js','.ts','.json','.yaml','.yml') -Recurse -ErrorAction SilentlyContinue
    $hardcodedPasswordCount = 0

    foreach ($file in $codeFiles) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) {
            foreach ($pattern in $dangerousPatterns) {
                if ($content -match $pattern) {
                    $hardcodedPasswordCount++
                }
            }
        }
    }

    if ($hardcodedPasswordCount -gt 0) {
        $penalty = 15 * $hardcodedPasswordCount
        $score = [math]::Max(0, $score - $penalty)
        $findings += "$hardcodedPasswordCount hardcoded passwords found"
        $recommendations.Add("Replace hardcoded passwords with SecretManager or environment variables")
    }

    # --- 4. Проверка устаревших зависимостей (пример для Python) ---
    $requirements = Join-Path $RepoPath "requirements.txt"
    $outdatedCount = 0

    if (Test-Path $requirements) {
        if (Get-Command "pip" -ErrorAction SilentlyContinue) {
            try {
                $outdated = pip list --outdated --format=json | ConvertFrom-Json
                $outdatedCount = $outdated.Count
                if ($outdatedCount -gt 0) {
                    $score -= 5 * $outdatedCount
                    $findings += "$outdatedCount outdated Python packages"
                    $recommendations.Add("Update outdated Python packages: $(($outdated.name) -join ', ')")
                }
            }
            catch {
                [StructuredLogger]::Log("pip list failed: $_", "DEBUG")
            }
        }
    }

    # --- 5. Проверка использования SecretManager ---
    $usesSecretManager = $false
    foreach ($file in $codeFiles) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -match '\[SecretManager\]::GetSecret') {
            $usesSecretManager = $true
            break
        }
    }

    if ($usesSecretManager) {
        $score = [math]::Min(100, $score + 20)  # Бонус
        $recommendations.Add("Good: Uses SecretManager for secure secret handling")
    } else {
        $score -= 30
        $recommendations.Add("Use SecretManager to manage secrets instead of environment variables or hardcoded values")
    }

    # --- 6. Проверка наличия security тестов ---
    $hasSecurityTests = @(Get-ChildItem $RepoPath -PathType Leaf -Filter "*security*.Tests.ps1" -Recurse).Count -gt 0
    if ($hasSecurityTests) {
        $score = [math]::Min(100, $score + 15)
        $recommendations.Add("Good: Security tests detected")
    } else {
        $recommendations.Add("Add security unit/integration tests")
    }

    # --- 7. Проверка .security-whitelist (если используется gitleaks) ---
    $hasWhitelist = Test-Path (Join-Path $RepoPath ".gitleaks.toml") -or
                    Test-Path (Join-Path $RepoPath ".gitleaks.yml") -or
                    Test-Path (Join-Path $RepoPath ".security-whitelist")

    if ($hasWhitelist) {
        $score = [math]::Min(100, $score + 10)
        $recommendations.Add("Good: Security whitelist detected (.gitleaks.*)")
    } else {
        $recommendations.Add("Add .gitleaks.toml to whitelist known safe patterns")
    }

    # --- Формирование результата ---
    $finalScore = [math]::Max(0, [math]::Min(100, $score))

    $grade = if ($finalScore -ge 90) { "A" }
             elseif ($finalScore -ge 80) { "B" }
             elseif ($finalScore -ge 70) { "C" }
             elseif ($finalScore -ge 60) { "D" }
             else { "F" }

    $result = @{
        Score           = $finalScore
        Grade           = $grade
        Findings        = $findings
        Recommendations = $recommendations
        Timestamp       = [DateTime]::UtcNow.ToString("o")
        RepoPath        = $RepoPath
    }

    [StructuredLogger]::Log("Security score calculated", "INFO", @{
        Score = $finalScore
        Grade = $grade
        FindingsCount = $findings.Count
    })

    return $result
}

# Экспорт функции
Export-ModuleMember -Function Invoke-SecurityScan, Get-SecurityScore

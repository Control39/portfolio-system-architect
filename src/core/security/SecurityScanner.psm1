# src/core/security/SecurityScanner.psm1

using module ../../core/logging/StructuredLogger
using module ../../core/validation/Validators

# Класс результата сканирования
class SecurityScanResult {
    [bool] $Success
    [System.Collections.Generic.List[hashtable]] $Findings
    [System.Collections.Generic.List[string]] $GitignoreIssues
    [hashtable] $ExternalToolResults
    [hashtable] $Summary
    [string] $TargetPath
    [datetime] $Timestamp

    SecurityScanResult([string]$TargetPath) {
        $this.TargetPath = $TargetPath
        $this.Timestamp = [DateTime]::UtcNow
        $this.Success = $true
        $this.Findings = [System.Collections.Generic.List[hashtable]]::new()
        $this.GitignoreIssues = [System.Collections.Generic.List[string]]::new()
        $this.ExternalToolResults = @{}
        $this.Summary = @{
            SecretsFound = 0
            GitignoreIssues = 0
            ExternalToolsRun = 0
        }
    }

    [void] AddFinding([string]$Type, [string]$Severity, [string]$FilePath, [int]$LineNumber, [string]$Message, [string]$Pattern) {
        $this.Findings.Add(@{
            Type = $Type
            Severity = $Severity
            FilePath = $FilePath
            LineNumber = $LineNumber
            Message = $Message
            Pattern = $Pattern
            Timestamp = $this.Timestamp
        })
        $this.Summary.SecretsFound++
        $this.Success = $false  # Хотя бы одно нахождение — уже проблема
    }

    [void] AddGitignoreIssue([string]$FilePath, [string]$Recommendation) {
        $this.GitignoreIssues.Add("$FilePath : $Recommendation")
        $this.Summary.GitignoreIssues++
        $this.Success = $false
    }
}

function Invoke-SecurityScan {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$TargetPath,

        [switch]$IncludeSubdirectories = $true,
        [switch]$ScanForSecrets = $true,
        [switch]$RunExternalTools = $true,
        [switch]$CheckGitignore = $true
    )

    # Разрешаем путь
    $TargetPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($TargetPath)
    if (-not (Test-Path $TargetPath)) {
        throw "Target path not found: $TargetPath"
    }

    # Инициализируем результат
    $result = [SecurityScanResult]::new($TargetPath)

    [StructuredLogger]::Log("Starting security scan", "INFO", @{
        TargetPath = $TargetPath
        ScanForSecrets = $ScanForSecrets
        RunExternalTools = $RunExternalTools
    })

    # --- 1. Проверка на секреты ---
    if ($ScanForSecrets) {
        try {
            $result = [SecurityScanner]::ScanForHardcodedSecrets($TargetPath, $IncludeSubdirectories, $result)
        }
        catch {
            [StructuredLogger]::Log("Error during secret scan: $($_.Exception.Message)", "ERROR")
            $result.Success = $false
        }
    }

    # --- 2. Проверка .gitignore ---
    if ($CheckGitignore) {
        try {
            $result = [SecurityScanner]::CheckGitignorePolicy($TargetPath, $result)
        }
        catch {
            [StructuredLogger]::Log("Error during .gitignore analysis: $($_.Exception.Message)", "ERROR")
        }
    }

    # --- 3. Внешние инструменты ---
    if ($RunExternalTools) {
        try {
            $result = [SecurityScanner]::RunExternalSecurityTools($TargetPath, $result)
        }
        catch {
            [StructuredLogger]::Log("Error during external tool execution: $($_.Exception.Message)", "ERROR")
        }
    }

    # --- 4. Логирование итогов ---
    $status = if ($result.Success) { "No critical issues found" } else { "Issues detected" }
    [StructuredLogger]::Log("Security scan completed: $status", "INFO", @{
        FindingsCount = $result.Findings.Count
        GitignoreIssues = $result.GitignoreIssues.Count
    })

    return $result
}

# Статический класс для логики
class SecurityScanner {
    # Основной поиск секретов
    static [SecurityScanResult] ScanForHardcodedSecrets([string]$Path, [bool]$Recurse, [SecurityScanResult]$Result) {
        $patterns = @(
            @{ Type = "Password"; Pattern = 'password\s*=\s*["''][^"''\s]{8,}["'']' }
            @{ Type = "Secret";   Pattern = 'secret\s*=\s*["''][^"''\s]{8,}["'']' }
            @{ Type = "Token";    Pattern = 'token\s*=\s*["''][^"''\s]{20,}["'']' }
            @{ Type = "API Key";  Pattern = 'api[_-]?key\s*=\s*["''][^"''\s]{20,}["'']' }
            @{ Type = "OpenAI Key"; Pattern = 'sk-[a-zA-Z0-9]{48,}' }
        )

        # Добавляем известные секреты из SecretManager
        if ([SecretManager]::IsInitialized) {
            $currentSecrets = [SecretManager]::GetAllSecretNames()
            foreach ($name in $currentSecrets) {
                $patterns += @{ Type = "Hardcoded Secret"; Pattern = [regex]::Escape($name) }
            }

            # Также проверим значения (аккуратно!)
            $allSecrets = [SecretManager]::GetAllSecrets()
            foreach ($secret in $allSecrets.GetEnumerator()) {
                $value = $secret.Value
                if ($value -and $value.Length -ge 10) {
                    # Экранируем только начало, чтобы не выдать всё
                    $safePattern = '^' + [regex]::Escape($value.Substring(0, [Math]::Min(10, $value.Length)))
                    $patterns += @{ Type = "Exposed Secret Value"; Pattern = $safePattern; IsValue = $true }
                }
            }
        }

        $fileTypes = @('.txt', '.json', '.yaml', '.yml', '.ps1', '.py', '.js', '.config', '.env', '.settings')

        $files = Get-ChildItem -Path $Path -File -Recurse:$Recurse | Where-Object { $_.Extension -in $fileTypes }

        foreach ($file in $files) {
            try {
                $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
                $lines = $content -split '\r?\n'

                foreach ($p in $patterns) {
                    $regex = [regex]::new($p.Pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
                    $matches = $regex.Matches($content)

                    foreach ($match in $matches) {
                        $lineNumber = ($content.Substring(0, $match.Index) -split '\r?\n').Count
                        $Result.AddFinding(
                            $p.Type,
                            "High",
                            $file.FullName,
                            $lineNumber,
                            "Potential secret detected",
                            $p.Pattern
                        )

                        [StructuredLogger]::Log(
                            "Potential secret found",
                            "WARN",
                            @{
                                File = $file.FullName
                                Line = $lineNumber
                                Type = $p.Type
                                Pattern = $p.Pattern
                            }
                        )
                    }
                }
            }
            catch {
                [StructuredLogger]::Log("Could not read file for scan: $($file.FullName)", "WARN")
            }
        }

        return $Result
    }

    # Проверка .gitignore
    static [SecurityScanResult] CheckGitignorePolicy([string]$Path, [SecurityScanResult]$Result) {
        $gitignore = Join-Path $Path ".gitignore"
        $importantPatterns = @(".env", "secrets.*", "*.pfx", "*.p12", "appsettings.*.json", "credentials", "id_rsa")

        if (-not (Test-Path $gitignore)) {
            $Result.AddGitignoreIssue($gitignore, "File does not exist - secrets may be committed")
            return $Result
        }

        $content = Get-Content $gitignore -Raw
        foreach ($pattern in $importantPatterns) {
            if ($content -notmatch [regex]::Escape($pattern)) {
                $Result.AddGitignoreIssue($gitignore, "Missing rule: $pattern")
            }
        }

        return $Result
    }

    # Запуск внешних инструментов
    static [SecurityScanResult] RunExternalSecurityTools([string]$Path, [SecurityScanResult]$Result) {
        $tools = @(
            @{ Name = "gitleaks"; Check = { Get-Command gitleaks -ErrorAction SilentlyContinue }; Script = { & gitleaks detect --source $Path --report-format json } }
            @{ Name = "bandit";   Check = { Get-Command bandit -ErrorAction SilentlyContinue }; Script = { & bandit -r $Path -f json } }
            @{ Name = "safety";   Check = { Get-Command safety -ErrorAction SilentlyContinue }; Script = { & safety check --file (Join-Path $Path "requirements.txt") --json } }
        )

        $toolResults = @{}
        foreach ($tool in $tools) {
            if (& $tool.Check) {
                try {
                    $output = & $tool.Script
                    $toolResults[$tool.Name] = @{
                        Success = $LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1
                        ExitCode = $LASTEXITCODE
                        Output = $output
                    }
                    [StructuredLogger]::Log("$($tool.Name) scan completed", "INFO", @{ ExitCode = $LASTEXITCODE })
                }
                catch {
                    $toolResults[$tool.Name] = @{ Success = $false; Error = $_.Exception.Message }
                    [StructuredLogger]::Log("$($tool.Name) failed to execute", "WARN")
                }
            }
            else {
                $toolResults[$tool.Name] = @{ Success = $false; Error = "Not found in PATH" }
                [StructuredLogger]::Log("$($tool.Name) not found", "DEBUG")
            }
        }

        $Result.ExternalToolResults = $toolResults
        $Result.Summary.ExternalToolsRun = ($toolResults.Values | Where-Object { $_.Success }).Count

        return $Result
    }
}

Export-ModuleMember -Function Invoke-SecurityScan

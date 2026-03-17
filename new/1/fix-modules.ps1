# fix-modules.ps1
# Создание модулей Arch-Compass вручную

# Создаём папки
New-Item -Path "src\core\utilities" -ItemType Directory -Force | Out-Null
New-Item -Path "src\infrastructure\security" -ItemType Directory -Force | Out-Null

# ConfigurationManager.psm1
Set-Content -Path "src\core\utilities\ConfigurationManager.psm1" -Value @"
class ConfigurationManager {
    static [hashtable] `$Configuration = @{}

    [void] Initialize([string]`$environment = 'default') {
        Write-Verbose 'Конфигурация инициализирована для окружения: `$environment'
        [ConfigurationManager]::Configuration = @{
            Environment = `$environment
            Paths = @{ Source = './src'; Artifacts = './artifacts' }
            Features = @{ AIEnabled = `$true; SecurityScan = `$true }
        }
    }

    [object] GetValue([string]`$key, [object]`$defaultValue = `$null) {
        `$keys = `$key -split '\.'
        `$current = [ConfigurationManager]::Configuration
        foreach (`$k in `$keys) {
            if (`$current.ContainsKey(`$k)) { 
                `$current = `$current[`$k] 
            } else { 
                return `$defaultValue 
            }
        }
        return `$current
    }

    [void] SetValue([string]`$key, [object]`$value) {
        `$keys = `$key -split '\.', 0, 'RegexMatch'
        `$current = [ConfigurationManager]::Configuration
        for (`$i = 0; `$i -lt `$keys.Length - 1; `$i++) {
            `$k = `$keys[`$i]
            if (-not `$current.ContainsKey(`$k)) { 
                `$current[`$k] = @{} 
            }
            `$current = `$current[`$k]
        }
        `$current[`$keys[-1]] = `$value
    }
}

Export-ModuleMember -Variable ConfigurationManager
"@ -Encoding UTF8

# SecurityScanner.psm1
Set-Content -Path "src\infrastructure\security\SecurityScanner.psm1" -Value @"
class SecurityScanResult {
    [string] `$Severity
    [string] `$Category
    [string] `$Message
    [string] `$File
    [int] `$Line
    [string] `$Recommendation

    SecurityScanResult([string]`$severity, [string]`$category, [string]`$message, [string]`$file, [int]`$line, [string]`$recommendation) {
        `$this.Severity = `$severity
        `$this.Category = `$category
        `$this.Message = `$message
        `$this.File = `$file
        `$this.Line = `$line
        `$this.Recommendation = `$recommendation
    }
}

class SecurityScanner {
    static [System.Collections.Generic.List[SecurityScanResult]] `$ScanResults = [System.Collections.Generic.List[SecurityScanResult]]::new()

    static [void] Invoke-SecurityScan([hashtable]`$config = @{}) {
        `$projectRoot = `$config.ProjectRoot ?? '..'
        if (-not (Test-Path `$projectRoot)) {
            Write-Warning 'Не удалось найти корень проекта: `$projectRoot'
            return
        }

        [SecurityScanner]::ScanResults.Clear()
        [SecurityScanner]::CheckForHardcodedSecrets(`$projectRoot)
        [SecurityScanner]::CheckGitIgnore(`$projectRoot)
        [SecurityScanner]::CheckFilePermissions(`$projectRoot)
    }

    hidden static [void] CheckForHardcodedSecrets([string]`$projectRoot) {
        `$searchPatterns = @(
            @{ Pattern = '(?i)(api[_-]?key|apikey)\s*[=:]\s*["'']?([a-zA-Z0-9_\-]{32,})'; Description = 'API Key' },
            @{ Pattern = '(?i)(token|auth[_-]?token)\s*[=:]\s*["'']?([a-zA-Z0-9\.\-_]{40,})'; Description = 'Auth Token' },
            @{ Pattern = '(?i)(password|pwd)\s*[=:]\s*["'']?(\w+)'; Description = 'Password' }
        )

        Get-ChildItem `$projectRoot -Recurse -Include *.ps1, *.psm1, *.json, *.yaml, *.yml, *.config, *.txt -ErrorAction SilentlyContinue | ForEach-Object {
            `$content = Get-Content `$_.FullName -Raw
            `$lines = Get-Content `$_.FullName

            foreach (`$pattern in `$searchPatterns) {
                `$matches = [regex]::Matches(`$content, `$pattern.Pattern)
                foreach (`$match in `$matches) {
                    `$lineNumber = 0
                    for (`$i = 0; `$i -lt `$lines.Count; `$i++) {
                        if (`$lines[`$i].Contains(`$match.Value)) {
                            `$lineNumber = `$i + 1
                            break
                        }
                    }

                    [SecurityScanner]::ScanResults += [SecurityScanResult]::new(
                        'High',
                        'HardcodedSecret',
                        'Найден `$($pattern.Description): `$($match.Groups[2].Value.Substring(0, 10))...',
                        `$_.FullName,
                        `$lineNumber,
                        'Используйте SecretManager для хранения секретов. Никогда не коммитьте секреты в репозиторий.'
                    )
                }
            }
        }
    }

    hidden static [void] CheckGitIgnore([string]`$projectRoot) {
        `$gitignorePath = Join-Path `$projectRoot '.gitignore'
        if (-not (Test-Path `$gitignorePath)) {
            [SecurityScanner]::ScanResults += [SecurityScanResult]::new(
                'Medium',
                'GitIgnore',
                'Файл .gitignore отсутствует',
                `$gitignorePath,
                0,
                'Создайте .gitignore для исключения чувствительных файлов'
            )
            return
        }

        `$gitignoreContent = Get-Content -Path `$gitignorePath -Raw
        `$requiredPatterns = @('.env', '*.key', '*.pem', 'secrets/', '*.secret')
        foreach (`$pattern in `$requiredPatterns) {
            if (`$gitignoreContent -notmatch [regex]::Escape(`$pattern)) {
                [SecurityScanner]::ScanResults += [SecurityScanResult]::new(
                    'Medium',
                    'GitIgnore',
                    'Паттерн ''`$pattern'' отсутствует в .gitignore',
                    `$gitignorePath,
                    0,
                    'Добавьте ''`$pattern'' в .gitignore'
                )
            }
        }
    }

    hidden static [void] CheckFilePermissions([string]`$projectRoot) {
        `$sensitivePaths = @('*.pem', '*.key', 'secrets.json')
        foreach (`$path in `$sensitivePaths) {
            Get-ChildItem `$projectRoot -Recurse -Include `$path -ErrorAction SilentlyContinue | ForEach-Object {
                `$acl = Get-Acl `$_.FullName
                if (`$acl.Owner -ne '$env:USERDOMAIN\$env:USERNAME') {
                    [SecurityScanner]::ScanResults += [SecurityScanResult]::new(
                        'Medium',
                        'FilePermission',
                        'Файл `$($_.Name) имеет неправильного владельца',
                        `$_.FullName,
                        0,
                        'Убедитесь, что владелец — текущий пользователь'
                    )
                }
            }
        }
    }

    static [SecurityScanResult[]] GetResults() {
        return [SecurityScanResult[]][SecurityScanner]::ScanResults.ToArray()
    }
}

Export-ModuleMember -Variable SecurityScanner
"@ -Encoding UTF8

Write-Host "✅ Модули созданы с правильной кодировкой UTF-8 (с BOM)" -ForegroundColor Green
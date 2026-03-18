class SecurityScanResult {
    [string] $Severity
    [string] $Category
    [string] $Message
    [string] $File
    [int] $Line
    [string] $Recommendation

    SecurityScanResult([string]$severity, [string]$category, [string]$message, [string]$file, [int]$line, [string]$recommendation) {
        $this.Severity = $severity
        $this.Category = $category
        $this.Message = $message
        $this.File = $file
        $this.Line = $line
        $this.Recommendation = $recommendation
    }
}

class SecurityScanner {
    static [System.Collections.Generic.List[SecurityScanResult]] $ScanResults = [System.Collections.Generic.List[SecurityScanResult]]::new()

    static [void] InvokeSecurityScan([hashtable]$config) {
        $projectRoot = if ($config.ContainsKey('ProjectRoot')) { $config.ProjectRoot } else { '..' }

        if (-not (Test-Path $projectRoot)) {
            Write-Warning "Project root not found: $projectRoot"
            return
        }

        [SecurityScanner]::ScanResults.Clear()
        [SecurityScanner]::CheckForHardcodedSecrets($projectRoot)
        [SecurityScanner]::CheckGitIgnore($projectRoot)
        [SecurityScanner]::CheckFilePermissions($projectRoot)
    }

    hidden static [void] CheckForHardcodedSecrets([string]$projectRoot) {
        $searchPatterns = @(
            @{ Pattern = '(?i)(api[_-]?key|apikey)\s*[=:]\s*["'']?([a-zA-Z0-9_\-]{32,})'; Description = 'API Key' },
            @{ Pattern = '(?i)(token|auth[_-]?token)\s*[=:]\s*["'']?([a-zA-Z0-9\.\-_]{40,})'; Description = 'Auth Token' },
            @{ Pattern = '(?i)(password|pwd)\s*[=:]\s*["'']?([a-zA-Z0-9!@#$%^&*()_+\-=\\[\\]{}|;:,.<>?]{8,})'; Description = 'Password' }
        )

        Get-ChildItem $projectRoot -Recurse -Include *.ps1, *.psm1, *.json, *.yaml, *.yml, *.config, *.txt -ErrorAction SilentlyContinue | ForEach-Object {
            $content = Get-Content $_.FullName -Raw
            $lines = Get-Content $_.FullName

            foreach ($pattern in $searchPatterns) {
                $matches = [regex]::Matches($content, $pattern.Pattern)
                foreach ($match in $matches) {
                    $lineNumber = 0
                    for ($i = 0; $i -lt $lines.Count; $i++) {
                        if ($lines[$i].Contains($match.Value)) {
                            $lineNumber = $i + 1
                            break
                        }
                    }

                    $secretValue = $match.Groups[2].Value
                    if ($secretValue.Length -gt 10) {
                        $displayValue = $secretValue.Substring(0, 10)
                    } else {
                        $displayValue = $secretValue
                    }
                    [SecurityScanner]::ScanResults += [SecurityScanResult]::new(
                        'High',
                        'HardcodedSecret',
                        "Found $($pattern.Description): ${displayValue}...",
                        $_.FullName,
                        $lineNumber,
                        "Use SecretManager to store secrets. Never commit secrets to the repository."
                    )
                }
            }
        }
    }

    hidden static [void] CheckGitIgnore([string]$projectRoot) {
        $gitignorePath = Join-Path $projectRoot '.gitignore'
        if (-not (Test-Path $gitignorePath)) {
            [SecurityScanner]::ScanResults += [SecurityScanResult]::new(
                'Medium',
                'GitIgnore',
                'File .gitignore is missing',
                $gitignorePath,
                0,
                'Create .gitignore to exclude sensitive files'
            )
            return
        }

        $gitignoreContent = Get-Content -Path $gitignorePath -Raw
        $requiredPatterns = @('.env', '*.key', '*.pem', 'secrets/', '*.secret', 'credentials.json', 'config.json', 'passwords.txt')
        foreach ($pattern in $requiredPatterns) {
            if ($gitignoreContent -notmatch [regex]::Escape($pattern)) {
                [SecurityScanner]::ScanResults += [SecurityScanResult]::new(
                    'Medium',
                    'GitIgnore',
                    "Pattern '$pattern' is missing in .gitignore",
                    $gitignorePath,
                    0,
                    "Add '$pattern' to .gitignore"
                )
            }
        }
    }

    hidden static [void] CheckFilePermissions([string]$projectRoot) {
        $sensitivePaths = @('*.pem', '*.key', 'secrets.json')
        foreach ($path in $sensitivePaths) {
            Get-ChildItem $projectRoot -Recurse -Include $path -ErrorAction SilentlyContinue | ForEach-Object {
                $acl = Get-Acl $_.FullName
                $currentUser = "$env:USERDOMAIN\$env:USERNAME"
                if ($acl.Owner -ne $currentUser) {
                    [SecurityScanner]::ScanResults += [SecurityScanResult]::new(
                        'Medium',
                        'FilePermission',
                        "File $($_.Name) has incorrect owner",
                        $_.FullName,
                        0,
                        "Ensure the owner is the current user ($currentUser)"
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
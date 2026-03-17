# src/core/security/SecretManager.psm1

using namespace System.Collections.Concurrent

class SecretManager {
    hidden static [ConcurrentDictionary[string, string]] $Cache = [ConcurrentDictionary[string, string]]::new()
    hidden static [bool] $Initialized = $false
    hidden static [scriptblock] $SecretMasker = $null

    static [void] Initialize() {
        if ([SecretManager]::$Initialized) { return }

        [SecretManager]::WriteInfoLog("Initializing SecretManager...")

        # === КРИТИЧЕСКИЙ МОМЕНТ: НЕ вызываем SecurityScanner здесь ===
        # Вместо этого — мы сообщаем, что готовы, и предлагаем использовать [SecretManager]::GetLeakCheckDelegate()

        [SecretManager]::$SecretMasker = {
            param([string]$text)
            return [SecretManager]::MaskSecretsInText($text)
        }

        [SecretManager]::$Initialized = $true
        [SecretManager]::WriteInfoLog("SecretManager initialized.")
    }

    static [void] SetSecret([string]$Name, [string]$Value) {
        if (-not [SecretManager]::$Initialized) { throw "Not initialized" }
        [SecretManager]::$Cache[$Name] = [SecretManager]::Encrypt($Value)
    }

    static [string] GetSecret([string]$Name, [string]$Default = $null) {
        if ([SecretManager]::$Cache.TryGetValue($Name, [ref]$encrypted)) {
            return [SecretManager]::Decrypt($encrypted)
        }
        return $Default
    }

    static [string] MaskSecretsInText([string]$Text) {
        if ([string]::IsNullOrWhiteSpace($Text)) { return $Text }
        $text = $Text
        foreach ($name in [SecretManager]::$Cache.Keys) {
            $value = [SecretManager]::Decrypt([SecretManager]::$Cache[$name])
            if ($value.Length -ge 6) {
                $text = $text -replace [regex]::Escape($value), "***SECRET***"
            }
        }
        return $text
    }

    # Возвращает делегат для проверки утечек — чтобы SecurityScanner мог использовать
    static [scriptblock] GetLeakCheckDelegate() {
        return {
            param([string]$Path)
            $result = [System.Collections.Generic.List[string]]::new()
            $files = Get-ChildItem $Path -File -Include @('.ps1','.py','.json','.yaml','.yml','.env') -Recurse -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
                if ($content) {
                    foreach ($name in [SecretManager]::$Cache.Keys) {
                        $value = [SecretManager]::Decrypt([SecretManager]::$Cache[$name])
                        if ($value -and $content -match [regex]::Escape($value)) {
                            $result.Add("Secret '$name' leaked in $($file.FullName)")
                        }
                    }
                }
            }
            return $result
        }
    }

    hidden static [string] Encrypt([string]$Data) {
        if (-not $Data) { return $Data }
        "enc:$([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Data)))"
    }

    hidden static [string] Decrypt([string]$Data) {
        if (-not $Data -or -not $Data.StartsWith("enc:")) { return $Data }
        try { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Data.Substring(4))) }
        catch { $Data }
    }

    hidden static [void] WriteInfoLog([string]$Message) {
        if (Get-Command Write-Log -ErrorAction SilentlyContinue) {
            Write-Log $Message -Level "INFO"
        } else {
            Write-Host "[SecretManager:INFO] $Message"
        }
    }
}

Export-ModuleMember -Class SecretManager

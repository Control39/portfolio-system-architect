# src/core/utilities/Utilities.psm1

# ... (вспомогательные функции) ...

# =================== ОСНОВНАЯ ЛОГИКА ===================
function Main {
    param(
        [ValidateSet("init", "deploy", "analyze", "report")]
        [string]$Command = "init",

        [string]$RepoName,
        [string]$ConfigFile,
        [ValidateSet("azure")]
        [string]$CloudProvider,
        [string]$SubscriptionId,
        [string]$ResourceGroup,
        [switch]$InteractiveAI,
        [ValidateSet("en-US", "ru-RU")]
        [string]$Language,
        [switch]$RunSecurityTests
    )

    try {
        Write-Log "Starting ArchCompass execution" -Level "INFO"

        # --- 1. Загрузка конфигурации ---
        $configManager = [ConfigurationManager]::GetInstance()

        if ($ConfigFile -and (Test-Path $ConfigFile)) {
            Write-Log "Loading configuration from file: $ConfigFile" -Level "INFO"
            $configManager.LoadConfiguration($ConfigFile)
        } else {
            Write-Log "Loading default configuration" -Level "INFO"
            $configManager.LoadConfiguration()
        }

        # --- 2. Применение параметров командной строки ---
        $overridesApplied = @()

        if ($PSBoundParameters.ContainsKey('RepoName')) {
            $configManager.SetValue("Repository.DefaultName", $RepoName)
            $overridesApplied += "Repository.DefaultName=$RepoName"
        }

        if ($PSBoundParameters.ContainsKey('Language')) {
            $configManager.SetValue("App.Language", $Language)
            $overridesApplied += "App.Language=$Language"
        }

        if ($PSBoundParameters.ContainsKey('CloudProvider')) {
            $configManager.SetValue("Cloud.Provider", $CloudProvider)
            $overridesApplied += "Cloud.Provider=$CloudProvider"
        }

        if ($PSBoundParameters.ContainsKey('SubscriptionId')) {
            $configManager.SetValue("Cloud.Azure.SubscriptionId", $SubscriptionId)
            $overridesApplied += "Cloud.Azure.SubscriptionId=***MASKED***"
        }

        if ($PSBoundParameters.ContainsKey('ResourceGroup')) {
            $configManager.SetValue("Cloud.Azure.ResourceGroup", $ResourceGroup)
            $overridesApplied += "Cloud.Azure.ResourceGroup=$ResourceGroup"
        }

        if ($InteractiveAI) {
            $configManager.SetValue("AI.Enabled", $true)
            $overridesApplied += "AI.Enabled=True"
        }

        Write-Log "Configuration overrides applied: $($overridesApplied -join ', ')" -Level "INFO"

        # --- 3. Инициализация SecretManager ---
        if (-not [SecretManager]::IsInitialized) {
            $securityConfig = $configManager.GetValue("Security", @{})
            $vaultType = $securityConfig.Vault.Type ?? "Environment"
            $cacheTtl = $securityConfig.Cache.TTLSeconds ?? 300

            Write-Log "Initializing SecretManager with Vault=$vaultType, CacheTTL=$cacheTtl" -Level "INFO"
            [SecretManager]::Initialize(@{
                VaultType = $vaultType
                CacheTTL    = $cacheTtl
            })
        }

        # --- 4. Получение секретов ---
        Write-Log "Fetching secrets via SecretManager..." -Level "INFO"
        $secrets = @{
            OpenAIKey          = [SecretManager]::GetSecret("OPENAI_API_KEY", $configManager.GetValue("AI.OpenAI.ApiKey"))
            PrometheusUrl      = [SecretManager]::GetSecret("PROMETHEUS_PUSHGATEWAY_URL", $configManager.GetValue("Monitoring.Prometheus.PushgatewayUrl"))
            AzureSubscriptionId = $SubscriptionId ? $SubscriptionId : [SecretManager]::GetSecret("AZURE_SUBSCRIPTION_ID", $configManager.GetValue("Cloud.Azure.SubscriptionId"))
        }

        # Обновим конфиг
        foreach ($kv in $secrets.GetEnumerator()) {
            if ($kv.Value) {
                $configManager.SetValue("Runtime.Secrets.$($kv.Key)", $kv.Value)
            }
        }

        # --- 5. Финальная конфигурация ---
        $finalConfig = $configManager.Configuration

        # --- 6. Локализация ---
        $effectiveLanguage = $finalConfig.App.Language
        Set-Localization -LanguageCode $effectiveLanguage

        # --- 7. Путь ---
        $effectiveRepoName = $finalConfig.Repository.DefaultName
        $script:BASE_PATH = Join-Path $PWD.Path $effectiveRepoName

        Write-Host "`n$(Get-LocalizedString -Key 'Title')`n" -ForegroundColor Green
        Write-Log (Get-LocalizedString -Key "Creating" -f $script:BASE_PATH) -Level "INFO"

        # --- 8. Проверка зависимостей ---
        $baseDeps = @("git")
        $conditionalDeps = @{}

        if ($Command -eq "deploy" -and $finalConfig.Cloud.Provider -eq "azure") {
            $conditionalDeps["Azure CLI"] = { Get-Command az -ErrorAction SilentlyContinue -ne $null }
        }

        if ($finalConfig.AI.Enabled -and $secrets.OpenAIKey) {
            $conditionalDeps["OpenAI API Key"] = { [SecretManager]::GetSecret("OPENAI_API_KEY", $secrets.OpenAIKey) -ne $null }
        }

        Write-Log "Checking dependencies..." -Level "INFO"
        if (-not (Test-Dependencies -Commands $baseDeps -ConditionalChecks $conditionalDeps)) {
            Write-Log "Dependency check failed." -Level "ERROR"
            exit 1
        }

        # --- 9. Security Scan ---
        if ($RunSecurityTests) {
            Write-Log "Running security scan on target path: $script:BASE_PATH" -Level "INFO"
            try {
                $scanResult = Invoke-SecurityScan -TargetPath $script:BASE_PATH -ScanForSecrets:$true -RunExternalTools:$true
                if ($scanResult.Findings.Count -gt 0) {
                    Write-Log "Security scan found $($scanResult.Findings.Count) issues." -Level "WARN"
                } else {
                    Write-Log "Security scan passed." -Level "INFO"
                }
            } catch {
                Write-Log "Security scan failed: $($_.Exception.Message)" -Level "ERROR"
            }
        }

        # --- 10. Основная логика команды ---
        # Здесь вызов команды: init, deploy и т.д.
        # Можно использовать CommandFactory
        Write-Log "Executing command: $Command" -Level "INFO"

        # Заглушка
        switch ($Command) {
            "init" { Write-Log "Init logic not implemented yet." -Level "WARN" }
            "deploy" { Write-Log "Deploy logic not implemented yet." -Level "WARN" }
            default { Write-Log "Command '$Command' not implemented." -Level "WARN" }
        }

    }
    catch {
        Write-Log "Unhandled error in Main: $($_.Exception.Message)" -Level "ERROR"
        throw
    }
}

Export-ModuleMember -Function Main, Write-Log, Get-LocalizedString, Test-Dependencies

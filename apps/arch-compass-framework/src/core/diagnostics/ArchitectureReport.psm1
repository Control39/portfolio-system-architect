function Export-ArchitectureDiagram {
    param(
        [ValidateSet('Mermaid', 'PlantUML', 'Markdown')]
        [string]$Format = 'Mermaid',
        [string]$OutputPath = './docs/architecture-diagram'
    )
    
    # Анализ структуры модулей
    $modules = Get-ChildItem 'src/' -Recurse -Filter '*.psm1' | ForEach-Object {
        $name = $_.BaseName
        $deps = Select-String -Path $_.FullName -Pattern 'Import-Module.*\.psm1' | 
        ForEach-Object { $_.Line -replace '.*Import-Module\s+["'']?([^"''\s]+\.psm1).*', '$1' }
        [PSCustomObject]@{ Name = $name; Dependencies = $deps }
    }
    
    # Генерация Mermaid-диаграммы
    if ($Format -eq 'Mermaid') {
        $diagram = @'
graph TD
    A[ArchCompass.psm1] --> B[ConfigurationManager]
    A --> C[SecretManager]
    A --> D[SecurityScanner]
    A --> E[StructuredLogger]
    A --> F[InputValidator]
    A --> G[CommandFactory]
    G --> H[OpenAIIntegration]
    C --> I[Secrets Backend]
    D --> J[Gitleaks/Trivy]
    E --> K[Prometheus/JSON Logs]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#bbf,stroke:#333
    style J fill:#bbf,stroke:#333
    style K fill:#bbf,stroke:#333
'@
        $diagram | Out-File -FilePath "$OutputPath.mmd" -Encoding utf8
    }
    
    # Генерация Markdown-отчёта
    $report = @"
# Arch-Compass Architecture Report
Generated: $(Get-Date -Format 'o')

## Module Dependency Graph
\`\`\`mermaid
$(Get-Content "$OutputPath.mmd")
\`\`\`

## Contract Compliance
$(Test-ModuleContract -ModulePath './ArchCompass.psm1' -ContractPath './src/core/contracts/IModule.psd1' | Format-List | Out-String)

## Health Status
$(Test-ArchCompassHealth -Detailed | Format-Table | Out-String)

## AI Provider Configuration
Available: OpenAI, YandexGPT, LocalLLM
Active: $(Get-AiProvider -Name 'OpenAI' -Config @{} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
"@
    
    $report | Out-File -FilePath "$OutputPath.md" -Encoding utf8
    Write-Host "✅ Architecture report generated: $OutputPath.{mmd,md}"
}
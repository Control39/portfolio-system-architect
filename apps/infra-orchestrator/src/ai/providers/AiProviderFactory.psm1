function Get-AiProvider {
    param(
        [Parameter(Mandatory)]
        [ValidateSet('OpenAI', 'YandexGPT', 'LocalLLM')]
        [string]$Name,
        [hashtable]$Config
    )
    
    $providerMap = @{
        'OpenAI'    = 'src/ai/providers/OpenAiProvider.psm1'
        'YandexGPT' = 'src/ai/providers/YandexGptProvider.psm1'
        'LocalLLM'  = 'src/ai/providers/LocalLlmProvider.psm1'
    }
    
    $modulePath = Join-Path $PSScriptRoot $providerMap[$Name]
    
    if (-not (Test-Path $modulePath)) {
        throw "Provider module not found: $modulePath"
    }
    
    Import-Module $modulePath -Force
    Initialize-Provider @Config
    
    return Get-Module -Name (Split-Path $modulePath -LeafBase)
}
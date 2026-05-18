# YandexGPT Provider Implementation
# Implements IAiProvider contract
# Priority provider for Russian market (Yandex Cloud)

$script:config = @{
    ApiKey = $null
    FolderId = $null
    Model = "yandexgpt-lite"
    Endpoint = "https://llm.api.cloud.yandex.net/foundationModels/v1"
    Timeout = 30
}

function Initialize-Provider {
    param(
        [Parameter(Mandatory)]
        [string]$ApiKey,

        [Parameter(Mandatory)]
        [string]$FolderId,

        [string]$Model = "yandexgpt-lite",

        [int]$Timeout = 30
    )

    $script:config.ApiKey = $ApiKey
    $script:config.FolderId = $FolderId
    $script:config.Model = $Model
    $script:config.Timeout = $Timeout

    Write-Verbose "YandexGPT Provider initialized. FolderId: $FolderId"
}

function Invoke-Completion {
    param(
        [Parameter(Mandatory)]
        [string]$Prompt,

        [int]$MaxTokens = 2048,

        [double]$Temperature = 0.7
    )

    if (-not $script:config.ApiKey) {
        throw "YandexGPT API key not set. Call Initialize-Provider first."
    }

    $body = @{
        modelUri = "gpt://$($script:config.FolderId)/$($script:config.Model)"
        completionOptions = @{
            stream = $false
            maxTokens = $MaxTokens
            temperature = $Temperature
        }
        messages = @(
            @{
                role = "user"
                text = $Prompt
            }
        )
    } | ConvertTo-Json -Depth 10

    $headers = @{
        "Authorization" = "Api-Key $($script:config.ApiKey)"
        "Content-Type" = "application/json"
        "x-folder-id" = $script:config.FolderId
    }

    try {
        $response = Invoke-RestMethod -Uri "$($script:config.Endpoint)/completion" `
            -Method Post `
            -Headers $headers `
            -Body $body `
            -TimeoutSec $script:config.Timeout

        if ($response.result -and $response.result.choices) {
            return $response.result.choices[0].message.text
        }

        throw "Unexpected response format from YandexGPT"
    }
    catch {
        throw "YandexGPT API call failed: $_"
    }
}

function Invoke-Embedding {
    param(
        [Parameter(Mandatory)]
        [string]$Text,

        [string]$Model = "embeddings-v1"
    )

    # YandexGPT пока не поддерживает embeddings через основной API
    # Возвращаем заглушку с предупреждением
    Write-Warning "YandexGPT Embedding API is not available. Use LocalLLM provider for vector operations."
    return $null
}

function Get-ProviderInfo {
    return [PSCustomObject]@{
        Name = "YandexGPT"
        Model = $script:config.Model
        FolderId = $script:config.FolderId
        Endpoint = $script:config.Endpoint
        SupportsEmbeddings = $false
        SupportsCompletion = $true
        Region = "Russia (Yandex Cloud)"
        Compliance = "152-FZ compliant"
        RateLimit = "60 requests/minute"
    }
}

function Test-Connection {
    param([int]$TimeoutSec = 5)

    if (-not $script:config.ApiKey) {
        return $false
    }

    try {
        $testBody = @{
            modelUri = "gpt://$($script:config.FolderId)/$($script:config.Model)"
            completionOptions = @{
                stream = $false
                maxTokens = 1
            }
            messages = @(
                @{
                    role = "user"
                    text = "test"
                }
            )
        } | ConvertTo-Json -Depth 5

        $headers = @{
            "Authorization" = "Api-Key $($script:config.ApiKey)"
            "Content-Type" = "application/json"
            "x-folder-id" = $script:config.FolderId
        }

        $response = Invoke-RestMethod -Uri "$($script:config.Endpoint)/completion" `
            -Method Post `
            -Headers $headers `
            -Body $testBody `
            -TimeoutSec $TimeoutSec

        return $true
    }
    catch {
        Write-Verbose "YandexGPT connection test failed: $_"
        return $false
    }
}

Export-ModuleMember -Function Initialize-Provider, Invoke-Completion, Invoke-Embedding, Get-ProviderInfo, Test-Connection

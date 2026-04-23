# OpenAI Provider Implementation
# Implements IAiProvider contract

$script:config = @{
    ApiKey = $null
    Endpoint = "https://api.openai.com/v1"
    Model = "gpt-4o"
    Timeout = 60
}

function Initialize-Provider {
    param(
        [Parameter(Mandatory)]
        [string]$ApiKey,
        
        [string]$Endpoint = "https://api.openai.com/v1",
        
        [string]$Model = "gpt-4o"
    )
    
    $script:config.ApiKey = $ApiKey
    $script:config.Endpoint = $Endpoint
    $script:config.Model = $Model
    
    Write-Verbose "OpenAI Provider initialized with model: $Model"
}

function Invoke-Completion {
    param(
        [Parameter(Mandatory)]
        [string]$Prompt,
        
        [int]$MaxTokens = 2048,
        
        [double]$Temperature = 0.7
    )
    
    if (-not $script:config.ApiKey) {
        throw "OpenAI API key not set. Call Initialize-Provider first."
    }
    
    $body = @{
        model = $script:config.Model
        messages = @(
            @{ role = "user"; content = $Prompt }
        )
        max_tokens = $MaxTokens
        temperature = $Temperature
    } | ConvertTo-Json -Depth 10
    
    $headers = @{
        "Authorization" = "Bearer $($script:config.ApiKey)"
        "Content-Type" = "application/json"
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$($script:config.Endpoint)/chat/completions" `
            -Method Post `
            -Headers $headers `
            -Body $body `
            -TimeoutSec $script:config.Timeout
        
        return $response.choices[0].message.content
    }
    catch {
        throw "OpenAI API call failed: $_"
    }
}

function Invoke-Embedding {
    param(
        [Parameter(Mandatory)]
        [string]$Text,
        
        [string]$Model = "text-embedding-3-small"
    )
    
    if (-not $script:config.ApiKey) {
        throw "OpenAI API key not set. Call Initialize-Provider first."
    }
    
    $body = @{
        model = $Model
        input = $Text
    } | ConvertTo-Json
    
    $headers = @{
        "Authorization" = "Bearer $($script:config.ApiKey)"
        "Content-Type" = "application/json"
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$($script:config.Endpoint)/embeddings" `
            -Method Post `
            -Headers $headers `
            -Body $body `
            -TimeoutSec $script:config.Timeout
        
        return $response.data[0].embedding
    }
    catch {
        throw "OpenAI Embedding API call failed: $_"
    }
}

function Get-ProviderInfo {
    return [PSCustomObject]@{
        Name = "OpenAI"
        Model = $script:config.Model
        Endpoint = $script:config.Endpoint
        SupportsEmbeddings = $true
        SupportsCompletion = $true
        RateLimit = "30000 requests/minute (enterprise)"
    }
}

function Test-Connection {
    param([int]$TimeoutSec = 5)
    
    if (-not $script:config.ApiKey) {
        return $false
    }
    
    try {
        $testBody = @{
            model = $script:config.Model
            messages = @(@{ role = "user"; content = "test" })
            max_tokens = 1
        } | ConvertTo-Json -Depth 5
        
        $headers = @{
            "Authorization" = "Bearer $($script:config.ApiKey)"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "$($script:config.Endpoint)/chat/completions" `
            -Method Post `
            -Headers $headers `
            -Body $testBody `
            -TimeoutSec $TimeoutSec
        
        return $true
    }
    catch {
        Write-Verbose "Connection test failed: $_"
        return $false
    }
}

Export-ModuleMember -Function Initialize-Provider, Invoke-Completion, Invoke-Embedding, Get-ProviderInfo, Test-Connection
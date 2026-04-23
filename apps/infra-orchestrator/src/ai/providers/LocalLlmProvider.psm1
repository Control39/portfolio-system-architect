# LocalLLM Provider Implementation
# Для оффлайн-режима и локальных LLM (Ollama, vLLM, LM Studio)
# Implements IAiProvider contract

$script:config = @{
    Endpoint = "http://localhost:11434"
    Model = "llama3"
    Timeout = 120
}

function Initialize-Provider {
    param(
        [string]$Endpoint = "http://localhost:11434",
        
        [string]$Model = "llama3",
        
        [int]$Timeout = 120
    )
    
    $script:config.Endpoint = $Endpoint
    $script:config.Model = $Model
    $script:config.Timeout = $Timeout
    
    Write-Verbose "LocalLLM Provider initialized: $Endpoint/$Model"
}

function Invoke-Completion {
    param(
        [Parameter(Mandatory)]
        [string]$Prompt,
        
        [int]$MaxTokens = 2048,
        
        [double]$Temperature = 0.7
    )
    
    $body = @{
        model = $script:config.Model
        prompt = $Prompt
        stream = $false
        options = @{
            num_predict = $MaxTokens
            temperature = $Temperature
        }
    } | ConvertTo-Json -Depth 5
    
    try {
        $response = Invoke-RestMethod -Uri "$($script:config.Endpoint)/api/generate" `
            -Method Post `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec $script:config.Timeout
        
        return $response.response
    }
    catch {
        throw "LocalLLM API call failed: $_"
    }
}

function Invoke-Embedding {
    param(
        [Parameter(Mandatory)]
        [string]$Text
    )
    
    $body = @{
        model = $script:config.Model
        prompt = $Text
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$($script:config.Endpoint)/api/embeddings" `
            -Method Post `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec $script:config.Timeout
        
        return $response.embedding
    }
    catch {
        throw "LocalLLM Embedding API call failed: $_"
    }
}

function Get-ProviderInfo {
    return [PSCustomObject]@{
        Name = "LocalLLM"
        Model = $script:config.Model
        Endpoint = $script:config.Endpoint
        SupportsEmbeddings = $true
        SupportsCompletion = $true
        Offline = $true
        Privacy = "All data stays local"
    }
}

function Test-Connection {
    param([int]$TimeoutSec = 5)
    
    try {
        $response = Invoke-RestMethod -Uri "$($script:config.Endpoint)/api/tags" `
            -Method Get `
            -TimeoutSec $TimeoutSec
        
        return $null -ne $response.models
    }
    catch {
        Write-Verbose "LocalLLM connection test failed: $_"
        return $false
    }
}

Export-ModuleMember -Function Initialize-Provider, Invoke-Completion, Invoke-Embedding, Get-ProviderInfo, Test-Connection

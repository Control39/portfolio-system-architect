# src/ai/OpenAIIntegration.psm1

function Invoke-AICompletion {
    param([string]$Prompt)
    $key = [SecretManager]::GetSecret("OPENAI_API_KEY")
    $url = "https://api.openai.com/v1/chat/completions"
    $headers = @{ "Authorization" = "Bearer $key" }
    $body = @{
        model = "gpt-4"
        messages = @( @{ role = "user"; content = $Prompt } )
    } | ConvertTo-Json

    try {
        $res = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -ContentType "application/json"
        return $res.choices[0].message.content
    } catch {
        Write-Log "AI request failed: $_" -Level "WARN"
        return $null
    }
}

Export-ModuleMember -Function Invoke-AICompletion

# src/queues/RabbitMQClient.psm1

function Connect-RabbitMQ {
    param([string]$Host = "localhost")
    $user = [SecretManager]::GetSecret("RABBITMQ_USERNAME", "guest")
    $pass = [SecretManager]::GetSecret("RABBITMQ_PASSWORD", "guest")
    Write-Log "Connecting to RabbitMQ at $Host as $user" -Level "INFO"
    # Здесь будет реальное подключение (требует установки клиента)
}

Export-ModuleMember -Function Connect-RabbitMQ

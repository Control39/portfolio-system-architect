# src/infrastructure/monitoring/Metrics.psm1

function Send-Metric {
    param(
        [string]$Job,
        [double]$DurationSec,
        [string]$Status = "success"
    )
    $metric = "arch_compass_job_duration_seconds{job=`"$Job`",status=`"$Status`"} $DurationSec"
    $url = [SecretManager]::GetSecret("PROMETHEUS_PUSHGATEWAY_URL", "http://localhost:9091")
    try {
        Invoke-RestMethod -Uri "$url/metrics/job/arch-compass" -Method POST -Body $metric -ContentType 'text/plain'
        Write-Log "Metric sent to Prometheus" -Level "DEBUG"
    } catch {
        Write-Log "Failed to send metric: $_" -Level "WARN"
    }
}

Export-ModuleMember -Function Send-Metric

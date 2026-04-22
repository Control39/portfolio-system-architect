function Export-PrometheusMetrics {
    param([string]$OutputPath = '/tmp/archcompass_metrics.prom')
    
    $metrics = @(
        '# HELP archcompass_module_load_time Module load duration in seconds',
        '# TYPE archcompass_module_load_time gauge',
        "archcompass_module_load_time{module='ArchCompass'} $(Measure-Command { Import-Module './ArchCompass.psm1' -Force }).TotalSeconds",
        
        '# HELP archcompass_commands_executed Total commands executed',
        '# TYPE archcompass_commands_executed counter',
        "archcompass_commands_executed{command='Start-ArchCompass'} 0",
        
        '# HELP archcompass_health_check Health status (1=healthy, 0=unhealthy)',
        '# TYPE archcompass_health_check gauge',
        "archcompass_health_check $((Test-ArchCompassHealth).Healthy.ToInt32())"
    )
    
    $metrics | Out-File -FilePath $OutputPath -Encoding utf8
    Write-Verbose "Metrics exported to $OutputPath"
}
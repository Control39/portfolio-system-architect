function Show-GroupedChanges {
    param(
        [string]$Path = "."
    )
    
    # Получаем все изменения
    $changes = git status --short | ForEach-Object {
        [PSCustomObject]@{
            Status = $_.Substring(0, 2).Trim()
            File = $_.Substring(3)
        }
    }
    
    # Группируем по типу/сервису
    $grouped = @{
        "apps/cloud-reason" = @()
        "apps/it-compass" = @()
        "apps/arch-compass-framework" = @()
        "apps/ml-model-registry" = @()
        "apps/auth-service" = @()
        "apps/career-development" = @()
        "apps/portfolio-organizer" = @()
        "apps/system-proof" = @()
        "docs" = @()
        "tools" = @()
        "scripts" = @()
        "deployment" = @()
        ".github" = @()
        "other" = @()
    }
    
    foreach ($change in $changes) {
        $file = $change.File
        
        $matched = $false
        foreach ($app in $grouped.Keys) {
            if ($file -like "$app/*") {
                $grouped[$app] += $change
                $matched = $true
                break
            }
        }
        
        if (-not $matched) {
            $grouped["other"] += $change
        }
    }
    
    # Выводим сгруппированно
    foreach ($group in $grouped.Keys | Sort-Object) {
        $files = $grouped[$group]
        if ($files.Count -gt 0) {
            Write-Host "`n📦 $group ($($files.Count) файлов)" -ForegroundColor Cyan
            foreach ($file in $files) {
                $statusColor = if ($file.Status -eq 'M') { "Yellow" } 
                              elseif ($file.Status -eq 'A') { "Green" }
                              else { "Gray" }
                Write-Host "  $($file.Status) $($file.File)" -ForegroundColor $statusColor
            }
        }
    }
}

function Show-ServiceHealth {
    Write-Host "📊 Состояние микросервисов" -ForegroundColor Magenta
    
    $services = Get-ChildItem apps -Directory
    foreach ($service in $services) {
        $changes = git status "apps/$($service.Name)" --short
        $changeCount = ($changes | Measure-Object).Count
        
        $status = if ($changeCount -eq 0) { "✅ Clean" } 
                  else { "⚡ $changeCount changes" }
        
        Write-Host "  $($service.Name) - $status" -ForegroundColor $(if ($changeCount -eq 0) { "Green" } else { "Yellow" })
    }
}

function SafeCommit {
    git status
    $service = Read-Host "Сервис для коммита (cloud-reason/it-compass/all)"
    $validServices = @('cloud-reason', 'it-compass', 'all')
    if ($validServices -notcontains $service) {
        Write-Error "Недопустимый сервис: $service"
        return
    }
    if ($service -eq 'all') { 
        git add apps/
    } else { 
        git add "apps/$service/"
    }
    $secrets = git diff --cached | Select-String 'secret|password|key|token'
    if ($secrets) {
        Write-Error "Найдены потенциальные секреты. Коммит отменен."
        return
    }
    git commit 
}

# Запуск анализа
Show-GroupedChanges
Show-ServiceHealth


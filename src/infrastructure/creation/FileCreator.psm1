# src/infrastructure/creation/FileCreator.psm1

function New-ProjectStructure {
    param([string]$BasePath)
    $dirs = @(
        "$BasePath/src"
        "$BasePath/tests"
        "$BasePath/docs"
        "$BasePath/scripts"
        "$BasePath/config"
    )
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "Created directory: $dir" -Level "INFO"
        }
    }
    # Пример файла
    $gitignore = "$BasePath/.gitignore"
    if (-not (Test-Path $gitignore)) {
        "@(__pycache__)", "/logs/", ".env" | Out-File $gitignore -Encoding UTF8
        Write-Log "Created .gitignore" -Level "INFO"
    }
}

Export-ModuleMember -Function New-ProjectStructure

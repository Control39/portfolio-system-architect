# compare_itcompass_versions.ps1
# Compare all IT-Compass versions in the system

$paths = @(
    @{ Name = "Backup"; Path = "C:\Users\Z\Desktop\portfolio-system-architect_backup\components\it-compass" },
    @{ Name = "Current"; Path = "C:\Users\Z\Desktop\portfolio-system-architect\components\it-compass" },
    @{ Name = "C_Root"; Path = "C:\it-compass" },
    @{ Name = "my-ecosystem-FINAL"; Path = "C:\Users\Z\my-ecosystem-FINAL\it-compass" },
    @{ Name = "tmp"; Path = "C:\tmp\it-compass" },
    @{ Name = "DevEnv_main"; Path = "C:\Users\Z\DeveloperEnvironment\main\it-compass" },
    @{ Name = "DevEnv_typo"; Path = "C:\Users\Z\DeveloperEnvironment\main\it-compasss" }
)

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "=== IT-COMPASS VERSIONS COMPARISON ===" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan

$results = @()

foreach ($item in $paths) {
    $exists = Test-Path $item.Path
    
    if ($exists) {
        $fileCount = (Get-ChildItem $item.Path -Recurse -File -ErrorAction SilentlyContinue).Count
        $folderCount = (Get-ChildItem $item.Path -Directory -ErrorAction SilentlyContinue).Count
        $lastModified = (Get-ChildItem $item.Path -Recurse -ErrorAction SilentlyContinue | 
            Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
        $sizeKB = [math]::Round(((Get-ChildItem $item.Path -Recurse -File -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum) / 1KB, 2)
    } else {
        $fileCount = 0
        $folderCount = 0
        $lastModified = "N/A"
        $sizeKB = 0
    }
    
    $results += [PSCustomObject]@{
        "Version" = $item.Name
        "Exists" = $exists
        "Files" = $fileCount
        "Folders" = $folderCount
        "SizeKB" = $sizeKB
        "LastModified" = $lastModified
        "Path" = $item.Path
    }
}

Write-Host "`n SUMMARY TABLE:" -ForegroundColor Green
$results | Format-Table -AutoSize -Property "Version", "Exists", "Files", "Folders", "SizeKB", "LastModified"

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "=== DETAILS BY EXISTING VERSIONS ===" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan

foreach ($result in $results | Where-Object { $_."Exists" -eq $true }) {
    Write-Host "`n Version: $($result.Version)" -ForegroundColor Yellow
    Write-Host "   Path: $($result.Path)" -ForegroundColor Gray
    Write-Host "   Files: $($result.Files)" -ForegroundColor White
    Write-Host "   Folders: $($result.Folders)" -ForegroundColor White
    Write-Host "   Size: $($result.SizeKB) KB" -ForegroundColor White
    Write-Host "   Last Modified: $($result.LastModified)" -ForegroundColor White
    
    Write-Host "   Structure:" -ForegroundColor Cyan
    Get-ChildItem $result.Path -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $count = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
        Write-Host "      +-- $($_.Name) ($count files)" -ForegroundColor Gray
    }
}

$existingVersions = $results | Where-Object { $_."Exists" -eq $true }

if ($existingVersions.Count -ge 2) {
    Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
    Write-Host "=== CONTENT COMPARISON ===" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    
    $v1 = $existingVersions | Select-Object -First 1
    $v2 = $existingVersions | Select-Object -Index 1
    
    Write-Host "`n Comparing: $($v1.Version) vs $($v2.Version)" -ForegroundColor Magenta
    
    $files1 = Get-ChildItem $v1.Path -Recurse -File -ErrorAction SilentlyContinue | 
        ForEach-Object { $_.FullName.Replace($v1.Path, '').TrimStart('\') } | Sort-Object
    $files2 = Get-ChildItem $v2.Path -Recurse -File -ErrorAction SilentlyContinue | 
        ForEach-Object { $_.FullName.Replace($v2.Path, '').TrimStart('\') } | Sort-Object
    
    $onlyInV1 = Compare-Object -ReferenceObject $files2 -DifferenceObject $files1 | 
        Where-Object { $_.SideIndicator -eq '<=' } | Select-Object -ExpandProperty InputObject
    $onlyInV2 = Compare-Object -ReferenceObject $files1 -DifferenceObject $files2 | 
        Where-Object { $_.SideIndicator -eq '=>' } | Select-Object -ExpandProperty InputObject
    $same = Compare-Object -ReferenceObject $files1 -DifferenceObject $files2 | 
        Where-Object { $_.SideIndicator -eq '==' } | Select-Object -ExpandProperty InputObject
    
    Write-Host "`n   Same files: $($same.Count)" -ForegroundColor Green
    Write-Host "   Only in $($v1.Version): $($onlyInV1.Count)" -ForegroundColor Yellow
    Write-Host "   Only in $($v2.Version): $($onlyInV2.Count)" -ForegroundColor Yellow
    
    if ($onlyInV1.Count -gt 0 -and $onlyInV1.Count -le 10) {
        Write-Host "`n   Files only in $($v1.Version):" -ForegroundColor Yellow
        $onlyInV1 | ForEach-Object { Write-Host "      - $_" -ForegroundColor Gray }
    }
    
    if ($onlyInV2.Count -gt 0 -and $onlyInV2.Count -le 10) {
        Write-Host "`n   Files only in $($v2.Version):" -ForegroundColor Yellow
        $onlyInV2 | ForEach-Object { Write-Host "      - $_" -ForegroundColor Gray }
    }
}

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "=== RECOMMENDATIONS ===" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan

$maxFiles = ($existingVersions | Measure-Object -Property "Files" -Maximum).Maximum
$richestVersion = $existingVersions | Where-Object { $_."Files" -eq $maxFiles } | Select-Object -First 1

if ($richestVersion) {
    Write-Host "`n Most complete version: $($richestVersion.Version) ($($richestVersion.Files) files)" -ForegroundColor Green
    Write-Host "   Path: $($richestVersion.Path)" -ForegroundColor Gray
}

Write-Host "`n What to do:" -ForegroundColor Cyan
Write-Host "   1. Choose the most complete version as main" -ForegroundColor White
Write-Host "   2. Delete or archive other versions" -ForegroundColor White
Write-Host "   3. Make sure only one version is in Git" -ForegroundColor White

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Cyan
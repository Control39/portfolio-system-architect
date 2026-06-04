# Path to root
$root = "C:\Users\Z\my-ecosystem-CLONE"

# Find all README.md in folders with 'it-compass' in name
$readmeFiles = Get-ChildItem -Path $root -Recurse -File -Force |
    Where-Object {
        $_.Name -eq "README.md" -and
        ($_.Directory.Name -like "*it-compass*" -or $_.Directory.Name -like "*IT-Compass*" -or $_.Directory.Name -like "*It-Compass*")
    } |
    Sort-Object FullName

# Output results
Write-Host "`n🔍 Found README.md in 'it-compass' folders:`n" -ForegroundColor Cyan

if ($readmeFiles.Count -eq 0) {
    Write-Host "❌ No README.md files found." -ForegroundColor Yellow
    exit
}

$readmeFiles | ForEach-Object {
    $relPath = $_.FullName.Substring($root.Length).TrimStart('\')
    Write-Host "📄 File: $relPath`n" -ForegroundColor Green
    Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray

    try {
        $content = [IO.File]::ReadAllText($_.FullName)
        Write-Host $content
    }
    catch {
        Write-Host "⚠️ Error reading file: $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "------------------------------------------------------------"
}

# migrate-skills-safe.ps1
# Безопасная миграция скиллов с проверкой содержимого

$ErrorActionPreference = "Continue"

function Get-FileHash-Safe($path) {
    if (Test-Path $path -PathType Leaf) {
        return (Get-FileHash $path -Algorithm SHA256).Hash
    }
    return $null
}

function Migrate-Skill($skillName, $sourcePath, $destPath, $sourceLabel) {
    $destSkillPath = Join-Path $destPath $skillName

    if (-not (Test-Path $destSkillPath)) {
        # Скилла нет — копируем целиком
        Copy-Item -Path $sourcePath -Destination $destSkillPath -Recurse -Force
        Write-Host "✅ $skillName — скопирован из $sourceLabel" -ForegroundColor Green
        return "COPIED"
    }

    # Скилл уже есть — проверяем содержимое
    $sourceFiles = Get-ChildItem -Path $sourcePath -Recurse -File
    $destFiles = Get-ChildItem -Path $destSkillPath -Recurse -File

    $allIdentical = $true
    foreach ($srcFile in $sourceFiles) {
        $relPath = $srcFile.FullName.Substring($sourcePath.Length)
        $destFile = Join-Path $destSkillPath $relPath

        if (-not (Test-Path $destFile)) {
            $allIdentical = $false
            break
        }

        $srcHash = Get-FileHash-Safe $srcFile.FullName
        $dstHash = Get-FileHash-Safe $destFile

        if ($srcHash -ne $dstHash) {
            $allIdentical = $false
            break
        }
    }

    if ($allIdentical) {
        Write-Host "⚪ $skillName — идентичен, пропуск" -ForegroundColor Gray
        return "IDENTICAL"
    }

    # Файлы отличаются — создаём версию с суффиксом
    $conflictPath = Join-Path $destPath "${skillName}_from_${sourceLabel}"
    Copy-Item -Path $sourcePath -Destination $conflictPath -Recurse -Force
    Write-Host "⚠️  $skillName — отличается, сохранён как ${skillName}_from_${sourceLabel}" -ForegroundColor Yellow
    return "CONFLICT"
}

Write-Host "🚀 Начало миграции скиллов" -ForegroundColor Cyan

$destSkills = "apps/cognitive_agent/skills"
$results = @()

# 1. Миграция из .agents/skills/
Write-Host "`n📂 Миграция из .agents/skills/" -ForegroundColor Yellow
if (Test-Path ".agents/skills") {
    Get-ChildItem ".agents/skills" -Directory | ForEach-Object {
        $result = Migrate-Skill $_.Name $_.FullName $destSkills "agents"
        $results += [PSCustomObject]@{Source=".agents"; Skill=$_.Name; Result=$result}
    }
}

# 2. Миграция из codeassistant/skills/
Write-Host "`n📂 Миграция из codeassistant/skills/" -ForegroundColor Yellow
if (Test-Path "codeassistant/skills") {
    Get-ChildItem "codeassistant/skills" -Directory | ForEach-Object {
        $result = Migrate-Skill $_.Name $_.FullName $destSkills "codeassistant"
        $results += [PSCustomObject]@{Source="codeassistant"; Skill=$_.Name; Result=$result}
    }
}

# 3. Миграция из .sourcecraft/skills/
Write-Host "`n📂 Миграция из .sourcecraft/skills/" -ForegroundColor Yellow
if (Test-Path ".sourcecraft/skills") {
    Get-ChildItem ".sourcecraft/skills" -Directory | ForEach-Object {
        $result = Migrate-Skill $_.Name $_.FullName $destSkills "sourcecraft"
        $results += [PSCustomObject]@{Source=".sourcecraft"; Skill=$_.Name; Result=$result}
    }
}

# Итоговый отчёт
Write-Host "`n📊 Итоговый отчёт" -ForegroundColor Cyan
$results | Group-Object Result | Select-Object Name, Count | Format-Table -AutoSize

$conflicts = $results | Where-Object { $_.Result -eq "CONFLICT" }
if ($conflicts) {
    Write-Host "`n⚠️  Конфликты (требуют ручного ревью):" -ForegroundColor Yellow
    $conflicts | ForEach-Object { Write-Host "  - $($_.Source)/skills/$($_.Skill)" -ForegroundColor Yellow }
}

Write-Host "`n✅ Миграция скиллов завершена" -ForegroundColor Green

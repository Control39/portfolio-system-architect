# Скрипт для пуша standalone репозиториев в GitHub
# username: Control39

$GITHUB_USER = "Control39"

function Push-StandaloneRepo {
    param(
        [string]$RepoName,
        [string]$RemoteName
    )

    Write-Host "=== Обработка $RepoName ===" -ForegroundColor Cyan

    Set-Location $RepoName

    # Проверка наличия remote
    $remotes = git remote -v 2>&1
    if ($remotes -like "*$RemoteName*") {
        Write-Host "Remote уже существует, обновляем..." -ForegroundColor Yellow
        git remote set-url origin "https://github.com/$GITHUB_USER/$RemoteName.git"
    } else {
        Write-Host "Добавляем remote..." -ForegroundColor Green
        git remote add origin "https://github.com/$GITHUB_USER/$RemoteName.git"
    }

    # Переименование ветки в main (если нужно)
    $currentBranch = git branch --show-current
    if ($currentBranch -ne "main") {
        Write-Host "Переименовываем ветку в main..." -ForegroundColor Yellow
        git branch -M main
    }

    # Пуш
    Write-Host "Пушим в GitHub..." -ForegroundColor Green
    git push -u origin main --force

    Set-Location ..
    Write-Host "✓ $RepoName успешно запушен`n" -ForegroundColor Green
}

# Пуш всех standalone репозиториев
Write-Host "=== Запуск пуша standalone репозиториев ===" -ForegroundColor Cyan
Write-Host "GitHub пользователь: $GITHUB_USER`n" -ForegroundColor Cyan

Push-StandaloneRepo -RepoName "cognitive-agent-standalone" -RemoteName "cognitive-agent-standalone"
Push-StandaloneRepo -RepoName "it_compass-standalone" -RemoteName "it_compass-standalone"
Push-StandaloneRepo -RepoName "portfolio_organizer-standalone" -RemoteName "portfolio_organizer-standalone"
Push-StandaloneRepo -RepoName "system_proof-standalone" -RemoteName "system_proof-standalone"

Write-Host "=== Все репозитории успешно запушены! ===" -ForegroundColor Green
Write-Host "`nСсылки на репозитории:" -ForegroundColor Cyan
Write-Host "https://github.com/$GITHUB_USER/cognitive-agent-standalone"
Write-Host "https://github.com/$GITHUB_USER/it_compass-standalone"
Write-Host "https://github.com/$GITHUB_USER/portfolio_organizer-standalone"
Write-Host "https://github.com/$GITHUB_USER/system_proof-standalone"

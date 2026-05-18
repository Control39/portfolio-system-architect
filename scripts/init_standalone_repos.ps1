# Инициализация standalone репозиториев

Write-Host "Инициализация cognitive-agent-standalone..."
Set-Location cognitive-agent-standalone
git add .
git commit -m "Initial commit: Cognitive Automation Agent standalone"
Set-Location ..

Write-Host "Инициализация it_compass-standalone..."
Set-Location it_compass-standalone
git add .
git commit -m "Initial commit: IT-Compass standalone"
Set-Location ..

Write-Host "Инициализация portfolio_organizer-standalone..."
Set-Location portfolio_organizer-standalone
git add .
git commit -m "Initial commit: Portfolio Organizer standalone"
Set-Location ..

Write-Host "Инициализация system_proof-standalone..."
Set-Location system_proof-standalone
git add .
git commit -m "Initial commit: System Proof standalone"
Set-Location ..

Write-Host "Готово!"

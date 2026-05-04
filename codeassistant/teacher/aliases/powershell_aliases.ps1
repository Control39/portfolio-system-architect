# Алиасы PowerShell для когнитивного архитектора
# Добавьте в ваш профиль PowerShell: $PROFILE

# ====================
# СИСТЕМНЫЕ КОМАНДЫ
# ====================

# Очистка системы
function Clear-Temp { Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue }
function Clear-RecycleBin { Clear-RecycleBin -Force }
function Show-DiskUsage { Get-ChildItem -Recurse | Measure-Object -Property Length -Sum | Select-Object @{Name="Size(GB)";Expression={[math]::Round($_.Sum/1GB,2)}} }

# Процессы
function Find-Process($name) { Get-Process | Where-Object { $_.ProcessName -like "*$name*" } }
function Kill-Port($port) { Get-Process -Id (Get-NetTCPConnection -LocalPort $port).OwningProcess | Stop-Process -Force }

# ====================
# GIT АЛИАСЫ
# ====================

function gs { git status }
function ga { git add . }
function gcm($msg) { git commit -m $msg }
function gcam($msg) { git commit -am $msg }
function gp { git push }
function gpl { git pull }
function gco($branch) { git checkout $branch }
function gcb($branch) { git checkout -b $branch }
function gb { git branch }
function gbd($branch) { git branch -d $branch }
function gl { git log --oneline --graph --all -10 }
function gd { git diff }
function gds { git diff --staged }
function grh { git reset --hard HEAD }
function grs { git reset --soft HEAD~1 }
function gst { git stash }
function gstp { git stash pop }
function glg { git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit }

# ====================
# DOCKER АЛИАСЫ
# ====================

function dps { docker ps }
function dpsa { docker ps -a }
function dim { docker images }
function dcup { docker-compose up }
function dcupd { docker-compose up -d }
function dcdown { docker-compose down }
function dcbuild { docker-compose build }
function dclogs($service) { docker-compose logs -f $service }
function dcrestart($service) { docker-compose restart $service }
function dcexec($service) { docker-compose exec $service bash }
function dprune { docker system prune -a -f }

# ====================
# PYTHON АЛИАСЫ
# ====================

function py { python }
function py3 { python3 }
function pipu { pip install --upgrade pip }
function pipi($package) { pip install $package }
function pipr { pip install -r requirements.txt }
function venv($name="venv") { python -m venv $name }
function activate { .\.venv\Scripts\Activate.ps1 }
function deactivate { deactivate }

# ====================
# VS CODE АЛИАСЫ
# ====================

function codec { code . }
function codel($path) { code $path }
function code-ext { code --list-extensions }
function code-install($ext) { code --install-extension $ext }
function code-uninstall($ext) { code --uninstall-extension $ext }

# ====================
# КОГНИТИВНЫЕ СИСТЕМЫ
# ====================

# Ollama
function ollama-list { curl http://localhost:11434/api/tags }
function ollama-pull($model) { ollama pull $model }
function ollama-run($model, $prompt) { ollama run $model $prompt }

# SourceCraft
function sc-status { git status }
function sc-push { git push origin main }
function sc-pull { git pull origin main }
function sc-log { git log --oneline -20 }

# ====================
# ПРОЕКТНЫЕ КОМАНДЫ
# ====================

# Запуск проекта
function run-dev { docker-compose up }
function run-test { python -m pytest }
function run-lint { python -m black . --check }
function run-format { python -m black . }

# Анализ
function analyze-deps { pip list --outdated }
function analyze-size { Get-ChildItem -Recurse | Measure-Object -Property Length -Sum }
function analyze-git { git log --since="1 month ago" --pretty=format:"%h %ad %s" --date=short }

# ====================
# УТИЛИТЫ
# ====================

# Поиск файлов
function find-file($name) { Get-ChildItem -Recurse -Filter "*$name*" -File }
function find-in-files($text) { Get-ChildItem -Recurse -File | Select-String $text }

# Работа с текстом
function count-lines($file) { Get-Content $file | Measure-Object -Line }
function show-head($file, $lines=10) { Get-Content $file -Head $lines }
function show-tail($file, $lines=10) { Get-Content $file -Tail $lines }

# Сеть
function my-ip { (Invoke-WebRequest -Uri "https://api.ipify.org").Content }
function ping-google { Test-Connection google.com }
function check-port($port) { Test-NetConnection -ComputerName localhost -Port $port }

# ====================
# БЫСТРЫЕ ДЕЙСТВИЯ
# ====================

# Создание проекта
function new-python-project($name) {
    New-Item -ItemType Directory -Path $name
    Set-Location $name
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    New-Item -ItemType File -Path "README.md"
    New-Item -ItemType File -Path "requirements.txt"
    New-Item -ItemType File -Path "main.py"
    code .
}

function new-git-repo {
    git init
    git add .
    git commit -m "Initial commit"
    Write-Host "Репозиторий инициализирован" -ForegroundColor Green
}

# Очистка проекта
function clean-project {
    Remove-Item -Path "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "*.pyc" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path ".coverage" -Force -ErrorAction SilentlyContinue
    Write-Host "Проект очищен" -ForegroundColor Green
}

# ====================
# ИНФОРМАЦИОННЫЕ КОМАНДЫ
# ====================

function show-help {
    Write-Host "=== АЛИАСЫ КОГНИТИВНОГО АРХИТЕКТОРА ===" -ForegroundColor Cyan
    Write-Host "Git: gs, ga, gcm, gp, gpl, gco, gb, gl, gd" -ForegroundColor Yellow
    Write-Host "Docker: dps, dcup, dcdown, dclogs, dprune" -ForegroundColor Yellow
    Write-Host "Python: py, pipi, venv, activate" -ForegroundColor Yellow
    Write-Host "VS Code: codec, code-ext, code-install" -ForegroundColor Yellow
    Write-Host "Проект: run-dev, run-test, clean-project" -ForegroundColor Yellow
    Write-Host "Утилиты: find-file, my-ip, check-port" -ForegroundColor Yellow
    Write-Host "======================================" -ForegroundColor Cyan
}

function show-system {
    Write-Host "=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===" -ForegroundColor Cyan
    Write-Host "ОС: $([System.Environment]::OSVersion.VersionString)"
    Write-Host "Пользователь: $env:USERNAME"
    Write-Host "Текущая директория: $(Get-Location)"
    Write-Host "Python: $(python --version 2>&1)"
    Write-Host "Git: $(git --version)"
    Write-Host "Docker: $(docker --version 2>&1)"
    Write-Host "=============================" -ForegroundColor Cyan
}

# ====================
# АВТОМАТИЧЕСКАЯ ЗАГРУЗКА
# ====================

# Добавьте эту строку в ваш $PROFILE для автоматической загрузки:
# . "$HOME\.codeassistant\teacher\aliases\powershell_aliases.ps1"

Write-Host "Алиасы PowerShell загружены. Используйте show-help для списка команд." -ForegroundColor Green

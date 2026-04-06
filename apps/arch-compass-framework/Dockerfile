FROM mcr.microsoft.com/powershell:7.4-ubuntu-22.04

WORKDIR /workspace

# Копируем только код (без конфигов, которые могут отсутствовать)
COPY ArchCompass.psd1 ArchCompass.psm1 ./
COPY src/ ./src/
COPY tests/ ./tests/

# Минимальная установка модулей (без флагов, которые ломают сборку)
RUN pwsh -Command "Install-Module -Name Pester -Force -Scope CurrentUser; Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser"

# Запускаем модуль при старте контейнера
CMD ["pwsh", "-Command", "Import-Module ./ArchCompass.psm1 -Force; Start-ArchCompass -Help"]
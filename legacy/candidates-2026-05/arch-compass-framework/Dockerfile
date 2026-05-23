FROM mcr.microsoft.com/powershell:latest

WORKDIR /workspace

COPY . .

RUN pwsh -Command 'Install-Module PSScriptAnalyzer -Force; Install-Module Pester -Force'

CMD ["pwsh"]


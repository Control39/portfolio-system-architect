git add scripts/create_standalone.py scripts/init_standalone_repos.ps1 scripts/push_standalone_repos.ps1 scripts/commit_standalone.ps1 .gitignore
git commit -m "feat: add scripts for extracting microservices to standalone repos"

Write-Host "Коммит выполнен успешно!" -ForegroundColor Green

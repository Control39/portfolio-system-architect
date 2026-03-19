## GitHub Actions Secrets Template

This template lists the required secrets for GitHub Actions workflows.

```
DOCKER_USERNAME = your_dockerhub_username
DOCKER_PASSWORD = your_dockerhub_token (app password)
TELEGRAM_BOT_TOKEN = bot token
TELEGRAM_CHAT_ID = chat id
```

To set up secrets:
1. Go to Repository Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Enter the secret name and value

See: https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions
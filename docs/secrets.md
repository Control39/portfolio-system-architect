# Управление секретами и ротация

## Общие принципы

Система управления секретами в этом проекте основана на следующих принципах:

1. **Минимальные привилегии** - каждый компонент получает только необходимые ему секреты
2. **Шифрование в покое и в движении** - все секреты шифруются при хранении и передаче
3. **Автоматическая ротация** - секреты автоматически обновляются по расписанию
4. **Аудит и мониторинг** - все операции с секретами логируются и отслеживаются

## Процесс ротации секретов

### 1. Планирование ротации

Ротация секретов выполняется по следующему графику:

| Тип секрета | Период ротации | Метод |
|-------------|----------------|-------|
| API-ключи | 90 дней | Автоматический |
| Пароли баз данных | 180 дней | Автоматический |
| TLS-сертификаты | 60 дней до истечения | Автоматический |
| SSH-ключи | 365 дней | Полуавтоматический |

### 2. Автоматическая ротация

Автоматическая ротация выполняется с помощью GitHub Actions и специальных скриптов:

```yaml
name: Rotate Secrets

on:
  schedule:
    - cron: '0 2 * * 1' # Каждый понедельник в 02:00
  workflow_dispatch:

jobs:
  rotate-secrets:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt

      - name: Rotate API keys
        run: |
          python scripts/rotate_api_keys.py

      - name: Rotate database passwords
        run: |
          python scripts/rotate_db_passwords.py

      - name: Update Kubernetes secrets
        run: |
          kubectl create secret generic app-secrets \
            --from-literal=api-key=$(cat new_api_key.txt) \
            --from-literal=db-password=$(cat new_db_password.txt) \
            --dry-run=client -o yaml | kubectl apply -f -

      - name: Restart deployments
        run: |
          kubectl rollout restart deployment/it-compass
          kubectl rollout restart deployment/cloud-reason
          kubectl rollout restart deployment/ml-model-registry

      - name: Commit new secrets to Sealed Secrets
        run: |
          kubeseal --controller-name=sealed-secrets --format=yaml < secret.yaml > sealed-secret.yaml
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add sealed-secret.yaml
          git commit -m "feat(security): rotate secrets [skip ci]"
          git push
```

### 3. Полуавтоматическая ротация SSH-ключей

Для SSH-ключей используется полуавтоматический процесс:

1. Скрипт генерирует новую пару ключей
2. Новый публичный ключ добавляется в `authorized_keys` на целевых серверах
3. Система переходит в режим двойного ключа (старый и новый)
4. Через 7 дней старый приватный ключ удаляется
5. Через 14 дней старый публичный ключ удаляется из `authorized_keys`

### 4. Ротация в экстренных случаях

В случае компрометации секрета выполняется экстренная ротация:

1. Немедленная ротация всех связанных секретов
2. Расследование инцидента
3. Обновление всех систем, использующих секреты
4. Уведомление заинтересованных сторон
5. Документирование инцидента

## Инструменты

### Sealed Secrets

Для безопасного хранения секретов в Git используется [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets):

```bash
# Установка kubeseal
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.25.0/kubeseal-linux-amd64 -O kubeseal
chmod +x kubeseal
sudo mv kubeseal /usr/local/bin/

# Создание sealed secret
kubectl create secret generic mysecret \
  --from-literal=password=mypass \
  --dry-run=client -o yaml | \
  kubeseal --controller-name=sealed-secrets --format=yaml > mysealedsecret.yaml
```

### HashiCorp Vault (альтернатива)

Для более сложных сценариев можно использовать HashiCorp Vault:

```python
import hvac

class VaultSecretManager:
    def __init__(self, vault_addr, token):
        self.client = hvac.Client(url=vault_addr, token=token)

    def get_secret(self, path):
        return self.client.secrets.kv.v2.read_secret_version(path=path)['data']['data']

    def rotate_secret(self, path):
        # Логика ротации секрета
        pass
```

## Мониторинг и аудит

Все операции с секретами логируются и отправляются в систему мониторинга:

```python
import logging
import json
from datetime import datetime

class SecretAuditLogger:
    def __init__(self, log_file="secrets_audit.log"):
        self.logger = logging.getLogger("SecretAudit")
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_access(self, user, secret_name, action):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user": user,
            "secret": secret_name,
            "action": action,
            "ip": self._get_client_ip()
        }
        self.logger.info(json.dumps(log_entry))

    def _get_client_ip(self):
        # Получение IP-адреса клиента
        pass
```

## Рекомендации

1. Регулярно проверяйте срок действия всех сертификатов
2. Используйте разные секреты для разных окружений (dev, stage, prod)
3. Ограничивайте доступ к секретам по принципу минимальных привилегий
4. Регулярно проводите аудит использования секретов
5. Используйте автоматизацию для ротации секретов

## Ссылки

- [Sealed Secrets Documentation](https://github.com/bitnami-labs/sealed-secrets)
- [Kubernetes Secrets Best Practices](https://kubernetes.io/docs/concepts/configuration/secret/)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

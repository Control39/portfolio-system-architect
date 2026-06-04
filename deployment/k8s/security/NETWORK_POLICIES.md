# Сетевые политики Kubernetes

## Обзор

Сетевые политики обеспечивают изоляцию микросервисов на уровне сети, реализуя принцип **zero-trust** — по умолчанию запрещён весь трафик, разрешены только явно определённые соединения.

## Архитектура

### Общий принцип

1. **Default Deny All** — базовая политика запрещает весь ingress и egress трафик
2. **Service-specific policies** — для каждого сервиса создаются точные правила
3. **Least privilege** — каждый сервис имеет доступ только к необходимым ресурсам

### Схема коммуникаций

```
┌─────────────────────────────────────────────────────────────┐
│                    Ingress Controller                        │
│                    (Traefik/NGINX)                           │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Микросервисы                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ it-compass   │───▶│decision-     │───▶│ml-model-     │  │
│  │ :8501        │◀───│engine        │◀───│registry      │  │
│  └──────────────┘    │:8001         │    │:8000         │  │
│                      └──────┬───────┘    └──────────────┘  │
│                             │                               │
│  ┌──────────────┐    ┌──────▼───────┐    ┌──────────────┐  │
│  │portfolio-    │───▶│auth-service  │    │system-       │  │
│  │organizer     │    │:8000         │    │proof         │  │
│  │:8002         │    └──────────────┘    │:8003         │  │
│  └──────────────┘                         └──────────────┘  │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │career-       │                                           │
│  │development   │                                           │
│  │:8004         │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
              │                   │
              ▼                   ▼
┌──────────────────────┐  ┌──────────────────────┐
│    PostgreSQL        │  │      Redis           │
│    :5432             │  │      :6379           │
└──────────────────────┘  └──────────────────────┘
                              ┌──────────────────────┐
                              │    ChromaDB          │
                              │    :8000             │
                              └──────────────────────┘
```

## Детали политик

### auth-service

**Порт:** 8000
**Роль:** JWT аутентификация и авторизация

**Входящий трафик (Ingress):**
- ✅ Из ingress-контроллера (Traefik/NGINX) → порт 8000
- ✅ Health checks из monitoring namespace → порт 8000

**Исходящий трафик (Egress):**
- ✅ DNS (UDP/TCP 53)
- ✅ PostgreSQL → порт 5432

**Запрещено:**
- ❌ Доступ к другим микросервисам

---

### decision-engine

**Порт:** 8001
**Роль:** AI reasoning engine с RAG

**Входящий трафик:**
- ✅ it-compass → порт 8001
- ✅ portfolio-organizer → порт 8001
- ✅ Health checks → порт 8001

**Исходящий трафик:**
- ✅ DNS (UDP/TCP 53)
- ✅ PostgreSQL → порт 5432
- ✅ ChromaDB → порт 8000
- ✅ Redis → порт 6379

---

### it-compass

**Порт:** 8501
**Роль:** Streamlit UI для трекинга компетенций

**Входящий трафик:**
- ✅ Из ingress-контроллера → порт 8501
- ✅ Health checks → порт 8501

**Исходящий трафик:**
- ✅ DNS (UDP/TCP 53)
- ✅ PostgreSQL → порт 5432
- ✅ decision-engine → порт 8001
- ✅ auth-service → порт 8000

---

### ml-model-registry

**Порт:** 8000
**Роль:** Регистр ML-моделей

**Входящий трафик:**
- ✅ decision-engine → порт 8000
- ✅ portfolio-organizer → порт 8000
- ✅ Health checks → порт 8000

**Исходящий трафик:**
- ✅ DNS (UDP/TCP 53)
- ✅ PostgreSQL → порт 5432
- ✅ MinIO/S3 → порт 9000

---

### portfolio-organizer

**Порт:** 8002
**Роль:** Автоматический сбор доказательств

**Входящий трафик:**
- ✅ Из ingress-контроллера → порт 8002
- ✅ Health checks → порт 8002

**Исходящий трафик:**
- ✅ DNS (UDP/TCP 53)
- ✅ PostgreSQL → порт 5432
- ✅ decision-engine → порт 8001
- ✅ ml-model-registry → порт 8000
- ✅ auth-service → порт 8000
- ✅ system-proof → порт 8003

---

### career-development

**Порт:** 8004
**Роль:** Рекомендации по карьерному развитию

**Входящий трафик:**
- ✅ it-compass → порт 8004
- ✅ Health checks → порт 8004

**Исходящий трафик:**
- ✅ DNS (UDP/TCP 53)
- ✅ PostgreSQL → порт 5432
- ✅ decision-engine → порт 8001
- ✅ Redis → порт 6379

---

### system-proof

**Порт:** 8003
**Роль:** Хранилище доказательств (CoT)

**Входящий трафик:**
- ✅ portfolio-organizer → порт 8003
- ✅ Health checks → порт 8003

**Исходящий трафик:**
- ✅ DNS (UDP/TCP 53)
- ✅ PostgreSQL → порт 5432
- ✅ ChromaDB → порт 8000

## Pod Security Standards

Все сервисы используют **Pod Security Standard: restricted**:

- ❌ Привилегированные контейнеры запрещены
- ❌ Повышение привилегий запрещено
- ✅ Запуск от non-root пользователя
- ✅ Drop всех capabilities
- ✅ Только разрешённые volumes (configMap, emptyDir, secret, pvc)

## Применение политик

```bash
# Применение через kustomize
cd deployment/k8s/base/services
kubectl apply -k .

# Проверка политик
kubectl get networkpolicies -n portfolio

# Детальная информация
kubectl describe networkpolicy <name> -n portfolio

# Тестирование conectivity
kubectl exec -it <pod> -- nslookup <service>
```

## Проверка безопасности

### 1. Проверка изоляции

```bash
# Попытка доступа из одного сервиса к другому (должна быть заблокирована)
kubectl exec -it it-compass-<id> -- curl decision-engine:8001/health
# Ожидается: connection refused или timeout
```

### 2. Проверка разрешённых путей

```bash
# it-compass → decision-engine (должен работать)
kubectl exec -it it-compass-<id> -- curl decision-engine:8001/health
# Ожидается: 200 OK
```

### 3. Мониторинг заблокированного трафика

```bash
# Просмотр логов network policy (требуются дополнительные инструменты)
kubectl logs -l app=calico-node | grep DROP
```

## Обновление политик

При добавлении нового сервиса или изменении коммуникаций:

1. Создайте `network-policy.yaml` в директории сервиса
2. Добавьте в `kustomization.yaml`
3. Обновите документацию (этот файл)
4. Протестируйте в staging-окружении
5. Примените к production

## Troubleshooting

### Проблема: Сервис не может подключиться к БД

**Диагностика:**
```bash
kubectl describe networkpolicy <service>-network-policy -n portfolio
kubectl exec -it <pod> -- nc -zv postgres 5432
```

**Решение:** Проверить, что egress правило для PostgreSQL существует

### Проблема: Health checks не работают

**Диагностика:**
```bash
kubectl get pods -n monitoring
kubectl describe networkpolicy <service>-network-policy -n portfolio
```

**Решение:** Убедиться, что monitoring namespace имеет правильные labels

### Проблема: DNS не работает

**Решение:** Проверить egress правило для DNS (порт 53 UDP/TCP)

## См. также

- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Calico Network Policies](https://docs.tigera.io/calico/latest/about/network-policies)

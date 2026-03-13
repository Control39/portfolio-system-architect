## Arch-Compass: Пример для практика

### Задача
Спроектировать архитектуру микросервисного приложения для обработки заказов.

### Действие
1. Создать описание архитектуры в JSON-формате:
   ```json
   {
     "name": "Order Processing System",
     "microservices": [
       {"name": "order-service", "responsibility": "order management"},
       {"name": "payment-service", "responsibility": "payment processing"},
       {"name": "notification-service", "responsibility": "user notifications"}
     ]
   }
   ```
2. Запустить генерацию документации:
   ```bash
   cd components/arch-compass-framework
   python src/cli.py generate docs --input architecture.json
   ```
3. Получить полную архитектурную документацию в `docs/architecture/order-system.md`

### Результат
Полная архитектурная документация с диаграммами, описанием API и рекомендациями по развёртыванию.


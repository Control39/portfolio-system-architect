# Интерактивная визуализация reasoning-маршрутов

Добро пожаловать в интерактивную визуализацию reasoning-маршрутов! Здесь вы можете исследовать различные маршруты мышления, фильтровать их по направлениям и изучать структуру логических цепочек.

## Фильтрация по направлениям

<select id="direction-filter" onchange="filterRoutes()">
  <option value="all">Все направления</option>
  <option value="Аналитика">Аналитика</option>
  <option value="DevOps">DevOps</option>
  <option value="MLOps">MLOps</option>
  <option value="Документирование">Документирование</option>
  <option value="ИИ">ИИ</option>
  <option value="Системное мышление">Системное мышление</option>
</select>

<div id="routes-container">

## GitHub: Оптимизация CI/CD пайплайна

<div class="route" data-direction="DevOps">
```mermaid
graph LR
    A[Источник: Проблема медленного развертывания] --> B[Задача: Оптимизировать время GitHub Actions]
    B --> C[Инструмент: GitHub Actions, Cache API]
    B --> D[Направление: DevOps]
    C --> E[Подтверждение: Снижение времени с 15 до 3 минут]
    D --> E
    E --> F[Результат: Оптимизированный пайплайн в основной ветке]
    style D fill:#FBBC05,stroke:#333
```
</div>

## Hexlet: Реализация системы автоматического тестирования

<div class="route" data-direction="MLOps">
```mermaid
graph LR
    A[Источник: Необходимость повышения качества кода] --> B[Задача: Создать систему автоматического тестирования]
    B --> C[Инструмент: Python, PyTest, Docker]
    B --> D[Направление: MLOps]
    C --> E[Подтверждение: 95% покрытие тестами]
    D --> E
    E --> F[Результат: Система в учебном процессе Hexlet]
    style D fill:#34A853,stroke:#333
```
</div>

## Kaggle: Прогнозирование временных рядов

<div class="route" data-direction="Аналитика">
```mermaid
graph LR
    A[Источник: Соревнование по прогнозированию продаж] --> B[Задача: Построить модель временных рядов]
    B --> C[Инструмент: Python, Pandas, Prophet]
    B --> D[Направление: Аналитика]
    C --> E[Подтверждение: MAE < 0.15, лидерство]
    D --> E
    E --> F[Результат: Модель в системе аналитики]
    style D fill:#4285F4,stroke:#333
```
</div>

## Системная интеграция: Микросервисная архитектура

<div class="route" data-direction="Системное мышление">
```mermaid
graph LR
    A[Источник: Монолитное приложение] --> B[Задача: Реорганизовать в микросервисы]
    B --> C[Инструмент: Docker, Kubernetes, gRPC]
    B --> D[Направление: Системное мышление]
    C --> E[Подтверждение: 12 микросервисов, независимые циклы]
    D --> E
    E --> F[Результат: Повышение отказоустойчивости]
    style D fill:#F4B400,stroke:#333
```
</div>

## Документирование: Автоматизация технической документации

<div class="route" data-direction="Документирование">
```mermaid
graph LR
    A[Источник: Устаревшая документация] --> B[Задача: Создать систему автоматической генерации]
    B --> C[Инструмент: Sphinx, MkDocs, OpenAPI]
    B --> D[Направление: Документирование]
    C --> E[Подтверждение: Полное покрытие API]
    D --> E
    E --> F[Результат: Документация обновляется автоматически]
    style D fill:#A142F4,stroke:#333
```
</div>

## Искусственный интеллект: Система рекомендаций

<div class="route" data-direction="ИИ">
```mermaid
graph LR
    A[Источник: Низкая конверсия] --> B[Задача: Разработать персонализированную систему рекомендаций]
    B --> C[Инструмент: TensorFlow, Redis, Kafka]
    B --> D[Направление: ИИ]
    C --> E[Подтверждение: Рост конверсии на 35%]
    D --> E
    E --> F[Результат: Модель интегрирована в приложение]
    style D fill:#EA4335,stroke:#333
```
</div>

</div>

<script>
function filterRoutes() {
    const filter = document.getElementById('direction-filter').value;
    const routes = document.getElementsByClassName('route');

    for (let i = 0; i < routes.length; i++) {
        const route = routes[i];
        const direction = route.getAttribute('data-direction');

        if (filter === 'all' || direction === filter) {
            route.style.display = 'block';
        } else {
            route.style.display = 'none';
        }
    }
}

// Initialize with all routes visible
filterRoutes();
</script>

<style>
#direction-filter {
    padding: 10px;
    margin: 20px 0;
    border-radius: 5px;
    border: 1px solid #ddd;
    font-size: 16px;
}

.route {
    margin: 30px 0;
    padding: 15px;
    border: 1px solid #eee;
    border-radius: 8px;
    background-color: #f9f9f9;
}

.route h3 {
    margin-top: 0;
    color: #333;
}

/* Стили для Mermaid-диаграмм будут применяться автоматически */
</style>

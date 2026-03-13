## Cloud Reason (RAG): Пример для практика

### Задача
Проанализировать архитектурные решения конкурентов.

### Действие
1. Подготовить данные в `data/competitor_architectures/`:
   - Файлы с описанием архитектур конкурентов
2. Запустить анализ:
   ```bash
   cd components/cloud_reason
   python scripts/analyze_all.py --input data/competitor_architectures/ --output reports/
   ```
3. Получить отчёт в `reports/competitor_analysis.md`

### Результат
Количественный и качественный анализ архитектурных решений конкурентов с рекомендациями.


## ML Model Registry: Пример для практика

### Задача
Оценить качество нескольких моделей для задачи классификации текста.

### Действие
1. Загрузить модели в реестр:
   ```bash
   cd components/ml-model-registry
   python src/api/main.py upload --model bert-base --task text-classification
   python src/api/main.py upload --model roberta-base --task text-classification
   ```
2. Запустить сравнительное тестирование:
   ```bash
   python src/api/main.py benchmark --models bert-base,roberta-base --dataset glue
   ```
3. Получить отчёт в `reports/model_comparison.md`

### Результат
Объективное сравнение моделей с метриками точности, скорости и потребления ресурсов.


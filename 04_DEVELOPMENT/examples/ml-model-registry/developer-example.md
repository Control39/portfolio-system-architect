## ML Model Registry: Пример для разработчика

### Задача
Добавить новый тип теста для оценки устойчивости модели к adversarial атакам.

### Действие
1. Создать тест в `components/ml-model-registry/tests/test_adversarial.py`:
   ```python
   def test_adversarial_robustness(model, test_data):
       # Тестирование устойчивости к adversarial атакам
       pass
   ```
2. Добавить конфигурацию в `components/ml-model-registry/config/test_config.yaml`
3. Обновить документацию в `components/ml-model-registry/docs/testing.md`

### Результат
ML Model Registry поддерживает тестирование устойчивости моделей к adversarial атакам.


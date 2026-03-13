# Developer Example

- **Путь**: `04_DEVELOPMENT\examples\ml-model-registry\developer-example.md`
- **Тип**: .MD
- **Размер**: 879 байт
- **Последнее изменение**: 2026-03-11 18:54:47

## Превью

```
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
3. Обновить документацию в `components/ml-model-re
... (файл продолжается)
```

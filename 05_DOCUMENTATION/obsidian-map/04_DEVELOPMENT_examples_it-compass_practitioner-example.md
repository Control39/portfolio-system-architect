# Practitioner Example

- **Путь**: `04_DEVELOPMENT\examples\it-compass\practitioner-example.md`
- **Тип**: .MD
- **Размер**: 873 байт
- **Последнее изменение**: 2026-03-11 18:53:33

## Превью

```
## IT-Compass: Пример для практика

### Задача
Оценить текущий уровень компетенций команды разработчиков.

### Действие
1. Подготовить CSV-файл с данными команды в формате:
   ```
   developer_id,skill_1,skill_2,skill_3
   dev_001,3,4,2
   dev_002,4,
   ```
23,3. Запустить анализ:
   ```bash
   cd components/it-compass
   python src/main.py analyze-team --input data/team_skills.csv
   ```
3. Получить отчёт в `reports/team_analysis.md` с рекомендациями по развитию.

### Результат
Объективная оцен
... (файл продолжается)
```

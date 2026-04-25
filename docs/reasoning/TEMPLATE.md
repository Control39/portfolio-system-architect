# Шаблон reasoning-маршрута

## Основная информация
- **Дата создания**: {{date}}
- **Направление**: {{direction}}
- **Уровень сложности**: {{complexity}}
- **Ожидаемая польза**: {{benefit}}

## Граф маршрута
```json
{
  "nodes": [
    {
      "id": "source",
      "type": "source",
      "label": "Источник",
      "data": {
        "description": "{{source_description}}"
      }
    },
    {
      "id": "task",
      "type": "task",
      "label": "Задача",
      "data": {
        "description": "{{task_description}}"
      }
    },
    {
      "id": "tool",
      "type": "tool",
      "label": "Инструмент",
      "data": {
        "description": "{{tool_description}}"
      }
    },
    {
      "id": "direction",
      "type": "direction",
      "label": "Направление",
      "data": {
        "description": "{{direction_description}}"
      }
    },
    {
      "id": "confirmation",
      "type": "confirmation",
      "label": "Подтверждение",
      "data": {
        "description": "{{confirmation_description}}"
      }
    },
    {
      "id": "result",
      "type": "result",
      "label": "Результат",
      "data": {
        "description": "{{result_description}}"
      }
    }
  ],
  "edges": [
    { "source": "source", "target": "task" },
    { "source": "task", "target": "tool" },
    { "source": "task", "target": "direction" },
    { "source": "tool", "target": "confirmation" },
    { "source": "direction", "target": "confirmation" },
    { "source": "confirmation", "target": "result" }
  ]
}
```

## Описание этапов
### Источник
{{source_explanation}}

### Задача
{{task_explanation}}

### Инструмент
{{tool_explanation}}

### Направление
{{direction_explanation}}

### Подтверждение
{{confirmation_explanation}}

### Результат
{{result_explanation}}

## Рекомендации
{{recommendations}}
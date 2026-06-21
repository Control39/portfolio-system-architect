# 📦 {{ service_name }}

> *Этот файл автоматически генерируется автономным когнитивным агентом на основе анализа исходного кода. Ручные изменения будут перезаписаны.*

## 🎯 Назначение сервиса

{{ purpose }}

## 🛠️ Технологический стек

*   **Язык:** {{ language }} {{ python_version if language == 'Python' else '' }}
*   **Фреймворк:** {{ framework }}
*   **Ключевые библиотеки:**
    {% for lib in libraries %}
    *   {{ lib }}
    {% endfor %}

## 🧱 Архитектура и модули

Сервис состоит из следующих основных модулей:
{% for module in modules %}
*   **{{ module.file_path }}**: {{ module.description }}
    *   Ключевые классы/функции: {{ module.key_elements | join(', ') }}
    *   Взаимодействие: {{ module.interaction }}
{% endfor %}

## 🚀 Ключевые возможности (реализованные в коде)

{% for capability in capabilities %}
*   {{ capability }}
{% endfor %}

## ✅ Статус готовности

*   **Уровень готовности:** {{ readiness_level }}
*   **Покрытие тестами:** {{ test_coverage }}%
*   **Наличие тестов:** {{ has_tests }}
*   **Критические замечания:** {% if critical_issues %}{{ critical_issues }}{% else %}Не обнаружено.{% endif %}

---
*Сгенерировано агентом ID: {{ agent_id }}*
*Время генерации: {{ timestamp }}*

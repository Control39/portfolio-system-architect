# Пользовательские инструменты для CodeAssistant

Каталог для пользовательских инструментов TypeScript/JavaScript, которые могут быть загружены CodeAssistant. Создано для проекта portfolio-system-architect.

## Структура каталога (актуальная)

```
codeassistant/tools/
├── README.md                    # Эта документация
├── index.ts                     # Главный файл экспорта
├── system-analysis/             # Инструменты анализа системы
│   └── project-scanner.ts       # Анализ технологического стека проекта
├── cognitive/                   # Когнитивные инструменты
│   └── rag-optimizer.ts         # Оптимизация RAG систем
├── productivity/                # Инструменты продуктивности
│   └── workspace-optimizer.ts   # Оптимизация рабочего пространства
├── security/                    # Инструменты безопасности
│   └── security-auditor.ts      # Аудит безопасности кода
├── monitoring/                  # Инструменты мониторинга
│   └── metrics-analyzer.ts      # Анализ метрик и мониторинг
└── templates/                   # Шаблоны инструментов (планируется)
```

## Доступные инструменты

### 1. project-scanner
**Категория:** system-analysis
**Описание:** Анализирует технологический стек проекта, определяет языки, фреймворки, зависимости и архитектурные паттерны.
**Использование:**
```typescript
import { projectScannerTool } from 'codeassistant/tools';

const result = await projectScannerTool.execute({
  path: './my-project',
  depth: 2,
  analyzeDependencies: true
});
```

### 2. rag-optimizer
**Категория:** cognitive
**Описание:** Анализирует и оптимизирует RAG (Retrieval-Augmented Generation) системы для улучшения качества ответов.
**Использование:**
```typescript
import { ragOptimizerTool } from 'codeassistant/tools';

const result = await ragOptimizerTool.execute({
  systemType: 'documentation',
  currentMetrics: { precision: 0.75, recall: 0.68 },
  optimizationGoals: ['precision', 'response_time']
});
```

### 3. workspace-optimizer
**Категория:** productivity
**Описание:** Анализирует и оптимизирует рабочее пространство разработчика, предлагая улучшения организации файлов и структуры.
**Использование:**
```typescript
import { workspaceOptimizerTool } from 'codeassistant/tools';

const result = await workspaceOptimizerTool.execute({
  workspacePath: '/home/user/projects',
  optimizationAreas: ['file_organization', 'tool_configuration']
});
```

### 4. security-auditor
**Категория:** security
**Описание:** Анализирует код на наличие уязвимостей безопасности и небезопасных практик для различных языков программирования.
**Использование:**
```typescript
import { securityAuditorTool } from 'codeassistant/tools';

const result = await securityAuditorTool.execute({
  code: 'def process(input): eval(input)',
  language: 'python',
  checkLevel: 'standard'
});
```

### 5. metrics-analyzer
**Категория:** monitoring
**Описание:** Анализирует метрики производительности, доступности и использования ресурсов системы, генерирует рекомендации.
**Использование:**
```typescript
import { metricsAnalyzerTool } from 'codeassistant/tools';

const result = await metricsAnalyzerTool.execute({
  metrics: {
    cpu: { current: 65, avg: 60 },
    memory: { current: 72, avg: 68 },
    application: { latency: { p95: 450 }, errorRate: 2.1 }
  },
  timeRange: '24h'
});
```

## Как создавать инструменты

### Базовый шаблон инструмента

```typescript
// basic-tool.ts
export const myTool = {
  name: "my_tool",
  description: "Описание того, что делает инструмент",
  parameters: {
    type: "object",
    properties: {
      param1: {
        type: "string",
        description: "Описание параметра"
      }
    },
    required: ["param1"]
  },
  execute: async (args: any) => {
    // Логика инструмента
    return { result: "Успешно выполнено", data: args.param1 };
  }
};
```

### Инструмент с интеграцией MCP

```typescript
// mcp-integration.ts
export const ollamaChatTool = {
  name: "ollama_chat",
  description: "Отправляет запрос к локальной модели Ollama",
  parameters: {
    type: "object",
    properties: {
      prompt: {
        type: "string",
        description: "Текст запроса к модели"
      },
      model: {
        type: "string",
        description: "Модель Ollama (по умолчанию: llama3.2:3b)",
        default: "llama3.2:3b"
      }
    },
    required: ["prompt"]
  },
  execute: async (args: any) => {
    // Интеграция с MCP сервером Ollama
    const response = await fetch("http://localhost:11434/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: args.model,
        prompt: args.prompt,
        stream: false
      })
    });

    const data = await response.json();
    return { response: data.response, model: args.model };
  }
};
```

## Регистрация инструментов

Инструменты автоматически загружаются при наличии файлов `.ts` или `.js` в этом каталоге.
Для ручной регистрации создайте файл `index.ts`:

```typescript
// index.ts
export * from './system-analysis/project-scanner';
export * from './cognitive/rag-optimizer';
export * from './productivity/task-organizer';
```

## Рекомендации по разработке

1. **Типизация**: Используйте TypeScript для лучшей типизации
2. **Обработка ошибок**: Всегда обрабатывайте ошибки в execute()
3. **Логирование**: Добавляйте логи для отладки
4. **Документация**: Комментируйте параметры и возвращаемые значения
5. **Безопасность**: Не включайте секреты в код

## Примеры использования

### Сканер технологического стека

```typescript
// system-analysis/tech-stack-analyzer.ts
export const techStackAnalyzer = {
  name: "analyze_tech_stack",
  description: "Анализирует технологический стек проекта",
  parameters: {
    type: "object",
    properties: {
      path: {
        type: "string",
        description: "Путь к проекту",
        default: "."
      }
    }
  },
  execute: async (args: any) => {
    // Анализ package.json, requirements.txt, Dockerfile и т.д.
    const stack = {
      languages: ["Python", "TypeScript"],
      frameworks: ["FastAPI", "React"],
      databases: ["PostgreSQL", "Redis"],
      tools: ["Docker", "Terraform", "Kubernetes"]
    };

    return {
      stack,
      recommendations: [
        "Добавить мониторинг с Prometheus",
        "Настроить автоматическое тестирование"
      ]
    };
  }
};
```

## Интеграция с существующей системой

Эти инструменты могут быть использованы:
1. **Cognitive Automation Agent** - для автоматизации задач
2. **SourceCraft** - как пользовательские MCP инструменты
3. **VS Code расширения** - через API CodeAssistant
4. **CI/CD пайплайны** - для автоматической проверки

## Следующие шаги

1. Создайте свой первый инструмент в `system-analysis/`
2. Протестируйте его через CodeAssistant
3. Добавьте документацию в этот README
4. Создайте pull request для добавления в основной репозиторий

// ============================================================================
// ИНИЦИАЛИЗАЦИЯ
// ============================================================================
let projectPath = null;
let editor = null;
let envEditor = document.getElementById('env-editor');
let currentConfig = null;
let statusChart = null;
let memoryChart = null;
let updateInterval = null;

// Информация о системе
document.getElementById('node-version').textContent = systemInfo.versions.node;
document.getElementById('platform').textContent = systemInfo.platform;

// ============================================================================
// MONACO EDITOR
// ============================================================================
require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' } });

require(['vs/editor/editor.main'], function() {
  editor = monaco.editor.create(document.getElementById('editor'), {
    value: '# Откройте проект для загрузки конфига',
    language: 'yaml',
    theme: 'vs-dark',
    automaticLayout: true,
    fontSize: 14,
    fontFamily: 'Consolas, Monaco, monospace',
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    lineNumbers: 'on',
    renderWhitespace: 'selection',
    tabSize: 2
  });

  // Добавляем сниппеты
  monaco.languages.registerCompletionItemProvider('yaml', {
    provideCompletionItems: (model, position) => {
      const suggestions = [
        {
          label: 'model-ollama',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: `- id: ${1:model-id}\n  name: ${2:Model Name}\n  provider:\n    type: ollama\n    baseUrl: http://localhost:11434\n    model: ${3:model-name:tag}\n  capabilities:\n    context: 4096\n    maxTokens: 2048\n  defaults:\n    temperature: 0.2\n  roles: [chat, edit]`,
          documentation: 'Добавить локальную модель Ollama',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
        },
        {
          label: 'model-gigachat',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: `- id: gigachat\n  name: GigaChat Pro\n  provider:\n    type: openai-compatible\n    baseUrl: https://api.sbercloud.ru/llm/v1\n    model: GigaChat\n    auth:\n      keyEnv: GIGACHAT_API_KEY\n  capabilities:\n    context: 8192\n    maxTokens: 2048`,
          documentation: 'Добавить GigaChat',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
        }
      ];
      return { suggestions };
    }
  });
});

// ============================================================================
// ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК
// ============================================================================
document.querySelectorAll('.editor-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.editor-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.editor-pane').forEach(p => p.classList.remove('active'));

    tab.classList.add('active');
    document.getElementById(tab.dataset.tab + '-pane').classList.add('active');

    if (tab.dataset.tab === 'monitor') {
      startMonitoring();
    } else {
      stopMonitoring();
    }
  });
});

// ============================================================================
// УПРАВЛЕНИЕ ОКНОМ
// ============================================================================
document.getElementById('minimize-btn').addEventListener('click', () => {
  window.electronAPI.minimizeWindow?.();
});

document.getElementById('maximize-btn').addEventListener('click', () => {
  window.electronAPI.maximizeWindow?.();
});

document.getElementById('close-btn').addEventListener('click', () => {
  window.electronAPI.closeWindow?.();
});

// ============================================================================
// ОТКРЫТИЕ ПРОЕКТА
// ============================================================================
document.getElementById('open-project-btn').addEventListener('click', async () => {
  const path = await window.electronAPI.openProject();
  if (path) {
    projectPath = path;
    document.getElementById('project-path').textContent = path;
    loadProjectConfig();
    checkOllama();
  }
});

// Слушатель события открытия проекта
window.electronAPI.onProjectOpened((path) => {
  projectPath = path;
  document.getElementById('project-path').textContent = path;
  loadProjectConfig();
  checkOllama();
});

// ============================================================================
// ЗАГРУЗКА КОНФИГА ПРОЕКТА
// ============================================================================
async function loadProjectConfig() {
  const result = await window.electronAPI.readConfig(projectPath);
  if (result.success) {
    currentConfig = result.config;
    editor.setValue(jsyaml.dump(result.config, { indent: 2 }));
    envEditor.value = result.env;
    updateModelsList(result.config.models);
    updateStatusBar();
    addOutput('✅ Конфиг загружен', 'success');
  } else {
    addOutput('❌ Ошибка загрузки: ' + result.error, 'error');
  }
}

// ============================================================================
// ОБНОВЛЕНИЕ СПИСКА МОДЕЛЕЙ
// ============================================================================
function updateModelsList(models) {
  const list = document.getElementById('models-list');
  if (!models || models.length === 0) {
    list.innerHTML = '<div class="text-muted text-center py-3">Нет моделей</div>';
    return;
  }

  list.innerHTML = models.map(model => `
    <div class="model-item" data-model='${JSON.stringify(model)}'>
      <div class="model-name">
        <i class="fas fa-microchip" style="color: ${getProviderColor(model.provider.type)}"></i>
        ${model.name}
      </div>
      <div class="model-type">
        ${model.provider.type} • ${model.capabilities.context} токенов
      </div>
    </div>
  `).join('');

  // Добавляем обработчики
  document.querySelectorAll('.model-item').forEach(item => {
    item.addEventListener('click', () => {
      const model = JSON.parse(item.dataset.model);
      showModelDetails(model);
    });
  });
}

function getProviderColor(type) {
  const colors = {
    ollama: '#2ecc71',
    'openai-compatible': '#3498db',
    yandex: '#f1c40f',
    deepseek: '#9b59b6'
  };
  return colors[type] || '#95a5a6';
}

// ============================================================================
// ПОКАЗ ДЕТАЛЕЙ МОДЕЛИ
// ============================================================================
function showModelDetails(model) {
  const modal = new bootstrap.Modal(document.getElementById('modelModal'));

  document.getElementById('model-details').innerHTML = `
    <table class="table table-sm table-dark">
      <tr><th>ID</th><td>${model.id}</td></tr>
      <tr><th>Имя</th><td>${model.name}</td></tr>
      <tr><th>Провайдер</th><td>${model.provider.type}</td></tr>
      <tr><th>Модель</th><td>${model.provider.model || '-'}</td></tr>
      <tr><th>Контекст</th><td>${model.capabilities.context} токенов</td></tr>
      <tr><th>Max токенов</th><td>${model.capabilities.maxTokens}</td></tr>
      <tr><th>Температура</th><td>${model.defaults?.temperature || 0.2}</td></tr>
      <tr><th>Роли</th><td>${(model.roles || []).join(', ')}</td></tr>
    </table>

    <h6 class="mt-3">Промпт:</h6>
    <pre class="bg-dark p-2" style="font-size: 11px;">${model.promptTemplate || 'Не задан'}</pre>
  `;

  modal.show();
}

// ============================================================================
// СОХРАНЕНИЕ
// ============================================================================
document.getElementById('save-btn')?.addEventListener('click', saveConfig);
window.electronAPI.onSaveConfig(saveConfig);

async function saveConfig() {
  if (!projectPath) {
    alert('Сначала откройте проект');
    return;
  }

  try {
    const configYaml = editor.getValue();
    const config = jsyaml.load(configYaml);
    const env = envEditor.value;

    const result = await window.electronAPI.saveConfig(projectPath, config, env);
    if (result.success) {
      addOutput('✅ Конфиг сохранён', 'success');
      currentConfig = config;
      updateModelsList(config.models);
    } else {
      addOutput('❌ Ошибка: ' + result.error, 'error');
    }
  } catch (error) {
    addOutput('❌ Ошибка в YAML: ' + error.message, 'error');
  }
}

// ============================================================================
// ГЕНЕРАЦИЯ КОНФИГОВ
// ============================================================================
document.getElementById('generate-btn').addEventListener('click', generateConfigs);

async function generateConfigs() {
  if (!projectPath) {
    alert('Сначала откройте проект');
    return;
  }

  addOutput('🔄 Генерация конфигов...', 'info');

  const result = await window.electronAPI.runGenerate(projectPath);

  if (result.success) {
    addOutput('✅ Генерация завершена', 'success');
  } else {
    addOutput('❌ Ошибка генерации', 'error');
  }
}

// Слушатель вывода генерации
window.electronAPI.onGenerateOutput((data) => {
  addOutput(data, 'info');
});

// ============================================================================
// ПРОВЕРКА OLLAMA
// ============================================================================
document.getElementById('check-ollama-btn').addEventListener('click', checkOllama);

async function checkOllama() {
  addOutput('🔄 Проверка Ollama...', 'info');

  const status = await window.electronAPI.checkOllama();

  const badge = document.getElementById('ollama-badge');
  const dot = document.getElementById('ollama-status-dot');
  const text = document.getElementById('ollama-status-text');

  if (status.running) {
    badge.className = 'status-badge online';
    badge.innerHTML = '<i class="fas fa-circle"></i> Ollama: работает';
    dot.className = 'status-dot online';
    text.textContent = `Ollama: ${status.version || 'работает'}`;

    addOutput(`✅ Ollama запущен. Моделей: ${status.models.length}`, 'success');
    if (status.models.length > 0) {
      status.models.forEach(m => addOutput(`  📦 ${m.name} (${m.size})`, 'info'));
    }
  } else {
    badge.className = 'status-badge offline';
    badge.innerHTML = '<i class="fas fa-circle"></i> Ollama: не запущен';
    dot.className = 'status-dot offline';
    text.textContent = 'Ollama: не запущен';

    addOutput('❌ Ollama не запущен', 'error');
  }

  updateStatusBar();
}

// ============================================================================
// ТЕСТЫ
// ============================================================================
document.getElementById('run-tests-btn').addEventListener('click', runTests);

async function runTests() {
  addOutput('🔄 Запуск тестов...', 'info');

  const result = await window.electronAPI.runTests(projectPath);

  if (result.success) {
    addOutput('✅ Тесты пройдены', 'success');
  } else {
    addOutput('❌ Ошибка в тестах', 'error');
  }
}

window.electronAPI.onTestOutput((data) => {
  addOutput(data, 'info');
});

// ============================================================================
// МОНИТОРИНГ
// ============================================================================
document.getElementById('open-monitor-btn').addEventListener('click', () => {
  document.querySelector('[data-tab="monitor"]').click();
});

function startMonitoring() {
  if (updateInterval) return;

  initCharts();
  updateSystemStatus();
  updateInterval = setInterval(updateSystemStatus, 5000);
}

function stopMonitoring() {
  if (updateInterval) {
    clearInterval(updateInterval);
    updateInterval = null;
  }
}

function initCharts() {
  const ctx = document.getElementById('status-chart').getContext('2d');
  statusChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Запросы',
        data: [],
        borderColor: '#007acc',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });

  const memCtx = document.getElementById('memory-chart').getContext('2d');
  memoryChart = new Chart(memCtx, {
    type: 'doughnut',
    data: {
      labels: ['Использовано', 'Свободно'],
      datasets: [{
        data: [0, 100],
        backgroundColor: ['#007acc', '#404040']
      }]
    }
  });
}

async function updateSystemStatus() {
  const status = await window.electronAPI.getSystemStatus();

  // Обновляем метрики
  document.getElementById('mon-ollama').textContent = status.ollama.running ? '✅ Работает' : '❌ Не запущен';
  document.getElementById('mon-models').textContent = status.ollama.models.length;

  const configsCount = Object.values(status.configs).filter(c => c.exists).length;
  document.getElementById('mon-configs').textContent = `${configsCount}/4`;

  const uptime = Math.floor(status.uptime / 60);
  document.getElementById('mon-uptime').textContent = `${uptime} мин`;

  // Обновляем графики
  if (statusChart) {
    const time = new Date().toLocaleTimeString();
    statusChart.data.labels.push(time);
    statusChart.data.datasets[0].data.push(Math.random() * 10);
    if (statusChart.data.labels.length > 10) {
      statusChart.data.labels.shift();
      statusChart.data.datasets[0].data.shift();
    }
    statusChart.update();
  }

  if (memoryChart) {
    const used = process.memoryUsage().heapUsed / 1024 / 1024;
    const total = process.memoryUsage().heapTotal / 1024 / 1024;
    memoryChart.data.datasets[0].data = [used, total - used];
    memoryChart.update();
  }
}

// ============================================================================
// ДОБАВЛЕНИЕ ВЫВОДА
// ============================================================================
function addOutput(text, type = 'info') {
  const panel = document.getElementById('output-panel');
  const line = document.createElement('div');
  line.className = 'output-line ' + (type === 'error' ? 'error' : type === 'success' ? 'success' : '');

  const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : '➡️';
  line.innerHTML = `${icon} ${text}`;

  panel.appendChild(line);
  panel.scrollTop = panel.scrollHeight;

  // Ограничиваем количество строк
  while (panel.children.length > 100) {
    panel.removeChild(panel.firstChild);
  }
}

// ============================================================================
// ОБНОВЛЕНИЕ СТАТУС БАРА
// ============================================================================
function updateStatusBar() {
  if (!currentConfig) return;

  const configs = [
    { name: 'Continue', path: systemInfo.homeDir + '\\.continue\\config.json' },
    { name: 'SourceCraft', path: projectPath + '\\.sourcecraft\\ci.yaml' },
    { name: 'Koda', path: projectPath + '\\.koda\\config.yaml' },
    { name: 'Cline', path: projectPath + '\\.cline\\config.yaml' }
  ];

  let count = 0;
  configs.forEach(c => {
    try {
      if (require('fs').existsSync(c.path)) count++;
    } catch {}
  });

  document.getElementById('configs-count').textContent = `${count}/4 конфигов`;
}

// ============================================================================
// ВРЕМЯ
// ============================================================================
setInterval(() => {
  document.getElementById('current-time').textContent = new Date().toLocaleTimeString();
}, 1000);

// ============================================================================
// ИНИЦИАЛИЗАЦИЯ
// ============================================================================
checkOllama();

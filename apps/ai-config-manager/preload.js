const { contextBridge, ipcRenderer } = require('electron');

// Безопасный API для рендерера
contextBridge.exposeInMainWorld('electronAPI', {
  // Проект
  openProject: () => ipcRenderer.invoke('open-project'),
  readConfig: (path) => ipcRenderer.invoke('read-config', path),
  saveConfig: (path, config, env) => ipcRenderer.invoke('save-config', path, config, env),

  // Генерация
  runGenerate: (path) => ipcRenderer.invoke('run-generate', path),

  // Проверка
  checkOllama: () => ipcRenderer.invoke('check-ollama'),
  getSystemStatus: () => ipcRenderer.invoke('get-system-status'),

  // Тесты
  runTests: (path) => ipcRenderer.invoke('run-tests', path),

  // Слушатели
  onProjectOpened: (callback) => {
    ipcRenderer.on('project-opened', (event, path) => callback(path));
  },
  onGenerateOutput: (callback) => {
    ipcRenderer.on('generate-output', (event, data) => callback(data));
  },
  onTestOutput: (callback) => {
    ipcRenderer.on('test-output', (event, data) => callback(data));
  },
  onSaveConfig: (callback) => {
    ipcRenderer.on('save-config', () => callback());
  }
});

// Информация о системе
contextBridge.exposeInMainWorld('systemInfo', {
  platform: process.platform,
  versions: process.versions,
  homeDir: process.env.USERPROFILE || process.env.HOME
});

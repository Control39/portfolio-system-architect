const { app, BrowserWindow, Menu, ipcMain, dialog, Tray, nativeImage } = require('electron');
const path = require('path');
const fs = require('fs-extra');
const yaml = require('js-yaml');
const { exec, spawn } = require('child_process');
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

let mainWindow;
let tray = null;
let monitorServer;

// ============================================================================
// МОНИТОРИНГ СЕРВЕР
// ============================================================================
function startMonitorServer() {
  const app = express();
  const server = http.createServer(app);
  const io = new Server(server);

  app.use(express.static(path.join(__dirname, '../monitor-public')));

  io.on('connection', (socket) => {
    console.log('👤 Клиент подключился к мониторингу');
    
    // Отправляем статус каждые 5 секунд
    const interval = setInterval(async () => {
      const status = await getSystemStatus();
      socket.emit('status-update', status);
    }, 5000);

    socket.on('disconnect', () => {
      clearInterval(interval);
    });
  });

  server.listen(3000, () => {
    console.log('📊 Мониторинг доступен на http://localhost:3000');
  });

  return server;
}

// ============================================================================
// ПОЛУЧЕНИЕ СТАТУСА СИСТЕМЫ
// ============================================================================
async function getSystemStatus() {
  const status = {
    timestamp: new Date().toISOString(),
    ollama: { running: false, models: [] },
    configs: {},
    memory: process.memoryUsage(),
    uptime: process.uptime()
  };

  // Проверка Ollama
  try {
    const { stdout } = await execPromise('ollama list');
    status.ollama.running = true;
    status.ollama.models = stdout.split('\n')
      .filter(line => line.includes(':'))
      .map(line => {
        const parts = line.split(/\s+/);
        return { name: parts[0], size: parts[2] + ' ' + (parts[3] || '') };
      });
  } catch {
    status.ollama.running = false;
  }

  // Проверка конфигов
  const projectPath = await getProjectPath();
  if (projectPath) {
    const configs = [
      { name: 'Continue', path: path.join(process.env.USERPROFILE, '.continue', 'config.json') },
      { name: 'SourceCraft', path: path.join(projectPath, '.sourcecraft', 'ci.yaml') },
      { name: 'Koda', path: path.join(projectPath, '.koda', 'config.yaml') },
      { name: 'Cline', path: path.join(projectPath, '.cline', 'config.yaml') }
    ];

    for (const config of configs) {
      try {
        const exists = await fs.pathExists(config.path);
        if (exists) {
          const stat = await fs.stat(config.path);
          status.configs[config.name] = {
            exists: true,
            size: stat.size,
            modified: stat.mtime
          };
        } else {
          status.configs[config.name] = { exists: false };
        }
      } catch {
        status.configs[config.name] = { exists: false, error: true };
      }
    }
  }

  return status;
}

function execPromise(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) reject(error);
      else resolve({ stdout, stderr });
    });
  });
}

// ============================================================================
// СОЗДАНИЕ ГЛАВНОГО ОКНА
// ============================================================================
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, '../preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    icon: path.join(__dirname, '../../build/icon.png'),
    title: 'AI Config Manager',
    frame: true,
    show: false
  });

  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Меню
  const menu = Menu.buildFromTemplate([
    {
      label: 'Файл',
      submenu: [
        {
          label: 'Открыть проект',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
              properties: ['openDirectory'],
              title: 'Выберите папку проекта',
              defaultPath: process.env.USERPROFILE + '\\Desktop'
            });
            if (!result.canceled) {
              mainWindow.webContents.send('project-opened', result.filePaths[0]);
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Сохранить',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.send('save-config');
          }
        },
        {
          label: 'Сохранить как...',
          accelerator: 'CmdOrCtrl+Shift+S',
          click: () => {
            mainWindow.webContents.send('save-config-as');
          }
        },
        { type: 'separator' },
        { label: 'Выход', role: 'quit', accelerator: 'CmdOrCtrl+Q' }
      ]
    },
    {
      label: 'Правка',
      submenu: [
        { label: 'Отменить', role: 'undo' },
        { label: 'Повторить', role: 'redo' },
        { type: 'separator' },
        { label: 'Вырезать', role: 'cut' },
        { label: 'Копировать', role: 'copy' },
        { label: 'Вставить', role: 'paste' }
      ]
    },
    {
      label: 'Инструменты',
      submenu: [
        {
          label: 'Сгенерировать конфиги',
          accelerator: 'F5',
          click: () => {
            mainWindow.webContents.send('run-generate');
          }
        },
        {
          label: 'Проверить Ollama',
          click: () => {
            mainWindow.webContents.send('check-ollama');
          }
        },
        { type: 'separator' },
        {
          label: 'Открыть мониторинг',
          accelerator: 'F6',
          click: () => {
            require('electron').shell.openExternal('http://localhost:3000');
          }
        },
        {
          label: 'Запустить тесты',
          click: () => {
            mainWindow.webContents.send('run-tests');
          }
        }
      ]
    },
    {
      label: 'Вид',
      submenu: [
        { label: 'Перезагрузить', role: 'reload' },
        { label: 'Увеличить', role: 'zoomin' },
        { label: 'Уменьшить', role: 'zoomout' },
        { type: 'separator' },
        { label: 'Полный экран', role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Помощь',
      submenu: [
        {
          label: 'Документация',
          click: () => {
            require('electron').shell.openExternal('https://github.com/yourusername/portfolio-system-architect');
          }
        },
        {
          label: 'Сообщить о проблеме',
          click: () => {
            require('electron').shell.openExternal('https://github.com/yourusername/portfolio-system-architect/issues');
          }
        },
        { type: 'separator' },
        { label: 'О программе', role: 'about' }
      ]
    }
  ]);
  Menu.setApplicationMenu(menu);

  // Трей
  tray = new Tray(nativeImage.createFromPath(path.join(__dirname, '../../build/icon.png')));
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Показать', click: () => mainWindow.show() },
    { label: 'Сгенерировать', click: () => mainWindow.webContents.send('run-generate') },
    { type: 'separator' },
    { label: 'Выход', click: () => app.quit() }
  ]);
  tray.setToolTip('AI Config Manager');
  tray.setContextMenu(contextMenu);
  tray.on('click', () => mainWindow.show());
}

// ============================================================================
// ЗАПУСК
// ============================================================================
app.whenReady().then(() => {
  monitorServer = startMonitorServer();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (monitorServer) monitorServer.close();
});

// ============================================================================
// IPC ОБРАБОТЧИКИ
// ============================================================================

// Открыть проект
ipcMain.handle('open-project', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: 'Выберите папку проекта'
  });
  return result.canceled ? null : result.filePaths[0];
});

// Чтение конфига
ipcMain.handle('read-config', async (event, projectPath) => {
  try {
    const configPath = path.join(projectPath, '.ai-config', 'master-config.yaml');
    const envPath = path.join(projectPath, '.env');
    
    const config = yaml.load(await fs.readFile(configPath, 'utf8'));
    const env = await fs.pathExists(envPath) ? await fs.readFile(envPath, 'utf8') : '';
    
    return { success: true, config, env };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Сохранение конфига
ipcMain.handle('save-config', async (event, projectPath, config, env) => {
  try {
    const configPath = path.join(projectPath, '.ai-config', 'master-config.yaml');
    const envPath = path.join(projectPath, '.env');
    
    await fs.writeFile(configPath, yaml.dump(config, { indent: 2 }));
    await fs.writeFile(envPath, env);
    
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Генерация конфигов
ipcMain.handle('run-generate', async (event, projectPath) => {
  return new Promise((resolve) => {
    const process = spawn('npm', ['run', 'generate:all'], {
      cwd: path.join(projectPath, '.ai-config'),
      shell: true
    });

    let output = '';
    let error = '';

    process.stdout.on('data', (data) => {
      output += data.toString();
      mainWindow.webContents.send('generate-output', data.toString());
    });

    process.stderr.on('data', (data) => {
      error += data.toString();
      mainWindow.webContents.send('generate-output', data.toString());
    });

    process.on('close', (code) => {
      resolve({
        success: code === 0,
        output,
        error
      });
    });
  });
});

// Проверка Ollama
ipcMain.handle('check-ollama', async () => {
  try {
    const { stdout } = await execPromise('ollama list');
    const models = stdout.split('\n')
      .filter(line => line.includes(':'))
      .map(line => {
        const parts = line.split(/\s+/);
        return { name: parts[0], size: parts[2] + ' ' + (parts[3] || '') };
      });
    
    // Получаем версию
    const { stdout: versionOut } = await execPromise('ollama --version');
    
    return {
      running: true,
      version: versionOut.trim(),
      models
    };
  } catch {
    return { running: false };
  }
});

// Получение статуса системы
ipcMain.handle('get-system-status', getSystemStatus);

// Запуск тестов
ipcMain.handle('run-tests', async (event, projectPath) => {
  return new Promise((resolve) => {
    const process = spawn('npm', ['test'], {
      cwd: path.join(__dirname, '..'),
      shell: true
    });

    let output = '';

    process.stdout.on('data', (data) => {
      output += data.toString();
      mainWindow.webContents.send('test-output', data.toString());
    });

    process.stderr.on('data', (data) => {
      output += data.toString();
      mainWindow.webContents.send('test-output', data.toString());
    });

    process.on('close', (code) => {
      resolve({
        success: code === 0,
        output
      });
    });
  });
});
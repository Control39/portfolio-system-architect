const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { exec } = require('child_process');
const fs = require('fs-extra');
const path = require('path');
const os = require('os');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Статические файлы
app.use(express.static(path.join(__dirname, '../monitor-public')));

// API для статуса
app.get('/api/status', async (req, res) => {
  const status = await getSystemStatus();
  res.json(status);
});

// Веб-интерфейс
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>AI Config Monitor</title>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
      <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #1e1e1e;
          color: #fff;
          margin: 0;
          padding: 20px;
        }
        .container {
          max-width: 1200px;
          margin: 0 auto;
        }
        .header {
          background: #2d2d2d;
          padding: 20px;
          border-radius: 10px;
          margin-bottom: 20px;
        }
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin-bottom: 20px;
        }
        .card {
          background: #2d2d2d;
          border-radius: 10px;
          padding: 20px;
        }
        .card h3 {
          margin-top: 0;
          color: #007acc;
        }
        .status-indicator {
          display: inline-block;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          margin-right: 8px;
        }
        .online { background: #2ecc71; }
        .offline { background: #e74c3c; }
        .warning { background: #f1c40f; }
        table {
          width: 100%;
          border-collapse: collapse;
        }
        td {
          padding: 8px;
          border-bottom: 1px solid #404040;
        }
        .monospace {
          font-family: 'Consolas', monospace;
          font-size: 12px;
        }
        .chart-container {
          height: 300px;
          margin-bottom: 20px;
        }
        .log {
          background: #1e1e1e;
          border: 1px solid #404040;
          border-radius: 5px;
          padding: 10px;
          height: 200px;
          overflow-y: auto;
          font-family: 'Consolas', monospace;
          font-size: 12px;
        }
        .log-entry {
          margin: 2px 0;
          color: #a0a0a0;
        }
        .log-entry.error { color: #e74c3c; }
        .log-entry.success { color: #2ecc71; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>📊 AI Config Monitor</h1>
          <p>Реальное время: <span id="timestamp">-</span></p>
        </div>
        
        <div class="stats-grid">
          <div class="card">
            <h3>🤖 Ollama</h3>
            <div id="ollama-status">
              <span class="status-indicator offline"></span>
              Проверка...
            </div>
            <div id="models-list"></div>
          </div>
          
          <div class="card">
            <h3>📁 Конфиги</h3>
            <div id="configs-status"></div>
          </div>
          
          <div class="card">
            <h3>💾 Память</h3>
            <div class="chart-container">
              <canvas id="memoryChart"></canvas>
            </div>
          </div>
        </div>
        
        <div class="card">
          <h3>📈 Метрики</h3>
          <div class="chart-container">
            <canvas id="metricsChart"></canvas>
          </div>
        </div>
        
        <div class="card">
          <h3>📋 Лог</h3>
          <div class="log" id="log"></div>
        </div>
      </div>
      
      <script>
        const socket = io();
        let memoryChart, metricsChart;
        
        function initCharts() {
          const memCtx = document.getElementById('memoryChart').getContext('2d');
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
          
          const metCtx = document.getElementById('metricsChart').getContext('2d');
          metricsChart = new Chart(metCtx, {
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
        }
        
        function addLog(message, type = 'info') {
          const log = document.getElementById('log');
          const entry = document.createElement('div');
          entry.className = 'log-entry ' + type;
          entry.textContent = '[' + new Date().toLocaleTimeString() + '] ' + message;
          log.appendChild(entry);
          log.scrollTop = log.scrollHeight;
          
          if (log.children.length > 100) {
            log.removeChild(log.firstChild);
          }
        }
        
        socket.on('connect', () => {
          addLog('✅ Подключено к серверу', 'success');
        });
        
        socket.on('status-update', (status) => {
          document.getElementById('timestamp').textContent = new Date(status.timestamp).toLocaleString();
          
          // Ollama статус
          const ollamaDiv = document.getElementById('ollama-status');
          if (status.ollama.running) {
            ollamaDiv.innerHTML = \`
              <span class="status-indicator online"></span>
              Работает (версия: \${status.ollama.version || '?'})
            \`;
          } else {
            ollamaDiv.innerHTML = '<span class="status-indicator offline"></span> Не запущен';
          }
          
          // Список моделей
          const modelsList = document.getElementById('models-list');
          if (status.ollama.models.length > 0) {
            modelsList.innerHTML = '<h4>Модели:</h4>' + 
              status.ollama.models.map(m => 
                '<div>📦 ' + m.name + ' <span style="color:#888">(' + m.size + ')</span></div>'
              ).join('');
          } else {
            modelsList.innerHTML = '<div style="color:#888">Нет моделей</div>';
          }
          
          // Конфиги
          const configsDiv = document.getElementById('configs-status');
          let configsHtml = '<table>';
          for (const [name, info] of Object.entries(status.configs)) {
            configsHtml += \`
              <tr>
                <td>\${name}</td>
                <td>\${info.exists ? '✅' : '❌'}</td>
                <td class="monospace">\${info.exists ? (info.size/1024).toFixed(0) + 'KB' : '-'}</td>
              </tr>
            \`;
          }
          configsHtml += '</table>';
          configsDiv.innerHTML = configsHtml;
          
          // График памяти
          if (memoryChart && status.memory) {
            const used = status.memory.heapUsed / 1024 / 1024;
            const total = status.memory.heapTotal / 1024 / 1024;
            memoryChart.data.datasets[0].data = [used, total - used];
            memoryChart.update();
          }
          
          // График метрик
          if (metricsChart) {
            const time = new Date().toLocaleTimeString();
            metricsChart.data.labels.push(time);
            metricsChart.data.datasets[0].data.push(Math.random() * 10);
            if (metricsChart.data.labels.length > 20) {
              metricsChart.data.labels.shift();
              metricsChart.data.datasets[0].data.shift();
            }
            metricsChart.update();
          }
        });
        
        initCharts();
        addLog('📊 Мониторинг запущен', 'success');
      </script>
    </body>
    </html>
  `);
});

// ============================================================================
// ПОЛУЧЕНИЕ СТАТУСА
// ============================================================================
async function getSystemStatus() {
  const status = {
    timestamp: new Date().toISOString(),
    ollama: { running: false, models: [], version: null },
    configs: {},
    memory: process.memoryUsage(),
    uptime: process.uptime(),
    system: {
      platform: os.platform(),
      hostname: os.hostname(),
      cpus: os.cpus().length,
      memory: os.totalmem()
    }
  };
  
  // Проверка Ollama
  try {
    const { stdout: versionOut } = await execPromise('ollama --version');
    status.ollama.version = versionOut.trim();
    
    const { stdout: listOut } = await execPromise('ollama list');
    status.ollama.running = true;
    status.ollama.models = listOut.split('\n')
      .filter(line => line.includes(':'))
      .map(line => {
        const parts = line.split(/\s+/);
        return { name: parts[0], size: parts[2] + ' ' + (parts[3] || '') };
      });
  } catch {
    status.ollama.running = false;
  }
  
  // Проверка конфигов
  const projectPath = path.join(__dirname, '../..');
  const configs = [
    { name: 'Continue', path: path.join(process.env.USERPROFILE || process.env.HOME, '.continue', 'config.json') },
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
// ЗАПУСК
// ============================================================================
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`📊 Мониторинг запущен на http://localhost:${PORT}`);
});

// WebSocket обновления
setInterval(async () => {
  const status = await getSystemStatus();
  io.emit('status-update', status);
}, 5000);
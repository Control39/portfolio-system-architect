# Package

- **Путь**: `07_TOOLS\.ai-config-gui\package.json`
- **Тип**: .JSON
- **Размер**: 1,502 байт
- **Последнее изменение**: 2026-03-12 21:04:03

## Превью

```
{
  "name": "ai-config-gui",
  "version": "1.0.0",
  "description": "Графический интерфейс для управления AI-конфигами",
  "main": "src/main/index.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "dev": "electron . --debug",
    "test": "jest",
    "test:watch": "jest --watch",
    "monitor": "node scripts/monitor.js",
    "monitor:watch": "nodemon --watch ../.ai-config/master-config.yaml --exec 'node scripts/monitor.js'"
  },
  "dependencies": {
    "electron"
... (файл продолжается)
```

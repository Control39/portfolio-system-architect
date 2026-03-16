# Examples Arch Compass Developer Example

- **Путь**: `docs\obsidian-map\examples_arch-compass_developer-example.md`
- **Тип**: .MD
- **Размер**: 941 байт
- **Последнее изменение**: 2026-03-12 11:24:56

## Превью

```
# Developer Example

- **Путь**: `examples\arch-compass\developer-example.md`
- **Тип**: .MD
- **Размер**: 912 байт
- **Последнее изменение**: 2026-03-11 18:53:50

## Превью

```
## Arch-Compass: Пример для разработчика

### Задача
Добавить новый плагин для интеграции с Kubernetes.

### Действие
1. Создать модуль в `components/arch-compass-framework/src/plugins/k8s_integration.py`
2. Реализовать интерфейс `IArchPlugin`:
   ```python
   class K8sPlugin(IArchPlugin):
       def generate_manifests(
... (файл продолжается)
```

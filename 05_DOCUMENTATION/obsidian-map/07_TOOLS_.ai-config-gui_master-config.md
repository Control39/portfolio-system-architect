# Master Config

- **Путь**: `07_TOOLS\.ai-config-gui\master-config.yaml`
- **Тип**: .YAML
- **Размер**: 272 байт
- **Последнее изменение**: 2026-03-12 18:11:48

## Превью

```


- id: huggingface-llama
  name: Llama 3 (Hugging Face)
  provider:
    type: huggingface
    model: meta-llama/Meta-Llama-3-8B
    auth:
      keyEnv: HUGGINGFACE_API_KEY
  capabilities:
    context: 8192
    maxTokens: 2048
  defaults:
    temperature: 0.3
```

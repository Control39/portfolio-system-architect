# AI Integrations Module
# GigaChat, Ollama, LangChain и другие LLM интеграции

# Ленивый импорт тяжёлых LLM-зависимостей:
# чтобы простые импорты shared-config (например src.ai.config.*)
# не падали из-за отсутствующих optional-зависимостей.
try:
    from .gigachat_bridge import GigaChainSettings, GigaMCPBridge

    __all__ = ["GigaMCPBridge", "GigaChainSettings"]
except Exception:
    __all__ = []

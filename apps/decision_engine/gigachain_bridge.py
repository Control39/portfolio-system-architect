#!/usr/bin/env python3
"""GigaChain Bridge for Think MCP Integration.
Integrates GigaChat API with it-compass context and Chroma RAG.
Self-Improving Loop stub included.
"""


from dotenv import load_dotenv

# Langchain 1.x совместимость
try:
    from langchain.prompts import PromptTemplate
except ImportError:
    from langchain_core.prompts import PromptTemplate

try:
    from langchain_community.llms import GigaChat
except ImportError:
    try:
        from langchain_gigachat import GigaChat
    except ImportError:
        GigaChat = None  # Fallback для тестирования
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


load_dotenv()


class GigaChainSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore", env_file=".env")
    gigachat_api_key: str = ""
    chroma_path: str = "./chroma_db"
    mcp_url: str = "http://localhost:8000/mcp"


class GigaMCPBridge:
    def __init__(self, settings: GigaChainSettings = GigaChainSettings()):
        self.settings = settings
        if GigaChat is None:
            raise RuntimeError(
                "GigaChat не доступен. Установите langchain-community или langchain-gigachat "
                "и настройте GIGACHAT_API_KEY в .env"
            )
        self.llm = GigaChat(
            api_key=settings.gigachat_api_key,
            model="gigachat:latest",
            verify_ssl=False,
        )
        self.prompt = PromptTemplate(
            input_variables=["context", "query"],
            template=("Context from MCP/it-compass: {{context}}\nQuery: {{query}}\nRespond with CoT:"),
        )
        self.chain = self.prompt | self.llm

    def giga_request(self, query: str, mcp_history: list | None = None) -> dict:
        """Giga-Request with session context (Step 2). Cross-Check stub."""
        if mcp_history is None:
            mcp_history = []
        context = "\\n".join([h.get("content", "") for h in mcp_history[-5:]])  # Last 5
        response = self.chain.invoke({"context": context, "query": query}).content

        trace = {"input": query, "context": context, "output": response}
        verified = self.verify_inference(trace)  # Step 3
        return {"response": response, "trace": trace, "verified": verified}

    def verify_inference(self, trace: dict) -> bool:
        """Inferences-verification (mock; integrate it-compass). Accuracy metric."""
        # Stub: >90% pass target
        return len(trace["output"]) > 50  # Placeholder

    def self_improve(self, traces: list) -> str:
        """Self-Improving Loop (Step 5). Analyze quality, suggest prompt fixes."""
        avg_len = sum(len(t["output"]) for t in traces) / len(traces)
        return f"Improve: Avg response len {avg_len:.1f}. Add more CoT if <100."


# Metrics stubs (Step 7)
def measure_latency(func, *args, **kwargs):
    import time

    start = time.time()
    result = func(*args, **kwargs)
    return result, time.time() - start  # Target <3s


if __name__ == "__main__":
    bridge = GigaMCPBridge()
    resp = bridge.giga_request("Explain RAG integration.")
    print(resp)

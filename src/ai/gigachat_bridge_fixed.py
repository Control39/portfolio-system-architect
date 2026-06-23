#!/usr/bin/env python3
"""GigaChain Bridge for Think MCP Integration - FIXED VERSION.
Integrates GigaChat API with it-compass context and Chroma RAG.
Self-Improving Loop stub included.
"""

import os
from typing import Any

# Отключаем проверку SSL для корпоративной среды (MITM-прокси)
os.environ["REQUESTS_CA_BUNDLE"] = ""
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["PYTHONHTTPSVERIFY"] = "0"

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()


class GigaChainSettings(BaseSettings):
    """Настройки для GigaChat Bridge"""

    model_config = ConfigDict(extra="ignore", env_file=".env")

    gigachat_api_key: str = ""
    gigachat_client_id: str = ""
    gigachat_client_secret: str = ""
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_api_url: str = "https://gigachat.devices.sberbank.ru/api/v1"
    gigachat_auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    chroma_path: str = "./chroma_db"
    mcp_url: str = "http://localhost:8000/mcp"


class GigaMCPBridge:
    """Мост для работы с GigaChat API с поддержкой LangChain"""

    def __init__(self, settings: GigaChainSettings | None = None):
        self.settings = settings or GigaChainSettings()
        self.llm = None
        self.prompt = None
        self.chain = None

        # Инициализируем LLM
        self._init_llm()

    def _init_llm(self):
        """Инициализация GigaChat с правильными параметрами"""

        # Пробуем разные варианты импорта

        # Вариант 1: langchain-gigachat (рекомендуемый)
        try:
            from langchain_gigachat import GigaChat

            print("✅ Использую langchain_gigachat.GigaChat")
        except ImportError:
            pass

        # Вариант 2: langchain_community (старый)
        if GigaChat is None:
            try:
                from langchain_community.llms import GigaChat

                print("✅ Использую langchain_community.llms.GigaChat")
            except ImportError:
                pass

        # Вариант 3: прямая работа через gigachat (fallback)
        if GigaChat is None:
            print("⚠️ LangChain GigaChat не найден, использую прямую работу с gigachat")
            self._init_direct_gigachat()
            return

        # Создаём HTTP клиент с отключённой SSL проверкой
        import httpx

        http_client = httpx.Client(
            verify=False,  # Отключаем SSL для корпоративного прокси
            timeout=httpx.Timeout(60.0, connect=10.0),
        )

        # Определяем credentials (приоритет: api_key > client_id+secret)
        credentials = self.settings.gigachat_api_key
        if not credentials and self.settings.gigachat_client_id:
            credentials = self.settings.gigachat_client_secret
            print("⚠️ Использую client_secret как credentials (OAuth2)")

        # Инициализация GigaChat
        try:
            self.llm = GigaChat(
                credentials=credentials,  # Важно: credentials, а не api_key!
                scope=self.settings.gigachat_scope,
                model="GigaChat",  # Правильное имя модели
                temperature=0.7,
                max_tokens=2000,
                timeout=60,
                http_client=http_client,
                verify_ssl=False,  # Дополнительная страховка
            )
            print("✅ GigaChat инициализирован успешно")
        except TypeError as e:
            # Fallback для старых версий
            if "unexpected keyword argument" in str(e):
                print("⚠️ Старая версия GigaChat, пробую без http_client...")
                self.llm = GigaChat(
                    credentials=credentials,
                    scope=self.settings.gigachat_scope,
                    model="GigaChat",
                    verify_ssl=False,
                )
            else:
                raise

        # Создаём промпт (исправленный: одиночные фигурные скобки)
        from langchain_core.prompts import PromptTemplate

        self.prompt = PromptTemplate(
            input_variables=["context", "query"],
            template=("Context from MCP/it-compass: {context}\nQuery: {query}\nRespond with Chain of Thought (CoT):"),
        )

        # Создаём цепочку
        from langchain_core.output_parsers import StrOutputParser

        self.chain = self.prompt | self.llm | StrOutputParser()

    def _init_direct_gigachat(self):
        """Прямая работа с gigachat (без LangChain)"""
        import httpx
        from gigachat import GigaChat

        # Определяем credentials
        credentials = self.settings.gigachat_api_key
        if not credentials and self.settings.gigachat_client_secret:
            credentials = self.settings.gigachat_client_secret

        # Создаём HTTP клиент
        http_client = httpx.Client(verify=False, timeout=60.0)

        # Инициализируем клиент
        self.direct_client = GigaChat(
            credentials=credentials,
            scope=self.settings.gigachat_scope,
            model="GigaChat",
            http_client=http_client,
            verify_ssl=False,
        )
        self.use_direct = True

        print("✅ Прямой GigaChat клиент инициализирован")

    def giga_request(self, query: str, mcp_history: list[dict] | None = None) -> dict[str, Any]:
        """Giga-Request with session context."""
        if mcp_history is None:
            mcp_history = []

        # Берём последние 5 сообщений из истории
        context = "\n".join([h.get("content", "") for h in mcp_history[-5:]])

        # Выбираем способ запроса
        if hasattr(self, "use_direct") and self.use_direct:
            response = self._direct_request(query, context)
        else:
            response = self._langchain_request(query, context)

        trace = {"input": query, "context": context, "output": response, "timestamp": __import__("time").time()}

        verified = self.verify_inference(trace)

        return {"response": response, "trace": trace, "verified": verified}

    def _langchain_request(self, query: str, context: str) -> str:
        """Запрос через LangChain"""
        try:
            response = self.chain.invoke({"context": context, "query": query})
            return response
        except Exception as e:
            error_msg = f"Ошибка LangChain запроса: {e}"
            print(error_msg)
            return error_msg

    def _direct_request(self, query: str, context: str) -> str:
        """Запрос напрямую через gigachat"""
        from gigachat.models import Chat, MessageRole, Messages

        try:
            messages = []
            if context:
                messages.append(Messages(role=MessageRole.SYSTEM, content=f"Контекст: {context}"))

            messages.append(Messages(role=MessageRole.USER, content=query))

            payload = Chat(
                messages=messages,
                model="GigaChat",
                temperature=0.7,
                max_tokens=2000,
            )

            response = self.direct_client.chat(payload)

            if response.choices:
                return response.choices[0].message.content
            return "Нет ответа от модели"

        except Exception as e:
            error_msg = f"Ошибка прямого запроса: {e}"
            print(error_msg)
            return error_msg

    def verify_inference(self, trace: dict) -> bool:
        """Inferences-verification (mock; integrate it-compass)."""
        # Улучшенная проверка
        output = trace.get("output", "")

        # Проверяем минимальную осмысленность
        if len(output) < 20:
            return False

        # Проверяем, что ответ не содержит ошибку
        return not ("ошибка" in output.lower() or "error" in output.lower())

    def self_improve(self, traces: list[dict]) -> str:
        """Self-Improving Loop."""
        if not traces:
            return "Нет данных для улучшения"

        avg_len = sum(len(t.get("output", "")) for t in traces) / len(traces)
        verified_count = sum(1 for t in traces if t.get("verified", False))
        verified_pct = (verified_count / len(traces)) * 100

        suggestions = []

        if avg_len < 100:
            suggestions.append("Увеличить минимальную длину ответа")
        if verified_pct < 90:
            suggestions.append("Улучшить точность верификации")

        return (
            f"Self-Improvement Report:\n"
            f"- Avg response length: {avg_len:.1f}\n"
            f"- Verified: {verified_pct:.1f}%\n"
            f"- Suggestions: {', '.join(suggestions) if suggestions else 'None, keep current'}"
        )


# Metrics stubs
def measure_latency(func, *args, **kwargs):
    import time

    start = time.time()
    result = func(*args, **kwargs)
    latency = time.time() - start
    print(f"⏱️ Latency: {latency:.2f}s (target <3s)")
    return result, latency


if __name__ == "__main__":
    print("=" * 50)
    print("GigaChat Bridge Test")
    print("=" * 50)

    # Инициализация
    bridge = GigaMCPBridge()

    # Тестовый запрос с замером времени
    resp, latency = measure_latency(bridge.giga_request, "Explain RAG integration in one sentence.")

    print(f"\n📝 Response: {resp['response']}")
    print(f"✅ Verified: {resp['verified']}")
    print(f"📊 Trace: {resp['trace']}")

#!/usr/bin/env python3
"""
Ollama Agent - с быстрой моделью qwen2.5-coder:3b
"""

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    print("❌ pip install requests")
    sys.exit(1)


class OllamaAgent:
    def __init__(self, model: str = "qwen2.5-coder:3b"):  # ⚡ Используем 3b (быстрее)
        self.model = model
        self.ollama_url = "http://localhost:11434"
        self.project_path = REPO_ROOT
        self.agent_id = f"agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        logger.info(f"🚀 Agent: {self.agent_id}")
        logger.info(f"🤖 Model: {self.model}")
        logger.info(f"📁 Project: {self.project_path}")

        # Проверяем Ollama
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                logger.info(f"✅ Ollama OK. Models: {models}")
                if self.model not in models:
                    logger.warning(f"⚠️ Model {self.model} not found, using {models[0] if models else 'llama3'}")
                    self.model = models[0] if models else "llama3:latest"
        except Exception as e:
            logger.error(f"❌ Ollama not available: {e}")

    def ask(self, prompt: str) -> str | None:
        """Запрос к Ollama с увеличенным таймаутом"""
        try:
            logger.info("⏳ Waiting for AI response... (max 120s)")
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2,  # Меньше случайности = быстрее
                    "max_tokens": 500,  # Ограничиваем ответ
                    "num_predict": 500,  # Альтернативный параметр
                },
                timeout=120,  # Увеличили до 120 секунд
            )
            if response.status_code == 200:
                result = response.json().get("response", "")
                logger.info(f"✅ Response received ({len(result)} chars)")
                return result
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            logger.error("⏰ Timeout! Попробуйте модель поменьше: qwen2.5-coder:3b")
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    def analyze_code(self, code: str, max_len: int = 2000) -> dict:
        """Анализ кода через AI (сокращенный промпт)"""
        # Обрезаем код
        if len(code) > max_len:
            code = code[:max_len] + "\n... (обрезано)"

        prompt = f"""
        Кратко проанализируй Python код. Найди проблемы и улучшения.

        Код:
        {code}

        Ответь JSON:
        {{"issues": ["проблема1", "проблема2"], "improvements": ["улучшение1"], "summary": "кратко"}}
        """

        response = self.ask(prompt)
        if response:
            # Ищем JSON
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return {"raw": response[:300], "summary": "См. raw"}
        return {"error": "No response"}

    def self_improve(self) -> dict:
        """Саморазвитие"""
        logger.info("🧬 Self-improvement...")

        # Анализируем сам агент (небольшую часть)
        agent_file = Path(__file__)
        with open(agent_file, encoding="utf-8") as f:
            code = f.read()

        logger.info("📝 Analyzing self...")
        self_analysis = self.analyze_code(code, max_len=1500)

        # Анализируем несколько файлов проекта
        python_files = []
        for f in self.project_path.rglob("*.py"):
            if not any(p in str(f) for p in [".venv", "__pycache__", ".git", "site-packages"]):
                if f.stat().st_size > 200 and f.stat().st_size < 50000:
                    python_files.append(f)

        logger.info(f"📁 Found {len(python_files)} Python files")

        # Анализируем первые 3 файла
        file_analyses = []
        for f in python_files[:3]:
            try:
                with open(f, encoding="utf-8") as fp:
                    content = fp.read()
                if len(content) > 100:
                    logger.info(f"   Analyzing: {f.name}")
                    result = self.analyze_code(content, max_len=1500)
                    file_analyses.append({"file": str(f.relative_to(self.project_path)), "analysis": result})
            except Exception as e:
                logger.warning(f"   Skip {f.name}: {e}")

        results = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "model": self.model,
            "self_analysis": self_analysis,
            "project_analysis": file_analyses,
            "status": "completed",
        }

        # Сохраняем
        result_file = REPO_ROOT / "logs" / "ollama_analysis.json"
        result_file.parent.mkdir(parents=True, exist_ok=True)
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Вывод
        print("\n" + "=" * 70)
        print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА")
        print("=" * 70)
        print(f"🤖 Модель: {self.model}")
        print(f"📁 Проанализировано: {len(file_analyses)} файлов")

        # Вывод самоанализа
        sa = self_analysis
        if sa.get("summary"):
            print(f"\n📝 О себе: {sa['summary']}")

        issues = sa.get("issues", [])
        if issues:
            print(f"\n🐛 Найдено проблем: {len(issues)}")
            for issue in issues[:3]:
                print(f"   - {issue}")

        improvements = sa.get("improvements", [])
        if improvements:
            print(f"\n💡 Улучшений: {len(improvements)}")
            for imp in improvements[:3]:
                print(f"   - {imp}")

        # Показываем результаты по файлам
        if file_analyses:
            print("\n📄 Анализ файлов:")
            for fa in file_analyses[:2]:
                analysis = fa.get("analysis", {})
                if analysis.get("issues") or analysis.get("improvements"):
                    print(f"\n   📄 {fa['file']}:")
                    for issue in analysis.get("issues", [])[:2]:
                        print(f"      🐛 {issue}")
                    for imp in analysis.get("improvements", [])[:2]:
                        print(f"      💡 {imp}")

        print(f"\n📄 Полные результаты: {result_file}")
        print("=" * 70)

        return results


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║  ⚡ OLLAMA AGENT (БЫСТРАЯ МОДЕЛЬ 3B)                      ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Используем быструю модель 3b
    agent = OllamaAgent(model="qwen2.5-coder:3b")
    results = agent.self_improve()
    print("\n✅ Done!")

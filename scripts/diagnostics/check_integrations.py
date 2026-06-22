# check_integrations.py
"""
Проверка интеграций ChromaDB и Job Agent
"""

from agents.cognitive_agent.autonomous_agent import get_agent


def check_integrations():
    agent = get_agent()

    print("🔍 ПРОВЕРКА ИНТЕГРАЦИЙ")
    print("=" * 50)

    # 1. Проверяем ChromaDB
    print("\n📚 CHROMADB:")
    print(f"  - chroma_available: {getattr(agent, 'chroma_available', False)}")
    print(f"  - chroma_indexer: {getattr(agent, 'chroma_indexer', None)}")
    print(f"  - index_project_documents: {hasattr(agent, 'index_project_documents')}")
    print(f"  - search_similar_documents: {hasattr(agent, 'search_similar_documents')}")

    # 2. Проверяем Job Agent
    print("\n💼 JOB AGENT:")
    print(f"  - job_agent_available: {getattr(agent, 'job_agent_available', False)}")
    print(f"  - analyze_job_requirements: {hasattr(agent, 'analyze_job_requirements')}")
    print(f"  - generate_optimized_resume: {hasattr(agent, 'generate_optimized_resume')}")
    print(f"  - search_job_automated: {hasattr(agent, 'search_job_automated')}")

    # 3. Проверяем быстрые методы
    print("\n🚀 БЫСТРЫЕ МЕТОДЫ:")
    print(f"  - quick_fix_bug: {hasattr(agent, 'quick_fix_bug')}")
    print(f"  - quick_refactor: {hasattr(agent, 'quick_refactor')}")
    print(f"  - quick_feature: {hasattr(agent, 'quick_feature')}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    check_integrations()

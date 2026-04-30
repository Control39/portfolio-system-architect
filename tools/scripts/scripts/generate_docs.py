from ..config.loader import COMPONENT_CONFIG


def generate_api_docs():
    """Генерирует документацию API на основе конфигурации."""
    docs = f"# {COMPONENT_CONFIG['component']['name']}\n\n"
    docs += f"**Версия:** {COMPONENT_CONFIG['component']['version']}\n\n"
    docs += "## Эндпоинты\n\n"

    for endpoint in COMPONENT_CONFIG["endpoints"]:
        docs += f"### {endpoint['method']} {endpoint['path']}\n"
        docs += f"{endpoint['description']}\n\n"

        if "parameters" in endpoint:
            docs += "**Параметры:**\n"
            for param in endpoint["parameters"]:
                docs += (
                    f"- `{param['name']}` ({param['type']}): {param['description']}\n"
                )
            docs += "\n"

    # Сохраняем в файл
    with open("docs/API_REFERENCE.md", "w", encoding="utf-8") as f:
        f.write(docs)

    print("✅ Документация сгенерирована: docs/API_REFERENCE.md")


generate_api_docs()

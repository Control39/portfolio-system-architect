from apps.knowledge_graph.src.config_integration import get_config

c = get_config()
print("Методы:", [m for m in dir(c) if not m.startswith("_")])
print("Тип:", type(c))
print("Is dict?", isinstance(c, dict))
if hasattr(c, "model_dump"):
    print("model_dump:", c.model_dump())
elif hasattr(c, "dict"):
    print("dict:", c.dict())

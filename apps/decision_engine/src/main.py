# apps/decision_engine/src/main.py
from fastapi import FastAPI

from src.config.client import ConfigClient  # ← Вот наш клиент

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("🚀decision_engine стартует...")

    # Создаём клиент
    client = ConfigClient(service_name="decision_engine")

    # Получаем конфиг
    try:
        config = await client.get_config()
        print(f"✅ Конфиг загружен: {config}")

        # Можно даже сохранить его в переменную для дальнейшего использования
        app.state.config = config

    except Exception as e:
        print(f"❌ Ошибка при загрузке конфига: {e}")
        # Здесь можно сделать fallback — например, загрузить дефолтный YAML

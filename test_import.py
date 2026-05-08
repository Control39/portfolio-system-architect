try:
    from python_server.core.room_store.memory import InMemoryRoomStore

    print("✅ Импорт InMemoryRoomStore прошёл успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Неизвестная ошибка: {e}")

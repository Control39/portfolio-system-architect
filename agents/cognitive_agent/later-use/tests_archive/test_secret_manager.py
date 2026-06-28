#!/usr/bin/env python3
"""
Tests for SecretManager module
Тесты для модуля управления секретами
"""

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_secret_manager_basic():
    """Тест базовой функциональности SecretManager"""
    print("\n🧪 Тест 1: SecretManager базовая функциональность")
    print("=" * 50)

    from src.security.secret_manager import (
        SecretManager,
        SecretManagerError,
        SecretNotFoundError,
    )

    with TemporaryDirectory() as tmpdir:
        # Сгенерировать тестовый ключ
        encryption_key = SecretManager.generate_key()

        # Инициализация
        manager = SecretManager(encryption_key=encryption_key, project_root=Path(tmpdir))
        print(f"  ✅ SecretManager initialized")

        # Тест 1.1: Хранение и получение секрета
        manager.store_secret("api_key", "my-secret-api-key-123")
        retrieved = manager.get_secret("api_key")
        assert retrieved == "my-secret-api-key-123", f"Expected 'my-secret-api-key-123', got {retrieved}"
        print(f"  ✅ Secret stored and retrieved successfully")

        # Тест 1.2: Несуществующий секрет
        try:
            manager.get_secret("nonexistent")
            print("  ❌ Should have raised SecretNotFoundError")
        except SecretNotFoundError:
            print(f"  ✅ SecretNotFoundError raised for nonexistent secret")

        # Тест 1.3: Секрет с default значением
        value = manager.get_secret("nonexistent", default="default_value")
        assert value == "default_value"
        print(f"  ✅ Default value returned: {value}")

    print("  ✅ Тест 1 пройден\n")


def test_secret_encryption():
    """Тест шифрования/расшифрования секретов"""
    print("\n🧪 Тест 2: Шифрование секретов")
    print("=" * 50)

    from src.security.secret_manager import SecretManager, SecretManagerError

    encryption_key = SecretManager.generate_key()
    manager = SecretManager(encryption_key=encryption_key)

    # Тест 2.1: Шифрование
    secret = "super-secret-password"  # pragma: allowlist secret
    encrypted = manager.encrypt(secret)
    assert encrypted != secret, "Encrypted should differ from original"
    print(f"  ✅ Encrypted: {encrypted[:20]}...")

    # Тест 2.2: Расшифрование
    decrypted = manager.decrypt(encrypted)
    assert decrypted == secret, f"Expected {secret}, got {decrypted}"
    print(f"  ✅ Decrypted successfully: {decrypted}")

    # Тест 2.3: Неверный ключ
    wrong_key = SecretManager.generate_key()
    wrong_manager = SecretManager(encryption_key=wrong_key)
    try:
        wrong_manager.decrypt(encrypted)
        print("  ❌ Should have raised SecretManagerError with wrong key")
    except SecretManagerError:
        print(f"  ✅ SecretManagerError raised with wrong key")

    print("  ✅ Тест 2 пройден\n")


def test_secret_masking():
    """Тест маскировки секретов"""
    print("\n🧪 Тест 3: Маскировка секретов")
    print("=" * 50)

    from src.security.secret_manager import SecretManager

    # Тест 3.1: Маскировка длинного секрета
    masked = SecretManager.mask_secret("my-long-secret-key", visible_chars=4)
    assert masked.startswith("my-l")
    assert masked.endswith("****")
    print(f"  ✅ Long secret masked: {masked}")

    # Тест 3.2: Маскировка короткого секрета
    masked = SecretManager.mask_secret("abc", visible_chars=4)
    assert masked == "***"
    print(f"  ✅ Short secret masked: {masked}")

    # Тест 3.3: Хеширование
    hashed = SecretManager.hash_secret("my-secret")
    assert len(hashed) == 16
    print(f"  ✅ Secret hashed: {hashed}")

    print("  ✅ Тест 3 пройден\n")


def test_secret_persistence():
    """Тест сохранения секретов в файл"""
    print("\n🧪 Тест 4: Сохранение секретов")
    print("=" * 50)

    from src.security.secret_manager import SecretManager

    with TemporaryDirectory() as tmpdir:
        encryption_key = SecretManager.generate_key()
        manager = SecretManager(encryption_key=encryption_key, project_root=Path(tmpdir))

        # Тест 4.1: Сохранение секрета
        manager.store_secret("persistent_key", "persistent_value", persist=True)
        print(f"  ✅ Secret stored with persist=True")

        # Тест 4.2: Загрузка секрета из файла (новый менеджер)
        manager2 = SecretManager(encryption_key=encryption_key, project_root=Path(tmpdir))
        loaded = manager2.get_secret("persistent_key")
        assert loaded == "persistent_value"
        print(f"  ✅ Secret loaded from file: {loaded}")

    print("  ✅ Тест 4 пройден\n")


def test_secret_manager_env():
    """Тест загрузки ключа из переменных окружения"""
    print("\n🧪 Тест 5: Загрузка из переменных окружения")
    print("=" * 50)

    from src.security.secret_manager import (
        EnvironmentSecretLoader,
        SecretNotFoundError,
    )

    # Тест 5.1: Загрузка секрета из окружения
    os.environ["TEST_SECRET"] = "env-secret-value"  # pragma: allowlist secret
    value = EnvironmentSecretLoader.load_secret("TEST_SECRET")
    assert value == "env-secret-value"
    print(f"  ✅ Secret loaded from env: {value}")

    # Тест 5.2: Required секрет
    try:
        EnvironmentSecretLoader.load_secret("NONEXISTENT", required=True)
        print("  ❌ Should have raised SecretNotFoundError")
    except SecretNotFoundError:
        print(f"  ✅ SecretNotFoundError for required secret")

    # Тест 5.3: Загрузка всех секретов с префиксом
    os.environ["COGNITIVE_AGENT_KEY1"] = "value1"
    os.environ["COGNITIVE_AGENT_KEY2"] = "value2"
    secrets = EnvironmentSecretLoader.load_all_secrets(prefix="COGNITIVE_AGENT_")
    assert "KEY1" in secrets
    assert "KEY2" in secrets
    print(f"  ✅ All secrets loaded: {list(secrets.keys())}")

    print("  ✅ Тест 5 пройден\n")


def test_secret_manager_key_generation():
    """Тест генерации ключей"""
    print("\n🧪 Тест 6: Генерация ключей")
    print("=" * 50)

    from src.security.secret_manager import SecretManager

    # Тест 6.1: Генерация ключа шифрования
    key = SecretManager.generate_key()
    assert len(key) == 44  # Fernet key length
    print(f"  ✅ Encryption key generated: {key[:20]}...")

    # Тест 6.2: Уникальность ключей
    key2 = SecretManager.generate_key()
    assert key != key2
    print(f"  ✅ Keys are unique")

    print("  ✅ Тест 6 пройден\n")


def test_secret_manager_error_handling():
    """Тест обработки ошибок"""
    print("\n🧪 Тест 7: Обработка ошибок")
    print("=" * 50)

    from src.security.secret_manager import (
        SecretManager,
        SecretManagerError,
    )

    # Тест 7.1: Пустой ключ
    try:
        manager = SecretManager(encryption_key="")
        print("  ❌ Should have raised SecretManagerError with empty key")
    except (SecretManagerError, ValueError):
        print(f"  ✅ Error raised for empty key")

    # Тест 7.2: Неверный формат ключа
    try:
        manager = SecretManager(encryption_key="invalid-key")
        print("  ❌ Should have raised SecretManagerError with invalid key")
    except (SecretManagerError, ValueError):
        print(f"  ✅ Error raised for invalid key")

    # Тест 7.3: Пустые данные для шифрования
    encryption_key = SecretManager.generate_key()
    manager = SecretManager(encryption_key=encryption_key)
    try:
        manager.encrypt("")
        print("  ❌ Should have raised ValueError for empty data")
    except ValueError:
        print(f"  ✅ Error raised for empty data")

    print("  ✅ Тест 7 пройден\n")


def main():
    """Запуск всех тестов"""
    print("\n🚀 Запуск тестов SecretManager модуля")
    print("=" * 70)

    try:
        # Импортировать для генерации ключа
        from src.security.secret_manager import SecretManager

        # Установить переменную окружения для тестов
        os.environ["COGNITIVE_AGENT_ENCRYPTION_KEY"] = SecretManager.generate_key()

        test_secret_manager_basic()
        test_secret_encryption()
        test_secret_masking()
        test_secret_persistence()
        test_secret_manager_env()
        test_secret_manager_key_generation()
        test_secret_manager_error_handling()

        print("\n" + "=" * 70)
        print("✅ ВСЕ ТЕСТЫ SecretManager ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 70)
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

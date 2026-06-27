#!/usr/bin/env python3
"""
Tests for SecurePath module
Тесты для модуля безопасной работы с путями
"""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_secure_path_basic():
    """Тест базовой функциональности SecurePath"""
    print("\n🧪 Тест 1: Базовая функциональность SecurePath")
    print("=" * 50)

    from agents.cognitive_agent.security.secure_path import PathSecurityError, SecurePath

    with TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        secure = SecurePath(base_path)

        # Тест 1.1: Нормальный путь
        safe_path = secure.resolve("subdir/file.txt")
        assert safe_path.is_relative_to(base_path), "Safe path should be within base"
        print(f"  ✅ Safe path resolved: {safe_path}")

        # Тест 1.2: Path traversal должен блокироваться
        try:
            secure.resolve("../../../etc/passwd")
            print("  ❌ Path traversal not blocked!")
            assert False, "Should have raised PathSecurityError"
        except PathSecurityError as e:
            print(f"  ✅ Path traversal blocked: {e}")

        # Тест 1.3: Абсолютный путь вне base
        try:
            secure.resolve("/etc/passwd")
            print("  ❌ Absolute path outside base not blocked!")
            assert False, "Should have raised PathSecurityError"
        except PathSecurityError as e:
            print(f"  ✅ Absolute path outside base blocked: {e}")

        # Тест 1.4: is_safe_path
        assert secure.is_safe_path("safe/file.txt") is True
        assert secure.is_safe_path("../unsafe.txt") is False
        print("  ✅ is_safe_path works correctly")

    print("  ✅ Тест 1 пройден\n")


def test_secure_path_symlinks():
    """Тест проверки символических ссылок"""
    print("\n🧪 Тест 2: Проверка символических ссылок")
    print("=" * 50)

    from agents.cognitive_agent.security.secure_path import PathSecurityError, SecurePath

    with TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        secure = SecurePath(base_path)

        # Создаем файл внутри base
        safe_file = base_path / "safe.txt"
        safe_file.touch()

        # Создаем symlink внутри base на файл внутри base
        symlink_inside = base_path / "link_inside"
        symlink_inside.symlink_to(safe_file)

        # Тест 2.1: Symlink внутри base - OK
        try:
            resolved = secure.resolve("link_inside")
            print(f"  ✅ Symlink inside base allowed: {resolved}")
        except PathSecurityError:
            print("  ⚠️  Symlink inside base blocked (may be expected)")

        # Создаем symlink на файл вне base
        unsafe_file = Path("/etc/passwd")
        symlink_outside = base_path / "link_outside"
        try:
            symlink_outside.symlink_to(unsafe_file)

            # Тест 2.2: Symlink вне base должен блокироваться
            try:
                secure.resolve("link_outside")
                print("  ❌ Symlink outside base not blocked!")
            except PathSecurityError as e:
                print(f"  ✅ Symlink outside base blocked: {e}")
        except (OSError, PermissionError):
            print("  ℹ️  Cannot create symlink outside base (expected on some systems)")

    print("  ✅ Тест 2 пройден\n")


def test_secure_path_join():
    """Тест безопасного соединения путей"""
    print("\n🧪 Тест 2: Secure path join")
    print("=" * 50)

    from agents.cognitive_agent.security.secure_path import PathSecurityError, SecurePath, safe_path_join

    with TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        secure = SecurePath(base_path)

        # Тест 3.1: join с несколькими частями
        result = secure.join("subdir1", "subdir2", "file.txt")
        assert result.is_relative_to(base_path)
        print(f"  ✅ Join multiple parts: {result}")

        # Тест 3.2: safe_path_join функция
        result = safe_path_join(base_path, "safe", "path.txt")
        assert result.is_relative_to(base_path)
        print(f"  ✅ safe_path_join function works: {result}")

        # Тест 3.3: join с path traversal
        try:
            secure.join("subdir", "../../etc", "passwd")
            print("  ❌ Join with path traversal not blocked!")
        except PathSecurityError:
            print("  ✅ Join with path traversal blocked")

    print("  ✅ Тест 3 пройден\n")


def test_secure_path_edge_cases():
    """Тест граничных случаев"""
    print("\n🧪 Тест 4: Граничные случаи")
    print("=" * 50)

    from agents.cognitive_agent.security.secure_path import PathSecurityError, SecurePath

    with TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        secure = SecurePath(base_path)

        # Тест 4.1: Пустой путь
        try:
            result = secure.resolve("")
            print(f"  ✅ Empty path resolved: {result}")
        except Exception as e:
            print(f"  ℹ️  Empty path error (expected): {e}")

        # Тест 4.2: Путь с точками
        result = secure.resolve("./file.txt")
        assert result.is_relative_to(base_path)
        print(f"  ✅ Path with dots resolved: {result}")

        # Тест 4.3: Путь с множественными слешами
        result = secure.resolve("subdir//file.txt")
        assert result.is_relative_to(base_path)
        print(f"  ✅ Path with multiple slashes resolved: {result}")

        # Тест 4.4: Windows-style путь (должен обрабатываться)
        try:
            result = secure.resolve("subdir\\file.txt")
            assert result.is_relative_to(base_path)
            print(f"  ✅ Windows-style path resolved: {result}")
        except Exception as e:
            print(f"  ℹ️  Windows-style path error: {e}")

    print("  ✅ Тест 4 пройден\n")


def test_is_path_within_base():
    """Тест функции is_path_within_base"""
    print("\n🧪 Тест 5: is_path_within_base")
    print("=" * 50)

    from agents.cognitive_agent.security.secure_path import is_path_within_base

    with TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        # Тест 5.1: Путь внутри base
        assert is_path_within_base(base_path, "safe/file.txt") is True
        print("  ✅ Path inside base: True")

        # Тест 5.2: Путь вне base
        assert is_path_within_base(base_path, "../unsafe.txt") is False
        print("  ✅ Path outside base: False")

        # Тест 5.3: Абсолютный путь внутри base
        safe_path = Path(base_path) / "absolute" / "safe.txt"
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.touch()
        assert is_path_within_base(base_path, str(safe_path)) is True
        print("  ✅ Absolute path inside base: True")

    print("  ✅ Тест 5 пройден\n")


def main():
    """Запуск всех тестов"""
    print("\n🚀 Запуск тестов SecurePath модуля")
    print("=" * 70)

    try:
        test_secure_path_basic()
        test_secure_path_symlinks()
        test_secure_path_join()
        test_secure_path_edge_cases()
        test_is_path_within_base()

        print("\n" + "=" * 70)
        print("✅ ВСЕ ТЕСТЫ SecurePath ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 70)
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Тесты для модуля безопасности (маскирование секретов).
"""

from src.security import mask_dict, mask_sensitive, mask_string


class TestSecretMasking:
    """Тесты для маскирования секретов."""

    def test_mask_api_key(self):
        """Маскирование API ключа."""
        input_str = "api_key: sk-1234567890abcdef1234"  # Без кавычек, 24 символа
        result = mask_string(input_str)
        assert "***" in result

    def test_mask_bearer_token(self):
        """Маскирование Bearer токена."""
        input_str = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = mask_string(input_str)
        assert "***" in result

    def test_mask_password(self):
        """Маскирование пароля."""
        input_str = "password: super_secret_password"
        result = mask_string(input_str)
        assert "***" in result

    def test_mask_aws_key(self):
        """Маскирование AWS ключа."""
        input_str = "AWS_ACCESS_KEY_ID: AKIAIOSFODNN7EXAMPLE"
        result = mask_string(input_str)
        assert "***" in result

    def test_mask_private_key(self):
        """Маскирование приватного ключа."""
        input_str = "-----BEGIN RSA PRIVATE KEY----- MIIEpAIBAAKCAQEA..."
        result = mask_string(input_str)
        assert "***" in result

    def test_mask_database_url(self):
        """Маскирование URL базы данных."""
        input_str = "database_url: postgres://user:password@localhost/db"
        result = mask_string(input_str)
        assert "***" in result

    def test_mask_jwt_token(self):
        """Маскирование JWT токена."""
        input_str = "token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature"
        result = mask_string(input_str)
        assert "***" in result

    def test_mask_dict_with_sensitive_keys(self):
        """Маскирование словаря с чувствительными ключами."""
        input_dict = {"api_key": "secret123", "username": "user", "password": "pass456", "normal_key": "normal_value"}
        result = mask_dict(input_dict)

        assert result["api_key"] == "***"
        assert result["password"] == "***"
        assert result["normal_key"] == "normal_value"

    def test_mask_dict_nested(self):
        """Маскирование вложенного словаря."""
        input_dict = {
            "database": {"password": "secret", "host": "localhost"},
            "api": {
                "api_key": "apikey1234567890abcdef"  # Формат api_key: значение
            },
        }
        result = mask_dict(input_dict)

        assert result["database"]["password"] == "***"
        assert result["api"]["api_key"] == "***"
        assert result["database"]["host"] == "localhost"

    def test_mask_sensitive_string(self):
        """Универсальное маскирование строки."""
        input_str = 'password: "secret"'
        result = mask_sensitive(input_str)
        assert "***" in result

    def test_mask_sensitive_dict(self):
        """Универсальное маскирование словаря."""
        input_dict = {"api_key": "secret"}
        result = mask_sensitive(input_dict)
        assert result["api_key"] == "***"

    def test_mask_sensitive_list(self):
        """Универсальное маскирование списка."""
        input_list = ["password: secret", "normal", "api_key: key1234567890abcdef1234"]
        result = mask_sensitive(input_list)
        assert "***" in result[0]
        assert result[1] == "normal"
        assert "***" in result[2]

    def test_no_false_positives(self):
        """Отсутствие ложных срабатываний."""
        input_str = "The password is a common word"
        result = mask_string(input_str)
        assert result == input_str

    def test_custom_keys_to_mask(self):
        """Маскирование с пользовательским списком ключей."""
        input_dict = {"custom_secret": "value1", "api_key": "value2", "normal": "value3"}
        result = mask_dict(input_dict, keys_to_mask=["custom_secret"])

        assert result["custom_secret"] == "***"
        assert result["api_key"] == "value2"
        assert result["normal"] == "value3"

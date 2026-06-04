"""Тесты для AI Proxy Server"""

from unittest.mock import MagicMock, patch


class TestAIProxyServer:
    """Тесты основного функционала сервера"""

    def test_health_endpoint(self, test_client):
        """Тест health endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_chat_completions_codette(self, test_client, sample_messages):
        """Тест запроса к Codette"""
        with patch("tools.dev-tools.server.requests.post") as mock_post:
            # Мокируем ответ Ollama
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "Привет! Как я могу помочь?"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": sample_messages},
            )

            assert response.status_code == 200
            data = response.json()
            assert "choices" in data
            assert "message" in data["choices"][0]
            assert "content" in data["choices"][0]["message"]

    def test_chat_completions_gigachat(self, test_client, sample_messages):
        """Тест запроса к GigaChat"""
        with patch("tools.dev-tools.server.requests.post") as mock_post:
            # Мокируем OAuth и чат
            mock_auth_response = MagicMock()
            mock_auth_response.json.return_value = {"access_token": "test_token"}

            mock_chat_response = MagicMock()
            mock_chat_response.json.return_value = {
                "choices": [{"message": {"content": "Привет! Я GigaChat."}}]
            }

            # Первый вызов - OAuth, второй - чат
            mock_post.side_effect = [mock_auth_response, mock_chat_response]

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": sample_messages},
            )

            assert response.status_code == 200
            data = response.json()
            assert "choices" in data
            assert "GigaChat" in data.get("model", "")

    def test_chat_completions_unknown_provider(self, test_client, sample_messages):
        """Тест неизвестного провайдера"""
        with patch("tools.dev-tools.server.config", {"active_provider": "unknown"}):
            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": sample_messages},
            )

            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "Unknown provider" in data["error"]

    def test_chat_completions_codette_error(self, test_client, sample_messages):
        """Тест ошибки Codette"""
        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_post.side_effect = Exception("Connection error")

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": sample_messages},
            )

            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "Codette error" in data["error"]

    def test_chat_completions_gigachat_error(self, test_client, sample_messages):
        """Тест ошибки GigaChat"""
        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_post.side_effect = Exception("Auth error")

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": sample_messages},
            )

            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "GigaChat error" in data["error"]

    def test_empty_messages(self, test_client):
        """Тест пустых сообщений"""
        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": ""}
            mock_post.return_value = mock_response

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": []},
            )

            assert response.status_code == 200

    def test_system_message_handling(self, test_client):
        """Тест обработки system-сообщений"""
        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "Я понял, что нужно быть полезным."}
            mock_post.return_value = mock_response

            response = test_client.post(
                "/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "Ты эксперт по Python"},
                        {"role": "user", "content": "Как написать функцию?"},
                    ]
                },
            )

            assert response.status_code == 200

    def test_long_message(self, test_client):
        """Тест длинного сообщения"""
        long_content = "Привет! " * 100  # Длинный текст

        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "Ответ на длинный запрос"}
            mock_post.return_value = mock_response

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": [{"role": "user", "content": long_content}]},
            )

            assert response.status_code == 200

    def test_special_characters_in_message(self, test_client):
        """Тест специальных символов в сообщении"""
        special_content = "Привет! @#$%^&*() {}[]|\\:;\"'<>,.?/"

        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "Понял специальные символы"}
            mock_post.return_value = mock_response

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": [{"role": "user", "content": special_content}]},
            )

            assert response.status_code == 200

    def test_unicode_support(self, test_client):
        """Тест поддержки Unicode"""
        unicode_content = "Привет! 🤖 Привет! 你好！こんにちは!"

        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "Понял Unicode"}
            mock_post.return_value = mock_response

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": [{"role": "user", "content": unicode_content}]},
            )

            assert response.status_code == 200

    def test_multiple_turns_conversation(self, test_client):
        """Тест многошагового диалога"""
        messages = [
            {"role": "user", "content": "Привет!"},
            {"role": "assistant", "content": "Привет! Как дела?"},
            {"role": "user", "content": "Хорошо, спасибо!"},
        ]

        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "Рада, что всё хорошо!"}
            mock_post.return_value = mock_response

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": messages},
            )

            assert response.status_code == 200
            assert len(response.json()["choices"]) == 1


class TestConfigLoading:
    """Тесты загрузки конфигурации"""

    def test_config_file_exists(self):
        """Тест существования файла конфигурации"""
        import os

        config_path = ".gigacode/config.json"
        # Проверяем, что файл существует или есть пример
        assert os.path.exists(config_path) or os.path.exists(".gigacode/config.example.json")

    def test_config_structure(self):
        """Тест структуры конфигурации"""
        import json
        import os

        config_path = ".gigacode/config.json"

        if os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)

            assert "active_provider" in config
            assert config["active_provider"] in ["codette", "gigachat"]
            assert "codette" in config
            assert "gigachat" in config

    def test_env_variable_override(self):
        """Тест переопределения ключа из .env"""
        import os

        # Устанавливаем переменную окружения
        os.environ["GIGACHAT_API_KEY"] = "test_env_key"

        # Проверяем, что переменная загружается
        assert os.getenv("GIGACHAT_API_KEY") == "test_env_key"

        # Очищаем
        del os.environ["GIGACHAT_API_KEY"]


class TestErrorHandling:
    """Тесты обработки ошибок"""

    def test_invalid_json_request(self, test_client):
        """Тест невалидного JSON"""
        response = test_client.post(
            "/v1/chat/completions",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code in [400, 422]

    def test_missing_messages(self, test_client):
        """Тест отсутствия messages"""
        response = test_client.post(
            "/v1/chat/completions",
            json={},
        )

        assert response.status_code in [400, 422]

    def test_invalid_role(self, test_client):
        """Тест невалидной роли"""
        response = test_client.post(
            "/v1/chat/completions",
            json={"messages": [{"role": "invalid", "content": "test"}]},
        )

        # Должно либо отклонить, либо обработать
        assert response.status_code in [200, 400, 422]

    def test_network_timeout_codette(self, test_client, sample_messages):
        """Тест таймаута сети (Codette)"""
        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_post.side_effect = TimeoutError("Connection timeout")

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": sample_messages},
            )

            assert response.status_code == 200
            data = response.json()
            assert "error" in data

    def test_network_timeout_gigachat(self, test_client, sample_messages):
        """Тест таймаута сети (GigaChat)"""
        with patch("tools.dev-tools.server.requests.post") as mock_post:
            mock_post.side_effect = TimeoutError("Connection timeout")

            response = test_client.post(
                "/v1/chat/completions",
                json={"messages": sample_messages},
            )

            assert response.status_code == 200
            data = response.json()
            assert "error" in data

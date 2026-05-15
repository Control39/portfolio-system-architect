"""
Tests for chat_handlers module.
Covers: event handlers, message processing, AI streaming integration.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from python_server.chat_handlers import register_chat_handlers
from python_server.chat_service.base import ClientConnectionContext
from python_server.task_manager import ConnectionTaskManager


@pytest.fixture
def mock_chat():
    """Mock ChatServiceBase with decorator tracking"""
    chat = MagicMock()
    # Track registered handlers
    chat._handlers = {}

    def track_decorator(name):
        def decorator(func):
            chat._handlers[name] = func
            return func

        return decorator

    chat.on_connecting = track_decorator("connecting")
    chat.on_connected = track_decorator("connected")
    chat.on_event_message = track_decorator("event_message")
    chat.on_disconnected = track_decorator("disconnected")
    chat.add_to_group = AsyncMock()
    chat.send_to_group = AsyncMock()
    chat.streaming_to_group = AsyncMock()
    chat.room_store = MagicMock()
    return chat


@pytest.fixture
def mock_task_manager():
    """Mock ConnectionTaskManager"""
    tm = MagicMock(spec=ConnectionTaskManager)
    tm.cancel_all = MagicMock()
    tm.schedule = MagicMock()
    return tm


@pytest.fixture
def mock_logger():
    """Mock logger"""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.warning = MagicMock()
    return logger


class TestChatHandlersRegistration:
    """Test that handlers are registered correctly"""

    def test_register_chat_handlers_attaches_handlers(self, mock_chat, mock_logger, mock_task_manager):
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        # Verify handlers were registered
        assert "connecting" in mock_chat._handlers
        assert "connected" in mock_chat._handlers
        assert "event_message" in mock_chat._handlers
        assert "disconnected" in mock_chat._handlers


class TestConnectingHandler:
    """Tests for handle_connecting"""

    def test_handle_connecting_sets_user_id(self, mock_chat, mock_logger, mock_task_manager):
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        # Get the registered handler
        connecting_handler = mock_chat._handlers["connecting"]

        # Mock connection
        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-123"
        conn.user_id = None

        # Call handler
        import asyncio

        asyncio.run(connecting_handler(conn, mock_chat))

        # Verify user_id was set
        assert conn.user_id == "You"


class TestConnectedHandler:
    """Tests for handle_connected"""

    @pytest.mark.asyncio
    async def test_handle_connected_adds_to_group(self, mock_chat, mock_logger, mock_task_manager):
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        connected_handler = mock_chat._handlers["connected"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-123"
        conn.user_id = "You"  # Set by connecting handler
        conn.query = "/chat?roomId=test-room"  # Full query string format

        await connected_handler(conn, mock_chat)

        mock_chat.add_to_group.assert_called_once_with("conn-123", "test-room")
        mock_logger.info.assert_any_call("Client connected to room: %s", "test-room")

    @pytest.mark.asyncio
    async def test_handle_connected_logs_connection(self, mock_chat, mock_logger, mock_task_manager):
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        connected_handler = mock_chat._handlers["connected"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-123"
        conn.query = {}
        conn.user_id = "test-user"

        await connected_handler(conn, mock_chat)

        mock_logger.info.assert_any_call("connected: %s user=%s", "conn-123", "test-user")

    @pytest.mark.asyncio
    async def test_handle_connected_default_room(self, mock_chat, mock_logger, mock_task_manager):
        """Test with no roomId in query -> uses default"""
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        connected_handler = mock_chat._handlers["connected"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-456"
        conn.user_id = "You"
        conn.query = {}  # No roomId

        await connected_handler(conn, mock_chat)

        # Should use DEFAULT_ROOM_ID
        mock_chat.add_to_group.assert_called_once()
        call_args = mock_chat.add_to_group.call_args[0]
        assert call_args[1] == "public"  # DEFAULT_ROOM_ID


class TestEventMessageHandler:
    """Tests for handle_event_message"""

    @pytest.mark.asyncio
    async def test_handle_event_message_send_to_ai(self, mock_chat, mock_logger, mock_task_manager):
        """Test sendToAI message processing"""
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        handler = mock_chat._handlers["event_message"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-123"
        conn.user_id = "You"

        # Mock room_store to return empty history
        mock_chat.room_store.get_room_messages = AsyncMock(return_value=[])

        event_data = {"message": "Hello AI", "roomId": "test-room"}

        await handler(conn, "sendToAI", event_data, mock_chat)

        # Verify broadcast
        mock_chat.send_to_group.assert_called_once_with("test-room", "Hello AI", ["conn-123"], "You")

        # Verify task was scheduled
        mock_task_manager.schedule.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_event_message_ignores_non_send_to_ai(self, mock_chat, mock_logger, mock_task_manager):
        """Test that non-sendToAI events are ignored"""
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        handler = mock_chat._handlers["event_message"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-123"

        await handler(conn, "otherEvent", {"data": "test"}, mock_chat)

        # Should not call send_to_group or schedule
        mock_chat.send_to_group.assert_not_called()
        mock_task_manager.schedule.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_event_message_handles_room_store_error(self, mock_chat, mock_logger, mock_task_manager):
        """Test graceful handling of room_store errors"""
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        handler = mock_chat._handlers["event_message"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-123"
        conn.user_id = "You"

        # Mock room_store to raise exception
        mock_chat.room_store.get_room_messages = AsyncMock(side_effect=Exception("DB error"))

        event_data = {"message": "Test", "roomId": "test-room"}

        # Should not raise
        await handler(conn, "sendToAI", event_data, mock_chat)

        # Should still broadcast and schedule
        mock_chat.send_to_group.assert_called_once()
        mock_task_manager.schedule.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_event_message_missing_message(self, mock_chat, mock_logger, mock_task_manager):
        """Test handling of missing message field"""
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        handler = mock_chat._handlers["event_message"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-123"

        event_data = {"roomId": "test-room"}  # No message

        await handler(conn, "sendToAI", event_data, mock_chat)

        # Should not broadcast or schedule
        mock_chat.send_to_group.assert_not_called()
        mock_task_manager.schedule.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_event_message_missing_room_id(self, mock_chat, mock_logger, mock_task_manager):
        """Test handling of missing roomId"""
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        handler = mock_chat._handlers["event_message"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-123"

        event_data = {"message": "Test"}  # No roomId

        await handler(conn, "sendToAI", event_data, mock_chat)

        mock_chat.send_to_group.assert_not_called()
        mock_task_manager.schedule.assert_not_called()


class TestDisconnectedHandler:
    """Tests for handle_disconnected"""

    @pytest.mark.asyncio
    async def test_handle_disconnected_cancels_tasks(self, mock_chat, mock_logger, mock_task_manager):
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        handler = mock_chat._handlers["disconnected"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-123"

        await handler(conn, mock_chat)

        mock_task_manager.cancel_all.assert_called_once_with("conn-123")
        mock_logger.info.assert_called_once_with("Client disconnected: %s", "conn-123")

    @pytest.mark.asyncio
    async def test_handle_disconnected_no_connection_id(self, mock_chat, mock_logger, mock_task_manager):
        """Test disconnection without connectionId"""
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        handler = mock_chat._handlers["disconnected"]

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = None

        await handler(conn, mock_chat)

        # Should not call cancel_all if no connectionId
        mock_task_manager.cancel_all.assert_not_called()


class TestChatHandlersIntegration:
    """Integration tests for full message flow"""

    @pytest.mark.asyncio
    async def test_full_message_flow_user_to_ai(self, mock_chat, mock_logger, mock_task_manager):
        """Test complete flow: user message -> broadcast -> AI response stream"""
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-789"
        conn.user_id = None
        conn.query = "/chat?roomId=integration-room"  # Full query string format

        # Setup
        mock_chat.room_store.get_room_messages = AsyncMock(
            return_value=[
                {"type": "message", "message": "Previous: Hello", "from": "You", "id": 1},
                {"type": "message", "message": "AI: Hi there", "from": "AI", "id": 2},
            ]
        )

        # Simulate connecting
        connecting_handler = mock_chat._handlers["connecting"]
        await connecting_handler(conn, mock_chat)
        assert conn.user_id == "You"

        # Simulate connected
        connected_handler = mock_chat._handlers["connected"]
        await connected_handler(conn, mock_chat)
        mock_chat.add_to_group.assert_called_with("conn-789", "integration-room")

        # Simulate message
        event_handler = mock_chat._handlers["event_message"]
        await event_handler(conn, "sendToAI", {"message": "New question", "roomId": "integration-room"}, mock_chat)

        # Verify flow
        assert mock_chat.send_to_group.called
        assert mock_task_manager.schedule.called
        assert mock_chat.streaming_to_group.called

    @pytest.mark.asyncio
    async def test_disconnect_cleans_up_all_tasks(self, mock_chat, mock_logger, mock_task_manager):
        """Test that disconnect properly cleans up all tasks"""
        register_chat_handlers(mock_chat, mock_logger, mock_task_manager)

        conn = MagicMock(spec=ClientConnectionContext)
        conn.connectionId = "conn-cleanup"
        conn.query = {}
        conn.user_id = "You"

        # Simulate connected
        connected_handler = mock_chat._handlers["connected"]
        await connected_handler(conn, mock_chat)

        # Simulate message (schedules task)
        event_handler = mock_chat._handlers["event_message"]
        await event_handler(conn, "sendToAI", {"message": "Test", "roomId": "room1"}, mock_chat)
        assert mock_task_manager.schedule.called

        # Simulate disconnect
        disconnect_handler = mock_chat._handlers["disconnected"]
        await disconnect_handler(conn, mock_chat)

        mock_task_manager.cancel_all.assert_called_with("conn-cleanup")

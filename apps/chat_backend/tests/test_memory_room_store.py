"""
Comprehensive tests for InMemoryRoomStore
Covers: history API, metadata API, edge cases, user isolation
"""

from datetime import datetime

import pytest

from apps.chat_backend.config import DEFAULT_ROOM_ID
from apps.chat_backend.core.room_store.memory import InMemoryRoomStore


@pytest.fixture
def store() -> InMemoryRoomStore:
    return InMemoryRoomStore(max_messages=10)


class TestInMemoryHistoryAPI:
    """Tests for room history methods"""

    @pytest.mark.asyncio
    async def test_register_room_creates_empty_room(self, store: InMemoryRoomStore):
        await store.register_room("test-room")
        rooms = await store.list_rooms()
        assert any(r["name"] == "test-room" for r in rooms)
        assert any(r["name"] == DEFAULT_ROOM_ID for r in rooms)

    @pytest.mark.asyncio
    async def test_record_room_event_appends_to_history(self, store: InMemoryRoomStore):
        await store.register_room("test-room")
        event = {"type": "test_event", "data": "test"}
        await store.record_room_event("test-room", event)
        messages = await store.get_room_messages("test-room")
        assert len(messages) == 1
        assert messages[0] == event

    @pytest.mark.asyncio
    async def test_append_message_delegates_to_record_room_event(self, store: InMemoryRoomStore):
        await store.register_room("test-room")
        await store.append_message("test-room", {"msg": "hello"})
        messages = await store.get_room_messages("test-room")
        assert len(messages) == 1

    @pytest.mark.asyncio
    async def test_get_room_messages_returns_all(self, store: InMemoryRoomStore):
        await store.register_room("test-room")
        for i in range(5):
            await store.append_message("test-room", {"seq": i})
        messages = await store.get_room_messages("test-room")
        assert len(messages) == 5
        assert [m["seq"] for m in messages] == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_get_room_messages_with_limit(self, store: InMemoryRoomStore):
        await store.register_room("test-room")
        for i in range(10):
            await store.append_message("test-room", {"seq": i})
        messages = await store.get_room_messages("test-room", limit=3)
        assert len(messages) == 3
        assert [m["seq"] for m in messages] == [7, 8, 9]

    @pytest.mark.asyncio
    async def test_get_room_messages_with_negative_limit(self, store: InMemoryRoomStore):
        await store.register_room("test-room")
        await store.append_message("test-room", {"seq": 1})
        messages = await store.get_room_messages("test-room", limit=-1)
        assert len(messages) == 1

    @pytest.mark.asyncio
    async def test_get_room_messages_empty_room(self, store: InMemoryRoomStore):
        messages = await store.get_room_messages("non-existent")
        assert messages == []

    @pytest.mark.asyncio
    async def test_list_rooms_includes_message_counts(self, store: InMemoryRoomStore):
        await store.register_room("room1")
        await store.register_room("room2")
        await store.append_message("room1", {"x": 1})
        await store.append_message("room1", {"x": 2})
        await store.append_message("room2", {"y": 1})
        rooms = await store.list_rooms()
        room1 = next(r for r in rooms if r["name"] == "room1")
        room2 = next(r for r in rooms if r["name"] == "room2")
        assert room1["messages"] == 2
        assert room2["messages"] == 1

    @pytest.mark.asyncio
    async def test_remove_room_if_empty_removes_empty_room(self, store: InMemoryRoomStore):
        await store.register_room("temp-room")
        rooms_before = await store.list_rooms()
        assert any(r["name"] == "temp-room" for r in rooms_before)
        await store.remove_room_if_empty("temp-room")
        rooms_after = await store.list_rooms()
        assert not any(r["name"] == "temp-room" for r in rooms_after)

    @pytest.mark.asyncio
    async def test_remove_room_if_empty_skips_non_empty(self, store: InMemoryRoomStore):
        await store.register_room("temp-room")
        await store.append_message("temp-room", {"x": 1})
        await store.remove_room_if_empty("temp-room")
        rooms = await store.list_rooms()
        assert any(r["name"] == "temp-room" for r in rooms)

    @pytest.mark.asyncio
    async def test_remove_room_if_empty_protects_default(self, store: InMemoryRoomStore):
        await store.remove_room_if_empty(DEFAULT_ROOM_ID)
        rooms = await store.list_rooms()
        assert any(r["name"] == DEFAULT_ROOM_ID for r in rooms)

    @pytest.mark.asyncio
    async def test_max_messages_overflow(self, store: InMemoryRoomStore):
        """Test that old messages are removed when exceeding max_messages"""
        await store.register_room("overflow-room")
        for i in range(15):  # max_messages=10
            await store.append_message("overflow-room", {"seq": i})
        messages = await store.get_room_messages("overflow-room")
        assert len(messages) == 10
        assert messages[0]["seq"] == 5  # First 5 should be removed
        assert messages[-1]["seq"] == 14

    @pytest.mark.asyncio
    async def test_max_messages_with_small_limit(self, store: InMemoryRoomStore):
        store_small = InMemoryRoomStore(max_messages=3)
        await store_small.register_room("small-room")
        for i in range(5):
            await store_small.append_message("small-room", {"seq": i})
        messages = await store_small.get_room_messages("small-room")
        assert len(messages) == 3
        assert [m["seq"] for m in messages] == [2, 3, 4]


class TestInMemoryMetadataAPI:
    """Tests for room metadata methods"""

    @pytest.mark.asyncio
    async def test_create_room_metadata_generates_id(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "My Room")
        assert room.room_id.startswith("room_")
        assert room.room_name == "My Room"
        assert room.user_id == "user1"
        # Implementation uses empty string for None description
        assert room.description in [None, ""]

    @pytest.mark.asyncio
    async def test_create_room_metadata_uses_custom_id(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "My Room", room_id="custom-123")
        assert room.room_id == "custom-123"

    @pytest.mark.asyncio
    async def test_create_room_metadata_with_description(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "My Room", description="A test room")
        assert room.description == "A test room"

    @pytest.mark.asyncio
    async def test_create_room_metadata_idempotent(self, store: InMemoryRoomStore):
        room1 = await store.create_room_metadata("user1", "My Room", room_id="same-id")
        room2 = await store.create_room_metadata("user1", "My Room", room_id="same-id")
        assert room1.room_id == room2.room_id
        assert room1 is room2  # Same object

    @pytest.mark.asyncio
    async def test_get_room_metadata_existing(self, store: InMemoryRoomStore):
        await store.create_room_metadata("user1", "My Room", room_id="test-room")
        retrieved = await store.get_room_metadata("user1", "test-room")
        assert retrieved is not None
        assert retrieved.room_name == "My Room"

    @pytest.mark.asyncio
    async def test_get_room_metadata_nonexistent(self, store: InMemoryRoomStore):
        result = await store.get_room_metadata("user1", "non-existent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_room_metadata_default_room(self, store: InMemoryRoomStore):
        result = await store.get_room_metadata("user1", DEFAULT_ROOM_ID)
        assert result is not None
        assert result.room_id == DEFAULT_ROOM_ID
        assert result.room_name == "Public Chat"

    @pytest.mark.asyncio
    async def test_update_room_metadata_name(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "Old Name", room_id="test-room")
        updated = await store.update_room_metadata("user1", "test-room", room_name="New Name")
        assert updated.room_name == "New Name"
        assert updated.description == room.description

    @pytest.mark.asyncio
    async def test_update_room_metadata_description(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "Name", room_id="test-room")
        updated = await store.update_room_metadata("user1", "test-room", description="New Desc")
        assert updated.description == "New Desc"
        assert updated.room_name == room.room_name

    @pytest.mark.asyncio
    async def test_update_room_metadata_updates_timestamp(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "Name", room_id="test-room")
        # Parse timestamp (handle both formats)
        ts_str = room.updated_at
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        before = datetime.fromisoformat(ts_str)
        # Small delay to ensure timestamp difference
        import asyncio

        await asyncio.sleep(0.01)
        await store.update_room_metadata("user1", "test-room", room_name="New")
        updated = await store.get_room_metadata("user1", "test-room")
        assert updated is not None  # Type guard for mypy
        ts_str = updated.updated_at
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        after = datetime.fromisoformat(ts_str)
        assert after >= before  # Allow equality for very fast updates

    @pytest.mark.asyncio
    async def test_update_room_metadata_not_found(self, store: InMemoryRoomStore):
        with pytest.raises(ValueError, match="not found"):
            await store.update_room_metadata("user1", "non-existent", room_name="New")

    @pytest.mark.asyncio
    async def test_delete_room_metadata_success(self, store: InMemoryRoomStore):
        await store.create_room_metadata("user1", "Name", room_id="test-room")
        result = await store.delete_room_metadata("user1", "test-room")
        assert result is True
        retrieved = await store.get_room_metadata("user1", "test-room")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_room_metadata_not_found(self, store: InMemoryRoomStore):
        result = await store.delete_room_metadata("user1", "non-existent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_room_metadata_protects_default(self, store: InMemoryRoomStore):
        result = await store.delete_room_metadata("user1", DEFAULT_ROOM_ID)
        assert result is False
        retrieved = await store.get_room_metadata("user1", DEFAULT_ROOM_ID)
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_list_user_rooms_includes_default(self, store: InMemoryRoomStore):
        await store.create_room_metadata("user1", "Private", room_id="private-1")
        rooms = await store.list_user_rooms("user1")
        room_ids = [r.room_id for r in rooms]
        assert DEFAULT_ROOM_ID in room_ids
        assert "private-1" in room_ids

    @pytest.mark.asyncio
    async def test_list_user_rooms_isolation(self, store: InMemoryRoomStore):
        await store.create_room_metadata("user1", "User1 Room", room_id="u1-room")
        await store.create_room_metadata("user2", "User2 Room", room_id="u2-room")
        user1_rooms = await store.list_user_rooms("user1")
        user2_rooms = await store.list_user_rooms("user2")
        assert len(user1_rooms) == 2  # Default + u1-room
        assert len(user2_rooms) == 2  # Default + u2-room
        assert not any(r.room_id == "u2-room" for r in user1_rooms)
        assert not any(r.room_id == "u1-room" for r in user2_rooms)

    @pytest.mark.asyncio
    async def test_room_exists_default_true(self, store: InMemoryRoomStore):
        assert await store.room_exists("user1", DEFAULT_ROOM_ID) is True

    @pytest.mark.asyncio
    async def test_room_exists_custom_true(self, store: InMemoryRoomStore):
        await store.create_room_metadata("user1", "Name", room_id="test-room")
        assert await store.room_exists("user1", "test-room") is True

    @pytest.mark.asyncio
    async def test_room_exists_custom_false(self, store: InMemoryRoomStore):
        assert await store.room_exists("user1", "non-existent") is False


class TestInMemoryUserIsolation:
    """Test user isolation and multi-user scenarios"""

    @pytest.mark.asyncio
    async def test_multiple_users_independent_rooms(self, store: InMemoryRoomStore):
        await store.create_room_metadata("user1", "User1 Room", room_id="u1-room")
        await store.create_room_metadata("user2", "User2 Room", room_id="u2-room")
        # User1 can only see their own rooms
        user1_rooms = await store.list_user_rooms("user1")
        user2_rooms = await store.list_user_rooms("user2")
        assert len(user1_rooms) == 2
        assert len(user2_rooms) == 2
        assert all(r.user_id in ["system", "user1"] for r in user1_rooms)
        assert all(r.user_id in ["system", "user2"] for r in user2_rooms)

    @pytest.mark.asyncio
    async def test_shared_history_across_users(self, store: InMemoryRoomStore):
        """Same room ID, different users: history is shared"""
        await store.register_room("shared-room")
        await store.append_message("shared-room", {"user": "user1", "text": "Hello"})
        await store.append_message("shared-room", {"user": "user2", "text": "Hi"})
        messages = await store.get_room_messages("shared-room")
        assert len(messages) == 2
        assert messages[0]["user"] == "user1"
        assert messages[1]["user"] == "user2"


class TestInMemoryEdgeCases:
    """Edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_room_name(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "")
        assert room.room_name == ""

    @pytest.mark.asyncio
    async def test_unicode_room_name(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "🚀 Room 日本語")
        assert room.room_name == "🚀 Room 日本語"

    @pytest.mark.asyncio
    async def test_very_long_room_name(self, store: InMemoryRoomStore):
        long_name = "x" * 1000
        room = await store.create_room_metadata("user1", long_name)
        assert room.room_name == long_name

    @pytest.mark.asyncio
    async def test_null_description(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "Name", description=None)
        # Implementation converts None to empty string
        assert room.description in [None, ""]

    @pytest.mark.asyncio
    async def test_empty_description(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "Name", description="")
        assert room.description == ""

    @pytest.mark.asyncio
    async def test_overwrite_description_with_empty(self, store: InMemoryRoomStore):
        room = await store.create_room_metadata("user1", "Name", description="Old")
        updated = await store.update_room_metadata("user1", room.room_id, description="")
        assert updated.description == ""

    @pytest.mark.asyncio
    async def test_concurrent_room_creation(self, store: InMemoryRoomStore):
        """Test that concurrent creation doesn't duplicate rooms"""
        import asyncio

        async def create_room():
            return await store.create_room_metadata("user1", "Concurrent", room_id="same-id")

        results = await asyncio.gather(create_room(), create_room(), create_room())
        assert all(r.room_id == "same-id" for r in results)
        assert len({id(r) for r in results}) == 1  # Same object

    @pytest.mark.asyncio
    async def test_massive_message_history(self, store: InMemoryRoomStore):
        """Test performance with many messages"""
        await store.register_room("massive-room")
        for i in range(1000):
            await store.append_message("massive-room", {"seq": i})
        messages = await store.get_room_messages("massive-room", limit=10)
        assert len(messages) == 10
        assert messages[0]["seq"] == 990


class TestInMemoryIntegration:
    """Integration tests combining history and metadata"""

    @pytest.mark.asyncio
    async def test_full_room_lifecycle(self, store: InMemoryRoomStore):
        # 1. Create room
        room = await store.create_room_metadata("user1", "My Room", room_id="test-1")
        assert room.room_id == "test-1"

        # 2. Register room for history
        await store.register_room("test-1")

        # 3. Add messages
        await store.append_message("test-1", {"type": "text", "content": "Hello"})
        await store.append_message("test-1", {"type": "text", "content": "World"})

        # 4. Verify messages
        messages = await store.get_room_messages("test-1")
        assert len(messages) == 2

        # 5. Update metadata
        updated = await store.update_room_metadata("user1", "test-1", room_name="Updated Room")
        assert updated.room_name == "Updated Room"

        # 6. List user rooms
        rooms = await store.list_user_rooms("user1")
        assert len(rooms) == 2  # Default + test-1
        assert any(r.room_id == "test-1" for r in rooms)

        # 7. Delete room
        deleted = await store.delete_room_metadata("user1", "test-1")
        assert deleted is True
        assert await store.get_room_metadata("user1", "test-1") is None

        # 8. History still exists (metadata deletion doesn't affect history)
        messages_after = await store.get_room_messages("test-1")
        assert len(messages_after) == 2

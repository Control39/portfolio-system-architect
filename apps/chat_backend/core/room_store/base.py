from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .models import RoomMetadata


class RoomStore(ABC):
    # -------- message history API (existing) --------
    @abstractmethod
    async def register_room(self, room: str) -> None: ...

    @abstractmethod
    async def record_room_event(self, room: str, event: dict[str, Any]) -> None: ...

    @abstractmethod
    async def append_message(self, room: str, event: dict[str, Any]) -> None: ...

    @abstractmethod
    async def get_room_messages(self, room: str, limit: int | None = None) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def list_rooms(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def remove_room_if_empty(self, room: str) -> None: ...

    # -------- metadata API (new, merged) --------
    @abstractmethod
    async def create_room_metadata(
        self,
        user_id: str,
        room_name: str,
        *,
        room_id: str | None = None,
        description: str | None = None,
    ) -> RoomMetadata: ...

    @abstractmethod
    async def get_room_metadata(self, user_id: str, room_id: str) -> RoomMetadata | None: ...

    @abstractmethod
    async def update_room_metadata(
        self,
        user_id: str,
        room_id: str,
        *,
        room_name: str | None = None,
        description: str | None = None,
    ) -> RoomMetadata: ...

    @abstractmethod
    async def delete_room_metadata(self, user_id: str, room_id: str) -> bool: ...

    @abstractmethod
    async def list_user_rooms(self, user_id: str) -> list[RoomMetadata]: ...

    @abstractmethod
    async def room_exists(self, user_id: str, room_id: str) -> bool: ...


__all__ = ["RoomStore"]

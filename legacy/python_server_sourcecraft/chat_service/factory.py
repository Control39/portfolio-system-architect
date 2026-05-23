"""Factory helpers for constructing chat services based on runtime transport mode."""

from __future__ import annotations

import logging
import os
from typing import Any

from ..core.runtime_config import TransportMode
from . import ChatService, ChatServiceBase


def resolve_webpubsub_config() -> tuple[str | None, str | None, str]:
    endpoint = os.getenv("WEBPUBSUB_ENDPOINT") or os.getenv("WEB_PUBSUB_ENDPOINT")
    conn_str = os.getenv("WEBPUBSUB_CONNECTION_STRING") or os.getenv("WEB_PUBSUB_CONNECTION_STRING")
    hub = os.getenv("WEBPUBSUB_HUB", "demo_ai_chat")
    return endpoint, conn_str, hub


def build_chat_service(
    public_endpoint: str | None,
    host: str,
    port: int,
    room_store: Any,
    app_logger: logging.Logger,
    *,
    flask_app: Any | None = None,
    loop: Any | None = None,
    transport_mode: TransportMode = TransportMode.SELF,
) -> ChatServiceBase:
    """Construct a concrete ChatService based on transport mode.

    Only imports WebPubSubChatService when needed to keep mypy subset small.
    """
    if not isinstance(transport_mode, TransportMode):
        raise RuntimeError("transport_mode must be a TransportMode enum instance")
    if transport_mode is TransportMode.SELF:
        return ChatService(public_endpoint=public_endpoint, host=host, port=port, room_store=room_store)

    # WebPubSub path
    endpoint, conn_str, hub = resolve_webpubsub_config()
    if not (endpoint or conn_str):
        raise RuntimeError("WEBPUBSUB_ENDPOINT or WEBPUBSUB_CONNECTION_STRING required for WebPubSub transport")
    try:
        from .transports.webpubsub import WebPubSubChatService  # local import to avoid hard dependency
    except Exception as e:
        raise RuntimeError("WebPubSub dependencies not available; install azure-messaging-webpubsubservice") from e
    return WebPubSubChatService(
        hub=hub,
        connection_string=conn_str,
        endpoint=endpoint,
        room_store=room_store,
        logger=app_logger,
        flask_app=flask_app,
        loop=loop,
    )


__all__ = [
    "build_chat_service",
    "resolve_webpubsub_config",
]

"""Custom chat protocol helpers.

Defines a lightweight application-layer packet format that every chat message
must follow when moving between the Flask UI and the community API service.

Packet schema (JSON):
{
    "header": {
        "version": "1.0",
        "message_type": "CHAT" | "SYSTEM" | "AI",
        "message_id": "<uuid4>",
        "sender": "<user identifier>",
        "channel": "<room name>",
        "timestamp": "<ISO-8601>"
    },
    "payload": {
        "body": "<message text>",
        "metadata": {... arbitrary extra fields ...}
    }
}
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


PROTOCOL_VERSION = "1.0"
DEFAULT_CHANNEL = "lobby"
VALID_MESSAGE_TYPES = {"CHAT", "SYSTEM", "AI"}


class ProtocolError(ValueError):
    """Raised when a packet does not comply with the contract."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Packet:
    message_type: str
    sender: str
    body: str
    channel: str = DEFAULT_CHANNEL
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=_utc_now_iso)
    version: str = PROTOCOL_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "header": {
                "version": self.version,
                "message_type": self.message_type,
                "message_id": self.message_id,
                "sender": self.sender,
                "channel": self.channel,
                "timestamp": self.timestamp,
            },
            "payload": {
                "body": self.body,
                "metadata": self.metadata,
            },
        }

    def dumps(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


def validate_packet(raw_packet: Dict[str, Any]) -> Dict[str, Any]:
    """Validate structure and return normalized packet dict."""
    if not isinstance(raw_packet, dict):
        raise ProtocolError("packet must be a JSON object")

    header = raw_packet.get("header")
    payload = raw_packet.get("payload")

    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise ProtocolError("packet requires header and payload objects")

    version = header.get("version")
    if version != PROTOCOL_VERSION:
        raise ProtocolError(f"unsupported protocol version: {version}")

    message_type = header.get("message_type")
    if message_type not in VALID_MESSAGE_TYPES:
        raise ProtocolError("invalid message_type")

    message_id = header.get("message_id") or str(uuid.uuid4())
    sender = header.get("sender")
    channel = header.get("channel") or DEFAULT_CHANNEL
    timestamp = header.get("timestamp") or _utc_now_iso()

    if not sender:
        raise ProtocolError("sender is required")

    body = payload.get("body")
    if body is None or body == "":
        raise ProtocolError("payload.body is required")

    metadata = payload.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise ProtocolError("payload.metadata must be an object")

    return {
        "header": {
            "version": PROTOCOL_VERSION,
            "message_type": message_type,
            "message_id": message_id,
            "sender": sender,
            "channel": channel,
            "timestamp": timestamp,
        },
        "payload": {
            "body": body,
            "metadata": metadata,
        },
    }


def build_packet(
    sender: str,
    body: str,
    *,
    message_type: str = "CHAT",
    channel: str = DEFAULT_CHANNEL,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Helper for server side packet creation."""
    packet = Packet(
        message_type=message_type,
        sender=sender,
        body=body,
        channel=channel,
        metadata=metadata or {},
    )
    return packet.to_dict()


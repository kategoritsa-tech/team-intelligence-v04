from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Одно сообщение Telegram."""

    message_id: int

    author: str
    date: datetime | None
    text: str

    reply_to_message_id: int | None = None

    has_media: bool = False
    media_type: str | None = None
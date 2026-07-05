from team_intelligence.parser.models import Message
from collections import Counter


class AttachmentAnalyzer:
    """Анализ вложений в сообщениях."""

    def __init__(self, messages: list[Message]):
        self.messages = messages

    def attachments(self) -> list[Message]:
        """Возвращает сообщения с вложениями."""

        return [
            message
            for message in self.messages
            if message.has_media
        ]

    def total_attachments(self) -> int:
        """Общее количество вложений."""

        return len(self.attachments())

    def attachments_by_type(self) -> Counter:
        """Количество вложений по типам."""

        return Counter(
            message.media_type
            for message in self.attachments()
            if message.media_type is not None
        )

    def top_attachment_authors(
            self,
            limit: int = 10,
    ) -> list[tuple[str, int]]:
        """Пользователи, чаще всего отправляющие вложения."""

        return Counter(
            message.author
            for message in self.attachments()
        ).most_common(limit)


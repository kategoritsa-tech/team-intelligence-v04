import re

from team_intelligence.parser.models import Message
from collections import Counter

class CommunicationAnalyzer:
    """Анализ коммуникаций между участниками."""

    def __init__(self, messages: list[Message]):
        self.messages = messages

    def all_mentions(self) -> list[tuple[str, str]]:
        """Возвращает все пары (автор → упоминание)."""

        pairs: list[tuple[str, str]] = []

        for message in self.messages:

            if not message.text:
                continue

            mentions = re.findall(r"@\w+", message.text)

            for mention in mentions:
                pairs.append((message.author, mention))

        return pairs

    def communication_pairs(self, limit: int = 20) -> list[tuple[tuple[str, str], int]]:
        """Самые частые пары общения."""

        return Counter(self.all_mentions()).most_common(limit)

    def reply_pairs(self) -> list[tuple[str, str]]:
        """Возвращает пары ответов (кто ответил -> кому ответил)."""

        messages_by_id = {
            message.message_id: message
            for message in self.messages
        }

        pairs = []

        for message in self.messages:
            if message.reply_to_message_id is None:
                continue

            original_message = messages_by_id.get(message.reply_to_message_id)

            if original_message is None:
                continue

            pairs.append((message.author, original_message.author))

        return pairs

    def top_reply_pairs(
            self,
            limit: int = 10,
    ) -> list[tuple[tuple[str, str], int]]:
        """Самые частые ответы между участниками."""

        return Counter(
            self.reply_pairs()
        ).most_common(limit)

    def top_mention_authors(
            self,
            limit: int = 10,
    ) -> list[tuple[str, int]]:
        """Кто чаще всего упоминает других участников."""

        return Counter(
            author
            for author, _ in self.all_mentions()
        ).most_common(limit)
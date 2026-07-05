import re
from collections import Counter

from team_intelligence.parser.models import Message

def most_mentioned(self, limit: int = 10) -> Counter:
    """Самые часто упоминаемые пользователи."""

    return Counter(self.mentions()).most_common(limit)
class MentionAnalyzer:
    """Анализ упоминаний пользователей."""

    def __init__(self, messages: list[Message]):
        self.messages = messages

    def mentions(self) -> list[str]:
        """Возвращает все упоминания пользователей."""

        mentions = []

        for message in self.messages:

            if not message.text:
                continue

            found = re.findall(r"@\w+", message.text)

            mentions.extend(found)

        return mentions

    def most_mentioned(self, limit: int = 10) -> list[tuple[str, int]]:
        """Самые часто упоминаемые пользователи."""

        return Counter(self.mentions()).most_common(limit)
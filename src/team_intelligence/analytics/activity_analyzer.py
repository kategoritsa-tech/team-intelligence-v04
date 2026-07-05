from collections import Counter
from datetime import date

from team_intelligence.parser.models import Message


class ActivityAnalyzer:
    """Анализ активности сообщений."""

    def __init__(self, messages: list[Message]):
        self.messages = messages

    def messages_by_day(self) -> Counter:
        """Количество сообщений по дням."""

        return Counter(
            message.date.date()
            for message in self.messages
            if message.date is not None
        )

    def messages_by_hour(self) -> Counter:
        """Количество сообщений по часам."""

        return Counter(
            message.date.hour
            for message in self.messages
            if message.date is not None
        )

    def messages_for_day(self, day: date) -> list[Message]:
        """Все сообщения за выбранный день."""

        return [
            message
            for message in self.messages
            if message.date is not None
            and message.date.date() == day
        ]
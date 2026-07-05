from collections import Counter
from datetime import date

from team_intelligence.parser.models import Message


class StatisticsAnalyzer:
    """Вычисляет базовую статистику сообщений."""

    def __init__(self, messages: list[Message]):
        self.messages = messages

    def total_messages(self) -> int:
        """Количество сообщений."""

        return len(self.messages)

    def unique_authors(self) -> int:
        """Количество участников."""

        authors = {
            message.author
            for message in self.messages
        }

        return len(authors)

    def messages_by_author(self) -> Counter:
        """Количество сообщений каждого автора."""

        return Counter(
            message.author
            for message in self.messages
        )

    def first_message_date(self) -> date | None:
        """Дата первого сообщения."""

        dates = [
            message.date.date()
            for message in self.messages
            if message.date is not None
        ]

        if not dates:
            return None

        return min(dates)

    def last_message_date(self) -> date | None:
        """Дата последнего сообщения."""

        dates = [
            message.date.date()
            for message in self.messages
            if message.date is not None
        ]

        if not dates:
            return None

        return max(dates)

    def days_count(self) -> int:
        """Количество дней переписки."""

        first = self.first_message_date()
        last = self.last_message_date()

        if first is None or last is None:
            return 0

        return (last - first).days + 1

    def average_messages_per_day(self) -> float:
        """Среднее количество сообщений в день."""

        days = self.days_count()

        if days == 0:
            return 0

        return round(
            self.total_messages() / days,
            1,
        )

    def top_author(self) -> str | None:
        """Самый активный автор."""

        stats = self.messages_by_author()

        if not stats:
            return None

        return stats.most_common(1)[0][0]
from collections import defaultdict
from datetime import date

from team_intelligence.daily.models import DailyReport
from team_intelligence.parser.models import Message


class DailyReportBuilder:
    """Строит ежедневные отчеты из сообщений Telegram."""

    REPORT_MARKERS = (
        "вчера",
        "сегодня",
        "проблем",
        "#тест",
        "#аналитика",
        "#анатилика",
        "#разработка",
    )

    def __init__(self, messages: list[Message]):
        self.messages = messages

    def build(self) -> list[DailyReport]:
        """Группирует сообщения одного автора за день в DailyReport."""

        grouped: dict[tuple[str, date], list[Message]] = defaultdict(list)

        for message in self.messages:
            if message.date is None or not message.text.strip():
                continue

            if not self._looks_like_report(message.text):
                continue

            key = (message.author, message.date.date())
            grouped[key].append(message)

        reports: list[DailyReport] = []

        for (author, report_date), messages in sorted(
            grouped.items(),
            key=lambda item: (item[0][1], item[0][0]),
        ):
            reports.append(
                DailyReport(
                    author=author,
                    report_date=report_date,
                    messages=sorted(
                        messages,
                        key=lambda message: message.date,
                    ),
                )
            )

        return reports

    def _looks_like_report(self, text: str) -> bool:
        """Проверяет, похоже ли сообщение на ежедневный отчет."""

        normalized = text.lower()

        if "библейском формате" in normalized or "каждый должен" in normalized:
            return False

        has_yesterday = "вчера" in normalized
        has_today = "сегодня" in normalized
        return has_yesterday and has_today

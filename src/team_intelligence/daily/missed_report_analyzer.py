from dataclasses import dataclass
from datetime import timedelta

from team_intelligence.daily.models import DailyReportMetrics


@dataclass(frozen=True)
class MissedDailyReport:
    """Пропущенный daily-отчет."""

    report_date: object
    author: str
    status: str
    comment: str


class MissedReportAnalyzer:
    """Анализирует пропущенные daily-отчеты."""

    def __init__(
        self,
        report_metrics: list[DailyReportMetrics],
    ):
        self.report_metrics = report_metrics

    def missed_reports(self) -> list[MissedDailyReport]:
        """Возвращает список пропущенных отчетов."""

        reports_by_author: dict[str, set] = {}

        for metric in self.report_metrics:
            if metric.report_date is None:
                continue

            reports_by_author.setdefault(
                metric.author,
                set(),
            ).add(metric.report_date)

        all_dates = sorted(
            {
                metric.report_date
                for metric in self.report_metrics
                if metric.report_date is not None
            }
        )

        if not all_dates:
            return []

        start_date = all_dates[0]
        end_date = all_dates[-1]

        workdays = []
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() < 5:
                workdays.append(current_date)

            current_date += timedelta(days=1)

        result = []

        for author, report_dates in sorted(reports_by_author.items()):
            if not report_dates:
                continue

            first_author_date = min(report_dates)
            last_author_date = max(report_dates)

            for workday in workdays:
                if workday < first_author_date or workday > last_author_date:
                    continue

                if workday in report_dates:
                    continue

                result.append(
                    MissedDailyReport(
                        report_date=workday,
                        author=author,
                        status="Нет отчета",
                        comment="Автор писал отчеты в другие дни, но за эту дату отчет не найден",
                    )
                )

        return sorted(
            result,
            key=lambda item: (
                item.report_date,
                item.author,
            ),
        )

    def total_missed(self) -> int:
        """Количество пропущенных отчетов."""

        return len(self.missed_reports())

    def authors_with_missed_reports(self) -> set[str]:
        """Авторы, у которых есть пропуски."""

        return {
            item.author
            for item in self.missed_reports()
        }

    def missed_count_by_author(self) -> dict[str, int]:
        """Количество пропусков по авторам."""

        result: dict[str, int] = {}

        for item in self.missed_reports():
            result[item.author] = result.get(
                item.author,
                0,
            ) + 1

        return result
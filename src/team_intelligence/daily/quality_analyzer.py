from collections import defaultdict
from datetime import time

from team_intelligence.daily.models import (
    AuthorDailyMetrics,
    DailyReportMetrics,
    StructuredDailyReport,
)


class DailyQualityAnalyzer:
    """Оценивает качество ежедневных отчетов."""

    VAGUE_PHRASES = (
        "по поступающим",
        "по потребности",
        "текущие задачи",
        "текущим задачам",
        "помощь коллегам",
        "вопросы команды",
        "вопросы 2лп",
        "заниматься",
        "разбираюсь",
        "в работе",
        "продолжить",
        "задача по",
    )

    def __init__(
        self,
        reports: list[StructuredDailyReport],
        deadline: time = time(11, 0),
    ):
        self.reports = reports
        self.deadline = deadline

    def report_metrics(self) -> list[DailyReportMetrics]:
        """Метрики по каждому отчету."""

        return [self._analyze_report(report) for report in self.reports]

    def author_metrics(self) -> list[AuthorDailyMetrics]:
        """Агрегированные метрики по авторам."""

        grouped: dict[str, list[DailyReportMetrics]] = defaultdict(list)

        for metric in self.report_metrics():
            grouped[metric.author].append(metric)

        result: list[AuthorDailyMetrics] = []

        for author, metrics in sorted(grouped.items()):
            result.append(
                AuthorDailyMetrics(
                    author=author,
                    reports_count=len(metrics),
                    average_quality=round(
                        sum(item.quality_score for item in metrics) / len(metrics),
                        1,
                    ),
                    average_completeness=round(
                        sum(item.completeness_score for item in metrics) / len(metrics),
                        1,
                    ),
                    average_completed_tasks=round(
                        sum(item.completed_tasks_count for item in metrics) / len(metrics),
                        1,
                    ),
                    average_planned_tasks=round(
                        sum(item.planned_tasks_count for item in metrics) / len(metrics),
                        1,
                    ),
                    late_reports=sum(1 for item in metrics if item.is_late),
                    reports_with_problems=sum(1 for item in metrics if item.problems_count > 0),
                    vague_items_count=sum(item.vague_items_count for item in metrics),
                )
            )

        return result

    def _analyze_report(self, report: StructuredDailyReport) -> DailyReportMetrics:
        """Оценивает один отчет."""

        notes: list[str] = []
        completeness = 0
        quality = 0

        if report.yesterday:
            completeness += 35
            quality += 25
        else:
            notes.append("нет блока 'Вчера'")

        if report.today:
            completeness += 35
            quality += 25
        else:
            notes.append("нет блока 'Сегодня'")

        if report.problems:
            completeness += 15
            quality += 15
        else:
            notes.append("нет блока 'Проблемы'")

        if report.role:
            completeness += 15
            quality += 10
        else:
            notes.append("нет роли/хэштега")

        if report.jira_keys:
            quality += 15
        else:
            notes.append("нет Jira-задач")

        if report.completed_tasks_count >= 2:
            quality += 10
        elif report.completed_tasks_count == 0:
            notes.append("нет выполненных задач")

        vague_count = self._vague_items_count(report)

        if vague_count:
            quality -= min(20, vague_count * 5)
            notes.append(f"Мало конкретики в формулировках: {vague_count}")

        post_time = report.first_time.time() if report.first_time else None
        is_late = bool(post_time and post_time > self.deadline)

        if is_late:
            quality -= 5
            notes.append("отчет опубликован после дедлайна")

        return DailyReportMetrics(
            author=report.author,
            report_date=report.report_date,
            role=report.role,
            quality_score=max(0, min(100, quality)),
            completeness_score=max(0, min(100, completeness)),
            completed_tasks_count=report.completed_tasks_count,
            planned_tasks_count=report.planned_tasks_count,
            problems_count=len(report.problems) if report.has_problems else 0,
            jira_count=len(report.jira_keys),
            vague_items_count=vague_count,
            is_late=is_late,
            post_time=post_time,
            notes=notes,
        )

    def _vague_items_count(self, report: StructuredDailyReport) -> int:
        """Считает расплывчатые формулировки."""

        items = report.yesterday + report.today + report.problems
        count = 0

        for item in items:
            lower = item.lower()
            if any(phrase in lower for phrase in self.VAGUE_PHRASES):
                count += 1

        return count

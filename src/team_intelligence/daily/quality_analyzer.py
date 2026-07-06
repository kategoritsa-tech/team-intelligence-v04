from collections import defaultdict
from datetime import time
import re

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
        "мониторинг",
        "разбор вопросов",
        "рабочие вопросы",
    )

    ALWAYS_VAGUE_PHRASES = (
        "по поступающим",
        "по потребности",
        "текущие задачи",
        "текущим задачам",
        "рабочие вопросы",
    )

    NO_PROBLEMS_PHRASES = (
        "нет",
        "нет проблем",
        "проблем нет",
        "блокеров нет",
        "нет блокеров",
        "отсутствуют",
        "не выявлено",
        "не обнаружено",
        "нет рисков",
        "рисков нет",
        "без блокеров",
        "без проблем",
    )

    CONCRETE_MARKERS = (
        "согласован",
        "согласована",
        "согласовано",
        "подготовлен",
        "подготовлена",
        "подготовлено",
        "направлен",
        "направлена",
        "направлено",
        "проверен",
        "проверена",
        "проверено",
        "исправлен",
        "исправлена",
        "исправлено",
        "доработан",
        "доработана",
        "доработано",
        "завершен",
        "завершена",
        "завершено",
        "сделан",
        "сделана",
        "сделано",
        "проведен",
        "проведена",
        "проведено",
        "описан",
        "описана",
        "описано",
        "сформирован",
        "сформирована",
        "сформировано",
        "выгружен",
        "выгружена",
        "выгружено",
        "протестирован",
        "протестирована",
        "протестировано",
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

        has_yesterday = bool(report.yesterday)
        has_today = bool(report.today)
        has_problem_section = self._has_problem_section(report)
        actual_problems = self._actual_problems(report)
        has_concrete_work = self._has_concrete_work(report)

        if has_yesterday:
            completeness += 35
            quality += 25
        else:
            notes.append("нет блока 'Вчера'")

        if has_today:
            completeness += 35
            quality += 25
        else:
            notes.append("нет блока 'Сегодня'")

        if has_problem_section:
            completeness += 15
            quality += 15
        else:
            notes.append("нет блока 'Проблемы/Блокеры'")

        if report.role:
            completeness += 15
            quality += 10
        else:
            notes.append("не указана роль/хэштег")

        if report.jira_keys:
            quality += 15
        elif has_concrete_work:
            quality += 10
        else:
            notes.append("нет привязки к задаче или объекту работ")

        if report.completed_tasks_count >= 2:
            quality += 10
        elif report.completed_tasks_count == 1:
            quality += 5
        elif has_yesterday:
            notes.append("нет выполненных задач за вчера")

        if report.planned_tasks_count == 0 and has_today:
            notes.append("нет плана на сегодня")

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
            problems_count=len(actual_problems),
            jira_count=len(report.jira_keys),
            vague_items_count=vague_count,
            is_late=is_late,
            post_time=post_time,
            notes=list(dict.fromkeys(notes)),
        )

    def _has_problem_section(
        self,
        report: StructuredDailyReport,
    ) -> bool:
        """Проверяет, есть ли в отчете секция проблем или блокеров."""

        if report.problems:
            return True

        raw_text = report.raw_text.lower()

        return bool(
            re.search(
                r"(?im)^\s*(проблемы|проблема|блокеры|блокер|блоккеры|блоккер)\s*:?",
                raw_text,
            )
        )

    def _actual_problems(
        self,
        report: StructuredDailyReport,
    ) -> list[str]:
        """Возвращает только реальные проблемы, исключая 'проблем нет'."""

        actual = []

        for item in report.problems:
            normalized = self._normalize_text(item)

            if not normalized:
                continue

            if normalized in self.NO_PROBLEMS_PHRASES:
                continue

            if any(phrase == normalized for phrase in self.NO_PROBLEMS_PHRASES):
                continue

            actual.append(item)

        return actual

    def _has_concrete_work(
        self,
        report: StructuredDailyReport,
    ) -> bool:
        """Проверяет, есть ли в отчете конкретная работа даже без Jira."""

        items = report.yesterday + report.today

        concrete_items = [
            item for item in items
            if self._is_concrete_item(item)
        ]

        return len(concrete_items) >= 2

    def _vague_items_count(
        self,
        report: StructuredDailyReport,
    ) -> int:
        """Считает расплывчатые формулировки."""

        items = report.yesterday + report.today + self._actual_problems(report)
        count = 0

        for item in items:
            if self._is_vague_item(item):
                count += 1

        return count

    def _is_vague_item(
        self,
        item: str,
    ) -> bool:
        """Проверяет, является ли пункт слишком общим."""

        lower = self._normalize_text(item)

        if not lower:
            return False

        if any(phrase in lower for phrase in self.ALWAYS_VAGUE_PHRASES):
            return True

        if not any(phrase in lower for phrase in self.VAGUE_PHRASES):
            return False

        return not self._is_concrete_item(item)

    def _is_concrete_item(
        self,
        item: str,
    ) -> bool:
        """Проверяет, достаточно ли конкретно описан пункт."""

        lower = self._normalize_text(item)

        if not lower:
            return False

        if len(lower) >= 45:
            return True

        if report_key := re.search(r"[A-ZА-Я]{2,}-\d+", item):
            return bool(report_key)

        if re.search(r"\d+", item):
            return True

        if any(marker in lower for marker in self.CONCRETE_MARKERS):
            return True

        if "/" in item or "\\" in item:
            return True

        if "«" in item or "»" in item or '"' in item:
            return True

        return False

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        """Нормализует текст для проверок."""

        normalized = text.lower().strip()
        normalized = normalized.strip("-—–•* ")
        normalized = re.sub(r"\s+", " ", normalized)

        return normalized
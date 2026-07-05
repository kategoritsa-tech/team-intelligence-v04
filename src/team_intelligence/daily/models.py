from dataclasses import dataclass, field
from datetime import date, datetime, time
import re

from team_intelligence.parser.models import Message


JIRA_PATTERN = re.compile(r"\b[A-ZА-Я]+[A-ZА-Я0-9]*-\d+\b")


@dataclass(slots=True)
class DailyReport:
    """Сырые сообщения одного автора за один отчетный день."""

    author: str
    report_date: date
    messages: list[Message] = field(default_factory=list)

    @property
    def text(self) -> str:
        """Полный текст отчета."""

        return "\n".join(
            message.text
            for message in self.messages
            if message.text
        )

    @property
    def first_message(self) -> Message | None:
        """Первое сообщение отчета."""

        if not self.messages:
            return None

        return self.messages[0]

    @property
    def first_time(self) -> datetime | None:
        """Дата и время первой публикации отчета."""

        if self.first_message is None:
            return None

        return self.first_message.date


@dataclass(slots=True)
class StructuredDailyReport:
    """Структурированный ежедневный отчет сотрудника."""

    author: str
    report_date: date
    role: str | None = None
    yesterday: list[str] = field(default_factory=list)
    today: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    raw_text: str = ""
    first_time: datetime | None = None

    @property
    def completed_tasks_count(self) -> int:
        """Количество пунктов в блоке 'Вчера'."""

        return len(self.yesterday)

    @property
    def planned_tasks_count(self) -> int:
        """Количество пунктов в блоке 'Сегодня'."""

        return len(self.today)

    @property
    def has_problems(self) -> bool:
        """Есть ли реальные проблемы/блокеры."""

        if not self.problems:
            return False

        normalized = " ".join(self.problems).strip().lower()

        return normalized not in {
            "нет",
            "проблем нет",
            "нет проблем",
            "проблемы нет",
            "блокеров нет",
            "нет блокеров",
            "-",
        }

    @property
    def jira_keys(self) -> list[str]:
        """Все найденные Jira-ключи в отчете."""

        return sorted(set(JIRA_PATTERN.findall(self.raw_text)))


@dataclass(slots=True)
class DailyReportMetrics:
    """Метрики качества одного ежедневного отчета."""

    author: str
    report_date: date
    role: str | None
    quality_score: int
    completeness_score: int
    completed_tasks_count: int
    planned_tasks_count: int
    problems_count: int
    jira_count: int
    vague_items_count: int
    is_late: bool
    post_time: time | None
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AuthorDailyMetrics:
    """Сводные метрики ежедневной отчетности по сотруднику."""

    author: str
    reports_count: int
    average_quality: float
    average_completeness: float
    average_completed_tasks: float
    average_planned_tasks: float
    late_reports: int
    reports_with_problems: int
    vague_items_count: int

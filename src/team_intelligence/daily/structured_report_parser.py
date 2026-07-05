import re

from team_intelligence.daily.item_extractor import ItemExtractor
from team_intelligence.daily.models import DailyReport, StructuredDailyReport
from team_intelligence.daily.sections_parser import SectionsParser


class StructuredReportParser:
    """Преобразует DailyReport в StructuredDailyReport."""

    ROLE_PATTERN = re.compile(r"#([\wа-яА-ЯёЁ-]+)")

    def __init__(self):
        self.sections_parser = SectionsParser()
        self.item_extractor = ItemExtractor()

    def parse(self, report: DailyReport) -> StructuredDailyReport:
        """Разбирает ежедневный отчет."""

        sections = self.sections_parser.parse(report.text)

        return StructuredDailyReport(
            author=report.author,
            report_date=report.report_date,
            role=self._extract_role(report.text),
            yesterday=self.item_extractor.extract(sections.yesterday),
            today=self.item_extractor.extract(sections.today),
            problems=self.item_extractor.extract(sections.problems),
            raw_text=report.text,
            first_time=report.first_time,
        )

    def parse_many(self, reports: list[DailyReport]) -> list[StructuredDailyReport]:
        """Разбирает список отчетов."""

        return [self.parse(report) for report in reports]

    def _extract_role(self, text: str) -> str | None:
        """Извлекает роль из хэштега."""

        matches = self.ROLE_PATTERN.findall(text.lower())

        for match in matches:
            if match in {"тест", "аналитика", "анатилика", "разработка"}:
                return "аналитика" if match == "анатилика" else match

        return matches[0] if matches else None

from dataclasses import dataclass

from team_intelligence.daily.text_normalizer import TextNormalizer


@dataclass(slots=True)
class ReportSections:
    """Разделы ежедневного отчета."""

    yesterday: str = ""
    today: str = ""
    problems: str = ""


class SectionsParser:
    """Выделяет разделы ежедневного отчета."""

    HEADINGS = {
        "вчера:": "yesterday",
        "сегодня:": "today",
        "проблемы:": "problems",
    }

    def parse(self, text: str) -> ReportSections:
        """Разбирает отчет на разделы."""

        text = TextNormalizer.normalize(text)
        sections = ReportSections()
        current: str | None = None

        for line in text.splitlines():
            value = line.strip()

            if not value:
                continue

            heading = self.HEADINGS.get(value.lower())

            if heading is not None:
                current = heading
                continue

            if current is None:
                continue

            previous = getattr(sections, current)

            if previous:
                previous += "\n"

            setattr(sections, current, previous + value)

        return sections

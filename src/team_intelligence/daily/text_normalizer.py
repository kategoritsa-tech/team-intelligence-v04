import re


class TextNormalizer:
    """Нормализует текст ежедневного отчета."""

    HEADINGS = {
        "вчера": "Вчера:",
        "что сделал": "Вчера:",
        "сделано": "Вчера:",
        "done": "Вчера:",
        "сегодня": "Сегодня:",
        "что делаю": "Сегодня:",
        "план": "Сегодня:",
        "планы": "Сегодня:",
        "today": "Сегодня:",
        "проблемы": "Проблемы:",
        "проблема": "Проблемы:",
        "проблемы/блокеры": "Проблемы:",
        "проблемы/блоккеры": "Проблемы:",
        "блокеры": "Проблемы:",
        "блоккеры": "Проблемы:",
        "blockers": "Проблемы:",
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        """Приводит текст к единому виду."""

        result = text.strip().replace("\r\n", "\n").replace("\r", "\n")
        result = re.sub(r"\n{3,}", "\n\n", result)

        for source, target in cls.HEADINGS.items():
            result = re.sub(
                rf"(?im)^\s*{re.escape(source)}\s*:?\s*$",
                target,
                result,
            )
            result = re.sub(
                rf"(?im)^\s*{re.escape(source)}\s*[:—-]\s*",
                f"{target}\n",
                result,
            )
            result = re.sub(
                rf"(?im)^\s*[-—–*•✔✓]?\s*{re.escape(source)}\s+",
                f"{target}\n",
                result,
            )

        return result

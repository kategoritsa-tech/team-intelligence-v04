import re


class TextNormalizer:
    """Нормализует текст ежедневного отчета."""

    HEADINGS = {
        "вчера": "Вчера:",
        "сегодня": "Сегодня:",

        "проблемы": "Проблемы:",
        "проблема": "Проблемы:",
        "проблемы/блокеры": "Проблемы:",
        "проблемы/блоккеры": "Проблемы:",

        "блокеры": "Проблемы:",
        "блокер": "Проблемы:",
        "блоккеры": "Проблемы:",
        "блоккер": "Проблемы:",
        "блокеры/проблемы": "Проблемы:",
        "блоккеры/проблемы": "Проблемы:",
    }

    @classmethod
    def normalize(
        cls,
        text: str,
    ) -> str:
        """Приводит текст к единому виду."""

        result = text.strip()
        result = result.replace("\r\n", "\n")
        result = result.replace("\r", "\n")

        result = re.sub(
            r"\n{2,}",
            "\n",
            result,
        )

        # Нормализуем заголовки вида:
        # вчера:
        # Вчера
        # СЕГОДНЯ:
        for source, target in cls.HEADINGS.items():
            result = re.sub(
                rf"(?im)^\s*{re.escape(source)}\s*:?\s*$",
                target,
                result,
            )

        # Нормализуем строки вида:
        # вчера сделал ...
        # сегодня занимаюсь ...
        result = re.sub(
            r"(?im)^\s*вчера\s+(.+)$",
            r"Вчера:\n\1",
            result,
        )

        result = re.sub(
            r"(?im)^\s*сегодня\s+(.+)$",
            r"Сегодня:\n\1",
            result,
        )

        return result
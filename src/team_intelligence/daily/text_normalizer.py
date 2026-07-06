import re


class TextNormalizer:
    """Нормализует текст ежедневного отчета."""

    HEADINGS = {
        "вчера": "Вчера:",
        "сегодня": "Сегодня:",

        "проблемы/блокеры": "Проблемы:",
        "проблемы/блоккеры": "Проблемы:",
        "блокеры/проблемы": "Проблемы:",
        "блоккеры/проблемы": "Проблемы:",

        "проблемы": "Проблемы:",
        "проблема": "Проблемы:",
        "блокеры": "Проблемы:",
        "блокер": "Проблемы:",
        "блоккеры": "Проблемы:",
        "блоккер": "Проблемы:",
    }

    @classmethod
    def normalize(
        cls,
        text: str,
    ) -> str:
        """Приводит текст daily-отчета к единому виду."""

        result = text.strip()
        result = result.replace("\r\n", "\n")
        result = result.replace("\r", "\n")

        lines = result.split("\n")
        normalized_lines = []

        heading_variants = sorted(
            cls.HEADINGS.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for line in lines:
            original_line = line.strip()

            if not original_line:
                continue

            normalized_line = cls._normalize_line_with_heading(
                original_line,
                heading_variants,
            )

            normalized_lines.extend(normalized_line)

        result = "\n".join(normalized_lines)

        result = re.sub(
            r"\n{2,}",
            "\n",
            result,
        )

        return result.strip()

    @classmethod
    def _normalize_line_with_heading(
        cls,
        line: str,
        heading_variants: list[tuple[str, str]],
    ) -> list[str]:
        """Нормализует строку, если она начинается с заголовка секции."""

        line_without_bullet = re.sub(
            r"^\s*[-—–•*]+\s*",
            "",
            line,
        ).strip()

        for source, target in heading_variants:
            pattern = rf"^{re.escape(source)}\s*(?:[:：\-—–])?\s*(.*)$"

            match = re.match(
                pattern,
                line_without_bullet,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            content = match.group(1).strip()
            content = re.sub(
                r"^\s*[-—–•*]+\s*",
                "",
                content,
            ).strip()

            if not content:
                return [target]

            return [
                target,
                f"- {content}",
            ]

        return [line]
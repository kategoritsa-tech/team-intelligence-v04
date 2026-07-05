import re


class ItemExtractor:
    """Извлекает пункты из разделов ежедневного отчета."""

    PREFIXES = ("-", "—", "–", "*", "•", "✔", "✓")
    JIRA_PATTERN = re.compile(r"\b[A-ZА-Я]+[A-ZА-Я0-9]*-\d+\b")

    ACTION_STARTS = (
        "закрыл",
        "закрыла",
        "сделал",
        "сделала",
        "написал",
        "написала",
        "перенес",
        "перенесла",
        "перенёс",
        "перенесла",
        "отправил",
        "отправила",
        "тестировал",
        "тестировала",
        "занимался",
        "занималась",
        "актуализировал",
        "актуализировала",
        "помощь",
        "вопросы",
        "анализ",
        "созвон",
        "фикс",
        "фиксы",
        "продолжить",
        "взять",
        "ждать",
        "писать",
    )

    def extract(self, text: str) -> list[str]:
        """Возвращает список пунктов."""

        items: list[str] = []
        current: str | None = None

        for raw_line in text.splitlines():
            line = self._clean_line(raw_line)

            if not line:
                continue

            starts_new_item = self._starts_new_item(raw_line, line, current)

            if starts_new_item:
                if current:
                    items.append(current)
                current = line
            else:
                if current:
                    current = f"{current} {line}"
                else:
                    current = line

        if current:
            items.append(current)

        return [item.strip() for item in items if item.strip()]

    def _clean_line(self, line: str) -> str:
        """Удаляет маркеры списка."""

        value = line.strip()

        for prefix in self.PREFIXES:
            if value.startswith(prefix):
                return value[len(prefix):].strip()

        return value

    def _starts_new_item(
        self,
        raw_line: str,
        line: str,
        current: str | None,
    ) -> bool:
        """Определяет, начинается ли новая задача."""

        stripped = raw_line.strip()

        if stripped.startswith(self.PREFIXES):
            return True

        if current is None:
            return True

        lower = line.lower()

        if lower.startswith(self.ACTION_STARTS):
            return True

        if self.JIRA_PATTERN.search(line) and self.JIRA_PATTERN.search(current or ""):
            return True

        return False

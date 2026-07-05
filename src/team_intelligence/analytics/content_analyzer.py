from collections import Counter

from team_intelligence.parser.models import Message

try:
    from pymorphy3 import MorphAnalyzer
except ImportError:  # pragma: no cover - optional dependency
    MorphAnalyzer = None


class ContentAnalyzer:
    """Анализ текста сообщений."""

    def __init__(self, messages: list[Message]):
        self.messages = messages
        self.morph = MorphAnalyzer() if MorphAnalyzer is not None else None

    def longest_messages(self, limit: int = 10) -> list[Message]:
        """Самые длинные сообщения."""

        messages = [
            message
            for message in self.messages
            if message.text.strip()
        ]

        return sorted(
            messages,
            key=lambda message: len(message.text),
            reverse=True,
        )[:limit]

    def all_words(self) -> list[str]:
        """Возвращает все слова из сообщений."""

        stop_words = {
            "цпиг",
            "продя",
            "анатилик",
        }

        words = []

        for message in self.messages:
            if not message.text:
                continue

            text = message.text.lower()

            for word in text.split():
                word = word.strip(".,!?():;\"'[]{}«»#")

                if len(word) < 4:
                    continue

                normal_word = self.normalize_word(word)

                if normal_word in stop_words:
                    continue

                words.append(normal_word)

        return words

    def normalize_word(self, word: str) -> str:
        """Нормализует слово, если доступен pymorphy3."""

        if self.morph is None:
            return word

        return self.morph.parse(word)[0].normal_form

    def hashtags(self) -> list[str]:
        """Возвращает все хэштеги."""

        tags = []

        for message in self.messages:
            if not message.text:
                continue

            for word in message.text.split():
                if word.startswith("#"):
                    tags.append(word.lower())

        return tags

    def most_common_hashtags(self, limit: int = 10) -> list[tuple[str, int]]:
        """Самые популярные хэштеги."""

        return Counter(self.hashtags()).most_common(limit)

    def most_common_words(self, limit: int = 20) -> list[tuple[str, int]]:
        """Самые популярные слова."""

        stop_words = {
            "сегодня",
            "вчера",
            "завтра",
            "понедельник",
            "вторник",
            "среда",
            "четверг",
            "пятница",
            "суббота",
            "воскресенье",
            "проде",
            "работа",
            "написала",
            "планирую",
            "коллегам",
            "обращениями",
        }

        words = [word for word in self.all_words() if word not in stop_words]

        return Counter(words).most_common(limit)

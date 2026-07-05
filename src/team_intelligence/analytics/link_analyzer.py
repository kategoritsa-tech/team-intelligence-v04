import re

from team_intelligence.parser.models import Message
from collections import Counter
from urllib.parse import urlparse


class LinkAnalyzer:
    """Анализ ссылок в сообщениях."""

    def __init__(self, messages: list[Message]):
        self.messages = messages

    def all_links(self) -> list[str]:
        """Возвращает все ссылки из сообщений."""

        links = []

        for message in self.messages:

            if not message.text:
                continue

            found = re.findall(r"https?://\S+", message.text)

            links.extend(found)

        return links

    def most_common_domains(self, limit: int = 10) -> list[tuple[str, int]]:
        """Самые популярные домены."""

        domains = []

        for link in self.all_links():
            domain = urlparse(link).netloc.lower()

            if domain.startswith("www."):
                domain = domain[4:]

            domains.append(domain)

        return Counter(domains).most_common(limit)
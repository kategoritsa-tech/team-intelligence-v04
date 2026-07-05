from pathlib import Path
from datetime import datetime

from bs4 import BeautifulSoup

from team_intelligence.parser.models import Message


class TelegramParser:
    """Парсер HTML-экспорта Telegram."""

    def __init__(self):
        self.last_author = None

    def read_html(self, file_path: Path) -> str:
        """Читает HTML-файл и возвращает его содержимое."""

        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        return file_path.read_text(encoding="utf-8")

    def get_messages(self, html: str) -> list[Message]:
        """Возвращает список сообщений."""

        soup = BeautifulSoup(html, "html.parser")
        html_messages = soup.find_all("div", class_="message")

        messages = []

        for html_message in html_messages:
            message = self.parse_message(html_message)

            if message is not None:
                messages.append(message)

        return messages

    def parse_message(self, message_div) -> Message | None:
        """Преобразует HTML-блок сообщения в объект Message."""

        # ---------- ID сообщения ----------
        message_id = -1

        message_id_attr = message_div.get("id")

        if message_id_attr:
            try:
                message_id = int(message_id_attr.replace("message", ""))
            except ValueError:
                pass

        # ---------- Автор ----------
        author_div = message_div.find("div", class_="from_name")

        if author_div is not None:
            self.last_author = author_div.get_text(strip=True)

        if self.last_author is None:
            return None

        # ---------- Дата ----------
        date = None

        date_div = message_div.find("div", class_="pull_right date details")

        if date_div:
            raw_date = date_div.get("title")

            if raw_date:
                try:
                    date = datetime.strptime(
                        raw_date,
                        "%d.%m.%Y %H:%M:%S UTC%z",
                    )
                except ValueError:
                    pass

        # ---------- Текст ----------
        text = ""

        text_div = message_div.find("div", class_="text")

        if text_div:
            text = text_div.get_text("\n", strip=True)

        # ---------- Ответ ----------
        reply_to_message_id = None

        reply_div = message_div.find("div", class_="reply_to")

        if reply_div:
            link = reply_div.find("a")

            if link:
                href = link.get("href", "")

                if href.startswith("#go_to_message"):
                    try:
                        reply_to_message_id = int(
                            href.replace("#go_to_message", "")
                        )
                    except ValueError:
                        pass

        has_media = False
        media_type = None

        if message_div.find("div", class_="media_wrap"):
            has_media = True

            if message_div.find("div", class_="photo"):
                media_type = "photo"

            elif message_div.find("div", class_="video_file"):
                media_type = "video"

            elif message_div.find("div", class_="voice_message"):
                media_type = "voice"

            elif message_div.find("div", class_="audio_file"):
                media_type = "audio"

            elif message_div.find("div", class_="file"):
                media_type = "document"

            else:
                media_type = "other"

        return Message(
            message_id=message_id,
            author=self.last_author,
            date=date,
            text=text,
            reply_to_message_id=reply_to_message_id,
            has_media=has_media,
            media_type=media_type,
        )
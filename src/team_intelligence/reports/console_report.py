from team_intelligence.analytics.activity_analyzer import ActivityAnalyzer
from team_intelligence.analytics.attachment_analyzer import AttachmentAnalyzer
from team_intelligence.analytics.communication_analyzer import CommunicationAnalyzer
from team_intelligence.analytics.content_analyzer import ContentAnalyzer
from team_intelligence.analytics.link_analyzer import LinkAnalyzer
from team_intelligence.analytics.mention_analyzer import MentionAnalyzer


class ConsoleReport:
    """Вывод статистики в консоль."""

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.activity = ActivityAnalyzer(analyzer.messages)
        self.content = ContentAnalyzer(analyzer.messages)
        self.mentions = MentionAnalyzer(analyzer.messages)
        self.communication = CommunicationAnalyzer(analyzer.messages)
        self.links = LinkAnalyzer(analyzer.messages)
        self.attachments = AttachmentAnalyzer(analyzer.messages)

    def show(self):
        print("✅ Файл открыт успешно")
        print(f"💬 Найдено сообщений: {self.analyzer.total_messages()}")
        print(f"👥 Участников: {self.analyzer.unique_authors()}")

        self.show_top_authors()
        self.show_activity_by_day()
        self.show_activity_by_hour()
        self.show_longest_messages()
        self.show_common_words()
        self.show_mentions()
        self.show_hashtags()
        self.show_communications()
        self.show_links()
        self.show_attachments()

    def show_top_authors(self):
        print("\n🏆 Самые активные авторы:\n")

        for author, count in self.analyzer.messages_by_author().most_common(10):
            print(f"{author:.<35} {count:>4}")

    def show_activity_by_day(self):
        print("\n📅 Активность по дням:\n")

        messages_by_day = self.activity.messages_by_day()

        for day, count in sorted(messages_by_day.items()):
            print(f"{day}  {'█' * min(count // 2, 40)} {count}")

        if not messages_by_day:
            return

        most_active_day = max(
            messages_by_day.items(),
            key=lambda item: item[1],
        )[0]

        print("\n🔥 Самый активный день:\n")
        print(most_active_day)
        print(f"\nСообщений: {len(self.activity.messages_for_day(most_active_day))}")

    def show_activity_by_hour(self):
        print("\n🕒 Активность по часам:\n")

        for hour, count in sorted(self.activity.messages_by_hour().items()):
            print(f"{hour:02d}:00  {'█' * min(count // 2, 40)} {count}")

    def show_longest_messages(self):
        print("\n📝 Самые длинные сообщения:\n")

        for message in self.content.longest_messages(5):
            print("=" * 60)
            print(message.author)
            print(message.date)
            print(f"{len(message.text)} символов\n")

            preview = message.text

            if len(preview) > 300:
                preview = preview[:300] + "..."

            print(preview)

    def show_common_words(self):
        print("\n🧠 Самые популярные слова:\n")

        for word, count in self.content.most_common_words(20):
            print(f"{word:.<25} {count}")

    def show_mentions(self):
        print("\n👤 Самые упоминаемые пользователи:\n")

        for user, count in self.mentions.most_mentioned(10):
            print(f"{user:.<25} {count}")

    def show_hashtags(self):
        print("\n🏷 Самые популярные хэштеги:\n")

        for tag, count in self.content.most_common_hashtags(10):
            print(f"{tag:.<25} {count}")

    def show_communications(self):
        print("\n🤝 Самые частые коммуникации:\n")

        for (author, mention), count in self.communication.communication_pairs(10):
            print(f"{author} → {mention} ({count})")

    def show_links(self):
        print("\n🔗 Самые популярные сайты:\n")

        for domain, count in self.links.most_common_domains(10):
            print(f"{domain:.<35} {count}")

    def show_attachments(self):
        print("\n📎 Вложения:\n")
        print(f"Всего вложений: {self.attachments.total_attachments()}")

        print("\nТипы вложений:\n")

        for media_type, count in self.attachments.attachments_by_type().items():
            print(f"{media_type:.<20} {count}")

        print("\n👤 Кто чаще всего отправляет вложения:\n")

        for author, count in self.attachments.top_attachment_authors(10):
            print(f"{author:.<35} {count}")
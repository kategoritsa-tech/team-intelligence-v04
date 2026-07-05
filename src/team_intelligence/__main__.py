from pathlib import Path
import argparse

from team_intelligence.analytics.statistics_analyzer import StatisticsAnalyzer
from team_intelligence.daily.quality_analyzer import DailyQualityAnalyzer
from team_intelligence.daily.report_builder import DailyReportBuilder
from team_intelligence.daily.structured_report_parser import StructuredReportParser
from team_intelligence.parser.telegram_parser import TelegramParser
from team_intelligence.reports.console_report import ConsoleReport
from team_intelligence.reports.excel_exporter import ExcelExporter
from team_intelligence.reports.exporter import ReportExporter
from team_intelligence.reports.pdf_exporter import PdfExporter


def resolve_input_path(raw_path: str | None) -> Path:
    """Определяет путь к HTML-экспорту Telegram."""

    candidates = []

    if raw_path:
        candidates.append(Path(raw_path))

    candidates.extend(
        [
            Path("data/messages.html"),
            Path("../data/messages.html"),
            Path("examples/minimal/messages.html"),
            Path("../examples/minimal/messages.html"),
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


def main():
    parser_args = argparse.ArgumentParser(
        description="Team Intelligence — анализ daily-отчетов из Telegram HTML export."
    )
    parser_args.add_argument(
        "--input",
        "-i",
        help="Путь к messages.html",
        default=None,
    )
    parser_args.add_argument(
        "--reports-dir",
        "-o",
        help="Папка для отчетов",
        default="reports",
    )

    args = parser_args.parse_args()

    print("=" * 50)
    print("🚀 Team Intelligence v0.4")
    print("=" * 50)

    file_path = resolve_input_path(args.input)
    reports_dir = Path(args.reports_dir)

    parser = TelegramParser()

    try:
        html = parser.read_html(file_path)
        messages = parser.get_messages(html)

        analyzer = StatisticsAnalyzer(messages)

        daily_builder = DailyReportBuilder(messages)
        daily_reports = daily_builder.build()

        structured_parser = StructuredReportParser()
        structured_reports = structured_parser.parse_many(daily_reports)

        quality_analyzer = DailyQualityAnalyzer(structured_reports)
        report_metrics = quality_analyzer.report_metrics()
        author_daily_metrics = quality_analyzer.author_metrics()

        ConsoleReport(analyzer).show()

        print("\n🧾 Daily-отчеты:")
        print(f"Найдено отчетов: {len(structured_reports)}")

        if report_metrics:
            average_quality = round(
                sum(metric.quality_score for metric in report_metrics) / len(report_metrics),
                1,
            )
            print(f"Среднее качество: {average_quality}")

        exporter = ReportExporter(reports_dir)

        report = (
            "Team Intelligence\n"
            "=================\n\n"
            f"Файл: {file_path}\n"
            f"Сообщений: {analyzer.total_messages()}\n"
            f"Участников: {analyzer.unique_authors()}\n"
            f"Daily-отчетов: {len(structured_reports)}\n"
        )

        report_path = exporter.export_text("report.txt", report)

        authors_path = exporter.export_csv(
            "authors.csv",
            ["Автор", "Количество сообщений"],
            [
                [author, count]
                for author, count in analyzer.messages_by_author().most_common()
            ],
        )

        reports_by_key = {
            (report.author, report.report_date): report
            for report in structured_reports
        }

        daily_path = exporter.export_csv(
            "daily_metrics.csv",
            [
                "Дата",
                "Автор",
                "Роль",
                "Качество",
                "Полнота",
                "Сделано",
                "План",
                "Проблемы",
                "Jira",
                "Опоздал",
                "Текст отчета",
                "Замечания",
            ],
            [
                [
                    metric.report_date,
                    metric.author,
                    metric.role,
                    metric.quality_score,
                    metric.completeness_score,
                    metric.completed_tasks_count,
                    metric.planned_tasks_count,
                    metric.problems_count,
                    metric.jira_count,
                    "Да" if metric.is_late else "Нет",
                    reports_by_key[
                        (metric.author, metric.report_date)
                    ].raw_text,
                    "; ".join(metric.notes),
                ]
                for metric in report_metrics
            ],
        )

        excel_exporter = ExcelExporter(reports_dir)
        excel_path = excel_exporter.export_summary(
            analyzer,
            structured_reports=structured_reports,
            report_metrics=report_metrics,
            author_daily_metrics=author_daily_metrics,
        )

        pdf_exporter = PdfExporter(reports_dir)
        pdf_path = pdf_exporter.export_summary(
            analyzer,
            report_metrics=report_metrics,
            author_daily_metrics=author_daily_metrics,
        )

        print(f"\n📄 TXT отчет сохранен: {report_path}")
        print(f"📊 CSV авторов сохранен: {authors_path}")
        print(f"🧾 CSV daily-метрик сохранен: {daily_path}")
        print(f"📗 Excel отчет сохранен: {excel_path}")
        print(f"📕 PDF отчет сохранен: {pdf_path}")

    except FileNotFoundError:
        print(f"❌ Файл не найден: {file_path}")
        print("Укажи файл явно: python -m team_intelligence --input path/to/messages.html")


if __name__ == "__main__":
    main()

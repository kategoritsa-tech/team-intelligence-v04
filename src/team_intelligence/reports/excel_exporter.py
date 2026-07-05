from datetime import date, datetime, time
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from team_intelligence.analytics.activity_analyzer import ActivityAnalyzer
from team_intelligence.daily.models import AuthorDailyMetrics, DailyReportMetrics, StructuredDailyReport


class ExcelExporter:
    """Экспорт аналитики в Excel."""

    HEADER_FILL = PatternFill(fill_type="solid", fgColor="4472C4")
    HEADER_FONT = Font(bold=True, color="FFFFFF")
    HEADER_ALIGNMENT = Alignment(horizontal="center", vertical="center")

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_summary(
        self,
        analyzer,
        structured_reports: list[StructuredDailyReport] | None = None,
        report_metrics: list[DailyReportMetrics] | None = None,
        author_daily_metrics: list[AuthorDailyMetrics] | None = None,
    ) -> Path:
        """Создает Excel-отчет."""

        workbook = Workbook()

        self.create_summary_sheet(workbook, analyzer, structured_reports, report_metrics)
        self.create_authors_sheet(workbook, analyzer)
        self.create_activity_sheet(workbook, analyzer)
        self.create_messages_sheet(workbook, analyzer)

        if structured_reports is not None:
            self.create_daily_reports_sheet(workbook, structured_reports, report_metrics or [])

        if author_daily_metrics is not None:
            self.create_daily_authors_sheet(workbook, author_daily_metrics)

        file_path = self.output_dir / "team_intelligence.xlsx"
        workbook.save(file_path)

        return file_path

    def create_summary_sheet(
        self,
        workbook,
        analyzer,
        structured_reports: list[StructuredDailyReport] | None = None,
        report_metrics: list[DailyReportMetrics] | None = None,
    ):
        """Создает лист Summary."""

        sheet = workbook.active
        sheet.title = "Summary"

        sheet.append(["Показатель", "Значение"])
        sheet.append(["💬 Количество сообщений", analyzer.total_messages()])
        sheet.append(["👥 Количество участников", analyzer.unique_authors()])
        sheet.append(["📅 Первый день", self.excel_safe_value(analyzer.first_message_date())])
        sheet.append(["📅 Последний день", self.excel_safe_value(analyzer.last_message_date())])
        sheet.append(["📆 Длительность переписки", f"{analyzer.days_count()} дней"])
        sheet.append(["📈 Среднее сообщений в день", analyzer.average_messages_per_day()])
        sheet.append(["🏆 Самый активный автор", analyzer.top_author()])

        if structured_reports is not None:
            sheet.append(["🧾 Найдено daily-отчетов", len(structured_reports)])

        if report_metrics:
            average_quality = round(
                sum(metric.quality_score for metric in report_metrics) / len(report_metrics),
                1,
            )
            average_completeness = round(
                sum(metric.completeness_score for metric in report_metrics) / len(report_metrics),
                1,
            )
            late_reports = sum(1 for metric in report_metrics if metric.is_late)
            sheet.append(["⭐ Среднее качество daily", average_quality])
            sheet.append(["✅ Средняя полнота daily", average_completeness])
            sheet.append(["⏰ Опоздавших отчетов", late_reports])

        self.format_sheet(sheet)

    def create_authors_sheet(self, workbook, analyzer):
        """Создает лист Authors."""

        sheet = workbook.create_sheet("Authors")
        sheet.append(["Автор", "Количество сообщений"])

        for author, count in analyzer.messages_by_author().most_common():
            sheet.append([author, count])

        self.format_sheet(sheet)

    def create_activity_sheet(self, workbook, analyzer):
        """Создает лист Activity."""

        sheet = workbook.create_sheet("Activity")
        sheet.append(["Дата", "Количество сообщений"])

        activity_analyzer = ActivityAnalyzer(analyzer.messages)

        for day, count in sorted(activity_analyzer.messages_by_day().items()):
            sheet.append([self.excel_safe_value(day), count])

        self.format_sheet(sheet)
        self.add_activity_chart(sheet)

    def add_activity_chart(self, sheet):
        """Добавляет график активности."""

        if sheet.max_row < 2:
            return

        chart = LineChart()
        chart.title = "Активность по дням"
        chart.style = 2
        chart.y_axis.title = "Сообщений"
        chart.x_axis.title = "Дата"

        values = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row)
        dates = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)

        chart.add_data(values, titles_from_data=True, from_rows=False)
        chart.set_categories(dates)
        chart.width = 18
        chart.height = 8

        sheet.add_chart(chart, "D2")

    def create_messages_sheet(self, workbook, analyzer):
        """Создает лист со всеми сообщениями."""

        sheet = workbook.create_sheet("Messages")
        sheet.append(["Дата", "Автор", "Сообщение", "Вложение"])

        for message in analyzer.messages:
            sheet.append(
                [
                    self.excel_safe_value(message.date),
                    message.author,
                    message.text,
                    "Да" if message.has_media else "Нет",
                ]
            )

        self.format_sheet(sheet)

    def create_daily_reports_sheet(
        self,
        workbook,
        structured_reports: list[StructuredDailyReport],
        report_metrics: list[DailyReportMetrics],
    ):
        """Создает лист с разбором daily-отчетов."""

        metrics_by_key = {
            (metric.author, metric.report_date): metric
            for metric in report_metrics
        }

        sheet = workbook.create_sheet("Daily Reports")
        sheet.append(
            [
                "Дата",
                "Автор",
                "Роль",
                "Время",
                "Вчера задач",
                "Сегодня задач",
                "Проблемы",
                "Jira",
                "Качество",
                "Полнота",
                "Опоздал",
                "Текст отчета",
                "Замечания",
            ]
        )

        for report in structured_reports:
            metric = metrics_by_key.get((report.author, report.report_date))
            sheet.append(
                [
                    self.excel_safe_value(report.report_date),
                    report.author,
                    report.role,
                    self.excel_safe_value(metric.post_time if metric else None),
                    report.completed_tasks_count,
                    report.planned_tasks_count,
                    len(report.problems) if report.has_problems else 0,
                    len(report.jira_keys),
                    metric.quality_score if metric else None,
                    metric.completeness_score if metric else None,
                    "Да" if metric and metric.is_late else "Нет",
                    report.raw_text,
                    "; ".join(metric.notes) if metric else "",
                ]
            )

        self.format_sheet(sheet)

    def create_daily_authors_sheet(
        self,
        workbook,
        author_metrics: list[AuthorDailyMetrics],
    ):
        """Создает лист со сводкой по сотрудникам."""

        sheet = workbook.create_sheet("Daily Authors")
        sheet.append(
            [
                "Автор",
                "Отчетов",
                "Среднее качество",
                "Средняя полнота",
                "Среднее сделано",
                "Среднее план",
                "Опозданий",
                "Отчетов с проблемами",
                "Уклончивых пунктов",
            ]
        )

        for metric in author_metrics:
            sheet.append(
                [
                    metric.author,
                    metric.reports_count,
                    metric.average_quality,
                    metric.average_completeness,
                    metric.average_completed_tasks,
                    metric.average_planned_tasks,
                    metric.late_reports,
                    metric.reports_with_problems,
                    metric.vague_items_count,
                ]
            )

        self.format_sheet(sheet)

    def excel_safe_value(self, value):
        """Преобразует значения в формат, безопасный для Excel."""

        if isinstance(value, datetime):
            return value.replace(tzinfo=None)

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, time):
            return value.strftime("%H:%M")

        return value

    def format_sheet(self, sheet):
        """Оформляет лист Excel."""

        for cell in sheet[1]:
            cell.fill = self.HEADER_FILL
            cell.font = self.HEADER_FONT
            cell.alignment = self.HEADER_ALIGNMENT

        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions

        for column in sheet.columns:
            max_length = max(
                len(str(cell.value)) if cell.value else 0
                for cell in column
            )

            sheet.column_dimensions[get_column_letter(column[0].column)].width = min(
                max_length + 3,
                80,
            )

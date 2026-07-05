from pathlib import Path
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PdfExporter:
    """Экспорт аналитики в PDF."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.font_name = self.register_font()

    def register_font(self) -> str:
        """Регистрирует Unicode-шрифт для кириллицы."""

        font_candidates = [
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for font_path in font_candidates:
            if os.path.exists(font_path):
                font_name = "SystemFont"
                if font_name not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name

        return "Helvetica"

    def export_summary(
        self,
        analyzer,
        report_metrics=None,
        author_daily_metrics=None,
    ) -> Path:
        """Создает PDF-отчет."""

        file_path = self.output_dir / "team_intelligence.pdf"
        document = SimpleDocTemplate(
            str(file_path),
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = self.build_styles()
        story = []

        story.append(Paragraph("Team Intelligence", styles["TitleCustom"]))
        story.append(Paragraph("Аналитический отчет по daily-коммуникации", styles["Subtitle"]))
        story.append(Spacer(1, 0.5 * cm))

        summary_rows = [
            ["Показатель", "Значение"],
            ["Количество сообщений", analyzer.total_messages()],
            ["Количество участников", analyzer.unique_authors()],
            ["Первый день", analyzer.first_message_date()],
            ["Последний день", analyzer.last_message_date()],
            ["Длительность", f"{analyzer.days_count()} дней"],
            ["Среднее сообщений в день", analyzer.average_messages_per_day()],
            ["Самый активный автор", analyzer.top_author()],
        ]

        if report_metrics:
            avg_quality = round(sum(m.quality_score for m in report_metrics) / len(report_metrics), 1)
            avg_completeness = round(sum(m.completeness_score for m in report_metrics) / len(report_metrics), 1)
            late_count = sum(1 for m in report_metrics if m.is_late)
            summary_rows.extend(
                [
                    ["Daily-отчетов", len(report_metrics)],
                    ["Среднее качество daily", avg_quality],
                    ["Средняя полнота daily", avg_completeness],
                    ["Опоздавших отчетов", late_count],
                ]
            )

        story.append(self.make_table(summary_rows))

        if author_daily_metrics:
            story.append(PageBreak())
            story.append(Paragraph("Сводка по сотрудникам", styles["Heading1"]))
            rows = [["Автор", "Отчетов", "Качество", "Полнота", "Сделано", "Опозданий"]]

            for metric in sorted(author_daily_metrics, key=lambda item: item.average_quality, reverse=True)[:30]:
                rows.append(
                    [
                        metric.author,
                        metric.reports_count,
                        metric.average_quality,
                        metric.average_completeness,
                        metric.average_completed_tasks,
                        metric.late_reports,
                    ]
                )

            story.append(self.make_table(rows))

        document.build(story)

        return file_path

    def build_styles(self):
        """Создает стили PDF."""

        styles = getSampleStyleSheet()

        for style_name in styles.byName:
            styles[style_name].fontName = self.font_name

        styles.add(
            ParagraphStyle(
                name="TitleCustom",
                parent=styles["Title"],
                fontName=self.font_name,
                fontSize=28,
                leading=34,
                spaceAfter=12,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Subtitle",
                parent=styles["BodyText"],
                fontName=self.font_name,
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#555555"),
            )
        )

        return styles

    def make_table(self, rows):
        """Создает оформленную таблицу."""

        table = Table(rows, repeatRows=1, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        return table

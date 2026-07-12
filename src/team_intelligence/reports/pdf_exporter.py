from pathlib import Path
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from team_intelligence.daily.missed_report_analyzer import MissedReportAnalyzer


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
                    pdfmetrics.registerFont(
                        TTFont(
                            font_name,
                            font_path,
                        )
                    )

                return font_name

        return "Helvetica"

    def export_summary(
        self,
        analyzer,
        report_metrics=None,
        author_daily_metrics=None,
    ) -> Path:
        """Создает краткий управленческий PDF-отчет."""

        metrics = report_metrics or []
        author_metrics = author_daily_metrics or []

        missed_analyzer = MissedReportAnalyzer(metrics)
        missed_reports = missed_analyzer.missed_reports()
        missed_authors = missed_analyzer.authors_with_missed_reports()
        missed_count_by_author = missed_analyzer.missed_count_by_author()

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

        story.append(
            Paragraph(
                "Team Intelligence",
                styles["TitleCustom"],
            )
        )
        story.append(
            Paragraph(
                "Управленческий отчет по daily-отчетам команды",
                styles["Subtitle"],
            )
        )
        story.append(Spacer(1, 0.5 * cm))

        total_reports = len(metrics)

        if total_reports > 0:
            avg_quality = round(
                sum(metric.quality_score for metric in metrics) / total_reports,
                1,
            )
            avg_completeness = round(
                sum(metric.completeness_score for metric in metrics) / total_reports,
                1,
            )
        else:
            avg_quality = 0
            avg_completeness = 0

        late_reports = sum(
            1 for metric in metrics
            if metric.is_late
        )

        reports_without_completed = sum(
            1 for metric in metrics
            if metric.completed_tasks_count == 0
        )

        reports_without_plan = sum(
            1 for metric in metrics
            if metric.planned_tasks_count == 0
        )

        reports_with_problems = sum(
            1 for metric in metrics
            if metric.problems_count > 0
        )

        def metric_reasons(metric):
            reasons = []

            if metric.quality_score < 70:
                reasons.append("низкое качество")

            if metric.completeness_score < 80:
                reasons.append("неполный отчет")

            if metric.is_late:
                reasons.append("после дедлайна")

            if metric.completed_tasks_count == 0:
                reasons.append("нет выполненных задач")

            if metric.planned_tasks_count == 0:
                reasons.append("нет плана")

            if metric.problems_count > 0:
                reasons.append("есть проблемы/блокеры")

            for note in metric.notes:
                note_lower = note.lower()

                if "мало конкретики" in note_lower:
                    reasons.append("мало конкретики")

                if "нет привязки" in note_lower or "jira" in note_lower or "джира" in note_lower:
                    reasons.append("нет привязки к задаче")

            return list(dict.fromkeys(reasons))

        problematic_metrics = [
            metric for metric in metrics
            if metric_reasons(metric)
        ]

        if total_reports > 0:
            problematic_percent = round(
                len(problematic_metrics) / total_reports * 100,
                1,
            )
        else:
            problematic_percent = 0

        story.append(
            Paragraph(
                "1. Сводка",
                styles["Heading1"],
            )
        )

        summary_rows = [
            ["Метрика", "Значение"],
            ["Всего сообщений", analyzer.total_messages()],
            ["Участников", analyzer.unique_authors()],
            [
                "Период",
                f"{analyzer.first_message_date()} — {analyzer.last_message_date()}",
            ],
            ["Daily-отчетов", total_reports],
            ["Среднее качество", avg_quality],
            ["Средняя полнота", avg_completeness],
            ["Проблемных отчетов", len(problematic_metrics)],
            ["Доля проблемных отчетов", f"{problematic_percent}%"],
            ["Пропущенных отчетов", len(missed_reports)],
            ["Авторов с пропусками", len(missed_authors)],
        ]

        story.append(self.make_table(summary_rows))
        story.append(Spacer(1, 0.4 * cm))

        story.append(
            Paragraph(
                "2. Ключевые риски",
                styles["Heading1"],
            )
        )

        risk_rows = [
            ["Риск", "Значение"],
            ["Отчетов после дедлайна", late_reports],
            ["Отчетов без выполненных задач", reports_without_completed],
            ["Отчетов без плана", reports_without_plan],
            ["Отчетов с проблемами/блокерами", reports_with_problems],
            ["Пропущенных отчетов", len(missed_reports)],
            ["Авторов с пропусками", len(missed_authors)],
        ]

        story.append(self.make_table(risk_rows))
        story.append(Spacer(1, 0.4 * cm))

        story.append(
            Paragraph(
                "3. Проблемные отчеты",
                styles["Heading1"],
            )
        )

        problem_rows = [
            ["Дата", "Автор", "Качество", "Полнота", "Причина"],
        ]

        for metric in sorted(
            problematic_metrics,
            key=lambda item: (
                item.quality_score,
                item.completeness_score,
            ),
        )[:25]:
            problem_rows.append(
                [
                    metric.report_date,
                    metric.author,
                    metric.quality_score,
                    metric.completeness_score,
                    ", ".join(metric_reasons(metric)[:4]),
                ]
            )

        if len(problem_rows) == 1:
            problem_rows.append(
                [
                    "-",
                    "-",
                    "-",
                    "-",
                    "Проблемные отчеты не выявлены",
                ]
            )

        story.append(self.make_table(problem_rows))
        story.append(Spacer(1, 0.4 * cm))

        story.append(
            Paragraph(
                "4. Риски по авторам",
                styles["Heading1"],
            )
        )

        author_rows = [
            [
                "Автор",
                "Отчетов",
                "Пропусков",
                "Качество",
                "Полнота",
                "Опозданий",
                "Риск",
            ],
        ]

        metrics_by_author = {}

        for metric in metrics:
            metrics_by_author.setdefault(
                metric.author,
                [],
            ).append(metric)

        author_risks = []

        for author, author_report_metrics in metrics_by_author.items():
            reports_count = len(author_report_metrics)

            if reports_count == 0:
                continue

            avg_author_quality = round(
                sum(metric.quality_score for metric in author_report_metrics) / reports_count,
                1,
            )

            avg_author_completeness = round(
                sum(metric.completeness_score for metric in author_report_metrics) / reports_count,
                1,
            )

            late_count = sum(
                1 for metric in author_report_metrics
                if metric.is_late
            )

            no_completed_count = sum(
                1 for metric in author_report_metrics
                if metric.completed_tasks_count == 0
            )

            no_plan_count = sum(
                1 for metric in author_report_metrics
                if metric.planned_tasks_count == 0
            )

            problems_count = sum(
                1 for metric in author_report_metrics
                if metric.problems_count > 0
            )

            notes_count = sum(
                1 for metric in author_report_metrics
                if metric.notes
            )

            missed_count = missed_count_by_author.get(
                author,
                0,
            )

            risk_score = 0

            if avg_author_quality < 60:
                risk_score += 3
            elif avg_author_quality < 70:
                risk_score += 2

            if avg_author_completeness < 70:
                risk_score += 3
            elif avg_author_completeness < 80:
                risk_score += 2

            if no_completed_count >= max(2, reports_count // 2):
                risk_score += 3
            elif no_completed_count > 0:
                risk_score += 1

            if no_plan_count >= max(2, reports_count // 2):
                risk_score += 3
            elif no_plan_count > 0:
                risk_score += 1

            if problems_count >= max(2, reports_count // 2):
                risk_score += 2
            elif problems_count > 0:
                risk_score += 1

            if late_count >= max(2, reports_count // 2):
                risk_score += 2
            elif late_count > 0:
                risk_score += 1

            if missed_count >= 3:
                risk_score += 3
            elif missed_count > 0:
                risk_score += 2

            if notes_count >= max(2, reports_count // 2):
                risk_score += 2

            if risk_score >= 7:
                risk = "Высокий"
            elif risk_score >= 3:
                risk = "Средний"
            else:
                risk = "Низкий"

            author_risks.append(
                [
                    risk_score,
                    author,
                    reports_count,
                    missed_count,
                    avg_author_quality,
                    avg_author_completeness,
                    late_count,
                    risk,
                ]
            )

        for row in sorted(
            author_risks,
            key=lambda item: item[0],
            reverse=True,
        )[:20]:
            author_rows.append(row[1:])

        if len(author_rows) == 1 and author_metrics:
            for metric in sorted(
                author_metrics,
                key=lambda item: item.average_quality,
            )[:20]:
                author_rows.append(
                    [
                        metric.author,
                        metric.reports_count,
                        0,
                        metric.average_quality,
                        metric.average_completeness,
                        metric.late_reports,
                        "Не рассчитан",
                    ]
                )

        story.append(self.make_table(author_rows))
        story.append(Spacer(1, 0.4 * cm))

        story.append(
            Paragraph(
                "5. Частые антипаттерны",
                styles["Heading1"],
            )
        )

        antipatterns = {}

        def add_antipattern(name):
            antipatterns[name] = antipatterns.get(
                name,
                0,
            ) + 1

        for metric in metrics:
            if metric.completed_tasks_count == 0:
                add_antipattern("Нет выполненных задач")

            if metric.planned_tasks_count == 0:
                add_antipattern("Нет плана на сегодня")

            if metric.problems_count > 0:
                add_antipattern("Есть проблемы или блокеры")

            if metric.is_late:
                add_antipattern("Отчет после дедлайна")

            if metric.quality_score < 70:
                add_antipattern("Низкое качество отчета")

            if metric.completeness_score < 80:
                add_antipattern("Неполный отчет")

            for note in metric.notes:
                note_lower = note.lower()

                if "мало конкретики" in note_lower:
                    add_antipattern("Мало конкретики")

                if "нет привязки" in note_lower or "jira" in note_lower or "джира" in note_lower:
                    add_antipattern("Нет привязки к задаче")

        if missed_reports:
            add_antipattern("Пропущенные daily-отчеты")

        antipattern_rows = [
            ["Антипаттерн", "Кол-во отчетов"],
        ]

        for name, count in sorted(
            antipatterns.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:10]:
            antipattern_rows.append(
                [
                    name,
                    count,
                ]
            )

        if len(antipattern_rows) == 1:
            antipattern_rows.append(
                [
                    "Не выявлено",
                    0,
                ]
            )

        story.append(self.make_table(antipattern_rows))
        story.append(Spacer(1, 0.4 * cm))

        story.append(
            Paragraph(
                "6. Выводы для лида",
                styles["Heading1"],
            )
        )

        conclusions = []

        if avg_quality < 70:
            conclusions.append(
                [
                    "Качество отчетов требует внимания",
                    "Согласовать с командой минимальный стандарт daily-отчета.",
                ]
            )

        if reports_without_completed > 0:
            conclusions.append(
                [
                    "Часть отчетов не фиксирует результат за вчера",
                    "Просить сотрудников писать не активность, а завершенный результат.",
                ]
            )

        if reports_without_plan > 0:
            conclusions.append(
                [
                    "В части отчетов нет плана на сегодня",
                    "Проверить, понятно ли сотрудникам, что является планом на день.",
                ]
            )

        if reports_with_problems > 0:
            conclusions.append(
                [
                    "В отчетах встречаются проблемы и блокеры",
                    "Разобрать повторяющиеся блокеры отдельно с лидами направлений.",
                ]
            )

        if missed_reports:
            conclusions.append(
                [
                    "Есть пропущенные daily-отчеты",
                    "Проверить регулярность отчетности по авторам с пропусками.",
                ]
            )

        if not conclusions:
            conclusions.append(
                [
                    "Критичных системных проблем не выявлено",
                    "Продолжать наблюдение по Excel-отчету.",
                ]
            )

        conclusion_rows = [
            ["Наблюдение", "Рекомендация"],
        ]
        conclusion_rows.extend(conclusions)

        story.append(self.make_table(conclusion_rows))

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

        styles.add(
            ParagraphStyle(
                name="TableCell",
                parent=styles["BodyText"],
                fontName=self.font_name,
                fontSize=8,
                leading=10,
            )
        )

        return styles

    def make_table(self, rows):
        """Создает оформленную таблицу."""

        styles = self.build_styles()
        table_cell_style = styles["TableCell"]

        prepared_rows = []

        for row in rows:
            prepared_row = []

            for value in row:
                prepared_row.append(
                    Paragraph(
                        str(value),
                        table_cell_style,
                    )
                )

            prepared_rows.append(prepared_row)

        column_count = len(rows[0]) if rows else 1
        available_width = A4[0] - 3 * cm
        column_width = available_width / column_count

        table = Table(
            prepared_rows,
            repeatRows=1,
            hAlign="LEFT",
            colWidths=[column_width] * column_count,
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        return table
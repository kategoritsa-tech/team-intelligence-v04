from pathlib import Path
import csv


class ReportExporter:
    """Экспорт аналитических отчетов."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.ensure_output_dir()

    def ensure_output_dir(self):
        """Создает папку для отчетов."""

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_text(self, filename: str, content: str) -> Path:
        """Экспортирует текстовый отчет."""

        file_path = self.output_dir / filename
        file_path.write_text(content, encoding="utf-8")

        return file_path

    def export_csv(
        self,
        filename: str,
        headers: list[str],
        rows: list[list],
    ) -> Path:
        """Экспортирует табличные данные в CSV."""

        file_path = self.output_dir / filename

        with file_path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

        return file_path

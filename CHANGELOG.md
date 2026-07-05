# Changelog

## [0.4.0] - 2026-07-05

### Added

- Добавлен пакет `daily`.
- Добавлен `DailyReportBuilder`.
- Добавлен `StructuredReportParser`.
- Добавлен `DailyQualityAnalyzer`.
- Добавлен разбор блоков `Вчера`, `Сегодня`, `Проблемы`.
- Добавлена оценка качества daily-отчетов.
- Добавлена оценка полноты daily-отчетов.
- Добавлен экспорт `daily_metrics.csv`.
- Добавлены листы Excel `Daily Reports` и `Daily Authors`.
- PDF-отчет расширен daily-метриками.

### Changed

- Точка входа поддерживает аргументы `--input` и `--reports-dir`.
- README обновлен под фокус на daily-отчетность.
- `ContentAnalyzer` теперь работает даже без `pymorphy3`.

## [0.3.0] - 2026-07-04

### Added

- Excel Exporter.
- PDF Exporter.
- Листы `Summary`, `Authors`, `Activity`, `Messages`.
- Улучшенные KPI в Summary.

## [0.2.0] - 2026-06-29

### Added

- Message model.
- Telegram HTML parser.
- StatisticsAnalyzer.
- ConsoleReport.

## [0.1.0] - 2026-06-28

### Added

- Создан проект.
- Настроен базовый запуск.

# Team Intelligence

Инструмент анализа ежедневной отчетности команды на основе HTML-экспорта Telegram.

Проект помогает PM быстро увидеть качество daily-отчетов, регулярность публикаций, количество выполненных и запланированных задач, опоздания, проблемы и уклончивые формулировки.

---

## Что умеет

### Парсинг Telegram

- чтение HTML-экспорта Telegram;
- извлечение сообщений, авторов, дат, текста, вложений;
- поддержка стандартного Telegram Desktop Export.

### Общая аналитика

- количество сообщений;
- количество участников;
- активность по дням и часам;
- топ авторов;
- ссылки, домены, упоминания, вложения.

### Daily Intelligence

- поиск daily-отчетов;
- разбор блоков `Вчера`, `Сегодня`, `Проблемы`;
- определение роли по хэштегу;
- подсчет выполненных задач;
- подсчет планов на день;
- поиск Jira-задач;
- оценка качества отчета;
- оценка полноты отчета;
- поиск опозданий после 11:00;
- поиск уклончивых формулировок.

### Экспорт

После запуска формируются:

- `report.txt`;
- `authors.csv`;
- `daily_metrics.csv`;
- `team_intelligence.xlsx`;
- `team_intelligence.pdf`.

Excel содержит листы:

- `Summary`;
- `Authors`;
- `Activity`;
- `Messages`;
- `Daily Reports`;
- `Daily Authors`.

---

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Запуск

Из корня проекта:

```bash
PYTHONPATH=src python -m team_intelligence --input examples/minimal/messages.html
```

Для своего экспорта Telegram:

```bash
PYTHONPATH=src python -m team_intelligence --input data/messages.html
```

Можно указать папку отчетов:

```bash
PYTHONPATH=src python -m team_intelligence --input data/messages.html --reports-dir reports
```

---

## Структура проекта

```text
src/team_intelligence/
├── analytics/      # общая аналитика Telegram-сообщений
├── daily/          # анализ ежедневных отчетов
├── parser/         # парсер Telegram HTML
└── reports/        # экспорт TXT, CSV, Excel, PDF
```

---

## Основной фокус проекта

Проект больше не является просто анализатором Telegram-чата. Основной фокус — анализ daily-отчетов команды:

- кто пишет качественные отчеты;
- кто пишет неполно;
- кто опаздывает;
- кто пишет уклончиво;
- сколько задач выполнено;
- сколько задач запланировано;
- где есть проблемы и блокеры.

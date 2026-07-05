from pathlib import Path
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent

SOURCE_FILE = ROOT / "data" / "messages.html"

OUTPUT_DIR = ROOT / "examples" / "minimal"
OUTPUT_FILE = OUTPUT_DIR / "messages.html"


def main():
    if not SOURCE_FILE.exists():
        print(f"❌ Не найден файл: {SOURCE_FILE}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("📄 Читаю экспорт Telegram...")

    html = SOURCE_FILE.read_text(encoding="utf-8")

    soup = BeautifulSoup(html, "html.parser")

    messages = soup.find_all("div", class_="message")

    print(f"✅ Найдено сообщений: {len(messages)}")

    keep = messages[:100]

    for message in messages[100:]:
        message.decompose()

    OUTPUT_FILE.write_text(str(soup), encoding="utf-8")

    print()
    print("🎉 Готово!")
    print(f"Создан файл:")
    print(OUTPUT_FILE)
    print(f"Сообщений сохранено: {len(keep)}")


if __name__ == "__main__":
    main()
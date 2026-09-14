import os
import requests
import time

from data import get_close_prices
from strategy import get_signal, sma, rsi


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN bulunamadı.")


BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=15
    )

    return response.json()


def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 10
    }

    if offset is not None:
        params["offset"] = offset

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    return response.json()


def analyze_stock(symbol):
    symbol = symbol.upper().strip()

    if not symbol.endswith(".IS"):
        symbol += ".IS"

    prices = get_close_prices(
        symbol,
        period="6mo"
    )

    current_price = prices[-1]
    sma20 = sma(prices, 20)
    current_rsi = rsi(prices, 14)
    signal = get_signal(prices)

    clean_symbol = symbol.replace(".IS", "")

    message = (
        "📊 HİSSE ANALİZİ\n\n"
        f"🏢 Hisse: {clean_symbol}\n"
        f"💰 Son fiyat: {current_price:.2f} TL\n\n"
        "📈 TEKNİK GÖSTERGELER\n"
        f"SMA20: {sma20:.2f} TL\n"
        f"RSI14: {current_rsi:.2f}\n\n"
        f"🎯 Sinyal: {signal}\n\n"
        "⚠️ Bu analiz yatırım tavsiyesi değildir."
    )

    return message


def handle_message(chat_id, text):
    text = text.strip()

    lower_text = text.lower()

    if lower_text == "/start":
        send_message(
            chat_id,
            "🤖 Trading Bot aktif!\n\n"
            "Komutlar:\n"
            "/analiz TUPRS\n"
            "/analiz SASA\n"
            "/analiz ASELS\n"
            "/analiz THYAO\n"
            "/durum\n\n"
            "Ayrıca doğal şekilde de sorabilirsin:\n"
            "TUPRS nasıl?\n"
            "SASA nasıl?"
        )

    elif lower_text == "/durum":
        send_message(
            chat_id,
            "🟢 Bot çalışıyor.\n\n"
            "Veri bağlantısı: Aktif\n"
            "Analiz motoru: Aktif"
        )

    elif lower_text.startswith("/analiz"):
        parts = text.split()

        if len(parts) < 2:
            send_message(
                chat_id,
                "❌ Hisse kodu yazmalısın.\n\n"
                "Örnek:\n"
                "/analiz TUPRS\n"
                "/analiz SASA\n"
                "/analiz ASELS"
            )
            return

        symbol = parts[1]

        try:
            message = analyze_stock(symbol)
            send_message(chat_id, message)

        except Exception as error:
            send_message(
                chat_id,
                f"❌ {symbol.upper()} analiz edilemedi.\n\n"
                "Hisse kodunu kontrol et."
            )

    elif lower_text.endswith(" nasıl?"):
        words = text.split()

        if len(words) >= 2:
            symbol = words[0]

            try:
                message = analyze_stock(symbol)
                send_message(chat_id, message)

            except Exception:
                send_message(
                    chat_id,
                    f"❌ {symbol.upper()} analiz edilemedi.\n\n"
                    "Hisse kodunu kontrol et."
                )
        else:
            send_message(
                chat_id,
                "Örnek: TUPRS nasıl?"
            )

    else:
        send_message(
            chat_id,
            "❓ Komutu anlayamadım.\n\n"
            "Örnek:\n"
            "/analiz TUPRS\n"
            "/analiz SASA\n"
            "TUPRS nasıl?"
        )


def main():
    print("=== BIST TELEGRAM TRADING BOT ===")
    print("Bot başlatılıyor...")

    offset = None

    while True:
        try:
            result = get_updates(offset)

            if not result.get("ok"):
                print("Telegram API hatası:", result)
                time.sleep(5)
                continue

            updates = result.get("result", [])

            for update in updates:
                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                print(f"Mesaj geldi: {text}")

                handle_message(
                    chat_id,
                    text
                )

        except Exception as error:
            print("Bot hatası:", error)
            time.sleep(5)


if __name__ == "__main__":
    main()

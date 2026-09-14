import os
import requests
import time

from data import get_market_data
from indicators import get_latest_indicators


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

    data = get_market_data(
        symbol,
        period="1y",
        interval="1d"
    )

    indicators = get_latest_indicators(data)

    clean_symbol = symbol.replace(".IS", "")

    price = indicators["price"]

    message = (
        "📊 HİSSE ANALİZİ\n\n"

        f"🏢 Hisse: {clean_symbol}\n"
        f"💰 Fiyat: {price:.2f} TL\n\n"

        "📈 HAREKETLİ ORTALAMALAR\n"
        f"SMA20: {indicators['sma20']:.2f}\n"
        f"SMA50: {indicators['sma50']:.2f}\n"
        f"SMA200: {indicators['sma200']:.2f}\n"
        f"EMA20: {indicators['ema20']:.2f}\n"
        f"EMA50: {indicators['ema50']:.2f}\n"
        f"EMA200: {indicators['ema200']:.2f}\n\n"

        "📊 MOMENTUM\n"
        f"RSI14: {indicators['rsi']:.2f}\n"
        f"Momentum10: {indicators['momentum']:.2f}%\n\n"

        "📉 MACD\n"
        f"MACD: {indicators['macd']:.4f}\n"
        f"Sinyal: {indicators['macd_signal']:.4f}\n"
        f"Histogram: {indicators['macd_hist']:.4f}\n\n"

        "📐 BOLLINGER\n"
        f"Üst: {indicators['bb_upper']:.2f}\n"
        f"Orta: {indicators['bb_middle']:.2f}\n"
        f"Alt: {indicators['bb_lower']:.2f}\n\n"

        "📦 HACİM\n"
        f"Hacim oranı: {indicators['volume_ratio']:.2f}x\n\n"

        "⚡ RİSK\n"
        f"ATR14: {indicators['atr']:.2f}\n"
        f"Volatilite: {indicators['volatility']:.2f}%\n\n"

        "⚠️ Bu analiz yatırım tavsiyesi değildir."
    )

    return message


def handle_message(chat_id, text):

    text = text.strip()

    lower_text = text.lower()

    if lower_text == "/start":

        send_message(
            chat_id,
            "🤖 BIST ANALİZ BOTU AKTİF!\n\n"

            "Komutlar:\n\n"

            "/analiz TUPRS\n"
            "/analiz SASA\n"
            "/analiz ASELS\n"
            "/analiz THYAO\n\n"

            "Doğal kullanım:\n"
            "TUPRS nasıl?\n"
            "SASA nasıl?"
        )

    elif lower_text == "/durum":

        send_message(
            chat_id,
            "🟢 Bot çalışıyor.\n\n"
            "Veri bağlantısı: Aktif\n"
            "Teknik analiz: Aktif\n"
            "MACD: Aktif\n"
            "RSI: Aktif\n"
            "Bollinger: Aktif\n"
            "ATR: Aktif\n"
            "Hacim analizi: Aktif"
        )

    elif lower_text.startswith("/analiz"):

        parts = text.split()

        if len(parts) < 2:

            send_message(
                chat_id,
                "❌ Hisse kodu yazmalısın.\n\n"
                "Örnek:\n"
                "/analiz TUPRS"
            )

            return

        symbol = parts[1]

        try:

            message = analyze_stock(symbol)

            send_message(
                chat_id,
                message
            )

        except Exception as error:

            print("Analiz hatası:", error)

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

                send_message(
                    chat_id,
                    message
                )

            except Exception as error:

                print("Analiz hatası:", error)

                send_message(
                    chat_id,
                    f"❌ {symbol.upper()} analiz edilemedi."
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
            "TUPRS nasıl?"
        )


def main():

    print("=== BIST TELEGRAM ANALİZ BOTU ===")
    print("Bot başlatılıyor...")

    offset = None

    while True:

        try:

            result = get_updates(offset)

            if not result.get("ok"):

                print(
                    "Telegram API hatası:",
                    result
                )

                time.sleep(5)

                continue

            updates = result.get(
                "result",
                []
            )

            for update in updates:

                offset = (
                    update["update_id"] + 1
                )

                message = update.get(
                    "message"
                )

                if not message:
                    continue

                chat_id = message["chat"]["id"]

                text = message.get(
                    "text",
                    ""
                )

                print(
                    f"Mesaj geldi: {text}"
                )

                handle_message(
                    chat_id,
                    text
                )

        except Exception as error:

            print(
                "Bot hatası:",
                error
            )

            time.sleep(5)


if __name__ == "__main__":

    main()

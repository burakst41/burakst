import os
import time
import requests

from data import get_close_prices
from strategy import get_signal, sma, rsi


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN bulunamadı.")


BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


def analyze_stock(symbol):
    symbol_map = {
        "THY": "THYAO.IS",
        "THYAO": "THYAO.IS",
        "ASELS": "ASELS.IS",
        "TUPRS": "TUPRS.IS",
        "BIMAS": "BIMAS.IS",
        "EREGL": "EREGL.IS",
        "AKBNK": "AKBNK.IS",
        "GARAN": "GARAN.IS",
        "KCHOL": "KCHOL.IS",
        "SISE": "SISE.IS",
    }

    symbol = symbol.upper().replace(".IS", "")
    yahoo_symbol = symbol_map.get(symbol, symbol + ".IS")

    try:
        prices = get_close_prices(yahoo_symbol, period="6mo")

        current_price = prices[-1]
        sma20 = sma(prices, 20)
        current_rsi = rsi(prices, 14)
        signal = get_signal(prices)

        if current_price > sma20:
            trend = "YUKARI"
        else:
            trend = "AŞAĞI"

        if signal == "AL":
            emoji = "🟢"
        elif signal == "SAT":
            emoji = "🔴"
        else:
            emoji = "🟡"

        message = (
            f"📊 {yahoo_symbol} ANALİZİ\n\n"
            f"💰 Fiyat: {current_price:.2f} TL\n"
            f"📈 SMA20: {sma20:.2f} TL\n"
            f"📉 RSI14: {current_rsi:.2f}\n"
            f"📊 Trend: {trend}\n\n"
            f"{emoji} SİNYAL: {signal}\n\n"
            f"⚠️ Bu sinyal yalnızca teknik göstergelere "
            f"dayalıdır, yatırım tavsiyesi değildir."
        )

        return message

    except Exception as error:
        return f"❌ Analiz yapılamadı.\nHata: {error}"


def send_message(chat_id, text):
    requests.post(
        f"{BASE_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=30
    )


def get_updates(offset=None):
    params = {
        "timeout": 30
    }

    if offset is not None:
        params["offset"] = offset

    response = requests.get(
        f"{BASE_URL}/getUpdates",
        params=params,
        timeout=35
    )

    return response.json()


def main():
    print("🤖 Telegram Trading Bot başladı.")

    offset = None

    while True:
        try:
            data = get_updates(offset)

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "").strip()

                print("Mesaj:", text)

                if text.lower() == "/start":
                    send_message(
                        chat_id,
                        "🤖 Trading Bot aktif!\n\n"
                        "Örnek:\n"
                        "THY hissesini incele\n\n"
                        "veya:\n"
                        "/analiz THY"
                    )
                    continue

                if text.lower().startswith("/analiz"):
                    parts = text.split()

                    if len(parts) < 2:
                        send_message(
                            chat_id,
                            "Örnek kullanım:\n/analiz THY"
                        )
                        continue

                    symbol = parts[1]
                    result = analyze_stock(symbol)
                    send_message(chat_id, result)
                    continue

                # Doğal Türkçe kullanım
                words = text.upper().split()

                possible_symbols = [
                    "THY",
                    "THYAO",
                    "ASELS",
                    "TUPRS",
                    "BIMAS",
                    "EREGL",
                    "AKBNK",
                    "GARAN",
                    "KCHOL",
                    "

from data import get_close_prices
from strategy import get_signal, sma, rsi


def main():
    symbol = "THYAO.IS"

    print("=== TRADING BOT ===")
    print()

    try:
        prices = get_close_prices(symbol, period="6mo")

        current_price = prices[-1]
        sma20 = sma(prices, 20)
        current_rsi = rsi(prices, 14)
        signal = get_signal(prices)

        print("Hisse:", symbol)
        print("Veri sayısı:", len(prices))
        print("Son fiyat:", round(current_price, 2))
        print("SMA20:", round(sma20, 2))
        print("RSI14:", round(current_rsi, 2))
        print("SİNYAL:", signal)

    except Exception as error:
        print("HATA:", error)


if __name__ == "__main__":
    main()

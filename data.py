import yfinance as yf


def get_market_data(symbol="THYAO.IS", period="6mo", interval="1d"):
    """
    Yahoo Finance üzerinden piyasa verisi çeker.
    """

    data = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        raise ValueError("Piyasa verisi alınamadı.")

    return data


def get_close_prices(symbol="THYAO.IS", period="6mo"):
    data = get_market_data(symbol, period)

    close = data["Close"]

    # Bazı yfinance sürümlerinde sütun MultiIndex olabilir.
    if hasattr(close, "columns"):
        close = close.iloc[:, 0]

    return close.dropna().tolist()


if __name__ == "__main__":
    symbol = "THYAO.IS"

    prices = get_close_prices(symbol)

    print("=== MARKET DATA ===")
    print("Hisse:", symbol)
    print("Veri sayısı:", len(prices))
    print("Son fiyat:", prices[-1])

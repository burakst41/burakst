import yfinance as yf
import pandas as pd


def get_market_data(symbol="THYAO.IS", period="1y", interval="1d"):
    """
    Yahoo Finance üzerinden OHLCV piyasa verisi çeker.

    OHLCV:
    Open   = Açılış
    High   = En yüksek
    Low    = En düşük
    Close  = Kapanış
    Volume = Hacim
    """

    symbol = symbol.upper().strip()

    if not symbol.endswith(".IS"):
        symbol += ".IS"

    data = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        raise ValueError(f"{symbol} için piyasa verisi alınamadı.")

    # Yeni yfinance sürümlerinde MultiIndex oluşabilir.
    if isinstance(data.columns, pd.MultiIndex):
        try:
            data.columns = data.columns.get_level_values(0)
        except Exception:
            data = data.xs(symbol, axis=1, level=-1)

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Eksik veri sütunları: {', '.join(missing)}"
        )

    data = data[required_columns].dropna()

    if data.empty:
        raise ValueError(f"{symbol} için kullanılabilir veri yok.")

    return data


def get_close_prices(symbol="THYAO.IS", period="1y"):
    """
    Sadece kapanış fiyatlarını döndürür.
    Eski kodlarla uyumluluk için korunmuştur.
    """

    data = get_market_data(
        symbol,
        period=period,
        interval="1d"
    )

    return data["Close"].tolist()


def get_ohlcv(symbol="THYAO.IS", period="1y"):
    """
    Tam OHLCV verisini döndürür.
    """

    return get_market_data(
        symbol,
        period=period,
        interval="1d"
    )


if __name__ == "__main__":

    symbol = "THYAO.IS"

    data = get_market_data(
        symbol,
        period="1y"
    )

    print("=== MARKET DATA ===")
    print("Hisse:", symbol)
    print("Veri sayısı:", len(data))
    print()

    print("Son gün:")
    print(data.tail(1))

    print()
    print("Son fiyat:", round(float(data["Close"].iloc[-1]), 2))
    print("Son hacim:", int(data["Volume"].iloc[-1]))

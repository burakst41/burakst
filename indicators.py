import pandas as pd
import numpy as np


def sma(series, period):
    return series.rolling(period).mean()


def ema(series, period):
    return series.ewm(
        span=period,
        adjust=False
    ).mean()


def rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def macd(series):
    ema12 = ema(series, 12)
    ema26 = ema(series, 26)

    macd_line = ema12 - ema26

    signal_line = ema(
        macd_line,
        9
    )

    histogram = macd_line - signal_line

    return (
        macd_line,
        signal_line,
        histogram
    )


def bollinger_bands(series, period=20, std_dev=2):
    middle = sma(series, period)

    std = series.rolling(
        period
    ).std()

    upper = middle + (
        std * std_dev
    )

    lower = middle - (
        std * std_dev
    )

    return (
        upper,
        middle,
        lower
    )


def atr(data, period=14):
    high = data["High"]
    low = data["Low"]
    close = data["Close"]

    previous_close = close.shift(1)

    tr1 = high - low

    tr2 = (
        high - previous_close
    ).abs()

    tr3 = (
        low - previous_close
    ).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    return true_range.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()


def momentum(series, period=10):
    return (
        series / series.shift(period) - 1
    ) * 100


def volatility(series, period=20):
    returns = series.pct_change()

    return (
        returns.rolling(period).std()
        * np.sqrt(252)
        * 100
    )


def volume_ratio(volume, period=20):
    average_volume = (
        volume.rolling(period).mean()
    )

    return volume / average_volume


def calculate_indicators(data):
    close = data["Close"]

    result = data.copy()

    # Hareketli ortalamalar
    result["SMA20"] = sma(close, 20)
    result["SMA50"] = sma(close, 50)
    result["SMA200"] = sma(close, 200)

    result["EMA20"] = ema(close, 20)
    result["EMA50"] = ema(close, 50)
    result["EMA200"] = ema(close, 200)

    # RSI
    result["RSI14"] = rsi(close, 14)

    # MACD
    (
        result["MACD"],
        result["MACD_SIGNAL"],
        result["MACD_HIST"]
    ) = macd(close)

    # Bollinger
    (
        result["BB_UPPER"],
        result["BB_MIDDLE"],
        result["BB_LOWER"]
    ) = bollinger_bands(close)

    # ATR
    result["ATR14"] = atr(
        result,
        14
    )

    # Momentum
    result["MOMENTUM10"] = momentum(
        close,
        10
    )

    # Volatilite
    result["VOLATILITY20"] = volatility(
        close,
        20
    )

    # Hacim oranı
    result["VOLUME_RATIO"] = volume_ratio(
        result["Volume"],
        20
    )

    return result
    def get_latest_indicators(data):
    result = calculate_indicators(data)

    latest = result.iloc[-1]

    return {
        "price": float(latest["Close"]),

        "sma20": float(latest["SMA20"]),
        "sma50": float(latest["SMA50"]),
        "sma200": float(latest["SMA200"]),

        "ema20": float(latest["EMA20"]),
        "ema50": float(latest["EMA50"]),
        "ema200": float(latest["EMA200"]),

        "rsi": float(latest["RSI14"]),

        "macd": float(latest["MACD"]),
        "macd_signal": float(latest["MACD_SIGNAL"]),
        "macd_hist": float(latest["MACD_HIST"]),

        "bb_upper": float(latest["BB_UPPER"]),
        "bb_middle": float(latest["BB_MIDDLE"]),
        "bb_lower": float(latest["BB_LOWER"]),

        "atr": float(latest["ATR14"]),

        "momentum": float(latest["MOMENTUM10"]),

        "volatility": float(latest["VOLATILITY20"]),

        "volume_ratio": float(latest["VOLUME_RATIO"])
    }



        

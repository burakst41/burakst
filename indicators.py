import pandas as pd
import numpy as np


# =========================================================
# BASİT HAREKETLİ ORTALAMA
# =========================================================

def sma(series, period):
    return series.rolling(period).mean()


# =========================================================
# ÜSTEL HAREKETLİ ORTALAMA
# =========================================================

def ema(series, period):
    return series.ewm(
        span=period,
        adjust=False
    ).mean()


# =========================================================
# RSI
# =========================================================

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

    result = 100 - (
        100 / (1 + rs)
    )

    return result


# =========================================================
# MACD
# =========================================================

def macd(series):

    ema12 = ema(series, 12)
    ema26 = ema(series, 26)

    macd_line = ema12 - ema26

    signal = macd_line.ewm(
        span=9,
        adjust=False
    ).mean()

    histogram = macd_line - signal

    return (
        macd_line,
        signal,
        histogram
    )


# =========================================================
# BOLLINGER BANDS
# =========================================================

def bollinger_bands(series, period=20):

    middle = series.rolling(
        period
    ).mean()

    std = series.rolling(
        period
    ).std()

    upper = middle + (
        std * 2
    )

    lower = middle - (
        std * 2
    )

    return (
        upper,
        middle,
        lower
    )


# =========================================================
# ATR
# =========================================================

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


# =========================================================
# MOMENTUM
# =========================================================

def momentum(series, period=10):

    return (
        series.pct_change(period)
        * 100
    )


# =========================================================
# VOLATİLİTE
# =========================================================

def volatility(series, period=20):

    returns = series.pct_change()

    return (
        returns
        .rolling(period)
        .std()
        * np.sqrt(252)
        * 100
    )


# =========================================================
# HACİM ORANI
# =========================================================

def volume_ratio(
    volume,
    period=20
):

    average_volume = (
        volume
        .rolling(period)
        .mean()
    )

    return (
        volume / average_volume
    )


# =========================================================
# TÜM GÖSTERGELER
# =========================================================

def calculate_indicators(data):

    data = data.copy()

    # YFinance MultiIndex güvenliği
    if isinstance(
        data.columns,
        pd.MultiIndex
    ):

        data.columns = (
            data.columns
            .get_level_values(0)
        )

    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    missing = [
        column
        for column in required
        if column not in data.columns
    ]

    if missing:

        raise ValueError(
            "Eksik veri sütunları: "
            + ", ".join(missing)
        )

    data = data[
        required
    ].copy()

    for column in required:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data = data.dropna()

    if len(data) < 200:

        raise ValueError(
            "Analiz için en az "
            "200 günlük veri gerekli."
        )

    close = data["Close"]

    # SMA
    data["SMA20"] = sma(
        close,
        20
    )

    data["SMA50"] = sma(
        close,
        50
    )

    data["SMA200"] = sma(
        close,
        200
    )

    # EMA
    data["EMA20"] = ema(
        close,
        20
    )

    data["EMA50"] = ema(
        close,
        50
    )

    data["EMA200"] = ema(
        close,
        200
    )

    # RSI
    data["RSI14"] = rsi(
        close,
        14
    )

    # MACD
    (
        data["MACD"],
        data["MACD_SIGNAL"],
        data["MACD_HIST"]
    ) = macd(close)

    # Bollinger
    (
        data["BB_UPPER"],
        data["BB_MIDDLE"],
        data["BB_LOWER"]
    ) = bollinger_bands(
        close,
        20
    )

    # ATR
    data["ATR14"] = atr(
        data,
        14
    )

    # Momentum
    data["MOMENTUM10"] = momentum(
        close,
        10
    )

    # Volatilite
    data["VOLATILITY20"] = volatility(
        close,
        20
    )

    # Hacim
    data["VOLUME_RATIO"] = volume_ratio(
        data["Volume"],
        20
    )

    return data


# =========================================================
# SON GÖSTERGELERİ AL
# =========================================================

def get_latest_indicators(data):

    result = calculate_indicators(
        data
    )

    latest = result.iloc[-1]

    return {

        "price": float(
            latest["Close"]
        ),

        "sma20": float(
            latest["SMA20"]
        ),

        "sma50": float(
            latest["SMA50"]
        ),

        "sma200": float(
            latest["SMA200"]
        ),

        "ema20": float(
            latest["EMA20"]
        ),

        "ema50": float(
            latest["EMA50"]
        ),

        "ema200": float(
            latest["EMA200"]
        ),

        "rsi": float(
            latest["RSI14"]
        ),

        "macd": float(
            latest["MACD"]
        ),

        "macd_signal": float(
            latest["MACD_SIGNAL"]
        ),

        "macd_hist": float(
            latest["MACD_HIST"]
        ),

        "bb_upper": float(
            latest["BB_UPPER"]
        ),

        "bb_middle": float(
            latest["BB_MIDDLE"]
        ),

        "bb_lower": float(
            latest["BB_LOWER"]
        ),

        "atr": float(
            latest["ATR14"]
        ),

        "momentum": float(
            latest["MOMENTUM10"]
        ),

        "volatility": float(
            latest["VOLATILITY20"]
        ),

        "volume_ratio": float(
            latest["VOLUME_RATIO"]
        )
    }

import math


def sma(values, period):
    """Simple Moving Average"""
    if len(values) < period:
        return None

    return sum(values[-period:]) / period


def rsi(prices, period=14):
    """Calculate RSI using simple average gains/losses."""
    if len(prices) <= period:
        return None

    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]

        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def signal(prices):
    """Generate a basic trading signal."""

    if len(prices) < 20:
        return "BEKLE"

    current_price = prices[-1]

    sma20 = sma(prices, 20)
    current_rsi = rsi(prices, 14)

    if sma20 is None or current_rsi is None:
        return "BEKLE"

    # Basic strategy
    if current_price > sma20 and current_rsi < 70:
        return "AL"

    if current_price < sma20 and current_rsi > 30:
        return "SAT"

    return "BEKLE"


def backtest(prices, initial_balance=10000):
    """
    Very simple backtest.

    Starts with cash.
    Buys when signal is AL.
    Sells when signal is SAT.
    """

    balance = initial_balance
    position = 0
    entry_price = None
    trades = []

    for i in range(20, len(prices)):
        history = prices[: i + 1]
        current_price = prices[i]

        current_signal = signal(history)

        if current_signal == "AL" and position == 0:
            position = balance / current_price
            entry_price = current_price
            balance = 0

            trades.append({
                "type": "BUY",
                "price": current_price
            })

        elif current_signal == "SAT" and position > 0:
            balance = position * current_price

            profit = (current_price - entry_price) * position

            trades.append({
                "type": "SELL",
                "price": current_price,
                "profit": profit
            })

            position = 0
            entry_price = None

    # Close open position at final price
    if position > 0:
        balance = position * prices[-1]

    profit = balance - initial_balance

    return {
        "initial_balance": initial_balance,
        "final_balance": balance,
        "profit": profit,
        "return_percent": (profit / initial_balance) * 100,
        "trades": trades
    }


def main():
    # Temporary test data.
    # Later this will be replaced with real market data.
    prices = [
        100, 101, 102, 101, 103,
        105, 104, 106, 108, 107,
        109, 111, 110, 112, 114,
        113, 115, 117, 116, 118,
        120, 119, 121, 123, 125,
        124, 126, 128, 127, 129
    ]

    print("=== TRADING BOT ===")
    print()

    print("Son fiyat:", prices[-1])
    print("SMA20:", sma(prices, 20))
    print("RSI14:", rsi(prices, 14))
    print("Sinyal:", signal(prices))

    print()
    print("=== BACKTEST ===")

    result = backtest(prices)

    print("Başlangıç:", result["initial_balance"])
    print("Bitiş:", round(result["final_balance"], 2))
    print("Kâr/Zarar:", round(result["profit"], 2))
    print("Getiri:", round(result["return_percent"], 2), "%")
    print("İşlem sayısı:", len(result["trades"]))


if __name__ == "__main__":
    main()

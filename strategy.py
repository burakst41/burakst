def sma(values, period):
    if len(values) < period:
        return None

    return sum(values[-period:]) / period


def rsi(prices, period=14):
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


def get_signal(prices):
    """
    RSI + SMA tabanlı temel strateji.
    """

    if len(prices) < 20:
        return "BEKLE"

    current_price = prices[-1]

    sma20 = sma(prices, 20)
    current_rsi = rsi(prices, 14)

    if sma20 is None or current_rsi is None:
        return "BEKLE"

    if current_price > sma20 and current_rsi < 70:
        return "AL"

    if current_price < sma20 and current_rsi > 30:
        return "SAT"

    return "BEKLE"

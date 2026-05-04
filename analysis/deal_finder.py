def calculate_median(prices):
    if not prices:
        return None
    prices = sorted(prices)
    return prices[len(prices) // 2]


def evaluate_listing(price, median, shipping=0):
    total_price = price + (shipping or 0)

    score = float(total_price) / median

    if score < 0.7:
        return "🔥 BUY", score
    elif score < 1.0:
        return "⚠️ OK"
    else:
        return "❌ NO BUY", score
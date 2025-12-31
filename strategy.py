def confidence_score(df, direction):
    score = 0
    c = df.iloc[-1]

    # Trend
    if direction == "LONG" and c.ema50 > c.ema200:
        score += 25
    if direction == "SHORT" and c.ema50 < c.ema200:
        score += 25

    # MACD
    if direction == "LONG" and c.macd > c.macd_signal:
        score += 25
    if direction == "SHORT" and c.macd < c.macd_signal:
        score += 25

    # RSI
    if direction == "LONG" and 45 <= c.rsi <= 65:
        score += 25
    if direction == "SHORT" and 35 <= c.rsi <= 55:
        score += 25

    return score

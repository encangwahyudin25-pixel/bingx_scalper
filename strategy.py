def signal_details(df, direction):
    c = df.iloc[-1]

    # RSI
    if direction == "LONG":
        rsi_valid = 45 <= c.rsi <= 65
    else:
        rsi_valid = 35 <= c.rsi <= 55

    rsi_icon = "✅" if rsi_valid else "❌"

    # MACD
    macd_valid = (
        c.macd > c.macd_signal if direction == "LONG"
        else c.macd < c.macd_signal
    )
    macd_icon = "✅" if macd_valid else "❌"

    # EMA Trend
    ema_valid = (
        c.ema50 > c.ema200 if direction == "LONG"
        else c.ema50 < c.ema200
    )
    ema_icon = "🟢" if ema_valid else "🔴"

    # Confidence (simple weighted score)
    score = 0
    score += 30 if ema_valid else 0
    score += 30 if macd_valid else 0
    score += 20 if rsi_valid else 0
    score += 20 if c.volume > c.vol_ma else 0

    return {
        "rsi_icon": rsi_icon,
        "macd_icon": macd_icon,
        "ema_icon": ema_icon,
        "confidence": score
    }

import ta

# =========================
# APPLY INDICATORS
# =========================
def apply_indicators(df):
    df["ema50"] = ta.trend.EMAIndicator(df["close"], 50).ema_indicator()
    df["ema200"] = ta.trend.EMAIndicator(df["close"], 200).ema_indicator()

    macd = ta.trend.MACD(df["close"], 12, 26, 9)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_hist"] = macd.macd_diff()

    df["rsi"] = ta.momentum.RSIIndicator(df["close"], 14).rsi()

    df["atr"] = ta.volatility.AverageTrueRange(
        df["high"], df["low"], df["close"], 14
    ).average_true_range()

    df["vol_ma"] = df["volume"].rolling(20).mean()
    return df


# =========================
# LONG SIGNAL
# =========================
def long_signal(df):
    c = df.iloc[-1]
    return (
        c.ema50 > c.ema200 and
        c.close > c.ema50 and
        45 <= c.rsi <= 65 and
        c.macd > c.macd_signal and
        c.macd_hist > 0 and
        c.volume > c.vol_ma
    )


# =========================
# SHORT SIGNAL
# =========================
def short_signal(df):
    c = df.iloc[-1]
    return (
        c.ema50 < c.ema200 and
        c.close < c.ema50 and
        35 <= c.rsi <= 55 and
        c.macd < c.macd_signal and
        c.macd_hist < 0 and
        c.volume > c.vol_ma
    )


# =========================
# CONFIDENCE SCORE
# =========================
def confidence_score(df, direction):
    score = 0
    c = df.iloc[-1]

    # EMA Trend
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

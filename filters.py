def no_trade(df):
    last = df.iloc[-1]
    if last.atr < df.atr.mean() * 0.7:
        return True, "ATR rendah (sideways)"
    if last.volume < last.vol_ma:
        return True, "Volume lemah"
    return False, ""

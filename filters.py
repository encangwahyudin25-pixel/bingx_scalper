def no_trade_filter(df, atr, volume_ma):
    if atr.iloc[-1] < df['close'].iloc[-1] * 0.001:
        return True
    if df['volume'].iloc[-1] < volume_ma.iloc[-1]:
        return True
    return False

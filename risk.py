def risk_levels(entry, atr, direction):
    sl = entry - atr*1.5 if direction == "LONG" else entry + atr*1.5
    tp1 = entry + atr*1.5 if direction == "LONG" else entry - atr*1.5
    tp2 = entry + atr*3 if direction == "LONG" else entry - atr*3
    tp3 = entry + atr*4.5 if direction == "LONG" else entry - atr*4.5
    return sl, tp1, tp2, tp3

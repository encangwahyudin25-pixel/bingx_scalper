def risk_levels(entry, atr, direction):
    if direction == "LONG":
        sl = entry - atr*1.5
        tps = [entry + atr*i for i in [1.5,3,4.5,6]]
    else:
        sl = entry + atr*1.5
        tps = [entry - atr*i for i in [1.5,3,4.5,6]]
    return sl, tps

def risk_levels(entry, atr, direction):
    if direction == "LONG":
        sl = entry - atr * 1.5
        tp1 = entry + atr * 1.5
        tp2 = entry + atr * 3
        tp3 = entry + atr * 4.5
        tp4 = entry + atr * 6
    else:
        sl = entry + atr * 1.5
        tp1 = entry - atr * 1.5
        tp2 = entry - atr * 3
        tp3 = entry - atr * 4.5
        tp4 = entry - atr * 6

    return sl, tp1, tp2, tp3, tp4

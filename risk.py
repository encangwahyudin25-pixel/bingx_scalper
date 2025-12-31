def calculate_levels(entry, atr, side):
    atr_val = atr.iloc[-1]

    if side == "LONG":
        sl = entry - atr_val
        tps = [entry + atr_val * i for i in [1,2,3,4]]
    else:
        sl = entry + atr_val
        tps = [entry - atr_val * i for i in [1,2,3,4]]

    return sl, tps

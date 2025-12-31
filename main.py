from bingx_client import BingX
from strategy import apply_indicators, long_signal, short_signal
from filters import no_trade
from risk import risk_levels
from notifier import send_signal

client = BingX()
pairs = client.get_all_usdt_pairs()

for pair in pairs:
    try:
        df = client.get_klines(pair)
        df = apply_indicators(df)

        block, reason = no_trade(df)
        if block:
            continue

        price = df.close.iloc[-1]
        atr = df.atr.iloc[-1]

        if long_signal(df):
            sl, tp1, tp2, tp3 = risk_levels(price, atr, "LONG")
            send_signal(
                f"📈 *LONG SIGNAL*\n"
                f"Pair: {pair}\n"
                f"Entry: {price}\n"
                f"SL: {sl}\n"
                f"TP1: {tp1}\nTP2: {tp2}\nTP3: {tp3}\n"
                f"Reason: EMA50>EMA200, MACD+, RSI OK"
            )

        if short_signal(df):
            sl, tp1, tp2, tp3 = risk_levels(price, atr, "SHORT")
            send_signal(
                f"📉 *SHORT SIGNAL*\n"
                f"Pair: {pair}\n"
                f"Entry: {price}\n"
                f"SL: {sl}\n"
                f"TP1: {tp1}\nTP2: {tp2}\nTP3: {tp3}\n"
                f"Reason: EMA50<EMA200, MACD-, RSI OK"
            )

    except Exception as e:
        print(pair, e)

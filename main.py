from bingx_client import BingX
from strategy import apply_indicators, long_signal, short_signal, confidence_score
from filters import no_trade
from risk import risk_levels
from notifier import send_signal, heartbeat
from datetime import datetime
import pytz

client = BingX()
pairs = client.get_all_usdt_pairs()
signal_found = False

tz = pytz.timezone("Asia/Jakarta")
now = datetime.now(tz).strftime("%H:%M WIB")

for pair in pairs:
    try:
        df = client.get_klines(pair)
        df = apply_indicators(df)

        block, _ = no_trade(df)
        if block:
            continue

        price = df.close.iloc[-1]
        atr = df.atr.iloc[-1]

        if long_signal(df):
            signal_found = True
            conf = confidence_score(df, "LONG")
            sl, tps = risk_levels(price, atr, "LONG")

            send_signal(
                f"*📈 LONG SIGNAL*\n"
                f"🕒 Time: {now}\n"
                f"KOIN: {pair}\n\n"
                f"📉 Trend EMA: 🟢\n"
                f"📊 MACD: ✅\n"
                f"RSI: {round(df.rsi.iloc[-1],1)} ✅\n"
                f"🔥 Confidence: {conf}%\n\n"
                f"Entry: {price}\n"
                f"SL: {sl}\n"
                f"TP1: {tps[0]}\nTP2: {tps[1]}\nTP3: {tps[2]}\nTP4: {tps[3]}\n\n"
                f"Reason: Trend kuat + momentum valid"
            )

        if short_signal(df):
            signal_found = True
            conf = confidence_score(df, "SHORT")
            sl, tps = risk_levels(price, atr, "SHORT")

            send_signal(
                f"*📉 SHORT SIGNAL*\n"
                f"🕒 Time: {now}\n"
                f"KOIN: {pair}\n\n"
                f"📉 Trend EMA: 🔴\n"
                f"📊 MACD: ❌\n"
                f"RSI: {round(df.rsi.iloc[-1],1)} ❌\n"
                f"🔥 Confidence: {conf}%\n\n"
                f"Entry: {price}\n"
                f"SL: {sl}\n"
                f"TP1: {tps[0]}\nTP2: {tps[1]}\nTP3: {tps[2]}\nTP4: {tps[3]}\n\n"
                f"Reason: Trend turun + momentum valid"
            )

    except Exception as e:
        print(pair, e)

if not signal_found:
    heartbeat()

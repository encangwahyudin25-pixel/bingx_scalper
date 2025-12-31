from bingx_client import BingX
from strategy import apply_indicators, long_signal, short_signal, signal_details
from filters import no_trade
from risk import risk_levels
from notifier import send_signal
from datetime import datetime, timedelta

client = BingX()
pairs = client.get_all_usdt_pairs()
signal_sent = False

wib_time = datetime.utcnow() + timedelta(hours=7)
time_str = wib_time.strftime("%H:%M WIB")

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
            detail = signal_details(df, "LONG")
            sl, tp1, tp2, tp3, tp4 = risk_levels(price, atr, "LONG")

            send_signal(
                f"🟢 *LONG SIGNAL*\n"
                f"🕒 Time: {time_str}\n"
                f"KOIN : {pair}\n\n"
                f"📉 Trend EMA: {detail['ema_icon']}\n"
                f"📊 MACD: {detail['macd_icon']}\n"
                f"RSI: {round(df.rsi.iloc[-1],2)} {detail['rsi_icon']}\n"
                f"🔥 Confidence: {detail['confidence']}%\n\n"
                f"Entry: {round(price,4)}\n"
                f"SL: {round(sl,4)}\n"
                f"TP1: {round(tp1,4)}\n"
                f"TP2: {round(tp2,4)}\n"
                f"TP3: {round(tp3,4)}\n"
                f"TP4: {round(tp4,4)}\n\n"
                f"Reason: Trend kuat + momentum valid"
            )
            signal_sent = True

        elif short_signal(df):
            detail = signal_details(df, "SHORT")
            sl, tp1, tp2, tp3, tp4 = risk_levels(price, atr, "SHORT")

            send_signal(
                f"🔴 *SHORT SIGNAL*\n"
                f"🕒 Time: {time_str}\n"
                f"KOIN : {pair}\n\n"
                f"📉 Trend EMA: {detail['ema_icon']}\n"
                f"📊 MACD: {detail['macd_icon']}\n"
                f"RSI: {round(df.rsi.iloc[-1],2)} {detail['rsi_icon']}\n"
                f"🔥 Confidence: {detail['confidence']}%\n\n"
                f"Entry: {round(price,4)}\n"
                f"SL: {round(sl,4)}\n"
                f"TP1: {round(tp1,4)}\n"
                f"TP2: {round(tp2,4)}\n"
                f"TP3: {round(tp3,4)}\n"
                f"TP4: {round(tp4,4)}\n\n"
                f"Reason: Trend kuat + momentum valid"
            )
            signal_sent = True

    except Exception as e:
        print(pair, e)

# Jika tidak ada signal → bot tetap kirim status
if not signal_sent:
    send_signal(
        f"⏳ *NO SIGNAL*\n"
        f"🕒 Time: {time_str}\n"
        f"Status: Bot aktif & scanning market\n"
        f"Alasan: Belum ada setup valid sesuai rule"
    )

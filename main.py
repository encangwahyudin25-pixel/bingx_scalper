from bingx_client import BingXClient
from strategy import EMA, RSI, MACD, ATR
from filters import no_trade_filter
from risk import calculate_levels
from notifier import send_telegram
from report import log_signal
import pytz, datetime

client = BingXClient()
pairs = client.get_futures_pairs()

def confidence_score(score):
    if score >= 80: return "HIGH CONFIDENCE 🚀"
    if score >= 60: return "MEDIUM"
    return "LOW CONFIDENCE ⚠️"

signals_today = 0

for symbol in pairs:
    df15 = client.get_klines(symbol, "15m")
    df5  = client.get_klines(symbol, "5m")

    close = df15['close']
    ema50 = EMA(close, 50)
    ema200 = EMA(close, 200)
    rsi = RSI(close)
    macd, signal, hist = MACD(close)
    atr = ATR(df15)
    vol_ma = df15['volume'].rolling(20).mean()

    if no_trade_filter(df15, atr, vol_ma):
        continue

    side = None
    score = 0

    if ema50.iloc[-1] > ema200.iloc[-1]:
        score += 30
        if macd.iloc[-1] > signal.iloc[-1] and hist.iloc[-1] > 0:
            score += 25
        if 45 <= rsi.iloc[-1] <= 65:
            score += 20
        if df15['volume'].iloc[-1] > vol_ma.iloc[-1]:
            score += 15
        side = "LONG"

    elif ema50.iloc[-1] < ema200.iloc[-1]:
        score += 30
        if macd.iloc[-1] < signal.iloc[-1] and hist.iloc[-1] < 0:
            score += 25
        if 35 <= rsi.iloc[-1] <= 55:
            score += 20
        if df15['volume'].iloc[-1] > vol_ma.iloc[-1]:
            score += 15
        side = "SHORT"

    if side:
        entry = close.iloc[-1]
        sl, tps = calculate_levels(entry, atr, side)

        tz = pytz.timezone("Asia/Jakarta")
        now = datetime.datetime.now(tz).strftime("%H:%M")

        msg = f"""
📈 {side} SIGNAL
🕒 Time: {now} WIB
🪙 {symbol}

📉 Trend EMA: {'🟢' if side=='LONG' else '🔴'}
📊 MACD: ✅
RSI: {rsi.iloc[-1]:.1f} ✅
🧭 MTF (5M): ✅

🔥 Confidence: {score}%
({confidence_score(score)})

Entry: {entry}
SL: {sl}
TP1: {tps[0]}
TP2: {tps[1]}
TP3: {tps[2]}
TP4: {tps[3]}

Reason: Trend kuat, momentum valid, volume mendukung
"""
        send_telegram(msg)
        log_signal(symbol, side, score)
        signals_today += 1

if signals_today == 0:
    send_telegram("🤖 Bot aktif – belum ada moment entry")

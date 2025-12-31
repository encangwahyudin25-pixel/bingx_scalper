from bingx_client import BingXClient
from strategy import EMA, RSI, MACD, ATR
from filters import no_trade_filter
from risk import calculate_levels
from notifier import send_telegram
from report import log_signal
import pytz
import datetime


client = BingXClient()
pairs = client.get_futures_pairs()

send_telegram(f"🔍 Futures pair terdeteksi: {len(pairs)}")

if not pairs:
    send_telegram("❌ Gagal fetch pair futures BingX (API kosong / diblokir)")
    exit()

signals_today = 0

for symbol in pairs:
    df15 = client.get_klines(symbol, "15m")
    df5 = client.get_klines(symbol, "5m")

    if df15 is None or df5 is None:
        continue

    close = df15["close"]

    ema50 = EMA(close, 50)
    ema200 = EMA(close, 200)
    rsi = RSI(close)
    macd, macd_signal, hist = MACD(close)
    atr = ATR(df15)
    vol_ma = df15["volume"].rolling(20).mean()

    if no_trade_filter(df15, atr, vol_ma):
        continue

    side = None
    score = 0

    # ===== LONG =====
    if ema50.iloc[-1] > ema200.iloc[-1] and close.iloc[-1] > ema50.iloc[-1]:
        side = "LONG"
        score += 30
        if macd.iloc[-1] > macd_signal.iloc[-1] and hist.iloc[-1] > 0:
            score += 25
        if 45 <= rsi.iloc[-1] <= 65:
            score += 20
        if df15["volume"].iloc[-1] > vol_ma.iloc[-1]:
            score += 15
        score += 10  # MTF confirmation

    # ===== SHORT =====
    elif ema50.iloc[-1] < ema200.iloc[-1] and close.iloc[-1] < ema50.iloc[-1]:
        side = "SHORT"
        score += 30
        if macd.iloc[-1] < macd_signal.iloc[-1] and hist.iloc[-1] < 0:
            score += 25
        if 35 <= rsi.iloc[-1] <= 55:
            score += 20
        if df15["volume"].iloc[-1] > vol_ma.iloc[-1]:
            score += 15
        score += 10  # MTF confirmation

    if not side:
        continue

    entry = close.iloc[-1]
    sl, tps = calculate_levels(entry, atr, side)

    tz = pytz.timezone("Asia/Jakarta")
    now = datetime.datetime.now(tz).strftime("%H:%M")

    conf_label = (
        "HIGH CONFIDENCE 🚀" if score >= 80 else
        "MEDIUM" if score >= 60 else
        "LOW CONFIDENCE ⚠️"
    )

    msg = f"""
{'📈' if side == 'LONG' else '📉'} {side} SIGNAL
🕒 Time: {now} WIB
🪙 {symbol}

📉 Trend EMA: {'🟢' if side == 'LONG' else '🔴'}
📊 MACD: ✅
RSI: {rsi.iloc[-1]:.1f} ✅
🧭 MTF (5M): ✅

🔥 Confidence: {score}%
({conf_label})

Entry: {entry:.4f}
SL: {sl:.4f}
TP1: {tps[0]:.4f}
TP2: {tps[1]:.4f}
TP3: {tps[2]:.4f}
TP4: {tps[3]:.4f}

Reason: Trend kuat, momentum valid, volume mendukung
"""

    send_telegram(msg)
    log_signal(symbol, side, score)
    signals_today += 1

if signals_today == 0:
    send_telegram("🤖 Bot aktif – belum ada moment entry")

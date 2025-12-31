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
last_signal = {}   # 🔒 ANTI SPAM MEMORY

for symbol in pairs:
    df15 = client.get_klines(symbol, "15m")
    df5 = client.get_klines(symbol, "5m")

    if df15 is None or df5 is None:
        continue

    # ===== DATA 15M =====
    close15 = df15["close"]
    ema50_15 = EMA(close15, 50)
    ema200_15 = EMA(close15, 200)
    rsi_series = RSI(close15)
    rsi_value = rsi_series.iloc[-1]
    macd15, macd_signal15, hist15 = MACD(close15)
    atr = ATR(df15)
    vol_ma = df15["volume"].rolling(20).mean()

    # ===== DATA 5M =====
    close5 = df5["close"]
    ema50_5 = EMA(close5, 50)
    ema200_5 = EMA(close5, 200)
    macd5, macd_signal5, hist5 = MACD(close5)

    if no_trade_filter(df15, atr, vol_ma):
        continue

    side = None
    score = 0
    rsi_valid = False
    mtf_valid = False
    volume_valid = df15["volume"].iloc[-1] > vol_ma.iloc[-1]

    # ======================
    # LONG LOGIC
    # ======================
    if ema50_15.iloc[-1] > ema200_15.iloc[-1] and close15.iloc[-1] > ema50_15.iloc[-1]:
        side = "LONG"
        score += 30

        if macd15.iloc[-1] > macd_signal15.iloc[-1] and hist15.iloc[-1] > 0:
            score += 25

        if 45 <= rsi_value <= 65:
            score += 20
            rsi_valid = True

        if volume_valid:
            score += 15

        if ema50_5.iloc[-1] > ema200_5.iloc[-1] and macd5.iloc[-1] > macd_signal5.iloc[-1]:
            score += 10
            mtf_valid = True

    # ======================
    # SHORT LOGIC
    # ======================
    elif ema50_15.iloc[-1] < ema200_15.iloc[-1] and close15.iloc[-1] < ema50_15.iloc[-1]:
        side = "SHORT"
        score += 30

        if macd15.iloc[-1] < macd_signal15.iloc[-1] and hist15.iloc[-1] < 0:
            score += 25

        if 35 <= rsi_value <= 55:
            score += 20
            rsi_valid = True

        if volume_valid:
            score += 15

        if ema50_5.iloc[-1] < ema200_5.iloc[-1] and macd5.iloc[-1] < macd_signal5.iloc[-1]:
            score += 10
            mtf_valid = True

    if not side:
        continue

    # ======================
    # 🔒 ANTI SPAM
    # ======================
    if last_signal.get(symbol) == side:
        continue

    last_signal[symbol] = side

    # ======================
    # RSI STRENGTH
    # ======================
    if side == "LONG":
        if rsi_value < 50:
            rsi_strength = "Weak"
        elif rsi_value <= 60:
            rsi_strength = "Ideal"
        else:
            rsi_strength = "Late"
    else:
        if rsi_value > 50:
            rsi_strength = "Late"
        elif rsi_value >= 40:
            rsi_strength = "Ideal"
        else:
            rsi_strength = "Weak"

    # ======================
    # CONFIDENCE
    # ======================
    display_score = min(score, 90)
    conf_label = (
        "HIGH CONFIDENCE 🚀" if display_score >= 80 else
        "MEDIUM" if display_score >= 60 else
        "LOW CONFIDENCE ⚠️"
    )

    entry = close15.iloc[-1]
    sl, tps = calculate_levels(entry, atr, side)

    tz = pytz.timezone("Asia/Jakarta")
    now = datetime.datetime.now(tz).strftime("%H:%M")

    reason = (
        f"EMA50 {'>' if side=='LONG' else '<'} EMA200 (trend), "
        f"MACD searah, RSI {rsi_strength.lower()}, "
        f"volume {'mendukung' if volume_valid else 'lemah'}, "
        f"MTF {'searah' if mtf_valid else 'belum searah'}"
    )

    msg = f"""
{'📈' if side == 'LONG' else '📉'} {side} SIGNAL
🕒 Time: {now} WIB
🪙 {symbol}

📉 Trend EMA: {'🟢 EMA50 > EMA200' if side=='LONG' else '🔴 EMA50 < EMA200'}
📊 MACD: ✅
RSI: {rsi_value:.1f} {'✅' if rsi_valid else '❌'} ({rsi_strength})
📦 Volume: {'✅' if volume_valid else '❌'}
🧭 MTF (5M): {'✅' if mtf_valid else '❌'}

🔥 Confidence: {display_score}%
({conf_label})

Entry: {entry:.4f}
SL: {sl:.4f}
TP1: {tps[0]:.4f}
TP2: {tps[1]:.4f}
TP3: {tps[2]:.4f}
TP4: {tps[3]:.4f}

Reason: {reason}
"""

    send_telegram(msg)
    log_signal(symbol, side, display_score)
    signals_today += 1

if signals_today == 0:
    send_telegram("🤖 Bot aktif – belum ada moment entry")

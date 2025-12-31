from bingx_client import BingXClient
from strategy import EMA, RSI, MACD, ATR
from filters import no_trade_filter
from risk import calculate_levels
from notifier import send_telegram
from report import log_signal
import pytz
import datetime

# ======================
# INIT
# ======================
client = BingXClient()
pairs = client.get_futures_pairs()

send_telegram(f"🔍 Futures pair terdeteksi: {len(pairs)}")

if not pairs:
    send_telegram("❌ Gagal fetch pair futures BingX (API kosong / diblokir)")
    exit()

signals_today = 0
last_signal = {}   # 🔒 ANTI SPAM

# ======================
# LOOP PAIR
# ======================
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
    volume_valid = df15["volume"].iloc[-1] > vol_ma.iloc[-1]

    # ===== DATA 5M =====
    close5 = df5["close"]
    ema50_5 = EMA(close5, 50)
    ema200_5 = EMA(close5, 200)
    macd5, macd_signal5, hist5 = MACD(close5)

    # ===== FILTER NO TRADE =====
    if no_trade_filter(df15, atr, vol_ma):
        continue

    # ======================
    # FLAGS
    # ======================
    side = None
    trend_valid = False
    macd_valid = False
    rsi_valid = False
    mtf_valid = False
    score = 0

    # ======================
    # TREND DETECTION (15M)
    # ======================
    if ema50_15.iloc[-1] > ema200_15.iloc[-1] and close15.iloc[-1] > ema50_15.iloc[-1]:
        side = "LONG"
        trend_valid = True

    elif ema50_15.iloc[-1] < ema200_15.iloc[-1] and close15.iloc[-1] < ema50_15.iloc[-1]:
        side = "SHORT"
        trend_valid = True

    if not side:
        continue

    # ======================
    # MACD (15M)
    # ======================
    if side == "LONG" and macd15.iloc[-1] > macd_signal15.iloc[-1] and hist15.iloc[-1] > 0:
        macd_valid = True

    if side == "SHORT" and macd15.iloc[-1] < macd_signal15.iloc[-1] and hist15.iloc[-1] < 0:
        macd_valid = True

    # ======================
    # RSI
    # ======================
    if side == "LONG" and 45 <= rsi_value <= 65:
        rsi_valid = True

    if side == "SHORT" and 35 <= rsi_value <= 55:
        rsi_valid = True

    # RSI Strength
    if side == "LONG":
        rsi_strength = "Weak" if rsi_value < 50 else "Ideal" if rsi_value <= 60 else "Late"
    else:
        rsi_strength = "Late" if rsi_value > 50 else "Ideal" if rsi_value >= 40 else "Weak"

    # ======================
    # MTF CONFIRMATION (5M)
    # ======================
    if side == "LONG":
        if ema50_5.iloc[-1] > ema200_5.iloc[-1] and macd5.iloc[-1] > macd_signal5.iloc[-1]:
            mtf_valid = True

    if side == "SHORT":
        if ema50_5.iloc[-1] < ema200_5.iloc[-1] and macd5.iloc[-1] < macd_signal5.iloc[-1]:
            mtf_valid = True

    # ======================
    # 🔒 ANTI SPAM
    # ======================
    if last_signal.get(symbol) == side:
        continue

    last_signal[symbol] = side

    # ======================
    # CONFIDENCE SCORING (REALISTIC)
    # ======================
    if trend_valid:
        score += 25

    if macd_valid:
        score += 20

    if rsi_valid:
        score += 15

    if volume_valid:
        score += 10
    else:
        score -= 5

    if mtf_valid:
        score += 10
    else:
        score -= 10

    display_score = max(0, min(score, 100))

    if display_score >= 80:
        conf_label = "HIGH CONFIDENCE 🚀"
    elif display_score >= 60:
        conf_label = "MEDIUM CONFIDENCE"
    else:
        conf_label = "LOW CONFIDENCE ⚠️"

    # ======================
    # ENTRY & RISK
    # ======================
    entry = close15.iloc[-1]
    sl, tps = calculate_levels(entry, atr, side)

    tz = pytz.timezone("Asia/Jakarta")
    now = datetime.datetime.now(tz).strftime("%H:%M")

    # ======================
    # REASON
    # ======================
    reason = (
        f"EMA trend {'bullish' if side=='LONG' else 'bearish'}, "
        f"MACD {'searah' if macd_valid else 'lemah'}, "
        f"RSI {rsi_strength.lower()}, "
        f"volume {'mendukung' if volume_valid else 'lemah'}, "
        f"MTF {'searah' if mtf_valid else 'belum searah'}"
    )

    # ======================
    # MESSAGE
    # ======================
    msg = f"""
{'📈' if side == 'LONG' else '📉'} {side} SIGNAL
🕒 Time: {now} WIB
🪙 {symbol}

📉 Trend EMA: {'🟢 EMA50 > EMA200' if side=='LONG' else '🔴 EMA50 < EMA200'}
📊 MACD: {'✅' if macd_valid else '❌'}
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

# ======================
# NO SIGNAL INFO
# ======================
if signals_today == 0:
    send_telegram("🤖 Bot aktif – belum ada moment entry")

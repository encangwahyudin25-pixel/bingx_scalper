from collections import Counter

signals_log = []

def log_signal(symbol, side, confidence):
    signals_log.append((symbol, side, confidence))

def weekly_report():
    total = len(signals_log)
    long = sum(1 for s in signals_log if s[1]=="LONG")
    short = total - long
    avg_conf = sum(s[2] for s in signals_log) / total if total else 0
    pair = Counter([s[0] for s in signals_log]).most_common(1)

    return f"""
📊 WEEKLY REPORT
Total Signal: {total}
LONG / SHORT: {long} / {short}
Avg Confidence: {avg_conf:.1f}%
Top Pair: {pair[0][0] if pair else '-'}
"""

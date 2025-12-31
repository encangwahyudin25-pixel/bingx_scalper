from datetime import datetime

def weekly_report(stats):
    return f"""
📊 *WEEKLY PERFORMANCE*
🗓 Week: {datetime.now().strftime('%Y-%m-%d')}

Total Signal : {stats['total']}
LONG / SHORT : {stats['long']} / {stats['short']}
Best Pair    : {stats['best_pair']}
Avg Confidence : {stats['confidence']}%

🤖 BingX Scalper Bot
"""

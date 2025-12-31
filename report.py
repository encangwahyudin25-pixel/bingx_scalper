from datetime import datetime

def weekly_report(stats):
    return f"""
📊 WEEKLY REPORT
Total Trade : {stats['total']}
Winrate     : {stats['winrate']}%
Profit      : {stats['profit']}%
Tanggal     : {datetime.now().strftime('%Y-%m-%d')}
"""

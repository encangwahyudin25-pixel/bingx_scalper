import requests
from config.telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

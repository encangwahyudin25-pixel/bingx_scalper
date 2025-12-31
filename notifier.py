import requests
from config.telegram_config import BOT_TOKEN, CHAT_ID

def send_signal(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

def heartbeat():
    send_signal("🤖 Bot AKTIF\nBelum ada moment entry saat ini.")

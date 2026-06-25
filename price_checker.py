import requests
import os
import time
from urllib.parse import quote

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_price(item_name):
    encoded = quote(item_name)
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={encoded}"
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('success'):
                return data.get('lowest_price', 'N/A')
            return 'N/A'
        except Exception:
            if attempt < 2:
                time.sleep(2)
    return '❌ خطا'

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()

def main():
    with open('skins.txt', 'r') as f:
        base_skins = [line.strip() for line in f if line.strip()]

    skins = [f"{s} (Factory New)" for s in base_skins]

    report = "📊 <b>گزارش هفتگی قیمت اسکین‌ها (Factory New)</b>\n"
    report += "━━━━━━━━━━━━━━━━━━━━━\n\n"

    # گروه‌بندی بر اساس اسلحه
    groups = {}
    for skin in skins:
        weapon = skin.split(' | ')[0]
        groups.setdefault(weapon, []).append(skin)

    for weapon, items in groups.items():
        report += f"🔫 <b>{weapon}</b>\n"
        for skin in items:
            price = get_price(skin)
            skin_name = skin.replace(f"{weapon} | ", "").replace(" (Factory New)", "")
            report += f"  🔹 {skin_name}: <b>{price}</b>\n"
            time.sleep(1.5)  # جلوگیری از بلاک شدن توسط Steam
        report += "\n"

    report += "━━━━━━━━━━━━━━━━━━━━━\n"
    report += "✅ گزارش کامل شد"

    # تلگرام محدودیت 4096 کاراکتر داره
    if len(report) > 4096:
        chunks = [report[i:i+4096] for i in range(0, len(report), 4096)]
        for chunk in chunks:
            send_telegram(chunk)
            time.sleep(0.5)
    else:
        send_telegram(report)

if __name__ == "__main__":
    main()

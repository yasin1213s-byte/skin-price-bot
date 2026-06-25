import requests
import os
import time
import json
from urllib.parse import quote

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
PRICES_FILE = 'last_prices.json'

def get_price(item_name):
    encoded = quote(item_name)
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={encoded}"
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('success'):
                price_str = data.get('lowest_price', '')
                price_num = float(price_str.replace('$', '').replace(',', ''))
                return price_num, price_str
            return None, 'N/A'
        except Exception:
            if attempt < 2:
                time.sleep(3)
    return None, '❌ خطا'

def load_last_prices():
    try:
        with open(PRICES_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_prices(prices):
    with open(PRICES_FILE, 'w') as f:
        json.dump(prices, f)

def change_emoji(pct):
    if pct > 0:
        return f"📈 +{pct:.1f}%"
    elif pct < 0:
        return f"📉 {pct:.1f}%"
    else:
        return "➡️ 0%"

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
    last_prices = load_last_prices()
    new_prices = {}

    report = "📊 <b>گزارش قیمت اسکین‌ها (Factory New)</b>\n"
    report += "━━━━━━━━━━━━━━━━━━━━━\n\n"

    groups = {}
    for skin in skins:
        weapon = skin.split(' | ')[0]
        groups.setdefault(weapon, []).append(skin)

    for weapon, items in groups.items():
        report += f"🔫 <b>{weapon}</b>\n"
        for skin in items:
            price_num, price_str = get_price(skin)
            skin_name = skin.replace(f"{weapon} | ", "").replace(" (Factory New)", "")

            if price_num is not None:
                new_prices[skin] = price_num
                if skin in last_prices:
                    pct = ((price_num - last_prices[skin]) / last_prices[skin]) * 100
                    change = change_emoji(pct)
                else:
                    change = "🆕"
                report += f"  🔹 {skin_name}: <b>{price_str}</b> {change}\n"
            else:
                report += f"  🔹 {skin_name}: {price_str}\n"

            time.sleep(1.5)
        report += "\n"

    report += "━━━━━━━━━━━━━━━━━━━━━\n"
    report += "✅ گزارش کامل شد"

    save_prices(new_prices)

    if len(report) > 4096:
        chunks = [report[i:i+4096] for i in range(0, len(report), 4096)]
        for chunk in chunks:
            send_telegram(chunk)
            time.sleep(0.5)
    else:
        send_telegram(report)

if __name__ == "__main__":
    main()

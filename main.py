import os
import requests
import asyncio
from datetime import datetime
from telethon import TelegramClient
from dotenv import load_dotenv

# --- Load ENV ---
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))
TO_USER_ID = int(os.getenv("TO_USER_ID"))
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

client = TelegramClient("x100_detector", API_ID, API_HASH)

# --- Fetch Trending CA from Pump.fun ---
async def fetch_trending_ca():
    try:
        res = requests.get("https://pump.fun/api/trending", timeout=10)
        print(f"[DEBUG] Status: {res.status_code}")
        print(f"[DEBUG] Text: {res.text}")
        return [item["address"] for item in res.json()[:10]]
    except Exception as e:
        print(f"[❌ fetch_trending_ca] {e}")
        return []

# --- Get Token Info from BirdEye ---
def fetch_token_info(ca):
    url = f"https://public-api.birdeye.so/public/token/{ca}"
    try:
        res = requests.get(url, headers={"X-API-KEY": BIRDEYE_API_KEY}, timeout=10)
        return res.json().get("data", {})
    except Exception as e:
        print(f"[❌ fetch_token_info] {e}")
        return {}

# --- Get Top Holders Info ---
def fetch_top_holders(ca):
    url = f"https://public-api.birdeye.so/public/token/top-holders?address={ca}&limit=5"
    try:
        res = requests.get(url, headers={"X-API-KEY": BIRDEYE_API_KEY}, timeout=10)
        return res.json().get("data", [])
    except Exception as e:
        print(f"[❌ fetch_top_holders] {e}")
        return []

# --- Skoring Token ---
def score_token(data, holders_info):
    score = 0
    liquidity = data.get("liquidity", 0)
    holders = data.get("holders", 0)
    market_cap = data.get("marketCap", 0)
    created_at = data.get("createdAtUnix", 0)

    if liquidity > 1000: score += 20
    if liquidity > 3000: score += 10
    if holders > 100: score += 15
    if holders > 300: score += 10
    if market_cap < 30000: score += 10
    if market_cap < 10000: score += 10

    if created_at:
        age_min = (datetime.utcnow().timestamp() - created_at) / 60
        if age_min < 60: score += 10

    if holders_info:
        top_pct = float(holders_info[0].get("percentage", 100))
        if top_pct < 10: score += 10
        elif top_pct > 30: score -= 10

    return score

# --- Kirim Notifikasi ---
async def notify(text):
    await client.send_message(OWNER_ID, text, parse_mode="md")

async def send_ca_only(ca):
    await client.send_message(TO_USER_ID, ca)

# --- Loop Utama Bot ---
async def monitor():
    await client.start()
    print("🚀 Bot started.")
    sent_set = set()

    while True:
        try:
            cas = await fetch_trending_ca()
            for ca in cas:
                if ca in sent_set:
                    continue

                data = fetch_token_info(ca)
                if not data or not data.get("symbol"): continue

                holders_info = fetch_top_holders(ca)
                score = score_token(data, holders_info)

                if score >= 60:
                    msg = (
                        f"🚀 *Token Potensial X100!*\n\n"
                        f"*Name:* {data.get('name')} ({data.get('symbol')})\n"
                        f"*CA:* `{ca}`\n"
                        f"*Liquidity:* ${data.get('liquidity',0):,.0f}\n"
                        f"*Holders:* {data.get('holders',0)}\n"
                        f"*Market Cap:* ${data.get('marketCap',0):,.0f}\n"
                        f"*Score:* {score}/100\n"
                        f"[🌐 Lihat di Pump.fun](https://pump.fun/{ca})"
                    )
                    await notify(msg)
                    await send_ca_only(ca)
                    sent_set.add(ca)
            await asyncio.sleep(60)
        except Exception as e:
            print(f"[ERROR LOOP] {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(monitor())

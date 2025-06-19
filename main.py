import re
import asyncio
import logging
import os
from datetime import datetime

from telethon import TelegramClient, events
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

# Load env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))
TO_USER_ID = int(os.getenv("TO_USER_ID"))
MONITOR_CHANNELS = [int(i) for i in os.getenv("MONITOR_CHANNELS").split(",") if i.strip()]

# Logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

client = TelegramClient("monitor_bot", API_ID, API_HASH)

# Regex for Solana CA (base58)
CA_REGEX = re.compile(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b')

# Fetch trending CA from Pump.fun via web scraping
def fetch_trending_ca():
    url = "https://pump.fun/trending"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"[ERROR] Failed to get page: {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        ca_list = []

        for a in soup.find_all("a", href=True):
            if "/token/" in a['href']:
                ca = a['href'].split("/token/")[-1]
                if 30 < len(ca) <= 44:
                    ca_list.append(ca)

        return list(dict.fromkeys(ca_list))[:10]

    except Exception as e:
        print(f"[ERROR] Scraping failed: {e}")
        return []

# Process and send detected CA
async def detect_and_forward_ca(event):
    text = event.message.message if event.message else ''
    matches = CA_REGEX.findall(text)

    if matches:
        ca_list = "\n".join(matches)
        sender = await event.get_sender()
        sender_name = sender.username or sender.first_name or "Unknown"

        logging.info(f"[CA DETECTED] From: {sender_name} | Matches: {ca_list}")

        # Kirim pesan penuh ke saved messages
        await client.send_message(OWNER_ID, f"📩 Pesan Baru dari {sender_name}:\n\n{text}")

        # Kirim CA list ke saved messages juga
        await client.send_message(OWNER_ID, f"🔍 CA Ditemukan:\n{ca_list}")

        # Kirim hanya CA ke TO_USER_ID
        await client.send_message(TO_USER_ID, ca_list)

# Event: Pesan baru di channel
@client.on(events.NewMessage(chats=MONITOR_CHANNELS))
async def handle_new_channel(event):
    print(f"[MESSAGE] New message in channel {event.chat.title or event.chat_id}")
    await detect_and_forward_ca(event)

# Heartbeat log
async def heartbeat():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[HEARTBEAT] {now}")
        logging.info("[HEARTBEAT]")
        await asyncio.sleep(2)

# Start bot
async def main():
    await client.start()
    print("🚀 Bot started.")

    # Debug: tampilkan 10 trending CA di awal
    cas = fetch_trending_ca()
    print(f"[DEBUG] Trending CA from Pump.fun:\n" + "\n".join(cas))

    await asyncio.gather(client.run_until_disconnected(), heartbeat())

if __name__ == "__main__":
    asyncio.run(main())
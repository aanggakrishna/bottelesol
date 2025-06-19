import os
import requests
from dotenv import load_dotenv
from telethon import TelegramClient

# Load ENV
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TO_USER_ID = int(os.getenv("TO_USER_ID"))
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

# Inisialisasi Telethon
client = TelegramClient('session_name', API_ID, API_HASH)

# Ambil token baru dari BirdEye
def get_new_tokens():
    url = "https://public-api.birdeye.so/public/tokenlist?sort=new"
    headers = {
        "X-API-KEY": BIRDEYE_API_KEY
    }
    response = requests.get(url, headers=headers)
    tokens = response.json().get("data", [])
    return tokens[:5]  # ambil 5 token teratas untuk contoh

# Kirim pesan ke Saved Messages
async def main():
    await client.start()

    tokens = get_new_tokens()
    message = "🆕 Token Baru dari BirdEye:\n\n"

    for token in tokens:
        name = token.get("name")
        symbol = token.get("symbol")
        price = token.get("price_usd")
        mc = token.get("mc", "-")
        message += f"🔸 {name} ({symbol})\n💲 Price: ${price:.6f}\n🧢 MC: {mc}\n\n"

    await client.send_message(TO_USER_ID, message)

with client:
    client.loop.run_until_complete(main())
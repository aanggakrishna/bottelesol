import os
import requests
import logging
from dotenv import load_dotenv
from telethon import TelegramClient

# 🔧 Setup Logging
logging.basicConfig(
    filename='birdeye_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ✅ Load ENV
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TO_USER_ID = int(os.getenv("TO_USER_ID"))
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

# ✅ Inisialisasi Telegram Client
client = TelegramClient('session_name', API_ID, API_HASH)

# ✅ Fungsi Ambil Token Baru
def get_new_tokens():
    url = "https://public-api.birdeye.so/public/tokenlist?sort=new"
    headers = {
        "X-API-KEY": BIRDEYE_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        logging.debug("API Response: %s", data)

        tokens = data.get("data", [])
        logging.info(f"Token Ditemukan: {len(tokens)}")
        return tokens
    except requests.exceptions.RequestException as e:
        logging.error(f"Gagal mengakses BirdEye API: {e}")
        return []

# ✅ Kirim Pesan ke Saved Messages
async def main():
    await client.start()

    tokens = get_new_tokens()
    message = "🆕 Token Baru dari BirdEye:\n\n"

    if not tokens:
        message += "❌ Tidak ada token baru atau gagal mengambil data dari BirdEye API."
    else:
        for token in tokens[:5]:
            try:
                name = token.get("name", "N/A")
                symbol = token.get("symbol", "N/A")
                price = token.get("price_usd", 0.0)
                mc = token.get("mc", "-")
                message += f"🔸 {name} ({symbol})\n💲 Price: ${price:.6f}\n🧢 MC: {mc}\n\n"
            except Exception as e:
                logging.error(f"Error parsing token: {e}")

    await client.send_message(TO_USER_ID, message)
    logging.info("Pesan dikirim ke Telegram.")

# ✅ Jalankan
with client:
    client.loop.run_until_complete(main())

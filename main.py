import os
import re
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telethon import TelegramClient
import logging
import json 
# --- Load .env ---
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))  # ID untuk Saved Messages
MONITOR_CHANNELS = [int(c) for c in os.getenv("MONITOR_CHANNELS").split(",") if c.strip()]

# --- Logging ke file ---
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Inisialisasi Telethon ---
client = TelegramClient("monitor_bot", API_ID, API_HASH)

# --- Fungsi untuk mengambil pesan selama 30 hari terakhir ---
# Ambil pesan dari channel

async def fetch_messages_from_channels():
    """Ambil semua pesan dari channel yang dimonitor selama 30 hari terakhir"""
    try:
        # Hitung tanggal 30 hari yang lalu
        thirty_days_ago = datetime.now() - timedelta(days=30)

        for channel_id in MONITOR_CHANNELS:
            try:
                # Ambil informasi channel
                channel = await client.get_entity(channel_id)
                channel_name = getattr(channel, "title", f"Unknown channel {channel_id}")
                logging.info(f"📥 Fetching messages from {channel_name} ({channel_id})")

                # List untuk menyimpan pesan
                messages = []

                # Ambil pesan dari channel
                async for message in client.iter_messages(channel, offset_date=thirty_days_ago):
    # Skip MessageService objects
    if message.action:  # Pesan layanan memiliki properti 'action'
        logging.info(f"⚠️ Pesan layanan dari {channel_name}, dilewati.")
        continue

    # Ambil teks pesan
    message_text = message.text or message.message or ""
    if not message_text and message.caption:
        message_text = message.caption

    if message_text:
        # Tambahkan pesan ke list
        messages.append({
            "date": message.date.isoformat(),
            "sender_id": message.sender_id,
            "text": message_text
        })
        logging.info(f"✅ Pesan dari {channel_name} ditambahkan ke list.")
    else:
        logging.info(f"⚠️ Pesan kosong dari {channel_name}, dilewati.")

                # Simpan semua pesan ke file JSON
                save_messages_to_json(channel_name, messages)

            except Exception as e:
                logging.error(f"❌ Error saat mengambil pesan dari channel {channel_id}: {e}")

    except Exception as e:
        logging.error(f"❌ Error saat mengambil pesan: {e}")

# --- Main ---
async def main():
    """Main entry point"""
    await client.start()
    print("✅ Bot is running...")
    logging.info("Bot started.")

    # Ambil pesan selama 30 hari terakhir
    await fetch_messages_from_channels()

    print("✅ Semua pesan selama 30 hari terakhir telah diambil.")
    logging.info("✅ Semua pesan selama 30 hari terakhir telah diambil.")

    # Stop client setelah selesai
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
import os
import sys
import asyncio
import logging
import importlib
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient
from dotenv import load_dotenv
from pyrogram import Client, idle, filters  # ✅ filters ditambah

# === SETUP DASAR ===
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# === KONEKSI DATABASE ===
try:
    mongo = MongoClient(MONGO_URI)
    db = mongo["garfieldbot"]
    logging.info("✅ MongoDB connected successfully.")
except Exception as e:
    logging.error(f"❌ MongoDB connection failed: {e}")
    db = None

# === INISIALISASI CLIENT ===
app = Client(
    "GarfieldBotManagement",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# === LOAD HANDLERS OTOMATIS ===
def load_handlers():
    handler_dir = os.path.join(os.getcwd(), "handlers")
    if not os.path.exists(handler_dir):
        os.makedirs(handler_dir)
        logging.warning("⚠️ Folder 'handlers' belum ada. Dibuat otomatis.")
        return

    for file in os.listdir(handler_dir):
        if file.endswith(".py") and not file.startswith("__"):
            module_path = f"handlers.{file[:-3]}"
            try:
                importlib.import_module(module_path)
                logging.info(f"📦 Loaded handler: {file}")
            except Exception as e:
                logging.error(f"❌ Failed to load handler {file}: {e}")

# === BACKUP OTOMATIS ===
async def daily_backup():
    try:
        now = datetime.now(timezone("Asia/Jakarta")).strftime("%Y%m%d_%H%M")
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        zip_path = os.path.join(backup_dir, f"backup_{now}.zip")
        os.system(f"zip -r {zip_path} data/ handlers/ utils/ database/ .env")
        logging.info(f"💾 Backup created: {zip_path}")
    except Exception as e:
        logging.error(f"⚠️ Backup failed: {e}")

# === RESTART OTOMATIS ===
async def restart_bot():
    try:
        logging.info("🔁 Restarting Garfield Bot Management...")
        await daily_backup()
        os.execv(sys.executable, ['python3'] + sys.argv)
    except Exception as e:
        logging.error(f"⚠️ Restart failed: {e}")

# === LOG AKTIVITAS PESAN ===
@app.on_message()
async def log_activity(client, message):
    try:
        chat = message.chat.title if message.chat.title else message.chat.id
        user = message.from_user.first_name if message.from_user else "Unknown"
        text = message.text or message.caption or "Media"
        logging.info(f"[{chat}] {user}: {text}")
    except Exception:
        pass

# === START COMMAND ===
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        f"🐾 Halo {message.from_user.mention}, selamat datang di <b>Garfield Management System</b>!\n"
        f"Bot aktif 24 jam penuh dan otomatis restart setiap 00:00 WIB.\n\n"
        f"Gunakan /help untuk melihat menu bantuan sesuai hak akses kamu."
    )

# === SCHEDULER (dipindah ke async function biar aman) ===
async def start_scheduler():
    scheduler = AsyncIOScheduler(timezone=timezone("Asia/Jakarta"))
    scheduler.add_job(daily_backup, "cron", hour=23, minute=55)
    scheduler.add_job(restart_bot, "cron", hour=0, minute=0)
    scheduler.start()

# ✅ Function ini biar bisa dipanggil main.py
async def start_bot(token=None):
    logging.info("🤖 Bot starting via start_bot()...")
    load_handlers()
    await start_scheduler()
    await app.start()
    logging.info("✅ Bot is running!")
    await idle()

# === MAIN ENTRY Jika dijalanin langsung ===
async def main():
    logging.info("🚀 Starting Garfield Bot Management (Full Version)...")
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped manually.")

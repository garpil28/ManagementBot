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

from pyrogram import Client, idle, filters  # <-- sudah diperbaiki

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

# === INISIALISASI CLIENT BOT ===
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
            try:
                module_name = file[:-3]
                importlib.import_module(f"handlers.{module_name}")
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
        os.system(f"zip -r {zip_path} data/ handlers/ utils/ db/ .env")
        logging.info(f"💾 Backup created: {zip_path}")
    except Exception as e:
        logging.error(f"⚠️ Backup failed: {e}")

# === RESTART OTOMATIS ===
async def restart_bot():
    try:
        logging.info("🔁 Restarting bot...")
        await daily_backup()
        os.execv(sys.executable, ['python3'] + sys.argv)
    except Exception as e:
        logging.error(f"⚠️ Restart failed: {e}")

# === JADWAL OTOMATIS ===
scheduler = AsyncIOScheduler(timezone=timezone("Asia/Jakarta"))
scheduler.add_job(daily_backup, "cron", hour=23, minute=55)
scheduler.add_job(restart_bot, "cron", hour=0, minute=0)
scheduler.start()

# === LOG SEMUA PESAN MASUK ===
@app.on_message()
async def log_activity(_, message):
    try:
        chat = message.chat.title if message.chat.title else message.chat.id
        user = message.from_user.first_name if message.from_user else "Unknown"
        text = message.text or message.caption or "Media"
        logging.info(f"[{chat}] {user}: {text}")
    except:
        pass

# === COMMAND START ===
@app.on_message(filters.command("start"))
async def start_command(_, message):
    await message.reply_text(
        f"🐾 Halo {message.from_user.mention}, selamat datang di *Garfield Management Bot*!\n\n"
        f"Gunakan /help untuk melihat menu."
    )

# === MAIN RUN ===
async def main():
    logging.info("🚀 Bot sedang dijalankan...")
    load_handlers()
    await app.start()
    logging.info("🔥 Bot berhasil hidup & berjalan!")
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Bot dimatikan manual.")

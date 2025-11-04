import os
import asyncio
import logging
import importlib
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient
from dotenv import load_dotenv
from pyrogram import Client

# ───────────────────────────────
# SETUP DASAR
# ───────────────────────────────
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ───────────────────────────────
# KONEKSI DATABASE
# ───────────────────────────────
try:
    mongo = MongoClient(MONGO_URI)
    db = mongo["garfieldbot"]
    logging.info("✅ MongoDB connected successfully.")
except Exception as e:
    logging.error(f"❌ MongoDB connection failed: {e}")
    db = None

# ───────────────────────────────
# INISIALISASI CLIENT
# ───────────────────────────────
app = Client(
    "GarfieldBotManagement",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ───────────────────────────────
# LOAD HANDLERS OTOMATIS
# ───────────────────────────────
def load_handlers():
    handler_dir = os.path.join(os.getcwd(), "handlers")
    for file in os.listdir(handler_dir):
        if file.endswith(".py") and not file.startswith("__"):
            name = file[:-3]
            module_path = f"handlers.{name}"
            try:
                importlib.import_module(module_path)
                logging.info(f"📦 Loaded handler: {name}")
            except Exception as e:
                logging.error(f"❌ Failed to load handler {name}: {e}")

# ───────────────────────────────
# FUNGSI BACKUP HARIAN
# ───────────────────────────────
async def daily_backup():
    try:
        now = datetime.now(timezone("Asia/Jakarta")).strftime("%Y%m%d_%H%M")
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        zip_path = os.path.join(backup_dir, f"backup_{now}.zip")
        os.system(f"zip -r {zip_path} data/")
        logging.info(f"💾 Backup created: {zip_path}")
    except Exception as e:
        logging.error(f"⚠️ Backup failed: {e}")

# ───────────────────────────────
# FUNGSI RESTART OTOMATIS
# ───────────────────────────────
async def restart_bot():
    try:
        logging.info("🔁 Restarting Garfield Bot Management ...")
        await daily_backup()
        os.execv(sys.executable, ['python3'] + sys.argv)
    except Exception as e:
        logging.error(f"⚠️ Restart failed: {e}")

# ───────────────────────────────
# JADWAL OTOMATIS
# ───────────────────────────────
scheduler = AsyncIOScheduler(timezone=timezone("Asia/Jakarta"))
scheduler.add_job(daily_backup, "cron", hour=23, minute=55)
scheduler.add_job(restart_bot, "cron", hour=0, minute=0)
scheduler.start()

# ───────────────────────────────
# EVENT STARTUP
# ───────────────────────────────
@app.on_message()
async def log_activity(client, message):
    # Log pesan user untuk keperluan audit ringan
    try:
        user = message.from_user.first_name if message.from_user else "Unknown"
        text = message.text or message.caption or "Media"
        logging.info(f"[{message.chat.title}] {user}: {text}")
    except:
        pass

# ───────────────────────────────
# MAIN ENTRY
# ───────────────────────────────
async def main():
    load_handlers()
    await app.start()
    logging.info("🤖 Garfield Bot Management started successfully.")
    await idle()

if __name__ == "__main__":
    from pyrogram import idle
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped manually.")

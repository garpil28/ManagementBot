import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# === Load Environment Variables ===
load_dotenv()

# === Project Imports ===
from config import BOT_TOKEN, MONGO_URI, OWNER_ID
from utils import scheduler, tools, backup, etc, timezone
from db import mongodb
from handlers import (
    help,
    owner_handlers,
    subowner_handlers,
    tagall_admin,
    catalog
)

# === Setup Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("ManagementBot")

# === Startup Functions ===
async def init_database():
    try:
        await mongodb.connect(MONGO_URI)
        logger.info("✅ Database connected successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

async def init_handlers():
    try:
        # Load handlers
        await help.register()
        await owner_handlers.register()
        await subowner_handlers.register()
        await tagall_admin.register()
        await catalog.register()
        logger.info("✅ All handlers loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Failed loading handlers: {e}")

async def init_schedulers():
    try:
        await scheduler.start()
        logger.info("✅ Scheduler started successfully.")
    except Exception as e:
        logger.warning(f"⚠️ Scheduler failed to start: {e}")

# === Main Function ===
async def main():
    logger.info("🚀 Starting ManagementBot...")

    # 1. Initialize Database
    await init_database()

    # 2. Load Handlers
    await init_handlers()

    # 3. Start Scheduler
    await init_schedulers()

    # 4. Start Backup Routine
    try:
        asyncio.create_task(backup.auto_backup())
        logger.info("💾 Auto-backup task initialized.")
    except Exception as e:
        logger.error(f"⚠️ Failed to start backup task: {e}")

    # 5. Start Main Bot
    try:
        from app import start_bot
        await start_bot(BOT_TOKEN)
    except Exception as e:
        logger.critical(f"🔥 Bot crashed: {e}")
        sys.exit(1)

# === Run the Bot ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Bot stopped manually.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

# db/mongodb.py — stable async MongoDB helper with auto reconnect
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI
from datetime import datetime

logger = logging.getLogger("MongoDB")

client = None
db = None
is_connected = False

# connect with auto retry
async def connect(uri: str, retries: int = 5, delay: int = 3):
    global client, db, is_connected
    for attempt in range(1, retries + 1):
        try:
            client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
            db = client["garfield_hq"]
            await db.command("ping")
            is_connected = True
            logger.info("✅ MongoDB connected successfully.")
            return
        except Exception as e:
            logger.warning(f"⚠️ MongoDB connection failed (attempt {attempt}/{retries}): {e}")
            await asyncio.sleep(delay)

    logger.critical("❌ MongoDB connection failed after multiple attempts. Exiting...")
    raise ConnectionError("Failed to connect to MongoDB after multiple attempts.")

# function to get a collection safely
def get_collection(name: str):
    if not is_connected or db is None:
        raise RuntimeError("Database not connected. Call connect() first.")
    return db[name]

# disconnect cleanly
async def disconnect():
    global client, is_connected
    if client:
        client.close()
        is_connected = False
        logger.info("🔌 MongoDB disconnected successfully.")

# helper — current UTC time ISO string
def now_iso():
    return datetime.utcnow().isoformat() + "Z"

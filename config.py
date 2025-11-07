
import os
from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")  # optional owner management bot
MONGO_URI = os.getenv("MONGO_URI", "")

AUTO_RESTART_HOUR = int(os.getenv("AUTO_RESTART_HOUR", "0"))
AUTO_RESTART_MINUTE = int(os.getenv("AUTO_RESTART_MINUTE", "0"))
BACKUP_HOUR = int(os.getenv("BACKUP_HOUR", "23"))
BACKUP_MINUTE = int(os.getenv("BACKUP_MINUTE", "55"))
BACKUP_FOLDER = os.getenv("BACKUP_FOLDER", "backups")

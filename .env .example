import os
from dotenv import load_dotenv
from datetime import timezone, timedelta

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
OWNER_BOT_TOKEN = os.getenv("OWNER_BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
MONGO_URI = os.getenv("MONGO_URI", "")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "0"))

# Restart & backup schedule (WIB in hours/minutes)
AUTO_RESTART_HOUR = int(os.getenv("AUTO_RESTART_HOUR", "0"))
AUTO_RESTART_MINUTE = int(os.getenv("AUTO_RESTART_MINUTE", "0"))
BACKUP_HOUR = int(os.getenv("BACKUP_HOUR", "0"))
BACKUP_MINUTE = int(os.getenv("BACKUP_MINUTE", "0"))
BACKUP_FOLDER = os.getenv("BACKUP_FOLDER", "backups")

TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")

# Safety
GIT_AUTO_PULL = os.getenv("GIT_AUTO_PULL", "true").lower() in ("1", "true", "yes")
REPO_UPDATE_GIT_URL = os.getenv("REPO_UPDATE_GIT_URL", "")

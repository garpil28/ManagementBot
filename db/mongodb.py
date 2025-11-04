# db/mongo.py — simple Mongo helper
from pymongo import MongoClient
from config import MONGO_URI
from datetime import datetime

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in config.py or .env")

client = MongoClient(MONGO_URI)
# database name: garfield_hq
db = client.garfield_hq

# collections
bots_col = db.bots          # stores sub-bot records
partners_col = db.partners  # partner metadata (owner info)
products_col = db.products  # products (global or per partner)
users_col = db.users        # known users by bot
backups_col = db.backups    # backup metadata

# helper
def now_iso():
    return datetime.utcnow().isoformat() + "Z"

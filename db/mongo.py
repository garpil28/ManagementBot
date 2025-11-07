from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.get_database("garfieladbot")

partners_col = db.get_collection("partners")   # partner docs (metadata only; secrets in secrets/)
bots_col = db.get_collection("bots")           # optional per-bot runtime config
products_col = db.get_collection("products")   # product docs
backups_col = db.get_collection("backups")     # backup records

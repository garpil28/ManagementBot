from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client['garfield_bot']

partners_col = db['partners']
bots_col = db['bots']
products_col = db['products']
backups_col = db['backups']

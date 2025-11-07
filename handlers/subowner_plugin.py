from pyrogram import Client, filters
from utils.helpers import safe_send
from db.mongo import partners_col

@Client.on_message(filters.command("setstore") & filters.private)
async def setstore(client, message):
    user_id = message.from_user.id
    rec = partners_col.find_one({"owner_id": user_id})
    if not rec:
        return await safe_send(client, message.chat.id, "⚠️ Kamu bukan sub-owner terdaftar.")
    payload = message.text.partition(' ')[2]
    if not payload:
        return await safe_send(client, message.chat.id, "Gunakan: /setstore Nama Toko")
    name = payload.strip()
    partners_col.update_one({"_id": rec["_id"]}, {"$set": {"store_name": name}})
    await safe_send(client, message.chat.id, "✅ Store updated.")

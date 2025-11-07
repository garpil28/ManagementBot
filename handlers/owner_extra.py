from pyrogram import Client, filters
from utils.helpers import safe_send
from db.mongo import partners_col
from config import OWNER_ID
from bson import ObjectId
import os

@Client.on_message(filters.command("listpartners") & filters.user(OWNER_ID))
async def list_partners(client, message):
    rows = list(partners_col.find())
    if not rows:
        return await safe_send(client, message.chat.id, "No partners yet.")
    s = "Partners:\n"
    for r in rows:
        s += f"• id:{r.get('_id')} type:{r.get('type')} store:{r.get('store_name')} enabled:{r.get('enabled')}\n"
    await safe_send(client, message.chat.id, s)

@Client.on_message(filters.command("delprem") & filters.user(OWNER_ID))
async def del_prem(client, message):
    args = message.text.split()
    if len(args) < 2:
        return await safe_send(client, message.chat.id, "Usage: /delprem <partner_id>")
    pid = args[1].strip()
    try:
        oid = ObjectId(pid)
    except:
        return await safe_send(client, message.chat.id, "Invalid partner id")
    doc = partners_col.find_one({"_id": oid})
    if doc:
        secret = doc.get("secret_path")
        if secret and os.path.exists(secret):
            try:
                os.remove(secret)
            except:
                pass
    partners_col.delete_one({"_id": oid})
    await safe_send(client, message.chat.id, "✅ Partner removed. Manager will stop it shortly.")

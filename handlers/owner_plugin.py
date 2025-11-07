import os
from pyrogram import Client, filters
from utils.helpers import safe_send
from db.mongo import partners_col
from utils.timezone import now_wib_iso
from config import OWNER_ID

SECRETS_DIR = os.path.join(os.getcwd(), "secrets")
os.makedirs(SECRETS_DIR, exist_ok=True)

# /addprem bot <BOT_TOKEN> <LOG_GROUP> <STORE_NAME>
# /addprem user <SESSION_STRING> <LOG_GROUP> <STORE_NAME>
@Client.on_message(filters.command("addprem") & filters.user(OWNER_ID))
async def addprem_cmd(client, message):
    args = message.text.split()
    if len(args) < 5:
        return await safe_send(client, message.chat.id, "Usage:\n/addprem bot <BOT_TOKEN> <LOG_GROUP> <STORE_NAME>\n/addprem user <SESSION_STRING> <LOG_GROUP> <STORE_NAME>")
    ptype = args[1].lower()
    key = args[2].strip()
    try:
        log_group = int(args[3])
    except:
        return await safe_send(client, message.chat.id, "LOG_GROUP_ID harus angka (contoh: -1001234567890)")
    store_name = " ".join(args[4:]).strip() or "My Store"

    # create DB doc WITHOUT secret content
    doc = {
        "type": "bot" if ptype != "user" else "user",
        "log_group": log_group,
        "store_name": store_name,
        "owner_id": message.from_user.id,
        "enabled": True,
        "created_at": now_wib_iso()
    }
    res = partners_col.insert_one(doc)
    pid = res.inserted_id

    # save secret on VPS: secrets/<pid>.secret
    secret_path = os.path.join(SECRETS_DIR, f"{str(pid)}.secret")
    try:
        with open(secret_path, "w") as f:
            f.write(key)
        os.chmod(secret_path, 0o600)
    except Exception as e:
        partners_col.delete_one({"_id": pid})
        return await safe_send(client, message.chat.id, f"❌ Gagal menyimpan secret: {e}")

    # update doc to reference secret_path (do not store token in DB)
    partners_col.update_one({"_id": pid}, {"$set": {"secret_path": secret_path}})

    await safe_send(client, message.chat.id, "✅ Partner ditambahkan. Manager akan auto-start dalam beberapa detik.")

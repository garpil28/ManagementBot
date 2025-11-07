from pyrogram import Client, filters
from utils.helpers import safe_send
from db.mongo import bots_col, partners_col

@Client.on_message(filters.command("jalan") & filters.group)
async def tagall_cmd(client, message):
    chat_id = message.chat.id
    bot_rec = bots_col.find_one({"group_id": chat_id})
    if bot_rec and bot_rec.get("tagall_enabled") is False:
        return await safe_send(client, chat_id, "🚫 Fitur TagAll dinonaktifkan untuk bot ini.")
    mentions = []
    admins = []
    try:
        async for m in client.get_chat_members(chat_id, filter="administrators"):
            if m.user and not m.user.is_bot:
                admins.append(m.user.id)
    except Exception as e:
        return await safe_send(client, chat_id, f"❌ Gagal ambil admin: {e}")

    for aid in admins:
        mentions.append(f"[👤](tg://user?id={aid})")
        if len(mentions) >= 5:
            await safe_send(client, chat_id, " ".join(mentions))
            mentions = []
    if mentions:
        await safe_send(client, chat_id, " ".join(mentions))
    await safe_send(client, chat_id, f"✅ Selesai memanggil {len(admins)} admin.")

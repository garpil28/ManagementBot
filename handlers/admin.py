# handlers/tagall_admin.py
# logic for /jalan command (tag admins only)
from pyrogram import filters
from pyrogram.types import Message
from db.mongo import db, bots_col
from utils.helpers import safe_send

async def is_admin(client, chat_id, user_id):
    try:
        async for m in client.get_chat_members(chat_id, filter="administrators"):
            if m.user and m.user.id == user_id:
                return True
    except Exception:
        return False
    return False


async def handle_jalan(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # find bot config for this token by matching owner's bot entry
    bot_rec = bots_col.find_one({'group_id': chat_id})
    # if not found, still allow but check default
    tagall_enabled = True
    if bot_rec:
        tagall_enabled = bot_rec.get('tagall_enabled', True)

    if not tagall_enabled:
        await safe_send(client, chat_id, '🚫 Fitur TagAll sedang dinonaktifkan oleh pemilik bot ini.')
        return

    # fetch admins list
    admins = []
    try:
        async for m in client.get_chat_members(chat_id, filter="administrators"):
            if m.user and not m.user.is_bot:
                admins.append(m.user.id)
    except Exception as e:
        await safe_send(client, chat_id, f"❌ Gagal mengambil daftar admin: {e}")
        return

    if not admins:
        await safe_send(client, chat_id, "⚠️ Tidak ada admin yang ditemukan di grup ini.")
        return

    # mention admins in batches of 5 to avoid very long message
    mentions = []
    count = 0
    for aid in admins:
        mentions.append(f"[👤](tg://user?id={aid})")
        count += 1
        if len(mentions) >= 5:
            teks = ' '.join(mentions)
            await safe_send(client, chat_id, teks)
            mentions.clear()
    if mentions:
        await safe_send(client, chat_id, ' '.join(mentions))

    await safe_send(client, chat_id, f"✅ Selesai memanggil {count} admin.")


# wrapper for Pyrogram
from pyrogram import Client

@Client.on_message(filters.command(['jalan']) & filters.group)
async def _on_jalan(client, message: Message):
    await handle_jalan(client, message)

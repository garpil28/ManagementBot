# handlers/subowner_handler.py — manage per-subowner settings via their bot PMs
from pyrogram import filters
from pyrogram.types import Message
from db.mongo import partners_col, bots_col
from utils.helpers import safe_send

@Client.on_message(filters.command(['setstore']) & filters.private)
async def _on_setstore(client, message: Message):
    # only allow if user is a registered subowner
    user_id = message.from_user.id
    rec = partners_col.find_one({'user_id': user_id})
    if not rec:
        await safe_send(client, message.chat.id, '⚠️ Kamu bukan sub-owner terdaftar.')
        return
    # simple format: /setstore Nama Toko | URL_BANNER
    payload = message.text.partition(' ')[2]
    if not payload:
        await safe_send(client, message.chat.id, 'Gunakan: /setstore Nama Toko | https://link-banner')
        return
    try:
        name, _, banner = payload.partition('|')
        name = name.strip()
        banner = banner.strip() if banner else rec.get('banner')
        partners_col.update_one({'user_id': user_id}, {'$set': {'store_name': name, 'banner': banner}})
        await safe_send(client, message.chat.id, '✅ Store updated.')
    except Exception as e:
        await safe_send(client, message.chat.id, f'❌ Gagal: {e}')

@Client.on_message(filters.command(['tagall_on','tagall_off']) & filters.private)
async def _on_toggle_tagall(client, message: Message):
    user_id = message.from_user.id
    rec = partners_col.find_one({'user_id': user_id})
    if not rec:
        await safe_send(client, message.chat.id, '⚠️ Kamu bukan sub-owner terdaftar.')
        return
    if message.text.startswith('/tagall_on'):
        bots_col.update_one({'owner_id': user_id}, {'$set': {'tagall_enabled': True}})
        await safe_send(client, message.chat.id, '✅ TagAll diaktifkan.')
    else:
        bots_col.update_one({'owner_id': user_id}, {'$set': {'tagall_enabled': False}})
        await safe_send(client, message.chat.id, '✅ TagAll dinonaktifkan.')

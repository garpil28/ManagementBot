# handlers/owner_handler.py — commands exclusive to the owner (OWNER_ID in config)
from pyrogram import filters
from pyrogram.types import Message
from config import OWNER_ID
from db.mongo import partners_col, bots_col
from utils.helpers import safe_send

@Client.on_message(filters.command(['addprem']) & filters.user(OWNER_ID))
async def _on_addprem(client, message: Message):
    # usage: /addprem <bot_token> <log_group_id> <store_name>
    args = message.text.split()
    if len(args) < 3:
        await safe_send(client, message.chat.id, 'Usage: /addprem <BOT_TOKEN> <LOG_GROUP_ID> <STORE_NAME>')
        return
    token = args[1]
    try:
        log_group = int(args[2])
    except:
        await safe_send(client, message.chat.id, 'LOG_GROUP_ID harus angka (contoh: -1001234567890)')
        return
    store_name = ' '.join(args[3:]) or 'My Store'
    # verify token — try creating temporary client
    try:
        from pyrogram import Client as PClient
        tmp = PClient('tmp', bot_token=token, api_id=int(os.getenv('API_ID')), api_hash=os.getenv('API_HASH'))
        tmp.start()
        bot_user = await tmp.get_me()
        await tmp.stop()
    except Exception as e:
        await safe_send(client, message.chat.id, f"❌ Token invalid atau gagal: {e}")
        return
    partners_col.insert_one({'bot_token': token, 'log_group': log_group, 'store_name': store_name, 'created_at': now_wib_iso()})
    await safe_send(client, message.chat.id, '✅ Partner added and will be loaded automatically.')

@Client.on_message(filters.command(['listprem']) & filters.user(OWNER_ID))
async def _on_listprem(client, message: Message):
    rows = list(partners_col.find())
    if not rows:
        await safe_send(client, message.chat.id, 'No partners yet.')
        return
    s = '📦 Partners:\n'
    for r in rows:
        s += f"• {r.get('store_name')} — log:{r.get('log_group')}\n"
    await safe_send(client, message.chat.id, s)

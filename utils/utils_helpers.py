# utils/helpers.py
import asyncio
from pyrogram.errors import FloodWait

async def safe_send(client, chat_id, text=None, **kwargs):
    try:
        return await client.send_message(chat_id, text, **kwargs)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await client.send_message(chat_id, text, **kwargs)
    except Exception as e:
        print("safe_send error:", e)
        return None

async def chunked_broadcast(client, chat_id_list, text, batch=20, delay=1):
    """Send to chat_id_list in chunks; handles FloodWait."""
    n = 0
    for cid in chat_id_list:
        try:
            await safe_send(client, cid, text)
        except Exception as e:
            print("broadcast to", cid, "failed", e)
        n += 1
        if n % batch == 0:
            await asyncio.sleep(delay)

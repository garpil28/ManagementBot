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

# subbot_runner.py — dynamic loader for partner bots
import asyncio
import threading
from pyrogram import Client
from db.mongo import partners_col, bots_col
from config import API_ID, API_HASH
from utils.timezone import now_wib_iso

# mapping token -> client and task
SUBCLIENTS = {}

async def start_subbot(token, owner_doc):
    name = f"subbot_{owner_doc.get('_id')}"
    client = Client(name, api_id=API_ID, api_hash=API_HASH, bot_token=token)
    await client.start()
    print(f"[+] Subbot started for {owner_doc.get('store_name')}")
    # store runtime record
    bots_col.update_one({'bot_token': token}, {'$set': {'active': True, 'started_at': now_wib_iso()}}, upsert=True)
    SUBCLIENTS[token] = client
    try:
        await asyncio.Event().wait()  # keep running until stopped
    finally:
        await client.stop()
        bots_col.update_one({'bot_token': token}, {'$set': {'active': False, 'stopped_at': now_wib_iso()}})


def spawn_all(loop):
    # spawn tasks for each partner
    for p in partners_col.find():
        token = p.get('bot_token')
        if token in SUBCLIENTS:
            continue
        # schedule start
        asyncio.run_coroutine_threadsafe(start_subbot(token, p), loop)


def stop_subbot(token):
    client = SUBCLIENTS.get(token)
    if not client:
        return False
    loop = asyncio.get_event_loop()
    loop.create_task(client.stop())
    SUBCLIENTS.pop(token, None)
    return True

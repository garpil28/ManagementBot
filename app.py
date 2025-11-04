# app.py — Garfield HQ main launcher
import asyncio
import os
from pyrogram import Client, idle
from config import OWNER_BOT_TOKEN, API_ID, API_HASH, OWNER_ID, AUTO_RESTART_HOUR, AUTO_RESTART_MINUTE, BACKUP_HOUR, BACKUP_MINUTE
from db.mongo import partners_col
from subbot_runner import spawn_all
from utils.scheduler import start_scheduler

# owner main client
app = Client('garfield_owner', api_id=API_ID, api_hash=API_HASH, bot_token=OWNER_BOT_TOKEN)


async def main():
    print('[🚀] Starting Garfield HQ Owner Bot...')
    await app.start()
    loop = asyncio.get_event_loop()
    # spawn subbots in background
    spawn_all(loop)
    # start scheduler (restart & backup)
    start_scheduler(loop)
    print('[✅] All modules loaded. Bot running.')
    await idle()
    await app.stop()

if name == 'main':
    asyncio.run(main())

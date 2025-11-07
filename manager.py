import asyncio
import logging
import os
from pyrogram import Client
from db.mongo import partners_col
from config import API_ID, API_HASH, BOT_TOKEN
from utils.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
ROOT = os.getcwd()
SECRETS_DIR = os.path.join(ROOT, "secrets")
os.makedirs(SECRETS_DIR, exist_ok=True)

clients = {}  # session_name -> Client instance

async def start_partner_client_by_doc(doc):
    try:
        ptype = doc.get("type", "bot")
        pid = str(doc.get("_id"))
        session_name = f"partner_{pid}"
        secret_path = doc.get("secret_path")
        if not secret_path:
            logging.error("doc missing secret_path for partner %s", pid)
            return None
        if not os.path.exists(secret_path):
            logging.error("secret file not found for %s", secret_path)
            return None
        with open(secret_path, "r") as f:
            secret = f.read().strip()

        if ptype == "bot":
            token = secret
            app = Client(session_name, api_id=API_ID, api_hash=API_HASH, bot_token=token, plugins={'root': 'handlers'})
        else:
            # user session string
            session_str = secret
            app = Client(session_name, api_id=API_ID, api_hash=API_HASH, session_string=session_str, plugins={'root': 'handlers'})

        await app.start()
        logging.info(f"[spawn] started client {session_name}")
        return app
    except Exception as e:
        logging.error(f"[spawn] failed to start partner: {e}")
        return None

async def spawn_existing_partners():
    rows = list(partners_col.find({"enabled": {"$ne": False}}))
    for r in rows:
        pid = str(r.get("_id"))
        session = f"partner_{pid}"
        if session in clients:
            continue
        app = await start_partner_client_by_doc(r)
        if app:
            clients[session] = app

async def watch_for_new_partners(poll_interval=5):
    while True:
        try:
            await spawn_existing_partners()
        except Exception as e:
            logging.error("watcher error: %s", e)
        await asyncio.sleep(poll_interval)

async def stop_and_remove_client(session_key):
    app = clients.get(session_key)
    if not app:
        return False
    try:
        await app.stop()
    except Exception as e:
        logging.error("stop client error: %s", e)
    clients.pop(session_key, None)
    return True

async def main():
    loop = asyncio.get_event_loop()
    # start scheduler background tasks
    start_scheduler(loop)

    # start owner manager bot if BOT_TOKEN present
    if BOT_TOKEN:
        owner_doc = {"type":"bot","secret_path":os.path.join(SECRETS_DIR, "owner_manager.secret")}
        try:
            with open(owner_doc["secret_path"], "w") as f:
                f.write(BOT_TOKEN)
            os.chmod(owner_doc["secret_path"], 0o600)
            app = await start_partner_client_by_doc(owner_doc)
            if app:
                clients["owner_manager"] = app
        except Exception as e:
            logging.error("owner manager creation failed: %s", e)

    # spawn partners from DB
    await spawn_existing_partners()

    # start watcher to auto-start newly added partners
    loop.create_task(watch_for_new_partners())

    logging.info("Manager running — all clients started (if any).")
    await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

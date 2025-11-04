# utils/tools.py
# ==========================================================
# Garfield Bot Management — Tools & Helper Functions
# Utility pendukung global buat semua handler
# ==========================================================

import asyncio
import datetime
import pytz
import random
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message
)
from pyrogram.errors import FloodWait, RPCError

from emoji_list import EMOJIS

# Zona waktu WIB (Jakarta)
TZ = pytz.timezone("Asia/Jakarta")

# ----------------------------------------------------------
# Fungsi waktu
# ----------------------------------------------------------
def wib_now(fmt: str = "%d-%m-%Y %H:%M:%S"):
    """Ambil waktu saat ini dalam format WIB"""
    return datetime.datetime.now(TZ).strftime(fmt)

def wib_today():
    """Ambil tanggal sekarang (WIB)"""
    return datetime.datetime.now(TZ).strftime("%d-%m-%Y")

# ----------------------------------------------------------
# Fungsi aman untuk kirim pesan (hindari FloodWait)
# ----------------------------------------------------------
async def safe_send(client, chat_id: int, text: str, **kwargs):
    """Kirim pesan aman (auto handle FloodWait)"""
    try:
        return await client.send_message(chat_id, text, **kwargs)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await safe_send(client, chat_id, text, **kwargs)
    except RPCError as e:
        print(f"[WARN] Gagal kirim pesan: {e}")
        return None

# ----------------------------------------------------------
# Fungsi kirim reply aman
# ----------------------------------------------------------
async def safe_reply(message: Message, text: str, **kwargs):
    try:
        return await message.reply_text(text, **kwargs)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await safe_reply(message, text, **kwargs)
    except RPCError as e:
        print(f"[WARN] Gagal reply: {e}")
        return None

# ----------------------------------------------------------
# Fungsi kirim media (foto katalog, banner, dll)
# ----------------------------------------------------------
async def send_photo_safe(client, chat_id: int, photo_url: str, caption: str, **kwargs):
    try:
        return await client.send_photo(chat_id, photo_url, caption=caption, **kwargs)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_photo_safe(client, chat_id, photo_url, caption, **kwargs)
    except Exception as e:
        print(f"[WARN] send_photo_safe error: {e}")
        return None

# ----------------------------------------------------------
# Fungsi log untuk group log
# ----------------------------------------------------------
async def log_event(client, log_group: int, text: str):
    """Kirim log event ke grup log masing-masing"""
    try:
        ts = wib_now()
        await safe_send(client, log_group, f"🕓 <b>{ts}</b>\n{text}", disable_web_page_preview=True)
    except Exception as e:
        print(f"[LOG_WARN] gagal kirim log: {e}")

# ----------------------------------------------------------
# Fungsi buat tombol dinamis
# ----------------------------------------------------------
def make_buttons(buttons: list):
    """Buat InlineKeyboardMarkup dari list of list"""
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, url=url)] for text, url in buttons])

def make_callback_buttons(buttons: list):
    """Buat tombol callback"""
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons])

# ----------------------------------------------------------
# Fungsi tag emoji random
# ----------------------------------------------------------
def random_emoji(count: int = 1):
    """Ambil emoji random dari daftar"""
    return " ".join(random.choice(EMOJIS) for _ in range(count))

# ----------------------------------------------------------
# Format teks pesan
# ----------------------------------------------------------
def format_user(user):
    """Format mention user"""
    if not user:
        return "Unknown"
    return f"[{user.first_name}](tg://user?id={user.id})"

def format_catalog_item(item):
    """Format tampilan katalog produk"""
    text = f"🛍️ <b>{item['name']}</b>\n"
    text += f"💬 {item['desc']}\n"
    text += f"💰 <b>Harga:</b> {item['price']}\n"
    text += f"📦 ID Produk: <code>{item['_id']}</code>\n"
    text += f"🕓 Ditambahkan: {item['added_at']:%d-%m-%Y %H:%M}"
    return text

# ----------------------------------------------------------
# Fungsi backup log zip (panggil dari owner)
# ----------------------------------------------------------
import os
import zipfile

def create_log_backup(folder="logs"):
    """Zip semua file log di folder tertentu"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = f"{folder}/log_backup_{wib_today()}.zip"
    with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                path = os.path.join(root, file)
                zipf.write(path, os.path.relpath(path, folder))
    return filename

# ----------------------------------------------------------
# Fungsi delay utility (misal buat tagall, broadcast, dll)
# ----------------------------------------------------------
async def sleep_delay(sec):
    """Delay async"""
    await asyncio.sleep(sec)

# ----------------------------------------------------------
# Fungsi random ID generator
# ----------------------------------------------------------
import secrets
def random_id(prefix="GARF"):
    """Generate ID unik"""
    rand = secrets.token_hex(3).upper()
    return f"{prefix}-{rand}"

# ----------------------------------------------------------
# Fungsi broadcast ke semua subs
# ----------------------------------------------------------
async def broadcast_message(client, user_ids: list, text: str):
    success, failed = 0, 0
    for uid in user_ids:
        try:
            await safe_send(client, uid, text)
            success += 1
        except Exception:
            failed += 1
            continue
        await asyncio.sleep(0.3)
    return success, failed

# ----------------------------------------------------------
# Fungsi convert waktu ke WIB readable
# ----------------------------------------------------------
def format_time_diff(seconds):
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours} jam {minutes} menit"
    elif minutes:
        return f"{minutes} menit {sec} detik"
    else:
        return f"{sec} detik"

# ----------------------------------------------------------
# Fungsi log global startup
# ----------------------------------------------------------
def startup_banner(bot_name):
    print("=======================================")
    print(f"🚀 Starting {bot_name}")
    print(f"🕓 Time: {wib_now()}")
    print(f"📍 Timezone: WIB (Asia/Jakarta)")
    print("=======================================")

# handlers/help.py — Garfield Bot Management (Help Menu)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from dotenv import load_dotenv

load_dotenv()

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Simulasi data sub owner (bisa ambil dari database juga)
SUB_OWNERS = []

def get_help_text(user_id: int):
    """Beda tampilan help tergantung role user."""
    if user_id == OWNER_ID:
        return (
            "<b>👑 Garfield Management — Owner Menu</b>\n\n"
            "Perintah penting untuk pemilik utama:\n"
            "• /addprem <user_id> — Tambahkan sub-owner baru\n"
            "• /delprem <user_id> — Hapus sub-owner\n"
            "• /broadcast — Kirim pesan ke semua pengguna aktif\n"
            "• /backup — Buat file backup manual\n"
            "• /restart — Restart bot manual\n"
            "• /dbcheck — Cek status database\n"
            "\n"
            "<i>Owner bisa kontrol penuh semua subs & data Mongo Atlas.</i>"
        )

    elif user_id in SUB_OWNERS:
        return (
            "<b>🛠️ Garfield Management — Sub Owner</b>\n\n"
            "Menu kontrol untuk sub-owner bot:\n"
            "• /setstore — Ubah nama toko kamu\n"
            "• /setbanner — Ganti foto/banner toko\n"
            "• /catalog — Lihat & edit katalog jualanmu\n"
            "• /addproduct — Tambah produk baru\n"
            "• /delproduct — Hapus produk\n"
            "• /tagadmin — Tag semua admin grup kamu\n"
            "• /onofftag — Aktif/Nonaktifkan fitur tag admin\n"
            "\n"
            "<i>Sub-owner punya kontrol penuh di bot mereka sendiri.</i>"
        )

    else:
        return (
            "<b>🛍️ Garfield Store Bot</b>\n\n"
            "Selamat datang di sistem GarfieldBot! 🐾\n\n"
            "Gunakan tombol di bawah ini untuk melihat produk dan informasi.\n\n"
            "• Klik <b>📦 Katalog Produk</b> untuk melihat daftar jualan.\n"
            "• Klik <b>💬 Hubungi Admin</b> untuk bantuan langsung.\n\n"
            "<i>GarfieldBot aktif 24 jam — nikmati belanja otomatis!</i>"
        )

@Client.on_message(filters.command("help"))
async def help_command(client, message):
    user_id = message.from_user.id
    help_text = get_help_text(user_id)

    # Tombol beda sesuai role
    if user_id == OWNER_ID:
        buttons = [
            [InlineKeyboardButton("📢 Broadcast", callback_data="owner:broadcast"),
             InlineKeyboardButton("💾 Backup", callback_data="owner:backup")],
            [InlineKeyboardButton("➕ AddPrem", callback_data="owner:addprem"),
             InlineKeyboardButton("♻️ Restart", callback_data="owner:restart")]
        ]
    elif user_id in SUB_OWNERS:
        buttons = [
            [InlineKeyboardButton("📦 Katalog", callback_data="sub:catalog"),
             InlineKeyboardButton("🖼️ Banner", callback_data="sub:banner")],
            [InlineKeyboardButton("⚙️ Setting Store", callback_data="sub:setting")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton("📦 Katalog Produk", callback_data="user:catalog")],
            [InlineKeyboardButton("💬 Hubungi Admin", url="https://t.me/kopi567")]
        ]

    await message.reply_photo(
        photo="https://telegra.ph/file/98ab6a3d0e12d53e7b548.jpg",
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

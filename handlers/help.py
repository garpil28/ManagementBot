from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID

@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    uid = message.from_user.id
    if uid == OWNER_ID:
        text = "<b>Owner Menu</b>\n/addprem <bot|user> <TOKEN/SESSION> <LOG_GROUP> <STORE_NAME>\n/listpartners\n/delprem <id>\n/reloadclients"
        kb = [[InlineKeyboardButton("Manage Partners", callback_data="owner:partners")]]
    else:
        text = "<b>User Menu</b>\nGunakan tombol di bawah untuk akses katalog."
        kb = [[InlineKeyboardButton("Catalog", callback_data="cat:None:0")]]
    await message.reply(text, reply_markup=InlineKeyboardMarkup(kb))

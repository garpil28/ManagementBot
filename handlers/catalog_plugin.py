from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.mongo import products_col

PAGE_SIZE = 6

def build_kb_for_items(items, page):
    start = page * PAGE_SIZE
    chunk = items[start:start+PAGE_SIZE]
    kb = []
    for it in chunk:
        kb.append([InlineKeyboardButton(f"{it.get('name')} — Rp{it.get('price')}", callback_data=f"prod:{it.get('_id')}")])
    nav = []
    if start > 0:
        nav.append(InlineKeyboardButton("⏮️ Prev", callback_data=f"cat:0:{page-1}"))
    if start + PAGE_SIZE < len(items):
        nav.append(InlineKeyboardButton("Next ⏭️", callback_data=f"cat:0:{page+1}"))
    if nav:
        kb.append(nav)
    return InlineKeyboardMarkup(kb)

@Client.on_message(filters.command(["catalog","produk"]) & filters.private)
async def catalog_cmd(client, message):
    items = list(products_col.find({}))
    kb = build_kb_for_items(items, 0)
    await message.reply_text("📦 Pilih produk:", reply_markup=kb)

@Client.on_callback_query(filters.regex(r"^cat:"))
async def on_cat(c, cq):
    _, owner_s, page_s = cq.data.split(":")
    page = int(page_s)
    items = list(products_col.find({}))
    kb = build_kb_for_items(items, page)
    await cq.message.edit_reply_markup(kb)

@Client.on_callback_query(filters.regex(r"^prod:"))
async def on_prod(c, cq):
    pid = cq.data.split(":",1)[1]
    doc = products_col.find_one({"_id": pid})
    if not doc:
        await cq.answer("Produk tidak ditemukan", show_alert=True)
        return
    text = f"*{doc.get('name')}*\n\n{doc.get('desc')}\n\nHarga: Rp{doc.get('price')}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Beli Sekarang", callback_data=f"buy:{pid}")], [InlineKeyboardButton("⬅️ Kembali", callback_data="cat:0:0")]])
    await cq.message.edit(text, reply_markup=kb)

# handlers/catalog.py — simple unlimited pagination catalog via inline buttons
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.mongo import products_col
from pyrogram.types import CallbackQuery

PAGE_SIZE = 6

async def make_category_keyboard(owner_id, page=0):
    # fetch all products for owner or global
    query = {'owner_id': owner_id} if owner_id else {}
    items = list(products_col.find(query))
    start = page * PAGE_SIZE
    chunk = items[start:start+PAGE_SIZE]
    kb = []
    for it in chunk:
        kb.append([InlineKeyboardButton(f"{it.get('name')} — Rp{it.get('price')}", callback_data=f"prod:{it.get('_id')}")])
    nav = []
    if start > 0:
        nav.append(InlineKeyboardButton('⏮️ Prev', callback_data=f'cat:{owner_id}:{page-1}'))
    if start + PAGE_SIZE < len(items):
        nav.append(InlineKeyboardButton('Next ⏭️', callback_data=f'cat:{owner_id}:{page+1}'))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton('🏪 STORE', url='https://t.me/storegarf')])
    return InlineKeyboardMarkup(kb)


@Client.on_message(filters.command(['catalog', 'produk']) & filters.private)
async def _on_catalog(client, message):
    owner_id = None
    kb = await make_category_keyboard(owner_id, page=0)
    await message.reply_text('📦 Pilih produk:', reply_markup=kb)


@Client.on_callback_query(filters.regex(r'^cat:'))
async def _on_cat_paged(c, cq: CallbackQuery):
    _, owner_s, page_s = cq.data.split(':')
    owner_id = None if owner_s in ('None', '0', '') else int(owner_s)
    page = int(page_s)
    kb = await make_category_keyboard(owner_id, page=page)
    await cq.message.edit_reply_markup(kb)


@Client.on_callback_query(filters.regex(r'^prod:'))
async def _on_prod(c, cq: CallbackQuery):
    pid = cq.data.split(':', 1)[1]
    doc = products_col.find_one({'_id': pid})
    if not doc:
        await cq.answer('Produk tidak ditemukan', show_alert=True)
        return
    text = f"*{doc.get('name')}*\n\n{doc.get('desc')}\n\nHarga: Rp{doc.get('price')}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton('💳 Beli Sekarang', callback_data=f'buy:{pid}')], [InlineKeyboardButton('⬅️ Kembali', callback_data='cat:None:0')]])
    await cq.message.edit(text, reply_markup=kb)

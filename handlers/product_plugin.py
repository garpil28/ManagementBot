from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from db.mongo import products_col, partners_col
from utils.helpers import safe_send
from bson import ObjectId
from utils.timezone import now_wib_iso

PAGE_SIZE = 6

def product_to_text(doc):
    lines = []
    lines.append(f"🛍️ <b>{doc.get('name')}</b>")
    if doc.get('price') is not None:
        lines.append(f"💰 Harga: Rp{doc.get('price')}")
    if doc.get('stock') is not None:
        lines.append(f"📦 Stok: {doc.get('stock')}")
    if doc.get('desc'):
        lines.append("\n" + doc.get('desc'))
    if doc.get('payment_info'):
        lines.append("\n<b>Info Pembayaran:</b>\n" + doc.get('payment_info'))
    lines.append(f"\n<code>id: {doc.get('_id')}</code>")
    return "\n".join(lines)

@Client.on_message(filters.command("addproduct") & filters.private)
async def add_product(client, message: Message):
    user_id = message.from_user.id
    partner = partners_col.find_one({"owner_id": user_id})
    if not partner:
        return await safe_send(client, message.chat.id, "⚠️ Kamu bukan sub-owner terdaftar.")

    payload = message.text.partition(' ')[2]
    if not payload:
        return await safe_send(client, message.chat.id, "Gunakan:\n/addproduct <name> | <price> | <stock> | <desc> | <payment_info>")

    parts = [p.strip() for p in payload.split("|")]
    name = parts[0] if len(parts) > 0 else None
    price = None
    stock = None
    try:
        price = int(parts[1]) if len(parts) > 1 and parts[1] != "" else None
    except:
        price = None
    try:
        stock = int(parts[2]) if len(parts) > 2 and parts[2] != "" else None
    except:
        stock = None
    desc = parts[3] if len(parts) > 3 else ""
    payment_info = parts[4] if len(parts) > 4 else ""

    doc = {
        "name": name,
        "price": price,
        "stock": stock,
        "desc": desc,
        "payment_info": payment_info,
        "owner_ref": partner.get("_id"),
        "created_at": now_wib_iso()
    }
    res = products_col.insert_one(doc)
    await safe_send(client, message.chat.id, f"✅ Produk ditambahkan. ID: {res.inserted_id}")

@Client.on_message(filters.command("editproduct") & filters.private)
async def edit_product(client, message: Message):
    user_id = message.from_user.id
    partner = partners_col.find_one({"owner_id": user_id})
    if not partner:
        return await safe_send(client, message.chat.id, "⚠️ Kamu bukan sub-owner terdaftar.")

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        return await safe_send(client, message.chat.id, "Usage: /editproduct <id> field=value|...")

    pid = args[1].strip()
    updates_raw = args[2].strip()
    updates = {}
    for pair in updates_raw.split("|"):
        if "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k in ("price", "stock"):
            try:
                v = int(v)
            except:
                continue
        updates[k] = v

    try:
        oid = ObjectId(pid)
    except:
        return await safe_send(client, message.chat.id, "ID produk invalid.")

    doc = products_col.find_one({"_id": oid, "owner_ref": partner.get("_id")})
    if not doc:
        return await safe_send(client, message.chat.id, "Produk tidak ditemukan atau bukan milikmu.")

    products_col.update_one({"_id": oid}, {"$set": updates})
    await safe_send(client, message.chat.id, "✅ Produk diupdate.")

@Client.on_message(filters.command("delproduct") & filters.private)
async def delete_product(client, message: Message):
    user_id = message.from_user.id
    partner = partners_col.find_one({"owner_id": user_id})
    if not partner:
        return await safe_send(client, message.chat.id, "⚠️ Kamu bukan sub-owner terdaftar.")

    args = message.text.split()
    if len(args) < 2:
        return await safe_send(client, message.chat.id, "Usage: /delproduct <id>")

    pid = args[1].strip()
    try:
        oid = ObjectId(pid)
    except:
        return await safe_send(client, message.chat.id, "ID produk invalid.")

    doc = products_col.find_one({"_id": oid, "owner_ref": partner.get("_id")})
    if not doc:
        return await safe_send(client, message.chat.id, "Produk tidak ditemukan atau bukan milikmu.")

    products_col.delete_one({"_id": oid})
    await safe_send(client, message.chat.id, "✅ Produk dihapus.")

@Client.on_message(filters.command("myproducts") & filters.private)
async def my_products_list(client, message: Message):
    user_id = message.from_user.id
    partner = partners_col.find_one({"owner_id": user_id})
    if not partner:
        return await safe_send(client, message.chat.id, "⚠️ Kamu bukan sub-owner terdaftar.")
    items = list(products_col.find({"owner_ref": partner.get("_id")}))
    if not items:
        return await safe_send(client, message.chat.id, "Belum ada produk.")
    s = "📦 Produkmu:\n"
    for it in items:
        s += f"• {it.get('name')} — Rp{it.get('price')} (id: {it.get('_id')})\n"
    await safe_send(client, message.chat.id, s)

@Client.on_message(filters.command("product") & filters.private)
async def product_detail(client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await safe_send(client, message.chat.id, "Usage: /product <id>")
    pid = args[1].strip()
    try:
        oid = ObjectId(pid)
    except:
        return await safe_send(client, message.chat.id, "ID produk invalid.")
    doc = products_col.find_one({"_id": oid})
    if not doc:
        return await safe_send(client, message.chat.id, "Produk tidak ditemukan.")
    text = product_to_text(doc)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("💳 Beli Sekarang", callback_data=f"buy:{pid}")]])
    await message.reply(text, reply_markup=kb)

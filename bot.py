#!/usr/bin/env python3
"""
🔍 Phone Number Intelligence Bot
Beautiful Buttons + Per User Expiry
Final Version - All Fixed
"""

import json
import requests
from datetime import date, timedelta
from pathlib import Path
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest

# ================== CONFIG ==================
BOT_TOKEN     = "8642873626:AAHkybZD5LBO7331YisbProHnp1P8e6nhQQ"
ADMIN_ID      = 5057489358
DEFAULT_PIN   = "764523"
API_URL       = "https://lk-api-pinsstm.ramaxinfo.workers.dev/"
DATA_FILE     = Path("users.json")
OWNER_CONTACT = "@theplayerror"

# Conversation states
WAITING_SINGLE = 1
WAITING_BATCH  = 2
ADMIN_ADD_ID   = 3
ADMIN_ADD_EXP  = 4
ADMIN_REM_ID   = 5
ADMIN_EXP_ID   = 6
ADMIN_EXP_DATE = 7


# ================== DATA ==================
def load_users():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except:
            return {}
    return {}


def save_users(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))


def check_access(user_id: int):
    users = load_users()
    uid   = str(user_id)

    if uid not in users:
        return False, "❌ No subscription", 0

    expiry_str = users[uid].get("expiry", "")
    try:
        expiry = date.fromisoformat(expiry_str)
        if date.today() > expiry:
            return False, f"❌ Expired on {expiry}", 0
        days = (expiry - date.today()).days
        return True, f"✅ Active ({days} days left)", days
    except:
        return False, "❌ Invalid license", 0


def search_api(term: str):
    try:
        r = requests.get(
            API_URL,
            params={"pin": DEFAULT_PIN, "term": term},
            timeout=20,
        )
        r.raise_for_status()
        return {"ok": True, "data": r.json()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def format_result(number, data):
    if isinstance(data, dict):
        lines = [f"📱 *Result for {number}*\n"]
        for k, v in data.items():
            if v not in (None, ""):
                emoji = get_emoji(k)
                lines.append(
                    f"{emoji} *{k.replace('_', ' ').title()}*: `{v}`"
                )
        return "\n".join(lines) if len(lines) > 1 else f"📱 *{number}*\n_No data found_"
    return f"📱 *{number}*\n`{str(data)}`"


def get_emoji(key):
    key    = key.lower()
    emojis = {
        "name": "👤", "first_name": "👤", "last_name": "👤",
        "phone": "📞", "number": "📞", "mobile": "📞",
        "email": "📧", "mail": "📧",
        "address": "📍", "city": "🏙️", "state": "🗺️",
        "country": "🌍", "zip": "📮", "pincode": "📮",
        "operator": "📡", "carrier": "📡",
        "upi": "💳", "bank": "🏦",
        "dob": "🎂", "age": "🎂",
        "gender": "🚻",
    }
    for keyword, emoji in emojis.items():
        if keyword in key:
            return emoji
    return "📌"


# ================== KEYBOARDS ==================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 Single Search", callback_data="single"),
            InlineKeyboardButton("📦 Batch Search",  callback_data="batch"),
        ],
        [
            InlineKeyboardButton("👤 My Profile", callback_data="profile"),
            InlineKeyboardButton("📊 Status",     callback_data="status"),
        ],
        [
            InlineKeyboardButton("💰 Buy Access", callback_data="buy"),
            InlineKeyboardButton("❓ Help",        callback_data="help"),
        ],
    ])


def admin_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add User",    callback_data="admin_add"),
            InlineKeyboardButton("❌ Remove User", callback_data="admin_remove"),
        ],
        [
            InlineKeyboardButton("📅 Set Expiry", callback_data="admin_expiry"),
            InlineKeyboardButton("📋 All Users",  callback_data="admin_list"),
        ],
        [
            InlineKeyboardButton("📊 Stats",      callback_data="admin_stats"),
            InlineKeyboardButton("🔙 Main Menu",  callback_data="main_menu"),
        ],
    ])


def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ])


def buy_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💬 Contact Admin",
                url=f"https://t.me/{OWNER_CONTACT.replace('@', '')}"
            )
        ]
    ])


def duration_keyboard(prefix: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("7 Days",   callback_data=f"{prefix}_7"),
            InlineKeyboardButton("30 Days",  callback_data=f"{prefix}_30"),
        ],
        [
            InlineKeyboardButton("90 Days",  callback_data=f"{prefix}_90"),
            InlineKeyboardButton("365 Days", callback_data=f"{prefix}_365"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel")],
    ])


# ================== HELPERS ==================
async def safe_edit(query, text, reply_markup=None, parse_mode="Markdown"):
    try:
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except Exception:
        pass


# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user          = update.effective_user
    ok, status, _ = check_access(user.id)

    text = (
        f"{'━' * 30}\n"
        f"   🔍 *Phone Lookup Bot*\n"
        f"{'━' * 30}\n\n"
        f"👋 Welcome *{user.first_name}*!\n\n"
        f"{'🟢' if ok else '🔴'} Status: *{'Active' if ok else 'Inactive'}*\n"
        f"📅 {status}\n\n"
        f"Choose an option below 👇"
    )

    if update.callback_query:
        await safe_edit(
            update.callback_query,
            text,
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
    return ConversationHandler.END


# ================== PROFILE ==================
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user             = query.from_user
    ok, status, days = check_access(user.id)

    bar_length = 20
    filled     = min(int((days / 365) * bar_length), bar_length) if ok and days > 0 else 0
    bar        = "█" * filled + "░" * (bar_length - filled)

    text = (
        f"{'━' * 30}\n"
        f"       👤 *Your Profile*\n"
        f"{'━' * 30}\n\n"
        f"🆔 *ID:* `{user.id}`\n"
        f"👤 *Name:* {user.first_name} {user.last_name or ''}\n"
        f"📛 *Username:* @{user.username or 'N/A'}\n\n"
        f"{'━' * 30}\n"
        f"       🔐 *License Info*\n"
        f"{'━' * 30}\n\n"
        f"📊 *Status:* {status}\n"
        f"⏳ *Days Left:* {days if ok else 0}\n"
        f"📈 `[{bar}]`\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== STATUS ==================
async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ok, status, days = check_access(query.from_user.id)

    if ok:
        text = (
            f"🟢 *Access: ACTIVE*\n\n"
            f"⏳ {days} days remaining\n"
            f"📅 {status}\n\n"
            f"✅ You can use all features!"
        )
    else:
        text = (
            f"🔴 *Access: INACTIVE*\n\n"
            f"📅 {status}\n\n"
            f"💰 Contact admin to buy access\n"
            f"📱 Admin: {OWNER_CONTACT}"
        )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== HELP ==================
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        f"{'━' * 30}\n"
        f"       ❓ *Help Guide*\n"
        f"{'━' * 30}\n\n"
        f"🔍 *Single Search*\n"
        f"   One number at a time\n"
        f"   Example: `919876543210`\n\n"
        f"📦 *Batch Search*\n"
        f"   Comma separated numbers\n"
        f"   Example: `9198...,9197...`\n\n"
        f"👤 *Profile* — Account info\n"
        f"📊 *Status* — Subscription check\n\n"
        f"{'━' * 30}\n"
        f"💡 *Tips:*\n"
        f"   • Use country code (91 for India)\n"
        f"   • No spaces or dashes\n"
        f"   • Max 15 numbers in batch\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== BUY ==================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        f"{'━' * 30}\n"
        f"       💰 *Buy Access*\n"
        f"{'━' * 30}\n\n"
        f"📋 *Plans:*\n\n"
        f"🥉 *7 Days*   → ₹99\n"
        f"🥈 *30 Days*  → ₹299\n"
        f"🥇 *90 Days*  → ₹699\n"
        f"💎 *365 Days* → ₹1999\n\n"
        f"{'━' * 30}\n\n"
        f"📱 Contact admin:\n"
        f"👉 {OWNER_CONTACT}\n\n"
        f"Your ID: `{query.from_user.id}`\n"
        f"_Share this ID with admin_"
    )
    await safe_edit(query, text, reply_markup=buy_keyboard())


# ================== SINGLE SEARCH ==================
async def single_search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ok, status, _ = check_access(query.from_user.id)
    if not ok:
        await safe_edit(
            query,
            f"❌ *Access Denied*\n{status}\n\nBuy access first!",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    await safe_edit(
        query,
        "🔍 *Single Search Mode*\n\n"
        "📱 Enter the phone number:\n"
        "_Example: 919876543210_\n\n"
        "Type /cancel to go back",
    )
    return WAITING_SINGLE


async def single_search_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()

    if not number.isdigit():
        await update.message.reply_text(
            "❌ Invalid! Only digits allowed.\nTry again or /cancel"
        )
        return WAITING_SINGLE

    msg    = await update.message.reply_text("🔍 Searching...")
    result = search_api(number)

    if result["ok"]:
        text = format_result(number, result["data"])
        await msg.edit_text(
            text,
            reply_markup=back_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await msg.edit_text(
            f"❌ *Search Failed*\n\nError: `{result['error']}`",
            reply_markup=back_keyboard(),
            parse_mode="Markdown",
        )
    return ConversationHandler.END


# ================== BATCH SEARCH ==================
async def batch_search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ok, status, _ = check_access(query.from_user.id)
    if not ok:
        await safe_edit(
            query,
            f"❌ *Access Denied*\n{status}",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    await safe_edit(
        query,
        "📦 *Batch Search Mode*\n\n"
        "📱 Enter numbers (comma separated):\n"
        "_Example: 9198...,9197...,9196..._\n"
        "_Max 15 numbers at once_\n\n"
        "Type /cancel to go back",
    )
    return WAITING_BATCH


async def batch_search_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw     = update.message.text.strip()
    numbers = [n.strip() for n in raw.replace(",", " ").split() if n.strip()]

    if not numbers:
        await update.message.reply_text(
            "❌ No numbers found! Try again or /cancel"
        )
        return WAITING_BATCH

    numbers = numbers[:15]
    total   = len(numbers)
    msg     = await update.message.reply_text(
        f"🚀 Processing {total} numbers...\n[{'░' * total}]"
    )

    for i, num in enumerate(numbers, 1):
        result   = search_api(num)
        progress = "█" * i + "░" * (total - i)

        if result["ok"]:
            text = format_result(num, result["data"])
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text(
                f"❌ *{num}*\n`{result['error']}`",
                parse_mode="Markdown"
            )

        try:
            await msg.edit_text(
                f"🚀 Processing... ({i}/{total})\n[{progress}]"
            )
        except:
            pass

    await msg.edit_text(
        f"✅ *Batch Complete!*\n📊 Processed: {total} numbers",
        reply_markup=back_keyboard(),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


# ================== CANCEL ==================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Cancelled.",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


# ================== ADMIN PANEL ==================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        if update.message:
            await update.message.reply_text("❌ Admin only!")
        return ConversationHandler.END

    text = (
        f"{'━' * 30}\n"
        f"       🛠️ *Admin Panel*\n"
        f"{'━' * 30}\n\n"
        f"Choose an action:"
    )

    if update.callback_query:
        await safe_edit(
            update.callback_query,
            text,
            reply_markup=admin_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=admin_menu_keyboard(),
            parse_mode="Markdown"
        )
    return ConversationHandler.END


# ── Add User ──
async def admin_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Admin only!")
        return ConversationHandler.END

    await query.answer()
    await safe_edit(
        query,
        "➕ *Add New User*\n\n"
        "Enter Telegram User ID:\n\n"
        "/cancel to go back",
    )
    return ADMIN_ADD_ID


async def admin_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    if not uid.isdigit():
        await update.message.reply_text(
            "❌ Invalid ID! Numbers only.\n/cancel to stop"
        )
        return ADMIN_ADD_ID

    context.user_data["new_uid"] = uid
    await update.message.reply_text(
        f"✅ User ID: `{uid}`\n\nSelect duration:",
        reply_markup=duration_keyboard("exp"),
        parse_mode="Markdown",
    )
    return ADMIN_ADD_EXP


async def admin_add_expiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "admin_cancel":
        await admin_panel(update, context)
        return ConversationHandler.END

    days_map = {"exp_7": 7, "exp_30": 30, "exp_90": 90, "exp_365": 365}
    days     = days_map.get(query.data, 30)
    expiry   = (date.today() + timedelta(days=days)).isoformat()
    uid      = context.user_data.get("new_uid")

    users      = load_users()
    users[uid] = {
        "expiry": expiry,
        "added": date.today().isoformat()
    }
    save_users(users)

    await safe_edit(
        query,
        f"✅ *User Added!*\n\n"
        f"🆔 ID: `{uid}`\n"
        f"📅 Expiry: `{expiry}`\n"
        f"⏳ Duration: {days} days",
        reply_markup=admin_menu_keyboard(),
    )
    return ConversationHandler.END


# ── Remove User ──
async def admin_remove_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return ConversationHandler.END

    await query.answer()
    await safe_edit(
        query,
        "❌ *Remove User*\n\n"
        "Enter Telegram User ID:\n\n"
        "/cancel to go back",
    )
    return ADMIN_REM_ID


async def admin_remove_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.message.text.strip()
    users = load_users()

    if uid in users:
        del users[uid]
        save_users(users)
        await update.message.reply_text(
            f"✅ User `{uid}` removed!",
            reply_markup=admin_menu_keyboard(),
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            f"❌ User `{uid}` not found!",
            reply_markup=admin_menu_keyboard(),
            parse_mode="Markdown",
        )
    return ConversationHandler.END


# ── Set Expiry ──
async def admin_expiry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return ConversationHandler.END

    await query.answer()
    await safe_edit(
        query,
        "📅 *Set Expiry*\n\n"
        "Enter User ID:\n\n"
        "/cancel to go back",
    )
    return ADMIN_EXP_ID


async def admin_expiry_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    context.user_data["exp_uid"] = uid
    await update.message.reply_text(
        f"User: `{uid}`\nSelect new duration:",
        reply_markup=duration_keyboard("setexp"),
        parse_mode="Markdown",
    )
    return ADMIN_EXP_DATE


async def admin_expiry_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "admin_cancel":
        await admin_panel(update, context)
        return ConversationHandler.END

    days_map = {
        "setexp_7": 7, "setexp_30": 30,
        "setexp_90": 90, "setexp_365": 365
    }
    days   = days_map.get(query.data, 30)
    expiry = (date.today() + timedelta(days=days)).isoformat()
    uid    = context.user_data.get("exp_uid")
    users  = load_users()

    if uid in users:
        users[uid]["expiry"] = expiry
        save_users(users)
        await safe_edit(
            query,
            f"✅ *Expiry Updated!*\n\n"
            f"🆔 User: `{uid}`\n"
            f"📅 New Expiry: `{expiry}`\n"
            f"⏳ Duration: {days} days",
            reply_markup=admin_menu_keyboard(),
        )
    else:
        await safe_edit(
            query,
            f"❌ User `{uid}` not found!\nAdd them first.",
            reply_markup=admin_menu_keyboard(),
        )
    return ConversationHandler.END


# ── List Users ──
async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return

    await query.answer()
    users = load_users()

    if not users:
        await safe_edit(
            query,
            "📋 *No users yet!*",
            reply_markup=admin_menu_keyboard()
        )
        return

    text = (
        f"{'━' * 30}\n"
        f"📋 *All Users ({len(users)})*\n"
        f"{'━' * 30}\n\n"
    )

    for uid, info in users.items():
        exp = info.get("expiry", "N/A")
        try:
            exp_date = date.fromisoformat(exp)
            if date.today() > exp_date:
                s = "🔴 Expired"
            else:
                d = (exp_date - date.today()).days
                s = f"🟢 {d}d left"
        except:
            s = "⚪ Unknown"
        text += f"🆔 `{uid}`\n   📅 {exp} | {s}\n\n"

    await safe_edit(
        query,
        text[:4000],
        reply_markup=admin_menu_keyboard()
    )


# ── Stats ──
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return

    await query.answer()
    users   = load_users()
    total   = len(users)
    active  = 0
    expired = 0

    for info in users.values():
        try:
            exp = date.fromisoformat(info.get("expiry", "2000-01-01"))
            if date.today() <= exp:
                active += 1
            else:
                expired += 1
        except:
            expired += 1

    text = (
        f"{'━' * 30}\n"
        f"       📊 *Bot Statistics*\n"
        f"{'━' * 30}\n\n"
        f"👥 Total Users : *{total}*\n"
        f"🟢 Active      : *{active}*\n"
        f"🔴 Expired     : *{expired}*\n"
        f"📅 Date        : {date.today()}\n"
    )
    await safe_edit(query, text, reply_markup=admin_menu_keyboard())


# ── Main Menu Callback ──
async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END


# ================== MAIN ==================
def main():
    # ✅ Fixed timeout - two separate request instances
    request = HTTPXRequest(
        connect_timeout=60.0,
        read_timeout=60.0,
        write_timeout=60.0,
        pool_timeout=60.0,
    )

    get_updates_request = HTTPXRequest(
        connect_timeout=60.0,
        read_timeout=60.0,
        write_timeout=60.0,
        pool_timeout=60.0,
    )

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .get_updates_request(get_updates_request)
        .build()
    )

    # ── Conversations ──
    search_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(single_search_start, pattern="^single$")
        ],
        states={
            WAITING_SINGLE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    single_search_process
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
        allow_reentry=True,
    )

    batch_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(batch_search_start, pattern="^batch$")
        ],
        states={
            WAITING_BATCH: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    batch_search_process
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
        allow_reentry=True,
    )

    admin_add_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_add_start, pattern="^admin_add$")
        ],
        states={
            ADMIN_ADD_ID: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    admin_add_id
                )
            ],
            ADMIN_ADD_EXP: [
                CallbackQueryHandler(
                    admin_add_expiry,
                    pattern="^exp_|^admin_cancel$"
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
        allow_reentry=True,
    )

    admin_remove_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_remove_start, pattern="^admin_remove$")
        ],
        states={
            ADMIN_REM_ID: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    admin_remove_process
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
        allow_reentry=True,
    )

    admin_expiry_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_expiry_start, pattern="^admin_expiry$")
        ],
        states={
            ADMIN_EXP_ID: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    admin_expiry_id
                )
            ],
            ADMIN_EXP_DATE: [
                CallbackQueryHandler(
                    admin_expiry_set,
                    pattern="^setexp_|^admin_cancel$"
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
        allow_reentry=True,
    )

    # ── Register All Handlers ──
    app.add_handler(search_conv)
    app.add_handler(batch_conv)
    app.add_handler(admin_add_conv)
    app.add_handler(admin_remove_conv)
    app.add_handler(admin_expiry_conv)

    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("admin",  admin_panel))

    app.add_handler(CallbackQueryHandler(profile,            pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(status_check,       pattern="^status$"))
    app.add_handler(CallbackQueryHandler(help_menu,          pattern="^help$"))
    app.add_handler(CallbackQueryHandler(buy,                pattern="^buy$"))
    app.add_handler(CallbackQueryHandler(admin_list,         pattern="^admin_list$"))
    app.add_handler(CallbackQueryHandler(admin_stats,        pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))

    print("🤖 Bot is running...")
    print(f"👤 Admin ID  : {ADMIN_ID}")
    print(f"🔗 Bot Link  : https://t.me/Legit_numinfo_bot")
    print("⏹  Press Ctrl+C to stop\n")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()

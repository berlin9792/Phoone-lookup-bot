#!/usr/bin/env python3
"""
🔍 Phone Number Intelligence Bot - 1 Free Search
"""

import json
import requests
from datetime import date, timedelta
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)
from telegram.request import HTTPXRequest

# ================== CONFIG ==================
BOT_TOKEN     = "8642873626:AAHkybZD5LBO7331YisbProHnp1P8e6nhQQ"
ADMIN_ID      = 5057489358
DEFAULT_PIN   = "912036"
API_URL       = "https://lk-api-pinsstm.ramaxinfo.workers.dev/"
DATA_FILE     = Path("users.json")
OWNER_CONTACT = "@theplayerror"
FREE_SEARCHES = 1

WAITING_SINGLE = 1
WAITING_BATCH  = 2
ADMIN_ADD_ID   = 3
ADMIN_ADD_EXP  = 4
ADMIN_REM_ID   = 5
ADMIN_EXP_ID   = 6
ADMIN_EXP_DATE = 7


def load_users():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except:
            return {}
    return {}

def save_users(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))

def get_or_create_user(user_id: int):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "expiry": "", "added": date.today().isoformat(),
            "is_premium": False, "free_used": 0, "total_searches": 0
        }
        save_users(users)
    return users[uid]

def get_free_remaining(user_id: int) -> int:
    user_data = get_or_create_user(user_id)
    used = user_data.get("free_used", 0)
    return max(0, FREE_SEARCHES - used)

def use_one_search(user_id: int):
    users = load_users()
    uid = str(user_id)
    user_data = users.get(uid, {})
    user_data["free_used"] = user_data.get("free_used", 0) + 1
    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    users[uid] = user_data
    save_users(users)

def use_premium_search(user_id: int):
    users = load_users()
    uid = str(user_id)
    user_data = users.get(uid, {})
    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    users[uid] = user_data
    save_users(users)

def check_access(user_id: int):
    get_or_create_user(user_id)
    users = load_users()
    uid = str(user_id)
    user_data = users[uid]
    is_premium = user_data.get("is_premium", False)
    expiry_str = user_data.get("expiry", "")

    if is_premium and expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                free_left = get_free_remaining(user_id)
                if free_left > 0:
                    return True, f"⚠️ Premium expired | 🆓 {free_left} left", 0, False
                return False, "❌ Premium expired & no free search left", 0, False
            days = (expiry - date.today()).days
            return True, f"✅ Premium ({days} days left)", days, True
        except:
            pass

    free_left = get_free_remaining(user_id)
    if free_left > 0:
        return True, f"🆓 Free ({free_left}/{FREE_SEARCHES} left)", 0, False
    return False, "❌ Free search used! Buy subscription.", 0, False

def upgrade_to_paid(user_id: int, days: int):
    users = load_users()
    uid = str(user_id)
    user_data = get_or_create_user(user_id)
    expiry = (date.today() + timedelta(days=days)).isoformat()
    user_data["expiry"] = expiry
    user_data["is_premium"] = True
    users[uid] = user_data
    save_users(users)
    # ================== SKIP KEYS ==================
SKIP_KEYS = {
    "timestamp", "response_time", "response_time_ms",
    "developer", "owner", "credit", "credits",
    "powered_by", "source", "api", "version",
    "status", "message", "code", "time",
    "created_at", "updated_at", "server",
    "watermark", "signature", "by", "made_by",
    "contact", "channel", "group", "join",
    "advertisement", "ads", "promo", "query",
}

SKIP_FIELDS_EXACT = {
    "EncryptedPassword", "encrypted_password",
    "Salt", "salt", "PinCode", "pin_code",
    "CreditsInappPoints", "IP", "ip",
    "TheDateOfTheEntrance",
}

def should_skip(key: str) -> bool:
    if key in SKIP_FIELDS_EXACT:
        return True
    key_lower = key.lower().strip()
    if key_lower in SKIP_KEYS:
        return True
    skip_words = [
        "timestamp", "response", "developer",
        "owner", "credit", "powered", "source",
        "version", "watermark", "pheevar",
        "advertisement", "promo", "channel",
        "server", "api_", "made_by",
        "encrypted", "password", "salt",
    ]
    for word in skip_words:
        if word in key_lower:
            return True
    return False

def should_skip_value(value) -> bool:
    if value is None or value == "":
        return True
    val_str = str(value).lower().strip()
    if val_str in ("", "none", "null", "n/a", "na", "-", "0", "0.00", "0000-00-00"):
        return True
    skip_values = ["@pheevar", "pheevar", "@lk_", "t.me/", "telegram.me/"]
    for sv in skip_values:
        if sv.lower() in val_str:
            return True
    return False

def get_emoji(key):
    key = key.lower()
    emojis = {
        "name": "👤", "fullname": "👤", "full_name": "👤",
        "first_name": "👤", "last_name": "👤", "surname": "👤",
        "phone": "📞", "phone2": "📞", "number": "📞", "mobile": "📞",
        "email": "📧", "mail": "📧",
        "adres": "📍", "address": "📍", "adres2": "📍",
        "city": "🏙️", "state": "🗺️", "region": "🗺️",
        "country": "🌍", "zip": "📮", "pincode": "📮",
        "postalcode": "📮", "postal_code": "📮",
        "operator": "📡", "carrier": "📡", "circle": "📡",
        "upi": "💳", "bank": "🏦", "ifsc": "🏦",
        "account": "🏦", "documentnumber": "🪪",
        "document_number": "🪪", "dob": "🎂",
        "dateofbirth": "🎂", "date_of_birth": "🎂",
        "birth": "🎂", "age": "🎂", "gender": "🚻",
        "sim": "📱", "imei": "📱", "device": "📱",
        "network": "📶", "type": "🔖", "id": "🆔",
        "pan": "🪪", "aadhar": "🪪", "voter": "🪪",
        "aadhaar": "🪪", "father": "👨", "fathername": "👨",
        "father_name": "👨", "mother": "👩",
        "husband": "👨", "wife": "👩",
        "district": "🗺️", "taluka": "🗺️",
        "post": "📮", "village": "🏘️",
        "income": "💰", "salary": "💰",
        "job": "💼", "company": "🏢", "work": "💼",
        "date": "📅", "registrationdate": "📅",
        "registration_date": "📅",
    }
    for keyword, emoji in emojis.items():
        if keyword in key:
            return emoji
    return "📌"

def format_record(record: dict) -> list:
    lines = []
    for k, v in record.items():
        if should_skip(k):
            continue
        if should_skip_value(v):
            continue
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if should_skip(sub_k) or should_skip_value(sub_v):
                    continue
                emoji = get_emoji(sub_k.lower())
                label = sub_k.replace("_", " ").replace("-", " ").title()
                lines.append(f"{emoji} *{label}*: `{sub_v}`")
            continue
        if isinstance(v, list):
            clean = [str(i) for i in v if not should_skip_value(i)]
            if clean:
                emoji = get_emoji(k.lower())
                label = k.replace("_", " ").replace("-", " ").title()
                lines.append(f"{emoji} *{label}*: `{', '.join(clean)}`")
            continue
        emoji = get_emoji(k.lower())
        label = k.replace("_", " ").replace("-", " ").title()
        lines.append(f"{emoji} *{label}*: `{v}`")
    return lines

def format_result(number, data):
    if not data:
        return f"📱 *{number}*\n_No data found_"
    if isinstance(data, list):
        if not data:
            return f"📱 *{number}*\n_No data found_"
        if isinstance(data[0], dict):
            data = {"data": {"source": {"records": data}}}
        else:
            return f"📱 *{number}*\n`{str(data[0])}`"
    if not isinstance(data, dict):
        return f"📱 *{number}*\n`{str(data)}`"

    main_data = data.get("data", data)
    all_records = []

    if isinstance(main_data, dict):
        has_sources = False
        for key, value in main_data.items():
            if isinstance(value, dict) and "records" in value:
                has_sources = True
                records = value["records"]
                if isinstance(records, list):
                    for rec in records:
                        if isinstance(rec, dict):
                            all_records.append(rec)
        if not has_sources and "records" in main_data:
            records = main_data["records"]
            if isinstance(records, list):
                for rec in records:
                    if isinstance(rec, dict):
                        all_records.append(rec)
        if not all_records and not has_sources:
            all_records.append(main_data)
    elif isinstance(main_data, list):
        for rec in main_data:
            if isinstance(rec, dict):
                all_records.append(rec)

    if not all_records:
        return f"📱 *{number}*\n_No data found_"

    seen = set()
    unique_records = []
    for rec in all_records:
        identifier = (
            str(rec.get("FullName", rec.get("Name", ""))).lower() +
            str(rec.get("Phone", rec.get("Phone2", "")))
        )
        if identifier not in seen:
            seen.add(identifier)
            unique_records.append(rec)

    output = [
        f"📱 *Result for* `{number}`",
        f"📊 *{len(unique_records)} record(s) found*",
        f"{'━' * 28}",
    ]
    for idx, record in enumerate(unique_records, 1):
        if len(unique_records) > 1:
            output.append(f"\n*━━ Record #{idx} ━━*")
        lines = format_record(record)
        if lines:
            output.extend(lines)
        else:
            output.append("_No relevant data_")
    return "\n".join(output)

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
        # ================== KEYBOARDS ==================
def main_menu_keyboard(user_id: int):
    ok, _, _, is_premium = check_access(user_id)
    free_left = get_free_remaining(user_id)

    if is_premium:
        search_label = "🔍 Single Search"
        batch_label  = "📦 Batch Search"
    elif free_left > 0:
        search_label = f"🔍 Search ({free_left} free)"
        batch_label  = f"📦 Batch ({free_left} free)"
    else:
        search_label = "🔍 Search (🔒)"
        batch_label  = "📦 Batch (🔒)"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(search_label, callback_data="single"),
            InlineKeyboardButton(batch_label,  callback_data="batch"),
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

def back_keyboard(user_id: int = None):
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
        ],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
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
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )
    except Exception:
        pass

# ================== START & MENUS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id)
    ok, status, days, is_premium = check_access(user.id)
    free_left = get_free_remaining(user.id)

    if is_premium:
        status_emoji, status_color = "💎", "Premium"
    elif ok:
        status_emoji, status_color = "🆓", "Free"
    else:
        status_emoji, status_color = "🔴", "Locked"

    used = FREE_SEARCHES - free_left
    bar  = "🟢" * free_left + "🔴" * used

    text = (
        f"{'━' * 30}\n"
        f"   🔍 *Phone Lookup Bot*\n"
        f"{'━' * 30}\n\n"
        f"👋 Welcome *{user.first_name}*!\n\n"
        f"{status_emoji} Account: *{status_color}*\n"
        f"📅 {status}\n\n"
    )

    if not is_premium:
        text += (
            f"{'━' * 25}\n"
            f"🆓 Free Search: {bar}\n"
            f"   {free_left}/{FREE_SEARCHES} remaining\n"
            f"{'━' * 25}\n\n"
        )

    text += "Choose an option below 👇"

    if update.callback_query:
        await safe_edit(update.callback_query, text, reply_markup=main_menu_keyboard(user.id))
    else:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    return ConversationHandler.END

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ok, status, days, is_premium = check_access(user.id)
    free_left = get_free_remaining(user.id)
    user_data = get_or_create_user(user.id)
    total_s = user_data.get("total_searches", 0)

    if is_premium:
        acc_type = "💎 Premium"
        bar_length = 20
        filled = min(int((days / 365) * bar_length), bar_length) if days > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        expiry_info = f"📅 *Expires:* {user_data.get('expiry', 'N/A')}\n⏳ *Days Left:* {days}\n📈 `[{bar}]`\n"
    else:
        acc_type = f"🆓 Free ({free_left} left)"
        used = FREE_SEARCHES - free_left
        bar = "🟢" * free_left + "🔴" * used
        expiry_info = f"🆓 *Free Search:* {free_left}/{FREE_SEARCHES}\n📊 {bar}\n"

    text = (
        f"{'━' * 30}\n       👤 *Your Profile*\n{'━' * 30}\n\n"
        f"🆔 *ID:* `{user.id}`\n👤 *Name:* {user.first_name} {user.last_name or ''}\n"
        f"📛 *Username:* @{user.username or 'N/A'}\n\n"
        f"{'━' * 30}\n       🔐 *Account Info*\n{'━' * 30}\n\n"
        f"📦 *Type:* {acc_type}\n{expiry_info}\n🔍 *Total Searches:* {total_s}\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard(user.id))

async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ok, status, days, is_premium = check_access(user.id)
    free_left = get_free_remaining(user.id)

    if is_premium:
        text = f"💎 *Account: PREMIUM*\n\n⏳ {days} days remaining\n📅 {status}\n\n✅ Unlimited searches!"
    elif ok:
        text = f"🆓 *Account: FREE*\n\n🔍 {free_left} search remaining\n📅 {status}\n\n💡 Buy Premium for unlimited:\n👉 {OWNER_CONTACT}"
    else:
        text = f"🔴 *Account: LOCKED*\n\n📅 {status}\n\n❌ Your {FREE_SEARCHES} free search is used!\n\n💰 Buy subscription:\n👉 {OWNER_CONTACT}\n\nYour ID: `{user.id}`"
    await safe_edit(query, text, reply_markup=back_keyboard(user.id))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        f"{'━' * 30}\n       ❓ *Help Guide*\n{'━' * 30}\n\n"
        f"🆓 *Free Users*\n   {FREE_SEARCHES} free search only\n   After that, buy subscription.\n\n"
        f"💎 *Premium Users*\n   Unlimited searches!\n\n"
        f"🔍 *Single Search*\n   One number at a time\n   Example: `919876543210`\n\n"
        f"📦 *Batch Search*\n   Comma separated numbers\n   Example: `9198...,9197...`\n   ⚠️ Each number = 1 search\n\n"
        f"{'━' * 30}\n💡 *Tips:*\n   • Use country code (91 for India)\n   • No spaces or dashes\n   • Max 15 numbers in batch\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    free_left = get_free_remaining(user.id)
    text = (
        f"{'━' * 30}\n       💰 *Buy Access*\n{'━' * 30}\n\n"
        f"🆓 Free used: {FREE_SEARCHES - free_left}/{FREE_SEARCHES}\n\n"
        f"📋 *Premium Plans:*\n\n🥉 *7 Days*   → ₹50\n🥈 *30 Days*  → ₹150\n🥇 *90 Days*  → ₹300\n💎 *365 Days* → ₹999\n\n"
        f"{'━' * 30}\n\n📱 Contact admin:\n👉 {OWNER_CONTACT}\n\nYour ID: `{user.id}`\n_Share this ID with admin_"
    )
    await safe_edit(query, text, reply_markup=buy_keyboard())
    # ================== SINGLE SEARCH ==================
async def single_search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ok, status, _, is_premium = check_access(user.id)
    free_left = get_free_remaining(user.id)

    if not ok:
        await safe_edit(
            query,
            f"🔒 *Search Locked!*\n\n{status}\n\n💰 Buy subscription:\n👉 {OWNER_CONTACT}\n\nYour ID: `{user.id}`",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    info = "💎 Premium — Unlimited" if is_premium else f"🆓 {free_left} search remaining"
    await safe_edit(
        query,
        f"🔍 *Single Search Mode*\n\n📊 {info}\n\n📱 Enter phone number:\n_Example: 919876543210_\n\nType /cancel to go back",
    )
    return WAITING_SINGLE

async def single_search_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    user = update.effective_user

    if not number.isdigit():
        await update.message.reply_text("❌ Invalid! Only digits.\nTry again or /cancel")
        return WAITING_SINGLE

    ok, status, _, is_premium = check_access(user.id)
    if not ok:
        await update.message.reply_text(
            f"🔒 *Locked!*\n{status}\n💰 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END

    msg = await update.message.reply_text("🔍 Searching...")
    result = search_api(number)

    if result["ok"]:
        if is_premium:
            use_premium_search(user.id)
        else:
            use_one_search(user.id)
        free_left = get_free_remaining(user.id)
        text = format_result(number, result["data"])
        if not is_premium:
            text += f"\n\n{'━' * 25}\n🆓 Remaining: *{free_left}/{FREE_SEARCHES}*"
        await msg.edit_text(text, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    else:
        await msg.edit_text(
            f"❌ *Search Failed*\n\nError: `{result['error']}`",
            reply_markup=back_keyboard(user.id), parse_mode="Markdown",
        )
    return ConversationHandler.END

# ================== BATCH SEARCH ==================
async def batch_search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ok, status, _, is_premium = check_access(user.id)
    free_left = get_free_remaining(user.id)

    if not ok:
        await safe_edit(
            query,
            f"🔒 *Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    info = "💎 Unlimited" if is_premium else f"🆓 {free_left} search left"
    await safe_edit(
        query,
        f"📦 *Batch Search Mode*\n\n📊 {info}\n\n📱 Enter numbers (comma separated):\n_Example: 9198...,9197...,9196..._\n_Max 15 numbers at once_\n\nType /cancel to go back",
    )
    return WAITING_BATCH

async def batch_search_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = update.message.text.strip()
    user = update.effective_user
    numbers = [n.strip() for n in raw.replace(",", " ").split() if n.strip()]

    if not numbers:
        await update.message.reply_text("❌ No numbers! Try again or /cancel")
        return WAITING_BATCH

    numbers = numbers[:15]
    total = len(numbers)
    ok, status, _, is_premium = check_access(user.id)
    free_left = get_free_remaining(user.id)

    if not is_premium and total > free_left:
        await update.message.reply_text(
            f"❌ *Not enough searches!*\n\nYou entered: *{total}* numbers\nAvailable: *{free_left}* search\n\n💡 You can only search *{free_left}* number\nOr buy premium for unlimited.\n👉 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END

    msg = await update.message.reply_text(f"🚀 Processing {total} numbers...\n[{'░' * total}]")

    for i, num in enumerate(numbers, 1):
        result = search_api(num)
        progress = "█" * i + "░" * (total - i)
        if result["ok"]:
            if is_premium:
                use_premium_search(user.id)
            else:
                use_one_search(user.id)
            text = format_result(num, result["data"])
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ *{num}*\n`{result['error']}`", parse_mode="Markdown")
        try:
            await msg.edit_text(f"🚀 Processing... ({i}/{total})\n[{progress}]")
        except:
            pass

    free_left = get_free_remaining(user.id)
    summary = f"✅ *Batch Complete!*\n📊 Processed: {total} numbers"
    if not is_premium:
        summary += f"\n🆓 Remaining: *{free_left}/{FREE_SEARCHES}*"
    await msg.edit_text(summary, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    return ConversationHandler.END

# ================== CANCEL ==================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text("❌ Cancelled.", reply_markup=main_menu_keyboard(user.id))
    return ConversationHandler.END

# ================== ADMIN ==================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        if update.message:
            await update.message.reply_text("❌ Admin only!")
        return ConversationHandler.END

    users = load_users()
    total = len(users)
    premium = sum(1 for u in users.values() if u.get("is_premium", False))
    free_u = total - premium
    text = (
        f"{'━' * 30}\n       🛠️ *Admin Panel*\n{'━' * 30}\n\n"
        f"👥 Total: {total} | 💎 Premium: {premium} | 🆓 Free: {free_u}\n\nChoose an action:"
    )
    if update.callback_query:
        await safe_edit(update.callback_query, text, reply_markup=admin_menu_keyboard())
    else:
        await update.message.reply_text(text, reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def admin_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "➕ *Add Premium User*\n\nEnter Telegram User ID:\n\n/cancel to go back")
    return ADMIN_ADD_ID

async def admin_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ Invalid ID!\n/cancel to stop")
        return ADMIN_ADD_ID
    context.user_data["new_uid"] = uid
    await update.message.reply_text(
        f"✅ User ID: `{uid}`\n\nSelect duration:",
        reply_markup=duration_keyboard("exp"), parse_mode="Markdown",
    )
    return ADMIN_ADD_EXP

async def admin_add_expiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_cancel":
        await admin_panel(update, context)
        return ConversationHandler.END
    days_map = {"exp_7": 7, "exp_30": 30, "exp_90": 90, "exp_365": 365}
    days = days_map.get(query.data, 30)
    uid = context.user_data.get("new_uid")
    upgrade_to_paid(int(uid), days)
    expiry = (date.today() + timedelta(days=days)).isoformat()
    await safe_edit(
        query,
        f"✅ *Premium Added!*\n\n🆔 ID: `{uid}`\n📅 Expiry: `{expiry}`\n⏳ {days} days",
        reply_markup=admin_menu_keyboard(),
    )
    return ConversationHandler.END

async def admin_remove_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "❌ *Remove User*\n\nEnter Telegram User ID:\n\n/cancel to go back")
    return ADMIN_REM_ID

async def admin_remove_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    users = load_users()
    if uid in users:
        del users[uid]
        save_users(users)
        await update.message.reply_text(f"✅ User `{uid}` removed!", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ User `{uid}` not found!", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def admin_expiry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "📅 *Set Expiry*\n\nEnter User ID:\n\n/cancel to go back")
    return ADMIN_EXP_ID

async def admin_expiry_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    context.user_data["exp_uid"] = uid
    await update.message.reply_text(
        f"User: `{uid}`\nSelect duration:",
        reply_markup=duration_keyboard("setexp"), parse_mode="Markdown",
    )
    return ADMIN_EXP_DATE

async def admin_expiry_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_cancel":
        await admin_panel(update, context)
        return ConversationHandler.END
    days_map = {"setexp_7": 7, "setexp_30": 30, "setexp_90": 90, "setexp_365": 365}
    days = days_map.get(query.data, 30)
    uid = context.user_data.get("exp_uid")
    upgrade_to_paid(int(uid), days)
    expiry = (date.today() + timedelta(days=days)).isoformat()
    await safe_edit(
        query,
        f"✅ *Upgraded to Premium!*\n\n🆔 User: `{uid}`\n📅 Expiry: `{expiry}`\n⏳ {days} days",
        reply_markup=admin_menu_keyboard(),
    )
    return ConversationHandler.END

async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    users = load_users()
    if not users:
        await safe_edit(query, "📋 *No users yet!*", reply_markup=admin_menu_keyboard())
        return
    text = f"{'━' * 30}\n📋 *All Users ({len(users)})*\n{'━' * 30}\n\n"
    for uid, info in users.items():
        is_prem = info.get("is_premium", False)
        acc_type = "💎" if is_prem else "🆓"
        free_u = info.get("free_used", 0)
        total_s = info.get("total_searches", 0)
        exp = info.get("expiry", "")
        if is_prem and exp:
            try:
                exp_date = date.fromisoformat(exp)
                if date.today() > exp_date:
                    s = "🔴 Expired"
                else:
                    d = (exp_date - date.today()).days
                    s = f"🟢 {d}d left"
            except:
                s = "⚪ N/A"
        else:
            left = max(0, FREE_SEARCHES - free_u)
            s = f"🔍 {left}/{FREE_SEARCHES} free"
        text += f"{acc_type} `{uid}` | {s} | 🔍{total_s}\n"
    await safe_edit(query, text[:4000], reply_markup=admin_menu_keyboard())

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    users = load_users()
    total = len(users)
    premium_act = premium_exp = free_active = free_done = total_searches = 0
    for info in users.values():
        is_prem = info.get("is_premium", False)
        total_searches += info.get("total_searches", 0)
        if is_prem:
            try:
                exp = date.fromisoformat(info.get("expiry", "2000-01-01"))
                if date.today() <= exp:
                    premium_act += 1
                else:
                    premium_exp += 1
            except:
                premium_exp += 1
        else:
            if info.get("free_used", 0) < FREE_SEARCHES:
                free_active += 1
            else:
                free_done += 1
    text = (
        f"{'━' * 30}\n       📊 *Bot Statistics*\n{'━' * 30}\n\n"
        f"👥 *Total Users*    : {total}\n🔍 *Total Searches* : {total_searches}\n\n"
        f"{'━' * 25}\n💎 *Premium*\n{'━' * 25}\n"
        f"🟢 Active  : {premium_act}\n🔴 Expired : {premium_exp}\n\n"
        f"{'━' * 25}\n🆓 *Free Users*\n{'━' * 25}\n"
        f"🟢 Has search : {free_active}\n🔴 Used       : {free_done}\n\n"
        f"📅 Date: {date.today()}\n"
    )
    await safe_edit(query, text, reply_markup=admin_menu_keyboard())

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END

# ================== MAIN ==================
def main():
    request = HTTPXRequest(
        connect_timeout=60.0, read_timeout=60.0,
        write_timeout=60.0, pool_timeout=60.0,
    )
    get_updates_request = HTTPXRequest(
        connect_timeout=60.0, read_timeout=60.0,
        write_timeout=60.0, pool_timeout=60.0,
    )
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .get_updates_request(get_updates_request)
        .build()
    )

    search_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(single_search_start, pattern="^single$")],
        states={WAITING_SINGLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, single_search_process)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )
    batch_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(batch_search_start, pattern="^batch$")],
        states={WAITING_BATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, batch_search_process)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )
    admin_add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_start, pattern="^admin_add$")],
        states={
            ADMIN_ADD_ID:  [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_id)],
            ADMIN_ADD_EXP: [CallbackQueryHandler(admin_add_expiry, pattern="^exp_|^admin_cancel$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )
    admin_remove_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_remove_start, pattern="^admin_remove$")],
        states={ADMIN_REM_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_remove_process)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )
    admin_expiry_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_expiry_start, pattern="^admin_expiry$")],
        states={
            ADMIN_EXP_ID:   [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_expiry_id)],
            ADMIN_EXP_DATE: [CallbackQueryHandler(admin_expiry_set, pattern="^setexp_|^admin_cancel$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )

    app.add_handler(search_conv)
    app.add_handler(batch_conv)
    app.add_handler(admin_add_conv)
    app.add_handler(admin_remove_conv)
    app.add_handler(admin_expiry_conv)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(profile,            pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(status_check,       pattern="^status$"))
    app.add_handler(CallbackQueryHandler(help_menu,          pattern="^help$"))
    app.add_handler(CallbackQueryHandler(buy,                pattern="^buy$"))
    app.add_handler(CallbackQueryHandler(admin_list,         pattern="^admin_list$"))
    app.add_handler(CallbackQueryHandler(admin_stats,        pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))

    print("🤖 Bot is running...")
    print(f"👤 Admin ID      : {ADMIN_ID}")
    print(f"🆓 Free Searches : {FREE_SEARCHES}")
    print("⏹  Press Ctrl+C to stop\n")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )

if __name__ == "__main__":
    main()

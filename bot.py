#!/usr/bin/env python3
"""
🔍 Phone Number Intelligence Bot
Trial: 1 search | Plans: 5/10/15/unlimited per day
"""

import json
import requests
from datetime import date, timedelta, datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)
from telegram.request import HTTPXRequest

# ================== CONFIG ==================
BOT_TOKEN     = "8642873626:AAFy5F79opcK_NMJ7NgGItd6sRrfbOc4TJU"
ADMIN_ID      = 5057489358
DEFAULT_PIN   = "912036"
API_URL       = "https://lk-api-pinsstm.ramaxinfo.workers.dev/"
DATA_FILE     = Path("users.json")
OWNER_CONTACT = "@theplayerror"
FREE_SEARCHES = 1

# ================== PLANS ==================
PLANS = {
    "trial": {
        "name"       : "🆓 Trial",
        "days"       : 0,
        "price"      : 0,
        "daily_limit": 0,
        "unlimited"  : False,
        "is_free"    : True,
    },
    "7days": {
        "name"       : "🥉 7 Days",
        "days"       : 7,
        "price"      : 50,
        "daily_limit": 5,
        "unlimited"  : False,
        "is_free"    : False,
    },
    "30days": {
        "name"       : "🥈 30 Days",
        "days"       : 30,
        "price"      : 130,
        "daily_limit": 10,
        "unlimited"  : False,
        "is_free"    : False,
    },
    "6months": {
        "name"       : "🥇 6 Months",
        "days"       : 180,
        "price"      : 300,
        "daily_limit": 15,
        "unlimited"  : False,
        "is_free"    : False,
    },
    "12months": {
        "name"       : "💎 12 Months",
        "days"       : 365,
        "price"      : 799,
        "daily_limit": 999999,
        "unlimited"  : True,
        "is_free"    : False,
    },
}

# Conversation states
WAITING_SINGLE = 1
WAITING_BATCH  = 2
ADMIN_ADD_ID   = 3
ADMIN_ADD_PLAN = 4
ADMIN_REM_ID   = 5
ADMIN_EXP_ID   = 6
ADMIN_EXP_PLAN = 7


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

def get_or_create_user(user_id: int):
    users = load_users()
    uid   = str(user_id)
    if uid not in users:
        users[uid] = {
            "plan"          : "trial",
            "expiry"        : "",
            "added"         : date.today().isoformat(),
            "is_premium"    : False,
            "free_used"     : 0,
            "total_searches": 0,
            "daily_searches": 0,
            "last_search_date": "",
        }
        save_users(users)
    return users[uid]

def get_free_remaining(user_id: int) -> int:
    user_data = get_or_create_user(user_id)
    used      = user_data.get("free_used", 0)
    return max(0, FREE_SEARCHES - used)

def get_daily_remaining(user_id: int) -> int:
    users     = load_users()
    uid       = str(user_id)
    user_data = users.get(uid, {})
    plan_key  = user_data.get("plan", "trial")
    plan      = PLANS.get(plan_key, PLANS["trial"])

    if plan.get("unlimited", False):
        return 999999

    daily_limit = plan.get("daily_limit", 0)
    today       = date.today().isoformat()
    last_date   = user_data.get("last_search_date", "")
    daily_used  = user_data.get("daily_searches", 0)

    if last_date != today:
        return daily_limit

    return max(0, daily_limit - daily_used)

def use_one_search(user_id: int):
    users     = load_users()
    uid       = str(user_id)
    user_data = users.get(uid, {})
    today     = date.today().isoformat()

    if user_data.get("last_search_date", "") != today:
        user_data["daily_searches"]   = 0
        user_data["last_search_date"] = today

    plan_key = user_data.get("plan", "trial")
    plan     = PLANS.get(plan_key, PLANS["trial"])

    if plan.get("is_free", True):
        user_data["free_used"] = user_data.get("free_used", 0) + 1
    else:
        user_data["daily_searches"] = user_data.get("daily_searches", 0) + 1

    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    users[uid] = user_data
    save_users(users)

def check_access(user_id: int):
    get_or_create_user(user_id)
    users     = load_users()
    uid       = str(user_id)
    user_data = users[uid]
    plan_key  = user_data.get("plan", "trial")
    plan      = PLANS.get(plan_key, PLANS["trial"])
    expiry_str = user_data.get("expiry", "")

    # Premium plan check
    if not plan.get("is_free", True) and expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                # Plan expired, check free searches
                free_left = get_free_remaining(user_id)
                if free_left > 0:
                    return True, "⚠️ Plan expired | 🆓 1 free left", 0, False, "trial"
                return False, "❌ Plan expired! Renew karo.", 0, False, "trial"

            days_left   = (expiry - date.today()).days
            daily_rem   = get_daily_remaining(user_id)
            daily_limit = plan.get("daily_limit", 0)
            is_unlimited = plan.get("unlimited", False)

            if is_unlimited:
                status = f"✅ {plan['name']} | Unlimited | {days_left}d left"
                return True, status, days_left, True, plan_key
            else:
                if daily_rem <= 0:
                    return False, f"❌ Aaj ka limit khatam! ({daily_limit}/day) Kal aana.", days_left, True, plan_key
                status = f"✅ {plan['name']} | {daily_rem}/{daily_limit} today | {days_left}d left"
                return True, status, days_left, True, plan_key
        except:
            pass

    # Free trial check
    free_left = get_free_remaining(user_id)
    if free_left > 0:
        return True, f"🆓 Trial ({free_left}/{FREE_SEARCHES} search left)", 0, False, "trial"

    return False, "❌ Trial khatam! Plan lo.", 0, False, "trial"

def upgrade_user(user_id: int, plan_key: str):
    users     = load_users()
    uid       = str(user_id)
    user_data = get_or_create_user(user_id)
    plan      = PLANS.get(plan_key, PLANS["7days"])
    expiry    = (date.today() + timedelta(days=plan["days"])).isoformat()

    user_data["plan"]           = plan_key
    user_data["expiry"]         = expiry
    user_data["is_premium"]     = True
    user_data["daily_searches"] = 0
    user_data["last_search_date"] = ""
    users[uid] = user_data
    save_users(users)
    return expiry
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

    main_data   = data.get("data", data)
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

    seen           = set()
    unique_records = []
    for rec in all_records:
        identifier = (
            str(rec.get("FullName", rec.get("Name", ""))).lower() +
            str(rec.get("Phone",    rec.get("Phone2", "")))
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
    ok, _, _, is_premium, plan_key = check_access(user_id)
    free_left  = get_free_remaining(user_id)
    daily_rem  = get_daily_remaining(user_id)

    if is_premium:
        plan    = PLANS.get(plan_key, PLANS["7days"])
        if plan.get("unlimited", False):
            search_label = "🔍 Search (Unlimited)"
            batch_label  = "📦 Batch (Unlimited)"
        else:
            search_label = f"🔍 Search ({daily_rem} today)"
            batch_label  = f"📦 Batch ({daily_rem} today)"
    elif free_left > 0:
        search_label = f"🔍 Search ({free_left} trial)"
        batch_label  = f"📦 Batch ({free_left} trial)"
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
            InlineKeyboardButton("💰 Buy Plan",   callback_data="buy"),
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
            InlineKeyboardButton("📅 Set Plan",   callback_data="admin_expiry"),
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

def plan_keyboard(prefix: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🥉 7 Days  - ₹50",      callback_data=f"{prefix}_7days"),
            InlineKeyboardButton("🥈 30 Days - ₹130",     callback_data=f"{prefix}_30days"),
        ],
        [
            InlineKeyboardButton("🥇 6 Months - ₹300",    callback_data=f"{prefix}_6months"),
            InlineKeyboardButton("💎 12 Months - ₹799",   callback_data=f"{prefix}_12months"),
        ],
        [InlineKeyboardButton("❌ Cancel",                 callback_data="admin_cancel")],
    ])

async def safe_edit(query, text, reply_markup=None, parse_mode="Markdown"):
    try:
        await query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )
    except Exception:
        pass
        # ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id)
    ok, status, days, is_premium, plan_key = check_access(user.id)
    free_left = get_free_remaining(user.id)
    daily_rem = get_daily_remaining(user.id)
    plan      = PLANS.get(plan_key, PLANS["trial"])

    if is_premium:
        if plan.get("unlimited", False):
            status_emoji = "💎"
            status_color = "Premium Unlimited"
        else:
            status_emoji = "✅"
            status_color = f"Premium ({plan['name']})"
    elif free_left > 0:
        status_emoji = "🆓"
        status_color = "Trial"
    else:
        status_emoji = "🔴"
        status_color = "Locked"

    text = (
        f"{'━' * 30}\n"
        f"   🔍 *Phone Lookup Bot*\n"
        f"{'━' * 30}\n\n"
        f"👋 Welcome *{user.first_name}*!\n\n"
        f"{status_emoji} Account: *{status_color}*\n"
        f"📅 {status}\n\n"
    )

    if is_premium and not plan.get("unlimited", False):
        daily_limit = plan.get("daily_limit", 0)
        used_today  = daily_limit - daily_rem
        bar         = "🟢" * daily_rem + "🔴" * used_today
        text += (
            f"{'━' * 25}\n"
            f"📊 Today: {bar}\n"
            f"   {daily_rem}/{daily_limit} remaining\n"
            f"{'━' * 25}\n\n"
        )
    elif not is_premium:
        used = FREE_SEARCHES - free_left
        bar  = "🟢" * free_left + "🔴" * used
        text += (
            f"{'━' * 25}\n"
            f"🆓 Trial: {bar}\n"
            f"   {free_left}/{FREE_SEARCHES} remaining\n"
            f"{'━' * 25}\n\n"
        )

    text += "Choose an option below 👇"

    if update.callback_query:
        await safe_edit(
            update.callback_query, text,
            reply_markup=main_menu_keyboard(user.id)
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=main_menu_keyboard(user.id),
            parse_mode="Markdown"
        )
    return ConversationHandler.END


# ================== PROFILE ==================
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user                              = query.from_user
    ok, status, days, is_premium, plan_key = check_access(user.id)
    free_left                         = get_free_remaining(user.id)
    daily_rem                         = get_daily_remaining(user.id)
    user_data                         = get_or_create_user(user.id)
    total_s                           = user_data.get("total_searches", 0)
    plan                              = PLANS.get(plan_key, PLANS["trial"])

    if is_premium:
        acc_type   = f"{plan['name']}"
        bar_length = 20
        filled     = min(int((days / plan["days"]) * bar_length), bar_length) if days > 0 else 0
        bar        = "█" * filled + "░" * (bar_length - filled)

        if plan.get("unlimited", False):
            expiry_info = (
                f"📅 *Expires:* {user_data.get('expiry', 'N/A')}\n"
                f"⏳ *Days Left:* {days}\n"
                f"🔍 *Daily Limit:* Unlimited\n"
                f"📈 `[{bar}]`\n"
            )
        else:
            daily_limit = plan.get("daily_limit", 0)
            expiry_info = (
                f"📅 *Expires:* {user_data.get('expiry', 'N/A')}\n"
                f"⏳ *Days Left:* {days}\n"
                f"🔍 *Today:* {daily_rem}/{daily_limit} remaining\n"
                f"📈 `[{bar}]`\n"
            )
    else:
        acc_type    = "🆓 Trial"
        used        = FREE_SEARCHES - free_left
        bar         = "🟢" * free_left + "🔴" * used
        expiry_info = (
            f"🆓 *Trial Search:* {free_left}/{FREE_SEARCHES}\n"
            f"📊 {bar}\n"
        )

    text = (
        f"{'━' * 30}\n"
        f"       👤 *Your Profile*\n"
        f"{'━' * 30}\n\n"
        f"🆔 *ID:* `{user.id}`\n"
        f"👤 *Name:* {user.first_name} {user.last_name or ''}\n"
        f"📛 *Username:* @{user.username or 'N/A'}\n\n"
        f"{'━' * 30}\n"
        f"       🔐 *Account Info*\n"
        f"{'━' * 30}\n\n"
        f"📦 *Plan:* {acc_type}\n"
        f"{expiry_info}\n"
        f"🔍 *Total Searches:* {total_s}\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard(user.id))


# ================== STATUS ==================
async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user                              = query.from_user
    ok, status, days, is_premium, plan_key = check_access(user.id)
    free_left                         = get_free_remaining(user.id)
    daily_rem                         = get_daily_remaining(user.id)
    plan                              = PLANS.get(plan_key, PLANS["trial"])

    if is_premium:
        if plan.get("unlimited", False):
            text = (
                f"💎 *Account: PREMIUM*\n\n"
                f"📦 Plan: {plan['name']}\n"
                f"⏳ {days} days remaining\n"
                f"🔍 Daily: *Unlimited*\n\n"
                f"✅ Search karo!"
            )
        else:
            daily_limit = plan.get("daily_limit", 0)
            text = (
                f"✅ *Account: PREMIUM*\n\n"
                f"📦 Plan: {plan['name']}\n"
                f"⏳ {days} days remaining\n"
                f"🔍 Today: *{daily_rem}/{daily_limit}*\n\n"
                f"💡 Kal reset hoga!"
            )
    elif ok:
        text = (
            f"🆓 *Account: TRIAL*\n\n"
            f"🔍 {free_left} search remaining\n\n"
            f"💡 Plans dekhne ke liye:\n"
            f"👉 Buy Plan button dabao"
        )
    else:
        text = (
            f"🔴 *Account: LOCKED*\n\n"
            f"📅 {status}\n\n"
            f"❌ Koi search nahi bacha!\n\n"
            f"💰 Plan lo:\n"
            f"👉 {OWNER_CONTACT}\n\n"
            f"Your ID: `{user.id}`"
        )
    await safe_edit(query, text, reply_markup=back_keyboard(user.id))


# ================== HELP ==================
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        f"{'━' * 30}\n"
        f"       ❓ *Help Guide*\n"
        f"{'━' * 30}\n\n"
        f"🆓 *Trial*\n"
        f"   Sirf 1 free search\n\n"
        f"💰 *Plans:*\n"
        f"   🥉 7 Days  → ₹50  → 5/day\n"
        f"   🥈 30 Days → ₹130 → 10/day\n"
        f"   🥇 6 Month → ₹300 → 15/day\n"
        f"   💎 12 Month→ ₹799 → Unlimited\n\n"
        f"🔍 *Single Search*\n"
        f"   Example: `919876543210`\n\n"
        f"📦 *Batch Search*\n"
        f"   Example: `9198...,9197...`\n"
        f"   ⚠️ Each number = 1 search\n\n"
        f"{'━' * 30}\n"
        f"💡 *Tips:*\n"
        f"   • Country code lagao (91)\n"
        f"   • No spaces or dashes\n"
        f"   • Daily limit midnight reset\n"
        f"   • Max 15 batch mein\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== BUY ==================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query     = update.callback_query
    await query.answer()
    user      = query.from_user
    free_left = get_free_remaining(user.id)

    text = (
        f"{'━' * 30}\n"
        f"       💰 *Buy Plan*\n"
        f"{'━' * 30}\n\n"
        f"🆓 Trial: {FREE_SEARCHES - free_left}/{FREE_SEARCHES} used\n\n"
        f"📋 *Available Plans:*\n\n"
        f"🥉 *7 Days*\n"
        f"   💵 ₹50 | 🔍 5 searches/day\n\n"
        f"🥈 *30 Days*\n"
        f"   💵 ₹130 | 🔍 10 searches/day\n\n"
        f"🥇 *6 Months*\n"
        f"   💵 ₹300 | 🔍 15 searches/day\n\n"
        f"💎 *12 Months*\n"
        f"   💵 ₹799 | 🔍 Unlimited\n\n"
        f"{'━' * 30}\n\n"
        f"📱 Contact admin:\n"
        f"👉 {OWNER_CONTACT}\n\n"
        f"Your ID: `{user.id}`\n"
        f"_Admin ko ye ID do_"
    )
    await safe_edit(query, text, reply_markup=buy_keyboard())


# ================== SINGLE SEARCH ==================
async def single_search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user                              = query.from_user
    ok, status, _, is_premium, plan_key = check_access(user.id)
    free_left                         = get_free_remaining(user.id)
    daily_rem                         = get_daily_remaining(user.id)
    plan                              = PLANS.get(plan_key, PLANS["trial"])

    if not ok:
        await safe_edit(
            query,
            f"🔒 *Search Locked!*\n\n"
            f"{status}\n\n"
            f"💰 Plan lo:\n"
            f"👉 {OWNER_CONTACT}\n\n"
            f"Your ID: `{user.id}`",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    if is_premium:
        if plan.get("unlimited", False):
            info = "💎 Unlimited searches"
        else:
            daily_limit = plan.get("daily_limit", 0)
            info = f"✅ {daily_rem}/{daily_limit} searches today"
    else:
        info = f"🆓 {free_left} trial search"

    await safe_edit(
        query,
        f"🔍 *Single Search Mode*\n\n"
        f"📊 {info}\n\n"
        f"📱 Phone number daalo:\n"
        f"_Example: 919876543210_\n\n"
        f"Type /cancel to go back",
    )
    return WAITING_SINGLE


async def single_search_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    user   = update.effective_user

    if not number.isdigit():
        await update.message.reply_text(
            "❌ Invalid! Sirf numbers.\nTry again or /cancel"
        )
        return WAITING_SINGLE

    ok, status, _, is_premium, plan_key = check_access(user.id)
    if not ok:
        await update.message.reply_text(
            f"🔒 *Locked!*\n{status}\n💰 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    msg    = await update.message.reply_text("🔍 Searching...")
    result = search_api(number)

    if result["ok"]:
        use_one_search(user.id)
        free_left = get_free_remaining(user.id)
        daily_rem = get_daily_remaining(user.id)
        plan      = PLANS.get(plan_key, PLANS["trial"])
        text      = format_result(number, result["data"])

        if is_premium and not plan.get("unlimited", False):
            daily_limit = plan.get("daily_limit", 0)
            text += (
                f"\n\n{'━' * 25}\n"
                f"📊 Today: *{daily_rem}/{daily_limit}* remaining"
            )
        elif not is_premium:
            text += (
                f"\n\n{'━' * 25}\n"
                f"🆓 Trial: *{free_left}/{FREE_SEARCHES}* remaining"
            )

        await msg.edit_text(
            text,
            reply_markup=main_menu_keyboard(user.id),
            parse_mode="Markdown"
        )
    else:
        await msg.edit_text(
            f"❌ *Search Failed*\n\nError: `{result['error']}`",
            reply_markup=back_keyboard(user.id),
            parse_mode="Markdown",
        )
    return ConversationHandler.END


# ================== BATCH SEARCH ==================
async def batch_search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user                              = query.from_user
    ok, status, _, is_premium, plan_key = check_access(user.id)
    free_left                         = get_free_remaining(user.id)
    daily_rem                         = get_daily_remaining(user.id)
    plan                              = PLANS.get(plan_key, PLANS["trial"])

    if not ok:
        await safe_edit(
            query,
            f"🔒 *Search Locked!*\n\n{status}\n\n"
            f"💰 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    if is_premium:
        if plan.get("unlimited", False):
            info = "💎 Unlimited"
        else:
            daily_limit = plan.get("daily_limit", 0)
            info = f"✅ {daily_rem}/{daily_limit} today"
    else:
        info = f"🆓 {free_left} trial"

    await safe_edit(
        query,
        f"📦 *Batch Search Mode*\n\n"
        f"📊 {info}\n\n"
        f"📱 Numbers daalo (comma se alag):\n"
        f"_Example: 9198...,9197...,9196..._\n"
        f"_Max 15 ek baar mein_\n\n"
        f"Type /cancel to go back",
    )
    return WAITING_BATCH


async def batch_search_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw     = update.message.text.strip()
    user    = update.effective_user
    numbers = [n.strip() for n in raw.replace(",", " ").split() if n.strip()]

    if not numbers:
        await update.message.reply_text("❌ Koi number nahi! Try again or /cancel")
        return WAITING_BATCH

    numbers                           = numbers[:15]
    total                             = len(numbers)
    ok, status, _, is_premium, plan_key = check_access(user.id)
    free_left                         = get_free_remaining(user.id)
    daily_rem                         = get_daily_remaining(user.id)
    plan                              = PLANS.get(plan_key, PLANS["trial"])

    available = 999999 if plan.get("unlimited", False) else (
        daily_rem if is_premium else free_left
    )

    if total > available:
        await update.message.reply_text(
            f"❌ *Searches kam hain!*\n\n"
            f"Aapne daala: *{total}* numbers\n"
            f"Available: *{available}* searches\n\n"
            f"💡 Max *{available}* numbers dalein\n"
            f"Ya premium lo unlimited ke liye\n"
            f"👉 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    msg = await update.message.reply_text(
        f"🚀 Processing {total} numbers...\n[{'░' * total}]"
    )

    for i, num in enumerate(numbers, 1):
        result   = search_api(num)
        progress = "█" * i + "░" * (total - i)

        if result["ok"]:
            use_one_search(user.id)
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

    daily_rem = get_daily_remaining(user.id)
    free_left = get_free_remaining(user.id)
    summary   = f"✅ *Batch Complete!*\n📊 Processed: {total} numbers"

    if is_premium and not plan.get("unlimited", False):
        daily_limit = plan.get("daily_limit", 0)
        summary += f"\n📊 Today Left: *{daily_rem}/{daily_limit}*"
    elif not is_premium:
        summary += f"\n🆓 Trial Left: *{free_left}/{FREE_SEARCHES}*"

    await msg.edit_text(
        summary,
        reply_markup=main_menu_keyboard(user.id),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


# ================== CANCEL ==================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        "❌ Cancelled.",
        reply_markup=main_menu_keyboard(user.id)
    )
    return ConversationHandler.END
    # ================== ADMIN ==================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        if update.message:
            await update.message.reply_text("❌ Admin only!")
        return ConversationHandler.END

    users    = load_users()
    total    = len(users)
    premium  = sum(1 for u in users.values() if u.get("is_premium", False))
    free_u   = total - premium

    text = (
        f"{'━' * 30}\n"
        f"       🛠️ *Admin Panel*\n"
        f"{'━' * 30}\n\n"
        f"👥 Total: {total} | 💎 Premium: {premium} | 🆓 Trial: {free_u}\n\n"
        f"Choose an action:"
    )

    if update.callback_query:
        await safe_edit(
            update.callback_query, text,
            reply_markup=admin_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=admin_menu_keyboard(),
            parse_mode="Markdown"
        )
    return ConversationHandler.END


async def admin_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(
        query,
        "➕ *Add Premium User*\n\n"
        "Telegram User ID daalo:\n\n"
        "/cancel to go back"
    )
    return ADMIN_ADD_ID


async def admin_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ Invalid ID!\n/cancel to stop")
        return ADMIN_ADD_ID
    context.user_data["new_uid"] = uid
    await update.message.reply_text(
        f"✅ User ID: `{uid}`\n\nPlan select karo:",
        reply_markup=plan_keyboard("addplan"),
        parse_mode="Markdown",
    )
    return ADMIN_ADD_PLAN


async def admin_add_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "admin_cancel":
        await admin_panel(update, context)
        return ConversationHandler.END

    plan_map = {
        "addplan_7days"  : "7days",
        "addplan_30days" : "30days",
        "addplan_6months": "6months",
        "addplan_12months": "12months",
    }

    plan_key = plan_map.get(query.data, "7days")
    uid      = context.user_data.get("new_uid")
    plan     = PLANS.get(plan_key, PLANS["7days"])
    expiry   = upgrade_user(int(uid), plan_key)

    await safe_edit(
        query,
        f"✅ *Plan Added!*\n\n"
        f"🆔 ID: `{uid}`\n"
        f"📦 Plan: {plan['name']}\n"
        f"💵 Price: ₹{plan['price']}\n"
        f"🔍 Daily: {plan['daily_limit'] if not plan['unlimited'] else 'Unlimited'}\n"
        f"📅 Expiry: `{expiry}`\n"
        f"⏳ Days: {plan['days']}",
        reply_markup=admin_menu_keyboard(),
    )
    return ConversationHandler.END


async def admin_remove_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(
        query,
        "❌ *Remove User*\n\n"
        "Telegram User ID daalo:\n\n"
        "/cancel to go back"
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
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"❌ User `{uid}` not found!",
            reply_markup=admin_menu_keyboard(),
            parse_mode="Markdown"
        )
    return ConversationHandler.END


async def admin_expiry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(
        query,
        "📅 *Set User Plan*\n\n"
        "User ID daalo:\n\n"
        "/cancel to go back"
    )
    return ADMIN_EXP_ID


async def admin_expiry_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    context.user_data["exp_uid"] = uid
    await update.message.reply_text(
        f"User: `{uid}`\nPlan select karo:",
        reply_markup=plan_keyboard("setplan"),
        parse_mode="Markdown",
    )
    return ADMIN_EXP_PLAN


async def admin_expiry_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "admin_cancel":
        await admin_panel(update, context)
        return ConversationHandler.END

    plan_map = {
        "setplan_7days"   : "7days",
        "setplan_30days"  : "30days",
        "setplan_6months" : "6months",
        "setplan_12months": "12months",
    }

    plan_key = plan_map.get(query.data, "7days")
    uid      = context.user_data.get("exp_uid")
    plan     = PLANS.get(plan_key, PLANS["7days"])
    expiry   = upgrade_user(int(uid), plan_key)

    await safe_edit(
        query,
        f"✅ *Plan Updated!*\n\n"
        f"🆔 User: `{uid}`\n"
        f"📦 Plan: {plan['name']}\n"
        f"💵 Price: ₹{plan['price']}\n"
        f"🔍 Daily: {plan['daily_limit'] if not plan['unlimited'] else 'Unlimited'}\n"
        f"📅 Expiry: `{expiry}`\n"
        f"⏳ Days: {plan['days']}",
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
        await safe_edit(
            query, "📋 *No users yet!*",
            reply_markup=admin_menu_keyboard()
        )
        return

    text = f"{'━' * 30}\n📋 *All Users ({len(users)})*\n{'━' * 30}\n\n"

    for uid, info in users.items():
        is_prem  = info.get("is_premium", False)
        plan_key = info.get("plan", "trial")
        plan     = PLANS.get(plan_key, PLANS["trial"])
        total_s  = info.get("total_searches", 0)
        exp      = info.get("expiry", "")

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
            free_u = info.get("free_used", 0)
            left   = max(0, FREE_SEARCHES - free_u)
            s      = f"🆓 {left}/{FREE_SEARCHES} trial"

        plan_emoji = plan.get("name", "🆓 Trial").split()[0]
        text += f"{plan_emoji} `{uid}` | {s} | 🔍{total_s}\n"

    await safe_edit(query, text[:4000], reply_markup=admin_menu_keyboard())


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌")
        return
    await query.answer()
    users = load_users()

    total          = len(users)
    total_searches = 0
    plan_counts    = {k: 0 for k in PLANS.keys()}
    expired        = 0

    for info in users.values():
        total_searches += info.get("total_searches", 0)
        plan_key        = info.get("plan", "trial")
        is_prem         = info.get("is_premium", False)
        exp             = info.get("expiry", "")

        if is_prem and exp:
            try:
                exp_date = date.fromisoformat(exp)
                if date.today() > exp_date:
                    expired += 1
                else:
                    plan_counts[plan_key] = plan_counts.get(plan_key, 0) + 1
            except:
                expired += 1
        else:
            plan_counts["trial"] = plan_counts.get("trial", 0) + 1

    text = (
        f"{'━' * 30}\n"
        f"       📊 *Bot Statistics*\n"
        f"{'━' * 30}\n\n"
        f"👥 *Total Users*    : {total}\n"
        f"🔍 *Total Searches* : {total_searches}\n\n"
        f"{'━' * 25}\n"
        f"📦 *Plan Breakdown*\n"
        f"{'━' * 25}\n"
        f"🆓 Trial     : {plan_counts.get('trial', 0)}\n"
        f"🥉 7 Days    : {plan_counts.get('7days', 0)}\n"
        f"🥈 30 Days   : {plan_counts.get('30days', 0)}\n"
        f"🥇 6 Months  : {plan_counts.get('6months', 0)}\n"
        f"💎 12 Months : {plan_counts.get('12months', 0)}\n"
        f"🔴 Expired   : {expired}\n\n"
        f"📅 Date: {date.today()}\n"
    )
    await safe_edit(query, text, reply_markup=admin_menu_keyboard())


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END


# ================== MAIN ==================
def main():
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
            ]
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
            ]
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
            ADMIN_ADD_PLAN: [
                CallbackQueryHandler(
                    admin_add_plan,
                    pattern="^addplan_|^admin_cancel$"
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
            ]
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
            ADMIN_EXP_PLAN: [
                CallbackQueryHandler(
                    admin_expiry_set,
                    pattern="^setplan_|^admin_cancel$"
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
        allow_reentry=True,
    )

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
    print(f"👤 Admin ID      : {ADMIN_ID}")
    print(f"🔑 PIN           : {DEFAULT_PIN}")
    print(f"🆓 Free Searches : {FREE_SEARCHES}")
    print("📦 Plans:")
    for k, v in PLANS.items():
        if not v["is_free"]:
            limit = "Unlimited" if v["unlimited"] else f"{v['daily_limit']}/day"
            print(f"   {v['name']} | ₹{v['price']} | {limit}")
    print("⏹  Press Ctrl+C to stop\n")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🔍 Phone & Email Intelligence Bot
Combined Bot - Phone + Email Search
ONE PLAN = BOTH ACCESS
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
BOT_TOKEN     = "8642873626:AAFy5F79opcK_NMJ7NgGItd6sRrfbOc4TJU"
ADMIN_IDS     = [5057489358, 1968142314]
DEFAULT_PIN   = "912036"
API_URL       = "https://lk-api-pinsstm.ramaxinfo.workers.dev/"
DATA_FILE     = Path("users.json")
OWNER_CONTACT = "@theplayerror"

# ================== FREE SEARCHES ==================
PHONE_FREE_SEARCHES = 1
EMAIL_FREE_SEARCHES = 3

# ================== PLANS ==================
PLANS = {
    "trial": {
        "name"       : "Trial",
        "days"       : 0,
        "price"      : 0,
        "daily_limit": 0,
        "unlimited"  : False,
        "is_free"    : True,
    },
    "7days": {
        "name"       : "7 Days",
        "days"       : 7,
        "price"      : 50,
        "daily_limit": 5,
        "unlimited"  : False,
        "is_free"    : False,
    },
    "30days": {
        "name"       : "30 Days",
        "days"       : 30,
        "price"      : 130,
        "daily_limit": 10,
        "unlimited"  : False,
        "is_free"    : False,
    },
    "6months": {
        "name"       : "6 Months",
        "days"       : 180,
        "price"      : 300,
        "daily_limit": 15,
        "unlimited"  : False,
        "is_free"    : False,
    },
    "12months": {
        "name"       : "12 Months",
        "days"       : 365,
        "price"      : 799,
        "daily_limit": 999999,
        "unlimited"  : True,
        "is_free"    : False,
    },
}

# ================== STATES ==================
PHONE_COUNTRY_SINGLE = 10
PHONE_COUNTRY_BATCH  = 11
PHONE_SINGLE_INDIA   = 12
PHONE_SINGLE_OTHER   = 13
PHONE_BATCH_INDIA    = 14
PHONE_BATCH_OTHER    = 15
EMAIL_SINGLE         = 20
EMAIL_BATCH          = 21
ADMIN_ADD_ID         = 30
ADMIN_ADD_PLAN       = 31
ADMIN_REM_ID         = 32
ADMIN_EXP_ID         = 33
ADMIN_EXP_PLAN       = 34


# ================== ADMIN CHECK ==================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ================== DATA ==================
def load_users():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_users(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))

def get_or_create_user(user_id: int):
    users = load_users()
    uid   = str(user_id)
    if uid not in users:
        users[uid] = {
            "plan"                : "trial",
            "expiry"              : "",
            "is_premium"          : False,
            "phone_free_used"     : 0,
            "phone_daily_searches": 0,
            "phone_last_date"     : "",
            "phone_total"         : 0,
            "email_free_used"     : 0,
            "email_total"         : 0,
            "added"               : date.today().isoformat(),
            "total_searches"      : 0,
        }
        save_users(users)
    return users[uid]


# ================== PLAN UPGRADE ==================
def upgrade_user(user_id: int, plan_key: str):
    users     = load_users()
    uid       = str(user_id)
    user_data = get_or_create_user(user_id)
    plan      = PLANS.get(plan_key, PLANS["7days"])
    expiry    = (date.today() + timedelta(days=plan["days"])).isoformat()
    user_data["plan"]                 = plan_key
    user_data["expiry"]               = expiry
    user_data["is_premium"]           = True
    user_data["phone_daily_searches"] = 0
    user_data["phone_last_date"]      = ""
    users[uid] = user_data
    save_users(users)
    return expiry


# ==================== PHONE ACCESS ====================
def get_phone_free_remaining(user_id: int) -> int:
    if is_admin(user_id):
        return 999999
    user_data = get_or_create_user(user_id)
    used      = user_data.get("phone_free_used", 0)
    return max(0, PHONE_FREE_SEARCHES - used)

def get_phone_daily_remaining(user_id: int) -> int:
    if is_admin(user_id):
        return 999999
    users     = load_users()
    uid       = str(user_id)
    user_data = users.get(uid, {})
    plan_key  = user_data.get("plan", "trial")
    plan      = PLANS.get(plan_key, PLANS["trial"])
    if plan.get("unlimited", False):
        return 999999
    daily_limit = plan.get("daily_limit", 0)
    today       = date.today().isoformat()
    last_date   = user_data.get("phone_last_date", "")
    daily_used  = user_data.get("phone_daily_searches", 0)
    if last_date != today:
        return daily_limit
    return max(0, daily_limit - daily_used)

def use_phone_search(user_id: int):
    users     = load_users()
    uid       = str(user_id)
    user_data = users.get(uid, {})
    today     = date.today().isoformat()
    if user_data.get("phone_last_date", "") != today:
        user_data["phone_daily_searches"] = 0
        user_data["phone_last_date"]      = today
    plan_key = user_data.get("plan", "trial")
    plan     = PLANS.get(plan_key, PLANS["trial"])
    if not is_admin(user_id):
        if plan.get("is_free", True):
            user_data["phone_free_used"] = user_data.get("phone_free_used", 0) + 1
        else:
            user_data["phone_daily_searches"] = user_data.get("phone_daily_searches", 0) + 1
    user_data["phone_total"]    = user_data.get("phone_total", 0) + 1
    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    users[uid] = user_data
    save_users(users)

def check_phone_access(user_id: int):
    if is_admin(user_id):
        return True, "Admin Unlimited", 9999, True, "12months"
    get_or_create_user(user_id)
    users      = load_users()
    uid        = str(user_id)
    user_data  = users[uid]
    plan_key   = user_data.get("plan", "trial")
    plan       = PLANS.get(plan_key, PLANS["trial"])
    expiry_str = user_data.get("expiry", "")
    is_premium = user_data.get("is_premium", False)
    if is_premium and expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                free_left = get_phone_free_remaining(user_id)
                if free_left > 0:
                    return True, "Plan expired | " + str(free_left) + " free left", 0, False, "trial"
                return False, "Plan expired! Renew karo.", 0, False, "trial"
            days_left    = (expiry - date.today()).days
            daily_rem    = get_phone_daily_remaining(user_id)
            daily_limit  = plan.get("daily_limit", 0)
            is_unlimited = plan.get("unlimited", False)
            if is_unlimited:
                return True, plan["name"] + " | Unlimited | " + str(days_left) + "d left", days_left, True, plan_key
            else:
                if daily_rem <= 0:
                    return False, "Daily limit khatam! (" + str(daily_limit) + "/day)", days_left, True, plan_key
                return True, plan["name"] + " | " + str(daily_rem) + "/" + str(daily_limit) + " today | " + str(days_left) + "d left", days_left, True, plan_key
        except Exception:
            pass
    free_left = get_phone_free_remaining(user_id)
    if free_left > 0:
        return True, "Trial (" + str(free_left) + "/" + str(PHONE_FREE_SEARCHES) + " left)", 0, False, "trial"
    return False, "Trial khatam! Plan lo.", 0, False, "trial"


# ==================== EMAIL ACCESS ====================
def get_email_free_remaining(user_id: int) -> int:
    if is_admin(user_id):
        return 999999
    user_data = get_or_create_user(user_id)
    used      = user_data.get("email_free_used", 0)
    return max(0, EMAIL_FREE_SEARCHES - used)

def use_email_search(user_id: int, is_premium: bool):
    users     = load_users()
    uid       = str(user_id)
    user_data = users.get(uid, {})
    if not is_admin(user_id):
        if not is_premium:
            user_data["email_free_used"] = user_data.get("email_free_used", 0) + 1
    user_data["email_total"]    = user_data.get("email_total", 0) + 1
    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    users[uid] = user_data
    save_users(users)

def check_email_access(user_id: int):
    if is_admin(user_id):
        return True, "Admin Unlimited", 9999, True
    get_or_create_user(user_id)
    users      = load_users()
    uid        = str(user_id)
    user_data  = users[uid]
    is_premium = user_data.get("is_premium", False)
    expiry_str = user_data.get("expiry", "")
    if is_premium and expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                free_left = get_email_free_remaining(user_id)
                if free_left > 0:
                    return True, "Plan expired | " + str(free_left) + " free left", 0, False
                return False, "Plan expired! Renew karo.", 0, False
            days = (expiry - date.today()).days
            return True, "Premium (" + str(days) + " days left)", days, True
        except Exception:
            pass
    free_left = get_email_free_remaining(user_id)
    if free_left > 0:
        return True, "Free (" + str(free_left) + "/" + str(EMAIL_FREE_SEARCHES) + " left)", 0, False
    return False, "Free khatam! Plan lo.", 0, False


# ================== API ==================
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


# ================== SKIP / FORMAT ==================
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
        "timestamp", "response", "developer", "owner", "credit",
        "powered", "source", "version", "watermark", "pheevar",
        "advertisement", "promo", "channel", "server", "api_",
        "made_by", "encrypted", "password", "salt",
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
        "email": "📧", "mail": "📧", "email2": "📧",
        "phone": "📞", "phone2": "📞", "number": "📞", "mobile": "📞",
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
        if should_skip(k) or should_skip_value(v):
            continue
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if should_skip(sub_k) or should_skip_value(sub_v):
                    continue
                emoji = get_emoji(sub_k.lower())
                label = sub_k.replace("_", " ").replace("-", " ").title()
                lines.append(emoji + " *" + label + "*: `" + str(sub_v) + "`")
            continue
        if isinstance(v, list):
            clean = [str(i) for i in v if not should_skip_value(i)]
            if clean:
                emoji = get_emoji(k.lower())
                label = k.replace("_", " ").replace("-", " ").title()
                lines.append(emoji + " *" + label + "*: `" + ", ".join(clean) + "`")
            continue
        emoji = get_emoji(k.lower())
        label = k.replace("_", " ").replace("-", " ").title()
        lines.append(emoji + " *" + label + "*: `" + str(v) + "`")
    return lines

def format_result(term: str, data, icon: str = "🔍"):
    if not data:
        return icon + " *" + str(term) + "*\n_No data found_"
    if isinstance(data, list):
        if not data:
            return icon + " *" + str(term) + "*\n_No data found_"
        if isinstance(data[0], dict):
            data = {"data": {"source": {"records": data}}}
        else:
            return icon + " *" + str(term) + "*\n`" + str(data[0]) + "`"
    if not isinstance(data, dict):
        return icon + " *" + str(term) + "*\n`" + str(data) + "`"

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
        return icon + " *" + str(term) + "*\n_No data found_"

    seen           = set()
    unique_records = []
    for rec in all_records:
        identifier = (
            str(rec.get("FullName", rec.get("Name", rec.get("Email", "")))).lower() +
            str(rec.get("Phone", rec.get("Phone2", "")))
        )
        if identifier not in seen:
            seen.add(identifier)
            unique_records.append(rec)

    divider = "\u2501" * 28
    output  = [
        icon + " *Result for* `" + str(term) + "`",
        "\U0001f4ca *" + str(len(unique_records)) + " record(s) found*",
        divider,
    ]
    for idx, record in enumerate(unique_records, 1):
        if len(unique_records) > 1:
            output.append("\n*\u2501\u2501 Record #" + str(idx) + " \u2501\u2501*")
        lines = format_record(record)
        if lines:
            output.extend(lines)
        else:
            output.append("_No relevant data_")
    return "\n".join(output)


# ================== KEYBOARDS ==================
def main_menu_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Phone Search", callback_data="mode_phone"),
            InlineKeyboardButton("📧 Email Search", callback_data="mode_email"),
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

def phone_menu_keyboard(user_id: int):
    if is_admin(user_id):
        single_label = "🔍 Single (Admin)"
        batch_label  = "📦 Batch (Admin)"
    else:
        ok, _, _, is_premium, plan_key = check_phone_access(user_id)
        free_left = get_phone_free_remaining(user_id)
        daily_rem = get_phone_daily_remaining(user_id)
        plan      = PLANS.get(plan_key, PLANS["trial"])
        if is_premium:
            if plan.get("unlimited", False):
                single_label = "🔍 Single (Unlimited)"
                batch_label  = "📦 Batch (Unlimited)"
            else:
                single_label = "🔍 Single (" + str(daily_rem) + " today)"
                batch_label  = "📦 Batch (" + str(daily_rem) + " today)"
        elif free_left > 0:
            single_label = "🔍 Single (" + str(free_left) + " trial)"
            batch_label  = "📦 Batch (" + str(free_left) + " trial)"
        else:
            single_label = "🔍 Single (🔒)"
            batch_label  = "📦 Batch (🔒)"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(single_label, callback_data="phone_single"),
            InlineKeyboardButton(batch_label,  callback_data="phone_batch"),
        ],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def email_menu_keyboard(user_id: int):
    if is_admin(user_id):
        single_label = "🔍 Single (Admin)"
        batch_label  = "📦 Batch (Admin)"
    else:
        ok, _, _, is_premium = check_email_access(user_id)
        free_left = get_email_free_remaining(user_id)
        if is_premium:
            single_label = "🔍 Single (Unlimited)"
            batch_label  = "📦 Batch (Unlimited)"
        elif free_left > 0:
            single_label = "🔍 Single (" + str(free_left) + " free)"
            batch_label  = "📦 Batch (" + str(free_left) + " free)"
        else:
            single_label = "🔍 Single (🔒)"
            batch_label  = "📦 Batch (🔒)"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(single_label, callback_data="email_single"),
            InlineKeyboardButton(batch_label,  callback_data="email_batch"),
        ],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def country_select_keyboard(mode: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇳 Indian Number (+91)", callback_data="country_india_" + mode)],
        [InlineKeyboardButton("🌍 Other Country (Manual Code)", callback_data="country_other_" + mode)],
        [InlineKeyboardButton("❌ Cancel", callback_data="main_menu")],
    ])

def admin_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add User",      callback_data="admin_add"),
            InlineKeyboardButton("❌ Remove User",   callback_data="admin_remove"),
        ],
        [
            InlineKeyboardButton("📅 Set Plan",     callback_data="admin_setplan"),
            InlineKeyboardButton("📋 All Users",    callback_data="admin_list"),
        ],
        [
            InlineKeyboardButton("📊 Stats",        callback_data="admin_stats"),
            # ✅ New Button - Free/Trial Monitor
            InlineKeyboardButton("🆓 Free Monitor", callback_data="admin_free_monitor"),
        ],
        [
            InlineKeyboardButton("🔙 Main Menu",    callback_data="main_menu"),
        ],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ])

def admin_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Admin Menu", callback_data="admin_back")]
    ])

def buy_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "💬 Contact Admin",
            url="https://t.me/" + OWNER_CONTACT.replace("@", "")
        )],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def plan_select_keyboard(prefix: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🥉 7 Days  - Rs50",    callback_data=prefix + "_7days"),
            InlineKeyboardButton("🥈 30 Days - Rs130",   callback_data=prefix + "_30days"),
        ],
        [
            InlineKeyboardButton("🥇 6 Months - Rs300",  callback_data=prefix + "_6months"),
            InlineKeyboardButton("💎 12 Months - Rs799", callback_data=prefix + "_12months"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_back")],
    ])

# ✅ Free Monitor Sub-Menu Keyboard
def free_monitor_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Phone Trial Users",  callback_data="monitor_phone"),
            InlineKeyboardButton("📧 Email Free Users",   callback_data="monitor_email"),
        ],
        [
            InlineKeyboardButton("🔴 All Exhausted",      callback_data="monitor_exhausted"),
            InlineKeyboardButton("🟢 Still Has Searches", callback_data="monitor_active"),
        ],
        [
            InlineKeyboardButton("📊 Full Summary",       callback_data="monitor_summary"),
        ],
        [InlineKeyboardButton("🔙 Admin Menu", callback_data="admin_back")],
    ])


# ================== HELPERS ==================
async def safe_edit(query, text, reply_markup=None, parse_mode="Markdown"):
    try:
        await query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode=parse_mode
        )
    except Exception:
        pass

def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1] and " " not in email

def make_bar(filled: int, total: int) -> str:
    filled = max(0, min(filled, total))
    return "█" * filled + "░" * (total - filled)


# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id)

    d1 = "\u2501" * 30
    d2 = "\u2501" * 25

    if is_admin(user.id):
        text = (
            d1 + "\n"
            "   🔍 *Phone & Email Lookup Bot*\n" +
            d1 + "\n\n"
            "👋 Welcome *" + user.first_name + "*!\n"
            "🛡️ *Admin — Unlimited Access*\n\n" +
            d2 + "\n"
            "📱 Phone Search : ∞ Unlimited\n"
            "📧 Email Search : ∞ Unlimited\n"
            "🔒 Restrictions : None\n" +
            d2 + "\n\n"
            "Choose search type below 👇"
        )
    else:
        users     = load_users()
        uid       = str(user.id)
        user_data = users.get(uid, {})
        is_prem   = user_data.get("is_premium", False)
        expiry    = user_data.get("expiry", "")
        plan_key  = user_data.get("plan", "trial")
        plan      = PLANS.get(plan_key, PLANS["trial"])
        p_free    = get_phone_free_remaining(user.id)
        e_free    = get_email_free_remaining(user.id)

        if is_prem and expiry:
            try:
                exp_date  = date.fromisoformat(expiry)
                days_left = (exp_date - date.today()).days
                if days_left >= 0:
                    daily_rem = get_phone_daily_remaining(user.id)
                    if plan.get("unlimited", False):
                        p_line = "💎 " + plan["name"] + " | Phone: Unlimited | " + str(days_left) + "d left"
                    else:
                        p_line = "💎 " + plan["name"] + " | Phone: " + str(daily_rem) + "/" + str(plan.get("daily_limit", 0)) + " today | " + str(days_left) + "d left"
                    e_line = "💎 " + plan["name"] + " | Email: Unlimited | " + str(days_left) + "d left"
                else:
                    p_bar  = "🟢" * p_free + "🔴" * (PHONE_FREE_SEARCHES - p_free)
                    p_line = "⚠️ Expired | Phone Trial: " + p_bar
                    e_bar  = "🟢" * e_free + "🔴" * (EMAIL_FREE_SEARCHES - e_free)
                    e_line = "⚠️ Expired | Email Free: " + e_bar
            except Exception:
                p_line = "⚪ Unknown"
                e_line = "⚪ Unknown"
        else:
            p_bar  = "🟢" * p_free + "🔴" * (PHONE_FREE_SEARCHES - p_free)
            p_line = "🆓 Trial: " + p_bar + " (" + str(p_free) + "/" + str(PHONE_FREE_SEARCHES) + ")"
            e_bar  = "🟢" * e_free + "🔴" * (EMAIL_FREE_SEARCHES - e_free)
            e_line = "🆓 Free: " + e_bar + " (" + str(e_free) + "/" + str(EMAIL_FREE_SEARCHES) + ")"

        text = (
            d1 + "\n"
            "   🔍 *Phone & Email Lookup Bot*\n" +
            d1 + "\n\n"
            "👋 Welcome *" + user.first_name + "*!\n\n" +
            d2 + "\n"
            "📱 *Phone Search*\n" +
            d2 + "\n" +
            p_line + "\n\n" +
            d2 + "\n"
            "📧 *Email Search*\n" +
            d2 + "\n" +
            e_line + "\n\n"
            "💡 *Ek plan se dono access milta hai!*\n\n" +
            d1 + "\n\n"
            "Choose search type below 👇"
        )

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


# ================== MODE SELECT ==================
async def mode_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        ok, status, days, is_premium, plan_key = check_phone_access(user.id)
        free_left = get_phone_free_remaining(user.id)
        daily_rem = get_phone_daily_remaining(user.id)
        plan      = PLANS.get(plan_key, PLANS["trial"])
        if is_premium:
            if plan.get("unlimited", False):
                info = "💎 Unlimited"
            else:
                info = "✅ " + str(daily_rem) + "/" + str(plan.get("daily_limit", 0)) + " today"
        else:
            info = "🆓 " + str(free_left) + "/" + str(PHONE_FREE_SEARCHES) + " trial"
    d1   = "\u2501" * 30
    text = (
        d1 + "\n"
        "   📱 *Phone Number Search*\n" +
        d1 + "\n\n"
        "📊 Status: " + info + "\n\n"
        "Single ya Batch search choose karo:"
    )
    await safe_edit(query, text, reply_markup=phone_menu_keyboard(user.id))

async def mode_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        ok, status, days, is_premium = check_email_access(user.id)
        free_left = get_email_free_remaining(user.id)
        if is_premium:
            info = "💎 Premium | " + str(days) + "d left"
        else:
            info = "🆓 " + str(free_left) + "/" + str(EMAIL_FREE_SEARCHES) + " free"
    d1   = "\u2501" * 30
    text = (
        d1 + "\n"
        "   📧 *Email Search*\n" +
        d1 + "\n\n"
        "📊 Status: " + info + "\n\n"
        "Single ya Batch search choose karo:"
    )
    await safe_edit(query, text, reply_markup=email_menu_keyboard(user.id))


# ================== PROFILE ==================
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user      = query.from_user
    user_data = get_or_create_user(user.id)
    total_s   = user_data.get("total_searches", 0)
    p_total   = user_data.get("phone_total", 0)
    e_total   = user_data.get("email_total", 0)
    d1        = "\u2501" * 30

    if is_admin(user.id):
        text = (
            d1 + "\n"
            "       👤 *Your Profile*\n" +
            d1 + "\n\n"
            "🆔 *ID:* `" + str(user.id) + "`\n"
            "👤 *Name:* " + str(user.first_name) + " " + str(user.last_name or "") + "\n"
            "📛 *Username:* @" + str(user.username or "N/A") + "\n"
            "🛡️ *Role:* Admin\n\n" +
            d1 + "\n"
            "📱 Phone : Unlimited\n"
            "📧 Email : Unlimited\n"
            "🔒 Limits: None\n\n" +
            d1 + "\n"
            "📱 Phone Searches : " + str(p_total) + "\n"
            "📧 Email Searches : " + str(e_total) + "\n"
            "🔍 Total          : " + str(total_s) + "\n"
        )
        await safe_edit(query, text, reply_markup=back_keyboard())
        return

    is_prem  = user_data.get("is_premium", False)
    plan_key = user_data.get("plan", "trial")
    plan     = PLANS.get(plan_key, PLANS["trial"])
    expiry   = user_data.get("expiry", "")
    p_free   = get_phone_free_remaining(user.id)
    e_free   = get_email_free_remaining(user.id)

    if is_prem and expiry:
        try:
            exp_date  = date.fromisoformat(expiry)
            days_left = (exp_date - date.today()).days
            if days_left >= 0:
                bar_len   = 20
                filled    = min(int((days_left / max(plan["days"], 1)) * bar_len), bar_len)
                bar       = make_bar(filled, bar_len)
                daily_rem = get_phone_daily_remaining(user.id)
                if plan.get("unlimited", False):
                    p_info = "💎 " + plan["name"] + " | Unlimited"
                else:
                    p_info = "💎 " + plan["name"] + " | " + str(daily_rem) + "/" + str(plan.get("daily_limit", 0)) + " today"
                plan_info = (
                    "📦 *Plan:* " + plan["name"] + "\n"
                    "📅 *Expiry:* " + expiry + "\n"
                    "⏳ *Days Left:* " + str(days_left) + "\n"
                    "📈 `[" + bar + "]`\n\n"
                    "📱 *Phone:* " + p_info + "\n"
                    "📧 *Email:* 💎 Unlimited\n"
                    "✅ *Dono access active!*"
                )
            else:
                plan_info = (
                    "⚠️ *Plan Expired!*\n"
                    "📱 Phone Trial: " + str(p_free) + "/" + str(PHONE_FREE_SEARCHES) + "\n"
                    "📧 Email Free: " + str(e_free) + "/" + str(EMAIL_FREE_SEARCHES)
                )
        except Exception:
            plan_info = "⚪ Unknown plan status"
    else:
        p_bar     = "🟢" * p_free + "🔴" * (PHONE_FREE_SEARCHES - p_free)
        e_bar     = "🟢" * e_free + "🔴" * (EMAIL_FREE_SEARCHES - e_free)
        plan_info = (
            "📦 *Plan:* Free/Trial\n\n"
            "📱 *Phone Trial:* " + p_bar + " (" + str(p_free) + "/" + str(PHONE_FREE_SEARCHES) + ")\n"
            "📧 *Email Free:*  " + e_bar + " (" + str(e_free) + "/" + str(EMAIL_FREE_SEARCHES) + ")\n\n"
            "💡 Ek plan lo — dono unlock!"
        )

    text = (
        d1 + "\n"
        "       👤 *Your Profile*\n" +
        d1 + "\n\n"
        "🆔 *ID:* `" + str(user.id) + "`\n"
        "👤 *Name:* " + str(user.first_name) + " " + str(user.last_name or "") + "\n"
        "📛 *Username:* @" + str(user.username or "N/A") + "\n\n" +
        d1 + "\n"
        "       🔐 *Account Info*\n" +
        d1 + "\n\n" +
        plan_info + "\n\n" +
        d1 + "\n"
        "📱 Phone Searches : " + str(p_total) + "\n"
        "📧 Email Searches : " + str(e_total) + "\n"
        "🔍 Total          : " + str(total_s) + "\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== STATUS ==================
async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    d1    = "\u2501" * 30
    d2    = "\u2501" * 25

    if is_admin(user.id):
        user_data = get_or_create_user(user.id)
        text = (
            d1 + "\n"
            "       🛡️ *Admin Status*\n" +
            d1 + "\n\n"
            "📱 *Phone* : Unlimited\n"
            "📧 *Email* : Unlimited\n"
            "🔒 Limits  : None\n\n"
            "🔍 Total: " + str(user_data.get("total_searches", 0)) + "\n\n"
            "✅ Full access!"
        )
        await safe_edit(query, text, reply_markup=back_keyboard())
        return

    p_ok, p_status, p_days, p_premium, p_plan_key = check_phone_access(user.id)
    e_ok, e_status, e_days, e_premium = check_email_access(user.id)
    plan = PLANS.get(p_plan_key, PLANS["trial"])

    if p_premium:
        daily_rem = get_phone_daily_remaining(user.id)
        if plan.get("unlimited", False):
            p_line = "💎 " + plan["name"] + " | Phone: Unlimited | " + str(p_days) + "d left"
        else:
            p_line = "💎 " + plan["name"] + " | Phone: " + str(daily_rem) + "/" + str(plan.get("daily_limit", 0)) + " | " + str(p_days) + "d left"
        e_line = "💎 Email: Unlimited | " + str(e_days) + "d left"
        note   = "✅ Dono access active hai!"
    else:
        p_free = get_phone_free_remaining(user.id)
        e_free = get_email_free_remaining(user.id)
        p_line = "🆓 Phone Trial: " + str(p_free) + "/" + str(PHONE_FREE_SEARCHES)
        e_line = "🆓 Email Free: " + str(e_free) + "/" + str(EMAIL_FREE_SEARCHES)
        note   = "💡 Ek plan lo — dono unlock!"

    text = (
        d1 + "\n"
        "       📊 *Account Status*\n" +
        d1 + "\n\n" +
        p_line + "\n" +
        e_line + "\n\n" +
        note + "\n\n" +
        d2 + "\n"
        "💰 Buy: " + OWNER_CONTACT + "\n"
        "Your ID: `" + str(user.id) + "`"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== HELP ==================
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    d1  = "\u2501" * 30
    d2  = "\u2501" * 25
    text = (
        d1 + "\n"
        "       ❓ *Help Guide*\n" +
        d1 + "\n\n"
        "🎯 *Ek Plan = Dono Access!*\n"
        "_(Phone + Email dono unlock)_\n\n" +
        d2 + "\n"
        "📋 *Plans:*\n" +
        d2 + "\n"
        "🥉 7 Days    Rs50  | Phone: 5/day  | Email: Unlimited\n"
        "🥈 30 Days   Rs130 | Phone: 10/day | Email: Unlimited\n"
        "🥇 6 Months  Rs300 | Phone: 15/day | Email: Unlimited\n"
        "💎 12 Months Rs799 | Phone: ∞      | Email: Unlimited\n\n" +
        d2 + "\n"
        "🆓 *Free Trial:*\n" +
        d2 + "\n"
        "📱 Phone: " + str(PHONE_FREE_SEARCHES) + " search\n"
        "📧 Email: " + str(EMAIL_FREE_SEARCHES) + " searches\n\n" +
        d2 + "\n"
        "📱 *Phone Tips:*\n" +
        d2 + "\n"
        "🇮🇳 India: 10 digit _(91 auto)_\n"
        "🌍 Other: Country code + number\n\n" +
        d2 + "\n"
        "📧 *Email Tips:*\n" +
        d2 + "\n"
        "Example: `user@gmail.com`\n\n" +
        d1 + "\n"
        "📦 Batch: Comma separated, Max 15\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== BUY ==================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user

    if is_admin(user.id):
        await safe_edit(
            query,
            "🛡️ *You are Admin!*\n\n"
            "✅ Unlimited access\n"
            "📱 Phone: ∞\n"
            "📧 Email: ∞\n\n"
            "No plan needed!",
            reply_markup=back_keyboard()
        )
        return

    d1   = "\u2501" * 30
    text = (
        d1 + "\n"
        "       💰 *Buy Plan*\n" +
        d1 + "\n\n"
        "🎯 *Ek Plan = Phone + Email Dono!*\n\n" +
        d1 + "\n\n"
        "🥉 *7 Days*    - Rs50\n"
        "   📱 Phone: 5/day\n"
        "   📧 Email: Unlimited\n\n"
        "🥈 *30 Days*   - Rs130\n"
        "   📱 Phone: 10/day\n"
        "   📧 Email: Unlimited\n\n"
        "🥇 *6 Months*  - Rs300\n"
        "   📱 Phone: 15/day\n"
        "   📧 Email: Unlimited\n\n"
        "💎 *12 Months* - Rs799\n"
        "   📱 Phone: Unlimited\n"
        "   📧 Email: Unlimited\n\n" +
        d1 + "\n\n"
        "📱 Contact: " + OWNER_CONTACT + "\n"
        "Your ID: `" + str(user.id) + "`\n"
        "_Admin ko ye ID bhejo_"
    )
    await safe_edit(query, text, reply_markup=buy_keyboard())


# ==================== PHONE SEARCH ====================
async def phone_single_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    ok, status, _, is_premium, plan_key = check_phone_access(user.id)

    if not ok:
        await safe_edit(
            query,
            "🔒 *Phone Search Locked!*\n\n" + status + "\n\n"
            "💰 " + OWNER_CONTACT + "\nYour ID: `" + str(user.id) + "`",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        free_left = get_phone_free_remaining(user.id)
        daily_rem = get_phone_daily_remaining(user.id)
        plan      = PLANS.get(plan_key, PLANS["trial"])
        if is_premium:
            info = "💎 Unlimited" if plan.get("unlimited") else "✅ " + str(daily_rem) + "/" + str(plan.get("daily_limit", 0)) + " today"
        else:
            info = "🆓 " + str(free_left) + "/" + str(PHONE_FREE_SEARCHES) + " trial"

    d2   = "\u2501" * 25
    await safe_edit(
        query,
        "📱 *Phone Single Search*\n\n"
        "📊 " + info + "\n\n" +
        d2 + "\n"
        "📍 Number kahan ka hai?\n" +
        d2 + "\n\n"
        "🇮🇳 India  10 digit (91 auto)\n"
        "🌍 Other   Country code + number",
        reply_markup=country_select_keyboard("single"),
    )
    return PHONE_COUNTRY_SINGLE

async def phone_batch_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    ok, status, _, is_premium, plan_key = check_phone_access(user.id)

    if not ok:
        await safe_edit(
            query,
            "🔒 *Phone Search Locked!*\n\n" + status + "\n\n💰 " + OWNER_CONTACT,
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        free_left = get_phone_free_remaining(user.id)
        daily_rem = get_phone_daily_remaining(user.id)
        plan      = PLANS.get(plan_key, PLANS["trial"])
        if is_premium:
            info = "💎 Unlimited" if plan.get("unlimited") else "✅ " + str(daily_rem) + "/" + str(plan.get("daily_limit", 0)) + " today"
        else:
            info = "🆓 " + str(free_left) + "/" + str(PHONE_FREE_SEARCHES) + " trial"

    d2   = "\u2501" * 25
    await safe_edit(
        query,
        "📦 *Phone Batch Search*\n\n"
        "📊 " + info + "\n\n" +
        d2 + "\n"
        "📍 Numbers kahan ke hain?\n" +
        d2 + "\n\n"
        "🇮🇳 India  10 digit each (91 auto)\n"
        "🌍 Other   Country code + number",
        reply_markup=country_select_keyboard("batch"),
    )
    return PHONE_COUNTRY_BATCH

async def country_selected_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data
    if "india" in data:
        context.user_data["phone_country"] = "india"
        await safe_edit(
            query,
            "🇮🇳 *Indian Number Search*\n\n"
            "📱 Sirf *10 digit* daalo:\n"
            "_(91 automatic add hoga)_\n\n"
            "✅ `9876543210`\n"
            "✅ `8123456789`\n\n"
            "❌ 91 mat lagao!\n\n"
            "/cancel to go back",
        )
        return PHONE_SINGLE_INDIA
    else:
        context.user_data["phone_country"] = "other"
        await safe_edit(
            query,
            "🌍 *Other Country Search*\n\n"
            "📱 Country code + Number:\n\n"
            "✅ USA: `14155552671`\n"
            "✅ UK:  `447911123456`\n"
            "✅ UAE: `971501234567`\n"
            "✅ PAK: `923001234567`\n\n"
            "⚠️ + mat lagao\n\n"
            "/cancel to go back",
        )
        return PHONE_SINGLE_OTHER

async def country_selected_batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data
    if "india" in data:
        context.user_data["phone_country"] = "india"
        await safe_edit(
            query,
            "🇮🇳 *Indian Batch Search*\n\n"
            "📱 10 digit numbers, comma se:\n\n"
            "✅ `9876543210,8123456789`\n\n"
            "⚠️ Max 15 | 91 mat lagao!\n\n"
            "/cancel to go back",
        )
        return PHONE_BATCH_INDIA
    else:
        context.user_data["phone_country"] = "other"
        await safe_edit(
            query,
            "🌍 *Other Country Batch*\n\n"
            "📱 Country code + number, comma se:\n\n"
            "✅ `14155552671,447911123456`\n\n"
            "⚠️ Max 15 | + mat lagao\n\n"
            "/cancel to go back",
        )
        return PHONE_BATCH_OTHER

async def phone_single_india(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw   = update.message.text.strip()
    user  = update.effective_user
    clean = raw.replace(" ", "").replace("-", "").replace("+", "")
    if not clean.isdigit():
        await update.message.reply_text("❌ Sirf numbers!\nExample: `9876543210`\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_SINGLE_INDIA
    if clean.startswith("91") and len(clean) == 12:
        clean = clean[2:]
    if len(clean) != 10:
        await update.message.reply_text("❌ 10 digit ka number!\nExample: `9876543210`\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_SINGLE_INDIA
    await _do_phone_single(update, context, "91" + clean, "🇮🇳 91" + clean)
    return ConversationHandler.END

async def phone_single_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw   = update.message.text.strip()
    clean = raw.replace(" ", "").replace("-", "").replace("+", "")
    if not clean.isdigit():
        await update.message.reply_text("❌ Sirf numbers!\nExample: `14155552671`\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_SINGLE_OTHER
    if not (7 <= len(clean) <= 15):
        await update.message.reply_text("❌ 7-15 digit hone chahiye!\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_SINGLE_OTHER
    await _do_phone_single(update, context, clean, "🌍 " + clean)
    return ConversationHandler.END

async def phone_batch_india(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw      = update.message.text.strip()
    raw_nums = [n.strip().replace(" ", "").replace("-", "").replace("+", "") for n in raw.split(",") if n.strip()]
    valid    = []
    invalid  = []
    for num in raw_nums:
        if num.startswith("91") and len(num) == 12:
            num = num[2:]
        if num.isdigit() and len(num) == 10:
            full = "91" + num
            if full not in valid:
                valid.append(full)
        else:
            invalid.append(num)
    if not valid:
        await update.message.reply_text("❌ Koi valid Indian number nahi!\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_BATCH_INDIA
    warning = ""
    if invalid:
        warning = "⚠️ Skip kiye " + str(len(invalid)) + ": `" + ", ".join(invalid[:3]) + "`\n"
    await _do_phone_batch(update, context, valid[:15], "india", warning)
    return ConversationHandler.END

async def phone_batch_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw      = update.message.text.strip()
    raw_nums = [n.strip().replace(" ", "").replace("-", "").replace("+", "") for n in raw.split(",") if n.strip()]
    valid    = []
    invalid  = []
    for num in raw_nums:
        if num.isdigit() and 7 <= len(num) <= 15:
            if num not in valid:
                valid.append(num)
        else:
            invalid.append(num)
    if not valid:
        await update.message.reply_text("❌ Koi valid number nahi!\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_BATCH_OTHER
    warning = ""
    if invalid:
        warning = "⚠️ Skip kiye " + str(len(invalid)) + ": `" + ", ".join(invalid[:3]) + "`\n"
    await _do_phone_batch(update, context, valid[:15], "other", warning)
    return ConversationHandler.END

async def _do_phone_single(update, context, number, display):
    user = update.effective_user
    ok, status, _, is_premium, plan_key = check_phone_access(user.id)
    if not ok:
        await update.message.reply_text(
            "🔒 *Locked!*\n" + status + "\n💰 " + OWNER_CONTACT,
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return
    msg    = await update.message.reply_text("🔍 Searching `" + display + "`...", parse_mode="Markdown")
    result = search_api(number)
    if result["ok"]:
        use_phone_search(user.id)
        text    = format_result(display, result["data"], "📱")
        divider = "\u2501" * 25
        if is_admin(user.id):
            text += "\n\n" + divider + "\n🛡️ Admin Search"
        elif is_premium:
            plan      = PLANS.get(plan_key, PLANS["trial"])
            daily_rem = get_phone_daily_remaining(user.id)
            if not plan.get("unlimited", False):
                text += "\n\n" + divider + "\n📊 Today: *" + str(daily_rem) + "/" + str(plan.get("daily_limit", 0)) + "*"
        else:
            free_left = get_phone_free_remaining(user.id)
            text += "\n\n" + divider + "\n🆓 Trial: *" + str(free_left) + "/" + str(PHONE_FREE_SEARCHES) + "*"
        await msg.edit_text(text, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    else:
        await msg.edit_text(
            "❌ *Search Failed*\n`" + str(result["error"]) + "`",
            reply_markup=back_keyboard(), parse_mode="Markdown"
        )

async def _do_phone_batch(update, context, numbers, country, warning=""):
    user  = update.effective_user
    ok, status, _, is_premium, plan_key = check_phone_access(user.id)
    plan  = PLANS.get(plan_key, PLANS["trial"])
    total = len(numbers)
    if is_admin(user.id):
        available = 999999
    elif plan.get("unlimited", False):
        available = 999999
    elif is_premium:
        available = get_phone_daily_remaining(user.id)
    else:
        available = get_phone_free_remaining(user.id)
    if total > available:
        await update.message.reply_text(
            "❌ *Searches kam hain!*\n\nNumbers: *" + str(total) + "* | Available: *" + str(available) + "*\n\n👉 " + OWNER_CONTACT,
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return
    if warning:
        await update.message.reply_text(warning, parse_mode="Markdown")
    flag = "🇮🇳" if country == "india" else "🌍"
    msg  = await update.message.reply_text(flag + " Processing " + str(total) + " numbers...\n[" + "░" * total + "]")
    for i, num in enumerate(numbers, 1):
        result   = search_api(num)
        progress = "█" * i + "░" * (total - i)
        display  = ("🇮🇳 " if country == "india" else "🌍 ") + num
        if result["ok"]:
            use_phone_search(user.id)
            text = format_result(display, result["data"], "📱")
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ *" + display + "*\n`" + str(result["error"]) + "`", parse_mode="Markdown")
        try:
            await msg.edit_text(flag + " Processing... (" + str(i) + "/" + str(total) + ")\n[" + progress + "]")
        except Exception:
            pass
    if is_admin(user.id):
        summary = "✅ *Batch Done!*\n📊 Processed: " + str(total) + "\n🛡️ Admin Search"
    elif is_premium and not plan.get("unlimited", False):
        daily_rem = get_phone_daily_remaining(user.id)
        summary   = "✅ *Batch Done!*\n📊 Processed: " + str(total) + "\n📊 Today Left: *" + str(daily_rem) + "/" + str(plan.get("daily_limit", 0)) + "*"
    elif not is_premium:
        free_left = get_phone_free_remaining(user.id)
        summary   = "✅ *Batch Done!*\n📊 Processed: " + str(total) + "\n🆓 Trial Left: *" + str(free_left) + "/" + str(PHONE_FREE_SEARCHES) + "*"
    else:
        summary = "✅ *Batch Done!*\n📊 Processed: " + str(total)
    await msg.edit_text(summary, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")


# ==================== EMAIL SEARCH ====================
async def email_single_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    ok, status, _, is_premium = check_email_access(user.id)
    if not ok:
        await safe_edit(
            query,
            "🔒 *Email Search Locked!*\n\n" + status + "\n\n💰 " + OWNER_CONTACT + "\nYour ID: `" + str(user.id) + "`",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END
    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        free_left = get_email_free_remaining(user.id)
        info      = "💎 Unlimited" if is_premium else "🆓 " + str(free_left) + "/" + str(EMAIL_FREE_SEARCHES) + " remaining"
    await safe_edit(
        query,
        "📧 *Email Single Search*\n\n"
        "📊 " + info + "\n\n"
        "📧 Email address daalo:\n"
        "_Example: user@gmail.com_\n\n"
        "/cancel to go back",
    )
    return EMAIL_SINGLE

async def email_single_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    user  = update.effective_user
    if not is_valid_email(email):
        await update.message.reply_text("❌ Invalid Email!\nExample: name@gmail.com\nTry again or /cancel")
        return EMAIL_SINGLE
    ok, status, _, is_premium = check_email_access(user.id)
    if not ok:
        await update.message.reply_text(
            "🔒 *Locked!*\n" + status + "\n💰 " + OWNER_CONTACT,
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END
    msg    = await update.message.reply_text("🔍 Searching...")
    result = search_api(email)
    if result["ok"]:
        use_email_search(user.id, is_premium)
        text    = format_result(email, result["data"], "📧")
        divider = "\u2501" * 25
        if is_admin(user.id):
            text += "\n\n" + divider + "\n🛡️ Admin Search"
        elif not is_premium:
            free_left = get_email_free_remaining(user.id)
            text += "\n\n" + divider + "\n🆓 Remaining: *" + str(free_left) + "/" + str(EMAIL_FREE_SEARCHES) + "*"
        await msg.edit_text(text, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    else:
        await msg.edit_text(
            "❌ *Search Failed*\n`" + str(result["error"]) + "`",
            reply_markup=back_keyboard(), parse_mode="Markdown"
        )
    return ConversationHandler.END

async def email_batch_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user
    ok, status, _, is_premium = check_email_access(user.id)
    if not ok:
        await safe_edit(
            query,
            "🔒 *Email Search Locked!*\n\n" + status + "\n\n💰 " + OWNER_CONTACT,
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END
    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        free_left = get_email_free_remaining(user.id)
        info = "💎 Unlimited" if is_premium else "🆓 " + str(free_left) + "/" + str(EMAIL_FREE_SEARCHES)
    await safe_edit(
        query,
        "📦 *Email Batch Search*\n\n"
        "📊 " + info + "\n\n"
        "📧 Emails comma se daalo:\n"
        "_a@gmail.com,b@yahoo.com_\n"
        "_Max 15 at once_\n\n"
        "/cancel to go back",
    )
    return EMAIL_BATCH

async def email_batch_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw  = update.message.text.strip()
    user = update.effective_user
    emails = []
    for item in raw.split(","):
        item = item.strip()
        if is_valid_email(item) and item not in emails:
            emails.append(item)
    if not emails:
        await update.message.reply_text("❌ No valid emails!\nTry again or /cancel")
        return EMAIL_BATCH
    emails    = emails[:15]
    total     = len(emails)
    ok, status, _, is_premium = check_email_access(user.id)
    if is_admin(user.id):
        available = 999999
    else:
        free_left = get_email_free_remaining(user.id)
        available = 999999 if is_premium else free_left
    if total > available:
        await update.message.reply_text(
            "❌ *Not enough searches!*\n\nEmails: *" + str(total) + "* | Available: *" + str(available) + "*\n\n👉 " + OWNER_CONTACT,
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END
    msg = await update.message.reply_text("🚀 Processing " + str(total) + " emails...\n[" + "░" * total + "]")
    for i, em in enumerate(emails, 1):
        result   = search_api(em)
        progress = "█" * i + "░" * (total - i)
        if result["ok"]:
            use_email_search(user.id, is_premium)
            text = format_result(em, result["data"], "📧")
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ *" + em + "*\n`" + str(result["error"]) + "`", parse_mode="Markdown")
        try:
            await msg.edit_text("🚀 Processing... (" + str(i) + "/" + str(total) + ")\n[" + progress + "]")
        except Exception:
            pass
    if is_admin(user.id):
        summary = "✅ *Batch Complete!*\n📊 Processed: " + str(total) + "\n🛡️ Admin"
    elif not is_premium:
        free_left = get_email_free_remaining(user.id)
        summary   = "✅ *Batch Complete!*\n📊 Processed: " + str(total) + "\n🆓 Remaining: *" + str(free_left) + "/" + str(EMAIL_FREE_SEARCHES) + "*"
    else:
        summary = "✅ *Batch Complete!*\n📊 Processed: " + str(total)
    await msg.edit_text(summary, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    return ConversationHandler.END


# ================== CANCEL ==================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled.", reply_markup=main_menu_keyboard(user.id))
    return ConversationHandler.END


# ==================== ADMIN PANEL ====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        if update.message:
            await update.message.reply_text("❌ Admin only!")
        return ConversationHandler.END
    users  = load_users()
    total  = len(users)
    prem   = sum(1 for u in users.values() if u.get("is_premium", False))
    trial  = total - prem
    d1     = "\u2501" * 30
    text = (
        d1 + "\n"
        "       🛠️ *Admin Panel*\n" +
        d1 + "\n\n"
        "🛡️ Admins     : " + str(len(ADMIN_IDS)) + "\n"
        "👥 Total Users : " + str(total) + "\n"
        "💎 Premium     : " + str(prem) + "\n"
        "🆓 Trial/Free  : " + str(trial) + "\n\n"
        "✅ *Ek plan = dono access*\n\n"
        "Choose action:"
    )
    if update.callback_query:
        await safe_edit(update.callback_query, text, reply_markup=admin_menu_keyboard())
    else:
        await update.message.reply_text(text, reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_panel(update, context)

async def admin_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(
        query,
        "➕ *Add Premium User*\n\n"
        "✅ Ek plan = Phone + Email dono!\n\n"
        "User ID daalo:\n\n"
        "/cancel to go back"
    )
    return ADMIN_ADD_ID

async def admin_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ Invalid ID!\n/cancel to stop")
        return ADMIN_ADD_ID
    context.user_data["admin_uid"] = uid
    await update.message.reply_text(
        "✅ User: `" + uid + "`\nPlan select karo:\n_(Phone + Email dono unlock hoga)_",
        reply_markup=plan_select_keyboard("plan"),
        parse_mode="Markdown"
    )
    return ADMIN_ADD_PLAN

async def admin_add_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_back":
        await admin_panel(update, context)
        return ConversationHandler.END
    plan_map = {
        "plan_7days"   : "7days",
        "plan_30days"  : "30days",
        "plan_6months" : "6months",
        "plan_12months": "12months",
    }
    plan_key   = plan_map.get(query.data, "7days")
    uid        = context.user_data.get("admin_uid")
    plan       = PLANS.get(plan_key)
    expiry     = upgrade_user(int(uid), plan_key)
    daily_info = "Unlimited" if plan["unlimited"] else str(plan["daily_limit"]) + "/day"
    await safe_edit(
        query,
        "✅ *Plan Added!*\n\n"
        "🆔 `" + str(uid) + "`\n"
        "📦 " + plan["name"] + "\n"
        "📅 Expiry: " + expiry + "\n\n"
        "📱 Phone: " + daily_info + "\n"
        "📧 Email: Unlimited\n\n"
        "✅ *Dono access unlock!*",
        reply_markup=admin_menu_keyboard()
    )
    return ConversationHandler.END

async def admin_remove_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "❌ *Remove User*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_REM_ID

async def admin_remove_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.message.text.strip()
    users = load_users()
    if uid in users:
        del users[uid]
        save_users(users)
        await update.message.reply_text("✅ `" + uid + "` removed!", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ `" + uid + "` not found!", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def admin_setplan_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(
        query,
        "📅 *Set User Plan*\n\n"
        "✅ Ek plan = Phone + Email dono!\n\n"
        "User ID daalo:\n\n"
        "/cancel to go back"
    )
    return ADMIN_EXP_ID

async def admin_setplan_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    context.user_data["admin_uid"] = uid
    await update.message.reply_text(
        "User: `" + uid + "`\nPlan select karo:\n_(Phone + Email dono unlock hoga)_",
        reply_markup=plan_select_keyboard("plan"),
        parse_mode="Markdown"
    )
    return ADMIN_EXP_PLAN

async def admin_setplan_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_back":
        await admin_panel(update, context)
        return ConversationHandler.END
    plan_map = {
        "plan_7days"   : "7days",
        "plan_30days"  : "30days",
        "plan_6months" : "6months",
        "plan_12months": "12months",
    }
    plan_key   = plan_map.get(query.data, "7days")
    uid        = context.user_data.get("admin_uid")
    plan       = PLANS.get(plan_key)
    expiry     = upgrade_user(int(uid), plan_key)
    daily_info = "Unlimited" if plan["unlimited"] else str(plan["daily_limit"]) + "/day"
    await safe_edit(
        query,
        "✅ *Plan Updated!*\n\n"
        "🆔 `" + str(uid) + "`\n"
        "📦 " + plan["name"] + "\n"
        "📅 Expiry: " + expiry + "\n\n"
        "📱 Phone: " + daily_info + "\n"
        "📧 Email: Unlimited\n\n"
        "✅ *Dono access unlock!*",
        reply_markup=admin_menu_keyboard()
    )
    return ConversationHandler.END

async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()
    users = load_users()
    if not users:
        await safe_edit(query, "📋 *No users yet!*", reply_markup=admin_menu_keyboard())
        return
    d1   = "\u2501" * 30
    text = d1 + "\n📋 *All Users (" + str(len(users)) + ")*\n" + d1 + "\n\n"
    for uid, info in users.items():
        is_prem = info.get("is_premium", False)
        plan_k  = info.get("plan", "trial")
        plan    = PLANS.get(plan_k, PLANS["trial"])
        total_s = info.get("total_searches", 0)
        expiry  = info.get("expiry", "")
        if int(uid) in ADMIN_IDS:
            badge  = " 🛡️"
            status = "∞ Admin"
        elif is_prem and expiry:
            try:
                ed = date.fromisoformat(expiry)
                if date.today() <= ed:
                    status = "💎" + plan["name"] + " " + str((ed - date.today()).days) + "d"
                else:
                    status = "🔴 Expired"
            except Exception:
                status = "⚪ N/A"
            badge = ""
        else:
            pf     = max(0, PHONE_FREE_SEARCHES - info.get("phone_free_used", 0))
            ef     = max(0, EMAIL_FREE_SEARCHES - info.get("email_free_used", 0))
            status = "🆓P:" + str(pf) + " E:" + str(ef)
            badge  = ""
        text += "`" + str(uid) + "`" + badge + " | " + status + " | 🔍" + str(total_s) + "\n"
    await safe_edit(query, text[:4000], reply_markup=admin_menu_keyboard())

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()
    users = load_users()
    total          = len(users)
    total_searches = 0
    active         = 0
    expired        = 0
    trial          = 0
    plan_counts    = {k: 0 for k in PLANS}
    for uid, info in users.items():
        total_searches += info.get("total_searches", 0)
        if int(uid) in ADMIN_IDS:
            continue
        if info.get("is_premium", False):
            try:
                exp = date.fromisoformat(info.get("expiry", "2000-01-01"))
                if date.today() <= exp:
                    active += 1
                    pk = info.get("plan", "trial")
                    plan_counts[pk] = plan_counts.get(pk, 0) + 1
                else:
                    expired += 1
            except Exception:
                expired += 1
        else:
            trial += 1
    d1  = "\u2501" * 30
    d2  = "\u2501" * 25
    text = (
        d1 + "\n"
        "       📊 *Bot Statistics*\n" +
        d1 + "\n\n"
        "👥 Total Users    : " + str(total) + "\n"
        "🔍 Total Searches : " + str(total_searches) + "\n"
        "🛡️ Admins (∞)     : " + str(len(ADMIN_IDS)) + "\n\n" +
        d2 + "\n"
        "✅ *Ek Plan = Phone + Email*\n" +
        d2 + "\n"
        "💎 Active Premium : " + str(active) + "\n"
        "🔴 Expired        : " + str(expired) + "\n"
        "🆓 Trial/Free     : " + str(trial) + "\n\n"
        "Plan Breakdown:\n"
        "  🥉 7D  : " + str(plan_counts.get("7days", 0)) + "\n"
        "  🥈 30D : " + str(plan_counts.get("30days", 0)) + "\n"
        "  🥇 6M  : " + str(plan_counts.get("6months", 0)) + "\n"
        "  💎 12M : " + str(plan_counts.get("12months", 0)) + "\n\n"
        "📅 " + str(date.today()) + "\n"
    )
    await safe_edit(query, text, reply_markup=admin_menu_keyboard())


# ==================== ✅ FREE MONITOR ====================
async def admin_free_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main free monitor menu"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()

    users = load_users()
    # Count free/trial users only (not premium, not admin)
    free_users = [
        (uid, info) for uid, info in users.items()
        if not info.get("is_premium", False) and int(uid) not in ADMIN_IDS
    ]

    p_has    = sum(1 for _, i in free_users if i.get("phone_free_used", 0) < PHONE_FREE_SEARCHES)
    p_done   = sum(1 for _, i in free_users if i.get("phone_free_used", 0) >= PHONE_FREE_SEARCHES)
    e_has    = sum(1 for _, i in free_users if i.get("email_free_used", 0) < EMAIL_FREE_SEARCHES)
    e_done   = sum(1 for _, i in free_users if i.get("email_free_used", 0) >= EMAIL_FREE_SEARCHES)

    d1  = "\u2501" * 30
    d2  = "\u2501" * 25
    text = (
        d1 + "\n"
        "   🆓 *Free / Trial Monitor*\n" +
        d1 + "\n\n"
        "👥 Total Free Users: " + str(len(free_users)) + "\n\n" +
        d2 + "\n"
        "📱 *Phone Trial Status*\n" +
        d2 + "\n"
        "🟢 Has searches  : " + str(p_has) + "\n"
        "🔴 All used up   : " + str(p_done) + "\n\n" +
        d2 + "\n"
        "📧 *Email Free Status*\n" +
        d2 + "\n"
        "🟢 Has searches  : " + str(e_has) + "\n"
        "🔴 All used up   : " + str(e_done) + "\n\n"
        "Choose filter below 👇"
    )
    await safe_edit(query, text, reply_markup=free_monitor_keyboard())


async def monitor_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all phone trial users with details"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()

    users      = load_users()
    d1         = "\u2501" * 30
    text       = d1 + "\n📱 *Phone Trial Users*\n" + d1 + "\n\n"
    text      += "Format: ID | Used/Total | Searches\n\n"

    count = 0
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS:
            continue
        if info.get("is_premium", False):
            continue

        p_used  = info.get("phone_free_used", 0)
        p_left  = max(0, PHONE_FREE_SEARCHES - p_used)
        total_s = info.get("total_searches", 0)
        added   = info.get("added", "N/A")

        if p_left > 0:
            icon = "🟢"
        else:
            icon = "🔴"

        # Progress bar
        bar = "🟢" * p_left + "🔴" * p_used

        text += (
            icon + " `" + str(uid) + "`\n"
            "   📱 Phone: " + bar + " (" + str(p_left) + "/" + str(PHONE_FREE_SEARCHES) + " left)\n"
            "   🔍 Total Searches: " + str(total_s) + "\n"
            "   📅 Joined: " + str(added) + "\n\n"
        )
        count += 1

    if count == 0:
        text += "_No trial users found_\n"

    text += d1 + "\nTotal: " + str(count) + " users"

    # Split if too long
    if len(text) > 4000:
        text = text[:3900] + "\n\n_...aur bhi hain (4000 char limit)_"

    await safe_edit(query, text, reply_markup=free_monitor_keyboard())


async def monitor_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all email free users with details"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()

    users = load_users()
    d1    = "\u2501" * 30
    text  = d1 + "\n📧 *Email Free Users*\n" + d1 + "\n\n"

    count = 0
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS:
            continue
        if info.get("is_premium", False):
            continue

        e_used  = info.get("email_free_used", 0)
        e_left  = max(0, EMAIL_FREE_SEARCHES - e_used)
        total_s = info.get("total_searches", 0)
        added   = info.get("added", "N/A")

        if e_left > 0:
            icon = "🟢"
        else:
            icon = "🔴"

        bar = "🟢" * e_left + "🔴" * e_used

        text += (
            icon + " `" + str(uid) + "`\n"
            "   📧 Email: " + bar + " (" + str(e_left) + "/" + str(EMAIL_FREE_SEARCHES) + " left)\n"
            "   🔍 Total Searches: " + str(total_s) + "\n"
            "   📅 Joined: " + str(added) + "\n\n"
        )
        count += 1

    if count == 0:
        text += "_No free email users found_\n"

    text += d1 + "\nTotal: " + str(count) + " users"

    if len(text) > 4000:
        text = text[:3900] + "\n\n_...aur bhi hain (4000 char limit)_"

    await safe_edit(query, text, reply_markup=free_monitor_keyboard())


async def monitor_exhausted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show users who have used ALL free searches - potential buyers"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()

    users = load_users()
    d1    = "\u2501" * 30
    text  = (
        d1 + "\n"
        "🔴 *All Searches Used Up*\n"
        "_(Potential buyers!)_\n" +
        d1 + "\n\n"
    )

    count = 0
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS:
            continue
        if info.get("is_premium", False):
            continue

        p_used = info.get("phone_free_used", 0)
        e_used = info.get("email_free_used", 0)
        p_left = max(0, PHONE_FREE_SEARCHES - p_used)
        e_left = max(0, EMAIL_FREE_SEARCHES - e_used)

        # Show only who has exhausted BOTH
        if p_left <= 0 and e_left <= 0:
            total_s = info.get("total_searches", 0)
            added   = info.get("added", "N/A")
            text += (
                "🔴 `" + str(uid) + "`\n"
                "   📱 Phone: 0/" + str(PHONE_FREE_SEARCHES) + " | "
                "📧 Email: 0/" + str(EMAIL_FREE_SEARCHES) + "\n"
                "   🔍 Total: " + str(total_s) + " | 📅 " + str(added) + "\n\n"
            )
            count += 1

    if count == 0:
        text += "_Koi nahi mila jo sab use kar chuka ho_\n"
    else:
        text += d1 + "\n"
        text += "💡 *" + str(count) + " users* plan le sakte hain!\n"
        text += "Contact: " + OWNER_CONTACT

    if len(text) > 4000:
        text = text[:3900] + "\n\n_...(4000 char limit)_"

    await safe_edit(query, text, reply_markup=free_monitor_keyboard())


async def monitor_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show users who still have free searches remaining"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()

    users = load_users()
    d1    = "\u2501" * 30
    text  = d1 + "\n🟢 *Active Free Users*\n_(Still has searches)_\n" + d1 + "\n\n"

    count = 0
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS:
            continue
        if info.get("is_premium", False):
            continue

        p_used = info.get("phone_free_used", 0)
        e_used = info.get("email_free_used", 0)
        p_left = max(0, PHONE_FREE_SEARCHES - p_used)
        e_left = max(0, EMAIL_FREE_SEARCHES - e_used)

        # Show only who still has at least one search left
        if p_left > 0 or e_left > 0:
            total_s = info.get("total_searches", 0)
            added   = info.get("added", "N/A")
            p_bar   = "🟢" * p_left + "🔴" * p_used
            e_bar   = "🟢" * e_left + "🔴" * e_used
            text += (
                "🟢 `" + str(uid) + "`\n"
                "   📱 " + p_bar + " (" + str(p_left) + "/" + str(PHONE_FREE_SEARCHES) + ")\n"
                "   📧 " + e_bar + " (" + str(e_left) + "/" + str(EMAIL_FREE_SEARCHES) + ")\n"
                "   🔍 " + str(total_s) + " searches | 📅 " + str(added) + "\n\n"
            )
            count += 1

    if count == 0:
        text += "_Koi active free user nahi hai_\n"

    text += d1 + "\nTotal Active: " + str(count) + " users"

    if len(text) > 4000:
        text = text[:3900] + "\n\n_...(4000 char limit)_"

    await safe_edit(query, text, reply_markup=free_monitor_keyboard())


async def monitor_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Full summary of all free/trial users"""
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()

    users = load_users()
    d1    = "\u2501" * 30
    d2    = "\u2501" * 25

    # ✅ Categorize all users
    total_users    = 0
    phone_active   = []   # has phone searches
    phone_done     = []   # phone exhausted
    email_active   = []   # has email searches
    email_done     = []   # email exhausted
    both_exhausted = []   # both done = potential buyers
    never_searched = []   # joined but never searched

    for uid, info in users.items():
        if int(uid) in ADMIN_IDS:
            continue
        if info.get("is_premium", False):
            continue

        total_users += 1
        p_used  = info.get("phone_free_used", 0)
        e_used  = info.get("email_free_used", 0)
        p_left  = max(0, PHONE_FREE_SEARCHES - p_used)
        e_left  = max(0, EMAIL_FREE_SEARCHES - e_used)
        total_s = info.get("total_searches", 0)

        if total_s == 0:
            never_searched.append(uid)
            continue

        if p_left > 0:
            phone_active.append(uid)
        else:
            phone_done.append(uid)

        if e_left > 0:
            email_active.append(uid)
        else:
            email_done.append(uid)

        if p_left <= 0 and e_left <= 0:
            both_exhausted.append(uid)

    text = (
        d1 + "\n"
        "   📊 *Free Users Full Summary*\n" +
        d1 + "\n\n"
        "👥 Total Free/Trial Users: " + str(total_users) + "\n\n" +

        d2 + "\n"
        "📱 *Phone Trial*\n" +
        d2 + "\n"
        "🟢 Has searches : " + str(len(phone_active)) + "\n"
        "🔴 All used     : " + str(len(phone_done)) + "\n\n" +

        d2 + "\n"
        "📧 *Email Free*\n" +
        d2 + "\n"
        "🟢 Has searches : " + str(len(email_active)) + "\n"
        "🔴 All used     : " + str(len(email_done)) + "\n\n" +

        d2 + "\n"
        "💡 *Insights*\n" +
        d2 + "\n"
        "🔴 Both exhausted : " + str(len(both_exhausted)) + " _(Buy karo!)_\n"
        "😴 Never searched : " + str(len(never_searched)) + "\n\n"
    )

    # ✅ List both_exhausted users (potential buyers)
    if both_exhausted:
        text += d2 + "\n"
        text += "🛒 *Potential Buyers (ID list):*\n"
        text += d2 + "\n"
        for uid in both_exhausted[:20]:  # Max 20
            text += "`" + str(uid) + "`\n"
        if len(both_exhausted) > 20:
            text += "_...aur " + str(len(both_exhausted) - 20) + " more_\n"
        text += "\n"

    # ✅ Never searched users
    if never_searched:
        text += d2 + "\n"
        text += "😴 *Never Searched (ID list):*\n"
        text += d2 + "\n"
        for uid in never_searched[:10]:  # Max 10
            text += "`" + str(uid) + "`\n"
        if len(never_searched) > 10:
            text += "_...aur " + str(len(never_searched) - 10) + " more_\n"

    text += "\n" + d1 + "\n📅 " + str(date.today())

    if len(text) > 4000:
        text = text[:3900] + "\n\n_...(4000 char limit)_"

    await safe_edit(query, text, reply_markup=free_monitor_keyboard())


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END


# ================== MAIN ==================
def main():
    request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0, pool_timeout=60.0)
    get_updates_request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0, pool_timeout=60.0)
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .get_updates_request(get_updates_request)
        .build()
    )

    phone_single_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(phone_single_start, pattern="^phone_single$")],
        states={
            PHONE_COUNTRY_SINGLE: [CallbackQueryHandler(country_selected_single, pattern="^country_(india|other)_single$")],
            PHONE_SINGLE_INDIA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_single_india)],
            PHONE_SINGLE_OTHER:   [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_single_other)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )
    phone_batch_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(phone_batch_start, pattern="^phone_batch$")],
        states={
            PHONE_COUNTRY_BATCH: [CallbackQueryHandler(country_selected_batch, pattern="^country_(india|other)_batch$")],
            PHONE_BATCH_INDIA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_batch_india)],
            PHONE_BATCH_OTHER:   [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_batch_other)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )
    email_single_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(email_single_start, pattern="^email_single$")],
        states={EMAIL_SINGLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_single_process)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )
    email_batch_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(email_batch_start, pattern="^email_batch$")],
        states={EMAIL_BATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_batch_process)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )
    admin_add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_start, pattern="^admin_add$")],
        states={
            ADMIN_ADD_ID:   [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_id)],
            ADMIN_ADD_PLAN: [CallbackQueryHandler(admin_add_plan, pattern="^plan_|^admin_back$")],
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
    admin_setplan_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_setplan_start, pattern="^admin_setplan$")],
        states={
            ADMIN_EXP_ID:   [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_setplan_id)],
            ADMIN_EXP_PLAN: [CallbackQueryHandler(admin_setplan_set, pattern="^plan_|^admin_back$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )

    for conv in [
        phone_single_conv, phone_batch_conv,
        email_single_conv, email_batch_conv,
        admin_add_conv, admin_remove_conv, admin_setplan_conv,
    ]:
        app.add_handler(conv)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))

    app.add_handler(CallbackQueryHandler(mode_phone,            pattern="^mode_phone$"))
    app.add_handler(CallbackQueryHandler(mode_email,            pattern="^mode_email$"))
    app.add_handler(CallbackQueryHandler(profile,               pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(status_check,          pattern="^status$"))
    app.add_handler(CallbackQueryHandler(help_menu,             pattern="^help$"))
    app.add_handler(CallbackQueryHandler(buy,                   pattern="^buy$"))
    app.add_handler(CallbackQueryHandler(admin_list,            pattern="^admin_list$"))
    app.add_handler(CallbackQueryHandler(admin_stats,           pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_back,            pattern="^admin_back$"))

    # ✅ Free Monitor handlers
    app.add_handler(CallbackQueryHandler(admin_free_monitor,    pattern="^admin_free_monitor$"))
    app.add_handler(CallbackQueryHandler(monitor_phone,         pattern="^monitor_phone$"))
    app.add_handler(CallbackQueryHandler(monitor_email,         pattern="^monitor_email$"))
    app.add_handler(CallbackQueryHandler(monitor_exhausted,     pattern="^monitor_exhausted$"))
    app.add_handler(CallbackQueryHandler(monitor_active,        pattern="^monitor_active$"))
    app.add_handler(CallbackQueryHandler(monitor_summary,       pattern="^monitor_summary$"))

    app.add_handler(CallbackQueryHandler(main_menu_callback,    pattern="^main_menu$"))

    print("🤖 Combined Bot Running!")
    print("🛡️  Admins    : " + str(ADMIN_IDS))
    print("✅ Ek Plan = Phone + Email dono!")
    print("📱 Phone Free: " + str(PHONE_FREE_SEARCHES))
    print("📧 Email Free: " + str(EMAIL_FREE_SEARCHES))
    print("🆓 Free Monitor: Added!")
    print("⏹  Ctrl+C to stop\n")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )

if __name__ == "__main__":
    main()

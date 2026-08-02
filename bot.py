#!/usr/bin/env python3
"""
🔍 Phone & Email Intelligence Bot
Combined Bot - Phone + Email Search
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
ADMIN_IDS     = [5057489358, 1968142314]
DEFAULT_PIN   = "912036"
API_URL       = "https://lk-api-pinsstm.ramaxinfo.workers.dev/"
DATA_FILE     = Path("users.json")
OWNER_CONTACT = "@theplayerror"

# ================== FREE SEARCHES ==================
PHONE_FREE_SEARCHES = 1
EMAIL_FREE_SEARCHES = 3

# ================== PLANS (Phone) ==================
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

# ================== CONVERSATION STATES ==================
PHONE_COUNTRY_SINGLE   = 10
PHONE_COUNTRY_BATCH    = 11
PHONE_SINGLE_INDIA     = 12
PHONE_SINGLE_OTHER     = 13
PHONE_BATCH_INDIA      = 14
PHONE_BATCH_OTHER      = 15
EMAIL_SINGLE           = 20
EMAIL_BATCH            = 21
ADMIN_ADD_ID           = 30
ADMIN_ADD_PLAN         = 31
ADMIN_REM_ID           = 32
ADMIN_EXP_ID           = 33
ADMIN_EXP_PLAN         = 34
ADMIN_EMAIL_ADD_ID     = 40
ADMIN_EMAIL_ADD_EXP    = 41
ADMIN_EMAIL_REM_ID     = 42
ADMIN_EMAIL_EXP_ID     = 43
ADMIN_EMAIL_EXP_DATE   = 44


# ================== ADMIN CHECK ==================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


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
            "phone_plan"          : "trial",
            "phone_expiry"        : "",
            "phone_is_premium"    : False,
            "phone_free_used"     : 0,
            "phone_daily_searches": 0,
            "phone_last_date"     : "",
            "phone_total"         : 0,
            "email_expiry"        : "",
            "email_is_premium"    : False,
            "email_free_used"     : 0,
            "email_total"         : 0,
            "added"               : date.today().isoformat(),
            "total_searches"      : 0,
        }
        save_users(users)
    return users[uid]


# ==================== PHONE DATA ====================
def get_phone_free_remaining(user_id: int) -> int:
    # ✅ Admin = unlimited
    if is_admin(user_id):
        return 999999
    user_data = get_or_create_user(user_id)
    used      = user_data.get("phone_free_used", 0)
    return max(0, PHONE_FREE_SEARCHES - used)

def get_phone_daily_remaining(user_id: int) -> int:
    # ✅ Admin = unlimited
    if is_admin(user_id):
        return 999999

    users     = load_users()
    uid       = str(user_id)
    user_data = users.get(uid, {})
    plan_key  = user_data.get("phone_plan", "trial")
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

    plan_key = user_data.get("phone_plan", "trial")
    plan     = PLANS.get(plan_key, PLANS["trial"])

    # ✅ Admin searches counted but no limits
    if is_admin(user_id):
        pass  # No deductions for admin
    elif plan.get("is_free", True):
        user_data["phone_free_used"] = user_data.get("phone_free_used", 0) + 1
    else:
        user_data["phone_daily_searches"] = user_data.get("phone_daily_searches", 0) + 1

    user_data["phone_total"]    = user_data.get("phone_total", 0) + 1
    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    users[uid] = user_data
    save_users(users)

def check_phone_access(user_id: int):
    # ✅ Admin = always unlimited access
    if is_admin(user_id):
        return True, "🛡️ Admin — Unlimited Access", 9999, True, "12months"

    get_or_create_user(user_id)
    users      = load_users()
    uid        = str(user_id)
    user_data  = users[uid]
    plan_key   = user_data.get("phone_plan", "trial")
    plan       = PLANS.get(plan_key, PLANS["trial"])
    expiry_str = user_data.get("phone_expiry", "")

    if not plan.get("is_free", True) and expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                free_left = get_phone_free_remaining(user_id)
                if free_left > 0:
                    return True, "⚠️ Plan expired | 🆓 1 free left", 0, False, "trial"
                return False, "❌ Plan expired! Renew karo.", 0, False, "trial"

            days_left    = (expiry - date.today()).days
            daily_rem    = get_phone_daily_remaining(user_id)
            daily_limit  = plan.get("daily_limit", 0)
            is_unlimited = plan.get("unlimited", False)

            if is_unlimited:
                return True, f"✅ {plan['name']} | Unlimited | {days_left}d left", days_left, True, plan_key
            else:
                if daily_rem <= 0:
                    return False, f"❌ Daily limit khatam! ({daily_limit}/day)", days_left, True, plan_key
                return True, f"✅ {plan['name']} | {daily_rem}/{daily_limit} today | {days_left}d left", days_left, True, plan_key
        except:
            pass

    free_left = get_phone_free_remaining(user_id)
    if free_left > 0:
        return True, f"🆓 Trial ({free_left}/{PHONE_FREE_SEARCHES} left)", 0, False, "trial"
    return False, "❌ Trial khatam! Plan lo.", 0, False, "trial"

def upgrade_phone_user(user_id: int, plan_key: str):
    users     = load_users()
    uid       = str(user_id)
    user_data = get_or_create_user(user_id)
    plan      = PLANS.get(plan_key, PLANS["7days"])
    expiry    = (date.today() + timedelta(days=plan["days"])).isoformat()

    user_data["phone_plan"]           = plan_key
    user_data["phone_expiry"]         = expiry
    user_data["phone_is_premium"]     = True
    user_data["phone_daily_searches"] = 0
    user_data["phone_last_date"]      = ""
    users[uid] = user_data
    save_users(users)
    return expiry


# ==================== EMAIL DATA ====================
def get_email_free_remaining(user_id: int) -> int:
    # ✅ Admin = unlimited
    if is_admin(user_id):
        return 999999
    user_data = get_or_create_user(user_id)
    used      = user_data.get("email_free_used", 0)
    return max(0, EMAIL_FREE_SEARCHES - used)

def use_email_search(user_id: int, is_premium: bool):
    users     = load_users()
    uid       = str(user_id)
    user_data = users.get(uid, {})

    # ✅ Admin - no deductions
    if not is_admin(user_id):
        if not is_premium:
            user_data["email_free_used"] = user_data.get("email_free_used", 0) + 1

    user_data["email_total"]    = user_data.get("email_total", 0) + 1
    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    users[uid] = user_data
    save_users(users)

def check_email_access(user_id: int):
    # ✅ Admin = always unlimited access
    if is_admin(user_id):
        return True, "🛡️ Admin — Unlimited Access", 9999, True

    get_or_create_user(user_id)
    users      = load_users()
    uid        = str(user_id)
    user_data  = users[uid]
    is_premium = user_data.get("email_is_premium", False)
    expiry_str = user_data.get("email_expiry", "")

    if is_premium and expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                free_left = get_email_free_remaining(user_id)
                if free_left > 0:
                    return True, f"⚠️ Premium expired | 🆓 {free_left} free left", 0, False
                return False, "❌ Premium expired & no free searches left", 0, False
            days = (expiry - date.today()).days
            return True, f"✅ Premium ({days} days left)", days, True
        except:
            pass

    free_left = get_email_free_remaining(user_id)
    if free_left > 0:
        return True, f"🆓 Free ({free_left}/{EMAIL_FREE_SEARCHES} searches left)", 0, False
    return False, "❌ Free searches khatam! Buy subscription.", 0, False

def upgrade_email_user(user_id: int, days: int):
    users     = load_users()
    uid       = str(user_id)
    user_data = get_or_create_user(user_id)
    expiry    = (date.today() + timedelta(days=days)).isoformat()
    user_data["email_expiry"]     = expiry
    user_data["email_is_premium"] = True
    users[uid] = user_data
    save_users(users)
    return expiry


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

def format_result(term: str, data, icon: str = "🔍"):
    if not data:
        return f"{icon} *{term}*\n_No data found_"
    if isinstance(data, list):
        if not data:
            return f"{icon} *{term}*\n_No data found_"
        if isinstance(data[0], dict):
            data = {"data": {"source": {"records": data}}}
        else:
            return f"{icon} *{term}*\n`{str(data[0])}`"
    if not isinstance(data, dict):
        return f"{icon} *{term}*\n`{str(data)}`"

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
        return f"{icon} *{term}*\n_No data found_"

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

    output = [
        f"{icon} *Result for* `{term}`",
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


# ================== KEYBOARDS ==================
def main_menu_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Phone Search", callback_data="mode_phone"),
            InlineKeyboardButton("📧 Email Search", callback_data="mode_email"),
        ],
        [
            InlineKeyboardButton("👤 My Profile",   callback_data="profile"),
            InlineKeyboardButton("📊 Status",       callback_data="status"),
        ],
        [
            InlineKeyboardButton("💰 Buy Plans",    callback_data="buy"),
            InlineKeyboardButton("❓ Help",          callback_data="help"),
        ],
    ])

def phone_menu_keyboard(user_id: int):
    # ✅ Admin always shows unlimited
    if is_admin(user_id):
        single_label = "🔍 Single (∞ Admin)"
        batch_label  = "📦 Batch (∞ Admin)"
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
                single_label = f"🔍 Single ({daily_rem} today)"
                batch_label  = f"📦 Batch ({daily_rem} today)"
        elif free_left > 0:
            single_label = f"🔍 Single ({free_left} trial)"
            batch_label  = f"📦 Batch ({free_left} trial)"
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
    # ✅ Admin always shows unlimited
    if is_admin(user_id):
        single_label = "🔍 Single (∞ Admin)"
        batch_label  = "📦 Batch (∞ Admin)"
    else:
        ok, _, _, is_premium = check_email_access(user_id)
        free_left = get_email_free_remaining(user_id)

        if is_premium:
            single_label = "🔍 Single Search"
            batch_label  = "📦 Batch Search"
        elif free_left > 0:
            single_label = f"🔍 Single ({free_left} free)"
            batch_label  = f"📦 Batch ({free_left} free)"
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
        [
            InlineKeyboardButton(
                "🇮🇳 Indian Number (+91)",
                callback_data=f"country_india_{mode}"
            ),
        ],
        [
            InlineKeyboardButton(
                "🌍 Other Country (Manual Code)",
                callback_data=f"country_other_{mode}"
            ),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="main_menu")],
    ])

def admin_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Phone Admin", callback_data="admin_phone"),
            InlineKeyboardButton("📧 Email Admin", callback_data="admin_email"),
        ],
        [
            InlineKeyboardButton("📋 All Users",   callback_data="admin_list"),
            InlineKeyboardButton("📊 Stats",       callback_data="admin_stats"),
        ],
        [InlineKeyboardButton("🔙 Main Menu",      callback_data="main_menu")],
    ])

def phone_admin_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Phone User",  callback_data="admin_phone_add"),
            InlineKeyboardButton("❌ Remove User",     callback_data="admin_phone_remove"),
        ],
        [InlineKeyboardButton("📅 Set Phone Plan",     callback_data="admin_phone_expiry")],
        [InlineKeyboardButton("🔙 Admin Menu",         callback_data="admin_back")],
    ])

def email_admin_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Email User",   callback_data="admin_email_add"),
            InlineKeyboardButton("❌ Remove User",      callback_data="admin_email_remove"),
        ],
        [InlineKeyboardButton("📅 Set Email Expiry",    callback_data="admin_email_expiry")],
        [InlineKeyboardButton("🔙 Admin Menu",          callback_data="admin_back")],
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
        ],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ])

def phone_plan_keyboard(prefix: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🥉 7 Days  - ₹50",    callback_data=f"{prefix}_7days"),
            InlineKeyboardButton("🥈 30 Days - ₹130",   callback_data=f"{prefix}_30days"),
        ],
        [
            InlineKeyboardButton("🥇 6 Months - ₹300",  callback_data=f"{prefix}_6months"),
            InlineKeyboardButton("💎 12 Months - ₹799", callback_data=f"{prefix}_12months"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_back")],
    ])

def email_duration_keyboard(prefix: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("7 Days",   callback_data=f"{prefix}_7"),
            InlineKeyboardButton("30 Days",  callback_data=f"{prefix}_30"),
        ],
        [
            InlineKeyboardButton("90 Days",  callback_data=f"{prefix}_90"),
            InlineKeyboardButton("365 Days", callback_data=f"{prefix}_365"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_back")],
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


# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id)

    # ✅ Admin special welcome
    if is_admin(user.id):
        text = (
            f"{'━' * 30}\n"
            f"   🔍 *Phone & Email Lookup Bot*\n"
            f"{'━' * 30}\n\n"
            f"👋 Welcome *{user.first_name}*!\n"
            f"🛡️ *Admin — Unlimited Access*\n\n"
            f"{'━' * 25}\n"
            f"📱 *Phone Search* : ∞ Unlimited\n"
            f"📧 *Email Search* : ∞ Unlimited\n"
            f"🔒 *Restrictions* : None\n"
            f"{'━' * 25}\n\n"
            f"Choose search type below 👇"
        )
    else:
        p_ok, p_status, p_days, p_premium, p_plan = check_phone_access(user.id)
        p_free = get_phone_free_remaining(user.id)
        e_ok, e_status, e_days, e_premium = check_email_access(user.id)
        e_free = get_email_free_remaining(user.id)

        text = (
            f"{'━' * 30}\n"
            f"   🔍 *Phone & Email Lookup Bot*\n"
            f"{'━' * 30}\n\n"
            f"👋 Welcome *{user.first_name}*!\n\n"
            f"{'━' * 25}\n"
            f"📱 *Phone Search*\n"
            f"{'━' * 25}\n"
        )

        if p_premium:
            plan  = PLANS.get(p_plan, PLANS["trial"])
            text += f"💎 {plan['name']} | {p_days}d left\n"
        else:
            p_bar = "🟢" * p_free + "🔴" * (PHONE_FREE_SEARCHES - p_free)
            text += f"🆓 Trial: {p_bar} ({p_free}/{PHONE_FREE_SEARCHES})\n"

        text += (
            f"\n{'━' * 25}\n"
            f"📧 *Email Search*\n"
            f"{'━' * 25}\n"
        )

        if e_premium:
            text += f"💎 Premium | {e_days}d left\n"
        else:
            e_bar = "🟢" * e_free + "🔴" * (EMAIL_FREE_SEARCHES - e_free)
            text += f"🆓 Free: {e_bar} ({e_free}/{EMAIL_FREE_SEARCHES})\n"

        text += f"\n{'━' * 30}\n\nChoose search type below 👇"

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
    user = query.from_user

    # ✅ Admin info
    if is_admin(user.id):
        info = "🛡️ Admin — ∞ Unlimited"
    else:
        ok, status, days, is_premium, plan_key = check_phone_access(user.id)
        free_left = get_phone_free_remaining(user.id)
        daily_rem = get_phone_daily_remaining(user.id)
        plan      = PLANS.get(plan_key, PLANS["trial"])

        if is_premium:
            info = "💎 Unlimited" if plan.get("unlimited") else f"✅ {daily_rem}/{plan.get('daily_limit',0)} today"
        else:
            info = f"🆓 {free_left}/{PHONE_FREE_SEARCHES} trial"

    text = (
        f"{'━' * 30}\n"
        f"   📱 *Phone Number Search*\n"
        f"{'━' * 30}\n\n"
        f"📊 Status: {info}\n\n"
        f"Single ya Batch search choose karo:"
    )
    await safe_edit(query, text, reply_markup=phone_menu_keyboard(user.id))

async def mode_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    # ✅ Admin info
    if is_admin(user.id):
        info = "🛡️ Admin — ∞ Unlimited"
    else:
        ok, status, days, is_premium = check_email_access(user.id)
        free_left = get_email_free_remaining(user.id)
        info = f"💎 Premium | {days}d left" if is_premium else f"🆓 {free_left}/{EMAIL_FREE_SEARCHES} free"

    text = (
        f"{'━' * 30}\n"
        f"   📧 *Email Search*\n"
        f"{'━' * 30}\n\n"
        f"📊 Status: {info}\n\n"
        f"Single ya Batch search choose karo:"
    )
    await safe_edit(query, text, reply_markup=email_menu_keyboard(user.id))


# ================== PROFILE ==================
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    user_data = get_or_create_user(user.id)
    total_s   = user_data.get("total_searches", 0)
    p_total   = user_data.get("phone_total", 0)
    e_total   = user_data.get("email_total", 0)

    # ✅ Admin profile special
    if is_admin(user.id):
        text = (
            f"{'━' * 30}\n"
            f"       👤 *Your Profile*\n"
            f"{'━' * 30}\n\n"
            f"🆔 *ID:* `{user.id}`\n"
            f"👤 *Name:* {user.first_name} {user.last_name or ''}\n"
            f"📛 *Username:* @{user.username or 'N/A'}\n"
            f"🛡️ *Role:* Admin\n\n"
            f"{'━' * 30}\n"
            f"📱 *Phone* : ∞ Unlimited (No expiry)\n"
            f"📧 *Email* : ∞ Unlimited (No expiry)\n"
            f"🔒 *Limits*: None\n\n"
            f"{'━' * 30}\n"
            f"📱 Phone Searches : {p_total}\n"
            f"📧 Email Searches : {e_total}\n"
            f"🔍 Total Searches : {total_s}\n"
        )
        await safe_edit(query, text, reply_markup=back_keyboard())
        return

    p_ok, p_status, p_days, p_premium, p_plan_key = check_phone_access(user.id)
    p_free  = get_phone_free_remaining(user.id)
    p_daily = get_phone_daily_remaining(user.id)
    p_plan  = PLANS.get(p_plan_key, PLANS["trial"])

    e_ok, e_status, e_days, e_premium = check_email_access(user.id)
    e_free = get_email_free_remaining(user.id)

    if p_premium:
        p_bar_len = 20
        p_filled  = min(int((p_days / max(p_plan["days"], 1)) * p_bar_len), p_bar_len)
        p_bar     = "█" * p_filled + "░" * (p_bar_len - p_filled)
        if p_plan.get("unlimited", False):
            p_info = f"💎 {p_plan['name']}\n   📅 {user_data.get('phone_expiry','N/A')} | ∞\n   `[{p_bar}]`"
        else:
            p_info = f"💎 {p_plan['name']}\n   📅 {user_data.get('phone_expiry','N/A')} | {p_daily}/{p_plan.get('daily_limit',0)} today\n   `[{p_bar}]`"
    else:
        p_bar  = "🟢" * p_free + "🔴" * (PHONE_FREE_SEARCHES - p_free)
        p_info = f"🆓 Trial {p_bar} ({p_free}/{PHONE_FREE_SEARCHES})"

    if e_premium:
        e_bar_len = 20
        e_filled  = min(int((e_days / 365) * e_bar_len), e_bar_len)
        e_bar     = "█" * e_filled + "░" * (e_bar_len - e_filled)
        e_info    = f"💎 Premium\n   📅 {user_data.get('email_expiry','N/A')} | {e_days}d left\n   `[{e_bar}]`"
    else:
        e_bar  = "🟢" * e_free + "🔴" * (EMAIL_FREE_SEARCHES - e_free)
        e_info = f"🆓 Free {e_bar} ({e_free}/{EMAIL_FREE_SEARCHES})"

    text = (
        f"{'━' * 30}\n"
        f"       👤 *Your Profile*\n"
        f"{'━' * 30}\n\n"
        f"🆔 *ID:* `{user.id}`\n"
        f"👤 *Name:* {user.first_name} {user.last_name or ''}\n"
        f"📛 *Username:* @{user.username or 'N/A'}\n\n"
        f"{'━' * 30}\n"
        f"📱 *Phone Account*\n"
        f"{'━' * 30}\n\n"
        f"{p_info}\n"
        f"🔍 Phone Searches: {p_total}\n\n"
        f"{'━' * 30}\n"
        f"📧 *Email Account*\n"
        f"{'━' * 30}\n\n"
        f"{e_info}\n"
        f"🔍 Email Searches: {e_total}\n\n"
        f"{'━' * 30}\n"
        f"🔍 *Total Searches:* {total_s}\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== STATUS ==================
async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    # ✅ Admin status
    if is_admin(user.id):
        user_data = get_or_create_user(user.id)
        text = (
            f"{'━' * 30}\n"
            f"       🛡️ *Admin Status*\n"
            f"{'━' * 30}\n\n"
            f"📱 *Phone Search*\n"
            f"   ∞ Unlimited — No restrictions\n\n"
            f"📧 *Email Search*\n"
            f"   ∞ Unlimited — No restrictions\n\n"
            f"🔍 Total Searches: {user_data.get('total_searches', 0)}\n\n"
            f"✅ Full access to everything!"
        )
        await safe_edit(query, text, reply_markup=back_keyboard())
        return

    p_ok, p_status, p_days, p_premium, p_plan_key = check_phone_access(user.id)
    p_free  = get_phone_free_remaining(user.id)
    p_daily = get_phone_daily_remaining(user.id)
    p_plan  = PLANS.get(p_plan_key, PLANS["trial"])

    e_ok, e_status, e_days, e_premium = check_email_access(user.id)
    e_free = get_email_free_remaining(user.id)

    text = (
        f"{'━' * 30}\n"
        f"       📊 *Account Status*\n"
        f"{'━' * 30}\n\n"
        f"📱 *Phone Search*\n"
        f"{'━' * 25}\n"
        f"{p_status}\n\n"
        f"📧 *Email Search*\n"
        f"{'━' * 25}\n"
        f"{e_status}\n\n"
        f"{'━' * 30}\n"
        f"💡 Buy Plan: {OWNER_CONTACT}\n"
        f"Your ID: `{user.id}`"
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
        f"📱 *Phone Search*\n"
        f"{'━' * 25}\n"
        f"🆓 Trial: {PHONE_FREE_SEARCHES} search\n\n"
        f"📋 Plans:\n"
        f"  🥉 7D  → ₹50  → 5/day\n"
        f"  🥈 30D → ₹130 → 10/day\n"
        f"  🥇 6M  → ₹300 → 15/day\n"
        f"  💎 12M → ₹799 → Unlimited\n\n"
        f"🇮🇳 India: Sirf 10 digit\n"
        f"   _(91 auto add)_\n"
        f"🌍 Other: Country code + number\n\n"
        f"{'━' * 25}\n"
        f"📧 *Email Search*\n"
        f"{'━' * 25}\n"
        f"🆓 Free: {EMAIL_FREE_SEARCHES} searches\n"
        f"💎 Premium: Unlimited\n\n"
        f"Example: `user@gmail.com`\n\n"
        f"{'━' * 30}\n"
        f"📦 *Batch*: Comma separated\n"
        f"⚠️ Max 15 per batch\n"
        f"⚠️ Each = 1 search\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== BUY ==================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user  = query.from_user

    # ✅ Admin already has everything
    if is_admin(user.id):
        await safe_edit(
            query,
            f"🛡️ *You are Admin!*\n\n"
            f"✅ You already have unlimited access\n"
            f"📱 Phone: ∞ Unlimited\n"
            f"📧 Email: ∞ Unlimited\n\n"
            f"No plan needed! 😎",
            reply_markup=back_keyboard()
        )
        return

    p_free = get_phone_free_remaining(user.id)
    e_free = get_email_free_remaining(user.id)

    text = (
        f"{'━' * 30}\n"
        f"       💰 *Buy Plans*\n"
        f"{'━' * 30}\n\n"
        f"📱 *Phone Plans:*\n\n"
        f"🥉 *7 Days*    → ₹50  | 5/day\n"
        f"🥈 *30 Days*   → ₹130 | 10/day\n"
        f"🥇 *6 Months*  → ₹300 | 15/day\n"
        f"💎 *12 Months* → ₹799 | Unlimited\n\n"
        f"{'━' * 30}\n\n"
        f"📧 *Email Plans:*\n\n"
        f"🥉 *7 Days*    → ₹50\n"
        f"🥈 *30 Days*   → ₹150\n"
        f"🥇 *90 Days*   → ₹300\n"
        f"💎 *365 Days*  → ₹999\n\n"
        f"{'━' * 30}\n\n"
        f"📱 Contact: {OWNER_CONTACT}\n"
        f"Your ID: `{user.id}`\n"
        f"_Admin ko ye ID bhejo_"
    )
    await safe_edit(query, text, reply_markup=buy_keyboard())


# ==================== PHONE SEARCH ====================
async def phone_single_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    ok, status, _, is_premium, plan_key = check_phone_access(user.id)
    if not ok:
        await safe_edit(
            query,
            f"🔒 *Phone Search Locked!*\n\n{status}\n\n"
            f"💰 {OWNER_CONTACT}\nYour ID: `{user.id}`",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    # ✅ Admin info
    if is_admin(user.id):
        info = "🛡️ Admin — ∞ Unlimited"
    else:
        free_left = get_phone_free_remaining(user.id)
        daily_rem = get_phone_daily_remaining(user.id)
        plan      = PLANS.get(plan_key, PLANS["trial"])
        if is_premium:
            info = "💎 Unlimited" if plan.get("unlimited") else f"✅ {daily_rem}/{plan.get('daily_limit',0)} today"
        else:
            info = f"🆓 {free_left}/{PHONE_FREE_SEARCHES} trial"

    await safe_edit(
        query,
        f"📱 *Phone Single Search*\n\n"
        f"📊 {info}\n\n"
        f"{'━' * 25}\n"
        f"📍 Number kahan ka hai?\n"
        f"{'━' * 25}\n\n"
        f"🇮🇳 India → 10 digit (91 auto)\n"
        f"🌍 Other  → Country code + number",
        reply_markup=country_select_keyboard("single"),
    )
    return PHONE_COUNTRY_SINGLE

async def phone_batch_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    ok, status, _, is_premium, plan_key = check_phone_access(user.id)
    if not ok:
        await safe_edit(
            query,
            f"🔒 *Phone Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    if is_admin(user.id):
        info = "🛡️ Admin — ∞ Unlimited"
    else:
        free_left = get_phone_free_remaining(user.id)
        daily_rem = get_phone_daily_remaining(user.id)
        plan      = PLANS.get(plan_key, PLANS["trial"])
        if is_premium:
            info = "💎 Unlimited" if plan.get("unlimited") else f"✅ {daily_rem}/{plan.get('daily_limit',0)} today"
        else:
            info = f"🆓 {free_left}/{PHONE_FREE_SEARCHES} trial"

    await safe_edit(
        query,
        f"📦 *Phone Batch Search*\n\n"
        f"📊 {info}\n\n"
        f"{'━' * 25}\n"
        f"📍 Numbers kahan ke hain?\n"
        f"{'━' * 25}\n\n"
        f"🇮🇳 India → 10 digit each (91 auto)\n"
        f"🌍 Other  → Country code + number",
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
            f"🇮🇳 *Indian Number Search*\n\n"
            f"📱 Sirf *10 digit* daalo:\n"
            f"_(91 automatic add hoga)_\n\n"
            f"✅ `9876543210`\n"
            f"✅ `8123456789`\n\n"
            f"❌ 91 mat lagao!\n\n"
            f"/cancel to go back",
        )
        return PHONE_SINGLE_INDIA
    else:
        context.user_data["phone_country"] = "other"
        await safe_edit(
            query,
            f"🌍 *Other Country Search*\n\n"
            f"📱 Country code + Number:\n\n"
            f"✅ USA:  `14155552671`\n"
            f"✅ UK:   `447911123456`\n"
            f"✅ UAE:  `971501234567`\n"
            f"✅ PAK:  `923001234567`\n\n"
            f"⚠️ + mat lagao\n\n"
            f"/cancel to go back",
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
            f"🇮🇳 *Indian Batch Search*\n\n"
            f"📱 10 digit numbers, comma se:\n\n"
            f"✅ `9876543210,8123456789`\n\n"
            f"⚠️ Max 15 | 91 mat lagao!\n\n"
            f"/cancel to go back",
        )
        return PHONE_BATCH_INDIA
    else:
        context.user_data["phone_country"] = "other"
        await safe_edit(
            query,
            f"🌍 *Other Country Batch*\n\n"
            f"📱 Country code + number, comma se:\n\n"
            f"✅ `14155552671,447911123456`\n\n"
            f"⚠️ Max 15 | + mat lagao\n\n"
            f"/cancel to go back",
        )
        return PHONE_BATCH_OTHER

async def phone_single_india(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw   = update.message.text.strip()
    user  = update.effective_user
    clean = raw.replace(" ", "").replace("-", "").replace("+", "")

    if not clean.isdigit():
        await update.message.reply_text("❌ Sirf numbers! Example: `9876543210`\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_SINGLE_INDIA

    if clean.startswith("91") and len(clean) == 12:
        clean = clean[2:]

    if len(clean) != 10:
        await update.message.reply_text("❌ 10 digit ka number daalo!\nExample: `9876543210`\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_SINGLE_INDIA

    final = f"91{clean}"
    await _do_phone_single(update, context, final, f"🇮🇳 {final}")
    return ConversationHandler.END

async def phone_single_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw   = update.message.text.strip()
    clean = raw.replace(" ", "").replace("-", "").replace("+", "")

    if not clean.isdigit():
        await update.message.reply_text("❌ Sirf numbers! Example: `14155552671`\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_SINGLE_OTHER

    if not (7 <= len(clean) <= 15):
        await update.message.reply_text("❌ 7-15 digit hone chahiye!\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_SINGLE_OTHER

    await _do_phone_single(update, context, clean, f"🌍 {clean}")
    return ConversationHandler.END

async def phone_batch_india(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw     = update.message.text.strip()
    user    = update.effective_user
    raw_nums = [n.strip().replace(" ","").replace("-","").replace("+","") for n in raw.split(",") if n.strip()]
    valid   = []
    invalid = []

    for num in raw_nums:
        if num.startswith("91") and len(num) == 12:
            num = num[2:]
        if num.isdigit() and len(num) == 10:
            full = f"91{num}"
            if full not in valid:
                valid.append(full)
        else:
            invalid.append(num)

    if not valid:
        await update.message.reply_text("❌ Koi valid Indian number nahi!\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_BATCH_INDIA

    warning = f"\n⚠️ Skip kiye {len(invalid)}: `{', '.join(invalid[:3])}`\n" if invalid else ""
    await _do_phone_batch(update, context, valid[:15], "india", warning)
    return ConversationHandler.END

async def phone_batch_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw     = update.message.text.strip()
    raw_nums = [n.strip().replace(" ","").replace("-","").replace("+","") for n in raw.split(",") if n.strip()]
    valid   = []
    invalid = []

    for num in raw_nums:
        if num.isdigit() and 7 <= len(num) <= 15:
            if num not in valid:
                valid.append(num)
        else:
            invalid.append(num)

    if not valid:
        await update.message.reply_text("❌ Koi valid number nahi!\nTry again ya /cancel", parse_mode="Markdown")
        return PHONE_BATCH_OTHER

    warning = f"\n⚠️ Skip kiye {len(invalid)}: `{', '.join(invalid[:3])}`\n" if invalid else ""
    await _do_phone_batch(update, context, valid[:15], "other", warning)
    return ConversationHandler.END

async def _do_phone_single(update, context, number, display):
    user = update.effective_user
    ok, status, _, is_premium, plan_key = check_phone_access(user.id)

    if not ok:
        await update.message.reply_text(
            f"🔒 *Locked!*\n{status}\n💰 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return

    msg    = await update.message.reply_text(f"🔍 Searching `{display}`...", parse_mode="Markdown")
    result = search_api(number)

    if result["ok"]:
        use_phone_search(user.id)
        text = format_result(display, result["data"], "📱")

        # ✅ Admin - no limit footer
        if is_admin(user.id):
            text += f"\n\n{'━'*25}\n🛡️ Admin Search"
        elif is_premium:
            plan      = PLANS.get(plan_key, PLANS["trial"])
            daily_rem = get_phone_daily_remaining(user.id)
            if not plan.get("unlimited"):
                text += f"\n\n{'━'*25}\n📊 Today: *{daily_rem}/{plan.get('daily_limit',0)}*"
        else:
            free_left = get_phone_free_remaining(user.id)
            text += f"\n\n{'━'*25}\n🆓 Trial: *{free_left}/{PHONE_FREE_SEARCHES}*"

        await msg.edit_text(text, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    else:
        await msg.edit_text(
            f"❌ *Search Failed*\n`{result['error']}`",
            reply_markup=back_keyboard(), parse_mode="Markdown"
        )

async def _do_phone_batch(update, context, numbers, country, warning=""):
    user  = update.effective_user
    ok, status, _, is_premium, plan_key = check_phone_access(user.id)
    plan  = PLANS.get(plan_key, PLANS["trial"])
    total = len(numbers)

    # ✅ Admin = always unlimited available
    if is_admin(user.id):
        available = 999999
    else:
        free_left = get_phone_free_remaining(user.id)
        daily_rem = get_phone_daily_remaining(user.id)
        available = 999999 if plan.get("unlimited") else (daily_rem if is_premium else free_left)

    if total > available:
        await update.message.reply_text(
            f"❌ *Searches kam hain!*\n\nNumbers: *{total}* | Available: *{available}*\n\n👉 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return

    if warning:
        await update.message.reply_text(warning, parse_mode="Markdown")

    flag = "🇮🇳" if country == "india" else "🌍"
    msg  = await update.message.reply_text(f"{flag} Processing {total} numbers...\n[{'░'*total}]")

    for i, num in enumerate(numbers, 1):
        result   = search_api(num)
        progress = "█" * i + "░" * (total - i)
        display  = f"🇮🇳 {num}" if country == "india" else f"🌍 {num}"

        if result["ok"]:
            use_phone_search(user.id)
            text = format_result(display, result["data"], "📱")
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ *{display}*\n`{result['error']}`", parse_mode="Markdown")

        try:
            await msg.edit_text(f"{flag} Processing... ({i}/{total})\n[{progress}]")
        except:
            pass

    # ✅ Admin summary
    if is_admin(user.id):
        summary = f"✅ *Batch Done!*\n📊 Processed: {total}\n🛡️ Admin Search"
    elif is_premium and not plan.get("unlimited"):
        daily_rem = get_phone_daily_remaining(user.id)
        summary   = f"✅ *Batch Done!*\n📊 Processed: {total}\n📊 Today Left: *{daily_rem}/{plan.get('daily_limit',0)}*"
    elif not is_premium:
        free_left = get_phone_free_remaining(user.id)
        summary   = f"✅ *Batch Done!*\n📊 Processed: {total}\n🆓 Trial Left: *{free_left}/{PHONE_FREE_SEARCHES}*"
    else:
        summary = f"✅ *Batch Done!*\n📊 Processed: {total}"

    await msg.edit_text(summary, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")


# ==================== EMAIL SEARCH ====================
async def email_single_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    ok, status, _, is_premium = check_email_access(user.id)
    if not ok:
        await safe_edit(
            query,
            f"🔒 *Email Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}\nYour ID: `{user.id}`",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    if is_admin(user.id):
        info = "🛡️ Admin — ∞ Unlimited"
    else:
        free_left = get_email_free_remaining(user.id)
        info = "💎 Premium — Unlimited" if is_premium else f"🆓 {free_left}/{EMAIL_FREE_SEARCHES} remaining"

    await safe_edit(
        query,
        f"📧 *Email Single Search*\n\n"
        f"📊 {info}\n\n"
        f"📧 Email address daalo:\n"
        f"_Example: user@gmail.com_\n\n"
        f"/cancel to go back",
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
            f"🔒 *Locked!*\n{status}\n💰 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END

    msg    = await update.message.reply_text("🔍 Searching...")
    result = search_api(email)

    if result["ok"]:
        use_email_search(user.id, is_premium)
        text = format_result(email, result["data"], "📧")

        # ✅ Admin footer
        if is_admin(user.id):
            text += f"\n\n{'━'*25}\n🛡️ Admin Search"
        elif not is_premium:
            free_left = get_email_free_remaining(user.id)
            text += f"\n\n{'━'*25}\n🆓 Remaining: *{free_left}/{EMAIL_FREE_SEARCHES}*"

        await msg.edit_text(text, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    else:
        await msg.edit_text(
            f"❌ *Search Failed*\n`{result['error']}`",
            reply_markup=back_keyboard(), parse_mode="Markdown"
        )
    return ConversationHandler.END

async def email_batch_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    ok, status, _, is_premium = check_email_access(user.id)
    if not ok:
        await safe_edit(
            query,
            f"🔒 *Email Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(),
        )
        return ConversationHandler.END

    if is_admin(user.id):
        info = "🛡️ Admin — ∞ Unlimited"
    else:
        free_left = get_email_free_remaining(user.id)
        info = "💎 Unlimited" if is_premium else f"🆓 {free_left}/{EMAIL_FREE_SEARCHES}"

    await safe_edit(
        query,
        f"📦 *Email Batch Search*\n\n"
        f"📊 {info}\n\n"
        f"📧 Emails comma se daalo:\n"
        f"_a@gmail.com,b@yahoo.com_\n"
        f"_Max 15 at once_\n\n"
        f"/cancel to go back",
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

    # ✅ Admin = always enough
    if is_admin(user.id):
        available = 999999
    else:
        free_left = get_email_free_remaining(user.id)
        available = 999999 if is_premium else free_left

    if total > available:
        await update.message.reply_text(
            f"❌ *Not enough searches!*\n\nEmails: *{total}* | Available: *{available}*\n\n👉 {OWNER_CONTACT}",
            reply_markup=buy_keyboard(), parse_mode="Markdown"
        )
        return ConversationHandler.END

    msg = await update.message.reply_text(f"🚀 Processing {total} emails...\n[{'░'*total}]")

    for i, em in enumerate(emails, 1):
        result   = search_api(em)
        progress = "█" * i + "░" * (total - i)

        if result["ok"]:
            use_email_search(user.id, is_premium)
            text = format_result(em, result["data"], "📧")
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ *{em}*\n`{result['error']}`", parse_mode="Markdown")

        try:
            await msg.edit_text(f"🚀 Processing... ({i}/{total})\n[{progress}]")
        except:
            pass

    # ✅ Admin summary
    if is_admin(user.id):
        summary = f"✅ *Batch Complete!*\n📊 Processed: {total}\n🛡️ Admin Search"
    elif not is_premium:
        free_left = get_email_free_remaining(user.id)
        summary   = f"✅ *Batch Complete!*\n📊 Processed: {total}\n🆓 Remaining: *{free_left}/{EMAIL_FREE_SEARCHES}*"
    else:
        summary = f"✅ *Batch Complete!*\n📊 Processed: {total}"

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
    p_prem = sum(1 for u in users.values() if u.get("phone_is_premium", False))
    e_prem = sum(1 for u in users.values() if u.get("email_is_premium", False))

    text = (
        f"{'━' * 30}\n"
        f"       🛠️ *Admin Panel*\n"
        f"{'━' * 30}\n\n"
        f"🛡️ Admins: {len(ADMIN_IDS)}\n"
        f"👥 Total Users : {total}\n"
        f"📱 Phone Prem  : {p_prem}\n"
        f"📧 Email Prem  : {e_prem}\n\n"
        f"Choose action:"
    )

    if update.callback_query:
        await safe_edit(update.callback_query, text, reply_markup=admin_menu_keyboard())
    else:
        await update.message.reply_text(text, reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_panel(update, context)

async def admin_phone_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()
    await safe_edit(query, "📱 *Phone Admin*\n\nChoose action:", reply_markup=phone_admin_keyboard())

async def admin_email_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return
    await query.answer()
    await safe_edit(query, "📧 *Email Admin*\n\nChoose action:", reply_markup=email_admin_keyboard())

# --- Phone Admin ---
async def admin_phone_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "📱 *Add Phone Premium*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_ADD_ID

async def admin_phone_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ Invalid ID!\n/cancel to stop")
        return ADMIN_ADD_ID
    context.user_data["admin_uid"] = uid
    await update.message.reply_text(
        f"✅ User: `{uid}`\nPlan select karo:",
        reply_markup=phone_plan_keyboard("phone_add"),
        parse_mode="Markdown"
    )
    return ADMIN_ADD_PLAN

async def admin_phone_add_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_back":
        await admin_panel(update, context)
        return ConversationHandler.END

    plan_map = {
        "phone_add_7days": "7days", "phone_add_30days": "30days",
        "phone_add_6months": "6months", "phone_add_12months": "12months",
    }
    plan_key = plan_map.get(query.data, "7days")
    uid      = context.user_data.get("admin_uid")
    plan     = PLANS.get(plan_key)
    expiry   = upgrade_phone_user(int(uid), plan_key)

    await safe_edit(
        query,
        f"✅ *Phone Plan Added!*\n\n"
        f"🆔 `{uid}`\n📦 {plan['name']}\n"
        f"🔍 {'Unlimited' if plan['unlimited'] else f\"{plan['daily_limit']}/day\"}\n"
        f"📅 {expiry}",
        reply_markup=admin_menu_keyboard()
    )
    return ConversationHandler.END

async def admin_phone_remove_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "❌ *Remove User*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_REM_ID

async def admin_phone_remove_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.message.text.strip()
    users = load_users()
    if uid in users:
        del users[uid]
        save_users(users)
        await update.message.reply_text(f"✅ `{uid}` removed!", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ `{uid}` not found!", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def admin_phone_expiry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "📅 *Set Phone Plan*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_EXP_ID

async def admin_phone_expiry_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    context.user_data["admin_uid"] = uid
    await update.message.reply_text(
        f"User: `{uid}`\nPlan select karo:",
        reply_markup=phone_plan_keyboard("phone_set"),
        parse_mode="Markdown"
    )
    return ADMIN_EXP_PLAN

async def admin_phone_expiry_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_back":
        await admin_panel(update, context)
        return ConversationHandler.END

    plan_map = {
        "phone_set_7days": "7days", "phone_set_30days": "30days",
        "phone_set_6months": "6months", "phone_set_12months": "12months",
    }
    plan_key = plan_map.get(query.data, "7days")
    uid      = context.user_data.get("admin_uid")
    plan     = PLANS.get(plan_key)
    expiry   = upgrade_phone_user(int(uid), plan_key)

    await safe_edit(
        query,
        f"✅ *Phone Plan Updated!*\n\n🆔 `{uid}`\n📦 {plan['name']}\n📅 {expiry}",
        reply_markup=admin_menu_keyboard()
    )
    return ConversationHandler.END

# --- Email Admin ---
async def admin_email_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "📧 *Add Email Premium*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_EMAIL_ADD_ID

async def admin_email_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ Invalid ID!\n/cancel to stop")
        return ADMIN_EMAIL_ADD_ID
    context.user_data["admin_email_uid"] = uid
    await update.message.reply_text(
        f"✅ User: `{uid}`\nDuration select karo:",
        reply_markup=email_duration_keyboard("email_add"),
        parse_mode="Markdown"
    )
    return ADMIN_EMAIL_ADD_EXP

async def admin_email_add_exp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_back":
        await admin_panel(update, context)
        return ConversationHandler.END

    days_map = {"email_add_7": 7, "email_add_30": 30, "email_add_90": 90, "email_add_365": 365}
    days     = days_map.get(query.data, 30)
    uid      = context.user_data.get("admin_email_uid")
    expiry   = upgrade_email_user(int(uid), days)

    await safe_edit(
        query,
        f"✅ *Email Premium Added!*\n\n🆔 `{uid}`\n📅 {expiry}\n⏳ {days} days",
        reply_markup=admin_menu_keyboard()
    )
    return ConversationHandler.END

async def admin_email_remove_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "❌ *Remove Email Premium*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_EMAIL_REM_ID

async def admin_email_remove_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.message.text.strip()
    users = load_users()
    if uid in users:
        users[uid]["email_is_premium"] = False
        users[uid]["email_expiry"]     = ""
        save_users(users)
        await update.message.reply_text(f"✅ `{uid}` email premium removed!", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ `{uid}` not found!", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def admin_email_expiry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("❌")
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "📅 *Set Email Expiry*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_EMAIL_EXP_ID

async def admin_email_expiry_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    context.user_data["admin_email_uid"] = uid
    await update.message.reply_text(
        f"User: `{uid}`\nDuration select karo:",
        reply_markup=email_duration_keyboard("email_set"),
        parse_mode="Markdown"
    )
    return ADMIN_EMAIL_EXP_DATE

async def admin_email_expiry_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_back":
        await admin_panel(update, context)
        return ConversationHandler.END

    days_map = {"email_set_7": 7, "email_set_30": 30, "email_set_90": 90, "email_set_365": 365}
    days     = days_map.get(query.data, 30)
    uid      = context.user_data.get("admin_email_uid")
    expiry   = upgrade_email_user(int(uid), days)

    await safe_edit(
        query,
        f"✅ *Email Premium Updated!*\n\n🆔 `{uid}`\n📅 {expiry}\n⏳ {days} days",
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

    text = f"{'━'*30}\n📋 *All Users ({len(users)})*\n{'━'*30}\n\n"

    for uid, info in users.items():
        p_prem  = info.get("phone_is_premium", False)
        e_prem  = info.get("email_is_premium", False)
        total_s = info.get("total_searches", 0)
        p_exp   = info.get("phone_expiry", "")
        e_exp   = info.get("email_expiry", "")

        # ✅ Show admin badge
        admin_m = " 🛡️∞" if int(uid) in ADMIN_IDS else ""

        if int(uid) in ADMIN_IDS:
            ps = "📱∞"
            es = "📧∞"
        else:
            if p_prem and p_exp:
                try:
                    pd = date.fromisoformat(p_exp)
                    ps = f"📱💎{(pd-date.today()).days}d" if date.today() <= pd else "📱🔴"
                except:
                    ps = "📱⚪"
            else:
                pf = max(0, PHONE_FREE_SEARCHES - info.get("phone_free_used", 0))
                ps = f"📱🆓{pf}"

            if e_prem and e_exp:
                try:
                    ed = date.fromisoformat(e_exp)
                    es = f"📧💎{(ed-date.today()).days}d" if date.today() <= ed else "📧🔴"
                except:
                    es = "📧⚪"
            else:
                ef = max(0, EMAIL_FREE_SEARCHES - info.get("email_free_used", 0))
                es = f"📧🆓{ef}"

        text += f"`{uid}`{admin_m} | {ps} | {es} | 🔍{total_s}\n"

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
    p_active = p_expired = p_trial = 0
    e_active = e_expired = e_trial = 0
    plan_counts = {k: 0 for k in PLANS}

    for uid, info in users.items():
        total_searches += info.get("total_searches", 0)

        if int(uid) in ADMIN_IDS:
            continue  # Skip admins from stats count

        if info.get("phone_is_premium"):
            try:
                exp = date.fromisoformat(info.get("phone_expiry", "2000-01-01"))
                if date.today() <= exp:
                    p_active += 1
                    plan_counts[info.get("phone_plan","trial")] = plan_counts.get(info.get("phone_plan","trial"),0)+1
                else:
                    p_expired += 1
            except:
                p_expired += 1
        else:
            p_trial += 1

        if info.get("email_is_premium"):
            try:
                exp = date.fromisoformat(info.get("email_expiry", "2000-01-01"))
                if date.today() <= exp:
                    e_active += 1
                else:
                    e_expired += 1
            except:
                e_expired += 1
        else:
            e_trial += 1

    text = (
        f"{'━'*30}\n"
        f"       📊 *Bot Statistics*\n"
        f"{'━'*30}\n\n"
        f"👥 Total Users     : {total}\n"
        f"🔍 Total Searches  : {total_searches}\n"
        f"🛡️ Admins (∞)      : {len(ADMIN_IDS)}\n\n"
        f"{'━'*25}\n"
        f"📱 *Phone Search*\n"
        f"{'━'*25}\n"
        f"🟢 Active Premium  : {p_active}\n"
        f"🔴 Expired         : {p_expired}\n"
        f"🆓 Trial           : {p_trial}\n\n"
        f"Plan Breakdown:\n"
        f"  🥉 7D  : {plan_counts.get('7days',0)}\n"
        f"  🥈 30D : {plan_counts.get('30days',0)}\n"
        f"  🥇 6M  : {plan_counts.get('6months',0)}\n"
        f"  💎 12M : {plan_counts.get('12months',0)}\n\n"
        f"{'━'*25}\n"
        f"📧 *Email Search*\n"
        f"{'━'*25}\n"
        f"🟢 Active Premium  : {e_active}\n"
        f"🔴 Expired         : {e_expired}\n"
        f"🆓 Free Users      : {e_trial}\n\n"
        f"📅 {date.today()}\n"
    )
    await safe_edit(query, text, reply_markup=admin_menu_keyboard())

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END


# ================== MAIN ==================
def main():
    request             = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0, pool_timeout=60.0)
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

    phone_add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_phone_add_start, pattern="^admin_phone_add$")],
        states={
            ADMIN_ADD_ID:   [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_phone_add_id)],
            ADMIN_ADD_PLAN: [CallbackQueryHandler(admin_phone_add_plan, pattern="^phone_add_|^admin_back$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )

    phone_remove_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_phone_remove_start, pattern="^admin_phone_remove$")],
        states={ADMIN_REM_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_phone_remove_process)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )

    phone_expiry_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_phone_expiry_start, pattern="^admin_phone_expiry$")],
        states={
            ADMIN_EXP_ID:   [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_phone_expiry_id)],
            ADMIN_EXP_PLAN: [CallbackQueryHandler(admin_phone_expiry_set, pattern="^phone_set_|^admin_back$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )

    email_add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_email_add_start, pattern="^admin_email_add$")],
        states={
            ADMIN_EMAIL_ADD_ID:  [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_email_add_id)],
            ADMIN_EMAIL_ADD_EXP: [CallbackQueryHandler(admin_email_add_exp, pattern="^email_add_|^admin_back$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )

    email_remove_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_email_remove_start, pattern="^admin_email_remove$")],
        states={ADMIN_EMAIL_REM_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_email_remove_process)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )

    email_expiry_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_email_expiry_start, pattern="^admin_email_expiry$")],
        states={
            ADMIN_EMAIL_EXP_ID:   [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_email_expiry_id)],
            ADMIN_EMAIL_EXP_DATE: [CallbackQueryHandler(admin_email_expiry_set, pattern="^email_set_|^admin_back$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False, allow_reentry=True,
    )

    for conv in [
        phone_single_conv, phone_batch_conv,
        email_single_conv, email_batch_conv,
        phone_add_conv, phone_remove_conv, phone_expiry_conv,
        email_add_conv, email_remove_conv, email_expiry_conv,
    ]:
        app.add_handler(conv)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))

    app.add_handler(CallbackQueryHandler(mode_phone,         pattern="^mode_phone$"))
    app.add_handler(CallbackQueryHandler(mode_email,         pattern="^mode_email$"))
    app.add_handler(CallbackQueryHandler(profile,            pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(status_check,       pattern="^status$"))
    app.add_handler(CallbackQueryHandler(help_menu,          pattern="^help$"))
    app.add_handler(CallbackQueryHandler(buy,                pattern="^buy$"))
    app.add_handler(CallbackQueryHandler(admin_phone_menu,   pattern="^admin_phone$"))
    app.add_handler(CallbackQueryHandler(admin_email_menu,   pattern="^admin_email$"))
    app.add_handler(CallbackQueryHandler(admin_list,         pattern="^admin_list$"))
    app.add_handler(CallbackQueryHandler(admin_stats,        pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_back,         pattern="^admin_back$"))
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))

    print("🤖 Combined Bot Running!")
    print(f"🛡️  Admins (Unlimited) : {ADMIN_IDS}")
    print(f"📱 Phone Free          : {PHONE_FREE_SEARCHES}")
    print(f"📧 Email Free          : {EMAIL_FREE_SEARCHES}")
    print("⏹  Ctrl+C to stop\n")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )

if __name__ == "__main__":
    main()

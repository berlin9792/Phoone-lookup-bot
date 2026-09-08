#!/usr/bin/env python3
"""
🔍 Ultimate Intelligence Bot - ZERO TRACE (BULLETPROOF INSTANT RESPONSE)
"""

import json, os, threading, requests, logging, asyncio, re, time, html, secrets, sys
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from collections import deque
from flask import Flask
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter, BadRequest, TelegramError
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters, TypeHandler
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== ⚙️ CONFIG ==================
BOT_TOKEN     = "8943597033:AAEF7OzTCWaWXv5D80LDR-iTKpm1vA1z4Go"
ADMIN_IDS     = [5057489358, 1968142314]
OWNER_CONTACT = "@theplayerror"

PRIMARY_API_URL = "https://api-src.alonepatel.shop/api"
PRIMARY_API_KEY = "INDIAN_HACKER_BRO"

TGID_API_URL = "https://api-src.alonepatel.shop/api"
TGID_API_KEY = "Tgid_num"

PHONE_ENGINE_ACTIVE = "primary"

ACTIVE_PHONE_API_URL = "https://storage-deutschland-don-patterns.trycloudflare.com/num"
ACTIVE_PHONE_API_KEY = "DADDY"

BACKUP_PIN             = "happyrb"
BACKUP_SEARCH_API_URL  = "https://num-info-hiteck.asurpapa.workers.dev/"
BACKUP_PHONE_API_URL   = "https://num-info-hiteck.asurpapa.workers.dev/api"
BACKUP_AADHAAR_API_URL = "https://ansh-apis.is-dev.org/api/ration"
BACKUP_AADHAAR_API_KEY = "shree"
BACKUP_VEHICLE_API_URL = "https://ansh-apis.is-dev.org/api/vehicle"
BACKUP_VEHICLE_API_KEY = "ansh"
BACKUP_IFSC_API_URL    = "https://all-api-by-nitin-developer-best1.binderdhaniya6.workers.dev/api"
BACKUP_IFSC_API_KEY    = "NITIN"
BACKUP_VINFO_API_URL   = "https://rtf-api-server.onrender.com/api"
BACKUP_VINFO_API_KEY   = "demo2"

FORCE_JOIN_CHANNEL_1    = "@hackkwr"
FORCE_JOIN_CHANNEL_1_ID = "@hackkwr"
FORCE_JOIN_CHANNEL_2    = "@zerotracelegit"
FORCE_JOIN_CHANNEL_2_ID = "@zerotracelegit"

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://httplegitfs_db_user:Q8uGZxERXsrf2VV1@cluster0.iojnad7.mongodb.net/?retryWrites=true&w=majority")
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://api-src.alonepatel.shop/",
}

FREE_LIMIT = 2

PLANS = {
    "trial": {"name": "Trial", "days": 0, "price": 0, "daily_limit": 0, "unlimited": False, "is_free": True},
    "7days": {"name": "7 Days", "days": 7, "price": 50, "daily_limit": 10, "unlimited": False, "is_free": False},
    "30days": {"name": "30 Days", "days": 30, "price": 130, "daily_limit": 20, "unlimited": False, "is_free": False},
    "6months": {"name": "6 Months", "days": 180, "price": 300, "daily_limit": 35, "unlimited": False, "is_free": False},
    "12months": {"name": "12 Months", "days": 365, "price": 799, "daily_limit": 999999, "unlimited": True, "is_free": False},
}

# ================== 🛡️ HARDCODED PROTECTED ADMIN IDS & NUMBERS ==================
# ⛔ HARDCODED PROTECTED NUMBERS - Custom Error Message
HARDCODED_PROTECTED_NUMBERS = {"9792574835", "7991927061"}

# ⛔ HARDCODED PROTECTED ADMIN TG IDS - Custom Error Message
HARDCODED_PROTECTED_ADMIN_IDS = {"5057489358", "1968142314"}

# Custom Error Messages
ADMIN_ID_BLOCK_MSG = (
    "🚫🔥 <b>OYE MADARCHOD!</b> 🔥🚫\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "😡 <b>bkl aukat mt bhul apni</b>\n\n"
    "⛔ Admin ki ID search karne ki himmat kaise hui teri?\n"
    "🔨 Ban ho jayega bhosdike!\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"📲 Roeda: {OWNER_CONTACT}"
)

OWNER_NUMBER_BLOCK_MSG = (
    "🚫🔥 <b>ABE CHUTIYE!</b> 🔥🚫\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "😡 <b>bhadwe number leke gand me dalega mera?</b>\n\n"
    "⛔ Owner ka number search karta hai bsdk?\n"
    "🔨 Aukat me reh warna ban permanent!\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"📲 Roeda: {OWNER_CONTACT}"
)

def normalize_number(val):
    """Normalize phone number - remove +, -, spaces, and country codes"""
    if not val: return ""
    clean = str(val).replace("+", "").replace("-", "").replace(" ", "").strip()
    # Remove country code prefixes
    if clean.startswith("91") and len(clean) == 12:
        clean = clean[2:]
    elif clean.startswith("0") and len(clean) == 11:
        clean = clean[1:]
    return clean

def is_hardcoded_protected_number(val):
    """Check if the value is a hardcoded protected phone number"""
    normalized = normalize_number(val)
    return normalized in HARDCODED_PROTECTED_NUMBERS

def is_hardcoded_protected_admin_id(val):
    """Check if the value is a hardcoded protected admin TG ID"""
    clean = str(val).strip()
    return clean in HARDCODED_PROTECTED_ADMIN_IDS

# ================== 🛡️ PROTECTED IDS/NUMBERS SYSTEM ==================
PROTECTED_ENTRIES = set()

def load_protected_entries():
    global PROTECTED_ENTRIES
    if db is not None:
        try:
            prot_col = db["protected_entries"]
            for doc in prot_col.find():
                PROTECTED_ENTRIES.add(str(doc["_id"]).strip())
            print(f"🛡️ Loaded {len(PROTECTED_ENTRIES)} protected entries from MongoDB.", flush=True)
            return
        except Exception as e:
            logger.warning(f"Protected entries DB load error: {e}")
    
    prot_file = Path("protected_entries.json")
    if prot_file.exists():
        try:
            data = json.loads(prot_file.read_text())
            PROTECTED_ENTRIES = set(str(x).strip() for x in data)
            print(f"🛡️ Loaded {len(PROTECTED_ENTRIES)} protected entries from local file.", flush=True)
        except Exception as e:
            logger.warning(f"Protected entries local load error: {e}")

def save_protected_entry(entry):
    entry = str(entry).strip()
    PROTECTED_ENTRIES.add(entry)
    def _save():
        if db is not None:
            try:
                prot_col = db["protected_entries"]
                prot_col.update_one(
                    {"_id": entry},
                    {"$set": {"added_at": datetime.now(timezone.utc).isoformat()}},
                    upsert=True
                )
            except Exception as e:
                logger.error(f"Protected entry DB save error: {e}")
        try:
            prot_file = Path("protected_entries.json")
            prot_file.write_text(json.dumps(list(PROTECTED_ENTRIES), indent=2))
        except Exception:
            pass
    threading.Thread(target=_save, daemon=True).start()

def remove_protected_entry(entry):
    entry = str(entry).strip()
    PROTECTED_ENTRIES.discard(entry)
    def _remove():
        if db is not None:
            try:
                prot_col = db["protected_entries"]
                prot_col.delete_one({"_id": entry})
            except Exception as e:
                logger.error(f"Protected entry DB remove error: {e}")
        try:
            prot_file = Path("protected_entries.json")
            prot_file.write_text(json.dumps(list(PROTECTED_ENTRIES), indent=2))
        except Exception:
            pass
    threading.Thread(target=_remove, daemon=True).start()

def is_protected(search_value):
    sv = str(search_value).strip()
    if sv in PROTECTED_ENTRIES:
        return True
    for prefix in ["91", "+91", "0"]:
        if sv.startswith(prefix):
            stripped = sv[len(prefix):]
            if stripped in PROTECTED_ENTRIES:
                return True
    if sv.isdigit():
        for entry in PROTECTED_ENTRIES:
            clean_entry = entry.replace("+", "").replace("-", "").replace(" ", "")
            clean_sv = sv.replace("+", "").replace("-", "").replace(" ", "")
            if clean_entry == clean_sv:
                return True
            if len(clean_entry) >= 10 and len(clean_sv) >= 10:
                if clean_entry[-10:] == clean_sv[-10:]:
                    return True
    return False

PROTECTED_BLOCK_MSG = (
    "🛡️🔒 <b>PROTECTED ENTITY</b> 🔒🛡️\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "⛔ This number/ID is <b>PROTECTED</b> and cannot be searched.\n\n"
    "🚫 All lookup operations are <b>BLOCKED</b> for this entry.\n\n"
    "⚠️ Repeated attempts may result in account restrictions.\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"📲 Contact: {OWNER_CONTACT}"
)

def get_block_message(feat_name, search_value):
    """Return appropriate block message based on feature and value"""
    # Check for hardcoded admin ID protection (TG features)
    if feat_name in ["tg", "tgid"]:
        if is_hardcoded_protected_admin_id(search_value):
            return ADMIN_ID_BLOCK_MSG, "hardcoded_admin"
    
    # Check for hardcoded phone number protection
    if feat_name in ["phone", "paytm", "upi", "imei"]:
        if is_hardcoded_protected_number(search_value):
            return OWNER_NUMBER_BLOCK_MSG, "hardcoded_number"
        # For UPI, also check if the prefix contains protected number
        if feat_name == "upi":
            upi_prefix = str(search_value).split("@")[0]
            if is_hardcoded_protected_number(upi_prefix):
                return OWNER_NUMBER_BLOCK_MSG, "hardcoded_number"
    
    # Fallback to normal protected message
    return PROTECTED_BLOCK_MSG, "protected"

def is_blocked_search(feat_name, search_value):
    """Universal block checker - returns (is_blocked, message, log_status)"""
    # Check hardcoded admin ID (for TG/TGID features)
    if feat_name in ["tg", "tgid"]:
        if is_hardcoded_protected_admin_id(search_value):
            return True, ADMIN_ID_BLOCK_MSG, "blocked_admin_id"
    
    # Check hardcoded phone numbers (for phone, paytm, imei)
    if feat_name in ["phone", "paytm", "imei"]:
        if is_hardcoded_protected_number(search_value):
            return True, OWNER_NUMBER_BLOCK_MSG, "blocked_owner_number"
    
    # Check UPI (both full string and prefix)
    if feat_name == "upi":
        if is_hardcoded_protected_number(search_value):
            return True, OWNER_NUMBER_BLOCK_MSG, "blocked_owner_number"
        upi_prefix = str(search_value).split("@")[0]
        if is_hardcoded_protected_number(upi_prefix):
            return True, OWNER_NUMBER_BLOCK_MSG, "blocked_owner_number"
    
    # Check regular protected entries (from admin panel)
    if is_protected(search_value):
        return True, PROTECTED_BLOCK_MSG, "blocked_protected"
    
    return False, None, None

# ================== 📚 FEATURE EXAMPLES ==================
FEATURE_EXAMPLES = {
    "phone":    "📞 <b>Example:</b> <code>9876543210</code>",
    "email":    "📧 <b>Example:</b> <code>john.doe@gmail.com</code>",
    "upi":      "💳 <b>Example:</b> <code>ramkumar@paytm</code> or <code>9876543210@ybl</code>",
    "aadhaar":  "🪪 <b>Example:</b> <code>123456789012</code> (12 digits)",
    "vehicle":  "🚗 <b>Example:</b> <code>DL8CAF5030</code> or <code>MH12AB1234</code>",
    "ifsc":     "🏦 <b>Example:</b> <code>SBIN0001234</code> (11 chars)",
    "tg":       "👤 <b>Example:</b> <code>7142426722</code> (Numeric TG ID)",
    "insta":    "📸 <b>Example:</b> <code>cristiano</code> or <code>@leomessi</code>",
    "imei":     "📱 <b>Example:</b> <code>354751093234567</code> (15 digits)",
    "pin":      "📮 <b>Example:</b> <code>110001</code> (6 digits)",
    "country":  "🌍 <b>Example:</b> <code>India</code> or <code>United States</code>",
    "paytm":    "💰 <b>Example:</b> <code>9876543210</code>",
    "ip":       "🌐 <b>Example:</b> <code>8.8.8.8</code> or <code>142.250.191.14</code>",
    "weather":  "🌤️ <b>Example:</b> <code>Mumbai</code>, <code>Delhi</code>, <code>London</code>",
    "tgid":     "🆔 <b>Example:</b> <code>8771611214</code> (Telegram User ID → Info)",
}

# ================== 📋 ACTIVITY LOGS SYSTEM ==================
IST = timezone(timedelta(hours=5, minutes=30))
ACTIVITY_LOGS = deque(maxlen=200)

def add_activity_log(user_id, username, first_name, feat_name, search_term, status="success"):
    now = datetime.now(IST)
    log_entry = {
        "time": now.strftime("%d-%m-%Y %H:%M:%S"),
        "time_short": now.strftime("%H:%M"),
        "date": now.strftime("%d-%m"),
        "user_id": user_id,
        "username": username or "N/A",
        "first_name": first_name or "Unknown",
        "feature": feat_name,
        "search_term": str(search_term)[:50],
        "status": status,
        "timestamp": time.time()
    }
    ACTIVITY_LOGS.append(log_entry)
    try:
        if users_col is not None:
            logs_col = db["activity_logs"]
            threading.Thread(
                target=lambda: logs_col.insert_one(log_entry),
                daemon=True
            ).start()
    except Exception:
        pass

def cleanup_old_logs_loop():
    while True:
        try:
            three_days_ago = time.time() - (3 * 24 * 3600)
            if db is not None:
                logs_col = db["activity_logs"]
                res = logs_col.delete_many({"timestamp": {"$lt": three_days_ago}})
                if res.deleted_count > 0:
                    logger.info(f"🧹 [Auto-Cleanup] Deleted {res.deleted_count} logs older than 3 days from MongoDB.")
            current_time = time.time()
            local_logs = list(ACTIVITY_LOGS)
            ACTIVITY_LOGS.clear()
            for log in local_logs:
                log_ts = log.get("timestamp")
                if log_ts and (current_time - log_ts < (3 * 24 * 3600)):
                    ACTIVITY_LOGS.append(log)
        except Exception as e:
            logger.error(f"❌ Error in auto-logs cleanup loop: {e}")
        time.sleep(1800)

def get_recent_logs(count=20):
    logs = list(ACTIVITY_LOGS)
    return logs[-count:] if len(logs) > count else logs

def get_user_logs(user_id, count=10):
    return [l for l in ACTIVITY_LOGS if l["user_id"] == user_id][-count:]

def get_feature_logs(feat_name, count=15):
    return [l for l in ACTIVITY_LOGS if l["feature"] == feat_name][-count:]

def format_logs_text(logs, title="📋 ACTIVITY LOGS"):
    if not logs:
        return f"<code>{BANNER_MINI}</code>\n\n{title}\n\n📭 <i>No activity logs yet.</i>"
    txt = f"<code>{BANNER_MINI}</code>\n\n<b>{title}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for log in reversed(logs):
        status_icon = "✅" if log["status"] == "success" else ("🛡️" if "blocked" in log["status"] else "❌")
        uname = f"@{log['username']}" if log['username'] != "N/A" else log['first_name']
        txt += (
            f"{status_icon} <b>{log['time_short']}</b> | "
            f"<code>{log['user_id']}</code> | "
            f"<b>{html.escape(uname)}</b>\n"
            f"   🔍 <b>{log['feature'].upper()}</b> → "
            f"<code>{html.escape(log['search_term'])}</code>\n\n"
        )
    return txt[:4000]

# ================== 🔧 PERSISTENT MAINTENANCE SYSTEM ==================
ALL_FEATURE_KEYS = [
    "phone", "email", "upi", "aadhaar", "vehicle", "ifsc",
    "tg", "insta", "imei", "pin", "country", "paytm", "ip", "weather", "tgid"
]

SETTINGS_FILE = Path("settings.json")
SETTINGS_CACHE = {
    "full_maintenance": False,
    "feature_maintenance": {feat: False for feat in ALL_FEATURE_KEYS}
}

def load_settings():
    global SETTINGS_CACHE
    if db is not None:
        try:
            settings_col = db["settings"]
            doc = settings_col.find_one({"_id": "global_settings"})
            if doc:
                SETTINGS_CACHE["full_maintenance"] = doc.get("full_maintenance", False)
                feat_maint = doc.get("feature_maintenance", {})
                for feat in ALL_FEATURE_KEYS:
                    SETTINGS_CACHE["feature_maintenance"][feat] = feat_maint.get(feat, False)
                print("✅ Global Settings loaded from MongoDB!", flush=True)
                return
        except Exception as e:
            logger.warning(f"DB Settings Load Error: {e}")

    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text())
            SETTINGS_CACHE["full_maintenance"] = data.get("full_maintenance", False)
            feat_maint = data.get("feature_maintenance", {})
            for feat in ALL_FEATURE_KEYS:
                SETTINGS_CACHE["feature_maintenance"][feat] = feat_maint.get(feat, False)
            print("💾 Global Settings loaded from Local JSON Backup!", flush=True)
        except Exception as e:
            logger.warning(f"Local Settings Load Error: {e}")

def save_settings():
    try:
        SETTINGS_FILE.write_text(json.dumps(SETTINGS_CACHE, indent=2))
    except Exception as e:
        logger.error(f"Local Settings Save Error: {e}")

    def _save():
        if db is not None:
            try:
                settings_col = db["settings"]
                settings_col.update_one(
                    {"_id": "global_settings"},
                    {"$set": {
                        "full_maintenance": SETTINGS_CACHE["full_maintenance"],
                        "feature_maintenance": SETTINGS_CACHE["feature_maintenance"]
                    }},
                    upsert=True
                )
            except Exception as e:
                logger.error(f"MongoDB Settings Sync Error: {e}")
    threading.Thread(target=_save, daemon=True).start()

def is_full_maintenance():
    return SETTINGS_CACHE["full_maintenance"]

def is_feature_maintenance(feat_name):
    return SETTINGS_CACHE["feature_maintenance"].get(feat_name, False)

def toggle_full_maintenance():
    SETTINGS_CACHE["full_maintenance"] = not SETTINGS_CACHE["full_maintenance"]
    save_settings()
    return SETTINGS_CACHE["full_maintenance"]

def toggle_feature_maintenance(feat_name):
    if feat_name in SETTINGS_CACHE["feature_maintenance"]:
        SETTINGS_CACHE["feature_maintenance"][feat_name] = not SETTINGS_CACHE["feature_maintenance"][feat_name]
        save_settings()
        return SETTINGS_CACHE["feature_maintenance"][feat_name]
    return False

def get_maintenance_status():
    lines = [f"🔧 <b>Full Bot Maintenance:</b> {'🔴 ON' if SETTINGS_CACHE['full_maintenance'] else '🟢 OFF'}", "", "<b>Per-Feature Maintenance:</b>"]
    for feat in ALL_FEATURE_KEYS:
        status = "🔴 ON" if SETTINGS_CACHE["feature_maintenance"].get(feat, False) else "🟢 OFF"
        lines.append(f"  • <b>{feat.title()}</b>: {status}")
    return "\n".join(lines)

MAINTENANCE_MSG_FULL = f"🛠️ <b>BOT UNDER MAINTENANCE</b>\n\n⚠️ All services temporarily unavailable.\n\n⏳ Please try again later.\n📞 Contact: {OWNER_CONTACT}"

def maintenance_msg_feature(feat_name):
    return f"🛠️ <b>{feat_name.upper()} - UNDER MAINTENANCE</b>\n\n⚠️ The <b>{html.escape(feat_name.title())}</b> feature is currently under maintenance.\nOther features may still be available.\n\n⏳ Try again later.\n📞 Contact: {OWNER_CONTACT}"

# ================== 🔢 CONVERSATION STATES ==================
PHONE_SINGLE, PHONE_BATCH       = 10, 11
EMAIL_SINGLE, EMAIL_BATCH       = 12, 13
UPI_SINGLE, UPI_BATCH           = 14, 15
AADHAAR_SINGLE, AADHAAR_BATCH   = 16, 17
VEHICLE_SINGLE, VEHICLE_BATCH   = 18, 19
IFSC_SINGLE, IFSC_BATCH         = 20, 21
TG_SINGLE, TG_BATCH             = 22, 23
INSTA_SINGLE, INSTA_BATCH       = 24, 25
IMEI_SINGLE, IMEI_BATCH         = 26, 27
PIN_SINGLE, PIN_BATCH           = 28, 29
COUNTRY_SINGLE, COUNTRY_BATCH   = 30, 31
PAYTM_SINGLE, PAYTM_BATCH       = 32, 33
IP_SINGLE, IP_BATCH             = 34, 35
WEATHER_SINGLE, WEATHER_BATCH   = 36, 37
TGID_SINGLE, TGID_BATCH         = 38, 39
ADMIN_ADD_ID, ADMIN_ADD_PLAN    = 50, 51
ADMIN_REM_ID                    = 52
ADMIN_EXP_ID, ADMIN_EXP_PLAN    = 53, 54
ADMIN_BROADCAST_MSG             = 55
ADMIN_BROADCAST_CONFIRM         = 56
ADMIN_CUSTOM_DAYS               = 57
ADMIN_CUSTOM_LIMIT              = 58
REDEEM_CREATE_CODE              = 70
REDEEM_CREATE_SEARCHES          = 71
REDEEM_CREATE_LIMIT             = 72
REDEEM_DELETE_CODE              = 73
ADMIN_LOGS_USER_ID              = 80
ADMIN_PROTECT_ADD               = 90
ADMIN_PROTECT_REMOVE            = 91

# ================== 🩸 BANNERS ==================
BANNER = (
    "╔══════════════════════════════╗\n"
    "║   ☠️  Z E R O  T R A C E  ☠️      ║\n"
    "║          ~BY  LEGIT               ║\n"
    "╚══════════════════════════════╝"
)
BANNER_MINI = (
    "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
    "┃  ☠️ ZERO TRACE ☠️        ┃\n"
    "┃     ~BY LEGIT            ┃\n"
    "┗━━━━━━━━━━━━━━━━━━━━━━┛"
)
BANNER_SEARCH = (
    "╔═══════════════════════╗\n"
    "║    ☠️ ZERO TRACE ☠️       ║\n"
    "║    ~BY LEGIT              ║\n"
    "╚═══════════════════════╝"
)

# ================== 🛡️ SAFE SENDERS ==================
async def safe_reply(update: Update, text: str, reply_markup=None):
    msg = update.effective_message
    if not msg: return None
    try:
        return await msg.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except RetryAfter as e:
        logger.warning(f"safe_reply RetryAfter: sleeping {e.retry_after}s")
        await asyncio.sleep(e.retry_after + 0.5)
        try: return await msg.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception: return None
    except Exception as e:
        clean = re.sub(r"</?(?:b|i|code|pre|u|s)>", "", text)
        clean = html.unescape(clean)
        try: return await msg.reply_text(clean[:4096], reply_markup=reply_markup)
        except Exception as e2: logger.error(f"safe_reply fallback error: {e2}"); return None

async def safe_edit(target, text: str, reply_markup=None):
    if not target: return None
    for attempt in range(2):
        try:
            if hasattr(target, "edit_message_text"):
                return await target.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
            elif hasattr(target, "edit_text"):
                return await target.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except RetryAfter as e:
            logger.warning(f"safe_edit RetryAfter: sleeping {e.retry_after}s")
            await asyncio.sleep(e.retry_after + 0.5)
            continue
        except BadRequest as e:
            if "Message is not modified" in str(e):
                return target
            clean = re.sub(r"</?(?:b|i|code|pre|u|s)>", "", text)
            clean = html.unescape(clean)
            try:
                if hasattr(target, "edit_message_text"):
                    return await target.edit_message_text(clean[:4096], reply_markup=reply_markup)
                elif hasattr(target, "edit_text"):
                    return await target.edit_text(clean[:4096], reply_markup=reply_markup)
            except Exception:
                return None
        except Exception as e:
            logger.warning(f"safe_edit error: {e}")
            break
    return None

def is_admin(uid): return int(uid) in ADMIN_IDS
def safe_name(user):
    return html.escape(user.first_name or "User")

# ================== 🎨 RATE-LIMIT FRIENDLY ANIMATED LOADER ==================
LOADING_STEPS = [
    ("🟡", "Scanning Database...", "██████░░░░░░░░░░░░░░", 35),
    ("🟣", "Decoding Records...",  "██████████████░░░░░░", 75),
    ("🟢", "Finalizing Report...", "████████████████████", 100)
]

def build_loading_text(icon, display, step_emoji, step_text, bar, percent):
    return (
        f"<code>{BANNER_SEARCH}</code>\n\n"
        f"{icon} <b>Searching:</b> <code>{html.escape(str(display))}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{step_emoji} <b>{step_text}</b>\n\n"
        f"<code>[{bar}]</code> <b>{percent}%</b>\n\n"
        f"⏳ <i>Please wait...</i>"
    )

async def animated_search(msg, icon, display):
    if not msg: return
    for i, (se, st, bar, pct) in enumerate(LOADING_STEPS):
        txt = build_loading_text(icon, display, se, st, bar, pct)
        await safe_edit(msg, txt)
        if i < len(LOADING_STEPS) - 1:
            await asyncio.sleep(1.2)

# ================== 🌐 FLASK KEEP-ALIVE ==================
web_app = Flask(__name__)
@web_app.route('/')
def keep_alive_status(): return "Bot Running 24/7!", 200
def start_webserver():
    import logging as lg; lg.getLogger('werkzeug').setLevel(lg.ERROR)
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================== 🔒 FAST DUAL FORCE JOIN ==================
async def check_joined(context, uid):
    if is_admin(uid): return True
    try:
        async def _check():
            m1 = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL_1_ID, uid)
            if m1.status not in ["member","administrator","creator","restricted"]: return False
            m2 = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL_2_ID, uid)
            return m2.status in ["member","administrator","creator","restricted"]
        return await asyncio.wait_for(_check(), timeout=1.5)
    except Exception as e:
        return True

def force_join_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel 1 ↗️", url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}")],
        [InlineKeyboardButton("📢 Join Channel 2 ↗️", url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton("✅ Verify Both ✅", callback_data="verify_join")],
    ])

# ================== 💾 MONGODB + LOCAL CACHE ==================
USERS_CACHE = {}; REDEEM_CODES = {}
LOCAL_FILE = Path("users.json"); REDEEM_FILE = Path("redeem_codes.json")

try:
    mc = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = mc["tele_intel_bot"]; users_col = db["users"]; redeem_col = db["redeem_codes"]
    print("✅ MongoDB Setup Initialized!", flush=True)
except Exception as e:
    users_col = None; redeem_col = None; db = None

DEFAULTS = {"plan": "trial", "expiry": "", "is_premium": False, "total_searches": 0, "redeemed_codes": []}
for feat in ALL_FEATURE_KEYS:
    DEFAULTS[f"{feat}_free_used"] = 0; DEFAULTS[f"{feat}_daily"] = 0; DEFAULTS[f"{feat}_date"] = ""; DEFAULTS[f"{feat}_total"] = 0

def init_cache():
    global USERS_CACHE, REDEEM_CODES, ACTIVITY_LOGS
    if users_col is not None:
        try:
            for doc in users_col.find(): USERS_CACHE[str(doc["_id"])] = {k: v for k, v in doc.items() if k != "_id"}
        except Exception: pass
    elif LOCAL_FILE.exists():
        try: USERS_CACHE = json.loads(LOCAL_FILE.read_text())
        except Exception: USERS_CACHE = {}
    if redeem_col is not None:
        try:
            for doc in redeem_col.find(): REDEEM_CODES[str(doc["_id"])] = {k: v for k, v in doc.items() if k != "_id"}
        except Exception: pass
    elif REDEEM_FILE.exists():
        try: REDEEM_CODES = json.loads(REDEEM_FILE.read_text())
        except Exception: REDEEM_CODES = {}

init_cache()

def sync_user_background(uid, data):
    def _s():
        if users_col is not None:
            try: users_col.update_one({"_id": str(uid)}, {"$set": data}, upsert=True); return
            except Exception: pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE, indent=2))
        except Exception: pass
    threading.Thread(target=_s, daemon=True).start()

def sync_redeem_background(code, data):
    def _s():
        if redeem_col is not None:
            try: redeem_col.update_one({"_id": code}, {"$set": data}, upsert=True); return
            except Exception: pass
        try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES, indent=2))
        except Exception: pass
    threading.Thread(target=_s, daemon=True).start()

def delete_redeem_background(code):
    def _d():
        if redeem_col is not None:
            try: redeem_col.delete_one({"_id": code})
            except Exception: pass
        try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES, indent=2))
        except Exception: pass
    threading.Thread(target=_d, daemon=True).start()

def get_user(uid):
    uid = str(uid)
    if uid not in USERS_CACHE:
        d = {**DEFAULTS, "added": date.today().isoformat()}
        USERS_CACHE[uid] = d
        sync_user_background(uid, d)
    return USERS_CACHE[uid]

def save_user(uid, data):
    uid = str(uid); USERS_CACHE[uid] = data; sync_user_background(uid, data)

def delete_user(uid):
    uid = str(uid)
    if uid in USERS_CACHE: del USERS_CACHE[uid]
    def _d():
        if users_col is not None:
            try: users_col.delete_one({"_id": uid})
            except Exception: pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE, indent=2))
        except Exception: pass
    threading.Thread(target=_d, daemon=True).start()

def load_users(): return USERS_CACHE

# ================== 🎟️ REDEEM ==================
def create_redeem_code(code, fs, mu):
    code = code.upper().strip()
    REDEEM_CODES[code] = {"free_searches": fs, "max_uses": mu, "used_count": 0, "used_by": [], "created_at": date.today().isoformat(), "active": True}
    sync_redeem_background(code, REDEEM_CODES[code])
    return True

def use_redeem_code(code, user_id):
    code = code.upper().strip(); user_id = str(user_id)
    if code not in REDEEM_CODES: return False, "❌ Invalid!"
    rc = REDEEM_CODES[code]
    if not rc.get("active", True): return False, "❌ Deactivated!"
    if rc["used_count"] >= rc["max_uses"]: return False, "❌ Max reached!"
    if user_id in rc.get("used_by", []): return False, "❌ Already redeemed!"
    ud = get_user(user_id); s = rc["free_searches"]
    for feat in ALL_FEATURE_KEYS: k = f"{feat}_free_used"; ud[k] = max(0, ud.get(k, 0) - s)
    if "redeemed_codes" not in ud: ud["redeemed_codes"] = []
    ud["redeemed_codes"].append(code); save_user(user_id, ud)
    rc["used_count"] += 1; rc["used_by"].append(user_id); REDEEM_CODES[code] = rc; sync_redeem_background(code, rc)
    return True, f"🎉 <code>{code}</code> redeemed!\n🎁 <b>+{s}</b> on ALL!\n📊 <code>{rc['used_count']}/{rc['max_uses']}</code>"

def delete_redeem_code(code):
    code = code.upper().strip()
    if code in REDEEM_CODES: del REDEEM_CODES[code]; delete_redeem_background(code); return True
    return False

def list_redeem_codes(): return REDEEM_CODES

# ================== 👑 PLAN RESOLVERS ==================
def get_plan(ud):
    pk = ud.get("plan", "trial")
    if pk.startswith("custom_"):
        try: d = int(pk.split("_")[1].replace("d", ""))
        except Exception: d = 30
        return {"name": f"Custom ({d}D)", "days": d, "daily_limit": ud.get("custom_limit", 0), "unlimited": ud.get("custom_unlimited", False), "is_free": False}
    return PLANS.get(pk, PLANS["trial"])

def upgrade(uid, pk):
    uid = str(uid); ud = get_user(uid); plan = PLANS.get(pk, PLANS["7days"])
    exp = (date.today() + timedelta(days=plan["days"])).isoformat()
    ud.update({"plan": pk, "expiry": exp, "is_premium": True})
    for feat in ALL_FEATURE_KEYS: ud[f"{feat}_daily"] = 0; ud[f"{feat}_date"] = ""
    save_user(uid, ud); return exp

def upgrade_custom(uid, days, lim, unl):
    uid = str(uid); ud = get_user(uid); exp = (date.today() + timedelta(days=days)).isoformat()
    ud.update({"plan": f"custom_{days}d", "expiry": exp, "is_premium": True, "custom_limit": lim, "custom_unlimited": unl})
    for feat in ALL_FEATURE_KEYS: ud[f"{feat}_daily"] = 0; ud[f"{feat}_date"] = ""
    save_user(uid, ud); return exp

# ================== 📊 LIMIT CHECKERS ==================
def check_feat_access(uid, feat_name, display_title):
    if is_admin(uid): return True, "Admin ∞", 9999, True, "12months"
    ud = get_user(uid); plan = get_plan(ud); pk = ud.get("plan", "trial"); exp_s = ud.get("expiry", ""); is_p = ud.get("is_premium", False)
    fk = f"{feat_name}_free_used"; dk = f"{feat_name}_daily"; dtk = f"{feat_name}_date"
    if is_p and exp_s:
        try:
            exp = date.fromisoformat(exp_s)
            if date.today() > exp:
                fl = max(0, FREE_LIMIT - ud.get(fk, 0))
                return (True, f"Expired|{fl}", 0, False, "trial") if fl > 0 else (False, "Expired!", 0, False, "trial")
            dl = (exp - date.today()).days; lim = plan.get("daily_limit", 0)
            if plan.get("unlimited"): return True, f"{plan['name']}|∞|{dl}d", dl, True, pk
            dr = lim if ud.get(dtk, "") != date.today().isoformat() else max(0, lim - ud.get(dk, 0))
            if dr <= 0: return False, f"Limit!({lim}/day)", dl, True, pk
            return True, f"{plan['name']}|{dr}/{lim}|{dl}d", dl, True, pk
        except Exception: pass
    fl = max(0, FREE_LIMIT - ud.get(fk, 0))
    return (True, f"Free({fl}/{FREE_LIMIT})", 0, False, "trial") if fl > 0 else (False, "Trial over!", 0, False, "trial")

def feat_free_rem(uid, fn):
    if is_admin(uid): return 999999
    return max(0, FREE_LIMIT - get_user(uid).get(f"{fn}_free_used", 0))

def feat_daily_rem(uid, fn):
    if is_admin(uid): return 999999
    ud = get_user(uid); plan = get_plan(ud)
    if plan.get("unlimited"): return 999999
    lim = plan.get("daily_limit", 0)
    if ud.get(f"{fn}_date", "") != date.today().isoformat(): return lim
    return max(0, lim - ud.get(f"{fn}_daily", 0))

def use_feature(uid, feat_name):
    uid = str(uid); ud = get_user(uid); today = date.today().isoformat()
    dk = f"{feat_name}_daily"; dtk = f"{feat_name}_date"; fk = f"{feat_name}_free_used"; tk = f"{feat_name}_total"
    if ud.get(dtk, "") != today: ud[dk] = 0; ud[dtk] = today
    plan = get_plan(ud)
    if not is_admin(int(uid)):
        if plan.get("is_free", True): ud[fk] = ud.get(fk, 0) + 1
        else: ud[dk] = ud.get(dk, 0) + 1
    ud[tk] = ud.get(tk, 0) + 1; ud["total_searches"] = ud.get("total_searches", 0) + 1; save_user(uid, ud)

# ================== 📡 API ENGINE ==================
def _safe_api(fn):
    try: return fn()
    except requests.exceptions.Timeout: return {"ok": False, "error": "⏱️ Timed out!"}
    except requests.exceptions.ConnectionError: return {"ok": False, "error": "🌐 Connection error!"}
    except Exception as e: return {"ok": False, "error": f"❌ {e}"}

def primary_api_call(action, params):
    def c():
        r = requests.get(PRIMARY_API_URL, params={"key": PRIMARY_API_KEY, "action": action, **params}, headers=COMMON_HEADERS, timeout=25)
        if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}"}
        try: data = r.json()
        except Exception: return {"ok": False, "error": "Invalid response."}
        if isinstance(data, dict) and (data.get("status") in [False, "error", 400, 404] or data.get("success") is False):
            return {"ok": False, "error": str(data.get("message") or data.get("error") or "No records.")}
        return {"ok": True, "data": data}
    return _safe_api(c)

def tgid_api_call(tg_id):
    def c():
        r = requests.get(
            TGID_API_URL,
            params={"key": TGID_API_KEY, "action": "tgid", "id": tg_id},
            headers=COMMON_HEADERS,
            timeout=25
        )
        if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}"}
        try: data = r.json()
        except Exception: return {"ok": False, "error": "Invalid response format from TG ID API."}
        if isinstance(data, dict) and (data.get("status") in [False, "error", 400, 404] or data.get("success") is False):
            return {"ok": False, "error": str(data.get("message") or data.get("error") or "No records found.")}
        return {"ok": True, "data": data}
    return _safe_api(c)

def active_phone_api_call(num):
    def c():
        r = requests.get(
            ACTIVE_PHONE_API_URL,
            params={"number": num, "key": ACTIVE_PHONE_API_KEY},
            headers=COMMON_HEADERS,
            timeout=25
        )
        if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}"}
        try: data = r.json()
        except Exception: return {"ok": False, "error": "Invalid response format from Phone API."}
        if isinstance(data, dict) and (data.get("status") in [False, "error", 400, 404] or data.get("success") is False):
            return {"ok": False, "error": str(data.get("message") or data.get("error") or "No records.")}
        return {"ok": True, "data": data}
    return _safe_api(c)

def backup_search_worker_api(term):
    def c():
        r = requests.get(BACKUP_SEARCH_API_URL, params={"pin": BACKUP_PIN, "term": term}, headers=COMMON_HEADERS, timeout=20)
        return {"ok": False, "error": f"HTTP {r.status_code}"} if r.status_code != 200 else {"ok": True, "data": r.json()}
    return _safe_api(c)

def backup_phone_api(num):
    def c():
        r = requests.get(BACKUP_PHONE_API_URL, params={"key": BACKUP_PIN, "number": num}, headers=COMMON_HEADERS, timeout=20)
        return {"ok": False, "error": f"HTTP {r.status_code}"} if r.status_code != 200 else {"ok": True, "data": r.json()}
    return _safe_api(c)

def backup_ifsc_api_call(ifsc_code):
    def c():
        r = requests.get(
            BACKUP_IFSC_API_URL,
            params={"key": BACKUP_IFSC_API_KEY, "ifsc": ifsc_code},
            headers=COMMON_HEADERS,
            timeout=20
        )
        if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}"}
        try: data = r.json()
        except Exception: return {"ok": False, "error": "Invalid response from IFSC backup API."}
        if isinstance(data, dict) and (data.get("status") in [False, "error", 400, 404] or data.get("success") is False):
            return {"ok": False, "error": str(data.get("message") or data.get("error") or "No records found.")}
        return {"ok": True, "data": data}
    return _safe_api(c)

# ================== 🧹 METADATA FILTER ==================
SKIP_K = {"metadata","meta","key_owner","key_usage","key_expiry","key_enabled","daily_limit","daily_used","api_key","key","action","parameters","service","success","violations","timestamp","response_time","response_time_ms","developer","owner","credit","credits","powered_by","source","api","version","status","message","code","time","created_at","updated_at","server","watermark","signature","by","made_by","contact_admin","channel","group","join","advertisement","ads","promo","query","req_id","request_id","execution_time","fizzagirl","nitin","shree","jaani","types","spell","type"}

def should_skip_key(k):
    if not k: return True
    kl = str(k).lower().strip().replace(" ", "_")
    if kl in SKIP_K: return True
    for w in ["metadata","timestamp","response_time","developer","credit","powered","watermark","pheevar","advertisement","promo","channel","server","api_","made_by","encrypted","password","salt","key_","daily_","auth","token","fizza"]:
        if w in kl: return True
    return False

def should_skip_val(v):
    if v is None or v == "": return True
    if isinstance(v, (dict, list)): return len(v) == 0
    vs = str(v).lower().strip()
    if vs in ("","none","null","n/a","na","-","0","0.00","0000-00-00","{}","[]"): return True
    for s in ["@pheevar","pheevar","@lk_","t.me/","telegram.me/","rtfgamming","dm for buy"]:
        if s in vs: return True
    return False

def clean_value_text(v):
    if not isinstance(v, str): return v
    for pat in [r"(?i)📌?\s*dm\s*for\s*buy\s*:\s*@rtfgamming",r"(?i)@rtfgamming",r"(?i)rtfgamming"]:
        v = re.sub(pat, "", v)
    return v.strip().strip("|").strip("-").strip("•").strip("📌").strip()

def em(k):
    k = str(k).lower()
    for kw, e in {"name":"👤","holder":"👤","email":"📧","phone":"📞","mobile":"📞","address":"📍","city":"🏙️","state":"🗺️","country":"🌍","pincode":"📮","upi":"💳","vpa":"💳","bank":"🏦","ifsc":"🏦","account":"🏦","dob":"🎂","gender":"🚻","pan":"🪪","aadhar":"🪪","aadhaar":"🪪","father":"👨","mother":"👩","vehicle":"🚗","rc":"🚗","owner":"👤","model":"🚗","fuel":"⛽","engine":"🔧","chassis":"🔧","registration":"📅","insurance":"📋","rto":"🏢","branch":"🏦","district":"🗺️","verified":"✅","valid":"✅","merchant":"🏪","color":"🎨","weight":"⚖️","number":"🔢","manufacturer":"🏭","blacklist":"⚠️","status":"📊","id":"🆔","username":"👤","user_id":"🆔","followers":"👥","following":"👥","bio":"📝","ip":"🌐","isp":"🏢","weather":"🌤️","temp":"🌡️","humidity":"💧","wind":"💨","imei":"📱","device":"📱"}.items():
        if kw in k: return e
    return "📌"

def clean_metadata(data):
    if isinstance(data, dict):
        cl = {}
        for k, v in data.items():
            if should_skip_key(k): continue
            cv = clean_metadata(v)
            if isinstance(cv, str): cv = clean_value_text(cv)
            if not should_skip_val(cv): cl[k] = cv
        return cl
    elif isinstance(data, list):
        return [cv for i in data if not should_skip_val((cv := clean_value_text(clean_metadata(i)) if isinstance(clean_metadata(i), str) else clean_metadata(i)))]
    return data

def format_universal_result(term, raw_data, icon="🔍"):
    cleaned = clean_metadata(raw_data)
    if not cleaned: return f"<code>{BANNER_MINI}</code>\n\n{icon} <b>Result:</b> <code>{html.escape(str(term))}</code>\n\n<i>No records.</i>"
    records = []
    def extract(item):
        if isinstance(item, dict):
            if any(not isinstance(v, (dict, list)) for v in item.values()): records.append(item)
            for v in item.values():
                if isinstance(v, (dict, list)): extract(v)
        elif isinstance(item, list):
            for s in item: extract(s)
    extract(cleaned)
    unique = []; seen = set()
    for r in records:
        fp = "-".join(sorted(f"{k}:{v}" for k, v in r.items() if not isinstance(v, (dict, list))))
        if fp and fp not in seen: seen.add(fp); unique.append(r)
    if not unique: return f"<code>{BANNER_MINI}</code>\n\n{icon} <b>Result:</b> <code>{html.escape(str(term))}</code>\n\n<i>No records.</i>"
    out = [f"<code>{BANNER_MINI}</code>", f"\n{icon} <b>Result:</b> <code>{html.escape(str(term))}</code>", f"📊 <b>{len(unique)} record(s)</b>", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]
    for idx, rec in enumerate(unique, 1):
        if len(unique) > 1: out.append(f"\n<b>━━ #{idx} ━━</b>")
        for k, v in rec.items():
            if isinstance(v, (dict, list)) or should_skip_key(k) or should_skip_val(v): continue
            emoji = em(k); label = str(k).replace("_"," ").replace("-"," ").title(); kl = str(k).lower().strip()
            if isinstance(v, bool): vs = ("Active ✅" if v else "Inactive ❌") if kl in ["valid","verified","active","success"] else ("Yes ✅" if v else "No ❌")
            elif str(v).lower() == "true": vs = "Yes ✅"
            elif str(v).lower() == "false": vs = "No ❌"
            else: val_str = str(v).strip(); vs = val_str if ("@" in val_str or kl in ["vpa","upi","email","ifsc","code","userid","ip"]) else val_str.title()
            out.append(f"{emoji} <b>{html.escape(label)}:</b> <code>{html.escape(vs)}</code>")
    return "\n".join(out)

# ================== 🕹️ KEYBOARDS ==================
def main_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Phone", callback_data="mode_phone"), InlineKeyboardButton("🪪 Aadhaar", callback_data="mode_aadhaar")],
        [InlineKeyboardButton("💳 UPI", callback_data="mode_upi"), InlineKeyboardButton("📧 Email", callback_data="mode_email")],
        [InlineKeyboardButton("🚗 Vehicle", callback_data="mode_vehicle"), InlineKeyboardButton("🏦 IFSC", callback_data="mode_ifsc")],
        [InlineKeyboardButton("👤 Telegram", callback_data="mode_tg"), InlineKeyboardButton("📸 Instagram", callback_data="mode_insta")],
        [InlineKeyboardButton("📱 IMEI", callback_data="mode_imei"), InlineKeyboardButton("📮 Pincode", callback_data="mode_pin")],
        [InlineKeyboardButton("🌍 Country", callback_data="mode_country"), InlineKeyboardButton("💰 Paytm", callback_data="mode_paytm")],
        [InlineKeyboardButton("🌐 IP", callback_data="mode_ip"), InlineKeyboardButton("🌤️ Weather", callback_data="mode_weather")],
        [InlineKeyboardButton("🆔 TG ID→Info", callback_data="mode_tgid")],
        [InlineKeyboardButton("🎟️ Redeem", callback_data="redeem_info"), InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("📊 Status", callback_data="status"), InlineKeyboardButton("💎 Premium", callback_data="buy")],
        [InlineKeyboardButton("📢 CH1", url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}")],
        [InlineKeyboardButton("📢 CH2", url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton("❓ Help ❓", callback_data="help")]
    ])

def search_sub_kb(uid, feat_name):
    if is_admin(uid): sl, bl = "🔍 Single (Admin)", "📦 Batch (Admin)"
    else:
        ok, _, _, ip, _ = check_feat_access(uid, feat_name, feat_name.title())
        fl = feat_free_rem(uid, feat_name); dr = feat_daily_rem(uid, feat_name); p = get_plan(get_user(uid))
        if ip: sl, bl = ("🟢 Single (∞)", "📦 Batch (∞)") if p.get("unlimited") else (f"🟢 Single ({dr})", f"📦 Batch ({dr})")
        elif fl > 0: sl, bl = f"🆓 Single ({fl})", f"📦 Batch ({fl})"
        else: sl, bl = "🔒 Locked", "🔒 Locked"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(sl, callback_data=f"{feat_name}_single")],
        [InlineKeyboardButton(bl, callback_data=f"{feat_name}_batch")],
        [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Plan", callback_data="admin_add"), InlineKeyboardButton("❌ Remove", callback_data="admin_remove")],
        [InlineKeyboardButton("📅 Set Plan", callback_data="admin_setplan"), InlineKeyboardButton("📋 Users", callback_data="admin_list")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats"), InlineKeyboardButton("🆓 Monitor", callback_data="admin_free_monitor")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🎟️ Create Code", callback_data="admin_redeem_create"), InlineKeyboardButton("📋 Codes", callback_data="admin_redeem_list")],
        [InlineKeyboardButton("🗑️ Del Code", callback_data="admin_redeem_delete")],
        [InlineKeyboardButton("🔧 Maintenance", callback_data="admin_maintenance")],
        [InlineKeyboardButton("📋 Activity Logs", callback_data="admin_logs")],
        [InlineKeyboardButton("🛡️ Protected IDs", callback_data="admin_protect")],
        [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
    ])

def logs_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Recent 20 Logs", callback_data="logs_recent")],
        [InlineKeyboardButton("🔍 Search by User ID", callback_data="logs_by_user")],
        [InlineKeyboardButton("📱 Phone Logs", callback_data="logs_feat_phone"), InlineKeyboardButton("🪪 Aadhaar Logs", callback_data="logs_feat_aadhaar")],
        [InlineKeyboardButton("💳 UPI Logs", callback_data="logs_feat_upi"), InlineKeyboardButton("🚗 Vehicle Logs", callback_data="logs_feat_vehicle")],
        [InlineKeyboardButton("👤 TG Logs", callback_data="logs_feat_tg"), InlineKeyboardButton("📸 Insta Logs", callback_data="logs_feat_insta")],
        [InlineKeyboardButton("🆔 TG ID Logs", callback_data="logs_feat_tgid")],
        [InlineKeyboardButton("📊 Log Stats", callback_data="logs_stats")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_back")]
    ])

def protect_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Protected Entry", callback_data="protect_add")],
        [InlineKeyboardButton("❌ Remove Protected Entry", callback_data="protect_remove")],
        [InlineKeyboardButton("📋 List All Protected", callback_data="protect_list")],
        [InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_back")]
    ])

def maintenance_kb():
    full_status = "🔴 ON" if is_full_maintenance() else "🟢 OFF"
    buttons = [[InlineKeyboardButton(f"🔧 Full Bot: {full_status}", callback_data="maint_toggle_full")]]
    feat_buttons = []
    for feat in ALL_FEATURE_KEYS:
        st = "🔴" if is_feature_maintenance(feat) else "🟢"
        feat_buttons.append(InlineKeyboardButton(f"{st} {feat.title()}", callback_data=f"maint_toggle_{feat}"))
    for i in range(0, len(feat_buttons), 2):
        buttons.append(feat_buttons[i:i+2])
    buttons.append([InlineKeyboardButton("🔙 Admin", callback_data="admin_back")])
    return InlineKeyboardMarkup(buttons)

def back_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
def buy_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("💬 Buy", url=f"https://t.me/{OWNER_CONTACT.replace('@','')}")], [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
def plan_kb(pf):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉 7D-₹50", callback_data=f"{pf}_7days")],[InlineKeyboardButton("🥈 30D-₹130", callback_data=f"{pf}_30days")],
        [InlineKeyboardButton("🥇 6M-₹300", callback_data=f"{pf}_6months")],[InlineKeyboardButton("💎 12M-₹799", callback_data=f"{pf}_12months")],
        [InlineKeyboardButton("⚙️ Custom", callback_data=f"{pf}_custom")],[InlineKeyboardButton("❌ Cancel", callback_data="admin_back")]
    ])

# ================== 🚀 BULLETPROOF START COMMAND ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return ConversationHandler.END
    
    print(f"⚡ [START TRIGGERED] User: {user.id} (@{user.username or 'N/A'})", flush=True)
    
    try:
        if is_full_maintenance() and not is_admin(user.id):
            if update.callback_query: await safe_edit(update.callback_query, MAINTENANCE_MSG_FULL, back_kb())
            else: await safe_reply(update, MAINTENANCE_MSG_FULL)
            return ConversationHandler.END
            
        get_user(user.id)
        u_name = safe_name(user)
        
        if not is_admin(user.id):
            if not await check_joined(context, user.id):
                t = f"<code>{BANNER}</code>\n\n🔴 <b>Force Join Required</b>\n\nWelcome <b>{u_name}</b>!\n\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}\n\nVerify 👇"
                if update.callback_query: await safe_edit(update.callback_query, t, force_join_kb())
                else: await safe_reply(update, t, force_join_kb())
                return ConversationHandler.END
                
        if is_admin(user.id):
            maint_note = "\n🔧 <b>MAINTENANCE: ON</b>\n" if is_full_maintenance() else ""
            prot_count = len(PROTECTED_ENTRIES)
            t = f"<code>{BANNER}</code>\n\n👋 Boss <b>{u_name}</b>! 🛡️ <code>ADMIN</code>{maint_note}\n\nAll: 💎 ∞ | 🛡️ Protected: <code>{prot_count}</code>\n\n👇 <b>Select:</b>"
        else:
            ud = get_user(user.id); plan = get_plan(ud); ip = ud.get("is_premium", False); exp = ud.get("expiry", "")
            lines = []
            for feat in ALL_FEATURE_KEYS[:8]:
                if is_feature_maintenance(feat): lines.append(f"🛠️ {feat.title()}: <code>Maintenance</code>"); continue
                fl = feat_free_rem(user.id, feat)
                if ip and exp:
                    try:
                        ed = date.fromisoformat(exp); dl = (ed - date.today()).days
                        if dl >= 0:
                            if plan.get("unlimited"): lines.append(f"🟢 {feat.title()}: <code>💎∞ ({dl}d)</code>")
                            else: dr = feat_daily_rem(user.id, feat); lines.append(f"🟢 {feat.title()}: <code>💎{dr}/{plan.get('daily_limit',0)} ({dl}d)</code>")
                        else: lines.append(f"🔴 {feat.title()}: <code>Expired({fl}/{FREE_LIMIT})</code>")
                    except Exception: lines.append(f"⚪ {feat.title()}: <code>Unknown</code>")
                else: lines.append(f"🆓 {feat.title()}: <code>{fl}/{FREE_LIMIT}</code>")
            t = f"<code>{BANNER}</code>\n\n👋 <b>{u_name}</b>!\n\n" + "\n".join(lines) + f"\n\n💡 <b>1 Plan = 15+ tools!</b>\n🎟️ <code>/redeem CODE</code>\n\n👇 <b>Select:</b>"
            
        if update.callback_query: await safe_edit(update.callback_query, t, main_kb(user.id))
        else: await safe_reply(update, t, main_kb(user.id))
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n👋 Welcome! Click below:", main_kb(user.id))
        
    return ConversationHandler.END

async def verify_join(update, context):
    q = update.callback_query; await q.answer("Verifying...")
    if await check_joined(context, q.from_user.id): await start(update, context)
    else: await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n⚠️ <b>Join both!</b>\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb())

async def main_menu_cb(update, context):
    context.user_data.clear()
    if update.callback_query: await update.callback_query.answer()
    await start(update, context); return ConversationHandler.END

async def cancel(update, context):
    context.user_data.clear()
    await safe_reply(update, "❌ Cancelled.", main_kb(update.effective_user.id)); return ConversationHandler.END

# ================== 🛠️ SEARCH EXECUTION WITH HARDCODED PROTECTION ==================
async def execute_search(update, context, feat_name, action, param_key, search_value, icon, display_value):
    u = update.effective_user
    if is_full_maintenance() and not is_admin(u.id):
        await safe_reply(update, MAINTENANCE_MSG_FULL, back_kb()); return
    if is_feature_maintenance(feat_name):
        await safe_reply(update, maintenance_msg_feature(feat_name), back_kb()); return
    
    # 🛡️ UNIVERSAL PROTECTION CHECK (Hardcoded + Regular)
    blocked, block_msg, log_status = is_blocked_search(feat_name, search_value)
    if blocked:
        add_activity_log(u.id, u.username, u.first_name, feat_name, display_value, log_status)
        await safe_reply(update, block_msg, back_kb())
        # Alert admins
        for admin_id in ADMIN_IDS:
            try:
                alert_type = "🔥 ADMIN ID SEARCH" if log_status == "blocked_admin_id" else ("🔥 OWNER NUMBER SEARCH" if log_status == "blocked_owner_number" else "🚨 PROTECTED SEARCH")
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"{alert_type} <b>ATTEMPT!</b>\n\n"
                        f"👤 User: <code>{u.id}</code> (@{u.username or 'N/A'})\n"
                        f"📛 Name: {html.escape(u.first_name or 'Unknown')}\n"
                        f"🔍 Feature: <b>{feat_name.upper()}</b>\n"
                        f"🔑 Search: <code>{html.escape(str(display_value))}</code>\n"
                        f"⏰ Time: <code>{datetime.now(IST).strftime('%d-%m-%Y %H:%M:%S')}</code>"
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass
        return
    
    ok, st, _, _, _ = check_feat_access(u.id, feat_name, feat_name.title())
    if not ok:
        await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n🔒 <b>Restricted!</b>\n{st}\n\n🎟️ <code>/redeem CODE</code>\n💎 {OWNER_CONTACT}", buy_kb()); return

    msg = await safe_reply(update, "⏳ <i>Initializing...</i>")
    
    if feat_name == "tgid":
        api_task = asyncio.get_event_loop().run_in_executor(None, lambda: tgid_api_call(search_value))
    elif feat_name == "phone":
        api_task = asyncio.get_event_loop().run_in_executor(None, lambda: primary_api_call(action, {param_key: search_value}))
    elif feat_name == "ifsc":
        api_task = asyncio.get_event_loop().run_in_executor(None, lambda: backup_ifsc_api_call(search_value))
    else:
        api_task = asyncio.get_event_loop().run_in_executor(None, lambda: primary_api_call(action, {param_key: search_value}))
        
    anim_task = animated_search(msg, icon, display_value)
    res, _ = await asyncio.gather(api_task, anim_task)
    
    if not res["ok"] and feat_name == "phone":
        res = await asyncio.get_event_loop().run_in_executor(None, lambda: active_phone_api_call(search_value))
        if not res["ok"]:
            res = await asyncio.get_event_loop().run_in_executor(None, lambda: backup_phone_api(search_value))
    elif not res["ok"] and feat_name == "email":
        res = await asyncio.get_event_loop().run_in_executor(None, lambda: backup_search_worker_api(search_value))

    if res["ok"]:
        use_feature(u.id, feat_name)
        add_activity_log(u.id, u.username, u.first_name, feat_name, display_value, "success")
        text = format_universal_result(display_value, res["data"], icon)
        final = f"⚡ <b>Report!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{text}"
        if msg: await safe_edit(msg, final, main_kb(u.id))
        else: await safe_reply(update, final, main_kb(u.id))
    else:
        add_activity_log(u.id, u.username, u.first_name, feat_name, display_value, "failed")
        err = f"<code>{BANNER_MINI}</code>\n\n🔴 <b>Failed!</b>\n\n❌ <code>{html.escape(str(display_value))}</code>\n📛 {html.escape(str(res['error']))}"
        if msg: await safe_edit(msg, err, back_kb())
        else: await safe_reply(update, err, back_kb())

async def execute_batch(update, context, feat_name, action, param_key, items, icon):
    u = update.effective_user; total = len(items)
    
    if is_full_maintenance() and not is_admin(u.id):
        await safe_reply(update, MAINTENANCE_MSG_FULL, back_kb()); return
    if is_feature_maintenance(feat_name):
        await safe_reply(update, maintenance_msg_feature(feat_name), back_kb()); return

    msg = await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n📦 <b>Batch:</b> <b>{total}</b>\n\n<code>[░░░░░░░░░░░░░░░░░░░░]</code> 0%")
    for idx, item in enumerate(items, 1):
        # 🛡️ Check hardcoded/regular protection in batch
        blocked, block_msg, log_status = is_blocked_search(feat_name, item)
        if blocked:
            add_activity_log(u.id, u.username, u.first_name, feat_name, item, log_status)
            await safe_reply(update, block_msg)
            # Alert admins on batch block
            for admin_id in ADMIN_IDS:
                try:
                    alert_type = "🔥 ADMIN ID SEARCH (Batch)" if log_status == "blocked_admin_id" else ("🔥 OWNER NUMBER SEARCH (Batch)" if log_status == "blocked_owner_number" else "🚨 PROTECTED SEARCH (Batch)")
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=(
                            f"{alert_type} <b>ATTEMPT!</b>\n\n"
                            f"👤 User: <code>{u.id}</code> (@{u.username or 'N/A'})\n"
                            f"🔍 Feature: <b>{feat_name.upper()}</b>\n"
                            f"🔑 Item: <code>{html.escape(str(item))}</code>\n"
                            f"⏰ <code>{datetime.now(IST).strftime('%d-%m-%Y %H:%M:%S')}</code>"
                        ),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
            continue
        
        pct = int((idx / total) * 100); filled = int(pct / 5); bar = "█" * filled + "░" * (20 - filled)
        await safe_edit(msg, f"<code>{BANNER_MINI}</code>\n\n📦 <code>{html.escape(str(item))}</code>\n📊 <b>{idx}/{total}</b>\n\n<code>[{bar}]</code> <b>{pct}%</b>")
        
        if feat_name == "tgid":
            res = tgid_api_call(item)
        elif feat_name == "phone":
            res = primary_api_call(action, {param_key: item})
            if not res["ok"]: 
                res = active_phone_api_call(item)
            if not res["ok"]: 
                res = backup_phone_api(item)
        elif feat_name == "ifsc":
            res = backup_ifsc_api_call(item)
        else:
            res = primary_api_call(action, {param_key: item})
            
        if res["ok"]:
            use_feature(u.id, feat_name)
            add_activity_log(u.id, u.username, u.first_name, feat_name, item, "success")
            await safe_reply(update, format_universal_result(item, res["data"], icon))
        else:
            add_activity_log(u.id, u.username, u.first_name, feat_name, item, "failed")
            await safe_reply(update, f"❌ <code>{html.escape(str(item))}</code>: {html.escape(str(res['error']))}")
        await asyncio.sleep(0.8)
    if msg: await safe_edit(msg, f"<code>{BANNER_MINI}</code>\n\n⚡ <b>Done!</b> ✅ <b>{total}</b>\n<code>[████████████████████]</code> <b>100%</b>", main_kb(u.id))

# ================== 📱 MODE PROMPTERS ==================
async def generic_mode_prompt(update, context, feat_name, display_title, icon):
    q = update.callback_query; await q.answer(); u = q.from_user
    if is_full_maintenance() and not is_admin(u.id): await safe_edit(q, MAINTENANCE_MSG_FULL, back_kb()); return
    if is_feature_maintenance(feat_name): await safe_edit(q, maintenance_msg_feature(feat_name), back_kb()); return
    if not is_admin(u.id) and not await check_joined(context, u.id): await safe_edit(q, "⚠️ Join!", force_join_kb()); return
    await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n{icon} <b>{display_title}</b> {icon}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nChoose:", search_sub_kb(u.id, feat_name))

async def mode_phone(u, c): await generic_mode_prompt(u, c, "phone", "Phone Tracker", "📱")
async def mode_email(u, c): await generic_mode_prompt(u, c, "email", "Email OSINT", "📧")
async def mode_upi(u, c): await generic_mode_prompt(u, c, "upi", "UPI Verifier", "💳")
async def mode_aadhaar(u, c): await generic_mode_prompt(u, c, "aadhaar", "Aadhaar Lookup", "🪪")
async def mode_vehicle(u, c): await generic_mode_prompt(u, c, "vehicle", "Vehicle RC", "🚗")
async def mode_ifsc(u, c): await generic_mode_prompt(u, c, "ifsc", "IFSC Lookup", "🏦")
async def mode_tg(u, c): await generic_mode_prompt(u, c, "tg", "Telegram Info", "👤")
async def mode_insta(u, c): await generic_mode_prompt(u, c, "insta", "Instagram Info", "📸")
async def mode_imei(u, c): await generic_mode_prompt(u, c, "imei", "IMEI Tracker", "📱")
async def mode_pin(u, c): await generic_mode_prompt(u, c, "pin", "Pincode Info", "📮")
async def mode_country(u, c): await generic_mode_prompt(u, c, "country", "Country Info", "🌍")
async def mode_paytm(u, c): await generic_mode_prompt(u, c, "paytm", "Paytm Info", "💰")
async def mode_ip(u, c): await generic_mode_prompt(u, c, "ip", "IP Lookup", "🌐")
async def mode_weather(u, c): await generic_mode_prompt(u, c, "weather", "Weather", "🌤️")
async def mode_tgid(u, c): await generic_mode_prompt(u, c, "tgid", "TG ID → Phone/Info", "🆔")

# ================== 📥 SEARCH HANDLERS ==================
def make_handler_pair(feat_name, action, param_key, icon, single_state, batch_state, prompt_single, prompt_batch, validator_fn=None):
    example = FEATURE_EXAMPLES.get(feat_name, "")
    
    async def single_start(update, context):
        q = update.callback_query; await q.answer()
        if is_full_maintenance() and not is_admin(q.from_user.id): 
            await safe_edit(q, MAINTENANCE_MSG_FULL, back_kb()); return ConversationHandler.END
        if is_feature_maintenance(feat_name): 
            await safe_edit(q, maintenance_msg_feature(feat_name), back_kb()); return ConversationHandler.END
        ok, st, _, _, _ = check_feat_access(q.from_user.id, feat_name, feat_name.title())
        if not ok: 
            await safe_edit(q, f"🔒 {st}", buy_kb()); return ConversationHandler.END
        await safe_edit(q, 
            f"<code>{BANNER_SEARCH}</code>\n\n"
            f"{icon} <b>{prompt_single}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{example}\n\n"
            f"✍️ <i>Send your input or /cancel:</i>"
        )
        return single_state

    async def batch_start(update, context):
        q = update.callback_query; await q.answer()
        if is_full_maintenance() and not is_admin(q.from_user.id): 
            await safe_edit(q, MAINTENANCE_MSG_FULL, back_kb()); return ConversationHandler.END
        if is_feature_maintenance(feat_name): 
            await safe_edit(q, maintenance_msg_feature(feat_name), back_kb()); return ConversationHandler.END
        ok, st, _, _, _ = check_feat_access(q.from_user.id, feat_name, feat_name.title())
        if not ok: 
            await safe_edit(q, f"🔒 {st}", buy_kb()); return ConversationHandler.END
        
        batch_ex_map = {
            "phone":    "9876543210, 9123456789, 9012345678",
            "email":    "user1@gmail.com, user2@yahoo.com",
            "upi":      "ram@paytm, 9876543210@ybl, rohit@oksbi",
            "aadhaar":  "123456789012, 987654321098",
            "vehicle":  "DL8CAF5030, MH12AB1234, KA05MJ6789",
            "ifsc":     "SBIN0001234, HDFC0000123, ICIC0004567",
            "tg":       "5057489358, 1968142314",
            "insta":    "cristiano, leomessi, virat.kohli",
            "imei":     "354751093234567, 123456789012345",
            "pin":      "110001, 400001, 500001",
            "country":  "India, United States, Canada",
            "paytm":    "9876543210, 9123456789",
            "ip":       "8.8.8.8, 1.1.1.1, 142.250.191.14",
            "weather":  "Mumbai, Delhi, London",
            "tgid":     "8771611214, 5057489358, 1968142314",
        }
        batch_ex = batch_ex_map.get(feat_name, "item1, item2, item3")
        
        await safe_edit(q, 
            f"<code>{BANNER_SEARCH}</code>\n\n"
            f"{icon} <b>{prompt_batch}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 <b>Batch Example:</b>\n<code>{batch_ex}</code>\n\n"
            f"ℹ️ Max <b>15 items</b>, comma-separated.\n"
            f"✍️ <i>Send list or /cancel:</i>"
        )
        return batch_state

    async def single_process(update, context):
        raw = update.message.text.strip()
        val = validator_fn(raw) if validator_fn else raw
        if not val: 
            await safe_reply(update, 
                f"❌ <b>Invalid Format!</b>\n\n{example}\n\nTry again or /cancel:"
            )
            return single_state
        await execute_search(update, context, feat_name, action, param_key, val, icon, val)
        return ConversationHandler.END

    async def batch_process(update, context):
        raw_list = [x.strip() for x in update.message.text.split(",") if x.strip()]
        valid_items = [validator_fn(x) if validator_fn else x for x in raw_list]
        valid_items = [x for x in valid_items if x][:15]
        if not valid_items: 
            await safe_reply(update, 
                f"❌ <b>No Valid Items Found!</b>\n\n{example}\n\nRetry or /cancel:"
            )
            return batch_state
        await execute_batch(update, context, feat_name, action, param_key, valid_items, icon)
        return ConversationHandler.END
        
    return single_start, batch_start, single_process, batch_process

def clean_num(x):
    c = x.replace(" ","").replace("-","").replace("+","")
    return c if c.isdigit() and 7 <= len(c) <= 15 else None
def clean_aadhaar(x):
    c = x.replace(" ","").replace("-","")
    return c if c.isdigit() and len(c) == 12 else None
def clean_rc(x):
    c = x.upper().replace(" ","").replace("-","")
    return c if len(c) >= 4 else None
def clean_ifsc(x):
    c = x.upper().replace(" ","")
    return c if len(c) == 11 else None
def clean_tgid(x):
    c = x.strip()
    return c if c.isdigit() and len(c) >= 4 else None

(p_ss, p_bs, p_sp, p_bp) = make_handler_pair("phone","num","number","📱",PHONE_SINGLE,PHONE_BATCH,"Enter Phone:","Phones (comma-sep):",clean_num)
(e_ss, e_bs, e_sp, e_bp) = make_handler_pair("email","email","email","📧",EMAIL_SINGLE,EMAIL_BATCH,"Enter Email:","Emails (comma-sep):",lambda x: x.strip() if "@" in x else None)
(u_ss, u_bs, u_sp, u_bp) = make_handler_pair("upi","upiinfo","upi","💳",UPI_SINGLE,UPI_BATCH,"Enter UPI:","UPIs (comma-sep):",lambda x: x.strip() if "@" in x else None)
(a_ss, a_bs, a_sp, a_bp) = make_handler_pair("aadhaar","aadhar","aadhar","🪪",AADHAAR_SINGLE,AADHAAR_BATCH,"Enter Aadhaar:","Aadhaars (comma-sep):",clean_aadhaar)
(v_ss, v_bs, v_sp, v_bp) = make_handler_pair("vehicle","vehicle-v1","rc","🚗",VEHICLE_SINGLE,VEHICLE_BATCH,"Enter RC:","RCs (comma-sep):",clean_rc)
(i_ss, i_bs, i_sp, i_bp) = make_handler_pair("ifsc","ifsc-info","ifsc","🏦",IFSC_SINGLE,IFSC_BATCH,"Enter IFSC:","IFSCs (comma-sep):",clean_ifsc)
(tg_ss, tg_bs, tg_sp, tg_bp) = make_handler_pair("tg","tg-registration","userid","👤",TG_SINGLE,TG_BATCH,"Enter TG ID:","TG IDs (comma-sep):",lambda x: x.strip() if x.strip().isdigit() else None)
(in_ss, in_bs, in_sp, in_bp) = make_handler_pair("insta","instagram-user","username","📸",INSTA_SINGLE,INSTA_BATCH,"Enter Username:","Usernames (comma-sep):",lambda x: x.strip().lstrip("@"))
(im_ss, im_bs, im_sp, im_bp) = make_handler_pair("imei","imei-info","imei_num","📱",IMEI_SINGLE,IMEI_BATCH,"Enter IMEI:","IMEIs (comma-sep):",lambda x: x.strip() if x.strip().isdigit() else None)
(pin_ss, pin_bs, pin_sp, pin_bp) = make_handler_pair("pin","pincode-info","pincode","📮",PIN_SINGLE,PIN_BATCH,"Enter Pincode:","Pincodes (comma-sep):",lambda x: x.strip() if len(x.strip())==6 else None)
(c_ss, c_bs, c_sp, c_bp) = make_handler_pair("country","country-info","name","🌍",COUNTRY_SINGLE,COUNTRY_BATCH,"Enter Country:","Countries (comma-sep):",lambda x: x.strip())
(pm_ss, pm_bs, pm_sp, pm_bp) = make_handler_pair("paytm","paytm","info","💰",PAYTM_SINGLE,PAYTM_BATCH,"Enter Paytm No:","Numbers (comma-sep):",clean_num)
(ip_ss, ip_bs, ip_sp, ip_bp) = make_handler_pair("ip","ip-v1","query","🌐",IP_SINGLE,IP_BATCH,"Enter IP:","IPs (comma-sep):",lambda x: x.strip())
(w_ss, w_bs, w_sp, w_bp) = make_handler_pair("weather","weather","search","🌤️",WEATHER_SINGLE,WEATHER_BATCH,"Enter City:","Cities (comma-sep):",lambda x: x.strip().title())
(tgid_ss, tgid_bs, tgid_sp, tgid_bp) = make_handler_pair("tgid","tgid","id","🆔",TGID_SINGLE,TGID_BATCH,"Enter Telegram ID:","TG IDs (comma-sep):",clean_tgid)

# ================== 👤 PROFILE / STATUS / HELP / BUY ==================
async def profile(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user; ud = get_user(u.id); plan = get_plan(ud)
    txt = f"<code>{BANNER_MINI}</code>\n\n👤 <b>PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🆔 <code>{u.id}</code>\n👤 <b>{safe_name(u)}</b>\n📦 <b>{plan['name']}</b>\n📅 <code>{ud.get('expiry','Free')}</code>\n🔍 <code>{ud.get('total_searches',0)}</code>\n🎟️ <code>{len(ud.get('redeemed_codes',[]))}</code>"
    await safe_edit(q, txt, back_kb())

async def status_check(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user
    if is_admin(u.id): await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🛡️ <code>ADMIN</code> — All ∞", back_kb()); return
    lines = []
    for feat in ALL_FEATURE_KEYS:
        if is_feature_maintenance(feat): lines.append(f"• <b>{feat.title()}</b>: <code>🛠️ Maint</code>"); continue
        ok, st, _, _, _ = check_feat_access(u.id, feat, feat.title())
        lines.append(f"• <b>{feat.title()}</b>: <code>{st}</code>")
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n📊 <b>STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(lines) + f"\n\n💰 {OWNER_CONTACT}\n🆔 <code>{u.id}</code>", back_kb())

async def help_menu(update, context):
    q = update.callback_query; await q.answer()
    txt = (
        f"<code>{BANNER}</code>\n\n"
        f"❓ <b>HELP & FEATURE EXAMPLES</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 <b>15+ Powerful OSINT Tools</b>\n\n"
        f"📱 <b>Phone:</b> <code>9876543210</code>\n"
        f"🪪 <b>Aadhaar:</b> <code>123456789012</code>\n"
        f"💳 <b>UPI:</b> <code>ram@paytm</code>\n"
        f"📧 <b>Email:</b> <code>user@gmail.com</code>\n"
        f"🚗 <b>Vehicle:</b> <code>DL8CAF5030</code>\n"
        f"🏦 <b>IFSC:</b> <code>SBIN0001234</code>\n"
        f"👤 <b>Telegram:</b> <code>5057489358</code>\n"
        f"📸 <b>Instagram:</b> <code>cristiano</code>\n"
        f"📱 <b>IMEI:</b> <code>354751093234567</code>\n"
        f"📮 <b>Pincode:</b> <code>110001</code>\n"
        f"🌍 <b>Country:</b> <code>India</code>\n"
        f"💰 <b>Paytm:</b> <code>9876543210</code>\n"
        f"🌐 <b>IP:</b> <code>8.8.8.8</code>\n"
        f"🌤️ <b>Weather:</b> <code>Mumbai</code>\n"
        f"🆔 <b>TG ID→Info:</b> <code>8771611214</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>Plans:</b>\n"
        f"  🥉 7D → ₹50 (10/day)\n"
        f"  🥈 30D → ₹130 (20/day)\n"
        f"  🥇 6M → ₹300 (35/day)\n"
        f"  💎 12M → ₹799 (∞ Unlimited)\n\n"
        f"🎟️ <b>Redeem:</b> <code>/redeem CODE</code>\n"
        f"📲 <b>Contact:</b> {OWNER_CONTACT}"
    )
    await safe_edit(q, txt, back_kb())

async def buy(update, context):
    q = update.callback_query; await q.answer()
    await safe_edit(q, f"<code>{BANNER}</code>\n\n💎 <b>PREMIUM</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🥉 7D-₹50 (10/day)\n🥈 30D-₹130 (20/day)\n🥇 6M-₹300 (35/day)\n💎 12M-₹799 (∞)\n\n📲 {OWNER_CONTACT}\n🆔 <code>{q.from_user.id}</code>", buy_kb())

async def redeem_command(update, context):
    user = update.effective_user
    if not user: return
    if not context.args: await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n🎟️ <code>/redeem CODE</code>", back_kb()); return
    ok, msg = use_redeem_code(context.args[0].upper().strip(), user.id)
    await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n{msg}", main_kb(user.id))

async def redeem_info(update, context):
    q = update.callback_query; await q.answer()
    await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n🎟️ <b>Redeem</b>\n\n<code>/redeem CODE</code>", back_kb())

# ================== 👑 ADMIN PANEL ==================
async def admin_panel(update, context):
    if not is_admin(update.effective_user.id): await safe_reply(update, "❌ Admin only!"); return ConversationHandler.END
    users = load_users(); t = len(users); p = sum(1 for v in users.values() if v.get("is_premium"))
    maint_status = "🔴 ON" if is_full_maintenance() else "🟢 OFF"
    feat_maint = sum(1 for f in ALL_FEATURE_KEYS if is_feature_maintenance(f))
    prot_count = len(PROTECTED_ENTRIES)
    hc_count = len(HARDCODED_PROTECTED_NUMBERS) + len(HARDCODED_PROTECTED_ADMIN_IDS)
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n🛠️ <b>ADMIN</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🛡️ <code>{len(ADMIN_IDS)}</code> | 👥 <code>{t}</code> | 💎 <code>{p}</code> | 🆓 <code>{t-p}</code>\n"
        f"🎟️ <code>{len(list_redeem_codes())}</code> | 📋 Logs: <code>{len(ACTIVITY_LOGS)}</code>\n"
        f"🔧 Full: <b>{maint_status}</b> | 🛠️ Features: <code>{feat_maint}</code>\n"
        f"🛡️ Dynamic Protected: <code>{prot_count}</code> | 🔒 Hardcoded: <code>{hc_count}</code>"
    )
    if update.callback_query: await safe_edit(update.callback_query, txt, admin_kb())
    else: await safe_reply(update, txt, admin_kb())
    return ConversationHandler.END

async def admin_back(u, c): await admin_panel(u, c)

# ================== 🛡️ ADMIN PROTECTION HANDLERS ==================
async def admin_protect_menu(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    prot_count = len(PROTECTED_ENTRIES)
    hc_nums = ", ".join(HARDCODED_PROTECTED_NUMBERS)
    hc_ids = ", ".join(HARDCODED_PROTECTED_ADMIN_IDS)
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"🛡️ <b>PROTECTED IDS/NUMBERS MANAGER</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Dynamic Protected: <code>{prot_count}</code>\n\n"
        f"🔒 <b>HARDCODED (Cannot be removed):</b>\n"
        f"  📞 Numbers: <code>{hc_nums}</code>\n"
        f"  🆔 Admin IDs: <code>{hc_ids}</code>\n\n"
        f"⚠️ <b>How it works:</b>\n"
        f"• Add phone, TG ID, Aadhaar, UPI, etc.\n"
        f"• <b>ALL features</b> will be blocked for that entry.\n"
        f"• Admin gets alert when someone searches it.\n\n"
        f"👇 <b>Select action:</b>"
    )
    await safe_edit(q, txt, protect_kb())

async def protect_add_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, 
        f"<code>{BANNER_MINI}</code>\n\n"
        f"🛡️ <b>ADD PROTECTED ENTRIES</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Send entries to protect (comma-separated):\n\n"
        f"📌 <b>Examples:</b>\n"
        f"• <code>9876543210</code>, <code>5057489358</code>, <code>ram@paytm</code>\n\n"
        f"✍️ <i>Send entries or /cancel:</i>"
    )
    return ADMIN_PROTECT_ADD

async def protect_add_process(update, context):
    raw = update.message.text.strip()
    entries = [x.strip() for x in raw.split(",") if x.strip()]
    if not entries:
        await safe_reply(update, "❌ No valid entries! Try again or /cancel:")
        return ADMIN_PROTECT_ADD
    added, already = [], []
    for entry in entries:
        clean = entry.replace(" ", "").replace("-", "").replace("+", "") if entry.replace(" ", "").replace("-", "").replace("+", "").isdigit() else entry.strip()
        if clean in PROTECTED_ENTRIES: already.append(clean)
        else: save_protected_entry(clean); added.append(clean)
    txt = f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>PROTECTION UPDATE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if added:
        txt += f"✅ <b>Added ({len(added)}):</b>\n" + "\n".join(f"  • <code>{html.escape(a)}</code>" for a in added) + "\n"
    if already:
        txt += f"\n⚠️ <b>Already Protected ({len(already)}):</b>\n" + "\n".join(f"  • <code>{html.escape(a)}</code>" for a in already) + "\n"
    txt += f"\n📊 Total Protected: <code>{len(PROTECTED_ENTRIES)}</code>"
    await safe_reply(update, txt, protect_kb())
    return ConversationHandler.END

async def protect_remove_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    if not PROTECTED_ENTRIES:
        await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n📭 No dynamic protected entries to remove.\n\n<i>Note: Hardcoded entries cannot be removed.</i>", protect_kb())
        return ConversationHandler.END
    entries_list = sorted(list(PROTECTED_ENTRIES))[:30]
    entries_txt = "\n".join(f"  • <code>{html.escape(e)}</code>" for e in entries_list)
    extra = f"\n  ... and {len(PROTECTED_ENTRIES) - 30} more" if len(PROTECTED_ENTRIES) > 30 else ""
    await safe_edit(q, 
        f"<code>{BANNER_MINI}</code>\n\n"
        f"❌ <b>REMOVE PROTECTED ENTRIES</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Current entries:</b>\n{entries_txt}{extra}\n\n"
        f"Send entries to remove (comma-separated) or /cancel:"
    )
    return ADMIN_PROTECT_REMOVE

async def protect_remove_process(update, context):
    raw = update.message.text.strip()
    entries = [x.strip() for x in raw.split(",") if x.strip()]
    if not entries:
        await safe_reply(update, "❌ No entries provided! Try again or /cancel:")
        return ADMIN_PROTECT_REMOVE
    removed, not_found = [], []
    for entry in entries:
        clean = entry.replace(" ", "").replace("-", "").replace("+", "") if entry.replace(" ", "").replace("-", "").replace("+", "").isdigit() else entry.strip()
        if clean in PROTECTED_ENTRIES: remove_protected_entry(clean); removed.append(clean)
        else: not_found.append(clean)
    txt = f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>REMOVAL UPDATE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if removed:
        txt += f"✅ <b>Removed ({len(removed)}):</b>\n" + "\n".join(f"  • <code>{html.escape(r)}</code>" for r in removed) + "\n"
    if not_found:
        txt += f"\n❌ <b>Not Found ({len(not_found)}):</b>\n" + "\n".join(f"  • <code>{html.escape(n)}</code>" for n in not_found) + "\n"
    txt += f"\n📊 Remaining Protected: <code>{len(PROTECTED_ENTRIES)}</code>"
    await safe_reply(update, txt, protect_kb())
    return ConversationHandler.END

async def protect_list(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    txt = f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>PROTECTED ENTRIES LIST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    txt += f"🔒 <b>HARDCODED NUMBERS:</b>\n"
    for n in HARDCODED_PROTECTED_NUMBERS:
        txt += f"  📞 <code>{n}</code>\n"
    txt += f"\n🔒 <b>HARDCODED ADMIN IDS:</b>\n"
    for i in HARDCODED_PROTECTED_ADMIN_IDS:
        txt += f"  🆔 <code>{i}</code>\n"
    txt += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    txt += f"📊 <b>DYNAMIC ENTRIES ({len(PROTECTED_ENTRIES)}):</b>\n\n"
    if not PROTECTED_ENTRIES:
        txt += "<i>No dynamic entries. Add some via ➕ button!</i>"
    else:
        entries_list = sorted(list(PROTECTED_ENTRIES))
        for idx, entry in enumerate(entries_list, 1):
            line = f"{idx}. <code>{html.escape(entry)}</code>\n"
            if len(txt) + len(line) > 3900:
                txt += f"\n⚠️ <i>...and {len(entries_list) - idx + 1} more (truncated)</i>"
                break
            txt += line
    await safe_edit(q, txt, protect_kb())

# ================== 📋 ADMIN LOGS HANDLERS ==================
async def admin_logs_menu(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"📋 <b>ACTIVITY LOGS CENTER</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Total Logs Stored: <code>{len(ACTIVITY_LOGS)}</code>\n"
        f"💾 Max Capacity: <code>200 (Auto-cleans &gt; 3 days)</code>\n\n"
        f"👇 <b>Select log view:</b>"
    )
    await safe_edit(q, txt, logs_kb())

async def logs_recent(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    logs = get_recent_logs(20)
    txt = format_logs_text(logs, "📋 RECENT 20 ACTIVITY LOGS")
    await safe_edit(q, txt, InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="logs_recent")],
        [InlineKeyboardButton("🔙 Logs Menu", callback_data="admin_logs")]
    ]))

async def logs_by_user_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🔍 <b>SEARCH USER LOGS</b>\n\nEnter User's Telegram ID or /cancel:")
    return ADMIN_LOGS_USER_ID

async def logs_by_user_process(update, context):
    uid_text = update.message.text.strip()
    if not uid_text.isdigit():
        await safe_reply(update, "❌ Invalid ID! Enter numbers or /cancel:")
        return ADMIN_LOGS_USER_ID
    uid = int(uid_text)
    logs = get_user_logs(uid, 15)
    if not logs:
        txt = f"<code>{BANNER_MINI}</code>\n\n📭 <b>No logs found for user</b> <code>{uid}</code>"
    else:
        uname = logs[0].get("username", "N/A")
        fname = logs[0].get("first_name", "Unknown")
        txt = format_logs_text(logs, f"📋 LOGS FOR {fname} (@{uname}) [{uid}]")
    await safe_reply(update, txt, InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Logs Menu", callback_data="admin_logs")],
        [InlineKeyboardButton("🔙 Admin", callback_data="admin_back")]
    ]))
    return ConversationHandler.END

async def logs_by_feature(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    data = q.data
    feat = data.replace("logs_feat_", "")
    if feat not in ALL_FEATURE_KEYS:
        await safe_edit(q, "❌ Invalid feature.", logs_kb()); return
    logs = get_feature_logs(feat, 15)
    txt = format_logs_text(logs, f"📋 {feat.upper()} FEATURE LOGS")
    await safe_edit(q, txt, InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data=f"logs_feat_{feat}")],
        [InlineKeyboardButton("🔙 Logs Menu", callback_data="admin_logs")]
    ]))

async def logs_stats(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    logs = list(ACTIVITY_LOGS)
    total = len(logs)
    success = sum(1 for l in logs if l["status"] == "success")
    failed = sum(1 for l in logs if l["status"] == "failed")
    blocked = sum(1 for l in logs if "blocked" in l["status"])
    blocked_admin = sum(1 for l in logs if l["status"] == "blocked_admin_id")
    blocked_owner = sum(1 for l in logs if l["status"] == "blocked_owner_number")
    feat_counts = {}
    for l in logs:
        feat = l["feature"]; feat_counts[feat] = feat_counts.get(feat, 0) + 1
    unique_users = len(set(l["user_id"] for l in logs))
    top_feats = sorted(feat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_txt = "\n".join(f"  • <b>{f.title()}</b>: <code>{c}</code>" for f, c in top_feats) if top_feats else "  <i>No data</i>"
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"📊 <b>LOG STATISTICS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 Total Active (3D): <code>{total}</code>\n"
        f"✅ Successful: <code>{success}</code>\n"
        f"❌ Failed: <code>{failed}</code>\n"
        f"🛡️ Total Blocks: <code>{blocked}</code>\n"
        f"  🔥 Admin ID Blocks: <code>{blocked_admin}</code>\n"
        f"  🔥 Owner Number Blocks: <code>{blocked_owner}</code>\n"
        f"👥 Unique Users: <code>{unique_users}</code>\n\n"
        f"🔝 <b>Top Features:</b>\n{top_txt}\n\n"
        f"📅 <code>{datetime.now(IST).strftime('%d-%m-%Y %H:%M IST')}</code>"
    )
    await safe_edit(q, txt, InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="logs_stats")],
        [InlineKeyboardButton("🔙 Logs Menu", callback_data="admin_logs")]
    ]))

# ================== 🔧 MAINTENANCE HANDLERS ==================
async def admin_maintenance(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    txt = f"<code>{BANNER_MINI}</code>\n\n🔧 <b>MAINTENANCE CONTROL</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{get_maintenance_status()}\n\n👇 <b>Toggle any option:</b>"
    await safe_edit(q, txt, maintenance_kb())

async def maint_toggle_handler(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    data = q.data
    if data == "maint_toggle_full":
        new_state = toggle_full_maintenance()
        logger.info(f"Full Maintenance toggled to: {new_state} by admin {q.from_user.id}")
    elif data.startswith("maint_toggle_"):
        feat = data.replace("maint_toggle_", "")
        if feat in ALL_FEATURE_KEYS:
            new_state = toggle_feature_maintenance(feat)
            logger.info(f"Feature '{feat}' Maintenance toggled to: {new_state} by admin {q.from_user.id}")
    txt = f"<code>{BANNER_MINI}</code>\n\n🔧 <b>MAINTENANCE CONTROL</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{get_maintenance_status()}\n\n👇 <b>Toggle any option:</b>"
    await safe_edit(q, txt, maintenance_kb())

# ================== ADMIN PLAN HANDLERS ==================
async def adm_add_s(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "➕ <b>Enter User ID:</b> (or /cancel)"); return ADMIN_ADD_ID

async def adm_add_id(u, c):
    uid = u.message.text.strip()
    if not uid.isdigit(): await safe_reply(u, "❌ Invalid! /cancel:"); return ADMIN_ADD_ID
    c.user_data["admin_uid"] = uid; await safe_reply(u, f"User: <code>{uid}</code>\nPlan:", plan_kb("plan")); return ADMIN_ADD_PLAN

async def adm_add_plan(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "admin_back": await admin_panel(u, c); return ConversationHandler.END
    pm = {"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk = pm.get(q.data, "7days"); uid = c.user_data.get("admin_uid"); plan = PLANS.get(pk)
    exp = upgrade(int(uid), pk); dl = "∞" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(q, f"✅ <b>Activated!</b>\n🆔 <code>{uid}</code>\n📦 <b>{plan['name']}</b>\n📅 <code>{exp}</code>\n⚡ <code>{dl}</code>", admin_kb()); return ConversationHandler.END

async def adm_rem_s(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "❌ <b>Enter User ID to remove:</b> (or /cancel)"); return ADMIN_REM_ID

async def adm_rem_p(u, c):
    uid = u.message.text.strip(); delete_user(uid)
    await safe_reply(u, f"✅ <code>{uid}</code> removed!", admin_kb()); return ConversationHandler.END

async def adm_sp_s(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "📅 <b>Enter User ID:</b> (or /cancel)"); return ADMIN_EXP_ID

async def adm_sp_id(u, c):
    uid = u.message.text.strip(); c.user_data["admin_uid"] = uid
    await safe_reply(u, f"User: <code>{uid}</code>\nPlan:", plan_kb("plan")); return ADMIN_EXP_PLAN

async def adm_sp_set(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "admin_back": await admin_panel(u, c); return ConversationHandler.END
    pm = {"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk = pm.get(q.data, "7days"); uid = c.user_data.get("admin_uid"); plan = PLANS.get(pk)
    exp = upgrade(int(uid), pk)
    await safe_edit(q, f"✅ <b>Updated!</b>\n🆔 <code>{uid}</code>\n📦 <b>{plan['name']}</b>\n📅 <code>{exp}</code>", admin_kb()); return ConversationHandler.END

# ================== 📖 ADMIN USERS PAGINATION SYSTEM ==================
async def adm_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not is_admin(q.from_user.id): 
        return

    # Parse target page from callback data
    data = q.data
    page = 0
    if data.startswith("admin_list_page_"):
        try:
            page = int(data.split("_")[-1])
        except ValueError:
            page = 0

    users = load_users()
    if not users: 
        await safe_edit(q, "📋 No users in database.", admin_kb())
        return

    # Ensure stable sorting layout
    def sort_key(item):
        try:
            return int(item[0])
        except ValueError:
            return item[0]

    sorted_users = sorted(users.items(), key=sort_key)
    total_users = len(sorted_users)
    
    USERS_PER_PAGE = 30
    total_pages = (total_users + USERS_PER_PAGE - 1) // USERS_PER_PAGE
    if page < 0: page = 0
    if page >= total_pages: page = max(0, total_pages - 1)

    start_idx = page * USERS_PER_PAGE
    end_idx = start_idx + USERS_PER_PAGE
    current_page_users = sorted_users[start_idx:end_idx]

    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"📋 <b>ALL USERS LIST ({total_users})</b>\n"
        f"📖 <b>Page:</b> <code>{page + 1}/{total_pages}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for uid, info in current_page_users:
        ts = info.get("total_searches", 0)
        if int(uid) in ADMIN_IDS: 
            st = "🛡️ Admin"
        elif info.get("is_premium") and info.get("expiry"):
            try: 
                ed = date.fromisoformat(info["expiry"])
                st = f"💎 {(ed-date.today()).days}d" if date.today() <= ed else "🔴 Expired"
            except Exception: 
                st = "⚪ Error"
        else: 
            st = "🆓 Free"
        txt += f"👤 <code>{uid}</code> | {st} | 🔍 <code>{ts}</code>\n"

    # Navigation layout
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"admin_list_page_{page - 1}"))
    if end_idx < total_users:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"admin_list_page_{page + 1}"))

    kbd = []
    if nav_buttons:
        kbd.append(nav_buttons)
    kbd.append([InlineKeyboardButton("🔙 Admin Menu", callback_data="admin_back")])

    await safe_edit(q, txt, InlineKeyboardMarkup(kbd))

async def adm_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    users = load_users()
    ts = sum(v.get("total_searches",0) for v in users.values())
    act = sum(1 for u2, v in users.items() if v.get("is_premium") and int(u2) not in ADMIN_IDS)
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"📊 <b>BOT SYSTEM STATS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total Members: <code>{len(users)}</code>\n"
        f"🔍 Total Searches Executed: <code>{ts}</code>\n"
        f"💎 Active Premium Users: <code>{act}</code>\n"
        f"🎟️ Active Redeem Codes: <code>{len(list_redeem_codes())}</code>\n"
        f"🛡️ Dynamic Protected: <code>{len(PROTECTED_ENTRIES)}</code>\n"
        f"🔒 Hardcoded Numbers: <code>{len(HARDCODED_PROTECTED_NUMBERS)}</code>\n"
        f"🔒 Hardcoded Admin IDs: <code>{len(HARDCODED_PROTECTED_ADMIN_IDS)}</code>\n\n"
        f"📅 Date: <code>{datetime.now(IST).strftime('%d-%m-%Y %H:%M:%S')} IST</code>"
    )
    await safe_edit(q, txt, admin_kb())

async def adm_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    users = load_users()
    free = [v for u2, v in users.items() if not v.get("is_premium") and int(u2) not in ADMIN_IDS]
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"🆓 <b>FREE USER MONITOR</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Active Trial/Free Users: <code>{len(free)}</code>\n\n"
        f"💡 Tip: Create promo codes to convert them into premium members!"
    )
    await safe_edit(q, txt, admin_kb())

async def bc_start(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n📢 <b>BROADCAST</b>\n\nSend message or /cancel:"); return ADMIN_BROADCAST_MSG

async def bc_msg(u, c):
    m = u.message.text.strip(); c.user_data["bc"] = m; users = load_users()
    await safe_reply(u, f"📢 <b>Preview:</b>\n\n{html.escape(m)}\n\n👥 <b>{len(users)}</b> users\nConfirm?",
        InlineKeyboardMarkup([[InlineKeyboardButton("✅ Send", callback_data="broadcast_confirm")],[InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]]))
    return ADMIN_BROADCAST_CONFIRM

async def bc_confirm(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "broadcast_cancel": await safe_edit(q, "❌ Cancelled.", admin_kb()); c.user_data.pop("bc",None); return ConversationHandler.END
    msg = c.user_data.get("bc",""); users = load_users(); total = len(users)
    bt = f"<code>{BANNER_MINI}</code>\n\n📢 <b>ANNOUNCEMENT</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{html.escape(msg)}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n💬 {OWNER_CONTACT}"
    sm = await safe_reply(u, f"🚀 <code>{total}</code>..."); s, f2, b, ct = 0, 0, 0, 0
    for uid in users:
        ct += 1
        try: await c.bot.send_message(chat_id=int(uid), text=bt, parse_mode="HTML"); s += 1
        except Exception as e:
            if any(w in str(e).lower() for w in ["blocked","forbidden","not found"]): b += 1
            else: f2 += 1
        if ct % 15 == 0 or ct == total:
            await safe_edit(sm, f"🚀 <code>{ct}/{total}</code>|✅<code>{s}</code>|🚫<code>{b}</code>|❌<code>{f2}</code>")
        await asyncio.sleep(0.05)
    await safe_reply(u, f"✅ <b>Done!</b> 👥<code>{total}</code>|✅<code>{s}</code>|🚫<code>{b}</code>|❌<code>{f2}</code>", admin_kb())
    c.user_data.pop("bc",None); return ConversationHandler.END

async def custom_s(u, c):
    q = u.callback_query; await q.answer()
    await safe_edit(q, "⚙️ <b>Days:</b> /cancel"); return ADMIN_CUSTOM_DAYS

async def custom_days(u, c):
    t = u.message.text.strip()
    if not t.isdigit() or int(t) <= 0: await safe_reply(u, "❌ Invalid!"); return ADMIN_CUSTOM_DAYS
    c.user_data["cd"] = int(t); await safe_reply(u, f"📅 <b>{t}D</b>\nDaily limit (<code>0</code>=∞):"); return ADMIN_CUSTOM_LIMIT

async def custom_limit(u, c):
    t = u.message.text.strip()
    if not t.isdigit(): await safe_reply(u, "❌!"); return ADMIN_CUSTOM_LIMIT
    lim = int(t); unl = (lim == 0); days = c.user_data.get("cd"); uid = c.user_data.get("admin_uid")
    exp = upgrade_custom(int(uid), days, lim, unl)
    await safe_reply(u, f"⚙️ <b>Set!</b> <code>{uid}</code>|{days}D|<code>{exp}</code>|<code>{'∞' if unl else f'{lim}/d'}</code>", admin_kb())
    c.user_data.pop("cd",None); c.user_data.pop("admin_uid",None); return ConversationHandler.END

async def admin_redeem_create_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, f"🎟️ <b>Code (3-20):</b> /cancel"); return REDEEM_CREATE_CODE

async def admin_redeem_code_input(update, context):
    code = update.message.text.strip().upper()
    if len(code) < 3 or len(code) > 20 or not code.isalnum(): await safe_reply(update, "❌ Invalid!"); return REDEEM_CREATE_CODE
    if code in REDEEM_CODES: await safe_reply(update, f"❌ <code>{code}</code> exists!"); return REDEEM_CREATE_CODE
    context.user_data["nrc"] = code; await safe_reply(update, f"<code>{code}</code>\n🎁 Searches?"); return REDEEM_CREATE_SEARCHES

async def admin_redeem_searches_input(update, context):
    t = update.message.text.strip()
    if not t.isdigit() or int(t) <= 0: await safe_reply(update, "❌ Positive!"); return REDEEM_CREATE_SEARCHES
    context.user_data["nrs"] = int(t); await safe_reply(update, f"<b>+{t}</b>\n🎁 Max users?"); return REDEEM_CREATE_LIMIT

async def admin_redeem_limit_input(update, context):
    t = update.message.text.strip()
    if not t.isdigit() or int(t) <= 0: await safe_reply(update, "❌ Positive!"); return REDEEM_CREATE_LIMIT
    mu = int(t); code = context.user_data.get("nrc"); fs = context.user_data.get("nrs")
    create_redeem_code(code, fs, mu)
    await safe_reply(update, f"🎉 <b>Created!</b> <code>{code}</code> | +{fs} | 👥{mu}\n<code>/redeem {code}</code>", admin_kb())
    context.user_data.pop("nrc",None); context.user_data.pop("nrs",None); return ConversationHandler.END

async def admin_redeem_list(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    codes = list_redeem_codes()
    if not codes: await safe_edit(q, "📋 No codes.", admin_kb()); return
    txt = f"<code>{BANNER_MINI}</code>\n\n🎟️ <b>CODES</b>\n\n"
    for code, info in codes.items():
        st = "🟢" if info.get("active",True) and info["used_count"] < info["max_uses"] else "🔴"
        txt += f"{st} <code>{code}</code>|🎁<code>+{info['free_searches']}</code>|👥<code>{info['used_count']}/{info['max_uses']}</code>\n"
    await safe_edit(q, txt[:4000], admin_kb())

async def admin_redeem_delete_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    codes = list_redeem_codes()
    if not codes: await safe_edit(q, "📋 No codes.", admin_kb()); return ConversationHandler.END
    txt = f"🗑️ <b>DELETE</b>\n\n" + "".join(f"• <code>{c}</code>\n" for c in codes) + "\nEnter code or /cancel:"
    await safe_edit(q, txt); return REDEEM_DELETE_CODE

async def admin_redeem_delete_input(update, context):
    code = update.message.text.strip().upper()
    if delete_redeem_code(code): await safe_reply(update, f"✅ <code>{code}</code> deleted!", admin_kb())
    else: await safe_reply(update, f"❌ <code>{code}</code> not found!", admin_kb())
    return ConversationHandler.END

async def error_handler(update, context):
    if isinstance(context.error, RetryAfter):
        return
    logger.error(f"❌ Global Error: {context.error}")

async def global_incoming_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        text = update.message.text if update.message else ("Callback: " + update.callback_query.data if update.callback_query else "Other")
        print(f"📩 [RAW UPDATE RECEIVED] User: {update.effective_user.id} -> {text}", flush=True)

async def general_fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await start(update, context)

def notify_admin_startup():
    time.sleep(3)
    for admin_id in ADMIN_IDS:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": admin_id,
                    "text": "🚀 <b>ZERO TRACE Bot is ONLINE & READY!</b>\n\n🛡️ Hardcoded Protection: ACTIVE\n  🔒 Admin IDs: 5057489358, 1968142314\n  🔒 Numbers: 9792574835, 7991927061\n\n👉 Tap /start to open menu.",
                    "parse_mode": "HTML"
                },
                timeout=15
            )
            print(f"✅ Startup ping delivered directly to Admin {admin_id} in Telegram!", flush=True)
        except Exception as e:
            print(f"⚠️ Startup ping delivery notice: {e}", flush=True)

# ================== 🏁 MAIN ==================
def main():
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=false", timeout=15)
        bot_data = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=15).json()
        if bot_data.get("ok"):
            b_user = bot_data["result"]["username"]
            print("\n" + "="*50, flush=True)
            print(f"🤖 CONNECTED BOT: @{b_user}", flush=True)
            print(f"👉 CLICK TO START: https://t.me/{b_user}", flush=True)
            print("="*50 + "\n", flush=True)
    except Exception as e:
        print(f"⚠️ Pre-init check error: {e}", flush=True)

    threading.Thread(target=start_webserver, daemon=True).start()
    print("🌐 Keep-alive server running on port 8080!", flush=True)

    threading.Thread(target=cleanup_old_logs_loop, daemon=True).start()
    print("🧹 Logs Auto-Cleanup Engine Started!", flush=True)

    threading.Thread(target=notify_admin_startup, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    C = ConversationHandler; CQ = CallbackQueryHandler; MH = MessageHandler; CMD = CommandHandler
    F = filters.TEXT & ~filters.COMMAND; UF = [CMD("cancel", cancel), CMD("start", start)]

    load_settings()
    load_protected_entries()

    print(f"🔒 HARDCODED PROTECTED NUMBERS: {HARDCODED_PROTECTED_NUMBERS}", flush=True)
    print(f"🔒 HARDCODED PROTECTED ADMIN IDS: {HARDCODED_PROTECTED_ADMIN_IDS}", flush=True)

    app.add_handler(TypeHandler(Update, global_incoming_tracker), group=-1)

    app.add_handler(CMD("start", start), group=0)
    app.add_handler(CMD("cancel", cancel), group=0)
    app.add_handler(CMD("admin", admin_panel), group=0)
    app.add_handler(CMD("redeem", redeem_command), group=0)

    convs = [
        C(entry_points=[CQ(p_ss,pattern="^phone_single$")],states={PHONE_SINGLE:[MH(F,p_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(p_bs,pattern="^phone_batch$")],states={PHONE_BATCH:[MH(F,p_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(e_ss,pattern="^email_single$")],states={EMAIL_SINGLE:[MH(F,e_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(e_bs,pattern="^email_batch$")],states={EMAIL_BATCH:[MH(F,e_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(u_ss,pattern="^upi_single$")],states={UPI_SINGLE:[MH(F,u_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(u_bs,pattern="^upi_batch$")],states={UPI_BATCH:[MH(F,u_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(a_ss,pattern="^aadhaar_single$")],states={AADHAAR_SINGLE:[MH(F,a_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(a_bs,pattern="^aadhaar_batch$")],states={AADHAAR_BATCH:[MH(F,a_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(v_ss,pattern="^vehicle_single$")],states={VEHICLE_SINGLE:[MH(F,v_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(v_bs,pattern="^vehicle_batch$")],states={VEHICLE_BATCH:[MH(F,v_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(i_ss,pattern="^ifsc_single$")],states={IFSC_SINGLE:[MH(F,i_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(i_bs,pattern="^ifsc_batch$")],states={IFSC_BATCH:[MH(F,i_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(tg_ss,pattern="^tg_single$")],states={TG_SINGLE:[MH(F,tg_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(tg_bs,pattern="^tg_batch$")],states={TG_BATCH:[MH(F,tg_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(in_ss,pattern="^insta_single$")],states={INSTA_SINGLE:[MH(F,in_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(in_bs,pattern="^insta_batch$")],states={INSTA_BATCH:[MH(F,in_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(im_ss,pattern="^imei_single$")],states={IMEI_SINGLE:[MH(F,im_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(im_bs,pattern="^imei_batch$")],states={IMEI_BATCH:[MH(F,im_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(pin_ss,pattern="^pin_single$")],states={PIN_SINGLE:[MH(F,pin_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(pin_bs,pattern="^pin_batch$")],states={PIN_BATCH:[MH(F,pin_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(c_ss,pattern="^country_single$")],states={COUNTRY_SINGLE:[MH(F,c_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(c_bs,pattern="^country_batch$")],states={COUNTRY_BATCH:[MH(F,c_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(pm_ss,pattern="^paytm_single$")],states={PAYTM_SINGLE:[MH(F,pm_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(pm_bs,pattern="^paytm_batch$")],states={PAYTM_BATCH:[MH(F,pm_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(ip_ss,pattern="^ip_single$")],states={IP_SINGLE:[MH(F,ip_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(ip_bs,pattern="^ip_batch$")],states={IP_BATCH:[MH(F,ip_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(w_ss,pattern="^weather_single$")],states={WEATHER_SINGLE:[MH(F,w_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(w_bs,pattern="^weather_batch$")],states={WEATHER_BATCH:[MH(F,w_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(tgid_ss,pattern="^tgid_single$")],states={TGID_SINGLE:[MH(F,tgid_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(tgid_bs,pattern="^tgid_batch$")],states={TGID_BATCH:[MH(F,tgid_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_add_s,pattern="^admin_add$")],states={ADMIN_ADD_ID:[MH(F,adm_add_id)],ADMIN_ADD_PLAN:[CQ(custom_s,pattern="^plan_custom$"),CQ(adm_add_plan,pattern="^plan_")],ADMIN_CUSTOM_DAYS:[MH(F,custom_days)],ADMIN_CUSTOM_LIMIT:[MH(F,custom_limit)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_rem_s,pattern="^admin_remove$")],states={ADMIN_REM_ID:[MH(F,adm_rem_p)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_sp_s,pattern="^admin_setplan$")],states={ADMIN_EXP_ID:[MH(F,adm_sp_id)],ADMIN_EXP_PLAN:[CQ(custom_s,pattern="^plan_custom$"),CQ(adm_sp_set,pattern="^plan_")],ADMIN_CUSTOM_DAYS:[MH(F,custom_days)],ADMIN_CUSTOM_LIMIT:[MH(F,custom_limit)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(bc_start,pattern="^admin_broadcast$")],states={ADMIN_BROADCAST_MSG:[MH(F,bc_msg)],ADMIN_BROADCAST_CONFIRM:[CQ(bc_confirm,pattern="^broadcast_(confirm|cancel)$")]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(admin_redeem_create_start,pattern="^admin_redeem_create$")],states={REDEEM_CREATE_CODE:[MH(F,admin_redeem_code_input)],REDEEM_CREATE_SEARCHES:[MH(F,admin_redeem_searches_input)],REDEEM_CREATE_LIMIT:[MH(F,admin_redeem_limit_input)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(admin_redeem_delete_start,pattern="^admin_redeem_delete$")],states={REDEEM_DELETE_CODE:[MH(F,admin_redeem_delete_input)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(logs_by_user_start,pattern="^logs_by_user$")],states={ADMIN_LOGS_USER_ID:[MH(F,logs_by_user_process)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(protect_add_start,pattern="^protect_add$")],states={ADMIN_PROTECT_ADD:[MH(F,protect_add_process)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(protect_remove_start,pattern="^protect_remove$")],states={ADMIN_PROTECT_REMOVE:[MH(F,protect_remove_process)]},fallbacks=UF,per_message=False,allow_reentry=True),
    ]

    for cv in convs: app.add_handler(cv)
    app.add_error_handler(error_handler)

    callbacks = [
        ("mode_phone",mode_phone),("mode_email",mode_email),("mode_upi",mode_upi),
        ("mode_aadhaar",mode_aadhaar),("mode_vehicle",mode_vehicle),("mode_ifsc",mode_ifsc),
        ("mode_tg",mode_tg),("mode_insta",mode_insta),("mode_imei",mode_imei),
        ("mode_pin",mode_pin),("mode_country",mode_country),("mode_paytm",mode_paytm),
        ("mode_ip",mode_ip),("mode_weather",mode_weather),("mode_tgid",mode_tgid),
        ("redeem_info",redeem_info),("profile",profile),("status",status_check),
        ("help",help_menu),("buy",buy),
        ("admin_stats",adm_stats),("admin_back",admin_back),("admin_free_monitor",adm_monitor),
        ("admin_redeem_list",admin_redeem_list),("admin_maintenance",admin_maintenance),
        ("admin_logs",admin_logs_menu),("logs_recent",logs_recent),("logs_stats",logs_stats),
        ("admin_protect",admin_protect_menu),("protect_list",protect_list),
        ("main_menu",main_menu_cb),("verify_join",verify_join)
    ]
    for pattern, fn in callbacks:
        app.add_handler(CQ(fn, pattern=f"^{pattern}$"))
    
    # Custom Paginated User List Handlers
    app.add_handler(CQ(adm_list, pattern=r"^admin_list$"))
    app.add_handler(CQ(adm_list, pattern=r"^admin_list_page_\d+$"))
    
    app.add_handler(CQ(maint_toggle_handler, pattern=r"^maint_toggle_"))
    app.add_handler(CQ(logs_by_feature, pattern=r"^logs_feat_"))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, general_fallback_handler), group=99)

    print("╔══════════════════════════════════════════════════════╗", flush=True)
    print("║  ☠️ ZERO TRACE + HARDCODED PROTECTION ACTIVE ☠️      ║", flush=True)
    print("╚══════════════════════════════════════════════════════╝", flush=True)
    
    app.run_polling(drop_pending_updates=False)

if __name__ == "__main__":
    main()

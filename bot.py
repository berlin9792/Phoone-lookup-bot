#!/usr/bin/env python3
"""
🔍 Ultimate Intelligence Bot - ZERO TRACE (BULLETPROOF INSTANT RESPONSE)
+ CUSTOM ERROR POPUP DIALOG SYSTEM
+ UPDATED PRICING PLANS
+ SMART SILENT GROUP HANDLING
+ ADVANCED PHOTO/TEXT BROADCASTER
"""

import json, os, threading, requests, logging, asyncio, re, time, html, secrets, sys
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from collections import deque
from flask import Flask
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter, BadRequest, TelegramError, Forbidden
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

# ================== 💎 UPDATED PLANS CONFIG ==================
PLANS = {
    "trial": {"name": "Trial", "days": 0, "price": 0, "daily_limit": 0, "unlimited": False, "is_free": True},
    "7days": {"name": "7 Days", "days": 7, "price": 70, "daily_limit": 5, "unlimited": False, "is_free": False},
    "30days": {"name": "30 Days", "days": 30, "price": 170, "daily_limit": 10, "unlimited": False, "is_free": False},
    "6months": {"name": "6 Months", "days": 180, "price": 350, "daily_limit": 25, "unlimited": False, "is_free": False},
    "12months": {"name": "12 Months", "days": 365, "price": 849, "daily_limit": 999999, "unlimited": True, "is_free": False},
}

# ================== 🛡️ HARDCODED PROTECTED ADMIN IDS & NUMBERS ==================
HARDCODED_PROTECTED_NUMBERS = {"9792574835", "7991927061"}
HARDCODED_PROTECTED_ADMIN_IDS = {"5057489358", "1968142314"}

# ================== 🎨 CUSTOM ERROR POPUP DIALOG SYSTEM ==================
def make_popup(title, icon, lines, footer=None):
    W = 35
    top = f"╭{'─' * (W + 2)}╮"
    bot = f"╰{'─' * (W + 2)}╯"
    sep = f"├{'─' * (W + 2)}┤"
    
    def pad(text, width=W):
        visible_len = len(text)
        padding = max(0, width - visible_len)
        return f"│ {text}{' ' * padding} │"
    
    empty = pad("", W)
    header_text = f"{icon} {title}"
    header_line = pad(header_text, W)
    
    body_lines = []
    for line in lines:
        while len(line) > W - 2:
            body_lines.append(pad(line[:W-2], W))
            line = line[W-2:]
        body_lines.append(pad(line, W))
    
    footer_line = pad(footer, W) if footer else ""
    
    parts = [f"<code>{top}", header_line, sep, empty]
    for bl in body_lines:
        parts.append(bl)
    parts.append(empty)
    if footer_line:
        parts.append(sep)
        parts.append(footer_line)
    parts.append(f"{bot}</code>")
    
    return "\n".join(parts)

def popup_force_join():
    return make_popup(
        "CHANNEL JOIN REQUIRED", "📢",
        [
            "🔴 You must join both",
            "   channels to use this bot.",
            "",
            f"  1️⃣ {FORCE_JOIN_CHANNEL_1}",
            f"  2️⃣ {FORCE_JOIN_CHANNEL_2}",
            "",
            "👇 Join & tap Verify below."
        ],
        f"📲 Help: {OWNER_CONTACT}"
    )

def popup_full_maintenance():
    return make_popup(
        "BOT UNDER MAINTENANCE", "🛠️",
        [
            "⚠️ All services are",
            "   temporarily unavailable.",
            "",
            "⏳ Please try again later.",
            "🔧 Our team is working on it."
        ],
        f"📲 Contact: {OWNER_CONTACT}"
    )

def popup_feature_maintenance(feat_name):
    return make_popup(
        f"{feat_name.upper()} - MAINTENANCE", "🛠️",
        [
            f"⚠️ The {feat_name.title()} feature",
            "   is currently under",
            "   maintenance.",
            "",
            "✅ Other features may still",
            "   be available.",
            "",
            "⏳ Try again later."
        ],
        f"📲 Contact: {OWNER_CONTACT}"
    )

def popup_access_denied(status_text):
    return make_popup(
        "ACCESS DENIED", "🚫",
        [
            "🔒 Your access is restricted!",
            "",
            f"📊 Status: {status_text}",
            "",
            "💎 Upgrade to Premium for",
            "   more searches.",
            "",
            "🎟️ Or use: /redeem CODE"
        ],
        f"💰 Buy: {OWNER_CONTACT}"
    )

def popup_protected_entity():
    return make_popup(
        "PROTECTED ENTITY", "🛡️",
        [
            "⛔ This number/ID is",
            "   PROTECTED and cannot",
            "   be searched.",
            "",
            "🚫 All lookup operations",
            "   are BLOCKED.",
            "",
            "⚠️ Repeated attempts may",
            "   result in BAN."
        ],
        f"📲 Contact: {OWNER_CONTACT}"
    )

def popup_admin_id_blocked():
    return make_popup(
        "CHAL NIKAL BSDK!", "🔥",
        [
            "😡 bkl aukat mt bhul apni",
            "",
            "⛔ Admin ki ID search karne",
            "   ki himmat kaise hui?",
            "",
            "🔨 Ban ho jayega bhosdike!",
            "",
            "🚫 PERMANENTLY BLOCKED"
        ],
        f"📲 Rone ja: {OWNER_CONTACT}"
    )

def popup_owner_number_blocked():
    return make_popup(
        "ABE CHUTIYE!", "🔥",
        [
            "😡 bhadwe number leke gand",
            "   me dalega mera?",
            "",
            "⛔ Owner ka number search",
            "   karta hai bsdk?",
            "",
            "🔨 Aukat me reh warna",
            "   ban permanent!"
        ],
        f"📲 Rone ja: {OWNER_CONTACT}"
    )

def popup_invalid_input(feat_name, example_text):
    return make_popup(
        "INVALID INPUT", "❌",
        [
            f"🚫 Wrong format for",
            f"   {feat_name.upper()} search!",
            "",
            f"📝 {example_text}",
            "",
            "✍️ Try again or /cancel"
        ]
    )

def popup_api_failed(search_term, error_msg):
    safe_term = str(search_term)[:20]
    safe_err = str(error_msg)[:25]
    return make_popup(
        "SEARCH FAILED", "🔴",
        [
            f"❌ Query: {safe_term}",
            "",
            f"📛 Error: {safe_err}",
            "",
            "🔄 Try again later or",
            "   use a different query."
        ],
        f"📲 Report: {OWNER_CONTACT}"
    )

def popup_not_admin():
    return make_popup(
        "UNAUTHORIZED", "⛔",
        [
            "🚫 You are NOT an admin!",
            "",
            "🔒 This command is only",
            "   for authorized admins.",
            "",
            "⚠️ Access attempt logged."
        ],
        f"📲 Contact: {OWNER_CONTACT}"
    )

def popup_expired_plan():
    return make_popup(
        "PLAN EXPIRED", "⏰",
        [
            "🔴 Your premium plan has",
            "   EXPIRED!",
            "",
            "💎 Renew now to continue",
            "   daily searches.",
            "",
            "🎟️ Or use: /redeem CODE"
        ],
        f"💰 Renew: {OWNER_CONTACT}"
    )

def popup_daily_limit():
    return make_popup(
        "DAILY LIMIT REACHED", "📊",
        [
            "🔒 You have used all your",
            "   searches for today!",
            "",
            "⏰ Limit resets at midnight.",
            "",
            "💎 Upgrade for higher daily",
            "   searches or unlimited."
        ],
        f"💰 Upgrade: {OWNER_CONTACT}"
    )

def popup_trial_over():
    return make_popup(
        "FREE TRIAL OVER", "🆓",
        [
            "🔒 Your free trial searches",
            "   are all used up!",
            "",
            "💎 Get Premium to access",
            "   15+ OSINT tools.",
            "",
            "🎟️ Or use: /redeem CODE"
        ],
        f"💰 Buy: {OWNER_CONTACT}"
    )

def dismiss_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✖ Dismiss", callback_data="dismiss_popup")],
        [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
    ])

def dismiss_buy_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Buy Premium", url=f"https://t.me/{OWNER_CONTACT.replace('@','')}")],
        [InlineKeyboardButton("✖ Dismiss", callback_data="dismiss_popup")],
        [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
    ])

def dismiss_only_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✖ OK", callback_data="dismiss_popup")]
    ])

# ================== NORMALIZATION & PROTECTION HELPERS ==================
def normalize_number(val):
    if not val: return ""
    clean = str(val).replace("+", "").replace("-", "").replace(" ", "").strip()
    if clean.startswith("91") and len(clean) == 12:
        clean = clean[2:]
    elif clean.startswith("0") and len(clean) == 11:
        clean = clean[1:]
    return clean

def is_hardcoded_protected_number(val):
    return normalize_number(val) in HARDCODED_PROTECTED_NUMBERS

def is_hardcoded_protected_admin_id(val):
    return str(val).strip() in HARDCODED_PROTECTED_ADMIN_IDS

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
                prot_col.update_one({"_id": entry}, {"$set": {"added_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
            except Exception as e:
                logger.error(f"Protected entry DB save error: {e}")
        try:
            Path("protected_entries.json").write_text(json.dumps(list(PROTECTED_ENTRIES), indent=2))
        except Exception: pass
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
            Path("protected_entries.json").write_text(json.dumps(list(PROTECTED_ENTRIES), indent=2))
        except Exception: pass
    threading.Thread(target=_remove, daemon=True).start()

def is_protected(search_value):
    sv = str(search_value).strip()
    if sv in PROTECTED_ENTRIES: return True
    for prefix in ["91", "+91", "0"]:
        if sv.startswith(prefix):
            if sv[len(prefix):] in PROTECTED_ENTRIES: return True
    if sv.isdigit():
        for entry in PROTECTED_ENTRIES:
            ce = entry.replace("+","").replace("-","").replace(" ","")
            cs = sv.replace("+","").replace("-","").replace(" ","")
            if ce == cs: return True
            if len(ce) >= 10 and len(cs) >= 10 and ce[-10:] == cs[-10:]: return True
    return False

def is_blocked_search(feat_name, search_value):
    if feat_name in ["tg", "tgid"]:
        if is_hardcoded_protected_admin_id(search_value):
            return True, popup_admin_id_blocked(), "blocked_admin_id"
    if feat_name in ["phone", "paytm", "imei"]:
        if is_hardcoded_protected_number(search_value):
            return True, popup_owner_number_blocked(), "blocked_owner_number"
    if feat_name == "upi":
        if is_hardcoded_protected_number(search_value):
            return True, popup_owner_number_blocked(), "blocked_owner_number"
        upi_prefix = str(search_value).split("@")[0]
        if is_hardcoded_protected_number(upi_prefix):
            return True, popup_owner_number_blocked(), "blocked_owner_number"
    if is_protected(search_value):
        return True, popup_protected_entity(), "blocked_protected"
    return False, None, None

# ================== 📚 FEATURE EXAMPLES ==================
FEATURE_EXAMPLES = {
    "phone":    "📞 Example: 9876543210",
    "email":    "📧 Example: john@gmail.com",
    "upi":      "💳 Example: ram@paytm",
    "aadhaar":  "🪪 Example: 123456789012",
    "vehicle":  "🚗 Example: DL8CAF5030",
    "ifsc":     "🏦 Example: SBIN0001234",
    "tg":       "👤 Example: 7142426722",
    "insta":    "📸 Example: cristiano",
    "imei":     "📱 Example: 354751093234567",
    "pin":      "📮 Example: 110001",
    "country":  "🌍 Example: India",
    "paytm":    "💰 Example: 9876543210",
    "ip":       "🌐 Example: 8.8.8.8",
    "weather":  "🌤️ Example: Mumbai",
    "tgid":     "🆔 Example: 8771611214",
}

FEATURE_EXAMPLES_HTML = {
    "phone":    "📞 <b>Example:</b> <code>9876543210</code>",
    "email":    "📧 <b>Example:</b> <code>john.doe@gmail.com</code>",
    "upi":      "💳 <b>Example:</b> <code>ramkumar@paytm</code>",
    "aadhaar":  "🪪 <b>Example:</b> <code>123456789012</code> (12 digits)",
    "vehicle":  "🚗 <b>Example:</b> <code>DL8CAF5030</code>",
    "ifsc":     "🏦 <b>Example:</b> <code>SBIN0001234</code> (11 chars)",
    "tg":       "👤 <b>Example:</b> <code>7142426722</code>",
    "insta":    "📸 <b>Example:</b> <code>cristiano</code>",
    "imei":     "📱 <b>Example:</b> <code>354751093234567</code> (15 digits)",
    "pin":      "📮 <b>Example:</b> <code>110001</code> (6 digits)",
    "country":  "🌍 <b>Example:</b> <code>India</code>",
    "paytm":    "💰 <b>Example:</b> <code>9876543210</code>",
    "ip":       "🌐 <b>Example:</b> <code>8.8.8.8</code>",
    "weather":  "🌤️ <b>Example:</b> <code>Mumbai</code>",
    "tgid":     "🆔 <b>Example:</b> <code>8771611214</code>",
}

# ================== 📋 ACTIVITY LOGS SYSTEM ==================
IST = timezone(timedelta(hours=5, minutes=30))
ACTIVITY_LOGS = deque(maxlen=200)

def add_activity_log(user_id, username, first_name, feat_name, search_term, status="success"):
    now = datetime.now(IST)
    log_entry = {
        "time": now.strftime("%d-%m-%Y %H:%M:%S"), "time_short": now.strftime("%H:%M"),
        "date": now.strftime("%d-%m"), "user_id": user_id, "username": username or "N/A",
        "first_name": first_name or "Unknown", "feature": feat_name,
        "search_term": str(search_term)[:50], "status": status, "timestamp": time.time()
    }
    ACTIVITY_LOGS.append(log_entry)
    try:
        if users_col is not None:
            logs_col = db["activity_logs"]
            threading.Thread(target=lambda: logs_col.insert_one(log_entry), daemon=True).start()
    except Exception: pass

def cleanup_old_logs_loop():
    while True:
        try:
            three_days_ago = time.time() - (3 * 24 * 3600)
            if db is not None:
                logs_col = db["activity_logs"]
                res = logs_col.delete_many({"timestamp": {"$lt": three_days_ago}})
                if res.deleted_count > 0:
                    logger.info(f"🧹 Deleted {res.deleted_count} old logs.")
            current_time = time.time()
            local_logs = list(ACTIVITY_LOGS); ACTIVITY_LOGS.clear()
            for log in local_logs:
                if log.get("timestamp") and (current_time - log["timestamp"] < (3*24*3600)):
                    ACTIVITY_LOGS.append(log)
        except Exception as e: logger.error(f"❌ Cleanup error: {e}")
        time.sleep(1800)

def get_recent_logs(count=20):
    logs = list(ACTIVITY_LOGS); return logs[-count:] if len(logs) > count else logs
def get_user_logs(user_id, count=10):
    return [l for l in ACTIVITY_LOGS if l["user_id"] == user_id][-count:]
def get_feature_logs(feat_name, count=15):
    return [l for l in ACTIVITY_LOGS if l["feature"] == feat_name][-count:]

def format_logs_text(logs, title="📋 ACTIVITY LOGS"):
    if not logs: return f"<code>{BANNER_MINI}</code>\n\n{title}\n\n📭 <i>No logs yet.</i>"
    txt = f"<code>{BANNER_MINI}</code>\n\n<b>{title}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for log in reversed(logs):
        si = "✅" if log["status"] == "success" else ("🛡️" if "blocked" in log["status"] else "❌")
        un = f"@{log['username']}" if log['username'] != "N/A" else log['first_name']
        txt += f"{si} <b>{log['time_short']}</b> | <code>{log['user_id']}</code> | <b>{html.escape(un)}</b>\n   🔍 <b>{log['feature'].upper()}</b> → <code>{html.escape(log['search_term'])}</code>\n\n"
    return txt[:4000]

# ================== 🔧 PERSISTENT MAINTENANCE SYSTEM ==================
ALL_FEATURE_KEYS = ["phone","email","upi","aadhaar","vehicle","ifsc","tg","insta","imei","pin","country","paytm","ip","weather","tgid"]

SETTINGS_FILE = Path("settings.json")
SETTINGS_CACHE = {"full_maintenance": False, "feature_maintenance": {f: False for f in ALL_FEATURE_KEYS}}

def load_settings():
    global SETTINGS_CACHE
    if db is not None:
        try:
            doc = db["settings"].find_one({"_id": "global_settings"})
            if doc:
                SETTINGS_CACHE["full_maintenance"] = doc.get("full_maintenance", False)
                fm = doc.get("feature_maintenance", {})
                for f in ALL_FEATURE_KEYS: SETTINGS_CACHE["feature_maintenance"][f] = fm.get(f, False)
                print("✅ Settings loaded from MongoDB!", flush=True); return
        except Exception as e: logger.warning(f"DB Settings Error: {e}")
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text())
            SETTINGS_CACHE["full_maintenance"] = data.get("full_maintenance", False)
            fm = data.get("feature_maintenance", {})
            for f in ALL_FEATURE_KEYS: SETTINGS_CACHE["feature_maintenance"][f] = fm.get(f, False)
        except Exception: pass

def save_settings():
    try: SETTINGS_FILE.write_text(json.dumps(SETTINGS_CACHE, indent=2))
    except Exception: pass
    def _s():
        if db is not None:
            try: db["settings"].update_one({"_id": "global_settings"}, {"$set": SETTINGS_CACHE}, upsert=True)
            except Exception: pass
    threading.Thread(target=_s, daemon=True).start()

def is_full_maintenance(): return SETTINGS_CACHE["full_maintenance"]
def is_feature_maintenance(fn): return SETTINGS_CACHE["feature_maintenance"].get(fn, False)
def toggle_full_maintenance():
    SETTINGS_CACHE["full_maintenance"] = not SETTINGS_CACHE["full_maintenance"]; save_settings()
    return SETTINGS_CACHE["full_maintenance"]
def toggle_feature_maintenance(fn):
    if fn in SETTINGS_CACHE["feature_maintenance"]:
        SETTINGS_CACHE["feature_maintenance"][fn] = not SETTINGS_CACHE["feature_maintenance"][fn]; save_settings()
        return SETTINGS_CACHE["feature_maintenance"][fn]
    return False

def get_maintenance_status():
    lines = [f"🔧 <b>Full:</b> {'🔴 ON' if SETTINGS_CACHE['full_maintenance'] else '🟢 OFF'}", "", "<b>Features:</b>"]
    for f in ALL_FEATURE_KEYS:
        lines.append(f"  • <b>{f.title()}</b>: {'🔴 ON' if SETTINGS_CACHE['feature_maintenance'].get(f) else '🟢 OFF'}")
    return "\n".join(lines)

# ================== 🔢 CONVERSATION STATES ==================
PHONE_SINGLE, PHONE_BATCH = 10, 11; EMAIL_SINGLE, EMAIL_BATCH = 12, 13
UPI_SINGLE, UPI_BATCH = 14, 15; AADHAAR_SINGLE, AADHAAR_BATCH = 16, 17
VEHICLE_SINGLE, VEHICLE_BATCH = 18, 19; IFSC_SINGLE, IFSC_BATCH = 20, 21
TG_SINGLE, TG_BATCH = 22, 23; INSTA_SINGLE, INSTA_BATCH = 24, 25
IMEI_SINGLE, IMEI_BATCH = 26, 27; PIN_SINGLE, PIN_BATCH = 28, 29
COUNTRY_SINGLE, COUNTRY_BATCH = 30, 31; PAYTM_SINGLE, PAYTM_BATCH = 32, 33
IP_SINGLE, IP_BATCH = 34, 35; WEATHER_SINGLE, WEATHER_BATCH = 36, 37
TGID_SINGLE, TGID_BATCH = 38, 39
ADMIN_ADD_ID, ADMIN_ADD_PLAN = 50, 51; ADMIN_REM_ID = 52
ADMIN_EXP_ID, ADMIN_EXP_PLAN = 53, 54; ADMIN_BROADCAST_MSG = 55
ADMIN_BROADCAST_CONFIRM = 56; ADMIN_CUSTOM_DAYS = 57; ADMIN_CUSTOM_LIMIT = 58
REDEEM_CREATE_CODE = 70; REDEEM_CREATE_SEARCHES = 71; REDEEM_CREATE_LIMIT = 72
REDEEM_DELETE_CODE = 73; ADMIN_LOGS_USER_ID = 80
ADMIN_PROTECT_ADD = 90; ADMIN_PROTECT_REMOVE = 91

# ================== 🩸 BANNERS ==================
BANNER = "╔══════════════════════════════╗\n║   ☠️  Z E R O  T R A C E  ☠️      ║\n║          ~BY  LEGIT               ║\n╚══════════════════════════════╝"
BANNER_MINI = "┏━━━━━━━━━━━━━━━━━━━━━━┓\n┃  ☠️ ZERO TRACE ☠️        ┃\n┃     ~BY LEGIT            ┃\n┗━━━━━━━━━━━━━━━━━━━━━━┛"
BANNER_SEARCH = "╔═══════════════════════╗\n║    ☠️ ZERO TRACE ☠️       ║\n║    ~BY LEGIT              ║\n╚═══════════════════════╝"

# ================== 🛡️ SAFE SENDERS ==================
async def safe_reply(update: Update, text: str, reply_markup=None):
    msg = update.effective_message
    if not msg: return None
    try: return await msg.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 0.5)
        try: return await msg.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except Exception: return None
    except Exception:
        clean = re.sub(r"</?(?:b|i|code|pre|u|s)>", "", text); clean = html.unescape(clean)
        try: return await msg.reply_text(clean[:4096], reply_markup=reply_markup)
        except Exception: return None

async def safe_edit(target, text: str, reply_markup=None):
    if not target: return None
    for _ in range(2):
        try:
            if hasattr(target, "edit_message_text"): return await target.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
            elif hasattr(target, "edit_text"): return await target.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        except RetryAfter as e: await asyncio.sleep(e.retry_after + 0.5); continue
        except BadRequest as e:
            if "not modified" in str(e): return target
            clean = re.sub(r"</?(?:b|i|code|pre|u|s)>", "", text); clean = html.unescape(clean)
            try:
                if hasattr(target, "edit_message_text"): return await target.edit_message_text(clean[:4096], reply_markup=reply_markup)
                elif hasattr(target, "edit_text"): return await target.edit_text(clean[:4096], reply_markup=reply_markup)
            except Exception: return None
        except Exception: break
    return None

def is_admin(uid): return int(uid) in ADMIN_IDS
def safe_name(user): return html.escape(user.first_name or "User")

# ================== 🎨 ANIMATED LOADER ==================
LOADING_STEPS = [
    ("🟡", "Scanning Database...", "██████░░░░░░░░░░░░░░", 35),
    ("🟣", "Decoding Records...",  "██████████████░░░░░░", 75),
    ("🟢", "Finalizing Report...", "████████████████████", 100)
]

def build_loading_text(icon, display, se, st, bar, pct):
    return f"<code>{BANNER_SEARCH}</code>\n\n{icon} <b>Searching:</b> <code>{html.escape(str(display))}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{se} <b>{st}</b>\n\n<code>[{bar}]</code> <b>{pct}%</b>\n\n⏳ <i>Please wait...</i>"

async def animated_search(msg, icon, display):
    if not msg: return
    for i, (se, st, bar, pct) in enumerate(LOADING_STEPS):
        await safe_edit(msg, build_loading_text(icon, display, se, st, bar, pct))
        if i < len(LOADING_STEPS) - 1: await asyncio.sleep(1.2)

# ================== 🌐 FLASK KEEP-ALIVE ==================
web_app = Flask(__name__)
@web_app.route('/')
def keep_alive_status(): return "Bot Running 24/7!", 200
def start_webserver():
    import logging as lg; lg.getLogger('werkzeug').setLevel(lg.ERROR)
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================== 🔒 FORCE JOIN ==================
async def check_joined(context, uid):
    if is_admin(uid): return True
    try:
        async def _c():
            m1 = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL_1_ID, uid)
            if m1.status not in ["member","administrator","creator","restricted"]: return False
            m2 = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL_2_ID, uid)
            return m2.status in ["member","administrator","creator","restricted"]
        return await asyncio.wait_for(_c(), timeout=1.5)
    except Exception: return True

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
    print("✅ MongoDB Initialized!", flush=True)
except Exception:
    users_col = None; redeem_col = None; db = None

DEFAULTS = {"plan": "trial", "expiry": "", "is_premium": False, "total_searches": 0, "redeemed_codes": []}
for feat in ALL_FEATURE_KEYS:
    DEFAULTS[f"{feat}_free_used"] = 0; DEFAULTS[f"{feat}_daily"] = 0; DEFAULTS[f"{feat}_date"] = ""; DEFAULTS[f"{feat}_total"] = 0

def init_cache():
    global USERS_CACHE, REDEEM_CODES
    if users_col is not None:
        try:
            for doc in users_col.find(): USERS_CACHE[str(doc["_id"])] = {k:v for k,v in doc.items() if k!="_id"}
        except Exception: pass
    elif LOCAL_FILE.exists():
        try: USERS_CACHE = json.loads(LOCAL_FILE.read_text())
        except Exception: pass
    if redeem_col is not None:
        try:
            for doc in redeem_col.find(): REDEEM_CODES[str(doc["_id"])] = {k:v for k,v in doc.items() if k!="_id"}
        except Exception: pass
    elif REDEEM_FILE.exists():
        try: REDEEM_CODES = json.loads(REDEEM_FILE.read_text())
        except Exception: pass
init_cache()

def sync_user_background(uid, data):
    def _s():
        if users_col: 
            try: users_col.update_one({"_id": str(uid)}, {"$set": data}, upsert=True); return
            except Exception: pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE, indent=2))
        except Exception: pass
    threading.Thread(target=_s, daemon=True).start()

def sync_redeem_background(code, data):
    def _s():
        if redeem_col:
            try: redeem_col.update_one({"_id": code}, {"$set": data}, upsert=True); return
            except Exception: pass
        try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES, indent=2))
        except Exception: pass
    threading.Thread(target=_s, daemon=True).start()

def delete_redeem_background(code):
    def _d():
        if redeem_col:
            try: redeem_col.delete_one({"_id": code})
            except Exception: pass
        try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES, indent=2))
        except Exception: pass
    threading.Thread(target=_d, daemon=True).start()

def get_user(uid):
    uid = str(uid)
    if uid not in USERS_CACHE:
        d = {**DEFAULTS, "added": date.today().isoformat()}; USERS_CACHE[uid] = d; sync_user_background(uid, d)
    return USERS_CACHE[uid]

def save_user(uid, data): uid = str(uid); USERS_CACHE[uid] = data; sync_user_background(uid, data)

def delete_user(uid):
    uid = str(uid)
    if uid in USERS_CACHE: del USERS_CACHE[uid]
    def _d():
        if users_col:
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
    sync_redeem_background(code, REDEEM_CODES[code]); return True

def use_redeem_code(code, user_id):
    code = code.upper().strip(); user_id = str(user_id)
    if code not in REDEEM_CODES: return False, "❌ Invalid!"
    rc = REDEEM_CODES[code]
    if not rc.get("active", True): return False, "❌ Deactivated!"
    if rc["used_count"] >= rc["max_uses"]: return False, "❌ Max reached!"
    if user_id in rc.get("used_by", []): return False, "❌ Already redeemed!"
    ud = get_user(user_id); s = rc["free_searches"]
    for feat in ALL_FEATURE_KEYS: ud[f"{feat}_free_used"] = max(0, ud.get(f"{feat}_free_used", 0) - s)
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
        try: d = int(pk.split("_")[1].replace("d",""))
        except Exception: d = 30
        return {"name": f"Custom ({d}D)", "days": d, "daily_limit": ud.get("custom_limit",0), "unlimited": ud.get("custom_unlimited",False), "is_free": False}
    return PLANS.get(pk, PLANS["trial"])

def upgrade(uid, pk):
    uid = str(uid); ud = get_user(uid); plan = PLANS.get(pk, PLANS["7days"])
    exp = (date.today() + timedelta(days=plan["days"])).isoformat()
    ud.update({"plan": pk, "expiry": exp, "is_premium": True})
    for f in ALL_FEATURE_KEYS: ud[f"{f}_daily"] = 0; ud[f"{f}_date"] = ""
    save_user(uid, ud); return exp

def upgrade_custom(uid, days, lim, unl):
    uid = str(uid); ud = get_user(uid); exp = (date.today() + timedelta(days=days)).isoformat()
    ud.update({"plan": f"custom_{days}d", "expiry": exp, "is_premium": True, "custom_limit": lim, "custom_unlimited": unl})
    for f in ALL_FEATURE_KEYS: ud[f"{f}_daily"] = 0; ud[f"{f}_date"] = ""
    save_user(uid, ud); return exp

# ================== 📊 LIMIT CHECKERS ==================
def check_feat_access(uid, feat_name, display_title):
    if is_admin(uid): return True, "Admin ∞", 9999, True, "12months"
    ud = get_user(uid); plan = get_plan(ud); pk = ud.get("plan","trial"); exp_s = ud.get("expiry",""); is_p = ud.get("is_premium",False)
    fk = f"{feat_name}_free_used"; dk = f"{feat_name}_daily"; dtk = f"{feat_name}_date"
    if is_p and exp_s:
        try:
            exp = date.fromisoformat(exp_s)
            if date.today() > exp:
                fl = max(0, FREE_LIMIT - ud.get(fk,0))
                return (True, f"Expired|{fl}", 0, False, "trial") if fl > 0 else (False, "Expired!", 0, False, "trial")
            dl = (exp - date.today()).days; lim = plan.get("daily_limit",0)
            if plan.get("unlimited"): return True, f"{plan['name']}|∞|{dl}d", dl, True, pk
            dr = lim if ud.get(dtk,"") != date.today().isoformat() else max(0, lim - ud.get(dk,0))
            if dr <= 0: return False, f"Limit!({lim}/day)", dl, True, pk
            return True, f"{plan['name']}|{dr}/{lim}|{dl}d", dl, True, pk
        except Exception: pass
    fl = max(0, FREE_LIMIT - ud.get(fk,0))
    return (True, f"Free({fl}/{FREE_LIMIT})", 0, False, "trial") if fl > 0 else (False, "Trial over!", 0, False, "trial")

def feat_free_rem(uid, fn):
    if is_admin(uid): return 999999
    return max(0, FREE_LIMIT - get_user(uid).get(f"{fn}_free_used",0))

def feat_daily_rem(uid, fn):
    if is_admin(uid): return 999999
    ud = get_user(uid); plan = get_plan(ud)
    if plan.get("unlimited"): return 999999
    lim = plan.get("daily_limit",0)
    if ud.get(f"{fn}_date","") != date.today().isoformat(): return lim
    return max(0, lim - ud.get(f"{fn}_daily",0))

def use_feature(uid, feat_name):
    uid = str(uid); ud = get_user(uid); today = date.today().isoformat()
    dk = f"{feat_name}_daily"; dtk = f"{feat_name}_date"; fk = f"{feat_name}_free_used"; tk = f"{feat_name}_total"
    if ud.get(dtk,"") != today: ud[dk] = 0; ud[dtk] = today
    plan = get_plan(ud)
    if not is_admin(int(uid)):
        if plan.get("is_free", True): ud[fk] = ud.get(fk,0) + 1
        else: ud[dk] = ud.get(dk,0) + 1
    ud[tk] = ud.get(tk,0) + 1; ud["total_searches"] = ud.get("total_searches",0) + 1; save_user(uid, ud)

# ================== 📡 API ENGINE ==================
def _safe_api(fn):
    try: return fn()
    except requests.exceptions.Timeout: return {"ok": False, "error": "Timed out!"}
    except requests.exceptions.ConnectionError: return {"ok": False, "error": "Connection error!"}
    except Exception as e: return {"ok": False, "error": str(e)}

def primary_api_call(action, params):
    def c():
        r = requests.get(PRIMARY_API_URL, params={"key": PRIMARY_API_KEY, "action": action, **params}, headers=COMMON_HEADERS, timeout=25)
        if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}"}
        try: data = r.json()
        except Exception: return {"ok": False, "error": "Invalid response."}
        if isinstance(data, dict) and (data.get("status") in [False,"error",400,404] or data.get("success") is False):
            return {"ok": False, "error": str(data.get("message") or data.get("error") or "No records.")}
        return {"ok": True, "data": data}
    return _safe_api(c)

def tgid_api_call(tg_id):
    def c():
        r = requests.get(TGID_API_URL, params={"key": TGID_API_KEY, "action": "tgid", "id": tg_id}, headers=COMMON_HEADERS, timeout=25)
        if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}"}
        try: data = r.json()
        except Exception: return {"ok": False, "error": "Invalid response."}
        if isinstance(data, dict) and (data.get("status") in [False,"error",400,404] or data.get("success") is False):
            return {"ok": False, "error": str(data.get("message") or data.get("error") or "No records.")}
        return {"ok": True, "data": data}
    return _safe_api(c)

def active_phone_api_call(num):
    def c():
        r = requests.get(ACTIVE_PHONE_API_URL, params={"number": num, "key": ACTIVE_PHONE_API_KEY}, headers=COMMON_HEADERS, timeout=25)
        if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}"}
        try: data = r.json()
        except Exception: return {"ok": False, "error": "Invalid response."}
        if isinstance(data, dict) and (data.get("status") in [False,"error",400,404] or data.get("success") is False):
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
        r = requests.get(BACKUP_IFSC_API_URL, params={"key": BACKUP_IFSC_API_KEY, "ifsc": ifsc_code}, headers=COMMON_HEADERS, timeout=20)
        if r.status_code != 200: return {"ok": False, "error": f"HTTP {r.status_code}"}
        try: data = r.json()
        except Exception: return {"ok": False, "error": "Invalid response."}
        if isinstance(data, dict) and (data.get("status") in [False,"error",400,404] or data.get("success") is False):
            return {"ok": False, "error": str(data.get("message") or data.get("error") or "No records.")}
        return {"ok": True, "data": data}
    return _safe_api(c)

# ================== 🧹 METADATA FILTER ==================
SKIP_K = {"metadata","meta","key_owner","key_usage","key_expiry","key_enabled","daily_limit","daily_used","api_key","key","action","parameters","service","success","violations","timestamp","response_time","response_time_ms","developer","owner","credit","credits","powered_by","source","api","version","status","message","code","time","created_at","updated_at","server","watermark","signature","by","made_by","contact_admin","channel","group","join","advertisement","ads","promo","query","req_id","request_id","execution_time","fizzagirl","nitin","shree","jaani","types","spell","type"}

def should_skip_key(k):
    if not k: return True
    kl = str(k).lower().strip().replace(" ","_")
    if kl in SKIP_K: return True
    for w in ["metadata","timestamp","response_time","developer","credit","powered","watermark","pheevar","advertisement","promo","channel","server","api_","made_by","encrypted","password","salt","key_","daily_","auth","token","fizza"]:
        if w in kl: return True
    return False

def should_skip_val(v):
    if v is None or v == "": return True
    if isinstance(v, (dict,list)): return len(v) == 0
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
            if any(not isinstance(v,(dict,list)) for v in item.values()): records.append(item)
            for v in item.values():
                if isinstance(v,(dict,list)): extract(v)
        elif isinstance(item, list):
            for s in item: extract(s)
    extract(cleaned)
    unique = []; seen = set()
    for r in records:
        fp = "-".join(sorted(f"{k}:{v}" for k,v in r.items() if not isinstance(v,(dict,list))))
        if fp and fp not in seen: seen.add(fp); unique.append(r)
    if not unique: return f"<code>{BANNER_MINI}</code>\n\n{icon} <b>Result:</b> <code>{html.escape(str(term))}</code>\n\n<i>No records.</i>"
    out = [f"<code>{BANNER_MINI}</code>", f"\n{icon} <b>Result:</b> <code>{html.escape(str(term))}</code>", f"📊 <b>{len(unique)} record(s)</b>", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]
    for idx, rec in enumerate(unique, 1):
        if len(unique) > 1: out.append(f"\n<b>━━ #{idx} ━━</b>")
        for k, v in rec.items():
            if isinstance(v,(dict,list)) or should_skip_key(k) or should_skip_val(v): continue
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
        [InlineKeyboardButton("📢 CH1", url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}"),
         InlineKeyboardButton("📢 CH2", url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")],
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
        [InlineKeyboardButton("📋 Recent 20", callback_data="logs_recent")],
        [InlineKeyboardButton("🔍 By User ID", callback_data="logs_by_user")],
        [InlineKeyboardButton("📱 Phone", callback_data="logs_feat_phone"), InlineKeyboardButton("🪪 Aadhaar", callback_data="logs_feat_aadhaar")],
        [InlineKeyboardButton("💳 UPI", callback_data="logs_feat_upi"), InlineKeyboardButton("🚗 Vehicle", callback_data="logs_feat_vehicle")],
        [InlineKeyboardButton("👤 TG", callback_data="logs_feat_tg"), InlineKeyboardButton("📸 Insta", callback_data="logs_feat_insta")],
        [InlineKeyboardButton("🆔 TG ID", callback_data="logs_feat_tgid")],
        [InlineKeyboardButton("📊 Stats", callback_data="logs_stats")],
        [InlineKeyboardButton("🔙 Admin", callback_data="admin_back")]
    ])

def protect_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add", callback_data="protect_add")],
        [InlineKeyboardButton("❌ Remove", callback_data="protect_remove")],
        [InlineKeyboardButton("📋 List All", callback_data="protect_list")],
        [InlineKeyboardButton("🔙 Admin", callback_data="admin_back")]
    ])

def maintenance_kb():
    fs = "🔴 ON" if is_full_maintenance() else "🟢 OFF"
    buttons = [[InlineKeyboardButton(f"🔧 Full Bot: {fs}", callback_data="maint_toggle_full")]]
    fb = []
    for f in ALL_FEATURE_KEYS:
        st = "🔴" if is_feature_maintenance(f) else "🟢"
        fb.append(InlineKeyboardButton(f"{st} {f.title()}", callback_data=f"maint_toggle_{f}"))
    for i in range(0, len(fb), 2): buttons.append(fb[i:i+2])
    buttons.append([InlineKeyboardButton("🔙 Admin", callback_data="admin_back")])
    return InlineKeyboardMarkup(buttons)

def back_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
def buy_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("💬 Buy", url=f"https://t.me/{OWNER_CONTACT.replace('@','')}")],[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])

def plan_kb(pf):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉 7D-₹70 (5/d)", callback_data=f"{pf}_7days")],[InlineKeyboardButton("🥈 30D-₹170 (10/d)", callback_data=f"{pf}_30days")],
        [InlineKeyboardButton("🥇 6M-₹350 (25/d)", callback_data=f"{pf}_6months")],[InlineKeyboardButton("💎 12M-₹849 (∞)", callback_data=f"{pf}_12months")],
        [InlineKeyboardButton("⚙️ Custom", callback_data=f"{pf}_custom")],[InlineKeyboardButton("❌ Cancel", callback_data="admin_back")]
    ])

# ================== 🚀 START COMMAND ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return ConversationHandler.END

    chat = update.effective_chat
    chat_type = chat.type if chat else "private"

    # ✅ 1. GROUP CHAT HANDLING: Don't spam groups. Point users to DM.
    if chat_type in ["group", "supergroup"]:
        # Only respond if the command specifically called the bot
        bot_username = context.bot.username or ""
        msg_text = update.message.text if update.message else ""
        if msg_text and f"@{bot_username}" not in msg_text and not msg_text.startswith("/start"):
            return ConversationHandler.END
        
        try:
            await update.effective_message.reply_text(
                f"👋 <b>Hey {safe_name(user)}!</b>\n\n"
                f"🛡️ <b>ZERO TRACE OSINT Bot</b> works in private messages to protect privacy.\n\n"
                f"👉 Click below to open bot in PM:",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🤖 Open In Private PM ↗️", url=f"https://t.me/{context.bot.username}?start=start")]
                ])
            )
        except Exception: pass
        return ConversationHandler.END

    # ✅ 2. PRIVATE CHAT HANDLING
    try:
        if is_full_maintenance() and not is_admin(user.id):
            popup = popup_full_maintenance()
            if update.callback_query: await safe_edit(update.callback_query, popup, dismiss_kb())
            else: await safe_reply(update, popup, dismiss_kb())
            return ConversationHandler.END
        get_user(user.id); u_name = safe_name(user)
        if not is_admin(user.id):
            if not await check_joined(context, user.id):
                popup = popup_force_join()
                if update.callback_query: await safe_edit(update.callback_query, popup, force_join_kb())
                else: await safe_reply(update, popup, force_join_kb())
                return ConversationHandler.END
        if is_admin(user.id):
            mn = "\n🔧 <b>MAINTENANCE: ON</b>\n" if is_full_maintenance() else ""
            t = f"<code>{BANNER}</code>\n\n👋 Boss <b>{u_name}</b>! 🛡️ <code>ADMIN</code>{mn}\n\nAll: 💎 ∞ | 🛡️ Protected: <code>{len(PROTECTED_ENTRIES)}</code>\n\n👇 <b>Select:</b>"
        else:
            ud = get_user(user.id); plan = get_plan(ud); ip = ud.get("is_premium",False); exp = ud.get("expiry","")
            lines = []
            for feat in ALL_FEATURE_KEYS[:8]:
                if is_feature_maintenance(feat): lines.append(f"🛠️ {feat.title()}: <code>Maint</code>"); continue
                fl = feat_free_rem(user.id, feat)
                if ip and exp:
                    try:
                        ed = date.fromisoformat(exp); dl = (ed-date.today()).days
                        if dl >= 0:
                            if plan.get("unlimited"): lines.append(f"🟢 {feat.title()}: <code>💎∞ ({dl}d)</code>")
                            else: dr = feat_daily_rem(user.id,feat); lines.append(f"🟢 {feat.title()}: <code>💎{dr}/{plan.get('daily_limit',0)} ({dl}d)</code>")
                        else: lines.append(f"🔴 {feat.title()}: <code>Expired({fl}/{FREE_LIMIT})</code>")
                    except Exception: lines.append(f"⚪ {feat.title()}: <code>Unknown</code>")
                else: lines.append(f"🆓 {feat.title()}: <code>{fl}/{FREE_LIMIT}</code>")
            t = f"<code>{BANNER}</code>\n\n👋 <b>{u_name}</b>!\n\n"+"\n".join(lines)+f"\n\n💡 <b>1 Plan = 15+ tools!</b>\n🎟️ <code>/redeem CODE</code>\n\n👇 <b>Select:</b>"
        if update.callback_query: await safe_edit(update.callback_query, t, main_kb(user.id))
        else: await safe_reply(update, t, main_kb(user.id))
    except Exception as e:
        logger.error(f"Start error: {e}")
        await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n👋 Welcome!", main_kb(user.id))
    return ConversationHandler.END

async def verify_join(update, context):
    q = update.callback_query; await q.answer("Verifying...")
    if await check_joined(context, q.from_user.id): await start(update, context)
    else:
        popup = popup_force_join()
        await safe_edit(q, popup, force_join_kb())

async def main_menu_cb(update, context):
    context.user_data.clear()
    if update.callback_query: await update.callback_query.answer()
    await start(update, context); return ConversationHandler.END

async def cancel(update, context):
    context.user_data.clear()
    await safe_reply(update, "❌ Cancelled.", main_kb(update.effective_user.id)); return ConversationHandler.END

# ================== DISMISS POPUP HANDLER ==================
async def dismiss_popup_handler(update, context):
    q = update.callback_query; await q.answer("Dismissed")
    try: await q.message.delete()
    except Exception:
        try: await q.edit_message_text("<i>Dismissed.</i>", parse_mode="HTML")
        except Exception: pass

# ================== 🛠️ SEARCH EXECUTION ==================
async def execute_search(update, context, feat_name, action, param_key, search_value, icon, display_value):
    u = update.effective_user
    if is_full_maintenance() and not is_admin(u.id):
        await safe_reply(update, popup_full_maintenance(), dismiss_kb()); return
    if is_feature_maintenance(feat_name):
        await safe_reply(update, popup_feature_maintenance(feat_name), dismiss_kb()); return
    
    # 🛡️ PROTECTION CHECK
    blocked, block_msg, log_status = is_blocked_search(feat_name, search_value)
    if blocked:
        add_activity_log(u.id, u.username, u.first_name, feat_name, display_value, log_status)
        await safe_reply(update, block_msg, dismiss_only_kb())
        for aid in ADMIN_IDS:
            try:
                at = "🔥 ADMIN ID" if log_status == "blocked_admin_id" else ("🔥 OWNER NUM" if log_status == "blocked_owner_number" else "🚨 PROTECTED")
                await context.bot.send_message(chat_id=aid, text=f"{at} <b>ATTEMPT!</b>\n\n👤 <code>{u.id}</code> (@{u.username or 'N/A'})\n🔍 <b>{feat_name.upper()}</b>\n🔑 <code>{html.escape(str(display_value))}</code>\n⏰ <code>{datetime.now(IST).strftime('%d-%m-%Y %H:%M:%S')}</code>", parse_mode="HTML")
            except Exception: pass
        return
    
    ok, st, _, _, _ = check_feat_access(u.id, feat_name, feat_name.title())
    if not ok:
        if "Expired" in st:
            popup = popup_expired_plan()
        elif "Limit" in st:
            popup = popup_daily_limit()
        elif "Trial" in st or "over" in st.lower():
            popup = popup_trial_over()
        else:
            popup = popup_access_denied(st)
        await safe_reply(update, popup, dismiss_buy_kb()); return

    msg = await safe_reply(update, "⏳ <i>Initializing...</i>")
    
    if feat_name == "tgid":
        api_task = asyncio.get_event_loop().run_in_executor(None, lambda: tgid_api_call(search_value))
    elif feat_name == "ifsc":
        api_task = asyncio.get_event_loop().run_in_executor(None, lambda: backup_ifsc_api_call(search_value))
    else:
        api_task = asyncio.get_event_loop().run_in_executor(None, lambda: primary_api_call(action, {param_key: search_value}))
        
    anim_task = animated_search(msg, icon, display_value)
    res, _ = await asyncio.gather(api_task, anim_task)
    
    if not res["ok"] and feat_name == "phone":
        res = await asyncio.get_event_loop().run_in_executor(None, lambda: active_phone_api_call(search_value))
        if not res["ok"]: res = await asyncio.get_event_loop().run_in_executor(None, lambda: backup_phone_api(search_value))
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
        popup = popup_api_failed(display_value, res['error'])
        if msg: await safe_edit(msg, popup, dismiss_kb())
        else: await safe_reply(update, popup, dismiss_kb())

async def execute_batch(update, context, feat_name, action, param_key, items, icon):
    u = update.effective_user; total = len(items)
    if is_full_maintenance() and not is_admin(u.id):
        await safe_reply(update, popup_full_maintenance(), dismiss_kb()); return
    if is_feature_maintenance(feat_name):
        await safe_reply(update, popup_feature_maintenance(feat_name), dismiss_kb()); return

    msg = await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n📦 <b>Batch:</b> <b>{total}</b>\n\n<code>[░░░░░░░░░░░░░░░░░░░░]</code> 0%")
    for idx, item in enumerate(items, 1):
        blocked, block_msg, log_status = is_blocked_search(feat_name, item)
        if blocked:
            add_activity_log(u.id, u.username, u.first_name, feat_name, item, log_status)
            await safe_reply(update, block_msg)
            for aid in ADMIN_IDS:
                try: await context.bot.send_message(chat_id=aid, text=f"🚨 BATCH BLOCK\n👤 <code>{u.id}</code>\n🔍 {feat_name.upper()}\n🔑 <code>{html.escape(str(item))}</code>", parse_mode="HTML")
                except Exception: pass
            continue
        
        pct = int((idx/total)*100); filled = int(pct/5); bar = "█"*filled + "░"*(20-filled)
        await safe_edit(msg, f"<code>{BANNER_MINI}</code>\n\n📦 <code>{html.escape(str(item))}</code>\n📊 <b>{idx}/{total}</b>\n\n<code>[{bar}]</code> <b>{pct}%</b>")
        
        if feat_name == "tgid": res = tgid_api_call(item)
        elif feat_name == "phone":
            res = primary_api_call(action, {param_key: item})
            if not res["ok"]: res = active_phone_api_call(item)
            if not res["ok"]: res = backup_phone_api(item)
        elif feat_name == "ifsc": res = backup_ifsc_api_call(item)
        else: res = primary_api_call(action, {param_key: item})
            
        if res["ok"]:
            use_feature(u.id, feat_name)
            add_activity_log(u.id, u.username, u.first_name, feat_name, item, "success")
            await safe_reply(update, format_universal_result(item, res["data"], icon))
        else:
            add_activity_log(u.id, u.username, u.first_name, feat_name, item, "failed")
            await safe_reply(update, popup_api_failed(item, res['error']), dismiss_only_kb())
        await asyncio.sleep(0.8)
    if msg: await safe_edit(msg, f"<code>{BANNER_MINI}</code>\n\n⚡ <b>Done!</b> ✅ <b>{total}</b>\n<code>[████████████████████]</code> <b>100%</b>", main_kb(u.id))

# ================== 📱 MODE PROMPTERS ==================
async def generic_mode_prompt(update, context, feat_name, display_title, icon):
    q = update.callback_query; await q.answer(); u = q.from_user
    if is_full_maintenance() and not is_admin(u.id):
        await safe_edit(q, popup_full_maintenance(), dismiss_kb()); return
    if is_feature_maintenance(feat_name):
        await safe_edit(q, popup_feature_maintenance(feat_name), dismiss_kb()); return
    if not is_admin(u.id) and not await check_joined(context, u.id):
        await safe_edit(q, popup_force_join(), force_join_kb()); return
    await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n{icon} <b>{display_title}</b> {icon}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nChoose:", search_sub_kb(u.id, feat_name))

async def mode_phone(u,c): await generic_mode_prompt(u,c,"phone","Phone Tracker","📱")
async def mode_email(u,c): await generic_mode_prompt(u,c,"email","Email OSINT","📧")
async def mode_upi(u,c): await generic_mode_prompt(u,c,"upi","UPI Verifier","💳")
async def mode_aadhaar(u,c): await generic_mode_prompt(u,c,"aadhaar","Aadhaar Lookup","🪪")
async def mode_vehicle(u,c): await generic_mode_prompt(u,c,"vehicle","Vehicle RC","🚗")
async def mode_ifsc(u,c): await generic_mode_prompt(u,c,"ifsc","IFSC Lookup","🏦")
async def mode_tg(u,c): await generic_mode_prompt(u,c,"tg","Telegram Info","👤")
async def mode_insta(u,c): await generic_mode_prompt(u,c,"insta","Instagram Info","📸")
async def mode_imei(u,c): await generic_mode_prompt(u,c,"imei","IMEI Tracker","📱")
async def mode_pin(u,c): await generic_mode_prompt(u,c,"pin","Pincode Info","📮")
async def mode_country(u,c): await generic_mode_prompt(u,c,"country","Country Info","🌍")
async def mode_paytm(u,c): await generic_mode_prompt(u,c,"paytm","Paytm Info","💰")
async def mode_ip(u,c): await generic_mode_prompt(u,c,"ip","IP Lookup","🌐")
async def mode_weather(u,c): await generic_mode_prompt(u,c,"weather","Weather","🌤️")
async def mode_tgid(u,c): await generic_mode_prompt(u,c,"tgid","TG ID → Info","🆔")

# ================== 📥 SEARCH HANDLERS ==================
def make_handler_pair(feat_name, action, param_key, icon, ss, bs, ps, pb, vfn=None):
    example_html = FEATURE_EXAMPLES_HTML.get(feat_name, "")
    example_plain = FEATURE_EXAMPLES.get(feat_name, "")
    
    async def single_start(update, context):
        q = update.callback_query; await q.answer()
        if is_full_maintenance() and not is_admin(q.from_user.id):
            await safe_edit(q, popup_full_maintenance(), dismiss_kb()); return ConversationHandler.END
        if is_feature_maintenance(feat_name):
            await safe_edit(q, popup_feature_maintenance(feat_name), dismiss_kb()); return ConversationHandler.END
        ok, st, _, _, _ = check_feat_access(q.from_user.id, feat_name, feat_name.title())
        if not ok:
            if "Expired" in st: popup = popup_expired_plan()
            elif "Limit" in st: popup = popup_daily_limit()
            elif "Trial" in st or "over" in st.lower(): popup = popup_trial_over()
            else: popup = popup_access_denied(st)
            await safe_edit(q, popup, dismiss_buy_kb()); return ConversationHandler.END
        await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n{icon} <b>{ps}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{example_html}\n\n✍️ <i>Send input or /cancel:</i>")
        return ss

    async def batch_start(update, context):
        q = update.callback_query; await q.answer()
        if is_full_maintenance() and not is_admin(q.from_user.id):
            await safe_edit(q, popup_full_maintenance(), dismiss_kb()); return ConversationHandler.END
        if is_feature_maintenance(feat_name):
            await safe_edit(q, popup_feature_maintenance(feat_name), dismiss_kb()); return ConversationHandler.END
        ok, st, _, _, _ = check_feat_access(q.from_user.id, feat_name, feat_name.title())
        if not ok:
            if "Expired" in st: popup = popup_expired_plan()
            elif "Limit" in st: popup = popup_daily_limit()
            elif "Trial" in st or "over" in st.lower(): popup = popup_trial_over()
            else: popup = popup_access_denied(st)
            await safe_edit(q, popup, dismiss_buy_kb()); return ConversationHandler.END
        await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n{icon} <b>{pb}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nℹ️ Max <b>15</b>, comma-separated.\n✍️ <i>Send list or /cancel:</i>")
        return bs

    async def single_process(update, context):
        raw = update.message.text.strip()
        val = vfn(raw) if vfn else raw
        if not val:
            popup = popup_invalid_input(feat_name, example_plain)
            await safe_reply(update, popup, dismiss_only_kb())
            return ss
        await execute_search(update, context, feat_name, action, param_key, val, icon, val)
        return ConversationHandler.END

    async def batch_process(update, context):
        raw_list = [x.strip() for x in update.message.text.split(",") if x.strip()]
        valid = [vfn(x) if vfn else x for x in raw_list]; valid = [x for x in valid if x][:15]
        if not valid:
            popup = popup_invalid_input(feat_name, example_plain)
            await safe_reply(update, popup, dismiss_only_kb())
            return bs
        await execute_batch(update, context, feat_name, action, param_key, valid, icon)
        return ConversationHandler.END
        
    return single_start, batch_start, single_process, batch_process

def clean_num(x):
    c = x.replace(" ","").replace("-","").replace("+","")
    return c if c.isdigit() and 7<=len(c)<=15 else None
def clean_aadhaar(x):
    c = x.replace(" ","").replace("-",""); return c if c.isdigit() and len(c)==12 else None
def clean_rc(x):
    c = x.upper().replace(" ","").replace("-",""); return c if len(c)>=4 else None
def clean_ifsc(x):
    c = x.upper().replace(" ",""); return c if len(c)==11 else None
def clean_tgid(x):
    c = x.strip(); return c if c.isdigit() and len(c)>=4 else None

(p_ss,p_bs,p_sp,p_bp) = make_handler_pair("phone","num","number","📱",PHONE_SINGLE,PHONE_BATCH,"Enter Phone:","Phones (comma-sep):",clean_num)
(e_ss,e_bs,e_sp,e_bp) = make_handler_pair("email","email","email","📧",EMAIL_SINGLE,EMAIL_BATCH,"Enter Email:","Emails (comma-sep):",lambda x: x.strip() if "@" in x else None)
(u_ss,u_bs,u_sp,u_bp) = make_handler_pair("upi","upiinfo","upi","💳",UPI_SINGLE,UPI_BATCH,"Enter UPI:","UPIs (comma-sep):",lambda x: x.strip() if "@" in x else None)
(a_ss,a_bs,a_sp,a_bp) = make_handler_pair("aadhaar","aadhar","aadhar","🪪",AADHAAR_SINGLE,AADHAAR_BATCH,"Enter Aadhaar:","Aadhaars (comma-sep):",clean_aadhaar)
(v_ss,v_bs,v_sp,v_bp) = make_handler_pair("vehicle","vehicle-v1","rc","🚗",VEHICLE_SINGLE,VEHICLE_BATCH,"Enter RC:","RCs (comma-sep):",clean_rc)
(i_ss,i_bs,i_sp,i_bp) = make_handler_pair("ifsc","ifsc-info","ifsc","🏦",IFSC_SINGLE,IFSC_BATCH,"Enter IFSC:","IFSCs (comma-sep):",clean_ifsc)
(tg_ss,tg_bs,tg_sp,tg_bp) = make_handler_pair("tg","tg-registration","userid","👤",TG_SINGLE,TG_BATCH,"Enter TG ID:","TG IDs (comma-sep):",lambda x: x.strip() if x.strip().isdigit() else None)
(in_ss,in_bs,in_sp,in_bp) = make_handler_pair("insta","instagram-user","username","📸",INSTA_SINGLE,INSTA_BATCH,"Enter Username:","Usernames (comma-sep):",lambda x: x.strip().lstrip("@"))
(im_ss,im_bs,im_sp,im_bp) = make_handler_pair("imei","imei-info","imei_num","📱",IMEI_SINGLE,IMEI_BATCH,"Enter IMEI:","IMEIs (comma-sep):",lambda x: x.strip() if x.strip().isdigit() else None)
(pin_ss,pin_bs,pin_sp,pin_bp) = make_handler_pair("pin","pincode-info","pincode","📮",PIN_SINGLE,PIN_BATCH,"Enter Pincode:","Pincodes (comma-sep):",lambda x: x.strip() if len(x.strip())==6 else None)
(c_ss,c_bs,c_sp,c_bp) = make_handler_pair("country","country-info","name","🌍",COUNTRY_SINGLE,COUNTRY_BATCH,"Enter Country:","Countries (comma-sep):",lambda x: x.strip())
(pm_ss,pm_bs,pm_sp,pm_bp) = make_handler_pair("paytm","paytm","info","💰",PAYTM_SINGLE,PAYTM_BATCH,"Enter Paytm No:","Numbers (comma-sep):",clean_num)
(ip_ss,ip_bs,ip_sp,ip_bp) = make_handler_pair("ip","ip-v1","query","🌐",IP_SINGLE,IP_BATCH,"Enter IP:","IPs (comma-sep):",lambda x: x.strip())
(w_ss,w_bs,w_sp,w_bp) = make_handler_pair("weather","weather","search","🌤️",WEATHER_SINGLE,WEATHER_BATCH,"Enter City:","Cities (comma-sep):",lambda x: x.strip().title())
(tgid_ss,tgid_bs,tgid_sp,tgid_bp) = make_handler_pair("tgid","tgid","id","🆔",TGID_SINGLE,TGID_BATCH,"Enter Telegram ID:","TG IDs (comma-sep):",clean_tgid)

# ================== 👤 PROFILE / STATUS / HELP / BUY ==================
async def profile(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user; ud = get_user(u.id); plan = get_plan(ud)
    txt = f"<code>{BANNER_MINI}</code>\n\n👤 <b>PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🆔 <code>{u.id}</code>\n👤 <b>{safe_name(u)}</b>\n📦 <b>{plan['name']}</b>\n📅 <code>{ud.get('expiry','Free')}</code>\n🔍 <code>{ud.get('total_searches',0)}</code>\n🎟️ <code>{len(ud.get('redeemed_codes',[]))}</code>"
    await safe_edit(q, txt, back_kb())

async def status_check(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user
    if is_admin(u.id): await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🛡️ <code>ADMIN</code> — All ∞", back_kb()); return
    lines = []
    for f in ALL_FEATURE_KEYS:
        if is_feature_maintenance(f): lines.append(f"• <b>{f.title()}</b>: <code>🛠️ Maint</code>"); continue
        ok, st, _, _, _ = check_feat_access(u.id, f, f.title())
        lines.append(f"• <b>{f.title()}</b>: <code>{st}</code>")
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n📊 <b>STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"+"\n".join(lines)+f"\n\n💰 {OWNER_CONTACT}\n🆔 <code>{u.id}</code>", back_kb())

async def help_menu(update, context):
    q = update.callback_query; await q.answer()
    txt = (
        f"<code>{BANNER}</code>\n\n"
        f"❓ <b>HELP & FEATURE EXAMPLES</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 <b>15+ Powerful OSINT Tools</b>\n\n"
        f"📱 Phone: <code>9876543210</code>\n"
        f"🪪 Aadhaar: <code>123456789012</code>\n"
        f"💳 UPI: <code>ram@paytm</code>\n"
        f"📧 Email: <code>user@gmail.com</code>\n"
        f"🚗 Vehicle: <code>DL8CAF5030</code>\n"
        f"🏦 IFSC: <code>SBIN0001234</code>\n"
        f"👤 TG: <code>5057489358</code>\n"
        f"📸 Insta: <code>cristiano</code>\n"
        f"📱 IMEI: <code>354751093234567</code>\n"
        f"📮 Pincode: <code>110001</code>\n"
        f"🌍 Country: <code>India</code>\n"
        f"💰 Paytm: <code>9876543210</code>\n"
        f"🌐 IP: <code>8.8.8.8</code>\n"
        f"🌤️ Weather: <code>Mumbai</code>\n"
        f"🆔 TG ID: <code>8771611214</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 <b>Plans:</b>\n"
        f"  🥉 7D → ₹70 (5/day)\n"
        f"  🥈 30D → ₹170 (10/day)\n"
        f"  🥇 6M → ₹350 (25/day)\n"
        f"  💎 12M → ₹849 (∞ Unlimited)\n\n"
        f"🎟️ <code>/redeem CODE</code>\n"
        f"📲 {OWNER_CONTACT}"
    )
    await safe_edit(q, txt, back_kb())

async def buy(update, context):
    q = update.callback_query; await q.answer()
    await safe_edit(q, (
        f"<code>{BANNER}</code>\n\n"
        f"💎 <b>PREMIUM PLANS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🥉 <b>7 Days:</b> ₹70 (5/day)\n"
        f"🥈 <b>30 Days:</b> ₹170 (10/day)\n"
        f"🥇 <b>6 Months:</b> ₹350 (25/day)\n"
        f"💎 <b>12 Months:</b> ₹849 (∞ Unlimited)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📲 <b>Contact:</b> {OWNER_CONTACT}\n"
        f"🆔 <b>Your ID:</b> <code>{q.from_user.id}</code>"
    ), buy_kb())

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
    if not is_admin(update.effective_user.id):
        popup = popup_not_admin()
        await safe_reply(update, popup, dismiss_only_kb())
        return ConversationHandler.END
    users = load_users(); t = len(users); p = sum(1 for v in users.values() if v.get("is_premium"))
    ms = "🔴 ON" if is_full_maintenance() else "🟢 OFF"
    fm = sum(1 for f in ALL_FEATURE_KEYS if is_feature_maintenance(f))
    hc = len(HARDCODED_PROTECTED_NUMBERS) + len(HARDCODED_PROTECTED_ADMIN_IDS)
    txt = f"<code>{BANNER_MINI}</code>\n\n🛠️ <b>ADMIN</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🛡️ <code>{len(ADMIN_IDS)}</code> | 👥 <code>{t}</code> | 💎 <code>{p}</code> | 🆓 <code>{t-p}</code>\n🎟️ <code>{len(list_redeem_codes())}</code> | 📋 <code>{len(ACTIVITY_LOGS)}</code>\n🔧 Full: <b>{ms}</b> | 🛠️ <code>{fm}</code>\n🛡️ Dynamic: <code>{len(PROTECTED_ENTRIES)}</code> | 🔒 HC: <code>{hc}</code>"
    if update.callback_query: await safe_edit(update.callback_query, txt, admin_kb())
    else: await safe_reply(update, txt, admin_kb())
    return ConversationHandler.END

async def admin_back(u, c): await admin_panel(u, c)

# ================== 🛡️ ADMIN PROTECTION HANDLERS ==================
async def admin_protect_menu(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    txt = f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>PROTECTED MANAGER</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Dynamic: <code>{len(PROTECTED_ENTRIES)}</code>\n🔒 HC Numbers: <code>{', '.join(HARDCODED_PROTECTED_NUMBERS)}</code>\n🔒 HC Admin IDs: <code>{', '.join(HARDCODED_PROTECTED_ADMIN_IDS)}</code>"
    await safe_edit(q, txt, protect_kb())

async def protect_add_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>ADD PROTECTED</b>\n\nSend entries (comma-sep) or /cancel:")
    return ADMIN_PROTECT_ADD

async def protect_add_process(update, context):
    raw = update.message.text.strip()
    entries = [x.strip() for x in raw.split(",") if x.strip()]
    if not entries: await safe_reply(update, "❌ No entries!"); return ADMIN_PROTECT_ADD
    added, already = [], []
    for e in entries:
        cl = e.replace(" ","").replace("-","").replace("+","") if e.replace(" ","").replace("-","").replace("+","").isdigit() else e.strip()
        if cl in PROTECTED_ENTRIES: already.append(cl)
        else: save_protected_entry(cl); added.append(cl)
    txt = f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>UPDATE</b>\n\n"
    if added: txt += f"✅ Added ({len(added)}):\n" + "\n".join(f"  • <code>{html.escape(a)}</code>" for a in added) + "\n"
    if already: txt += f"\n⚠️ Already ({len(already)}):\n" + "\n".join(f"  • <code>{html.escape(a)}</code>" for a in already) + "\n"
    txt += f"\n📊 Total: <code>{len(PROTECTED_ENTRIES)}</code>"
    await safe_reply(update, txt, protect_kb()); return ConversationHandler.END

async def protect_remove_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    if not PROTECTED_ENTRIES: await safe_edit(q, "📭 No entries.", protect_kb()); return ConversationHandler.END
    el = sorted(list(PROTECTED_ENTRIES))[:30]
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n❌ <b>REMOVE</b>\n\n"+"\n".join(f"  • <code>{html.escape(e)}</code>" for e in el)+"\n\nSend to remove or /cancel:")
    return ADMIN_PROTECT_REMOVE

async def protect_remove_process(update, context):
    entries = [x.strip() for x in update.message.text.split(",") if x.strip()]
    if not entries: await safe_reply(update, "❌ No entries!"); return ADMIN_PROTECT_REMOVE
    removed, nf = [], []
    for e in entries:
        cl = e.replace(" ","").replace("-","").replace("+","") if e.replace(" ","").replace("-","").replace("+","").isdigit() else e.strip()
        if cl in PROTECTED_ENTRIES: remove_protected_entry(cl); removed.append(cl)
        else: nf.append(cl)
    txt = f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>REMOVAL</b>\n\n"
    if removed: txt += f"✅ Removed ({len(removed)}):\n"+"\n".join(f"  • <code>{html.escape(r)}</code>" for r in removed)+"\n"
    if nf: txt += f"\n❌ Not found ({len(nf)}):\n"+"\n".join(f"  • <code>{html.escape(n)}</code>" for n in nf)+"\n"
    txt += f"\n📊 Remaining: <code>{len(PROTECTED_ENTRIES)}</code>"
    await safe_reply(update, txt, protect_kb()); return ConversationHandler.END

async def protect_list(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    txt = f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>PROTECTED LIST</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔒 HC Numbers: "+", ".join(f"<code>{n}</code>" for n in HARDCODED_PROTECTED_NUMBERS)+"\n🔒 HC IDs: "+", ".join(f"<code>{i}</code>" for i in HARDCODED_PROTECTED_ADMIN_IDS)+f"\n\n📊 Dynamic ({len(PROTECTED_ENTRIES)}):\n"
    if not PROTECTED_ENTRIES: txt += "<i>None</i>"
    else:
        for idx, e in enumerate(sorted(list(PROTECTED_ENTRIES)),1):
            line = f"{idx}. <code>{html.escape(e)}</code>\n"
            if len(txt)+len(line) > 3900: txt += f"\n⚠️ ...truncated"; break
            txt += line
    await safe_edit(q, txt, protect_kb())

# ================== 📋 ADMIN LOGS ==================
async def admin_logs_menu(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n📋 <b>LOGS</b>\n📊 Total: <code>{len(ACTIVITY_LOGS)}</code>", logs_kb())

async def logs_recent(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    await safe_edit(q, format_logs_text(get_recent_logs(20), "📋 RECENT 20"), InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="logs_recent")],[InlineKeyboardButton("🔙 Logs", callback_data="admin_logs")]]))

async def logs_by_user_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "🔍 Enter User ID or /cancel:"); return ADMIN_LOGS_USER_ID

async def logs_by_user_process(update, context):
    uid = update.message.text.strip()
    if not uid.isdigit(): await safe_reply(update, "❌ Invalid!"); return ADMIN_LOGS_USER_ID
    logs = get_user_logs(int(uid), 15)
    txt = format_logs_text(logs, f"📋 USER {uid}") if logs else f"📭 No logs for <code>{uid}</code>"
    await safe_reply(update, txt, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Logs", callback_data="admin_logs")]])); return ConversationHandler.END

async def logs_by_feature(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    feat = q.data.replace("logs_feat_","")
    if feat not in ALL_FEATURE_KEYS: return
    await safe_edit(q, format_logs_text(get_feature_logs(feat,15), f"📋 {feat.upper()}"), InlineKeyboardMarkup([[InlineKeyboardButton("🔄",callback_data=f"logs_feat_{feat}")],[InlineKeyboardButton("🔙",callback_data="admin_logs")]]))

async def logs_stats(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    logs = list(ACTIVITY_LOGS); t = len(logs)
    s = sum(1 for l in logs if l["status"]=="success"); f = sum(1 for l in logs if l["status"]=="failed")
    b = sum(1 for l in logs if "blocked" in l["status"])
    fc = {}
    for l in logs: fc[l["feature"]] = fc.get(l["feature"],0)+1
    tf = sorted(fc.items(),key=lambda x:x[1],reverse=True)[:5]
    tt = "\n".join(f"  • <b>{fn.title()}</b>: <code>{c}</code>" for fn,c in tf) if tf else "  None"
    txt = f"<code>{BANNER_MINI}</code>\n\n📊 <b>STATS</b>\n\n📋 Total: <code>{t}</code>\n✅ OK: <code>{s}</code>\n❌ Fail: <code>{f}</code>\n🛡️ Block: <code>{b}</code>\n👥 Users: <code>{len(set(l['user_id'] for l in logs))}</code>\n\n🔝 Top:\n{tt}"
    await safe_edit(q, txt, InlineKeyboardMarkup([[InlineKeyboardButton("🔄",callback_data="logs_stats")],[InlineKeyboardButton("🔙",callback_data="admin_logs")]]))

# ================== 🔧 MAINTENANCE ==================
async def admin_maintenance(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🔧 <b>MAINTENANCE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{get_maintenance_status()}", maintenance_kb())

async def maint_toggle_handler(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    d = q.data
    if d == "maint_toggle_full": toggle_full_maintenance()
    elif d.startswith("maint_toggle_"):
        f = d.replace("maint_toggle_","")
        if f in ALL_FEATURE_KEYS: toggle_feature_maintenance(f)
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🔧 <b>MAINTENANCE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{get_maintenance_status()}", maintenance_kb())

# ================== ADMIN PLAN HANDLERS ==================
async def adm_add_s(u,c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "➕ Enter User ID:"); return ADMIN_ADD_ID

async def adm_add_id(u,c):
    uid = u.message.text.strip()
    if not uid.isdigit(): await safe_reply(u, "❌ Invalid!"); return ADMIN_ADD_ID
    c.user_data["admin_uid"] = uid; await safe_reply(u, f"User: <code>{uid}</code>\nPlan:", plan_kb("plan")); return ADMIN_ADD_PLAN

async def adm_add_plan(u,c):
    q = u.callback_query; await q.answer()
    if q.data == "admin_back": await admin_panel(u,c); return ConversationHandler.END
    pm = {"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk = pm.get(q.data,"7days"); uid = c.user_data.get("admin_uid"); plan = PLANS.get(pk)
    exp = upgrade(int(uid),pk); dl = "∞" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(q, f"✅ <b>Activated!</b>\n🆔 <code>{uid}</code>\n📦 <b>{plan['name']}</b>\n📅 <code>{exp}</code>\n⚡ <code>{dl}</code>", admin_kb()); return ConversationHandler.END

async def adm_rem_s(u,c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "❌ Enter User ID:"); return ADMIN_REM_ID

async def adm_rem_p(u,c):
    uid = u.message.text.strip(); delete_user(uid)
    await safe_reply(u, f"✅ <code>{uid}</code> removed!", admin_kb()); return ConversationHandler.END

async def adm_sp_s(u,c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "📅 Enter User ID:"); return ADMIN_EXP_ID

async def adm_sp_id(u,c):
    uid = u.message.text.strip(); c.user_data["admin_uid"] = uid
    await safe_reply(u, f"User: <code>{uid}</code>", plan_kb("plan")); return ADMIN_EXP_PLAN

async def adm_sp_set(u,c):
    q = u.callback_query; await q.answer()
    if q.data == "admin_back": await admin_panel(u,c); return ConversationHandler.END
    pm = {"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk = pm.get(q.data,"7days"); uid = c.user_data.get("admin_uid"); plan = PLANS.get(pk); exp = upgrade(int(uid),pk)
    await safe_edit(q, f"✅ Updated! <code>{uid}</code> → <b>{plan['name']}</b> (<code>{exp}</code>)", admin_kb()); return ConversationHandler.END

# ================== 📖 PAGINATED USER LIST ==================
async def adm_list(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    page = 0
    if q.data.startswith("admin_list_page_"):
        try: page = int(q.data.split("_")[-1])
        except: page = 0
    users = load_users()
    if not users: await safe_edit(q, "📋 Empty.", admin_kb()); return
    su = sorted(users.items(), key=lambda x: (int(x[0]) if x[0].isdigit() else x[0]))
    t = len(su); pp = 30; tp = (t+pp-1)//pp
    page = max(0, min(page, tp-1))
    si = page*pp; ei = si+pp
    txt = f"<code>{BANNER_MINI}</code>\n\n📋 <b>USERS ({t})</b> | Page <code>{page+1}/{tp}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for uid, info in su[si:ei]:
        ts = info.get("total_searches",0)
        if int(uid) in ADMIN_IDS: st = "🛡️ Admin"
        elif info.get("is_premium") and info.get("expiry"):
            try: ed = date.fromisoformat(info["expiry"]); st = f"💎 {(ed-date.today()).days}d" if date.today()<=ed else "🔴 Exp"
            except: st = "⚪"
        else: st = "🆓"
        txt += f"👤 <code>{uid}</code> | {st} | 🔍 <code>{ts}</code>\n"
    nav = []
    if page > 0: nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"admin_list_page_{page-1}"))
    if ei < t: nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"admin_list_page_{page+1}"))
    kbd = [nav] if nav else []
    kbd.append([InlineKeyboardButton("🔙 Admin", callback_data="admin_back")])
    await safe_edit(q, txt, InlineKeyboardMarkup(kbd))

async def adm_stats(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    users = load_users(); ts = sum(v.get("total_searches",0) for v in users.values())
    act = sum(1 for u,v in users.items() if v.get("is_premium") and int(u) not in ADMIN_IDS)
    txt = f"<code>{BANNER_MINI}</code>\n\n📊 <b>STATS</b>\n\n👥 <code>{len(users)}</code> | 🔍 <code>{ts}</code> | 💎 <code>{act}</code>\n🎟️ <code>{len(list_redeem_codes())}</code> | 🛡️ <code>{len(PROTECTED_ENTRIES)}</code>"
    await safe_edit(q, txt, admin_kb())

async def adm_monitor(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    free = sum(1 for u,v in load_users().items() if not v.get("is_premium") and int(u) not in ADMIN_IDS)
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🆓 Free Users: <code>{free}</code>", admin_kb())

# ================== 📢 BROADCAST SYSTEM (PRO FIXED) ==================
async def bc_start(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(
        q,
        f"<code>{BANNER_MINI}</code>\n\n"
        f"📢 <b>ADMIN BROADCAST</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✍️ <b>Send your broadcast message now.</b>\n\n"
        f"💡 <i>Supports:</i>\n"
        f"  • Text messages (with HTML formatting)\n"
        f"  • Photos with caption\n\n"
        f"❌ Send /cancel to abort.",
        InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_back")]])
    )
    return ADMIN_BROADCAST_MSG

async def bc_msg(u, c):
    msg = u.message
    if not msg: return ADMIN_BROADCAST_MSG
    
    broadcast_data = {}
    if msg.photo:
        broadcast_data["type"] = "photo"
        broadcast_data["file_id"] = msg.photo[-1].file_id
        broadcast_data["caption"] = msg.caption or ""
        preview_text = f"📷 <b>Photo Broadcast</b>\n\n{html.escape(broadcast_data['caption']) if broadcast_data['caption'] else '<i>(No Caption)</i>'}"
    elif msg.text:
        broadcast_data["type"] = "text"
        broadcast_data["text"] = msg.text
        preview_text = html.escape(msg.text)
    else:
        await safe_reply(u, "❌ Only text or photos with caption are supported! Send again or /cancel:")
        return ADMIN_BROADCAST_MSG
    
    c.user_data["bc"] = broadcast_data
    total_users = len(load_users())
    
    await safe_reply(
        u,
        f"<code>{BANNER_MINI}</code>\n\n"
        f"📢 <b>BROADCAST PREVIEW</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{preview_text[:2000]}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Target Audience:</b> <code>{total_users} users</code>\n\n"
        f"⚠️ Are you sure you want to broadcast this message to all users?",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ CONFIRM & SEND", callback_data="broadcast_confirm")],
            [InlineKeyboardButton("❌ CANCEL", callback_data="broadcast_cancel")]
        ])
    )
    return ADMIN_BROADCAST_CONFIRM

async def bc_confirm(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "broadcast_cancel":
        await safe_edit(q, "❌ Broadcast cancelled.", admin_kb())
        c.user_data.pop("bc", None)
        return ConversationHandler.END
    
    broadcast_data = c.user_data.get("bc")
    if not broadcast_data:
        await safe_edit(q, "❌ Broadcast session expired. Try again.", admin_kb())
        return ConversationHandler.END
    
    users = load_users()
    user_ids = list(users.keys())
    total = len(user_ids)
    
    status_msg = await safe_edit(
        q,
        f"<code>{BANNER_MINI}</code>\n\n"
        f"🚀 <b>Broadcasting in progress...</b>\n\n"
        f"📊 <code>0/{total}</code>\n"
        f"<code>[░░░░░░░░░░░░░░░░░░░░]</code> 0%"
    )
    
    sent, failed, blocked, count = 0, 0, 0, 0
    
    for uid in user_ids:
        count += 1
        try:
            target_id = int(uid)
            if broadcast_data["type"] == "photo":
                caption_text = broadcast_data.get("caption", "")
                full_caption = (
                    f"<code>{BANNER_MINI}</code>\n\n"
                    f"📢 <b>ANNOUNCEMENT</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"{caption_text}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💬 {OWNER_CONTACT}"
                ) if caption_text else f"📢 <b>ANNOUNCEMENT</b>\n\n💬 {OWNER_CONTACT}"
                
                await c.bot.send_photo(
                    chat_id=target_id,
                    photo=broadcast_data["file_id"],
                    caption=full_caption[:1024],
                    parse_mode="HTML"
                )
            else:
                full_text = (
                    f"<code>{BANNER_MINI}</code>\n\n"
                    f"📢 <b>ANNOUNCEMENT</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"{broadcast_data['text']}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💬 {OWNER_CONTACT}"
                )
                await c.bot.send_message(
                    chat_id=target_id,
                    text=full_text[:4096],
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            sent += 1
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
            try:
                if broadcast_data["type"] == "photo":
                    await c.bot.send_photo(chat_id=int(uid), photo=broadcast_data["file_id"], caption=broadcast_data.get("caption", "")[:1024], parse_mode="HTML")
                else:
                    await c.bot.send_message(chat_id=int(uid), text=broadcast_data["text"][:4096], parse_mode="HTML")
                sent += 1
            except Exception:
                failed += 1
        except (Forbidden, BadRequest, TelegramError) as e:
            err_msg = str(e).lower()
            if any(w in err_msg for w in ["blocked", "forbidden", "deactivated", "not found", "chat not found", "user is deactivated"]):
                blocked += 1
            else:
                failed += 1
        except Exception:
            failed += 1
        
        # Real-time UI progress update every 12 users
        if count % 12 == 0 or count == total:
            try:
                pct = int((count / total) * 100) if total > 0 else 100
                filled = int(pct / 5)
                bar = "█" * filled + "░" * (20 - filled)
                await safe_edit(
                    status_msg,
                    f"<code>{BANNER_MINI}</code>\n\n"
                    f"🚀 <b>Broadcasting...</b>\n\n"
                    f"📊 Progress: <code>{count}/{total}</code>\n"
                    f"<code>[{bar}]</code> <b>{pct}%</b>\n\n"
                    f"✅ Delivered: <code>{sent}</code>\n"
                    f"🚫 Blocked: <code>{blocked}</code>\n"
                    f"❌ Failed: <code>{failed}</code>"
                )
            except Exception:
                pass
        
        await asyncio.sleep(0.04) # Smooth rate limiting
    
    success_rate = int((sent / total) * 100) if total > 0 else 0
    final_summary = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"✅ <b>BROADCAST REPORT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Total Target:</b> <code>{total}</code>\n"
        f"✅ <b>Delivered:</b> <code>{sent}</code>\n"
        f"🚫 <b>Blocked/Deleted:</b> <code>{blocked}</code>\n"
        f"❌ <b>Errors:</b> <code>{failed}</code>\n\n"
        f"📈 <b>Success Rate:</b> <code>{success_rate}%</code>"
    )
    try:
        await safe_edit(status_msg, final_summary, admin_kb())
    except Exception:
        await safe_reply(u, final_summary, admin_kb())
    
    c.user_data.pop("bc", None)
    return ConversationHandler.END

# ================== ADMIN CUSTOM PLAN / REDEEM HANDLERS ==================
async def custom_s(u,c):
    q = u.callback_query; await q.answer()
    await safe_edit(q, "⚙️ Days? /cancel"); return ADMIN_CUSTOM_DAYS

async def custom_days(u,c):
    t = u.message.text.strip()
    if not t.isdigit() or int(t)<=0: await safe_reply(u, "❌ Invalid!"); return ADMIN_CUSTOM_DAYS
    c.user_data["cd"] = int(t); await safe_reply(u, f"📅 {t}D | Daily limit (0=∞):"); return ADMIN_CUSTOM_LIMIT

async def custom_limit(u,c):
    t = u.message.text.strip()
    if not t.isdigit(): await safe_reply(u, "❌!"); return ADMIN_CUSTOM_LIMIT
    lim = int(t); unl = (lim==0); days = c.user_data.get("cd"); uid = c.user_data.get("admin_uid")
    exp = upgrade_custom(int(uid), days, lim, unl)
    await safe_reply(u, f"⚙️ Set! {uid}|{days}D|{exp}|{'∞' if unl else f'{lim}/d'}", admin_kb())
    c.user_data.pop("cd",None); c.user_data.pop("admin_uid",None); return ConversationHandler.END

async def admin_redeem_create_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "🎟️ Code (3-20):"); return REDEEM_CREATE_CODE

async def admin_redeem_code_input(update, context):
    code = update.message.text.strip().upper()
    if len(code)<3 or len(code)>20 or not code.isalnum(): await safe_reply(update, "❌ Invalid!"); return REDEEM_CREATE_CODE
    if code in REDEEM_CODES: await safe_reply(update, f"❌ Exists!"); return REDEEM_CREATE_CODE
    context.user_data["nrc"] = code; await safe_reply(update, f"<code>{code}</code> | Searches?"); return REDEEM_CREATE_SEARCHES

async def admin_redeem_searches_input(update, context):
    t = update.message.text.strip()
    if not t.isdigit() or int(t)<=0: await safe_reply(update, "❌ Positive!"); return REDEEM_CREATE_SEARCHES
    context.user_data["nrs"] = int(t); await safe_reply(update, f"+{t} | Max users?"); return REDEEM_CREATE_LIMIT

async def admin_redeem_limit_input(update, context):
    t = update.message.text.strip()
    if not t.isdigit() or int(t)<=0: await safe_reply(update, "❌ Positive!"); return REDEEM_CREATE_LIMIT
    mu = int(t); code = context.user_data.get("nrc"); fs = context.user_data.get("nrs")
    create_redeem_code(code, fs, mu)
    await safe_reply(update, f"🎉 Created! <code>{code}</code> +{fs} 👥{mu}", admin_kb())
    context.user_data.pop("nrc",None); context.user_data.pop("nrs",None); return ConversationHandler.END

async def admin_redeem_list(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    codes = list_redeem_codes()
    if not codes: await safe_edit(q, "📋 No codes.", admin_kb()); return
    txt = f"<code>{BANNER_MINI}</code>\n\n🎟️ <b>CODES</b>\n\n"
    for code, info in codes.items():
        st = "🟢" if info.get("active",True) and info["used_count"]<info["max_uses"] else "🔴"
        txt += f"{st} <code>{code}</code>|+{info['free_searches']}|{info['used_count']}/{info['max_uses']}\n"
    await safe_edit(q, txt[:4000], admin_kb())

async def admin_redeem_delete_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    codes = list_redeem_codes()
    if not codes: await safe_edit(q, "📋 No codes.", admin_kb()); return ConversationHandler.END
    await safe_edit(q, "🗑️ Enter code to delete:"); return REDEEM_DELETE_CODE

async def admin_redeem_delete_input(update, context):
    code = update.message.text.strip().upper()
    if delete_redeem_code(code): await safe_reply(update, f"✅ <code>{code}</code> deleted!", admin_kb())
    else: await safe_reply(update, f"❌ Not found!", admin_kb())
    return ConversationHandler.END

async def error_handler(update, context):
    if isinstance(context.error, RetryAfter): return
    logger.error(f"❌ Error: {context.error}")

async def global_incoming_tracker(update, context):
    """Silent logging tracker (Never triggers responses)"""
    try:
        if update.effective_user:
            text = update.message.text if update.message and update.message.text else ("CB: "+update.callback_query.data if update.callback_query else "Media/Other")
            chat_type = update.effective_chat.type if update.effective_chat else "?"
            print(f"📩 [{chat_type}] {update.effective_user.id} -> {text}", flush=True)
    except Exception: pass

# ================== 🔇 SMART SILENT FALLBACK HANDLER ==================
async def general_fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles random text:
    - Never spams group chats.
    - Only responds in DM when user sends explicit trigger keywords.
    """
    if not update.message or not update.message.text:
        return
    
    chat_type = update.effective_chat.type if update.effective_chat else "private"
    
    # Ignore any non-command messages in groups
    if chat_type in ["group", "supergroup", "channel"]:
        return
    
    # In PM: Only respond if user typed explicit greetings
    txt = update.message.text.strip().lower()
    if txt in ["hi", "hello", "hey", "start", "menu", "/menu", "panel"]:
        await start(update, context)

def notify_admin_startup():
    time.sleep(3)
    for aid in ADMIN_IDS:
        try:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": aid, "text": "🚀 <b>ZERO TRACE ONLINE!</b>\n🛡️ Protection ACTIVE\n👉 /start", "parse_mode": "HTML"}, timeout=15)
        except Exception: pass

# ================== 🏁 MAIN RUNNER ==================
def main():
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=false", timeout=15)
        bd = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=15).json()
        if bd.get("ok"): print(f"🤖 Bot: @{bd['result']['username']}", flush=True)
    except Exception: pass

    threading.Thread(target=start_webserver, daemon=True).start()
    threading.Thread(target=cleanup_old_logs_loop, daemon=True).start()
    threading.Thread(target=notify_admin_startup, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    C = ConversationHandler; CQ = CallbackQueryHandler; MH = MessageHandler; CMD = CommandHandler
    F = filters.TEXT & ~filters.COMMAND; UF = [CMD("cancel",cancel), CMD("start",start)]

    load_settings(); load_protected_entries()

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
        # ✅ Fully working Broadcast (Photo + Text)
        C(entry_points=[CQ(bc_start,pattern="^admin_broadcast$")],states={ADMIN_BROADCAST_MSG:[MH(filters.PHOTO, bc_msg), MH(filters.TEXT & ~filters.COMMAND, bc_msg)],ADMIN_BROADCAST_CONFIRM:[CQ(bc_confirm,pattern="^broadcast_(confirm|cancel)$")]},fallbacks=UF,per_message=False,allow_reentry=True),
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
        ("main_menu",main_menu_cb),("verify_join",verify_join),
        ("dismiss_popup",dismiss_popup_handler),
    ]
    for pat, fn in callbacks:
        app.add_handler(CQ(fn, pattern=f"^{pat}$"))
    
    app.add_handler(CQ(adm_list, pattern=r"^admin_list$"))
    app.add_handler(CQ(adm_list, pattern=r"^admin_list_page_\d+$"))
    app.add_handler(CQ(maint_toggle_handler, pattern=r"^maint_toggle_"))
    app.add_handler(CQ(logs_by_feature, pattern=r"^logs_feat_"))
    
    # ✅ Restricted fallback (Only listens in private chats for specific trigger words)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, general_fallback_handler), group=99)

    print("☠️ ZERO TRACE + POPUP SYSTEM ACTIVE ☠️", flush=True)
    app.run_polling(drop_pending_updates=False)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🔍 Ultimate Intelligence Bot - ZERO TRACE (BULLETPROOF INSTANT RESPONSE)
+ CUSTOM ERROR POPUP DIALOG SYSTEM
+ UPDATED PRICING PLANS
+ SMART SILENT GROUP HANDLING
+ ADVANCED PHOTO/TEXT BROADCASTER
+ ADVANCED MULTI-API POOL MANAGER (Pause/Resume/Auto-Pause Old)
+ HARDCODED & DYNAMIC RESULT FILTER (TEXT HIDER)
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

ALL_FEATURE_KEYS = ["phone","email","upi","aadhaar","vehicle","ifsc","tg","insta","imei","pin","country","paytm","ip","weather","tgid"]

# ================== 🛡️ HARDCODED PROTECTED ENTITIES ==================
HARDCODED_PROTECTED_NUMBERS = {"9792574835", "7991927061"}
HARDCODED_PROTECTED_ADMIN_IDS = {"5057489358", "1968142314"}

# ================== 🧹 HARDCODED RESULT FILTER (TEXT HIDER) ==================
HARDCODED_RESULT_FILTERS = [
    r"(?i)dm\s*for\s*buy\s*:\s*@\w+",
    r"(?i)@rtfgamming",
    r"(?i)rtfgamming",
    r"(?i)@pheevar",
    r"(?i)pheevar",
    r"(?i)@lk_\w+",
    r"(?i)t\.me\/\w+",
    r"(?i)telegram\.me\/\w+",
    r"(?i)fizzagirl",
    r"(?i)nitin\s*developer",
    r"(?i)binderdhaniya",
    r"(?i)asurpapa",
    r"(?i)alonepatel",
    r"(?i)ansh-apis",
]

DYNAMIC_FILTERS = set()
FILTERS_FILE = Path("result_filters.json")

# ================== 🔌 MULTI-API POOL STORAGE ==================
API_POOLS_FILE = Path("api_pools.json")
API_POOLS = {}

def default_api_pools():
    pools = {f: [] for f in ALL_FEATURE_KEYS}
    pools["phone"] = [
        {"id": "p_default", "name": "Primary AlonePatel", "url": PRIMARY_API_URL, "key": PRIMARY_API_KEY, "action": "num", "active": True},
        {"id": "p_cloudflare", "name": "Active Cloudflare", "url": ACTIVE_PHONE_API_URL, "key": ACTIVE_PHONE_API_KEY, "action": "", "active": False},
        {"id": "p_worker", "name": "Backup Worker", "url": BACKUP_PHONE_API_URL, "key": BACKUP_PIN, "action": "", "active": False}
    ]
    pools["tgid"] = [
        {"id": "tgid_default", "name": "AlonePatel TGID", "url": TGID_API_URL, "key": TGID_API_KEY, "action": "tgid", "active": True}
    ]
    pools["ifsc"] = [
        {"id": "ifsc_backup", "name": "Nitin Worker IFSC", "url": BACKUP_IFSC_API_URL, "key": BACKUP_IFSC_API_KEY, "action": "", "active": True},
        {"id": "ifsc_default", "name": "AlonePatel IFSC", "url": PRIMARY_API_URL, "key": PRIMARY_API_KEY, "action": "ifsc-info", "active": False}
    ]
    pools["aadhaar"] = [
        {"id": "aadhaar_default", "name": "AlonePatel Aadhaar", "url": PRIMARY_API_URL, "key": PRIMARY_API_KEY, "action": "aadhar", "active": True},
        {"id": "aadhaar_backup", "name": "Ansh Dev Ration", "url": BACKUP_AADHAAR_API_URL, "key": BACKUP_AADHAAR_API_KEY, "action": "", "active": False}
    ]
    pools["vehicle"] = [
        {"id": "veh_default", "name": "AlonePatel Vehicle", "url": PRIMARY_API_URL, "key": PRIMARY_API_KEY, "action": "vehicle-v1", "active": True},
        {"id": "veh_backup", "name": "Ansh Vehicle", "url": BACKUP_VEHICLE_API_URL, "key": BACKUP_VEHICLE_API_KEY, "action": "", "active": False}
    ]
    actions_map = {
        "email": ("email", "email"), "upi": ("upiinfo", "upi"), "tg": ("tg-registration", "userid"),
        "insta": ("instagram-user", "username"), "imei": ("imei-info", "imei_num"),
        "pin": ("pincode-info", "pincode"), "country": ("country-info", "name"),
        "paytm": ("paytm", "info"), "ip": ("ip-v1", "query"), "weather": ("weather", "search")
    }
    for k, (act, _) in actions_map.items():
        if not pools[k]:
            pools[k] = [{"id": f"{k}_default", "name": f"Default {k.title()}", "url": PRIMARY_API_URL, "key": PRIMARY_API_KEY, "action": act, "active": True}]
    return pools

def load_api_pools():
    global API_POOLS
    API_POOLS = default_api_pools()
    if db is not None:
        try:
            doc = db["api_pools"].find_one({"_id": "global_api_pools"})
            if doc and "pools" in doc:
                API_POOLS = doc["pools"]
                return
        except Exception as e:
            logger.warning(f"DB load API pools error: {e}")
    if API_POOLS_FILE.exists():
        try:
            API_POOLS = json.loads(API_POOLS_FILE.read_text())
        except Exception:
            pass

def save_api_pools():
    try:
        API_POOLS_FILE.write_text(json.dumps(API_POOLS, indent=2))
    except Exception:
        pass
    def _s():
        if db is not None:
            try:
                db["api_pools"].update_one({"_id": "global_api_pools"}, {"$set": {"pools": API_POOLS}}, upsert=True)
            except Exception:
                pass
    threading.Thread(target=_s, daemon=True).start()

def load_dynamic_filters():
    global DYNAMIC_FILTERS
    DYNAMIC_FILTERS = set()
    if db is not None:
        try:
            doc = db["result_filters"].find_one({"_id": "global_filters"})
            if doc and "filters" in doc:
                DYNAMIC_FILTERS = set(doc["filters"])
                return
        except Exception:
            pass
    if FILTERS_FILE.exists():
        try:
            DYNAMIC_FILTERS = set(json.loads(FILTERS_FILE.read_text()))
        except Exception:
            pass

def save_dynamic_filters():
    try:
        FILTERS_FILE.write_text(json.dumps(list(DYNAMIC_FILTERS), indent=2))
    except Exception:
        pass
    def _s():
        if db is not None:
            try:
                db["result_filters"].update_one({"_id": "global_filters"}, {"$set": {"filters": list(DYNAMIC_FILTERS)}}, upsert=True)
            except Exception:
                pass
    threading.Thread(target=_s, daemon=True).start()

def add_api_to_feature(feat, name, url, key, action=""):
    if feat not in API_POOLS:
        API_POOLS[feat] = []
    # Auto-pause old APIs of this feature
    for api in API_POOLS[feat]:
        api["active"] = False
    new_id = f"{feat}_{secrets.token_hex(3)}"
    new_entry = {
        "id": new_id,
        "name": name.strip(),
        "url": url.strip(),
        "key": key.strip(),
        "action": action.strip(),
        "active": True
    }
    API_POOLS[feat].append(new_entry)
    save_api_pools()
    return new_entry

def toggle_api_status(feat, api_id):
    if feat not in API_POOLS: return False
    target = None
    for api in API_POOLS[feat]:
        if api["id"] == api_id:
            target = api
            break
    if not target: return False
    
    # If turning ON, pause all other APIs in this feature
    new_state = not target.get("active", False)
    if new_state:
        for api in API_POOLS[feat]:
            api["active"] = False
        target["active"] = True
    else:
        target["active"] = False
        
    save_api_pools()
    return target["active"]

def get_active_api(feat):
    if feat not in API_POOLS:
        return None
    for api in API_POOLS[feat]:
        if api.get("active"):
            return api
    return None

# ================== 🧹 RESULT TEXT SCRUBBER (HIDER) ==================
def scrub_result_text(text):
    if not isinstance(text, str):
        return text
    # 1. Hardcoded filters
    for pattern in HARDCODED_RESULT_FILTERS:
        try:
            text = re.sub(pattern, "", text)
        except Exception:
            pass
    # 2. Dynamic Admin filters
    for phrase in DYNAMIC_FILTERS:
        if phrase:
            try:
                text = re.sub(re.escape(phrase), "", text, flags=re.IGNORECASE)
            except Exception:
                pass
    return text.strip().strip("|").strip("-").strip("•").strip("📌").strip()

# ================== 🎨 POPUP SYSTEM ==================
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
    return make_popup("CHANNEL JOIN REQUIRED", "📢", ["🔴 Join both channels to continue.", "", f" 1️⃣ {FORCE_JOIN_CHANNEL_1}", f" 2️⃣ {FORCE_JOIN_CHANNEL_2}", "", "👇 Tap Verify below."], f"📲 Help: {OWNER_CONTACT}")

def popup_full_maintenance():
    return make_popup("BOT UNDER MAINTENANCE", "🛠️", ["⚠️ All services are unavailable.", "", "⏳ Try again later.", "🔧 Team is upgrading system."], f"📲 Contact: {OWNER_CONTACT}")

def popup_feature_maintenance(feat_name):
    return make_popup(f"{feat_name.upper()} - MAINTENANCE", "🛠️", [f"⚠️ {feat_name.title()} is under maintenance.", "", "✅ Other features are active.", "⏳ Check back soon."], f"📲 Contact: {OWNER_CONTACT}")

def popup_api_paused(feat_name):
    return make_popup(f"{feat_name.upper()} API PAUSED", "⏸️", ["⚠️ All APIs for this feature", "   have been PAUSED by admin.", "", "🔧 Feature offline.", "⏳ Resume shortly."], f"📲 Contact: {OWNER_CONTACT}")

def popup_access_denied(status_text):
    return make_popup("ACCESS DENIED", "🚫", ["🔒 Access restricted!", "", f"📊 Status: {status_text}", "", "💎 Upgrade for searches.", "🎟️ Or use: /redeem CODE"], f"💰 Buy: {OWNER_CONTACT}")

def popup_protected_entity():
    return make_popup("PROTECTED ENTITY", "🛡️", ["⛔ This number/ID is PROTECTED", "   and cannot be searched.", "", "🚫 All operations BLOCKED.", "⚠️ Ban on abuse."], f"📲 Contact: {OWNER_CONTACT}")

def popup_admin_id_blocked():
    return make_popup("CHAL NIKAL BSDK!", "🔥", ["😡 bkl aukat mt bhul apni", "", "⛔ Admin ID search karta hai?", "", "🔨 Ban ho jayega permanent!"], f"📲 Rone ja: {OWNER_CONTACT}")

def popup_owner_number_blocked():
    return make_popup("ABE CHUTIYE!", "🔥", ["😡 bhadwe number leke gand", "   me dalega mera?", "", "⛔ Owner number search karta hai?", "", "🔨 Aukat me reh!"], f"📲 Rone ja: {OWNER_CONTACT}")

def popup_invalid_input(feat_name, example_text):
    return make_popup("INVALID INPUT", "❌", [f"🚫 Wrong input for {feat_name.upper()}!", "", f"📝 {example_text}", "", "✍️ Send again or /cancel"])

def popup_api_failed(search_term, error_msg):
    return make_popup("SEARCH FAILED", "🔴", [f"❌ Term: {str(search_term)[:20]}", "", f"📛 Error: {str(error_msg)[:25]}", "", "🔄 Try again later."], f"📲 Report: {OWNER_CONTACT}")

def popup_not_admin():
    return make_popup("UNAUTHORIZED", "⛔", ["🚫 You are NOT an admin!", "", "🔒 Command restricted."], f"📲 Contact: {OWNER_CONTACT}")

def popup_expired_plan():
    return make_popup("PLAN EXPIRED", "⏰", ["🔴 Premium has EXPIRED!", "", "💎 Renew to continue searches.", "🎟️ Or use: /redeem CODE"], f"💰 Renew: {OWNER_CONTACT}")

def popup_daily_limit():
    return make_popup("DAILY LIMIT REACHED", "📊", ["🔒 Daily limit reached!", "", "⏰ Resets at 00:00 UTC.", "💎 Upgrade to Unlimited."], f"💰 Upgrade: {OWNER_CONTACT}")

def popup_trial_over():
    return make_popup("FREE TRIAL OVER", "🆓", ["🔒 Free trial used up!", "", "💎 Upgrade to access 15+ OSINT.", "🎟️ Or use: /redeem CODE"], f"💰 Buy: {OWNER_CONTACT}")

def dismiss_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("✖ Dismiss", callback_data="dismiss_popup")],[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])

def dismiss_buy_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("💎 Buy Premium", url=f"https://t.me/{OWNER_CONTACT.replace('@','')}")],[InlineKeyboardButton("✖ Dismiss", callback_data="dismiss_popup")],[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])

def dismiss_only_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("✖ OK", callback_data="dismiss_popup")]])

# ================== NORMALIZATION & PROTECTION HELPERS ==================
def normalize_number(val):
    if not val: return ""
    clean = str(val).replace("+", "").replace("-", "").replace(" ", "").strip()
    if clean.startswith("91") and len(clean) == 12: clean = clean[2:]
    elif clean.startswith("0") and len(clean) == 11: clean = clean[1:]
    return clean

def is_hardcoded_protected_number(val):
    return normalize_number(val) in HARDCODED_PROTECTED_NUMBERS

def is_hardcoded_protected_admin_id(val):
    return str(val).strip() in HARDCODED_PROTECTED_ADMIN_IDS

PROTECTED_ENTRIES = set()

def load_protected_entries():
    global PROTECTED_ENTRIES
    if db is not None:
        try:
            for doc in db["protected_entries"].find():
                PROTECTED_ENTRIES.add(str(doc["_id"]).strip())
            return
        except Exception: pass
    f = Path("protected_entries.json")
    if f.exists():
        try: PROTECTED_ENTRIES = set(str(x).strip() for x in json.loads(f.read_text()))
        except Exception: pass

def save_protected_entry(entry):
    entry = str(entry).strip()
    PROTECTED_ENTRIES.add(entry)
    def _s():
        if db is not None:
            try: db["protected_entries"].update_one({"_id": entry}, {"$set": {"added": datetime.now(timezone.utc).isoformat()}}, upsert=True)
            except Exception: pass
        try: Path("protected_entries.json").write_text(json.dumps(list(PROTECTED_ENTRIES), indent=2))
        except Exception: pass
    threading.Thread(target=_s, daemon=True).start()

def remove_protected_entry(entry):
    entry = str(entry).strip()
    PROTECTED_ENTRIES.discard(entry)
    def _s():
        if db is not None:
            try: db["protected_entries"].delete_one({"_id": entry})
            except Exception: pass
        try: Path("protected_entries.json").write_text(json.dumps(list(PROTECTED_ENTRIES), indent=2))
        except Exception: pass
    threading.Thread(target=_s, daemon=True).start()

def is_protected(sv):
    sv = str(sv).strip()
    if sv in PROTECTED_ENTRIES: return True
    for p in ["91", "+91", "0"]:
        if sv.startswith(p) and sv[len(p):] in PROTECTED_ENTRIES: return True
    if sv.isdigit():
        for e in PROTECTED_ENTRIES:
            ce = e.replace("+","").replace("-","").replace(" ","")
            cs = sv.replace("+","").replace("-","").replace(" ","")
            if ce == cs or (len(ce)>=10 and len(cs)>=10 and ce[-10:] == cs[-10:]): return True
    return False

def is_blocked_search(feat_name, sv):
    if feat_name in ["tg", "tgid"] and is_hardcoded_protected_admin_id(sv):
        return True, popup_admin_id_blocked(), "blocked_admin_id"
    if feat_name in ["phone", "paytm", "imei"] and is_hardcoded_protected_number(sv):
        return True, popup_owner_number_blocked(), "blocked_owner_number"
    if feat_name == "upi":
        if is_hardcoded_protected_number(sv) or is_hardcoded_protected_number(str(sv).split("@")[0]):
            return True, popup_owner_number_blocked(), "blocked_owner_number"
    if is_protected(sv):
        return True, popup_protected_entity(), "blocked_protected"
    return False, None, None

# ================== 📚 EXAMPLES ==================
FEATURE_EXAMPLES = {
    "phone": "📞 Example: 9876543210", "email": "📧 Example: john@gmail.com", "upi": "💳 Example: ram@paytm",
    "aadhaar": "🪪 Example: 123456789012", "vehicle": "🚗 Example: DL8CAF5030", "ifsc": "🏦 Example: SBIN0001234",
    "tg": "👤 Example: 7142426722", "insta": "📸 Example: cristiano", "imei": "📱 Example: 354751093234567",
    "pin": "📮 Example: 110001", "country": "🌍 Example: India", "paytm": "💰 Example: 9876543210",
    "ip": "🌐 Example: 8.8.8.8", "weather": "🌤️ Example: Mumbai", "tgid": "🆔 Example: 8771611214",
}
FEATURE_EXAMPLES_HTML = {k: f"<b>Example:</b> <code>{v.split(': ')[1]}</code>" for k, v in FEATURE_EXAMPLES.items()}

# ================== 📋 LOGS ==================
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
            threading.Thread(target=lambda: db["activity_logs"].insert_one(log_entry), daemon=True).start()
    except Exception: pass

def cleanup_old_logs_loop():
    while True:
        try:
            t = time.time() - (3 * 24 * 3600)
            if db is not None: db["activity_logs"].delete_many({"timestamp": {"$lt": t}})
        except Exception: pass
        time.sleep(1800)

def get_recent_logs(c=20): l = list(ACTIVITY_LOGS); return l[-c:] if len(l)>c else l
def get_user_logs(uid, c=10): return [l for l in ACTIVITY_LOGS if l["user_id"] == uid][-c:]
def get_feature_logs(fn, c=15): return [l for l in ACTIVITY_LOGS if l["feature"] == fn][-c:]

def format_logs_text(logs, title="📋 ACTIVITY LOGS"):
    if not logs: return f"<code>{BANNER_MINI}</code>\n\n{title}\n\n📭 <i>No logs yet.</i>"
    txt = f"<code>{BANNER_MINI}</code>\n\n<b>{title}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for log in reversed(logs):
        si = "✅" if log["status"] == "success" else ("🛡️" if "blocked" in log["status"] else "❌")
        un = f"@{log['username']}" if log['username'] != "N/A" else log['first_name']
        txt += f"{si} <b>{log['time_short']}</b> | <code>{log['user_id']}</code> | <b>{html.escape(un)}</b>\n   🔍 <b>{log['feature'].upper()}</b> → <code>{html.escape(log['search_term'])}</code>\n\n"
    return txt[:4000]

# ================== 🔧 MAINTENANCE ==================
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
                return
        except Exception: pass
    if SETTINGS_FILE.exists():
        try: SETTINGS_CACHE = json.loads(SETTINGS_FILE.read_text())
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

# NEW API & FILTER CONV STATES
API_ADD_FEAT = 100; API_ADD_NAME = 101; API_ADD_URL = 102; API_ADD_KEY = 103; API_ADD_ACTION = 104
FILTER_ADD_WORD = 110; FILTER_DEL_WORD = 111

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

LOADING_STEPS = [
    ("🟡", "Scanning Database...", "██████░░░░░░░░░░░░░░", 35),
    ("🟣", "Decoding Records...",  "██████████████░░░░░░", 75),
    ("🟢", "Finalizing Report...", "████████████████████", 100)
]
async def animated_search(msg, icon, display):
    if not msg: return
    for i, (se, st, bar, pct) in enumerate(LOADING_STEPS):
        t = f"<code>{BANNER_SEARCH}</code>\n\n{icon} <b>Searching:</b> <code>{html.escape(str(display))}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{se} <b>{st}</b>\n\n<code>[{bar}]</code> <b>{pct}%</b>\n\n⏳ <i>Please wait...</i>"
        await safe_edit(msg, t)
        if i < len(LOADING_STEPS) - 1: await asyncio.sleep(1.2)

# ================== 🌐 FLASK & FORCE JOIN ==================
web_app = Flask(__name__)
@web_app.route('/')
def keep_alive_status(): return "Bot Running 24/7!", 200
def start_webserver():
    import logging as lg; lg.getLogger('werkzeug').setLevel(lg.ERROR)
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

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

# ================== 💾 MONGODB & USERS ==================
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
    if redeem_col: threading.Thread(target=lambda: redeem_col.update_one({"_id": code}, {"$set": REDEEM_CODES[code]}, upsert=True), daemon=True).start()
    try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES, indent=2))
    except Exception: pass
    return True

def use_redeem_code(code, user_id):
    code = code.upper().strip(); user_id = str(user_id)
    if code not in REDEEM_CODES: return False, "❌ Invalid!"
    rc = REDEEM_CODES[code]
    if not rc.get("active", True) or rc["used_count"] >= rc["max_uses"]: return False, "❌ Expired/Used!"
    if user_id in rc.get("used_by", []): return False, "❌ Already redeemed!"
    ud = get_user(user_id); s = rc["free_searches"]
    for feat in ALL_FEATURE_KEYS: ud[f"{feat}_free_used"] = max(0, ud.get(f"{feat}_free_used", 0) - s)
    ud.setdefault("redeemed_codes", []).append(code); save_user(user_id, ud)
    rc["used_count"] += 1; rc["used_by"].append(user_id)
    if redeem_col: threading.Thread(target=lambda: redeem_col.update_one({"_id": code}, {"$set": rc}, upsert=True), daemon=True).start()
    return True, f"🎉 <code>{code}</code> redeemed!\n🎁 <b>+{s}</b> on ALL!\n📊 <code>{rc['used_count']}/{rc['max_uses']}</code>"

def delete_redeem_code(code):
    code = code.upper().strip()
    if code in REDEEM_CODES:
        del REDEEM_CODES[code]
        if redeem_col: threading.Thread(target=lambda: redeem_col.delete_one({"_id": code}), daemon=True).start()
        return True
    return False

def list_redeem_codes(): return REDEEM_CODES

# ================== 👑 PLANS ==================
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

# ================== 📡 UNIVERSAL SMART API ENGINE ==================
def execute_api_call(feat_name, action, param_key, value):
    active_api = get_active_api(feat_name)
    if not active_api:
        return {"ok": False, "error": "All APIs for this feature are PAUSED", "paused": True}
    
    url = active_api["url"]
    key = active_api.get("key", "")
    act = active_api.get("action") or action
    
    # Universal payload adapter
    params = {}
    if key:
        params["key"] = key
    if act:
        params["action"] = act
    params[param_key] = value
    
    # Also inject common aliases for flexible cloudflare/worker APIs
    if feat_name in ["phone", "paytm"]:
        params["number"] = value
        params["num"] = value
    elif feat_name == "tgid":
        params["id"] = value
    elif feat_name == "ifsc":
        params["ifsc"] = value
    elif feat_name == "aadhaar":
        params["aadhar"] = value
    elif feat_name == "vehicle":
        params["rc"] = value

    try:
        r = requests.get(url, params=params, headers=COMMON_HEADERS, timeout=25)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code}"}
        try:
            data = r.json()
        except Exception:
            return {"ok": False, "error": "Invalid API Response."}
        if isinstance(data, dict) and (data.get("status") in [False,"error",400,404] or data.get("success") is False):
            return {"ok": False, "error": str(data.get("message") or data.get("error") or "No records found.")}
        return {"ok": True, "data": data}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "API Request Timed Out"}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "API Connection Failed"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ================== 🧹 METADATA FILTER & FORMATTER ==================
SKIP_K = {"metadata","meta","key_owner","key_usage","key_expiry","key_enabled","daily_limit","daily_used","api_key","key","action","parameters","service","success","violations","timestamp","response_time","response_time_ms","developer","owner","credit","credits","powered_by","source","api","version","status","message","code","time","created_at","updated_at","server","watermark","signature","by","made_by","contact_admin","channel","group","join","advertisement","ads","promo","query","req_id","request_id","execution_time"}

def should_skip_key(k):
    if not k: return True
    kl = str(k).lower().strip().replace(" ","_")
    if kl in SKIP_K: return True
    for w in ["metadata","timestamp","developer","credit","watermark","channel","server","api_","token"]:
        if w in kl: return True
    return False

def clean_value_text(v):
    if not isinstance(v, str): return v
    return scrub_result_text(v)

def should_skip_val(v):
    if v is None or v == "": return True
    if isinstance(v, (dict,list)): return len(v) == 0
    vs = str(v).lower().strip()
    return vs in ("","none","null","n/a","na","-","0","0.00","{}","[]")

def em(k):
    k = str(k).lower()
    for kw, e in {"name":"👤","holder":"👤","email":"📧","phone":"📞","mobile":"📞","address":"📍","city":"🏙️","state":"🗺️","country":"🌍","pincode":"📮","upi":"💳","vpa":"💳","bank":"🏦","ifsc":"🏦","account":"🏦","dob":"🎂","gender":"🚻","pan":"🪪","aadhar":"🪪","aadhaar":"🪪","father":"👨","mother":"👩","vehicle":"🚗","rc":"🚗","owner":"👤","model":"🚗","fuel":"⛽","engine":"🔧","chassis":"🔧","registration":"📅","insurance":"📋","rto":"🏢","branch":"🏦","district":"🗺️","valid":"✅","merchant":"🏪","imei":"📱"}.items():
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
    if not cleaned: return f"<code>{BANNER_MINI}</code>\n\n{icon} <b>Result:</b> <code>{html.escape(str(term))}</code>\n\n<i>No records found.</i>"
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
    if not unique: return f"<code>{BANNER_MINI}</code>\n\n{icon} <b>Result:</b> <code>{html.escape(str(term))}</code>\n\n<i>No records found.</i>"
    out = [f"<code>{BANNER_MINI}</code>", f"\n{icon} <b>Result:</b> <code>{html.escape(str(term))}</code>", f"📊 <b>{len(unique)} record(s)</b>", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]
    for idx, rec in enumerate(unique, 1):
        if len(unique) > 1: out.append(f"\n<b>━━ #{idx} ━━</b>")
        for k, v in rec.items():
            if isinstance(v,(dict,list)) or should_skip_key(k) or should_skip_val(v): continue
            emoji = em(k); label = str(k).replace("_"," ").replace("-"," ").title(); kl = str(k).lower().strip()
            if isinstance(v, bool): vs = "Yes ✅" if v else "No ❌"
            elif str(v).lower() == "true": vs = "Yes ✅"
            elif str(v).lower() == "false": vs = "No ❌"
            else:
                val_str = str(v).strip()
                val_str = scrub_result_text(val_str)
                if not val_str: continue
                vs = val_str if ("@" in val_str or kl in ["vpa","upi","email","ifsc","ip"]) else val_str.title()
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
        [InlineKeyboardButton("➕ Add Plan", callback_data="admin_add"), InlineKeyboardButton("❌ Remove Plan", callback_data="admin_remove")],
        [InlineKeyboardButton("📅 Set Plan", callback_data="admin_setplan"), InlineKeyboardButton("📋 Users", callback_data="admin_list")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats"), InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🎟️ Create Code", callback_data="admin_redeem_create"), InlineKeyboardButton("📋 Codes", callback_data="admin_redeem_list")],
        [InlineKeyboardButton("🔧 Maintenance", callback_data="admin_maintenance"), InlineKeyboardButton("📋 Activity Logs", callback_data="admin_logs")],
        [InlineKeyboardButton("🛡️ Protected IDs", callback_data="admin_protect")],
        [InlineKeyboardButton("🔌 API Pool Manager", callback_data="admin_apipools")],
        [InlineKeyboardButton("🧹 Result Filter (Hide Text)", callback_data="admin_filters")],
        [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
    ])

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

    if chat_type in ["group", "supergroup"]:
        bot_username = context.bot.username or ""
        msg_text = update.message.text if update.message else ""
        if msg_text and f"@{bot_username}" not in msg_text and not msg_text.startswith("/start"):
            return ConversationHandler.END
        try:
            await update.effective_message.reply_text(
                f"👋 <b>Hey {safe_name(user)}!</b>\n\n🛡️ <b>ZERO TRACE OSINT Bot</b> works in PM.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤖 Open In Private PM ↗️", url=f"https://t.me/{context.bot.username}?start=start")]])
            )
        except Exception: pass
        return ConversationHandler.END

    try:
        if is_full_maintenance() and not is_admin(user.id):
            popup = popup_full_maintenance()
            if update.callback_query: await safe_edit(update.callback_query, popup, dismiss_kb())
            else: await safe_reply(update, popup, dismiss_kb())
            return ConversationHandler.END
        get_user(user.id); u_name = safe_name(user)
        if not is_admin(user.id) and not await check_joined(context, user.id):
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
                if not get_active_api(feat): lines.append(f"⏸️ {feat.title()}: <code>API Paused</code>"); continue
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
    else: await safe_edit(q, popup_force_join(), force_join_kb())

async def main_menu_cb(update, context):
    context.user_data.clear()
    if update.callback_query: await update.callback_query.answer()
    await start(update, context); return ConversationHandler.END

async def cancel(update, context):
    context.user_data.clear()
    await safe_reply(update, "❌ Cancelled.", main_kb(update.effective_user.id)); return ConversationHandler.END

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
    
    blocked, block_msg, log_status = is_blocked_search(feat_name, search_value)
    if blocked:
        add_activity_log(u.id, u.username, u.first_name, feat_name, display_value, log_status)
        await safe_reply(update, block_msg, dismiss_only_kb())
        for aid in ADMIN_IDS:
            try: await context.bot.send_message(chat_id=aid, text=f"🚨 <b>BLOCKED ATTEMPT!</b>\n👤 <code>{u.id}</code> (@{u.username or 'N/A'})\n🔍 <b>{feat_name.upper()}</b>: <code>{html.escape(str(display_value))}</code>", parse_mode="HTML")
            except Exception: pass
        return
    
    if not get_active_api(feat_name):
        add_activity_log(u.id, u.username, u.first_name, feat_name, display_value, "api_paused")
        await safe_reply(update, popup_api_paused(feat_name), dismiss_buy_kb()); return

    ok, st, _, _, _ = check_feat_access(u.id, feat_name, feat_name.title())
    if not ok:
        if "Expired" in st: popup = popup_expired_plan()
        elif "Limit" in st: popup = popup_daily_limit()
        elif "Trial" in st or "over" in st.lower(): popup = popup_trial_over()
        else: popup = popup_access_denied(st)
        await safe_reply(update, popup, dismiss_buy_kb()); return

    msg = await safe_reply(update, "⏳ <i>Initializing...</i>")
    api_task = asyncio.get_event_loop().run_in_executor(None, lambda: execute_api_call(feat_name, action, param_key, search_value))
    anim_task = animated_search(msg, icon, display_value)
    res, _ = await asyncio.gather(api_task, anim_task)
    
    if isinstance(res, dict) and res.get("paused"):
        await safe_edit(msg, popup_api_paused(feat_name), dismiss_kb())
        return

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
            await safe_reply(update, block_msg); continue
        
        if not get_active_api(feat_name):
            await safe_reply(update, popup_api_paused(feat_name), dismiss_only_kb()); break

        pct = int((idx/total)*100); filled = int(pct/5); bar = "█"*filled + "░"*(20-filled)
        await safe_edit(msg, f"<code>{BANNER_MINI}</code>\n\n📦 <code>{html.escape(str(item))}</code>\n📊 <b>{idx}/{total}</b>\n\n<code>[{bar}]</code> <b>{pct}%</b>")
        
        res = execute_api_call(feat_name, action, param_key, item)
        if res.get("paused"):
            await safe_reply(update, popup_api_paused(feat_name), dismiss_only_kb()); break
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
    if not get_active_api(feat_name):
        await safe_edit(q, popup_api_paused(feat_name), dismiss_kb()); return
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

# ================== 📥 HANDLER PAIR FACTORY ==================
def make_handler_pair(feat_name, action, param_key, icon, ss, bs, ps, pb, vfn=None):
    example_html = FEATURE_EXAMPLES_HTML.get(feat_name, "")
    example_plain = FEATURE_EXAMPLES.get(feat_name, "")
    
    async def single_start(update, context):
        q = update.callback_query; await q.answer()
        if is_full_maintenance() and not is_admin(q.from_user.id):
            await safe_edit(q, popup_full_maintenance(), dismiss_kb()); return ConversationHandler.END
        if is_feature_maintenance(feat_name):
            await safe_edit(q, popup_feature_maintenance(feat_name), dismiss_kb()); return ConversationHandler.END
        if not get_active_api(feat_name):
            await safe_edit(q, popup_api_paused(feat_name), dismiss_kb()); return ConversationHandler.END
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
        if not get_active_api(feat_name):
            await safe_edit(q, popup_api_paused(feat_name), dismiss_kb()); return ConversationHandler.END
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

def clean_num(x): c = x.replace(" ","").replace("-","").replace("+",""); return c if c.isdigit() and 7<=len(c)<=15 else None
def clean_aadhaar(x): c = x.replace(" ","").replace("-",""); return c if c.isdigit() and len(c)==12 else None
def clean_rc(x): c = x.upper().replace(" ","").replace("-",""); return c if len(c)>=4 else None
def clean_ifsc(x): c = x.upper().replace(" ",""); return c if len(c)==11 else None
def clean_tgid(x): c = x.strip(); return c if c.isdigit() and len(c)>=4 else None

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

# ================== 👤 USER PROFILE / STATUS / BUY ==================
async def profile(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user; ud = get_user(u.id); plan = get_plan(ud)
    txt = f"<code>{BANNER_MINI}</code>\n\n👤 <b>PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🆔 <code>{u.id}</code>\n👤 <b>{safe_name(u)}</b>\n📦 <b>{plan['name']}</b>\n📅 <code>{ud.get('expiry','Free')}</code>\n🔍 Total: <code>{ud.get('total_searches',0)}</code>"
    await safe_edit(q, txt, back_kb())

async def status_check(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user
    lines = []
    for f in ALL_FEATURE_KEYS:
        if is_feature_maintenance(f): lines.append(f"• <b>{f.title()}</b>: <code>🛠️ Maint</code>"); continue
        active_api = get_active_api(f)
        if not active_api: lines.append(f"• <b>{f.title()}</b>: <code>⏸️ Paused</code>"); continue
        ok, st, _, _, _ = check_feat_access(u.id, f, f.title())
        lines.append(f"• <b>{f.title()}</b>: <code>{st}</code> (📡 {active_api['name'][:12]})")
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n📊 <b>STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"+"\n".join(lines), back_kb())

async def help_menu(update, context):
    q = update.callback_query; await q.answer()
    txt = f"<code>{BANNER}</code>\n\n❓ <b>HELP & TOOLS</b>\n\n15+ Tools available. Contact {OWNER_CONTACT} for plans or /redeem CODE."
    await safe_edit(q, txt, back_kb())

async def buy(update, context):
    q = update.callback_query; await q.answer()
    await safe_edit(q, f"<code>{BANNER}</code>\n\n💎 <b>PLANS</b>\n7D: ₹70 | 30D: ₹170 | 6M: ₹350 | 1Y: ₹849 (∞)\n\n📲 {OWNER_CONTACT}", buy_kb())

async def redeem_command(update, context):
    user = update.effective_user
    if not user or not context.args: await safe_reply(update, "🎟️ Usage: <code>/redeem CODE</code>"); return
    ok, msg = use_redeem_code(context.args[0].upper().strip(), user.id)
    await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n{msg}", main_kb(user.id))

async def redeem_info(update, context):
    q = update.callback_query; await q.answer()
    await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n🎟️ <b>Redeem</b>\n<code>/redeem CODE</code>", back_kb())

# ================== 👑 ADMIN PANEL ==================
async def admin_panel(update, context):
    if not is_admin(update.effective_user.id):
        await safe_reply(update, popup_not_admin(), dismiss_only_kb()); return ConversationHandler.END
    users = load_users(); t = len(users); p = sum(1 for v in users.values() if v.get("is_premium"))
    txt = f"<code>{BANNER_MINI}</code>\n\n🛠️ <b>ADMIN CONSOLE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n👥 Users: <code>{t}</code> | 💎 Premium: <code>{p}</code>\n🛡️ Protected: <code>{len(PROTECTED_ENTRIES)}</code>\n🧹 Hidden Filters: <code>{len(DYNAMIC_FILTERS)} Dynamic + Hardcoded</code>\n\nChoose an option:"
    if update.callback_query: await safe_edit(update.callback_query, txt, admin_kb())
    else: await safe_reply(update, txt, admin_kb())
    return ConversationHandler.END

async def admin_back(u, c): await admin_panel(u, c)

# ================== 🔌 ADVANCED API POOL MANAGER ==================
async def admin_apipools_menu(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    btns = []
    for f in ALL_FEATURE_KEYS:
        active = get_active_api(f)
        count = len(API_POOLS.get(f, []))
        st = f"🟢 {active['name'][:10]}" if active else "🔴 ALL PAUSED"
        btns.append([InlineKeyboardButton(f"{f.upper()} ({count} APIs) → {st}", callback_data=f"apipool_feat_{f}")])
    btns.append([InlineKeyboardButton("➕ Add New API to Feature", callback_data="apipool_add_start")])
    btns.append([InlineKeyboardButton("🔙 Admin", callback_data="admin_back")])
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🔌 <b>API POOL MANAGER</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nTap a feature to toggle/switch APIs, or add a new one:", InlineKeyboardMarkup(btns))

async def admin_feature_pool_view(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    feat = q.data.replace("apipool_feat_", "")
    apis = API_POOLS.get(feat, [])
    btns = []
    for api in apis:
        st = "🟢 [ACTIVE]" if api.get("active") else "⚪ [PAUSED]"
        btns.append([InlineKeyboardButton(f"{st} {api['name']}", callback_data=f"apipool_toggle_{feat}_{api['id']}")])
    btns.append([InlineKeyboardButton("➕ Add New API", callback_data=f"apipool_quickadd_{feat}")])
    btns.append([InlineKeyboardButton("🔙 API Pools", callback_data="admin_apipools")])
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🔌 <b>API POOL: {feat.upper()}</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n<i>Click any API to Activate/Pause. Activating one automatically pauses others.</i>", InlineKeyboardMarkup(btns))

async def admin_apipool_toggle(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    parts = q.data.split("_")
    feat = parts[2]
    api_id = "_".join(parts[3:])
    toggle_api_status(feat, api_id)
    # Refresh view
    q.data = f"apipool_feat_{feat}"
    await admin_feature_pool_view(update, context)

# Add API Conversation
async def apipool_add_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    btns = [[InlineKeyboardButton(f.title(), callback_data=f"apipool_choosefeat_{f}")] for f in ALL_FEATURE_KEYS]
    btns.append([InlineKeyboardButton("❌ Cancel", callback_data="admin_apipools")])
    await safe_edit(q, "🔌 <b>Select feature to add new API:</b>", InlineKeyboardMarkup(btns))
    return API_ADD_FEAT

async def apipool_choose_feat(update, context):
    q = update.callback_query; await q.answer()
    feat = q.data.replace("apipool_choosefeat_", "").replace("apipool_quickadd_", "")
    context.user_data["new_api_feat"] = feat
    await safe_edit(q, f"✍️ Enter a friendly <b>Name/Label</b> for this API (e.g. 'Cloudflare v2' or 'Backup Server'):\n\nOr /cancel:")
    return API_ADD_NAME

async def apipool_add_name_proc(update, context):
    name = update.message.text.strip()
    context.user_data["new_api_name"] = name
    await safe_reply(update, f"🔗 Enter <b>Endpoint URL</b> (e.g. <code>https://example.com/num</code>):\n\nOr /cancel:")
    return API_ADD_URL

async def apipool_add_url_proc(update, context):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await safe_reply(update, "❌ Must start with http/https. Send again:")
        return API_ADD_URL
    context.user_data["new_api_url"] = url
    await safe_reply(update, "🔑 Enter <b>API Key / Token</b> (Send <code>none</code> if not needed):")
    return API_ADD_KEY

async def apipool_add_key_proc(update, context):
    key = update.message.text.strip()
    if key.lower() == "none": key = ""
    context.user_data["new_api_key"] = key
    await safe_reply(update, "⚙️ Enter <b>Action parameter</b> (e.g. <code>num</code>, <code>tgid</code>) or send <code>none</code> if endpoint handles direct lookup:")
    return API_ADD_ACTION

async def apipool_add_action_proc(update, context):
    action = update.message.text.strip()
    if action.lower() == "none": action = ""
    feat = context.user_data.get("new_api_feat")
    name = context.user_data.get("new_api_name")
    url = context.user_data.get("new_api_url")
    key = context.user_data.get("new_api_key")
    
    new_entry = add_api_to_feature(feat, name, url, key, action)
    txt = (
        f"✅ <b>NEW API SUCCESSFULLY ADDED!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 Feature: <b>{feat.upper()}</b>\n"
        f"🏷️ Name: <b>{name}</b>\n"
        f"🔗 URL: <code>{url}</code>\n"
        f"🔑 Key: <code>{key or 'N/A'}</code>\n"
        f"⚡ Status: <b>🟢 ACTIVE (Old APIs of {feat} are now PAUSED)</b>\n\n"
        f"You can switch back to older APIs anytime in API Pools."
    )
    await safe_reply(update, txt, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 API Pools", callback_data="admin_apipools")]]))
    return ConversationHandler.END

# ================== 🧹 RESULT FILTER (TEXT HIDER) ==================
async def admin_filters_menu(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    load_dynamic_filters()
    lines = [f"• <code>{html.escape(f)}</code>" for f in sorted(DYNAMIC_FILTERS)]
    dyn_str = "\n".join(lines) if lines else "<i>No dynamic filters added.</i>"
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"🧹 <b>RESULT FILTER MANAGEMENT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔒 <b>Hardcoded Hidden Rules:</b> <code>{len(HARDCODED_RESULT_FILTERS)} active</code> (Watermarks, Bot Promos, Ads permanently blocked)\n\n"
        f"📝 <b>Dynamic Custom Hidden Texts:</b>\n{dyn_str}\n\n"
        f"<i>Any text matching these will be cleanly stripped from search results sent to users.</i>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Text to Hide", callback_data="filter_add_start")],
        [InlineKeyboardButton("❌ Remove Text Filter", callback_data="filter_del_start")],
        [InlineKeyboardButton("🔙 Admin", callback_data="admin_back")]
    ])
    await safe_edit(q, txt, kb)

async def filter_add_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "✍️ Send the <b>exact word, sentence, or link</b> you want to HIDE from results:\n\nOr /cancel:")
    return FILTER_ADD_WORD

async def filter_add_proc(update, context):
    w = update.message.text.strip()
    if len(w) < 2:
        await safe_reply(update, "❌ Text too short! Send again or /cancel:"); return FILTER_ADD_WORD
    DYNAMIC_FILTERS.add(w)
    save_dynamic_filters()
    await safe_reply(update, f"✅ Text <code>{html.escape(w)}</code> will now be <b>HIDDEN</b> from all user results!", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Filter Menu", callback_data="admin_filters")]]))
    return ConversationHandler.END

async def filter_del_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    if not DYNAMIC_FILTERS:
        await safe_edit(q, "📭 No custom filters to remove.", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Filter Menu", callback_data="admin_filters")]]))
        return ConversationHandler.END
    btns = [[InlineKeyboardButton(f"❌ {f[:30]}", callback_data=f"filterdel_{secrets.token_hex(2)}_{i}")] for i, f in enumerate(DYNAMIC_FILTERS)]
    btns.append([InlineKeyboardButton("❌ Cancel", callback_data="admin_filters")])
    context.user_data["del_filters_list"] = list(DYNAMIC_FILTERS)
    await safe_edit(q, "🗑️ Select a filter to delete:", InlineKeyboardMarkup(btns))
    return FILTER_DEL_WORD

async def filter_del_proc(update, context):
    q = update.callback_query; await q.answer()
    flist = context.user_data.get("del_filters_list", [])
    try:
        idx = int(q.data.split("_")[-1])
        removed = flist[idx]
        DYNAMIC_FILTERS.discard(removed)
        save_dynamic_filters()
        await safe_edit(q, f"✅ Filter <code>{html.escape(removed)}</code> deleted!", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Filter Menu", callback_data="admin_filters")]]))
    except Exception:
        await safe_edit(q, "❌ Failed to remove.", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Filter Menu", callback_data="admin_filters")]]))
    return ConversationHandler.END

# ================== 📢 BROADCASTER ==================
async def bc_start(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "📢 <b>BROADCAST</b>\n\nSend Photo with Caption or Text Message to broadcast to all users. /cancel to abort:")
    return ADMIN_BROADCAST_MSG

async def bc_msg(u, c):
    msg = u.message
    if not msg: return ADMIN_BROADCAST_MSG
    bc_data = {}
    if msg.photo:
        bc_data = {"type": "photo", "file_id": msg.photo[-1].file_id, "caption": msg.caption or ""}
    elif msg.text:
        bc_data = {"type": "text", "text": msg.text}
    else:
        await safe_reply(u, "❌ Send photo or text only! /cancel:"); return ADMIN_BROADCAST_MSG
    c.user_data["bc"] = bc_data
    await safe_reply(u, f"⚠️ Broadcast ready for <code>{len(load_users())}</code> users.\n\nConfirm?", InlineKeyboardMarkup([[InlineKeyboardButton("✅ CONFIRM & SEND", callback_data="broadcast_confirm")],[InlineKeyboardButton("❌ CANCEL", callback_data="broadcast_cancel")]]))
    return ADMIN_BROADCAST_CONFIRM

async def bc_confirm(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "broadcast_cancel":
        await safe_edit(q, "❌ Cancelled.", admin_kb()); return ConversationHandler.END
    bc_data = c.user_data.get("bc")
    if not bc_data: return ConversationHandler.END
    users = list(load_users().keys())
    s_msg = await safe_edit(q, "🚀 Broadcasting started...")
    sent, failed = 0, 0
    for uid in users:
        try:
            if bc_data["type"] == "photo":
                await c.bot.send_photo(chat_id=int(uid), photo=bc_data["file_id"], caption=bc_data.get("caption",""), parse_mode="HTML")
            else:
                await c.bot.send_message(chat_id=int(uid), text=bc_data["text"], parse_mode="HTML")
            sent += 1
        except Exception: failed += 1
        await asyncio.sleep(0.04)
    await safe_edit(s_msg, f"✅ <b>Done!</b> Delivered: <code>{sent}</code> | Failed: <code>{failed}</code>", admin_kb())
    return ConversationHandler.END

# ================== ADMIN PLANS & PROTECT HANDLERS ==================
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
    exp = upgrade(int(uid),pk)
    await safe_edit(q, f"✅ <b>Plan Activated!</b>\nID: <code>{uid}</code>\nPlan: <b>{plan['name']}</b> ({exp})", admin_kb()); return ConversationHandler.END

async def adm_rem_s(u,c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "❌ Enter User ID to reset to free:"); return ADMIN_REM_ID

async def adm_rem_p(u,c):
    uid = u.message.text.strip(); delete_user(uid)
    await safe_reply(u, f"✅ <code>{uid}</code> reset!", admin_kb()); return ConversationHandler.END

async def adm_list(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    users = load_users(); t = len(users)
    txt = f"<code>{BANNER_MINI}</code>\n\n👥 <b>Total Users ({t}):</b>\n\n"
    for k, v in list(users.items())[:30]:
        txt += f"• <code>{k}</code> | {v.get('plan','trial')} | 🔍 {v.get('total_searches',0)}\n"
    await safe_edit(q, txt[:4000], admin_kb())

async def adm_stats(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    users = load_users(); ts = sum(v.get("total_searches",0) for v in users.values())
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n📊 <b>Stats:</b>\nUsers: <code>{len(users)}</code>\nSearches: <code>{ts}</code>", admin_kb())

# Protected Handlers
async def admin_protect_menu(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    txt = f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>PROTECTED MANAGER</b>\nDynamic: <code>{len(PROTECTED_ENTRIES)}</code>\nHC Numbers: <code>{', '.join(HARDCODED_PROTECTED_NUMBERS)}</code>"
    await safe_edit(q, txt, InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add", callback_data="protect_add")],[InlineKeyboardButton("❌ Remove", callback_data="protect_remove")],[InlineKeyboardButton("🔙 Admin", callback_data="admin_back")]]))

async def protect_add_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "🛡️ Enter Numbers/IDs to protect (comma-sep):"); return ADMIN_PROTECT_ADD

async def protect_add_process(update, context):
    entries = [x.strip() for x in update.message.text.split(",") if x.strip()]
    for e in entries: save_protected_entry(e)
    await safe_reply(update, f"✅ Added {len(entries)} protected entries!", admin_kb()); return ConversationHandler.END

async def protect_remove_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "❌ Enter Numbers/IDs to unprotect (comma-sep):"); return ADMIN_PROTECT_REMOVE

async def protect_remove_process(update, context):
    entries = [x.strip() for x in update.message.text.split(",") if x.strip()]
    for e in entries: remove_protected_entry(e)
    await safe_reply(update, f"✅ Removed {len(entries)} entries!", admin_kb()); return ConversationHandler.END

# Logs & Maintenance Callbacks
async def admin_logs_menu(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    await safe_edit(q, format_logs_text(get_recent_logs(20), "📋 RECENT LOGS"), InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin", callback_data="admin_back")]]))

async def admin_maintenance_menu(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    fs = "🔴 ON" if is_full_maintenance() else "🟢 OFF"
    btns = [[InlineKeyboardButton(f"🔧 Full Bot Maint: {fs}", callback_data="maint_toggle_full")]]
    fb = [InlineKeyboardButton(f"{'🔴' if is_feature_maintenance(f) else '🟢'} {f.title()}", callback_data=f"maint_toggle_{f}") for f in ALL_FEATURE_KEYS]
    for i in range(0, len(fb), 2): btns.append(fb[i:i+2])
    btns.append([InlineKeyboardButton("🔙 Admin", callback_data="admin_back")])
    await safe_edit(q, "🔧 <b>MAINTENANCE SETTINGS</b>", InlineKeyboardMarkup(btns))

async def maint_toggle_handler(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    d = q.data
    if d == "maint_toggle_full": toggle_full_maintenance()
    elif d.startswith("maint_toggle_"): toggle_feature_maintenance(d.replace("maint_toggle_",""))
    await admin_maintenance_menu(u, c)

# Fallback & Error Handlers
async def general_fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    chat_type = update.effective_chat.type if update.effective_chat else "private"
    if chat_type in ["group", "supergroup", "channel"]: return
    txt = update.message.text.strip().lower()
    if txt in ["hi", "hello", "hey", "start", "menu", "/menu"]: await start(update, context)

async def error_handler(update, context):
    if isinstance(context.error, RetryAfter): return
    logger.error(f"❌ Error: {context.error}")

def notify_admin_startup():
    time.sleep(3)
    for aid in ADMIN_IDS:
        try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": aid, "text": "🚀 <b>ZERO TRACE ONLINE!</b>\n🛡️ Protection & Multi-API Pools ACTIVE\n👉 /start", "parse_mode": "HTML"}, timeout=15)
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

    load_settings()
    load_protected_entries()
    load_api_pools()
    load_dynamic_filters()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    C = ConversationHandler; CQ = CallbackQueryHandler; MH = MessageHandler; CMD = CommandHandler
    F = filters.TEXT & ~filters.COMMAND; UF = [CMD("cancel",cancel), CMD("start",start)]

    app.add_handler(CMD("start", start))
    app.add_handler(CMD("cancel", cancel))
    app.add_handler(CMD("admin", admin_panel))
    app.add_handler(CMD("redeem", redeem_command))

    convs = [
        C(entry_points=[CQ(p_ss,pattern="^phone_single$")],states={PHONE_SINGLE:[MH(F,p_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(p_bs,pattern="^phone_batch$")],states={PHONE_BATCH:[MH(F,p_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(e_ss,pattern="^email_single$")],states={EMAIL_SINGLE:[MH(F,e_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(e_bs,pattern="^email_batch$")],states={EMAIL_BATCH:[MH(F,e_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(u_ss,pattern="^upi_single$")],states={UPI_SINGLE:[MH(F,u_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(u_bs,pattern="^upi_batch$")],states={UPI_BATCH:[MH(F,u_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(a_ss,pattern="^aadhaar_single$")],states={AADHAAR_SINGLE:[MH(F,a_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(a_bs,pattern="^aadhaar_batch$")],states={AADHAAR_BATCH:[MH(F,a_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(v_ss,pattern="^vehicle_single$")],states={VEHICLE_SINGLE:[MH(F,v_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(v_bs,pattern="^vehicle_batch$")],states={VEHICLE_BATCH:[MH(F,v_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(i_ss,pattern="^ifsc_single$")],states={IFSC_SINGLE:[MH(F,i_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(i_bs,pattern="^ifsc_batch$")],states={IFSC_BATCH:[MH(F,i_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(tg_ss,pattern="^tg_single$")],states={TG_SINGLE:[MH(F,tg_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(tg_bs,pattern="^tg_batch$")],states={TG_BATCH:[MH(F,tg_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(in_ss,pattern="^insta_single$")],states={INSTA_SINGLE:[MH(F,in_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(in_bs,pattern="^insta_batch$")],states={INSTA_BATCH:[MH(F,in_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(im_ss,pattern="^imei_single$")],states={IMEI_SINGLE:[MH(F,im_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(im_bs,pattern="^imei_batch$")],states={IMEI_BATCH:[MH(F,im_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(pin_ss,pattern="^pin_single$")],states={PIN_SINGLE:[MH(F,pin_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(pin_bs,pattern="^pin_batch$")],states={PIN_BATCH:[MH(F,pin_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(c_ss,pattern="^country_single$")],states={COUNTRY_SINGLE:[MH(F,c_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(c_bs,pattern="^country_batch$")],states={COUNTRY_BATCH:[MH(F,c_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(pm_ss,pattern="^paytm_single$")],states={PAYTM_SINGLE:[MH(F,pm_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(pm_bs,pattern="^paytm_batch$")],states={PAYTM_BATCH:[MH(F,pm_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(ip_ss,pattern="^ip_single$")],states={IP_SINGLE:[MH(F,ip_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(ip_bs,pattern="^ip_batch$")],states={IP_BATCH:[MH(F,ip_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(w_ss,pattern="^weather_single$")],states={WEATHER_SINGLE:[MH(F,w_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(w_bs,pattern="^weather_batch$")],states={WEATHER_BATCH:[MH(F,w_bp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(tgid_ss,pattern="^tgid_single$")],states={TGID_SINGLE:[MH(F,tgid_sp)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(tgid_bs,pattern="^tgid_batch$")],states={TGID_BATCH:[MH(F,tgid_bp)]},fallbacks=UF,allow_reentry=True),
        # Admin Conversations
        C(entry_points=[CQ(adm_add_s,pattern="^admin_add$")],states={ADMIN_ADD_ID:[MH(F,adm_add_id)],ADMIN_ADD_PLAN:[CQ(adm_add_plan,pattern="^plan_")]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(adm_rem_s,pattern="^admin_remove$")],states={ADMIN_REM_ID:[MH(F,adm_rem_p)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(bc_start,pattern="^admin_broadcast$")],states={ADMIN_BROADCAST_MSG:[MH(filters.PHOTO | filters.TEXT, bc_msg)],ADMIN_BROADCAST_CONFIRM:[CQ(bc_confirm,pattern="^broadcast_")]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(protect_add_start,pattern="^protect_add$")],states={ADMIN_PROTECT_ADD:[MH(F,protect_add_process)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(protect_remove_start,pattern="^protect_remove$")],states={ADMIN_PROTECT_REMOVE:[MH(F,protect_remove_process)]},fallbacks=UF,allow_reentry=True),
        # API Pool Add Conv
        C(entry_points=[CQ(apipool_add_start,pattern="^apipool_add_start$"), CQ(apipool_choose_feat,pattern=r"^apipool_quickadd_")],states={API_ADD_FEAT:[CQ(apipool_choose_feat,pattern=r"^apipool_choosefeat_")],API_ADD_NAME:[MH(F,apipool_add_name_proc)],API_ADD_URL:[MH(F,apipool_add_url_proc)],API_ADD_KEY:[MH(F,apipool_add_key_proc)],API_ADD_ACTION:[MH(F,apipool_add_action_proc)]},fallbacks=UF,allow_reentry=True),
        # Result Filter Add/Remove Conv
        C(entry_points=[CQ(filter_add_start,pattern="^filter_add_start$")],states={FILTER_ADD_WORD:[MH(F,filter_add_proc)]},fallbacks=UF,allow_reentry=True),
        C(entry_points=[CQ(filter_del_start,pattern="^filter_del_start$")],states={FILTER_DEL_WORD:[CQ(filter_del_proc,pattern=r"^filterdel_")]},fallbacks=UF,allow_reentry=True),
    ]
    for cv in convs: app.add_handler(cv)
    app.add_error_handler(error_handler)

    callbacks = [
        ("mode_phone",mode_phone),("mode_email",mode_email),("mode_upi",mode_upi),
        ("mode_aadhaar",mode_aadhaar),("mode_vehicle",mode_vehicle),("mode_ifsc",mode_ifsc),
        ("mode_tg",mode_tg),("mode_insta",mode_insta),("mode_imei",mode_imei),
        ("mode_pin",mode_pin),("mode_country",mode_country),("mode_paytm",mode_paytm),
        ("mode_ip",mode_ip),("mode_weather",mode_weather),("mode_tgid",mode_tgid),
        ("profile",profile),("status",status_check),("help",help_menu),("buy",buy),
        ("admin_stats",adm_stats),("admin_list",adm_list),("admin_back",admin_back),
        ("admin_protect",admin_protect_menu),("admin_logs",admin_logs_menu),
        ("admin_maintenance",admin_maintenance_menu),("main_menu",main_menu_cb),
        ("verify_join",verify_join),("dismiss_popup",dismiss_popup_handler),
        ("admin_apipools",admin_apipools_menu),("admin_filters",admin_filters_menu),
    ]
    for pat, fn in callbacks:
        app.add_handler(CQ(fn, pattern=f"^{pat}$"))

    app.add_handler(CQ(admin_feature_pool_view, pattern=r"^apipool_feat_.*$"))
    app.add_handler(CQ(admin_apipool_toggle, pattern=r"^apipool_toggle_.*$"))
    app.add_handler(CQ(maint_toggle_handler, pattern=r"^maint_toggle_.*$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, general_fallback_handler), group=99)

    print("☠️ ZERO TRACE + MULTI-API POOLS + RESULT FILTER ACTIVE ☠️", flush=True)
    app.run_polling(drop_pending_updates=False)

if __name__ == "__main__":
    main()

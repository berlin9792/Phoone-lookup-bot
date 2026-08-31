#!/usr/bin/env python3
"""
🔍 Ultimate Intelligence Bot
Phone + Email + UPI + Aadhaar + Vehicle + IFSC + Vehicle Info
ONE PLAN = ALL ACCESS
+ Dual Channel Force Join Check
+ Clean Results Only (ALL Metadata Blocked)
+ Fast In-Memory Cache + MongoDB Cloud + 24/7 Keep Alive
+ Highly Colorful & Premium Emoji Theme Buttons
"""

import json, os, threading, requests, logging, asyncio
from datetime import date, timedelta
from pathlib import Path
from flask import Flask
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)
from telegram.request import HTTPXRequest

# ================== LOGGING ==================
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== CONFIG ==================
BOT_TOKEN     = "8642873626:AAFy5F79opcK_NMJ7NgGItd6sRrfbOc4TJU"
ADMIN_IDS     = [5057489358, 1968142314]
DEFAULT_PIN   = "240841"
API_URL       = "https://lk-api-pinsstm.ramaxinfo.workers.dev/"
UPI_API_URL   = "https://nitin-developer-api-paid.nitinshab43.workers.dev/api"
AADHAAR_API_URL = "https://nitin-developer-api-paid.nitinshab43.workers.dev/api"
VEHICLE_API_URL = "https://ansh-apis.is-dev.org/api/vehicle"
IFSC_API_URL    = "https://all-api-by-nitin-developer-best1.binderdhaniya6.workers.dev/api"
VINFO_API_URL   = "https://rtf-api-server.onrender.com/api"
NITIN_API_KEY   = "JAANI"
VEHICLE_API_KEY = "ansh"
IFSC_API_KEY    = "NITIN"
VINFO_API_KEY   = "demo2"
OWNER_CONTACT   = "@theplayerror"

# --- DUAL CHANNEL FORCE JOIN CONFIG ---
FORCE_JOIN_CHANNEL_1    = "@hackkwr"
FORCE_JOIN_CHANNEL_1_ID = "@hackkwr"
FORCE_JOIN_CHANNEL_2    = "@zerotracelegit"
FORCE_JOIN_CHANNEL_2_ID = "@zerotracelegit"

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://httplegitfs_db_user:Q8uGZxERXsrf2VV1@cluster0.iojnad7.mongodb.net/?retryWrites=true&w=majority"
)

# ================== FREE SEARCHES ==================
PHONE_FREE   = 2
EMAIL_FREE   = 2
UPI_FREE     = 2
AADHAAR_FREE = 2
VEHICLE_FREE = 2
IFSC_FREE    = 2
VINFO_FREE   = 2

# ================== PLANS ==================
PLANS = {
    "trial":    {"name":"Trial",     "days":0,   "price":0,   "daily_limit":0,      "unlimited":False, "is_free":True},
    "7days":    {"name":"7 Days",    "days":7,   "price":50,  "daily_limit":5,      "unlimited":False, "is_free":False},
    "30days":   {"name":"30 Days",   "days":30,  "price":130, "daily_limit":10,     "unlimited":False, "is_free":False},
    "6months":  {"name":"6 Months",  "days":180, "price":300, "daily_limit":15,     "unlimited":False, "is_free":False},
    "12months": {"name":"12 Months", "days":365, "price":799, "daily_limit":999999, "unlimited":True,  "is_free":False},
}

# ================== STATES ==================
PHONE_COUNTRY_SINGLE=10; PHONE_COUNTRY_BATCH=11; PHONE_SINGLE_INDIA=12
PHONE_SINGLE_OTHER=13; PHONE_BATCH_INDIA=14; PHONE_BATCH_OTHER=15
EMAIL_SINGLE=20; EMAIL_BATCH=21
ADMIN_ADD_ID=30; ADMIN_ADD_PLAN=31; ADMIN_REM_ID=32
ADMIN_EXP_ID=33; ADMIN_EXP_PLAN=34
ADMIN_BROADCAST_MSG=35; ADMIN_BROADCAST_CONFIRM=36
ADMIN_CUSTOM_DAYS=37; ADMIN_CUSTOM_LIMIT=38
UPI_SINGLE=40; UPI_BATCH=41
AADHAAR_SINGLE=50; AADHAAR_BATCH=51
VEHICLE_SINGLE=60; VEHICLE_BATCH=61
IFSC_SINGLE=70; IFSC_BATCH=71
VINFO_SINGLE=80; VINFO_BATCH=81

# ================== SAFE SENDERS & UTILS ==================
async def safe_reply(update: Update, text: str, reply_markup=None):
    try:
        if update.message:
            return await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        elif update.callback_query and update.callback_query.message:
            return await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:
        clean = text.replace("*", "").replace("`", "").replace("_", "").replace("[", "").replace("]", "")
        try:
            if update.message:
                return await update.message.reply_text(clean, reply_markup=reply_markup)
            elif update.callback_query and update.callback_query.message:
                return await update.callback_query.message.reply_text(clean, reply_markup=reply_markup)
        except Exception:
            pass

async def safe_edit(target, text: str, reply_markup=None):
    try:
        if hasattr(target, "edit_text"):
            return await target.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        elif hasattr(target, "edit_message_text"):
            return await target.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:
        clean = text.replace("*", "").replace("`", "").replace("_", "").replace("[", "").replace("]", "")
        try:
            if hasattr(target, "edit_text"):
                return await target.edit_text(clean, reply_markup=reply_markup)
            elif hasattr(target, "edit_message_text"):
                return await target.edit_message_text(clean, reply_markup=reply_markup)
        except Exception:
            pass

def is_admin(uid): return int(uid) in ADMIN_IDS

def safe_name(user):
    name = user.first_name or "User"
    for ch in ["*", "_", "`", "[", "]", "(", ")"]:
        name = name.replace(ch, "")
    return name

def valid_email(e): return "@" in e and "." in e.split("@")[-1] and " " not in e
def valid_upi(u): return "@" in u and len(u) >= 5 and " " not in u
def valid_aadhaar(a): return a.isdigit() and len(a) == 12
def valid_ifsc(c): return len(c) == 11 and c[:4].isalpha() and c[4] == "0"
def valid_vehicle_number(v): return len(v) >= 4 and any(c.isalpha() for c in v) and any(c.isdigit() for c in v)

# ================== FLASK KEEP-ALIVE ==================
web_app = Flask(__name__)
@web_app.route('/')
def keep_alive_status(): return "Bot Running 24/7!", 200
def start_webserver():
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================== FORCE JOIN ==================
async def check_joined(context, uid):
    if is_admin(uid): return True
    try:
        # Check Channel 1
        m1 = await asyncio.wait_for(context.bot.get_chat_member(FORCE_JOIN_CHANNEL_1_ID, uid), timeout=3.0)
        joined_1 = m1.status in ["member", "administrator", "creator", "restricted"]
        if not joined_1:
            return False
            
        # Check Channel 2
        m2 = await asyncio.wait_for(context.bot.get_chat_member(FORCE_JOIN_CHANNEL_2_ID, uid), timeout=3.0)
        joined_2 = m2.status in ["member", "administrator", "creator", "restricted"]
        return joined_2
    except Exception as e:
        logger.warning(f"Force join check warning: {e}")
        return False

def force_join_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel 1 ↗️", url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}")],
        [InlineKeyboardButton("📢 Join Channel 2 ↗️", url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton("✅ Verify Both Channels ✅", callback_data="verify_join")],
    ])

# ================== IN-MEMORY CACHE + MONGODB ==================
USERS_CACHE = {}
LOCAL_FILE = Path("users.json")

try:
    mc = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = mc["tele_intel_bot"]
    users_col = db["users"]
    mc.admin.command('ping')
    print("✅ MongoDB Connected!")
except Exception as e:
    print("⚠️ MongoDB Warning:", e)
    users_col = None

DEFAULTS = {
    "plan":"trial","expiry":"","is_premium":False,
    "phone_free_used":0,"phone_daily":0,"phone_date":"","phone_total":0,
    "email_free_used":0,"email_total":0,
    "upi_free_used":0,"upi_daily":0,"upi_date":"","upi_total":0,
    "aadhaar_free_used":0,"aadhaar_daily":0,"aadhaar_date":"","aadhaar_total":0,
    "vehicle_free_used":0,"vehicle_daily":0,"vehicle_date":"","vehicle_total":0,
    "ifsc_free_used":0,"ifsc_daily":0,"ifsc_date":"","ifsc_total":0,
    "vinfo_free_used":0,"vinfo_daily":0,"vinfo_date":"","vinfo_total":0,
    "total_searches":0,
}

def init_cache():
    global USERS_CACHE
    if users_col is not None:
        try:
            for doc in users_col.find():
                uid = doc["_id"]
                USERS_CACHE[uid] = {k: v for k, v in doc.items() if k != "_id"}
            return
        except Exception:
            pass
    if LOCAL_FILE.exists():
        try:
            USERS_CACHE = json.loads(LOCAL_FILE.read_text())
        except Exception:
            USERS_CACHE = {}

init_cache()

def sync_user_background(uid: str, data: dict):
    def _save():
        if users_col is not None:
            try:
                users_col.update_one({"_id": str(uid)}, {"$set": data}, upsert=True)
                return
            except Exception:
                pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE, indent=2))
        except Exception: pass
    threading.Thread(target=_save, daemon=True).start()

def get_user(uid):
    uid = str(uid)
    if uid not in USERS_CACHE:
        user_data = {**DEFAULTS, "added": date.today().isoformat()}
        USERS_CACHE[uid] = user_data
        sync_user_background(uid, user_data)
    else:
        user_data = USERS_CACHE[uid]
        updated = False
        for k, v in DEFAULTS.items():
            if k not in user_data:
                user_data[k] = v
                updated = True
        if updated:
            sync_user_background(uid, user_data)
    return USERS_CACHE[uid]

def save_user(uid, data):
    uid = str(uid)
    USERS_CACHE[uid] = data
    sync_user_background(uid, data)

def delete_user(uid):
    uid = str(uid)
    if uid in USERS_CACHE:
        del USERS_CACHE[uid]
    def _del():
        if users_col is not None:
            try: users_col.delete_one({"_id": uid})
            except Exception: pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE, indent=2))
        except Exception: pass
    threading.Thread(target=_del, daemon=True).start()

def load_users():
    return USERS_CACHE

# ================== PLAN RESOLVER & UPGRADES ==================
def get_plan(ud):
    pk = ud.get("plan", "trial")
    if pk.startswith("custom_"):
        try: d = int(pk.split("_")[1].replace("d", ""))
        except: d = 30
        return {"name": f"Custom ({d}D)", "days": d, "daily_limit": ud.get("custom_limit", 0), "unlimited": ud.get("custom_unlimited", False), "is_free": False}
    return PLANS.get(pk, PLANS["trial"])

def upgrade(uid, pk):
    uid = str(uid); ud = get_user(uid); plan = PLANS.get(pk, PLANS["7days"])
    exp = (date.today() + timedelta(days=plan["days"])).isoformat()
    ud.update({"plan": pk, "expiry": exp, "is_premium": True,
               "phone_daily": 0, "phone_date": "",
               "upi_daily": 0, "upi_date": "",
               "aadhaar_daily": 0, "aadhaar_date": "",
               "vehicle_daily": 0, "vehicle_date": "",
               "ifsc_daily": 0, "ifsc_date": "",
               "vinfo_daily": 0, "vinfo_date": ""})
    save_user(uid, ud); return exp

def upgrade_custom(uid, days, lim, unl):
    uid = str(uid); ud = get_user(uid)
    exp = (date.today() + timedelta(days=days)).isoformat()
    ud.update({"plan": f"custom_{days}d", "expiry": exp, "is_premium": True,
               "phone_daily": 0, "phone_date": "",
               "upi_daily": 0, "upi_date": "",
               "aadhaar_daily": 0, "aadhaar_date": "",
               "vehicle_daily": 0, "vehicle_date": "",
               "ifsc_daily": 0, "ifsc_date": "",
               "vinfo_daily": 0, "vinfo_date": "",
               "custom_limit": lim, "custom_unlimited": unl})
    save_user(uid, ud); return exp

# ================== LIMITS & TRACKING ==================
def free_rem(uid, key, mx):
    if is_admin(uid): return 999999
    return max(0, mx - get_user(uid).get(key, 0))

def daily_rem(uid, dk, dtk):
    if is_admin(uid): return 999999
    ud = get_user(uid); plan = get_plan(ud)
    if plan.get("unlimited"): return 999999
    lim = plan.get("daily_limit", 0)
    if ud.get(dtk, "") != date.today().isoformat(): return lim
    return max(0, lim - ud.get(dk, 0))

def use_search(uid, fk, dk, dtk, tk):
    uid = str(uid); ud = get_user(uid); today = date.today().isoformat()
    if ud.get(dtk, "") != today: ud[dk] = 0; ud[dtk] = today
    plan = get_plan(ud)
    if not is_admin(int(uid)):
        if plan.get("is_free", True): ud[fk] = ud.get(fk, 0) + 1
        else: ud[dk] = ud.get(dk, 0) + 1
    ud[tk] = ud.get(tk, 0) + 1; ud["total_searches"] = ud.get("total_searches", 0) + 1
    save_user(uid, ud)

def check_access(uid, fk, mx, dk, dtk, name):
    if is_admin(uid): return True, "Admin ∞", 9999, True, "12months"
    ud = get_user(uid); plan = get_plan(ud); pk = ud.get("plan", "trial")
    exp_s = ud.get("expiry", ""); is_p = ud.get("is_premium", False)
    if is_p and exp_s:
        try:
            exp = date.fromisoformat(exp_s)
            if date.today() > exp:
                fl = free_rem(uid, fk, mx)
                if fl > 0: return True, f"Expired | {fl} free left", 0, False, "trial"
                return False, "Plan Expired! Renew karo.", 0, False, "trial"
            days_left = (exp - date.today()).days
            dr = daily_rem(uid, dk, dtk)
            lim = plan.get("daily_limit", 0)
            unl = plan.get("unlimited", False)
            if unl: return True, f"{plan['name']} | Unlimited | {days_left}d left", days_left, True, pk
            if dr <= 0: return False, f"Daily {name} limit khatam! ({lim}/day)", days_left, True, pk
            return True, f"{plan['name']}|{dr}/{lim} today|{days_left}d left", days_left, True, pk
        except Exception:
            pass
    fl = free_rem(uid, fk, mx)
    if fl > 0: return True, f"Trial ({fl}/{mx} left)", 0, False, "trial"
    return False, "Trial khatam! Plan lo.", 0, False, "trial"

def phone_free(u): return free_rem(u, "phone_free_used", PHONE_FREE)
def phone_daily(u): return daily_rem(u, "phone_daily", "phone_date")
def phone_use(u): use_search(u, "phone_free_used", "phone_daily", "phone_date", "phone_total")
def phone_check(u): return check_access(u, "phone_free_used", PHONE_FREE, "phone_daily", "phone_date", "Phone")

def email_free(u): return free_rem(u, "email_free_used", EMAIL_FREE)
def email_use(uid, is_p):
    uid = str(uid); ud = get_user(uid)
    if not is_admin(int(uid)) and not is_p: ud["email_free_used"] = ud.get("email_free_used", 0) + 1
    ud["email_total"] = ud.get("email_total", 0) + 1; ud["total_searches"] = ud.get("total_searches", 0) + 1
    save_user(uid, ud)

def email_check(uid):
    if is_admin(uid): return True, "Admin ∞", 9999, True
    ud = get_user(uid); is_p = ud.get("is_premium", False); exp_s = ud.get("expiry", "")
    if is_p and exp_s:
        try:
            exp = date.fromisoformat(exp_s)
            if date.today() > exp:
                fl = email_free(uid)
                if fl > 0: return True, f"Expired | {fl} free left", 0, False
                return False, "Expired!", 0, False
            return True, f"Premium ({(exp - date.today()).days}d left)", (exp - date.today()).days, True
        except: pass
    fl = email_free(uid)
    if fl > 0: return True, f"Free ({fl}/{EMAIL_FREE} left)", 0, False
    return False, "Free trial khatam! Plan lo.", 0, False

def upi_free(u): return free_rem(u, "upi_free_used", UPI_FREE)
def upi_daily(u): return daily_rem(u, "upi_daily", "upi_date")
def upi_use(u): use_search(u, "upi_free_used", "upi_daily", "upi_date", "upi_total")
def upi_check(u): return check_access(u, "upi_free_used", UPI_FREE, "upi_daily", "upi_date", "UPI")

def aadhaar_free(u): return free_rem(u, "aadhaar_free_used", AADHAAR_FREE)
def aadhaar_daily(u): return daily_rem(u, "aadhaar_daily", "aadhaar_date")
def aadhaar_use(u): use_search(u, "aadhaar_free_used", "aadhaar_daily", "aadhaar_date", "aadhaar_total")
def aadhaar_check(u): return check_access(u, "aadhaar_free_used", AADHAAR_FREE, "aadhaar_daily", "aadhaar_date", "Aadhaar")

def vehicle_free(u): return free_rem(u, "vehicle_free_used", VEHICLE_FREE)
def vehicle_daily(u): return daily_rem(u, "vehicle_daily", "vehicle_date")
def vehicle_use(u): use_search(u, "vehicle_free_used", "vehicle_daily", "vehicle_date", "vehicle_total")
def vehicle_check(u): return check_access(u, "vehicle_free_used", VEHICLE_FREE, "vehicle_daily", "vehicle_date", "Vehicle")

def ifsc_free(u): return free_rem(u, "ifsc_free_used", IFSC_FREE)
def ifsc_daily(u): return daily_rem(u, "ifsc_daily", "ifsc_date")
def ifsc_use(u): use_search(u, "ifsc_free_used", "ifsc_daily", "ifsc_date", "ifsc_total")
def ifsc_check(u): return check_access(u, "ifsc_free_used", IFSC_FREE, "ifsc_daily", "ifsc_date", "IFSC")

def vinfo_free(u): return free_rem(u, "vinfo_free_used", VINFO_FREE)
def vinfo_daily(u): return daily_rem(u, "vinfo_daily", "vinfo_date")
def vinfo_use(u): use_search(u, "vinfo_free_used", "vinfo_daily", "vinfo_date", "vinfo_total")
def vinfo_check(u): return check_access(u, "vinfo_free_used", VINFO_FREE, "vinfo_daily", "vinfo_date", "VehicleInfo")

# ================== SAFE API CALLS ==================
def _safe_api(fn):
    try: return fn()
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "⏱️ Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "🌐 Service connection error. Please try later."}
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else "Error"
        return {"ok": False, "error": f"⚠️ Service error response: {code}"}
    except Exception:
        return {"ok": False, "error": "❌ Service temporarily unavailable."}

def search_api(term):
    def call():
        r = requests.get(API_URL, params={"pin": DEFAULT_PIN, "term": term}, timeout=15)
        r.raise_for_status(); return {"ok": True, "data": r.json()}
    return _safe_api(call)

def upi_api(upi_id):
    def call():
        r = requests.get(UPI_API_URL, params={"action": "upiinfo", "upi": upi_id, "key": NITIN_API_KEY}, timeout=15)
        r.raise_for_status(); return {"ok": True, "data": r.json()}
    return _safe_api(call)

def aadhaar_api(num):
    def call():
        r = requests.get(AADHAAR_API_URL, params={"action": "aadhar", "aadhar": num, "key": NITIN_API_KEY}, timeout=15)
        r.raise_for_status(); return {"ok": True, "data": r.json()}
    return _safe_api(call)

def vehicle_api(rc):
    def call():
        r = requests.get(VEHICLE_API_URL, params={"key": VEHICLE_API_KEY, "rc": rc}, timeout=15)
        r.raise_for_status(); return {"ok": True, "data": r.json()}
    return _safe_api(call)

def ifsc_api(code):
    def call():
        r = requests.get(IFSC_API_URL, params={"type": "ifsc", "search": code, "api_key": IFSC_API_KEY}, timeout=15)
        r.raise_for_status(); return {"ok": True, "data": r.json()}
    return _safe_api(call)

def vinfo_api(vehicle_num):
    def call():
        r = requests.get(VINFO_API_URL, params={"types": "vinfo", "key": VINFO_API_KEY, "spell": vehicle_num}, timeout=15)
        r.raise_for_status(); return {"ok": True, "data": r.json()}
    return _safe_api(call)

# ================== STRICT METADATA FILTERING ==================
SKIP_K = {
    "metadata", "meta", "key_owner", "key_usage", "key_expiry", "key_enabled",
    "daily_limit", "daily_used", "api_key", "key", "action", "parameters", "service",
    "success", "violations", "timestamp", "response_time", "response_time_ms",
    "developer", "owner", "credit", "credits", "powered_by", "source", "api", "version",
    "status", "message", "code", "time", "created_at", "updated_at", "server", "watermark",
    "signature", "by", "made_by", "contact_admin", "channel", "group", "join", "advertisement",
    "ads", "promo", "query", "req_id", "request_id", "execution_time", "fizzagirl", "nitin",
    "shree", "jaani", "types", "spell", "type"
}

def should_skip_key(k: str) -> bool:
    if not k: return True
    kl = str(k).lower().strip().replace(" ", "_")
    if kl in SKIP_K: return True
    bad_words = [
        "metadata", "timestamp", "response_time", "developer",
        "credit", "powered", "watermark", "pheevar", "advertisement",
        "promo", "channel", "server", "api_", "made_by", "encrypted",
        "password", "salt", "key_", "daily_", "auth", "token", "fizza"
    ]
    for w in bad_words:
        if w in kl: return True
    return False

def should_skip_val(v) -> bool:
    if v is None or v == "": return True
    vs = str(v).lower().strip()
    if vs in ("", "none", "null", "n/a", "na", "-", "0", "0.00", "0000-00-00", "{}", "[]"): return True
    for s in ["@pheevar", "pheevar", "@lk_", "t.me/", "telegram.me/"]:
        if s in vs: return True
    return False

def em(k):
    k = str(k).lower()
    for kw, e in {
        "name":"👤","holder":"👤","email":"📧","phone":"📞","mobile":"📞",
        "address":"📍","city":"🏙️","state":"🗺️","country":"🌍","pincode":"📮",
        "upi":"💳","vpa":"💳","bank":"🏦","ifsc":"🏦","account":"🏦","dob":"🎂",
        "gender":"🚻","pan":"🪪","aadhar":"🪪","aadhaar":"🪪","father":"👨","mother":"👩",
        "vehicle":"🚗","rc":"🚗","owner":"👤","model":"🚗","maker":"🚗","fuel":"⛽",
        "engine":"🔧","chassis":"🔧","registration":"📅","insurance":"📋","fitness":"📋",
        "rto":"🏢","branch":"🏦","district":"🗺️","micr":"🔢","swift":"🔢",
        "verified":"✅","valid":"✅","merchant":"🏪",
        "class":"📋","color":"🎨","colour":"🎨","seating":"💺","standing":"🧍",
        "wheel":"🛞","cylinder":"🔩","cubic":"📐","weight":"⚖️","unladen":"⚖️",
        "norms":"🌿","emission":"🌿","financer":"💰","permit":"📄","tax":"💵",
        "number":"🔢","plate":"🔢","type":"📋","category":"📋","body":"🚗",
        "manufacturer":"🏭","manufacturing":"📅","purchase":"🛒","hypothecation":"🔗",
        "blacklist":"⚠️","noc":"📄","challan":"🎫","status":"📊",
    }.items():
        if kw in k: return e
    return "📌"

# ================== METADATA CLEANER PIPELINE ==================
def clean_metadata(data):
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if should_skip_key(k):
                continue
            cleaned_val = clean_metadata(v)
            if not should_skip_val(cleaned_val):
                cleaned[k] = cleaned_val
        return cleaned
    elif isinstance(data, list):
        cleaned = []
        for item in data:
            cleaned_item = clean_metadata(item)
            if not should_skip_val(cleaned_item):
                cleaned.append(cleaned_item)
        return cleaned
    return data

def format_universal_result(term: str, raw_data, icon: str = "🔍"):
    cleaned = clean_metadata(raw_data)
    if not cleaned:
        return f"{icon} *Result for* `{term}`\n_No data found_"

    records = []

    def extract_records(item):
        if isinstance(item, dict):
            has_flat_fields = any(not isinstance(val, (dict, list)) for val in item.values())
            if has_flat_fields:
                records.append(item)
            for val in item.values():
                if isinstance(val, (dict, list)):
                    extract_records(val)
        elif isinstance(item, list):
            for sub_item in item:
                extract_records(sub_item)

    extract_records(cleaned)

    unique_records = []
    seen_fingerprints = set()
    for rec in records:
        fp = "-".join(sorted(f"{k}:{v}" for k, v in rec.items() if not isinstance(v, (dict, list))))
        if fp and fp not in seen_fingerprints:
            seen_fingerprints.add(fp)
            unique_records.append(rec)

    if not unique_records:
        return f"{icon} *Result for* `{term}`\n_No data found_"

    div = "━" * 28
    out = [f"{icon} *Result for* `{term}`", f"📊 *{len(unique_records)} record(s) found*", div]

    for idx, rec in enumerate(unique_records, 1):
        if len(unique_records) > 1:
            out.append(f"\n*━━ Record #{idx} ━━*")

        for k, v in rec.items():
            if isinstance(v, (dict, list)) or should_skip_key(k) or should_skip_val(v):
                continue
            emoji = em(k)
            label = str(k).replace("_", " ").replace("-", " ").title()

            if isinstance(v, bool):
                val_str = "Verified & Active ✅" if v else "Invalid / Inactive ❌"
            elif str(v).lower() == "true":
                val_str = "Verified & Active ✅"
            elif str(v).lower() == "false":
                val_str = "Invalid / Inactive ❌"
            else:
                val_str = str(v).strip().title()

            out.append(f"{emoji} *{label}*: `{val_str}`")

    return "\n".join(out)

# ================== KEYBOARDS ==================
def main_kb(uid):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Phone Tracker", callback_data="mode_phone"),
            InlineKeyboardButton("📧 Email OSINT", callback_data="mode_email")
        ],
        [
            InlineKeyboardButton("💳 UPI Verifier", callback_data="mode_upi"),
            InlineKeyboardButton("🪪 Aadhaar Check", callback_data="mode_aadhaar")
        ],
        [
            InlineKeyboardButton("🚗 Vehicle RC", callback_data="mode_vehicle"),
            InlineKeyboardButton("🏦 IFSC Finder", callback_data="mode_ifsc")
        ],
        [
            InlineKeyboardButton("🚘 Vehicle Detailed Info", callback_data="mode_vinfo")
        ],
        [
            InlineKeyboardButton("👤 My Profile", callback_data="profile"),
            InlineKeyboardButton("📊 API Status", callback_data="status")
        ],
        [
            InlineKeyboardButton("📢 Channel 1", url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}"),
            InlineKeyboardButton("📢 Channel 2", url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")
        ],
        [
            InlineKeyboardButton("💎 Purchase Premium Plan 💎", callback_data="buy")
        ],
        [
            InlineKeyboardButton("❓ Help & Documentation ❓", callback_data="help")
        ],
    ])

def search_kb(uid, check_fn, free_fn, daily_fn, prefix, mx):
    if is_admin(uid): 
        sl, bl = "🔍 Single Search (Admin)", "📦 Batch Processing (Admin)"
    else:
        ok, _, _, ip, _ = check_fn(uid); fl = free_fn(uid); dr = daily_fn(uid)
        ud = get_user(uid); p = get_plan(ud)
        if ip:
            if p.get("unlimited"): 
                sl, bl = "🟢 Single Search (Unlimited)", "📦 Batch Processing (Unlimited)"
            else: 
                sl, bl = f"🟢 Single Search ({dr} Today)", f"📦 Batch Processing ({dr} Today)"
        elif fl > 0: 
            sl, bl = f"🆓 Single Search ({fl} Free Trial)", f"📦 Batch Processing ({fl} Free Trial)"
        else: 
            sl, bl = "🔒 Single Search (Locked)", "🔒 Batch Processing (Locked)"
            
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(sl, callback_data=f"{prefix}_single")],
        [InlineKeyboardButton(bl, callback_data=f"{prefix}_batch")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")],
    ])

def email_kb(uid):
    if is_admin(uid): 
        sl, bl = "🔍 Single Email (Admin)", "📦 Batch Emails (Admin)"
    else:
        ok, _, _, ip = email_check(uid); fl = email_free(uid)
        if ip: 
            sl, bl = "🟢 Single Email (Unlimited)", "📦 Batch Emails (Unlimited)"
        elif fl > 0: 
            sl, bl = f"🆓 Single Email ({fl} Trial)", f"📦 Batch Emails ({fl} Trial)"
        else: 
            sl, bl = "🔒 Single Email (Locked)", "🔒 Batch Emails (Locked)"
            
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(sl, callback_data="email_single")],
        [InlineKeyboardButton(bl, callback_data="email_batch")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")],
    ])

def country_kb(m):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇳 Indian Standard (+91)", callback_data=f"country_india_{m}")],
        [InlineKeyboardButton("🌍 International / Other", callback_data=f"country_other_{m}")],
        [InlineKeyboardButton("❌ Abort Operation", callback_data="main_menu")],
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Register User", callback_data="admin_add"), 
            InlineKeyboardButton("❌ Remove User", callback_data="admin_remove")
        ],
        [
            InlineKeyboardButton("📅 Modify/Set Plan", callback_data="admin_setplan"), 
            InlineKeyboardButton("📋 Registered Users", callback_data="admin_list")
        ],
        [
            InlineKeyboardButton("📊 System Stats", callback_data="admin_stats"), 
            InlineKeyboardButton("🆓 Trial Monitor", callback_data="admin_free_monitor")
        ],
        [
            InlineKeyboardButton("📢 Global Broadcast", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton("🔙 Return to User Interface", callback_data="main_menu")
        ],
    ])

def back_kb(): 
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ])

def buy_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Instant Support/Billing", url=f"https://t.me/{OWNER_CONTACT.replace('@','')}")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")],
    ])

def plan_kb(pf):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🥉 Plan Bronze: 7 Days - ₹50", callback_data=f"{pf}_7days"), 
        ],
        [
            InlineKeyboardButton("🥈 Plan Silver: 30 Days - ₹130", callback_data=f"{pf}_30days"),
        ],
        [
            InlineKeyboardButton("🥇 Plan Gold: 6 Months - ₹300", callback_data=f"{pf}_6months"), 
        ],
        [
            InlineKeyboardButton("💎 Plan Diamond: 12 Months - ₹799", callback_data=f"{pf}_12months")
        ],
        [
            InlineKeyboardButton("⚙️ Configure Custom Days Plan", callback_data=f"{pf}_custom")
        ],
        [
            InlineKeyboardButton("❌ Return to Admin Suite", callback_data="admin_back")
        ],
    ])

def monitor_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔴 Limit Exhausted Users", callback_data="monitor_exhausted"), 
            InlineKeyboardButton("🟢 Active Free Users", callback_data="monitor_active")
        ],
        [
            InlineKeyboardButton("📊 Performance Summary", callback_data="monitor_summary")
        ],
        [
            InlineKeyboardButton("🔙 Return to Admin Suite", callback_data="admin_back")
        ],
    ])

# ================== START & VERIFICATION ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user(user.id)
    u_name = safe_name(user)

    if not is_admin(user.id):
        joined = await check_joined(context, user.id)
        if not joined:
            d1 = "━" * 30
            text = (
                f"{d1}\n🔴  *Force Join Required*  🔴\n{d1}\n\n"
                f"Welcome *{u_name}*!\n\n"
                "⚠️ *System access unlock karne ke liye niche dono official channels ko join karna zaroori hai:*\n\n"
                f"🔵 Channel 1: {FORCE_JOIN_CHANNEL_1}\n"
                f"🟣 Channel 2: {FORCE_JOIN_CHANNEL_2}\n\n"
                "👇 Join karke verify button par click karein:"
            )
            if update.callback_query:
                await safe_edit(update.callback_query, text, force_join_kb())
            else:
                await safe_reply(update, text, force_join_kb())
            return ConversationHandler.END

    d1, d2 = "━" * 30, "━" * 25
    if is_admin(user.id):
        text = (
            f"{d1}\n⚡  *Ultimate Intelligence System*  ⚡\n{d1}\n\n"
            f"👋 Welcome *{u_name}*! 🛡️ `System Administrator`\n\n"
            f"{d2}\n"
            "📱 Phone Searches : 💎 Unlimited\n"
            "📧 Email OSINT    : 💎 Unlimited\n"
            "💳 UPI Verifier   : 💎 Unlimited\n"
            "🪪 Aadhaar Engine : 💎 Unlimited\n"
            "🚗 Vehicle Engine : 💎 Unlimited\n"
            "🏦 IFSC Lookup    : 💎 Unlimited\n"
            "🚘 Vehicle Info   : 💎 Unlimited\n"
            f"{d2}\n\n"
            "Niche diye gaye operations me se select karein 👇"
        )
    else:
        ud = get_user(user.id); plan = get_plan(ud)
        ip, exp = ud.get("is_premium", False), ud.get("expiry", "")
        lines = []
        features = [
            ("📱 Phone Tracker", phone_free, phone_daily, PHONE_FREE),
            ("📧 Email OSINT", email_free, lambda u: 999999, EMAIL_FREE),
            ("💳 UPI Verifier", upi_free, upi_daily, UPI_FREE),
            ("🪪 Aadhaar Check", aadhaar_free, aadhaar_daily, AADHAAR_FREE),
            ("🚗 Vehicle RC", vehicle_free, vehicle_daily, VEHICLE_FREE),
            ("🏦 IFSC Lookup", ifsc_free, ifsc_daily, IFSC_FREE),
            ("🚘 Vehicle Info", vinfo_free, vinfo_daily, VINFO_FREE),
        ]
        for nm, ff, df, mx in features:
            fl = ff(user.id)
            if ip and exp:
                try:
                    ed = date.fromisoformat(exp); dl = (ed - date.today()).days
                    if dl >= 0:
                        if nm == "📧 Email OSINT": 
                            lines.append(f"🟢 {nm}: `💎 Unlimited` (Active)")
                        elif plan.get("unlimited"): 
                            lines.append(f"🟢 {nm}: `💎 Unlimited` (Active)")
                        else: 
                            dr = df(user.id)
                            lines.append(f"🟢 {nm}: `💎 {dr}/{plan.get('daily_limit',0)} Left` ({dl}d)")
                    else: 
                        lines.append(f"🔴 {nm}: `Expired` ({fl}/{mx} Free Left)")
                except: 
                    lines.append(f"⚪ {nm}: `Status Unknown`")
            else: 
                lines.append(f"🆓 {nm}: `{fl}/{mx} Free Trials Left`")
                
        text = (
            f"{d1}\n⚡  *Ultimate Intelligence System*  ⚡\n{d1}\n\n"
            f"👋 Welcome back, *{u_name}*!\n\n"
            f"{d2}\n" + "\n".join(lines) + f"\n{d2}\n\n"
            "💡 *Note: Ek premium subscription se saare 7 high-end utilities unlock hote hain!*\n\n"
            "Chose searching option from below 👇"
        )

    if update.callback_query:
        await safe_edit(update.callback_query, text, main_kb(user.id))
    else:
        await safe_reply(update, text, main_kb(user.id))
    return ConversationHandler.END

async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    u = q.from_user
    joined = await check_joined(context, u.id)
    if joined:
        await q.answer("🎉 Verification Successful! Enjoy your access.", show_alert=False)
        await start(update, context)
    else:
        await q.answer("⚠️ Access Denied! Please join both channels.", show_alert=True)
        d1 = "━" * 30
        text = (
            f"{d1}\n⚠️  *Channels Join Verification Pending*  ⚠️\n{d1}\n\n"
            f"❌ *Dono channels par subscription missing hai!*\n\n"
            f"📢 Channel 1: {FORCE_JOIN_CHANNEL_1}\n"
            f"📢 Channel 2: {FORCE_JOIN_CHANNEL_2}\n\n"
            "Dono join karke verify button click karein 👇"
        )
        await safe_edit(q, text, force_join_kb())

# ================== MODES ==================
async def _mode(update, context, title, icon, chk, ff, df, mx, mkb):
    q = update.callback_query; await q.answer(); u = q.from_user
    if not is_admin(u.id) and not await check_joined(context, u.id):
        d1 = "━" * 30
        await safe_edit(q, f"{d1}\n⚠️  *Force Join Violation*  ⚠️\n{d1}\n\nKripya pehle dono channels join karein:\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}\n\nVerify par click karein 👇", force_join_kb())
        return
    if is_admin(u.id): 
        info = "🛡️ System Administrator"
    else:
        ok, _, _, ip, _ = chk(u.id)
        fl, dr = ff(u.id), df(u.id)
        p = get_plan(get_user(u.id))
        info = "💎 Unlimited Premium" if ip and p.get("unlimited") else (f"🟢 Premium: {dr}/{p.get('daily_limit',0)} Left Today" if ip else f"🆓 Free Trial: {fl}/{mx} Left")
        
    await safe_edit(q, f"━"*30+f"\n{icon}  *{title}*  {icon}\n"+"━"*30+f"\n\n📊 Subscription Status: `{info}`\n\nSingle ya Batch verification select karein:", mkb(u.id))

async def mode_phone(u,c): await _mode(u,c,"Phone Search","📱",phone_check,phone_free,phone_daily,PHONE_FREE,lambda uid:search_kb(uid,phone_check,phone_free,phone_daily,"phone",PHONE_FREE))

async def mode_email(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user
    if not is_admin(u.id) and not await check_joined(context, u.id):
        d1 = "━" * 30
        await safe_edit(q, f"{d1}\n⚠️  *Force Join Violation*  ⚠️\n{d1}\n\nKripya pehle dono channels join karein:\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}\n\nVerify par click karein 👇", force_join_kb())
        return
    if is_admin(u.id): 
        info = "🛡️ System Administrator"
    else:
        ok, _, d, ip = email_check(u.id); fl = email_free(u.id)
        info = f"💎 Premium Plan: {d} Days Left" if ip else f"🆓 Free Trial: {fl}/{EMAIL_FREE} Left"
        
    await safe_edit(q, f"━"*30+f"\n📧  *Email Search*  📧\n"+"━"*30+f"\n\n📊 Subscription Status: `{info}`\n\nSingle ya Batch verification select karein:", email_kb(u.id))

async def mode_upi(u,c): await _mode(u,c,"UPI Search","💳",upi_check,upi_free,upi_daily,UPI_FREE,lambda uid:search_kb(uid,upi_check,upi_free,upi_daily,"upi",UPI_FREE))
async def mode_aadhaar(u,c): await _mode(u,c,"Aadhaar Search","🪪",aadhaar_check,aadhaar_free,aadhaar_daily,AADHAAR_FREE,lambda uid:search_kb(uid,aadhaar_check,aadhaar_free,aadhaar_daily,"aadhaar",AADHAAR_FREE))
async def mode_vehicle(u,c): await _mode(u,c,"Vehicle RC Search","🚗",vehicle_check,vehicle_free,vehicle_daily,VEHICLE_FREE,lambda uid:search_kb(uid,vehicle_check,vehicle_free,vehicle_daily,"vehicle",VEHICLE_FREE))
async def mode_ifsc(u,c): await _mode(u,c,"IFSC Lookup","🏦",ifsc_check,ifsc_free,ifsc_daily,IFSC_FREE,lambda uid:search_kb(uid,ifsc_check,ifsc_free,ifsc_daily,"ifsc",IFSC_FREE))
async def mode_vinfo(u,c): await _mode(u,c,"Vehicle Info","🚘",vinfo_check,vinfo_free,vinfo_daily,VINFO_FREE,lambda uid:search_kb(uid,vinfo_check,vinfo_free,vinfo_daily,"vinfo",VINFO_FREE))

# ================== PROFILE / STATUS / HELP / BUY ==================
async def profile(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user; ud = get_user(u.id)
    u_name = safe_name(u); ts = ud.get("total_searches", 0)
    t = (f"━"*30+f"\n👤  *User Identity Profile*  👤\n"+"━"*30+
         f"\n\n🆔 User ID: `{u.id}`\n"
         f"👤 User Name: `{u_name}`\n\n"
         f"📱 Phone Searches: `{ud.get('phone_total',0)}` used\n"
         f"📧 Email Searches: `{ud.get('email_total',0)}` used\n"
         f"💳 UPI Searches: `{ud.get('upi_total',0)}` used\n"
         f"🪪 Aadhaar Searches: `{ud.get('aadhaar_total',0)}` used\n"
         f"🚗 Vehicle Searches: `{ud.get('vehicle_total',0)}` used\n"
         f"🏦 IFSC Searches: `{ud.get('ifsc_total',0)}` used\n"
         f"🚘 Vehicle Info: `{ud.get('vinfo_total',0)}` used\n\n"
         f"🔄 Cumulative System Queries: `{ts}`")
    await safe_edit(q, t, back_kb())

async def status_check(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user
    if is_admin(u.id): await safe_edit(q, "🛡️ *Admin Account Status*\n\nAll features: Unlimited Access Active", back_kb()); return
    lines = []
    feats = [
        ("📱 Phone Tracker",phone_check,phone_free,phone_daily,PHONE_FREE),
        ("💳 UPI Verifier",upi_check,upi_free,upi_daily,UPI_FREE),
        ("🪪 Aadhaar Check",aadhaar_check,aadhaar_free,aadhaar_daily,AADHAAR_FREE),
        ("🚗 Vehicle RC",vehicle_check,vehicle_free,vehicle_daily,VEHICLE_FREE),
        ("🏦 IFSC Finder",ifsc_check,ifsc_free,ifsc_daily,IFSC_FREE),
        ("🚘 Vehicle Info",vinfo_check,vinfo_free,vinfo_daily,VINFO_FREE),
    ]
    for nm, chk, ff, df, mx in feats:
        ok, st, _, ip, _ = chk(u.id)
        if ip:
            p = get_plan(get_user(u.id)); dr = df(u.id); lim = p.get("daily_limit", 0)
            lines.append(f"🟢 {nm}: {'💎 Unlimited Access' if p.get('unlimited') else f'💎 {dr}/{lim} Available Today'}")
        else: 
            lines.append(f"🆓 {nm}: `{ff(u.id)}/{mx} Free Quota Left`")
            
    ok, st, _, ip = email_check(u.id)
    lines.append(f"📧 Email Search: {'💎 Unlimited Access' if ip else f'🆓 {email_free(u.id)}/{EMAIL_FREE} Free Quota Left'}")
    await safe_edit(q, f"📊  *System Engine Subscriptions*  📊\n\n" + "\n".join(lines) + f"\n\n💳 Billing Support: {OWNER_CONTACT}\nYour Telegram ID: `{u.id}`", back_kb())

async def help_menu(update, context):
    q = update.callback_query; await q.answer()
    t = (
        f"━"*30+f"\n❓  *Help Desk & Manual*  ❓\n"+"━"*30+"\n\n"
        "🎯 *Ek single plan se saare 7 premium checks unlock hote hain!*\n\n"
        "💎 *Premium Tariffs:*\n"
        "🥉 Bronze: 7 Days   - ₹50  (5 queries/day limit)\n"
        "🥈 Silver: 30 Days  - ₹130 (10 queries/day limit)\n"
        "🥇 Gold: 6 Months - ₹300 (15 queries/day limit)\n"
        "💎 Diamond: 12 Months - ₹799 (Unlimited queries daily)\n\n"
        "💡 *Syntax Formats:*\n"
        "📱 Phone: Standard 10 digit number\n"
        "💳 UPI ID: `user@upi` or `9876543210@ybl`\n"
        "🪪 Aadhaar: Clean 12 digit format\n"
        "🚗 Vehicle RC: `DL3CCE1234` (Without spacing)\n"
        "🏦 IFSC: Bank code `SBIN0001234`\n"
        "🚘 Vehicle Info: `UP32AB1234`\n"
        "📦 Batch Checks: Separate items using a comma (Max 15 items)"
    )
    await safe_edit(q, t, back_kb())

async def buy(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user
    if is_admin(u.id): await safe_edit(q, "🛡️ Admin Account active. Billing is bypassed.", back_kb()); return
    t = (
        f"━"*30+f"\n🛒  *Tariff Subscription Center*  🛒\n"+"━"*30+"\n\n"
        "📦 *All-In-One Plan (Full 7 Intelligence Suite access):*\n\n"
        "🥉 *Bronze: 7 Days*    - ₹50 (5 checks daily)\n"
        "🥈 *Silver: 30 Days*   - ₹130 (10 checks daily)\n"
        "🥇 *Gold: 6 Months*  - ₹300 (15 checks daily)\n"
        "💎 *Diamond: 12 Months* - ₹799 (Unlimited checks daily)\n\n"
        f"📩 System Billing Agent: {OWNER_CONTACT}\nYour Account ID: `{u.id}`"
    )
    await safe_edit(q, t, buy_kb())

# ================== SEARCH EXECUTION ==================
async def _do_single(update, context, api_fn, term, display, icon, use_fn, chk):
    u = update.effective_user
    r = chk(u.id); ok = r[0]; st = r[1]
    if not ok: await safe_reply(update, f"🔒 *Access Blocked!* \n{st}\n\n💳 Billing Support: {OWNER_CONTACT}", buy_kb()); return
    msg = await safe_reply(update, f"🔍 Initiating verification for `{display}`...")
    res = api_fn(term)
    if res["ok"]:
        use_fn(u.id)
        text = format_universal_result(display, res["data"], icon)
        if msg: await safe_edit(msg, text, main_kb(u.id))
        else: await safe_reply(update, text, main_kb(u.id))
    else:
        err_msg = f"❌ *Query Evaluation Failure*\n\nDetail: `{res['error']}`"
        if msg: await safe_edit(msg, err_msg, back_kb())
        else: await safe_reply(update, err_msg, back_kb())

async def _do_batch(update, context, api_fn, items, icon, use_fn, chk):
    u = update.effective_user; total = len(items)
    msg = await safe_reply(update, f"🚀 Executing batch processing for {total} objects...")
    for i, item in enumerate(items, 1):
        res = api_fn(item)
        if res["ok"]:
            use_fn(u.id)
            text = format_universal_result(item, res["data"], icon)
            await safe_reply(update, text)
        else:
            await safe_reply(update, f"❌ *Failed Object: {item}*\n`Reason: {res['error']}`")
    if msg: await safe_edit(msg, f"✅ *Batch Processing Concluded!* Total processed: {total}", main_kb(u.id))
    else: await safe_reply(update, f"✅ *Batch Processing Concluded!* Total processed: {total}", main_kb(u.id))

# Phone Handlers
async def phone_single_s2(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = phone_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}\n💰 Billing Agent: {OWNER_CONTACT}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "📱 Target Number ki Standard region select karein:", country_kb("single")); return PHONE_COUNTRY_SINGLE

async def phone_batch_s2(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = phone_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}\n💰 Billing Agent: {OWNER_CONTACT}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "📦 Batch numbers ki standard region select karein:", country_kb("batch")); return PHONE_COUNTRY_BATCH

async def cs_single(u, c):
    q = u.callback_query; await q.answer()
    if "india" in q.data:
        c.user_data["pc"] = "india"; await safe_edit(q, "🇮🇳 *10-Digit Indian Target Number daalo:*\n_(91 region code autodetect ho jayega)_\n\nSend /cancel to abort."); return PHONE_SINGLE_INDIA
    c.user_data["pc"] = "other"; await safe_edit(q, "🌍 *Target international phone number daalo:*\n_(E.g. +14155552671 with region code)_\n\nSend /cancel to abort."); return PHONE_SINGLE_OTHER

async def cs_batch(u, c):
    q = u.callback_query; await q.answer()
    if "india" in q.data:
        c.user_data["pc"] = "india"; await safe_edit(q, "🇮🇳 *Indian target numbers comma-separated format me daalo (Max 15):*\n\nSend /cancel to abort."); return PHONE_BATCH_INDIA
    c.user_data["pc"] = "other"; await safe_edit(q, "🌍 *International numbers comma-separated formats me daalo (Max 15):*\n\nSend /cancel to abort."); return PHONE_BATCH_OTHER

async def psi(update, context):
    cl = update.message.text.strip().replace(" ","").replace("-","").replace("+","")
    if cl.startswith("91") and len(cl) == 12: cl = cl[2:]
    if not cl.isdigit() or len(cl) != 10: await safe_reply(update, "❌ Incomplete Indian syntax! Provide 10 digits.\n/cancel to exit"); return PHONE_SINGLE_INDIA
    await _do_single(update, context, search_api, "91"+cl, "🇮🇳 91"+cl, "📱", phone_use, phone_check); return ConversationHandler.END

async def pso(update, context):
    cl = update.message.text.strip().replace(" ","").replace("-","").replace("+","")
    if not cl.isdigit() or not(7 <= len(cl) <= 15): await safe_reply(update, "❌ Invalid structure! Provide 7 to 15 digits.\n/cancel to exit"); return PHONE_SINGLE_OTHER
    await _do_single(update, context, search_api, cl, "🌍 "+cl, "📱", phone_use, phone_check); return ConversationHandler.END

async def pbi(update, context):
    nums = [n.strip().replace(" ","").replace("-","").replace("+","") for n in update.message.text.split(",") if n.strip()]
    valid = []
    for n in nums:
        if n.startswith("91") and len(n) == 12: n = n[2:]
        if n.isdigit() and len(n) == 10 and "91"+n not in valid: valid.append("91"+n)
    if not valid: await safe_reply(update, "❌ No structured Indian targets parsed!\n/cancel"); return PHONE_BATCH_INDIA
    await _do_batch(update, context, search_api, valid[:15], "📱", phone_use, phone_check); return ConversationHandler.END

async def pbo(update, context):
    nums = [n.strip().replace(" ","").replace("-","").replace("+","") for n in update.message.text.split(",") if n.strip()]
    valid = [n for n in nums if n.isdigit() and 7 <= len(n) <= 15]
    if not valid: await safe_reply(update, "❌ No international structured phone systems parsed!\n/cancel"); return PHONE_BATCH_OTHER
    await _do_batch(update, context, search_api, valid[:15], "📱", phone_use, phone_check); return ConversationHandler.END

# Email Handlers
async def email_ss(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _ = email_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}\n💰 Billing Agent: {OWNER_CONTACT}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "📧 *Target Email address daalo:*\n_E.g. user@domain.com_\n\nSend /cancel to exit."); return EMAIL_SINGLE

async def email_sp(update, context):
    e = update.message.text.strip()
    if not valid_email(e): await safe_reply(update, "❌ Target address email structure failure!\n/cancel"); return EMAIL_SINGLE
    await _do_single(update, context, search_api, e, e, "📧", lambda uid: email_use(uid, email_check(uid)[3]), lambda uid: (*email_check(uid), None)); return ConversationHandler.END

async def email_bs(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _ = email_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "📦 *Batch Emails comma-separated format me daalo (Max 15):*\n\nSend /cancel to exit."); return EMAIL_BATCH

async def email_bp(update, context):
    emails = [e.strip() for e in update.message.text.split(",") if valid_email(e.strip())][:15]
    if not emails: await safe_reply(update, "❌ No emails passed criteria verification!\n/cancel"); return EMAIL_BATCH
    await _do_batch(update, context, search_api, emails, "📧", lambda uid: email_use(uid, email_check(uid)[3]), lambda uid: (*email_check(uid), None)); return ConversationHandler.END

# UPI Handlers
async def upi_ss(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = upi_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}\n💰 Billing Agent: {OWNER_CONTACT}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "💳 *Target UPI VPA address daalo:*\n✅ `target@bank`\n\nSend /cancel to exit."); return UPI_SINGLE

async def upi_sp(update, context):
    uid = update.message.text.strip()
    if not valid_upi(uid): await safe_reply(update, "❌ Standard format required: `id@handle`\n/cancel"); return UPI_SINGLE
    await _do_single(update, context, upi_api, uid, uid, "💳", upi_use, upi_check); return ConversationHandler.END

async def upi_bs(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = upi_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "📦 *Batch UPI VPAs comma-separated format me daalo (Max 15):*\n\nSend /cancel to exit."); return UPI_BATCH

async def upi_bp(update, context):
    upis = [u.strip() for u in update.message.text.split(",") if valid_upi(u.strip())][:15]
    if not upis: await safe_reply(update, "❌ Zero elements matched structure!\n/cancel"); return UPI_BATCH
    await _do_batch(update, context, upi_api, upis, "💳", upi_use, upi_check); return ConversationHandler.END

# Aadhaar Handlers
async def aadh_ss(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = aadhaar_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}\n💰 Billing Agent: {OWNER_CONTACT}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "🪪 *12-Digit clean Aadhaar index daalo:*\n✅ `E.g. 112233445566`\n\nSend /cancel to exit."); return AADHAAR_SINGLE

async def aadh_sp(update, context):
    a = update.message.text.strip().replace(" ", "").replace("-", "")
    if not valid_aadhaar(a): await safe_reply(update, "❌ Aadhaar verification index must be exactly 12 digits.\n/cancel"); return AADHAAR_SINGLE
    await _do_single(update, context, aadhaar_api, a, a, "🪪", aadhaar_use, aadhaar_check); return ConversationHandler.END

async def aadh_bs(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = aadhaar_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "📦 *Batch Aadhaar keys comma-separated format me daalo (Max 15):*\n\nSend /cancel to exit."); return AADHAAR_BATCH

async def aadh_bp(update, context):
    nums = [a.strip().replace(" ", "").replace("-", "") for a in update.message.text.split(",") if valid_aadhaar(a.strip().replace(" ", "").replace("-", ""))][:15]
    if not nums: await safe_reply(update, "❌ Batch syntax has no verifiable keys!\n/cancel"); return AADHAAR_BATCH
    await _do_batch(update, context, aadhaar_api, nums, "🪪", aadhaar_use, aadhaar_check); return ConversationHandler.END

# Vehicle RC Handlers
async def veh_ss(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = vehicle_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}\n💰 Billing Agent: {OWNER_CONTACT}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "🚗 *Verifiable Vehicle number index daalo:*\n✅ `DL3CCE1234`\n\nSend /cancel to exit."); return VEHICLE_SINGLE

async def veh_sp(update, context):
    rc = update.message.text.strip().upper().replace(" ", "").replace("-", "")
    if len(rc) < 4: await safe_reply(update, "❌ Invalid plate syntax registration index!\n/cancel"); return VEHICLE_SINGLE
    await _do_single(update, context, vehicle_api, rc, rc, "🚗", vehicle_use, vehicle_check); return ConversationHandler.END

async def veh_bs(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = vehicle_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "📦 *Batch Plates comma-separated format me daalo (Max 15):*\n\nSend /cancel to exit."); return VEHICLE_BATCH

async def veh_bp(update, context):
    rcs = [r.strip().upper().replace(" ", "").replace("-", "") for r in update.message.text.split(",") if len(r.strip()) >= 4][:15]
    if not rcs: await safe_reply(update, "❌ No verifiable plates passed standard tests!\n/cancel"); return VEHICLE_BATCH
    await _do_batch(update, context, vehicle_api, rcs, "🚗", vehicle_use, vehicle_check); return ConversationHandler.END

# IFSC Handlers
async def ifsc_ss(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = ifsc_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}\n💰 Billing Agent: {OWNER_CONTACT}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "🏦 *Bank index IFSC syntax daalo:*\n✅ `E.g. HDFC0000001`\n\nSend /cancel to exit."); return IFSC_SINGLE

async def ifsc_sp(update, context):
    code = update.message.text.strip().upper().replace(" ", "")
    if not valid_ifsc(code): await safe_reply(update, "❌ IFSC requirements: 11 alpha-numeric index.\n/cancel"); return IFSC_SINGLE
    await _do_single(update, context, ifsc_api, code, code, "🏦", ifsc_use, ifsc_check); return ConversationHandler.END

async def ifsc_bs(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = ifsc_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "📦 *Batch IFSC parameters comma-separated format me daalo (Max 15):*\n\nSend /cancel to exit."); return IFSC_BATCH

async def ifsc_bp(update, context):
    codes = [c.strip().upper().replace(" ", "") for c in update.message.text.split(",") if valid_ifsc(c.strip().upper().replace(" ", ""))][:15]
    if not codes: await safe_reply(update, "❌ Batch index contains no verified IFSC instances!\n/cancel"); return IFSC_BATCH
    await _do_batch(update, context, ifsc_api, codes, "🏦", ifsc_use, ifsc_check); return ConversationHandler.END

# ================== VEHICLE INFO HANDLERS ==================
async def vinfo_ss(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = vinfo_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}\n💰 Billing Agent: {OWNER_CONTACT}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "🚘 *Verifiable Vehicle Detailed plate daalo:*\n✅ `E.g. UP32AB1234`\n\nSend /cancel to exit."); return VINFO_SINGLE

async def vinfo_sp(update, context):
    vn = update.message.text.strip().upper().replace(" ", "").replace("-", "")
    if not valid_vehicle_number(vn):
        await safe_reply(update, "❌ Invalid index layout standards.\n/cancel"); return VINFO_SINGLE
    await _do_single(update, context, vinfo_api, vn, vn, "🚘", vinfo_use, vinfo_check); return ConversationHandler.END

async def vinfo_bs(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c, q.from_user.id):
        await safe_edit(q, f"⚠️ *Dono Channels Join Karna Zaroori Hai!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return ConversationHandler.END
    ok, st, _, _, _ = vinfo_check(q.from_user.id)
    if not ok: await safe_edit(q, f"🔒 {st}", buy_kb()); return ConversationHandler.END
    await safe_edit(q, "📦 *Batch plates comma-separated format me daalo (Max 15):*\n\nSend /cancel to exit."); return VINFO_BATCH

async def vinfo_bp(update, context):
    vehicles = [v.strip().upper().replace(" ", "").replace("-", "") for v in update.message.text.split(",") if valid_vehicle_number(v.strip().upper().replace(" ", "").replace("-", ""))][:15]
    if not vehicles: await safe_reply(update, "❌ Batch array validation rejected! No matched patterns.\n/cancel"); return VINFO_BATCH
    await _do_batch(update, context, vinfo_api, vehicles, "🚘", vinfo_use, vinfo_check); return ConversationHandler.END

# Cancel
async def cancel(u, c):
    c.user_data.clear()
    await safe_reply(u, "❌ Operation cancelled on user request.", main_kb(u.effective_user.id))
    return ConversationHandler.END

# ================== ADMIN ACTIONS ==================
async def admin_panel(update, context):
    if not is_admin(update.effective_user.id):
        await safe_reply(update, "❌ Admin Credentials Required!")
        return ConversationHandler.END
    users = load_users(); t = len(users); p = sum(1 for v in users.values() if v.get("is_premium"))
    txt = f"━"*30+f"\n🛠️  *System Administrator Core Panel*  🛠️\n"+"━"*30+f"\n\n🛡️ Admin Instances: `{len(ADMIN_IDS)}` active\n👥 Total Client Node DB: `{t}`\n💎 Premium Tier Status: `{p}`\n🆓 Trial Nodes Online: `{t-p}`\n\nPerform operations via nodes below:"
    if update.callback_query: await safe_edit(update.callback_query, txt, admin_kb())
    else: await safe_reply(update, txt, admin_kb())
    return ConversationHandler.END

async def admin_back(u, c): await admin_panel(u, c)

async def adm_add_s(u, c):
    q = u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer(); await safe_edit(q, "➕ *Provision Client Node*\n\nProvide Telegram UID:\n/cancel to exit."); return ADMIN_ADD_ID

async def adm_add_id(u, c):
    uid = u.message.text.strip()
    if not uid.isdigit(): await safe_reply(u, "❌ Structural violation! Provide positive integers.\n/cancel"); return ADMIN_ADD_ID
    c.user_data["admin_uid"] = uid
    await safe_reply(u, f"✅ Targeted User Node: `{uid}`\nChoose package structure:", plan_kb("plan")); return ADMIN_ADD_PLAN

async def adm_add_plan(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "admin_back": await admin_panel(u, c); return ConversationHandler.END
    pm = {"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk = pm.get(q.data, "7days"); uid = c.user_data.get("admin_uid"); plan = PLANS.get(pk)
    exp = upgrade(int(uid), pk); dl = "Unlimited Daily" if plan["unlimited"] else f"{plan['daily_limit']}/Day"
    await safe_edit(q, f"✅ *Package Provision Complete!*\n🆔 Node: `{uid}`\n📦 Tier: `{plan['name']}`\n📅 Expiry Date: `{exp}`\n📱 Search Limit: `{dl}`", admin_kb()); return ConversationHandler.END

async def adm_rem_s(u, c):
    q = u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer(); await safe_edit(q, "❌ *De-Provision Client Node*\n\nProvide Telegram UID:\n/cancel"); return ADMIN_REM_ID

async def adm_rem_p(u, c):
    uid = u.message.text.strip(); delete_user(uid)
    await safe_reply(u, f"✅ Client Node `{uid}` successfully deleted from storage!", admin_kb()); return ConversationHandler.END

async def adm_sp_s(u, c):
    q = u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer(); await safe_edit(q, "📅 *Modify Subscription Plan*\n\nProvide Telegram UID:\n/cancel"); return ADMIN_EXP_ID

async def adm_sp_id(u, c):
    uid = u.message.text.strip(); c.user_data["admin_uid"] = uid
    await safe_reply(u, f"Targeted Node: `{uid}`\nChoose new plan structure:", plan_kb("plan")); return ADMIN_EXP_PLAN

async def adm_sp_set(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "admin_back": await admin_panel(u, c); return ConversationHandler.END
    pm = {"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk = pm.get(q.data, "7days"); uid = c.user_data.get("admin_uid"); plan = PLANS.get(pk)
    exp = upgrade(int(uid), pk); dl = "Unlimited Daily" if plan["unlimited"] else f"{plan['daily_limit']}/Day"
    await safe_edit(q, f"✅ *Package Overwritten successfully!*\n🆔 Node: `{uid}`\n📦 Tier: `{plan['name']}`\n📅 Expiry Date: `{exp}`\n📱 Search Limit: `{dl}`", admin_kb()); return ConversationHandler.END

async def adm_list(u, c):
    q = u.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer(); users = load_users()
    if not users: await safe_edit(q, "📋 System databases are empty!", admin_kb()); return
    txt = f"📋 *Provisioned Nodes list ({len(users)})*\n\n"
    for uid, info in users.items():
        plan = get_plan(info); ts = info.get("total_searches", 0)
        if int(uid) in ADMIN_IDS: st = "🛡️ Admin"
        elif info.get("is_premium") and info.get("expiry"):
            try:
                ed = date.fromisoformat(info["expiry"])
                st = f"💎 {plan['name']} ({(ed-date.today()).days}d)" if date.today() <= ed else "🔴 Expired"
            except: st = "⚪ N/A"
        else: st = "🆓 Trial Mode"
        txt += f"`{uid}` | {st} | 🔍 `{ts}` queries\n"
    await safe_edit(q, txt[:4000], admin_kb())

async def adm_stats(u, c):
    q = u.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer(); users = load_users(); ts = sum(v.get("total_searches", 0) for v in users.values())
    act = sum(1 for u2, v in users.items() if v.get("is_premium") and int(u2) not in ADMIN_IDS)
    await safe_edit(q, f"📊  *Core Metrics Information*  📊\n\n👥 Storage Client Nodes: `{len(users)}` database instances\n🔍 Total Processed Queries: `{ts}` operations\n💎 Active Paying Clients: `{act}` premium\n📅 Date: `{date.today()}`", admin_kb())

async def adm_monitor(u, c):
    q = u.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer()
    users = load_users(); free = [v for u2, v in users.items() if not v.get("is_premium") and int(u2) not in ADMIN_IDS]
    await safe_edit(q, f"🆓  *Trial Allocation Monitor*  🆓\n\n👥 Registered free trials: `{len(free)}` nodes\n\nSelect diagnostic filters below:", monitor_kb())

async def mon_exhausted(u, c):
    q = u.callback_query; await q.answer(); users = load_users(); txt = "🔴 *Allocation Exhausted Nodes*\n\n"; cnt = 0
    all_keys = [("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE),("vinfo_free_used",VINFO_FREE)]
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"): continue
        if all(max(0, mx - info.get(k, 0)) <= 0 for k, mx in all_keys):
            txt += f"🔴 UID: `{uid}` | Total searches: `{info.get('total_searches',0)}` used\n"; cnt += 1
    txt += f"\n💡 *{cnt} nodes* are currently fully exhausted!"
    await safe_edit(q, txt[:4000], monitor_kb())

async def mon_active(u, c):
    q = u.callback_query; await q.answer(); users = load_users(); txt = "🟢 *Active Trial Nodes*\n\n"; cnt = 0
    all_keys = [("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE),("vinfo_free_used",VINFO_FREE)]
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"): continue
        if any(max(0, mx - info.get(k, 0)) > 0 for k, mx in all_keys):
            txt += f"🟢 UID: `{uid}`\n"; cnt += 1
    txt += f"\nDiagnostic count: {cnt}"
    await safe_edit(q, txt[:4000], monitor_kb())

async def mon_summary(u, c):
    q = u.callback_query; await q.answer(); users = load_users(); t = 0; ex = 0
    all_keys = [("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE),("vinfo_free_used",VINFO_FREE)]
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"): continue
        t += 1
        if all(max(0, mx - info.get(k, 0)) <= 0 for k, mx in all_keys): ex += 1
    await safe_edit(q, f"📊 *Trial Nodes summary*\n\n👥 Total Free Nodes: `{t}`\n🔴 Exhausted instances: `{ex}`\n📅 Diagnostic Date: `{date.today()}`", monitor_kb())

# Broadcast Handlers
async def bc_start(u, c):
    q = u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer(); await safe_edit(q, f"📢 *Global Signal Broadcaster*\n\n👥 Target node clusters: *{len(load_users())}*\n\nWrite broadcast signal below:\n/cancel to abort."); return ADMIN_BROADCAST_MSG

async def bc_msg(u, c):
    m = u.message.text.strip()
    if not m: await safe_reply(u, "❌ Signal cannot be void!\n/cancel"); return ADMIN_BROADCAST_MSG
    c.user_data["bc"] = m
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm Signal Broadcast", callback_data="broadcast_confirm")],[InlineKeyboardButton("❌ Abort Operation", callback_data="broadcast_cancel")]])
    await safe_reply(u, f"📢 *Core Transmission Signal preview:*\n\n{m}\n\n👥 Target receivers: `{len(load_users())}` nodes.\nExecute?", kb); return ADMIN_BROADCAST_CONFIRM

async def bc_confirm(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "broadcast_cancel":
        await safe_edit(q, "❌ Signal transmission aborted by admin.", admin_kb()); c.user_data.pop("bc", None); return ConversationHandler.END
    msg = c.user_data.get("bc", ""); users = load_users(); total = len(users)
    bt = f"📢  *Official Broadcast Transmission*  📢\n{'━'*25}\n\n{msg}\n\n{'━'*25}\n💬 System Agent: {OWNER_CONTACT}"
    sm = await safe_reply(u, f"🚀 Injecting signal to {total} client nodes...")
    s, f2, b, ct = 0, 0, 0, 0
    for uid in users:
        ct += 1
        try: await c.bot.send_message(chat_id=int(uid), text=bt, parse_mode="Markdown"); s += 1
        except Exception as e:
            if any(w in str(e).lower() for w in ["blocked", "forbidden", "not found"]): b += 1
            else: f2 += 1
        if ct % 10 == 0 or ct == total:
            try: await sm.edit_text(f"🚀 Injection Progress: {ct}/{total}\n✅ Deliveries: {s}\n🚫 Node Blocks: {b}\n❌ System Rejections: {f2}", parse_mode="Markdown")
            except: pass
    await safe_reply(u, f"✅ *Transmission Concluded!*\n\n👥 Target DB nodes: `{total}`\n✅ Dispatched successfully: `{s}`\n🚫 System Blocked: `{b}`\n❌ Network Drops: `{f2}`", admin_kb())
    c.user_data.pop("bc", None); return ConversationHandler.END

# Custom Plan Handlers
async def custom_s(u, c):
    q = u.callback_query; await q.answer()
    await safe_edit(q, "⚙️ *Custom Node Configurations*\n\nSet duration (Provide days as positive integer):\n/cancel"); return ADMIN_CUSTOM_DAYS

async def custom_days(u, c):
    t = u.message.text.strip()
    if not t.isdigit() or int(t) <= 0: await safe_reply(u, "❌ Positive integers required!\n/cancel"); return ADMIN_CUSTOM_DAYS
    c.user_data["cd"] = int(t)
    await safe_reply(u, f"📅 Duration configured: *{t} Days*\n\nSet Daily query capacity limit: (0 to assign unlimited)\n/cancel to abort"); return ADMIN_CUSTOM_LIMIT

async def custom_limit(u, c):
    t = u.message.text.strip()
    if not t.isdigit(): await safe_reply(u, "❌ Syntax error. Daily limit must be integer.\n/cancel"); return ADMIN_CUSTOM_LIMIT
    lim = int(t); unl = (lim == 0); days = c.user_data.get("cd"); uid = c.user_data.get("admin_uid")
    exp = upgrade_custom(int(uid), days, lim, unl)
    ls = "Unlimited access" if unl else f"{lim} Checks Daily"
    await safe_reply(u, f"⚙️ *Custom Provision Complete!*\n🆔 Targeted Node: `{uid}`\n📅 Config: `{days} Days` | Expiry: `{exp}`\n📱 Limits: `{ls}`", admin_kb())
    c.user_data.pop("cd", None); c.user_data.pop("admin_uid", None); return ConversationHandler.END

async def main_menu_cb(u, c): await start(u, c); return ConversationHandler.END

# Error Handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"❌ Exception: {context.error}")

# ================== MAIN ==================
def main():
    threading.Thread(target=start_webserver, daemon=True).start()
    print("🌐 Keep-alive Flask server started!")

    req = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30, pool_timeout=30)
    gur = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30, pool_timeout=30)
    app = ApplicationBuilder().token(BOT_TOKEN).request(req).get_updates_request(gur).build()

    C = ConversationHandler; CQ = CallbackQueryHandler; MH = MessageHandler; CMD = CommandHandler
    F = filters.TEXT & ~filters.COMMAND
    UNIVERSAL_FALLBACKS = [CMD("cancel", cancel), CMD("start", start)]

    convs = [
        C(entry_points=[CQ(phone_single_s2, pattern="^phone_single$")], states={PHONE_COUNTRY_SINGLE:[CQ(cs_single, pattern="^country_(india|other)_single$")], PHONE_SINGLE_INDIA:[MH(F, psi)], PHONE_SINGLE_OTHER:[MH(F, pso)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(phone_batch_s2, pattern="^phone_batch$")], states={PHONE_COUNTRY_BATCH:[CQ(cs_batch, pattern="^country_(india|other)_batch$")], PHONE_BATCH_INDIA:[MH(F, pbi)], PHONE_BATCH_OTHER:[MH(F, pbo)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(email_ss, pattern="^email_single$")], states={EMAIL_SINGLE:[MH(F, email_sp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(email_bs, pattern="^email_batch$")], states={EMAIL_BATCH:[MH(F, email_bp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(upi_ss, pattern="^upi_single$")], states={UPI_SINGLE:[MH(F, upi_sp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(upi_bs, pattern="^upi_batch$")], states={UPI_BATCH:[MH(F, upi_bp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(aadh_ss, pattern="^aadhaar_single$")], states={AADHAAR_SINGLE:[MH(F, aadh_sp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(aadh_bs, pattern="^aadhaar_batch$")], states={AADHAAR_BATCH:[MH(F, aadh_bp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(veh_ss, pattern="^vehicle_single$")], states={VEHICLE_SINGLE:[MH(F, veh_sp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(veh_bs, pattern="^vehicle_batch$")], states={VEHICLE_BATCH:[MH(F, veh_bp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(ifsc_ss, pattern="^ifsc_single$")], states={IFSC_SINGLE:[MH(F, ifsc_sp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(ifsc_bs, pattern="^ifsc_batch$")], states={IFSC_BATCH:[MH(F, ifsc_bp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(vinfo_ss, pattern="^vinfo_single$")], states={VINFO_SINGLE:[MH(F, vinfo_sp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(vinfo_bs, pattern="^vinfo_batch$")], states={VINFO_BATCH:[MH(F, vinfo_bp)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        # Admin Conversations
        C(entry_points=[CQ(adm_add_s, pattern="^admin_add$")], states={ADMIN_ADD_ID:[MH(F, adm_add_id)], ADMIN_ADD_PLAN:[CQ(custom_s, pattern="^plan_custom$"), CQ(adm_add_plan, pattern="^plan_")], ADMIN_CUSTOM_DAYS:[MH(F, custom_days)], ADMIN_CUSTOM_LIMIT:[MH(F, custom_limit)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(adm_rem_s, pattern="^admin_remove$")], states={ADMIN_REM_ID:[MH(F, adm_rem_p)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(adm_sp_s, pattern="^admin_setplan$")], states={ADMIN_EXP_ID:[MH(F, adm_sp_id)], ADMIN_EXP_PLAN:[CQ(custom_s, pattern="^plan_custom$"), CQ(adm_sp_set, pattern="^plan_")], ADMIN_CUSTOM_DAYS:[MH(F, custom_days)], ADMIN_CUSTOM_LIMIT:[MH(F, custom_limit)]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(bc_start, pattern="^admin_broadcast$")], states={ADMIN_BROADCAST_MSG:[MH(F, bc_msg)], ADMIN_BROADCAST_CONFIRM:[CQ(bc_confirm, pattern="^broadcast_(confirm|cancel)$")]}, fallbacks=UNIVERSAL_FALLBACKS, per_message=False, allow_reentry=True),
    ]
    for cv in convs: app.add_handler(cv)

    app.add_handler(CMD("start", start))
    app.add_handler(CMD("admin", admin_panel))
    app.add_error_handler(error_handler)

    for p, f2 in [
        ("mode_phone", mode_phone), ("mode_email", mode_email),
        ("mode_upi", mode_upi), ("mode_aadhaar", mode_aadhaar),
        ("mode_vehicle", mode_vehicle), ("mode_ifsc", mode_ifsc),
        ("mode_vinfo", mode_vinfo),
        ("profile", profile), ("status", status_check),
        ("help", help_menu), ("buy", buy),
        ("admin_list", adm_list), ("admin_stats", adm_stats),
        ("admin_back", admin_back), ("admin_free_monitor", adm_monitor),
        ("monitor_exhausted", mon_exhausted), ("monitor_active", mon_active),
        ("monitor_summary", mon_summary), ("main_menu", main_menu_cb),
        ("verify_join", verify_join),
    ]:
        app.add_handler(CQ(f2, pattern=f"^{p}$"))

    print("🤖 Bot Running! Dual Channel & Premium Colorful UI Active.")
    app.run_polling(drop_pending_updates=True, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()

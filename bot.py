#!/usr/bin/env python3
"""
🔍 Ultimate Intelligence Bot
Phone + Email + UPI + Aadhaar + Vehicle + IFSC + Vehicle Info
ONE PLAN = ALL ACCESS
+ Dual Channel Force Join Check
+ Redeem Code System (Admin Generated)
+ Clean Results Only (ALL Metadata & Rtfgamming Watermarks Blocked)
+ Fast In-Memory Cache + MongoDB Cloud + 24/7 Keep Alive
+ Highly Colorful & Premium Emoji Theme Buttons
"""

import json, os, threading, requests, logging, asyncio, re
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
DEFAULT_PIN   = "happyrb"
API_URL       = "https://num-info-hiteck.asurpapa.workers.dev/"

# --- UPI CONFIG ---
UPI_API_URL   = "https://api-src.alonepatel.shop/api"
UPI_API_KEY   = "INDIAN_HACKER_BRO"

AADHAAR_API_URL = "https://ansh-apis.is-dev.org/api/ration"
VEHICLE_API_URL = "https://ansh-apis.is-dev.org/api/vehicle"
IFSC_API_URL    = "https://all-api-by-nitin-developer-best1.binderdhaniya6.workers.dev/api"
VINFO_API_URL   = "https://rtf-api-server.onrender.com/api"

NITIN_API_KEY   = "INDIAN_HACKER_BRO"
AADHAAR_API_KEY = "shree"
VEHICLE_API_KEY = "ansh"
IFSC_API_KEY    = "NITIN"
VINFO_API_KEY   = "demo2"
OWNER_CONTACT   = "@theplayerror"

FORCE_JOIN_CHANNEL_1    = "@hackkwr"
FORCE_JOIN_CHANNEL_1_ID = "@hackkwr"
FORCE_JOIN_CHANNEL_2    = "@zerotracelegit"
FORCE_JOIN_CHANNEL_2_ID = "@zerotracelegit"

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://httplegitfs_db_user:Q8uGZxERXsrf2VV1@cluster0.iojnad7.mongodb.net/?retryWrites=true&w=majority"
)

# Common headers to avoid 403 / Cloudflare blocks
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

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
PHONE_SINGLE=10; PHONE_BATCH=11
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
# Redeem Code Admin States
REDEEM_CREATE_CODE=90; REDEEM_CREATE_SEARCHES=91; REDEEM_CREATE_LIMIT=92
REDEEM_DELETE_CODE=93

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
    import logging as lg
    lg.getLogger('werkzeug').setLevel(lg.ERROR)
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================== FORCE JOIN ==================
async def check_joined(context, uid):
    if is_admin(uid): return True
    try:
        m1 = await asyncio.wait_for(context.bot.get_chat_member(FORCE_JOIN_CHANNEL_1_ID, uid), timeout=3.0)
        joined_1 = m1.status in ["member", "administrator", "creator", "restricted"]
        if not joined_1: return False
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
REDEEM_CODES = {}
LOCAL_FILE = Path("users.json")
REDEEM_FILE = Path("redeem_codes.json")

try:
    mc = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = mc["tele_intel_bot"]
    users_col = db["users"]
    redeem_col = db["redeem_codes"]
    mc.admin.command('ping')
    print("✅ MongoDB Connected!")
except Exception as e:
    print("⚠️ MongoDB Warning:", e)
    users_col = None
    redeem_col = None

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
    "redeemed_codes": [],
}

def init_cache():
    global USERS_CACHE, REDEEM_CODES
    if users_col is not None:
        try:
            for doc in users_col.find():
                uid = doc["_id"]
                USERS_CACHE[uid] = {k: v for k, v in doc.items() if k != "_id"}
        except Exception: pass
    elif LOCAL_FILE.exists():
        try: USERS_CACHE = json.loads(LOCAL_FILE.read_text())
        except Exception: USERS_CACHE = {}
    if redeem_col is not None:
        try:
            for doc in redeem_col.find():
                code = doc["_id"]
                REDEEM_CODES[code] = {k: v for k, v in doc.items() if k != "_id"}
        except Exception: pass
    elif REDEEM_FILE.exists():
        try: REDEEM_CODES = json.loads(REDEEM_FILE.read_text())
        except Exception: REDEEM_CODES = {}

init_cache()

def sync_user_background(uid: str, data: dict):
    def _save():
        if users_col is not None:
            try: users_col.update_one({"_id": str(uid)}, {"$set": data}, upsert=True); return
            except Exception: pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE, indent=2))
        except Exception: pass
    threading.Thread(target=_save, daemon=True).start()

def sync_redeem_background(code: str, data: dict):
    def _save():
        if redeem_col is not None:
            try: redeem_col.update_one({"_id": code}, {"$set": data}, upsert=True); return
            except Exception: pass
        try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES, indent=2))
        except Exception: pass
    threading.Thread(target=_save, daemon=True).start()

def delete_redeem_background(code: str):
    def _del():
        if redeem_col is not None:
            try: redeem_col.delete_one({"_id": code})
            except Exception: pass
        try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES, indent=2))
        except Exception: pass
    threading.Thread(target=_del, daemon=True).start()

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
    if uid in USERS_CACHE: del USERS_CACHE[uid]
    def _del():
        if users_col is not None:
            try: users_col.delete_one({"_id": uid})
            except Exception: pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE, indent=2))
        except Exception: pass
    threading.Thread(target=_del, daemon=True).start()

def load_users(): return USERS_CACHE

# ================== REDEEM CODE SYSTEM ==================
def create_redeem_code(code, free_searches, max_uses):
    code = code.upper().strip()
    REDEEM_CODES[code] = {
        "free_searches": free_searches,
        "max_uses": max_uses,
        "used_count": 0,
        "used_by": [],
        "created_at": date.today().isoformat(),
        "active": True
    }
    sync_redeem_background(code, REDEEM_CODES[code])
    return True

def get_redeem_code(code):
    code = code.upper().strip()
    return REDEEM_CODES.get(code, None)

def use_redeem_code(code, user_id):
    code = code.upper().strip()
    user_id = str(user_id)
    
    if code not in REDEEM_CODES:
        return False, "❌ Invalid redeem code! Code does not exist."
    
    rc = REDEEM_CODES[code]
    
    if not rc.get("active", True):
        return False, "❌ This code has been deactivated by admin."
    
    if rc["used_count"] >= rc["max_uses"]:
        return False, "❌ This code has reached its maximum redemption limit!"
    
    if user_id in rc.get("used_by", []):
        return False, "❌ You have already redeemed this code!"
    
    ud = get_user(user_id)
    searches = rc["free_searches"]
    
    free_keys = [
        "phone_free_used", "email_free_used", "upi_free_used",
        "aadhaar_free_used", "vehicle_free_used", "ifsc_free_used", "vinfo_free_used"
    ]
    free_maxes = {
        "phone_free_used": PHONE_FREE,
        "email_free_used": EMAIL_FREE,
        "upi_free_used": UPI_FREE,
        "aadhaar_free_used": AADHAAR_FREE,
        "vehicle_free_used": VEHICLE_FREE,
        "ifsc_free_used": IFSC_FREE,
        "vinfo_free_used": VINFO_FREE,
    }
    
    for key in free_keys:
        current_used = ud.get(key, 0)
        new_used = max(0, current_used - searches)
        ud[key] = new_used
    
    if "redeemed_codes" not in ud:
        ud["redeemed_codes"] = []
    ud["redeemed_codes"].append(code)
    save_user(user_id, ud)
    
    rc["used_count"] += 1
    rc["used_by"].append(user_id)
    REDEEM_CODES[code] = rc
    sync_redeem_background(code, rc)
    
    return True, f"🎉 Code `{code}` redeemed successfully!\n\n🎁 You received *{searches} extra free searches* on ALL features!\n\n📊 Code used by: `{rc['used_count']}/{rc['max_uses']}` users"

def delete_redeem_code(code):
    code = code.upper().strip()
    if code in REDEEM_CODES:
        del REDEEM_CODES[code]
        delete_redeem_background(code)
        return True
    return False

def list_redeem_codes():
    return REDEEM_CODES

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
               "phone_daily": 0, "phone_date": "", "upi_daily": 0, "upi_date": "",
               "aadhaar_daily": 0, "aadhaar_date": "", "vehicle_daily": 0, "vehicle_date": "",
               "ifsc_daily": 0, "ifsc_date": "", "vinfo_daily": 0, "vinfo_date": ""})
    save_user(uid, ud); return exp

def upgrade_custom(uid, days, lim, unl):
    uid = str(uid); ud = get_user(uid)
    exp = (date.today() + timedelta(days=days)).isoformat()
    ud.update({"plan": f"custom_{days}d", "expiry": exp, "is_premium": True,
               "phone_daily": 0, "phone_date": "", "upi_daily": 0, "upi_date": "",
               "aadhaar_daily": 0, "aadhaar_date": "", "vehicle_daily": 0, "vehicle_date": "",
               "ifsc_daily": 0, "ifsc_date": "", "vinfo_daily": 0, "vinfo_date": "",
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
        except Exception: pass
    fl = free_rem(uid, fk, mx)
    if fl > 0: return True, f"Trial ({fl}/{mx} left)", 0, False, "trial"
    return False, "Trial khatam! Plan lo ya redeem code use karo.", 0, False, "trial"

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
    return False, "Free trial khatam! Plan lo ya redeem code use karo.", 0, False

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
    try:
        return fn()
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "⏱️ Request timed out. Server is taking too long."}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "🌐 Connection error. API host is currently unreachable."}
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response is not None else "Unknown"
        return {"ok": False, "error": f"⚠️ Server Error (HTTP {code})"}
    except Exception as e:
        logger.error(f"API Execution Error: {e}", exc_info=True)
        return {"ok": False, "error": f"❌ Error: {str(e)}"}

def phone_api(number):
    def call():
        url = "https://num-info-hiteck.asurpapa.workers.dev/api"
        r = requests.get(url, params={"key": DEFAULT_PIN, "number": number}, headers=COMMON_HEADERS, timeout=15)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code} Error"}
        return {"ok": True, "data": r.json()}
    return _safe_api(call)

def search_api(term):
    def call():
        r = requests.get(API_URL, params={"pin": DEFAULT_PIN, "term": term}, headers=COMMON_HEADERS, timeout=15)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code} Error"}
        return {"ok": True, "data": r.json()}
    return _safe_api(call)

# --- REFINED UPI API CALL ---
def upi_api(upi_id):
    def call():
        params = {
            "key": UPI_API_KEY,
            "action": "upiinfo",
            "upi": upi_id.strip()
        }
        r = requests.get(UPI_API_URL, params=params, headers=COMMON_HEADERS, timeout=15)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code}: Unable to fetch UPI details."}
        
        try:
            data = r.json()
        except Exception:
            return {"ok": False, "error": "API response was not in valid JSON format."}

        # Check API level internal error
        if isinstance(data, dict):
            if data.get("status") in [False, "error", 400, 404] or data.get("success") is False:
                msg = data.get("message") or data.get("error") or data.get("msg") or "Invalid UPI or No Record Found."
                return {"ok": False, "error": str(msg)}
        return {"ok": True, "data": data}
    return _safe_api(call)

def aadhaar_api(num):
    def call():
        r = requests.get(AADHAAR_API_URL, params={"key": AADHAAR_API_KEY, "id": num}, headers=COMMON_HEADERS, timeout=15)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code} Error"}
        return {"ok": True, "data": r.json()}
    return _safe_api(call)

def vehicle_api(rc):
    def call():
        r = requests.get(VEHICLE_API_URL, params={"key": VEHICLE_API_KEY, "rc": rc}, headers=COMMON_HEADERS, timeout=15)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code} Error"}
        return {"ok": True, "data": r.json()}
    return _safe_api(call)

def ifsc_api(code):
    def call():
        r = requests.get(IFSC_API_URL, params={"type": "ifsc", "search": code, "api_key": IFSC_API_KEY}, headers=COMMON_HEADERS, timeout=15)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code} Error"}
        return {"ok": True, "data": r.json()}
    return _safe_api(call)

def vinfo_api(vehicle_num):
    def call():
        r = requests.get(VINFO_API_URL, params={"types": "vinfo", "key": VINFO_API_KEY, "spell": vehicle_num}, headers=COMMON_HEADERS, timeout=15)
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code} Error"}
        return {"ok": True, "data": r.json()}
    return _safe_api(call)

# ================== METADATA & AD FILTERING ==================
SKIP_K = {
    "metadata","meta","key_owner","key_usage","key_expiry","key_enabled",
    "daily_limit","daily_used","api_key","key","action","parameters","service",
    "success","violations","timestamp","response_time","response_time_ms",
    "developer","owner","credit","credits","powered_by","source","api","version",
    "status","message","code","time","created_at","updated_at","server","watermark",
    "signature","by","made_by","contact_admin","channel","group","join","advertisement",
    "ads","promo","query","req_id","request_id","execution_time","fizzagirl","nitin",
    "shree","jaani","types","spell","type"
}

def should_skip_key(k):
    if not k: return True
    kl = str(k).lower().strip().replace(" ", "_")
    if kl in SKIP_K: return True
    for w in ["metadata","timestamp","response_time","developer","credit","powered","watermark","pheevar","advertisement","promo","channel","server","api_","made_by","encrypted","password","salt","key_","daily_","auth","token","fizza"]:
        if w in kl: return True
    return False

def should_skip_val(v):
    if v is None or v == "": return True
    if isinstance(v, (dict, list)):
        return len(v) == 0
    vs = str(v).lower().strip()
    if vs in ("","none","null","n/a","na","-","0","0.00","0000-00-00","{}","[]"): return True
    for s in ["@pheevar", "pheevar", "@lk_", "t.me/", "telegram.me/", "rtfgamming", "dm for buy"]:
        if s in vs: return True
    return False

def clean_value_text(v):
    if not isinstance(v, str):
        return v
    patterns = [
        r"(?i)📌?\s*dm\s*for\s*buy\s*:\s*@rtfgamming",
        r"(?i)@rtfgamming",
        r"(?i)rtfgamming",
        r"(?i)📌?\s*dm\s*for\s*buy\s*:",
    ]
    vs = v
    for pat in patterns:
        vs = re.sub(pat, "", vs)
    vs = vs.strip().strip("|").strip("-").strip("•").strip("📌").strip()
    return vs

def em(k):
    k = str(k).lower()
    for kw, e in {"name":"👤","holder":"👤","email":"📧","phone":"📞","mobile":"📞","address":"📍","city":"🏙️","state":"🗺️","country":"🌍","pincode":"📮","upi":"💳","vpa":"💳","bank":"🏦","ifsc":"🏦","account":"🏦","dob":"🎂","gender":"🚻","pan":"🪪","aadhar":"🪪","aadhaar":"🪪","father":"👨","mother":"👩","vehicle":"🚗","rc":"🚗","owner":"👤","model":"🚗","maker":"🚗","fuel":"⛽","engine":"🔧","chassis":"🔧","registration":"📅","insurance":"📋","fitness":"📋","rto":"🏢","branch":"🏦","district":"🗺️","micr":"🔢","swift":"🔢","verified":"✅","valid":"✅","merchant":"🏪","class":"📋","color":"🎨","colour":"🎨","seating":"💺","standing":"🧍","wheel":"🛞","cylinder":"🔩","cubic":"📐","weight":"⚖️","unladen":"⚖️","norms":"🌿","emission":"🌿","financer":"💰","permit":"📄","tax":"💵","number":"🔢","plate":"🔢","type":"📋","category":"📋","body":"🚗","manufacturer":"🏭","manufacturing":"📅","purchase":"🛒","hypothecation":"🔗","blacklist":"⚠️","noc":"📄","challan":"🎫","status":"📊","ration":"🍚","card":"💳","family":"👨‍👩‍👧","member":"👥","head":"👤","relation":"🔗","age":"🎂","fps":"🏪","shop":"🏪","scheme":"📋","unit":"🔢","id":"🆔"}.items():
        if kw in k: return e
    return "📌"

def clean_metadata(data):
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if should_skip_key(k): continue
            cv = clean_metadata(v)
            if isinstance(cv, str):
                cv = clean_value_text(cv)
            if not should_skip_val(cv): cleaned[k] = cv
        return cleaned
    elif isinstance(data, list):
        cleaned_list = []
        for i in data:
            cv = clean_metadata(i)
            if isinstance(cv, str):
                cv = clean_value_text(cv)
            if not should_skip_val(cv):
                cleaned_list.append(cv)
        return cleaned_list
    return data

def format_universal_result(term, raw_data, icon="🔍"):
    cleaned = clean_metadata(raw_data)
    if not cleaned: return f"{icon} *Result for* `{term}`\n_No data found_"
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
    if not unique: return f"{icon} *Result for* `{term}`\n_No data found_"
    out = [f"{icon} *Result for* `{term}`", f"📊 *{len(unique)} record(s) found*", "━"*28]
    for idx, rec in enumerate(unique, 1):
        if len(unique) > 1: out.append(f"\n*━━ Record #{idx} ━━*")
        for k, v in rec.items():
            if isinstance(v, (dict, list)) or should_skip_key(k) or should_skip_val(v): continue
            emoji = em(k)
            label = str(k).replace("_"," ").replace("-"," ").title()
            
            # --- SMART VALUE FORMATTING SYSTEM ---
            k_lower = str(k).lower().strip()
            if isinstance(v, bool):
                if k_lower in ["valid", "verified", "active", "success"]:
                    vs = "Active ✅" if v else "Inactive/Invalid ❌"
                else:
                    vs = "Yes ✅" if v else "No ❌"
            elif str(v).lower() == "true":
                vs = "Active ✅" if k_lower in ["valid", "verified", "active", "success"] else "Yes ✅"
            elif str(v).lower() == "false":
                vs = "Inactive/Invalid ❌" if k_lower in ["valid", "verified", "active", "success"] else "No ❌"
            else:
                val_str = str(v).strip()
                # Preserves casing for Email, VPA, UPI, IFSC codes
                if "@" in val_str or k_lower in ["vpa", "upi", "email", "ifsc", "code"]:
                    vs = val_str
                else:
                    vs = val_str.title()
            
            out.append(f"{emoji} *{label}*: `{vs}`")
    return "\n".join(out)

# ================== KEYBOARDS ==================
def main_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Phone Tracker", callback_data="mode_phone"), InlineKeyboardButton("📧 Email OSINT", callback_data="mode_email")],
        [InlineKeyboardButton("💳 UPI Verifier", callback_data="mode_upi"), InlineKeyboardButton("🪪 Aadhaar Check", callback_data="mode_aadhaar")],
        [InlineKeyboardButton("🚗 Vehicle RC", callback_data="mode_vehicle"), InlineKeyboardButton("🏦 IFSC Finder", callback_data="mode_ifsc")],
        [InlineKeyboardButton("🚘 Vehicle Detailed Info", callback_data="mode_vinfo")],
        [InlineKeyboardButton("🎟️ Redeem Code", callback_data="redeem_info")],
        [InlineKeyboardButton("👤 My Profile", callback_data="profile"), InlineKeyboardButton("📊 API Status", callback_data="status")],
        [InlineKeyboardButton("📢 Channel 1", url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}"), InlineKeyboardButton("📢 Channel 2", url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton("💎 Purchase Premium 💎", callback_data="buy")],
        [InlineKeyboardButton("❓ Help Guide ❓", callback_data="help")],
    ])

def search_kb(uid, check_fn, free_fn, daily_fn, prefix, mx):
    if is_admin(uid): sl, bl = "🔍 Single (Admin)", "📦 Batch (Admin)"
    else:
        ok, _, _, ip, _ = check_fn(uid); fl = free_fn(uid); dr = daily_fn(uid)
        ud = get_user(uid); p = get_plan(ud)
        if ip:
            if p.get("unlimited"): sl, bl = "🟢 Single (Unlimited)", "📦 Batch (Unlimited)"
            else: sl, bl = f"🟢 Single ({dr} Today)", f"📦 Batch ({dr} Today)"
        elif fl > 0: sl, bl = f"🆓 Single ({fl} Free)", f"📦 Batch ({fl} Free)"
        else: sl, bl = "🔒 Single (Locked)", "🔒 Batch (Locked)"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(sl, callback_data=f"{prefix}_single")],
        [InlineKeyboardButton(bl, callback_data=f"{prefix}_batch")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def email_kb(uid):
    if is_admin(uid): sl, bl = "🔍 Single (Admin)", "📦 Batch (Admin)"
    else:
        ok, _, _, ip = email_check(uid); fl = email_free(uid)
        if ip: sl, bl = "🟢 Single (∞)", "📦 Batch (∞)"
        elif fl > 0: sl, bl = f"🆓 Single ({fl} Free)", f"📦 Batch ({fl} Free)"
        else: sl, bl = "🔒 Single (Locked)", "🔒 Batch (Locked)"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(sl, callback_data="email_single")],
        [InlineKeyboardButton(bl, callback_data="email_batch")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add User", callback_data="admin_add"), InlineKeyboardButton("❌ Remove User", callback_data="admin_remove")],
        [InlineKeyboardButton("📅 Set Plan", callback_data="admin_setplan"), InlineKeyboardButton("📋 All Users", callback_data="admin_list")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats"), InlineKeyboardButton("🆓 Monitor", callback_data="admin_free_monitor")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🎟️ Create Redeem Code", callback_data="admin_redeem_create")],
        [InlineKeyboardButton("📋 View All Codes", callback_data="admin_redeem_list")],
        [InlineKeyboardButton("🗑️ Delete Redeem Code", callback_data="admin_redeem_delete")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]])
def buy_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{OWNER_CONTACT.replace('@','')}")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])
def plan_kb(pf):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉 7 Days - ₹50", callback_data=f"{pf}_7days")],
        [InlineKeyboardButton("🥈 30 Days - ₹130", callback_data=f"{pf}_30days")],
        [InlineKeyboardButton("🥇 6 Months - ₹300", callback_data=f"{pf}_6months")],
        [InlineKeyboardButton("💎 12 Months - ₹799", callback_data=f"{pf}_12months")],
        [InlineKeyboardButton("⚙️ Custom Plan", callback_data=f"{pf}_custom")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_back")],
    ])
def monitor_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 Exhausted", callback_data="monitor_exhausted"), InlineKeyboardButton("🟢 Active", callback_data="monitor_active")],
        [InlineKeyboardButton("📊 Summary", callback_data="monitor_summary")],
        [InlineKeyboardButton("🔙 Admin Menu", callback_data="admin_back")],
    ])

# ================== START & VERIFICATION ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user; get_user(user.id); u_name = safe_name(user)
    if not is_admin(user.id):
        joined = await check_joined(context, user.id)
        if not joined:
            text = (f"━"*30+f"\n🔴  *Force Join Required*  🔴\n"+"━"*30+f"\n\nWelcome *{u_name}*!\n\n⚠️ Dono channels join karein:\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}\n\nVerify button dabayein 👇")
            if update.callback_query: await safe_edit(update.callback_query, text, force_join_kb())
            else: await safe_reply(update, text, force_join_kb())
            return ConversationHandler.END
    d1, d2 = "━"*30, "━"*25
    if is_admin(user.id):
        text = (f"{d1}\n⚡  *Ultimate Intelligence System*  ⚡\n{d1}\n\n👋 Welcome *{u_name}*! 🛡️ `Admin`\n\n{d2}\n📱 Phone  : 💎 Unlimited\n📧 Email  : 💎 Unlimited\n💳 UPI    : 💎 Unlimited\n🪪 Aadhaar: 💎 Unlimited\n🚗 Vehicle: 💎 Unlimited\n🏦 IFSC   : 💎 Unlimited\n🚘 V-Info : 💎 Unlimited\n{d2}\n\nSelect option below 👇")
    else:
        ud = get_user(user.id); plan = get_plan(ud)
        ip, exp = ud.get("is_premium", False), ud.get("expiry", "")
        lines = []
        for nm, ff, df, mx in [("📱 Phone",phone_free,phone_daily,PHONE_FREE),("📧 Email",email_free,lambda u:999999,EMAIL_FREE),("💳 UPI",upi_free,upi_daily,UPI_FREE),("🪪 Aadhaar",aadhaar_free,aadhaar_daily,AADHAAR_FREE),("🚗 Vehicle",vehicle_free,vehicle_daily,VEHICLE_FREE),("🏦 IFSC",ifsc_free,ifsc_daily,IFSC_FREE),("🚘 V-Info",vinfo_free,vinfo_daily,VINFO_FREE)]:
            fl = ff(user.id)
            if ip and exp:
                try:
                    ed = date.fromisoformat(exp); dl = (ed-date.today()).days
                    if dl >= 0:
                        if nm=="📧 Email" or plan.get("unlimited"): lines.append(f"🟢 {nm}: 💎 Unlimited ({dl}d)")
                        else: dr = df(user.id); lines.append(f"🟢 {nm}: 💎 {dr}/{plan.get('daily_limit',0)} ({dl}d)")
                    else: lines.append(f"🔴 {nm}: Expired ({fl}/{mx})")
                except: lines.append(f"⚪ {nm}: Unknown")
            else: lines.append(f"🆓 {nm}: {fl}/{mx} free")
        text = (f"{d1}\n⚡  *Ultimate Intelligence System*  ⚡\n{d1}\n\n👋 Welcome *{u_name}*!\n\n{d2}\n"+"\n".join(lines)+f"\n{d2}\n\n💡 *Ek plan = saare 7 features!*\n🎟️ *Free searches? Use* /redeem CODE\n\nSelect option 👇")
    if update.callback_query: await safe_edit(update.callback_query, text, main_kb(user.id))
    else: await safe_reply(update, text, main_kb(user.id))
    return ConversationHandler.END

async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; u = q.from_user
    joined = await check_joined(context, u.id)
    if joined:
        await q.answer("🎉 Verified!", show_alert=False)
        await start(update, context)
    else:
        await q.answer("❌ Dono channels join nahi kiye!", show_alert=True)
        text = (f"━"*30+f"\n⚠️  *Join Both Channels!*  ⚠️\n"+"━"*30+f"\n\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}\n\nVerify dabayein 👇")
        await safe_edit(q, text, force_join_kb())

# ================== MODES ==================
async def _mode(update, context, title, icon, chk, ff, df, mx, mkb):
    q = update.callback_query; await q.answer(); u = q.from_user
    if not is_admin(u.id) and not await check_joined(context, u.id):
        await safe_edit(q, f"⚠️ Dono channels join karein!\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return
    if is_admin(u.id): info = "🛡️ Admin"
    else:
        ok,_,_,ip,_ = chk(u.id); fl,dr = ff(u.id),df(u.id); p = get_plan(get_user(u.id))
        info = "💎 Unlimited" if ip and p.get("unlimited") else (f"🟢 {dr}/{p.get('daily_limit',0)} today" if ip else f"🆓 {fl}/{mx} free")
    await safe_edit(q, f"━"*30+f"\n{icon}  *{title}*  {icon}\n"+"━"*30+f"\n\n📊 Status: `{info}`\n\nChoose mode:", mkb(u.id))

async def mode_phone(u,c): await _mode(u,c,"Phone Search","📱",phone_check,phone_free,phone_daily,PHONE_FREE,lambda uid:search_kb(uid,phone_check,phone_free,phone_daily,"phone",PHONE_FREE))
async def mode_email(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user
    if not is_admin(u.id) and not await check_joined(context, u.id):
        await safe_edit(q, f"⚠️ Dono channels join karein!\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb()); return
    if is_admin(u.id): info = "🛡️ Admin"
    else:
        ok,_,d,ip = email_check(u.id); fl = email_free(u.id)
        info = f"💎 Premium ({d}d)" if ip else f"🆓 {fl}/{EMAIL_FREE} free"
    await safe_edit(q, f"━"*30+f"\n📧  *Email Search*  📧\n"+"━"*30+f"\n\n📊 Status: `{info}`\n\nChoose mode:", email_kb(u.id))
async def mode_upi(u,c): await _mode(u,c,"UPI Search","💳",upi_check,upi_free,upi_daily,UPI_FREE,lambda uid:search_kb(uid,upi_check,upi_free,upi_daily,"upi",UPI_FREE))
async def mode_aadhaar(u,c): await _mode(u,c,"Aadhaar Search","🪪",aadhaar_check,aadhaar_free,aadhaar_daily,AADHAAR_FREE,lambda uid:search_kb(uid,aadhaar_check,aadhaar_free,aadhaar_daily,"aadhaar",AADHAAR_FREE))
async def mode_vehicle(u,c): await _mode(u,c,"Vehicle RC","🚗",vehicle_check,vehicle_free,vehicle_daily,VEHICLE_FREE,lambda uid:search_kb(uid,vehicle_check,vehicle_free,vehicle_daily,"vehicle",VEHICLE_FREE))
async def mode_ifsc(u,c): await _mode(u,c,"IFSC Lookup","🏦",ifsc_check,ifsc_free,ifsc_daily,IFSC_FREE,lambda uid:search_kb(uid,ifsc_check,ifsc_free,ifsc_daily,"ifsc",IFSC_FREE))
async def mode_vinfo(u,c): await _mode(u,c,"Vehicle Info","🚘",vinfo_check,vinfo_free,vinfo_daily,VINFO_FREE,lambda uid:search_kb(uid,vinfo_check,vinfo_free,vinfo_daily,"vinfo",VINFO_FREE))

# ================== REDEEM CODE USER COMMAND ==================
async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args or len(context.args) == 0:
        await safe_reply(update, "🎟️ *Redeem Code System*\n\n📝 Usage: `/redeem YOUR_CODE`\n\nExample: `/redeem AB12CD`\n\n💡 Get redeem codes from admin or giveaways!", back_kb())
        return
    
    code = context.args[0].upper().strip()
    if len(code) < 3 or len(code) > 20:
        await safe_reply(update, "❌ Invalid code format!", back_kb())
        return
    
    success, message = use_redeem_code(code, user.id)
    await safe_reply(update, message, main_kb(user.id))

async def redeem_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    text = (
        f"━"*30+f"\n🎟️  *Redeem Code System*  🎟️\n"+"━"*30+"\n\n"
        "📝 *How to use:*\n"
        "Simply type: `/redeem YOUR_CODE`\n\n"
        "✅ Example: `/redeem AB12CD`\n\n"
        "💡 *Where to get codes?*\n"
        "🎁 Admin giveaways\n"
        "📢 Channel promotions\n"
        "🤝 Special events\n\n"
        "🎯 Each code gives you *extra free searches* on ALL 7 features!"
    )
    await safe_edit(q, text, back_kb())

# ================== PROFILE / STATUS / HELP / BUY ==================
async def profile(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user; ud = get_user(u.id)
    u_name = safe_name(u); ts = ud.get("total_searches", 0)
    redeemed = ud.get("redeemed_codes", [])
    redeem_text = f"\n🎟️ Codes Redeemed: `{len(redeemed)}`" if redeemed else "\n🎟️ Codes Redeemed: `0`"
    t = (f"━"*30+f"\n👤  *Profile: {u_name}*\n"+"━"*30+
         f"\n\n🆔 `{u.id}`\n\n"
         f"📱 Phone: `{ud.get('phone_total',0)}`\n"
         f"📧 Email: `{ud.get('email_total',0)}`\n"
         f"💳 UPI: `{ud.get('upi_total',0)}`\n"
         f"🪪 Aadhaar: `{ud.get('aadhaar_total',0)}`\n"
         f"🚗 Vehicle: `{ud.get('vehicle_total',0)}`\n"
         f"🏦 IFSC: `{ud.get('ifsc_total',0)}`\n"
         f"🚘 V-Info: `{ud.get('vinfo_total',0)}`\n\n"
         f"🔍 Total: `{ts}`"
         f"{redeem_text}")
    await safe_edit(q, t, back_kb())

async def status_check(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user
    if is_admin(u.id): await safe_edit(q, "🛡️ *Admin* — All Unlimited", back_kb()); return
    lines = []
    for nm,chk,ff,df,mx in [("📱 Phone",phone_check,phone_free,phone_daily,PHONE_FREE),("💳 UPI",upi_check,upi_free,upi_daily,UPI_FREE),("🪪 Aadhaar",aadhaar_check,aadhaar_free,aadhaar_daily,AADHAAR_FREE),("🚗 Vehicle",vehicle_check,vehicle_free,vehicle_daily,VEHICLE_FREE),("🏦 IFSC",ifsc_check,ifsc_free,ifsc_daily,IFSC_FREE),("🚘 V-Info",vinfo_check,vinfo_free,vinfo_daily,VINFO_FREE)]:
        ok,st,_,ip,_ = chk(u.id)
        if ip: p=get_plan(get_user(u.id)); dr=df(u.id); lim=p.get("daily_limit",0); lines.append(f"{nm}: {'💎 ∞' if p.get('unlimited') else f'💎 {dr}/{lim}'}")
        else: lines.append(f"{nm}: 🆓 {ff(u.id)}/{mx}")
    ok,st,_,ip = email_check(u.id)
    lines.append(f"📧 Email: {'💎 ∞' if ip else f'🆓 {email_free(u.id)}/{EMAIL_FREE}'}")
    await safe_edit(q, f"📊 *Status*\n\n"+"\n".join(lines)+f"\n\n💰 {OWNER_CONTACT}\nID: `{u.id}`", back_kb())

async def help_menu(update, context):
    q = update.callback_query; await q.answer()
    t = (f"━"*30+f"\n❓  *Help Guide*  ❓\n"+"━"*30+"\n\n"
        "🎯 *1 Plan = 7 Features!*\n\n"
        "💎 *Plans:*\n🥉 7D-₹50 | 🥈 30D-₹130 | 🥇 6M-₹300 | 💎 12M-₹799\n\n"
        "💡 *Formats:*\n📱 Phone: Type direct numeric number\n💳 UPI: `user@bank`\n🪪 Aadhaar: 12 digits\n🚗 RC: `MH01AB1234`\n🏦 IFSC: `SBIN0001234`\n🚘 V-Info: `UP32AB1234`\n📦 Batch: Comma sep, Max 15\n\n"
        "🎟️ *Redeem Code:*\n`/redeem YOUR_CODE` for free searches!")
    await safe_edit(q, t, back_kb())

async def buy(update, context):
    q = update.callback_query; await q.answer(); u = q.from_user
    if is_admin(u.id): await safe_edit(q, "🛡️ Admin!", back_kb()); return
    t = (f"━"*30+f"\n💰  *Buy Plan*  💰\n"+"━"*30+"\n\n"
        "🥉 *7 Days* - ₹50 (5/day)\n🥈 *30 Days* - ₹130 (10/day)\n🥇 *6 Months* - ₹300 (15/day)\n💎 *12 Months* - ₹799 (∞)\n\n"
        f"📱 {OWNER_CONTACT}\nID: `{u.id}`")
    await safe_edit(q, t, buy_kb())

# ================== SEARCH EXECUTION ==================
async def _do_single(update, context, api_fn, term, display, icon, use_fn, chk):
    u = update.effective_user; r = chk(u.id); ok = r[0]; st = r[1]
    if not ok: await safe_reply(update, f"🔒 *Locked!*\n{st}\n\n🎟️ Use `/redeem CODE` for free searches!\n💰 {OWNER_CONTACT}", buy_kb()); return
    msg = await safe_reply(update, f"🔍 Searching `{display}`...")
    res = api_fn(term)
    if res["ok"]:
        use_fn(u.id); text = format_universal_result(display, res["data"], icon)
        if msg: await safe_edit(msg, text, main_kb(u.id))
        else: await safe_reply(update, text, main_kb(u.id))
    else:
        err = f"❌ *Failed*\n{res['error']}"
        if msg: await safe_edit(msg, err, back_kb())
        else: await safe_reply(update, err, back_kb())

async def _do_batch(update, context, api_fn, items, icon, use_fn, chk):
    u = update.effective_user; total = len(items)
    msg = await safe_reply(update, f"🚀 Processing {total} items...")
    for item in items:
        res = api_fn(item)
        if res["ok"]: use_fn(u.id); await safe_reply(update, format_universal_result(item, res["data"], icon))
        else: await safe_reply(update, f"❌ *{item}*\n{res['error']}")
    if msg: await safe_edit(msg, f"✅ *Done!* Processed: {total}", main_kb(u.id))

# ================== SEARCH HANDLERS ==================
async def phone_single_s2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(context, q.from_user.id):
        await safe_edit(q, f"⚠️ Join channels!\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb())
        return ConversationHandler.END
    ok, st, _, _, _ = phone_check(q.from_user.id)
    if not ok:
        await safe_edit(q, f"🔒 {st}\n🎟️ `/redeem CODE`\n💰 {OWNER_CONTACT}", buy_kb())
        return ConversationHandler.END
    await safe_edit(q, "📱 Enter phone number to track (eg: 9729535354):\n/cancel")
    return PHONE_SINGLE

async def phone_batch_s2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(context, q.from_user.id):
        await safe_edit(q, f"⚠️ Join channels!", force_join_kb())
        return ConversationHandler.END
    ok, st, _, _, _ = phone_check(q.from_user.id)
    if not ok:
        await safe_edit(q, f"🔒 {st}", buy_kb())
        return ConversationHandler.END
    await safe_edit(q, "📦 Enter phone numbers separated by commas (Max 15):\n/cancel")
    return PHONE_BATCH

async def phone_single_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cl = update.message.text.strip().replace(" ", "").replace("-", "").replace("+", "")
    if not cl.isdigit() or not (5 <= len(cl) <= 15):
        await safe_reply(update, "❌ Invalid phone format! Input must be 5 to 15 digits without spaces or signs.\n/cancel")
        return PHONE_SINGLE

    await _do_single(update, context, phone_api, cl, cl, "📱", phone_use, phone_check)
    return ConversationHandler.END

async def phone_batch_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_nums = [n.strip().replace(" ", "").replace("-", "").replace("+", "") for n in update.message.text.split(",") if n.strip()]
    valid = [n for n in raw_nums if n.isdigit() and (5 <= len(n) <= 15)]
    if not valid:
        await safe_reply(update, "❌ No valid phone numbers found! Please enter numeric numbers between 5 and 15 digits.\n/cancel")
        return PHONE_BATCH
    await _do_batch(update, context, phone_api, valid[:15], "📱", phone_use, phone_check)
    return ConversationHandler.END

async def email_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,f"⚠️ Join channels!",force_join_kb());return ConversationHandler.END
    ok,st,_,_=email_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"📧 Email daalo:\n/cancel");return EMAIL_SINGLE

async def email_sp(update,context):
    e=update.message.text.strip()
    if not valid_email(e):await safe_reply(update,"❌ Invalid!\n/cancel");return EMAIL_SINGLE
    await _do_single(update,context,search_api,e,e,"📧",lambda uid:email_use(uid,email_check(uid)[3]),lambda uid:(*email_check(uid),None));return ConversationHandler.END

async def email_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,f"⚠️ Join channels!",force_join_kb());return ConversationHandler.END
    ok,st,_,_=email_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"📦 Emails comma se (Max 15):\n/cancel");return EMAIL_BATCH

async def email_bp(update,context):
    emails=[e.strip() for e in update.message.text.split(",") if valid_email(e.strip())][:15]
    if not emails:await safe_reply(update,"❌ No valid!\n/cancel");return EMAIL_BATCH
    await _do_batch(update,context,search_api,emails,"📧",lambda uid:email_use(uid,email_check(uid)[3]),lambda uid:(*email_check(uid),None));return ConversationHandler.END

async def upi_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,f"⚠️ Join channels!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=upi_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"💳 UPI ID daalo (eg: example@okaxis / 9876543210@ybl):\n/cancel");return UPI_SINGLE

async def upi_sp(update,context):
    uid=update.message.text.strip()
    if not valid_upi(uid):await safe_reply(update,"❌ Format: id@bank\n/cancel");return UPI_SINGLE
    await _do_single(update,context,upi_api,uid,uid,"💳",upi_use,upi_check);return ConversationHandler.END

async def upi_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,f"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=upi_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"📦 UPIs comma se (Max 15):\n/cancel");return UPI_BATCH

async def upi_bp(update,context):
    upis=[u.strip() for u in update.message.text.split(",") if valid_upi(u.strip())][:15]
    if not upis:await safe_reply(update,"❌ No valid!\n/cancel");return UPI_BATCH
    await _do_batch(update,context,upi_api,upis,"💳",upi_use,upi_check);return ConversationHandler.END

async def aadh_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,"⚠️ Join channels!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=aadhaar_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"🪪 12 digit Aadhaar number daalo:\n/cancel");return AADHAAR_SINGLE

async def aadh_sp(update,context):
    a=update.message.text.strip().replace(" ","").replace("-","")
    if not valid_aadhaar(a):await safe_reply(update,"❌ 12 digits chahiye!\n/cancel");return AADHAAR_SINGLE
    await _do_single(update,context,aadhaar_api,a,a,"🪪",aadhaar_use,aadhaar_check);return ConversationHandler.END

async def aadh_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=aadhaar_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"📦 Aadhaars comma se (Max 15):\n/cancel");return AADHAAR_BATCH

async def aadh_bp(update,context):
    nums=[a.strip().replace(" ","").replace("-","") for a in update.message.text.split(",") if valid_aadhaar(a.strip().replace(" ","").replace("-",""))][:15]
    if not nums:await safe_reply(update,"❌ No valid!\n/cancel");return AADHAAR_BATCH
    await _do_batch(update,context,aadhaar_api,nums,"🪪",aadhaar_use,aadhaar_check);return ConversationHandler.END

async def veh_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=vehicle_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"🚗 Vehicle number:\n/cancel");return VEHICLE_SINGLE

async def veh_sp(update,context):
    rc=update.message.text.strip().upper().replace(" ","").replace("-","")
    if len(rc)<4:await safe_reply(update,"❌ Invalid!\n/cancel");return VEHICLE_SINGLE
    await _do_single(update,context,vehicle_api,rc,rc,"🚗",vehicle_use,vehicle_check);return ConversationHandler.END

async def veh_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=vehicle_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"📦 RCs comma se (Max 15):\n/cancel");return VEHICLE_BATCH

async def veh_bp(update,context):
    rcs=[r.strip().upper().replace(" ","").replace("-","") for r in update.message.text.split(",") if len(r.strip())>=4][:15]
    if not rcs:await safe_reply(update,"❌ No valid!\n/cancel");return VEHICLE_BATCH
    await _do_batch(update,context,vehicle_api,rcs,"🚗",vehicle_use,vehicle_check);return ConversationHandler.END

async def ifsc_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=ifsc_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"🏦 IFSC Code:\n/cancel");return IFSC_SINGLE

async def ifsc_sp(update,context):
    code=update.message.text.strip().upper().replace(" ","")
    if not valid_ifsc(code):await safe_reply(update,"❌ 11 char IFSC!\n/cancel");return IFSC_SINGLE
    await _do_single(update,context,ifsc_api,code,code,"🏦",ifsc_use,ifsc_check);return ConversationHandler.END

async def ifsc_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=ifsc_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"📦 IFSCs comma se (Max 15):\n/cancel");return IFSC_BATCH

async def ifsc_bp(update,context):
    codes=[c.strip().upper().replace(" ","") for c in update.message.text.split(",") if valid_ifsc(c.strip().upper().replace(" ",""))][:15]
    if not codes:await safe_reply(update,"❌ No valid!\n/cancel");return IFSC_BATCH
    await _do_batch(update,context,ifsc_api,codes,"🏦",ifsc_use,ifsc_check);return ConversationHandler.END

async def vinfo_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=vinfo_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"🚘 Vehicle number:\n/cancel");return VINFO_SINGLE

async def vinfo_sp(update,context):
    vn=update.message.text.strip().upper().replace(" ","").replace("-","")
    if not valid_vehicle_number(vn):await safe_reply(update,"❌ Invalid!\n/cancel");return VINFO_SINGLE
    await _do_single(update,context,vinfo_api,vn,vn,"🚘",vinfo_use,vinfo_check);return ConversationHandler.END

async def vinfo_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id):
        await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=vinfo_check(q.from_user.id)
    if not ok:await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,"📦 Vehicles comma se (Max 15):\n/cancel");return VINFO_BATCH

async def vinfo_bp(update,context):
    vehicles=[v.strip().upper().replace(" ","").replace("-","") for v in update.message.text.split(",") if valid_vehicle_number(v.strip().upper().replace(" ","").replace("-",""))][:15]
    if not vehicles:await safe_reply(update,"❌ No valid!\n/cancel");return VINFO_BATCH
    await _do_batch(update,context,vinfo_api,vehicles,"🚘",vinfo_use,vinfo_check);return ConversationHandler.END

async def cancel(u,c):
    c.user_data.clear()
    await safe_reply(u,"❌ Cancelled.",main_kb(u.effective_user.id))
    return ConversationHandler.END

# ================== ADMIN REDEEM CODE HANDLERS ==================
async def admin_redeem_create_start(update, context):
    q = update.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer()
    await safe_edit(q, "🎟️ *Create Redeem Code*\n\n📝 Enter your custom code (3-20 chars, letters+numbers):\n\nExample: `AB12CD`, `FREE50`, `GIFT2025`\n\n/cancel to abort")
    return REDEEM_CREATE_CODE

async def admin_redeem_code_input(update, context):
    code = update.message.text.strip().upper()
    if len(code) < 3 or len(code) > 20:
        await safe_reply(update, "❌ Code must be 3-20 characters!\n/cancel")
        return REDEEM_CREATE_CODE
    if not code.isalnum():
        await safe_reply(update, "❌ Only letters and numbers allowed!\n/cancel")
        return REDEEM_CREATE_CODE
    if code in REDEEM_CODES:
        await safe_reply(update, f"❌ Code `{code}` already exists!\nChoose different code.\n/cancel")
        return REDEEM_CREATE_CODE
    
    context.user_data["new_redeem_code"] = code
    await safe_reply(update, f"Base Code: `{code}`\n\n🎁 Kitne *free searches* dene hain per user?\n(Number daalo, eg: 5, 10, 20)\n\n/cancel to abort")
    return REDEEM_CREATE_SEARCHES

async def admin_redeem_searches_input(update, context):
    text = update.message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await safe_reply(update, "❌ Positive number daalo!\n/cancel")
        return REDEEM_CREATE_SEARCHES
    
    searches = int(text)
    context.user_data["new_redeem_searches"] = searches
    await safe_reply(update, f"✅ Free Searches: `{searches}` per user\n\n👥 Maximum kitne users is code ko redeem kar sakte hain?\n(Number daalo, eg: 10, 50, 100)\n\n/cancel to abort")
    return REDEEM_CREATE_LIMIT

async def admin_redeem_limit_input(update, context):
    text = update.message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await safe_reply(update, "❌ Positive number daalo!\n/cancel")
        return REDEEM_CREATE_LIMIT
    
    max_uses = int(text)
    code = context.user_data.get("new_redeem_code")
    searches = context.user_data.get("new_redeem_searches")
    
    create_redeem_code(code, searches, max_uses)
    
    await safe_reply(update, 
        f"━"*30+f"\n🎟️  *Redeem Code Created!*  🎟️\n"+"━"*30+"\n\n"
        f"🔑 Code: `{code}`\n"
        f"🎁 Free Searches: `{searches}` per user\n"
        f"👥 Max Redemptions: `{max_uses}` users\n"
        f"📅 Created: `{date.today()}`\n\n"
        f"💡 Users ko batayein: `/redeem {code}`",
        admin_kb()
    )
    
    context.user_data.pop("new_redeem_code", None)
    context.user_data.pop("new_redeem_searches", None)
    return ConversationHandler.END

async def admin_redeem_list(update, context):
    q = update.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer()
    
    codes = list_redeem_codes()
    if not codes:
        await safe_edit(q, "📋 No redeem codes exist yet!\n\nCreate one from Admin Panel.", admin_kb())
        return
    
    txt = f"━"*30+f"\n🎟️  *All Redeem Codes*  🎟️\n"+"━"*30+"\n\n"
    for code, info in codes.items():
        active = "🟢 Active" if info.get("active", True) and info["used_count"] < info["max_uses"] else "🔴 Exhausted"
        txt += (
            f"🔑 `{code}` | {active}\n"
            f"   🎁 {info['free_searches']} searches | 👥 {info['used_count']}/{info['max_uses']} used\n\n"
        )
    
    await safe_edit(q, txt[:4000], admin_kb())

async def admin_redeem_delete_start(update, context):
    q = update.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer()
    
    codes = list_redeem_codes()
    if not codes:
        await safe_edit(q, "📋 No codes to delete!", admin_kb())
        return ConversationHandler.END
    
    txt = "🗑️ *Delete Redeem Code*\n\nExisting codes:\n"
    for code in codes:
        txt += f"• `{code}`\n"
    txt += "\nCode name type karo jo delete karna hai:\n/cancel to abort"
    
    await safe_edit(q, txt)
    return REDEEM_DELETE_CODE

async def admin_redeem_delete_input(update, context):
    code = update.message.text.strip().upper()
    
    if delete_redeem_code(code):
        await safe_reply(update, f"✅ Code `{code}` successfully deleted!", admin_kb())
    else:
        await safe_reply(update, f"❌ Code `{code}` not found!\n/cancel", admin_kb())
    
    return ConversationHandler.END

# ================== ADMIN ACTIONS ==================
async def admin_panel(update, context):
    if not is_admin(update.effective_user.id):
        await safe_reply(update, "❌ Admin only!"); return ConversationHandler.END
    users = load_users(); t = len(users); p = sum(1 for v in users.values() if v.get("is_premium"))
    codes_count = len(list_redeem_codes())
    txt = f"━"*30+f"\n🛠️  *Admin Panel*  🛠️\n"+"━"*30+f"\n\n🛡️ Admins: `{len(ADMIN_IDS)}`\n👥 Users: `{t}`\n💎 Premium: `{p}`\n🆓 Free: `{t-p}`\n🎟️ Redeem Codes: `{codes_count}`\n\nChoose action:"
    if update.callback_query: await safe_edit(update.callback_query, txt, admin_kb())
    else: await safe_reply(update, txt, admin_kb())
    return ConversationHandler.END

async def admin_back(u,c): await admin_panel(u,c)

async def adm_add_s(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id):return ConversationHandler.END
    await q.answer();await safe_edit(q,"➕ User ID daalo:\n/cancel");return ADMIN_ADD_ID

async def adm_add_id(u,c):
    uid=u.message.text.strip()
    if not uid.isdigit():await safe_reply(u,"❌ Invalid!\n/cancel");return ADMIN_ADD_ID
    c.user_data["admin_uid"]=uid;await safe_reply(u,f"User: `{uid}`\nPlan select:",plan_kb("plan"));return ADMIN_ADD_PLAN

async def adm_add_plan(u,c):
    q=u.callback_query;await q.answer()
    if q.data=="admin_back":await admin_panel(u,c);return ConversationHandler.END
    pm={"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk=pm.get(q.data,"7days");uid=c.user_data.get("admin_uid");plan=PLANS.get(pk)
    exp=upgrade(int(uid),pk);dl="∞" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(q,f"✅ *Added!*\n🆔 `{uid}`\n📦 {plan['name']}\n📅 {exp}\n📱 {dl}",admin_kb());return ConversationHandler.END

async def adm_rem_s(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id):return ConversationHandler.END
    await q.answer();await safe_edit(q,"❌ User ID daalo:\n/cancel");return ADMIN_REM_ID

async def adm_rem_p(u,c):
    uid=u.message.text.strip();delete_user(uid)
    await safe_reply(u,f"✅ `{uid}` removed!",admin_kb());return ConversationHandler.END

async def adm_sp_s(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id):return ConversationHandler.END
    await q.answer();await safe_edit(q,"📅 User ID:\n/cancel");return ADMIN_EXP_ID

async def adm_sp_id(u,c):
    uid=u.message.text.strip();c.user_data["admin_uid"]=uid
    await safe_reply(u,f"User: `{uid}`\nPlan:",plan_kb("plan"));return ADMIN_EXP_PLAN

async def adm_sp_set(u,c):
    q=u.callback_query;await q.answer()
    if q.data=="admin_back":await admin_panel(u,c);return ConversationHandler.END
    pm={"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk=pm.get(q.data,"7days");uid=c.user_data.get("admin_uid");plan=PLANS.get(pk)
    exp=upgrade(int(uid),pk);dl="∞" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(q,f"✅ *Updated!*\n🆔 `{uid}`\n📦 {plan['name']}\n📅 {exp}\n📱 {dl}",admin_kb());return ConversationHandler.END

async def adm_list(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id):return
    await q.answer();users=load_users()
    if not users:await safe_edit(q,"📋 No users!",admin_kb());return
    txt=f"📋 *Users ({len(users)})*\n\n"
    for uid,info in users.items():
        plan=get_plan(info);ts=info.get("total_searches",0)
        if int(uid) in ADMIN_IDS:st="🛡️ Admin"
        elif info.get("is_premium") and info.get("expiry"):
            try:
                ed=date.fromisoformat(info["expiry"]);st=f"💎 {plan['name']} ({(ed-date.today()).days}d)" if date.today()<=ed else "🔴 Expired"
            except:st="⚪ N/A"
        else:st="🆓 Free"
        txt+=f"`{uid}` | {st} | 🔍 {ts}\n"
    await safe_edit(q,txt[:4000],admin_kb())

async def adm_stats(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id):return
    await q.answer();users=load_users();ts=sum(v.get("total_searches",0) for v in users.values())
    act=sum(1 for u2,v in users.items() if v.get("is_premium") and int(u2) not in ADMIN_IDS)
    await safe_edit(q,f"📊 *Stats*\n\n👥 Users: `{len(users)}`\n🔍 Searches: `{ts}`\n💎 Premium: `{act}`\n🎟️ Codes: `{len(list_redeem_codes())}`\n📅 {date.today()}",admin_kb())

async def adm_monitor(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id):return
    await q.answer()
    users=load_users();free=[v for u2,v in users.items() if not v.get("is_premium") and int(u2) not in ADMIN_IDS]
    await safe_edit(q,f"🆓 *Monitor*\n\n👥 Free: `{len(free)}`\n\nFilter:",monitor_kb())

async def mon_exhausted(u,c):
    q=u.callback_query;await q.answer();users=load_users();txt="🔴 *Exhausted*\n\n";cnt=0
    all_keys=[("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE),("vinfo_free_used",VINFO_FREE)]
    for uid,info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"):continue
        if all(max(0,mx-info.get(k,0))<=0 for k,mx in all_keys):
            txt+=f"🔴 `{uid}` | 🔍 {info.get('total_searches',0)}\n";cnt+=1
    txt+=f"\n💡 *{cnt}* potential buyers!"
    await safe_edit(q,txt[:4000],monitor_kb())

async def mon_active(u,c):
    q=u.callback_query;await q.answer();users=load_users();txt="🟢 *Active*\n\n";cnt=0
    all_keys=[("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE),("vinfo_free_used",VINFO_FREE)]
    for uid,info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"):continue
        if any(max(0,mx-info.get(k,0))>0 for k,mx in all_keys):
            txt+=f"🟢 `{uid}`\n";cnt+=1
    txt+=f"\nActive: {cnt}"
    await safe_edit(q,txt[:4000],monitor_kb())

async def mon_summary(u,c):
    q=u.callback_query;await q.answer();users=load_users();t=0;ex=0
    all_keys=[("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE),("vinfo_free_used",VINFO_FREE)]
    for uid,info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"):continue
        t+=1
        if all(max(0,mx-info.get(k,0))<=0 for k,mx in all_keys):ex+=1
    await safe_edit(q,f"📊 *Summary*\n\n👥 Free: `{t}`\n🔴 Exhausted: `{ex}`\n📅 {date.today()}",monitor_kb())

async def bc_start(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id):return ConversationHandler.END
    await q.answer();await safe_edit(q,f"📢 *Broadcast*\n\n👥 Recipients: *{len(load_users())}*\n\nMessage likho:\n/cancel");return ADMIN_BROADCAST_MSG

async def bc_msg(u,c):
    m=u.message.text.strip()
    if not m:await safe_reply(u,"❌ Empty!\n/cancel");return ADMIN_BROADCAST_MSG
    c.user_data["bc"]=m
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Send!",callback_data="broadcast_confirm")],[InlineKeyboardButton("❌ Cancel",callback_data="broadcast_cancel")]])
    await safe_reply(u,f"📢 *Preview:*\n\n{m}\n\n👥 {len(load_users())} users\nSure?",kb);return ADMIN_BROADCAST_CONFIRM

async def bc_confirm(u,c):
    q=u.callback_query;await q.answer()
    if q.data=="broadcast_cancel":
        await safe_edit(q,"❌ Cancelled!",admin_kb());c.user_data.pop("bc",None);return ConversationHandler.END
    msg=c.user_data.get("bc","");users=load_users();total=len(users)
    bt=f"📢 *Announcement*\n{'━'*25}\n\n{msg}\n\n{'━'*25}\n💬 {OWNER_CONTACT}"
    sm=await safe_reply(u,f"🚀 Broadcasting to {total}...")
    s,f2,b,ct=0,0,0,0
    for uid in users:
        ct+=1
        try:await c.bot.send_message(chat_id=int(uid),text=bt,parse_mode="Markdown");s+=1
        except Exception as e:
            if any(w in str(e).lower() for w in ["blocked","forbidden","not found"]):b+=1
            else:f2+=1
        if ct%10==0 or ct==total:
            try:await sm.edit_text(f"🚀 {ct}/{total}\n✅ {s} | 🚫 {b} | ❌ {f2}",parse_mode="Markdown")
            except:pass
    await safe_reply(u,f"✅ *Done!*\n👥 {total} | ✅ {s} | 🚫 {b} | ❌ {f2}",admin_kb())
    c.user_data.pop("bc",None);return ConversationHandler.END

async def custom_s(u,c):
    q=u.callback_query;await q.answer()
    await safe_edit(q,"⚙️ *Custom Plan*\n\nKitne din?\n/cancel");return ADMIN_CUSTOM_DAYS

async def custom_days(u,c):
    t=u.message.text.strip()
    if not t.isdigit() or int(t)<=0:await safe_reply(u,"❌ Valid days!\n/cancel");return ADMIN_CUSTOM_DAYS
    c.user_data["cd"]=int(t);await safe_reply(u,f"📅 Days: *{t}*\n\nDaily Limit? (0=∞)\n/cancel");return ADMIN_CUSTOM_LIMIT

async def custom_limit(u,c):
    t=u.message.text.strip()
    if not t.isdigit():await safe_reply(u,"❌ Number!\n/cancel");return ADMIN_CUSTOM_LIMIT
    lim=int(t);unl=(lim==0);days=c.user_data.get("cd");uid=c.user_data.get("admin_uid")
    exp=upgrade_custom(int(uid),days,lim,unl);ls="∞" if unl else f"{lim}/day"
    await safe_reply(u,f"⚙️ *Custom Set!*\n🆔 `{uid}`\n📅 {days}D | {exp}\n📱 {ls}",admin_kb())
    c.user_data.pop("cd",None);c.user_data.pop("admin_uid",None);return ConversationHandler.END

async def main_menu_cb(u,c): await start(u,c); return ConversationHandler.END

async def error_handler(update,context):
    logger.error(f"❌ {context.error}")

# ================== MAIN ==================
def main():
    threading.Thread(target=start_webserver, daemon=True).start()
    print("🌐 Keep-alive started!")

    req = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30, pool_timeout=30)
    gur = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30, pool_timeout=30)
    app = ApplicationBuilder().token(BOT_TOKEN).request(req).get_updates_request(gur).build()

    C=ConversationHandler; CQ=CallbackQueryHandler; MH=MessageHandler; CMD=CommandHandler
    F=filters.TEXT & ~filters.COMMAND
    UF=[CMD("cancel",cancel),CMD("start",start)]

    convs = [
        C(entry_points=[CQ(phone_single_s2,pattern="^phone_single$")],states={PHONE_SINGLE:[MH(F,phone_single_process)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(phone_batch_s2,pattern="^phone_batch$")],states={PHONE_BATCH:[MH(F,phone_batch_process)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(email_ss,pattern="^email_single$")],states={EMAIL_SINGLE:[MH(F,email_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(email_bs,pattern="^email_batch$")],states={EMAIL_BATCH:[MH(F,email_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(upi_ss,pattern="^upi_single$")],states={UPI_SINGLE:[MH(F,upi_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(upi_bs,pattern="^upi_batch$")],states={UPI_BATCH:[MH(F,upi_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(aadh_ss,pattern="^aadhaar_single$")],states={AADHAAR_SINGLE:[MH(F,aadh_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(aadh_bs,pattern="^aadhaar_batch$")],states={AADHAAR_BATCH:[MH(F,aadh_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(veh_ss,pattern="^vehicle_single$")],states={VEHICLE_SINGLE:[MH(F,veh_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(veh_bs,pattern="^vehicle_batch$")],states={VEHICLE_BATCH:[MH(F,veh_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(ifsc_ss,pattern="^ifsc_single$")],states={IFSC_SINGLE:[MH(F,ifsc_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(ifsc_bs,pattern="^ifsc_batch$")],states={IFSC_BATCH:[MH(F,ifsc_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(vinfo_ss,pattern="^vinfo_single$")],states={VINFO_SINGLE:[MH(F,vinfo_sp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(vinfo_bs,pattern="^vinfo_batch$")],states={VINFO_BATCH:[MH(F,vinfo_bp)]},fallbacks=UF,per_message=False,allow_reentry=True),
        # Admin Redeem Code Conversations
        C(entry_points=[CQ(admin_redeem_create_start,pattern="^admin_redeem_create$")],states={REDEEM_CREATE_CODE:[MH(F,admin_redeem_code_input)],REDEEM_CREATE_SEARCHES:[MH(F,admin_redeem_searches_input)],REDEEM_CREATE_LIMIT:[MH(F,admin_redeem_limit_input)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(admin_redeem_delete_start,pattern="^admin_redeem_delete$")],states={REDEEM_DELETE_CODE:[MH(F,admin_redeem_delete_input)]},fallbacks=UF,per_message=False,allow_reentry=True),
        # Other Admin Conversations
        C(entry_points=[CQ(adm_add_s,pattern="^admin_add$")],states={ADMIN_ADD_ID:[MH(F,adm_add_id)],ADMIN_ADD_PLAN:[CQ(custom_s,pattern="^plan_custom$"),CQ(adm_add_plan,pattern="^plan_")],ADMIN_CUSTOM_DAYS:[MH(F,custom_days)],ADMIN_CUSTOM_LIMIT:[MH(F,custom_limit)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_rem_s,pattern="^admin_remove$")],states={ADMIN_REM_ID:[MH(F,adm_rem_p)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_sp_s,pattern="^admin_setplan$")],states={ADMIN_EXP_ID:[MH(F,adm_sp_id)],ADMIN_EXP_PLAN:[CQ(custom_s,pattern="^plan_custom$"),CQ(adm_sp_set,pattern="^plan_")],ADMIN_CUSTOM_DAYS:[MH(F,custom_days)],ADMIN_CUSTOM_LIMIT:[MH(F,custom_limit)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(bc_start,pattern="^admin_broadcast$")],states={ADMIN_BROADCAST_MSG:[MH(F,bc_msg)],ADMIN_BROADCAST_CONFIRM:[CQ(bc_confirm,pattern="^broadcast_(confirm|cancel)$")]},fallbacks=UF,per_message=False,allow_reentry=True),
    ]
    for cv in convs: app.add_handler(cv)

    app.add_handler(CMD("start", start))
    app.add_handler(CMD("admin", admin_panel))
    app.add_handler(CMD("redeem", redeem_command))
    app.add_error_handler(error_handler)

    for p, f2 in [
        ("mode_phone",mode_phone),("mode_email",mode_email),
        ("mode_upi",mode_upi),("mode_aadhaar",mode_aadhaar),
        ("mode_vehicle",mode_vehicle),("mode_ifsc",mode_ifsc),
        ("mode_vinfo",mode_vinfo),("redeem_info",redeem_info),
        ("profile",profile),("status",status_check),
        ("help",help_menu),("buy",buy),
        ("admin_list",adm_list),("admin_stats",adm_stats),
        ("admin_back",admin_back),("admin_free_monitor",adm_monitor),
        ("admin_redeem_list",admin_redeem_list),
        ("monitor_exhausted",mon_exhausted),("monitor_active",mon_active),
        ("monitor_summary",mon_summary),("main_menu",main_menu_cb),
        ("verify_join",verify_join),
    ]:
        app.add_handler(CQ(f2, pattern=f"^{p}$"))

    print("🤖 Bot Running! Watermarks filtered successfully.")
    app.run_polling(drop_pending_updates=True, allowed_updates=["message","callback_query"])

if __name__ == "__main__":
    main()

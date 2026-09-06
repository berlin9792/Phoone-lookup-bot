#!/usr/bin/env python3
"""
🔍 Ultimate Intelligence Bot - ZERO TRACE (FULL MERGED ENGINE - FIXED)
Primary All-in-One Engine: alonepatel API
Backup Engine: Old Individual API Endpoints
Dual Force Join + Blood ASCII Banner + Animated Loader + Redeem Code + MongoDB Cloud + 24/7 Keep Alive
"""

import json, os, threading, requests, logging, asyncio, re, time, html, secrets
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from flask import Flask
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)
from telegram.request import HTTPXRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== ⚙️ CONFIG ==================
BOT_TOKEN     = os.environ.get("BOT_TOKEN", "8642873626:AAFy5F79opcK_NMJ7NgGItd6sRrfbOc4TJU")
ADMIN_IDS     = [5057489358, 1968142314]
OWNER_CONTACT = "@theplayerror"

# ── Primary All-In-One API (ZEROTRACEC Engine) ──
PRIMARY_API_URL = "https://api-src.alonepatel.shop/api"
PRIMARY_API_KEY = "INDIAN_HACKER_BRO"

# ── Old APIs Kept as Backup (Easily switchable) ──
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

# ── Force Join Channels (Dual) ──
FORCE_JOIN_CHANNEL_1    = "@hackkwr"
FORCE_JOIN_CHANNEL_1_ID = "@hackkwr"
FORCE_JOIN_CHANNEL_2    = "@zerotracelegit"
FORCE_JOIN_CHANNEL_2_ID = "@zerotracelegit"

# ── MongoDB & Headers ──
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://httplegitfs_db_user:Q8uGZxERXsrf2VV1@cluster0.iojnad7.mongodb.net/?retryWrites=true&w=majority")
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://api-src.alonepatel.shop/",
}

# ================== 🎁 FREE LIMITS ==================
FREE_LIMIT = 2

# ================== 💎 SUBSCRIPTION PLANS ==================
PLANS = {
    "trial": {"name": "Trial", "days": 0, "price": 0, "daily_limit": 0, "unlimited": False, "is_free": True},
    "7days": {"name": "7 Days", "days": 7, "price": 50, "daily_limit": 10, "unlimited": False, "is_free": False},
    "30days": {"name": "30 Days", "days": 30, "price": 130, "daily_limit": 20, "unlimited": False, "is_free": False},
    "6months": {"name": "6 Months", "days": 180, "price": 300, "daily_limit": 35, "unlimited": False, "is_free": False},
    "12months": {"name": "12 Months", "days": 365, "price": 799, "daily_limit": 999999, "unlimited": True, "is_free": False},
}

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

# ================== 🩸 BLOOD ASCII BANNERS ==================
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
    if not msg:
        return None
    try:
        return await msg.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"safe_reply HTML failed: {e}. Retrying plain text...")
        clean = re.sub(r"</?(?:b|i|code|pre|u|s)>", "", text)
        clean = html.unescape(clean)
        try:
            return await msg.reply_text(clean[:4096], reply_markup=reply_markup)
        except Exception as e2:
            logger.error(f"safe_reply fallback error: {e2}")
            return None

async def safe_edit(target, text: str, reply_markup=None):
    try:
        if hasattr(target, "edit_message_text"):
            return await target.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
        elif hasattr(target, "edit_text"):
            return await target.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"safe_edit HTML failed: {e}. Retrying plain text...")
        clean = re.sub(r"</?(?:b|i|code|pre|u|s)>", "", text)
        clean = html.unescape(clean)
        try:
            if hasattr(target, "edit_message_text"):
                return await target.edit_message_text(clean[:4096], reply_markup=reply_markup)
            elif hasattr(target, "edit_text"):
                return await target.edit_text(clean[:4096], reply_markup=reply_markup)
        except Exception as e2:
            logger.error(f"safe_edit fallback error: {e2}")
            return None

def is_admin(uid): 
    return int(uid) in ADMIN_IDS

def safe_name(user):
    name = user.first_name or "User"
    return html.escape(name)

# ================== 🎨 ANIMATED LOADING BAR ==================
LOADING_STEPS = [
    ("🔴", "Initializing Scan...", "░░░░░░░░░░░░░░░░░░░░"),
    ("🟡", "Scanning Database...", "█████░░░░░░░░░░░░░░░"),
    ("🔵", "Fetching Records...", "██████████░░░░░░░░░░"),
    ("🟣", "Decoding Info...", "███████████████░░░░░"),
    ("🟢", "Finalizing...", "████████████████████"),
    ("⚡", "Complete!", "████████████████████")
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
    if not msg:
        return
    percents = [10, 30, 55, 75, 95, 100]
    for i, (se, st, bar) in enumerate(LOADING_STEPS):
        pct = percents[i] if i < len(percents) else 100
        txt = build_loading_text(icon, display, se, st, bar, pct)
        try:
            await msg.edit_text(txt, parse_mode="HTML")
        except Exception:
            pass
        if i < len(LOADING_STEPS) - 1:
            await asyncio.sleep(0.4)

# ================== 🌐 FLASK KEEP-ALIVE ==================
web_app = Flask(__name__)
@web_app.route('/')
def keep_alive_status(): return "Bot Running 24/7!", 200

def start_webserver():
    import logging as lg
    lg.getLogger('werkzeug').setLevel(lg.ERROR)
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================== 🔒 DUAL FORCE JOIN ==================
async def check_joined(context, uid):
    if is_admin(uid): return True
    try:
        m1 = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL_1_ID, uid)
        if m1.status not in ["member", "administrator", "creator", "restricted"]:
            return False
        m2 = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL_2_ID, uid)
        return m2.status in ["member", "administrator", "creator", "restricted"]
    except Exception as e:
        logger.warning(f"Channel join check notice (User {uid}): {e}")
        # Agar bot admin nahi hai channel me toh user ko block na kare
        return True

def force_join_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel 1 ↗️", url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}")],
        [InlineKeyboardButton("📢 Join Channel 2 ↗️", url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton("✅ Verify Both ✅", callback_data="verify_join")],
    ])

# ================== 💾 MONGODB + LOCAL CACHE ==================
USERS_CACHE = {}
REDEEM_CODES = {}
LOCAL_FILE = Path("users.json")
REDEEM_FILE = Path("redeem_codes.json")

try:
    mc = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2500)
    db = mc["tele_intel_bot"]
    users_col = db["users"]
    redeem_col = db["redeem_codes"]
    mc.admin.command('ping')
    print("✅ MongoDB Connected!")
except Exception as e:
    print("⚠️ MongoDB Connection Warning:", e)
    users_col = None
    redeem_col = None

ALL_FEATURE_KEYS = [
    "phone", "email", "upi", "aadhaar", "vehicle", "ifsc",
    "tg", "insta", "imei", "pin", "country", "paytm", "ip", "weather"
]

DEFAULTS = {
    "plan": "trial", "expiry": "", "is_premium": False,
    "total_searches": 0, "redeemed_codes": []
}
for feat in ALL_FEATURE_KEYS:
    DEFAULTS[f"{feat}_free_used"] = 0
    DEFAULTS[f"{feat}_daily"] = 0
    DEFAULTS[f"{feat}_date"] = ""
    DEFAULTS[f"{feat}_total"] = 0

def init_cache():
    global USERS_CACHE, REDEEM_CODES
    if users_col is not None:
        try:
            for doc in users_col.find():
                USERS_CACHE[str(doc["_id"])] = {k: v for k, v in doc.items() if k != "_id"}
        except Exception:
            pass
    elif LOCAL_FILE.exists():
        try: USERS_CACHE = json.loads(LOCAL_FILE.read_text())
        except Exception: USERS_CACHE = {}

    if redeem_col is not None:
        try:
            for doc in redeem_col.find():
                REDEEM_CODES[str(doc["_id"])] = {k: v for k, v in doc.items() if k != "_id"}
        except Exception:
            pass
    elif REDEEM_FILE.exists():
        try: REDEEM_CODES = json.loads(REDEEM_FILE.read_text())
        except Exception: REDEEM_CODES = {}

init_cache()

def sync_user_background(uid, data):
    def _s():
        if users_col is not None:
            try:
                users_col.update_one({"_id": str(uid)}, {"$set": data}, upsert=True)
                return
            except Exception:
                pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE, indent=2))
        except Exception: pass
    threading.Thread(target=_s, daemon=True).start()

def sync_redeem_background(code, data):
    def _s():
        if redeem_col is not None:
            try:
                redeem_col.update_one({"_id": code}, {"$set": data}, upsert=True)
                return
            except Exception:
                pass
        try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES, indent=2))
        except Exception: pass
    threading.Thread(target=_s, daemon=True).start()

def delete_redeem_background(code):
    def _d():
        if redeem_col is not None:
            try:
                redeem_col.delete_one({"_id": code})
            except Exception:
                pass
        try:
            REDEEM_FILE.write_text(json.dumps(REDEEM_CODES, indent=2))
        except Exception:
            pass
    threading.Thread(target=_d, daemon=True).start()

def get_user(uid):
    uid = str(uid)
    if uid not in USERS_CACHE:
        d = {**DEFAULTS, "added": date.today().isoformat()}
        USERS_CACHE[uid] = d
        sync_user_background(uid, d)
    else:
        d = USERS_CACHE[uid]
        updated = False
        for k, v in DEFAULTS.items():
            if k not in d:
                d[k] = v
                updated = True
        if updated:
            sync_user_background(uid, d)
    return USERS_CACHE[uid]

def save_user(uid, data):
    uid = str(uid)
    USERS_CACHE[uid] = data
    sync_user_background(uid, data)

def delete_user(uid):
    uid = str(uid)
    if uid in USERS_CACHE:
        del USERS_CACHE[uid]
    def _d():
        if users_col is not None:
            try: users_col.delete_one({"_id": uid})
            except Exception: pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE, indent=2))
        except Exception: pass
    threading.Thread(target=_d, daemon=True).start()

def load_users(): return USERS_CACHE

# ================== 🎟️ REDEEM CODE SYSTEM ==================
def create_redeem_code(code, fs, mu):
    code = code.upper().strip()
    REDEEM_CODES[code] = {
        "free_searches": fs, "max_uses": mu, "used_count": 0,
        "used_by": [], "created_at": date.today().isoformat(), "active": True
    }
    sync_redeem_background(code, REDEEM_CODES[code])
    return True

def use_redeem_code(code, user_id):
    code = code.upper().strip()
    user_id = str(user_id)
    if code not in REDEEM_CODES: return False, "❌ Invalid promo code!"
    rc = REDEEM_CODES[code]
    if not rc.get("active", True): return False, "❌ Promo code is deactivated!"
    if rc["used_count"] >= rc["max_uses"]: return False, "❌ Max user redemptions reached!"
    if user_id in rc.get("used_by", []): return False, "❌ You have already redeemed this code!"
    
    ud = get_user(user_id)
    s = rc["free_searches"]
    for feat in ALL_FEATURE_KEYS:
        k = f"{feat}_free_used"
        ud[k] = max(0, ud.get(k, 0) - s)
    
    if "redeemed_codes" not in ud: ud["redeemed_codes"] = []
    ud["redeemed_codes"].append(code)
    save_user(user_id, ud)
    
    rc["used_count"] += 1
    rc["used_by"].append(user_id)
    REDEEM_CODES[code] = rc
    sync_redeem_background(code, rc)
    return True, f"🎉 <code>{code}</code> redeemed successfully!\n🎁 <b>+{s} Extra Searches</b> added to ALL tools!\n📊 Uses: <code>{rc['used_count']}/{rc['max_uses']}</code>"

def delete_redeem_code(code):
    code = code.upper().strip()
    if code in REDEEM_CODES:
        del REDEEM_CODES[code]
        delete_redeem_background(code)
        return True
    return False

def list_redeem_codes(): return REDEEM_CODES

# ================== 👑 PLAN RESOLVERS ==================
def get_plan(ud):
    pk = ud.get("plan", "trial")
    if pk.startswith("custom_"):
        try: d = int(pk.split("_")[1].replace("d", ""))
        except Exception: d = 30
        return {
            "name": f"Custom ({d}D)", "days": d,
            "daily_limit": ud.get("custom_limit", 0),
            "unlimited": ud.get("custom_unlimited", False),
            "is_free": False
        }
    return PLANS.get(pk, PLANS["trial"])

def upgrade(uid, pk):
    uid = str(uid)
    ud = get_user(uid)
    plan = PLANS.get(pk, PLANS["7days"])
    exp = (date.today() + timedelta(days=plan["days"])).isoformat()
    ud.update({"plan": pk, "expiry": exp, "is_premium": True})
    for feat in ALL_FEATURE_KEYS:
        ud[f"{feat}_daily"] = 0
        ud[f"{feat}_date"] = ""
    save_user(uid, ud)
    return exp

def upgrade_custom(uid, days, lim, unl):
    uid = str(uid)
    ud = get_user(uid)
    exp = (date.today() + timedelta(days=days)).isoformat()
    ud.update({
        "plan": f"custom_{days}d", "expiry": exp, "is_premium": True,
        "custom_limit": lim, "custom_unlimited": unl
    })
    for feat in ALL_FEATURE_KEYS:
        ud[f"{feat}_daily"] = 0
        ud[f"{feat}_date"] = ""
    save_user(uid, ud)
    return exp

# ================== 📊 LIMIT CHECKERS ==================
def check_feat_access(uid, feat_name, display_title):
    if is_admin(uid): return True, "Admin ∞", 9999, True, "12months"
    ud = get_user(uid)
    plan = get_plan(ud)
    pk = ud.get("plan", "trial")
    exp_s = ud.get("expiry", "")
    is_p = ud.get("is_premium", False)
    
    fk = f"{feat_name}_free_used"
    dk = f"{feat_name}_daily"
    dtk = f"{feat_name}_date"
    
    if is_p and exp_s:
        try:
            exp = date.fromisoformat(exp_s)
            if date.today() > exp:
                fl = max(0, FREE_LIMIT - ud.get(fk, 0))
                return (True, f"Expired | {fl} Free", 0, False, "trial") if fl > 0 else (False, "Plan Expired!", 0, False, "trial")
            dl = (exp - date.today()).days
            lim = plan.get("daily_limit", 0)
            if plan.get("unlimited"): return True, f"{plan['name']} | ∞ | {dl}d", dl, True, pk
            
            dr = lim if ud.get(dtk, "") != date.today().isoformat() else max(0, lim - ud.get(dk, 0))
            if dr <= 0: return False, f"Daily limit over! ({lim}/day)", dl, True, pk
            return True, f"{plan['name']} | {dr}/{lim} | {dl}d", dl, True, pk
        except Exception:
            pass

    fl = max(0, FREE_LIMIT - ud.get(fk, 0))
    return (True, f"Free ({fl}/{FREE_LIMIT})", 0, False, "trial") if fl > 0 else (False, "Trial limits exhausted!", 0, False, "trial")

def feat_free_rem(uid, feat_name):
    if is_admin(uid): return 999999
    return max(0, FREE_LIMIT - get_user(uid).get(f"{feat_name}_free_used", 0))

def feat_daily_rem(uid, feat_name):
    if is_admin(uid): return 999999
    ud = get_user(uid)
    plan = get_plan(ud)
    if plan.get("unlimited"): return 999999
    lim = plan.get("daily_limit", 0)
    if ud.get(f"{feat_name}_date", "") != date.today().isoformat(): return lim
    return max(0, lim - ud.get(f"{feat_name}_daily", 0))

def use_feature(uid, feat_name):
    uid = str(uid)
    ud = get_user(uid)
    today = date.today().isoformat()
    dk = f"{feat_name}_daily"
    dtk = f"{feat_name}_date"
    fk = f"{feat_name}_free_used"
    tk = f"{feat_name}_total"
    
    if ud.get(dtk, "") != today:
        ud[dk] = 0
        ud[dtk] = today
    plan = get_plan(ud)
    if not is_admin(int(uid)):
        if plan.get("is_free", True):
            ud[fk] = ud.get(fk, 0) + 1
        else:
            ud[dk] = ud.get(dk, 0) + 1
    ud[tk] = ud.get(tk, 0) + 1
    ud["total_searches"] = ud.get("total_searches", 0) + 1
    save_user(uid, ud)

# ================== 📡 API ENGINE ==================
def _safe_api(fn):
    try: return fn()
    except requests.exceptions.Timeout: return {"ok": False, "error": "⏱️ Timed out! API took too long."}
    except requests.exceptions.ConnectionError: return {"ok": False, "error": "🌐 Connection error! Server unreachable."}
    except requests.exceptions.HTTPError as e: return {"ok": False, "error": f"⚠️ HTTP {e.response.status_code if e.response else 'Error'}"}
    except Exception as e:
        logger.error(f"API Error: {e}", exc_info=True)
        return {"ok": False, "error": f"❌ {e}"}

def primary_api_call(action: str, params: dict):
    def c():
        r = requests.get(
            PRIMARY_API_URL,
            params={"key": PRIMARY_API_KEY, "action": action, **params},
            headers=COMMON_HEADERS,
            timeout=25
        )
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code}"}
        try:
            data = r.json()
        except Exception:
            return {"ok": False, "error": "Invalid response format from API."}
        if isinstance(data, dict) and (data.get("status") in [False, "error", 400, 404] or data.get("success") is False):
            return {"ok": False, "error": str(data.get("message") or data.get("error") or "No records found.")}
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

# ================== 🧹 METADATA FILTER & FORMATTERS ==================
SKIP_K = {
    "metadata", "meta", "key_owner", "key_usage", "key_expiry", "key_enabled",
    "daily_limit", "daily_used", "api_key", "key", "action", "parameters", "service",
    "success", "violations", "timestamp", "response_time", "response_time_ms",
    "developer", "owner", "credit", "credits", "powered_by", "source", "api",
    "version", "status", "message", "code", "time", "created_at", "updated_at",
    "server", "watermark", "signature", "by", "made_by", "contact_admin", "channel",
    "group", "join", "advertisement", "ads", "promo", "query", "req_id", "request_id",
    "execution_time", "fizzagirl", "nitin", "shree", "jaani", "types", "spell", "type"
}

def should_skip_key(k):
    if not k: return True
    kl = str(k).lower().strip().replace(" ", "_")
    if kl in SKIP_K: return True
    for w in ["metadata", "timestamp", "response_time", "developer", "credit", "powered", "watermark", "pheevar", "advertisement", "promo", "channel", "server", "api_", "made_by", "encrypted", "password", "salt", "key_", "daily_", "auth", "token", "fizza"]:
        if w in kl: return True
    return False

def should_skip_val(v):
    if v is None or v == "": return True
    if isinstance(v, (dict, list)): return len(v) == 0
    vs = str(v).lower().strip()
    if vs in ("", "none", "null", "n/a", "na", "-", "0", "0.00", "0000-00-00", "{}", "[]"): return True
    for s in ["@pheevar", "pheevar", "@lk_", "t.me/", "telegram.me/", "rtfgamming", "dm for buy"]:
        if s in vs: return True
    return False

def clean_value_text(v):
    if not isinstance(v, str): return v
    for pat in [r"(?i)📌?\s*dm\s*for\s*buy\s*:\s*@rtfgamming", r"(?i)@rtfgamming", r"(?i)rtfgamming", r"(?i)📌?\s*dm\s*for\s*buy\s*:"]:
        v = re.sub(pat, "", v)
    return v.strip().strip("|").strip("-").strip("•").strip("📌").strip()

def em(k):
    k = str(k).lower()
    for kw, e in {
        "name": "👤", "holder": "👤", "email": "📧", "phone": "📞", "mobile": "📞",
        "address": "📍", "city": "🏙️", "state": "🗺️", "country": "🌍", "pincode": "📮",
        "upi": "💳", "vpa": "💳", "bank": "🏦", "ifsc": "🏦", "account": "🏦", "dob": "🎂",
        "gender": "🚻", "pan": "🪪", "aadhar": "🪪", "aadhaar": "🪪", "father": "👨",
        "mother": "👩", "vehicle": "🚗", "rc": "🚗", "owner": "👤", "model": "🚗",
        "fuel": "⛽", "engine": "🔧", "chassis": "🔧", "registration": "📅", "insurance": "📋",
        "fitness": "📋", "rto": "🏢", "branch": "🏦", "district": "🗺️", "micr": "🔢",
        "swift": "🔢", "verified": "✅", "valid": "✅", "merchant": "🏪", "class": "📋",
        "color": "🎨", "colour": "🎨", "seating": "💺", "wheel": "🛞", "cylinder": "🔩",
        "weight": "⚖️", "norms": "🌿", "financer": "💰", "permit": "📄", "tax": "💵",
        "number": "🔢", "plate": "🔢", "type": "📋", "category": "📋", "body": "🚗",
        "manufacturer": "🏭", "manufacturing": "📅", "purchase": "🛒", "hypothecation": "🔗",
        "blacklist": "⚠️", "noc": "📄", "challan": "🎫", "status": "📊", "ration": "🍚",
        "card": "💳", "family": "👨‍👩‍👧", "member": "👥", "head": "👤", "relation": "🔗",
        "age": "🎂", "fps": "🏪", "shop": "🏪", "scheme": "📋", "unit": "🔢", "id": "🆔",
        "username": "👤", "user_id": "🆔", "followers": "👥", "following": "👥",
        "bio": "📝", "ip": "🌐", "isp": "🏢", "weather": "🌤️", "temp": "🌡️",
        "humidity": "💧", "wind": "💨", "imei": "📱", "device": "📱"
    }.items():
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
        return [
            cv for i in data
            if not should_skip_val((cv := clean_value_text(clean_metadata(i)) if isinstance(clean_metadata(i), str) else clean_metadata(i)))
        ]
    return data

def format_universal_result(term, raw_data, icon="🔍"):
    cleaned = clean_metadata(raw_data)
    if not cleaned:
        return f"<code>{BANNER_MINI}</code>\n\n{icon} <b>Result for:</b> <code>{html.escape(str(term))}</code>\n\n<i>No records found in database.</i>"
    
    records = []
    def extract(item):
        if isinstance(item, dict):
            if any(not isinstance(v, (dict, list)) for v in item.values()):
                records.append(item)
            for v in item.values():
                if isinstance(v, (dict, list)): extract(v)
        elif isinstance(item, list):
            for s in item: extract(s)
            
    extract(cleaned)
    unique = []
    seen = set()
    for r in records:
        fp = "-".join(sorted(f"{k}:{v}" for k, v in r.items() if not isinstance(v, (dict, list))))
        if fp and fp not in seen:
            seen.add(fp)
            unique.append(r)
            
    if not unique:
        return f"<code>{BANNER_MINI}</code>\n\n{icon} <b>Result for:</b> <code>{html.escape(str(term))}</code>\n\n<i>No records found.</i>"
        
    out = [f"<code>{BANNER_MINI}</code>", f"\n{icon} <b>Search Result:</b> <code>{html.escape(str(term))}</code>", f"📊 <b>{len(unique)} record(s) found</b>", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]
    for idx, rec in enumerate(unique, 1):
        if len(unique) > 1:
            out.append(f"\n<b>━━ Record #{idx} ━━</b>")
        for k, v in rec.items():
            if isinstance(v, (dict, list)) or should_skip_key(k) or should_skip_val(v): continue
            emoji = em(k)
            label = str(k).replace("_", " ").replace("-", " ").title()
            kl = str(k).lower().strip()
            
            if isinstance(v, bool):
                vs = ("Active ✅" if v else "Inactive ❌") if kl in ["valid", "verified", "active", "success"] else ("Yes ✅" if v else "No ❌")
            elif str(v).lower() == "true":
                vs = "Active ✅" if kl in ["valid", "verified", "active", "success"] else "Yes ✅"
            elif str(v).lower() == "false":
                vs = "Inactive ❌" if kl in ["valid", "verified", "active", "success"] else "No ❌"
            else:
                val_str = str(v).strip()
                vs = val_str if ("@" in val_str or kl in ["vpa", "upi", "email", "ifsc", "code", "userid", "ip"]) else val_str.title()
            out.append(f"{emoji} <b>{html.escape(label)}:</b> <code>{html.escape(vs)}</code>")
            
    return "\n".join(out)

# ================== 🕹️ KEYBOARDS ==================
def main_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Phone Tracker", callback_data="mode_phone"), InlineKeyboardButton("🪪 Aadhaar Lookup", callback_data="mode_aadhaar")],
        [InlineKeyboardButton("💳 UPI Verification", callback_data="mode_upi"), InlineKeyboardButton("📧 Email OSINT", callback_data="mode_email")],
        [InlineKeyboardButton("🚗 Vehicle RC (V1-V4)", callback_data="mode_vehicle"), InlineKeyboardButton("🏦 Bank IFSC", callback_data="mode_ifsc")],
        [InlineKeyboardButton("👤 Telegram Info", callback_data="mode_tg"), InlineKeyboardButton("📸 Instagram OSINT", callback_data="mode_insta")],
        [InlineKeyboardButton("📱 IMEI Tracker", callback_data="mode_imei"), InlineKeyboardButton("📮 Postal Pincode", callback_data="mode_pin")],
        [InlineKeyboardButton("🌍 Country Info", callback_data="mode_country"), InlineKeyboardButton("💰 Paytm Info", callback_data="mode_paytm")],
        [InlineKeyboardButton("🌐 IP Lookup", callback_data="mode_ip"), InlineKeyboardButton("🌤️ Weather Forecast", callback_data="mode_weather")],
        [InlineKeyboardButton("🎟️ Redeem Code", callback_data="redeem_info"), InlineKeyboardButton("👤 My Profile", callback_data="profile")],
        [InlineKeyboardButton("📊 Bot Status", callback_data="status"), InlineKeyboardButton("💎 Upgrade Premium", callback_data="buy")],
        [InlineKeyboardButton("📢 Channel 1", url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}"), InlineKeyboardButton("📢 Channel 2", url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton("❓ Help Guide ❓", callback_data="help")]
    ])

def search_sub_kb(uid, feat_name):
    if is_admin(uid):
        sl, bl = "🔍 Single Search (Admin)", "📦 Batch Search (Admin)"
    else:
        ok, _, _, ip, _ = check_feat_access(uid, feat_name, feat_name.title())
        fl = feat_free_rem(uid, feat_name)
        dr = feat_daily_rem(uid, feat_name)
        p = get_plan(get_user(uid))
        if ip:
            sl, bl = ("🟢 Single (∞)", "📦 Batch (∞)") if p.get("unlimited") else (f"🟢 Single ({dr} Left)", f"📦 Batch ({dr} Left)")
        elif fl > 0:
            sl, bl = f"🆓 Single ({fl} Left)", f"📦 Batch ({fl} Left)"
        else:
            sl, bl = "🔒 Limit Over (Locked)", "🔒 Limit Over (Locked)"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(sl, callback_data=f"{feat_name}_single")],
        [InlineKeyboardButton(bl, callback_data=f"{feat_name}_batch")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add User Plan", callback_data="admin_add"), InlineKeyboardButton("❌ Remove User", callback_data="admin_remove")],
        [InlineKeyboardButton("📅 Change Plan", callback_data="admin_setplan"), InlineKeyboardButton("📋 Users List", callback_data="admin_list")],
        [InlineKeyboardButton("📊 System Stats", callback_data="admin_stats"), InlineKeyboardButton("🆓 Usage Monitor", callback_data="admin_free_monitor")],
        [InlineKeyboardButton("📢 Broadcast Msg", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🎟️ Create Promo", callback_data="admin_redeem_create"), InlineKeyboardButton("📋 Promo Codes", callback_data="admin_redeem_list")],
        [InlineKeyboardButton("🗑️ Delete Promo", callback_data="admin_redeem_delete")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ])

def back_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]])
def buy_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("💬 Contact Owner / Buy", url=f"https://t.me/{OWNER_CONTACT.replace('@','')}")], [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
def plan_kb(pf):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉 7 Days - ₹50", callback_data=f"{pf}_7days")],
        [InlineKeyboardButton("🥈 30 Days - ₹130", callback_data=f"{pf}_30days")],
        [InlineKeyboardButton("🥇 6 Months - ₹300", callback_data=f"{pf}_6months")],
        [InlineKeyboardButton("💎 12 Months - ₹799", callback_data=f"{pf}_12months")],
        [InlineKeyboardButton("⚙️ Custom Plan", callback_data=f"{pf}_custom")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_back")]
    ])

# ================== 🚀 START / MENU ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return ConversationHandler.END
    get_user(user.id)
    u_name = safe_name(user)
    
    if not is_admin(user.id):
        if not await check_joined(context, user.id):
            t = (
                f"<code>{BANNER}</code>\n\n"
                f"🔴 <b>Force Join Required</b>\n\n"
                f"Welcome <b>{u_name}</b>!\n\n"
                f"⚠️ Join our dual channels to access:\n"
                f"📢 {FORCE_JOIN_CHANNEL_1}\n"
                f"📢 {FORCE_JOIN_CHANNEL_2}\n\n"
                f"Click below to verify 👇"
            )
            if update.callback_query:
                await safe_edit(update.callback_query, t, force_join_kb())
            else:
                await safe_reply(update, t, force_join_kb())
            return ConversationHandler.END

    if is_admin(user.id):
        t = (
            f"<code>{BANNER}</code>\n\n"
            f"👋 Welcome Boss <b>{u_name}</b>! 🛡️ <code>ADMIN ACCESS</code>\n\n"
            f"All tools active with unlimited access (💎 ∞).\n\n"
            f"👇 <b>Select an Intelligence tool:</b>"
        )
    else:
        ud = get_user(user.id)
        plan = get_plan(ud)
        ip = ud.get("is_premium", False)
        exp = ud.get("expiry", "")
        
        status_lines = []
        for feat in ALL_FEATURE_KEYS[:8]:
            fl = feat_free_rem(user.id, feat)
            if ip and exp:
                try:
                    ed = date.fromisoformat(exp)
                    dl = (ed - date.today()).days
                    if dl >= 0:
                        if plan.get("unlimited"):
                            status_lines.append(f"🟢 {feat.title()}: <code>💎 ∞ ({dl}d)</code>")
                        else:
                            dr = feat_daily_rem(user.id, feat)
                            status_lines.append(f"🟢 {feat.title()}: <code>💎 {dr}/{plan.get('daily_limit',0)} ({dl}d)</code>")
                    else:
                        status_lines.append(f"🔴 {feat.title()}: <code>Expired ({fl}/{FREE_LIMIT})</code>")
                except Exception:
                    status_lines.append(f"⚪ {feat.title()}: <code>Unknown</code>")
            else:
                status_lines.append(f"🆓 {feat.title()}: <code>{fl}/{FREE_LIMIT} Free</code>")
                
        t = (
            f"<code>{BANNER}</code>\n\n"
            f"👋 Hello <b>{u_name}</b>!\n\n"
            + "\n".join(status_lines)
            + f"\n\n💡 <b>1 Plan unlocks all 14+ tools!</b>\n"
            f"🎟️ Redeem code: <code>/redeem CODE</code>\n\n"
            f"👇 <b>Select an OSINT module:</b>"
        )
        
    if update.callback_query:
        await safe_edit(update.callback_query, t, main_kb(user.id))
    else:
        await safe_reply(update, t, main_kb(user.id))
    return ConversationHandler.END

async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("Verifying membership...")
    u = q.from_user
    if await check_joined(context, u.id):
        await start(update, context)
    else:
        await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n⚠️ <b>Join both channels to continue!</b>\n\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}", force_join_kb())

async def main_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    if update.callback_query:
        await update.callback_query.answer()
    await start(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await safe_reply(update, "❌ Operation cancelled.", main_kb(update.effective_user.id))
    return ConversationHandler.END

# ================== 🛠️ SEARCH EXECUTION ==================
async def execute_search(update, context, feat_name, action, param_key, search_value, icon, display_value):
    u = update.effective_user
    ok, st, _, _, _ = check_feat_access(u.id, feat_name, feat_name.title())
    if not ok:
        await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n🔒 <b>Access Restricted!</b>\n{st}\n\n🎟️ <code>/redeem CODE</code>\n💎 Contact {OWNER_CONTACT} for Premium.", buy_kb())
        return

    msg = await safe_reply(update, "⏳ <i>Initializing Engine...</i>")
    
    api_task = asyncio.get_event_loop().run_in_executor(
        None,
        lambda: primary_api_call(action, {param_key: search_value})
    )
    anim_task = animated_search(msg, icon, display_value)
    res, _ = await asyncio.gather(api_task, anim_task)
    
    if not res["ok"] and feat_name == "email":
        res = await asyncio.get_event_loop().run_in_executor(None, lambda: backup_search_worker_api(search_value))
    elif not res["ok"] and feat_name == "phone":
        res = await asyncio.get_event_loop().run_in_executor(None, lambda: backup_phone_api(search_value))

    if res["ok"]:
        use_feature(u.id, feat_name)
        text = format_universal_result(display_value, res["data"], icon)
        final_text = f"⚡ <b>Intelligence Report Generated!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{text}"
        if msg: await safe_edit(msg, final_text, main_kb(u.id))
        else: await safe_reply(update, final_text, main_kb(u.id))
    else:
        err = f"<code>{BANNER_MINI}</code>\n\n🔴 <b>Query Failed!</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n❌ Term: <code>{html.escape(str(display_value))}</code>\n📛 Error: {html.escape(str(res['error']))}\n\n💡 <i>Please check the input and try again.</i>"
        if msg: await safe_edit(msg, err, back_kb())
        else: await safe_reply(update, err, back_kb())

async def execute_batch(update, context, feat_name, action, param_key, items, icon):
    u = update.effective_user
    total = len(items)
    msg = await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n📦 <b>Batch Processing Initiated</b>\n🚀 Items: <b>{total}</b>\n\n<code>[░░░░░░░░░░░░░░░░░░░░]</code> 0%")
    
    for idx, item in enumerate(items, 1):
        pct = int((idx / total) * 100)
        filled = int(pct / 5)
        bar = "█" * filled + "░" * (20 - filled)
        try:
            await msg.edit_text(f"<code>{BANNER_MINI}</code>\n\n📦 <b>Batch Processing:</b>\n🔍 <code>{html.escape(str(item))}</code>\n📊 Progress: <b>{idx}/{total}</b>\n\n<code>[{bar}]</code> <b>{pct}%</b>", parse_mode="HTML")
        except Exception:
            pass
            
        res = primary_api_call(action, {param_key: item})
        if res["ok"]:
            use_feature(u.id, feat_name)
            await safe_reply(update, format_universal_result(item, res["data"], icon))
        else:
            await safe_reply(update, f"❌ <code>{html.escape(str(item))}</code>: {html.escape(str(res['error']))}")
        await asyncio.sleep(0.3)
        
    if msg:
        await safe_edit(msg, f"<code>{BANNER_MINI}</code>\n\n⚡ <b>Batch Processing Complete!</b>\n✅ Total: <b>{total}</b> items\n<code>[████████████████████]</code> <b>100%</b>", main_kb(u.id))

# ================== 📱 MODE PROMPTERS ==================
async def generic_mode_prompt(update, context, feat_name, display_title, icon):
    q = update.callback_query
    await q.answer()
    u = q.from_user
    if not is_admin(u.id) and not await check_joined(context, u.id):
        await safe_edit(q, "⚠️ Join required!", force_join_kb())
        return
    await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n{icon} <b>{display_title} OSINT</b> {icon}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nChoose search type:", search_sub_kb(u.id, feat_name))

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
async def mode_weather(u, c): await generic_mode_prompt(u, c, "weather", "Weather Forecast", "🌤️")

# ================== 📥 SEARCH HANDLERS ==================
def make_handler_pair(feat_name, action, param_key, icon, single_state, batch_state, prompt_single, prompt_batch, validator_fn=None):
    async def single_start(update, context):
        q = update.callback_query; await q.answer()
        ok, st, _, _, _ = check_feat_access(q.from_user.id, feat_name, feat_name.title())
        if not ok:
            await safe_edit(q, f"🔒 {st}", buy_kb())
            return ConversationHandler.END
        await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n{icon} <b>{prompt_single}</b>\n\nSend input or type /cancel:")
        return single_state

    async def batch_start(update, context):
        q = update.callback_query; await q.answer()
        ok, st, _, _, _ = check_feat_access(q.from_user.id, feat_name, feat_name.title())
        if not ok:
            await safe_edit(q, f"🔒 {st}", buy_kb())
            return ConversationHandler.END
        await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n{icon} <b>{prompt_batch}</b>\n\nSend comma-separated list (Max 15) or /cancel:")
        return batch_state

    async def single_process(update, context):
        raw = update.message.text.strip()
        val = validator_fn(raw) if validator_fn else raw
        if not val:
            await safe_reply(update, "❌ Invalid format! Please try again or type /cancel:")
            return single_state
        await execute_search(update, context, feat_name, action, param_key, val, icon, val)
        return ConversationHandler.END

    async def batch_process(update, context):
        raw_list = [x.strip() for x in update.message.text.split(",") if x.strip()]
        valid_items = [validator_fn(x) if validator_fn else x for x in raw_list]
        valid_items = [x for x in valid_items if x][:15]
        if not valid_items:
            await safe_reply(update, "❌ No valid entries found! Try again or /cancel:")
            return batch_state
        await execute_batch(update, context, feat_name, action, param_key, valid_items, icon)
        return ConversationHandler.END

    return single_start, batch_start, single_process, batch_process

def clean_num(x):
    c = x.replace(" ", "").replace("-", "").replace("+", "")
    return c if c.isdigit() and 7 <= len(c) <= 15 else None

def clean_aadhaar(x):
    c = x.replace(" ", "").replace("-", "")
    return c if c.isdigit() and len(c) == 12 else None

def clean_rc(x):
    c = x.upper().replace(" ", "").replace("-", "")
    return c if len(c) >= 4 else None

def clean_ifsc(x):
    c = x.upper().replace(" ", "")
    return c if len(c) == 11 else None

(p_ss, p_bs, p_sp, p_bp) = make_handler_pair("phone", "num", "number", "📱", PHONE_SINGLE, PHONE_BATCH, "Enter Phone Number (e.g. 9876543210):", "Enter Phone Numbers (comma-separated):", clean_num)
(e_ss, e_bs, e_sp, e_bp) = make_handler_pair("email", "email", "email", "📧", EMAIL_SINGLE, EMAIL_BATCH, "Enter Email Address:", "Enter Emails (comma-separated):", lambda x: x.strip() if "@" in x else None)
(u_ss, u_bs, u_sp, u_bp) = make_handler_pair("upi", "upiinfo", "upi", "💳", UPI_SINGLE, UPI_BATCH, "Enter UPI ID (e.g. name@okhdfcbank):", "Enter UPI IDs (comma-separated):", lambda x: x.strip() if "@" in x else None)
(a_ss, a_bs, a_sp, a_bp) = make_handler_pair("aadhaar", "aadhar", "aadhar", "🪪", AADHAAR_SINGLE, AADHAAR_BATCH, "Enter 12-Digit Aadhaar Number:", "Enter Aadhaar Numbers (comma-separated):", clean_aadhaar)
(v_ss, v_bs, v_sp, v_bp) = make_handler_pair("vehicle", "vehicle-v1", "rc", "🚗", VEHICLE_SINGLE, VEHICLE_BATCH, "Enter Vehicle RC (e.g. DL01AB1234):", "Enter RC Numbers (comma-separated):", clean_rc)
(i_ss, i_bs, i_sp, i_bp) = make_handler_pair("ifsc", "ifsc-info", "ifsc", "🏦", IFSC_SINGLE, IFSC_BATCH, "Enter Bank IFSC Code (e.g. SBIN0001234):", "Enter IFSC Codes (comma-separated):", clean_ifsc)
(tg_ss, tg_bs, tg_sp, tg_bp) = make_handler_pair("tg", "tg-registration", "userid", "👤", TG_SINGLE, TG_BATCH, "Enter Telegram Numeric User ID:", "Enter Telegram User IDs (comma-separated):", lambda x: x.strip() if x.strip().isdigit() else None)
(in_ss, in_bs, in_sp, in_bp) = make_handler_pair("insta", "instagram-user", "username", "📸", INSTA_SINGLE, INSTA_BATCH, "Enter Instagram Username (without @):", "Enter Usernames (comma-separated):", lambda x: x.strip().lstrip("@"))
(im_ss, im_bs, im_sp, im_bp) = make_handler_pair("imei", "imei-info", "imei_num", "📱", IMEI_SINGLE, IMEI_BATCH, "Enter 15-Digit IMEI Number:", "Enter IMEIs (comma-separated):", lambda x: x.strip() if x.strip().isdigit() else None)
(pin_ss, pin_bs, pin_sp, pin_bp) = make_handler_pair("pin", "pincode-info", "pincode", "📮", PIN_SINGLE, PIN_BATCH, "Enter 6-Digit Postal Pincode:", "Enter Pincodes (comma-separated):", lambda x: x.strip() if len(x.strip()) == 6 else None)
(c_ss, c_bs, c_sp, c_bp) = make_handler_pair("country", "country-info", "name", "🌍", COUNTRY_SINGLE, COUNTRY_BATCH, "Enter Country Name (e.g. India):", "Enter Countries (comma-separated):", lambda x: x.strip())
(pm_ss, pm_bs, pm_sp, pm_bp) = make_handler_pair("paytm", "paytm", "info", "💰", PAYTM_SINGLE, PAYTM_BATCH, "Enter Paytm Registered Phone Number:", "Enter Phone Numbers (comma-separated):", clean_num)
(ip_ss, ip_bs, ip_sp, ip_bp) = make_handler_pair("ip", "ip-v1", "query", "🌐", IP_SINGLE, IP_BATCH, "Enter IP Address (e.g. 8.8.8.8):", "Enter IPs (comma-separated):", lambda x: x.strip())
(w_ss, w_bs, w_sp, w_bp) = make_handler_pair("weather", "weather", "search", "🌤️", WEATHER_SINGLE, WEATHER_BATCH, "Enter City Name for Weather:", "Enter City Names (comma-separated):", lambda x: x.strip().title())

# ================== 👤 USER PROFILE & STATUS ==================
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    u = q.from_user
    ud = get_user(u.id)
    plan = get_plan(ud)
    ts = ud.get("total_searches", 0)
    rc = ud.get("redeemed_codes", [])
    
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"👤 <b>USER INTELLIGENCE PROFILE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 User ID: <code>{u.id}</code>\n"
        f"👤 Name: <b>{safe_name(u)}</b>\n"
        f"📦 Active Plan: <b>{plan['name']}</b>\n"
        f"📅 Expiry: <code>{ud.get('expiry', 'Lifetime Free')}</code>\n"
        f"🔍 Total Lookups: <code>{ts}</code>\n"
        f"🎟️ Codes Redeemed: <code>{len(rc)}</code>\n\n"
        f"💎 <b>Search Breakdown:</b>\n"
        f"📱 Phone: <code>{ud.get('phone_total',0)}</code> | 🪪 Aadhaar: <code>{ud.get('aadhaar_total',0)}</code>\n"
        f"💳 UPI: <code>{ud.get('upi_total',0)}</code> | 📧 Email: <code>{ud.get('email_total',0)}</code>\n"
        f"🚗 Vehicle: <code>{ud.get('vehicle_total',0)}</code> | 🏦 IFSC: <code>{ud.get('ifsc_total',0)}</code>\n"
        f"👤 Telegram: <code>{ud.get('tg_total',0)}</code> | 📸 Insta: <code>{ud.get('insta_total',0)}</code>"
    )
    await safe_edit(q, txt, back_kb())

async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    u = q.from_user
    if is_admin(u.id):
        await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🛡️ <b>System Status:</b> <code>ADMIN MASTER</code>\n\nAll tools unlocked with unlimited quota (💎 ∞).", back_kb())
        return
        
    lines = []
    for feat in ALL_FEATURE_KEYS:
        ok, st, _, ip, _ = check_feat_access(u.id, feat, feat.title())
        lines.append(f"• <b>{feat.title()}</b>: <code>{st}</code>")
        
    txt = f"<code>{BANNER_MINI}</code>\n\n📊 <b>YOUR USAGE & QUOTA STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join(lines) + f"\n\n💰 <b>Upgrade Quota:</b> {OWNER_CONTACT}\n🆔 Your ID: <code>{u.id}</code>"
    await safe_edit(q, txt, back_kb())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    txt = (
        f"<code>{BANNER}</code>\n\n"
        f"❓ <b>ZERO TRACE BOT MANUAL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 <b>All-In-One Intelligence Suite:</b>\n"
        f"• 📱 <b>Phone</b>: Location & carrier info\n"
        f"• 🪪 <b>Aadhaar</b>: UIDAI Ration details\n"
        f"• 💳 <b>UPI</b>: Resolve real holder name\n"
        f"• 🚗 <b>Vehicle</b>: Complete VAHAN RC info\n"
        f"• 🏦 <b>IFSC</b>: Bank branch details\n"
        f"• 👤 <b>Telegram / Insta</b>: OSINT Profiler\n"
        f"• 📱 <b>IMEI / Pincode</b>: Device & Geo info\n\n"
        f"💎 <b>Subscriptions:</b>\n"
        f"🥉 7 Days: ₹50 | 🥈 30 Days: ₹130 | 💎 1 Year: ₹799\n\n"
        f"🎟️ <b>Promo Codes:</b> Use <code>/redeem CODE</code>"
    )
    await safe_edit(q, txt, back_kb())

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    u = q.from_user
    txt = (
        f"<code>{BANNER}</code>\n\n"
        f"💎 <b>ZERO TRACE PREMIUM ACCESS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🥉 <b>7 Days Plan</b> - ₹50 (10 searches/day)\n"
        f"🥈 <b>30 Days Plan</b> - ₹130 (20 searches/day)\n"
        f"🥇 <b>6 Months Plan</b> - ₹300 (35 searches/day)\n"
        f"💎 <b>12 Months Plan</b> - ₹799 (Unlimited ∞ searches)\n\n"
        f"⚡ <b>Features:</b> Access to all 14+ Intelligence OSINT tools without restrictions.\n\n"
        f"📲 <b>Contact Admin to Activate:</b> {OWNER_CONTACT}\n"
        f"🆔 Your Telegram ID: <code>{u.id}</code>"
    )
    await safe_edit(q, txt, buy_kb())

# ================== 🎟️ REDEEM COMMAND ==================
async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return
    if not context.args:
        await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n🎟️ <b>Usage:</b> <code>/redeem CODE</code>\nExample: <code>/redeem ZERO50</code>", back_kb())
        return
    code = context.args[0].upper().strip()
    ok, msg = use_redeem_code(code, user.id)
    await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n{msg}", main_kb(user.id))

async def redeem_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await safe_edit(q, f"<code>{BANNER_SEARCH}</code>\n\n🎟️ <b>Redeem Promo Codes</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nGet free extra lookups by redeeming promo codes.\n\n👉 <b>Command:</b> <code>/redeem CODE</code>\nExample: <code>/redeem LEGITBONUS</code>", back_kb())

# ================== 👑 ADMIN PANEL ==================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await safe_reply(update, "❌ Unauthorized! Admin access only.")
        return ConversationHandler.END
    users = load_users()
    t = len(users)
    p = sum(1 for v in users.values() if v.get("is_premium"))
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"🛠️ <b>ADMIN MASTER DASHBOARD</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🛡️ Active Admins: <code>{len(ADMIN_IDS)}</code>\n"
        f"👥 Total Users: <code>{t}</code>\n"
        f"💎 Premium Subscribers: <code>{p}</code>\n"
        f"🆓 Free Tier Users: <code>{t - p}</code>\n"
        f"🎟️ Active Promos: <code>{len(list_redeem_codes())}</code>"
    )
    if update.callback_query: await safe_edit(update.callback_query, txt, admin_kb())
    else: await safe_reply(update, txt, admin_kb())
    return ConversationHandler.END

async def admin_back(u, c): await admin_panel(u, c)

async def adm_add_s(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "➕ <b>Enter User Telegram ID to add plan:</b> (or /cancel)")
    return ADMIN_ADD_ID

async def adm_add_id(u, c):
    uid = u.message.text.strip()
    if not uid.isdigit():
        await safe_reply(u, "❌ Invalid ID! Enter numbers only or /cancel:")
        return ADMIN_ADD_ID
    c.user_data["admin_uid"] = uid
    await safe_reply(u, f"Selected User: <code>{uid}</code>\nChoose plan duration:", plan_kb("plan"))
    return ADMIN_ADD_PLAN

async def adm_add_plan(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "admin_back": await admin_panel(u, c); return ConversationHandler.END
    pm = {"plan_7days": "7days", "plan_30days": "30days", "plan_6months": "6months", "plan_12months": "12months"}
    pk = pm.get(q.data, "7days")
    uid = c.user_data.get("admin_uid")
    plan = PLANS.get(pk)
    exp = upgrade(int(uid), pk)
    dl = "∞" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(q, f"✅ <b>Plan Activated!</b>\n🆔 User: <code>{uid}</code>\n📦 Plan: <b>{plan['name']}</b>\n📅 Expiry: <code>{exp}</code>\n⚡ Quota: <code>{dl}</code>", admin_kb())
    return ConversationHandler.END

async def adm_rem_s(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "❌ <b>Enter User ID to delete database records:</b> (or /cancel)")
    return ADMIN_REM_ID

async def adm_rem_p(u, c):
    uid = u.message.text.strip()
    delete_user(uid)
    await safe_reply(u, f"✅ User records for <code>{uid}</code> wiped successfully!", admin_kb())
    return ConversationHandler.END

async def adm_sp_s(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, "📅 <b>Enter User ID to modify plan:</b> (or /cancel)")
    return ADMIN_EXP_ID

async def adm_sp_id(u, c):
    uid = u.message.text.strip()
    c.user_data["admin_uid"] = uid
    await safe_reply(u, f"User: <code>{uid}</code>\nSelect new plan:", plan_kb("plan"))
    return ADMIN_EXP_PLAN

async def adm_sp_set(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "admin_back": await admin_panel(u, c); return ConversationHandler.END
    pm = {"plan_7days": "7days", "plan_30days": "30days", "plan_6months": "6months", "plan_12months": "12months"}
    pk = pm.get(q.data, "7days")
    uid = c.user_data.get("admin_uid")
    plan = PLANS.get(pk)
    exp = upgrade(int(uid), pk)
    await safe_edit(q, f"✅ <b>Subscription Updated!</b>\n🆔 User: <code>{uid}</code>\n📦 Plan: <b>{plan['name']}</b>\n📅 New Expiry: <code>{exp}</code>", admin_kb())
    return ConversationHandler.END

async def adm_list(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    users = load_users()
    if not users:
        await safe_edit(q, "📋 No users found.", admin_kb()); return
    txt = f"<code>{BANNER_MINI}</code>\n\n📋 <b>REGISTERED USERS ({len(users)})</b>\n\n"
    for uid, info in list(users.items())[-30:]:
        plan = get_plan(info)
        ts = info.get("total_searches", 0)
        if int(uid) in ADMIN_IDS: st = "🛡️ Admin"
        elif info.get("is_premium") and info.get("expiry"):
            try:
                ed = date.fromisoformat(info["expiry"])
                st = f"💎 {(ed - date.today()).days}d" if date.today() <= ed else "🔴 Exp"
            except Exception: st = "⚪"
        else: st = "🆓 Free"
        txt += f"<code>{uid}</code> | {st} | 🔍 <code>{ts}</code>\n"
    await safe_edit(q, txt[:4000], admin_kb())

async def adm_stats(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    users = load_users()
    ts = sum(v.get("total_searches", 0) for v in users.values())
    act = sum(1 for u2, v in users.items() if v.get("is_premium") and int(u2) not in ADMIN_IDS)
    txt = (
        f"<code>{BANNER_MINI}</code>\n\n"
        f"📊 <b>SYSTEM OVERVIEW STATS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total Registered: <code>{len(users)}</code>\n"
        f"🔍 Total Queries Served: <code>{ts}</code>\n"
        f"💎 Active Premium Users: <code>{act}</code>\n"
        f"🎟️ Active Redeem Codes: <code>{len(list_redeem_codes())}</code>\n"
        f"📅 Date (IST): <code>{datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d-%m-%Y %H:%M')}</code>"
    )
    await safe_edit(q, txt, admin_kb())

async def adm_monitor(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    users = load_users()
    free = [v for u2, v in users.items() if not v.get("is_premium") and int(u2) not in ADMIN_IDS]
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🆓 <b>FREE TIER MONITOR</b>\n\n👥 Free Users Total: <code>{len(free)}</code>", admin_kb())

async def bc_start(u, c):
    q = u.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n📢 <b>GLOBAL BROADCAST</b>\n\nSend broadcast text message or /cancel:")
    return ADMIN_BROADCAST_MSG

async def bc_msg(u, c):
    m = u.message.text.strip()
    c.user_data["bc"] = m
    users = load_users()
    await safe_reply(
        u,
        f"📢 <b>Broadcast Preview:</b>\n\n{html.escape(m)}\n\n👥 Target audience: <b>{len(users)} users</b>\nConfirm broadcast?",
        InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Send Broadcast", callback_data="broadcast_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
        ])
    )
    return ADMIN_BROADCAST_CONFIRM

async def bc_confirm(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "broadcast_cancel":
        await safe_edit(q, "❌ Broadcast cancelled.", admin_kb())
        c.user_data.pop("bc", None)
        return ConversationHandler.END
    msg = c.user_data.get("bc", "")
    users = load_users()
    total = len(users)
    bt = f"<code>{BANNER_MINI}</code>\n\n📢 <b>GLOBAL ANNOUNCEMENT</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{html.escape(msg)}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n💬 Contact: {OWNER_CONTACT}"
    
    sm = await safe_reply(u, f"🚀 Broadcasting to <b>{total}</b> users...")
    s, f2, b, ct = 0, 0, 0, 0
    for uid in users:
        ct += 1
        try:
            await c.bot.send_message(chat_id=int(uid), text=bt, parse_mode="HTML")
            s += 1
        except Exception as e:
            if any(w in str(e).lower() for w in ["blocked", "forbidden", "not found"]): b += 1
            else: f2 += 1
        if ct % 15 == 0 or ct == total:
            try: await sm.edit_text(f"🚀 Progress: <code>{ct}/{total}</code> | ✅ <code>{s}</code> | 🚫 <code>{b}</code> | ❌ <code>{f2}</code>", parse_mode="HTML")
            except Exception: pass
            
    await safe_reply(u, f"✅ <b>Broadcast Complete!</b>\n👥 Total: <code>{total}</code> | ✅ Success: <code>{s}</code> | 🚫 Blocked: <code>{b}</code> | ❌ Failed: <code>{f2}</code>", admin_kb())
    c.user_data.pop("bc", None)
    return ConversationHandler.END

async def custom_s(u, c):
    q = u.callback_query; await q.answer()
    await safe_edit(q, "⚙️ <b>Enter custom duration in DAYS:</b> (e.g. 45) or /cancel")
    return ADMIN_CUSTOM_DAYS

async def custom_days(u, c):
    t = u.message.text.strip()
    if not t.isdigit() or int(t) <= 0:
        await safe_reply(u, "❌ Invalid days! Enter a positive integer or /cancel:")
        return ADMIN_CUSTOM_DAYS
    c.user_data["cd"] = int(t)
    await safe_reply(u, f"📅 Duration: <b>{t} Days</b>\nEnter daily search limit (Enter <code>0</code> for unlimited ∞):")
    return ADMIN_CUSTOM_LIMIT

async def custom_limit(u, c):
    t = u.message.text.strip()
    if not t.isdigit():
        await safe_reply(u, "❌ Invalid limit! Enter number or /cancel:")
        return ADMIN_CUSTOM_LIMIT
    lim = int(t)
    unl = (lim == 0)
    days = c.user_data.get("cd")
    uid = c.user_data.get("admin_uid")
    exp = upgrade_custom(int(uid), days, lim, unl)
    await safe_reply(u, f"⚙️ <b>Custom Plan Set!</b>\n🆔 User: <code>{uid}</code>\n📅 Days: <code>{days}</code>\n📅 Expiry: <code>{exp}</code>\n⚡ Quota: <code>{'∞ Unlimited' if unl else f'{lim}/day'}</code>", admin_kb())
    c.user_data.pop("cd", None)
    c.user_data.pop("admin_uid", None)
    return ConversationHandler.END

# Admin Promo Handlers
async def admin_redeem_create_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n🎟️ <b>CREATE PROMO CODE</b>\n\nEnter Code Name (3-20 chars) or /cancel:")
    return REDEEM_CREATE_CODE

async def admin_redeem_code_input(update, context):
    code = update.message.text.strip().upper()
    if len(code) < 3 or len(code) > 20 or not code.isalnum():
        await safe_reply(update, "❌ Invalid! 3-20 alphanumeric letters only. Try again or /cancel:")
        return REDEEM_CREATE_CODE
    if code in REDEEM_CODES:
        await safe_reply(update, f"❌ Code <code>{code}</code> already exists! Try another or /cancel:")
        return REDEEM_CREATE_CODE
    context.user_data["nrc"] = code
    await safe_reply(update, f"Code Name: <code>{code}</code>\n🎁 How many free searches per tool should it give?")
    return REDEEM_CREATE_SEARCHES

async def admin_redeem_searches_input(update, context):
    t = update.message.text.strip()
    if not t.isdigit() or int(t) <= 0:
        await safe_reply(update, "❌ Positive number only! Try again:")
        return REDEEM_CREATE_SEARCHES
    context.user_data["nrs"] = int(t)
    await safe_reply(update, f"Searches: <b>+{t}</b>\n👥 Maximum users who can redeem this code?")
    return REDEEM_CREATE_LIMIT

async def admin_redeem_limit_input(update, context):
    t = update.message.text.strip()
    if not t.isdigit() or int(t) <= 0:
        await safe_reply(update, "❌ Positive number only! Try again:")
        return REDEEM_CREATE_LIMIT
    mu = int(t)
    code = context.user_data.get("nrc")
    fs = context.user_data.get("nrs")
    create_redeem_code(code, fs, mu)
    await safe_reply(update, f"<code>{BANNER_MINI}</code>\n\n🎉 <b>PROMO CODE CREATED!</b>\n\n🔑 Code: <code>{code}</code>\n🎁 Extra Searches: <code>+{fs}</code>\n👥 Max Redemptions: <code>{mu}</code>\n\n📢 Users can claim via: <code>/redeem {code}</code>", admin_kb())
    context.user_data.pop("nrc", None)
    context.user_data.pop("nrs", None)
    return ConversationHandler.END

async def admin_redeem_list(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return
    codes = list_redeem_codes()
    if not codes:
        await safe_edit(q, f"<code>{BANNER_MINI}</code>\n\n📋 No promo codes active.", admin_kb()); return
    txt = f"<code>{BANNER_MINI}</code>\n\n🎟️ <b>ACTIVE PROMO CODES</b>\n\n"
    for code, info in codes.items():
        st = "🟢" if info.get("active", True) and info["used_count"] < info["max_uses"] else "🔴"
        txt += f"{st} <code>{code}</code> | 🎁 <code>+{info['free_searches']}</code> | 👥 <code>{info['used_count']}/{info['max_uses']}</code>\n"
    await safe_edit(q, txt[:4000], admin_kb())

async def admin_redeem_delete_start(update, context):
    q = update.callback_query; await q.answer()
    if not is_admin(q.from_user.id): return ConversationHandler.END
    codes = list_redeem_codes()
    if not codes:
        await safe_edit(q, "📋 No promo codes exist.", admin_kb()); return ConversationHandler.END
    txt = f"<code>{BANNER_MINI}</code>\n\n🗑️ <b>DELETE PROMO CODE</b>\n\n" + "".join(f"• <code>{c}</code>\n" for c in codes) + "\nEnter code name to delete or /cancel:"
    await safe_edit(q, txt)
    return REDEEM_DELETE_CODE

async def admin_redeem_delete_input(update, context):
    code = update.message.text.strip().upper()
    if delete_redeem_code(code):
        await safe_reply(update, f"✅ Promo code <code>{code}</code> deleted successfully!", admin_kb())
    else:
        await safe_reply(update, f"❌ Promo code <code>{code}</code> not found!", admin_kb())
    return ConversationHandler.END

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"❌ Exception in update: {context.error}")

# ================== 🏁 MAIN ENGINE ==================
def main():
    # Start Flask Webserver for 24/7 keep-alive
    threading.Thread(target=start_webserver, daemon=True).start()
    print("🌐 Keep-alive server running on port 8080!")

    # Separate request instances to avoid HTTPX transport deadlocks
    req = HTTPXRequest(connect_timeout=20, read_timeout=20, write_timeout=20)
    get_updates_req = HTTPXRequest(connect_timeout=20, read_timeout=30, write_timeout=20)
    app = ApplicationBuilder().token(BOT_TOKEN).request(req).get_updates_request(get_updates_req).build()
    
    C = ConversationHandler
    CQ = CallbackQueryHandler
    MH = MessageHandler
    CMD = CommandHandler
    F = filters.TEXT & ~filters.COMMAND
    UF = [CMD("cancel", cancel), CMD("start", start)]

    convs = [
        # Search Tools
        C(entry_points=[CQ(p_ss, pattern="^phone_single$")], states={PHONE_SINGLE: [MH(F, p_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(p_bs, pattern="^phone_batch$")], states={PHONE_BATCH: [MH(F, p_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(e_ss, pattern="^email_single$")], states={EMAIL_SINGLE: [MH(F, e_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(e_bs, pattern="^email_batch$")], states={EMAIL_BATCH: [MH(F, e_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(u_ss, pattern="^upi_single$")], states={UPI_SINGLE: [MH(F, u_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(u_bs, pattern="^upi_batch$")], states={UPI_BATCH: [MH(F, u_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(a_ss, pattern="^aadhaar_single$")], states={AADHAAR_SINGLE: [MH(F, a_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(a_bs, pattern="^aadhaar_batch$")], states={AADHAAR_BATCH: [MH(F, a_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(v_ss, pattern="^vehicle_single$")], states={VEHICLE_SINGLE: [MH(F, v_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(v_bs, pattern="^vehicle_batch$")], states={VEHICLE_BATCH: [MH(F, v_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(i_ss, pattern="^ifsc_single$")], states={IFSC_SINGLE: [MH(F, i_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(i_bs, pattern="^ifsc_batch$")], states={IFSC_BATCH: [MH(F, i_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(tg_ss, pattern="^tg_single$")], states={TG_SINGLE: [MH(F, tg_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(tg_bs, pattern="^tg_batch$")], states={TG_BATCH: [MH(F, tg_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(in_ss, pattern="^insta_single$")], states={INSTA_SINGLE: [MH(F, in_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(in_bs, pattern="^insta_batch$")], states={INSTA_BATCH: [MH(F, in_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(im_ss, pattern="^imei_single$")], states={IMEI_SINGLE: [MH(F, im_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(im_bs, pattern="^imei_batch$")], states={IMEI_BATCH: [MH(F, im_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(pin_ss, pattern="^pin_single$")], states={PIN_SINGLE: [MH(F, pin_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(pin_bs, pattern="^pin_batch$")], states={PIN_BATCH: [MH(F, pin_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(c_ss, pattern="^country_single$")], states={COUNTRY_SINGLE: [MH(F, c_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(c_bs, pattern="^country_batch$")], states={COUNTRY_BATCH: [MH(F, c_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(pm_ss, pattern="^paytm_single$")], states={PAYTM_SINGLE: [MH(F, pm_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(pm_bs, pattern="^paytm_batch$")], states={PAYTM_BATCH: [MH(F, pm_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(ip_ss, pattern="^ip_single$")], states={IP_SINGLE: [MH(F, ip_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(ip_bs, pattern="^ip_batch$")], states={IP_BATCH: [MH(F, ip_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(w_ss, pattern="^weather_single$")], states={WEATHER_SINGLE: [MH(F, w_sp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(w_bs, pattern="^weather_batch$")], states={WEATHER_BATCH: [MH(F, w_bp)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        
        # Admin Dialogs
        C(entry_points=[CQ(adm_add_s, pattern="^admin_add$")], states={ADMIN_ADD_ID: [MH(F, adm_add_id)], ADMIN_ADD_PLAN: [CQ(custom_s, pattern="^plan_custom$"), CQ(adm_add_plan, pattern="^plan_")], ADMIN_CUSTOM_DAYS: [MH(F, custom_days)], ADMIN_CUSTOM_LIMIT: [MH(F, custom_limit)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(adm_rem_s, pattern="^admin_remove$")], states={ADMIN_REM_ID: [MH(F, adm_rem_p)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(adm_sp_s, pattern="^admin_setplan$")], states={ADMIN_EXP_ID: [MH(F, adm_sp_id)], ADMIN_EXP_PLAN: [CQ(custom_s, pattern="^plan_custom$"), CQ(adm_sp_set, pattern="^plan_")], ADMIN_CUSTOM_DAYS: [MH(F, custom_days)], ADMIN_CUSTOM_LIMIT: [MH(F, custom_limit)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(bc_start, pattern="^admin_broadcast$")], states={ADMIN_BROADCAST_MSG: [MH(F, bc_msg)], ADMIN_BROADCAST_CONFIRM: [CQ(bc_confirm, pattern="^broadcast_(confirm|cancel)$")]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(admin_redeem_create_start, pattern="^admin_redeem_create$")], states={REDEEM_CREATE_CODE: [MH(F, admin_redeem_code_input)], REDEEM_CREATE_SEARCHES: [MH(F, admin_redeem_searches_input)], REDEEM_CREATE_LIMIT: [MH(F, admin_redeem_limit_input)]}, fallbacks=UF, per_message=False, allow_reentry=True),
        C(entry_points=[CQ(admin_redeem_delete_start, pattern="^admin_redeem_delete$")], states={REDEEM_DELETE_CODE: [MH(F, admin_redeem_delete_input)]}, fallbacks=UF, per_message=False, allow_reentry=True),
    ]

    for cv in convs: app.add_handler(cv)
    
    app.add_handler(CMD("start", start))
    app.add_handler(CMD("cancel", cancel))
    app.add_handler(CMD("admin", admin_panel))
    app.add_handler(CMD("redeem", redeem_command))
    app.add_error_handler(error_handler)

    # Callback Routes
    callbacks = [
        ("mode_phone", mode_phone), ("mode_email", mode_email), ("mode_upi", mode_upi),
        ("mode_aadhaar", mode_aadhaar), ("mode_vehicle", mode_vehicle), ("mode_ifsc", mode_ifsc),
        ("mode_tg", mode_tg), ("mode_insta", mode_insta), ("mode_imei", mode_imei),
        ("mode_pin", mode_pin), ("mode_country", mode_country), ("mode_paytm", mode_paytm),
        ("mode_ip", mode_ip), ("mode_weather", mode_weather),
        ("redeem_info", redeem_info), ("profile", profile), ("status", status_check),
        ("help", help_menu), ("buy", buy), ("admin_list", adm_list),
        ("admin_stats", adm_stats), ("admin_back", admin_back), ("admin_free_monitor", adm_monitor),
        ("admin_redeem_list", admin_redeem_list), ("main_menu", main_menu_cb), ("verify_join", verify_join)
    ]
    for pattern, fn in callbacks:
        app.add_handler(CQ(fn, pattern=f"^{pattern}$"))

    print("╔══════════════════════════════════════════╗")
    print("║   ☠️ ZERO TRACE MERGED OSINT RUNNING ☠️   ║")
    print("╚══════════════════════════════════════════╝")
    app.run_polling(drop_pending_updates=True, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()

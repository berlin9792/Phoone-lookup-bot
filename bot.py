#!/usr/bin/env python3
"""
🔍 Phone & Email & UPI Intelligence Bot
Combined Bot - Phone + Email + UPI Search
ONE PLAN = ALL ACCESS
+ Broadcast Feature
+ Custom Days Plan
+ UPI Search (Daily Limit like Phone)
+ MongoDB Cloud Database
"""

import json
import os
import threading
import requests
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

# ================== CONFIG ==================
BOT_TOKEN     = "8642873626:AAFy5F79opcK_NMJ7NgGItd6sRrfbOc4TJU"
ADMIN_IDS     = [5057489358, 1968142314]
DEFAULT_PIN   = "240841"
API_URL       = "https://lk-api-pinsstm.ramaxinfo.workers.dev/"
UPI_API_URL   = "https://nitin-developer-api-paid.nitinshab43.workers.dev/api"
UPI_API_KEY   = "JAANI"
OWNER_CONTACT = "@theplayerror"

# 🌐 MongoDB Cloud Connection String
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://httplegitfs_db_user:Q8uGZxERXsrf2VV1@cluster0.iojnad7.mongodb.net/?retryWrites=true&w=majority"
)

# ================== FREE SEARCHES ==================
PHONE_FREE_SEARCHES = 2
EMAIL_FREE_SEARCHES = 2
UPI_FREE_SEARCHES   = 2

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
PHONE_COUNTRY_SINGLE    = 10
PHONE_COUNTRY_BATCH     = 11
PHONE_SINGLE_INDIA      = 12
PHONE_SINGLE_OTHER      = 13
PHONE_BATCH_INDIA       = 14
PHONE_BATCH_OTHER       = 15
EMAIL_SINGLE            = 20
EMAIL_BATCH             = 21
ADMIN_ADD_ID            = 30
ADMIN_ADD_PLAN          = 31
ADMIN_REM_ID            = 32
ADMIN_EXP_ID            = 33
ADMIN_EXP_PLAN          = 34
ADMIN_BROADCAST_MSG     = 35
ADMIN_BROADCAST_CONFIRM = 36
ADMIN_CUSTOM_DAYS       = 37
ADMIN_CUSTOM_LIMIT      = 38
UPI_SINGLE              = 40
UPI_BATCH               = 41


# ================== DUMMY WEBSERVER FOR RENDER ==================
web_app = Flask(__name__)

@web_app.route('/')
def render_keep_alive():
    return "Bot is active and running with Cloud Database!", 200

def start_webserver():
    port = int(os.environ.get("PORT", 8080))
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    web_app.run(host="0.0.0.0", port=port)


# ================== ADMIN CHECK ==================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ================== MONGODB CLOUD DATABASE ==================
try:
    mongo_client = MongoClient(MONGO_URI)
    db           = mongo_client["tele_intel_bot"]
    users_col    = db["users"]
    mongo_client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Cloud Database!")
except Exception as e:
    print("⚠️ MongoDB Connection Warning:", e)
    users_col = None

LOCAL_DATA_FILE = Path("users.json")

def load_users():
    if users_col is not None:
        try:
            records    = users_col.find()
            users_dict = {}
            for doc in records:
                uid  = doc["_id"]
                data = {k: v for k, v in doc.items() if k != "_id"}
                users_dict[uid] = data
            return users_dict
        except Exception:
            pass
    if LOCAL_DATA_FILE.exists():
        try:
            return json.loads(LOCAL_DATA_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_user_to_db(uid: str, user_data: dict):
    if users_col is not None:
        try:
            users_col.update_one({"_id": str(uid)}, {"$set": user_data}, upsert=True)
            return
        except Exception:
            pass
    data          = load_users()
    data[str(uid)] = user_data
    LOCAL_DATA_FILE.write_text(json.dumps(data, indent=2))

def save_users(data):
    if users_col is not None:
        try:
            for uid, udata in data.items():
                users_col.update_one({"_id": str(uid)}, {"$set": udata}, upsert=True)
            return
        except Exception:
            pass
    LOCAL_DATA_FILE.write_text(json.dumps(data, indent=2))

def delete_user_from_db(uid: str):
    if users_col is not None:
        try:
            users_col.delete_one({"_id": str(uid)})
            return
        except Exception:
            pass
    data = load_users()
    if str(uid) in data:
        del data[str(uid)]
        LOCAL_DATA_FILE.write_text(json.dumps(data, indent=2))

def get_or_create_user(user_id: int):
    uid = str(user_id)
    if users_col is not None:
        try:
            doc = users_col.find_one({"_id": uid})
            if not doc:
                default_data = {
                    "plan"                : "trial",
                    "expiry"              : "",
                    "is_premium"          : False,
                    "phone_free_used"     : 0,
                    "phone_daily_searches": 0,
                    "phone_last_date"     : "",
                    "phone_total"         : 0,
                    "email_free_used"     : 0,
                    "email_total"         : 0,
                    "upi_free_used"       : 0,
                    "upi_daily_searches"  : 0,
                    "upi_last_date"       : "",
                    "upi_total"           : 0,
                    "added"               : date.today().isoformat(),
                    "total_searches"      : 0,
                }
                users_col.insert_one({"_id": uid, **default_data})
                return default_data
            else:
                doc.pop("_id", None)
                changed = False
                if "upi_free_used" not in doc:
                    doc["upi_free_used"] = 0
                    changed = True
                if "upi_total" not in doc:
                    doc["upi_total"] = 0
                    changed = True
                if "upi_daily_searches" not in doc:
                    doc["upi_daily_searches"] = 0
                    changed = True
                if "upi_last_date" not in doc:
                    doc["upi_last_date"] = ""
                    changed = True
                if changed:
                    save_user_to_db(uid, doc)
                return doc
        except Exception:
            pass

    users = load_users()
    if uid not in users:
        users[uid] = {
            "plan": "trial", "expiry": "", "is_premium": False,
            "phone_free_used": 0, "phone_daily_searches": 0, "phone_last_date": "",
            "phone_total": 0, "email_free_used": 0, "email_total": 0,
            "upi_free_used": 0, "upi_daily_searches": 0, "upi_last_date": "",
            "upi_total": 0, "added": date.today().isoformat(),
            "total_searches": 0,
        }
        save_users(users)
    return users[uid]


# ================== PLAN RESOLVER ==================
def get_user_plan_details(user_data: dict):
    plan_key = user_data.get("plan", "trial")
    if plan_key.startswith("custom_"):
        try:
            days = int(plan_key.split("_")[1].replace("d", ""))
        except Exception:
            days = 30
        return {
            "name"       : f"Custom ({days} Days)",
            "days"       : days,
            "daily_limit": user_data.get("custom_limit", 0),
            "unlimited"  : user_data.get("custom_unlimited", False),
            "is_free"    : False,
        }
    else:
        return PLANS.get(plan_key, PLANS["trial"])


# ================== PLAN UPGRADE ==================
def upgrade_user(user_id: int, plan_key: str):
    uid       = str(user_id)
    user_data = get_or_create_user(user_id)
    plan      = PLANS.get(plan_key, PLANS["7days"])
    expiry    = (date.today() + timedelta(days=plan["days"])).isoformat()
    user_data["plan"]                 = plan_key
    user_data["expiry"]               = expiry
    user_data["is_premium"]           = True
    user_data["phone_daily_searches"] = 0
    user_data["phone_last_date"]      = ""
    user_data["upi_daily_searches"]   = 0
    user_data["upi_last_date"]        = ""
    save_user_to_db(uid, user_data)
    return expiry

def upgrade_user_custom(user_id: int, days: int, daily_limit: int, is_unlimited: bool):
    uid       = str(user_id)
    user_data = get_or_create_user(user_id)
    expiry    = (date.today() + timedelta(days=days)).isoformat()
    user_data["plan"]                 = f"custom_{days}d"
    user_data["expiry"]               = expiry
    user_data["is_premium"]           = True
    user_data["phone_daily_searches"] = 0
    user_data["phone_last_date"]      = ""
    user_data["upi_daily_searches"]   = 0
    user_data["upi_last_date"]        = ""
    user_data["custom_limit"]         = daily_limit
    user_data["custom_unlimited"]     = is_unlimited
    save_user_to_db(uid, user_data)
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
    user_data = get_or_create_user(user_id)
    plan      = get_user_plan_details(user_data)
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
    uid       = str(user_id)
    user_data = get_or_create_user(user_id)
    today     = date.today().isoformat()
    if user_data.get("phone_last_date", "") != today:
        user_data["phone_daily_searches"] = 0
        user_data["phone_last_date"]      = today
    plan = get_user_plan_details(user_data)
    if not is_admin(user_id):
        if plan.get("is_free", True):
            user_data["phone_free_used"] = user_data.get("phone_free_used", 0) + 1
        else:
            user_data["phone_daily_searches"] = user_data.get("phone_daily_searches", 0) + 1
    user_data["phone_total"]    = user_data.get("phone_total", 0) + 1
    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    save_user_to_db(uid, user_data)

def check_phone_access(user_id: int):
    if is_admin(user_id):
        return True, "Admin Unlimited", 9999, True, "12months"
    user_data  = get_or_create_user(user_id)
    plan       = get_user_plan_details(user_data)
    plan_key   = user_data.get("plan", "trial")
    expiry_str = user_data.get("expiry", "")
    is_premium = user_data.get("is_premium", False)
    if is_premium and expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                free_left = get_phone_free_remaining(user_id)
                if free_left > 0:
                    return True, f"Plan expired | {free_left} free left", 0, False, "trial"
                return False, "Plan expired! Renew karo.", 0, False, "trial"
            days_left    = (expiry - date.today()).days
            daily_rem    = get_phone_daily_remaining(user_id)
            daily_limit  = plan.get("daily_limit", 0)
            is_unlimited = plan.get("unlimited", False)
            if is_unlimited:
                return True, f"{plan['name']} | Unlimited | {days_left}d left", days_left, True, plan_key
            else:
                if daily_rem <= 0:
                    return False, f"Daily limit khatam! ({daily_limit}/day)", days_left, True, plan_key
                return True, f"{plan['name']} | {daily_rem}/{daily_limit} today | {days_left}d left", days_left, True, plan_key
        except Exception:
            pass
    free_left = get_phone_free_remaining(user_id)
    if free_left > 0:
        return True, f"Trial ({free_left}/{PHONE_FREE_SEARCHES} left)", 0, False, "trial"
    return False, "Trial khatam! Plan lo.", 0, False, "trial"


# ==================== EMAIL ACCESS ====================
def get_email_free_remaining(user_id: int) -> int:
    if is_admin(user_id):
        return 999999
    user_data = get_or_create_user(user_id)
    used      = user_data.get("email_free_used", 0)
    return max(0, EMAIL_FREE_SEARCHES - used)

def use_email_search(user_id: int, is_premium: bool):
    uid       = str(user_id)
    user_data = get_or_create_user(user_id)
    if not is_admin(user_id):
        if not is_premium:
            user_data["email_free_used"] = user_data.get("email_free_used", 0) + 1
    user_data["email_total"]    = user_data.get("email_total", 0) + 1
    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    save_user_to_db(uid, user_data)

def check_email_access(user_id: int):
    if is_admin(user_id):
        return True, "Admin Unlimited", 9999, True
    user_data  = get_or_create_user(user_id)
    is_premium = user_data.get("is_premium", False)
    expiry_str = user_data.get("expiry", "")
    if is_premium and expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                free_left = get_email_free_remaining(user_id)
                if free_left > 0:
                    return True, f"Plan expired | {free_left} free left", 0, False
                return False, "Plan expired! Renew karo.", 0, False
            days = (expiry - date.today()).days
            return True, f"Premium ({days} days left)", days, True
        except Exception:
            pass
    free_left = get_email_free_remaining(user_id)
    if free_left > 0:
        return True, f"Free ({free_left}/{EMAIL_FREE_SEARCHES} left)", 0, False
    return False, "Free khatam! Plan lo.", 0, False


# ==================== UPI ACCESS (LIKE PHONE - DAILY LIMIT) ====================
def get_upi_free_remaining(user_id: int) -> int:
    if is_admin(user_id):
        return 999999
    user_data = get_or_create_user(user_id)
    used      = user_data.get("upi_free_used", 0)
    return max(0, UPI_FREE_SEARCHES - used)

def get_upi_daily_remaining(user_id: int) -> int:
    if is_admin(user_id):
        return 999999
    user_data = get_or_create_user(user_id)
    plan      = get_user_plan_details(user_data)
    if plan.get("unlimited", False):
        return 999999
    daily_limit = plan.get("daily_limit", 0)
    today       = date.today().isoformat()
    last_date   = user_data.get("upi_last_date", "")
    daily_used  = user_data.get("upi_daily_searches", 0)
    if last_date != today:
        return daily_limit
    return max(0, daily_limit - daily_used)

def use_upi_search(user_id: int):
    uid       = str(user_id)
    user_data = get_or_create_user(user_id)
    today     = date.today().isoformat()
    if user_data.get("upi_last_date", "") != today:
        user_data["upi_daily_searches"] = 0
        user_data["upi_last_date"]      = today
    plan = get_user_plan_details(user_data)
    if not is_admin(user_id):
        if plan.get("is_free", True):
            user_data["upi_free_used"] = user_data.get("upi_free_used", 0) + 1
        else:
            user_data["upi_daily_searches"] = user_data.get("upi_daily_searches", 0) + 1
    user_data["upi_total"]      = user_data.get("upi_total", 0) + 1
    user_data["total_searches"] = user_data.get("total_searches", 0) + 1
    save_user_to_db(uid, user_data)

def check_upi_access(user_id: int):
    if is_admin(user_id):
        return True, "Admin Unlimited", 9999, True, "12months"
    user_data  = get_or_create_user(user_id)
    plan       = get_user_plan_details(user_data)
    plan_key   = user_data.get("plan", "trial")
    expiry_str = user_data.get("expiry", "")
    is_premium = user_data.get("is_premium", False)
    if is_premium and expiry_str:
        try:
            expiry = date.fromisoformat(expiry_str)
            if date.today() > expiry:
                free_left = get_upi_free_remaining(user_id)
                if free_left > 0:
                    return True, f"Plan expired | {free_left} free left", 0, False, "trial"
                return False, "Plan expired! Renew karo.", 0, False, "trial"
            days_left    = (expiry - date.today()).days
            daily_rem    = get_upi_daily_remaining(user_id)
            daily_limit  = plan.get("daily_limit", 0)
            is_unlimited = plan.get("unlimited", False)
            if is_unlimited:
                return True, f"{plan['name']} | Unlimited | {days_left}d left", days_left, True, plan_key
            else:
                if daily_rem <= 0:
                    return False, f"Daily UPI limit khatam! ({daily_limit}/day)", days_left, True, plan_key
                return True, f"{plan['name']} | {daily_rem}/{daily_limit} today | {days_left}d left", days_left, True, plan_key
        except Exception:
            pass
    free_left = get_upi_free_remaining(user_id)
    if free_left > 0:
        return True, f"Trial ({free_left}/{UPI_FREE_SEARCHES} left)", 0, False, "trial"
    return False, "Trial khatam! Plan lo.", 0, False, "trial"


# ================== APIs ==================
def search_api(term: str):
    try:
        r = requests.get(API_URL, params={"pin": DEFAULT_PIN, "term": term}, timeout=20)
        r.raise_for_status()
        return {"ok": True, "data": r.json()}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def upi_search_api(upi_id: str):
    try:
        r = requests.get(UPI_API_URL, params={"key": UPI_API_KEY, "id": upi_id}, timeout=20)
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
        "upi": "💳", "vpa": "💳", "bank": "🏦", "ifsc": "🏦",
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
        "payee": "💳", "payer": "💳", "merchant": "🏪",
        "verified": "✅", "valid": "✅",
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
            return f"{icon} *{term}*\n`{data[0]}`"
    if not isinstance(data, dict):
        return f"{icon} *{term}*\n`{data}`"

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

    divider = "━" * 28
    output  = [
        f"{icon} *Result for* `{term}`",
        f"📊 *{len(unique_records)} record(s) found*",
        divider,
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

def format_upi_result(upi_id: str, data):
    if not data:
        return f"💳 *{upi_id}*\n_No data found_"
    if not isinstance(data, dict):
        return f"💳 *{upi_id}*\n`{data}`"

    divider = "━" * 28
    lines   = [
        "💳 *UPI Lookup Result*",
        divider,
        f"🆔 *UPI ID:* `{upi_id}`",
    ]

    key_map = {
        "name": ("👤", "Name"), "payeeAccountName": ("👤", "Account Name"),
        "payeeName": ("👤", "Payee Name"), "accountName": ("👤", "Account Name"),
        "customerName": ("👤", "Customer Name"), "bankName": ("🏦", "Bank Name"),
        "bank": ("🏦", "Bank"), "ifsc": ("🏦", "IFSC"),
        "accountNumber": ("🔢", "Account Number"), "vpa": ("💳", "VPA"),
        "upi": ("💳", "UPI"), "mobile": ("📞", "Mobile"), "phone": ("📞", "Phone"),
        "email": ("📧", "Email"), "verified": ("✅", "Verified"),
        "valid": ("✅", "Valid"), "status": ("📊", "Status"),
        "merchant": ("🏪", "Merchant"), "type": ("🔖", "Type"),
    }

    found_data = False
    for key, value in data.items():
        if should_skip(key) or should_skip_value(value):
            continue
        if isinstance(value, dict):
            for sub_k, sub_v in value.items():
                if should_skip(sub_k) or should_skip_value(sub_v):
                    continue
                emoji, label = key_map.get(sub_k, (get_emoji(sub_k.lower()), sub_k.replace("_", " ").title()))
                lines.append(f"{emoji} *{label}*: `{sub_v}`")
                found_data = True
            continue
        emoji, label = key_map.get(key, (get_emoji(key.lower()), key.replace("_", " ").title()))
        lines.append(f"{emoji} *{label}*: `{value}`")
        found_data = True

    if not found_data:
        lines.append("_No relevant data found_")
    lines.append(divider)
    return "\n".join(lines)


# ================== KEYBOARDS ==================
def main_menu_keyboard(user_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Phone Search", callback_data="mode_phone"),
            InlineKeyboardButton("📧 Email Search", callback_data="mode_email"),
        ],
        [
            InlineKeyboardButton("💳 UPI Search", callback_data="mode_upi"),
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
        single_label, batch_label = "🔍 Single (Admin)", "📦 Batch (Admin)"
    else:
        ok, _, _, is_premium, _ = check_phone_access(user_id)
        free_left = get_phone_free_remaining(user_id)
        daily_rem = get_phone_daily_remaining(user_id)
        user_data = get_or_create_user(user_id)
        plan      = get_user_plan_details(user_data)
        if is_premium:
            if plan.get("unlimited", False):
                single_label, batch_label = "🔍 Single (Unlimited)", "📦 Batch (Unlimited)"
            else:
                single_label, batch_label = f"🔍 Single ({daily_rem} today)", f"📦 Batch ({daily_rem} today)"
        elif free_left > 0:
            single_label, batch_label = f"🔍 Single ({free_left} trial)", f"📦 Batch ({free_left} trial)"
        else:
            single_label, batch_label = "🔍 Single (🔒)", "📦 Batch (🔒)"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(single_label, callback_data="phone_single"),
         InlineKeyboardButton(batch_label,  callback_data="phone_batch")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def email_menu_keyboard(user_id: int):
    if is_admin(user_id):
        single_label, batch_label = "🔍 Single (Admin)", "📦 Batch (Admin)"
    else:
        ok, _, _, is_premium = check_email_access(user_id)
        free_left = get_email_free_remaining(user_id)
        if is_premium:
            single_label, batch_label = "🔍 Single (Unlimited)", "📦 Batch (Unlimited)"
        elif free_left > 0:
            single_label, batch_label = f"🔍 Single ({free_left} free)", f"📦 Batch ({free_left} free)"
        else:
            single_label, batch_label = "🔍 Single (🔒)", "📦 Batch (🔒)"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(single_label, callback_data="email_single"),
         InlineKeyboardButton(batch_label,  callback_data="email_batch")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def upi_menu_keyboard(user_id: int):
    if is_admin(user_id):
        single_label, batch_label = "🔍 Single (Admin)", "📦 Batch (Admin)"
    else:
        ok, _, _, is_premium, _ = check_upi_access(user_id)
        free_left = get_upi_free_remaining(user_id)
        daily_rem = get_upi_daily_remaining(user_id)
        user_data = get_or_create_user(user_id)
        plan      = get_user_plan_details(user_data)
        if is_premium:
            if plan.get("unlimited", False):
                single_label, batch_label = "🔍 Single (Unlimited)", "📦 Batch (Unlimited)"
            else:
                single_label, batch_label = f"🔍 Single ({daily_rem} today)", f"📦 Batch ({daily_rem} today)"
        elif free_left > 0:
            single_label, batch_label = f"🔍 Single ({free_left} trial)", f"📦 Batch ({free_left} trial)"
        else:
            single_label, batch_label = "🔍 Single (🔒)", "📦 Batch (🔒)"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(single_label, callback_data="upi_single"),
         InlineKeyboardButton(batch_label,  callback_data="upi_batch")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def country_select_keyboard(mode: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇳 Indian Number (+91)", callback_data=f"country_india_{mode}")],
        [InlineKeyboardButton("🌍 Other Country (Manual Code)", callback_data=f"country_other_{mode}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="main_menu")],
    ])

def admin_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add User", callback_data="admin_add"),
         InlineKeyboardButton("❌ Remove User", callback_data="admin_remove")],
        [InlineKeyboardButton("📅 Set Plan", callback_data="admin_setplan"),
         InlineKeyboardButton("📋 All Users", callback_data="admin_list")],
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
         InlineKeyboardButton("🆓 Free Monitor", callback_data="admin_free_monitor")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]])

def admin_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Menu", callback_data="admin_back")]])

def buy_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Contact Admin", url="https://t.me/" + OWNER_CONTACT.replace("@", ""))],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ])

def plan_select_keyboard(prefix: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉 7 Days  - Rs50", callback_data=f"{prefix}_7days"),
         InlineKeyboardButton("🥈 30 Days - Rs130", callback_data=f"{prefix}_30days")],
        [InlineKeyboardButton("🥇 6 Months - Rs300", callback_data=f"{prefix}_6months"),
         InlineKeyboardButton("💎 12 Months - Rs799", callback_data=f"{prefix}_12months")],
        [InlineKeyboardButton("⚙️ Custom Days Plan", callback_data=f"{prefix}_custom")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_back")],
    ])

def free_monitor_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Phone Trial Users", callback_data="monitor_phone"),
         InlineKeyboardButton("📧 Email Free Users",  callback_data="monitor_email")],
        [InlineKeyboardButton("🔴 All Exhausted",     callback_data="monitor_exhausted"),
         InlineKeyboardButton("🟢 Still Has Searches",callback_data="monitor_active")],
        [InlineKeyboardButton("📊 Full Summary",      callback_data="monitor_summary")],
        [InlineKeyboardButton("🔙 Admin Menu", callback_data="admin_back")],
    ])


# ================== HELPERS ==================
async def safe_edit(query, text, reply_markup=None, parse_mode="Markdown"):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception:
        pass

def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1] and " " not in email

def is_valid_upi(upi: str) -> bool:
    return "@" in upi and len(upi) >= 5 and " " not in upi

def make_bar(filled: int, total: int) -> str:
    filled = max(0, min(filled, total))
    return "█" * filled + "░" * (total - filled)


# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id)

    d1, d2 = "━" * 30, "━" * 25
    if is_admin(user.id):
        text = (
            f"{d1}\n  🔍 *Phone, Email & UPI Lookup Bot*\n{d1}\n\n"
            f"👋 Welcome *{user.first_name}*!\n🛡️ *Admin — Unlimited Access*\n\n"
            f"{d2}\n📱 Phone Search : ∞ Unlimited\n📧 Email Search : ∞ Unlimited\n💳 UPI Search   : ∞ Unlimited\n🔒 Restrictions : None\n{d2}\n\n"
            "Choose search type below 👇"
        )
    else:
        user_data = get_or_create_user(user.id)
        is_prem   = user_data.get("is_premium", False)
        expiry    = user_data.get("expiry", "")
        plan      = get_user_plan_details(user_data)
        p_free    = get_phone_free_remaining(user.id)
        e_free    = get_email_free_remaining(user.id)
        u_free    = get_upi_free_remaining(user.id)

        if is_prem and expiry:
            try:
                exp_date  = date.fromisoformat(expiry)
                days_left = (exp_date - date.today()).days
                if days_left >= 0:
                    p_daily_rem = get_phone_daily_remaining(user.id)
                    u_daily_rem = get_upi_daily_remaining(user.id)
                    daily_limit = plan.get("daily_limit", 0)
                    p_line = f"💎 {plan['name']} | Phone: Unlimited | {days_left}d left" if plan.get("unlimited", False) else f"💎 {plan['name']} | Phone: {p_daily_rem}/{daily_limit} today | {days_left}d left"
                    e_line = f"💎 {plan['name']} | Email: Unlimited | {days_left}d left"
                    u_line = f"💎 {plan['name']} | UPI: Unlimited | {days_left}d left" if plan.get("unlimited", False) else f"💎 {plan['name']} | UPI: {u_daily_rem}/{daily_limit} today | {days_left}d left"
                else:
                    p_line = f"⚠️ Expired | Phone Trial: {'🟢'*p_free}{'🔴'*(PHONE_FREE_SEARCHES-p_free)}"
                    e_line = f"⚠️ Expired | Email Free: {'🟢'*e_free}{'🔴'*(EMAIL_FREE_SEARCHES-e_free)}"
                    u_line = f"⚠️ Expired | UPI Free: {'🟢'*u_free}{'🔴'*(UPI_FREE_SEARCHES-u_free)}"
            except Exception:
                p_line, e_line, u_line = "⚪ Unknown", "⚪ Unknown", "⚪ Unknown"
        else:
            p_line = f"🆓 Trial: {'🟢'*p_free}{'🔴'*(PHONE_FREE_SEARCHES-p_free)} ({p_free}/{PHONE_FREE_SEARCHES})"
            e_line = f"🆓 Free: {'🟢'*e_free}{'🔴'*(EMAIL_FREE_SEARCHES-e_free)} ({e_free}/{EMAIL_FREE_SEARCHES})"
            u_line = f"🆓 Trial: {'🟢'*u_free}{'🔴'*(UPI_FREE_SEARCHES-u_free)} ({u_free}/{UPI_FREE_SEARCHES})"

        text = (
            f"{d1}\n  🔍 *Phone, Email & UPI Lookup Bot*\n{d1}\n\n"
            f"👋 Welcome *{user.first_name}*!\n\n"
            f"{d2}\n📱 *Phone Search*\n{d2}\n{p_line}\n\n"
            f"{d2}\n📧 *Email Search*\n{d2}\n{e_line}\n\n"
            f"{d2}\n💳 *UPI Search*\n{d2}\n{u_line}\n\n"
            "💡 *Ek plan se teeno access milta hai!*\n\n"
            f"{d1}\n\nChoose search type below 👇"
        )

    if update.callback_query:
        await safe_edit(update.callback_query, text, reply_markup=main_menu_keyboard(user.id))
    else:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    return ConversationHandler.END


# ================== MODE SELECT ==================
async def mode_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        ok, _, _, is_premium, _ = check_phone_access(user.id)
        free_left = get_phone_free_remaining(user.id)
        daily_rem = get_phone_daily_remaining(user.id)
        user_data = get_or_create_user(user.id)
        plan      = get_user_plan_details(user_data)
        info = "💎 Unlimited" if is_premium and plan.get("unlimited") else (f"✅ {daily_rem}/{plan.get('daily_limit', 0)} today" if is_premium else f"🆓 {free_left}/{PHONE_FREE_SEARCHES} trial")
    d1 = "━" * 30
    await safe_edit(query, f"{d1}\n   📱 *Phone Number Search*\n{d1}\n\n📊 Status: {info}\n\nSingle ya Batch search choose karo:", reply_markup=phone_menu_keyboard(user.id))

async def mode_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        ok, _, days, is_premium = check_email_access(user.id)
        free_left = get_email_free_remaining(user.id)
        info = f"💎 Premium | {days}d left" if is_premium else f"🆓 {free_left}/{EMAIL_FREE_SEARCHES} free"
    d1 = "━" * 30
    await safe_edit(query, f"{d1}\n   📧 *Email Search*\n{d1}\n\n📊 Status: {info}\n\nSingle ya Batch search choose karo:", reply_markup=email_menu_keyboard(user.id))

async def mode_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        ok, _, _, is_premium, _ = check_upi_access(user.id)
        free_left = get_upi_free_remaining(user.id)
        daily_rem = get_upi_daily_remaining(user.id)
        user_data = get_or_create_user(user.id)
        plan      = get_user_plan_details(user_data)
        info = "💎 Unlimited" if is_premium and plan.get("unlimited") else (f"✅ {daily_rem}/{plan.get('daily_limit', 0)} today" if is_premium else f"🆓 {free_left}/{UPI_FREE_SEARCHES} trial")
    d1 = "━" * 30
    await safe_edit(query, f"{d1}\n   💳 *UPI ID Search*\n{d1}\n\n📊 Status: {info}\n\nSingle ya Batch search choose karo:", reply_markup=upi_menu_keyboard(user.id))


# ================== PROFILE ==================
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user      = query.from_user
    user_data = get_or_create_user(user.id)
    total_s   = user_data.get("total_searches", 0)
    p_total   = user_data.get("phone_total", 0)
    e_total   = user_data.get("email_total", 0)
    u_total   = user_data.get("upi_total", 0)
    d1        = "━" * 30

    if is_admin(user.id):
        text = (
            f"{d1}\n       👤 *Your Profile*\n{d1}\n\n"
            f"🆔 *ID:* `{user.id}`\n👤 *Name:* {user.first_name} {user.last_name or ''}\n"
            f"📛 *Username:* @{user.username or 'N/A'}\n🛡️ *Role:* Admin\n\n{d1}\n"
            "📱 Phone : Unlimited\n📧 Email : Unlimited\n💳 UPI   : Unlimited\n🔒 Limits: None\n\n"
            f"📱 Phone Searches : {p_total}\n📧 Email Searches : {e_total}\n💳 UPI Searches   : {u_total}\n🔍 Total          : {total_s}\n"
        )
        await safe_edit(query, text, reply_markup=back_keyboard())
        return

    is_prem = user_data.get("is_premium", False)
    expiry  = user_data.get("expiry", "")
    plan    = get_user_plan_details(user_data)
    p_free  = get_phone_free_remaining(user.id)
    e_free  = get_email_free_remaining(user.id)
    u_free  = get_upi_free_remaining(user.id)

    if is_prem and expiry:
        try:
            exp_date  = date.fromisoformat(expiry)
            days_left = (exp_date - date.today()).days
            if days_left >= 0:
                bar_len     = 20
                filled      = min(int((days_left / max(plan["days"], 1)) * bar_len), bar_len)
                bar         = make_bar(filled, bar_len)
                p_daily_rem = get_phone_daily_remaining(user.id)
                u_daily_rem = get_upi_daily_remaining(user.id)
                daily_limit = plan.get("daily_limit", 0)
                p_info      = f"💎 {plan['name']} | Unlimited" if plan.get("unlimited") else f"💎 {plan['name']} | {p_daily_rem}/{daily_limit} today"
                u_info      = f"💎 {plan['name']} | Unlimited" if plan.get("unlimited") else f"💎 {plan['name']} | {u_daily_rem}/{daily_limit} today"
                plan_info = (
                    f"📦 *Plan:* {plan['name']}\n📅 *Expiry:* {expiry}\n⏳ *Days Left:* {days_left}\n📈 `[{bar}]`\n\n"
                    f"📱 *Phone:* {p_info}\n📧 *Email:* 💎 Unlimited\n💳 *UPI:* {u_info}\n✅ *Teeno access active!*"
                )
            else:
                plan_info = f"⚠️ *Plan Expired!*\n📱 Phone: {p_free}/{PHONE_FREE_SEARCHES}\n📧 Email: {e_free}/{EMAIL_FREE_SEARCHES}\n💳 UPI: {u_free}/{UPI_FREE_SEARCHES}"
        except Exception:
            plan_info = "⚪ Unknown plan status"
    else:
        plan_info = (
            f"📦 *Plan:* Free/Trial\n\n"
            f"📱 *Phone Trial:* {'🟢'*p_free}{'🔴'*(PHONE_FREE_SEARCHES-p_free)} ({p_free}/{PHONE_FREE_SEARCHES})\n"
            f"📧 *Email Free:*  {'🟢'*e_free}{'🔴'*(EMAIL_FREE_SEARCHES-e_free)} ({e_free}/{EMAIL_FREE_SEARCHES})\n"
            f"💳 *UPI Trial:*   {'🟢'*u_free}{'🔴'*(UPI_FREE_SEARCHES-u_free)} ({u_free}/{UPI_FREE_SEARCHES})\n\n"
            "💡 Ek plan lo — teeno unlock!"
        )

    text = (
        f"{d1}\n       👤 *Your Profile*\n{d1}\n\n"
        f"🆔 *ID:* `{user.id}`\n👤 *Name:* {user.first_name} {user.last_name or ''}\n"
        f"📛 *Username:* @{user.username or 'N/A'}\n\n{d1}\n       🔐 *Account Info*\n{d1}\n\n"
        f"{plan_info}\n\n{d1}\n"
        f"📱 Phone Searches : {p_total}\n📧 Email Searches : {e_total}\n💳 UPI Searches   : {u_total}\n🔍 Total          : {total_s}\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== STATUS ==================
async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    d1, d2 = "━" * 30, "━" * 25

    if is_admin(user.id):
        user_data = get_or_create_user(user.id)
        text = f"{d1}\n       🛡️ *Admin Status*\n{d1}\n\n📱 *Phone* : Unlimited\n📧 *Email* : Unlimited\n💳 *UPI*   : Unlimited\n🔒 Limits  : None\n\n🔍 Total: {user_data.get('total_searches', 0)}\n\n✅ Full access!"
        await safe_edit(query, text, reply_markup=back_keyboard())
        return

    p_ok, _, p_days, p_premium, _ = check_phone_access(user.id)
    _, _, e_days, _               = check_email_access(user.id)
    u_ok, _, u_days, u_premium, _ = check_upi_access(user.id)
    user_data = get_or_create_user(user.id)
    plan      = get_user_plan_details(user_data)

    if p_premium:
        p_daily_rem = get_phone_daily_remaining(user.id)
        u_daily_rem = get_upi_daily_remaining(user.id)
        daily_limit = plan.get("daily_limit", 0)
        p_line = f"💎 {plan['name']} | Phone: Unlimited | {p_days}d left" if plan.get("unlimited") else f"💎 {plan['name']} | Phone: {p_daily_rem}/{daily_limit} | {p_days}d left"
        e_line = f"💎 Email: Unlimited | {e_days}d left"
        u_line = f"💎 UPI: Unlimited | {u_days}d left" if plan.get("unlimited") else f"💎 UPI: {u_daily_rem}/{daily_limit} | {u_days}d left"
        note   = "✅ Teeno access active hai!"
    else:
        p_line = f"🆓 Phone Trial: {get_phone_free_remaining(user.id)}/{PHONE_FREE_SEARCHES}"
        e_line = f"🆓 Email Free: {get_email_free_remaining(user.id)}/{EMAIL_FREE_SEARCHES}"
        u_line = f"🆓 UPI Trial: {get_upi_free_remaining(user.id)}/{UPI_FREE_SEARCHES}"
        note   = "💡 Ek plan lo — teeno unlock!"

    text = f"{d1}\n       📊 *Account Status*\n{d1}\n\n{p_line}\n{e_line}\n{u_line}\n\n{note}\n\n{d2}\n💰 Buy: {OWNER_CONTACT}\nYour ID: `{user.id}`"
    await safe_edit(query, text, reply_markup=back_keyboard())


# ================== HELP & BUY ==================
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    d1, d2 = "━" * 30, "━" * 25
    text = (
        f"{d1}\n       ❓ *Help Guide*\n{d1}\n\n"
        "🎯 *Ek Plan = Teeno Access!*\n_(Phone + Email + UPI unlock)_\n\n"
        f"{d2}\n📋 *Plans:*\n{d2}\n"
        "🥉 7 Days    Rs50  | Phone: 5/day  | UPI: 5/day   | Email: Unlimited\n"
        "🥈 30 Days   Rs130 | Phone: 10/day | UPI: 10/day  | Email: Unlimited\n"
        "🥇 6 Months  Rs300 | Phone: 15/day | UPI: 15/day  | Email: Unlimited\n"
        "💎 12 Months Rs799 | All Unlimited\n\n"
        f"{d2}\n🆓 *Free Trial:*\n{d2}\n"
        f"📱 Phone: {PHONE_FREE_SEARCHES} searches\n📧 Email: {EMAIL_FREE_SEARCHES} searches\n💳 UPI:   {UPI_FREE_SEARCHES} searches\n\n"
        f"{d2}\n💳 *UPI Tips:*\n{d2}\n"
        "Format: `username@bankname`\nExample: `ansh@paytm`\n\n"
        f"{d1}\n📦 Batch: Comma separated, Max 15\n"
    )
    await safe_edit(query, text, reply_markup=back_keyboard())

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if is_admin(user.id):
        await safe_edit(query, "🛡️ *You are Admin!*\n\n✅ Unlimited access\n📱 Phone: ∞\n📧 Email: ∞\n💳 UPI: ∞\n\nNo plan needed!", reply_markup=back_keyboard())
        return
    d1 = "━" * 30
    text = (
        f"{d1}\n       💰 *Buy Plan*\n{d1}\n\n"
        "🎯 *Ek Plan = Phone + Email + UPI!*\n\n"
        f"{d1}\n\n"
        "🥉 *7 Days*    - Rs50\n   📱 Phone: 5/day\n   💳 UPI: 5/day\n   📧 Email: Unlimited\n\n"
        "🥈 *30 Days*   - Rs130\n   📱 Phone: 10/day\n   💳 UPI: 10/day\n   📧 Email: Unlimited\n\n"
        "🥇 *6 Months*  - Rs300\n   📱 Phone: 15/day\n   💳 UPI: 15/day\n   📧 Email: Unlimited\n\n"
        "💎 *12 Months* - Rs799\n   All Unlimited\n\n"
        f"{d1}\n\n📱 Contact: {OWNER_CONTACT}\nYour ID: `{user.id}`\n_Admin ko ye ID bhejo_"
    )
    await safe_edit(query, text, reply_markup=buy_keyboard())


# ==================== PHONE SEARCH ====================
async def phone_single_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ok, status, _, is_premium, _ = check_phone_access(user.id)
    if not ok:
        await safe_edit(query, f"🔒 *Phone Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}\nYour ID: `{user.id}`", reply_markup=buy_keyboard())
        return ConversationHandler.END
    await safe_edit(query, "📱 *Phone Single Search*\n\n📍 Number kahan ka hai?\n\n🇮🇳 India  10 digit (91 auto)\n🌍 Other   Country code + number", reply_markup=country_select_keyboard("single"))
    return PHONE_COUNTRY_SINGLE

async def phone_batch_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ok, status, _, is_premium, _ = check_phone_access(user.id)
    if not ok:
        await safe_edit(query, f"🔒 *Phone Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}", reply_markup=buy_keyboard())
        return ConversationHandler.END
    await safe_edit(query, "📦 *Phone Batch Search*\n\n📍 Numbers kahan ke hain?\n\n🇮🇳 India  10 digit each (91 auto)\n🌍 Other   Country code + number", reply_markup=country_select_keyboard("batch"))
    return PHONE_COUNTRY_BATCH

async def country_selected_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if "india" in query.data:
        context.user_data["phone_country"] = "india"
        await safe_edit(query, "🇮🇳 *Indian Number Search*\n\n📱 Sirf *10 digit* daalo:\n_(91 auto lag jayega)_\n\n/cancel to go back")
        return PHONE_SINGLE_INDIA
    else:
        context.user_data["phone_country"] = "other"
        await safe_edit(query, "🌍 *Other Country Search*\n\n📱 Country code + Number:\n\n/cancel to go back")
        return PHONE_SINGLE_OTHER

async def country_selected_batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if "india" in query.data:
        context.user_data["phone_country"] = "india"
        await safe_edit(query, "🇮🇳 *Indian Batch Search*\n\n📱 10 digit numbers, comma se:\n\n/cancel to go back")
        return PHONE_BATCH_INDIA
    else:
        context.user_data["phone_country"] = "other"
        await safe_edit(query, "🌍 *Other Country Batch*\n\n📱 Country code + numbers, comma se:\n\n/cancel to go back")
        return PHONE_BATCH_OTHER

async def phone_single_india(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw   = update.message.text.strip()
    clean = raw.replace(" ", "").replace("-", "").replace("+", "")
    if clean.startswith("91") and len(clean) == 12:
        clean = clean[2:]
    if not clean.isdigit() or len(clean) != 10:
        await update.message.reply_text("❌ 10 digit Indian number daalo!\nTry again or /cancel")
        return PHONE_SINGLE_INDIA
    await _do_phone_single(update, context, "91" + clean, "🇮🇳 91" + clean)
    return ConversationHandler.END

async def phone_single_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clean = update.message.text.strip().replace(" ", "").replace("-", "").replace("+", "")
    if not clean.isdigit() or not (7 <= len(clean) <= 15):
        await update.message.reply_text("❌ 7-15 digit number daalo!\nTry again or /cancel")
        return PHONE_SINGLE_OTHER
    await _do_phone_single(update, context, clean, "🌍 " + clean)
    return ConversationHandler.END

async def phone_batch_india(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_nums = [n.strip().replace(" ", "").replace("-", "").replace("+", "") for n in update.message.text.split(",") if n.strip()]
    valid = []
    for num in raw_nums:
        if num.startswith("91") and len(num) == 12:
            num = num[2:]
        if num.isdigit() and len(num) == 10 and ("91"+num) not in valid:
            valid.append("91" + num)
    if not valid:
        await update.message.reply_text("❌ Koi valid Indian number nahi!\nTry again or /cancel")
        return PHONE_BATCH_INDIA
    await _do_phone_batch(update, context, valid[:15], "india")
    return ConversationHandler.END

async def phone_batch_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_nums = [n.strip().replace(" ", "").replace("-", "").replace("+", "") for n in update.message.text.split(",") if n.strip()]
    valid = [num for num in raw_nums if num.isdigit() and 7 <= len(num) <= 15]
    if not valid:
        await update.message.reply_text("❌ Koi valid number nahi!\nTry again or /cancel")
        return PHONE_BATCH_OTHER
    await _do_phone_batch(update, context, valid[:15], "other")
    return ConversationHandler.END

async def _do_phone_single(update, context, number, display):
    user = update.effective_user
    ok, status, _, is_premium, _ = check_phone_access(user.id)
    if not ok:
        await update.message.reply_text(f"🔒 *Locked!*\n{status}\n💰 {OWNER_CONTACT}", reply_markup=buy_keyboard(), parse_mode="Markdown")
        return
    msg = await update.message.reply_text(f"🔍 Searching `{display}`...", parse_mode="Markdown")
    result = search_api(number)
    if result["ok"]:
        use_phone_search(user.id)
        text = format_result(display, result["data"], "📱")
        await msg.edit_text(text, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    else:
        await msg.edit_text(f"❌ *Search Failed*\n`{result['error']}`", reply_markup=back_keyboard(), parse_mode="Markdown")

async def _do_phone_batch(update, context, numbers, country):
    user  = update.effective_user
    ok, status, _, is_premium, plan_key = check_phone_access(user.id)
    user_data = get_or_create_user(user.id)
    plan      = get_user_plan_details(user_data)
    total     = len(numbers)
    if is_admin(user.id):
        available = 999999
    elif plan.get("unlimited", False):
        available = 999999
    elif is_premium:
        available = get_phone_daily_remaining(user.id)
    else:
        available = get_phone_free_remaining(user.id)
    if total > available:
        await update.message.reply_text(f"❌ *Searches kam hain!*\n\nNumbers: *{total}* | Available: *{available}*\n\n👉 {OWNER_CONTACT}", reply_markup=buy_keyboard(), parse_mode="Markdown")
        return
    flag = "🇮🇳" if country == "india" else "🌍"
    msg = await update.message.reply_text(f"{flag} Processing {total} numbers...\n[{'░'*total}]")
    for i, num in enumerate(numbers, 1):
        result = search_api(num)
        display = f"{flag} {num}"
        if result["ok"]:
            use_phone_search(user.id)
            await update.message.reply_text(format_result(display, result["data"], "📱"), parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ *{display}*\n`{result['error']}`", parse_mode="Markdown")
        try:
            await msg.edit_text(f"{flag} Processing... ({i}/{total})\n[{'█'*i}{'░'*(total-i)}]")
        except Exception:
            pass
    await msg.edit_text(f"✅ *Batch Done!*\n📊 Processed: {total}", reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")


# ==================== EMAIL SEARCH ====================
async def email_single_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ok, status, _, _ = check_email_access(query.from_user.id)
    if not ok:
        await safe_edit(query, f"🔒 *Email Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}", reply_markup=buy_keyboard())
        return ConversationHandler.END
    await safe_edit(query, "📧 *Email Single Search*\n\n📧 Email address daalo:\n_Example: user@gmail.com_\n\n/cancel to go back")
    return EMAIL_SINGLE

async def email_single_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    user  = update.effective_user
    if not is_valid_email(email):
        await update.message.reply_text("❌ Invalid Email!\nTry again or /cancel")
        return EMAIL_SINGLE
    ok, status, _, is_premium = check_email_access(user.id)
    if not ok:
        await update.message.reply_text(f"🔒 *Locked!*\n{status}\n💰 {OWNER_CONTACT}", reply_markup=buy_keyboard(), parse_mode="Markdown")
        return ConversationHandler.END
    msg = await update.message.reply_text("🔍 Searching...")
    result = search_api(email)
    if result["ok"]:
        use_email_search(user.id, is_premium)
        await msg.edit_text(format_result(email, result["data"], "📧"), reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    else:
        await msg.edit_text(f"❌ *Search Failed*\n`{result['error']}`", reply_markup=back_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def email_batch_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ok, status, _, _ = check_email_access(query.from_user.id)
    if not ok:
        await safe_edit(query, f"🔒 *Email Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}", reply_markup=buy_keyboard())
        return ConversationHandler.END
    await safe_edit(query, "📦 *Email Batch Search*\n\n📧 Emails comma se daalo (Max 15):\n/cancel to go back")
    return EMAIL_BATCH

async def email_batch_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_emails = [e.strip() for e in update.message.text.split(",") if is_valid_email(e.strip())][:15]
    if not raw_emails:
        await update.message.reply_text("❌ No valid emails!\nTry again or /cancel")
        return EMAIL_BATCH
    user = update.effective_user
    ok, _, _, is_premium = check_email_access(user.id)
    msg = await update.message.reply_text(f"🚀 Processing {len(raw_emails)} emails...")
    for em in raw_emails:
        res = search_api(em)
        if res["ok"]:
            use_email_search(user.id, is_premium)
            await update.message.reply_text(format_result(em, res["data"], "📧"), parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ *{em}*\n`{res['error']}`", parse_mode="Markdown")
    await msg.edit_text(f"✅ *Batch Complete!*\n📊 Processed: {len(raw_emails)}", reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    return ConversationHandler.END


# ==================== UPI SEARCH (WITH DAILY LIMIT) ====================
async def upi_single_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ok, status, _, is_premium, _ = check_upi_access(user.id)
    if not ok:
        await safe_edit(query, f"🔒 *UPI Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}\nYour ID: `{user.id}`", reply_markup=buy_keyboard())
        return ConversationHandler.END
    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        free_left = get_upi_free_remaining(user.id)
        daily_rem = get_upi_daily_remaining(user.id)
        user_data = get_or_create_user(user.id)
        plan      = get_user_plan_details(user_data)
        if is_premium:
            info = "💎 Unlimited" if plan.get("unlimited") else f"✅ {daily_rem}/{plan.get('daily_limit', 0)} today"
        else:
            info = f"🆓 {free_left}/{UPI_FREE_SEARCHES} trial"
    await safe_edit(query, f"💳 *UPI Single Search*\n\n📊 {info}\n\n💳 UPI ID daalo:\n✅ `ansh@paytm`\n✅ `9876543210@ybl`\n✅ `name@oksbi`\n\n/cancel to go back")
    return UPI_SINGLE

async def upi_single_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    upi_id = update.message.text.strip()
    user   = update.effective_user
    if not is_valid_upi(upi_id):
        await update.message.reply_text("❌ Invalid UPI ID! Format: `name@bank`\nTry again or /cancel", parse_mode="Markdown")
        return UPI_SINGLE
    ok, status, _, is_premium, plan_key = check_upi_access(user.id)
    if not ok:
        await update.message.reply_text(f"🔒 *Locked!*\n{status}\n💰 {OWNER_CONTACT}", reply_markup=buy_keyboard(), parse_mode="Markdown")
        return ConversationHandler.END
    msg = await update.message.reply_text(f"🔍 Searching UPI `{upi_id}`...", parse_mode="Markdown")
    result = upi_search_api(upi_id)
    if result["ok"]:
        use_upi_search(user.id)
        text = format_upi_result(upi_id, result["data"])
        divider = "━" * 25
        if is_admin(user.id):
            text += f"\n🛡️ Admin Search"
        elif is_premium:
            user_data = get_or_create_user(user.id)
            plan      = get_user_plan_details(user_data)
            daily_rem = get_upi_daily_remaining(user.id)
            if not plan.get("unlimited", False):
                text += f"\n📊 Today: *{daily_rem}/{plan.get('daily_limit', 0)}*"
        else:
            free_left = get_upi_free_remaining(user.id)
            text += f"\n🆓 Trial: *{free_left}/{UPI_FREE_SEARCHES}*"
        await msg.edit_text(text, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    else:
        await msg.edit_text(f"❌ *UPI Search Failed*\n`{result['error']}`", reply_markup=back_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def upi_batch_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ok, status, _, is_premium, _ = check_upi_access(user.id)
    if not ok:
        await safe_edit(query, f"🔒 *UPI Search Locked!*\n\n{status}\n\n💰 {OWNER_CONTACT}", reply_markup=buy_keyboard())
        return ConversationHandler.END
    if is_admin(user.id):
        info = "🛡️ Admin — Unlimited"
    else:
        free_left = get_upi_free_remaining(user.id)
        daily_rem = get_upi_daily_remaining(user.id)
        user_data = get_or_create_user(user.id)
        plan      = get_user_plan_details(user_data)
        if is_premium:
            info = "💎 Unlimited" if plan.get("unlimited") else f"✅ {daily_rem}/{plan.get('daily_limit', 0)} today"
        else:
            info = f"🆓 {free_left}/{UPI_FREE_SEARCHES} trial"
    await safe_edit(query, f"📦 *UPI Batch Search*\n\n📊 {info}\n\n💳 UPI IDs comma se daalo (Max 15):\n/cancel to go back")
    return UPI_BATCH

async def upi_batch_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    upis = [u.strip() for u in update.message.text.split(",") if is_valid_upi(u.strip())][:15]
    if not upis:
        await update.message.reply_text("❌ No valid UPI IDs!\nTry again or /cancel")
        return UPI_BATCH
    user  = update.effective_user
    ok, status, _, is_premium, plan_key = check_upi_access(user.id)
    user_data = get_or_create_user(user.id)
    plan      = get_user_plan_details(user_data)
    total     = len(upis)
    if is_admin(user.id):
        available = 999999
    elif plan.get("unlimited", False):
        available = 999999
    elif is_premium:
        available = get_upi_daily_remaining(user.id)
    else:
        available = get_upi_free_remaining(user.id)
    if total > available:
        await update.message.reply_text(f"❌ *Searches kam hain!*\n\nUPIs: *{total}* | Available: *{available}*\n\n👉 {OWNER_CONTACT}", reply_markup=buy_keyboard(), parse_mode="Markdown")
        return ConversationHandler.END
    msg = await update.message.reply_text(f"💳 Processing {total} UPI IDs...")
    for i, u in enumerate(upis, 1):
        res = upi_search_api(u)
        if res["ok"]:
            use_upi_search(user.id)
            await update.message.reply_text(format_upi_result(u, res["data"]), parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ *{u}*\n`{res['error']}`", parse_mode="Markdown")
        try:
            await msg.edit_text(f"💳 Processing... ({i}/{total})")
        except Exception:
            pass
    if is_admin(user.id):
        summary = f"✅ *UPI Batch Complete!*\n📊 Processed: {total}\n🛡️ Admin"
    elif is_premium and not plan.get("unlimited", False):
        daily_rem = get_upi_daily_remaining(user.id)
        summary   = f"✅ *UPI Batch Complete!*\n📊 Processed: {total}\n📊 Today Left: *{daily_rem}/{plan.get('daily_limit', 0)}*"
    elif not is_premium:
        free_left = get_upi_free_remaining(user.id)
        summary   = f"✅ *UPI Batch Complete!*\n📊 Processed: {total}\n🆓 Trial Left: *{free_left}/{UPI_FREE_SEARCHES}*"
    else:
        summary = f"✅ *UPI Batch Complete!*\n📊 Processed: {total}"
    await msg.edit_text(summary, reply_markup=main_menu_keyboard(user.id), parse_mode="Markdown")
    return ConversationHandler.END


# ================== CANCEL ==================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled.", reply_markup=main_menu_keyboard(update.effective_user.id))
    return ConversationHandler.END


# ==================== ADMIN PANEL ====================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        if update.message:
            await update.message.reply_text("❌ Admin only!")
        return ConversationHandler.END
    users = load_users()
    total = len(users)
    prem  = sum(1 for u in users.values() if u.get("is_premium", False))
    d1    = "━" * 30
    text  = (
        f"{d1}\n       🛠️ *Admin Panel*\n{d1}\n\n"
        f"🛡️ Admins     : {len(ADMIN_IDS)}\n👥 Total Users : {total}\n"
        f"💎 Premium     : {prem}\n🆓 Trial/Free  : {total - prem}\n\n"
        "✅ *Ek plan = teeno access*\n\nChoose action:"
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
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "➕ *Add Premium User*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_ADD_ID

async def admin_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ Invalid ID!\n/cancel to stop")
        return ADMIN_ADD_ID
    context.user_data["admin_uid"] = uid
    await update.message.reply_text(f"✅ User: `{uid}`\nPlan select karo:", reply_markup=plan_select_keyboard("plan"), parse_mode="Markdown")
    return ADMIN_ADD_PLAN

async def admin_add_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_back":
        await admin_panel(update, context)
        return ConversationHandler.END
    plan_map = {"plan_7days": "7days", "plan_30days": "30days", "plan_6months": "6months", "plan_12months": "12months"}
    plan_key = plan_map.get(query.data, "7days")
    uid      = context.user_data.get("admin_uid")
    plan     = PLANS.get(plan_key)
    expiry   = upgrade_user(int(uid), plan_key)
    daily_info = "Unlimited" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(query, f"✅ *Plan Added to Cloud DB!*\n\n🆔 `{uid}`\n📦 {plan['name']}\n📅 Expiry: {expiry}\n\n📱 Phone: {daily_info}\n💳 UPI: {daily_info}\n📧 Email: Unlimited", reply_markup=admin_menu_keyboard())
    return ConversationHandler.END

async def admin_remove_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "❌ *Remove User*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_REM_ID

async def admin_remove_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    delete_user_from_db(uid)
    await update.message.reply_text(f"✅ `{uid}` removed from Cloud Database!", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def admin_setplan_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return ConversationHandler.END
    await query.answer()
    await safe_edit(query, "📅 *Set User Plan*\n\nUser ID daalo:\n\n/cancel to go back")
    return ADMIN_EXP_ID

async def admin_setplan_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text.strip()
    context.user_data["admin_uid"] = uid
    await update.message.reply_text(f"User: `{uid}`\nPlan select karo:", reply_markup=plan_select_keyboard("plan"), parse_mode="Markdown")
    return ADMIN_EXP_PLAN

async def admin_setplan_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_back":
        await admin_panel(update, context)
        return ConversationHandler.END
    plan_map = {"plan_7days": "7days", "plan_30days": "30days", "plan_6months": "6months", "plan_12months": "12months"}
    plan_key = plan_map.get(query.data, "7days")
    uid      = context.user_data.get("admin_uid")
    plan     = PLANS.get(plan_key)
    expiry   = upgrade_user(int(uid), plan_key)
    daily_info = "Unlimited" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(query, f"✅ *Plan Updated in Cloud DB!*\n\n🆔 `{uid}`\n📦 {plan['name']}\n📅 Expiry: {expiry}\n\n📱 Phone: {daily_info}\n💳 UPI: {daily_info}\n📧 Email: Unlimited", reply_markup=admin_menu_keyboard())
    return ConversationHandler.END

async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return
    await query.answer()
    users = load_users()
    if not users:
        await safe_edit(query, "📋 *No users yet!*", reply_markup=admin_menu_keyboard())
        return
    d1 = "━" * 30
    text = f"{d1}\n📋 *All Users in Cloud DB ({len(users)})*\n{d1}\n\n"
    for uid, info in users.items():
        is_prem = info.get("is_premium", False)
        plan    = get_user_plan_details(info)
        total_s = info.get("total_searches", 0)
        expiry  = info.get("expiry", "")
        if int(uid) in ADMIN_IDS:
            badge, status = " 🛡️", "∞ Admin"
        elif is_prem and expiry:
            try:
                ed = date.fromisoformat(expiry)
                status = f"💎{plan['name']} {(ed - date.today()).days}d" if date.today() <= ed else "🔴 Expired"
            except Exception:
                status = "⚪ N/A"
            badge = ""
        else:
            status = f"🆓P:{max(0, PHONE_FREE_SEARCHES-info.get('phone_free_used', 0))} E:{max(0, EMAIL_FREE_SEARCHES-info.get('email_free_used', 0))} U:{max(0, UPI_FREE_SEARCHES-info.get('upi_free_used', 0))}"
            badge  = ""
        text += f"`{uid}`{badge} | {status} | 🔍{total_s}\n"
    await safe_edit(query, text[:4000], reply_markup=admin_menu_keyboard())

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return
    await query.answer()
    users = load_users()
    total_searches, active, expired, trial = 0, 0, 0, 0
    plan_counts = {k: 0 for k in PLANS}
    plan_counts["custom"] = 0
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
                    if pk.startswith("custom_"):
                        plan_counts["custom"] += 1
                    else:
                        plan_counts[pk] = plan_counts.get(pk, 0) + 1
                else:
                    expired += 1
            except Exception:
                expired += 1
        else:
            trial += 1
    d1, d2 = "━" * 30, "━" * 25
    text = (
        f"{d1}\n       📊 *Cloud DB Statistics*\n{d1}\n\n"
        f"👥 Total Users    : {len(users)}\n🔍 Total Searches : {total_searches}\n🛡️ Admins (∞)     : {len(ADMIN_IDS)}\n\n"
        f"{d2}\n💎 Active Premium : {active}\n🔴 Expired        : {expired}\n🆓 Trial/Free     : {trial}\n\n"
        f"Plan Breakdown:\n  🥉 7D  : {plan_counts.get('7days', 0)}\n  🥈 30D : {plan_counts.get('30days', 0)}\n  🥇 6M  : {plan_counts.get('6months', 0)}\n  💎 12M : {plan_counts.get('12months', 0)}\n  ⚙️ Custom: {plan_counts.get('custom', 0)}\n\n📅 {date.today()}\n"
    )
    await safe_edit(query, text, reply_markup=admin_menu_keyboard())


# ==================== FREE MONITOR ====================
async def admin_free_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return
    await query.answer()
    users = load_users()
    free_users = [(uid, info) for uid, info in users.items() if not info.get("is_premium", False) and int(uid) not in ADMIN_IDS]
    p_has  = sum(1 for _, i in free_users if i.get("phone_free_used", 0) < PHONE_FREE_SEARCHES)
    p_done = sum(1 for _, i in free_users if i.get("phone_free_used", 0) >= PHONE_FREE_SEARCHES)
    e_has  = sum(1 for _, i in free_users if i.get("email_free_used", 0) < EMAIL_FREE_SEARCHES)
    e_done = sum(1 for _, i in free_users if i.get("email_free_used", 0) >= EMAIL_FREE_SEARCHES)
    u_has  = sum(1 for _, i in free_users if i.get("upi_free_used", 0) < UPI_FREE_SEARCHES)
    u_done = sum(1 for _, i in free_users if i.get("upi_free_used", 0) >= UPI_FREE_SEARCHES)
    d1, d2 = "━" * 30, "━" * 25
    text = (
        f"{d1}\n   🆓 *Free / Trial Monitor*\n{d1}\n\n"
        f"👥 Total Free Users: {len(free_users)}\n\n"
        f"{d2}\n📱 *Phone Trial*\n{d2}\n🟢 Has: {p_has} | 🔴 Done: {p_done}\n\n"
        f"{d2}\n📧 *Email Free*\n{d2}\n🟢 Has: {e_has} | 🔴 Done: {e_done}\n\n"
        f"{d2}\n💳 *UPI Trial*\n{d2}\n🟢 Has: {u_has} | 🔴 Done: {u_done}\n\nChoose filter below 👇"
    )
    await safe_edit(query, text, reply_markup=free_monitor_keyboard())

async def monitor_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return
    await query.answer()
    users = load_users()
    text  = "━" * 30 + "\n📱 *Phone Trial Users*\n" + "━" * 30 + "\n\n"
    count = 0
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium", False):
            continue
        p_used, p_left = info.get("phone_free_used", 0), max(0, PHONE_FREE_SEARCHES - info.get("phone_free_used", 0))
        text += f"{'🟢' if p_left > 0 else '🔴'} `{uid}` ({p_left}/{PHONE_FREE_SEARCHES}) 🔍{info.get('total_searches', 0)}\n"
        count += 1
    text += f"\nTotal: {count} users"
    await safe_edit(query, text[:4000], reply_markup=free_monitor_keyboard())

async def monitor_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return
    await query.answer()
    users = load_users()
    text  = "━" * 30 + "\n📧 *Email Free Users*\n" + "━" * 30 + "\n\n"
    count = 0
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium", False):
            continue
        e_used, e_left = info.get("email_free_used", 0), max(0, EMAIL_FREE_SEARCHES - info.get("email_free_used", 0))
        text += f"{'🟢' if e_left > 0 else '🔴'} `{uid}` ({e_left}/{EMAIL_FREE_SEARCHES}) 🔍{info.get('total_searches', 0)}\n"
        count += 1
    text += f"\nTotal: {count} users"
    await safe_edit(query, text[:4000], reply_markup=free_monitor_keyboard())

async def monitor_exhausted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return
    await query.answer()
    users = load_users()
    text  = "━" * 30 + "\n🔴 *All Searches Used Up*\n" + "━" * 30 + "\n\n"
    count = 0
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium", False):
            continue
        if max(0, PHONE_FREE_SEARCHES-info.get("phone_free_used", 0)) <= 0 and max(0, EMAIL_FREE_SEARCHES-info.get("email_free_used", 0)) <= 0 and max(0, UPI_FREE_SEARCHES-info.get("upi_free_used", 0)) <= 0:
            text += f"🔴 `{uid}` | 🔍 {info.get('total_searches', 0)}\n"
            count += 1
    text += f"\n💡 *{count} users* potential buyers!\nContact: {OWNER_CONTACT}"
    await safe_edit(query, text[:4000], reply_markup=free_monitor_keyboard())

async def monitor_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return
    await query.answer()
    users = load_users()
    text  = "━" * 30 + "\n🟢 *Active Free Users*\n" + "━" * 30 + "\n\n"
    count = 0
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium", False):
            continue
        pf = max(0, PHONE_FREE_SEARCHES-info.get("phone_free_used", 0))
        ef = max(0, EMAIL_FREE_SEARCHES-info.get("email_free_used", 0))
        uf = max(0, UPI_FREE_SEARCHES-info.get("upi_free_used", 0))
        if pf > 0 or ef > 0 or uf > 0:
            text += f"🟢 `{uid}` (P:{pf} E:{ef} U:{uf})\n"
            count += 1
    text += f"\nTotal Active: {count}"
    await safe_edit(query, text[:4000], reply_markup=free_monitor_keyboard())

async def monitor_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return
    await query.answer()
    users = load_users()
    total_users, both_exhausted = 0, []
    for uid, info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium", False):
            continue
        total_users += 1
        if max(0, PHONE_FREE_SEARCHES-info.get("phone_free_used", 0)) <= 0 and max(0, EMAIL_FREE_SEARCHES-info.get("email_free_used", 0)) <= 0 and max(0, UPI_FREE_SEARCHES-info.get("upi_free_used", 0)) <= 0:
            both_exhausted.append(uid)
    text = (
        f"{'━'*30}\n   📊 *Free Users Summary*\n{'━'*30}\n\n"
        f"👥 Total Free/Trial: {total_users}\n🔴 All exhausted : {len(both_exhausted)}\n\n"
        f"📅 {date.today()}"
    )
    await safe_edit(query, text[:4000], reply_markup=free_monitor_keyboard())


# ==================== 📢 BROADCAST ====================
async def admin_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return ConversationHandler.END
    await query.answer()
    users = load_users()
    d1 = "━" * 30
    await safe_edit(query, f"{d1}\n   📢 *Broadcast Message*\n{d1}\n\n👥 Total Recipients: *{len(users)}*\n\n📝 Message likho:\n\n/cancel to go back")
    return ADMIN_BROADCAST_MSG

async def admin_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()
    if not message:
        await update.message.reply_text("❌ Empty message!\nTry again or /cancel")
        return ADMIN_BROADCAST_MSG
    context.user_data["broadcast_msg"] = message
    users = load_users()
    d1 = "━" * 30
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Yes, Send!", callback_data="broadcast_confirm"), InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]])
    await update.message.reply_text(f"{d1}\n   📢 *Broadcast Preview*\n{d1}\n\n{message}\n\n👥 Recipients: *{len(users)} users*\n\n⚠️ Sure bhejna hai?", reply_markup=keyboard, parse_mode="Markdown")
    return ADMIN_BROADCAST_CONFIRM

async def admin_broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "broadcast_cancel":
        await safe_edit(query, "❌ *Broadcast Cancelled!*", reply_markup=admin_menu_keyboard())
        context.user_data.pop("broadcast_msg", None)
        return ConversationHandler.END
    message = context.user_data.get("broadcast_msg", "")
    users = load_users()
    total = len(users)
    broadcast_text = f"📢 *Announcement*\n{'━'*25}\n\n{message}\n\n{'━'*25}\n💬 {OWNER_CONTACT}"
    status_msg = await query.message.reply_text(f"🚀 *Broadcasting to {total} users...*", parse_mode="Markdown")
    sent, failed, blocked, count = 0, 0, 0, 0
    for uid in users.keys():
        count += 1
        try:
            await context.bot.send_message(chat_id=int(uid), text=broadcast_text, parse_mode="Markdown")
            sent += 1
        except Exception as e:
            err_str = str(e).lower()
            if "blocked" in err_str or "forbidden" in err_str or "not found" in err_str:
                blocked += 1
            else:
                failed += 1
        if count % 10 == 0 or count == total:
            try:
                await status_msg.edit_text(f"🚀 *Broadcasting...*\n\n📊 Progress: {count}/{total}\n✅ Sent: {sent}\n🚫 Blocked: {blocked}\n❌ Failed: {failed}", parse_mode="Markdown")
            except Exception:
                pass
    await status_msg.edit_text(f"✅ *Broadcast Complete!*\n\n👥 Total: {total}\n✅ Sent: {sent}\n🚫 Blocked: {blocked}\n❌ Failed: {failed}\n\n📅 {date.today()}", reply_markup=admin_menu_keyboard(), parse_mode="Markdown")
    context.user_data.pop("broadcast_msg", None)
    return ConversationHandler.END


# ==================== ⚙️ CUSTOM PLAN ====================
async def admin_custom_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await safe_edit(query, "⚙️ *Custom Plan Creator*\n\nKitne din *(Days)* ka plan?\n_(eg: `45` ya `150`)_\n\n👉 /cancel to abort.")
    return ADMIN_CUSTOM_DAYS

async def admin_custom_days_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await update.message.reply_text("❌ Valid number of days daalo!\nTry again or /cancel")
        return ADMIN_CUSTOM_DAYS
    context.user_data["custom_days"] = int(text)
    await update.message.reply_text(f"📅 Days: *{text}*\n\nAb *Daily Limit* daalo (0 for unlimited):\n_(Ye limit Phone aur UPI dono par apply hogi)_\n\n/cancel to abort.", parse_mode="Markdown")
    return ADMIN_CUSTOM_LIMIT

async def admin_custom_limit_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ Valid limit daalo!\nTry again or /cancel")
        return ADMIN_CUSTOM_LIMIT
    limit        = int(text)
    is_unlimited = (limit == 0)
    days         = context.user_data.get("custom_days")
    uid          = context.user_data.get("admin_uid")
    expiry       = upgrade_user_custom(int(uid), days, limit, is_unlimited)
    limit_str    = "Unlimited" if is_unlimited else f"{limit}/day"
    await update.message.reply_text(
        f"⚙️ *Custom Plan Saved to Cloud DB!*\n\n🆔 User: `{uid}`\n📅 Duration: *{days} Days*\n⌛ Expiry: *{expiry}*\n📱 Phone: *{limit_str}*\n💳 UPI: *{limit_str}*\n📧 Email: *Unlimited*",
        reply_markup=admin_menu_keyboard(), parse_mode="Markdown"
    )
    context.user_data.pop("custom_days", None)
    context.user_data.pop("admin_uid", None)
    return ConversationHandler.END


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END


# ================== MAIN ==================
def main():
    web_server_thread = threading.Thread(target=start_webserver, daemon=True)
    web_server_thread.start()
    print("🌐 Keep-alive Flask server started!")

    request             = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0, pool_timeout=60.0)
    get_updates_request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0, write_timeout=60.0, pool_timeout=60.0)
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).get_updates_request(get_updates_request).build()

    phone_single_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(phone_single_start, pattern="^phone_single$")],
        states={
            PHONE_COUNTRY_SINGLE: [CallbackQueryHandler(country_selected_single, pattern="^country_(india|other)_single$")],
            PHONE_SINGLE_INDIA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_single_india)],
            PHONE_SINGLE_OTHER:   [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_single_other)],
        },
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )
    phone_batch_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(phone_batch_start, pattern="^phone_batch$")],
        states={
            PHONE_COUNTRY_BATCH: [CallbackQueryHandler(country_selected_batch, pattern="^country_(india|other)_batch$")],
            PHONE_BATCH_INDIA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_batch_india)],
            PHONE_BATCH_OTHER:   [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_batch_other)],
        },
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )
    email_single_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(email_single_start, pattern="^email_single$")],
        states={EMAIL_SINGLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_single_process)]},
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )
    email_batch_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(email_batch_start, pattern="^email_batch$")],
        states={EMAIL_BATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_batch_process)]},
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )
    upi_single_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(upi_single_start, pattern="^upi_single$")],
        states={UPI_SINGLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, upi_single_process)]},
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )
    upi_batch_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(upi_batch_start, pattern="^upi_batch$")],
        states={UPI_BATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, upi_batch_process)]},
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )
    admin_add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_start, pattern="^admin_add$")],
        states={
            ADMIN_ADD_ID:       [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_id)],
            ADMIN_ADD_PLAN:     [CallbackQueryHandler(admin_custom_start, pattern="^plan_custom$"), CallbackQueryHandler(admin_add_plan, pattern="^plan_")],
            ADMIN_CUSTOM_DAYS:  [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_custom_days_process)],
            ADMIN_CUSTOM_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_custom_limit_process)],
        },
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )
    admin_remove_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_remove_start, pattern="^admin_remove$")],
        states={ADMIN_REM_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_remove_process)]},
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )
    admin_setplan_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_setplan_start, pattern="^admin_setplan$")],
        states={
            ADMIN_EXP_ID:       [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_setplan_id)],
            ADMIN_EXP_PLAN:     [CallbackQueryHandler(admin_custom_start, pattern="^plan_custom$"), CallbackQueryHandler(admin_setplan_set, pattern="^plan_")],
            ADMIN_CUSTOM_DAYS:  [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_custom_days_process)],
            ADMIN_CUSTOM_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_custom_limit_process)],
        },
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )
    admin_broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_broadcast_start, pattern="^admin_broadcast$")],
        states={
            ADMIN_BROADCAST_MSG:     [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_broadcast_message)],
            ADMIN_BROADCAST_CONFIRM: [CallbackQueryHandler(admin_broadcast_confirm, pattern="^broadcast_(confirm|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)], per_message=False, allow_reentry=True,
    )

    for conv in [
        phone_single_conv, phone_batch_conv,
        email_single_conv, email_batch_conv,
        upi_single_conv, upi_batch_conv,
        admin_add_conv, admin_remove_conv, admin_setplan_conv,
        admin_broadcast_conv,
    ]:
        app.add_handler(conv)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(mode_phone,         pattern="^mode_phone$"))
    app.add_handler(CallbackQueryHandler(mode_email,         pattern="^mode_email$"))
    app.add_handler(CallbackQueryHandler(mode_upi,           pattern="^mode_upi$"))
    app.add_handler(CallbackQueryHandler(profile,            pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(status_check,       pattern="^status$"))
    app.add_handler(CallbackQueryHandler(help_menu,          pattern="^help$"))
    app.add_handler(CallbackQueryHandler(buy,                pattern="^buy$"))
    app.add_handler(CallbackQueryHandler(admin_list,         pattern="^admin_list$"))
    app.add_handler(CallbackQueryHandler(admin_stats,        pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_back,         pattern="^admin_back$"))
    app.add_handler(CallbackQueryHandler(admin_free_monitor, pattern="^admin_free_monitor$"))
    app.add_handler(CallbackQueryHandler(monitor_phone,      pattern="^monitor_phone$"))
    app.add_handler(CallbackQueryHandler(monitor_email,      pattern="^monitor_email$"))
    app.add_handler(CallbackQueryHandler(monitor_exhausted,  pattern="^monitor_exhausted$"))
    app.add_handler(CallbackQueryHandler(monitor_active,     pattern="^monitor_active$"))
    app.add_handler(CallbackQueryHandler(monitor_summary,    pattern="^monitor_summary$"))
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))

    print("🤖 Combined Bot Running!")
    print(f"🛡️ Admins: {ADMIN_IDS}")
    print("☁️ Cloud Database: Connected!")
    print("📱 Phone: Daily Limit | 📧 Email: Unlimited | 💳 UPI: Daily Limit")
    app.run_polling(drop_pending_updates=True, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()

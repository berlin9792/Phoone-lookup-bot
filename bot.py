#!/usr/bin/env python3
"""
🔍 Ultimate Intelligence Bot - ZERO TRACE
Phone + Email + UPI + Aadhaar + Vehicle + IFSC + Vehicle Info
ONE PLAN = ALL ACCESS
+ Blood ASCII Banner on Every Screen
+ Animated ASCII Loading Bar with Colors
+ Dual Channel Force Join Check
+ Redeem Code System (Admin Generated)
+ Clean Results Only
+ Fast In-Memory Cache + MongoDB Cloud + 24/7 Keep Alive
"""

import json, os, threading, requests, logging, asyncio, re, time
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

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== CONFIG ==================
BOT_TOKEN     = "8642873626:AAFy5F79opcK_NMJ7NgGItd6sRrfbOc4TJU"
ADMIN_IDS     = [5057489358, 1968142314]
DEFAULT_PIN   = "happyrb"
API_URL       = "https://num-info-hiteck.asurpapa.workers.dev/"
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
MONGO_URI = os.environ.get("MONGO_URI","mongodb+srv://httplegitfs_db_user:Q8uGZxERXsrf2VV1@cluster0.iojnad7.mongodb.net/?retryWrites=true&w=majority")
COMMON_HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36","Accept":"application/json, text/plain, */*","Accept-Language":"en-US,en;q=0.9"}

PHONE_FREE=2;EMAIL_FREE=2;UPI_FREE=2;AADHAAR_FREE=2;VEHICLE_FREE=2;IFSC_FREE=2;VINFO_FREE=2

PLANS = {
    "trial":{"name":"Trial","days":0,"price":0,"daily_limit":0,"unlimited":False,"is_free":True},
    "7days":{"name":"7 Days","days":7,"price":50,"daily_limit":5,"unlimited":False,"is_free":False},
    "30days":{"name":"30 Days","days":30,"price":130,"daily_limit":10,"unlimited":False,"is_free":False},
    "6months":{"name":"6 Months","days":180,"price":300,"daily_limit":15,"unlimited":False,"is_free":False},
    "12months":{"name":"12 Months","days":365,"price":799,"daily_limit":999999,"unlimited":True,"is_free":False},
}

PHONE_SINGLE=10;PHONE_BATCH=11;EMAIL_SINGLE=20;EMAIL_BATCH=21
ADMIN_ADD_ID=30;ADMIN_ADD_PLAN=31;ADMIN_REM_ID=32
ADMIN_EXP_ID=33;ADMIN_EXP_PLAN=34;ADMIN_BROADCAST_MSG=35;ADMIN_BROADCAST_CONFIRM=36
ADMIN_CUSTOM_DAYS=37;ADMIN_CUSTOM_LIMIT=38
UPI_SINGLE=40;UPI_BATCH=41;AADHAAR_SINGLE=50;AADHAAR_BATCH=51
VEHICLE_SINGLE=60;VEHICLE_BATCH=61;IFSC_SINGLE=70;IFSC_BATCH=71
VINFO_SINGLE=80;VINFO_BATCH=81
REDEEM_CREATE_CODE=90;REDEEM_CREATE_SEARCHES=91;REDEEM_CREATE_LIMIT=92;REDEEM_DELETE_CODE=93

# ================== 🩸 BLOOD ASCII BANNER ==================
BANNER = """```
╔══════════════════════════════╗
║  ▀█ █▀▀ █▀█ █▀█   ▀█▀ █▀█  ║
║  █▄ ██▄ █▀▄ █▄█    █  █▀▄  ║
║  ▄█ █▄▄ █ █ █  █   █  █ █  ║
║         ▄▀█ █▀▀ █▀▀        ║
║         █▀█ █▄▄ ██▄        ║
║                              ║
║     ☠️  Z E R O  T R A C E  ☠️  ║
║          ~BY  LEGIT          ║
╚══════════════════════════════╝
```"""

BANNER_MINI = """```
┏━━━━━━━━━━━━━━━━━━━━━━┓
┃  ☠️ ZERO TRACE ☠️     ┃
┃     ~BY LEGIT         ┃
┗━━━━━━━━━━━━━━━━━━━━━━┛
```"""

BANNER_SEARCH = """```
╔═══════════════════════╗
║ ☠️ ZERO TRACE ☠️      ║
║    ~BY LEGIT          ║
╚═══════════════════════╝
```"""

# ================== SAFE SENDERS ==================
async def safe_reply(update, text, reply_markup=None):
    try:
        if update.message: return await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        elif update.callback_query and update.callback_query.message:
            return await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except:
        clean=text.replace("*","").replace("`","").replace("_","").replace("[","").replace("]","")
        try:
            if update.message: return await update.message.reply_text(clean, reply_markup=reply_markup)
            elif update.callback_query and update.callback_query.message:
                return await update.callback_query.message.reply_text(clean, reply_markup=reply_markup)
        except: pass

async def safe_edit(target, text, reply_markup=None):
    try:
        if hasattr(target,"edit_text"): return await target.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        elif hasattr(target,"edit_message_text"): return await target.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except:
        clean=text.replace("*","").replace("`","").replace("_","").replace("[","").replace("]","")
        try:
            if hasattr(target,"edit_text"): return await target.edit_text(clean, reply_markup=reply_markup)
            elif hasattr(target,"edit_message_text"): return await target.edit_message_text(clean, reply_markup=reply_markup)
        except: pass

def is_admin(uid): return int(uid) in ADMIN_IDS
def safe_name(user):
    name=user.first_name or "User"
    for ch in ["*","_","`","[","]","(",")"]: name=name.replace(ch,"")
    return name
def valid_email(e): return "@" in e and "." in e.split("@")[-1] and " " not in e
def valid_upi(u): return "@" in u and len(u)>=5 and " " not in u
def valid_aadhaar(a): return a.isdigit() and len(a)==12
def valid_ifsc(c): return len(c)==11 and c[:4].isalpha() and c[4]=="0"
def valid_vehicle_number(v): return len(v)>=4 and any(c.isalpha() for c in v) and any(c.isdigit() for c in v)

# ================== ANIMATED LOADING BAR ==================
LOADING_STEPS = {
    "📱":[("🔴","Initializing Scan...","░░░░░░░░░░░░░░░░░░░░"),("🟡","Scanning Database...","█████░░░░░░░░░░░░░░░"),("🔵","Fetching Records...","██████████░░░░░░░░░░"),("🟣","Decoding Info...","███████████████░░░░░"),("🟢","Finalizing...","████████████████████"),("⚡","Complete!","████████████████████")],
    "📧":[("🔴","Connecting Server...","░░░░░░░░░░░░░░░░░░░░"),("🟡","Querying Email DB...","█████░░░░░░░░░░░░░░░"),("🔵","Extracting Data...","██████████░░░░░░░░░░"),("🟣","Verifying...","███████████████░░░░░"),("🟢","Preparing...","████████████████████"),("⚡","Complete!","████████████████████")],
    "💳":[("🔴","Connecting UPI...","░░░░░░░░░░░░░░░░░░░░"),("🟡","Verifying VPA...","█████░░░░░░░░░░░░░░░"),("🔵","Fetching Bank...","██████████░░░░░░░░░░"),("🟣","Resolving Holder...","███████████████░░░░░"),("🟢","Validating...","████████████████████"),("⚡","Complete!","████████████████████")],
    "🪪":[("🔴","Connecting UIDAI...","░░░░░░░░░░░░░░░░░░░░"),("🟡","Scanning Aadhaar...","█████░░░░░░░░░░░░░░░"),("🔵","Extracting...","██████████░░░░░░░░░░"),("🟣","Verifying ID...","███████████████░░░░░"),("🟢","Finalizing...","████████████████████"),("⚡","Complete!","████████████████████")],
    "🚗":[("🔴","Connecting RTO...","░░░░░░░░░░░░░░░░░░░░"),("🟡","Scanning Vehicle...","█████░░░░░░░░░░░░░░░"),("🔵","Fetching RC...","██████████░░░░░░░░░░"),("🟣","Verifying Owner...","███████████████░░░░░"),("🟢","Compiling...","████████████████████"),("⚡","Complete!","████████████████████")],
    "🏦":[("🔴","Connecting RBI...","░░░░░░░░░░░░░░░░░░░░"),("🟡","Resolving IFSC...","█████░░░░░░░░░░░░░░░"),("🔵","Fetching Branch...","██████████░░░░░░░░░░"),("🟣","Verifying...","███████████████░░░░░"),("🟢","Preparing...","████████████████████"),("⚡","Complete!","████████████████████")],
    "🚘":[("🔴","Connecting VAHAN...","░░░░░░░░░░░░░░░░░░░░"),("🟡","Scanning Records...","█████░░░░░░░░░░░░░░░"),("🔵","Extracting Data...","██████████░░░░░░░░░░"),("🟣","Verifying Insurance...","███████████████░░░░░"),("🟢","Compiling...","████████████████████"),("⚡","Complete!","████████████████████")],
}

def build_loading_text(icon,display,step_emoji,step_text,bar,percent):
    return (f"{BANNER_SEARCH}\n"
        f"{icon}  *Searching:* `{display}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{step_emoji} *{step_text}*\n\n"
        f"`[{bar}]` *{percent}%*\n\n"
        f"⏳ _Please wait..._")

async def animated_search(msg,icon,display):
    steps=LOADING_STEPS.get(icon,LOADING_STEPS["📱"])
    percents=[10,30,55,75,95,100]
    for i,(se,st,bar) in enumerate(steps):
        pct=percents[i] if i<len(percents) else 100
        txt=build_loading_text(icon,display,se,st,bar,pct)
        try: await msg.edit_text(txt,parse_mode="Markdown")
        except:
            try: await msg.edit_text(txt.replace("*","").replace("`","").replace("_",""))
            except: pass
        if i<len(steps)-1: await asyncio.sleep(0.6)

# ================== FLASK KEEP-ALIVE ==================
web_app = Flask(__name__)
@web_app.route('/')
def keep_alive_status(): return "Bot Running 24/7!", 200
def start_webserver():
    import logging as lg; lg.getLogger('werkzeug').setLevel(lg.ERROR)
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT",8080)))

# ================== FORCE JOIN ==================
async def check_joined(context,uid):
    if is_admin(uid): return True
    try:
        m1=await asyncio.wait_for(context.bot.get_chat_member(FORCE_JOIN_CHANNEL_1_ID,uid),timeout=3.0)
        if m1.status not in ["member","administrator","creator","restricted"]: return False
        m2=await asyncio.wait_for(context.bot.get_chat_member(FORCE_JOIN_CHANNEL_2_ID,uid),timeout=3.0)
        return m2.status in ["member","administrator","creator","restricted"]
    except: return False

def force_join_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel 1 ↗️",url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}")],
        [InlineKeyboardButton("📢 Join Channel 2 ↗️",url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton("✅ Verify Both ✅",callback_data="verify_join")],
    ])

# ================== CACHE + MONGODB ==================
USERS_CACHE={};REDEEM_CODES={};LOCAL_FILE=Path("users.json");REDEEM_FILE=Path("redeem_codes.json")
try:
    mc=MongoClient(MONGO_URI,serverSelectionTimeoutMS=2000);db=mc["tele_intel_bot"];users_col=db["users"];redeem_col=db["redeem_codes"]
    mc.admin.command('ping');print("✅ MongoDB Connected!")
except Exception as e: print("⚠️ MongoDB:",e);users_col=None;redeem_col=None

DEFAULTS={"plan":"trial","expiry":"","is_premium":False,"phone_free_used":0,"phone_daily":0,"phone_date":"","phone_total":0,"email_free_used":0,"email_total":0,"upi_free_used":0,"upi_daily":0,"upi_date":"","upi_total":0,"aadhaar_free_used":0,"aadhaar_daily":0,"aadhaar_date":"","aadhaar_total":0,"vehicle_free_used":0,"vehicle_daily":0,"vehicle_date":"","vehicle_total":0,"ifsc_free_used":0,"ifsc_daily":0,"ifsc_date":"","ifsc_total":0,"vinfo_free_used":0,"vinfo_daily":0,"vinfo_date":"","vinfo_total":0,"total_searches":0,"redeemed_codes":[]}

def init_cache():
    global USERS_CACHE,REDEEM_CODES
    if users_col:
        try:
            for doc in users_col.find(): USERS_CACHE[doc["_id"]]={k:v for k,v in doc.items() if k!="_id"}
        except: pass
    elif LOCAL_FILE.exists():
        try: USERS_CACHE=json.loads(LOCAL_FILE.read_text())
        except: USERS_CACHE={}
    if redeem_col:
        try:
            for doc in redeem_col.find(): REDEEM_CODES[doc["_id"]]={k:v for k,v in doc.items() if k!="_id"}
        except: pass
    elif REDEEM_FILE.exists():
        try: REDEEM_CODES=json.loads(REDEEM_FILE.read_text())
        except: REDEEM_CODES={}
init_cache()

def sync_user_background(uid,data):
    def _s():
        if users_col:
            try: users_col.update_one({"_id":str(uid)},{"$set":data},upsert=True);return
            except: pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE,indent=2))
        except: pass
    threading.Thread(target=_s,daemon=True).start()

def sync_redeem_background(code,data):
    def _s():
        if redeem_col:
            try: redeem_col.update_one({"_id":code},{"$set":data},upsert=True);return
            except: pass
        try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES,indent=2))
        except: pass
    threading.Thread(target=_s,daemon=True).start()

def delete_redeem_background(code):
    def _d():
        if redeem_col:
            try: redeem_col.delete_one({"_id":code})
            except: pass
        try: REDEEM_FILE.write_text(json.dumps(REDEEM_CODES,indent=2))
        except: pass
    threading.Thread(target=_d,daemon=True).start()

def get_user(uid):
    uid=str(uid)
    if uid not in USERS_CACHE:
        d={**DEFAULTS,"added":date.today().isoformat()};USERS_CACHE[uid]=d;sync_user_background(uid,d)
    else:
        d=USERS_CACHE[uid];u=False
        for k,v in DEFAULTS.items():
            if k not in d: d[k]=v;u=True
        if u: sync_user_background(uid,d)
    return USERS_CACHE[uid]

def save_user(uid,data): uid=str(uid);USERS_CACHE[uid]=data;sync_user_background(uid,data)

def delete_user(uid):
    uid=str(uid)
    if uid in USERS_CACHE: del USERS_CACHE[uid]
    def _d():
        if users_col:
            try: users_col.delete_one({"_id":uid})
            except: pass
        try: LOCAL_FILE.write_text(json.dumps(USERS_CACHE,indent=2))
        except: pass
    threading.Thread(target=_d,daemon=True).start()

def load_users(): return USERS_CACHE

# ================== REDEEM ==================
def create_redeem_code(code,fs,mu):
    code=code.upper().strip();REDEEM_CODES[code]={"free_searches":fs,"max_uses":mu,"used_count":0,"used_by":[],"created_at":date.today().isoformat(),"active":True}
    sync_redeem_background(code,REDEEM_CODES[code]);return True

def use_redeem_code(code,user_id):
    code=code.upper().strip();user_id=str(user_id)
    if code not in REDEEM_CODES: return False,"❌ Invalid code!"
    rc=REDEEM_CODES[code]
    if not rc.get("active",True): return False,"❌ Deactivated!"
    if rc["used_count"]>=rc["max_uses"]: return False,"❌ Max reached!"
    if user_id in rc.get("used_by",[]): return False,"❌ Already redeemed!"
    ud=get_user(user_id);s=rc["free_searches"]
    for k in ["phone_free_used","email_free_used","upi_free_used","aadhaar_free_used","vehicle_free_used","ifsc_free_used","vinfo_free_used"]:
        ud[k]=max(0,ud.get(k,0)-s)
    if "redeemed_codes" not in ud: ud["redeemed_codes"]=[]
    ud["redeemed_codes"].append(code);save_user(user_id,ud)
    rc["used_count"]+=1;rc["used_by"].append(user_id);REDEEM_CODES[code]=rc;sync_redeem_background(code,rc)
    return True,f"🎉 `{code}` redeemed!\n🎁 *{s} extra searches* on ALL!\n📊 `{rc['used_count']}/{rc['max_uses']}`"

def delete_redeem_code(code):
    code=code.upper().strip()
    if code in REDEEM_CODES: del REDEEM_CODES[code];delete_redeem_background(code);return True
    return False
def list_redeem_codes(): return REDEEM_CODES

# ================== PLAN RESOLVER ==================
def get_plan(ud):
    pk=ud.get("plan","trial")
    if pk.startswith("custom_"):
        try: d=int(pk.split("_")[1].replace("d",""))
        except: d=30
        return {"name":f"Custom ({d}D)","days":d,"daily_limit":ud.get("custom_limit",0),"unlimited":ud.get("custom_unlimited",False),"is_free":False}
    return PLANS.get(pk,PLANS["trial"])

def upgrade(uid,pk):
    uid=str(uid);ud=get_user(uid);plan=PLANS.get(pk,PLANS["7days"])
    exp=(date.today()+timedelta(days=plan["days"])).isoformat()
    ud.update({"plan":pk,"expiry":exp,"is_premium":True,"phone_daily":0,"phone_date":"","upi_daily":0,"upi_date":"","aadhaar_daily":0,"aadhaar_date":"","vehicle_daily":0,"vehicle_date":"","ifsc_daily":0,"ifsc_date":"","vinfo_daily":0,"vinfo_date":""})
    save_user(uid,ud);return exp

def upgrade_custom(uid,days,lim,unl):
    uid=str(uid);ud=get_user(uid);exp=(date.today()+timedelta(days=days)).isoformat()
    ud.update({"plan":f"custom_{days}d","expiry":exp,"is_premium":True,"phone_daily":0,"phone_date":"","upi_daily":0,"upi_date":"","aadhaar_daily":0,"aadhaar_date":"","vehicle_daily":0,"vehicle_date":"","ifsc_daily":0,"ifsc_date":"","vinfo_daily":0,"vinfo_date":"","custom_limit":lim,"custom_unlimited":unl})
    save_user(uid,ud);return exp

# ================== LIMITS ==================
def free_rem(uid,key,mx):
    if is_admin(uid): return 999999
    return max(0,mx-get_user(uid).get(key,0))
def daily_rem(uid,dk,dtk):
    if is_admin(uid): return 999999
    ud=get_user(uid);plan=get_plan(ud)
    if plan.get("unlimited"): return 999999
    lim=plan.get("daily_limit",0)
    if ud.get(dtk,"")!=date.today().isoformat(): return lim
    return max(0,lim-ud.get(dk,0))
def use_search(uid,fk,dk,dtk,tk):
    uid=str(uid);ud=get_user(uid);today=date.today().isoformat()
    if ud.get(dtk,"")!=today: ud[dk]=0;ud[dtk]=today
    plan=get_plan(ud)
    if not is_admin(int(uid)):
        if plan.get("is_free",True): ud[fk]=ud.get(fk,0)+1
        else: ud[dk]=ud.get(dk,0)+1
    ud[tk]=ud.get(tk,0)+1;ud["total_searches"]=ud.get("total_searches",0)+1;save_user(uid,ud)
def check_access(uid,fk,mx,dk,dtk,name):
    if is_admin(uid): return True,"Admin ∞",9999,True,"12months"
    ud=get_user(uid);plan=get_plan(ud);pk=ud.get("plan","trial");exp_s=ud.get("expiry","");is_p=ud.get("is_premium",False)
    if is_p and exp_s:
        try:
            exp=date.fromisoformat(exp_s)
            if date.today()>exp:
                fl=free_rem(uid,fk,mx)
                return (True,f"Expired|{fl} free",0,False,"trial") if fl>0 else (False,"Expired!",0,False,"trial")
            dl=(exp-date.today()).days;dr=daily_rem(uid,dk,dtk);lim=plan.get("daily_limit",0);unl=plan.get("unlimited",False)
            if unl: return True,f"{plan['name']}|∞|{dl}d",dl,True,pk
            if dr<=0: return False,f"Daily {name} done! ({lim}/day)",dl,True,pk
            return True,f"{plan['name']}|{dr}/{lim}|{dl}d",dl,True,pk
        except: pass
    fl=free_rem(uid,fk,mx)
    return (True,f"Trial ({fl}/{mx})",0,False,"trial") if fl>0 else (False,"Trial over!",0,False,"trial")

def phone_free(u): return free_rem(u,"phone_free_used",PHONE_FREE)
def phone_daily(u): return daily_rem(u,"phone_daily","phone_date")
def phone_use(u): use_search(u,"phone_free_used","phone_daily","phone_date","phone_total")
def phone_check(u): return check_access(u,"phone_free_used",PHONE_FREE,"phone_daily","phone_date","Phone")
def email_free(u): return free_rem(u,"email_free_used",EMAIL_FREE)
def email_use(uid,is_p):
    uid=str(uid);ud=get_user(uid)
    if not is_admin(int(uid)) and not is_p: ud["email_free_used"]=ud.get("email_free_used",0)+1
    ud["email_total"]=ud.get("email_total",0)+1;ud["total_searches"]=ud.get("total_searches",0)+1;save_user(uid,ud)
def email_check(uid):
    if is_admin(uid): return True,"Admin ∞",9999,True
    ud=get_user(uid);is_p=ud.get("is_premium",False);exp_s=ud.get("expiry","")
    if is_p and exp_s:
        try:
            exp=date.fromisoformat(exp_s)
            if date.today()>exp: fl=email_free(uid);return (True,f"Expired|{fl}",0,False) if fl>0 else (False,"Expired!",0,False)
            return True,f"Premium ({(exp-date.today()).days}d)",(exp-date.today()).days,True
        except: pass
    fl=email_free(uid);return (True,f"Free ({fl}/{EMAIL_FREE})",0,False) if fl>0 else (False,"Trial over!",0,False)

def upi_free(u): return free_rem(u,"upi_free_used",UPI_FREE)
def upi_daily(u): return daily_rem(u,"upi_daily","upi_date")
def upi_use(u): use_search(u,"upi_free_used","upi_daily","upi_date","upi_total")
def upi_check(u): return check_access(u,"upi_free_used",UPI_FREE,"upi_daily","upi_date","UPI")
def aadhaar_free(u): return free_rem(u,"aadhaar_free_used",AADHAAR_FREE)
def aadhaar_daily(u): return daily_rem(u,"aadhaar_daily","aadhaar_date")
def aadhaar_use(u): use_search(u,"aadhaar_free_used","aadhaar_daily","aadhaar_date","aadhaar_total")
def aadhaar_check(u): return check_access(u,"aadhaar_free_used",AADHAAR_FREE,"aadhaar_daily","aadhaar_date","Aadhaar")
def vehicle_free(u): return free_rem(u,"vehicle_free_used",VEHICLE_FREE)
def vehicle_daily(u): return daily_rem(u,"vehicle_daily","vehicle_date")
def vehicle_use(u): use_search(u,"vehicle_free_used","vehicle_daily","vehicle_date","vehicle_total")
def vehicle_check(u): return check_access(u,"vehicle_free_used",VEHICLE_FREE,"vehicle_daily","vehicle_date","Vehicle")
def ifsc_free(u): return free_rem(u,"ifsc_free_used",IFSC_FREE)
def ifsc_daily(u): return daily_rem(u,"ifsc_daily","ifsc_date")
def ifsc_use(u): use_search(u,"ifsc_free_used","ifsc_daily","ifsc_date","ifsc_total")
def ifsc_check(u): return check_access(u,"ifsc_free_used",IFSC_FREE,"ifsc_daily","ifsc_date","IFSC")
def vinfo_free(u): return free_rem(u,"vinfo_free_used",VINFO_FREE)
def vinfo_daily(u): return daily_rem(u,"vinfo_daily","vinfo_date")
def vinfo_use(u): use_search(u,"vinfo_free_used","vinfo_daily","vinfo_date","vinfo_total")
def vinfo_check(u): return check_access(u,"vinfo_free_used",VINFO_FREE,"vinfo_daily","vinfo_date","VehicleInfo")

# ================== API CALLS ==================
def _safe_api(fn):
    try: return fn()
    except requests.exceptions.Timeout: return {"ok":False,"error":"⏱️ Timed out"}
    except requests.exceptions.ConnectionError: return {"ok":False,"error":"🌐 Connection error"}
    except requests.exceptions.HTTPError as e: return {"ok":False,"error":f"⚠️ HTTP {e.response.status_code if e.response else '?'}"}
    except Exception as e: logger.error(f"API: {e}",exc_info=True);return {"ok":False,"error":f"❌ {e}"}

def phone_api(n):
    def c():
        r=requests.get("https://num-info-hiteck.asurpapa.workers.dev/api",params={"key":DEFAULT_PIN,"number":n},headers=COMMON_HEADERS,timeout=15)
        return {"ok":False,"error":f"HTTP {r.status_code}"} if r.status_code!=200 else {"ok":True,"data":r.json()}
    return _safe_api(c)
def search_api(t):
    def c():
        r=requests.get(API_URL,params={"pin":DEFAULT_PIN,"term":t},headers=COMMON_HEADERS,timeout=15)
        return {"ok":False,"error":f"HTTP {r.status_code}"} if r.status_code!=200 else {"ok":True,"data":r.json()}
    return _safe_api(c)
def upi_api(upi_id):
    def c():
        r=requests.get(UPI_API_URL,params={"key":UPI_API_KEY,"action":"upiinfo","upi":upi_id.strip()},headers=COMMON_HEADERS,timeout=15)
        if r.status_code!=200: return {"ok":False,"error":f"HTTP {r.status_code}"}
        try: data=r.json()
        except: return {"ok":False,"error":"Invalid JSON"}
        if isinstance(data,dict) and (data.get("status") in [False,"error",400,404] or data.get("success") is False):
            return {"ok":False,"error":str(data.get("message") or data.get("error") or "Invalid UPI")}
        return {"ok":True,"data":data}
    return _safe_api(c)
def aadhaar_api(n):
    def c():
        r=requests.get(AADHAAR_API_URL,params={"key":AADHAAR_API_KEY,"id":n},headers=COMMON_HEADERS,timeout=15)
        return {"ok":False,"error":f"HTTP {r.status_code}"} if r.status_code!=200 else {"ok":True,"data":r.json()}
    return _safe_api(c)
def vehicle_api(rc):
    def c():
        r=requests.get(VEHICLE_API_URL,params={"key":VEHICLE_API_KEY,"rc":rc},headers=COMMON_HEADERS,timeout=15)
        return {"ok":False,"error":f"HTTP {r.status_code}"} if r.status_code!=200 else {"ok":True,"data":r.json()}
    return _safe_api(c)
def ifsc_api(code):
    def c():
        r=requests.get(IFSC_API_URL,params={"type":"ifsc","search":code,"api_key":IFSC_API_KEY},headers=COMMON_HEADERS,timeout=15)
        return {"ok":False,"error":f"HTTP {r.status_code}"} if r.status_code!=200 else {"ok":True,"data":r.json()}
    return _safe_api(c)
def vinfo_api(vn):
    def c():
        r=requests.get(VINFO_API_URL,params={"types":"vinfo","key":VINFO_API_KEY,"spell":vn},headers=COMMON_HEADERS,timeout=15)
        return {"ok":False,"error":f"HTTP {r.status_code}"} if r.status_code!=200 else {"ok":True,"data":r.json()}
    return _safe_api(c)

# ================== METADATA FILTERING ==================
SKIP_K={"metadata","meta","key_owner","key_usage","key_expiry","key_enabled","daily_limit","daily_used","api_key","key","action","parameters","service","success","violations","timestamp","response_time","response_time_ms","developer","owner","credit","credits","powered_by","source","api","version","status","message","code","time","created_at","updated_at","server","watermark","signature","by","made_by","contact_admin","channel","group","join","advertisement","ads","promo","query","req_id","request_id","execution_time","fizzagirl","nitin","shree","jaani","types","spell","type"}
def should_skip_key(k):
    if not k: return True
    kl=str(k).lower().strip().replace(" ","_")
    if kl in SKIP_K: return True
    for w in ["metadata","timestamp","response_time","developer","credit","powered","watermark","pheevar","advertisement","promo","channel","server","api_","made_by","encrypted","password","salt","key_","daily_","auth","token","fizza"]:
        if w in kl: return True
    return False
def should_skip_val(v):
    if v is None or v=="": return True
    if isinstance(v,(dict,list)): return len(v)==0
    vs=str(v).lower().strip()
    if vs in ("","none","null","n/a","na","-","0","0.00","0000-00-00","{}","[]"): return True
    for s in ["@pheevar","pheevar","@lk_","t.me/","telegram.me/","rtfgamming","dm for buy"]:
        if s in vs: return True
    return False
def clean_value_text(v):
    if not isinstance(v,str): return v
    for pat in [r"(?i)📌?\s*dm\s*for\s*buy\s*:\s*@rtfgamming",r"(?i)@rtfgamming",r"(?i)rtfgamming",r"(?i)📌?\s*dm\s*for\s*buy\s*:"]:
        v=re.sub(pat,"",v)
    return v.strip().strip("|").strip("-").strip("•").strip("📌").strip()
def em(k):
    k=str(k).lower()
    for kw,e in {"name":"👤","holder":"👤","email":"📧","phone":"📞","mobile":"📞","address":"📍","city":"🏙️","state":"🗺️","country":"🌍","pincode":"📮","upi":"💳","vpa":"💳","bank":"🏦","ifsc":"🏦","account":"🏦","dob":"🎂","gender":"🚻","pan":"🪪","aadhar":"🪪","aadhaar":"🪪","father":"👨","mother":"👩","vehicle":"🚗","rc":"🚗","owner":"👤","model":"🚗","fuel":"⛽","engine":"🔧","chassis":"🔧","registration":"📅","insurance":"📋","fitness":"📋","rto":"🏢","branch":"🏦","district":"🗺️","micr":"🔢","swift":"🔢","verified":"✅","valid":"✅","merchant":"🏪","class":"📋","color":"🎨","colour":"🎨","seating":"💺","wheel":"🛞","cylinder":"🔩","weight":"⚖️","norms":"🌿","financer":"💰","permit":"📄","tax":"💵","number":"🔢","plate":"🔢","type":"📋","category":"📋","body":"🚗","manufacturer":"🏭","manufacturing":"📅","purchase":"🛒","hypothecation":"🔗","blacklist":"⚠️","noc":"📄","challan":"🎫","status":"📊","ration":"🍚","card":"💳","family":"👨‍👩‍👧","member":"👥","head":"👤","relation":"🔗","age":"🎂","fps":"🏪","shop":"🏪","scheme":"📋","unit":"🔢","id":"🆔"}.items():
        if kw in k: return e
    return "📌"
def clean_metadata(data):
    if isinstance(data,dict):
        cl={}
        for k,v in data.items():
            if should_skip_key(k): continue
            cv=clean_metadata(v)
            if isinstance(cv,str): cv=clean_value_text(cv)
            if not should_skip_val(cv): cl[k]=cv
        return cl
    elif isinstance(data,list): return [cv for i in data if not should_skip_val((cv:=clean_value_text(clean_metadata(i)) if isinstance(clean_metadata(i),str) else clean_metadata(i)))]
    return data

# ================== UPI CUSTOM PARSER ==================
def format_upi_result(term,raw_data):
    try:
        data_list=raw_data.get("result",{}).get("response",{}).get("data",[])
        if not data_list: return None
        d=data_list[0];vpa=d.get("vpa") or term;valid=d.get("valid");name=d.get("account_holder_name")
        merchant=d.get("merchant");merchant_ver=d.get("merchant_verified");bank_id=d.get("bank_id");acc_type=d.get("account_type")
        out=[BANNER_MINI,"💳  *UPI Verification Result*  💳","━━━━━━━━━━━━━━━━━━━━━━━━━━━━","",f"💳 *UPI ID (VPA)*: `{vpa}`"]
        if valid is True or str(valid).lower()=="true": out.append("📊 *Status*: `Active ✅`")
        elif valid is False or str(valid).lower()=="false": out.append("📊 *Status*: `Invalid ❌`")
        else: out.append("📊 *Status*: `Unknown 🔍`")
        if name and str(name).strip().lower() not in ["null","none",""]: out.append(f"👤 *Account Holder*: `{str(name).strip().upper()}`")
        else: out.append("👤 *Account Holder*: `N/A`")
        if merchant is True: out.append("🏪 *Merchant*: `Yes ✅`")
        elif merchant is False: out.append("🏪 *Merchant*: `No ❌`")
        if merchant_ver is True: out.append("✅ *Verified*: `Yes ✅`")
        elif merchant_ver is False: out.append("✅ *Verified*: `No ❌`")
        if bank_id and str(bank_id).lower() not in ["null","none",""]: out.append(f"🏦 *Bank ID*: `{str(bank_id).upper()}`")
        if acc_type and str(acc_type).lower() not in ["null","none",""]: out.append(f"🏦 *Acc Type*: `{str(acc_type).title()}`")
        out.append("");out.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━");return "\n".join(out)
    except: return None

# ================== UNIVERSAL FORMATTER (WITH BANNER) ==================
def format_universal_result(term,raw_data,icon="🔍"):
    if icon=="💳" and isinstance(raw_data,dict) and "result" in raw_data:
        r=format_upi_result(term,raw_data)
        if r: return r
    cleaned=clean_metadata(raw_data)
    if not cleaned: return f"{BANNER_MINI}\n{icon} *Result for* `{term}`\n_No data found_"
    records=[]
    def extract(item):
        if isinstance(item,dict):
            if any(not isinstance(v,(dict,list)) for v in item.values()): records.append(item)
            for v in item.values():
                if isinstance(v,(dict,list)): extract(v)
        elif isinstance(item,list):
            for s in item: extract(s)
    extract(cleaned)
    unique=[];seen=set()
    for r in records:
        fp="-".join(sorted(f"{k}:{v}" for k,v in r.items() if not isinstance(v,(dict,list))))
        if fp and fp not in seen: seen.add(fp);unique.append(r)
    if not unique: return f"{BANNER_MINI}\n{icon} *Result for* `{term}`\n_No data found_"
    out=[BANNER_MINI,f"{icon} *Result for* `{term}`",f"📊 *{len(unique)} record(s)*","━"*28]
    for idx,rec in enumerate(unique,1):
        if len(unique)>1: out.append(f"\n*━━ #{idx} ━━*")
        for k,v in rec.items():
            if isinstance(v,(dict,list)) or should_skip_key(k) or should_skip_val(v): continue
            emoji=em(k);label=str(k).replace("_"," ").replace("-"," ").title();kl=str(k).lower().strip()
            if isinstance(v,bool): vs=("Active ✅" if v else "Inactive ❌") if kl in ["valid","verified","active","success"] else ("Yes ✅" if v else "No ❌")
            elif str(v).lower()=="true": vs="Active ✅" if kl in ["valid","verified","active","success"] else "Yes ✅"
            elif str(v).lower()=="false": vs="Inactive ❌" if kl in ["valid","verified","active","success"] else "No ❌"
            else: val_str=str(v).strip();vs=val_str if ("@" in val_str or kl in ["vpa","upi","email","ifsc","code"]) else val_str.title()
            out.append(f"{emoji} *{label}*: `{vs}`")
    return "\n".join(out)

# ================== KEYBOARDS ==================
def main_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Phone Tracker",callback_data="mode_phone"),InlineKeyboardButton("📧 Email OSINT",callback_data="mode_email")],
        [InlineKeyboardButton("💳 UPI Verifier",callback_data="mode_upi"),InlineKeyboardButton("🪪 Aadhaar Check",callback_data="mode_aadhaar")],
        [InlineKeyboardButton("🚗 Vehicle RC",callback_data="mode_vehicle"),InlineKeyboardButton("🏦 IFSC Finder",callback_data="mode_ifsc")],
        [InlineKeyboardButton("🚘 Vehicle Info",callback_data="mode_vinfo")],
        [InlineKeyboardButton("🎟️ Redeem Code",callback_data="redeem_info")],
        [InlineKeyboardButton("👤 Profile",callback_data="profile"),InlineKeyboardButton("📊 Status",callback_data="status")],
        [InlineKeyboardButton("📢 CH 1",url=f"https://t.me/{FORCE_JOIN_CHANNEL_1.replace('@','')}"),InlineKeyboardButton("📢 CH 2",url=f"https://t.me/{FORCE_JOIN_CHANNEL_2.replace('@','')}")],
        [InlineKeyboardButton("💎 Buy Premium 💎",callback_data="buy")],
        [InlineKeyboardButton("❓ Help ❓",callback_data="help")],
    ])
def search_kb(uid,check_fn,free_fn,daily_fn,prefix,mx):
    if is_admin(uid): sl,bl="🔍 Single (Admin)","📦 Batch (Admin)"
    else:
        ok,_,_,ip,_=check_fn(uid);fl=free_fn(uid);dr=daily_fn(uid);p=get_plan(get_user(uid))
        if ip: sl,bl=("🟢 Single (∞)","📦 Batch (∞)") if p.get("unlimited") else (f"🟢 Single ({dr})",f"📦 Batch ({dr})")
        elif fl>0: sl,bl=f"🆓 Single ({fl})",f"📦 Batch ({fl})"
        else: sl,bl="🔒 Locked","🔒 Locked"
    return InlineKeyboardMarkup([[InlineKeyboardButton(sl,callback_data=f"{prefix}_single")],[InlineKeyboardButton(bl,callback_data=f"{prefix}_batch")],[InlineKeyboardButton("🔙 Menu",callback_data="main_menu")]])
def email_kb(uid):
    if is_admin(uid): sl,bl="🔍 Single (Admin)","📦 Batch (Admin)"
    else:
        ok,_,_,ip=email_check(uid);fl=email_free(uid)
        if ip: sl,bl="🟢 Single (∞)","📦 Batch (∞)"
        elif fl>0: sl,bl=f"🆓 Single ({fl})",f"📦 Batch ({fl})"
        else: sl,bl="🔒 Locked","🔒 Locked"
    return InlineKeyboardMarkup([[InlineKeyboardButton(sl,callback_data="email_single")],[InlineKeyboardButton(bl,callback_data="email_batch")],[InlineKeyboardButton("🔙 Menu",callback_data="main_menu")]])
def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add",callback_data="admin_add"),InlineKeyboardButton("❌ Remove",callback_data="admin_remove")],
        [InlineKeyboardButton("📅 Plan",callback_data="admin_setplan"),InlineKeyboardButton("📋 Users",callback_data="admin_list")],
        [InlineKeyboardButton("📊 Stats",callback_data="admin_stats"),InlineKeyboardButton("🆓 Monitor",callback_data="admin_free_monitor")],
        [InlineKeyboardButton("📢 Broadcast",callback_data="admin_broadcast")],
        [InlineKeyboardButton("🎟️ Create Code",callback_data="admin_redeem_create")],
        [InlineKeyboardButton("📋 Codes",callback_data="admin_redeem_list")],
        [InlineKeyboardButton("🗑️ Del Code",callback_data="admin_redeem_delete")],
        [InlineKeyboardButton("🔙 Menu",callback_data="main_menu")],
    ])
def back_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu",callback_data="main_menu")]])
def buy_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("💬 Admin",url=f"https://t.me/{OWNER_CONTACT.replace('@','')}")],[InlineKeyboardButton("🔙 Menu",callback_data="main_menu")]])
def plan_kb(pf):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🥉 7D-₹50",callback_data=f"{pf}_7days")],[InlineKeyboardButton("🥈 30D-₹130",callback_data=f"{pf}_30days")],[InlineKeyboardButton("🥇 6M-₹300",callback_data=f"{pf}_6months")],[InlineKeyboardButton("💎 12M-₹799",callback_data=f"{pf}_12months")],[InlineKeyboardButton("⚙️ Custom",callback_data=f"{pf}_custom")],[InlineKeyboardButton("❌ Cancel",callback_data="admin_back")]])
def monitor_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("🔴 Exhausted",callback_data="monitor_exhausted"),InlineKeyboardButton("🟢 Active",callback_data="monitor_active")],[InlineKeyboardButton("📊 Summary",callback_data="monitor_summary")],[InlineKeyboardButton("🔙 Admin",callback_data="admin_back")]])

# ================== START (WITH BANNER) ==================
async def start(update,context):
    user=update.effective_user;get_user(user.id);u_name=safe_name(user)
    if not is_admin(user.id):
        if not await check_joined(context,user.id):
            t=f"{BANNER}\n🔴  *Force Join Required*\n\nWelcome *{u_name}*!\n\n⚠️ Join both:\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}\n\nVerify 👇"
            if update.callback_query: await safe_edit(update.callback_query,t,force_join_kb())
            else: await safe_reply(update,t,force_join_kb())
            return ConversationHandler.END
    if is_admin(user.id):
        t=f"{BANNER}\n👋 *{u_name}*! 🛡️ `Admin`\n\n📱 Phone: 💎∞ | 📧 Email: 💎∞\n💳 UPI: 💎∞ | 🪪 Aadhaar: 💎∞\n🚗 Vehicle: 💎∞ | 🏦 IFSC: 💎∞\n🚘 V-Info: 💎∞\n\nSelect 👇"
    else:
        ud=get_user(user.id);plan=get_plan(ud);ip,exp=ud.get("is_premium",False),ud.get("expiry","");lines=[]
        for nm,ff,df,mx in [("📱Phone",phone_free,phone_daily,PHONE_FREE),("📧Email",email_free,lambda u:999999,EMAIL_FREE),("💳UPI",upi_free,upi_daily,UPI_FREE),("🪪Aadhaar",aadhaar_free,aadhaar_daily,AADHAAR_FREE),("🚗Vehicle",vehicle_free,vehicle_daily,VEHICLE_FREE),("🏦IFSC",ifsc_free,ifsc_daily,IFSC_FREE),("🚘VInfo",vinfo_free,vinfo_daily,VINFO_FREE)]:
            fl=ff(user.id)
            if ip and exp:
                try:
                    ed=date.fromisoformat(exp);dl=(ed-date.today()).days
                    if dl>=0:
                        if nm=="📧Email" or plan.get("unlimited"): lines.append(f"🟢 {nm}: 💎∞ ({dl}d)")
                        else: dr=df(user.id);lines.append(f"🟢 {nm}: 💎{dr}/{plan.get('daily_limit',0)} ({dl}d)")
                    else: lines.append(f"🔴 {nm}: Expired ({fl}/{mx})")
                except: lines.append(f"⚪ {nm}: Unknown")
            else: lines.append(f"🆓 {nm}: {fl}/{mx}")
        t=f"{BANNER}\n👋 *{u_name}*!\n\n"+"\n".join(lines)+f"\n\n💡 *1 plan = 7 features!*\n🎟️ `/redeem CODE`\n\nSelect 👇"
    if update.callback_query: await safe_edit(update.callback_query,t,main_kb(user.id))
    else: await safe_reply(update,t,main_kb(user.id))
    return ConversationHandler.END

async def verify_join(update,context):
    q=update.callback_query;u=q.from_user
    if await check_joined(context,u.id): await q.answer("🎉 Verified!");await start(update,context)
    else: await q.answer("❌ Join both!",show_alert=True);await safe_edit(q,f"{BANNER_MINI}\n⚠️ *Join Both!*\n📢 {FORCE_JOIN_CHANNEL_1}\n📢 {FORCE_JOIN_CHANNEL_2}",force_join_kb())

# ================== MODES (WITH BANNER) ==================
async def _mode(update,context,title,icon,chk,ff,df,mx,mkb):
    q=update.callback_query;await q.answer();u=q.from_user
    if not is_admin(u.id) and not await check_joined(context,u.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return
    if is_admin(u.id): info="🛡️ Admin"
    else:
        ok,_,_,ip,_=chk(u.id);fl,dr=ff(u.id),df(u.id);p=get_plan(get_user(u.id))
        info="💎∞" if ip and p.get("unlimited") else (f"🟢{dr}/{p.get('daily_limit',0)}" if ip else f"🆓{fl}/{mx}")
    await safe_edit(q,f"{BANNER_SEARCH}\n{icon}  *{title}*  {icon}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📊 Status: `{info}`\n\nChoose:",mkb(u.id))

async def mode_phone(u,c): await _mode(u,c,"Phone Search","📱",phone_check,phone_free,phone_daily,PHONE_FREE,lambda uid:search_kb(uid,phone_check,phone_free,phone_daily,"phone",PHONE_FREE))
async def mode_email(update,context):
    q=update.callback_query;await q.answer();u=q.from_user
    if not is_admin(u.id) and not await check_joined(context,u.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return
    if is_admin(u.id): info="🛡️ Admin"
    else: ok,_,d,ip=email_check(u.id);fl=email_free(u.id);info=f"💎({d}d)" if ip else f"🆓{fl}/{EMAIL_FREE}"
    await safe_edit(q,f"{BANNER_SEARCH}\n📧  *Email Search*  📧\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📊 `{info}`\n\nChoose:",email_kb(u.id))
async def mode_upi(u,c): await _mode(u,c,"UPI Search","💳",upi_check,upi_free,upi_daily,UPI_FREE,lambda uid:search_kb(uid,upi_check,upi_free,upi_daily,"upi",UPI_FREE))
async def mode_aadhaar(u,c): await _mode(u,c,"Aadhaar Search","🪪",aadhaar_check,aadhaar_free,aadhaar_daily,AADHAAR_FREE,lambda uid:search_kb(uid,aadhaar_check,aadhaar_free,aadhaar_daily,"aadhaar",AADHAAR_FREE))
async def mode_vehicle(u,c): await _mode(u,c,"Vehicle RC","🚗",vehicle_check,vehicle_free,vehicle_daily,VEHICLE_FREE,lambda uid:search_kb(uid,vehicle_check,vehicle_free,vehicle_daily,"vehicle",VEHICLE_FREE))
async def mode_ifsc(u,c): await _mode(u,c,"IFSC Lookup","🏦",ifsc_check,ifsc_free,ifsc_daily,IFSC_FREE,lambda uid:search_kb(uid,ifsc_check,ifsc_free,ifsc_daily,"ifsc",IFSC_FREE))
async def mode_vinfo(u,c): await _mode(u,c,"Vehicle Info","🚘",vinfo_check,vinfo_free,vinfo_daily,VINFO_FREE,lambda uid:search_kb(uid,vinfo_check,vinfo_free,vinfo_daily,"vinfo",VINFO_FREE))

# ================== REDEEM ==================
async def redeem_command(update,context):
    user=update.effective_user
    if not context.args: await safe_reply(update,f"{BANNER_MINI}\n🎟️ Usage: `/redeem CODE`",back_kb());return
    code=context.args[0].upper().strip()
    if len(code)<3 or len(code)>20: await safe_reply(update,"❌ Invalid!",back_kb());return
    ok,msg=use_redeem_code(code,user.id);await safe_reply(update,f"{BANNER_MINI}\n{msg}",main_kb(user.id))
async def redeem_info(update,context):
    q=update.callback_query;await q.answer()
    await safe_edit(q,f"{BANNER_SEARCH}\n🎟️ *Redeem Code*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📝 `/redeem CODE`\n✅ Example: `/redeem AB12CD`\n\n🎁 Giveaways\n📢 Promotions\n🎯 Extra free searches!",back_kb())

# ================== PROFILE / STATUS / HELP / BUY (WITH BANNER) ==================
async def profile(update,context):
    q=update.callback_query;await q.answer();u=q.from_user;ud=get_user(u.id);ts=ud.get("total_searches",0)
    rc=ud.get("redeemed_codes",[])
    await safe_edit(q,f"{BANNER_MINI}\n👤 *{safe_name(u)}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🆔 `{u.id}`\n\n📱 Phone: `{ud.get('phone_total',0)}`\n📧 Email: `{ud.get('email_total',0)}`\n💳 UPI: `{ud.get('upi_total',0)}`\n🪪 Aadhaar: `{ud.get('aadhaar_total',0)}`\n🚗 Vehicle: `{ud.get('vehicle_total',0)}`\n🏦 IFSC: `{ud.get('ifsc_total',0)}`\n🚘 VInfo: `{ud.get('vinfo_total',0)}`\n\n🔍 Total: `{ts}`\n🎟️ Redeemed: `{len(rc)}`",back_kb())

async def status_check(update,context):
    q=update.callback_query;await q.answer();u=q.from_user
    if is_admin(u.id): await safe_edit(q,f"{BANNER_MINI}\n🛡️ *Admin* — All ∞",back_kb());return
    lines=[]
    for nm,chk,ff,df,mx in [("📱",phone_check,phone_free,phone_daily,PHONE_FREE),("💳",upi_check,upi_free,upi_daily,UPI_FREE),("🪪",aadhaar_check,aadhaar_free,aadhaar_daily,AADHAAR_FREE),("🚗",vehicle_check,vehicle_free,vehicle_daily,VEHICLE_FREE),("🏦",ifsc_check,ifsc_free,ifsc_daily,IFSC_FREE),("🚘",vinfo_check,vinfo_free,vinfo_daily,VINFO_FREE)]:
        ok,st,_,ip,_=chk(u.id)
        if ip: p=get_plan(get_user(u.id));dr=df(u.id);lim=p.get("daily_limit",0);lines.append(f"{nm}:{'💎∞' if p.get('unlimited') else f'💎{dr}/{lim}'}")
        else: lines.append(f"{nm}:🆓{ff(u.id)}/{mx}")
    ok,st,_,ip=email_check(u.id);lines.append(f"📧:{'💎∞' if ip else f'🆓{email_free(u.id)}/{EMAIL_FREE}'}")
    await safe_edit(q,f"{BANNER_MINI}\n📊 *Status*\n\n"+"\n".join(lines)+f"\n\n💰 {OWNER_CONTACT}\nID: `{u.id}`",back_kb())

async def help_menu(update,context):
    q=update.callback_query;await q.answer()
    await safe_edit(q,f"{BANNER}\n❓ *Help Guide*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🎯 *1 Plan = 7 Features!*\n\n💎 7D-₹50|30D-₹130|6M-₹300|12M-₹799\n\n💡 *Formats:*\n📱 Phone number\n💳 UPI: `id@bank`\n🪪 Aadhaar: 12 digits\n🚗 RC: `MH01AB1234`\n🏦 IFSC: `SBIN0001234`\n🚘 Vehicle: `UP32AB1234`\n📦 Batch: comma, Max 15\n\n🎟️ `/redeem CODE`",back_kb())

async def buy(update,context):
    q=update.callback_query;await q.answer();u=q.from_user
    if is_admin(u.id): await safe_edit(q,f"{BANNER_MINI}\n🛡️ Admin!",back_kb());return
    await safe_edit(q,f"{BANNER}\n💰 *Premium Plans*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🥉 *7 Days* - ₹50 (5/day)\n🥈 *30 Days* - ₹130 (10/day)\n🥇 *6 Months* - ₹300 (15/day)\n💎 *12 Months* - ₹799 (∞)\n\n📱 {OWNER_CONTACT}\nID: `{u.id}`",buy_kb())

# ================== SEARCH EXECUTION (WITH BANNER) ==================
async def _do_single(update,context,api_fn,term,display,icon,use_fn,chk):
    u=update.effective_user;r=chk(u.id);ok=r[0];st=r[1]
    if not ok: await safe_reply(update,f"{BANNER_MINI}\n🔒 *Locked!*\n{st}\n\n🎟️ `/redeem CODE`\n💰 {OWNER_CONTACT}",buy_kb());return
    msg=await safe_reply(update,f"⏳ Initializing...")
    if msg:
        api_task=asyncio.get_event_loop().run_in_executor(None,api_fn,term)
        anim_task=animated_search(msg,icon,display)
        res,_=await asyncio.gather(api_task,anim_task)
    else: res=api_fn(term)
    if res["ok"]:
        use_fn(u.id);text=format_universal_result(display,res["data"],icon)
        final=f"⚡ *Search Complete!*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{text}"
        if msg: await safe_edit(msg,final,main_kb(u.id))
        else: await safe_reply(update,final,main_kb(u.id))
    else:
        err=f"{BANNER_MINI}\n🔴 *Failed!*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n❌ `{display}`\n📛 {res['error']}\n\n💡 _Try again_"
        if msg: await safe_edit(msg,err,back_kb())
        else: await safe_reply(update,err,back_kb())

async def _do_batch(update,context,api_fn,items,icon,use_fn,chk):
    u=update.effective_user;total=len(items)
    msg=await safe_reply(update,f"{BANNER_MINI}\n📦 *Batch*\n🚀 Processing *{total}*...\n\n`[░░░░░░░░░░░░░░░░░░░░]` 0%")
    for idx,item in enumerate(items,1):
        pct=int((idx/total)*100);filled=int(pct/5);bar="█"*filled+"░"*(20-filled)
        try: await msg.edit_text(f"{BANNER_MINI}\n📦 *Batch*\n🔍 `{item}`\n📊 *{idx}/{total}*\n\n`[{bar}]` *{pct}%*",parse_mode="Markdown")
        except: pass
        res=api_fn(item)
        if res["ok"]: use_fn(u.id);await safe_reply(update,format_universal_result(item,res["data"],icon))
        else: await safe_reply(update,f"❌ *{item}*\n{res['error']}")
    if msg: await safe_edit(msg,f"{BANNER_MINI}\n⚡ *Batch Done!*\n✅ *{total}* items\n`[████████████████████]` *100%*",main_kb(u.id))

# ================== SEARCH HANDLERS ==================
async def phone_single_s2(update,context):
    q=update.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(context,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=phone_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n📱 Enter phone number:\n/cancel");return PHONE_SINGLE
async def phone_batch_s2(update,context):
    q=update.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(context,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=phone_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n📦 Phones comma se (Max 15):\n/cancel");return PHONE_BATCH
async def phone_single_process(update,context):
    cl=update.message.text.strip().replace(" ","").replace("-","").replace("+","")
    if not cl.isdigit() or not (5<=len(cl)<=15): await safe_reply(update,"❌ Invalid!\n/cancel");return PHONE_SINGLE
    await _do_single(update,context,phone_api,cl,cl,"📱",phone_use,phone_check);return ConversationHandler.END
async def phone_batch_process(update,context):
    valid=[n.strip().replace(" ","").replace("-","").replace("+","") for n in update.message.text.split(",") if n.strip().replace(" ","").replace("-","").replace("+","").isdigit() and 5<=len(n.strip().replace(" ","").replace("-","").replace("+",""))<=15][:15]
    if not valid: await safe_reply(update,"❌ No valid!\n/cancel");return PHONE_BATCH
    await _do_batch(update,context,phone_api,valid,"📱",phone_use,phone_check);return ConversationHandler.END

async def email_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_=email_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n📧 Email daalo:\n/cancel");return EMAIL_SINGLE
async def email_sp(update,context):
    e=update.message.text.strip()
    if not valid_email(e): await safe_reply(update,"❌ Invalid!\n/cancel");return EMAIL_SINGLE
    await _do_single(update,context,search_api,e,e,"📧",lambda uid:email_use(uid,email_check(uid)[3]),lambda uid:(*email_check(uid),None));return ConversationHandler.END
async def email_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_=email_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n📦 Emails comma se:\n/cancel");return EMAIL_BATCH
async def email_bp(update,context):
    emails=[e.strip() for e in update.message.text.split(",") if valid_email(e.strip())][:15]
    if not emails: await safe_reply(update,"❌ No valid!\n/cancel");return EMAIL_BATCH
    await _do_batch(update,context,search_api,emails,"📧",lambda uid:email_use(uid,email_check(uid)[3]),lambda uid:(*email_check(uid),None));return ConversationHandler.END

async def upi_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=upi_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n💳 UPI ID (eg: id@ybl):\n/cancel");return UPI_SINGLE
async def upi_sp(update,context):
    uid=update.message.text.strip()
    if not valid_upi(uid): await safe_reply(update,"❌ Format: id@bank\n/cancel");return UPI_SINGLE
    await _do_single(update,context,upi_api,uid,uid,"💳",upi_use,upi_check);return ConversationHandler.END
async def upi_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=upi_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n📦 UPIs comma se:\n/cancel");return UPI_BATCH
async def upi_bp(update,context):
    upis=[u.strip() for u in update.message.text.split(",") if valid_upi(u.strip())][:15]
    if not upis: await safe_reply(update,"❌ No valid!\n/cancel");return UPI_BATCH
    await _do_batch(update,context,upi_api,upis,"💳",upi_use,upi_check);return ConversationHandler.END

async def aadh_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=aadhaar_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n🪪 12 digit Aadhaar:\n/cancel");return AADHAAR_SINGLE
async def aadh_sp(update,context):
    a=update.message.text.strip().replace(" ","").replace("-","")
    if not valid_aadhaar(a): await safe_reply(update,"❌ 12 digits!\n/cancel");return AADHAAR_SINGLE
    await _do_single(update,context,aadhaar_api,a,a,"🪪",aadhaar_use,aadhaar_check);return ConversationHandler.END
async def aadh_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=aadhaar_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n📦 Aadhaars comma se:\n/cancel");return AADHAAR_BATCH
async def aadh_bp(update,context):
    nums=[a.strip().replace(" ","").replace("-","") for a in update.message.text.split(",") if valid_aadhaar(a.strip().replace(" ","").replace("-",""))][:15]
    if not nums: await safe_reply(update,"❌ No valid!\n/cancel");return AADHAAR_BATCH
    await _do_batch(update,context,aadhaar_api,nums,"🪪",aadhaar_use,aadhaar_check);return ConversationHandler.END

async def veh_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=vehicle_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n🚗 Vehicle number:\n/cancel");return VEHICLE_SINGLE
async def veh_sp(update,context):
    rc=update.message.text.strip().upper().replace(" ","").replace("-","")
    if len(rc)<4: await safe_reply(update,"❌ Invalid!\n/cancel");return VEHICLE_SINGLE
    await _do_single(update,context,vehicle_api,rc,rc,"🚗",vehicle_use,vehicle_check);return ConversationHandler.END
async def veh_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=vehicle_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n📦 RCs comma se:\n/cancel");return VEHICLE_BATCH
async def veh_bp(update,context):
    rcs=[r.strip().upper().replace(" ","").replace("-","") for r in update.message.text.split(",") if len(r.strip())>=4][:15]
    if not rcs: await safe_reply(update,"❌ No valid!\n/cancel");return VEHICLE_BATCH
    await _do_batch(update,context,vehicle_api,rcs,"🚗",vehicle_use,vehicle_check);return ConversationHandler.END

async def ifsc_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=ifsc_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n🏦 IFSC Code:\n/cancel");return IFSC_SINGLE
async def ifsc_sp(update,context):
    code=update.message.text.strip().upper().replace(" ","")
    if not valid_ifsc(code): await safe_reply(update,"❌ Invalid!\n/cancel");return IFSC_SINGLE
    await _do_single(update,context,ifsc_api,code,code,"🏦",ifsc_use,ifsc_check);return ConversationHandler.END
async def ifsc_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=ifsc_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n📦 IFSCs comma se:\n/cancel");return IFSC_BATCH
async def ifsc_bp(update,context):
    codes=[c.strip().upper().replace(" ","") for c in update.message.text.split(",") if valid_ifsc(c.strip().upper().replace(" ",""))][:15]
    if not codes: await safe_reply(update,"❌ No valid!\n/cancel");return IFSC_BATCH
    await _do_batch(update,context,ifsc_api,codes,"🏦",ifsc_use,ifsc_check);return ConversationHandler.END

async def vinfo_ss(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=vinfo_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n🚘 Vehicle number:\n/cancel");return VINFO_SINGLE
async def vinfo_sp(update,context):
    vn=update.message.text.strip().upper().replace(" ","").replace("-","")
    if not valid_vehicle_number(vn): await safe_reply(update,"❌ Invalid!\n/cancel");return VINFO_SINGLE
    await _do_single(update,context,vinfo_api,vn,vn,"🚘",vinfo_use,vinfo_check);return ConversationHandler.END
async def vinfo_bs(u,c):
    q=u.callback_query;await q.answer()
    if not is_admin(q.from_user.id) and not await check_joined(c,q.from_user.id): await safe_edit(q,"⚠️ Join!",force_join_kb());return ConversationHandler.END
    ok,st,_,_,_=vinfo_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒 {st}",buy_kb());return ConversationHandler.END
    await safe_edit(q,f"{BANNER_SEARCH}\n📦 Vehicles comma se:\n/cancel");return VINFO_BATCH
async def vinfo_bp(update,context):
    vehicles=[v.strip().upper().replace(" ","").replace("-","") for v in update.message.text.split(",") if valid_vehicle_number(v.strip().upper().replace(" ","").replace("-",""))][:15]
    if not vehicles: await safe_reply(update,"❌ No valid!\n/cancel");return VINFO_BATCH
    await _do_batch(update,context,vinfo_api,vehicles,"🚘",vinfo_use,vinfo_check);return ConversationHandler.END

async def cancel(u,c): c.user_data.clear();await safe_reply(u,"❌ Cancelled.",main_kb(u.effective_user.id));return ConversationHandler.END

# ================== ADMIN REDEEM ==================
async def admin_redeem_create_start(update,context):
    q=update.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer();await safe_edit(q,f"{BANNER_MINI}\n🎟️ *Create Code*\n📝 Code (3-20):\n/cancel");return REDEEM_CREATE_CODE
async def admin_redeem_code_input(update,context):
    code=update.message.text.strip().upper()
    if len(code)<3 or len(code)>20: await safe_reply(update,"❌ 3-20!\n/cancel");return REDEEM_CREATE_CODE
    if not code.isalnum(): await safe_reply(update,"❌ Letters+nums!\n/cancel");return REDEEM_CREATE_CODE
    if code in REDEEM_CODES: await safe_reply(update,f"❌ `{code}` exists!\n/cancel");return REDEEM_CREATE_CODE
    context.user_data["nrc"]=code;await safe_reply(update,f"Code: `{code}`\n🎁 Free searches?\n/cancel");return REDEEM_CREATE_SEARCHES
async def admin_redeem_searches_input(update,context):
    t=update.message.text.strip()
    if not t.isdigit() or int(t)<=0: await safe_reply(update,"❌ Positive!\n/cancel");return REDEEM_CREATE_SEARCHES
    context.user_data["nrs"]=int(t);await safe_reply(update,f"✅ {t}\n👥 Max users?\n/cancel");return REDEEM_CREATE_LIMIT
async def admin_redeem_limit_input(update,context):
    t=update.message.text.strip()
    if not t.isdigit() or int(t)<=0: await safe_reply(update,"❌ Positive!\n/cancel");return REDEEM_CREATE_LIMIT
    mu=int(t);code=context.user_data.get("nrc");fs=context.user_data.get("nrs")
    create_redeem_code(code,fs,mu)
    await safe_reply(update,f"{BANNER_MINI}\n🎟️ *Created!*\n🔑 `{code}`\n🎁 {fs}\n👥 {mu}\n\n`/redeem {code}`",admin_kb())
    context.user_data.pop("nrc",None);context.user_data.pop("nrs",None);return ConversationHandler.END
async def admin_redeem_list(update,context):
    q=update.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer();codes=list_redeem_codes()
    if not codes: await safe_edit(q,f"{BANNER_MINI}\n📋 No codes!",admin_kb());return
    txt=f"{BANNER_MINI}\n🎟️ *All Codes*\n\n"
    for code,info in codes.items():
        st="🟢" if info.get("active",True) and info["used_count"]<info["max_uses"] else "🔴"
        txt+=f"{st} `{code}` | 🎁{info['free_searches']} | 👥{info['used_count']}/{info['max_uses']}\n"
    await safe_edit(q,txt[:4000],admin_kb())
async def admin_redeem_delete_start(update,context):
    q=update.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer();codes=list_redeem_codes()
    if not codes: await safe_edit(q,"📋 No codes!",admin_kb());return ConversationHandler.END
    txt=f"{BANNER_MINI}\n🗑️ *Delete*\n\n"+"".join(f"• `{c}`\n" for c in codes)+"\nType code:\n/cancel"
    await safe_edit(q,txt);return REDEEM_DELETE_CODE
async def admin_redeem_delete_input(update,context):
    code=update.message.text.strip().upper()
    if delete_redeem_code(code): await safe_reply(update,f"✅ `{code}` deleted!",admin_kb())
    else: await safe_reply(update,f"❌ `{code}` not found!",admin_kb())
    return ConversationHandler.END

# ================== ADMIN PANEL (WITH BANNER) ==================
async def admin_panel(update,context):
    if not is_admin(update.effective_user.id): await safe_reply(update,"❌ Admin only!");return ConversationHandler.END
    users=load_users();t=len(users);p=sum(1 for v in users.values() if v.get("is_premium"))
    txt=f"{BANNER_MINI}\n🛠️ *Admin Panel*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🛡️ Admins: `{len(ADMIN_IDS)}`\n👥 Users: `{t}`\n💎 Premium: `{p}`\n🆓 Free: `{t-p}`\n🎟️ Codes: `{len(list_redeem_codes())}`"
    if update.callback_query: await safe_edit(update.callback_query,txt,admin_kb())
    else: await safe_reply(update,txt,admin_kb())
    return ConversationHandler.END

async def admin_back(u,c): await admin_panel(u,c)
async def adm_add_s(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer();await safe_edit(q,"➕ User ID:\n/cancel");return ADMIN_ADD_ID
async def adm_add_id(u,c):
    uid=u.message.text.strip()
    if not uid.isdigit(): await safe_reply(u,"❌ Invalid!\n/cancel");return ADMIN_ADD_ID
    c.user_data["admin_uid"]=uid;await safe_reply(u,f"User: `{uid}`\nPlan:",plan_kb("plan"));return ADMIN_ADD_PLAN
async def adm_add_plan(u,c):
    q=u.callback_query;await q.answer()
    if q.data=="admin_back": await admin_panel(u,c);return ConversationHandler.END
    pm={"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk=pm.get(q.data,"7days");uid=c.user_data.get("admin_uid");plan=PLANS.get(pk)
    exp=upgrade(int(uid),pk);dl="∞" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(q,f"✅ *Added!*\n🆔 `{uid}`\n📦 {plan['name']}\n📅 {exp}\n📱 {dl}",admin_kb());return ConversationHandler.END
async def adm_rem_s(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer();await safe_edit(q,"❌ User ID:\n/cancel");return ADMIN_REM_ID
async def adm_rem_p(u,c):
    uid=u.message.text.strip();delete_user(uid);await safe_reply(u,f"✅ `{uid}` removed!",admin_kb());return ConversationHandler.END
async def adm_sp_s(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer();await safe_edit(q,"📅 User ID:\n/cancel");return ADMIN_EXP_ID
async def adm_sp_id(u,c):
    uid=u.message.text.strip();c.user_data["admin_uid"]=uid;await safe_reply(u,f"User: `{uid}`\nPlan:",plan_kb("plan"));return ADMIN_EXP_PLAN
async def adm_sp_set(u,c):
    q=u.callback_query;await q.answer()
    if q.data=="admin_back": await admin_panel(u,c);return ConversationHandler.END
    pm={"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk=pm.get(q.data,"7days");uid=c.user_data.get("admin_uid");plan=PLANS.get(pk)
    exp=upgrade(int(uid),pk);dl="∞" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(q,f"✅ *Updated!*\n🆔 `{uid}`\n📦 {plan['name']}\n📅 {exp}\n📱 {dl}",admin_kb());return ConversationHandler.END
async def adm_list(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer();users=load_users()
    if not users: await safe_edit(q,"📋 No users!",admin_kb());return
    txt=f"{BANNER_MINI}\n📋 *Users ({len(users)})*\n\n"
    for uid,info in users.items():
        plan=get_plan(info);ts=info.get("total_searches",0)
        if int(uid) in ADMIN_IDS: st="🛡️"
        elif info.get("is_premium") and info.get("expiry"):
            try: ed=date.fromisoformat(info["expiry"]);st=f"💎{(ed-date.today()).days}d" if date.today()<=ed else "🔴Exp"
            except: st="⚪"
        else: st="🆓"
        txt+=f"`{uid}`|{st}|🔍{ts}\n"
    await safe_edit(q,txt[:4000],admin_kb())
async def adm_stats(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer();users=load_users();ts=sum(v.get("total_searches",0) for v in users.values())
    act=sum(1 for u2,v in users.items() if v.get("is_premium") and int(u2) not in ADMIN_IDS)
    await safe_edit(q,f"{BANNER_MINI}\n📊 *Stats*\n\n👥{len(users)}|🔍{ts}|💎{act}|🎟️{len(list_redeem_codes())}\n📅{date.today()}",admin_kb())
async def adm_monitor(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer();users=load_users();free=[v for u2,v in users.items() if not v.get("is_premium") and int(u2) not in ADMIN_IDS]
    await safe_edit(q,f"{BANNER_MINI}\n🆓 *Monitor*\n👥 Free: `{len(free)}`",monitor_kb())
async def mon_exhausted(u,c):
    q=u.callback_query;await q.answer();users=load_users();txt=f"{BANNER_MINI}\n🔴 *Exhausted*\n\n";cnt=0
    aks=[("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE),("vinfo_free_used",VINFO_FREE)]
    for uid,info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"): continue
        if all(max(0,mx-info.get(k,0))<=0 for k,mx in aks): txt+=f"🔴`{uid}`|🔍{info.get('total_searches',0)}\n";cnt+=1
    txt+=f"\n💡 *{cnt}*";await safe_edit(q,txt[:4000],monitor_kb())
async def mon_active(u,c):
    q=u.callback_query;await q.answer();users=load_users();txt=f"{BANNER_MINI}\n🟢 *Active*\n\n";cnt=0
    aks=[("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE),("vinfo_free_used",VINFO_FREE)]
    for uid,info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"): continue
        if any(max(0,mx-info.get(k,0))>0 for k,mx in aks): txt+=f"🟢`{uid}`\n";cnt+=1
    txt+=f"\n{cnt}";await safe_edit(q,txt[:4000],monitor_kb())
async def mon_summary(u,c):
    q=u.callback_query;await q.answer();users=load_users();t=0;ex=0
    aks=[("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE),("vinfo_free_used",VINFO_FREE)]
    for uid,info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"): continue
        t+=1
        if all(max(0,mx-info.get(k,0))<=0 for k,mx in aks): ex+=1
    await safe_edit(q,f"{BANNER_MINI}\n📊 Free:`{t}`|Exhausted:`{ex}`|📅{date.today()}",monitor_kb())
async def bc_start(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer();await safe_edit(q,f"{BANNER_MINI}\n📢 *Broadcast*\n👥{len(load_users())}\nMessage:\n/cancel");return ADMIN_BROADCAST_MSG
async def bc_msg(u,c):
    m=u.message.text.strip()
    if not m: await safe_reply(u,"❌ Empty!\n/cancel");return ADMIN_BROADCAST_MSG
    c.user_data["bc"]=m
    await safe_reply(u,f"📢 *Preview:*\n\n{m}\n\n👥{len(load_users())}\nSure?",InlineKeyboardMarkup([[InlineKeyboardButton("✅ Send!",callback_data="broadcast_confirm")],[InlineKeyboardButton("❌ Cancel",callback_data="broadcast_cancel")]]));return ADMIN_BROADCAST_CONFIRM
async def bc_confirm(u,c):
    q=u.callback_query;await q.answer()
    if q.data=="broadcast_cancel": await safe_edit(q,"❌ Cancelled!",admin_kb());c.user_data.pop("bc",None);return ConversationHandler.END
    msg=c.user_data.get("bc","");users=load_users();total=len(users)
    bt=f"{BANNER_MINI}\n📢 *Announcement*\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{msg}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━\n💬 {OWNER_CONTACT}"
    sm=await safe_reply(u,f"🚀 {total}...");s,f2,b,ct=0,0,0,0
    for uid in users:
        ct+=1
        try: await c.bot.send_message(chat_id=int(uid),text=bt,parse_mode="Markdown");s+=1
        except Exception as e:
            if any(w in str(e).lower() for w in ["blocked","forbidden","not found"]): b+=1
            else: f2+=1
        if ct%10==0 or ct==total:
            try: await sm.edit_text(f"🚀{ct}/{total}|✅{s}|🚫{b}|❌{f2}",parse_mode="Markdown")
            except: pass
    await safe_reply(u,f"✅ Done!\n👥{total}|✅{s}|🚫{b}|❌{f2}",admin_kb());c.user_data.pop("bc",None);return ConversationHandler.END
async def custom_s(u,c):
    q=u.callback_query;await q.answer();await safe_edit(q,"⚙️ Days?\n/cancel");return ADMIN_CUSTOM_DAYS
async def custom_days(u,c):
    t=u.message.text.strip()
    if not t.isdigit() or int(t)<=0: await safe_reply(u,"❌!\n/cancel");return ADMIN_CUSTOM_DAYS
    c.user_data["cd"]=int(t);await safe_reply(u,f"📅{t}D\nLimit? (0=∞)\n/cancel");return ADMIN_CUSTOM_LIMIT
async def custom_limit(u,c):
    t=u.message.text.strip()
    if not t.isdigit(): await safe_reply(u,"❌!\n/cancel");return ADMIN_CUSTOM_LIMIT
    lim=int(t);unl=(lim==0);days=c.user_data.get("cd");uid=c.user_data.get("admin_uid")
    exp=upgrade_custom(int(uid),days,lim,unl);await safe_reply(u,f"⚙️ Set!\n`{uid}`|{days}D|{exp}|{'∞' if unl else f'{lim}/day'}",admin_kb())
    c.user_data.pop("cd",None);c.user_data.pop("admin_uid",None);return ConversationHandler.END

async def main_menu_cb(u,c): await start(u,c);return ConversationHandler.END
async def error_handler(update,context): logger.error(f"❌ {context.error}")

# ================== MAIN ==================
def main():
    threading.Thread(target=start_webserver,daemon=True).start();print("🌐 Keep-alive!")
    req=HTTPXRequest(connect_timeout=30,read_timeout=30,write_timeout=30,pool_timeout=30)
    gur=HTTPXRequest(connect_timeout=30,read_timeout=30,write_timeout=30,pool_timeout=30)
    app=ApplicationBuilder().token(BOT_TOKEN).request(req).get_updates_request(gur).build()
    C=ConversationHandler;CQ=CallbackQueryHandler;MH=MessageHandler;CMD=CommandHandler
    F=filters.TEXT&~filters.COMMAND;UF=[CMD("cancel",cancel),CMD("start",start)]
    convs=[
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
        C(entry_points=[CQ(admin_redeem_create_start,pattern="^admin_redeem_create$")],states={REDEEM_CREATE_CODE:[MH(F,admin_redeem_code_input)],REDEEM_CREATE_SEARCHES:[MH(F,admin_redeem_searches_input)],REDEEM_CREATE_LIMIT:[MH(F,admin_redeem_limit_input)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(admin_redeem_delete_start,pattern="^admin_redeem_delete$")],states={REDEEM_DELETE_CODE:[MH(F,admin_redeem_delete_input)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_add_s,pattern="^admin_add$")],states={ADMIN_ADD_ID:[MH(F,adm_add_id)],ADMIN_ADD_PLAN:[CQ(custom_s,pattern="^plan_custom$"),CQ(adm_add_plan,pattern="^plan_")],ADMIN_CUSTOM_DAYS:[MH(F,custom_days)],ADMIN_CUSTOM_LIMIT:[MH(F,custom_limit)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_rem_s,pattern="^admin_remove$")],states={ADMIN_REM_ID:[MH(F,adm_rem_p)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_sp_s,pattern="^admin_setplan$")],states={ADMIN_EXP_ID:[MH(F,adm_sp_id)],ADMIN_EXP_PLAN:[CQ(custom_s,pattern="^plan_custom$"),CQ(adm_sp_set,pattern="^plan_")],ADMIN_CUSTOM_DAYS:[MH(F,custom_days)],ADMIN_CUSTOM_LIMIT:[MH(F,custom_limit)]},fallbacks=UF,per_message=False,allow_reentry=True),
        C(entry_points=[CQ(bc_start,pattern="^admin_broadcast$")],states={ADMIN_BROADCAST_MSG:[MH(F,bc_msg)],ADMIN_BROADCAST_CONFIRM:[CQ(bc_confirm,pattern="^broadcast_(confirm|cancel)$")]},fallbacks=UF,per_message=False,allow_reentry=True),
    ]
    for cv in convs: app.add_handler(cv)
    app.add_handler(CMD("start",start));app.add_handler(CMD("admin",admin_panel));app.add_handler(CMD("redeem",redeem_command))
    app.add_error_handler(error_handler)
    for p,f2 in [("mode_phone",mode_phone),("mode_email",mode_email),("mode_upi",mode_upi),("mode_aadhaar",mode_aadhaar),("mode_vehicle",mode_vehicle),("mode_ifsc",mode_ifsc),("mode_vinfo",mode_vinfo),("redeem_info",redeem_info),("profile",profile),("status",status_check),("help",help_menu),("buy",buy),("admin_list",adm_list),("admin_stats",adm_stats),("admin_back",admin_back),("admin_free_monitor",adm_monitor),("admin_redeem_list",admin_redeem_list),("monitor_exhausted",mon_exhausted),("monitor_active",mon_active),("monitor_summary",mon_summary),("main_menu",main_menu_cb),("verify_join",verify_join)]:
        app.add_handler(CQ(f2,pattern=f"^{p}$"))
    print("🤖 ZERO TRACE Bot Running! Banner + Loading + UPI Active!")
    app.run_polling(drop_pending_updates=True,allowed_updates=["message","callback_query"])

if __name__=="__main__": main()

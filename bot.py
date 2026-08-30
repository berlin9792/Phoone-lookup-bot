#!/usr/bin/env python3
"""
🔍 Ultimate Intelligence Bot
Phone + Email + UPI + Aadhaar + Vehicle + IFSC
ONE PLAN = ALL ACCESS
+ Force Join + Broadcast + Custom Plan + MongoDB Cloud
"""

import json, os, threading, requests
from datetime import date, timedelta
from pathlib import Path
from flask import Flask
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
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
AADHAAR_API_URL = "https://nitin-developer-api-paid.nitinshab43.workers.dev/api"
VEHICLE_API_URL = "https://ansh-apis.is-dev.org/api/vehicle"
IFSC_API_URL    = "https://all-api-by-nitin-developer-best1.binderdhaniya6.workers.dev/api"
NITIN_API_KEY   = "JAANI"
VEHICLE_API_KEY = "ansh"
IFSC_API_KEY    = "NITIN"
OWNER_CONTACT   = "@theplayerror"
FORCE_JOIN_CHANNEL    = "@hackkwr"
FORCE_JOIN_CHANNEL_ID = "@hackkwr"

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

# ================== FLASK WEBSERVER ==================
web_app = Flask(__name__)
@web_app.route('/')
def keep_alive(): return "Bot Active!", 200
def start_webserver():
    import logging; logging.getLogger('werkzeug').setLevel(logging.ERROR)
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================== ADMIN CHECK ==================
def is_admin(uid): return uid in ADMIN_IDS

# ================== FORCE JOIN ==================
async def check_joined(context, uid):
    if is_admin(uid): return True
    try:
        m = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL_ID, uid)
        return m.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except: return False

def force_join_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_JOIN_CHANNEL.replace('@','')}")],
        [InlineKeyboardButton("✅ I Joined — Verify", callback_data="verify_join")],
    ])

# ================== MONGODB ==================
try:
    mc = MongoClient(MONGO_URI); db = mc["tele_intel_bot"]; users_col = db["users"]
    mc.admin.command('ping'); print("✅ MongoDB Connected!")
except Exception as e: print("⚠️ MongoDB:", e); users_col = None

LOCAL_FILE = Path("users.json")

def load_users():
    if users_col:
        try: return {d["_id"]:{k:v for k,v in d.items() if k!="_id"} for d in users_col.find()}
        except: pass
    if LOCAL_FILE.exists():
        try: return json.loads(LOCAL_FILE.read_text())
        except: return {}
    return {}

def save_user(uid, data):
    if users_col:
        try: users_col.update_one({"_id":str(uid)},{"$set":data},upsert=True); return
        except: pass
    d=load_users(); d[str(uid)]=data; LOCAL_FILE.write_text(json.dumps(d,indent=2))

def save_users(data):
    if users_col:
        try:
            for u,d in data.items(): users_col.update_one({"_id":str(u)},{"$set":d},upsert=True)
            return
        except: pass
    LOCAL_FILE.write_text(json.dumps(data,indent=2))

def delete_user(uid):
    if users_col:
        try: users_col.delete_one({"_id":str(uid)}); return
        except: pass
    d=load_users()
    if str(uid) in d: del d[str(uid)]; LOCAL_FILE.write_text(json.dumps(d,indent=2))

DEFAULTS = {
    "plan":"trial","expiry":"","is_premium":False,
    "phone_free_used":0,"phone_daily":0,"phone_date":"","phone_total":0,
    "email_free_used":0,"email_total":0,
    "upi_free_used":0,"upi_daily":0,"upi_date":"","upi_total":0,
    "aadhaar_free_used":0,"aadhaar_daily":0,"aadhaar_date":"","aadhaar_total":0,
    "vehicle_free_used":0,"vehicle_daily":0,"vehicle_date":"","vehicle_total":0,
    "ifsc_free_used":0,"ifsc_daily":0,"ifsc_date":"","ifsc_total":0,
    "total_searches":0,
}

def get_user(uid):
    uid=str(uid)
    if users_col:
        try:
            doc=users_col.find_one({"_id":uid})
            if not doc:
                d={**DEFAULTS,"added":date.today().isoformat()}
                users_col.insert_one({"_id":uid,**d}); return d
            doc.pop("_id",None); ch=False
            for k,v in DEFAULTS.items():
                if k not in doc: doc[k]=v; ch=True
            if ch: save_user(uid,doc)
            return doc
        except: pass
    users=load_users()
    if uid not in users:
        users[uid]={**DEFAULTS,"added":date.today().isoformat()}
        save_users(users)
    return users[uid]

# ================== PLAN RESOLVER ==================
def get_plan(ud):
    pk=ud.get("plan","trial")
    if pk.startswith("custom_"):
        try: d=int(pk.split("_")[1].replace("d",""))
        except: d=30
        return {"name":f"Custom ({d}D)","days":d,"daily_limit":ud.get("custom_limit",0),"unlimited":ud.get("custom_unlimited",False),"is_free":False}
    return PLANS.get(pk,PLANS["trial"])

# ================== PLAN UPGRADE ==================
def upgrade(uid, pk):
    uid=str(uid); ud=get_user(uid); plan=PLANS.get(pk,PLANS["7days"])
    exp=(date.today()+timedelta(days=plan["days"])).isoformat()
    ud.update({"plan":pk,"expiry":exp,"is_premium":True,"phone_daily":0,"phone_date":"","upi_daily":0,"upi_date":"","aadhaar_daily":0,"aadhaar_date":"","vehicle_daily":0,"vehicle_date":"","ifsc_daily":0,"ifsc_date":""})
    save_user(uid,ud); return exp

def upgrade_custom(uid, days, lim, unl):
    uid=str(uid); ud=get_user(uid)
    exp=(date.today()+timedelta(days=days)).isoformat()
    ud.update({"plan":f"custom_{days}d","expiry":exp,"is_premium":True,"phone_daily":0,"phone_date":"","upi_daily":0,"upi_date":"","aadhaar_daily":0,"aadhaar_date":"","vehicle_daily":0,"vehicle_date":"","ifsc_daily":0,"ifsc_date":"","custom_limit":lim,"custom_unlimited":unl})
    save_user(uid,ud); return exp

# ================== GENERIC ACCESS SYSTEM ==================
def free_rem(uid, key, mx):
    if is_admin(uid): return 999999
    return max(0, mx - get_user(uid).get(key, 0))

def daily_rem(uid, dk, dtk):
    if is_admin(uid): return 999999
    ud=get_user(uid); plan=get_plan(ud)
    if plan.get("unlimited"): return 999999
    lim=plan.get("daily_limit",0)
    if ud.get(dtk,"")!=date.today().isoformat(): return lim
    return max(0, lim-ud.get(dk,0))

def use_search(uid, fk, dk, dtk, tk):
    uid=str(uid); ud=get_user(uid); today=date.today().isoformat()
    if ud.get(dtk,"")!=today: ud[dk]=0; ud[dtk]=today
    plan=get_plan(ud)
    if not is_admin(int(uid)):
        if plan.get("is_free",True): ud[fk]=ud.get(fk,0)+1
        else: ud[dk]=ud.get(dk,0)+1
    ud[tk]=ud.get(tk,0)+1; ud["total_searches"]=ud.get("total_searches",0)+1
    save_user(uid,ud)

def check_access(uid, fk, mx, dk, dtk, name):
    if is_admin(uid): return True,"Admin ∞",9999,True,"12months"
    ud=get_user(uid); plan=get_plan(ud); pk=ud.get("plan","trial")
    exp_s=ud.get("expiry",""); is_p=ud.get("is_premium",False)
    if is_p and exp_s:
        try:
            exp=date.fromisoformat(exp_s)
            if date.today()>exp:
                fl=free_rem(uid,fk,mx)
                if fl>0: return True,f"Expired|{fl} free",0,False,"trial"
                return False,"Expired! Renew.",0,False,"trial"
            dl=(exp-date.today()).days; dr=daily_rem(uid,dk,dtk); lim=plan.get("daily_limit",0)
            if plan.get("unlimited"): return True,f"{plan['name']}|∞|{dl}d",dl,True,pk
            if dr<=0: return False,f"{name} limit done!({lim}/day)",dl,True,pk
            return True,f"{plan['name']}|{dr}/{lim}|{dl}d",dl,True,pk
        except: pass
    fl=free_rem(uid,fk,mx)
    if fl>0: return True,f"Trial({fl}/{mx})",0,False,"trial"
    return False,"Trial done! Buy plan.",0,False,"trial"

# Shortcuts
def phone_free(u): return free_rem(u,"phone_free_used",PHONE_FREE)
def phone_daily(u): return daily_rem(u,"phone_daily","phone_date")
def phone_use(u): use_search(u,"phone_free_used","phone_daily","phone_date","phone_total")
def phone_check(u): return check_access(u,"phone_free_used",PHONE_FREE,"phone_daily","phone_date","Phone")

def email_free(u): return free_rem(u,"email_free_used",EMAIL_FREE)
def email_use(uid, is_p):
    uid=str(uid); ud=get_user(uid)
    if not is_admin(int(uid)) and not is_p: ud["email_free_used"]=ud.get("email_free_used",0)+1
    ud["email_total"]=ud.get("email_total",0)+1; ud["total_searches"]=ud.get("total_searches",0)+1
    save_user(uid,ud)
def email_check(uid):
    if is_admin(uid): return True,"Admin ∞",9999,True
    ud=get_user(uid); is_p=ud.get("is_premium",False); exp_s=ud.get("expiry","")
    if is_p and exp_s:
        try:
            exp=date.fromisoformat(exp_s)
            if date.today()>exp:
                fl=email_free(uid)
                if fl>0: return True,f"Expired|{fl} free",0,False
                return False,"Expired!",0,False
            return True,f"Premium({(exp-date.today()).days}d)",( exp-date.today()).days,True
        except: pass
    fl=email_free(uid)
    if fl>0: return True,f"Free({fl}/{EMAIL_FREE})",0,False
    return False,"Free done!",0,False

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

# ================== SAFE API CALLS (HIDE URL ON ERROR) ==================
def _safe_api(fn):
    """Wraps API call to hide URL in error messages"""
    try:
        return fn()
    except requests.exceptions.Timeout:
        return {"ok":False,"error":"⏱️ Request timed out. Try again later."}
    except requests.exceptions.ConnectionError:
        return {"ok":False,"error":"🌐 Connection error. Service temporarily unavailable."}
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else "Unknown"
        return {"ok":False,"error":f"⚠️ Service returned error code: {code}"}
    except Exception:
        return {"ok":False,"error":"❌ Service temporarily unavailable. Try again later."}

def search_api(term):
    def call():
        r=requests.get(API_URL,params={"pin":DEFAULT_PIN,"term":term},timeout=20)
        r.raise_for_status(); return {"ok":True,"data":r.json()}
    return _safe_api(call)

def upi_api(upi_id):
    def call():
        r=requests.get(UPI_API_URL,params={"action":"upiinfo","upi":upi_id,"key":NITIN_API_KEY},timeout=20)
        r.raise_for_status(); return {"ok":True,"data":r.json()}
    return _safe_api(call)

def aadhaar_api(num):
    def call():
        r=requests.get(AADHAAR_API_URL,params={"action":"aadhar","aadhar":num,"key":NITIN_API_KEY},timeout=20)
        r.raise_for_status(); return {"ok":True,"data":r.json()}
    return _safe_api(call)

def vehicle_api(rc):
    def call():
        r=requests.get(VEHICLE_API_URL,params={"key":VEHICLE_API_KEY,"rc":rc},timeout=20)
        r.raise_for_status(); return {"ok":True,"data":r.json()}
    return _safe_api(call)

def ifsc_api(code):
    def call():
        r=requests.get(IFSC_API_URL,params={"type":"ifsc","search":code,"api_key":IFSC_API_KEY},timeout=20)
        r.raise_for_status(); return {"ok":True,"data":r.json()}
    return _safe_api(call)

# ================== FORMAT ==================
SKIP_K={"timestamp","response_time","response_time_ms","developer","owner","credit","credits","powered_by","source","api","version","status","message","code","time","created_at","updated_at","server","watermark","signature","by","made_by","contact","channel","group","join","advertisement","ads","promo","query"}
SKIP_E={"EncryptedPassword","encrypted_password","Salt","salt","PinCode","pin_code","CreditsInappPoints","IP","ip","TheDateOfTheEntrance"}
def sk(k):
    if k in SKIP_E: return True
    kl=k.lower().strip()
    if kl in SKIP_K: return True
    for w in ["timestamp","response","developer","owner","credit","powered","source","version","watermark","pheevar","advertisement","promo","channel","server","api_","made_by","encrypted","password","salt"]:
        if w in kl: return True
    return False
def sv(v):
    if v is None or v=="": return True
    vs=str(v).lower().strip()
    if vs in ("","none","null","n/a","na","-","0","0.00","0000-00-00"): return True
    for s in ["@pheevar","pheevar","@lk_","t.me/","telegram.me/"]:
        if s in vs: return True
    return False
def em(k):
    k=k.lower()
    for kw,e in {"name":"👤","email":"📧","phone":"📞","mobile":"📞","address":"📍","city":"🏙️","state":"🗺️","country":"🌍","pincode":"📮","upi":"💳","vpa":"💳","bank":"🏦","ifsc":"🏦","account":"🏦","dob":"🎂","gender":"🚻","pan":"🪪","aadhar":"🪪","aadhaar":"🪪","father":"👨","mother":"👩","vehicle":"🚗","rc":"🚗","owner":"👤","model":"🚗","fuel":"⛽","engine":"🔧","chassis":"🔧","registration":"📅","insurance":"📋","fitness":"📋","branch":"🏦","district":"🗺️","contact":"📞","micr":"🔢","swift":"🔢","verified":"✅","valid":"✅","payee":"💳","merchant":"🏪"}.items():
        if kw in k: return e
    return "📌"

def fmt_rec(rec):
    lines=[]
    for k,v in rec.items():
        if sk(k) or sv(v): continue
        if isinstance(v,dict):
            for a,b in v.items():
                if sk(a) or sv(b): continue
                lines.append(f"{em(a.lower())} *{a.replace('_',' ').title()}*: `{b}`")
            continue
        if isinstance(v,list):
            cl=[str(i) for i in v if not sv(i)]
            if cl: lines.append(f"{em(k.lower())} *{k.replace('_',' ').title()}*: `{', '.join(cl)}`")
            continue
        lines.append(f"{em(k.lower())} *{k.replace('_',' ').title()}*: `{v}`")
    return lines

def fmt(term,data,icon="🔍"):
    if not data: return f"{icon} *{term}*\n_No data found_"
    if isinstance(data,list):
        if not data: return f"{icon} *{term}*\n_No data found_"
        if isinstance(data[0],dict): data={"data":{"s":{"records":data}}}
        else: return f"{icon} *{term}*\n`{data[0]}`"
    if not isinstance(data,dict): return f"{icon} *{term}*\n`{data}`"
    md=data.get("data",data); recs=[]
    if isinstance(md,dict):
        hs=False
        for k,v in md.items():
            if isinstance(v,dict) and "records" in v:
                hs=True
                for r in (v["records"] if isinstance(v["records"],list) else []):
                    if isinstance(r,dict): recs.append(r)
        if not hs and "records" in md:
            for r in (md["records"] if isinstance(md["records"],list) else []):
                if isinstance(r,dict): recs.append(r)
        if not recs and not hs: recs.append(md)
    elif isinstance(md,list):
        for r in md:
            if isinstance(r,dict): recs.append(r)
    if not recs: return f"{icon} *{term}*\n_No data found_"
    seen,uniq=set(),[]
    for r in recs:
        ident=str(r.get("FullName",r.get("Name",r.get("Email","")))).lower()+str(r.get("Phone",r.get("Phone2","")))
        if ident not in seen: seen.add(ident); uniq.append(r)
    div="━"*28
    out=[f"{icon} *Result for* `{term}`",f"📊 *{len(uniq)} record(s)*",div]
    for i,r in enumerate(uniq,1):
        if len(uniq)>1: out.append(f"\n*━━ #{i} ━━*")
        ls=fmt_rec(r); out.extend(ls if ls else ["_No data_"])
    return "\n".join(out)

def fmt_special(title, icon, id_label, search_id, data):
    if not data: return f"{icon} *{search_id}*\n_No data found_"
    if not isinstance(data,dict): return f"{icon} *{search_id}*\n`{data}`"
    div="━"*28
    lines=[f"{icon} *{title}*",div,f"🆔 *{id_label}:* `{search_id}`"]
    found=False
    for k,v in data.items():
        if sk(k) or sv(v): continue
        if isinstance(v,dict):
            for a,b in v.items():
                if sk(a) or sv(b): continue
                lines.append(f"{em(a.lower())} *{a.replace('_',' ').title()}*: `{b}`"); found=True
            continue
        lines.append(f"{em(k.lower())} *{k.replace('_',' ').title()}*: `{v}`"); found=True
    if not found: lines.append("_No relevant data_")
    lines.append(div); return "\n".join(lines)

# ================== KEYBOARDS ==================
def main_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Phone",callback_data="mode_phone"),InlineKeyboardButton("📧 Email",callback_data="mode_email")],
        [InlineKeyboardButton("💳 UPI",callback_data="mode_upi"),InlineKeyboardButton("🪪 Aadhaar",callback_data="mode_aadhaar")],
        [InlineKeyboardButton("🚗 Vehicle RC",callback_data="mode_vehicle"),InlineKeyboardButton("🏦 IFSC",callback_data="mode_ifsc")],
        [InlineKeyboardButton("👤 Profile",callback_data="profile"),InlineKeyboardButton("📊 Status",callback_data="status")],
        [InlineKeyboardButton("💰 Buy Plan",callback_data="buy"),InlineKeyboardButton("❓ Help",callback_data="help")],
    ])

def search_kb(uid, check_fn, free_fn, daily_fn, prefix, mx):
    if is_admin(uid): sl,bl="🔍Single(Admin)","📦Batch(Admin)"
    else:
        ok,_,_,ip,_=check_fn(uid); fl=free_fn(uid); dr=daily_fn(uid)
        ud=get_user(uid); p=get_plan(ud)
        if ip:
            if p.get("unlimited"): sl,bl="🔍Single(∞)","📦Batch(∞)"
            else: sl,bl=f"🔍Single({dr}today)",f"📦Batch({dr}today)"
        elif fl>0: sl,bl=f"🔍Single({fl}trial)",f"📦Batch({fl}trial)"
        else: sl,bl="🔍Single(🔒)","📦Batch(🔒)"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(sl,callback_data=f"{prefix}_single"),InlineKeyboardButton(bl,callback_data=f"{prefix}_batch")],
        [InlineKeyboardButton("🔙 Menu",callback_data="main_menu")],
    ])

def email_kb(uid):
    if is_admin(uid): sl,bl="🔍Single(Admin)","📦Batch(Admin)"
    else:
        ok,_,_,ip=email_check(uid); fl=email_free(uid)
        if ip: sl,bl="🔍Single(∞)","📦Batch(∞)"
        elif fl>0: sl,bl=f"🔍Single({fl}free)",f"📦Batch({fl}free)"
        else: sl,bl="🔍Single(🔒)","📦Batch(🔒)"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(sl,callback_data="email_single"),InlineKeyboardButton(bl,callback_data="email_batch")],
        [InlineKeyboardButton("🔙 Menu",callback_data="main_menu")],
    ])

def country_kb(m):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇳 India(+91)",callback_data=f"country_india_{m}")],
        [InlineKeyboardButton("🌍 Other",callback_data=f"country_other_{m}")],
        [InlineKeyboardButton("❌ Cancel",callback_data="main_menu")],
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕Add",callback_data="admin_add"),InlineKeyboardButton("❌Remove",callback_data="admin_remove")],
        [InlineKeyboardButton("📅Plan",callback_data="admin_setplan"),InlineKeyboardButton("📋Users",callback_data="admin_list")],
        [InlineKeyboardButton("📊Stats",callback_data="admin_stats"),InlineKeyboardButton("🆓Monitor",callback_data="admin_free_monitor")],
        [InlineKeyboardButton("📢Broadcast",callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙Menu",callback_data="main_menu")],
    ])

def back_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu",callback_data="main_menu")]])
def buy_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Contact",url=f"https://t.me/{OWNER_CONTACT.replace('@','')}")],
        [InlineKeyboardButton("🔙 Menu",callback_data="main_menu")],
    ])
def plan_kb(pf):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🥉7D₹50",callback_data=f"{pf}_7days"),InlineKeyboardButton("🥈30D₹130",callback_data=f"{pf}_30days")],
        [InlineKeyboardButton("🥇6M₹300",callback_data=f"{pf}_6months"),InlineKeyboardButton("💎12M₹799",callback_data=f"{pf}_12months")],
        [InlineKeyboardButton("⚙️Custom",callback_data=f"{pf}_custom")],
        [InlineKeyboardButton("❌Cancel",callback_data="admin_back")],
    ])
def monitor_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴Exhausted",callback_data="monitor_exhausted"),InlineKeyboardButton("🟢Active",callback_data="monitor_active")],
        [InlineKeyboardButton("📊Summary",callback_data="monitor_summary")],
        [InlineKeyboardButton("🔙Admin",callback_data="admin_back")],
    ])

# ================== HELPERS ==================
async def safe_edit(q, t, kb=None, pm="Markdown"):
    try: await q.edit_message_text(t, reply_markup=kb, parse_mode=pm)
    except: pass

def valid_email(e): return "@" in e and "." in e.split("@")[-1] and " " not in e
def valid_upi(u): return "@" in u and len(u)>=5 and " " not in u
def valid_aadhaar(a): return a.isdigit() and len(a)==12
def valid_ifsc(c): return len(c)==11 and c[:4].isalpha() and c[4]=="0" and c[5:].isdigit()

# ================== START ==================
async def start(update: Update, context):
    user=update.effective_user; get_user(user.id)
    if not is_admin(user.id):
        if not await check_joined(context,user.id):
            t=f"━"*30+f"\n🔍 *Ultimate Lookup Bot*\n"+"━"*30+f"\n\n👋 *{user.first_name}*!\n\n⚠️ *Pehle channel join karo!*\n📢 {FORCE_JOIN_CHANNEL}\n\nJoin → ✅ Verify 👇"
            if update.callback_query: await safe_edit(update.callback_query,t,force_join_kb())
            else: await update.message.reply_text(t,reply_markup=force_join_kb(),parse_mode="Markdown")
            return ConversationHandler.END
    d1="━"*30
    if is_admin(user.id):
        t=f"{d1}\n🔍 *Ultimate Lookup Bot*\n{d1}\n\n👋 *{user.first_name}*! 🛡️Admin\n\nAll: ∞ Unlimited\n\nChoose search 👇"
    else:
        ud=get_user(user.id); plan=get_plan(ud)
        ip,exp=ud.get("is_premium",False),ud.get("expiry","")
        lines=[]
        for nm,ff,df,mx in [("📱Phone",phone_free,phone_daily,PHONE_FREE),("📧Email",email_free,lambda u:999999,EMAIL_FREE),("💳UPI",upi_free,upi_daily,UPI_FREE),("🪪Aadhaar",aadhaar_free,aadhaar_daily,AADHAAR_FREE),("🚗Vehicle",vehicle_free,vehicle_daily,VEHICLE_FREE),("🏦IFSC",ifsc_free,ifsc_daily,IFSC_FREE)]:
            fl=ff(user.id)
            if ip and exp:
                try:
                    ed=date.fromisoformat(exp); dl=(ed-date.today()).days
                    if dl>=0:
                        if nm=="📧Email": lines.append(f"{nm}: 💎∞ | {dl}d")
                        elif plan.get("unlimited"): lines.append(f"{nm}: 💎∞ | {dl}d")
                        else: dr=df(user.id); lines.append(f"{nm}: 💎{dr}/{plan.get('daily_limit',0)} | {dl}d")
                    else: lines.append(f"{nm}: ⚠️Expired({fl}/{mx})")
                except: lines.append(f"{nm}: ⚪Unknown")
            else: lines.append(f"{nm}: 🆓{fl}/{mx}")
        t=f"{d1}\n🔍 *Ultimate Lookup Bot*\n{d1}\n\n👋 *{user.first_name}*!\n\n"+"\n".join(lines)+f"\n\n💡 *Ek plan = sab access!*\n\n{d1}\nChoose search 👇"
    if update.callback_query: await safe_edit(update.callback_query,t,main_kb(user.id))
    else: await update.message.reply_text(t,reply_markup=main_kb(user.id),parse_mode="Markdown")
    return ConversationHandler.END

async def verify_join(update,context):
    q=update.callback_query; await q.answer()
    if await check_joined(context,q.from_user.id):
        await safe_edit(q,"✅ *Verified!* 🎉"); await start(update,context)
    else: await safe_edit(q,f"❌ *Join nahi kiya!*\n📢 {FORCE_JOIN_CHANNEL}",force_join_kb())

# ================== MODE HANDLERS ==================
async def _mode(update,context,title,icon,chk,ff,df,mx,mkb):
    q=update.callback_query; await q.answer(); u=q.from_user
    if not is_admin(u.id) and not await check_joined(context,u.id):
        await safe_edit(q,f"⚠️ *Join channel!*\n📢 {FORCE_JOIN_CHANNEL}",force_join_kb()); return
    if is_admin(u.id): info="🛡️Admin∞"
    else:
        ok,_,_,ip,_=chk(u.id); fl=ff(u.id); dr=df(u.id)
        p=get_plan(get_user(u.id))
        info="💎∞" if ip and p.get("unlimited") else (f"✅{dr}/{p.get('daily_limit',0)}" if ip else f"🆓{fl}/{mx}")
    await safe_edit(q,f"━"*30+f"\n{icon} *{title}*\n"+"━"*30+f"\n\n📊 {info}\n\nChoose:",mkb(u.id))

async def mode_phone(u,c): await _mode(u,c,"Phone Search","📱",phone_check,phone_free,phone_daily,PHONE_FREE,lambda uid:search_kb(uid,phone_check,phone_free,phone_daily,"phone",PHONE_FREE))
async def mode_email(update,context):
    q=update.callback_query; await q.answer(); u=q.from_user
    if not is_admin(u.id) and not await check_joined(context,u.id):
        await safe_edit(q,f"⚠️ *Join!*\n📢 {FORCE_JOIN_CHANNEL}",force_join_kb()); return
    if is_admin(u.id): info="🛡️Admin∞"
    else:
        ok,_,d,ip=email_check(u.id); fl=email_free(u.id)
        info=f"💎{d}d" if ip else f"🆓{fl}/{EMAIL_FREE}"
    await safe_edit(q,f"━"*30+f"\n📧 *Email Search*\n"+"━"*30+f"\n\n📊 {info}\n\nChoose:",email_kb(u.id))
async def mode_upi(u,c): await _mode(u,c,"UPI Search","💳",upi_check,upi_free,upi_daily,UPI_FREE,lambda uid:search_kb(uid,upi_check,upi_free,upi_daily,"upi",UPI_FREE))
async def mode_aadhaar(u,c): await _mode(u,c,"Aadhaar Search","🪪",aadhaar_check,aadhaar_free,aadhaar_daily,AADHAAR_FREE,lambda uid:search_kb(uid,aadhaar_check,aadhaar_free,aadhaar_daily,"aadhaar",AADHAAR_FREE))
async def mode_vehicle(u,c): await _mode(u,c,"Vehicle RC Search","🚗",vehicle_check,vehicle_free,vehicle_daily,VEHICLE_FREE,lambda uid:search_kb(uid,vehicle_check,vehicle_free,vehicle_daily,"vehicle",VEHICLE_FREE))
async def mode_ifsc(u,c): await _mode(u,c,"IFSC Lookup","🏦",ifsc_check,ifsc_free,ifsc_daily,IFSC_FREE,lambda uid:search_kb(uid,ifsc_check,ifsc_free,ifsc_daily,"ifsc",IFSC_FREE))

# ================== PROFILE / STATUS / HELP / BUY ==================
async def profile(update,context):
    q=update.callback_query; await q.answer(); u=q.from_user; ud=get_user(u.id)
    ts=ud.get("total_searches",0)
    t=f"━"*30+f"\n👤 *Profile*\n"+"━"*30+f"\n\n🆔 `{u.id}`\n👤 {u.first_name}\n\n📱:{ud.get('phone_total',0)} 📧:{ud.get('email_total',0)} 💳:{ud.get('upi_total',0)} 🪪:{ud.get('aadhaar_total',0)} 🚗:{ud.get('vehicle_total',0)} 🏦:{ud.get('ifsc_total',0)}\n🔍Total: {ts}"
    await safe_edit(q,t,back_kb())

async def status_check(update,context):
    q=update.callback_query; await q.answer(); u=q.from_user
    if is_admin(u.id): await safe_edit(q,"🛡️ *Admin* All ∞",back_kb()); return
    lines=[]
    for nm,chk,ff,df,mx in [("📱Phone",phone_check,phone_free,phone_daily,PHONE_FREE),("💳UPI",upi_check,upi_free,upi_daily,UPI_FREE),("🪪Aadhaar",aadhaar_check,aadhaar_free,aadhaar_daily,AADHAAR_FREE),("🚗Vehicle",vehicle_check,vehicle_free,vehicle_daily,VEHICLE_FREE),("🏦IFSC",ifsc_check,ifsc_free,ifsc_daily,IFSC_FREE)]:
        ok,st,_,ip,_=chk(u.id)
        if ip:
            p=get_plan(get_user(u.id)); dr=df(u.id); lim=p.get("daily_limit",0)
            lines.append(f"{nm}: {'∞' if p.get('unlimited') else f'{dr}/{lim}'}")
        else: lines.append(f"{nm}: 🆓{ff(u.id)}/{mx}")
    ok,st,_,ip=email_check(u.id)
    lines.append(f"📧Email: {'💎∞' if ip else f'🆓{email_free(u.id)}/{EMAIL_FREE}'}")
    await safe_edit(q,f"📊 *Status*\n\n"+"\n".join(lines)+f"\n\n💰 {OWNER_CONTACT}\nID: `{u.id}`",back_kb())

async def help_menu(update,context):
    q=update.callback_query; await q.answer()
    t=(f"━"*30+f"\n❓ *Help*\n"+"━"*30+"\n\n🎯 *Ek Plan = Sab Access!*\n\n"
       f"🥉7D₹50(5/day) 🥈30D₹130(10/day)\n🥇6M₹300(15/day) 💎12M₹799(∞)\n\n"
       f"🆓Free: Phone:{PHONE_FREE} Email:{EMAIL_FREE} UPI:{UPI_FREE} Aadhaar:{AADHAAR_FREE} Vehicle:{VEHICLE_FREE} IFSC:{IFSC_FREE}\n\n"
       "💳UPI: `name@bank`\n🪪Aadhaar: 12 digits\n🚗Vehicle: `MH01AB1234`\n🏦IFSC: `SBIN0001234`\n📦Batch: Comma, Max 15")
    await safe_edit(q,t,back_kb())

async def buy(update,context):
    q=update.callback_query; await q.answer(); u=q.from_user
    if is_admin(u.id): await safe_edit(q,"🛡️Admin! All ∞",back_kb()); return
    t=(f"━"*30+f"\n💰 *Buy Plan*\n"+"━"*30+"\n\n🎯 *All 6 Features in 1 Plan!*\n\n"
       "🥉7D₹50 🥈30D₹130 🥇6M₹300 💎12M₹799\n\n"
       f"📱{OWNER_CONTACT}\nID: `{u.id}`")
    await safe_edit(q,t,buy_kb())

# ================== GENERIC SEARCH HANDLER ==================
async def _single_start(update,context,chk,locked_msg,prompt,state):
    q=update.callback_query; await q.answer(); u=q.from_user
    if not is_admin(u.id) and not await check_joined(context,u.id):
        await safe_edit(q,f"⚠️ *Join!*\n📢 {FORCE_JOIN_CHANNEL}",force_join_kb()); return ConversationHandler.END
    ok,st,_,_,_=chk(u.id) if len(chk(u.id))==5 else (*chk(u.id),None)
    if not ok: await safe_edit(q,f"🔒 *Locked!*\n{st}\n💰 {OWNER_CONTACT}",buy_kb()); return ConversationHandler.END
    await safe_edit(q,prompt); return state

async def _batch_start(update,context,chk,prompt,state):
    q=update.callback_query; await q.answer(); u=q.from_user
    if not is_admin(u.id) and not await check_joined(context,u.id):
        await safe_edit(q,f"⚠️ *Join!*\n📢 {FORCE_JOIN_CHANNEL}",force_join_kb()); return ConversationHandler.END
    r=chk(u.id); ok=r[0]; st=r[1]
    if not ok: await safe_edit(q,f"🔒 *Locked!*\n{st}",buy_kb()); return ConversationHandler.END
    await safe_edit(q,prompt); return state

async def _do_single(update,context,api_fn,term,display,icon,use_fn,chk,fmt_fn=None):
    u=update.effective_user
    r=chk(u.id); ok=r[0]; st=r[1]
    if not ok: await update.message.reply_text(f"🔒 *Locked!*\n{st}",reply_markup=buy_kb(),parse_mode="Markdown"); return
    msg=await update.message.reply_text(f"🔍 Searching `{display}`...",parse_mode="Markdown")
    res=api_fn(term)
    if res["ok"]:
        use_fn(u.id)
        text=fmt_fn(term,res["data"]) if fmt_fn else fmt(display,res["data"],icon)
        await msg.edit_text(text,reply_markup=main_kb(u.id),parse_mode="Markdown")
    else:
        await msg.edit_text(f"❌ *Search Failed*\n`{res['error']}`",reply_markup=back_kb(),parse_mode="Markdown")

async def _do_batch(update,context,api_fn,items,icon,use_fn,chk,fmt_fn=None):
    u=update.effective_user; total=len(items)
    msg=await update.message.reply_text(f"🚀 Processing {total}...")
    for i,item in enumerate(items,1):
        res=api_fn(item)
        if res["ok"]:
            use_fn(u.id)
            text=fmt_fn(item,res["data"]) if fmt_fn else fmt(item,res["data"],icon)
            await update.message.reply_text(text,parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ *{item}*\n`{res['error']}`",parse_mode="Markdown")
    await msg.edit_text(f"✅ *Done!* Processed: {total}",reply_markup=main_kb(u.id),parse_mode="Markdown")

# ================== PHONE ==================
async def phone_single_s(u,c): return await _single_start(u,c,phone_check,"Phone","📱 Country?",PHONE_COUNTRY_SINGLE)
async def phone_batch_s(u,c): return await _batch_start(u,c,phone_check,"📦 Country?",PHONE_COUNTRY_BATCH)

async def phone_single_s2(u,c):
    q=u.callback_query; await q.answer()
    ok,st,_,_,_=phone_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒{st}",buy_kb()); return ConversationHandler.END
    await safe_edit(q,"📱 Country?",country_kb("single")); return PHONE_COUNTRY_SINGLE
async def phone_batch_s2(u,c):
    q=u.callback_query; await q.answer()
    ok,st,_,_,_=phone_check(q.from_user.id)
    if not ok: await safe_edit(q,f"🔒{st}",buy_kb()); return ConversationHandler.END
    await safe_edit(q,"📦 Country?",country_kb("batch")); return PHONE_COUNTRY_BATCH

async def cs_single(u,c):
    q=u.callback_query; await q.answer()
    if "india" in q.data:
        c.user_data["pc"]="india"; await safe_edit(q,"🇮🇳 10 digit:\n/cancel"); return PHONE_SINGLE_INDIA
    c.user_data["pc"]="other"; await safe_edit(q,"🌍 Code+Number:\n/cancel"); return PHONE_SINGLE_OTHER

async def cs_batch(u,c):
    q=u.callback_query; await q.answer()
    if "india" in q.data:
        c.user_data["pc"]="india"; await safe_edit(q,"🇮🇳 Numbers comma:\n/cancel"); return PHONE_BATCH_INDIA
    c.user_data["pc"]="other"; await safe_edit(q,"🌍 Numbers comma:\n/cancel"); return PHONE_BATCH_OTHER

async def psi(update,context):
    cl=update.message.text.strip().replace(" ","").replace("-","").replace("+","")
    if cl.startswith("91") and len(cl)==12: cl=cl[2:]
    if not cl.isdigit() or len(cl)!=10: await update.message.reply_text("❌ 10 digit!\n/cancel"); return PHONE_SINGLE_INDIA
    await _do_single(update,context,search_api,"91"+cl,"🇮🇳91"+cl,"📱",phone_use,phone_check); return ConversationHandler.END

async def pso(update,context):
    cl=update.message.text.strip().replace(" ","").replace("-","").replace("+","")
    if not cl.isdigit() or not(7<=len(cl)<=15): await update.message.reply_text("❌ 7-15 digit!\n/cancel"); return PHONE_SINGLE_OTHER
    await _do_single(update,context,search_api,cl,"🌍"+cl,"📱",phone_use,phone_check); return ConversationHandler.END

async def pbi(update,context):
    nums=[n.strip().replace(" ","").replace("-","").replace("+","") for n in update.message.text.split(",") if n.strip()]
    valid=[]
    for n in nums:
        if n.startswith("91") and len(n)==12: n=n[2:]
        if n.isdigit() and len(n)==10 and "91"+n not in valid: valid.append("91"+n)
    if not valid: await update.message.reply_text("❌ No valid!\n/cancel"); return PHONE_BATCH_INDIA
    await _do_batch(update,context,search_api,valid[:15],"📱",phone_use,phone_check); return ConversationHandler.END

async def pbo(update,context):
    nums=[n.strip().replace(" ","").replace("-","").replace("+","") for n in update.message.text.split(",") if n.strip()]
    valid=[n for n in nums if n.isdigit() and 7<=len(n)<=15]
    if not valid: await update.message.reply_text("❌ No valid!\n/cancel"); return PHONE_BATCH_OTHER
    await _do_batch(update,context,search_api,valid[:15],"📱",phone_use,phone_check); return ConversationHandler.END

# ================== EMAIL ==================
async def email_ss(u,c): return await _single_start(u,c,lambda uid:(*email_check(uid),None),"Email","📧 Email daalo:\n/cancel",EMAIL_SINGLE)
async def email_sp(update,context):
    e=update.message.text.strip(); u=update.effective_user
    if not valid_email(e): await update.message.reply_text("❌ Invalid!\n/cancel"); return EMAIL_SINGLE
    ok,_,_,ip=email_check(u.id)
    if not ok: await update.message.reply_text("🔒 Locked!",reply_markup=buy_kb(),parse_mode="Markdown"); return ConversationHandler.END
    msg=await update.message.reply_text("🔍 Searching...")
    res=search_api(e)
    if res["ok"]: email_use(u.id,ip); await msg.edit_text(fmt(e,res["data"],"📧"),reply_markup=main_kb(u.id),parse_mode="Markdown")
    else: await msg.edit_text(f"❌ *Failed*\n`{res['error']}`",reply_markup=back_kb(),parse_mode="Markdown")
    return ConversationHandler.END

async def email_bs(u,c): return await _batch_start(u,c,lambda uid:(*email_check(uid),None),"📦 Emails comma(Max15):\n/cancel",EMAIL_BATCH)
async def email_bp(update,context):
    emails=[e.strip() for e in update.message.text.split(",") if valid_email(e.strip())][:15]
    if not emails: await update.message.reply_text("❌ No valid!\n/cancel"); return EMAIL_BATCH
    u=update.effective_user; _,_,_,ip=email_check(u.id)
    msg=await update.message.reply_text(f"🚀 Processing {len(emails)}...")
    for e in emails:
        res=search_api(e)
        if res["ok"]: email_use(u.id,ip); await update.message.reply_text(fmt(e,res["data"],"📧"),parse_mode="Markdown")
        else: await update.message.reply_text(f"❌ *{e}*\n`{res['error']}`",parse_mode="Markdown")
    await msg.edit_text(f"✅ Done! {len(emails)}",reply_markup=main_kb(u.id),parse_mode="Markdown"); return ConversationHandler.END

# ================== UPI ==================
async def upi_ss(u,c): return await _single_start(u,c,upi_check,"UPI","💳 UPI ID:\n`name@bank`\n/cancel",UPI_SINGLE)
async def upi_sp(update,context):
    uid=update.message.text.strip(); u=update.effective_user
    if not valid_upi(uid): await update.message.reply_text("❌ `name@bank`\n/cancel",parse_mode="Markdown"); return UPI_SINGLE
    await _do_single(update,context,upi_api,uid,uid,"💳",upi_use,upi_check,lambda t,d:fmt_special("UPI Lookup","💳","UPI ID",t,d)); return ConversationHandler.END

async def upi_bs(u,c): return await _batch_start(u,c,upi_check,"📦 UPI IDs comma(Max15):\n/cancel",UPI_BATCH)
async def upi_bp(update,context):
    upis=[u.strip() for u in update.message.text.split(",") if valid_upi(u.strip())][:15]
    if not upis: await update.message.reply_text("❌ No valid!\n/cancel"); return UPI_BATCH
    await _do_batch(update,context,upi_api,upis,"💳",upi_use,upi_check,lambda t,d:fmt_special("UPI","💳","UPI",t,d)); return ConversationHandler.END

# ================== AADHAAR ==================
async def aadh_ss(u,c): return await _single_start(u,c,aadhaar_check,"Aadhaar","🪪 12 digit Aadhaar:\n/cancel",AADHAAR_SINGLE)
async def aadh_sp(update,context):
    a=update.message.text.strip().replace(" ","").replace("-","")
    if not valid_aadhaar(a): await update.message.reply_text("❌ 12 digits!\n/cancel"); return AADHAAR_SINGLE
    await _do_single(update,context,aadhaar_api,a,a,"🪪",aadhaar_use,aadhaar_check,lambda t,d:fmt_special("Aadhaar Lookup","🪪","Aadhaar",t,d)); return ConversationHandler.END

async def aadh_bs(u,c): return await _batch_start(u,c,aadhaar_check,"📦 Aadhaar numbers comma:\n/cancel",AADHAAR_BATCH)
async def aadh_bp(update,context):
    nums=[a.strip().replace(" ","").replace("-","") for a in update.message.text.split(",") if valid_aadhaar(a.strip().replace(" ","").replace("-",""))][:15]
    if not nums: await update.message.reply_text("❌ No valid!\n/cancel"); return AADHAAR_BATCH
    await _do_batch(update,context,aadhaar_api,nums,"🪪",aadhaar_use,aadhaar_check,lambda t,d:fmt_special("Aadhaar","🪪","Aadhaar",t,d)); return ConversationHandler.END

# ================== VEHICLE RC ==================
async def veh_ss(u,c): return await _single_start(u,c,vehicle_check,"Vehicle","🚗 Vehicle number:\n✅ `MH01AB1234`\n/cancel",VEHICLE_SINGLE)
async def veh_sp(update,context):
    rc=update.message.text.strip().upper().replace(" ","").replace("-","")
    if len(rc)<4: await update.message.reply_text("❌ Valid RC!\n/cancel"); return VEHICLE_SINGLE
    await _do_single(update,context,vehicle_api,rc,rc,"🚗",vehicle_use,vehicle_check,lambda t,d:fmt_special("Vehicle RC Lookup","🚗","RC Number",t,d)); return ConversationHandler.END

async def veh_bs(u,c): return await _batch_start(u,c,vehicle_check,"📦 RC numbers comma:\n/cancel",VEHICLE_BATCH)
async def veh_bp(update,context):
    rcs=[r.strip().upper().replace(" ","").replace("-","") for r in update.message.text.split(",") if len(r.strip())>=4][:15]
    if not rcs: await update.message.reply_text("❌ No valid!\n/cancel"); return VEHICLE_BATCH
    await _do_batch(update,context,vehicle_api,rcs,"🚗",vehicle_use,vehicle_check,lambda t,d:fmt_special("Vehicle","🚗","RC",t,d)); return ConversationHandler.END

# ================== IFSC ==================
async def ifsc_ss(u,c): return await _single_start(u,c,ifsc_check,"IFSC","🏦 IFSC Code:\n✅ `SBIN0001234`\n/cancel",IFSC_SINGLE)
async def ifsc_sp(update,context):
    code=update.message.text.strip().upper().replace(" ","")
    if not valid_ifsc(code): await update.message.reply_text("❌ Valid IFSC! (11 chars, 4 letters + 0 + 6 digits)\n/cancel"); return IFSC_SINGLE
    await _do_single(update,context,ifsc_api,code,code,"🏦",ifsc_use,ifsc_check,lambda t,d:fmt_special("IFSC Lookup","🏦","IFSC Code",t,d)); return ConversationHandler.END

async def ifsc_bs(u,c): return await _batch_start(u,c,ifsc_check,"📦 IFSC codes comma:\n/cancel",IFSC_BATCH)
async def ifsc_bp(update,context):
    codes=[c.strip().upper().replace(" ","") for c in update.message.text.split(",") if valid_ifsc(c.strip().upper().replace(" ",""))][:15]
    if not codes: await update.message.reply_text("❌ No valid!\n/cancel"); return IFSC_BATCH
    await _do_batch(update,context,ifsc_api,codes,"🏦",ifsc_use,ifsc_check,lambda t,d:fmt_special("IFSC","🏦","IFSC",t,d)); return ConversationHandler.END

# ================== CANCEL ==================
async def cancel(u,c): c.user_data.clear(); await u.message.reply_text("❌ Cancelled.",reply_markup=main_kb(u.effective_user.id)); return ConversationHandler.END

# ================== ADMIN ==================
async def admin_panel(update,context):
    if not is_admin(update.effective_user.id):
        if update.message: await update.message.reply_text("❌ Admin only!")
        return ConversationHandler.END
    users=load_users(); t=len(users); p=sum(1 for v in users.values() if v.get("is_premium"))
    txt=f"━"*30+f"\n🛠️ *Admin*\n"+"━"*30+f"\n\n🛡️{len(ADMIN_IDS)} 👥{t} 💎{p} 🆓{t-p}\n\nAction:"
    if update.callback_query: await safe_edit(update.callback_query,txt,admin_kb())
    else: await update.message.reply_text(txt,reply_markup=admin_kb(),parse_mode="Markdown")
    return ConversationHandler.END

async def admin_back(u,c): await admin_panel(u,c)

async def adm_add_s(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer(); await safe_edit(q,"➕ User ID:\n/cancel"); return ADMIN_ADD_ID

async def adm_add_id(u,c):
    uid=u.message.text.strip()
    if not uid.isdigit(): await u.message.reply_text("❌ Invalid!\n/cancel"); return ADMIN_ADD_ID
    c.user_data["admin_uid"]=uid
    await u.message.reply_text(f"✅ `{uid}`\nPlan:",reply_markup=plan_kb("plan"),parse_mode="Markdown"); return ADMIN_ADD_PLAN

async def adm_add_plan(u,c):
    q=u.callback_query; await q.answer()
    if q.data=="admin_back": await admin_panel(u,c); return ConversationHandler.END
    pm={"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk=pm.get(q.data,"7days"); uid=c.user_data.get("admin_uid"); plan=PLANS.get(pk)
    exp=upgrade(int(uid),pk); dl="∞" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(q,f"✅ *Added!*\n🆔`{uid}`\n📦{plan['name']}\n📅{exp}\nLimit:{dl}",admin_kb()); return ConversationHandler.END

async def adm_rem_s(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer(); await safe_edit(q,"❌ User ID:\n/cancel"); return ADMIN_REM_ID

async def adm_rem_p(u,c):
    uid=u.message.text.strip(); delete_user(uid)
    await u.message.reply_text(f"✅ `{uid}` removed!",reply_markup=admin_kb(),parse_mode="Markdown"); return ConversationHandler.END

async def adm_sp_s(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer(); await safe_edit(q,"📅 User ID:\n/cancel"); return ADMIN_EXP_ID

async def adm_sp_id(u,c):
    uid=u.message.text.strip(); c.user_data["admin_uid"]=uid
    await u.message.reply_text(f"`{uid}` Plan:",reply_markup=plan_kb("plan"),parse_mode="Markdown"); return ADMIN_EXP_PLAN

async def adm_sp_set(u,c):
    q=u.callback_query; await q.answer()
    if q.data=="admin_back": await admin_panel(u,c); return ConversationHandler.END
    pm={"plan_7days":"7days","plan_30days":"30days","plan_6months":"6months","plan_12months":"12months"}
    pk=pm.get(q.data,"7days"); uid=c.user_data.get("admin_uid"); plan=PLANS.get(pk)
    exp=upgrade(int(uid),pk); dl="∞" if plan["unlimited"] else f"{plan['daily_limit']}/day"
    await safe_edit(q,f"✅ *Updated!*\n🆔`{uid}`\n📦{plan['name']}\n📅{exp}\nLimit:{dl}",admin_kb()); return ConversationHandler.END

async def adm_list(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer(); users=load_users()
    if not users: await safe_edit(q,"📋 No users!",admin_kb()); return
    txt=f"📋 *Users({len(users)})*\n\n"
    for uid,info in users.items():
        plan=get_plan(info); ts=info.get("total_searches",0)
        if int(uid) in ADMIN_IDS: st="🛡️Admin"
        elif info.get("is_premium") and info.get("expiry"):
            try:
                ed=date.fromisoformat(info["expiry"])
                st=f"💎{plan['name']}{(ed-date.today()).days}d" if date.today()<=ed else "🔴Exp"
            except: st="⚪"
        else: st=f"🆓"
        txt+=f"`{uid}`|{st}|🔍{ts}\n"
    await safe_edit(q,txt[:4000],admin_kb())

async def adm_stats(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer(); users=load_users(); ts=sum(v.get("total_searches",0) for v in users.values())
    act=sum(1 for u2,v in users.items() if v.get("is_premium") and int(u2) not in ADMIN_IDS)
    await safe_edit(q,f"📊 *Stats*\n👥{len(users)} 🔍{ts} 💎Active:{act}\n📅{date.today()}",admin_kb())

async def adm_monitor(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return
    await q.answer()
    users=load_users(); free=[v for u2,v in users.items() if not v.get("is_premium") and int(u2) not in ADMIN_IDS]
    await safe_edit(q,f"🆓 *Monitor*\n👥Free: {len(free)}\n\nFilter 👇",monitor_kb())

async def mon_exhausted(u,c):
    q=u.callback_query; await q.answer(); users=load_users(); txt="🔴 *Exhausted*\n\n"; cnt=0
    all_keys=[("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE)]
    for uid,info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"): continue
        if all(max(0,mx-info.get(k,0))<=0 for k,mx in all_keys):
            txt+=f"🔴`{uid}`\n"; cnt+=1
    txt+=f"\n💡{cnt} buyers!"
    await safe_edit(q,txt[:4000],monitor_kb())

async def mon_active(u,c):
    q=u.callback_query; await q.answer(); users=load_users(); txt="🟢 *Active*\n\n"; cnt=0
    all_keys=[("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE)]
    for uid,info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"): continue
        if any(max(0,mx-info.get(k,0))>0 for k,mx in all_keys):
            txt+=f"🟢`{uid}`\n"; cnt+=1
    txt+=f"\nActive:{cnt}"
    await safe_edit(q,txt[:4000],monitor_kb())

async def mon_summary(u,c):
    q=u.callback_query; await q.answer(); users=load_users(); t=0; ex=0
    all_keys=[("phone_free_used",PHONE_FREE),("email_free_used",EMAIL_FREE),("upi_free_used",UPI_FREE),("aadhaar_free_used",AADHAAR_FREE),("vehicle_free_used",VEHICLE_FREE),("ifsc_free_used",IFSC_FREE)]
    for uid,info in users.items():
        if int(uid) in ADMIN_IDS or info.get("is_premium"): continue
        t+=1
        if all(max(0,mx-info.get(k,0))<=0 for k,mx in all_keys): ex+=1
    await safe_edit(q,f"📊 Free:{t} Exhausted:{ex}\n📅{date.today()}",monitor_kb())

# ================== BROADCAST ==================
async def bc_start(u,c):
    q=u.callback_query
    if not is_admin(q.from_user.id): return ConversationHandler.END
    await q.answer(); await safe_edit(q,f"📢 *Broadcast*\n👥{len(load_users())}\nMessage:\n/cancel"); return ADMIN_BROADCAST_MSG

async def bc_msg(u,c):
    m=u.message.text.strip()
    if not m: await u.message.reply_text("❌ Empty!\n/cancel"); return ADMIN_BROADCAST_MSG
    c.user_data["bc"]=m
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("✅Send",callback_data="broadcast_confirm"),InlineKeyboardButton("❌Cancel",callback_data="broadcast_cancel")]])
    await u.message.reply_text(f"📢 *Preview:*\n\n{m}\n\n👥{len(load_users())}\nSure?",reply_markup=kb,parse_mode="Markdown"); return ADMIN_BROADCAST_CONFIRM

async def bc_confirm(u,c):
    q=u.callback_query; await q.answer()
    if q.data=="broadcast_cancel":
        await safe_edit(q,"❌ Cancelled!",admin_kb()); c.user_data.pop("bc",None); return ConversationHandler.END
    msg=c.user_data.get("bc",""); users=load_users(); total=len(users)
    bt=f"📢 *Announcement*\n{'━'*25}\n\n{msg}\n\n{'━'*25}\n💬{OWNER_CONTACT}"
    sm=await q.message.reply_text(f"🚀 {total}...",parse_mode="Markdown")
    s,f2,b,ct=0,0,0,0
    for uid in users:
        ct+=1
        try: await c.bot.send_message(chat_id=int(uid),text=bt,parse_mode="Markdown"); s+=1
        except Exception as e:
            if any(w in str(e).lower() for w in ["blocked","forbidden","not found"]): b+=1
            else: f2+=1
        if ct%10==0 or ct==total:
            try: await sm.edit_text(f"🚀{ct}/{total} ✅{s}🚫{b}❌{f2}",parse_mode="Markdown")
            except: pass
    await sm.edit_text(f"✅ Done! 👥{total} ✅{s} 🚫{b} ❌{f2}",reply_markup=admin_kb(),parse_mode="Markdown")
    c.user_data.pop("bc",None); return ConversationHandler.END

# ================== CUSTOM PLAN ==================
async def custom_s(u,c):
    q=u.callback_query; await q.answer()
    await safe_edit(q,"⚙️ Days?\n/cancel"); return ADMIN_CUSTOM_DAYS

async def custom_days(u,c):
    t=u.message.text.strip()
    if not t.isdigit() or int(t)<=0: await u.message.reply_text("❌ Valid!\n/cancel"); return ADMIN_CUSTOM_DAYS
    c.user_data["cd"]=int(t)
    await u.message.reply_text(f"📅{t}D\nDaily limit? (0=∞)\n/cancel",parse_mode="Markdown"); return ADMIN_CUSTOM_LIMIT

async def custom_limit(u,c):
    t=u.message.text.strip()
    if not t.isdigit(): await u.message.reply_text("❌ Valid!\n/cancel"); return ADMIN_CUSTOM_LIMIT
    lim=int(t); unl=lim==0; days=c.user_data.get("cd"); uid=c.user_data.get("admin_uid")
    exp=upgrade_custom(int(uid),days,lim,unl)
    ls="∞" if unl else f"{lim}/day"
    await u.message.reply_text(f"⚙️ *Custom Set!*\n🆔`{uid}`\n📅{days}D|{exp}\nLimit:{ls}",reply_markup=admin_kb(),parse_mode="Markdown")
    c.user_data.pop("cd",None); c.user_data.pop("admin_uid",None); return ConversationHandler.END

async def main_menu_cb(u,c): await start(u,c); return ConversationHandler.END

# ================== MAIN ==================
def main():
    threading.Thread(target=start_webserver,daemon=True).start(); print("🌐 Flask!")
    req=HTTPXRequest(connect_timeout=60,read_timeout=60,write_timeout=60,pool_timeout=60)
    gur=HTTPXRequest(connect_timeout=60,read_timeout=60,write_timeout=60,pool_timeout=60)
    app=ApplicationBuilder().token(BOT_TOKEN).request(req).get_updates_request(gur).build()

    C=ConversationHandler; CQ=CallbackQueryHandler; MH=MessageHandler; CMD=CommandHandler
    F=filters.TEXT&~filters.COMMAND

    convs=[
        C(entry_points=[CQ(phone_single_s2,pattern="^phone_single$")],states={PHONE_COUNTRY_SINGLE:[CQ(cs_single,pattern="^country_(india|other)_single$")],PHONE_SINGLE_INDIA:[MH(F,psi)],PHONE_SINGLE_OTHER:[MH(F,pso)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(phone_batch_s2,pattern="^phone_batch$")],states={PHONE_COUNTRY_BATCH:[CQ(cs_batch,pattern="^country_(india|other)_batch$")],PHONE_BATCH_INDIA:[MH(F,pbi)],PHONE_BATCH_OTHER:[MH(F,pbo)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(email_ss,pattern="^email_single$")],states={EMAIL_SINGLE:[MH(F,email_sp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(email_bs,pattern="^email_batch$")],states={EMAIL_BATCH:[MH(F,email_bp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(upi_ss,pattern="^upi_single$")],states={UPI_SINGLE:[MH(F,upi_sp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(upi_bs,pattern="^upi_batch$")],states={UPI_BATCH:[MH(F,upi_bp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(aadh_ss,pattern="^aadhaar_single$")],states={AADHAAR_SINGLE:[MH(F,aadh_sp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(aadh_bs,pattern="^aadhaar_batch$")],states={AADHAAR_BATCH:[MH(F,aadh_bp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(veh_ss,pattern="^vehicle_single$")],states={VEHICLE_SINGLE:[MH(F,veh_sp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(veh_bs,pattern="^vehicle_batch$")],states={VEHICLE_BATCH:[MH(F,veh_bp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(ifsc_ss,pattern="^ifsc_single$")],states={IFSC_SINGLE:[MH(F,ifsc_sp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(ifsc_bs,pattern="^ifsc_batch$")],states={IFSC_BATCH:[MH(F,ifsc_bp)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_add_s,pattern="^admin_add$")],states={ADMIN_ADD_ID:[MH(F,adm_add_id)],ADMIN_ADD_PLAN:[CQ(custom_s,pattern="^plan_custom$"),CQ(adm_add_plan,pattern="^plan_")],ADMIN_CUSTOM_DAYS:[MH(F,custom_days)],ADMIN_CUSTOM_LIMIT:[MH(F,custom_limit)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_rem_s,pattern="^admin_remove$")],states={ADMIN_REM_ID:[MH(F,adm_rem_p)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(adm_sp_s,pattern="^admin_setplan$")],states={ADMIN_EXP_ID:[MH(F,adm_sp_id)],ADMIN_EXP_PLAN:[CQ(custom_s,pattern="^plan_custom$"),CQ(adm_sp_set,pattern="^plan_")],ADMIN_CUSTOM_DAYS:[MH(F,custom_days)],ADMIN_CUSTOM_LIMIT:[MH(F,custom_limit)]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
        C(entry_points=[CQ(bc_start,pattern="^admin_broadcast$")],states={ADMIN_BROADCAST_MSG:[MH(F,bc_msg)],ADMIN_BROADCAST_CONFIRM:[CQ(bc_confirm,pattern="^broadcast_(confirm|cancel)$")]},fallbacks=[CMD("cancel",cancel)],per_message=False,allow_reentry=True),
    ]
    for cv in convs: app.add_handler(cv)

    app.add_handler(CMD("start",start)); app.add_handler(CMD("admin",admin_panel))
    for p,f2 in [("mode_phone",mode_phone),("mode_email",mode_email),("mode_upi",mode_upi),("mode_aadhaar",mode_aadhaar),("mode_vehicle",mode_vehicle),("mode_ifsc",mode_ifsc),("profile",profile),("status",status_check),("help",help_menu),("buy",buy),("admin_list",adm_list),("admin_stats",adm_stats),("admin_back",admin_back),("admin_free_monitor",adm_monitor),("monitor_exhausted",mon_exhausted),("monitor_active",mon_active),("monitor_summary",mon_summary),("main_menu",main_menu_cb),("verify_join",verify_join)]:
        app.add_handler(CQ(f2,pattern=f"^{p}$"))

    print("🤖 Bot Running! 📱📧💳🪪🚗🏦")
    print(f"🛡️ Admins:{ADMIN_IDS} 📢Force:{FORCE_JOIN_CHANNEL}")
    print("🔒 API URLs Hidden in Errors!")
    app.run_polling(drop_pending_updates=True,allowed_updates=["message","callback_query"])

if __name__=="__main__": main()

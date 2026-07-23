import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn

app = FastAPI()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量读取密钥
SECRET = os.environ.get("RELAY_SECRET", "YuXiaoChi_0722")

# 内存存储（简化版，不用数据库）
sessions = {}
messages = {}
next_id = 1

@app.get("/healthz")
async def healthz():
    return {"ok": True, "plugin_subs": 0, "app_subs": 0}

@app.get("/app/sessions")
async def get_sessions(secret: str = None):
    if secret != SECRET:
        return JSONResponse(status_code=401, content={"detail": "unauthorized"})
    return {"sessions": list(sessions.values()), "active_session": None}

@app.post("/app/sessions")
async def create_session(secret: str = None):
    if secret != SECRET:
        return JSONResponse(status_code=401, content={"detail": "unauthorized"})
    sid = str(uuid.uuid4())
    session = {"id": sid, "title": "新对话", "created_at": datetime.now().isoformat()}
    sessions[sid] = session
    messages[sid] = []
    return {"session": session, "sessions": list(sessions.values())}

@app.get("/app/history")
async def get_history(session_id: str = None, since: int = 0, limit: int = 50, secret: str = None):
    if secret != SECRET:
        return JSONResponse(status_code=401, content={"detail": "unauthorized"})
    sid = session_id or list(sessions.keys())[0] if sessions else None
    if not sid or sid not in messages:
        return {"messages": []}
    msgs = messages.get(sid, [])
    return {"messages": msgs[-limit:]}

@app.post("/app/send")
async def send_message(request: Request):
    try:
        body = await request.json()
        secret = request.headers.get("Authorization", "").replace("Bearer ", "")
        if secret != SECRET:
            return JSONResponse(status_code=401, content={"detail": "unauthorized"})
        text = body.get("text", "")
        session_id = body.get("api_session") or list(sessions.keys())[0] if sessions else None
        if not session_id:
            return JSONResponse(status_code=400, content={"detail": "no session"})
        global next_id
        msg_id = str(next_id)
        next_id += 1
        msg = {
            "id": msg_id,
            "ts": datetime.now().isoformat(),
            "from": "human",
            "kind": "user",
            "text": text,
            "meta": {}
        }
        if session_id not in messages:
            messages[session_id] = []
        messages[session_id].append(msg)
        return {"id": msg_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

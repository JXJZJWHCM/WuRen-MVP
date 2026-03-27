from fastapi import FastAPI, Request, Query, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import asyncio
import os
import json
import re
import ipaddress
import shutil
import time
import subprocess
from typing import Optional, Any, Dict, List
from urllib.parse import urlparse, quote
from dotenv import load_dotenv
from src.tools.manager import ToolManager
from src.tools.executor import ToolExecutor
from src.agent.core import PentestAgent
from sse_starlette.sse import EventSourceResponse
from src.utils.network import list_network_interfaces, get_ip_address, get_default_interface_name
from src.utils.ocr import ocr_image
from src.utils.task_store import TaskStore
from src.utils.audit_log_store import AuditLogStore
from src.utils.vuln_store import VulnStore
from src.utils.report_renderer import render_report_html

load_dotenv()

APP_VERSION = "1.0"

app = FastAPI(title="雾刃渗透测试系统1.0", version=APP_VERSION)

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "tools")
WEB_PATH = os.path.join(BASE_DIR, "web")

# Init Core
tool_manager = ToolManager(CONFIG_PATH)
executor = ToolExecutor(tool_manager, base_dir=BASE_DIR)
task_store = TaskStore(BASE_DIR)
audit_store = AuditLogStore(BASE_DIR)
vuln_store = VulnStore(BASE_DIR)

_SAFE_ENV_VALUE_RE = re.compile(r"^[^\r\n]*$")
_SAFE_IFACE_RE = re.compile(r"^[a-zA-Z0-9_.:-]+$")
_SAFE_MODEL_RE = re.compile(r"^[a-zA-Z0-9_.:-]+$")
_SAFE_TASK_ID_RE = re.compile(r"^[a-zA-Z0-9_.:-]{1,80}$")

_AGENT_ALLOWED_TOOLS_CACHE: Optional[set] = None
_EXPLOITDB_STATS_CACHE: Dict[str, Any] = {"ts": 0.0, "data": None}

def _audit_max_rows() -> int:
    try:
        v = int(os.getenv("AUDIT_LOG_MAX_ROWS", "10000") or "10000")
    except Exception:
        v = 10000
    if v < 1:
        v = 1
    if v > 100000:
        v = 100000
    return v

def _client_ip(request: Request) -> str:
    xff = (request.headers.get("x-forwarded-for") or "").strip()
    if xff:
        return xff.split(",")[0].strip()
    try:
        if request.client and request.client.host:
            return str(request.client.host)
    except Exception:
        pass
    return ""

def _sanitize_task_id(task_id: str) -> Optional[str]:
    v = (task_id or "").strip()
    if not v:
        return None
    if ".." in v or "/" in v or "\\" in v:
        return None
    if not _SAFE_TASK_ID_RE.match(v):
        return None
    return v

def _safe_join_under_allow_empty(base_dir: str, rel_path: str) -> Optional[str]:
    base_abs = os.path.abspath(base_dir)
    rel_path = (rel_path or "").replace("\\", "/").lstrip("/")
    if not rel_path:
        return base_abs
    if ".." in rel_path:
        return None
    candidate = os.path.abspath(os.path.join(base_abs, rel_path))
    if not (candidate == base_abs or candidate.startswith(base_abs + os.sep)):
        return None
    return candidate

def _loot_task_root(task_id: str) -> Optional[str]:
    safe_id = _sanitize_task_id(task_id)
    if not safe_id:
        return None
    return os.path.abspath(os.path.join(DATA_DIR, "loot", safe_id))

@app.middleware("http")
async def _audit_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    try:
        path = request.url.path or ""
        if not path.startswith("/api/"):
            return response
        if getattr(request.state, "audit_skip", False):
            return response
        if path in {"/api/system/metrics", "/api/health"}:
            return response
        if path.startswith("/api/audit/") and path not in {"/api/audit/clear", "/api/audit/ui"}:
            return response
        if path == "/api/scan/stream":
            return response

        dur_ms = int(max(0.0, (time.time() - start)) * 1000.0)
        status_code = None
        try:
            status_code = int(getattr(response, "status_code", None) or 0) or None
        except Exception:
            status_code = None

        action = getattr(request.state, "audit_action", "") or f"{request.method} {path}"
        detail = getattr(request.state, "audit_detail", None)
        query = request.url.query or ""
        audit_store.append(
            actor_ip=_client_ip(request),
            user_agent=request.headers.get("user-agent", ""),
            method=request.method,
            path=path,
            query=query,
            status_code=status_code,
            duration_ms=dur_ms,
            action=action,
            detail=detail if isinstance(detail, dict) else {},
            max_rows=_audit_max_rows(),
        )
    except Exception:
        pass
    return response

def _compute_exploitdb_total() -> Dict[str, Any]:
    candidates = [
        ("/usr/share/exploitdb/files_exploits.csv", "files_exploits.csv"),
        ("/usr/share/exploitdb/files_shellcodes.csv", "files_shellcodes.csv"),
        ("/opt/exploitdb/files_exploits.csv", "files_exploits.csv"),
        ("/opt/exploitdb/files_shellcodes.csv", "files_shellcodes.csv"),
    ]

    total = 0
    sources: List[str] = []
    for path, label in candidates:
        try:
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = 0
                for _ in f:
                    lines += 1
            if lines > 0:
                lines -= 1
            total += max(0, lines)
            sources.append(label)
        except Exception:
            continue

    if sources:
        return {
            "exploitdb_available": True,
            "exploitdb_total": total,
            "sources": sources,
        }

    return {
        "exploitdb_available": False,
        "exploitdb_total": None,
        "sources": [],
    }

def _get_agent_allowed_tools() -> set:
    global _AGENT_ALLOWED_TOOLS_CACHE
    if _AGENT_ALLOWED_TOOLS_CACHE is not None:
        return _AGENT_ALLOWED_TOOLS_CACHE
    allowed = set()
    try:
        for t in tool_manager.list_tools():
            if t.get("enabled", True) is False:
                continue
            name = str(t.get("name") or "").strip()
            if name:
                allowed.add(name)
    except Exception:
        allowed = set()
    _AGENT_ALLOWED_TOOLS_CACHE = allowed
    return allowed

def _sanitize_env_value(value: str) -> str:
    if value is None:
        return ""
    value = str(value)
    value = value.replace("\r", "").replace("\n", "")
    return value

def _validate_env_value(value: str) -> bool:
    return bool(_SAFE_ENV_VALUE_RE.match(value or ""))

def _validate_iface_name(value: str) -> bool:
    return bool(_SAFE_IFACE_RE.match(value or ""))

def _validate_lhost(value: str) -> bool:
    if not value:
        return True
    v = value.strip()
    if any(c.isspace() for c in v):
        return False
    try:
        ipaddress.ip_address(v)
        return True
    except Exception:
        return bool(re.match(r"^[a-zA-Z0-9.-]+$", v))

def _validate_model_name(value: str) -> bool:
    return bool(_SAFE_MODEL_RE.match(value or ""))

def _validate_proxy_url(value: str) -> bool:
    v = (value or "").strip()
    if not v:
        return True
    try:
        parsed = urlparse(v)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False

def _validate_http_url(value: str) -> bool:
    v = (value or "").strip()
    if not v:
        return True
    try:
        parsed = urlparse(v)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False

class VulnRequest(BaseModel):
    task_id: str = ""
    target: str = ""
    title: str
    severity: str
    cvss: float | None = None
    status: str = "open"
    details: dict = Field(default_factory=dict)

class TaskCreateRequest(BaseModel):
    task_id: str
    goal: str = ""

class TaskStartRequest(BaseModel):
    goal: str = ""

def _build_task_goal(target: str, goal: str) -> str:
    return f"目标IP: {target}\n任务: {goal}\n请直接开始对该IP进行渗透测试，不需要询问用户。"

def _append_task_event(task_id: str, event: Dict[str, Any]):
    try:
        if task_id in active_tasks:
            active_tasks[task_id]["history"].append(event)
            for q in list(active_tasks[task_id]["listeners"]):
                try:
                    asyncio.create_task(q.put(event))
                except Exception:
                    pass
    except Exception:
        pass
    try:
        task_store.append_event(task_id, event)
    except Exception:
        pass

def _ensure_task_started(target: str, goal: str):
    task_id = _sanitize_task_id(target)
    if not task_id:
        raise ValueError("invalid_task_id")
    if task_id in active_tasks:
        return task_id

    agent = PentestAgent(tool_manager, executor, base_dir=BASE_DIR)
    agent.task_id = task_id
    agent.vuln_store = vuln_store
    pause_event = asyncio.Event()
    pause_event.set()
    agent.pause_event = pause_event
    full_goal = _build_task_goal(task_id, goal)

    task_store.upsert_task(task_id, goal=goal, status="running")
    active_tasks[task_id] = {
        "agent": agent,
        "listeners": [],
        "status": "running",
        "pause_event": pause_event,
        "history": [],
        "bg_task": None,
        "goal": goal,
    }

    async def run_agent_bg():
        try:
            async for event in agent.run_stream(full_goal):
                task_info = active_tasks.get(task_id)
                if not task_info:
                    break
                task_info["history"].append(event)
                try:
                    task_store.append_event(task_id, event)
                except Exception:
                    pass
                for q in list(task_info["listeners"]):
                    await q.put(event)
        except asyncio.CancelledError:
            executor.cancel(task_id)
            cancel_event = {"type": "log", "content": "任务已取消"}
            task_info = active_tasks.get(task_id)
            if task_info:
                task_info["history"].append(cancel_event)
            try:
                task_store.append_event(task_id, cancel_event)
            except Exception:
                pass
            if task_info:
                for q in list(task_info["listeners"]):
                    await q.put(cancel_event)
        except Exception as e:
            error_event = {"type": "error", "content": f"Agent crashed: {str(e)}"}
            task_info = active_tasks.get(task_id)
            if task_info:
                task_info["history"].append(error_event)
            try:
                task_store.append_event(task_id, error_event)
            except Exception:
                pass
            if task_info:
                for q in list(task_info["listeners"]):
                    await q.put(error_event)
        finally:
            executor.cancel(task_id)
            task_info = active_tasks.get(task_id)
            if task_info:
                if task_info.get("status") not in {"paused", "cancelled", "error"}:
                    task_info["status"] = "finished"
            try:
                task_store.mark_finished(task_id, status=active_tasks.get(task_id, {}).get("status", "finished"))
            except Exception:
                pass
            if task_info:
                for q in list(task_info["listeners"]):
                    await q.put(None)

    bg_task = asyncio.create_task(run_agent_bg())
    active_tasks[task_id]["bg_task"] = bg_task
    return task_id

# Global Task Registry
# task_id -> {"agent": agent_instance, "queue": asyncio.Queue(), "status": "running"|"finished"}
active_tasks = {}

@app.get("/api/tasks")
def list_tasks(limit: int = 50):
    return {"tasks": task_store.list_tasks(limit=limit)}

@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    task_id = _sanitize_task_id(task_id)
    if not task_id:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    stored = task_store.get_task(task_id) or {}
    active = active_tasks.get(task_id) or {}
    out = dict(stored) if stored else {"task_id": task_id}
    if active:
        out["status"] = active.get("status") or out.get("status")
        out["history_len"] = len(active.get("history") or [])
    else:
        out["history_len"] = len(task_store.load_events(task_id, limit=5000))
    return out

@app.post("/api/tasks")
def create_task(request: Request, req: TaskCreateRequest):
    raw_task_id = (req.task_id or "").strip()
    if not raw_task_id:
        return JSONResponse(status_code=400, content={"error": "missing_task_id"})
    task_id = _sanitize_task_id(raw_task_id)
    if not task_id:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    goal = (req.goal or "").strip() or "对该目标进行全面的渗透测试"
    existing = task_store.get_task(task_id)
    if existing and existing.get("status") in {"running", "paused"}:
        request.state.audit_action = "task_create"
        request.state.audit_detail = {"task_id": task_id, "exists": True, "status": existing.get("status")}
        return {"ok": True, "task_id": task_id, "status": existing.get("status"), "exists": True}
    task_store.upsert_task(task_id, goal=goal, status="created")
    request.state.audit_action = "task_create"
    request.state.audit_detail = {"task_id": task_id, "exists": False}
    return {"ok": True, "task_id": task_id, "status": "created"}

@app.post("/api/tasks/{task_id}/start")
async def start_task(request: Request, task_id: str, req: TaskStartRequest):
    provider = os.getenv("AI_PROVIDER", "deepseek")
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            return JSONResponse(status_code=400, content={"error": "未配置 OPENAI_API_KEY"})
    else:
        if not os.getenv("DEEPSEEK_API_KEY"):
            return JSONResponse(status_code=400, content={"error": "未配置 DEEPSEEK_API_KEY"})

    task_id = _sanitize_task_id(task_id)
    if not task_id:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    goal = (req.goal or "").strip()
    stored = task_store.get_task(task_id)
    if not goal:
        goal = (stored or {}).get("goal") or "对该目标进行全面的渗透测试"

    if task_id in active_tasks:
        info = active_tasks[task_id]
        if info.get("status") == "paused":
            pe = info.get("pause_event")
            if pe:
                pe.set()
            info["status"] = "running"
            task_store.upsert_task(task_id, goal=goal, status="running")
            _append_task_event(task_id, {"type": "log", "content": "[系统] 任务已继续"})
        request.state.audit_action = "task_start"
        request.state.audit_detail = {"task_id": task_id, "goal": goal, "status": active_tasks[task_id].get("status", "running")}
        return {"ok": True, "task_id": task_id, "status": active_tasks[task_id].get("status", "running"), "stream_url": f"/api/scan/stream?target={quote(task_id)}&goal={quote(goal)}"}

    task_id = _ensure_task_started(task_id, goal)
    _append_task_event(task_id, {"type": "log", "content": "[系统] 任务已开始"})
    request.state.audit_action = "task_start"
    request.state.audit_detail = {"task_id": task_id, "goal": goal, "status": "running"}
    return {"ok": True, "task_id": task_id, "status": "running", "stream_url": f"/api/scan/stream?target={quote(task_id)}&goal={quote(goal)}"}

@app.post("/api/tasks/{task_id}/pause")
def pause_task(request: Request, task_id: str):
    task_id = _sanitize_task_id(task_id)
    if not task_id:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    info = active_tasks.get(task_id)
    if not info:
        stored = task_store.get_task(task_id)
        if not stored:
            return JSONResponse(status_code=404, content={"error": "not_found"})
        task_store.upsert_task(task_id, goal=stored.get("goal") or "", status="paused")
        request.state.audit_action = "task_pause"
        request.state.audit_detail = {"task_id": task_id, "status": "paused", "active": False}
        return {"ok": True, "task_id": task_id, "status": "paused"}
    pe = info.get("pause_event")
    if pe:
        pe.clear()
    info["status"] = "paused"
    task_store.upsert_task(task_id, goal=info.get("goal") or "", status="paused")
    _append_task_event(task_id, {"type": "log", "content": "[系统] 任务已暂停"})
    request.state.audit_action = "task_pause"
    request.state.audit_detail = {"task_id": task_id, "status": "paused", "active": True}
    return {"ok": True, "task_id": task_id, "status": "paused"}

@app.post("/api/tasks/{task_id}/resume")
def resume_task(request: Request, task_id: str):
    task_id = _sanitize_task_id(task_id)
    if not task_id:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    info = active_tasks.get(task_id)
    if not info:
        stored = task_store.get_task(task_id)
        if not stored:
            return JSONResponse(status_code=404, content={"error": "not_found"})
        if stored.get("status") == "paused":
            task_store.upsert_task(task_id, goal=stored.get("goal") or "", status="running")
        request.state.audit_action = "task_resume"
        request.state.audit_detail = {"task_id": task_id, "status": "running", "active": False}
        return {"ok": True, "task_id": task_id, "status": "running"}
    pe = info.get("pause_event")
    if pe:
        pe.set()
    info["status"] = "running"
    task_store.upsert_task(task_id, goal=info.get("goal") or "", status="running")
    _append_task_event(task_id, {"type": "log", "content": "[系统] 任务已继续"})
    request.state.audit_action = "task_resume"
    request.state.audit_detail = {"task_id": task_id, "status": "running", "active": True}
    return {"ok": True, "task_id": task_id, "status": "running"}

@app.post("/api/tasks/{task_id}/stop")
async def stop_task(request: Request, task_id: str):
    task_id = _sanitize_task_id(task_id)
    if not task_id:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    task = active_tasks.get(task_id)
    if not task:
        stored = task_store.get_task(task_id)
        if stored:
            task_store.mark_finished(task_id, status="finished")
            try:
                executor.msf_cli_stop(task_id)
            except Exception:
                pass
            request.state.audit_action = "task_stop"
            request.state.audit_detail = {"task_id": task_id, "status": stored.get("status", "finished"), "active": False}
            return {"ok": True, "task_id": task_id, "status": stored.get("status", "finished")}
        return JSONResponse(status_code=404, content={"error": "not_found"})
    pe = task.get("pause_event")
    if pe:
        pe.set()
    task["status"] = "cancelled"
    _append_task_event(task_id, {"type": "log", "content": "[系统] 任务已停止"})
    executor.cancel(task_id)
    try:
        executor.msf_cli_stop(task_id)
    except Exception:
        pass
    bg_task = task.get("bg_task")
    if bg_task and not bg_task.done():
        bg_task.cancel()
    task_store.mark_finished(task_id, status="cancelled")
    request.state.audit_action = "task_stop"
    request.state.audit_detail = {"task_id": task_id, "status": "cancelled", "active": True}
    return {"ok": True, "task_id": task_id, "status": "cancelled"}

@app.delete("/api/tasks/{task_id}")
async def delete_task(request: Request, task_id: str):
    task_id = _sanitize_task_id(task_id)
    if not task_id:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    if task_id in active_tasks:
        await stop_task(request, task_id)
        try:
            active_tasks.pop(task_id, None)
        except Exception:
            pass
    ok = task_store.delete_task(task_id, delete_events=True)
    if not ok:
        return JSONResponse(status_code=404, content={"error": "not_found"})

    deleted_vulns = 0
    try:
        deleted_vulns = int(vuln_store.delete_by_task(task_id) or 0)
    except Exception:
        deleted_vulns = 0

    deleted_paths = []
    try:
        loot_root = os.path.join(BASE_DIR, "data", "loot", task_id)
        if os.path.isdir(loot_root):
            shutil.rmtree(loot_root, ignore_errors=True)
            deleted_paths.append("loot")
    except Exception:
        pass
    try:
        tool_root = os.path.join(BASE_DIR, "data", "temp", "tool_runs", task_id)
        if os.path.isdir(tool_root):
            shutil.rmtree(tool_root, ignore_errors=True)
            deleted_paths.append("tool_runs")
    except Exception:
        pass

    request.state.audit_action = "task_delete"
    request.state.audit_detail = {"task_id": task_id, "deleted_vulns": deleted_vulns, "deleted_paths": deleted_paths}
    return {"ok": True, "task_id": task_id, "deleted_vulns": deleted_vulns, "deleted_paths": deleted_paths}

@app.get("/api/tasks/{task_id}/events")
def get_task_events(task_id: str, limit: int = 2000, since_id: int = 0):
    task_id = _sanitize_task_id(task_id)
    if not task_id:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    rows = task_store.load_events_with_meta(task_id, limit=limit, since_id=since_id)
    return {"task_id": task_id, "events": rows}

class AuditClearRequest(BaseModel):
    reason: str = ""

class AuditUiEventRequest(BaseModel):
    event: str
    detail: Dict[str, Any] = Field(default_factory=dict)

@app.get("/api/audit/stats")
def audit_stats():
    s = audit_store.stats()
    s["max_rows"] = _audit_max_rows()
    s["max_rows_limit"] = 100000
    return s

@app.get("/api/audit/logs")
def audit_logs(
    limit: int = 200,
    offset: int = 0,
    q: str = "",
    method: str = "",
    path: str = "",
    action: str = "",
    kind: str = "",
    status_code: Optional[int] = None,
    since_id: int = 0,
):
    logs = audit_store.list_logs(
        limit=limit,
        offset=offset,
        q=(q or "").strip(),
        method=(method or "").strip(),
        path=(path or "").strip(),
        action=(action or "").strip(),
        kind=(kind or "").strip(),
        status_code=status_code,
        since_id=since_id,
    )
    return {"logs": logs}

@app.post("/api/audit/clear")
def audit_clear(request: Request, req: AuditClearRequest):
    before = audit_store.count()
    audit_store.clear_all()
    request.state.audit_action = "audit_clear"
    request.state.audit_detail = {
        "cleared_rows": before,
        "reason": (req.reason or "").strip(),
    }
    return {"ok": True, "cleared_rows": before}

@app.post("/api/audit/ui")
def audit_ui_event(request: Request, req: AuditUiEventRequest):
    request.state.audit_action = "ui_event"
    request.state.audit_detail = {"event": (req.event or "").strip(), "detail": req.detail if isinstance(req.detail, dict) else {}}
    return {"ok": True}

@app.get("/api/vulns")
def list_vulns(task_id: Optional[str] = None, limit: int = 200):
    if task_id is not None and str(task_id).strip():
        safe_task_id = _sanitize_task_id(task_id)
        if not safe_task_id:
            return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
        task_id = safe_task_id
    else:
        task_id = None
    return {"vulns": vuln_store.list(task_id=task_id, limit=limit)}

@app.get("/api/vulns/{vuln_id}")
def get_vuln(vuln_id: str):
    v = vuln_store.get(vuln_id)
    if not v:
        return JSONResponse(status_code=404, content={"error": "not_found"})
    return v

@app.post("/api/vulns")
def upsert_vuln(request: Request, req: VulnRequest):
    raw_task_id = (req.task_id or "").strip()
    if raw_task_id:
        safe_task_id = _sanitize_task_id(raw_task_id)
        if not safe_task_id:
            return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    else:
        safe_task_id = ""

    severity = (req.severity or "").strip()
    if severity not in {"严重", "高危", "中危", "低危"}:
        return JSONResponse(status_code=400, content={"error": "invalid_severity"})
    status = (req.status or "open").strip()
    if status not in {"open", "fixed", "accepted", "false_positive"}:
        status = "open"
    v = vuln_store.upsert(
        {
            "task_id": safe_task_id,
            "target": (req.target or "").strip(),
            "title": (req.title or "").strip(),
            "severity": severity,
            "cvss": req.cvss,
            "status": status,
            "details": req.details if isinstance(req.details, dict) else {},
        }
    )
    request.state.audit_action = "vuln_upsert"
    request.state.audit_detail = {"task_id": v.get("task_id", ""), "vuln_id": v.get("vuln_id", ""), "severity": v.get("severity", ""), "status": v.get("status", "")}
    return v

@app.delete("/api/vulns/{vuln_id}")
def delete_vuln(request: Request, vuln_id: str):
    ok = vuln_store.delete(vuln_id)
    if not ok:
        return JSONResponse(status_code=404, content={"error": "not_found"})
    request.state.audit_action = "vuln_delete"
    request.state.audit_detail = {"vuln_id": (vuln_id or "").strip()}
    return {"ok": True}


@app.get("/api/loot/list")
def loot_list(task_id: str = Query(""), path: str = Query("")):
    root = _loot_task_root(task_id)
    if not root:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    abs_dir = _safe_join_under_allow_empty(root, path)
    if not abs_dir:
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    if not os.path.exists(abs_dir):
        return {"task_id": task_id, "path": (path or "").replace("\\", "/").lstrip("/"), "entries": []}
    if not os.path.isdir(abs_dir):
        return JSONResponse(status_code=400, content={"error": "not_a_directory"})

    entries: List[Dict[str, Any]] = []
    try:
        for name in os.listdir(abs_dir):
            if not name:
                continue
            p = os.path.join(abs_dir, name)
            try:
                st = os.stat(p)
            except Exception:
                continue
            rel = os.path.relpath(p, root).replace("\\", "/")
            entries.append(
                {
                    "name": name,
                    "path": rel,
                    "is_dir": os.path.isdir(p),
                    "size": int(getattr(st, "st_size", 0) or 0),
                    "mtime": float(getattr(st, "st_mtime", 0.0) or 0.0),
                }
            )
    except Exception:
        entries = []

    entries.sort(key=lambda x: (0 if x.get("is_dir") else 1, str(x.get("name") or "").lower()))
    return {"task_id": task_id, "path": (path or "").replace("\\", "/").lstrip("/"), "entries": entries}

@app.get("/api/loot/read")
def loot_read(task_id: str = Query(""), path: str = Query(""), max_chars: int = Query(20000)):
    root = _loot_task_root(task_id)
    if not root:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    abs_path = _safe_join_under_allow_empty(root, path)
    if not abs_path:
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
        return JSONResponse(status_code=404, content={"error": "not_found"})

    max_chars = max(100, min(int(max_chars), 200000))
    try:
        with open(abs_path, "rb") as f:
            b = f.read(min(4 * 1024 * 1024, max_chars * 4 + 1024))
    except Exception:
        return JSONResponse(status_code=500, content={"error": "read_failed"})

    is_binary = b"\x00" in b[:4096]
    try:
        text = b.decode("utf-8", errors="replace")
    except Exception:
        text = str(b)

    truncated = False
    if len(text) > max_chars:
        text = text[:max_chars] + "\n...[内容已截断]..."
        truncated = True

    rel = os.path.relpath(abs_path, root).replace("\\", "/")
    return {"task_id": task_id, "path": rel, "text": text, "truncated": truncated, "binary_hint": bool(is_binary)}

@app.get("/api/loot/download")
def loot_download(request: Request, task_id: str = Query(""), path: str = Query("")):
    root = _loot_task_root(task_id)
    if not root:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    abs_path = _safe_join_under_allow_empty(root, path)
    if not abs_path:
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
        return JSONResponse(status_code=404, content={"error": "not_found"})
    filename = os.path.basename(abs_path)
    request.state.audit_action = "loot_download"
    request.state.audit_detail = {"task_id": task_id, "path": (path or "").replace("\\", "/").lstrip("/")}
    return FileResponse(abs_path, filename=filename)

@app.post("/api/loot/upload")
async def loot_upload(
    request: Request,
    file: UploadFile = File(...),
    task_id: str = Query(""),
    path: str = Query(""),
    overwrite: bool = Query(False),
):
    root = _loot_task_root(task_id)
    if not root:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    abs_dir = _safe_join_under_allow_empty(root, path)
    if not abs_dir:
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    try:
        os.makedirs(abs_dir, exist_ok=True)
    except Exception:
        return JSONResponse(status_code=500, content={"error": "mkdir_failed"})

    name = os.path.basename((file.filename or "").replace("\\", "/"))
    name = re.sub(r"[^\w.\-()\u4e00-\u9fff ]+", "_", name).strip()
    if not name:
        return JSONResponse(status_code=400, content={"error": "invalid_filename"})

    abs_path = os.path.abspath(os.path.join(abs_dir, name))
    base_abs = os.path.abspath(root)
    if not (abs_path == base_abs or abs_path.startswith(base_abs + os.sep)):
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    if os.path.exists(abs_path) and not overwrite:
        return JSONResponse(status_code=409, content={"error": "already_exists"})

    max_bytes = 50 * 1024 * 1024
    try:
        data = await file.read()
    except Exception:
        return JSONResponse(status_code=500, content={"error": "read_failed"})
    if data is None:
        return JSONResponse(status_code=400, content={"error": "empty"})
    if len(data) > max_bytes:
        return JSONResponse(status_code=400, content={"error": "file_too_large"})
    try:
        with open(abs_path, "wb") as f:
            f.write(data)
    except Exception:
        return JSONResponse(status_code=500, content={"error": "write_failed"})

    rel = os.path.relpath(abs_path, root).replace("\\", "/")
    request.state.audit_action = "loot_upload"
    request.state.audit_detail = {"task_id": task_id, "path": rel, "size": len(data)}
    return {"ok": True, "task_id": task_id, "path": rel, "size": len(data)}

class LootMkdirRequest(BaseModel):
    task_id: str = Field(default="")
    path: str = Field(default="")

@app.post("/api/loot/mkdir")
def loot_mkdir(request: Request, req: LootMkdirRequest):
    root = _loot_task_root(req.task_id)
    if not root:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    p = (req.path or "").replace("\\", "/").strip()
    if not p or p in {"/", "."}:
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    abs_dir = _safe_join_under_allow_empty(root, p)
    if not abs_dir:
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    try:
        os.makedirs(abs_dir, exist_ok=True)
    except Exception:
        return JSONResponse(status_code=500, content={"error": "mkdir_failed"})
    rel = os.path.relpath(abs_dir, root).replace("\\", "/")
    request.state.audit_action = "loot_mkdir"
    request.state.audit_detail = {"task_id": req.task_id, "path": rel}
    return {"ok": True, "task_id": req.task_id, "path": rel}

@app.delete("/api/loot/delete")
def loot_delete(request: Request, task_id: str = Query(""), path: str = Query("")):
    root = _loot_task_root(task_id)
    if not root:
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    p = (path or "").replace("\\", "/").strip().lstrip("/")
    if not p:
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    abs_path = _safe_join_under_allow_empty(root, p)
    if not abs_path:
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    if not os.path.exists(abs_path):
        return JSONResponse(status_code=404, content={"error": "not_found"})
    try:
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)
    except Exception:
        return JSONResponse(status_code=500, content={"error": "delete_failed"})
    request.state.audit_action = "loot_delete"
    request.state.audit_detail = {"task_id": task_id, "path": p}
    return {"ok": True}

@app.get("/api/msf/sessions")
def msf_sessions(task_id: str = Query(""), limit: int = 20000):
    task_id = (task_id or "").strip()
    if not _sanitize_task_id(task_id):
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    try:
        limit = max(100, min(int(limit), 50000))
    except Exception:
        limit = 20000
    rows = task_store.load_events_with_meta(task_id, limit=limit, since_id=0)
    sessions = {}
    for r in rows or []:
        ev = (r or {}).get("event") or {}
        if ev.get("type") != "log":
            continue
        content = str(ev.get("content") or "")
        if not content:
            continue
        if "[工具结果] msfconsole" not in content and "session" not in content.lower():
            continue
        m = re.search(r"(?:command shell|meterpreter)?\s*session\s+(\d+)\s+opened", content, re.IGNORECASE)
        if not m:
            m = re.search(r"Session\s+(\d+)\s+opened", content, re.IGNORECASE)
        if not m:
            continue
        sid = str(m.group(1) or "").strip()
        if not sid:
            continue
        kind = "unknown"
        if "meterpreter" in content.lower():
            kind = "meterpreter"
        elif "command shell" in content.lower():
            kind = "shell"
        sessions[sid] = {
            "session_id": int(sid),
            "kind": kind,
        }
    out = sorted(sessions.values(), key=lambda x: int(x.get("session_id") or 0))
    return {"task_id": task_id, "sessions": out}

@app.get("/api/msf/cli/status")
def msf_cli_status(task_id: str = Query("")):
    task_id = (task_id or "").strip()
    if not _sanitize_task_id(task_id):
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    return {"task_id": task_id, **executor.msf_cli_status(task_id)}

@app.get("/api/msf/cli/output")
def msf_cli_output(task_id: str = Query(""), since: int = Query(0), limit: int = Query(400)):
    task_id = (task_id or "").strip()
    if not _sanitize_task_id(task_id):
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    return {"task_id": task_id, **executor.msf_cli_output(task_id, since_seq=since, limit=limit)}

class MsfCliSendRequest(BaseModel):
    task_id: str = Field(default="")
    cmd: str = Field(default="")

@app.post("/api/msf/cli/send")
def msf_cli_send(request: Request, req: MsfCliSendRequest):
    task_id = (req.task_id or "").strip()
    if not _sanitize_task_id(task_id):
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    cmd = (req.cmd or "").rstrip("\r\n")
    if not cmd:
        return JSONResponse(status_code=400, content={"error": "missing_cmd"})
    res = executor.msf_cli_send(task_id, cmd)
    if not res.get("ok"):
        return JSONResponse(status_code=400, content={"error": res.get("error") or "send_failed"})
    request.state.audit_action = "msf_cli_send"
    request.state.audit_detail = {"task_id": task_id, "cmd_len": len(cmd)}
    return {"ok": True}

class MsfCliStopRequest(BaseModel):
    task_id: str = Field(default="")

@app.post("/api/msf/cli/stop")
def msf_cli_stop(request: Request, req: MsfCliStopRequest):
    task_id = (req.task_id or "").strip()
    if not _sanitize_task_id(task_id):
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    res = executor.msf_cli_stop(task_id)
    request.state.audit_action = "msf_cli_stop"
    request.state.audit_detail = {"task_id": task_id, "stopped": bool(res.get("stopped"))}
    return {"ok": True, "stopped": bool(res.get("stopped"))}

@app.get("/api/msf/read_file")
def msf_read_file(
    request: Request,
    task_id: str = Query(""),
    session_id: int = Query(0),
    path: str = Query(""),
    max_chars: int = Query(20000),
):
    task_id = (task_id or "").strip()
    if not _sanitize_task_id(task_id):
        return JSONResponse(status_code=400, content={"error": "invalid_task_id"})
    try:
        session_id = int(session_id)
    except Exception:
        session_id = 0
    if session_id <= 0 or session_id > 9999:
        return JSONResponse(status_code=400, content={"error": "invalid_session_id"})
    p = (path or "").strip()
    if not p or len(p) > 400 or "\n" in p or "\r" in p:
        return JSONResponse(status_code=400, content={"error": "invalid_path"})
    try:
        max_chars = max(100, min(int(max_chars), 200000))
    except Exception:
        max_chars = 20000

    tool_def = tool_manager.get_tool("msfconsole")
    if not tool_def or tool_def.get("enabled", True) is False:
        return JSONResponse(status_code=400, content={"error": "msfconsole_not_available"})

    st = executor.msf_cli_status(task_id)
    if not st.get("running"):
        return JSONResponse(status_code=400, content={"error": "msf_not_running"})

    work_root = os.path.join(BASE_DIR, "data", "temp", "tool_runs", task_id)
    os.makedirs(work_root, exist_ok=True)
    ts = int(time.time() * 1000)
    rc_path = os.path.join(work_root, f"read_file_{session_id}_{ts}.rc")

    begin = "__APAI_BEGIN_FILE__"
    end = "__APAI_END_FILE__"
    inner_path = p.replace("\\", "\\\\").replace('"', '\\"')
    def _run_read_command(cmd_text: str) -> str:
        cmd_for_c = cmd_text.replace('"', '\\"')
        lines = [
            f'echo {begin}',
            f'sessions -i {session_id} -C "{cmd_for_c}"',
            f'echo {end}',
        ]
        with open(rc_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        executor.msf_cli_send(task_id, f'resource "{rc_path.replace("\\\\", "/").replace("\\", "/")}"')
        begin_ts = time.time()
        raw_lines: List[str] = []
        cursor = 0
        while time.time() - begin_ts < 20:
            out = executor.msf_cli_output(task_id, since_seq=cursor, limit=800)
            cursor = int(out.get("seq") or cursor)
            for item in out.get("lines") or []:
                raw_lines.append(str(item.get("line") or ""))
            joined = "".join(raw_lines)
            if begin in joined and end in joined:
                break
            time.sleep(0.2)
        return "".join(raw_lines)

    raw = _run_read_command(f'cat "{inner_path}"')
    extracted = ""
    truncated = False
    i1 = raw.find(begin)
    i2 = raw.find(end)
    if i1 >= 0 and i2 >= 0 and i2 > i1:
        extracted = raw[i1 + len(begin) : i2]
        extracted = extracted.strip("\r\n")
    else:
        extracted = raw.strip()
    if len(extracted) > max_chars:
        extracted = extracted[:max_chars] + "\n...[内容已截断]..."
        truncated = True

    if re.search(r"not recognized|command not found", extracted, re.IGNORECASE):
        raw2 = _run_read_command(f'type "{inner_path}"')
        i1b = raw2.find(begin)
        i2b = raw2.find(end)
        if i1b >= 0 and i2b >= 0 and i2b > i1b:
            extracted2 = raw2[i1b + len(begin) : i2b].strip("\r\n")
        else:
            extracted2 = raw2.strip()
        if extracted2 and extracted2 != extracted:
            extracted = extracted2
            if len(extracted) > max_chars:
                extracted = extracted[:max_chars] + "\n...[内容已截断]..."
                truncated = True

    request.state.audit_action = "msf_read_file"
    request.state.audit_detail = {"task_id": task_id, "session_id": session_id, "path": p}

    try:
        os.remove(rc_path)
    except Exception:
        pass

    return {
        "task_id": task_id,
        "session_id": session_id,
        "path": p,
        "text": extracted,
        "truncated": truncated,
        "return_code": 0,
        "stderr": "",
    }


@app.get("/api/scan/stream")
async def stream_scan(request: Request, target: str, goal: str = "对该目标进行全面的渗透测试"):
    provider = os.getenv("AI_PROVIDER", "deepseek")
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            return EventSourceResponse([{"type": "error", "content": "错误: 未配置 OPENAI_API_KEY"}])
    else:
        if not os.getenv("DEEPSEEK_API_KEY"):
            return EventSourceResponse([{"type": "error", "content": "错误: 未配置 DEEPSEEK_API_KEY"}])

    # Simple task ID based on target for now (one active scan per target)
    task_id = _sanitize_task_id(target)
    if not task_id:
        return EventSourceResponse([{"type": "error", "content": "错误: invalid_task_id"}])
    target = task_id
    
    # If task exists and is running, attach to it
    if task_id in active_tasks:
        task_info = active_tasks[task_id]
        
        # Create a new queue for this client
        client_queue = asyncio.Queue()
        task_info["listeners"].append(client_queue)
        
        async def event_generator():
            try:
                yield {"data": json.dumps({"type": "log", "content": f"[系统] 已连接到任务: {target}"}, ensure_ascii=False)}
                
                # Replay history first
                for hist_event in task_info["history"]:
                    yield {"data": json.dumps(hist_event, ensure_ascii=False)}
                
                # Stream new events
                ping_counter = 0
                while True:
                    # Check if client disconnected
                    if await request.is_disconnected():
                        break
                        
                    # Use wait_for to prevent blocking forever if client disconnects during get()
                    try:
                        event = await asyncio.wait_for(client_queue.get(), timeout=1.0)
                    except asyncio.TimeoutError:
                        ping_counter += 1
                        if ping_counter >= 15:
                            ping_counter = 0
                            yield {"data": json.dumps({"type": "ping"}, ensure_ascii=False)}
                        continue
                    
                    if event is None: # Sentinel for end
                        break
                    ping_counter = 0
                    yield {"data": json.dumps(event, ensure_ascii=False)}
                    
                    # Check task status
                    if task_info["status"] == "finished" and client_queue.empty():
                        break
            except Exception as e:
                yield {"data": json.dumps({"type": "error", "content": f"Stream error: {str(e)}"}, ensure_ascii=False)}
            finally:
                # Cleanup listener
                if client_queue in task_info["listeners"]:
                    task_info["listeners"].remove(client_queue)
    
        return EventSourceResponse(event_generator())

    stored = task_store.get_task(task_id)
    if stored and stored.get("status") in {"finished", "cancelled", "error"}:
        history = task_store.load_events(task_id, limit=5000)

        async def replay_generator():
            for ev in history:
                yield {"data": json.dumps(ev, ensure_ascii=False)}
            yield {"data": json.dumps({"type": "log", "content": "[系统] 任务已结束（历史回放）"}, ensure_ascii=False)}

        return EventSourceResponse(replay_generator())

    _ensure_task_started(target, goal)
    
    # Recursive call to attach to the task we just created
    # But we can just duplicate the logic or redirect
    # Let's duplicate the attach logic for simplicity and correct context
    task_info = active_tasks[task_id]
    client_queue = asyncio.Queue()
    task_info["listeners"].append(client_queue)
    
    async def event_generator():
        try:
            yield {"data": json.dumps({"type": "log", "content": f"[系统] 任务启动: {target}"}, ensure_ascii=False)}
            
            ping_counter = 0
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    event = await asyncio.wait_for(client_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    ping_counter += 1
                    if ping_counter >= 15:
                        ping_counter = 0
                        yield {"data": json.dumps({"type": "ping"}, ensure_ascii=False)}
                    continue

                if event is None:
                    break
                ping_counter = 0
                yield {"data": json.dumps(event, ensure_ascii=False)}
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "content": f"Stream error: {str(e)}"}, ensure_ascii=False)}
        finally:
             if client_queue in task_info["listeners"]:
                task_info["listeners"].remove(client_queue)
            
    return EventSourceResponse(event_generator())

@app.get("/api/tools")
def list_tools():
    allowed = _get_agent_allowed_tools()
    tools = []
    for t in tool_manager.list_tools():
        if t.get("enabled", True) is False:
            continue
        tool_name = t.get("name", "")
        item = dict(t)
        item["agent_allowed"] = bool(tool_name and tool_name in allowed)
        tools.append(item)
    internal_tools = [
        {
            "name": "web_search",
            "enabled": True,
            "internal": True,
            "short_description": "联网搜索（Bing/DDG 自动回退）",
            "description": "用于联网检索资料页链接与摘要，适合在知识库不足时补充信息来源。",
            "parameters": [
                {"name": "query", "type": "string", "description": "搜索关键词", "required": True},
                {"name": "max_results", "type": "int", "description": "返回结果数（默认 5）", "required": False},
                {"name": "engine", "type": "string", "description": "bing/ddg/auto（默认 bing）", "required": False},
            ],
            "agent_allowed": True,
        },
        {
            "name": "web_fetch",
            "enabled": True,
            "internal": True,
            "short_description": "抓取网页正文（安全限制）",
            "description": "抓取指定网页并提取可读文本，仅允许 http/https，禁止访问 localhost/内网/私有 IP。",
            "parameters": [
                {"name": "url", "type": "string", "description": "网页 URL（http/https）", "required": True},
                {"name": "max_chars", "type": "int", "description": "最大返回字符数（默认 20000）", "required": False},
            ],
            "agent_allowed": True,
        },
        {
            "name": "search_knowledge",
            "enabled": True,
            "internal": True,
            "short_description": "知识库检索（RAG / 关键词降级）",
            "description": "在 data/knowledge、data/skills、data/vulndb、data/playbooks 内检索相关内容；RAG 不可用时自动降级关键词检索。",
            "parameters": [
                {"name": "query", "type": "string", "description": "检索关键词", "required": True},
            ],
            "agent_allowed": True,
        },
        {
            "name": "add_knowledge",
            "enabled": True,
            "internal": True,
            "short_description": "写入知识库条目",
            "description": "将总结后的知识写入 data/knowledge 目录，供后续检索复用。",
            "parameters": [
                {"name": "filename", "type": "string", "description": "文件名（.md）", "required": True},
                {"name": "content", "type": "string", "description": "正文内容", "required": True},
                {"name": "category", "type": "string", "description": "分类（可选）", "required": False},
            ],
            "agent_allowed": True,
        },
        {
            "name": "save_playbook",
            "enabled": True,
            "internal": True,
            "short_description": "沉淀复现/排障 Playbook",
            "description": "将可复用的验证/排障步骤写入 data/playbooks，便于后续复用。",
            "parameters": [
                {"name": "filename", "type": "string", "description": "文件名（.md）", "required": True},
                {"name": "content", "type": "string", "description": "正文内容", "required": True},
            ],
            "agent_allowed": True,
        },
        {
            "name": "search_playbooks",
            "enabled": True,
            "internal": True,
            "short_description": "检索 Playbooks",
            "description": "在 data/playbooks 中检索可复用方案。",
            "parameters": [
                {"name": "query", "type": "string", "description": "检索关键词", "required": True},
                {"name": "limit", "type": "int", "description": "返回条数（默认 5）", "required": False},
            ],
            "agent_allowed": True,
        },
    ]
    tools.extend(internal_tools)
    return {"tools": tools}

@app.get("/api/config")
def get_config():
    """Get current configuration (masked API Key, Max Steps, and Proxy)."""
    ai_provider = os.getenv("AI_PROVIDER", "deepseek")
    ai_model = os.getenv("AI_MODEL", "deepseek-reasoner" if ai_provider == "deepseek" else "gpt-5.2")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    masked_key = f"{deepseek_key[:4]}...{deepseek_key[-4:]}" if len(deepseek_key) > 8 else ("****" if deepseek_key else "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    masked_openai_key = f"{openai_key[:4]}...{openai_key[-4:]}" if len(openai_key) > 8 else ("****" if openai_key else "")
    ocr_key = os.getenv("DEEPSEEK_OCR_API_KEY", "")
    masked_ocr_key = f"{ocr_key[:4]}...{ocr_key[-4:]}" if len(ocr_key) > 8 else ("****" if ocr_key else "")
    max_steps = int(os.getenv("MAX_STEPS", "500"))
    proxy_url = os.getenv("PROXY_URL", "")
    language = os.getenv("LANGUAGE", "zh")
    ai_bind_interface = os.getenv("AI_BIND_INTERFACE", "eth0")
    ai_lhost = os.getenv("AI_LHOST", "")
    tool_workdir_mode = os.getenv("TOOL_WORKDIR_MODE", "project")
    try:
        tool_max_output_chars = int(os.getenv("TOOL_MAX_OUTPUT_CHARS", "200000") or "200000")
    except Exception:
        tool_max_output_chars = 200000
    tool_sandbox = os.getenv("TOOL_SANDBOX", "process")
    tool_docker_image = os.getenv("TOOL_DOCKER_IMAGE", "")
    tool_docker_network = os.getenv("TOOL_DOCKER_NETWORK", "bridge")
    tool_docker_memory = os.getenv("TOOL_DOCKER_MEMORY", "")
    tool_docker_pids_limit = os.getenv("TOOL_DOCKER_PIDS_LIMIT", "")
    try:
        audit_log_max_rows = int(os.getenv("AUDIT_LOG_MAX_ROWS", "10000") or "10000")
    except Exception:
        audit_log_max_rows = 10000
    audit_log_max_rows = max(1, min(100000, audit_log_max_rows))
    deepseek_ocr_base_url = os.getenv("DEEPSEEK_OCR_BASE_URL", "")
    deepseek_ocr_model = os.getenv("DEEPSEEK_OCR_MODEL", "")
    deepseek_ocr_timeout = os.getenv("DEEPSEEK_OCR_TIMEOUT", "120")
    return {
        "app_version": APP_VERSION,
        "ai_provider": ai_provider,
        "ai_model": ai_model,
        "openai_base_url": openai_base_url,
        "deepseek_base_url": deepseek_base_url,
        "deepseek_api_key": masked_key, 
        "deepseek_is_set": bool(deepseek_key),
        "openai_api_key": masked_openai_key,
        "openai_is_set": bool(openai_key),
        "deepseek_ocr_api_key": masked_ocr_key,
        "ocr_is_set": bool(ocr_key),
        "max_steps": max_steps,
        "proxy_url": proxy_url,
        "language": language,
        "ai_bind_interface": ai_bind_interface,
        "ai_lhost": ai_lhost,
        "tool_workdir_mode": tool_workdir_mode,
        "tool_max_output_chars": tool_max_output_chars,
        "tool_sandbox": tool_sandbox,
        "tool_docker_image": tool_docker_image,
        "tool_docker_network": tool_docker_network,
        "tool_docker_memory": tool_docker_memory,
        "tool_docker_pids_limit": tool_docker_pids_limit,
        "audit_log_max_rows": audit_log_max_rows,
        "deepseek_ocr_base_url": deepseek_ocr_base_url,
        "deepseek_ocr_model": deepseek_ocr_model,
        "deepseek_ocr_timeout": deepseek_ocr_timeout,
    }

@app.get("/api/health")
def health():
    ai_provider = os.getenv("AI_PROVIDER", "deepseek")
    deepseek_ok = bool(os.getenv("DEEPSEEK_API_KEY", ""))
    openai_ok = bool(os.getenv("OPENAI_API_KEY", ""))
    ai_key_ok = openai_ok if ai_provider == "openai" else deepseek_ok

    rag_available = True
    try:
        import chromadb  # noqa: F401
        import sentence_transformers  # noqa: F401
    except Exception:
        rag_available = False

    searchsploit_available = bool(shutil.which("searchsploit"))

    state_dir = os.path.join(BASE_DIR, "data", "state")
    os.makedirs(state_dir, exist_ok=True)
    db_writable = True
    try:
        probe = os.path.join(state_dir, f".write_probe_{int(time.time())}")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
    except Exception:
        db_writable = False

    ok = bool(ai_key_ok and db_writable)
    warnings = []
    if not rag_available:
        warnings.append("RAG 依赖未安装（语义检索降级）")
    if not searchsploit_available:
        warnings.append("searchsploit 未安装（Exploit-DB 搜索不可用）")
    if not ai_key_ok:
        warnings.append("AI API Key 未配置（无法发起扫描）")
    if not db_writable:
        warnings.append("data/state 不可写（任务/漏洞无法落盘）")

    return {
        "app_version": APP_VERSION,
        "ok": ok,
        "ai_provider": ai_provider,
        "ai_key_ok": ai_key_ok,
        "rag_available": rag_available,
        "searchsploit_available": searchsploit_available,
        "db_writable": db_writable,
        "warnings": warnings,
    }

@app.get("/api/system/metrics")
def system_metrics():
    ts = time.time()
    disk = shutil.disk_usage(BASE_DIR)
    payload: Dict[str, Any] = {
        "available": True,
        "timestamp": ts,
        "cpu_percent": None,
        "memory": None,
        "disk": {
            "path": BASE_DIR,
            "total": int(disk.total),
            "used": int(disk.used),
            "free": int(disk.free),
            "percent": float((disk.used / disk.total * 100.0) if disk.total else 0.0),
        },
        "disk_io": None,
    }

    try:
        import psutil  # type: ignore

        try:
            payload["cpu_percent"] = float(psutil.cpu_percent(interval=None))
        except Exception:
            payload["cpu_percent"] = None

        try:
            vm = psutil.virtual_memory()
            payload["memory"] = {
                "total": int(vm.total),
                "available": int(vm.available),
                "used": int(vm.used),
                "percent": float(vm.percent),
            }
        except Exception:
            payload["memory"] = None

        try:
            io = psutil.disk_io_counters()
            if io:
                payload["disk_io"] = {
                    "read_bytes": int(getattr(io, "read_bytes", 0)),
                    "write_bytes": int(getattr(io, "write_bytes", 0)),
                }
        except Exception:
            payload["disk_io"] = None
    except Exception:
        payload["available"] = False
        payload["error"] = "psutil_not_installed"

    return payload

class ConfigRequest(BaseModel):
    deepseek_api_key: str = None
    deepseek_ocr_api_key: str = None
    deepseek_ocr_base_url: str = None
    deepseek_ocr_model: str = None
    deepseek_ocr_timeout: str = None
    openai_api_key: str = None
    openai_base_url: str = None
    deepseek_base_url: str = None
    ai_provider: str = None
    ai_model: str = None
    max_steps: int = None
    proxy_url: str = None
    language: str = None
    ai_bind_interface: str = None
    ai_lhost: str = None
    tool_workdir_mode: str = None
    tool_max_output_chars: int = None
    tool_sandbox: str = None
    tool_docker_image: str = None
    tool_docker_network: str = None
    tool_docker_memory: str = None
    tool_docker_pids_limit: str = None
    audit_log_max_rows: int = None

@app.get("/api/network/interfaces")
def get_network_interfaces():
    interfaces = list_network_interfaces()
    current_iface = os.getenv("AI_BIND_INTERFACE", "") or ""
    if current_iface and any(i.get("name") == current_iface for i in interfaces):
        selected = current_iface
    else:
        default_iface = get_default_interface_name()
        if default_iface and any(i.get("name") == default_iface for i in interfaces):
            selected = default_iface
        else:
            preferred = next((i for i in interfaces if not i.get("loopback") and i.get("up") and i.get("ipv4")), None)
            selected = preferred.get("name") if preferred else (interfaces[0].get("name") if interfaces else "")

    ipv4 = get_ip_address(selected) if selected else None
    ai_lhost = os.getenv("AI_LHOST", "")
    effective_lhost = ai_lhost if ai_lhost else (ipv4 or "127.0.0.1")

    return {
        "interfaces": interfaces,
        "selected": selected,
        "selected_ipv4": ipv4,
        "ai_lhost": ai_lhost,
        "effective_lhost": effective_lhost,
    }

@app.get("/api/ocr")
def ocr_file(path: str, provider: Optional[str] = None, lang: Optional[str] = None):
    if not path:
        return JSONResponse(status_code=400, content={"error": "Missing path"})

    path = path.replace("\\", "/").lstrip("/")
    if ".." in path or path.startswith("/"):
        return JSONResponse(status_code=400, content={"error": "Invalid path"})

    data_dir = os.path.join(BASE_DIR, "data")
    abs_path = os.path.realpath(os.path.join(data_dir, path))
    if not abs_path.startswith(os.path.realpath(data_dir) + os.sep):
        return JSONResponse(status_code=400, content={"error": "Invalid path"})

    if not os.path.exists(abs_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})

    try:
        text, used_provider = ocr_image(abs_path)
        return {"provider": used_provider, "text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/config")
def update_config(request: Request, config: ConfigRequest):
    """Update configuration (API Key, Max Steps, Proxy, and Language)."""
    env_path = os.path.join(BASE_DIR, ".env")
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
    new_lines = []
    key_found = False
    openai_key_found = False
    steps_found = False
    proxy_found = False
    lang_found = False
    iface_found = False
    lhost_found = False
    provider_found = False
    model_found = False
    ocr_base_url_found = False
    ocr_model_found = False
    ocr_timeout_found = False
    tool_workdir_found = False
    tool_max_output_found = False
    tool_sandbox_found = False
    tool_docker_image_found = False
    tool_docker_network_found = False
    tool_docker_memory_found = False
    tool_docker_pids_found = False
    openai_base_url_found = False
    deepseek_base_url_found = False
    audit_log_max_rows_found = False

    fields_set = getattr(config, "__fields_set__", set())
    try:
        changed = sorted([str(x) for x in fields_set if x])
    except Exception:
        changed = []
    request.state.audit_action = "update_config"
    request.state.audit_detail = {
        "changed_fields": changed,
        "has_deepseek_api_key": bool(getattr(config, "deepseek_api_key", None)),
        "has_openai_api_key": bool(getattr(config, "openai_api_key", None)),
        "has_proxy_url": bool(getattr(config, "proxy_url", None)),
        "ai_provider": getattr(config, "ai_provider", None),
        "ai_model": getattr(config, "ai_model", None),
        "audit_log_max_rows": getattr(config, "audit_log_max_rows", None),
    }
    max_steps_set = "max_steps" in fields_set
    proxy_url_set = "proxy_url" in fields_set
    language_set = "language" in fields_set
    ai_bind_interface_set = "ai_bind_interface" in fields_set
    ai_lhost_set = "ai_lhost" in fields_set
    deepseek_ocr_api_key_set = "deepseek_ocr_api_key" in fields_set
    deepseek_ocr_base_url_set = "deepseek_ocr_base_url" in fields_set
    deepseek_ocr_model_set = "deepseek_ocr_model" in fields_set
    deepseek_ocr_timeout_set = "deepseek_ocr_timeout" in fields_set
    openai_api_key_set = "openai_api_key" in fields_set
    openai_base_url_set = "openai_base_url" in fields_set
    deepseek_base_url_set = "deepseek_base_url" in fields_set
    ai_provider_set = "ai_provider" in fields_set
    ai_model_set = "ai_model" in fields_set
    tool_workdir_mode_set = "tool_workdir_mode" in fields_set
    tool_max_output_chars_set = "tool_max_output_chars" in fields_set
    tool_sandbox_set = "tool_sandbox" in fields_set
    tool_docker_image_set = "tool_docker_image" in fields_set
    tool_docker_network_set = "tool_docker_network" in fields_set
    tool_docker_memory_set = "tool_docker_memory" in fields_set
    tool_docker_pids_limit_set = "tool_docker_pids_limit" in fields_set
    audit_log_max_rows_set = "audit_log_max_rows" in fields_set

    deepseek_api_key = _sanitize_env_value(config.deepseek_api_key) if config.deepseek_api_key else None
    deepseek_ocr_api_key = _sanitize_env_value(config.deepseek_ocr_api_key) if deepseek_ocr_api_key_set else None
    deepseek_ocr_base_url = _sanitize_env_value(config.deepseek_ocr_base_url) if deepseek_ocr_base_url_set else None
    deepseek_ocr_model = _sanitize_env_value(config.deepseek_ocr_model) if deepseek_ocr_model_set else None
    deepseek_ocr_timeout = _sanitize_env_value(config.deepseek_ocr_timeout) if deepseek_ocr_timeout_set else None
    openai_api_key = _sanitize_env_value(config.openai_api_key) if openai_api_key_set else None
    openai_base_url = _sanitize_env_value(config.openai_base_url) if openai_base_url_set else None
    deepseek_base_url = _sanitize_env_value(config.deepseek_base_url) if deepseek_base_url_set else None
    ai_provider = _sanitize_env_value(config.ai_provider) if ai_provider_set else None
    ai_model = _sanitize_env_value(config.ai_model) if ai_model_set else None
    proxy_url = _sanitize_env_value(config.proxy_url) if proxy_url_set else None
    language = _sanitize_env_value(config.language) if (language_set and config.language) else None
    ai_bind_interface = _sanitize_env_value(config.ai_bind_interface) if (ai_bind_interface_set and config.ai_bind_interface) else None
    ai_lhost = _sanitize_env_value(config.ai_lhost) if ai_lhost_set else None
    tool_workdir_mode = _sanitize_env_value(config.tool_workdir_mode) if tool_workdir_mode_set else None
    tool_sandbox = _sanitize_env_value(config.tool_sandbox) if tool_sandbox_set else None
    tool_docker_image = _sanitize_env_value(config.tool_docker_image) if tool_docker_image_set else None
    tool_docker_network = _sanitize_env_value(config.tool_docker_network) if tool_docker_network_set else None
    tool_docker_memory = _sanitize_env_value(config.tool_docker_memory) if tool_docker_memory_set else None
    tool_docker_pids_limit = _sanitize_env_value(config.tool_docker_pids_limit) if tool_docker_pids_limit_set else None

    if audit_log_max_rows_set:
        v = config.audit_log_max_rows
        if v is None:
            v = 10000
        try:
            v = int(v)
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid audit_log_max_rows"})
        v = max(1, min(100000, v))
        audit_log_max_rows_val = str(v)
    else:
        audit_log_max_rows_val = None

    try:
        changed = sorted([str(x) for x in fields_set])
        request.state.audit_action = "update_config"
        request.state.audit_detail = {
            "changed_fields": changed,
            "sensitive_fields_changed": sorted([x for x in changed if x in {"deepseek_api_key", "openai_api_key", "deepseek_ocr_api_key"}]),
        }
    except Exception:
        pass

    if tool_max_output_chars_set:
        tool_max_output_chars = config.tool_max_output_chars
        if tool_max_output_chars is None:
            tool_max_output_chars_val = "200000"
        else:
            try:
                tool_max_output_chars_val = str(int(tool_max_output_chars))
            except Exception:
                return JSONResponse(status_code=400, content={"error": "Invalid tool_max_output_chars"})
    else:
        tool_max_output_chars_val = None

    if deepseek_ocr_timeout_set and deepseek_ocr_timeout is not None and not deepseek_ocr_timeout.strip():
        deepseek_ocr_timeout = "120"
    if openai_base_url_set and openai_base_url is not None and not openai_base_url.strip():
        openai_base_url = "https://api.openai.com/v1"
    if deepseek_base_url_set and deepseek_base_url is not None and not deepseek_base_url.strip():
        deepseek_base_url = "https://api.deepseek.com/v1"

    if deepseek_api_key and not _validate_env_value(deepseek_api_key):
        return JSONResponse(status_code=400, content={"error": "Invalid deepseek_api_key"})
    if deepseek_ocr_api_key_set and (deepseek_ocr_api_key is not None) and not _validate_env_value(deepseek_ocr_api_key):
        return JSONResponse(status_code=400, content={"error": "Invalid deepseek_ocr_api_key"})
    if deepseek_ocr_base_url_set and (deepseek_ocr_base_url is not None) and not _validate_env_value(deepseek_ocr_base_url):
        return JSONResponse(status_code=400, content={"error": "Invalid deepseek_ocr_base_url"})
    if deepseek_ocr_base_url_set and not _validate_http_url(deepseek_ocr_base_url or ""):
        return JSONResponse(status_code=400, content={"error": "Invalid deepseek_ocr_base_url"})
    if deepseek_ocr_model_set and (deepseek_ocr_model is not None) and deepseek_ocr_model and not _validate_model_name(deepseek_ocr_model):
        return JSONResponse(status_code=400, content={"error": "Invalid deepseek_ocr_model"})
    if deepseek_ocr_timeout_set and (deepseek_ocr_timeout is not None):
        if deepseek_ocr_timeout.strip():
            try:
                t = float(deepseek_ocr_timeout)
                if t < 5 or t > 600:
                    return JSONResponse(status_code=400, content={"error": "Invalid deepseek_ocr_timeout"})
            except Exception:
                return JSONResponse(status_code=400, content={"error": "Invalid deepseek_ocr_timeout"})
    if openai_api_key_set and (openai_api_key is not None) and not _validate_env_value(openai_api_key):
        return JSONResponse(status_code=400, content={"error": "Invalid openai_api_key"})
    if openai_base_url_set and (openai_base_url is not None) and not _validate_env_value(openai_base_url):
        return JSONResponse(status_code=400, content={"error": "Invalid openai_base_url"})
    if openai_base_url_set and not _validate_http_url(openai_base_url or ""):
        return JSONResponse(status_code=400, content={"error": "Invalid openai_base_url"})
    if deepseek_base_url_set and (deepseek_base_url is not None) and not _validate_env_value(deepseek_base_url):
        return JSONResponse(status_code=400, content={"error": "Invalid deepseek_base_url"})
    if deepseek_base_url_set and not _validate_http_url(deepseek_base_url or ""):
        return JSONResponse(status_code=400, content={"error": "Invalid deepseek_base_url"})
    if ai_provider_set and ai_provider not in ("deepseek", "openai"):
        return JSONResponse(status_code=400, content={"error": "Invalid ai_provider"})
    if ai_model_set and ai_model and not _validate_model_name(ai_model):
        return JSONResponse(status_code=400, content={"error": "Invalid ai_model"})
    if proxy_url_set and (proxy_url is not None) and not _validate_env_value(proxy_url):
        return JSONResponse(status_code=400, content={"error": "Invalid proxy_url"})
    if proxy_url_set and not _validate_proxy_url(proxy_url or ""):
        return JSONResponse(status_code=400, content={"error": "Invalid proxy_url"})
    if language and not _validate_env_value(language):
        return JSONResponse(status_code=400, content={"error": "Invalid language"})
    if ai_bind_interface and not _validate_iface_name(ai_bind_interface):
        return JSONResponse(status_code=400, content={"error": "Invalid ai_bind_interface"})
    if ai_lhost_set and not _validate_lhost(ai_lhost or ""):
        return JSONResponse(status_code=400, content={"error": "Invalid ai_lhost"})
    if tool_workdir_mode_set and tool_workdir_mode and tool_workdir_mode not in {"project", "isolated", "inherit"}:
        return JSONResponse(status_code=400, content={"error": "Invalid tool_workdir_mode"})
    if tool_sandbox_set and tool_sandbox and tool_sandbox not in {"process", "docker"}:
        return JSONResponse(status_code=400, content={"error": "Invalid tool_sandbox"})
    if tool_docker_network_set and tool_docker_network and tool_docker_network not in {"bridge", "host", "none"}:
        return JSONResponse(status_code=400, content={"error": "Invalid tool_docker_network"})
    if tool_docker_image_set and (tool_docker_image is not None) and not _validate_env_value(tool_docker_image):
        return JSONResponse(status_code=400, content={"error": "Invalid tool_docker_image"})
    if tool_docker_memory_set and (tool_docker_memory is not None) and not _validate_env_value(tool_docker_memory):
        return JSONResponse(status_code=400, content={"error": "Invalid tool_docker_memory"})
    if tool_docker_pids_limit_set and (tool_docker_pids_limit is not None) and not _validate_env_value(tool_docker_pids_limit):
        return JSONResponse(status_code=400, content={"error": "Invalid tool_docker_pids_limit"})
    
    # Process API Key
    if deepseek_api_key:
        os.environ["DEEPSEEK_API_KEY"] = deepseek_api_key

    if deepseek_ocr_api_key_set:
        os.environ["DEEPSEEK_OCR_API_KEY"] = deepseek_ocr_api_key
    if deepseek_ocr_base_url_set:
        os.environ["DEEPSEEK_OCR_BASE_URL"] = deepseek_ocr_base_url
    if deepseek_ocr_model_set:
        os.environ["DEEPSEEK_OCR_MODEL"] = deepseek_ocr_model
    if deepseek_ocr_timeout_set:
        os.environ["DEEPSEEK_OCR_TIMEOUT"] = deepseek_ocr_timeout

    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    if openai_base_url_set:
        os.environ["OPENAI_BASE_URL"] = openai_base_url
    if deepseek_base_url_set:
        os.environ["DEEPSEEK_BASE_URL"] = deepseek_base_url

    if ai_provider_set and ai_provider:
        os.environ["AI_PROVIDER"] = ai_provider

    if ai_model_set and ai_model:
        os.environ["AI_MODEL"] = ai_model
        
    # Process Max Steps
    if max_steps_set and config.max_steps:
        os.environ["MAX_STEPS"] = str(config.max_steps)
        
    # Process Proxy (allow empty string to clear it)
    if proxy_url_set:
        os.environ["PROXY_URL"] = proxy_url
        
    # Process Language
    if language:
        os.environ["LANGUAGE"] = language
    
    if ai_bind_interface:
        os.environ["AI_BIND_INTERFACE"] = ai_bind_interface
        
    if ai_lhost_set:
        os.environ["AI_LHOST"] = ai_lhost
    if tool_workdir_mode_set:
        os.environ["TOOL_WORKDIR_MODE"] = tool_workdir_mode
    if tool_max_output_chars_set:
        os.environ["TOOL_MAX_OUTPUT_CHARS"] = tool_max_output_chars_val
    if tool_sandbox_set:
        os.environ["TOOL_SANDBOX"] = tool_sandbox
    if tool_docker_image_set:
        os.environ["TOOL_DOCKER_IMAGE"] = tool_docker_image
    if tool_docker_network_set:
        os.environ["TOOL_DOCKER_NETWORK"] = tool_docker_network
    if tool_docker_memory_set:
        os.environ["TOOL_DOCKER_MEMORY"] = tool_docker_memory
    if tool_docker_pids_limit_set:
        os.environ["TOOL_DOCKER_PIDS_LIMIT"] = tool_docker_pids_limit
    if audit_log_max_rows_set and audit_log_max_rows_val is not None:
        os.environ["AUDIT_LOG_MAX_ROWS"] = audit_log_max_rows_val
        try:
            audit_store.prune_keep_latest(int(audit_log_max_rows_val))
        except Exception:
            pass

    for line in lines:
        if line.strip().startswith("DEEPSEEK_API_KEY="):
            if deepseek_api_key:
                new_lines.append(f"DEEPSEEK_API_KEY={deepseek_api_key}\n")
            else:
                new_lines.append(line)
            key_found = True
        elif line.strip().startswith("OPENAI_API_KEY="):
            if openai_api_key:
                new_lines.append(f"OPENAI_API_KEY={openai_api_key}\n")
            else:
                new_lines.append(line)
            openai_key_found = True
        elif line.strip().startswith("OPENAI_BASE_URL="):
            if openai_base_url_set:
                new_lines.append(f"OPENAI_BASE_URL={openai_base_url}\n")
            else:
                new_lines.append(line)
            openai_base_url_found = True
        elif line.strip().startswith("DEEPSEEK_BASE_URL="):
            if deepseek_base_url_set:
                new_lines.append(f"DEEPSEEK_BASE_URL={deepseek_base_url}\n")
            else:
                new_lines.append(line)
            deepseek_base_url_found = True
        elif line.strip().startswith("AI_PROVIDER="):
            if ai_provider_set and ai_provider:
                new_lines.append(f"AI_PROVIDER={ai_provider}\n")
            else:
                new_lines.append(line)
            provider_found = True
        elif line.strip().startswith("AI_MODEL="):
            if ai_model_set and ai_model:
                new_lines.append(f"AI_MODEL={ai_model}\n")
            else:
                new_lines.append(line)
            model_found = True
        elif line.strip().startswith("DEEPSEEK_OCR_API_KEY="):
            if deepseek_ocr_api_key_set:
                new_lines.append(f"DEEPSEEK_OCR_API_KEY={deepseek_ocr_api_key}\n")
            else:
                new_lines.append(line)
        elif line.strip().startswith("DEEPSEEK_OCR_BASE_URL="):
            if deepseek_ocr_base_url_set:
                new_lines.append(f"DEEPSEEK_OCR_BASE_URL={deepseek_ocr_base_url}\n")
            else:
                new_lines.append(line)
            ocr_base_url_found = True
        elif line.strip().startswith("DEEPSEEK_OCR_MODEL="):
            if deepseek_ocr_model_set:
                new_lines.append(f"DEEPSEEK_OCR_MODEL={deepseek_ocr_model}\n")
            else:
                new_lines.append(line)
            ocr_model_found = True
        elif line.strip().startswith("DEEPSEEK_OCR_TIMEOUT="):
            if deepseek_ocr_timeout_set:
                new_lines.append(f"DEEPSEEK_OCR_TIMEOUT={deepseek_ocr_timeout}\n")
            else:
                new_lines.append(line)
            ocr_timeout_found = True
        elif line.strip().startswith("MAX_STEPS="):
            if max_steps_set and config.max_steps:
                new_lines.append(f"MAX_STEPS={config.max_steps}\n")
            else:
                new_lines.append(line)
            steps_found = True
        elif line.strip().startswith("PROXY_URL="):
            if proxy_url_set:
                new_lines.append(f"PROXY_URL={proxy_url}\n")
            else:
                new_lines.append(line)
            proxy_found = True
        elif line.strip().startswith("LANGUAGE="):
            if language:
                new_lines.append(f"LANGUAGE={language}\n")
            else:
                new_lines.append(line)
            lang_found = True
        elif line.strip().startswith("AI_BIND_INTERFACE="):
            if ai_bind_interface:
                new_lines.append(f"AI_BIND_INTERFACE={ai_bind_interface}\n")
            else:
                new_lines.append(line)
            iface_found = True
        elif line.strip().startswith("AI_LHOST="):
            if ai_lhost_set:
                new_lines.append(f"AI_LHOST={ai_lhost}\n")
            else:
                new_lines.append(line)
            lhost_found = True
        elif line.strip().startswith("TOOL_WORKDIR_MODE="):
            if tool_workdir_mode_set:
                new_lines.append(f"TOOL_WORKDIR_MODE={tool_workdir_mode}\n")
            else:
                new_lines.append(line)
            tool_workdir_found = True
        elif line.strip().startswith("TOOL_MAX_OUTPUT_CHARS="):
            if tool_max_output_chars_set:
                new_lines.append(f"TOOL_MAX_OUTPUT_CHARS={tool_max_output_chars_val}\n")
            else:
                new_lines.append(line)
            tool_max_output_found = True
        elif line.strip().startswith("TOOL_SANDBOX="):
            if tool_sandbox_set:
                new_lines.append(f"TOOL_SANDBOX={tool_sandbox}\n")
            else:
                new_lines.append(line)
            tool_sandbox_found = True
        elif line.strip().startswith("TOOL_DOCKER_IMAGE="):
            if tool_docker_image_set:
                new_lines.append(f"TOOL_DOCKER_IMAGE={tool_docker_image}\n")
            else:
                new_lines.append(line)
            tool_docker_image_found = True
        elif line.strip().startswith("TOOL_DOCKER_NETWORK="):
            if tool_docker_network_set:
                new_lines.append(f"TOOL_DOCKER_NETWORK={tool_docker_network}\n")
            else:
                new_lines.append(line)
            tool_docker_network_found = True
        elif line.strip().startswith("TOOL_DOCKER_MEMORY="):
            if tool_docker_memory_set:
                new_lines.append(f"TOOL_DOCKER_MEMORY={tool_docker_memory}\n")
            else:
                new_lines.append(line)
            tool_docker_memory_found = True
        elif line.strip().startswith("TOOL_DOCKER_PIDS_LIMIT="):
            if tool_docker_pids_limit_set:
                new_lines.append(f"TOOL_DOCKER_PIDS_LIMIT={tool_docker_pids_limit}\n")
            else:
                new_lines.append(line)
            tool_docker_pids_found = True
        elif line.strip().startswith("AUDIT_LOG_MAX_ROWS="):
            if audit_log_max_rows_set and audit_log_max_rows_val is not None:
                new_lines.append(f"AUDIT_LOG_MAX_ROWS={audit_log_max_rows_val}\n")
            else:
                new_lines.append(line)
            audit_log_max_rows_found = True
        else:
            new_lines.append(line)
    
    if not key_found and deepseek_api_key:
        new_lines.append(f"\nDEEPSEEK_API_KEY={deepseek_api_key}\n")

    if deepseek_ocr_api_key_set and not any(l.strip().startswith("DEEPSEEK_OCR_API_KEY=") for l in new_lines):
        new_lines.append(f"DEEPSEEK_OCR_API_KEY={deepseek_ocr_api_key}\n")
    if deepseek_ocr_base_url_set and not ocr_base_url_found:
        new_lines.append(f"DEEPSEEK_OCR_BASE_URL={deepseek_ocr_base_url}\n")
    if deepseek_ocr_model_set and not ocr_model_found:
        new_lines.append(f"DEEPSEEK_OCR_MODEL={deepseek_ocr_model}\n")
    if deepseek_ocr_timeout_set and not ocr_timeout_found:
        new_lines.append(f"DEEPSEEK_OCR_TIMEOUT={deepseek_ocr_timeout}\n")

    if not openai_key_found and openai_api_key:
        new_lines.append(f"OPENAI_API_KEY={openai_api_key}\n")
    if not openai_base_url_found and openai_base_url_set:
        new_lines.append(f"OPENAI_BASE_URL={openai_base_url}\n")
    if not deepseek_base_url_found and deepseek_base_url_set:
        new_lines.append(f"DEEPSEEK_BASE_URL={deepseek_base_url}\n")

    if not provider_found and ai_provider_set and ai_provider:
        new_lines.append(f"AI_PROVIDER={ai_provider}\n")

    if not model_found and ai_model_set and ai_model:
        new_lines.append(f"AI_MODEL={ai_model}\n")
        
    if not steps_found and max_steps_set and config.max_steps:
        new_lines.append(f"MAX_STEPS={config.max_steps}\n")
        
    if not proxy_found and proxy_url_set:
        new_lines.append(f"PROXY_URL={proxy_url}\n")
        
    if not lang_found and language:
        new_lines.append(f"LANGUAGE={language}\n")

    if not iface_found and ai_bind_interface:
        new_lines.append(f"AI_BIND_INTERFACE={ai_bind_interface}\n")
        
    if not lhost_found and ai_lhost_set:
        new_lines.append(f"AI_LHOST={ai_lhost}\n")
    if not tool_workdir_found and tool_workdir_mode_set:
        new_lines.append(f"TOOL_WORKDIR_MODE={tool_workdir_mode}\n")
    if not tool_max_output_found and tool_max_output_chars_set:
        new_lines.append(f"TOOL_MAX_OUTPUT_CHARS={tool_max_output_chars_val}\n")
    if not tool_sandbox_found and tool_sandbox_set:
        new_lines.append(f"TOOL_SANDBOX={tool_sandbox}\n")
    if not tool_docker_image_found and tool_docker_image_set:
        new_lines.append(f"TOOL_DOCKER_IMAGE={tool_docker_image}\n")
    if not tool_docker_network_found and tool_docker_network_set:
        new_lines.append(f"TOOL_DOCKER_NETWORK={tool_docker_network}\n")
    if not tool_docker_memory_found and tool_docker_memory_set:
        new_lines.append(f"TOOL_DOCKER_MEMORY={tool_docker_memory}\n")
    if not tool_docker_pids_found and tool_docker_pids_limit_set:
        new_lines.append(f"TOOL_DOCKER_PIDS_LIMIT={tool_docker_pids_limit}\n")

    if not audit_log_max_rows_found and audit_log_max_rows_set and audit_log_max_rows_val is not None:
        new_lines.append(f"AUDIT_LOG_MAX_ROWS={audit_log_max_rows_val}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
    return {"status": "success", "message": "Configuration updated"}

@app.get("/api/reports")
def list_reports():
    report_dir = os.path.join(BASE_DIR, "data", "reports")
    if not os.path.exists(report_dir):
        return {"reports": []}
    reports = []
    for f in os.listdir(report_dir):
        if f.endswith(".md") or f.endswith(".txt") or f.endswith(".html") or f.endswith(".pdf"):
            reports.append(f)
    return {"reports": reports}

def _sanitize_report_base(name: str) -> str:
    s = (name or "").strip()
    s = os.path.basename(s)
    for ext in (".md", ".txt", ".html", ".pdf"):
        if s.lower().endswith(ext):
            s = s[: -len(ext)]
            break
    s = "".join(x for x in s if x.isalnum() or x in " ._-")
    s = s.strip().strip(".")
    return s

def _report_paths(report_dir: str, base: str) -> Dict[str, str]:
    return {
        "md": os.path.join(report_dir, f"{base}.md"),
        "txt": os.path.join(report_dir, f"{base}.txt"),
        "html": os.path.join(report_dir, f"{base}.html"),
        "pdf": os.path.join(report_dir, f"{base}.pdf"),
    }

def _find_headless_browser() -> Optional[str]:
    candidates = [
        "chromium",
        "chromium-browser",
        "google-chrome",
        "google-chrome-stable",
        "chrome",
        "msedge",
        "microsoft-edge",
        "MicrosoftEdge",
    ]
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p
    return None

def _ensure_report_html(report_dir: str, base: str) -> str:
    paths = _report_paths(report_dir, base)
    if os.path.exists(paths["html"]):
        return paths["html"]
    src_path = paths["md"] if os.path.exists(paths["md"]) else (paths["txt"] if os.path.exists(paths["txt"]) else "")
    if not src_path:
        raise FileNotFoundError("report_source_not_found")
    with open(src_path, "r", encoding="utf-8", errors="replace") as f:
        md_text = f.read()
    html = render_report_html(base_dir=BASE_DIR, markdown_text=md_text, filename=os.path.basename(src_path), target="")
    with open(paths["html"], "w", encoding="utf-8") as f:
        f.write(html)
    return paths["html"]

def _ensure_report_pdf(report_dir: str, base: str, base_url: str) -> str:
    paths = _report_paths(report_dir, base)
    if os.path.exists(paths["pdf"]):
        return paths["pdf"]

    _ensure_report_html(report_dir, base)

    browser = _find_headless_browser()
    if not browser:
        raise RuntimeError("no_headless_browser")

    url = f"{base_url.rstrip('/')}/files/reports/{base}.html"
    args = [
        browser,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={paths['pdf']}",
        "--print-to-pdf-no-header",
        url,
    ]
    p = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        raise RuntimeError("pdf_generation_failed")
    if not os.path.exists(paths["pdf"]):
        raise RuntimeError("pdf_generation_failed")
    return paths["pdf"]

@app.get("/api/reports/download")
def download_report(request: Request, name: str, format: str = "md"):
    report_dir = os.path.join(BASE_DIR, "data", "reports")
    os.makedirs(report_dir, exist_ok=True)

    base = _sanitize_report_base(name)
    if not base:
        return JSONResponse(status_code=400, content={"error": "invalid_name"})

    fmt = (format or "").lower().strip()
    if fmt not in {"md", "html", "pdf"}:
        return JSONResponse(status_code=400, content={"error": "invalid_format"})

    paths = _report_paths(report_dir, base)

    if fmt == "md":
        src = paths["md"] if os.path.exists(paths["md"]) else (paths["txt"] if os.path.exists(paths["txt"]) else "")
        if not src:
            return JSONResponse(status_code=404, content={"error": "not_found"})
        return FileResponse(src, media_type="text/markdown; charset=utf-8", filename=os.path.basename(src))

    if fmt == "html":
        try:
            html_path = _ensure_report_html(report_dir, base)
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"error": "not_found"})
        return FileResponse(html_path, media_type="text/html; charset=utf-8", filename=f"{base}.html")

    try:
        base_url = str(request.base_url)
        pdf_path = _ensure_report_pdf(report_dir, base, base_url=base_url)
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"{base}.pdf")
    except RuntimeError as e:
        return JSONResponse(status_code=501, content={"error": str(e)})

def _sanitize_report_filename(filename: str) -> str:
    s = (filename or "").strip()
    if not s:
        return ""
    if ".." in s or "/" in s or "\\" in s:
        return ""
    s = os.path.basename(s)
    if not s:
        return ""
    ext = os.path.splitext(s)[1].lower()
    if ext not in {".md", ".txt", ".html", ".pdf"}:
        return ""
    return s

@app.get("/api/reports/{filename}")
def get_report(filename: str):
    report_dir = os.path.join(BASE_DIR, "data", "reports")
    safe = _sanitize_report_filename(filename)
    if not safe:
        return JSONResponse(status_code=400, content={"error": "Invalid filename"})
    file_path = os.path.realpath(os.path.join(report_dir, safe))
    if not file_path.startswith(os.path.realpath(report_dir) + os.sep):
        return JSONResponse(status_code=400, content={"error": "Invalid filename"})
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    if safe.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "binary_report_not_supported"})
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return {"content": f.read()}

@app.delete("/api/reports/{filename}")
def delete_report(filename: str):
    report_dir = os.path.join(BASE_DIR, "data", "reports")
    safe = _sanitize_report_filename(filename)
    if not safe:
        return JSONResponse(status_code=400, content={"error": "Invalid filename"})
    file_path = os.path.realpath(os.path.join(report_dir, safe))
    if not file_path.startswith(os.path.realpath(report_dir) + os.sep):
        return JSONResponse(status_code=400, content={"error": "Invalid filename"})
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return {"status": "success", "message": f"Deleted {safe}"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
    return JSONResponse(status_code=404, content={"error": "File not found"})


@app.get("/api/skills")
def list_skills():
    skills_dir = os.path.join(BASE_DIR, "data", "skills")
    if not os.path.exists(skills_dir):
        return {"skills": []}
    skills = []
    for f in os.listdir(skills_dir):
        if f.endswith(".md") or f.endswith(".txt") or f.endswith(".yaml"):
            # Try to read content to get description if possible, or just return filename
            skills.append({"name": f, "path": f})
    return {"skills": skills}

@app.get("/api/knowledge")
def list_knowledge():
    kb_dir = os.path.join(BASE_DIR, "data", "knowledge")
    if not os.path.exists(kb_dir):
        return {"knowledge": []}
    items = []
    for f in os.listdir(kb_dir):
        if f.endswith(".md") or f.endswith(".txt") or f.endswith(".pdf"):
            items.append({"name": f, "path": f})
    return {"knowledge": items}

@app.get("/api/vulndb")
def list_vulndb():
    db_dir = os.path.join(BASE_DIR, "data", "vulndb")
    if not os.path.exists(db_dir):
        return {"vulndb": []}
    items = []
    for f in os.listdir(db_dir):
        if f.endswith(".md") or f.endswith(".txt"):
            items.append({"name": f, "path": f})
    items.sort(key=lambda x: x["name"])
    return {"vulndb": items}

@app.get("/api/vulnerabilities")
def list_vulnerabilities(query: str = None):
    # Try to use searchsploit if query provided
    if query:
        import subprocess
        try:
            # -j for JSON output
            # We assume searchsploit is in PATH
            result = subprocess.run(
                ["searchsploit", "-j", query], 
                capture_output=True, 
                text=True, 
                encoding='utf-8' # Force utf-8
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                # data format: {'RESULTS_EXPLOIT': [...], 'RESULTS_SHELLCODE': [...]}
                exploits = data.get('RESULTS_EXPLOIT', [])
                # Normalize keys to match our frontend expectation
                # Frontend expects: Title, EDB-ID, Type, Platform
                return {"vulnerabilities": exploits}
            else:
                # If searchsploit fails (e.g. command not found or error)
                return {"vulnerabilities": [], "error": f"Searchsploit execution failed: {result.stderr or 'Command not found'}"}
                
        except FileNotFoundError:
             return {"vulnerabilities": [], "error": "Searchsploit tool not found in system PATH"}
        except Exception as e:
            return {"vulnerabilities": [], "error": str(e)}

    # If no query, return empty list or instruction
    return {"vulnerabilities": [], "message": "Please provide a search query"}


@app.get("/api/vulnerabilities/stats")
def vulnerabilities_stats():
    now = time.time()
    cached = _EXPLOITDB_STATS_CACHE.get("data")
    ts = float(_EXPLOITDB_STATS_CACHE.get("ts") or 0.0)
    if cached and (now - ts) < 3600:
        return cached

    data = _compute_exploitdb_total()
    _EXPLOITDB_STATS_CACHE["ts"] = now
    _EXPLOITDB_STATS_CACHE["data"] = data
    return data

# Mount data directory for accessing reports and images
DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
LOOT_DIR = os.path.join(DATA_DIR, "loot")
if not os.path.exists(LOOT_DIR):
    os.makedirs(LOOT_DIR)
# Mount /files AFTER / so it doesn't get swallowed by static mount?
# No, order matters. If we mount / last, it catches everything.
# But here / is mounted to WEB_PATH.
# Let's ensure /files is mounted BEFORE /.
# FastAPI checks routes in order.
# Actually, explicit routes are checked first, then mounts.
# If multiple mounts match, the first one might take precedence if paths overlap.
# But /files is more specific than /.

app.mount("/files", StaticFiles(directory=DATA_DIR), name="files")
app.mount("/", StaticFiles(directory=WEB_PATH, html=True), name="static")

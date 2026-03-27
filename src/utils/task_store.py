import json
import os
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional


class TaskStore:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        db_dir = os.path.join(base_dir, "data", "state")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, "tasks.db")
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        task_id TEXT PRIMARY KEY,
                        goal TEXT,
                        status TEXT,
                        created_at REAL,
                        updated_at REAL,
                        finished_at REAL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id TEXT,
                        ts REAL,
                        event_json TEXT
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_events_task_ts ON events(task_id, ts);")
                conn.commit()
            finally:
                conn.close()

    def upsert_task(self, task_id: str, goal: str, status: str):
        now = time.time()
        with self._lock:
            conn = self._connect()
            try:
                existing = conn.execute(
                    "SELECT task_id FROM tasks WHERE task_id = ?",
                    (task_id,),
                ).fetchone()
                if existing:
                    conn.execute(
                        "UPDATE tasks SET goal = COALESCE(?, goal), status = ?, updated_at = ? WHERE task_id = ?",
                        (goal, status, now, task_id),
                    )
                else:
                    conn.execute(
                        "INSERT INTO tasks(task_id, goal, status, created_at, updated_at, finished_at) VALUES(?,?,?,?,?,NULL)",
                        (task_id, goal, status, now, now),
                    )
                conn.commit()
            finally:
                conn.close()

    def mark_finished(self, task_id: str, status: str = "finished"):
        now = time.time()
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    "UPDATE tasks SET status = ?, updated_at = ?, finished_at = ? WHERE task_id = ?",
                    (status, now, now, task_id),
                )
                conn.commit()
            finally:
                conn.close()

    def delete_task(self, task_id: str, delete_events: bool = True) -> bool:
        task_id = (task_id or "").strip()
        if not task_id:
            return False
        with self._lock:
            conn = self._connect()
            try:
                if delete_events:
                    conn.execute("DELETE FROM events WHERE task_id = ?", (task_id,))
                cur = conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
                conn.commit()
                return bool(cur.rowcount)
            finally:
                conn.close()

    def append_event(self, task_id: str, event: Dict[str, Any]):
        ts = time.time()
        payload = json.dumps(event, ensure_ascii=False)
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    "INSERT INTO events(task_id, ts, event_json) VALUES(?,?,?)",
                    (task_id, ts, payload),
                )
                conn.execute(
                    "UPDATE tasks SET updated_at = ? WHERE task_id = ?",
                    (ts, task_id),
                )
                conn.commit()
            finally:
                conn.close()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT task_id, goal, status, created_at, updated_at, finished_at FROM tasks WHERE task_id = ?",
                    (task_id,),
                ).fetchone()
                if not row:
                    return None
                return {
                    "task_id": row[0],
                    "goal": row[1],
                    "status": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                    "finished_at": row[5],
                }
            finally:
                conn.close()

    def list_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT task_id, goal, status, created_at, updated_at, finished_at FROM tasks ORDER BY updated_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
                return [
                    {
                        "task_id": r[0],
                        "goal": r[1],
                        "status": r[2],
                        "created_at": r[3],
                        "updated_at": r[4],
                        "finished_at": r[5],
                    }
                    for r in rows
                ]
            finally:
                conn.close()

    def load_events(self, task_id: str, limit: int = 2000) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 10000))
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT event_json FROM events WHERE task_id = ? ORDER BY ts ASC LIMIT ?",
                    (task_id, limit),
                ).fetchall()
                events: List[Dict[str, Any]] = []
                for (event_json,) in rows:
                    try:
                        events.append(json.loads(event_json))
                    except Exception:
                        continue
                return events
            finally:
                conn.close()

    def load_events_with_meta(self, task_id: str, limit: int = 2000, since_id: int = 0) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 20000))
        try:
            since_id = int(since_id or 0)
        except Exception:
            since_id = 0
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT id, ts, event_json FROM events WHERE task_id = ? AND id > ? ORDER BY id ASC LIMIT ?",
                    (task_id, since_id, limit),
                ).fetchall()
                out: List[Dict[str, Any]] = []
                for rid, ts, event_json in rows:
                    try:
                        ev = json.loads(event_json)
                    except Exception:
                        continue
                    out.append({"id": rid, "ts": ts, "event": ev})
                return out
            finally:
                conn.close()

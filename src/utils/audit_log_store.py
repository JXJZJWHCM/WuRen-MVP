import json
import os
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional


class AuditLogStore:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        db_dir = os.path.join(base_dir, "data", "state")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, "audit_logs.db")
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
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts REAL,
                        actor_ip TEXT,
                        user_agent TEXT,
                        method TEXT,
                        path TEXT,
                        query TEXT,
                        status_code INTEGER,
                        duration_ms INTEGER,
                        action TEXT,
                        detail_json TEXT
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_logs(ts);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_path ON audit_logs(path);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);")
                conn.commit()
            finally:
                conn.close()

    def count(self) -> int:
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute("SELECT COUNT(1) FROM audit_logs").fetchone()
                return int(row[0] or 0) if row else 0
            finally:
                conn.close()

    def prune_keep_latest(self, max_rows: int) -> int:
        try:
            max_rows = int(max_rows)
        except Exception:
            return 0
        if max_rows <= 0:
            return 0
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute(
                    "DELETE FROM audit_logs WHERE id NOT IN (SELECT id FROM audit_logs ORDER BY id DESC LIMIT ?)",
                    (max_rows,),
                )
                conn.commit()
                return int(cur.rowcount or 0)
            finally:
                conn.close()

    def append(
        self,
        *,
        actor_ip: str = "",
        user_agent: str = "",
        method: str = "",
        path: str = "",
        query: str = "",
        status_code: int | None = None,
        duration_ms: int | None = None,
        action: str = "",
        detail: Optional[Dict[str, Any]] = None,
        max_rows: int = 10000,
    ) -> int:
        ts = time.time()
        try:
            status_code_int = int(status_code) if status_code is not None else None
        except Exception:
            status_code_int = None
        try:
            duration_ms_int = int(duration_ms) if duration_ms is not None else None
        except Exception:
            duration_ms_int = None
        detail_json = json.dumps(detail or {}, ensure_ascii=False)

        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute(
                    """
                    INSERT INTO audit_logs(ts, actor_ip, user_agent, method, path, query, status_code, duration_ms, action, detail_json)
                    VALUES(?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        ts,
                        (actor_ip or "")[:128],
                        (user_agent or "")[:512],
                        (method or "")[:16],
                        (path or "")[:512],
                        (query or "")[:2048],
                        status_code_int,
                        duration_ms_int,
                        (action or "")[:128],
                        detail_json,
                    ),
                )
                conn.commit()
                last_id = int(cur.lastrowid or 0)
            finally:
                conn.close()

        self.prune_keep_latest(max_rows)
        return last_id

    def list_logs(
        self,
        *,
        limit: int = 200,
        offset: int = 0,
        q: str = "",
        method: str = "",
        path: str = "",
        action: str = "",
        kind: str = "",
        status_code: int | None = None,
        since_id: int = 0,
    ) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 2000))
        offset = max(0, int(offset))
        since_id = max(0, int(since_id))

        where = ["id > ?"]
        params: List[Any] = [since_id]

        kind_norm = (kind or "").strip().lower()
        if kind_norm in {"ui", "user", "ui_event"}:
            where.append("action = ?")
            params.append("ui_event")
        elif kind_norm in {"platform", "system", "op"}:
            where.append("action != ?")
            params.append("ui_event")
            where.append("action NOT LIKE ?")
            params.append("GET %")
            where.append("action NOT LIKE ?")
            params.append("POST %")
            where.append("action NOT LIKE ?")
            params.append("PUT %")
            where.append("action NOT LIKE ?")
            params.append("DELETE %")
        elif kind_norm in {"request", "http"}:
            where.append("(action LIKE ? OR action LIKE ? OR action LIKE ? OR action LIKE ?)")
            params.extend(["GET %", "POST %", "PUT %", "DELETE %"])
        elif kind_norm in {"ops", "operations"}:
            where.append(
                "("
                "action = ? OR "
                "("
                "action != ? AND action NOT LIKE ? AND action NOT LIKE ? AND action NOT LIKE ? AND action NOT LIKE ?"
                ")"
                ")"
            )
            params.extend(["ui_event", "ui_event", "GET %", "POST %", "PUT %", "DELETE %"])

        if method:
            where.append("method = ?")
            params.append(method.upper())
        if path:
            where.append("path LIKE ?")
            params.append(f"%{path}%")
        if action:
            where.append("action LIKE ?")
            params.append(f"%{action}%")
        if status_code is not None:
            try:
                where.append("status_code = ?")
                params.append(int(status_code))
            except Exception:
                pass
        if q:
            where.append("(path LIKE ? OR action LIKE ? OR detail_json LIKE ? OR query LIKE ?)")
            params.extend([f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"])

        sql = (
            "SELECT id, ts, actor_ip, user_agent, method, path, query, status_code, duration_ms, action, detail_json "
            f"FROM audit_logs WHERE {' AND '.join(where)} "
            "ORDER BY id DESC LIMIT ? OFFSET ?"
        )
        params.extend([limit, offset])

        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(sql, tuple(params)).fetchall()
            finally:
                conn.close()

        out: List[Dict[str, Any]] = []
        for r in rows:
            try:
                detail = json.loads(r[10] or "{}")
            except Exception:
                detail = {}
            out.append(
                {
                    "id": int(r[0]),
                    "ts": float(r[1] or 0),
                    "actor_ip": r[2] or "",
                    "user_agent": r[3] or "",
                    "method": r[4] or "",
                    "path": r[5] or "",
                    "query": r[6] or "",
                    "status_code": r[7],
                    "duration_ms": r[8],
                    "action": r[9] or "",
                    "detail": detail,
                }
            )
        return out

    def clear_all(self) -> int:
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute("DELETE FROM audit_logs")
                conn.commit()
                return int(cur.rowcount or 0)
            finally:
                conn.close()

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute("SELECT COUNT(1), MIN(ts), MAX(ts), MAX(id) FROM audit_logs").fetchone()
            finally:
                conn.close()
        total = int(row[0] or 0) if row else 0
        return {
            "total": total,
            "oldest_ts": float(row[1] or 0) if row else 0,
            "newest_ts": float(row[2] or 0) if row else 0,
            "max_id": int(row[3] or 0) if row else 0,
        }

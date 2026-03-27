import json
import os
import sqlite3
import threading
import time
import uuid
from typing import Any, Dict, List, Optional


class VulnStore:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        db_dir = os.path.join(base_dir, "data", "state")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, "vulns.db")
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
                    CREATE TABLE IF NOT EXISTS vulns (
                        vuln_id TEXT PRIMARY KEY,
                        task_id TEXT,
                        target TEXT,
                        title TEXT,
                        severity TEXT,
                        cvss REAL,
                        status TEXT,
                        details_json TEXT,
                        created_at REAL,
                        updated_at REAL
                    )
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_vulns_task ON vulns(task_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_vulns_updated ON vulns(updated_at);")
                conn.commit()
            finally:
                conn.close()

    def upsert(self, vuln: Dict[str, Any]) -> Dict[str, Any]:
        now = time.time()
        v = dict(vuln or {})
        vuln_id = (v.get("vuln_id") or "").strip() or str(uuid.uuid4())
        task_id = (v.get("task_id") or "").strip()
        target = (v.get("target") or "").strip()
        title = (v.get("title") or "").strip()
        severity = (v.get("severity") or "").strip()
        status = (v.get("status") or "").strip() or "open"
        cvss = v.get("cvss")
        try:
            cvss_val = float(cvss) if cvss is not None and str(cvss).strip() != "" else None
        except Exception:
            cvss_val = None

        details = v.get("details") if isinstance(v.get("details"), dict) else {}
        details_json = json.dumps(details, ensure_ascii=False)

        with self._lock:
            conn = self._connect()
            try:
                existing = conn.execute("SELECT vuln_id FROM vulns WHERE vuln_id = ?", (vuln_id,)).fetchone()
                if existing:
                    conn.execute(
                        """
                        UPDATE vulns
                        SET task_id=?, target=?, title=?, severity=?, cvss=?, status=?, details_json=?, updated_at=?
                        WHERE vuln_id=?
                        """,
                        (task_id, target, title, severity, cvss_val, status, details_json, now, vuln_id),
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO vulns(vuln_id, task_id, target, title, severity, cvss, status, details_json, created_at, updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?)
                        """,
                        (vuln_id, task_id, target, title, severity, cvss_val, status, details_json, now, now),
                    )
                conn.commit()
            finally:
                conn.close()

        v["vuln_id"] = vuln_id
        v["task_id"] = task_id
        v["target"] = target
        v["title"] = title
        v["severity"] = severity
        v["cvss"] = cvss_val
        v["status"] = status
        v["details"] = details
        v["updated_at"] = now
        return v

    def get(self, vuln_id: str) -> Optional[Dict[str, Any]]:
        vuln_id = (vuln_id or "").strip()
        if not vuln_id:
            return None
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    """
                    SELECT vuln_id, task_id, target, title, severity, cvss, status, details_json, created_at, updated_at
                    FROM vulns WHERE vuln_id = ?
                    """,
                    (vuln_id,),
                ).fetchone()
                if not row:
                    return None
                details = {}
                try:
                    details = json.loads(row[7] or "{}")
                except Exception:
                    details = {}
                return {
                    "vuln_id": row[0],
                    "task_id": row[1],
                    "target": row[2],
                    "title": row[3],
                    "severity": row[4],
                    "cvss": row[5],
                    "status": row[6],
                    "details": details,
                    "created_at": row[8],
                    "updated_at": row[9],
                }
            finally:
                conn.close()

    def list(self, task_id: str | None = None, limit: int = 200) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 2000))
        with self._lock:
            conn = self._connect()
            try:
                if task_id:
                    rows = conn.execute(
                        """
                        SELECT vuln_id, task_id, target, title, severity, cvss, status, details_json, created_at, updated_at
                        FROM vulns WHERE task_id = ? ORDER BY updated_at DESC LIMIT ?
                        """,
                        (task_id, limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """
                        SELECT vuln_id, task_id, target, title, severity, cvss, status, details_json, created_at, updated_at
                        FROM vulns ORDER BY updated_at DESC LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()
                out: List[Dict[str, Any]] = []
                for r in rows:
                    details = {}
                    try:
                        details = json.loads(r[7] or "{}")
                    except Exception:
                        details = {}
                    out.append(
                        {
                            "vuln_id": r[0],
                            "task_id": r[1],
                            "target": r[2],
                            "title": r[3],
                            "severity": r[4],
                            "cvss": r[5],
                            "status": r[6],
                            "details": details,
                            "created_at": r[8],
                            "updated_at": r[9],
                        }
                    )
                return out
            finally:
                conn.close()

    def delete(self, vuln_id: str) -> bool:
        vuln_id = (vuln_id or "").strip()
        if not vuln_id:
            return False
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute("DELETE FROM vulns WHERE vuln_id = ?", (vuln_id,))
                conn.commit()
                return cur.rowcount > 0
            finally:
                conn.close()

    def delete_by_task(self, task_id: str) -> int:
        task_id = (task_id or "").strip()
        if not task_id:
            return 0
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute("DELETE FROM vulns WHERE task_id = ?", (task_id,))
                conn.commit()
                return int(cur.rowcount or 0)
            finally:
                conn.close()

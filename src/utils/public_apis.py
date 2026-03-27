import re
from typing import Any, Dict, Optional

import httpx


_IP_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?:\.(?!-)[A-Za-z0-9-]{1,63})+$")


def _is_ip(value: str) -> bool:
    if not value or not _IP_RE.match(value):
        return False
    parts = value.split(".")
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except Exception:
        return False


def _is_domain(value: str) -> bool:
    return bool(value) and bool(_DOMAIN_RE.match(value))


def ipinfo_lookup(query: str, timeout_s: float = 15.0) -> Dict[str, Any]:
    query = (query or "").strip()
    if query and not (_is_ip(query) or _is_domain(query)):
        return {"ok": False, "error": "invalid_query", "message": "query 必须是 IPv4 或域名"}

    url = "https://ipinfo.io/json" if not query else f"https://ipinfo.io/{query}/json"
    try:
        r = httpx.get(url, timeout=timeout_s, headers={"User-Agent": "雾刃渗透测试系统1.0/1.0"})
        r.raise_for_status()
        data = r.json()
        return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "error": "request_failed", "message": str(e)}


def shodan_internetdb_lookup(ip: str, timeout_s: float = 15.0) -> Dict[str, Any]:
    ip = (ip or "").strip()
    if not _is_ip(ip):
        return {"ok": False, "error": "invalid_ip", "message": "ip 必须是 IPv4"}

    url = f"https://internetdb.shodan.io/{ip}"
    try:
        r = httpx.get(url, timeout=timeout_s, headers={"User-Agent": "雾刃渗透测试系统1.0/1.0"})
        r.raise_for_status()
        data = r.json()
        return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "error": "request_failed", "message": str(e)}


def urlhaus_lookup(kind: str, indicator: str, timeout_s: float = 20.0) -> Dict[str, Any]:
    kind = (kind or "").strip().lower()
    indicator = (indicator or "").strip()

    if kind not in ("host", "url"):
        return {"ok": False, "error": "invalid_kind", "message": "kind 必须为 host 或 url"}
    if not indicator:
        return {"ok": False, "error": "empty_indicator", "message": "indicator 不能为空"}

    endpoint = "host" if kind == "host" else "url"
    url = f"https://urlhaus-api.abuse.ch/v1/{endpoint}/"
    payload: Dict[str, str] = {"host" if kind == "host" else "url": indicator}

    try:
        r = httpx.post(url, data=payload, timeout=timeout_s, headers={"User-Agent": "雾刃渗透测试系统1.0/1.0"})
        r.raise_for_status()
        data = r.json()
        return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "error": "request_failed", "message": str(e)}

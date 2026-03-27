import re
from typing import List


_TTP_RE = re.compile(r"\bT\d{4}(?:\.\d{3})?\b", re.IGNORECASE)
_CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)


def extract_ttps(text: str) -> List[str]:
    if not text:
        return []
    seen = set()
    out: List[str] = []
    for m in _TTP_RE.finditer(text):
        v = m.group(0).upper()
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out[:50]


def extract_cves(text: str) -> List[str]:
    if not text:
        return []
    seen = set()
    out: List[str] = []
    for m in _CVE_RE.finditer(text):
        v = m.group(0).upper()
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out[:50]

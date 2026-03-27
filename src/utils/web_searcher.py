import httpx
from bs4 import BeautifulSoup
import urllib.parse
import logging
import os
import time
import ipaddress
import socket
from typing import Dict, List, Optional, Tuple
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

logger = logging.getLogger(__name__)

class WebSearcher:
    _SEARCH_CACHE: Dict[Tuple[str, int, str, str], Tuple[float, List[Dict]]] = {}
    _FETCH_CACHE: Dict[str, Tuple[float, Dict]] = {}

    @staticmethod
    def _resolve_proxy_url() -> str:
        proxy_url = (os.getenv("PROXY_URL") or "").strip()
        if proxy_url:
            return proxy_url
        return ""

    @staticmethod
    def _http_client(timeout: float, proxy_url: str = "", follow_redirects: bool = True) -> httpx.Client:
        kwargs = {"timeout": timeout, "follow_redirects": follow_redirects, "trust_env": True}
        if proxy_url:
            kwargs["proxy"] = proxy_url
        return httpx.Client(**kwargs)

    @staticmethod
    def _is_probably_blocked_html(html: str) -> bool:
        t = (html or "").lower()
        needles = [
            "unusual traffic",
            "verify you are a human",
            "captcha",
            "our systems have detected",
            "检测到异常流量",
            "验证您是否为人类",
            "请输入验证码",
        ]
        return any(n in t for n in needles)

    @staticmethod
    def _now() -> float:
        return time.time()

    @staticmethod
    def _cache_get_search(key: Tuple[str, int, str, str], ttl_seconds: int) -> Optional[List[Dict]]:
        item = WebSearcher._SEARCH_CACHE.get(key)
        if not item:
            return None
        ts, val = item
        if WebSearcher._now() - ts > ttl_seconds:
            WebSearcher._SEARCH_CACHE.pop(key, None)
            return None
        return val

    @staticmethod
    def _cache_set_search(key: Tuple[str, int, str, str], val: List[Dict]) -> None:
        if len(WebSearcher._SEARCH_CACHE) > 256:
            WebSearcher._SEARCH_CACHE.clear()
        WebSearcher._SEARCH_CACHE[key] = (WebSearcher._now(), val)

    @staticmethod
    def _cache_get_fetch(url: str, ttl_seconds: int) -> Optional[Dict]:
        item = WebSearcher._FETCH_CACHE.get(url)
        if not item:
            return None
        ts, val = item
        if WebSearcher._now() - ts > ttl_seconds:
            WebSearcher._FETCH_CACHE.pop(url, None)
            return None
        return val

    @staticmethod
    def _cache_set_fetch(url: str, val: Dict) -> None:
        if len(WebSearcher._FETCH_CACHE) > 128:
            WebSearcher._FETCH_CACHE.clear()
        WebSearcher._FETCH_CACHE[url] = (WebSearcher._now(), val)

    @staticmethod
    def _is_private_host(hostname: str) -> bool:
        if not hostname:
            return True
        h = hostname.strip().lower()
        if h in {"localhost", "localhost.localdomain"}:
            return True
        if h.endswith(".local"):
            return True
        try:
            ip = ipaddress.ip_address(h)
            return bool(
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
            )
        except Exception:
            return False

    @staticmethod
    def _dns_resolves_to_private(hostname: str) -> bool:
        h = (hostname or "").strip().lower()
        if not h:
            return True
        try:
            ip = ipaddress.ip_address(h)
            return WebSearcher._is_private_host(str(ip))
        except Exception:
            pass

        try:
            infos = socket.getaddrinfo(h, None, proto=socket.IPPROTO_TCP)
        except Exception:
            raise ValueError("dns_resolution_failed")

        if not infos:
            raise ValueError("dns_resolution_failed")

        for info in infos:
            sockaddr = info[4]
            ip_str = sockaddr[0] if isinstance(sockaddr, tuple) and sockaddr else ""
            try:
                ip = ipaddress.ip_address(ip_str)
            except Exception:
                continue
            if WebSearcher._is_private_host(str(ip)):
                return True
        return False

    @staticmethod
    def _sanitize_url(url: str) -> str:
        u = (url or "").strip()
        if not u:
            raise ValueError("empty_url")
        parsed = urllib.parse.urlparse(u)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("invalid_scheme")
        host = parsed.hostname or ""
        if WebSearcher._is_private_host(host):
            raise ValueError("private_host_not_allowed")
        if WebSearcher._dns_resolves_to_private(host):
            raise ValueError("private_host_not_allowed")
        return u

    @staticmethod
    def _dedupe_results(results: List[Dict]) -> List[Dict]:
        seen = set()
        out = []
        for r in results or []:
            if not isinstance(r, dict):
                continue
            href = (r.get("href") or "").strip()
            title = (r.get("title") or "").strip()
            if not href or not title:
                continue
            key = href.split("#", 1)[0].rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
        return out

    @staticmethod
    def _extract_readable_text(html: str) -> Dict[str, str]:
        soup = BeautifulSoup(html or "", "html.parser")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        for tag in soup(["header", "footer", "nav", "aside", "form"]):
            try:
                tag.decompose()
            except Exception:
                pass

        title = ""
        if soup.title and soup.title.get_text(strip=True):
            title = soup.title.get_text(strip=True)

        container = soup.find("main") or soup.find("article") or soup.body or soup
        text = container.get_text("\n", strip=True) if container else ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        text = "\n".join(lines)
        return {"title": title, "text": text}

    @staticmethod
    def search_bing(query, max_results=5):
        """
        Perform a search using Bing (mimicking Edge browser).
        Useful when DuckDuckGo is blocked.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
        }
        url = f"https://cn.bing.com/search?q={urllib.parse.quote(query)}"
        
        logger.info(f"Searching Bing: {url}")
        proxy_url = WebSearcher._resolve_proxy_url()
        try:
            last_err = None
            for attempt in range(3):
                try:
                    with WebSearcher._http_client(timeout=20.0, proxy_url=proxy_url, follow_redirects=True) as client:
                        response = client.get(url, headers=headers)
                    if response.status_code != 200:
                        last_err = f"http_status_{response.status_code}"
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    if WebSearcher._is_probably_blocked_html(response.text):
                        last_err = "blocked_or_captcha"
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    break
                except Exception as e:
                    last_err = str(e)
                    time.sleep(0.5 * (attempt + 1))
                    continue
            else:
                logger.error(f"Bing search failed after retries: {last_err}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Bing standard result container
            # Look for <li class="b_algo">
            for item in soup.find_all('li', class_='b_algo', limit=max_results):
                try:
                    title_tag = item.find('h2')
                    link_tag = item.find('a')
                    
                    if not title_tag or not link_tag:
                        continue
                        
                    title = title_tag.get_text(strip=True)
                    href = link_tag.get('href')
                    
                    # Extract snippet
                    snippet = ""
                    # Snippet can be in .b_caption p, or .b_snippet
                    caption = item.find('div', class_='b_caption')
                    if caption:
                        p_tag = caption.find('p')
                        if p_tag:
                            snippet = p_tag.get_text(strip=True)
                    
                    if not snippet:
                        # Fallback for other layouts
                        snippet_div = item.find('div', class_='b_snippet')
                        if snippet_div:
                            snippet = snippet_div.get_text(strip=True)

                    results.append({
                        "title": title,
                        "href": href,
                        "body": snippet
                    })
                except Exception as e:
                    continue
            
            return results
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            return []

    @staticmethod
    def search_duckduckgo(query, max_results=5, proxy=None):
        if DDGS is None:
            return None
            
        try:
            ddgs = DDGS(proxy=proxy, timeout=25) if proxy else DDGS(timeout=25)
                
            # Returns a list of dicts: {'title':..., 'href':..., 'body':...}
            return list(ddgs.text(query, max_results=max_results))
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return None # Indicate failure

    @staticmethod
    def search_with_meta(query, max_results=5, preferred_engine="auto") -> Tuple[List[Dict], Dict]:
        q = (query or "").strip()
        if not q:
            return [], {"ok": False, "error": "empty_query", "attempts": []}

        proxy = WebSearcher._resolve_proxy_url()
        engine = (preferred_engine or "auto").strip().lower()
        cache_key = (q, int(max_results), engine, proxy)
        cached = WebSearcher._cache_get_search(cache_key, ttl_seconds=600)
        if cached is not None:
            return cached, {"ok": True, "cached": True, "attempts": [], "engine_used": "cache"}

        attempts = []

        def _try_bing() -> List[Dict]:
            try:
                r = WebSearcher.search_bing(q, max_results)
                attempts.append({"engine": "bing", "ok": bool(r), "error": "" if r else "no_results_or_failed"})
                return r
            except Exception as e:
                attempts.append({"engine": "bing", "ok": False, "error": str(e)})
                return []

        def _try_ddg() -> List[Dict]:
            try:
                r = WebSearcher.search_duckduckgo(q, max_results, proxy)
                if r is None:
                    attempts.append({"engine": "ddg", "ok": False, "error": "ddg_unavailable_or_failed"})
                    return []
                attempts.append({"engine": "ddg", "ok": bool(r), "error": "" if r else "no_results"})
                return r
            except Exception as e:
                attempts.append({"engine": "ddg", "ok": False, "error": str(e)})
                return []

        results: List[Dict] = []
        used = "auto"

        if engine == "bing":
            used = "bing"
            results = _try_bing()
            if not results:
                used = "ddg"
                results = _try_ddg()
        elif engine in {"duckduckgo", "ddg"}:
            used = "ddg"
            results = _try_ddg()
            if not results:
                used = "bing"
                results = _try_bing()
        else:
            if not proxy:
                used = "bing"
                results = _try_bing()
                if not results:
                    used = "ddg"
                    results = _try_ddg()
            else:
                used = "ddg"
                results = _try_ddg()
                if not results:
                    used = "bing"
                    results = _try_bing()

        results = WebSearcher._dedupe_results(results or [])
        WebSearcher._cache_set_search(cache_key, results)
        ok = bool(results)
        meta = {
            "ok": ok,
            "cached": False,
            "engine_used": used,
            "proxy_set": bool(proxy),
            "attempts": attempts,
        }
        if not ok:
            meta["error"] = "no_results_or_search_failed"
        return results, meta

    @staticmethod
    def search(query, max_results=5, preferred_engine="auto"):
        results, _meta = WebSearcher.search_with_meta(query, max_results, preferred_engine=preferred_engine)
        return results

    @staticmethod
    def fetch_url_text(url: str, max_chars: int = 20000) -> Dict:
        safe_url = WebSearcher._sanitize_url(url)
        try:
            max_chars = int(max_chars)
        except Exception:
            max_chars = 20000
        max_chars = max(500, min(max_chars, 200000))

        cached = WebSearcher._cache_get_fetch(safe_url, ttl_seconds=1800)
        if cached is not None:
            return cached

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        }

        proxy_url = WebSearcher._resolve_proxy_url()
        client_kwargs = {"timeout": 25.0, "follow_redirects": False, "trust_env": True}
        if proxy_url:
            client_kwargs["proxy"] = proxy_url
        current_url = safe_url
        max_redirects = 5
        with httpx.Client(**client_kwargs) as client:
            resp = None
            for _ in range(max_redirects + 1):
                last_err = None
                for attempt in range(3):
                    try:
                        resp = client.get(current_url, headers=headers)
                        break
                    except Exception as e:
                        last_err = str(e)
                        time.sleep(0.5 * (attempt + 1))
                        continue
                if resp is None:
                    raise RuntimeError(f"http_request_failed:{last_err or 'unknown'}")
                if resp.status_code in {301, 302, 303, 307, 308}:
                    location = resp.headers.get("location") or ""
                    if not location:
                        break
                    next_url = urllib.parse.urljoin(current_url, location)
                    current_url = WebSearcher._sanitize_url(next_url)
                    continue
                break
            if resp is None:
                raise RuntimeError("http_no_response")

        content_type = (resp.headers.get("content-type") or "").lower()
        final_url = WebSearcher._sanitize_url(str(resp.url))
        if resp.status_code < 200 or resp.status_code >= 300:
            raise RuntimeError(f"http_status_{resp.status_code}")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            raise RuntimeError("unsupported_content_type")

        extracted = WebSearcher._extract_readable_text(resp.text)
        text = extracted.get("text") or ""
        truncated = False
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[内容已截断]..."
            truncated = True

        out = {
            "url": safe_url,
            "final_url": final_url,
            "status_code": resp.status_code,
            "content_type": content_type,
            "title": extracted.get("title") or "",
            "text": text,
            "truncated": truncated,
        }
        WebSearcher._cache_set_fetch(safe_url, out)
        return out

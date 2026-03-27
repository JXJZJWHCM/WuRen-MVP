import argparse
import json
import os
import re
import shlex
import socket
import ssl
import sys
import time
import urllib.parse
from typing import Dict, List, Tuple

try:
    import httpx
except ImportError:
    print("Missing dependency: httpx. Install it with `pip install httpx`.", file=sys.stderr)
    sys.exit(1)

try:
    from charset_normalizer import from_bytes as charset_from_bytes
except ImportError:
    charset_from_bytes = None

try:
    import chardet
except ImportError:
    chardet = None

METRIC_KEYS = [
    "dns_lookup",
    "tcp_connect",
    "tls_handshake",
    "pretransfer",
    "ttfb",
    "total",
    "speed_download",
    "size_download",
    "http_code",
    "redirects",
]


def parse_headers(raw: str) -> List[Tuple[str, str]]:
    if not raw:
        return []
    raw = raw.strip()
    if not raw:
        return []
    headers: List[Tuple[str, str]] = []
    parsed = None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        for key, value in parsed.items():
            headers.append((str(key).strip(), str(value).strip()))
        return headers
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, str) and ":" in item:
                key, value = item.split(":", 1)
                headers.append((key.strip(), value.strip()))
        if headers:
            return headers
    for line in raw.replace(";", "\n").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers.append((key.strip(), value.strip()))
    return headers


def parse_cookies(raw: str) -> Dict[str, str]:
    cookies: Dict[str, str] = {}
    if not raw:
        return cookies
    for part in raw.split(";"):
        if "=" not in part:
            continue
        name, value = part.split("=", 1)
        name = name.strip()
        if not name:
            continue
        cookies[name] = value.strip()
    return cookies


def parse_additional_options(raw: str) -> Dict[str, str]:
    options: Dict[str, str] = {}
    if not raw:
        return options
    try:
        tokens = shlex.split(raw)
    except ValueError:
        tokens = raw.split()
    for token in tokens:
        if "=" in token:
            key, value = token.split("=", 1)
            options[key.strip()] = value.strip()
        else:
            options[token.strip()] = "true"
    return options


def str_to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def smart_encode_url(url: str, safe_path="/:@&=%+,$-~", safe_query="/:@&=%+,$-~"):
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return url
    path = urllib.parse.quote(parts.path or "/", safe=safe_path)
    query = urllib.parse.quote(parts.query, safe=safe_query)
    fragment = urllib.parse.quote(parts.fragment, safe=safe_query)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, fragment))


def encode_form_data(data: str) -> str:
    if not data:
        return data

    def find_key_value_pairs(text):
        pairs = []
        i = 0
        text_len = len(text)

        while i < text_len:
            while i < text_len and text[i] in " \t\n\r":
                i += 1
            if i >= text_len:
                break

            key_start = i
            while i < text_len and text[i] != "=":
                i += 1

            if i >= text_len:
                remaining = text[key_start:].strip()
                if remaining:
                    pairs.append((None, remaining))
                break

            key = text[key_start:i].strip()
            i += 1

            if not key:
                continue

            value_start = i
            value_end = text_len

            j = value_start
            while j < text_len:
                if text[j] == "&":
                    k = j + 1
                    while k < text_len and text[k] in " \t\n\r":
                        k += 1
                    m = k
                    while m < text_len and text[m] not in "=&":
                        m += 1
                    if m < text_len and text[m] == "=":
                        value_end = j
                        i = j + 1
                        break
                j += 1

            value = text[value_start:value_end]
            pairs.append((key, value))

            if value_end < text_len:
                i = value_end + 1
            else:
                break

        return pairs

    pairs = find_key_value_pairs(data)
    parts = []

    for key, value in pairs:
        if key is None:
            parts.append(urllib.parse.quote_plus(value, safe=""))
        else:
            encoded_value = urllib.parse.quote_plus(value, safe="")
            parts.append(f"{key}={encoded_value}")

    return "&".join(parts)


def should_encode_form(headers: httpx.Headers, data: str) -> bool:
    if not data:
        return False
    if not headers:
        return False
    content_type = headers.get("Content-Type")
    if not content_type:
        return False
    return "application/x-www-form-urlencoded" in content_type.lower()


def extract_charset_from_content_type(content_type: str) -> str:
    if not content_type:
        return ""
    parts = content_type.split(";")
    for part in parts[1:]:
        lowered = part.strip().lower()
        if lowered.startswith("charset="):
            return part.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def extract_declared_charset_from_body(data: bytes) -> str:
    if not data:
        return ""
    sample = data[:16384]
    try:
        sample_text = sample.decode("iso-8859-1", errors="ignore")
    except UnicodeDecodeError:
        return ""
    for line in sample_text.splitlines():
        lowered = line.lower()
        if "content-type:" in lowered and "charset=" in lowered:
            charset_index = lowered.index("charset=") + len("charset=")
            remainder = line[charset_index:]
            for separator in [";", " ", "\t"]:
                remainder = remainder.split(separator)[0]
            return remainder.strip().strip('"').strip("'")
    meta_match = re.search(r'charset=["\']?([a-zA-Z0-9_\-.:]+)', sample_text, re.IGNORECASE)
    if meta_match:
        return meta_match.group(1)
    return ""


def decode_body_bytes(data: bytes, headers: httpx.Headers, user_encoding: str = ""):
    attempts = []
    if user_encoding:
        attempts.append(("user", user_encoding))
    header_declared = extract_charset_from_content_type(headers.get("Content-Type", "")) if headers else ""
    if header_declared:
        attempts.append(("header", header_declared))
    body_declared = extract_declared_charset_from_body(data) if not header_declared else ""
    if body_declared:
        attempts.append(("body", body_declared))
    for source, encoding in attempts:
        enc = (encoding or "").strip()
        if not enc:
            continue
        try:
            return data.decode(enc), enc, source
        except (LookupError, UnicodeDecodeError):
            continue
    if charset_from_bytes is not None and data:
        best = charset_from_bytes(data).best()
        if best and best.encoding:
            try:
                return data.decode(best.encoding), best.encoding, "detected"
            except (LookupError, UnicodeDecodeError):
                pass
    if chardet is not None and data:
        detection = chardet.detect(data)
        encoding = detection.get("encoding")
        if encoding:
            try:
                return data.decode(encoding), encoding, "detected"
            except (LookupError, UnicodeDecodeError):
                pass
    try:
        return data.decode("utf-8"), "utf-8", "fallback"
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace"), "utf-8", "fallback"


def prepare_body(data: str, headers: httpx.Headers, debug: bool = False):
    meta = {
        "source": "inline",
        "mode": "none",
        "length": 0,
        "charset": None,
        "encoded": False,
    }
    if not data:
        return None, meta
    if data.startswith("@"):
        path = data[1:]
        if path == "-":
            payload = sys.stdin.buffer.read()
            meta["source"] = "stdin"
        else:
            path = os.path.expanduser(path)
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Body file not found: {path}")
            with open(path, "rb") as fh:
                payload = fh.read()
            meta["source"] = path
        meta["mode"] = "binary"
        meta["length"] = len(payload)
        return payload, meta
    stripped = data.strip()
    content_type = headers.get("Content-Type")
    if not content_type:
        guessed = ""
        if stripped.startswith("{") or stripped.startswith("["):
            guessed = "application/json"
        elif "=" in stripped and "&" in stripped:
            guessed = "application/x-www-form-urlencoded"
        elif stripped.startswith("<"):
            guessed = "application/xml"
        if guessed:
            headers["Content-Type"] = guessed
            content_type = guessed
    processed = data
    if should_encode_form(headers, data):
        processed = encode_form_data(data)
        meta["mode"] = "form-urlencoded"
        meta["encoded"] = True
    else:
        normalized = (headers.get("Content-Type") or "").lower()
        if normalized.startswith("application/json"):
            meta["mode"] = "json"
        elif normalized.startswith("multipart/form-data"):
            meta["mode"] = "multipart"
        elif normalized.startswith("text/") or "xml" in normalized:
            meta["mode"] = "text"
        else:
            meta["mode"] = "raw"
    content_type = headers.get("Content-Type")
    charset = extract_charset_from_content_type(content_type) if content_type else ""
    if not charset and meta["mode"] in ("json", "text", "form-urlencoded"):
        charset = "utf-8"
        base = (content_type or "text/plain").split(";")[0].strip()
        headers["Content-Type"] = f"{base}; charset={charset}"
    elif not charset:
        charset = "utf-8"
    body_bytes = processed.encode(charset, errors="surrogatepass")
    meta["charset"] = charset
    meta["length"] = len(body_bytes)
    if debug:
        print("\n===== Debug: Body Encoding =====")
        print(f"Mode: {meta['mode']}")
        print(f"Charset: {charset}")
        print(f"Length: {meta['length']} bytes")
        print(f"Source: {meta['source']}")
        if meta["encoded"]:
            print("Form data was URL-encoded prior to sending.")
    return body_bytes, meta


def probe_connection(url: str, timeout: float, verify_tls: bool, skip: bool):
    metrics = {}
    if skip:
        return metrics
    parsed = urllib.parse.urlsplit(url)
    host = parsed.hostname
    if not host:
        return metrics
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    dns_start = time.perf_counter()
    try:
        addr_info = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return metrics
    dns_time = time.perf_counter() - dns_start
    family, socktype, proto, _, sockaddr = addr_info[0]
    sock = socket.socket(family, socktype, proto)
    sock.settimeout(timeout or 30.0)
    try:
        connect_start = time.perf_counter()
        sock.connect(sockaddr)
        connect_time = time.perf_counter() - connect_start
        tls_time = 0.0
        if parsed.scheme == "https":
            ctx = ssl.create_default_context()
            if not verify_tls:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            try:
                tls_start = time.perf_counter()
                tls_sock = ctx.wrap_socket(sock, server_hostname=host, do_handshake_on_connect=False)
                try:
                    tls_sock.do_handshake()
                    tls_time = time.perf_counter() - tls_start
                finally:
                    tls_sock.close()
            except ssl.SSLError:
                tls_time = 0.0
        else:
            sock.close()
    except OSError:
        sock.close()
        return {"dns_lookup": dns_time}
    metrics["dns_lookup"] = dns_time
    metrics["tcp_connect"] = connect_time
    metrics["tls_handshake"] = tls_time
    metrics["pretransfer"] = dns_time + connect_time + tls_time
    return metrics


def format_metric_value(key: str, value):
    if value is None:
        return "n/a"
    if key in {"http_code", "redirects", "size_download"}:
        return str(int(value))
    if key == "speed_download":
        return f"{value:.2f} B/s"
    return f"{value:.6f}s"


def summarize(values):
    if not values:
        return None
    count = len(values)
    total = sum(values)
    return min(values), total / count, max(values)


def render_request_overview(method: str, url: str, headers: httpx.Headers, body_meta: Dict[str, str]):
    items = list(headers.items())
    print("\n===== Prepared Request =====")
    print(f"Method: {method}")
    print(f"URL: {url}")
    print(f"Headers ({len(items)} total):")
    for key, value in items:
        print(f"  {key}: {value}")
    if body_meta["length"]:
        charset = body_meta.get("charset") or "n/a"
        print(f"Body: {body_meta['length']} bytes ({body_meta['mode']}, charset={charset}, source={body_meta['source']})")
    else:
        print("Body: <empty>")


def main():
    parser = argparse.ArgumentParser(description="Pure Python HTTP testing helper powered by httpx")
    parser.add_argument("--url", required=True)
    parser.add_argument("--method", default="GET")
    parser.add_argument("--data", default="")
    parser.add_argument("--headers", default="", type=str)
    parser.add_argument("--cookies", default="")
    parser.add_argument("--user-agent", dest="user_agent", default="")
    parser.add_argument("--proxy", default="")
    parser.add_argument("--timeout", default="")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--delay", default="0")
    parser.add_argument("--additional-args", dest="additional_args", default="")
    parser.add_argument("--action", default="")
    parser.add_argument("--include-headers", dest="include_headers", action="store_true")
    parser.add_argument("--no-include-headers", dest="include_headers", action="store_false")
    parser.add_argument("--auto-encode-url", dest="auto_encode_url", action="store_true")
    parser.add_argument("--no-auto-encode-url", dest="auto_encode_url", action="store_false")
    parser.add_argument("--follow-redirects", dest="follow_redirects", action="store_true")
    parser.add_argument("--allow-insecure", dest="allow_insecure", action="store_true")
    parser.add_argument("--verbose-output", dest="verbose_output", action="store_true")
    parser.add_argument("--show-command", dest="show_command", action="store_true")
    parser.add_argument("--show-summary", dest="show_summary", action="store_true")
    parser.add_argument("--debug", dest="debug", action="store_true")
    parser.add_argument("--response-encoding", dest="response_encoding", default="")
    parser.add_argument("--download", dest="download", default="")
    parser.set_defaults(
        include_headers=False,
        auto_encode_url=False,
        follow_redirects=False,
        allow_insecure=False,
        verbose_output=False,
        show_command=False,
        show_summary=False,
        debug=False,
    )
    args = parser.parse_args()

    repeat = max(1, args.repeat)
    try:
        delay_between = float(args.delay or "0")
        if delay_between < 0:
            delay_between = 0.0
    except ValueError:
        delay_between = 0.0

    prepared_url = smart_encode_url(args.url) if args.auto_encode_url else args.url
    method = (args.method or "GET").upper()

    # 处理 headers：支持字典（JSON字符串）和字符串格式
    # 框架会将 object 类型序列化为 JSON 字符串传递
    headers_list = []
    if args.headers:
        headers_str = args.headers.strip()
        # 优先尝试解析为 JSON（框架传递的字典会被序列化为 JSON）
        if headers_str.startswith("{") or headers_str.startswith("["):
            try:
                parsed = json.loads(headers_str)
                if isinstance(parsed, dict):
                    # 字典格式：直接转换为 (key, value) 元组列表
                    headers_list = [(str(k).strip(), str(v).strip()) for k, v in parsed.items()]
                elif isinstance(parsed, list):
                    # 数组格式：使用原有的 parse_headers 函数处理
                    headers_list = parse_headers(headers_str)
                else:
                    headers_list = parse_headers(headers_str)
            except (json.JSONDecodeError, ValueError):
                # JSON 解析失败，回退到原有的字符串解析逻辑
                headers_list = parse_headers(headers_str)
        else:
            # 非 JSON 格式，使用原有的字符串解析逻辑（向后兼容）
            headers_list = parse_headers(headers_str)
    headers = httpx.Headers(headers_list)
    if args.user_agent:
        headers["User-Agent"] = args.user_agent

    body_bytes = None
    body_meta = {
        "source": "inline",
        "mode": "none",
        "length": 0,
        "charset": None,
        "encoded": False,
    }
    try:
        body_bytes, body_meta = prepare_body(args.data, headers, args.debug)
    except FileNotFoundError as exc:
        print(f"Body preparation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    cookie_dict = parse_cookies(args.cookies)
    cookie_jar = httpx.Cookies()
    for name, value in cookie_dict.items():
        cookie_jar.set(name, value)

    additional_options = parse_additional_options(args.additional_args)

    timeout_value = None
    if args.timeout:
        try:
            timeout_value = float(args.timeout)
        except ValueError:
            timeout_value = None
    timeout = httpx.Timeout(timeout_value or 60.0)

    client_kwargs = {
        "timeout": timeout,
        "verify": not args.allow_insecure,
        "follow_redirects": args.follow_redirects,
        "cookies": cookie_jar,
    }
    if args.proxy:
        client_kwargs["proxy"] = args.proxy
    if "http2" in additional_options:
        client_kwargs["http2"] = str_to_bool(additional_options["http2"])
    if "cert" in additional_options:
        client_kwargs["cert"] = additional_options["cert"]
    if "verify" in additional_options:
        value = additional_options["verify"]
        lowered = value.strip().lower()
        client_kwargs["verify"] = str_to_bool(value) if lowered in {"true", "false", "1", "0", "yes", "no", "on", "off"} else value
    if "max_redirects" in additional_options:
        try:
            client_kwargs["max_redirects"] = int(additional_options["max_redirects"])
        except ValueError:
            pass
    if "trust_env" in additional_options:
        client_kwargs["trust_env"] = str_to_bool(additional_options["trust_env"])

    if args.show_command:
        render_request_overview(method, prepared_url, headers, body_meta)

    aggregate = None
    if args.show_summary:
        aggregate = {key: [] for key in METRIC_KEYS}
        aggregate["wall_time"] = []

    exit_code = 0
    verify_option = client_kwargs.get("verify", True)
    verify_tls = verify_option if isinstance(verify_option, bool) else True
    skip_probe = bool(args.proxy)

    client = httpx.Client(**client_kwargs)
    try:
        for run_index in range(repeat):
            if run_index > 0 and delay_between > 0:
                time.sleep(delay_between)

            metrics = {key: None for key in METRIC_KEYS}
            probe_metrics = probe_connection(prepared_url, timeout_value or 60.0, verify_tls, skip_probe)
            metrics.update(probe_metrics)

            start = time.perf_counter()
            first_byte_time = None
            body_buffer = bytearray()

            try:
                stream_kwargs = {
                    "method": method,
                    "url": prepared_url,
                    "headers": headers,
                }
                if body_bytes is not None:
                    stream_kwargs["content"] = body_bytes

                with client.stream(**stream_kwargs) as response:
                    status_code = response.status_code
                    metrics["http_code"] = status_code
                    metrics["redirects"] = len(response.history)
                    http_version = response.http_version or "HTTP/1.1"

                    for chunk in response.iter_bytes():
                        if first_byte_time is None:
                            first_byte_time = time.perf_counter()
                        body_buffer.extend(chunk)

                    total_elapsed = time.perf_counter() - start
                    metrics["total"] = total_elapsed
                    metrics["ttfb"] = (first_byte_time - start) if first_byte_time else total_elapsed
                    metrics["size_download"] = len(body_buffer)
                    metrics["speed_download"] = (len(body_buffer) / total_elapsed) if total_elapsed > 0 else 0.0
                    if metrics.get("pretransfer") is None:
                        metrics["pretransfer"] = (metrics.get("dns_lookup") or 0.0) + (metrics.get("tcp_connect") or 0.0) + (metrics.get("tls_handshake") or 0.0)

                    decoded_body, used_encoding, encoding_source = decode_body_bytes(bytes(body_buffer), response.headers, args.response_encoding)

                    print(f"\n===== Response #{run_index + 1} =====")
                    download_target = (args.download or "").strip()
                    if download_target:
                        # 支持多次请求时通过 {i} 占位符区分文件名
                        if repeat > 1 and "{i}" in download_target:
                            filename = download_target.format(i=run_index + 1)
                        else:
                            filename = download_target
                        try:
                            if os.path.dirname(filename):
                                os.makedirs(os.path.dirname(filename), exist_ok=True)
                            with open(filename, "wb") as fh:
                                fh.write(body_buffer)
                            print(f"[saved response body to file: {filename}]")
                        except OSError as exc:
                            print(f"[failed to save response body to {filename}: {exc}]", file=sys.stderr)
                    if args.include_headers:
                        status_line = f"{http_version} {status_code} {response.reason_phrase}"
                        print(status_line)
                        for key, value in response.headers.items():
                            print(f"{key}: {value}")
                        print("")
                    output_body = decoded_body.rstrip()
                    if output_body:
                        print(output_body)
                    else:
                        print("[no body]")

                    print(f"\n----- Meta #{run_index + 1} -----")
                    if args.show_summary:
                        for key in METRIC_KEYS:
                            label = key.replace("_", " ").title()
                            print(f"{label}: {format_metric_value(key, metrics.get(key))}")
                            value = metrics.get(key)
                            if aggregate is not None and isinstance(value, (int, float)):
                                aggregate[key].append(float(value))
                        print(f"Wall Time (client): {total_elapsed:.6f}s")
                        if aggregate is not None:
                            aggregate["wall_time"].append(total_elapsed)
                    else:
                        print("Summary disabled (--show-summary=false).")
                        print(f"Wall Time (client): {total_elapsed:.6f}s")

                    print(f"Encoding Used: {used_encoding} ({encoding_source})")

                    if args.verbose_output:
                        sent_bytes = len(body_bytes) if body_bytes else 0
                        print("\nVerbose diagnostics:")
                        print(f"  Sent body bytes: {sent_bytes}")
                        if probe_metrics:
                            for key, value in probe_metrics.items():
                                print(f"  Probe {key}: {value:.6f}s")
                        print(f"  History length: {len(response.history)}")

            except httpx.HTTPError as exc:
                exit_code = 1
                elapsed = time.perf_counter() - start
                print(f"\n===== Response #{run_index + 1} =====")
                print(f"Request failed after {elapsed:.6f}s: {exc}")
                continue

        if aggregate and repeat > 1:
            print("\n===== Aggregate Timing =====")
            for key, values in aggregate.items():
                summary = summarize(values)
                if not summary:
                    continue
                label = key.replace("_", " ").title()
                min_v, avg_v, max_v = summary
                if key == "speed_download":
                    print(f"{label}: min {min_v:.2f} B/s | avg {avg_v:.2f} B/s | max {max_v:.2f} B/s")
                elif key == "size_download":
                    print(f"{label}: min {min_v:.0f}B | avg {avg_v:.0f}B | max {max_v:.0f}B")
                elif key in {"http_code", "redirects"}:
                    print(f"{label}: min {min_v:.0f} | avg {avg_v:.2f} | max {max_v:.0f}")
                else:
                    print(f"{label}: min {min_v:.6f}s | avg {avg_v:.6f}s | max {max_v:.6f}s")

    finally:
        client.close()

    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)

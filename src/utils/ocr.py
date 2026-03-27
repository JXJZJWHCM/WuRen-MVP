import os
import base64
from typing import Tuple

import httpx
from openai import OpenAI


def _read_image_as_data_url(image_path: str) -> Tuple[str, str]:
    ext = os.path.splitext(image_path)[1].lower().lstrip(".")
    mime = "image/png"
    if ext in ("jpg", "jpeg"):
        mime = "image/jpeg"
    elif ext in ("webp",):
        mime = "image/webp"

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}", mime


def ocr_deepseek(image_path: str, prompt: str = "Free OCR.") -> str:
    api_key = os.getenv("DEEPSEEK_OCR_API_KEY") or os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")

    model = os.getenv("DEEPSEEK_OCR_MODEL", "").strip() or "DeepSeek-OCR-2"
    base_url = os.getenv("DEEPSEEK_OCR_BASE_URL", "").strip() or "https://api.deepseek.com/v1"
    timeout_s = float(os.getenv("DEEPSEEK_OCR_TIMEOUT", "120"))

    data_url, _ = _read_image_as_data_url(image_path)

    timeout = httpx.Timeout(timeout_s, connect=30.0)
    proxy_url = (os.getenv("PROXY_URL") or "").strip()
    http_client = httpx.Client(timeout=timeout, proxy=proxy_url) if proxy_url else httpx.Client(timeout=timeout)
    client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "<image>\n" + prompt},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
        temperature=0,
    )
    text = (resp.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("Empty OCR result")
    return text


def ocr_image(image_path: str) -> Tuple[str, str]:
    text = ocr_deepseek(image_path)
    return text, "deepseek"

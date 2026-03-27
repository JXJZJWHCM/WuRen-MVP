import datetime as _dt
import os
import re
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.utils.defense_search import extract_cves, extract_ttps


def _extract_title(markdown_text: str) -> Optional[str]:
    for line in (markdown_text or "").splitlines():
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("#").strip() or None
    return None


def _normalize_links(html: str) -> str:
    if not html:
        return html
    html = re.sub(r'href="reports/images/', 'href="/files/reports/images/', html)
    html = re.sub(r'src="reports/images/', 'src="/files/reports/images/', html)
    html = re.sub(r'href="data/reports/images/', 'href="/files/reports/images/', html)
    html = re.sub(r'src="data/reports/images/', 'src="/files/reports/images/', html)
    return html


def render_report_html(
    base_dir: str,
    markdown_text: str,
    *,
    filename: str,
    target: str = "",
    engine_name: str = "雾刃渗透测试系统1.0",
    generated_at: Optional[_dt.datetime] = None,
) -> str:
    try:
        import markdown as _md  # type: ignore
    except Exception as e:
        raise RuntimeError("缺少 markdown 依赖，请安装 requirements.txt") from e

    generated_at = generated_at or _dt.datetime.now()
    title = _extract_title(markdown_text) or "安全测试报告"
    full_title = f"{engine_name} - {title}"

    html_body = _md.markdown(
        markdown_text or "",
        extensions=["fenced_code", "tables"],
        output_format="html5",
    )
    html_body = _normalize_links(html_body)

    ttps = extract_ttps(markdown_text)
    cves = extract_cves(markdown_text)

    templates_dir = os.path.join(base_dir, "src", "utils", "report_templates")
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
    tpl = env.get_template("report.html.j2")

    meta: Dict[str, Any] = {
        "engine_name": engine_name,
        "filename": filename,
        "target": target,
        "generated_at": generated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    defense: Dict[str, Any] = {
        "ttps": ttps,
        "cves": cves,
    }
    return tpl.render(title=full_title, meta=meta, body_html=html_body, defense=defense)

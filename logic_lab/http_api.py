"""Transport-independent routing, shared by local HTTP and production WSGI."""
import json
from pathlib import Path
import threading
from urllib.parse import urlparse

from .levels import public_levels
from . import service

STATIC = Path(__file__).resolve().parent.parent / "web"
SEARCH_SLOTS = threading.BoundedSemaphore(2)
FILES = {"/": ("index.html", "text/html; charset=utf-8"),
         "/app.js": ("app.js", "text/javascript; charset=utf-8"),
         "/api.js": ("api.js", "text/javascript; charset=utf-8"),
         "/board.js": ("board.js", "text/javascript; charset=utf-8"),
         "/pipe-hint.js": ("pipe-hint.js", "text/javascript; charset=utf-8"),
         "/pipe-hint.css": ("pipe-hint.css", "text/css; charset=utf-8"),
         "/victory.css": ("victory.css", "text/css; charset=utf-8"),
         "/style.css": ("style.css", "text/css; charset=utf-8"),
         "/favicon.svg": ("favicon.svg", "image/svg+xml")}
SECURITY_HEADERS = [
    ("Cache-Control", "no-store"),
    ("X-Content-Type-Options", "nosniff"),
    ("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; script-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'"),
    ("Referrer-Policy", "same-origin"),
]


def response(status, payload, mime="application/json; charset=utf-8"):
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8") if isinstance(payload, (dict, list)) else payload
    return status, [("Content-Type", mime), ("Content-Length", str(len(raw))), *SECURITY_HEADERS], raw


def route(method, path, body=b"", content_type="", origin=None, host=""):
    path = urlparse(path).path
    if method == "GET":
        if path == "/api/levels":
            return response(200, public_levels())
        if path in FILES:
            name, mime = FILES[path]
            return response(200, (STATIC / name).read_bytes(), mime)
        return response(404, {"error": "Không tìm thấy trang."})
    if method != "POST":
        return response(405, {"error": "Phương thức không được hỗ trợ."})
    if origin and (urlparse(origin).scheme not in ("http", "https") or urlparse(origin).netloc != host):
        return response(403, {"error": "Nguồn yêu cầu không hợp lệ."})
    if content_type.split(";")[0].strip() != "application/json":
        return response(415, {"error": "Yêu cầu phải dùng JSON."})
    if not body or len(body) > 32768:
        return response(413, {"error": "Yêu cầu quá lớn hoặc trống."})
    try:
        data = json.loads(body)
        if path == "/api/check":
            return response(200, service.check(data))
        if path not in ("/api/hint", "/api/solve"):
            return response(404, {"error": "Không tìm thấy chức năng."})
        if not SEARCH_SLOTS.acquire(blocking=False):
            return response(429, {"error": "Máy đang tìm kiếm. Vui lòng thử lại sau vài giây."})
        try:
            result = service.hint(data) if path == "/api/hint" else service.solve(data, trace=True)
            return response(200, result)
        finally:
            SEARCH_SLOTS.release()
    except (ValueError, TypeError, KeyError) as exc:
        return response(400, {"error": str(exc)})

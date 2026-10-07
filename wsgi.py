"""Production adapter for Gunicorn / Render. No framework needed."""
from http import HTTPStatus
from logic_lab.http_api import route, response


def application(environ, start_response):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = -1
    if length < 0 or length > 32768:
        result = response(413, {"error": "Kích thước yêu cầu không hợp lệ."})
    else:
        raw = environ["wsgi.input"].read(length) if length else b""
        result = route(environ.get("REQUEST_METHOD", "GET"), environ.get("PATH_INFO", "/"),
                       raw, environ.get("CONTENT_TYPE", ""), environ.get("HTTP_ORIGIN"),
                       environ.get("HTTP_HOST", ""))
    status, headers, body = result
    start_response(f"{status} {HTTPStatus(status).phrase}", headers)
    return [body]

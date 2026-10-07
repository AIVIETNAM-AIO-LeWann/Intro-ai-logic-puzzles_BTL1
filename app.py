"""Local development launcher. Production entry point: wsgi:application."""
import argparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from logic_lab.http_api import route, response


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def handle_request(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = -1
        if length < 0 or length > 32768:
            result = response(413, {"error": "Kích thước yêu cầu không hợp lệ."})
        else:
            body = self.rfile.read(length) if length else b""
            result = route(self.command, self.path, body,
                           self.headers.get("Content-Type", ""),
                           self.headers.get("Origin"), self.headers.get("Host", ""))
        status, headers, raw = result
        self.send_response(status)
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    do_GET = do_POST = handle_request


def main():
    parser = argparse.ArgumentParser(description="Mạch — Logic Lab")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Logic Lab: http://127.0.0.1:{args.port}", flush=True)
    print("Nhan Ctrl+C de dung. Python 3.10+; khong can cai thu vien.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDa dung Logic Lab.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

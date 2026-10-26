import io
import json
import unittest
from logic_lab.http_api import route
from wsgi import application
from logic_lab.http_api import SEARCH_SLOTS


class ApiTests(unittest.TestCase):
    def test_malformed_origins_and_deep_json_return_errors(self):
        for origin in ("http://[", "null", "http://localhost/path", "https://other.test"):
            self.assertEqual(route("POST", "/api/check", b"{}", "application/json", origin, "localhost")[0], 403)
        raw = b"[" * 1500 + b"0" + b"]" * 1500
        self.assertEqual(route("POST", "/api/check", raw, "application/json")[0], 400)
        self.assertEqual(route("POST", "/api/check", b"\xff", "application/json")[0], 400)

    def test_bad_input_releases_search_capacity(self):
        for payload in (None, [], {"level": []}, {"level": "pipes-3", "state": {"tiles": [0]}},
                        {"level": "lightup-3", "algorithm": "bad", "state": {"bulbs": [0, 8]}}):
            raw = json.dumps(payload).encode()
            self.assertEqual(route("POST", "/api/hint", raw, "application/json")[0], 400)
        self.assertTrue(SEARCH_SLOTS.acquire(blocking=False))
        try:
            self.assertTrue(SEARCH_SLOTS.acquire(blocking=False))
            SEARCH_SLOTS.release()
        finally:
            SEARCH_SLOTS.release()

    def test_busy_search_returns_retryable_error(self):
        SEARCH_SLOTS.acquire()
        SEARCH_SLOTS.acquire()
        try:
            self.assertEqual(route("POST", "/api/solve", b'{"level":"pipes-3"}', "application/json")[0], 429)
        finally:
            SEARCH_SLOTS.release()
            SEARCH_SLOTS.release()
    def test_no_answers_exposed_in_level_listing(self):
        status, _, raw = route("GET", "/api/levels")
        self.assertEqual(status, 200)
        levels = json.loads(raw)
        self.assertEqual(len(levels), 8)
        self.assertTrue(all("_witness" not in level for level in levels))

    def test_assets_and_no_traversal(self):
        for path in ("/", "/style.css", "/app.js", "/board.js", "/pipe-hint.js", "/api.js", "/favicon.svg"):
            self.assertEqual(route("GET", path)[0], 200)
        self.assertEqual(route("GET", "/../app.py")[0], 404)

    def test_malformed_input_and_cross_origin(self):
        self.assertEqual(route("POST", "/api/check", b"bad", "application/json")[0], 400)
        self.assertEqual(route("POST", "/api/check", b"{}", "text/plain")[0], 415)
        self.assertEqual(route("POST", "/api/check", b"{}", "application/json", "https://other.test", "localhost")[0], 403)
        for state in ({"bulbs": [4]}, {"bulbs": [0], "crosses": [0]}, {"bulbs": [True]}, {"bulbs": [-1]}):
            raw = json.dumps({"level": "lightup-3", "state": state}).encode()
            self.assertEqual(route("POST", "/api/check", raw, "application/json")[0], 400)

    def test_wsgi_production_adapter(self):
        raw = json.dumps({"level": "lightup-3", "state": {"bulbs": [0, 8]}}).encode()
        environ = {"REQUEST_METHOD": "POST", "PATH_INFO": "/api/check", "CONTENT_LENGTH": str(len(raw)),
                   "CONTENT_TYPE": "application/json", "HTTP_HOST": "example.onrender.com",
                   "HTTP_ORIGIN": "https://example.onrender.com", "wsgi.input": io.BytesIO(raw)}
        received = []
        body = b"".join(application(environ, lambda status, headers: received.append((status, headers))))
        self.assertEqual(received[0][0], "200 OK")
        self.assertTrue(json.loads(body)["solved"])


if __name__ == "__main__":
    unittest.main()

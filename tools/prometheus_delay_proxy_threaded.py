from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse, parse_qs
import threading
import time
import json

UPSTREAM = "http://127.0.0.1:9090"

state = {"delay_ms": 0}
lock = threading.Lock()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/__set_delay":
            qs = parse_qs(parsed.query)
            ms = int(qs.get("ms", ["0"])[0])
            with lock:
                state["delay_ms"] = ms
            body = json.dumps({"delay_ms": ms}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/__get_delay":
            with lock:
                ms = state["delay_ms"]
            body = json.dumps({"delay_ms": ms}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        with lock:
            delay_ms = state["delay_ms"]

        time.sleep(delay_ms / 1000.0)

        target = UPSTREAM + self.path
        try:
            req = Request(target, headers={"User-Agent": "delay-proxy-threaded"})
            with urlopen(req, timeout=20) as resp:
                body = resp.read()
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    lk = k.lower()
                    if lk not in (
                        "transfer-encoding",
                        "connection",
                        "keep-alive",
                        "proxy-authenticate",
                        "proxy-authorization",
                        "te",
                        "trailers",
                        "upgrade",
                    ):
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
        except HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except URLError as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))

    def log_message(self, fmt, *args):
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), fmt % args))

class Server(ThreadingHTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    Server(("0.0.0.0", 9091), Handler).serve_forever()

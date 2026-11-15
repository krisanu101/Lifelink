"""Web server: serves the frontend files and the /api/... routes. Made by Krisanu.
Run:  python backend/server.py   (or double-click start.bat)
For a real site run it behind HTTPS (Caddy or nginx) and set HTTPS=1 and TRUST_PROXY=1 in config.env."""
import http.server, json, os, threading, webbrowser
from urllib.parse import urlparse, parse_qs

import auth, config, database, maintenance, seed
import routes_public, routes_auth, routes_donor, routes_requests, routes_hospital, routes_admin   # noqa: F401 (registers the routes)
from router import dispatch, ApiError

CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=config.FRONTEND_DIR, **kwargs)

    def log_message(self, *args):
        pass

    def end_headers(self):
        """Safety headers on every response (pages, scripts and the API)."""
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy", CSP)
        if self.is_https():
            self.send_header("Strict-Transport-Security", "max-age=31536000")
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")      # always check for the newest files
        super().end_headers()

    def is_https(self):
        return config.HTTPS or (config.TRUST_PROXY and self.headers.get("X-Forwarded-Proto", "") == "https")

    def client_ip(self):
        if config.TRUST_PROXY and self.headers.get("X-Forwarded-For"):
            return self.headers["X-Forwarded-For"].split(",")[0].strip()
        return self.client_address[0]

    def send_json(self, payload, code=200, cookie=None):
        data = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(data)

    def cookie_text(self, token, max_age):
        flags = "; HttpOnly; Path=/; SameSite=Lax; Max-Age=%d" % max_age
        return "ll_session=%s%s%s" % (token, flags, "; Secure" if self.is_https() else "")

    def handle_api(self, method):
        url = urlparse(self.path)
        body = {}
        if method == "POST":
            if "application/json" not in self.headers.get("Content-Type", ""):
                return self.send_json({"error": "Bad request."}, 400)        # plain HTML forms from other sites are refused (CSRF)
            try:
                length = max(0, min(int(self.headers.get("Content-Length", 0) or 0), 200_000))
                body = json.loads(self.rfile.read(length) or b"{}")
            except ValueError:
                return self.send_json({"error": "Bad request."}, 400)
            if not isinstance(body, dict):
                return self.send_json({"error": "Bad request."}, 400)
        cookie_header = self.headers.get("Cookie", "")
        try:
            user = auth.user_from_cookie(cookie_header)
            result, ctx = dispatch(method, url.path, parse_qs(url.query), body, user, self.client_ip())
            cookie = None
            if ctx.set_cookie:
                cookie = self.cookie_text(ctx.set_cookie, config.SESSION_DAYS * 86400)
            elif ctx.clear_cookie:
                auth.end_session(cookie_header)
                cookie = self.cookie_text("", 0)
            self.send_json(result, 200, cookie)
        except ApiError as error:
            self.send_json({"error": str(error)}, error.code)
        except (ValueError, TypeError) as error:                # for example a text where a number was expected
            self.send_json({"error": "Please check what you entered."}, 400)
        except Exception as error:               # unexpected problem: tell the user, keep the server alive
            print("Server error:", repr(error))
            self.send_json({"error": "Something went wrong on the server."}, 500)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.handle_api("GET")
        return super().do_GET()

    def do_POST(self):
        self.handle_api("POST")


def prepare():
    """Create tables, sample data or the first admin, and start the housekeeping thread. Returns the engine name."""
    engine = database.setup()
    if seed.seed_if_empty():
        print("Sample data created. Demo logins are in README.md. Do not use them on a real site.")
    seed.ensure_admin()
    maintenance.start()
    return engine


if __name__ == "__main__":
    engine = prepare()
    http.server.ThreadingHTTPServer.request_queue_size = 128
    server = http.server.ThreadingHTTPServer((config.HOST, config.PORT), Handler)
    url = "http://127.0.0.1:%d" % config.PORT
    print("LifeLink is running (%s database): %s" % (engine.upper(), url))
    if config.HOST != "127.0.0.1" and config.SEED_DEMO:
        print("WARNING: sample data and demo logins are ON while the server is open to the network. "
              "Set SEED_DEMO=0 in config.env for a real site.")
    if config.HOST != "127.0.0.1" and config.SMS_PROVIDER == "demo":
        print("WARNING: SMS_PROVIDER=demo means nobody will receive login codes. Set a real SMS provider.")
    print("Close this window or press Ctrl+C to stop.")
    if not os.environ.get("NO_BROWSER") and config.HOST == "127.0.0.1":
        threading.Timer(1, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

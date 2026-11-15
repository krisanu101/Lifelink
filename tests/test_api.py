"""Automatic checks for the whole backend (uses a temporary SQLite database).
Run:  python tests/test_api.py        Made by Krisanu."""
import datetime, http.cookiejar, json, os, sys, tempfile, threading, unittest, urllib.error, urllib.request

TMP = tempfile.mkdtemp()
os.environ.update({"DB_ENGINE": "sqlite", "SQLITE_PATH": os.path.join(TMP, "test.db"), "SEED_DEMO": "1", "SMS_PROVIDER": "demo"})
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

import http.server
import server as srv, maintenance                      # noqa: E402
from database import run                               # noqa: E402

srv.prepare()
HTTPD = http.server.ThreadingHTTPServer(("127.0.0.1", 0), srv.Handler)
BASE = "http://127.0.0.1:%d" % HTTPD.server_address[1]
threading.Thread(target=HTTPD.serve_forever, daemon=True).start()


class Client:
    def __init__(self):
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def call(self, path, body=None, raw_type=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": raw_type or "application/json"} if data is not None else {})
        try:
            with self.opener.open(req) as r:
                return r.status, json.loads(r.read() or b"{}"), r.headers
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}"), e.headers

    def ok(self, path, body=None):
        status, data, _ = self.call(path, body)
        assert status == 200, (path, status, data)
        return data

    def login(self, who, password):
        return self.ok("/api/auth/login", {"login": who, "password": password})


def donor_form(phone, **extra):
    form = {"role": "donor", "name": "Test Donor", "phone": phone, "password": "abc123", "blood_group": "B+", "gender": "male",
            "birth_date": "1995-01-01", "weight": 70, "area": "Dhaka", "upazila": "Dhanmondi", "consent": True, "health_risk": False}
    form.update(extra)
    return form


class LifeLinkTests(unittest.TestCase):
    def test_1_public_and_headers(self):
        c = Client()
        status, meta, headers = c.call("/api/meta")
        self.assertEqual(len(meta["areas"]), 64)
        self.assertEqual(len(meta["divisions"]), 8)
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertIn("default-src", headers["Content-Security-Policy"])
        self.assertTrue(c.ok("/api/public/needs"))
        self.assertTrue(c.ok("/api/public/stock?group=O%2B&area=Dhaka"))
        self.assertEqual(c.call("/api/health")[0], 200)
        status, html, _ = Client().call("/api/requests/1")
        self.assertEqual(status, 401)

    def test_2_register_login_rules(self):
        c = Client()
        c.ok("/api/auth/register", donor_form("+880 1811-111111"))          # phone in +880 format is accepted
        self.assertEqual(Client().call("/api/auth/register", donor_form("01811111111"))[0], 400)      # same phone again
        self.assertEqual(Client().call("/api/auth/register", donor_form("01811111112", password="123"))[0], 400)   # too short
        self.assertEqual(Client().call("/api/auth/register", donor_form("12345"))[0], 400)               # bad phone
        self.assertEqual(Client().call("/api/auth/register", donor_form("01811111113", area="Atlantis"))[0], 400)
        self.assertEqual(Client().call("/api/auth/register", donor_form("01811111114", weight=40))[0], 400)
        d = Client()
        self.assertEqual(d.login("01811-111111", "abc123")["user"]["role"], "donor")     # login by phone
        self.assertEqual(d.ok("/api/auth/me")["user"]["phone"], "01811111111")

    def test_3_login_rate_limit(self):
        c = Client()
        codes = [c.call("/api/auth/login", {"login": "01999999999", "password": "x"})[0] for _ in range(10)]
        self.assertEqual(codes[:8], [401] * 8)
        self.assertEqual(codes[9], 429)

    def test_4_otp_login_and_reset(self):
        c = Client()
        out = c.ok("/api/auth/otp/send", {"phone": "01700400001", "purpose": "login"})
        self.assertEqual(len(out["demo_code"]), 6)
        self.assertEqual(c.call("/api/auth/otp/send", {"phone": "01700400001", "purpose": "login"})[0], 429)   # one per minute
        self.assertEqual(Client().call("/api/auth/otp/login", {"phone": "01700400001", "code": "000000"})[0], 401)
        self.assertEqual(c.ok("/api/auth/otp/login", {"phone": "01700400001", "code": out["demo_code"]})["user"]["role"], "donor")
        self.assertEqual(Client().call("/api/auth/otp/login", {"phone": "01700400001", "code": out["demo_code"]})[0], 401)   # used once only
        out2 = Client().ok("/api/auth/otp/send", {"phone": "01700400002", "purpose": "reset"})
        r = Client()
        r.ok("/api/auth/reset", {"phone": "01700400002", "code": out2["demo_code"], "password": "newpass1"})
        Client().login("01700400002", "newpass1")
        self.assertNotIn("demo_code", Client().ok("/api/auth/otp/send", {"phone": "01600000000", "purpose": "login"}))   # unknown phone: no hint

    def test_5_full_blood_flow(self):
        req, hosp, donor, admin = Client(), Client(), Client(), Client()
        req.login("01700300001", "user123")
        hosp.login("01700200001", "hospital123")
        donor.login("01700400001", "donor123")                 # Rakib, B+, Dhaka
        rid = req.ok("/api/requests", {"patient_name": "Test", "blood_group": "B+", "units": 1, "urgency": "urgent", "hospital_id": 1,
                                       "area": "Dhaka", "upazila": "Dhanmondi", "contact_phone": "01700300001"})["id"]
        self.assertEqual(req.call("/api/requests", {"patient_name": "T", "blood_group": "B+", "units": 1, "hospital_id": 1, "area": "Dhaka",
                                                    "needed_by": "2000-01-01"})[0], 400)           # date in the past
        self.assertNotIn(rid, [n["id"] for n in req.ok("/api/public/needs")])                        # not verified yet
        req.ok("/api/requests/%d/update" % rid, {"units": 2, "note": "ward 5"})
        hosp.ok("/api/hospital/requests/%d/verify" % rid, {"ok": True})
        self.assertIn(rid, [n["id"] for n in req.ok("/api/public/needs")])
        near = hosp.ok("/api/hospital/requests/%d/matches?scope=district" % rid)
        self.assertTrue(near and all(m["area"] == "Dhaka" for m in near))
        far = hosp.ok("/api/hospital/requests/%d/matches?scope=all" % rid)
        self.assertGreater(len(far), len(near))
        self.assertEqual(far[0]["tier"], min(m["tier"] for m in far))          # nearest first
        n = hosp.ok("/api/hospital/requests/%d/notify" % rid, {"scope": "district", "limit": 30})["notified"]
        self.assertEqual(n, len(near))
        self.assertTrue(any(i["id"] == rid for i in donor.ok("/api/donor/inbox")))
        donor.ok("/api/donor/respond", {"request_id": rid, "accept": True})
        detail = req.ok("/api/requests/%d" % rid)
        self.assertIn("01700400001", [d["phone"] for d in detail["donors"]])        # phone visible only after accept
        donor.ok("/api/donor/cancel", {"request_id": rid})
        self.assertTrue(all(d["phone"] is None for d in req.ok("/api/requests/%d" % rid)["donors"] if d["status"] != "accepted"))
        # record a donation by phone: donor then blocked for 120 days
        other = [d for d in req.ok("/api/requests/%d" % rid)["donors"] if d["status"] == "asked"][0]["donor_id"]
        phone = run("SELECT phone FROM users WHERE id=?", (other,))[0]["phone"]
        hosp.ok("/api/hospital/donations", {"donor_phone": phone, "units": 1, "request_id": rid})
        status, data, _ = hosp.call("/api/hospital/donations", {"donor_phone": phone, "units": 1})
        self.assertEqual(status, 400)
        self.assertIn("Next donation possible", data["error"])
        row = run("SELECT last_donation FROM donors WHERE user_id=?", (other,))[0]
        self.assertEqual(str(row["last_donation"]), datetime.date.today().isoformat())
        # privacy: a donor cannot open someone else's request
        self.assertEqual(donor.call("/api/requests/%d" % rid)[0], 403)

    def test_6_stock_expiry(self):
        h = Client()
        h.login("01700200002", "hospital123")
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        h.ok("/api/hospital/stock/adjust", {"blood_group": "AB-", "delta": 5, "expires_on": yesterday})
        rows = Client().ok("/api/public/stock?group=AB-")
        self.assertFalse(any(r["id"] == 2 and r["units"] == 7 for r in rows))
        h.ok("/api/hospital/stock/adjust", {"blood_group": "AB-", "discard": True})
        self.assertEqual([s for s in h.ok("/api/hospital/stock") if s["blood_group"] == "AB-"][0]["units"], 0)
        self.assertEqual(h.call("/api/hospital/stock/adjust", {"blood_group": "AB-", "delta": 0})[0], 400)

    def test_7_admin_and_expiry(self):
        a, victim = Client(), Client()
        a.login("admin@lifelink.local", "admin123")                      # email login still works
        users = a.ok("/api/admin/users?q=Rakib")
        self.assertEqual(len(users["items"]), 1)
        uid = users["items"][0]["id"]
        v = Client(); v.login("01700400001", "donor123")
        a.ok("/api/admin/users/%d/suspend" % uid, {})
        self.assertEqual(v.call("/api/auth/me")[1]["user"], None)         # session ended at once
        self.assertEqual(Client().call("/api/auth/login", {"login": "01700400001", "password": "donor123"})[0], 403)
        a.ok("/api/admin/users/%d/activate" % uid, {})
        Client().login("01700400001", "donor123")
        self.assertEqual(a.call("/api/admin/users/%d/suspend" % 1, {})[0], 400)          # cannot suspend yourself (admin is user 1)
        self.assertEqual(Client().call("/api/admin/users")[0], 401)
        # old requests close by themselves
        r = Client(); r.login("01700300001", "user123")
        rid = r.ok("/api/requests", {"patient_name": "Old", "blood_group": "A+", "units": 1, "hospital_id": 1, "area": "Dhaka"})["id"]
        run("UPDATE requests SET created_at='2000-01-01 00:00:00' WHERE id=?", (rid,))
        maintenance.run_once()
        self.assertEqual(run("SELECT status FROM requests WHERE id=?", (rid,))[0]["status"], "expired")

    def test_8_csrf_and_bad_input(self):
        c = Client()
        self.assertEqual(c.call("/api/auth/login", {"login": "a", "password": "b"}, raw_type="application/x-www-form-urlencoded")[0], 400)
        self.assertEqual(c.call("/api/auth/login", ["list"])[0], 400)
        r = Client(); r.login("01700300001", "user123")
        self.assertEqual(r.call("/api/requests", {"patient_name": "x", "blood_group": "B+", "units": "abc", "hospital_id": 1, "area": "Dhaka"})[0], 400)

    def test_9_hospital_staff_register_pending(self):
        c = Client()
        out = c.ok("/api/auth/register", {"role": "hospital", "name": "New Staff", "phone": "01322222222", "password": "hosp123",
                                          "new_hospital_name": "Sylhet Test Hospital", "new_hospital_area": "Sylhet"})
        self.assertTrue(out["pending"])
        self.assertEqual(Client().call("/api/auth/login", {"login": "01322222222", "password": "hosp123"})[0], 403)

    def test_10_delete_account_and_password_change(self):
        c = Client()
        c.ok("/api/auth/register", donor_form("01877777777"))
        c.ok("/api/auth/change-password", {"old_password": "abc123", "new_password": "xyz789"})
        self.assertEqual(c.call("/api/auth/change-password", {"old_password": "wrong1", "new_password": "xyz789"})[0], 401)
        Client().login("01877777777", "xyz789")
        self.assertEqual(c.call("/api/auth/delete-account", {"password": "bad"})[0], 401)
        c.ok("/api/auth/delete-account", {"password": "xyz789"})
        self.assertEqual(Client().call("/api/auth/login", {"login": "01877777777", "password": "xyz789"})[0], 401)
        self.assertIsNone(c.ok("/api/auth/me")["user"])
        self.assertEqual(run("SELECT name, email FROM users WHERE status='deleted'")[0]["name"], "Deleted user")

    def test_11_password_hash_upgrade_and_hashed_sessions(self):
        import hashlib, auth
        # an account made with the old hash format (salt$digest, 120000 rounds) can still log in and is upgraded
        salt = os.urandom(16)
        old = salt.hex() + "$" + hashlib.pbkdf2_hmac("sha256", b"oldpass1", salt, 120000).hex()
        self.assertTrue(auth.check_password("oldpass1", old))
        self.assertTrue(auth.needs_rehash(old))
        c = Client()
        c.ok("/api/auth/register", donor_form("01866666666"))
        # store an old-format hash for the password abc123 used at registration
        salt2 = os.urandom(16)
        old2 = salt2.hex() + "$" + hashlib.pbkdf2_hmac("sha256", b"abc123", salt2, 120000).hex()
        run("UPDATE users SET pass_hash=? WHERE phone='01866666666'", (old2,))
        Client().login("01866666666", "abc123")
        new_hash = run("SELECT pass_hash FROM users WHERE phone='01866666666'")[0]["pass_hash"]
        self.assertFalse(auth.needs_rehash(new_hash))
        self.assertTrue(auth.check_password("abc123", new_hash))
        # the cookie value itself is never stored in the sessions table
        token = auth.new_session(run("SELECT id FROM users WHERE phone='01866666666'")[0]["id"])
        self.assertEqual(run("SELECT COUNT(*) AS c FROM sessions WHERE token=?", (token,))[0]["c"], 0)
        self.assertEqual(run("SELECT COUNT(*) AS c FROM sessions WHERE token=?", (auth._token_hash(token),))[0]["c"], 1)

    def test_12_demo_codes_need_demo_mode_and_bad_length(self):
        import config
        self.assertTrue(config.SHOW_DEMO_CODES)                     # this test run is a demo setup
        self.assertEqual(config.SMS_PROVIDER == "demo" and config.SEED_DEMO, config.SHOW_DEMO_CODES)
        # a broken Content-Length header gets a clean 400, not a crashed handler
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", HTTPD.server_address[1])
        conn.putrequest("POST", "/api/auth/login")
        conn.putheader("Content-Type", "application/json")
        conn.putheader("Content-Length", "abc")
        conn.endheaders()
        self.assertEqual(conn.getresponse().status, 400)
        conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)

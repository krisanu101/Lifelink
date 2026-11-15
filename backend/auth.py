"""Passwords, phone numbers, login sessions, one-time codes (OTP) and login rate limits. Made by Krisanu."""
import datetime, hashlib, hmac, os, re, secrets, threading, time
import config
from database import run, insert
from router import ApiError


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_time(value):
    """Database times come back as text (SQLite) or datetime objects (MySQL)."""
    return datetime.datetime.strptime(str(value)[:19], "%Y-%m-%d %H:%M:%S")


def ago(seconds):
    return (datetime.datetime.now() - datetime.timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S")


# ---------- phone numbers and email ----------
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_phone(raw):
    """Bangladesh mobile number as 01XXXXXXXXX. Accepts spaces, dashes, +880 and 880. Returns None if invalid."""
    digits = re.sub(r"\D", "", str(raw or ""))
    if digits.startswith("00880"):
        digits = digits[2:]
    if digits.startswith("880") and len(digits) == 13:
        digits = "0" + digits[3:]
    return digits if re.fullmatch(r"01[3-9]\d{8}", digits) else None


def need_phone(raw):
    phone = normalize_phone(raw)
    if not phone:
        raise ApiError("Enter a valid Bangladesh mobile number, for example 01712345678.")
    return phone


# ---------- passwords ----------
PBKDF2_ROUNDS = 600000      # current recommendation for PBKDF2-SHA256; older accounts used 120000


def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS)
    return "%d$%s$%s" % (PBKDF2_ROUNDS, salt.hex(), digest.hex())


def _split_hash(stored):
    """Returns (rounds, salt_hex, digest_hex). Old hashes were saved as salt$digest with 120000 rounds."""
    parts = stored.split("$")
    if len(parts) == 3:
        return int(parts[0]), parts[1], parts[2]
    salt, digest = parts
    return 120000, salt, digest


def check_password(password, stored):
    try:
        rounds, salt, digest = _split_hash(stored)
        test = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), rounds)
        return hmac.compare_digest(test.hex(), digest)
    except ValueError:
        return False


def needs_rehash(stored):
    try:
        return _split_hash(stored)[0] < PBKDF2_ROUNDS
    except ValueError:
        return False


def check_new_password(password):
    if len(password or "") < config.MIN_PASSWORD:
        raise ApiError("Password must be at least %d characters." % config.MIN_PASSWORD)


# ---------- users and sessions ----------
USER_FIELDS = "u.id, u.name, u.email, u.phone, u.role, u.hospital_id, u.status"


def public_user(user_id):
    rows = run("SELECT id, name, email, phone, role, hospital_id, status FROM users WHERE id=?", (user_id,))
    return rows[0] if rows else None


def find_user(identifier):
    """Find a user by phone number or email."""
    identifier = (identifier or "").strip()
    phone = normalize_phone(identifier)
    if phone:
        rows = run("SELECT id, pass_hash, status FROM users WHERE phone=?", (phone,))
    else:
        rows = run("SELECT id, pass_hash, status FROM users WHERE email=?", (identifier.lower(),))
    return rows[0] if rows else None


def _token_hash(token):
    """Only a hash of the login cookie is stored, so a leaked database cannot be used to log in."""
    return hashlib.sha256(token.encode()).hexdigest()


def new_session(user_id):
    token = secrets.token_hex(24)
    run("INSERT INTO sessions(token, user_id, created_at) VALUES(?,?,?)", (_token_hash(token), user_id, now()))
    return token


def user_from_cookie(cookie_header):
    if not cookie_header:
        return None
    for part in cookie_header.split(";"):
        name, _, value = part.strip().partition("=")
        if name == "ll_session" and value:
            rows = run("SELECT " + USER_FIELDS + ", s.created_at AS started FROM sessions s "
                       "JOIN users u ON u.id = s.user_id WHERE s.token=?", (_token_hash(value),))
            if not rows:
                return None
            row = rows[0]
            if parse_time(row.pop("started")) < datetime.datetime.now() - datetime.timedelta(days=config.SESSION_DAYS):
                run("DELETE FROM sessions WHERE token=?", (_token_hash(value),))
                return None
            return row if row["status"] == "active" else None
    return None


def end_session(cookie_header):
    for part in (cookie_header or "").split(";"):
        name, _, value = part.strip().partition("=")
        if name == "ll_session":
            run("DELETE FROM sessions WHERE token=?", (_token_hash(value),))


def end_all_sessions(user_id):
    run("DELETE FROM sessions WHERE user_id=?", (user_id,))


# ---------- login rate limit (in memory) ----------
_FAILS, _FLOCK = {}, threading.Lock()


def check_rate(key, limit=8, window=600):
    with _FLOCK:
        stamps = [s for s in _FAILS.get(key, []) if s > time.time() - window]
        _FAILS[key] = stamps
        if len(stamps) >= limit:
            raise ApiError("Too many wrong attempts. Please wait 10 minutes and try again.", 429)


def record_fail(key):
    with _FLOCK:
        _FAILS.setdefault(key, []).append(time.time())


def clear_fails(key):
    with _FLOCK:
        _FAILS.pop(key, None)


# ---------- one-time codes ----------
def _hash_code(phone, code):
    return hashlib.sha256((phone + ":" + code).encode()).hexdigest()


def create_otp(phone, purpose):
    """Make a 6-digit code for this phone and return it. Limits: one per minute, five per hour."""
    if run("SELECT id FROM otps WHERE phone=? AND created_at>?", (phone, ago(60))):
        raise ApiError("Please wait a minute before asking for another code.", 429)
    if len(run("SELECT id FROM otps WHERE phone=? AND created_at>?", (phone, ago(3600)))) >= 5:
        raise ApiError("Too many codes were requested. Please try again later.", 429)
    code = "%06d" % secrets.randbelow(1000000)
    insert("INSERT INTO otps(phone, purpose, code_hash, attempts, used, created_at) VALUES(?,?,?,0,0,?)",
           (phone, purpose, _hash_code(phone, code), now()))
    return code


def check_otp(phone, purpose, code):
    """True if the code is right (and then it cannot be used again)."""
    rows = run("SELECT id, code_hash, attempts FROM otps WHERE phone=? AND purpose=? AND used=0 AND created_at>? "
               "ORDER BY id DESC LIMIT 1", (phone, purpose, ago(config.OTP_MINUTES * 60)))
    if not rows or rows[0]["attempts"] >= 5:
        return False
    run("UPDATE otps SET attempts=attempts+1 WHERE id=?", (rows[0]["id"],))
    if hmac.compare_digest(rows[0]["code_hash"], _hash_code(phone, str(code or "").strip())):
        run("UPDATE otps SET used=1 WHERE id=?", (rows[0]["id"],))
        return True
    return False

"""Settings and fixed lists. Made by Krisanu.
Values come from config.env (in the project root) and can be overridden by environment variables."""
import os

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
DATABASE_DIR = os.path.join(ROOT_DIR, "database")


def _read_env_file():
    values = {}
    path = os.path.join(ROOT_DIR, "config.env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
    return values


_FILE = _read_env_file()


def get(key, default=""):
    return os.environ.get(key, _FILE.get(key, default))


PORT = int(get("PORT", "8000"))
HOST = get("HOST", "127.0.0.1")                    # use 0.0.0.0 inside Docker or on a server
HTTPS = get("HTTPS", "0") == "1"                   # 1 = site is served over HTTPS (cookie gets the Secure flag)
TRUST_PROXY = get("TRUST_PROXY", "0") == "1"       # 1 = running behind nginx/Caddy (read X-Forwarded-* headers)
SESSION_DAYS = int(get("SESSION_DAYS", "30"))
SQLITE_PATH = get("SQLITE_PATH", os.path.join(DATABASE_DIR, "lifelink.db"))

DB_ENGINE = get("DB_ENGINE", "mysql").lower()      # "mysql" or "sqlite"
MYSQL_HOST = get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(get("MYSQL_PORT", "3306"))
MYSQL_USER = get("MYSQL_USER", "root")
MYSQL_PASSWORD = get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = get("MYSQL_DATABASE", "lifelink")
DB_POOL = int(get("DB_POOL", "8"))

# SMS: demo = only stored in the SMS log. greenweb / bulksmsbd / custom = real delivery (see README).
SMS_PROVIDER = get("SMS_PROVIDER", "demo").lower()
SMS_API_KEY = get("SMS_API_KEY", "")
SMS_SENDER_ID = get("SMS_SENDER_ID", "")
SMS_URL = get("SMS_URL", "")                       # only for SMS_PROVIDER=custom, with {to} {message} {key} placeholders
SMS_LANG = get("SMS_LANG", "en")                   # en or bn (bn needs a gateway that accepts Unicode SMS)

SEED_DEMO = get("SEED_DEMO", "1") == "1"           # create fictional sample data on the first run
# Codes are shown on screen only in demo mode (no real SMS AND sample data on). A real site must never do this.
SHOW_DEMO_CODES = SMS_PROVIDER == "demo" and SEED_DEMO
ADMIN_PHONE = get("ADMIN_PHONE", "")               # first admin for a real site (used when no admin exists)
ADMIN_PASSWORD = get("ADMIN_PASSWORD", "")
ADMIN_NAME = get("ADMIN_NAME", "Site Admin")

GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
# recipient group -> donor groups that can give to that recipient
COMPAT = {"A+": ["A+", "A-", "O+", "O-"], "A-": ["A-", "O-"], "B+": ["B+", "B-", "O+", "O-"],
          "B-": ["B-", "O-"], "O+": ["O+", "O-"], "O-": ["O-"], "AB+": GROUPS,
          "AB-": ["A-", "B-", "O-", "AB-"]}

# Bangladesh: 8 divisions and 64 districts. Donors, requests and hospitals store the district in "area".
DIVISIONS = [
    ("Barishal", ["Barguna", "Barishal", "Bhola", "Jhalokathi", "Patuakhali", "Pirojpur"]),
    ("Chattogram", ["Bandarban", "Brahmanbaria", "Chandpur", "Chattogram", "Cumilla", "Cox's Bazar", "Feni", "Khagrachhari",
                    "Lakshmipur", "Noakhali", "Rangamati"]),
    ("Dhaka", ["Dhaka", "Faridpur", "Gazipur", "Gopalganj", "Kishoreganj", "Madaripur", "Manikganj", "Munshiganj",
               "Narayanganj", "Narsingdi", "Rajbari", "Shariatpur", "Tangail"]),
    ("Khulna", ["Bagerhat", "Chuadanga", "Jashore", "Jhenaidah", "Khulna", "Kushtia", "Magura", "Meherpur", "Narail", "Satkhira"]),
    ("Mymensingh", ["Jamalpur", "Mymensingh", "Netrokona", "Sherpur"]),
    ("Rajshahi", ["Bogura", "Chapainawabganj", "Joypurhat", "Naogaon", "Natore", "Pabna", "Rajshahi", "Sirajganj"]),
    ("Rangpur", ["Dinajpur", "Gaibandha", "Kurigram", "Lalmonirhat", "Nilphamari", "Panchagarh", "Rangpur", "Thakurgaon"]),
    ("Sylhet", ["Habiganj", "Moulvibazar", "Sunamganj", "Sylhet"]),
]
DISTRICTS = [d for _, ds in DIVISIONS for d in ds]
DIVISION_OF = {d: div for div, ds in DIVISIONS for d in ds}
AREAS = DISTRICTS

# Eligibility limits. Sources differ a little, so these are the cautious values.
# Check them against the official national guideline before real use.
MIN_AGE, MAX_AGE = 18, 60
MIN_WEIGHT = 50
GAP_MALE, GAP_FEMALE = 120, 180     # days between whole-blood donations

REQUEST_STALE_DAYS = 7              # a request nobody verified for this long is closed automatically
STOCK_SHELF_DAYS = 35               # shelf life of a new whole-blood bag
OTP_MINUTES = 10
MIN_PASSWORD = 6

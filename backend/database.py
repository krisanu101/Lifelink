"""Database layer. Works with MySQL (default) and falls back to SQLite if MySQL is not available.
All SQL in the project is written with ? placeholders; this file adapts it for the active engine.
MySQL uses a small connection pool, so many visitors can be served at the same time. Made by Krisanu."""
import os, queue, re, sqlite3, threading
import config

ENGINE = config.DB_ENGINE
_mysql = None
_POOL = None
LOCK = threading.RLock()        # SQLite only: one writer at a time

# (index name, table, columns): they make searches by blood group, district and status fast.
INDEXES = [
    ("idx_donors_group_area", "donors", "blood_group, area"),
    ("idx_donors_area", "donors", "area"),
    ("idx_requests_status", "requests", "status, hospital_id"),
    ("idx_requests_requester", "requests", "requester_id"),
    ("idx_requests_group_area", "requests", "blood_group, area"),
    ("idx_rd_donor", "request_donors", "donor_id"),
    ("idx_donations_donor", "donations", "donor_id"),
    ("idx_notif_user", "notifications", "user_id, is_read"),
    ("idx_stock_group", "stock", "blood_group"),
    ("idx_sessions_user", "sessions", "user_id"),
    ("idx_otps_phone", "otps", "phone, purpose"),
    ("idx_hospitals_area", "hospitals", "area"),
    ("idx_audit_created", "audit_log", "created_at"),
]


class _Pool:
    def __init__(self, size):
        self.size, self.count = max(1, size), 0
        self.idle, self.lock = queue.LifoQueue(), threading.Lock()

    def get(self):
        try:
            conn = self.idle.get_nowait()
        except queue.Empty:
            with self.lock:
                make = self.count < self.size
                if make:
                    self.count += 1
            if make:
                try:
                    return _new_mysql()
                except Exception:
                    with self.lock:
                        self.count -= 1
                    raise
            conn = self.idle.get(timeout=30)
        try:
            conn.ping(reconnect=True, attempts=2, delay=1)
            return conn
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            try:
                return _new_mysql()
            except Exception:
                with self.lock:
                    self.count -= 1
                raise

    def put(self, conn):
        self.idle.put(conn)


def _new_mysql():
    return _mysql.connect(host=config.MYSQL_HOST, port=config.MYSQL_PORT, user=config.MYSQL_USER,
                          password=config.MYSQL_PASSWORD, database=config.MYSQL_DATABASE, charset="utf8mb4")


def _adapt(sql):
    if ENGINE == "mysql":
        return sql.replace("?", "%s")
    return sql.replace("INSERT IGNORE", "INSERT OR IGNORE")


def execute(sql, args=(), want_id=False):
    """Run one statement. Returns rows (list of dicts) for SELECT, or the new row id if want_id=True."""
    if ENGINE == "mysql":
        conn = _POOL.get()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(_adapt(sql), tuple(args))
            rows = cur.fetchall() if cur.description else []
            conn.commit()
            result = cur.lastrowid if want_id else rows
            cur.close()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            _POOL.put(conn)
            raise
        _POOL.put(conn)
        return result
    with LOCK:
        conn = sqlite3.connect(config.SQLITE_PATH, timeout=15)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute(_adapt(sql), tuple(args))
            rows = [dict(r) for r in cur.fetchall()] if cur.description else []
            conn.commit()
            return cur.lastrowid if want_id else rows
        finally:
            conn.close()


def run(sql, args=()):
    return execute(sql, args)


def insert(sql, args=()):
    return execute(sql, args, want_id=True)


def _render_schema():
    text = open(os.path.join(config.DATABASE_DIR, "schema.sql"), encoding="utf-8").read()
    if ENGINE == "mysql":
        tokens = {"{PK}": "INT AUTO_INCREMENT PRIMARY KEY", "{DT}": "DATETIME",
                  "{ENGINE}": " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"}
    else:
        tokens = {"{PK}": "INTEGER PRIMARY KEY AUTOINCREMENT", "{DT}": "TEXT", "{ENGINE}": ""}
    for key, value in tokens.items():
        text = text.replace(key, value)
    return text


def _create_indexes():
    for name, table, columns in INDEXES:
        try:
            execute("CREATE INDEX %s ON %s (%s)" % (name, table, columns))
        except Exception as error:
            message = str(error).lower()
            if "already exists" in message or "duplicate key name" in message:
                continue
            raise


def setup():
    """Connect (creating the MySQL database if needed), then create all tables and indexes. Returns the engine used."""
    global ENGINE, _mysql, _POOL
    if ENGINE == "mysql":
        try:
            import mysql.connector as mysql_connector
            conn = mysql_connector.connect(host=config.MYSQL_HOST, port=config.MYSQL_PORT,
                                           user=config.MYSQL_USER, password=config.MYSQL_PASSWORD)
            conn.cursor().execute("CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4" % config.MYSQL_DATABASE)
            conn.close()
            _mysql = mysql_connector
            _POOL = _Pool(config.DB_POOL)
        except Exception as error:
            print("MySQL is not available (%s)." % error)
            print("Using SQLite instead. Install MySQL and edit config.env to use MySQL.")
            ENGINE = "sqlite"
    if ENGINE == "sqlite":
        os.makedirs(os.path.dirname(config.SQLITE_PATH) or ".", exist_ok=True)
    schema = re.sub(r"--[^\n]*", "", _render_schema())
    for statement in schema.split(";"):
        if statement.strip():
            execute(statement)
    _create_indexes()
    return ENGINE

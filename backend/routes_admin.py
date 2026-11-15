"""Admin tools: approve or suspend accounts, reports, audit log, SMS log. Made by Krisanu."""
from collections import Counter
from config import GROUPS
from database import run
from notify import notify, audit
from router import route, ApiError

ADMIN = ["admin"]


@route("GET", "/api/admin/pending", ADMIN)
def pending(ctx):
    return run("SELECT u.id, u.name, u.email, u.phone, h.name AS hospital_name, h.area FROM users u "
               "LEFT JOIN hospitals h ON h.id = u.hospital_id WHERE u.status='pending' ORDER BY u.id")


@route("POST", "/api/admin/users/<uid>/approve", ADMIN)
def approve(ctx):
    uid = int(ctx.args["uid"])
    rows = run("SELECT hospital_id FROM users WHERE id=? AND status='pending'", (uid,))
    if not rows:
        raise ApiError("User not found.", 404)
    run("UPDATE users SET status='active' WHERE id=?", (uid,))
    if rows[0]["hospital_id"]:
        run("UPDATE hospitals SET approved=1 WHERE id=?", (rows[0]["hospital_id"],))
    notify(uid, "Your account was approved. You can now use the hospital tools.")
    audit(ctx.user["id"], "account_approved", "user %d" % uid)
    return {"ok": True}


@route("POST", "/api/admin/users/<uid>/suspend", ADMIN)
def suspend(ctx):
    uid = int(ctx.args["uid"])
    if uid == ctx.user["id"]:
        raise ApiError("You cannot suspend your own account.")
    if not run("SELECT id FROM users WHERE id=?", (uid,)):
        raise ApiError("User not found.", 404)
    run("UPDATE users SET status='suspended' WHERE id=?", (uid,))
    run("DELETE FROM sessions WHERE user_id=?", (uid,))
    audit(ctx.user["id"], "account_suspended", "user %d" % uid)
    return {"ok": True}


@route("POST", "/api/admin/users/<uid>/activate", ADMIN)
def activate(ctx):
    uid = int(ctx.args["uid"])
    if not run("SELECT id FROM users WHERE id=?", (uid,)):
        raise ApiError("User not found.", 404)
    run("UPDATE users SET status='active' WHERE id=?", (uid,))
    audit(ctx.user["id"], "account_activated", "user %d" % uid)
    return {"ok": True}


@route("GET", "/api/admin/users", ADMIN)
def users(ctx):
    """Search by name, phone or email (q) and page through the list (offset). 50 per page."""
    q, offset = ctx.q("q").strip(), max(0, int(ctx.q("offset", "0") or 0))
    sql = ("SELECT u.id, u.name, u.email, u.phone, u.role, u.status, h.name AS hospital_name FROM users u "
           "LEFT JOIN hospitals h ON h.id = u.hospital_id")
    args = []
    if q:
        like = "%" + q + "%"
        sql += " WHERE u.name LIKE ? OR u.phone LIKE ? OR u.email LIKE ?"
        args = [like, like, like]
    rows = run(sql + " ORDER BY u.id DESC LIMIT 51 OFFSET %d" % offset, args)
    return {"items": rows[:50], "more": len(rows) > 50}


@route("GET", "/api/admin/report", ADMIN)
def report(ctx):
    demand = {g: 0 for g in GROUPS}
    supply = {g: 0 for g in GROUPS}
    for r in run("SELECT blood_group, SUM(units - units_received) AS n FROM requests WHERE status IN ('pending','verified') GROUP BY blood_group"):
        demand[r["blood_group"]] = int(r["n"] or 0)
    for r in run("SELECT blood_group, SUM(units) AS n FROM stock GROUP BY blood_group"):
        supply[r["blood_group"]] = int(r["n"] or 0)
    statuses = {r["status"]: r["n"] for r in run("SELECT status, COUNT(*) AS n FROM requests GROUP BY status")}
    months = Counter(str(r["donated_on"])[:7] for r in run("SELECT donated_on FROM donations"))
    donors = {r["area"]: r["n"] for r in run("SELECT area, COUNT(*) AS n FROM donors GROUP BY area ORDER BY n DESC LIMIT 8")}
    return {"demand": demand, "supply": supply, "statuses": statuses, "donations_by_month": sorted(months.items())[-6:],
            "donors_by_district": list(donors.items())}


@route("GET", "/api/admin/audit", ADMIN)
def audit_log(ctx):
    return run("SELECT a.id, a.action, a.detail, a.created_at, u.name FROM audit_log a LEFT JOIN users u ON u.id = a.user_id "
               "ORDER BY a.id DESC LIMIT 100")


@route("GET", "/api/admin/sms", ADMIN)
def sms(ctx):
    return run("SELECT id, phone, message, status, created_at FROM sms_log ORDER BY id DESC LIMIT 100")

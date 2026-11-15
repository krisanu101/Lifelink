"""Public pages: meta data, stats, urgent needs board and find blood. Made by Krisanu."""
import datetime
import config
from config import GROUPS, COMPAT, DIVISIONS, DISTRICTS, MIN_AGE, MAX_AGE, MIN_WEIGHT, GAP_MALE, GAP_FEMALE
from database import run
from router import route


def days_left(expires_on):
    return (datetime.date.fromisoformat(str(expires_on)) - datetime.date.today()).days


@route("GET", "/api/health")
def health(ctx):
    run("SELECT 1 AS ok")
    return {"ok": True}


@route("GET", "/api/meta")
def meta(ctx):
    hospitals = run("SELECT id, name, area, upazila FROM hospitals WHERE approved=1 ORDER BY name")
    return {"groups": GROUPS, "compat": COMPAT, "areas": DISTRICTS,
            "divisions": [{"name": name, "districts": districts} for name, districts in DIVISIONS],
            "hospitals": hospitals, "demo_sms": config.SHOW_DEMO_CODES,
            "rules": {"min_age": MIN_AGE, "max_age": MAX_AGE, "min_weight": MIN_WEIGHT,
                      "gap_male": GAP_MALE, "gap_female": GAP_FEMALE}}


@route("GET", "/api/public/stats")
def stats(ctx):
    def count(sql):
        return run(sql)[0]["c"]
    return {"donors": count("SELECT COUNT(*) AS c FROM donors"),
            "donations": count("SELECT COUNT(*) AS c FROM donations"),
            "hospitals": count("SELECT COUNT(*) AS c FROM hospitals WHERE approved=1"),
            "fulfilled": count("SELECT COUNT(*) AS c FROM requests WHERE status='fulfilled'")}


@route("GET", "/api/public/stock")
def public_stock(ctx):
    """Hospitals that have a blood group in stock today. Optional filter: area=<district>."""
    group, area = ctx.q("group"), ctx.q("area")
    today = datetime.date.today().isoformat()
    sql = ("SELECT h.id, h.name, h.area, h.upazila, h.phone, s.blood_group, s.units, s.expires_on FROM stock s "
           "JOIN hospitals h ON h.id = s.hospital_id WHERE h.approved=1 AND s.units>0 AND s.expires_on>=?")
    args = [today]
    if group:
        sql += " AND s.blood_group=?"
        args.append(group)
    if area:
        sql += " AND h.area=?"
        args.append(area)
    rows = run(sql + " ORDER BY s.units DESC", args)
    for r in rows:
        r["expiry_days"] = days_left(r.pop("expires_on"))
    return rows


@route("GET", "/api/public/needs")
def public_needs(ctx):
    """Verified requests that still need blood. No names and no phone numbers are shown."""
    today = datetime.date.today().isoformat()
    rows = run("SELECT r.id, r.blood_group, r.units - r.units_received AS units_left, r.urgency, r.area, r.upazila, r.needed_by, "
               "r.created_at, h.name AS hospital_name, h.phone AS hospital_phone FROM requests r JOIN hospitals h ON h.id = r.hospital_id "
               "WHERE r.status='verified' AND r.units > r.units_received AND (r.needed_by IS NULL OR r.needed_by>=?) "
               "ORDER BY r.id DESC LIMIT 60", (today,))
    area = ctx.q("area")
    if area:
        rows = [r for r in rows if r["area"] == area]
    rank = {"critical": 0, "urgent": 1, "normal": 2}
    rows.sort(key=lambda r: rank.get(r["urgency"], 3))
    return rows[:30]

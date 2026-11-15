"""Blood requests for any logged-in user: create, edit, list, details, notifications. Made by Krisanu."""
import datetime
from config import GROUPS, DISTRICTS
from database import run, insert
from notify import notify, notify_hospital_staff, audit
from auth import now, need_phone, normalize_phone
from router import route, ApiError

OPEN = ("pending", "verified")


def clean_date(value):
    if not value:
        return None
    try:
        day = datetime.date.fromisoformat(str(value))
    except ValueError:
        raise ApiError("Enter a valid date.")
    if day < datetime.date.today():
        raise ApiError("The date cannot be in the past.")
    return day.isoformat()


@route("POST", "/api/requests", "any")
def create_request(ctx):
    b, user = ctx.body, ctx.user
    patient, group, units, hospital_id, area = ctx.need("patient_name", "blood_group", "units", "hospital_id", "area")
    if group not in GROUPS:
        raise ApiError("Choose a blood group.")
    if area not in DISTRICTS:
        raise ApiError("Choose a district.")
    units = int(units)
    if units < 1 or units > 10:
        raise ApiError("Units must be between 1 and 10.")
    urgency = b.get("urgency", "normal")
    if urgency not in ("normal", "urgent", "critical"):
        raise ApiError("Choose an urgency level.")
    if not run("SELECT id FROM hospitals WHERE id=? AND approved=1", (int(hospital_id),)):
        raise ApiError("Hospital not found.")
    phone = need_phone(b.get("contact_phone") or user["phone"])
    own_hospital = user["role"] == "hospital" and user["hospital_id"] == int(hospital_id)
    if not own_hospital and len(run("SELECT id FROM requests WHERE requester_id=? AND status IN ('pending','verified')", (user["id"],))) >= 5:
        raise ApiError("You already have 5 open requests. Please close one before making a new one.")
    status = "verified" if own_hospital else "pending"
    request_id = insert("INSERT INTO requests(requester_id, patient_name, blood_group, units, units_received, hospital_id, area, upazila, "
                        "urgency, needed_by, note, contact_phone, status, created_at) VALUES(?,?,?,?,0,?,?,?,?,?,?,?,?,?)",
                        (user["id"], patient.strip()[:120], group, units, int(hospital_id), area, (b.get("upazila") or "").strip()[:80] or None,
                         urgency, clean_date(b.get("needed_by")), (b.get("note") or "")[:300], phone, status, now()))
    notify_hospital_staff(int(hospital_id), "New %s request #%d: %s, %d unit(s)." % (urgency, request_id, group, units))
    audit(user["id"], "request_created", "request %d" % request_id)
    return {"id": request_id, "status": status}


@route("GET", "/api/requests/mine", "any")
def my_requests(ctx):
    return run("SELECT r.*, h.name AS hospital_name, "
               "(SELECT COUNT(*) FROM request_donors rd WHERE rd.request_id = r.id AND rd.status IN ('accepted','donated')) AS accepted "
               "FROM requests r JOIN hospitals h ON h.id = r.hospital_id WHERE r.requester_id=? ORDER BY r.id DESC", (ctx.user["id"],))


@route("GET", "/api/requests/<rid>", "any")
def request_detail(ctx):
    rid, user = int(ctx.args["rid"]), ctx.user
    rows = run("SELECT r.*, h.name AS hospital_name, h.phone AS hospital_phone FROM requests r JOIN hospitals h ON h.id = r.hospital_id WHERE r.id=?", (rid,))
    if not rows:
        raise ApiError("Request not found.", 404)
    req = rows[0]
    allowed = (user["role"] == "admin" or req["requester_id"] == user["id"]
               or (user["role"] == "hospital" and user["hospital_id"] == req["hospital_id"]))
    if not allowed:
        raise ApiError("You do not have access to this.", 403)
    donors, revealed = [], False
    for row in run("SELECT rd.status, rd.donor_id, u.name, u.phone, d.blood_group, d.area FROM request_donors rd "
                   "JOIN users u ON u.id = rd.donor_id JOIN donors d ON d.user_id = rd.donor_id WHERE rd.request_id=?", (rid,)):
        shown = row["status"] in ("accepted", "donated")
        revealed = revealed or shown
        donors.append({"donor_id": row["donor_id"], "status": row["status"], "blood_group": row["blood_group"], "area": row["area"],
                       "name": row["name"] if shown else row["name"].split()[0], "phone": row["phone"] if shown else None})
    if revealed:
        audit(user["id"], "view_donor_contact", "request %d" % rid)   # every phone number view is recorded
    return {"request": req, "donors": donors}


def own_open_request(ctx):
    rid = int(ctx.args["rid"])
    rows = run("SELECT * FROM requests WHERE id=? AND requester_id=?", (rid, ctx.user["id"]))
    if not rows:
        raise ApiError("Request not found.", 404)
    if rows[0]["status"] not in OPEN:
        raise ApiError("This request is already finished and cannot be changed.")
    return rows[0]


@route("POST", "/api/requests/<rid>/update", "any")
def update_request(ctx):
    req, b = own_open_request(ctx), ctx.body
    units = int(b.get("units") or req["units"])
    if units < max(1, req["units_received"]) or units > 10:
        raise ApiError("Units must be between 1 and 10.")
    urgency = b.get("urgency") or req["urgency"]
    if urgency not in ("normal", "urgent", "critical"):
        raise ApiError("Choose an urgency level.")
    phone = need_phone(b.get("contact_phone") or req["contact_phone"])
    needed_by = clean_date(b["needed_by"]) if "needed_by" in b else req["needed_by"]
    run("UPDATE requests SET units=?, urgency=?, needed_by=?, note=?, contact_phone=? WHERE id=?",
        (units, urgency, needed_by, (b.get("note") if "note" in b else req["note"] or "")[:300], phone, req["id"]))
    notify_hospital_staff(req["hospital_id"], "Request #%d was updated by the patient family." % req["id"])
    return {"ok": True}


@route("POST", "/api/requests/<rid>/close", "any")
def close_request(ctx):
    req = own_open_request(ctx)
    run("UPDATE requests SET status='closed' WHERE id=?", (req["id"],))
    audit(ctx.user["id"], "request_closed", "request %d" % req["id"])
    return {"ok": True}


@route("GET", "/api/notifications", "any")
def notifications(ctx):
    rows = run("SELECT id, message, is_read, created_at FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 50", (ctx.user["id"],))
    return {"items": rows, "unread": sum(1 for r in rows if not r["is_read"])}


@route("POST", "/api/notifications/read", "any")
def mark_read(ctx):
    run("UPDATE notifications SET is_read=1 WHERE user_id=?", (ctx.user["id"],))
    return {"ok": True}

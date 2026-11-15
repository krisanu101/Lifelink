"""Hospital staff tools: verify requests, notify donors, stock, record donations, thalassemia list. Made by Krisanu."""
import datetime
import rules
from config import GROUPS, DISTRICTS, STOCK_SHELF_DAYS
from database import run, insert
from notify import notify, send_sms, sms_text, audit
from auth import now, normalize_phone
from router import route, ApiError
from routes_public import days_left

STAFF = ["hospital"]


def own_request(ctx):
    rows = run("SELECT * FROM requests WHERE id=? AND hospital_id=?", (int(ctx.args["rid"]), ctx.user["hospital_id"]))
    if not rows:
        raise ApiError("Request not found.", 404)
    return rows[0]


def clean_expiry(value):
    if not value:
        return (datetime.date.today() + datetime.timedelta(days=STOCK_SHELF_DAYS)).isoformat()
    try:
        return datetime.date.fromisoformat(str(value)).isoformat()
    except ValueError:
        raise ApiError("Enter a valid date.")


def add_stock(hospital_id, group, units, expires_on=None):
    """Add (or remove) bags. A shelf with no valid bags takes the new expiry; otherwise the nearest expiry is kept."""
    today = datetime.date.today().isoformat()
    new_expiry = clean_expiry(expires_on)
    row = run("SELECT units, expires_on FROM stock WHERE hospital_id=? AND blood_group=?", (hospital_id, group))
    if row:
        old = row[0]
        keep = old["expires_on"] if old["units"] > 0 and str(old["expires_on"]) >= today else new_expiry
        if units > 0 and old["units"] > 0 and str(old["expires_on"]) >= today:
            keep = min(str(old["expires_on"]), new_expiry)
        run("REPLACE INTO stock(hospital_id, blood_group, units, expires_on) VALUES(?,?,?,?)",
            (hospital_id, group, max(0, old["units"] + units), keep))
    else:
        run("INSERT INTO stock(hospital_id, blood_group, units, expires_on) VALUES(?,?,?,?)",
            (hospital_id, group, max(0, units), new_expiry))


def count_received(req, units):
    """Add received units to a request; mark it fulfilled when enough blood has arrived."""
    received = req["units_received"] + units
    status = "fulfilled" if received >= req["units"] else req["status"]
    run("UPDATE requests SET units_received=?, status=? WHERE id=?", (received, status, req["id"]))
    if status == "fulfilled" and req["status"] != "fulfilled":
        notify(req["requester_id"], "Good news: request #%d has received all the blood it needed." % req["id"])


@route("GET", "/api/hospital/requests", STAFF)
def list_requests(ctx):
    return run("SELECT r.*, u.name AS requester_name, "
               "(SELECT COUNT(*) FROM request_donors rd WHERE rd.request_id = r.id) AS asked, "
               "(SELECT COUNT(*) FROM request_donors rd WHERE rd.request_id = r.id AND rd.status IN ('accepted','donated')) AS accepted "
               "FROM requests r JOIN users u ON u.id = r.requester_id "
               "WHERE r.hospital_id=? AND r.status IN ('pending','verified','fulfilled') ORDER BY r.id DESC LIMIT 100", (ctx.user["hospital_id"],))


@route("POST", "/api/hospital/requests/<rid>/verify", STAFF)
def verify(ctx):
    req = own_request(ctx)
    ok = bool(ctx.body.get("ok"))
    if req["status"] != "pending":
        raise ApiError("This request was already handled.")
    run("UPDATE requests SET status=? WHERE id=?", ("verified" if ok else "rejected", req["id"]))
    notify(req["requester_id"], "Your request #%d was %s by the hospital." % (req["id"], "verified" if ok else "rejected"))
    audit(ctx.user["id"], "request_verified" if ok else "request_rejected", "request %d" % req["id"])
    return {"ok": True}


@route("GET", "/api/hospital/requests/<rid>/matches", STAFF)
def matches(ctx):
    req = own_request(ctx)
    scope = ctx.q("scope", "all")
    asked = {r["donor_id"]: r["status"] for r in run("SELECT donor_id, status FROM request_donors WHERE request_id=?", (req["id"],))}
    return [{"donor_id": d["user_id"], "name": d["name"].split()[0], "blood_group": d["blood_group"], "area": d["area"],
             "upazila": d.get("upazila"), "tier": d["tier"], "same_area": d["area"] == req["area"],
             "last_donation": d["last_donation"], "status": asked.get(d["user_id"], "")}
            for d in rules.matching_donors(req["blood_group"], req["area"], req["upazila"], scope)][:100]


@route("POST", "/api/hospital/requests/<rid>/notify", STAFF)
def notify_matches(ctx):
    """Alert the nearest eligible donors. scope: district (same district only), division or all."""
    req = own_request(ctx)
    if req["status"] != "verified":
        raise ApiError("Verify the request first.")
    scope = ctx.body.get("scope") if ctx.body.get("scope") in rules.SCOPES else "division"
    limit = max(1, min(int(ctx.body.get("limit", 5)), 30))
    asked = {r["donor_id"] for r in run("SELECT donor_id FROM request_donors WHERE request_id=?", (req["id"],))}
    chosen = [d for d in rules.matching_donors(req["blood_group"], req["area"], req["upazila"], scope) if d["user_id"] not in asked][:limit]
    hospital = run("SELECT name FROM hospitals WHERE id=?", (req["hospital_id"],))[0]["name"]
    text = "%s blood is needed at %s (%d unit(s), %s). Please log in to LifeLink to answer." % (req["blood_group"], hospital, req["units"], req["urgency"])
    sms = sms_text("alert", group=req["blood_group"], hospital=hospital, district=req["area"], units=req["units"], urgency=req["urgency"])
    for donor in chosen:
        run("INSERT INTO request_donors(request_id, donor_id, status, updated_at) VALUES(?,?,'asked',?)", (req["id"], donor["user_id"], now()))
        notify(donor["user_id"], text)
        send_sms(donor["phone"], sms)
    audit(ctx.user["id"], "donors_notified", "request %d, %d donors, %s" % (req["id"], len(chosen), scope))
    return {"notified": len(chosen)}


@route("POST", "/api/hospital/requests/<rid>/issue", STAFF)
def issue_blood(ctx):
    req = own_request(ctx)
    units = int(ctx.body.get("units", 0))
    today = datetime.date.today().isoformat()
    row = run("SELECT units FROM stock WHERE hospital_id=? AND blood_group=? AND expires_on>=?", (req["hospital_id"], req["blood_group"], today))
    if units < 1 or not row or row[0]["units"] < units:
        raise ApiError("Not enough stock.")
    add_stock(req["hospital_id"], req["blood_group"], -units)
    count_received(req, units)
    audit(ctx.user["id"], "blood_issued", "request %d, %d units" % (req["id"], units))
    return {"ok": True}


@route("POST", "/api/hospital/donations", STAFF)
def record_donation(ctx):
    """Record a donation. The donor is found by phone number or by ID."""
    body = ctx.body
    if body.get("donor_phone"):
        phone = normalize_phone(body["donor_phone"])
        found = run("SELECT u.id FROM users u JOIN donors d ON d.user_id = u.id WHERE u.phone=?", (phone,)) if phone else []
        donor_id = found[0]["id"] if found else None
    else:
        donor_id = int(body["donor_id"]) if body.get("donor_id") else None
    donor = run("SELECT * FROM donors WHERE user_id=?", (donor_id,)) if donor_id else []
    if not donor:
        raise ApiError("Donor not found.")
    donor = donor[0]
    units = max(1, min(int(body.get("units") or 1), 2))
    problems = rules.eligibility(donor)
    if problems:
        raise ApiError("This donor cannot donate today: " + "; ".join(problems))
    hospital_id, req = ctx.user["hospital_id"], None
    if body.get("request_id"):
        rows = run("SELECT * FROM requests WHERE id=? AND hospital_id=?", (int(body["request_id"]), hospital_id))
        if not rows:
            raise ApiError("Request not found.")
        req = rows[0]
    today = datetime.date.today().isoformat()
    insert("INSERT INTO donations(donor_id, hospital_id, request_id, units, donated_on) VALUES(?,?,?,?,?)",
           (donor["user_id"], hospital_id, req["id"] if req else None, units, today))
    run("UPDATE donors SET last_donation=?, reminder_sent=0 WHERE user_id=?", (today, donor["user_id"]))   # blocked for the next 120/180 days
    add_stock(hospital_id, donor["blood_group"], units)
    if req:
        run("UPDATE request_donors SET status='donated', updated_at=? WHERE request_id=? AND donor_id=?", (now(), req["id"], donor["user_id"]))
        count_received(req, units)
    notify(donor["user_id"], "Thank you for donating blood today. Your certificate is ready in your dashboard.")
    audit(ctx.user["id"], "donation_recorded", "donor %d, %d units" % (donor["user_id"], units))
    return {"ok": True}


@route("GET", "/api/hospital/stock", STAFF)
def stock(ctx):
    rows = {r["blood_group"]: r for r in run("SELECT * FROM stock WHERE hospital_id=?", (ctx.user["hospital_id"],))}
    out = []
    for g in GROUPS:
        r = rows.get(g)
        out.append({"blood_group": g, "units": r["units"] if r else 0, "expiry_days": days_left(r["expires_on"]) if r and r["units"] else 0,
                    "expires_on": str(r["expires_on"]) if r and r["units"] else ""})
    return out


@route("POST", "/api/hospital/stock/adjust", STAFF)
def adjust_stock(ctx):
    """delta = bags to add (or remove, if negative); expires_on = expiry date of the new bags; discard = true removes expired bags."""
    group, = ctx.need("blood_group")
    if group not in GROUPS:
        raise ApiError("Choose a blood group.")
    if ctx.body.get("discard"):
        run("UPDATE stock SET units=0 WHERE hospital_id=? AND blood_group=?", (ctx.user["hospital_id"], group))
        audit(ctx.user["id"], "stock_discarded", group)
        return {"ok": True}
    delta = int(ctx.body.get("delta") or 0)
    if delta == 0 or abs(delta) > 500:
        raise ApiError("Enter how many bags to add or remove.")
    add_stock(ctx.user["hospital_id"], group, delta, ctx.body.get("expires_on"))
    return {"ok": True}


@route("GET", "/api/hospital/profile", STAFF)
def hospital_profile(ctx):
    return run("SELECT id, name, area, upazila, address, phone FROM hospitals WHERE id=?", (ctx.user["hospital_id"],))[0]


@route("POST", "/api/hospital/profile", STAFF)
def update_hospital_profile(ctx):
    b = ctx.body
    if b.get("area") not in DISTRICTS:
        raise ApiError("Choose a district.")
    run("UPDATE hospitals SET area=?, upazila=?, address=?, phone=? WHERE id=?",
        (b["area"], (b.get("upazila") or "").strip()[:80] or None, (b.get("address") or "").strip()[:200], (b.get("phone") or "").strip()[:30], ctx.user["hospital_id"]))
    return {"ok": True}


@route("GET", "/api/hospital/thal", STAFF)
def thal_list(ctx):
    h = run("SELECT area, upazila FROM hospitals WHERE id=?", (ctx.user["hospital_id"],))[0]
    out = []
    for p in run("SELECT * FROM thal_patients WHERE hospital_id=? ORDER BY next_date", (ctx.user["hospital_id"],)):
        p["regular_donors"] = [{"donor_id": d["user_id"], "name": d["name"].split()[0]} for d in rules.matching_donors(p["blood_group"], h["area"], h["upazila"], "division")[:3]]
        out.append(p)
    return out


@route("POST", "/api/hospital/thal", STAFF)
def thal_add(ctx):
    name, group, next_date, weeks = ctx.need("name", "blood_group", "next_date", "frequency_weeks")
    if group not in GROUPS:
        raise ApiError("Choose a blood group.")
    insert("INSERT INTO thal_patients(hospital_id, name, blood_group, next_date, frequency_weeks, notes) VALUES(?,?,?,?,?,?)",
           (ctx.user["hospital_id"], name.strip(), group, clean_expiry(next_date), max(1, int(weeks)), (ctx.body.get("notes") or "")[:200]))
    return {"ok": True}


@route("POST", "/api/hospital/thal/<pid>/done", STAFF)
def thal_done(ctx):
    rows = run("SELECT * FROM thal_patients WHERE id=? AND hospital_id=?", (int(ctx.args["pid"]), ctx.user["hospital_id"]))
    if not rows:
        raise ApiError("Patient not found.", 404)
    nxt = datetime.date.fromisoformat(str(rows[0]["next_date"])) + datetime.timedelta(weeks=rows[0]["frequency_weeks"])
    run("UPDATE thal_patients SET next_date=? WHERE id=?", (nxt.isoformat(), rows[0]["id"]))
    return {"next_date": nxt.isoformat()}

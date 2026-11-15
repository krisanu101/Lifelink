"""Donor dashboard: profile, inbox of requests, accept, decline or cancel. Made by Krisanu."""
import config, rules
from config import DISTRICTS
from database import run
from notify import notify, notify_hospital_staff, audit, send_sms, sms_text
from auth import now, need_phone
from router import route, ApiError
from routes_auth import clean_email


@route("GET", "/api/donor/profile", ["donor"])
def profile(ctx):
    uid = ctx.user["id"]
    donor = run("SELECT d.*, u.name, u.email, u.phone FROM donors d JOIN users u ON u.id = d.user_id "
                "WHERE d.user_id=?", (uid,))[0]
    history = run("SELECT n.id, n.units, n.donated_on, h.name AS hospital FROM donations n "
                  "JOIN hospitals h ON h.id = n.hospital_id WHERE n.donor_id=? ORDER BY n.donated_on DESC", (uid,))
    reasons = rules.eligibility(donor)
    nxt = rules.next_eligible(donor["last_donation"], donor["gender"])
    return {"donor": donor, "age": rules.age_of(donor["birth_date"]), "reasons": reasons,
            "eligible": not reasons, "next_eligible": nxt.isoformat() if nxt else None, "history": history}


@route("POST", "/api/donor/profile", ["donor"])
def update_profile(ctx):
    b, uid = ctx.body, ctx.user["id"]
    if "available" in b:
        run("UPDATE donors SET available=? WHERE user_id=?", (1 if b["available"] else 0, uid))
    if b.get("area"):
        if b["area"] not in DISTRICTS:
            raise ApiError("Choose a district.")
        run("UPDATE donors SET area=? WHERE user_id=?", (b["area"], uid))
    if "upazila" in b:
        run("UPDATE donors SET upazila=? WHERE user_id=?", ((b["upazila"] or "").strip()[:80] or None, uid))
    if b.get("weight"):
        run("UPDATE donors SET weight=? WHERE user_id=?", (int(b["weight"]), uid))
    if b.get("name"):
        run("UPDATE users SET name=? WHERE id=?", (b["name"].strip()[:120], uid))
    if b.get("phone"):
        phone = need_phone(b["phone"])
        if run("SELECT id FROM users WHERE phone=? AND id<>?", (phone, uid)):
            raise ApiError("This phone number is already registered. Please log in.")
        run("UPDATE users SET phone=? WHERE id=?", (phone, uid))
    if "email" in b:
        email = clean_email(b["email"])
        if email and run("SELECT id FROM users WHERE email=? AND id<>?", (email, uid)):
            raise ApiError("This email is already registered.")
        run("UPDATE users SET email=? WHERE id=?", (email, uid))
    return {"ok": True}


@route("GET", "/api/donor/inbox", ["donor"])
def inbox(ctx):
    return run("SELECT r.id, r.patient_name, r.blood_group, r.units, r.area, r.upazila, r.urgency, r.needed_by, r.status AS request_status, "
               "h.name AS hospital_name, h.phone AS hospital_phone, rd.status AS my_status FROM request_donors rd "
               "JOIN requests r ON r.id = rd.request_id JOIN hospitals h ON h.id = r.hospital_id "
               "WHERE rd.donor_id=? ORDER BY r.id DESC", (ctx.user["id"],))


@route("POST", "/api/donor/respond", ["donor"])
def respond(ctx):
    request_id, = ctx.need("request_id")
    accept = bool(ctx.body.get("accept"))
    uid = ctx.user["id"]
    row = run("SELECT rd.status, r.requester_id, r.hospital_id, r.blood_group, r.status AS request_status FROM request_donors rd "
              "JOIN requests r ON r.id = rd.request_id WHERE rd.request_id=? AND rd.donor_id=?", (int(request_id), uid))
    if not row or row[0]["status"] != "asked":
        raise ApiError("There is nothing to answer for this request.")
    if row[0]["request_status"] != "verified":
        raise ApiError("This request is no longer open.")
    if accept:
        donor = run("SELECT * FROM donors WHERE user_id=?", (uid,))[0]
        problems = rules.eligibility(donor)
        if problems:
            raise ApiError("You cannot donate right now: " + "; ".join(problems))
    run("UPDATE request_donors SET status=?, updated_at=? WHERE request_id=? AND donor_id=?",
        ("accepted" if accept else "declined", now(), int(request_id), uid))
    if accept:
        notify(row[0]["requester_id"], "A donor agreed to help with request #%s (%s). Open the request to see contact details." % (request_id, row[0]["blood_group"]))
        notify_hospital_staff(row[0]["hospital_id"], "A donor accepted request #%s." % request_id)
        phone = run("SELECT phone FROM users WHERE id=?", (row[0]["requester_id"],))[0]["phone"]
        send_sms(phone, sms_text("accepted", id=request_id))
    audit(uid, "donor_accept" if accept else "donor_decline", "request %s" % request_id)
    return {"ok": True}


@route("POST", "/api/donor/cancel", ["donor"])
def cancel(ctx):
    """A donor who accepted but cannot come any more. The hospital and the requester are told, so they can ask someone else."""
    request_id, = ctx.need("request_id")
    uid = ctx.user["id"]
    row = run("SELECT rd.status, r.requester_id, r.hospital_id FROM request_donors rd JOIN requests r ON r.id = rd.request_id "
              "WHERE rd.request_id=? AND rd.donor_id=?", (int(request_id), uid))
    if not row or row[0]["status"] != "accepted":
        raise ApiError("There is nothing to cancel for this request.")
    run("UPDATE request_donors SET status='cancelled', updated_at=? WHERE request_id=? AND donor_id=?", (now(), int(request_id), uid))
    notify(row[0]["requester_id"], "A donor can no longer help with request #%s." % request_id)
    notify_hospital_staff(row[0]["hospital_id"], "A donor can no longer help with request #%s. You can alert more donors." % request_id)
    audit(uid, "donor_cancel", "request %s" % request_id)
    return {"ok": True}

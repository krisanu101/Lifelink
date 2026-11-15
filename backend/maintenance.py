"""Background housekeeping: closes old requests, removes old sessions, sends reminders. Made by Krisanu.
It runs when the server starts and then every 30 minutes. Daily reminders are sent once per day."""
import datetime, threading, time
import auth, config, rules
from database import run
from notify import notify, notify_hospital_staff, audit


def expire_requests():
    today = datetime.date.today().isoformat()
    stale = (datetime.date.today() - datetime.timedelta(days=config.REQUEST_STALE_DAYS)).isoformat() + " 00:00:00"
    rows = run("SELECT id, requester_id, status, needed_by, created_at FROM requests WHERE status IN ('pending','verified')")
    for r in rows:
        late = r["needed_by"] and str(r["needed_by"]) < today
        old = r["status"] == "pending" and str(r["created_at"])[:19] < stale
        if late or old:
            run("UPDATE requests SET status='expired' WHERE id=?", (r["id"],))
            notify(r["requester_id"], "Request #%d has expired. You can make a new request if blood is still needed." % r["id"])


def clean_old_rows():
    run("DELETE FROM sessions WHERE created_at<?", (auth.ago(config.SESSION_DAYS * 86400),))
    run("DELETE FROM otps WHERE created_at<?", (auth.ago(86400),))


def donor_reminders():
    """Tell donors when they can give blood again (once per donation)."""
    for d in run("SELECT user_id, last_donation, gender FROM donors WHERE reminder_sent=0 AND last_donation IS NOT NULL"):
        nxt = rules.next_eligible(d["last_donation"], d["gender"])
        if nxt and nxt <= datetime.date.today():
            notify(d["user_id"], "You can donate blood again now. Thank you for being a donor!")
            run("UPDATE donors SET reminder_sent=1 WHERE user_id=?", (d["user_id"],))


def hospital_reminders():
    today = datetime.date.today()
    soon = (today + datetime.timedelta(days=3)).isoformat()
    for p in run("SELECT hospital_id, name, next_date FROM thal_patients WHERE next_date<=?", (soon,)):
        notify_hospital_staff(p["hospital_id"], "Regular patient %s needs a transfusion on %s." % (p["name"], p["next_date"]))
    for s in run("SELECT hospital_id, blood_group, units, expires_on FROM stock WHERE units>0 AND expires_on<=?", (soon,)):
        word = "expired" if str(s["expires_on"]) < today.isoformat() else "expires soon"
        notify_hospital_staff(s["hospital_id"], "%s blood (%d unit(s)) %s: %s." % (s["blood_group"], s["units"], word, s["expires_on"]))


def run_once():
    expire_requests()
    clean_old_rows()
    donor_reminders()
    key = datetime.date.today().isoformat()
    if not run("SELECT id FROM audit_log WHERE action='daily_job' AND detail=?", (key,)):
        audit(None, "daily_job", key)
        hospital_reminders()


def start():
    def loop():
        while True:
            try:
                run_once()
            except Exception as error:               # never let housekeeping stop the server
                print("Maintenance problem:", repr(error))
            time.sleep(1800)
    threading.Thread(target=loop, daemon=True).start()

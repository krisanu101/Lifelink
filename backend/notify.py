"""In-app notifications, SMS sending and the audit log. Made by Krisanu.
SMS_PROVIDER in config.env: demo (only stored in the SMS log), greenweb, bulksmsbd or custom."""
import threading, urllib.parse, urllib.request
import config
from auth import now
from database import run, insert


def notify(user_id, message):
    run("INSERT INTO notifications(user_id, message, is_read, created_at) VALUES(?,?,0,?)", (user_id, message[:300], now()))


def audit(user_id, action, detail=""):
    run("INSERT INTO audit_log(user_id, action, detail, created_at) VALUES(?,?,?,?)", (user_id, action, detail[:300], now()))


def notify_hospital_staff(hospital_id, message):
    for row in run("SELECT id FROM users WHERE role='hospital' AND hospital_id=? AND status='active'", (hospital_id,)):
        notify(row["id"], message)


def notify_admins(message):
    for row in run("SELECT id FROM users WHERE role='admin'"):
        notify(row["id"], message)


# ---------- SMS ----------
def sms_text(kind, **v):
    """Short SMS texts. English by default; set SMS_LANG=bn for Bangla (the gateway must accept Unicode SMS)."""
    bn = config.SMS_LANG == "bn"
    if kind == "alert":
        return ("লাইফলিংক: %(group)s রক্ত দরকার, %(hospital)s, %(district)s (%(units)s ব্যাগ, %(urgency)s)। সাড়া দিতে লগইন করুন।" if bn else
                "LifeLink: %(group)s blood needed at %(hospital)s, %(district)s (%(units)s bag, %(urgency)s). Log in to reply.") % v
    if kind == "accepted":
        return ("লাইফলিংক: অনুরোধ #%(id)s-এ একজন ডোনার রাজি হয়েছেন। যোগাযোগের তথ্য দেখতে লগইন করুন।" if bn else
                "LifeLink: a donor agreed to help with request #%(id)s. Log in to see the contact.") % v
    if kind == "otp":
        return ("লাইফলিংক কোড: %(code)s। %(min)s মিনিট চলবে। কাউকে বলবেন না।" if bn else
                "LifeLink code: %(code)s. Valid for %(min)s minutes. Do not share it.") % v
    return v.get("text", "")


def send_sms(phone, message):
    """Store the SMS in sms_log and, unless SMS_PROVIDER=demo, send it in the background."""
    message = message[:300]
    live = config.SMS_PROVIDER != "demo"
    sms_id = insert("INSERT INTO sms_log(phone, message, status, created_at) VALUES(?,?,?,?)",
                    (phone, message, "queued" if live else "logged", now()))
    if live:
        threading.Thread(target=_deliver, args=(sms_id, phone, message), daemon=True).start()
    return sms_id


def _deliver(sms_id, phone, message):
    to = "88" + phone                                  # gateways want 8801XXXXXXXXX
    status = "sent"
    try:
        key, sender, provider = config.SMS_API_KEY, config.SMS_SENDER_ID, config.SMS_PROVIDER
        if provider == "greenweb":
            data = urllib.parse.urlencode({"token": key, "to": to, "message": message}).encode()
            reply = _open(urllib.request.Request("https://api.greenweb.com.bd/api.php", data=data))
            ok = reply.strip().lower().startswith("ok")
        elif provider == "bulksmsbd":
            data = urllib.parse.urlencode({"api_key": key, "type": "text", "number": to, "senderid": sender,
                                           "message": message}).encode()
            reply = _open(urllib.request.Request("http://bulksmsbd.net/api/smsapi", data=data))
            ok = "202" in reply
        elif provider == "custom":
            url = config.SMS_URL.replace("{to}", urllib.parse.quote(to)).replace("{key}", urllib.parse.quote(key)) \
                                .replace("{message}", urllib.parse.quote(message))
            reply = _open(urllib.request.Request(url))
            ok = True
        else:
            reply, ok = "unknown SMS_PROVIDER", False
        if not ok:
            status = "failed: " + reply.strip().replace("\n", " ")[:60]
    except Exception as error:
        status = "failed: " + str(error)[:60]
    run("UPDATE sms_log SET status=? WHERE id=?", (status, sms_id))


def _open(request):
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", "replace")

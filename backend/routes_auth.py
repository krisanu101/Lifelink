"""Accounts: register, log in (phone or email, or SMS code), forgot password, change password. Made by Krisanu."""
import auth, config, rules
from config import GROUPS, DISTRICTS
from database import run, insert
from notify import notify_admins, send_sms, sms_text, audit
from router import route, ApiError


def clean_email(raw):
    email = (raw or "").strip().lower()
    if not email:
        return None
    if not auth.EMAIL.match(email):
        raise ApiError("Enter a valid email address.")
    return email


def need_district(value):
    if value not in DISTRICTS:
        raise ApiError("Choose a district.")
    return value


@route("GET", "/api/auth/me")
def me(ctx):
    return {"user": ctx.user}


@route("POST", "/api/auth/register")
def register(ctx):
    b = ctx.body
    role = b.get("role")
    if role not in ("donor", "requester", "hospital"):
        raise ApiError("Choose an account type.")
    name, phone, password = ctx.need("name", "phone", "password")
    phone, email = auth.need_phone(phone), clean_email(b.get("email"))
    auth.check_new_password(password)
    if run("SELECT id FROM users WHERE phone=?", (phone,)):
        raise ApiError("This phone number is already registered. Please log in.")
    if email and run("SELECT id FROM users WHERE email=?", (email,)):
        raise ApiError("This email is already registered.")

    hospital_id, status, donor = None, "active", None
    if role == "donor":
        group, gender, birth, weight, area = ctx.need("blood_group", "gender", "birth_date", "weight", "area")
        need_district(area)
        if group not in GROUPS or gender not in ("male", "female"):
            raise ApiError("Check blood group and gender.")
        try:
            weight = int(weight)
        except ValueError:
            raise ApiError("Weight must be at least %d kg" % config.MIN_WEIGHT)
        last = b.get("last_donation") or None
        problems = rules.registration_problems(birth, weight, last, gender, b.get("consent"), b.get("health_risk"))
        if problems:
            raise ApiError("You cannot register as a donor right now: " + "; ".join(problems))
        donor = (group, gender, birth, weight, area, (b.get("upazila") or "").strip()[:80] or None, last)
    if role == "hospital":
        status = "pending"
        if b.get("hospital_id"):
            if not run("SELECT id FROM hospitals WHERE id=?", (int(b["hospital_id"]),)):
                raise ApiError("Hospital not found.")
            hospital_id = int(b["hospital_id"])
        else:
            hname, harea = ctx.need("new_hospital_name", "new_hospital_area")
            need_district(harea)
            hospital_id = insert("INSERT INTO hospitals(name, area, upazila, address, phone, approved) VALUES(?,?,?,?,?,0)",
                                 (hname.strip()[:150], harea, (b.get("upazila") or "").strip()[:80] or None, "", phone))

    user_id = insert("INSERT INTO users(name, email, phone, pass_hash, role, hospital_id, status, created_at) VALUES(?,?,?,?,?,?,?,?)",
                     (name.strip()[:120], email, phone, auth.hash_password(password), role, hospital_id, status, auth.now()))
    if donor:
        run("INSERT INTO donors(user_id, blood_group, gender, birth_date, weight, area, upazila, last_donation, available) "
            "VALUES(?,?,?,?,?,?,?,?,1)", (user_id,) + donor)
    if role == "hospital":
        notify_admins("New hospital staff account waiting for approval: " + name)
        return {"pending": True}
    ctx.set_cookie = auth.new_session(user_id)
    return {"user": auth.public_user(user_id)}


def finish_login(ctx, row):
    if row["status"] == "pending":
        raise ApiError("Your account is waiting for admin approval.", 403)
    if row["status"] != "active":
        raise ApiError("This account is suspended. Please contact the LifeLink team.", 403)
    ctx.set_cookie = auth.new_session(row["id"])
    return {"user": auth.public_user(row["id"])}


@route("POST", "/api/auth/login")
def login(ctx):
    who, password = ctx.need("login", "password")
    key = ctx.ip + ":" + str(who).strip().lower()
    auth.check_rate(key)
    row = auth.find_user(who)
    if not row or not auth.check_password(password, row["pass_hash"]):
        auth.record_fail(key)
        raise ApiError("Wrong phone, email or password.", 401)
    auth.clear_fails(key)
    if auth.needs_rehash(row["pass_hash"]):          # quietly upgrade accounts made with the older, weaker setting
        run("UPDATE users SET pass_hash=? WHERE id=?", (auth.hash_password(password), row["id"]))
    return finish_login(ctx, row)


@route("POST", "/api/auth/otp/send")
def otp_send(ctx):
    """Send a 6-digit code by SMS. purpose is "login" or "reset". The answer is the same whether or not the phone is registered."""
    phone = auth.need_phone(ctx.body.get("phone"))
    purpose = ctx.body.get("purpose")
    if purpose not in ("login", "reset"):
        raise ApiError("Bad request.")
    auth.check_rate("otp:" + ctx.ip, limit=10, window=3600)
    auth.record_fail("otp:" + ctx.ip)
    result = {"ok": True}
    if run("SELECT id FROM users WHERE phone=?", (phone,)):
        code = auth.create_otp(phone, purpose)
        send_sms(phone, sms_text("otp", code=code, min=config.OTP_MINUTES))
        if config.SHOW_DEMO_CODES:                   # demo mode only: no real SMS exists, so show the code on screen
            result["demo_code"] = code
    return result


@route("POST", "/api/auth/otp/login")
def otp_login(ctx):
    phone, code = auth.need_phone(ctx.body.get("phone")), ctx.body.get("code")
    key = "otpcheck:" + phone
    auth.check_rate(key, limit=6, window=600)
    row = auth.find_user(phone)
    if not row or not auth.check_otp(phone, "login", code):
        auth.record_fail(key)
        raise ApiError("The code is wrong or has expired.", 401)
    return finish_login(ctx, row)


@route("POST", "/api/auth/reset")
def reset_password(ctx):
    phone, code, password = auth.need_phone(ctx.body.get("phone")), ctx.body.get("code"), ctx.body.get("password")
    auth.check_new_password(password)
    key = "otpcheck:" + phone
    auth.check_rate(key, limit=6, window=600)
    row = auth.find_user(phone)
    if not row or not auth.check_otp(phone, "reset", code):
        auth.record_fail(key)
        raise ApiError("The code is wrong or has expired.", 401)
    run("UPDATE users SET pass_hash=? WHERE id=?", (auth.hash_password(password), row["id"]))
    auth.end_all_sessions(row["id"])
    audit(row["id"], "password_reset", "")
    return finish_login(ctx, row)


@route("POST", "/api/auth/change-password", "any")
def change_password(ctx):
    old, new = ctx.need("old_password", "new_password")
    auth.check_new_password(new)
    row = run("SELECT pass_hash FROM users WHERE id=?", (ctx.user["id"],))[0]
    if not auth.check_password(old, row["pass_hash"]):
        raise ApiError("Your current password is wrong.", 401)
    run("UPDATE users SET pass_hash=? WHERE id=?", (auth.hash_password(new), ctx.user["id"]))
    return {"ok": True}


@route("POST", "/api/auth/delete-account", "any")
def delete_account(ctx):
    """Remove the person's details for good. Donation and request records stay, without a name or phone number."""
    password, = ctx.need("password")
    uid = ctx.user["id"]
    if ctx.user["role"] == "admin":
        raise ApiError("An admin account cannot be deleted here.")
    if not auth.check_password(password, run("SELECT pass_hash FROM users WHERE id=?", (uid,))[0]["pass_hash"]):
        raise ApiError("Your current password is wrong.", 401)
    run("UPDATE users SET name='Deleted user', email=NULL, phone=?, pass_hash='x', status='deleted' WHERE id=?", ("d%d" % uid, uid))
    run("UPDATE donors SET available=0, upazila=NULL WHERE user_id=?", (uid,))
    run("DELETE FROM notifications WHERE user_id=?", (uid,))
    auth.end_all_sessions(uid)
    audit(uid, "account_deleted", "")
    ctx.clear_cookie = True
    return {"ok": True}


@route("POST", "/api/auth/logout", "any")
def logout(ctx):
    ctx.clear_cookie = True
    return {"ok": True}

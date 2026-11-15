"""Sample data so the app is not empty on first run, plus the first real admin. Made by Krisanu.
Demo logins are listed in README.md. Everything here is fictional. For a real site set SEED_DEMO=0 in config.env
and create the first admin with ADMIN_PHONE and ADMIN_PASSWORD."""
import datetime
import auth, config
from database import run, insert

TODAY = datetime.date.today()


def days_ago(n):
    return (TODAY - datetime.timedelta(days=n)).isoformat()


def user(name, email, phone, password, role, hospital_id=None):
    return insert("INSERT INTO users(name, email, phone, pass_hash, role, hospital_id, status, created_at) VALUES(?,?,?,?,?,?,'active',?)",
                  (name, email, phone, auth.hash_password(password), role, hospital_id, auth.now()))


def ensure_admin():
    """Create the first admin from ADMIN_PHONE / ADMIN_PASSWORD when the database has no admin yet."""
    if run("SELECT id FROM users WHERE role='admin'") or not (config.ADMIN_PHONE and config.ADMIN_PASSWORD):
        return False
    phone = auth.normalize_phone(config.ADMIN_PHONE)
    if not phone or len(config.ADMIN_PASSWORD) < config.MIN_PASSWORD:
        print("ADMIN_PHONE or ADMIN_PASSWORD is not valid, so no admin was created.")
        return False
    user(config.ADMIN_NAME, None, phone, config.ADMIN_PASSWORD, "admin")
    print("First admin created. Log in with phone %s." % phone)
    return True


def seed_if_empty():
    if run("SELECT COUNT(*) AS c FROM users")[0]["c"] or not config.SEED_DEMO:
        return False
    hospitals = [("City Central Hospital (sample)", "Dhaka", "Dhanmondi", "01700100001"),
                 ("Green Crescent Medical (sample)", "Dhaka", "Mirpur", "01700100002"),
                 ("Lakeside Clinic (sample)", "Gazipur", "Gazipur Sadar", "01700100003"),
                 ("Port City Hospital (sample)", "Chattogram", "Panchlaish", "01700100004"),
                 ("Rajshahi Care Centre (sample)", "Rajshahi", "Boalia", "01700100005")]
    hids = [insert("INSERT INTO hospitals(name, area, upazila, address, phone, approved) VALUES(?,?,?,?,?,1)", (n, a, u, "", p)) for n, a, u, p in hospitals]

    user("Site Admin", "admin@lifelink.local", "01700000000", "admin123", "admin")
    for i, hid in enumerate(hids[:3], 1):
        user("Hospital Staff %d" % i, "hospital%d@lifelink.local" % i, "0170020000%d" % i, "hospital123", "hospital", hid)
    requester = user("Rahim Requester", "requester@lifelink.local", "01700300001", "user123", "requester")

    donors = [("Rakib Hasan", "male", "B+", "Dhaka", "Dhanmondi", 1998, 68, 200), ("Tania Akter", "female", "O+", "Dhaka", "Mirpur", 1999, 54, 230),
              ("Sabbir Ahmed", "male", "A+", "Dhaka", "Uttara", 1995, 72, 30), ("Nadim Khan", "male", "O-", "Dhaka", "Dhanmondi", 1992, 75, 150),
              ("Mim Rahman", "female", "AB+", "Dhaka", "Mohammadpur", 2000, 56, None), ("Fahim Islam", "male", "B+", "Dhaka", "Mirpur", 1997, 66, 140),
              ("Nusrat Jahan", "female", "A-", "Gazipur", "Tongi", 1996, 58, 400), ("Imran Hossain", "male", "O+", "Narayanganj", "Fatullah", 1990, 80, 125),
              ("Sadia Sultana", "female", "B-", "Chattogram", "Panchlaish", 2001, 52, None), ("Arif Chowdhury", "male", "AB-", "Sylhet", "Zindabazar", 1994, 70, 300),
              ("Jahid Hasan", "male", "B+", "Gazipur", "Gazipur Sadar", 1993, 71, 180), ("Rima Khatun", "female", "O+", "Rajshahi", "Boalia", 1998, 55, None)]
    donor_ids = []
    for i, (name, gender, group, district, upazila, year, weight, ago) in enumerate(donors, 1):
        uid = user(name, "donor%d@lifelink.local" % i, "01700400%03d" % i, "donor123", "donor")
        run("INSERT INTO donors(user_id, blood_group, gender, birth_date, weight, area, upazila, last_donation, available) VALUES(?,?,?,?,?,?,?,?,1)",
            (uid, group, gender, "%d-06-15" % year, weight, district, upazila, days_ago(ago) if ago else None))
        donor_ids.append(uid)

    groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    levels = [[14, 3, 9, 2, 16, 4, 6, 1], [8, 6, 11, 3, 12, 5, 4, 2], [10, 2, 7, 1, 13, 3, 5, 2], [9, 4, 6, 2, 10, 3, 3, 1], [7, 2, 8, 1, 9, 2, 2, 1]]
    expiry = [20, 3, 14, 9, 25, 6, 12, 2]
    for hid, units in zip(hids, levels):
        for g, u, e in zip(groups, units, expiry):
            run("INSERT INTO stock(hospital_id, blood_group, units, expires_on) VALUES(?,?,?,?)", (hid, g, u, (TODAY + datetime.timedelta(days=e)).isoformat()))

    for n, g, d, w, note in [("Thalassemia patient A (sample)", "B+", 6, 3, "Needs 1 bag"), ("Thalassemia patient B (sample)", "O+", 12, 4, ""),
                             ("Thalassemia patient C (sample)", "A+", 20, 3, "")]:
        run("INSERT INTO thal_patients(hospital_id, name, blood_group, next_date, frequency_weeks, notes) VALUES(?,?,?,?,?,?)",
            (hids[0], n, g, (TODAY + datetime.timedelta(days=d)).isoformat(), w, note))

    for g, units, status, got, urgency in [("B+", 2, "verified", 0, "urgent"), ("O-", 1, "verified", 0, "critical"), ("A+", 3, "fulfilled", 3, "normal"), ("O+", 2, "fulfilled", 2, "normal")]:
        run("INSERT INTO requests(requester_id, patient_name, blood_group, units, units_received, hospital_id, area, upazila, urgency, "
            "needed_by, note, contact_phone, status, created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (requester, "Sample patient", g, units, got, hids[0], "Dhaka", "Dhanmondi", urgency, None, "", "01700300001", status, auth.now()))
    for i, ago in enumerate([20, 45, 75, 110, 140, 170]):
        run("INSERT INTO donations(donor_id, hospital_id, request_id, units, donated_on) VALUES(?,?,?,?,?)",
            (donor_ids[i % len(donor_ids)], hids[i % 3], None, 1, days_ago(ago)))
    return True

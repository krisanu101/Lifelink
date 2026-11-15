"""Donor eligibility and blood group matching. Made by Krisanu."""
import datetime
from config import COMPAT, MIN_AGE, MAX_AGE, MIN_WEIGHT, GAP_MALE, GAP_FEMALE, DIVISION_OF
from database import run


def today():
    return datetime.date.today()


def age_of(birth_date):
    born = datetime.date.fromisoformat(str(birth_date))
    now = today()
    return now.year - born.year - ((now.month, now.day) < (born.month, born.day))


def gap_days(gender):
    return GAP_FEMALE if gender == "female" else GAP_MALE


def next_eligible(last_donation, gender):
    if not last_donation:
        return None
    return datetime.date.fromisoformat(str(last_donation)) + datetime.timedelta(days=gap_days(gender))


def registration_problems(birth_date, weight, last_donation, gender, consent, health_risk):
    """Reasons a person cannot be registered as a donor right now (empty list = fine)."""
    problems = []
    try:
        age = age_of(birth_date)
        if age < MIN_AGE or age > MAX_AGE:
            problems.append("Age must be between %d and %d" % (MIN_AGE, MAX_AGE))
    except ValueError:
        problems.append("Enter a valid date of birth")
    if int(weight) < MIN_WEIGHT:
        problems.append("Weight must be at least %d kg" % MIN_WEIGHT)
    if health_risk:
        problems.append("Your health answers show a risk, please see a doctor first")
    if not consent:
        problems.append("Privacy consent is required")
    try:
        nxt = next_eligible(last_donation, gender)
    except ValueError:
        problems.append("Enter a valid date for the last donation")
        nxt = None
    if nxt and nxt > today():
        problems.append("Next donation possible on " + nxt.isoformat())
    return problems


def eligibility(donor):
    """Reasons this registered donor cannot donate today (empty list = can donate).
    After a donation the donor is blocked for 120 days (women 180), so nobody can give blood too often."""
    problems = []
    age = age_of(donor["birth_date"])
    if age < MIN_AGE or age > MAX_AGE:
        problems.append("Age must be between %d and %d" % (MIN_AGE, MAX_AGE))
    if int(donor["weight"]) < MIN_WEIGHT:
        problems.append("Weight must be at least %d kg" % MIN_WEIGHT)
    nxt = next_eligible(donor["last_donation"], donor["gender"])
    if nxt and nxt > today():
        problems.append("Next donation possible on " + nxt.isoformat())
    return problems


SCOPES = {"district": 1, "division": 2, "all": 3}


def closeness(donor, district, upazila=None):
    """0 same upazila, 1 same district, 2 same division, 3 elsewhere in Bangladesh."""
    if donor["area"] == district:
        a, b = (donor.get("upazila") or "").strip().lower(), (upazila or "").strip().lower()
        return 0 if a and a == b else 1
    return 2 if DIVISION_OF.get(donor["area"]) == DIVISION_OF.get(district) else 3


def matching_donors(blood_group, district, upazila=None, scope="all"):
    """Active, available, eligible donors with a compatible blood group, nearest first.
    scope limits the search: "district" (same district only), "division" or "all" (whole country)."""
    groups = COMPAT[blood_group]
    marks = ",".join("?" * len(groups))
    rows = run("SELECT d.*, u.name, u.phone FROM donors d JOIN users u ON u.id = d.user_id "
               "WHERE u.status='active' AND d.available=1 AND d.blood_group IN (%s)" % marks, groups)
    limit = SCOPES.get(scope, 3)
    out = []
    for r in rows:
        r["tier"] = closeness(r, district, upazila)
        if r["tier"] <= limit and not eligibility(r):
            out.append(r)
    # nearest first, then the exact blood group, then the donor who has rested the longest
    out.sort(key=lambda r: (r["tier"], r["blood_group"] != blood_group, str(r["last_donation"] or "")))
    return out

# LifeLink: Blood Donation Network for Bangladesh

LifeLink connects **patient families**, **blood donors** and **hospitals**. A family asks for blood, the hospital verifies the request,
and eligible donors nearby are alerted by app and SMS. A donor's phone number is shown only after the donor accepts.
The whole app works in **Bangla and English** (Bangla is the default; use the language button at the top).

Made by Krisanu.

## What the app does

**Easy to use**
- Log in with **phone number + password**, or with a **6-digit SMS code** (no password needed). "Forgot password" also works by SMS code.
- Password needs only 6 characters, with a Show button to check what you typed. Email is optional.
- Phone-first design, large tap buttons, installable on the home screen (PWA), Bangla and English everywhere.
- **Urgent needs** page with a Share button (WhatsApp, Messenger, SMS) so a request can spread fast.

**For donors**
- Registered by blood group, **district (all 64) and upazila**. Health check and consent at sign-up.
- After a donation the donor is blocked for **120 days (women 180)**. The system enforces it. A reminder arrives when the donor can give again.
- Accept, decline, or cancel later with "I cannot come" (the hospital is told and can alert someone else).
- Edit profile, change password, delete account, donation history and certificate.

**For patient families**
- Request blood with hospital, district, urgency and date. Edit or close the request. Requests that nobody handles expire by themselves.
- See donors only after they accept. Each phone view is logged.

**For hospitals**
- Verify or reject requests, alert donors **by distance**: same upazila, same district, same division, or all Bangladesh (choose 5 to 30 donors).
- Live stock with expiry dates, shortage and expiring warnings, one-click removal of expired blood (expired blood is hidden from the public list).
- Record a donation by the donor's **phone number**; stock, donor rest period and request update together.
- Thalassemia (regular transfusion) list with reminders.

**For admins**
- Approve hospital staff, search users, suspend or activate accounts, reports (including donors by district), audit log, SMS log with delivery status.

**Safety and privacy**
- Passwords stored with PBKDF2 (600,000 rounds; older accounts are upgraded at their next login). Login cookies are stored only as hashes. SMS codes appear on screen only in demo mode (`SMS_PROVIDER=demo` **and** `SEED_DEMO=1`). Login rate limit (8 wrong tries per 10 minutes). Codes: 1 per minute, 5 per hour, 5 tries each.
- Sessions expire after 30 days. Secure cookie when HTTPS is on. Safety headers (CSP, frame, referrer). Forms from other sites are refused (CSRF).
- Public pages never show names or phone numbers of donors or patients.

## Files

```
backend/    server.py, routes_*.py, rules.py (eligibility), notify.py (SMS), maintenance.py (auto-expire, reminders), database.py, auth.py, seed.py
frontend/   index.html, css/style.css, js/ (i18n.js + i18n2.js = Bangla), sw.js and manifest (installable app), icons/
database/   schema.sql (source), schema_mysql.sql, schema_sqlite.sql (ready to import, with indexes)

```

## Please read: limits and honesty

- **Medical rules:** age 18 to 60, weight 50 kg, 120/180 days between donations are cautious defaults in `backend/config.py`. Confirm them with a doctor or the national guideline before real use.
  A hospital doctor always makes the final decision.
- **MySQL** and the **real SMS gateways** could not be tested in the build environment (SQLite and the demo SMS mode were tested). Do a small trial first.
- The built-in Python web server is fine for a small or medium site behind Caddy/nginx. For very high traffic, run several copies behind a load balancer.
- Hospital accounts must be approved by an admin. Check real hospitals before approving them.
- LifeLink is a connection tool, not a medical service. Never take money for blood.

  KRISANU DAS

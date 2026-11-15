-- LifeLink database schema. Made by Krisanu.
-- The placeholders PK, DT and ENGINE (in curly braces) are filled in by backend/database.py for MySQL or SQLite.
-- Ready-to-import copies (tables and indexes): schema_mysql.sql and schema_sqlite.sql (made by tools/build_schemas.py).
-- "area" always holds a district name (one of the 64 districts of Bangladesh). "upazila" is optional free text.

CREATE TABLE IF NOT EXISTS hospitals (
  id {PK},
  name VARCHAR(150) NOT NULL,
  area VARCHAR(80) NOT NULL,
  upazila VARCHAR(80) NULL,
  address VARCHAR(200),
  phone VARCHAR(30),
  approved INT NOT NULL DEFAULT 0
){ENGINE};

-- Everyone who logs in. role: donor, requester, hospital, admin.
-- status: active, pending (hospital staff wait for approval) or suspended.
-- phone is stored as 01XXXXXXXXX and is the main login. email is optional.
CREATE TABLE IF NOT EXISTS users (
  id {PK},
  name VARCHAR(120) NOT NULL,
  email VARCHAR(190) NULL UNIQUE,
  phone VARCHAR(20) NOT NULL UNIQUE,
  pass_hash VARCHAR(200) NOT NULL,
  role VARCHAR(20) NOT NULL,
  hospital_id INT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  created_at {DT},
  FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
){ENGINE};

-- Extra details for donors (one row per donor user).
CREATE TABLE IF NOT EXISTS donors (
  user_id INT PRIMARY KEY,
  blood_group VARCHAR(3) NOT NULL,
  gender VARCHAR(10) NOT NULL,
  birth_date VARCHAR(10) NOT NULL,
  weight INT NOT NULL,
  area VARCHAR(80) NOT NULL,
  upazila VARCHAR(80) NULL,
  last_donation VARCHAR(10) NULL,
  available INT NOT NULL DEFAULT 1,
  reminder_sent INT NOT NULL DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id)
){ENGINE};

-- Blood requests. status: pending -> verified -> fulfilled, or rejected / closed / expired.
CREATE TABLE IF NOT EXISTS requests (
  id {PK},
  requester_id INT NOT NULL,
  patient_name VARCHAR(120) NOT NULL,
  blood_group VARCHAR(3) NOT NULL,
  units INT NOT NULL,
  units_received INT NOT NULL DEFAULT 0,
  hospital_id INT NOT NULL,
  area VARCHAR(80) NOT NULL,
  upazila VARCHAR(80) NULL,
  urgency VARCHAR(10) NOT NULL DEFAULT 'normal',
  needed_by VARCHAR(10) NULL,
  note VARCHAR(300) NULL,
  contact_phone VARCHAR(30) NULL,
  status VARCHAR(15) NOT NULL DEFAULT 'pending',
  created_at {DT},
  FOREIGN KEY (requester_id) REFERENCES users(id),
  FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
){ENGINE};

-- Which donor was asked for which request. status: asked, accepted, declined, cancelled, donated.
CREATE TABLE IF NOT EXISTS request_donors (
  request_id INT NOT NULL,
  donor_id INT NOT NULL,
  status VARCHAR(12) NOT NULL,
  updated_at {DT},
  PRIMARY KEY (request_id, donor_id),
  FOREIGN KEY (request_id) REFERENCES requests(id),
  FOREIGN KEY (donor_id) REFERENCES users(id)
){ENGINE};

CREATE TABLE IF NOT EXISTS donations (
  id {PK},
  donor_id INT NOT NULL,
  hospital_id INT NOT NULL,
  request_id INT NULL,
  units INT NOT NULL,
  donated_on VARCHAR(10) NOT NULL,
  FOREIGN KEY (donor_id) REFERENCES users(id),
  FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
){ENGINE};

-- Blood bags per hospital and blood group. expires_on is the date the nearest bag expires.
CREATE TABLE IF NOT EXISTS stock (
  hospital_id INT NOT NULL,
  blood_group VARCHAR(3) NOT NULL,
  units INT NOT NULL,
  expires_on VARCHAR(10) NOT NULL,
  PRIMARY KEY (hospital_id, blood_group),
  FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
){ENGINE};

-- Patients who need regular transfusion (for example thalassemia).
CREATE TABLE IF NOT EXISTS thal_patients (
  id {PK},
  hospital_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  blood_group VARCHAR(3) NOT NULL,
  next_date VARCHAR(10) NOT NULL,
  frequency_weeks INT NOT NULL,
  notes VARCHAR(200) NULL,
  FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
){ENGINE};

CREATE TABLE IF NOT EXISTS notifications (
  id {PK},
  user_id INT NOT NULL,
  message VARCHAR(300) NOT NULL,
  is_read INT NOT NULL DEFAULT 0,
  created_at {DT},
  FOREIGN KEY (user_id) REFERENCES users(id)
){ENGINE};

-- Every SMS the system sends. status: queued, sent, logged (demo mode) or failed.
CREATE TABLE IF NOT EXISTS sms_log (
  id {PK},
  phone VARCHAR(30) NOT NULL,
  message VARCHAR(300) NOT NULL,
  status VARCHAR(80) NOT NULL DEFAULT 'logged',
  created_at {DT}
){ENGINE};

-- Who did what, for example when a donor's phone number is viewed.
CREATE TABLE IF NOT EXISTS audit_log (
  id {PK},
  user_id INT NULL,
  action VARCHAR(60) NOT NULL,
  detail VARCHAR(300) NULL,
  created_at {DT}
){ENGINE};

CREATE TABLE IF NOT EXISTS sessions (
  token VARCHAR(64) PRIMARY KEY,
  user_id INT NOT NULL,
  created_at {DT},
  FOREIGN KEY (user_id) REFERENCES users(id)
){ENGINE};

-- One-time codes sent by SMS for login and password reset (only a hash of the code is stored).
CREATE TABLE IF NOT EXISTS otps (
  id {PK},
  phone VARCHAR(20) NOT NULL,
  purpose VARCHAR(10) NOT NULL,
  code_hash VARCHAR(64) NOT NULL,
  attempts INT NOT NULL DEFAULT 0,
  used INT NOT NULL DEFAULT 0,
  created_at {DT}
){ENGINE};

// Public pages: home, find blood, request blood, donor guide, log in, join, notifications. Made by Krisanu.

async function home() {
  const [stats, needs] = await Promise.all([api('/public/stats'), api('/public/needs')]);
  const rows = S.meta.groups.map(g => '<tr><th>' + g + '</th><td>' + S.meta.compat[g].map(d => '<span class="chip-g">' + d + '</span>').join('') + '</td></tr>').join('');
  const features = [
    ['Verified requests', 'A hospital confirms every request before any donor is contacted, so fake requests never reach you.'],
    ['Private by design', 'Your phone number stays hidden until you agree to help with a specific request.'],
    ['Smart matching', 'Donors are matched by blood group and distance: same upazila, same district, then same division. Only people who are eligible today are asked.'],
    ['Live blood stock', 'See which hospitals in your district have blood in stock right now and how long it stays fresh.'],
    ['SMS and app alerts', 'Donors get a notification and a text message, so help can arrive even without internet.'],
    ['Thalassemia care', 'Hospitals can plan regular transfusions in advance and keep a group of regular donors.']];
  $('app').innerHTML = `
  <section class="hero container">
    <div class="hero-text">
      <span class="eyebrow">${t('Bangladesh blood donation network')}</span>
      <h1>${t('Give blood.')} <em>${t('Save a life today.')}</em></h1>
      <p class="lead">${t('LifeLink connects donors, patient families and hospitals. Hospitals verify every request, and your phone number stays private until you agree to help.')}</p>
      <div class="cta"><a class="btn big" href="#/request">${t('Request blood')}</a><a class="btn ghost big" href="#/register?role=donor">${t('Become a donor')}</a></div>
      <ul class="trust"><li>${t('Hospital-verified')}</li><li>${t('Phone stays private')}</li><li>${t('Works with SMS')}</li></ul>
    </div>
    <div class="hero-art">${drop(220, 'big-drop')}
      <svg class="pulse" viewBox="0 0 300 60" aria-hidden="true"><polyline points="0,30 70,30 90,30 105,8 125,52 142,18 156,30 300,30" fill="none" stroke="#b0102e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <span class="float f1">${t('Request verified')}</span><span class="float f2">${t('Donor agreed')}</span><span class="float f3">${t('Blood delivered')}</span>
    </div>
  </section>
  <section class="container statband glass">
    <div><b>${stats.donors}</b><span>${t('Registered donors')}</span></div><div><b>${stats.donations}</b><span>${t('Donations recorded')}</span></div>
    <div><b>${stats.hospitals}</b><span>${t('Partner hospitals')}</span></div><div><b>${stats.fulfilled}</b><span>${t('Requests fulfilled')}</span></div>
  </section>
  ${needs.length ? '<section class="container"><div class="sec-head"><h2 class="sec">' + t('Urgent needs') + '</h2><a href="#/needs">' + t('See all') + '</a></div>' + needsCards(needs.slice(0, 3)) + '</section>' : ''}
  <section class="container"><h2 class="sec">${t('How it works')}</h2>
    <div class="grid3">
      <div class="card step"><span class="num">1</span><h3>${t('Ask for blood')}</h3><p>${t('Fill in the patient, blood group and hospital. It takes about a minute.')}</p></div>
      <div class="card step"><span class="num">2</span><h3>${t('Hospital verifies')}</h3><p>${t('The hospital confirms the request and alerts eligible donors nearby.')}</p></div>
      <div class="card step"><span class="num">3</span><h3>${t('Donors respond')}</h3><p>${t('Donors who agree share their contact with you, and the donation is recorded.')}</p></div>
    </div></section>
  <section class="container"><h2 class="sec">${t('Why people trust LifeLink')}</h2>
    <div class="grid3">${features.map(f => '<div class="card feat"><h3>' + t(f[0]) + '</h3><p>' + t(f[1]) + '</p></div>').join('')}</div></section>
  <section class="container"><h2 class="sec">${t('Who can give blood to whom')}</h2>
    <div class="card"><p class="muted">${t('Each row shows a patient blood group and the donor groups that can safely give to them.')}</p>
    <div class="scroll"><table class="compat"><thead><tr><th>${t('Patient group')}</th><th>${t('Can receive from')}</th></tr></thead><tbody>${rows}</tbody></table></div></div></section>
  <section class="container"><div class="cta-band glass"><div><h2>${t('Ready to help?')}</h2><p>${t('Register in two minutes and be there when someone needs you.')}</p></div>
    <a class="btn big" href="#/register?role=donor">${t('Become a donor')}</a></div></section>`;
}


function needsCards(list) {
  S.needs = list;
  return list.map((n, i) => `<div class="card need ${esc(n.urgency)}"><div class="need-g">${esc(n.blood_group)}</div>
    <div class="need-info"><h3>${t('{n} bag(s) of {g} needed', { n: n.units_left, g: esc(n.blood_group) })} ${statusPill(n.urgency)}</h3>
      <p class="muted">${esc(n.hospital_name)} · ${areaText(n.area, n.upazila)}${n.needed_by ? ' · ' + t('Needed by {d}', { d: esc(n.needed_by) }) : ''}</p></div>
    <div class="actions">${telLink(n.hospital_phone, t('Call hospital'))}<button class="btn small" onclick="shareNeed(${i})">${t('Share')}</button></div></div>`).join('');
}

function shareNeed(i) {
  const n = S.needs[i];
  shareText(t('Urgent: {g} blood needed at {h}, {a}. Please help or share. LifeLink:', { g: n.blood_group, h: n.hospital_name, a: t(n.area) }) + ' ' + location.origin + '/#/needs');
}

async function needsPage() {
  const area = S.needsArea || '';
  const list = await api('/public/needs' + (area ? '?area=' + encodeURIComponent(area) : ''));
  $('app').innerHTML = `<section class="container narrow"><h1 class="page">${t('Urgent needs')}</h1>
    <p class="muted">${t('Hospital-verified requests that still need blood. Names and phone numbers of patients are never shown here.')}</p>
    <label>${t('District')}<select id="n_area" onchange="S.needsArea=this.value;needsPage()">${districtOptions(area, 'All Bangladesh')}</select></label>
    <div class="results">${list.length ? needsCards(list) : empty('No open requests right now. Thank you for checking.')}</div>
    <div class="card center"><h3>${t('Want to be alerted when someone near you needs blood?')}</h3><p class="muted">${t('Register as a donor. Hospitals alert eligible donors by app and SMS.')}</p>
      <a class="btn" href="#/register?role=donor">${t('Become a donor')}</a></div></section>`;
}

async function findBlood() {
  S.stockGroup = S.stockGroup || 'O+';
  $('app').innerHTML = `<section class="container narrow"><h1 class="page">${t('Find blood in stock')}</h1>
    <p class="muted">${t('Choose a blood group to see hospitals that have it right now. Always call the hospital before you travel.')}</p>
    <label>${t('District')}<select id="f_area" onchange="loadStock()">${districtOptions(S.stockArea || '', 'All Bangladesh')}</select></label>
    <div class="chips" id="gchips">${S.meta.groups.map(g => '<button class="chip-btn" onclick="loadStock(\'' + g + '\')">' + g + '</button>').join('')}</div>
    <div id="stockout" class="results"></div></section>`;
  loadStock(S.stockGroup);
}




async function loadStock(group) {
  if (group) S.stockGroup = group;
  group = S.stockGroup;
  S.stockArea = $('f_area') ? $('f_area').value : '';
  [].forEach.call(document.querySelectorAll('#gchips .chip-btn'), b => b.classList.toggle('on', b.textContent === group));
  const rows = await guard(() => api('/public/stock?group=' + encodeURIComponent(group) + '&area=' + encodeURIComponent(S.stockArea)));
  if (!rows) return;
  $('stockout').innerHTML = rows.length ? rows.map(r => `<div class="card hosp"><div><h3>${esc(r.name)}</h3><p class="muted">${areaText(r.area, r.upazila)}</p>${telLink(r.phone, t('Call') + ' ' + r.phone)}</div>
      <div class="units"><b>${r.units}</b><span>${t('units of {g}', { g: esc(group) })}</span><small>${t('Fresh for about {n} days', { n: r.expiry_days })}</small></div></div>`).join('')
    : empty(S.stockArea ? 'No hospital in this district has this blood group right now. Try All Bangladesh, or send a request.' : 'No hospital has this blood group in stock right now. Send a request and donors will be alerted.') +
      '<p class="center"><a class="btn" href="#/request">' + t('Request blood') + '</a></p>';
}


function requestFormHtml() {
  const own = S.user && S.user.role === 'hospital' ? S.user.hospital_id : null;
  const first = own || (S.meta.hospitals[0] || {}).id;
  const h = S.meta.hospitals.find(x => x.id === first) || {};
  const today = new Date().toISOString().slice(0, 10);
  return `<div class="card form"><div class="row">
      <label>${t('Patient name')}<input id="q_patient" required></label>
      <label>${t('Blood group')}<select id="q_group">${options(S.meta.groups, 'O+')}</select></label></div>
    <div class="row"><label>${t('Units needed')}<input id="q_units" type="number" min="1" max="10" value="1" inputmode="numeric"></label>
      <label>${t('Urgency')}<select id="q_urgency"><option value="normal">${t('Normal')}</option><option value="urgent">${t('Urgent')}</option><option value="critical">${t('Critical')}</option></select></label></div>
    <label>${t('Hospital')}<select id="q_hospital" onchange="hospitalChanged()">${hospitalOptions(first)}</select></label>
    <div class="row"><label>${t('District')}<select id="q_area">${districtOptions(h.area)}</select></label>
      <label>${t('Upazila or area (optional)')}<input id="q_upazila" value="${esc(h.upazila || '')}"></label></div>
    <div class="row"><label>${t('Needed by (optional)')}<input id="q_date" type="date" min="${today}"></label>
      <label>${t('Contact phone')}<input id="q_phone" inputmode="tel" value="${esc(S.user ? S.user.phone : '')}"></label></div>
    <label>${t('Note (optional)')}<textarea id="q_note" rows="2" maxlength="300"></textarea></label>
    <button class="btn big" onclick="submitRequest()">${t('Send request')}</button></div>`;
}

function hospitalChanged() {
  const h = S.meta.hospitals.find(x => String(x.id) === $('q_hospital').value);
  if (h) { $('q_area').value = h.area; $('q_upazila').value = h.upazila || ''; }
}




async function submitRequest() {
  const body = { patient_name: $('q_patient').value, blood_group: $('q_group').value, units: $('q_units').value, urgency: $('q_urgency').value,
    hospital_id: $('q_hospital').value, area: $('q_area').value, upazila: $('q_upazila').value, needed_by: $('q_date').value, contact_phone: $('q_phone').value, note: $('q_note').value };
  const result = await guard(() => api('/requests', body));
  if (!result) return;
  toast(t(result.status === 'verified' ? 'Request sent and verified.' : 'Request sent. The hospital will verify it shortly.'));
  location.hash = '#/dashboard';
}

async function requestPage() {
  if (!S.user) {
    $('app').innerHTML = `<section class="container narrow"><h1 class="page">${t('Request blood')}</h1><div class="card center"><p>${t('Please log in or create a free account so the hospital can reach you.')}</p>
      <a class="btn" href="#/login">${t('Log in')}</a> <a class="btn ghost" href="#/register?role=requester">${t('Create account')}</a></div></section>`;
    return;
  }
  $('app').innerHTML = `<section class="container narrow"><h1 class="page">${t('Request blood')}</h1>
    <p class="muted">${t('The hospital verifies your request first. Then eligible donors are alerted.')}</p>${requestFormHtml()}</section>`;
}

function guide() {
  const list = items => '<ul>' + items.map(i => '<li>' + t(i) + '</li>').join('') + '</ul>';
  const r = S.meta.rules;
  const faq = [['Does donating blood make me weak?', 'Most healthy donors feel fine. Drink water, eat well and rest a little afterwards.'],
    ['How much blood is taken?', 'A standard donation is about one bag (350 to 450 ml), and the body replaces it over the following weeks.'],
    ['Is it safe?', 'Yes. New sterile equipment is used for each donor, and a doctor checks you first.'],
    ['Will my blood be tested?', 'Yes. Donated blood is tested for infections such as hepatitis B and C, HIV, syphilis and malaria.'],
    ['Can I be paid for blood?', 'No. Paid donation is discouraged because it can make blood less safe. LifeLink is for voluntary donors only.']];
  $('app').innerHTML = `<section class="container"><h1 class="page">${t('Donor guide')}</h1>
    <p class="muted">${t('Typical rules are shown here. The doctor at the blood centre makes the final decision.')}</p>
    <div class="grid3">
      <div class="card"><h3>${t('Who can donate')}</h3>${list([t('Age {a} to {b} years', { a: r.min_age, b: r.max_age }), t('Weight at least {w} kg (some centres accept 45 kg)', { w: r.min_weight }),
        t('Feeling healthy, with no fever or infection'), t('About {m} months since your last donation (women: about {f} months)', { m: r.gap_male / 30, f: r.gap_female / 30 })])}</div>
      <div class="card"><h3>${t('Before you donate')}</h3>${list(['Eat a healthy meal and do not donate on an empty stomach.', 'Drink plenty of water.', 'Sleep well the night before.', 'Bring a photo ID if you have one.'])}</div>
      <div class="card"><h3>${t('After you donate')}</h3>${list(['Rest for 10 to 15 minutes and have a snack.', 'Drink extra fluids for the rest of the day.', 'Avoid heavy exercise until the next day.', 'Keep the bandage on for a few hours.'])}</div>
    </div>
    <h2 class="sec">${t('Common questions')}</h2>
    <div class="faq">${faq.map(f => '<details class="card"><summary>' + t(f[0]) + '</summary><p>' + t(f[1]) + '</p></details>').join('')}</div></section>`;
}

function privacyPage() {
  const list = items => '<ul>' + items.map(i => '<li>' + t(i) + '</li>').join('') + '</ul>';
  $('app').innerHTML = `<section class="container narrow"><h1 class="page">${t('Privacy and terms')}</h1>
    <div class="card"><h3>${t('What we keep')}</h3>${list(['Your name, mobile number and password (the password is stored in a scrambled form that nobody can read).', 'For donors: blood group, date of birth, weight, district and donation dates.', 'For requests: the patient name, hospital and contact number you enter.'])}</div>
    <div class="card"><h3>${t('Who can see your phone number')}</h3>${list(['A donor phone number is shown only to the requester and the hospital of a request that the donor accepted.', 'Every time a phone number is viewed, it is recorded in a log.', 'The public pages never show names or phone numbers of donors or patients.'])}</div>
    <div class="card"><h3>${t('Your choices')}</h3>${list(['You can switch "Available for requests" off at any time.', 'You can change your details in your dashboard.', 'You can delete your account in your dashboard. Your personal details are then removed.'])}</div>
    <div class="card"><h3>${t('Please remember')}</h3>${list(['LifeLink connects people. It does not give medical advice. The doctor at the blood centre decides who can donate.', 'Never pay anyone for blood. Never share your password or SMS code.'])}</div></section>`;
}


function loginPage() {
  const mode = S.loginMode || 'password';
  const seg = `<div class="seg"><button class="${mode === 'password' ? 'on' : ''}" onclick="setLoginMode('password')">${t('Password')}</button><button class="${mode === 'otp' ? 'on' : ''}" onclick="setLoginMode('otp')">${t('SMS code')}</button></div>`;
  const form = mode === 'password'
    ? `<label>${t('Phone or email')}<input id="l_id" autocomplete="username" placeholder="01XXXXXXXXX"></label>${passField('l_pass', 'Password', 'current-password', 'doLogin()')}
       <button class="btn big" onclick="doLogin()">${t('Log in')}</button><p class="center"><a href="#/forgot">${t('Forgot password?')}</a></p>`
    : `<p class="muted small">${t('No password needed. We send a 6-digit code to your mobile number.')}</p>
       <label>${t('Mobile number')}<input id="l_phone" inputmode="tel" autocomplete="tel" placeholder="01XXXXXXXXX"></label>
       <button class="btn big" onclick="sendOtp('login')">${t('Send code')}</button><div id="otpbox" class="form"></div>`;
  $('app').innerHTML = `<section class="container auth"><div class="card form"><h1 class="page">${t('Welcome back')}</h1>${seg}${form}
    <p class="muted center">${t('New here?')} <a href="#/register">${t('Create an account')}</a></p></div></section>`;
}

function setLoginMode(mode) { S.loginMode = mode; loginPage(); }



// Send a one-time code by SMS. purpose "login" (log in without a password) or "reset" (forgot password).
async function sendOtp(purpose) {
  const phone = $(purpose === 'login' ? 'l_phone' : 'f_phone').value;
  const r = await guard(() => api('/auth/otp/send', { phone, purpose }));
  if (!r) return;
  $('otpbox').innerHTML = `<p class="muted small">${t('We sent a 6-digit code by SMS. It works for {m} minutes.', { m: 10 })}</p>` +
    (r.demo_code ? `<div class="notice">${t('Demo mode: no real SMS is sent. Your code is {c}', { c: r.demo_code })}</div>` : '') +
    `<label>${t('6-digit code')}<input id="o_code" inputmode="numeric" maxlength="6" autocomplete="one-time-code"></label>` +
    (purpose === 'reset' ? passField('o_pass', 'New password (6+ characters)', 'new-password') : '') +
    `<button class="btn big" onclick="${purpose === 'login' ? 'otpLogin()' : 'doReset()'}">${t(purpose === 'login' ? 'Log in' : 'Save new password')}</button>`;
}

async function otpLogin() {
  const data = await guard(() => api('/auth/otp/login', { phone: $('l_phone').value, code: $('o_code').value }));
  if (!data) return;
  S.user = data.user;
  await refreshUser();
  location.hash = '#/dashboard';
}

function forgotPage() {
  $('app').innerHTML = `<section class="container auth"><div class="card form"><h1 class="page">${t('Forgot password?')}</h1>
    <p class="muted">${t('Enter your mobile number. We will send a code to set a new password.')}</p>
    <label>${t('Mobile number')}<input id="f_phone" inputmode="tel" autocomplete="tel" placeholder="01XXXXXXXXX"></label>
    <button class="btn big" onclick="sendOtp('reset')">${t('Send code')}</button><div id="otpbox" class="form"></div>
    <p class="center"><a href="#/login">${t('Back to log in')}</a></p></div></section>`;
}

async function doReset() {
  const data = await guard(() => api('/auth/reset', { phone: $('f_phone').value, code: $('o_code').value, password: $('o_pass').value }));
  if (!data) return;
  S.user = data.user;
  await refreshUser();
  toast(t('Your password was changed.'));
  location.hash = '#/dashboard';
}


async function doLogin() {
  const data = await guard(() => api('/auth/login', { login: $('l_id').value, password: $('l_pass').value }));
  if (!data) return;
  S.user = data.user;
  await refreshUser();
  location.hash = '#/dashboard';
}


function registerPage() {
  const role = new URLSearchParams(location.hash.split('?')[1] || '').get('role') || 'donor';
  const roles = [['donor', 'Blood donor', 'Give blood and get alerts when someone nearby needs you.'], ['requester', 'Patient family', 'Ask for blood for a patient.'], ['hospital', 'Hospital staff', 'Verify requests and manage stock (needs admin approval).']];
  $('app').innerHTML = `<section class="container narrow"><h1 class="page">${t('Create your account')}</h1>
    <div class="grid3 roles">${roles.map(r => '<button class="card rolecard' + (r[0] === role ? ' on' : '') + '" onclick="location.hash=\'#/register?role=' + r[0] + '\'"><h3>' + t(r[1]) + '</h3><p>' + t(r[2]) + '</p></button>').join('')}</div>
    <div class="card form" id="regform"></div></section>`;
  const hospital = role === 'hospital' ? `<label>${t('Your hospital')}<select id="r_hospital" onchange="document.getElementById('newhosp').style.display=this.value?'none':'grid'"><option value="">${t('My hospital is not listed')}</option>${hospitalOptions()}</select></label>
      <div class="row" id="newhosp"><label>${t('Hospital name')}<input id="r_hname"></label><label>${t('Hospital district')}<select id="r_harea">${districtOptions('Dhaka')}</select></label></div>` : '';
  const donor = role === 'donor' ? `<div class="row"><label>${t('Blood group')}<select id="r_group">${options(S.meta.groups, 'O+')}</select></label>
      <label>${t('Gender')}<select id="r_gender"><option value="male">${t('Male')}</option><option value="female">${t('Female')}</option></select></label></div>
    <div class="row"><label>${t('Date of birth')}<input id="r_birth" type="date"></label><label>${t('Weight (kg)')}<input id="r_weight" type="number" min="30" max="200" inputmode="numeric"></label></div>
    <div class="row"><label>${t('District')}<select id="r_area">${districtOptions('Dhaka')}</select></label><label>${t('Upazila or area (optional)')}<input id="r_upazila"></label></div>
    <label>${t('Last donation (leave empty if never)')}<input id="r_last" type="date"></label>
    <fieldset><legend>${t('Health check: tick any that apply to you')}</legend>
      ${['Tattoo, piercing or surgery in the last 6 months', 'Fever or infection right now', 'Pregnant or breastfeeding', 'History of hepatitis B or C, or HIV'].map(q => '<label class="check"><input type="checkbox" class="risk"> ' + t(q) + '</label>').join('')}</fieldset>
    <label class="check"><input type="checkbox" id="r_consent"> ${t('I agree that my phone number is shown only to a requester after I accept their request.')}</label>` : '';
  $('regform').innerHTML = `<div class="row"><label>${t('Full name')}<input id="r_name" autocomplete="name"></label><label>${t('Mobile number')}<input id="r_phone" inputmode="tel" autocomplete="tel" placeholder="01XXXXXXXXX"></label></div>
    <div class="row">${passField('r_pass', 'Password (6+ characters)', 'new-password')}<label>${t('Email (optional)')}<input id="r_email" type="email" autocomplete="email"></label></div>
    <p class="muted small">${t('Your mobile number is your login. You can also log in with an SMS code.')}</p>
    ${donor}${hospital}<button class="btn big" onclick="doRegister('${role}')">${t('Create account')}</button>`;
}

async function doRegister(role) {
  const v = id => { const el = $(id); return el ? el.value : undefined; };
  const body = { role, name: v('r_name'), phone: v('r_phone'), email: v('r_email'), password: v('r_pass') };
  if (role === 'donor') Object.assign(body, { blood_group: v('r_group'), gender: v('r_gender'), birth_date: v('r_birth'), weight: v('r_weight'), area: v('r_area'), upazila: v('r_upazila'),
    last_donation: v('r_last'), consent: $('r_consent').checked, health_risk: [].some.call(document.querySelectorAll('.risk'), c => c.checked) });
  if (role === 'hospital') Object.assign(body, { hospital_id: v('r_hospital'), new_hospital_name: v('r_hname'), new_hospital_area: v('r_harea') });
  const data = await guard(() => api('/auth/register', body));
  if (!data) return;
  if (data.pending) { toast(t('Account created. An administrator will approve it soon.')); location.hash = '#/login'; return; }
  S.user = data.user;
  await refreshUser();
  toast(t('Welcome to LifeLink!'));
  location.hash = '#/dashboard';
}

async function notificationsPage() {
  if (!S.user) { location.hash = '#/login'; return; }
  const data = await api('/notifications');
  $('app').innerHTML = `<section class="container narrow"><h1 class="page">${t('Notifications')}</h1>
    ${data.items.length ? data.items.map(n => '<div class="card note' + (n.is_read ? '' : ' new') + '"><p>' + esc(tm(n.message)) + '</p><small>' + esc(n.created_at) + '</small></div>').join('') : empty('No notifications yet.')}</section>`;
  if (data.unread) { await api('/notifications/read', {}); S.unread = 0; renderNav(); }
}

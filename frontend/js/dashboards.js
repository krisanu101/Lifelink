// Dashboards for each kind of user: donor, patient family, hospital staff, admin. Made by Krisanu.

function tabsHtml(role, items) {
  const current = S.tab[role] || items[0][0];
  return '<div class="tabs">' + items.map(i => '<button class="' + (i[0] === current ? 'on' : '') + '" onclick="setTab(\'' + role + '\',\'' + i[0] + '\')">' + t(i[1]) + '</button>').join('') + '</div>';
}
function setTab(role, key) { S.tab[role] = key; dashboard(); }
function currentTab(role, first) { return S.tab[role] || first; }

async function dashboard() {
  if (!S.user) { location.hash = '#/login'; return; }
  const role = S.user.role;
  if (role === 'donor') return donorDash();
  if (role === 'hospital') return hospitalDash();
  if (role === 'admin') return adminDash();
  return requesterDash();
}

// ---------- requests (shared by donors and patient families) ----------

async function myRequestsHtml() {
  const rows = await api('/requests/mine');
  if (!rows.length) return empty('You have not made any requests yet.') + '<p class="center"><a class="btn" href="#/request">' + t('Request blood') + '</a></p>';
  return rows.map(r => `<div class="item"><div><b>#${r.id} · ${esc(r.patient_name)}</b> ${pill(r.blood_group, 'blood')} ${statusPill(r.status)} ${statusPill(r.urgency)}
      <p class="muted">${esc(r.hospital_name)} · ${t('{n} of {m} units received', { n: r.units_received, m: r.units })} · ${t('{n} donor(s) agreed', { n: r.accepted })}</p></div>
      <div class="actions"><button class="btn small" onclick="showRequest(${r.id})">${t('Details')}</button>
      ${r.status === 'pending' || r.status === 'verified' ? '<button class="btn ghost small" onclick="editRequest(' + r.id + ')">' + t('Edit') + '</button><button class="btn ghost small" onclick="closeRequest(' + r.id + ')">' + t('Close request') + '</button>' : ''}</div></div>`).join('');
}


async function showRequest(id) {
  const d = await guard(() => api('/requests/' + id));
  if (!d) return;
  const r = d.request;
  window.__req = r;
  const donors = d.donors.length ? d.donors.map(x => `<div class="item"><div><b>${esc(x.name)}</b> ${pill(x.blood_group, 'blood')} <span class="muted">${esc(t(x.area))}</span></div>
      <div>${x.phone ? '<a class="btn small" href="tel:' + esc(x.phone) + '">' + esc(x.phone) + '</a>' : ''} ${statusPill(x.status)}</div></div>`).join('') : empty('No donors have been alerted yet.');
  const share = r.status === 'verified' ? `<button class="btn ghost small" onclick="shareRequest()">${t('Share')}</button>` : '';
  modal(`<h2>${t('Request')} #${r.id}</h2><p>${esc(r.patient_name)} · ${pill(r.blood_group, 'blood')} · ${t('{n} unit(s)', { n: r.units })} · ${esc(r.hospital_name)} ${statusPill(r.status)}</p>
    <p class="muted">${areaText(r.area, r.upazila)}${r.needed_by ? ' · ' + t('Needed by {d}', { d: esc(r.needed_by) }) : ''}</p>
    ${r.note ? '<p class="muted">' + esc(r.note) + '</p>' : ''}<div class="actions">${telLink(r.hospital_phone, t('Call hospital'))}${share}</div>
    <h3>${t('Donors')}</h3>${donors}<p class="muted small">${t('Phone numbers appear only after a donor accepts, and each view is recorded.')}</p>`);
}

function shareRequest() {
  const r = window.__req;
  shareText(t('Urgent: {g} blood needed at {h}, {a}. Please help or share. LifeLink:', { g: r.blood_group, h: r.hospital_name, a: t(r.area) }) + ' ' + location.origin + '/#/needs');
}

async function editRequest(id) {
  const d = await guard(() => api('/requests/' + id));
  if (!d) return;
  const r = d.request;
  modal(`<h2>${t('Edit request')} #${r.id}</h2><div class="form">
    <div class="row"><label>${t('Units needed')}<input id="e_units" type="number" min="${Math.max(1, r.units_received)}" max="10" value="${r.units}" inputmode="numeric"></label>
      <label>${t('Urgency')}<select id="e_urgency">${['normal', 'urgent', 'critical'].map(u => '<option value="' + u + '"' + (u === r.urgency ? ' selected' : '') + '>' + t(cap(u)) + '</option>').join('')}</select></label></div>
    <div class="row"><label>${t('Needed by (optional)')}<input id="e_date" type="date" value="${esc(r.needed_by || '')}"></label><label>${t('Contact phone')}<input id="e_phone" inputmode="tel" value="${esc(r.contact_phone || '')}"></label></div>
    <label>${t('Note (optional)')}<textarea id="e_note" rows="2" maxlength="300">${esc(r.note || '')}</textarea></label>
    <button class="btn" onclick="saveRequest(${r.id})">${t('Save changes')}</button></div>`);
}
async function saveRequest(id) {
  const body = { units: $('e_units').value, urgency: $('e_urgency').value, needed_by: $('e_date').value, contact_phone: $('e_phone').value, note: $('e_note').value };
  if (await guard(() => api('/requests/' + id + '/update', body))) { closeModal(); toast(t('Request updated.')); dashboard(); }
}

async function closeRequest(id) {
  if (!(await guard(() => api('/requests/' + id + '/close', {})))) return;
  toast(t('Request closed.'));
  dashboard();
}


async function requesterDash() {
  const tab = currentTab('requester', 'mine');
  const body = tab === 'account' ? accountTools() : await myRequestsHtml();
  $('app').innerHTML = `<section class="container"><div class="dash-head"><div><h1 class="page">${t('Hello, {name}', { name: esc(S.user.name) })}</h1><p class="muted">${t('Your blood requests')}</p></div>
    <a class="btn" href="#/request">${t('New request')}</a></div>${tabsHtml('requester', [['mine', 'My requests'], ['account', 'Account']])}<div class="card">${body}</div></section>`;
}

// ---------- donor ----------

async function donorDash() {
  const [p, inbox] = await Promise.all([api('/donor/profile'), api('/donor/inbox')]);
  window.__history = p.history;
  const tab = currentTab('donor', 'inbox');
  const status = p.eligible ? `<div class="status ok"><b>${t('You can donate today')}</b><span>${t('Thank you for being ready to help.')}</span></div>`
    : `<div class="status wait"><b>${t('Not available to donate yet')}</b><span>${p.reasons.map(x => esc(tm(x))).join('<br>')}</span></div>`;
  let body = '';
  if (tab === 'inbox') {
    body = inbox.length ? inbox.map(i => {
      let act = statusPill(i.my_status);
      if (i.my_status === 'asked') act = '<button class="btn small" onclick="respond(' + i.id + ',true)">' + t('I can help') + '</button><button class="btn ghost small" onclick="respond(' + i.id + ',false)">' + t('Not now') + '</button>';
      if (i.my_status === 'accepted') act = statusPill('accepted') + telLink(i.hospital_phone, t('Call hospital')) + '<button class="btn ghost small" onclick="cancelHelp(' + i.id + ')">' + t('I cannot come') + '</button>';
      return `<div class="item"><div><b>${pill(i.blood_group, 'blood')} ${t('needed at {h}', { h: esc(i.hospital_name) })}</b> ${statusPill(i.urgency)}
        <p class="muted">${esc(i.patient_name)} · ${t('{n} unit(s)', { n: i.units })} · ${areaText(i.area, i.upazila)}</p></div><div class="actions">${act}</div></div>`;
    }).join('') : empty('No requests for you right now. We will alert you here and by SMS.');
  } else if (tab === 'history') {
    body = p.history.length ? tableHtml(['Date', 'Hospital', 'Units', 'Certificate'], p.history.map((h, i) => [esc(h.donated_on), esc(h.hospital), h.units, '<button class="btn ghost small" onclick="showCert(' + i + ')">' + t('View') + '</button>']))
      : empty('Your donations will appear here after a hospital records them.');
  } else if (tab === 'profile') { body = donorProfileForm(p); }
  else { body = await myRequestsHtml(); }
  $('app').innerHTML = `<section class="container"><div class="dash-head"><div><h1 class="page">${t('Hello, {name}', { name: esc(S.user.name) })}</h1>
      <p class="muted">${pill(p.donor.blood_group, 'blood')} ${areaText(p.donor.area, p.donor.upazila)} · ${t('{n} years', { n: p.age })}</p></div>
      <label class="switch"><input type="checkbox" ${p.donor.available ? 'checked' : ''} onchange="setAvailable(this.checked)"><span></span>${t('Available for requests')}</label></div>
    <div class="grid2">${status}<div class="status info"><b>${p.history.length}</b><span>${t('donations recorded')}</span>${p.next_eligible && p.next_eligible > new Date().toISOString().slice(0, 10) ? '<small>' + t('Next donation possible on {d}', { d: p.next_eligible }) + '</small>' : ''}</div></div>
    ${tabsHtml('donor', [['inbox', 'Requests for me'], ['history', 'My donations'], ['mine', 'My requests'], ['profile', 'My profile']])}<div class="card">${body}</div></section>`;
}

function donorProfileForm(p) {
  const d = p.donor;
  return `<div class="form"><div class="row"><label>${t('Full name')}<input id="p_name" value="${esc(d.name)}"></label><label>${t('Mobile number')}<input id="p_phone" inputmode="tel" value="${esc(d.phone)}"></label></div>
    <div class="row"><label>${t('District')}<select id="p_area">${districtOptions(d.area)}</select></label><label>${t('Upazila or area (optional)')}<input id="p_upazila" value="${esc(d.upazila || '')}"></label></div>
    <div class="row"><label>${t('Weight (kg)')}<input id="p_weight" type="number" min="30" max="200" inputmode="numeric" value="${d.weight}"></label><label>${t('Email (optional)')}<input id="p_email" type="email" value="${esc(d.email || '')}"></label></div>
    <button class="btn" onclick="saveProfile()">${t('Save changes')}</button></div>` + accountTools();
}
async function saveProfile() {
  const body = { name: $('p_name').value, phone: $('p_phone').value, area: $('p_area').value, upazila: $('p_upazila').value, weight: $('p_weight').value, email: $('p_email').value };
  if (await guard(() => api('/donor/profile', body))) { await refreshUser(); toast(t('Profile saved.')); dashboard(); }
}

// Password change and account deletion (for every kind of user).
function accountTools() {
  return `<h3>${t('Change password')}</h3><div class="form"><div class="row">${passField('c_old', 'Current password', 'current-password')}${passField('c_new', 'New password (6+ characters)', 'new-password')}</div>
    <button class="btn ghost" onclick="changePassword()">${t('Change password')}</button></div>
    <h3>${t('Delete my account')}</h3><p class="muted small">${t('This removes your personal details for good. Donation records stay without your name.')}</p>
    <div class="form"><div class="row">${passField('x_pass', 'Your password', 'current-password')}<span></span></div><button class="btn ghost" onclick="deleteAccount()">${t('Delete my account')}</button></div>`;
}
async function changePassword() {
  if (await guard(() => api('/auth/change-password', { old_password: $('c_old').value, new_password: $('c_new').value }))) { toast(t('Your password was changed.')); $('c_old').value = ''; $('c_new').value = ''; }
}
async function deleteAccount() {
  if (!confirm(t('Delete your account? This cannot be undone.'))) return;
  if (await guard(() => api('/auth/delete-account', { password: $('x_pass').value }))) { S.user = null; S.unread = 0; toast(t('Your account was deleted.')); location.hash = '#/'; showPage(); }
}
async function cancelHelp(id) {
  if (!confirm(t('Tell the hospital you can no longer help?'))) return;
  if (await guard(() => api('/donor/cancel', { request_id: id }))) { toast(t('Thank you for telling us. The hospital will ask someone else.')); dashboard(); }
}

async function setAvailable(value) { if (await guard(() => api('/donor/profile', { available: value }))) toast(t(value ? 'You are available for requests.' : 'You will not receive new requests.')); }
async function respond(id, accept) { if (await guard(() => api('/donor/respond', { request_id: id, accept }))) { toast(t(accept ? 'Thank you! The requester can now contact you.' : 'Noted.')); dashboard(); } }

function showCert(i) {
  const h = window.__history[i];
  modal(`<div class="cert"><div class="cert-in">${drop(54)}<p class="muted">${t('Certificate of appreciation')}</p><h2>${esc(S.user.name)}</h2>
    <p>${t('donated blood at {h} on {d} and helped save lives.', { h: esc(h.hospital), d: esc(h.donated_on) })}</p><p class="sign">LifeLink</p></div></div>
    <p class="center"><button class="btn" onclick="window.print()">${t('Print')}</button></p>`);
}

// ---------- hospital ----------

async function hospitalDash() {
  const tab = currentTab('hospital', 'requests');
  let body = '';
  if (tab === 'requests') body = await hospitalRequests();
  else if (tab === 'stock') body = await hospitalStock();
  else if (tab === 'donation') body = hospitalDonationForm();
  else if (tab === 'thal') body = await hospitalThal();
  else if (tab === 'info') body = await hospitalInfo();
  else body = requestFormHtml();
  $('app').innerHTML = `<section class="container"><div class="dash-head"><div><h1 class="page">${t('Hospital dashboard')}</h1><p class="muted">${esc(S.user.name)}</p></div></div>
    ${tabsHtml('hospital', [['requests', 'Requests'], ['stock', 'Stock'], ['donation', 'Record donation'], ['thal', 'Thalassemia'], ['new', 'New request'], ['info', 'Hospital info']])}<div class="card">${body}</div></section>`;
}


async function hospitalRequests() {
  const rows = await api('/hospital/requests');
  if (!rows.length) return empty('No requests for your hospital yet.');
  return rows.map(r => {
    let actions = '';
    if (r.status === 'pending') actions = `<button class="btn small" onclick="hVerify(${r.id},true)">${t('Verify')}</button><button class="btn ghost small" onclick="hVerify(${r.id},false)">${t('Reject')}</button>`;
    if (r.status === 'verified') actions = `<span class="inline"><select class="mini wide" id="sc${r.id}"><option value="district">${t('Same district')}</option><option value="division"${r.urgency === 'normal' ? ' selected' : ''}>${t('Same division')}</option><option value="all"${r.urgency !== 'normal' ? ' selected' : ''}>${t('All Bangladesh')}</option></select>
      <select class="mini" id="lm${r.id}"><option>5</option><option>10</option><option>20</option><option>30</option></select><button class="btn small" onclick="hNotify(${r.id})">${t('Alert donors')}</button></span>
      <button class="btn ghost small" onclick="hMatches(${r.id})">${t('Matches')}</button>
      <span class="inline"><input class="mini" id="iss${r.id}" type="number" min="1" value="1" inputmode="numeric"><button class="btn ghost small" onclick="hIssue(${r.id})">${t('Issue from stock')}</button></span>`;
    return `<div class="item"><div><b>#${r.id} · ${esc(r.patient_name)}</b> ${pill(r.blood_group, 'blood')} ${statusPill(r.status)} ${statusPill(r.urgency)}
      <p class="muted">${esc(r.requester_name)} · ${areaText(r.area, r.upazila)} · ${t('{n} of {m} units received', { n: r.units_received, m: r.units })} · ${t('{a} alerted, {b} agreed', { a: r.asked, b: r.accepted })}</p></div>
      <div class="actions"><button class="btn ghost small" onclick="showRequest(${r.id})">${t('Details')}</button>${actions}</div></div>`;
  }).join('');
}

async function hVerify(id, ok) { if (await guard(() => api('/hospital/requests/' + id + '/verify', { ok }))) { toast(t(ok ? 'Request verified.' : 'Request rejected.')); dashboard(); } }

async function hNotify(id) {
  const r = await guard(() => api('/hospital/requests/' + id + '/notify', { limit: $('lm' + id).value, scope: $('sc' + id).value }));
  if (r) { toast(r.notified ? t('{n} donor(s) alerted.', { n: r.notified }) : t('No new eligible donors found. Try a wider area.')); dashboard(); }
}
async function hIssue(id) { if (await guard(() => api('/hospital/requests/' + id + '/issue', { units: $('iss' + id).value }))) { toast(t('Blood issued from stock.')); dashboard(); } }

async function hMatches(id) {
  const rows = await guard(() => api('/hospital/requests/' + id + '/matches?scope=all'));
  if (!rows) return;
  const near = ['Same upazila', 'Same district', 'Same division', 'Other area'];
  modal(`<h2>${t('Eligible donors')}</h2>${rows.length ? tableHtml(['ID', 'Donor', 'Group', 'Area', 'Distance', 'Status'], rows.map(m => ['#' + m.donor_id, esc(m.name), m.blood_group, areaText(m.area, m.upazila), t(near[m.tier]), m.status ? statusPill(m.status) : '-'])) : empty('No eligible donors found.')}
    <p class="muted small">${t('Phone numbers are hidden until a donor accepts.')}</p>`);
}


async function hospitalStock() {
  const rows = await api('/hospital/stock');
  const soon = new Date(Date.now() + 35 * 864e5).toISOString().slice(0, 10);
  const table = tableHtml(['Group', 'Units', 'Expiry', 'Status', 'Change'], rows.map(s => {
    const expired = s.units > 0 && s.expiry_days < 0;
    return [pill(s.blood_group, 'blood'), s.units, s.units ? esc(s.expires_on) + ' (' + t('{n} days', { n: s.expiry_days }) + ')' : '-',
      expired ? pill('Expired', 'bad') : (s.units < 5 ? pill('Shortage', 'bad') : pill('OK', 'ok')) + (s.units > 0 && s.expiry_days < 4 ? ' ' + pill('Expiring soon', 'warn') : ''),
      expired ? '<button class="btn ghost small" onclick="hDiscard(\'' + s.blood_group + '\')">' + t('Remove expired') + '</button>'
        : '<button class="btn ghost small" onclick="hStock(\'' + s.blood_group + '\',-1)">-1</button>'];
  }));
  return `<p class="muted">${t('Under 5 units is a shortage. Under 4 days to expiry is a warning. Expired blood is hidden from the public list.')}</p>${table}
    <h3>${t('Add new bags')}</h3><div class="form"><div class="row"><label>${t('Blood group')}<select id="s_group">${options(S.meta.groups, 'O+')}</select></label><label>${t('Units')}<input id="s_units" type="number" min="1" value="1" inputmode="numeric"></label></div>
    <label>${t('Expiry date of these bags')}<input id="s_exp" type="date" value="${soon}"></label><button class="btn" onclick="hAddStock()">${t('Add to stock')}</button></div>`;
}

async function hDiscard(group) { if (await guard(() => api('/hospital/stock/adjust', { blood_group: group, discard: true }))) { toast(t('Expired blood removed.')); dashboard(); } }
async function hAddStock() { if (await guard(() => api('/hospital/stock/adjust', { blood_group: $('s_group').value, delta: $('s_units').value, expires_on: $('s_exp').value }))) { toast(t('Stock updated.')); dashboard(); } }
async function hStock(group, delta) { if (await guard(() => api('/hospital/stock/adjust', { blood_group: group, delta }))) dashboard(); }


function hospitalDonationForm() {
  return `<p class="muted">${t('Record a donation made at your hospital. This updates the donor, the stock and the request.')}</p><div class="form"><div class="row">
    <label>${t('Donor mobile number')}<input id="d_phone" inputmode="tel" placeholder="01XXXXXXXXX"></label><label>${t('Units')}<input id="d_units" type="number" min="1" max="2" value="1" inputmode="numeric"></label></div>
    <div class="row"><label>${t('Or donor ID (optional)')}<input id="d_donor" type="number" inputmode="numeric" placeholder="${t('See the ID in Matches')}"></label>
    <label>${t('Request number (optional)')}<input id="d_request" type="number" inputmode="numeric"></label></div><button class="btn" onclick="hDonation()">${t('Record donation')}</button></div>`;
}

async function hDonation() {
  const body = { donor_phone: $('d_phone').value, donor_id: $('d_donor').value, units: $('d_units').value, request_id: $('d_request').value || null };
  if (await guard(() => api('/hospital/donations', body))) { toast(t('Donation recorded.')); dashboard(); }
}

async function hospitalInfo() {
  const h = await api('/hospital/profile');
  return `<p class="muted">${t('This is shown on the public blood stock page. Add a phone number so people can call you.')}</p><div class="form"><b>${esc(h.name)}</b>
    <div class="row"><label>${t('District')}<select id="h_area">${districtOptions(h.area)}</select></label><label>${t('Upazila or area (optional)')}<input id="h_upazila" value="${esc(h.upazila || '')}"></label></div>
    <div class="row"><label>${t('Hospital phone')}<input id="h_phone" inputmode="tel" value="${esc(h.phone || '')}"></label><label>${t('Address')}<input id="h_address" value="${esc(h.address || '')}"></label></div>
    <button class="btn" onclick="saveHospital()">${t('Save changes')}</button></div>` + accountTools();
}
async function saveHospital() {
  if (await guard(() => api('/hospital/profile', { area: $('h_area').value, upazila: $('h_upazila').value, phone: $('h_phone').value, address: $('h_address').value }))) { toast(t('Profile saved.')); dashboard(); }
}

async function hospitalThal() {
  const rows = await api('/hospital/thal');
  const list = rows.length ? rows.map(p => `<div class="item"><div><b>${esc(p.name)}</b> ${pill(p.blood_group, 'blood')}<p class="muted">${t('Next transfusion: {d}', { d: p.next_date })} · ${t('every {n} weeks', { n: p.frequency_weeks })}
      · ${t('Regular donors')}: ${p.regular_donors.map(d => '#' + d.donor_id + ' ' + esc(d.name)).join(', ') || '-'}</p></div><button class="btn ghost small" onclick="thalDone(${p.id})">${t('Mark transfusion done')}</button></div>`).join('') : empty('No regular patients yet.');
  return list + `<h3>${t('Add a regular patient')}</h3><div class="form"><div class="row"><label>${t('Patient name')}<input id="t_name"></label><label>${t('Blood group')}<select id="t_group">${options(S.meta.groups)}</select></label></div>
    <div class="row"><label>${t('Next transfusion date')}<input id="t_date" type="date"></label><label>${t('Repeat every (weeks)')}<input id="t_weeks" type="number" min="1" value="3"></label></div>
    <button class="btn" onclick="thalAdd()">${t('Add patient')}</button></div>`;
}
async function thalAdd() { if (await guard(() => api('/hospital/thal', { name: $('t_name').value, blood_group: $('t_group').value, next_date: $('t_date').value, frequency_weeks: $('t_weeks').value }))) dashboard(); }
async function thalDone(id) { if (await guard(() => api('/hospital/thal/' + id + '/done', {}))) { toast(t('Next date updated.')); dashboard(); } }

// ---------- admin ----------

async function adminDash() {
  const tab = currentTab('admin', 'approvals');
  let body = '';
  if (tab === 'approvals') {
    const rows = await api('/admin/pending');
    body = rows.length ? rows.map(u => `<div class="item"><div><b>${esc(u.name)}</b><p class="muted">${esc(u.phone)} · ${esc(u.email || '')} · ${esc(u.hospital_name || '')} (${esc(t(u.area || ''))})</p></div><button class="btn small" onclick="approve(${u.id})">${t('Approve')}</button></div>`).join('') : empty('Nothing is waiting for approval.');
  } else if (tab === 'users') {
    body = await adminUsers(S.userQuery || '', 0);
  } else if (tab === 'report') {
    const r = await api('/admin/report');
    body = `<div class="grid2"><div><h3>${t('Blood still needed')}</h3>${barsHtml(S.meta.groups.map(g => [g, r.demand[g]]), 0, 'red')}</div><div><h3>${t('Blood in stock')}</h3>${barsHtml(S.meta.groups.map(g => [g, r.supply[g]]), 0, 'green')}</div></div>
      <div class="grid2"><div><h3>${t('Requests by status')}</h3>${barsHtml(Object.entries(r.statuses).map(e => [t(cap(e[0])), e[1]]), 0, 'blue')}</div><div><h3>${t('Donations by month')}</h3>${r.donations_by_month.length ? barsHtml(r.donations_by_month, 0, 'red') : empty('No donations yet.')}</div></div>
      <h3>${t('Donors by district')}</h3>${barsHtml(r.donors_by_district.map(e => [t(e[0]), e[1]]), 0, 'green')}`;
  } else if (tab === 'audit') {
    body = tableHtml(['When', 'Who', 'Action', 'Detail'], (await api('/admin/audit')).map(a => [esc(a.created_at), esc(a.name || '-'), esc(a.action), esc(a.detail)]));
  } else {
    body = tableHtml(['When', 'Phone', 'Message', 'Status'], (await api('/admin/sms')).map(x => [esc(x.created_at), esc(x.phone), esc(x.message), esc(x.status)])) +
      (S.meta.demo_sms ? '<p class="muted small">' + t('SMS messages are simulated and only stored here.') + '</p>' : '');
  }
  $('app').innerHTML = `<section class="container"><div class="dash-head"><div><h1 class="page">${t('Admin dashboard')}</h1></div></div>
    ${tabsHtml('admin', [['approvals', 'Approvals'], ['users', 'Users'], ['report', 'Reports'], ['audit', 'Audit log'], ['sms', 'SMS log']])}<div class="card">${body}</div></section>`;
}

async function adminUsers(q, offset) {
  S.userQuery = q;
  const data = await api('/admin/users?q=' + encodeURIComponent(q) + '&offset=' + offset);
  const rows = data.items.map(u => [esc(u.name), esc(u.phone), esc(u.email || ''), t(cap(u.role)), statusPill(u.status === 'active' ? 'Active' : cap(u.status)), esc(u.hospital_name || ''),
    u.role === 'admin' ? '' : (u.status === 'suspended' ? '<button class="btn ghost small" onclick="setUserStatus(' + u.id + ',\'activate\')">' + t('Activate') + '</button>'
      : u.status === 'active' ? '<button class="btn ghost small" onclick="setUserStatus(' + u.id + ',\'suspend\')">' + t('Suspend') + '</button>' : '')]);
  return `<div class="row"><label>${t('Search by name, phone or email')}<input id="u_q" value="${esc(q)}" onkeydown="if(event.key==='Enter')searchUsers()"></label><span class="actions"><button class="btn small" onclick="searchUsers()">${t('Search')}</button></span></div>` +
    tableHtml(['Name', 'Phone', 'Email', 'Role', 'Status', 'Hospital', 'Action'], rows) +
    (offset ? '<button class="btn ghost small" onclick="pageUsers(' + Math.max(0, offset - 50) + ')">' + t('Previous') + '</button> ' : '') +
    (data.more ? '<button class="btn ghost small" onclick="pageUsers(' + (offset + 50) + ')">' + t('Next') + '</button>' : '');
}
async function searchUsers() { S.userQuery = $('u_q').value; dashboard(); }
async function pageUsers(offset) { $('app').querySelector('.card').innerHTML = await adminUsers(S.userQuery || '', offset); }
async function setUserStatus(id, action) { if (await guard(() => api('/admin/users/' + id + '/' + action, {}))) { toast(t('Account updated.')); dashboard(); } }
async function approve(id) { if (await guard(() => api('/admin/users/' + id + '/approve', {}))) { toast(t('Account approved.')); dashboard(); } }

// Shared helpers: API calls, messages, dialogs, navigation bar, footer. Made by Krisanu.
const $ = id => document.getElementById(id);
const S = { user: null, meta: null, tab: {}, unread: 0 };

const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// Talk to the backend. Throws an Error (with the server message) when something is wrong.
async function api(path, body) {
  const options = { credentials: 'same-origin' };
  if (body !== undefined) {
    options.method = 'POST';
    options.headers = { 'Content-Type': 'application/json' };
    options.body = JSON.stringify(body);
  }
  let response;
  try { response = await fetch('/api' + path, options); }
  catch (e) { throw new Error('No internet connection. Please try again.'); }
  let data = {};
  try { data = await response.json(); } catch (e) { /* empty body */ }
  if (!response.ok) {
    const error = new Error(data.error || 'Something went wrong.');
    error.status = response.status;
    throw error;
  }
  return data;
}

// Run an action; show the error as a message instead of breaking the page.
async function guard(action) {
  try { return await action(); }
  catch (error) { toast(tm(error.message), 'err'); return null; }
}

function toast(message, kind) {
  const box = document.createElement('div');
  box.className = 'toast ' + (kind || 'ok');
  box.textContent = message;
  $('toast').appendChild(box);
  setTimeout(() => box.remove(), 4200);
}

function modal(html) {
  $('modal').innerHTML = '<div class="overlay" onclick="closeModal(event)"><div class="dialog" role="dialog">' + html +
    '<div class="dialog-actions"><button class="btn ghost" onclick="closeModal()">' + t('Close') + '</button></div></div></div>';
}
function closeModal(event) {
  if (!event || event.target.classList.contains('overlay')) $('modal').innerHTML = '';
}

const options = (list, selected) => list.map(x => '<option value="' + esc(x) + '"' + (x === selected ? ' selected' : '') + '>' + esc(t(x)) + '</option>').join('');
const hospitalOptions = selected => S.meta.hospitals.map(h => '<option value="' + h.id + '"' + (h.id === selected ? ' selected' : '') + '>' + esc(h.name) + ' (' + esc(t(h.area)) + ')</option>').join('');
// District list grouped by division (8 divisions, 64 districts). allLabel adds a first option with an empty value.
const districtOptions = (selected, allLabel) => (allLabel ? '<option value="">' + esc(t(allLabel)) + '</option>' : '') +
  S.meta.divisions.map(d => '<optgroup label="' + esc(t('{d} Division', { d: t(d.name) })) + '">' + d.districts.map(x => '<option value="' + esc(x) + '"' + (x === selected ? ' selected' : '') + '>' + esc(t(x)) + '</option>').join('') + '</optgroup>').join('');
const areaText = (area, upazila) => esc(t(area)) + (upazila ? ', ' + esc(upazila) : '');
// Password box with a Show / Hide button, so people can check what they typed on a small phone keyboard.
const passField = (id, label, auto, onkey) => '<label>' + t(label) + '<span class="pw"><input id="' + id + '" type="password" autocomplete="' + auto + '"' + (onkey ? ' onkeydown="if(event.key===\'Enter\')' + onkey + '"' : '') + '>' +
  '<button type="button" class="eye" onclick="togglePw(\'' + id + '\',this)">' + t('Show') + '</button></span></label>';
function togglePw(id, button) {
  const box = $(id), hidden = box.type === 'password';
  box.type = hidden ? 'text' : 'password';
  button.textContent = t(hidden ? 'Hide' : 'Show');
}
// Share a text through the phone's share sheet (WhatsApp, Messenger, SMS...), or open WhatsApp on a computer.
function shareText(text) {
  if (navigator.share) { navigator.share({ text }).catch(() => {}); return; }
  window.open('https://wa.me/?text=' + encodeURIComponent(text), '_blank', 'noopener');
}
const telLink = (phone, label) => phone ? '<a class="btn ghost small" href="tel:' + esc(phone) + '">' + esc(label || phone) + '</a>' : '';
const pill = (text, kind) => '<span class="pill ' + (kind || '') + '">' + esc(t(text)) + '</span>';
const STATUS_KIND = { Pending: 'warn', Verified: 'info', Fulfilled: 'ok', Rejected: 'bad', Closed: '', Asked: 'warn', Accepted: 'ok', Declined: 'bad', Donated: 'ok', Normal: '', Urgent: 'warn', Critical: 'bad', Cancelled: 'bad', Expired: '', Suspended: 'bad', Active: 'ok' };
const cap = s => s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
const statusPill = s => pill(cap(s), STATUS_KIND[cap(s)]);
const empty = text => '<div class="empty">' + esc(t(text)) + '</div>';
const drop = (size, cls) => '<svg class="drop ' + (cls || '') + '" width="' + size + '" viewBox="0 0 64 80" aria-hidden="true"><path d="M32 3C32 3 7 33 7 52a25 25 0 0 0 50 0C57 33 32 3 32 3z" fill="url(#dropg)"/><path d="M20 50a12 12 0 0 0 9 12" stroke="#fff" stroke-opacity=".55" stroke-width="4" fill="none" stroke-linecap="round"/></svg>';

function tableHtml(headers, rows) {
  return '<div class="scroll"><table><thead><tr>' + headers.map(h => '<th>' + esc(t(h)) + '</th>').join('') + '</tr></thead><tbody>' +
    rows.map(r => '<tr>' + r.map(c => '<td>' + c + '</td>').join('') + '</tr>').join('') + '</tbody></table></div>';
}

function barsHtml(pairs, max, kind) {
  const top = Math.max(max || 0, ...pairs.map(p => p[1]), 1);
  return pairs.map(p => '<div class="bar"><span class="bl">' + esc(p[0]) + '</span><i class="' + (kind || '') + '" style="width:' + Math.round(p[1] / top * 100) + '%"></i><b>' + p[1] + '</b></div>').join('');
}

function renderNav() {
  const hash = location.hash.split('?')[0] || '#/';
  const links = [['#/', 'Home'], ['#/needs', 'Urgent needs'], ['#/find', 'Find blood'], ['#/request', 'Request blood'], ['#/guide', 'Donor guide']];
  const user = S.user;
  $('nav').innerHTML = '<header class="top"><a class="brand" href="#/">' + drop(26) + '<span>Life<b>Link</b></span></a>' +
    '<nav class="links">' + links.map(l => '<a href="' + l[0] + '"' + (hash === l[0] ? ' class="on"' : '') + '>' + t(l[1]) + '</a>').join('') + '</nav>' +
    '<div class="right"><button class="lang" onclick="setLang(LANG === \'en\' ? \'bn\' : \'en\')" aria-label="Language">' + (LANG === 'en' ? 'বাংলা' : 'English') + '</button>' +
    (user
      ? '<a class="bell" href="#/notifications" aria-label="' + t('Notifications') + '"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>' + (S.unread ? '<span class="dot">' + S.unread + '</span>' : '') + '</a>' +
        '<a class="btn small" href="#/dashboard">' + t('Dashboard') + '</a><button class="btn ghost small" onclick="logout()">' + t('Log out') + '</button>'
      : '<a class="btn ghost small" href="#/login">' + t('Log in') + '</a><a class="btn small" href="#/register">' + t('Join') + '</a>') +
    '</div></header>';
}

function renderFooter() {
  $('foot').innerHTML = '<div class="container foot"><div><b>Life<span>Link</span></b><p>' + t('Safe blood, shared quickly. Always follow the medical screening at the blood centre.') + '</p></div>' +
    '<div class="made"><a href="#/privacy">' + t('Privacy and terms') + '</a><br>' + t('Made by') + ' <b>Krisanu</b></div></div>';
}

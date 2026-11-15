// Start the app and switch pages when the address (#/...) changes. Made by Krisanu.
const PAGES = {
  '/': () => home(), '/find': () => findBlood(), '/request': () => requestPage(), '/guide': () => guide(),
  '/login': () => loginPage(), '/register': () => registerPage(), '/dashboard': () => dashboard(), '/notifications': () => notificationsPage(),
  '/needs': () => needsPage(), '/privacy': () => privacyPage(), '/forgot': () => forgotPage()
};

async function refreshUser() {
  try {
    S.user = (await api('/auth/me')).user;
    S.unread = S.user ? (await api('/notifications')).unread : 0;
  } catch (e) { S.user = null; S.unread = 0; }
}

async function showPage() {
  const path = (location.hash.slice(1) || '/').split('?')[0];
  renderNav();
  renderFooter();
  $('app').innerHTML = '<div class="loading"><span></span></div>';
  await guard(PAGES[path] || PAGES['/']);
  window.scrollTo(0, 0);
}

function setLang(lang) {
  LANG = lang;
  try { localStorage.setItem('ll_lang', lang); } catch (e) { /* storage may be blocked */ }
  document.documentElement.lang = lang;
  document.title = t('LifeLink: Blood Donation Network');
  showPage();
}

async function logout() {
  await guard(() => api('/auth/logout', {}));
  S.user = null; S.unread = 0;
  location.hash = '#/';
  showPage();
}

async function boot() {
  document.documentElement.lang = LANG;
  document.title = t('LifeLink: Blood Donation Network');
  S.meta = await api('/meta');
  await refreshUser();
  window.addEventListener('hashchange', showPage);
  showPage();
}
if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}));
boot();

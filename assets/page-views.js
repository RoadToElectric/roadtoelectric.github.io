/* Page-view counter. Each visit calls the Supabase function hit_page (the only thing the public key can do: add 1 to the page and to the whole site,
   in a total table, page_views, and in a daily table, page_views_daily; monthly / weekly / yearly roll-ups are the views page_views_monthly etc., readable only by the owner).
   One count per page per browser session; a visit from localhost or a file is shown but not counted. The numbers are shown at the bottom of the page.
   A counted visit also sends the reading mode (the site's own view, mobile or desktop): hit_page adds 1 to a counter per day / page / mode / country (the country is read from the request
   by the database; the IP address is never stored, and there is no visit-level log). The owner's own browser is not counted (localStorage 'rte-notrack', set when stats.html is unlocked).
   New or returning reader (2026-11-13): the browser keeps two dates in its own localStorage ('rte-seen': first and last visit, dropped after 390 days (13 months)) and tells the database only 'new' or 'back'
   (a first visit on an earlier day = back) plus whether this is its first counted view of the day. No number or identifier is sent or stored: hit_page adds 1 to a daily counter per kind.
   The private page stats.html reads the counters through the passphrase-protected function site_stats. */
(function(){
  'use strict';
  var URL_ = 'https://rtmlxvjpjxcvjdykrkvm.supabase.co/rest/v1/rpc/hit_page', KEY = 'sb_publishable_RU6wsMy6kxytGFfsMR4l6w_uSSntvgP';
  var page = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  if(!/\.html$/.test(page)) page = 'index.html';
  var local = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname) || location.protocol === 'file:' || /\.localhost$/.test(location.hostname);
  var seen = false, ssKey = 'rte-pv:' + page;
  try{ seen = sessionStorage.getItem(ssKey) === '1'; }catch(e){}
  var bot = !!navigator.webdriver || /bot|crawl|spider|headless|preview/i.test(navigator.userAgent || '');
  var mine = false; try{ mine = localStorage.getItem('rte-notrack') === '1' || localStorage.getItem('rte-optout') === '1'; }catch(e){}       // rte-notrack: the owner's browser; rte-optout: a reader's "Don't count my visits" switch (contact.html#privacy)
  var count = !local && !seen && !bot && !mine;
  // new or returning reader: only 'new' / 'back' and 'first view of the day' leave the browser, never an identifier
  var RK = 'rte-seen', today = (function(){ try{ return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Toronto' }).format(new Date()); }catch(e){ return new Date().toISOString().slice(0, 10); } })(), mark = null;
  try{ var rawMark = JSON.parse(localStorage.getItem(RK) || 'null'); if(rawMark && /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(rawMark.f) && /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(rawMark.l) && (Date.parse(today) - Date.parse(rawMark.l)) / 864e5 < 390) mark = rawMark; }catch(e){}
  var ret = (mark && mark.f < today) ? 'back' : 'new', day1 = !mark || mark.l !== today;
  // the view this page is shown in (assets/view-mode.js)
  function mode(){ return document.documentElement.getAttribute('data-view') === 'mobile' ? 'mobile' : 'desktop'; }
  function fmt(n){ try{ return Number(n).toLocaleString('en-US'); }catch(e){ return String(n); } }
  function show(r){
    if(!r || r.page == null) return;
    var host = document.querySelector('.page-footer'), el = document.getElementById('rte-views');
    if(!el){
      el = document.createElement('div'); el.id = 'rte-views'; el.className = 'rte-views';
      if(host) host.appendChild(el); else { var pg = document.querySelector('.main .page') || document.querySelector('.page') || document.body; pg.appendChild(el); }
    }
    el.innerHTML = '👁 <b>' + fmt(r.page) + '</b> views of this page · <b>' + fmt(r.site) + '</b> across the whole site · <a href="contact.html#privacy" style="color:inherit">Privacy and opt-out</a>';
  }
  var st = document.createElement('style');
  st.textContent = '.rte-views{margin-top:8px;font-size:12px;font-weight:600;color:var(--text-muted);letter-spacing:.01em}.rte-views b{color:var(--text);font-variant-numeric:tabular-nums}' +
    'div.rte-views:only-child,.page > .rte-views{text-align:center;padding:14px 0 4px}';
  document.head.appendChild(st);
  function go(){
    var ctl = window.AbortController ? new AbortController() : null, t = setTimeout(function(){ if(ctl) ctl.abort(); }, 8000);
    fetch(URL_, { method: 'POST', headers: { 'Content-Type': 'application/json', apikey: KEY, Authorization: 'Bearer ' + KEY }, body: JSON.stringify(count ? { p: page, count_it: true, x_mode: mode(), x_ret: ret, x_day1: day1 } : { p: page, count_it: false }), signal: ctl ? ctl.signal : undefined })
      .then(function(r){ return r.ok ? r.json() : null; }).then(function(j){ clearTimeout(t); if(count){ try{ sessionStorage.setItem(ssKey, '1'); }catch(e){} try{ localStorage.setItem(RK, JSON.stringify({ f: mark ? mark.f : today, l: today })); }catch(e){} } show(j); }).catch(function(){ clearTimeout(t); });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
})();

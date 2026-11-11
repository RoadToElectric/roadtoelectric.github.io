/* Page-view counter. Each visit calls the Supabase function hit_page (the only thing the public key can do: add 1 to the page and to the whole site,
   in a total table, page_views, and in a daily table, page_views_daily; monthly / weekly / yearly roll-ups are the views page_views_monthly etc., readable only by the owner).
   One count per page per browser session; a visit from localhost or a file is shown but not counted. The numbers are shown at the bottom of the page.
   A counted visit also sends what the reader uses (the site's own reading mode mobile / desktop, kind of device, window width, referrer host, language, a random id of this browser session):
   hit_page keeps it in page_hits with the reader's country (read from the request by the database; the IP address is never stored). The owner's own browser is not counted
   (localStorage 'rte-notrack', set when stats.html is unlocked). The private page stats.html reads it all through the passphrase-protected function site_stats. */
(function(){
  'use strict';
  var URL_ = 'https://rtmlxvjpjxcvjdykrkvm.supabase.co/rest/v1/rpc/hit_page', KEY = 'sb_publishable_RU6wsMy6kxytGFfsMR4l6w_uSSntvgP';
  var page = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  if(!/\.html$/.test(page)) page = 'index.html';
  var local = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname) || location.protocol === 'file:' || /\.localhost$/.test(location.hostname);
  var seen = false, ssKey = 'rte-pv:' + page;
  try{ seen = sessionStorage.getItem(ssKey) === '1'; }catch(e){}
  var bot = !!navigator.webdriver || /bot|crawl|spider|headless|preview/i.test(navigator.userAgent || '');
  var mine = false; try{ mine = localStorage.getItem('rte-notrack') === '1'; }catch(e){}
  var count = !local && !seen && !bot && !mine;
  function detail(){
    var d = {};
    try{
      d.x_mode = document.documentElement.getAttribute('data-view') === 'mobile' ? 'mobile' : 'desktop';          // assets/view-mode.js: the view this page is shown in
      var coarse = !!(window.matchMedia && window.matchMedia('(pointer: coarse)').matches), sm = Math.min(screen.width || 0, screen.height || 0);
      d.x_device = coarse ? (sm && sm < 600 ? 'phone' : 'tablet') : 'desktop';
      d.x_w = Math.round(window.innerWidth || 0);
      var rf = document.referrer ? new URL(document.referrer).hostname.replace(/^www\./, '') : '';
      if(rf && rf !== location.hostname) d.x_ref = rf;
      d.x_lang = (navigator.language || '').slice(0, 2);
      var sid = null; try{ sid = sessionStorage.getItem('rte-sid'); }catch(e){}
      if(!sid){ sid = ''; var a = new Uint8Array(9); (window.crypto || window.msCrypto).getRandomValues(a); for(var i = 0; i < a.length; i++) sid += (a[i] % 36).toString(36); try{ sessionStorage.setItem('rte-sid', sid); }catch(e){} }
      d.x_sid = sid;
    }catch(e){}
    return d;
  }
  function fmt(n){ try{ return Number(n).toLocaleString('en-US'); }catch(e){ return String(n); } }
  function show(r){
    if(!r || r.page == null) return;
    var host = document.querySelector('.page-footer'), el = document.getElementById('rte-views');
    if(!el){
      el = document.createElement('div'); el.id = 'rte-views'; el.className = 'rte-views';
      if(host) host.appendChild(el); else { var pg = document.querySelector('.main .page') || document.querySelector('.page') || document.body; pg.appendChild(el); }
    }
    el.innerHTML = '👁 <b>' + fmt(r.page) + '</b> views of this page · <b>' + fmt(r.site) + '</b> across the whole site';
  }
  var st = document.createElement('style');
  st.textContent = '.rte-views{margin-top:8px;font-size:12px;font-weight:600;color:var(--text-muted);letter-spacing:.01em}.rte-views b{color:var(--text);font-variant-numeric:tabular-nums}' +
    'div.rte-views:only-child,.page > .rte-views{text-align:center;padding:14px 0 4px}';
  document.head.appendChild(st);
  function go(){
    var ctl = window.AbortController ? new AbortController() : null, t = setTimeout(function(){ if(ctl) ctl.abort(); }, 8000);
    fetch(URL_, { method: 'POST', headers: { 'Content-Type': 'application/json', apikey: KEY, Authorization: 'Bearer ' + KEY }, body: JSON.stringify(Object.assign({ p: page, count_it: count }, count ? detail() : {})), signal: ctl ? ctl.signal : undefined })
      .then(function(r){ return r.ok ? r.json() : null; }).then(function(j){ clearTimeout(t); if(count){ try{ sessionStorage.setItem(ssKey, '1'); }catch(e){} } show(j); }).catch(function(){ clearTimeout(t); });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
})();

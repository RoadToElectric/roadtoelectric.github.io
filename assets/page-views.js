/* Page-view counter. Each visit calls the Supabase function hit_page (the only thing the public key can do: add 1 to the page and to the whole site,
   in a total table, page_views, and in a daily table, page_views_daily; monthly / weekly / yearly roll-ups are the views page_views_monthly etc., readable only by the owner).
   One count per page per browser session; a visit from localhost or a file is shown but not counted. The numbers are shown at the bottom of the page. */
(function(){
  'use strict';
  var URL_ = 'https://rtmlxvjpjxcvjdykrkvm.supabase.co/rest/v1/rpc/hit_page', KEY = 'sb_publishable_RU6wsMy6kxytGFfsMR4l6w_uSSntvgP';
  var page = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  if(!/\.html$/.test(page)) page = 'index.html';
  var local = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname) || location.protocol === 'file:' || /\.localhost$/.test(location.hostname);
  var seen = false, ssKey = 'rte-pv:' + page;
  try{ seen = sessionStorage.getItem(ssKey) === '1'; }catch(e){}
  var bot = !!navigator.webdriver || /bot|crawl|spider|headless|preview/i.test(navigator.userAgent || '');
  var count = !local && !seen && !bot;
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
    fetch(URL_, { method: 'POST', headers: { 'Content-Type': 'application/json', apikey: KEY, Authorization: 'Bearer ' + KEY }, body: JSON.stringify({ p: page, count_it: count }), signal: ctl ? ctl.signal : undefined })
      .then(function(r){ return r.ok ? r.json() : null; }).then(function(j){ clearTimeout(t); if(count){ try{ sessionStorage.setItem(ssKey, '1'); }catch(e){} } show(j); }).catch(function(){ clearTimeout(t); });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
})();

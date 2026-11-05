/* Road to Electric -- desktop / mobile view switch.
   Loaded in <head> (right after the viewport meta) so <html data-view="mobile|desktop"> is set before the first paint; assets/mobile.css reacts to it.
   Which view?   1. the visitor's choice (button, or ?view=mobile / ?view=desktop in the address; ?view=auto forgets the choice), kept in localStorage 'rte-view'
                 2. otherwise automatic: a phone (mobile user agent) or a window narrower than 821 px gets the mobile view, everything else the desktop view.
   On a phone that chose the desktop view the viewport is widened to 1200 px so the desktop layout is shown scaled down, with a floating "Mobile view" button to come back.
   Pages can listen to  window 'rte-viewchange' ({detail:{view}})  and the API is window.RTEView {get(), pref(), set('mobile'|'desktop'|'auto'), toggle()}. */
(function(){
  'use strict';
  var KEY = 'rte-view', root = document.documentElement, current = null;
  function readPref(){ try{ var v = localStorage.getItem(KEY); return v === 'mobile' || v === 'desktop' ? v : null; }catch(e){ return null; } }
  function writePref(v){ try{ if(v) localStorage.setItem(KEY, v); else localStorage.removeItem(KEY); }catch(e){} }
  var q = null; try{ q = new URLSearchParams(location.search).get('view'); }catch(e){}
  if(q === 'mobile' || q === 'desktop') writePref(q); else if(q === 'auto') writePref(null);
  var ua = navigator.userAgent || '';
  var phone = !!(navigator.userAgentData && navigator.userAgentData.mobile) || /Android.+Mobile|iPhone|iPod|Windows Phone|Mobile Safari|Opera Mini|IEMobile/i.test(ua);
  function narrow(){ return !!(window.matchMedia && window.matchMedia('(max-width: 820px)').matches); }
  function resolve(){ return readPref() || ((phone || narrow()) ? 'mobile' : 'desktop'); }
  function viewport(v){
    var m = document.querySelector('meta[name="viewport"]'); if(!m) return;
    m.setAttribute('content', v === 'desktop' && phone ? 'width=1200' : 'width=device-width, initial-scale=1');
  }
  function apply(fire){
    var v = resolve(), changed = v !== current; current = v;
    root.setAttribute('data-view', v); root.setAttribute('data-view-pref', readPref() || 'auto');
    viewport(v);
    if(changed){ root.classList.remove('rte-nav-open'); ui(); if(fire) window.dispatchEvent(new CustomEvent('rte-viewchange', { detail: { view: v } })); }
  }
  function set(v){ writePref(v === 'mobile' || v === 'desktop' ? v : null); apply(true); }
  window.RTEView = { get: function(){ return current; }, pref: readPref, set: set, toggle: function(){ set(current === 'mobile' ? 'desktop' : 'mobile'); } };

  // ---------- buttons (built once the markup exists) ----------
  var link = null, pill = null, burger = null;
  function mk(tag, cls, txt){ var e = document.createElement(tag); e.className = cls; if(txt) e.textContent = txt; return e; }
  function ui(){
    if(!document.body) return;
    var side = document.querySelector('.sidebar'), nav = document.querySelector('.sidebar-nav'), foot = document.querySelector('.sidebar-footer');
    if(side && !burger){
      burger = mk('button', 'rte-menu-btn', '☰'); burger.type = 'button'; burger.setAttribute('aria-label', 'Menu'); burger.setAttribute('aria-expanded', 'false');
      burger.addEventListener('click', function(){ var on = !root.classList.contains('rte-nav-open'); root.classList.toggle('rte-nav-open', on); burger.setAttribute('aria-expanded', String(on)); burger.textContent = on ? '✕' : '☰'; });
      side.appendChild(burger);
      if(nav) nav.addEventListener('click', function(e){ if(e.target.closest('a')){ root.classList.remove('rte-nav-open'); burger.setAttribute('aria-expanded', 'false'); burger.textContent = '☰'; } });
    }
    if(!link){ link = mk('button', 'rte-view-link'); link.type = 'button'; link.addEventListener('click', function(){ window.RTEView.toggle(); }); }
    var label = current === 'mobile' ? '🖥 Switch to desktop view' : '📱 Switch to mobile view';
    link.textContent = label;
    var host = current === 'mobile' ? nav : foot;
    if(host && link.parentNode !== host) host.appendChild(link);
    var needPill = current === 'desktop' && phone;
    if(needPill && !pill){ pill = mk('button', 'rte-view-pill', '📱 Mobile view'); pill.type = 'button'; pill.addEventListener('click', function(){ window.RTEView.set('mobile'); }); document.body.appendChild(pill); }
    if(pill) pill.hidden = !needPill;
  }
  apply(false);
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ui); else ui();
  var t = null;
  window.addEventListener('resize', function(){ if(readPref()) return; clearTimeout(t); t = setTimeout(function(){ apply(true); }, 150); });
})();

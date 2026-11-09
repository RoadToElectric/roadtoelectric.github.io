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
    drawer();
  }

  // ---------- filters drawer: a panel marked data-rte-drawer (optional data-rte-summary = selectors whose values make the one-line summary) becomes a full-screen sheet opened from a bar under the top bar ----------
  var dBar = null, dBtn = null, dSum = null, dDone = null, sumT = null;
  function summary(panel){
    var sels = (panel.getAttribute('data-rte-summary') || '').split(','), out = [], i, e, v;
    for(i = 0; i < sels.length; i++){ e = sels[i] && document.querySelector(sels[i].trim()); if(!e) continue; v = e.tagName === 'SELECT' ? (e.selectedOptions[0] ? e.selectedOptions[0].textContent : '') : e.value; v = (v || '').trim(); if(v) out.push(v); }
    return out.join(' · ');
  }
  function setDrawer(on){
    var panel = document.querySelector('[data-rte-drawer]'); if(!panel || !dBtn) return;
    root.classList.toggle('rte-drawer-open', on); dBtn.setAttribute('aria-expanded', String(on));
    if(on) root.classList.remove('rte-nav-open'); else { dSum.textContent = summary(panel) || 'All data'; dBar.scrollIntoView(); }
  }
  function drawer(){
    var panel = document.querySelector('[data-rte-drawer]'); if(!panel) return;
    if(current !== 'mobile'){ root.classList.remove('rte-drawer-open'); if(dBar) dBar.hidden = true; return; }
    if(!dBar){
      var wrap = panel.parentNode; dBar = mk('div', 'rte-filter-bar'); dBtn = mk('button', 'rte-filter-btn', '☰ ' + (panel.getAttribute('data-rte-drawer') || 'Filters')); dBtn.type = 'button'; dBtn.setAttribute('aria-expanded', 'false');
      dSum = mk('span', 'rte-filter-sum'); dBar.appendChild(dBtn); dBar.appendChild(dSum); wrap.parentNode.insertBefore(dBar, wrap);
      dDone = mk('button', 'rte-drawer-done', 'Show results'); dDone.type = 'button'; panel.appendChild(dDone);
      dBtn.addEventListener('click', function(){ setDrawer(!root.classList.contains('rte-drawer-open')); }); dDone.addEventListener('click', function(){ setDrawer(false); });
      var upd = function(){ clearTimeout(sumT); sumT = setTimeout(function(){ dSum.textContent = summary(panel) || 'All data'; }, 150); };
      panel.addEventListener('change', upd); panel.addEventListener('click', upd); panel.addEventListener('input', upd);
    }
    dBar.hidden = false; dSum.textContent = summary(panel) || 'All data';
  }
  // ---------- wide charts: on a phone they scroll sideways at a readable size instead of shrinking to a third (text under 4 px) ----------
  // An SVG chart whose viewBox is much wider than its box gets a min-width that keeps its smallest text near 8.5 px, and its parent becomes a sideways scroller (class rte-xscroll).
  var MIN_TEXT = 8.5, MAX_K = 0.85, fitT = null;
  function unfit(s){ if(!s.__rteFit) return; s.style.minWidth = ''; s.__rteFit = false; var p = s.parentElement; if(p) p.classList.remove('rte-xscroll'); }
  function fitOne(s){
    var vb = s.viewBox && s.viewBox.baseVal, p = s.parentElement;
    if(current !== 'mobile' || !vb || !vb.width || !p || /map/i.test(s.id) || s.closest('[data-rte-nofit]')){ unfit(s); return; }
    var box = p.clientWidth; if(!box){ return; }
    var texts = s.querySelectorAll('text'); if(texts.length < 3){ unfit(s); return; }
    var min = 99, step = Math.max(1, Math.floor(texts.length / 40)), i, f;
    for(i = 0; i < texts.length; i += step){ f = parseFloat(getComputedStyle(texts[i]).fontSize); if(f && f < min) min = f; }
    var k0 = (s.__rteFit ? parseFloat(s.style.minWidth) : s.getBoundingClientRect().width) / vb.width;   // scale the chart has right now
    if(!s.__rteFit && k0 >= 0.7){ return; }
    var need = Math.min(MAX_K, MIN_TEXT / min), width = Math.round(vb.width * Math.max(need, Math.min(k0, 0.7)));
    if(width <= box + 2){ unfit(s); return; }
    s.style.minWidth = width + 'px'; s.__rteFit = true; p.classList.add('rte-xscroll');
  }
  function fitAll(){ fitT = null; var all = document.querySelectorAll('svg[viewBox]'), i; for(i = 0; i < all.length; i++) fitOne(all[i]); }
  function scheduleFit(ms){ if(fitT) clearTimeout(fitT); fitT = setTimeout(fitAll, ms || 200); }
  function watchCharts(){
    scheduleFit(400);
    if(window.MutationObserver) new MutationObserver(function(list){
      for(var i = 0; i < list.length; i++) for(var j = 0; j < list[i].addedNodes.length; j++){ var n = list[i].addedNodes[j]; if(n.nodeName === 'svg' || (n.querySelector && n.querySelector('svg'))){ scheduleFit(250); return; } }
    }).observe(document.body, { childList: true, subtree: true });
    document.addEventListener('click', function(){ scheduleFit(600); }, true);
    document.addEventListener('change', function(){ scheduleFit(600); }, true);
    window.addEventListener('load', function(){ scheduleFit(300); });
    window.addEventListener('rte-viewchange', function(){ scheduleFit(50); });
    window.addEventListener('resize', function(){ scheduleFit(300); });
  }

  // ---------- section bar (phone): the sections of the page (the direct children of .page) with Previous / Next buttons ----------
  var sn = null, snT = null, snP = null, snN = null, snRaf = null;
  function secList(){
    var pg = document.querySelector('.main .page') || document.querySelector('.page'), out = [], i, c;
    if(!pg) return out;
    for(i = 0; i < pg.children.length; i++){ c = pg.children[i]; if(c.matches('footer, .page-footer, .mfr-sales-preview, .fx-chipbar, script, style') || c.offsetHeight < 80) continue; out.push(c); }
    return out;
  }
  function secOff(){ var b = document.querySelector('.rte-filter-bar:not([hidden]), .fl-bar'); return (b && b.offsetHeight && getComputedStyle(b).position === 'sticky' ? b.offsetHeight : 0) + 6; }
  function secTitle(el){ if(el.getAttribute('data-rte-title')) return el.getAttribute('data-rte-title'); var h = el.querySelector('h1, h2, h3, .wp-eyebrow, .wo-eyebrow'), t = h ? h.textContent.replace(/\s+/g, ' ').trim() : ''; return (t || (el.id ? el.id.replace(/[-_]/g, ' ') : 'Section')).slice(0, 60); }
  function secIdx(list){ var off = secOff() + 40, idx = 0, i; for(i = 0; i < list.length; i++){ if(list[i].getBoundingClientRect().top <= off) idx = i; else break; } return idx; }
  function secUpdate(){
    snRaf = null; if(!sn) return;
    if(current !== 'mobile'){ sn.hidden = true; return; }
    var list = secList(), idx = secIdx(list); sn.hidden = list.length < 2; if(!list.length) return;
    snT.textContent = (idx + 1) + ' / ' + list.length + ' · ' + secTitle(list[idx]); snP.disabled = idx === 0; snN.disabled = idx >= list.length - 1;
  }
  function secSoon(ms){ if(snRaf) return; snRaf = setTimeout(secUpdate, ms || 60); }
  function secGo(dir){
    var list = secList(); if(!list.length) return; var idx = secIdx(list), cur = list[idx], target;
    if(dir < 0){ target = cur.getBoundingClientRect().top - secOff() < -40 ? idx : idx - 1; }      // inside a long section, Previous first goes back to its top
    else target = idx + 1;
    target = Math.max(0, Math.min(list.length - 1, target));
    window.scrollTo({ top: list[target].getBoundingClientRect().top + window.pageYOffset - secOff() - 4, behavior: 'smooth' });
    secSoon(500); secSoon(900);
  }
  function secnav(){
    if(!document.body || !document.querySelector('.page')) return;
    if(!sn){
      sn = mk('div', 'rte-secnav'); sn.setAttribute('role', 'navigation'); sn.setAttribute('aria-label', 'Sections');
      snP = mk('button', 'rte-secnav-prev', '‹ Prev'); snP.type = 'button'; snN = mk('button', 'rte-secnav-next', 'Next ›'); snN.type = 'button'; snT = mk('span', 'rte-secnav-lbl');
      sn.appendChild(snP); sn.appendChild(snT); sn.appendChild(snN); document.body.appendChild(sn);
      snP.addEventListener('click', function(){ secGo(-1); }); snN.addEventListener('click', function(){ secGo(1); });
      window.addEventListener('scroll', function(){ secSoon(60); }, { passive: true }); window.addEventListener('resize', function(){ secSoon(200); });
      document.addEventListener('click', function(){ secSoon(500); }, true); document.addEventListener('change', function(){ secSoon(500); }, true);
      if(window.MutationObserver) new MutationObserver(function(){ secSoon(300); }).observe(document.querySelector('.page'), { attributes: true, childList: true });
    }
    secUpdate();
  }
  document.addEventListener('click', function(e){ var t = e.target.closest && e.target.closest('header.page-header .subtitle'); if(t && current === 'mobile') t.classList.toggle('rte-open'); });   // a long intro: tap to read it all
  window.addEventListener('rte-viewchange', function(){ secnav(); });
  window.addEventListener('load', function(){ secnav(); setTimeout(secnav, 1200); });

  // ---------- native portrait charts: RTEView.native(svg, deskW, deskH, {h}) sizes a chart's drawing to the width of its box on a phone (real pixels, readable text, no sideways scroll) ----------
  // Returns {mobile, W, H}: the chart code draws with these (desktop keeps its own W x H). RTEView.onResize(fn) re-draws after a rotation / view switch.
  window.RTEView.native = function(svgEl, deskW, deskH, opt){
    opt = opt || {};
    var host = svgEl.parentElement, w = svgEl.getBoundingClientRect().width || (host && host.clientWidth) || 0;
    if(current !== 'mobile' || w < 120){ svgEl.removeAttribute('data-rte-nofit'); svgEl.setAttribute('viewBox', '0 0 ' + deskW + ' ' + deskH); return { mobile: false, W: deskW, H: deskH }; }
    var W = Math.max(280, Math.round(w)), H = Math.round(opt.h || Math.min(deskH, W * 0.9));
    svgEl.setAttribute('data-rte-nofit', '1'); svgEl.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    return { mobile: true, W: W, H: H };
  };
  var reCbs = [], reT = null, lastIW = window.innerWidth;
  window.RTEView.onResize = function(fn){ reCbs.push(fn); };
  function fireRe(){ reCbs.forEach(function(f){ try{ f(); }catch(e){ if(window.console) console.error(e); } }); }
  window.addEventListener('resize', function(){ if(current !== 'mobile' || Math.abs(window.innerWidth - lastIW) < 30) return; lastIW = window.innerWidth; clearTimeout(reT); reT = setTimeout(fireRe, 250); });
  window.addEventListener('rte-viewchange', function(){ lastIW = window.innerWidth; clearTimeout(reT); reT = setTimeout(fireRe, 150); });

  apply(false);
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ ui(); watchCharts(); }); else { ui(); watchCharts(); }
  var t = null;
  window.addEventListener('resize', function(){ if(readPref()) return; clearTimeout(t); t = setTimeout(function(){ apply(true); }, 150); });
})();

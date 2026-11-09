/* "Link to this graph": every card gets a small 🔗 button that copies the page address with the current filter selections (?fm=, see filter-memory.js)
   and the card's anchor (#id), so the reader lands directly on that graph, even in the middle of a long page (the scrolling itself is assets/deeplink.js).
   A card without an id gets a stable one from its position among the page's sections (sec-N). */
(function(){
  'use strict';
  function cards(){ return document.querySelectorAll('.page .card, .page .chart-card'); }
  function topSection(el){ var pg = document.querySelector('.main .page') || document.querySelector('.page'), c = el; while(c && c.parentElement !== pg) c = c.parentElement; return c; }
  function ensureId(card){
    if(card.id) return card.id;
    var pg = document.querySelector('.main .page') || document.querySelector('.page'), top = topSection(card), n = pg && top ? Array.prototype.indexOf.call(pg.children, top) : -1;
    if(n < 0) return '';
    card.id = 'sec-' + n + (card === top ? '' : '-' + Array.prototype.indexOf.call(top.querySelectorAll('.card, .chart-card'), card));
    return card.id;
  }
  function copy(text){
    if(navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    return new Promise(function(ok, no){ try{ var t = document.createElement('textarea'); t.value = text; t.style.cssText = 'position:fixed;opacity:0'; document.body.appendChild(t); t.select(); var r = document.execCommand('copy'); document.body.removeChild(t); r ? ok() : no(); }catch(e){ no(e); } });
  }
  function linkFor(card){
    if(window.FilterMemory && FilterMemory.sync) FilterMemory.sync();
    var id = ensureId(card), q = new URLSearchParams(location.search); q.delete('view');          // the reader's own device decides between the phone and the desktop view
    var u = (location.origin === 'null' ? location.href.split('#')[0].split('?')[0] : location.origin + location.pathname) + (q.toString() ? '?' + q.toString() : '');
    return id ? u + '#' + encodeURIComponent(id) : u;
  }
  function addButton(card){
    if(card.querySelector(':scope > .rte-sec-link') || !card.querySelector('h2, h3') || card.offsetHeight < 60) return;
    var b = document.createElement('button'); b.type = 'button'; b.className = 'rte-sec-link'; b.textContent = '🔗';
    b.title = 'Copy a link to this graph (with the current filters)'; b.setAttribute('aria-label', 'Copy a link to this graph');
    b.addEventListener('click', function(e){
      e.stopPropagation();
      copy(linkFor(card)).then(function(){ b.textContent = '✓'; b.classList.add('ok'); }, function(){ b.textContent = '⚠'; })
        .then(function(){ setTimeout(function(){ b.textContent = '🔗'; b.classList.remove('ok'); }, 1500); });
    });
    card.insertBefore(b, card.firstChild);
  }
  function scan(){ var all = cards(), i; for(i = 0; i < all.length; i++){ ensureId(all[i]); addButton(all[i]); } }
  var st = document.createElement('style');
  st.textContent = '.rte-sec-link{float:right;margin:0 0 4px 8px;appearance:none;border:1px solid var(--border);background:var(--surface);color:var(--text-muted);border-radius:999px;width:30px;height:30px;padding:0;font-size:14px;line-height:1;cursor:pointer;opacity:.75}' +
    '.rte-sec-link:hover,.rte-sec-link.ok{opacity:1;border-color:var(--accent);color:var(--accent)}' +
    '@keyframes rteFlash{0%,60%{box-shadow:0 0 0 4px var(--accent)}100%{box-shadow:0 0 0 0 transparent}}.rte-sec-flash{animation:rteFlash 2.2s ease-out 1}';
  document.head.appendChild(st);
  var t = null, soon = function(){ clearTimeout(t); t = setTimeout(scan, 400); };
  window.addEventListener('load', function(){ scan(); setTimeout(scan, 1500); setTimeout(scan, 4000); });
  if(window.MutationObserver) document.addEventListener('DOMContentLoaded', function(){ var pg = document.querySelector('.page'); if(pg) new MutationObserver(soon).observe(pg, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] }); });
})();

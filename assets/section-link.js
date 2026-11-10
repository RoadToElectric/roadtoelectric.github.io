/* Each card also gets a 📷 button that copies the whole chart as a picture (assets/chart-copy.js, loaded here on demand).
   "Link to this graph": every card gets a small 🔗 button that copies the page address with the current filter selections (?fm=, see filter-memory.js)
   and the card's anchor (#id), so the reader lands directly on that graph, even in the middle of a long page (the scrolling itself is assets/deeplink.js).
   A card without an id gets a stable one from its position among the page's sections (sec-N). */
(function(){
  'use strict';
  var BASE = (document.currentScript && document.currentScript.src || '').replace(/[^\/]*$/, '') || 'assets/';
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
  var ccP = null;
  function loadCopyTool(){
    if(window.RteChartCopy) return Promise.resolve();
    return ccP || (ccP = new Promise(function(ok, no){
      var s = document.createElement('script'); s.src = BASE + 'chart-copy.js?v=7'; s.onload = ok; s.onerror = function(){ ccP = null; no(new Error('could not load the copy tool')); };
      document.head.appendChild(s);
    }));
  }
  // click = copy the picture to the clipboard, Shift+click = save it as a .png file, Alt+click = leave the notes out of the picture
  function addCopyButton(card, after){
    if(card.querySelector(':scope > .rte-copy-chart')) return;
    var b = document.createElement('button'); b.type = 'button'; b.className = 'rte-copy-chart'; b.textContent = '📷';
    var tip = 'Copy this chart as an image (Shift+click: save as a PNG file · Alt+click: without the notes)';
    b.title = tip; b.setAttribute('aria-label', 'Copy this chart as an image');
    b.addEventListener('click', function(e){
      e.stopPropagation();
      if(b.disabled) return;
      var canClip = navigator.clipboard && navigator.clipboard.write && window.ClipboardItem && window.isSecureContext, save = e.shiftKey || !canClip;
      var blobP = loadCopyTool().then(function(){ return RteChartCopy.render(card, { notes: !e.altKey }); });
      b.disabled = true; b.textContent = '…';
      var finish = function(sym, msg, ok){ b.textContent = sym; b.title = msg; b.classList.toggle('ok', !!ok); setTimeout(function(){ b.textContent = '📷'; b.title = tip; b.classList.remove('ok'); b.disabled = false; }, 2200); };
      var fail = function(err){ if(window.console) console.error('chart copy failed', err); finish('⚠', 'Could not make the image: ' + (err && err.message || err)); };
      var saveIt = function(msg){ blobP.then(function(bl){ RteChartCopy.download(bl, card); finish('⬇', msg, true); }, fail); };
      if(save) return saveIt(canClip ? 'Saved as a PNG file' : 'Saved as a PNG file (this browser cannot copy images here)');
      navigator.clipboard.write([new ClipboardItem({ 'image/png': blobP })]).then(function(){ finish('✓', 'Image copied: paste it into your post', true); }, function(){ saveIt('Saved as a PNG file (the browser did not allow copying)'); });
    });
    card.insertBefore(b, after ? after.nextSibling : card.firstChild);
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
    addCopyButton(card, b);
  }
  function scan(){ var all = cards(), i; for(i = 0; i < all.length; i++){ ensureId(all[i]); addButton(all[i]); } }
  var st = document.createElement('style');
  st.textContent = '.rte-sec-link{float:right;margin:0 0 4px 8px;appearance:none;border:1px solid var(--border);background:var(--surface);color:var(--text-muted);border-radius:999px;width:30px;height:30px;padding:0;font-size:14px;line-height:1;cursor:pointer;opacity:.75}' +
    '.rte-sec-link:hover,.rte-sec-link.ok{opacity:1;border-color:var(--accent);color:var(--accent)}' +
    '.rte-copy-chart{float:right;margin:0 0 4px 8px;appearance:none;border:1px solid var(--border);background:var(--surface);color:var(--text-muted);border-radius:999px;width:30px;height:30px;padding:0;font-size:14px;line-height:1;cursor:pointer;opacity:.75}' +
    '.rte-copy-chart:hover,.rte-copy-chart.ok{opacity:1;border-color:var(--accent);color:var(--accent)}.rte-copy-chart:disabled{cursor:progress}html[data-view="mobile"] .rte-copy-chart{margin-top:-2px}' +
    '@keyframes rteFlash{0%,60%{box-shadow:0 0 0 4px var(--accent)}100%{box-shadow:0 0 0 0 transparent}}.rte-sec-flash{animation:rteFlash 2.2s ease-out 1}';
  document.head.appendChild(st);
  var t = null, soon = function(){ clearTimeout(t); t = setTimeout(scan, 400); };
  window.addEventListener('load', function(){ scan(); setTimeout(scan, 1500); setTimeout(scan, 4000); setTimeout(function(){ loadCopyTool().catch(function(){}); }, 2500); });
  if(window.MutationObserver) document.addEventListener('DOMContentLoaded', function(){ var pg = document.querySelector('.page'); if(pg) new MutationObserver(soon).observe(pg, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] }); });
})();

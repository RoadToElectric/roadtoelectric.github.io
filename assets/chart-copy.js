/* "Copy this chart as an image": renders a whole card (title, key, bars, notes) to a PNG, without the controls (toggles, drop-downs, the 🔗 / 📷 buttons),
   framed on the card's own background with a small "Road to Electric" footer, ready to paste into a post. Loaded on demand by section-link.js, which owns the button.
   RteChartCopy.render(card, { notes:false }) -> Promise<Blob>;  RteChartCopy.download(blob, card) saves it as a .png file.
   Drawing is done by html-to-image (assets/html-to-image.min.js, MIT): it copies each element's computed style, so CSS-variable colours in the SVG charts come out right. */
(function(){
  'use strict';
  var BASE = (document.currentScript && document.currentScript.src || '').replace(/[^\/]*$/, '') || 'assets/';
  var PAD = 22, FOOT = 34, SITE = 'roadtoelectric.github.io';
  var CLEAR = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
  // controls that mean nothing in a picture; .note is dropped too when the caller asks for a chart without its notes
  var CONTROLS = ['.rte-sec-link', '.rte-copy-chart', '.chart-mode-toggle', '.mfr-reset-link', '.movers-see-all', 'select', 'input[type="range"]', '.tooltip', '[data-nocapture]',
                  '.wo-filters', '.wo-frow', '.wo-tl',                                          // World Oil: filter panel, presets, timeline frame
                  '.tl-chip-group', '.ch-zoom', '.ch-maptools', '.ch-seg', '.ch-bigtoggle',      // Manufacturers year chips, Charging map tools and toggles
                  '.tk-zoom', '.tk-seg', '.tk-toggle', '.pe-era-dots', '.pe-play-btn',           // EV Trucking, Population & Energy, World Population (its Filters header line, which names the year shown, is kept)
                  '.map-zoom-controls', '.wp-fbody', '.wp-frow', '.wp-seg', '.wp-more'].join(', '), NOTES = '.note, .wo-note';

  var st = document.createElement('style'); st.textContent = '.rte-capture-hide{display:none !important}'; document.head.appendChild(st);
  var libP = null;
  function loadLib(){
    if(window.htmlToImage) return Promise.resolve();
    return libP || (libP = new Promise(function(ok, no){
      var s = document.createElement('script'); s.src = BASE + 'html-to-image.min.js?v=1'; s.onload = ok; s.onerror = function(){ libP = null; no(new Error('could not load the image library')); };
      document.head.appendChild(s);
    }));
  }
  function bgOf(el){
    for(var n = el; n && n.nodeType === 1; n = n.parentElement){
      var c = getComputedStyle(n).backgroundColor;
      if(c && c !== 'transparent' && !/rgba\(\s*\d+,\s*\d+,\s*\d+,\s*0\s*\)/.test(c)) return c;
    }
    return '#ffffff';
  }
  function logo(){
    return new Promise(function(ok){ var i = new Image(); i.onload = function(){ ok(i); }; i.onerror = function(){ ok(null); }; i.src = BASE + 'road-to-electric-logo-square-192.png'; });
  }
  function frame(c, r, bg, lg){
    var out = document.createElement('canvas'), pad = PAD * r, foot = FOOT * r;
    out.width = c.width + 2 * pad; out.height = c.height + 2 * pad + foot;
    var x = out.getContext('2d');
    x.fillStyle = bg; x.fillRect(0, 0, out.width, out.height);
    x.drawImage(c, pad, pad);
    var y = pad + c.height + foot * 0.55, ls = 22 * r, tx = pad;
    if(lg){ x.drawImage(lg, pad, y - ls / 2, ls, ls); tx += ls + 8 * r; }
    x.textBaseline = 'middle'; x.font = '700 ' + 13 * r + 'px -apple-system, "Segoe UI", system-ui, Roboto, sans-serif';
    x.fillStyle = '#111827'; x.fillText('Road to Electric', tx, y);
    x.textAlign = 'right'; x.font = '600 ' + 12 * r + 'px -apple-system, "Segoe UI", system-ui, Roboto, sans-serif'; x.fillStyle = '#6b7280';
    x.fillText(SITE, out.width - pad, y);
    return out;
  }
  function render(card, opt){
    opt = opt || {};
    var w = card.offsetWidth, h = card.offsetHeight;
    if(!w || !h) return Promise.reject(new Error('the chart is not visible'));
    var r = Math.max(0.5, Math.min(2, 16000 / (Math.max(w, h) + 2 * PAD + FOOT))), bg = bgOf(card);
    // the controls are hidden in the live page for the few seconds of the drawing (not filtered out of the copy): the library copies every element's measured size,
    // so removing a control from the copy would leave its empty space behind
    var hide = [].slice.call(card.querySelectorAll(CONTROLS + (opt.notes === false ? ', ' + NOTES : '')));
    var restore = function(){ hide.forEach(function(n){ n.classList.remove('rte-capture-hide'); }); };
    hide.forEach(function(n){ n.classList.add('rte-capture-hide'); });
    var o = { pixelRatio: r, backgroundColor: bg, skipFonts: true, fontEmbedCSS: '', imagePlaceholder: CLEAR,
              style: { margin: '0', border: '0', borderWidth: '0', borderInlineWidth: '0', borderBlockWidth: '0', boxShadow: 'none', borderRadius: '0' } };
    var safari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);          // Safari draws nothing on the first pass
    return Promise.all([loadLib(), logo()]).then(function(v){
      var lg = v[1], first = safari ? window.htmlToImage.toCanvas(card, o).catch(function(){}) : Promise.resolve();
      return first.then(function(){ return window.htmlToImage.toCanvas(card, o); }).then(function(c){ restore(); return frame(c, r, bg, lg); });
    }).catch(function(e){ restore(); throw e; }).then(function(out){
      return new Promise(function(ok, no){ out.toBlob(function(b){ b ? ok(b) : no(new Error('the picture is too large for this browser')); }, 'image/png'); });
    });
  }
  function name(card){
    var h = card.querySelector('h2, h3'), t = (h ? h.textContent : card.id || 'chart').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70);
    return 'road-to-electric-' + (t || 'chart') + '.png';
  }
  function download(blob, card){
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name(card); document.body.appendChild(a); a.click();
    setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 1500);
  }
  window.RteChartCopy = { render: render, download: download };
  loadLib().catch(function(){});                                                              // warm up, so the first click is quick
})();

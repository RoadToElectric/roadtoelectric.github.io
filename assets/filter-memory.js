/* Remembers each page's filter selections, and puts them in the address bar so a link carries them.
   - localStorage (30 days, per page): leaving a page and coming back (or opening it in another tab) does not reset the filters.
   - Link: every change also rewrites the page address as  page.html?fm=<encoded selections>  (only what differs from the page's defaults),
     so copying the address, or the floating "Copy link" button, sends exactly this view. A link's selections win over the visitor's remembered ones.
   Three ways to use it:
     FilterMemory.load() / FilterMemory.save(state)      the page keeps its own state object (Manufacturers). A state with a `qs` key (Mix by Country) keeps its own address.
     FilterMemory.attach([...]); FilterMemory.restore()  list the controls: { key, sel, type:'select' | 'check' | 'range' | 'seg' | 'fn', n?, get?, set? }
                                                          seg = a group of buttons, the one with the class `active` (cls) is remembered; fn = { get(), set(v) } for state the page keeps itself
     FilterMemory.auto({ exclude:[ids], extra:[items] }); FilterMemory.restore()
                                                          no list: every select / range / checkbox with an id and every group of buttons with an id is found by itself (a control with data-nofm is skipped)
   Restoring replays the page's own events (change / input / click), so every handler runs exactly as if the visitor had picked the values;
   controls the page builds a moment after load (options, dynamic buttons) are retried for a few seconds. */
(function(){
  const page = location.pathname.split('/').pop() || 'index.html', KEY = 'was-filters:' + page, TTL = 30 * 24 * 3600 * 1000, URLK = 'fm';
  let items = [], extras = [], autoOpts = null, restoring = false, timer = null, used = false;
  const baseline = {};
  const b64e = o => btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  const b64d = s => JSON.parse(decodeURIComponent(escape(atob(s.replace(/-/g, '+').replace(/_/g, '/')))));
  const fromUrl = () => { try{ const v = new URLSearchParams(location.search).get(URLK); return v ? b64d(v) : null; }catch(e){ return null; } };
  const readLocal = () => { try{ const o = JSON.parse(localStorage.getItem(KEY) || 'null'); return o && Date.now() - o.t < TTL ? o.s : null; }catch(e){ return null; } };
  const read = () => { used = true; ensureButton(); return fromUrl() || readLocal(); };
  function toUrl(s){
    try{
      const p = new URLSearchParams(location.search);
      if(s && Object.keys(s).length) p.set(URLK, b64e(s)); else p.delete(URLK);
      const q = p.toString(); history.replaceState(null, '', location.pathname + (q ? '?' + q : '') + location.hash);
    }catch(e){}
  }
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const urlState = s => {                                   // attached pages: only what differs from the defaults the page started with
    if(!curItems().length) return s;
    const d = {}; Object.keys(s).forEach(k => { if(!(k in baseline) || !same(baseline[k], s[k])) d[k] = s[k]; }); return d;
  };
  let pageState = null;                                     // a page that keeps its own state (save()) and also has controls (auto): Mix by Country keeps its core filters in its own address (qs)
  const store = s => { try{ localStorage.setItem(KEY, JSON.stringify({ t:Date.now(), s })); }catch(e){} };
  const write = s => {
    used = true; ensureButton();
    if(s && 'qs' in s){ pageState = s; if(curItems().length){ store(Object.assign({}, s, snap())); toUrl(urlState(snap())); } else store(s); return; }   // own address: nothing in ?fm= for qs
    store(pageState ? Object.assign({}, pageState, s) : s); toUrl(urlState(s));
  };

  // ---------- controls ----------
  const SEG_CLS = ['active', 'on', 'sel', 'selected'];
  function discover(){
    const out = [], skip = e => e.hasAttribute('data-nofm') || (autoOpts && (autoOpts.exclude || []).includes(e.id));
    document.querySelectorAll('select[id]').forEach(e => { if(!skip(e)) out.push({ key:'s:' + e.id, el:e, type:'select' }); });
    document.querySelectorAll('input[id]').forEach(e => {
      if(skip(e)) return;
      if(e.type === 'range') out.push({ key:'r:' + e.id, el:e, type:'range' });
      else if(e.type === 'checkbox') out.push({ key:'c:' + e.id, el:e, type:'check' });
    });
    document.querySelectorAll('[id]').forEach(e => {
      if(skip(e) || e.children.length < 2 || ![...e.children].every(c => c.tagName === 'BUTTON')) return;
      const cls = SEG_CLS.find(c => [...e.children].some(b => b.classList.contains(c)));
      if(cls) out.push({ key:'g:' + e.id, el:e, type:'seg', cls });
    });
    // toggles without an id (.chart-mode-toggle, .wp-seg, .wo-seg ...): keyed by their position and the text of their buttons
    document.querySelectorAll('.chart-mode-toggle:not([id]), .wp-seg:not([id]), .wo-seg:not([id])').forEach((e, n) => {
      if(skip(e) || e.children.length < 2 || ![...e.children].every(c => c.tagName === 'BUTTON')) return;
      const cls = SEG_CLS.find(c => [...e.children].some(b => b.classList.contains(c)));
      if(cls) out.push({ key:'g@' + n + ':' + [...e.children].map(b => b.textContent.trim().slice(0, 6)).join('').replace(/[^a-z0-9]/gi, '').slice(0, 14), el:e, type:'seg', cls });
    });
    return out;
  }
  const curItems = () => {
    if(!autoOpts) return items.concat(extras);
    const found = discover(), els = new Set(found.map(it => it.el));
    // an explicit item for a control the auto-discovery already found is dropped (no double entry)
    return found.concat((autoOpts.extra || []).filter(it => it.type === 'fn' || !els.has(elOf(it)))).concat(extras);
  };
  const elOf = it => it.el || document.querySelectorAll(it.sel)[it.n || 0] || null;
  const activeCls = it => it.cls || 'active';
  function value(it){
    if(it.type === 'fn') return it.get();
    const e = elOf(it); if(!e) return undefined;
    if(it.type === 'select' || it.type === 'range') return e.value;
    if(it.type === 'check') return e.checked;
    if(it.type === 'seg'){ const i = [...e.querySelectorAll('button')].findIndex(b => b.classList.contains(activeCls(it))); return i >= 0 ? i : undefined; }
  }
  function snap(){
    const s = {};
    curItems().forEach(it => { let v; try{ v = value(it); }catch(e){} if(v === undefined) return; s[it.key] = v; if(!(it.key in baseline)) baseline[it.key] = v; });
    return s;
  }
  const sync = () => { clearTimeout(timer); if(!restoring && used && curItems().length) write(snap()); };
  const saveSoon = () => { if(restoring || !used || !curItems().length) return;      // pages that save their own state (save()) have no control list to snapshot
    clearTimeout(timer); timer = setTimeout(() => write(snap()), 80); };
  // true = done (applied, or already what was saved); false = the control is not there yet (or has no such option yet)
  function applyOne(it, v){
    if(it.type === 'fn'){ if(!(it.key in baseline)) { try{ baseline[it.key] = it.get(); }catch(e){} } return it.set(v) !== false; }
    const e = elOf(it); if(!e) return false;
    if(!(it.key in baseline)){ const b = value(it); if(b !== undefined) baseline[it.key] = b; }
    if(it.type === 'select'){
      if(e.value === v) return true;
      if(![...e.options].some(o => o.value === v)) return false;
      e.value = v; e.dispatchEvent(new Event('change', { bubbles:true })); return true;
    }
    if(it.type === 'range'){ if(e.value !== v){ e.value = v; e.dispatchEvent(new Event('input', { bubbles:true })); } return true; }
    if(it.type === 'check'){ if(e.checked !== v){ e.checked = v; e.dispatchEvent(new Event('change', { bubbles:true })); } return true; }
    if(it.type === 'seg'){
      const b = [...e.querySelectorAll('button')][v]; if(!b) return false;
      if(!b.classList.contains(activeCls(it)) && !b.disabled) b.click();
      return true;
    }
    return true;
  }
  function restore(){
    used = true; ensureButton();
    curItems().forEach(it => { try{ const v = value(it); if(v !== undefined && !(it.key in baseline)) baseline[it.key] = v; }catch(e){} });   // the page's own defaults, before anything is put back
    const s = fromUrl() || readLocal(); if(!s) return;
    const done = new Set(); let tries = 0;
    const step = () => {
      restoring = true;
      try{ curItems().forEach(it => { if(it.key in s && !done.has(it.key) && applyOne(it, s[it.key])) done.add(it.key); }); } finally { restoring = false; }
      if(Object.keys(s).some(k => k !== 'qs' && !done.has(k)) && ++tries < 12) return void setTimeout(step, 300);   // controls the page builds late are retried for ~3.5 s
      saveSoon();
    };
    step();
  }

  // ---------- copy-link button ----------
  function ensureButton(){
    if(document.getElementById('fm-copy') || document.getElementById('copy-link-btn')) return;
    const make = () => {
      if(document.getElementById('fm-copy') || !document.body) return;
      const b = document.createElement('button'); b.id = 'fm-copy'; b.type = 'button'; b.textContent = '🔗 Copy link to this view'; b.title = 'Copies a link that reproduces the current filter selections';
      b.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:900;border:1px solid var(--border,#cbd5e1);background:var(--surface,#fff);color:var(--text,#0f172a);border-radius:999px;padding:8px 14px;font:inherit;font-size:12.5px;font-weight:800;cursor:pointer;box-shadow:0 6px 18px rgba(0,16,40,.22)';
      b.addEventListener('click', async () => {
        sync();
        const url = location.href; let ok = false;
        try{ await navigator.clipboard.writeText(url); ok = true; }catch(e){ try{ const t = document.createElement('textarea'); t.value = url; t.style.cssText = 'position:fixed;opacity:0'; document.body.appendChild(t); t.select(); ok = document.execCommand('copy'); document.body.removeChild(t); }catch(e2){} }
        const o = b.textContent; b.textContent = ok ? '✓ Link copied' : '⚠ Copy failed — copy the address bar'; setTimeout(() => { b.textContent = o; }, 1700);
      });
      document.body.appendChild(b);
    };
    if(document.body) make(); else document.addEventListener('DOMContentLoaded', make);
  }

  ['click', 'change', 'input'].forEach(ev => document.addEventListener(ev, saveSoon, true));
  window.FilterMemory = { load:read, save:write, attach(list){ used = true; items = list; ensureButton(); }, auto(o){ used = true; autoOpts = o || {}; ensureButton(); }, extra(list){ extras = extras.concat(list); }, restore, sync };
})();

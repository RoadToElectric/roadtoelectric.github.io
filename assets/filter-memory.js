/* Remembers each page's filter selections, so leaving a page and coming back (or opening it in another tab) does not reset them.
   Stored per page in localStorage for 30 days. Two ways to use it:
     FilterMemory.load() / FilterMemory.save(state)      the page keeps its own state object (Manufacturers, Mix by Country)
     FilterMemory.attach([...]); FilterMemory.restore()  simple pages: list the controls and they are saved on every change and put back on load
       { key, sel, type:'select' | 'check' | 'range' | 'seg', n? }   seg = a group of buttons, the one with the class `active` (cls) is remembered
   Restoring replays the page's own events (change / input / click), so every handler runs exactly as if the visitor had picked the values;
   controls the page builds a moment after load (options, dynamic buttons) are retried for a few seconds. */
(function(){
  const page = location.pathname.split('/').pop() || 'index.html', KEY = 'was-filters:' + page, TTL = 30 * 24 * 3600 * 1000;
  let items = [], restoring = false, timer = null;
  const read = () => { try{ const o = JSON.parse(localStorage.getItem(KEY) || 'null'); return o && Date.now() - o.t < TTL ? o.s : null; }catch(e){ return null; } };
  const write = s => { try{ localStorage.setItem(KEY, JSON.stringify({ t:Date.now(), s })); }catch(e){} };
  const el = it => document.querySelectorAll(it.sel)[it.n || 0] || null;
  const activeCls = it => it.cls || 'active';
  function snap(){
    const s = {};
    items.forEach(it => {
      const e = el(it); if(!e) return;
      if(it.type === 'select' || it.type === 'range') s[it.key] = e.value;
      else if(it.type === 'check') s[it.key] = e.checked;
      else if(it.type === 'seg'){ const i = [...e.querySelectorAll('button')].findIndex(b => b.classList.contains(activeCls(it))); if(i >= 0) s[it.key] = i; }
    });
    return s;
  }
  const saveSoon = () => { if(restoring || !items.length) return; clearTimeout(timer); timer = setTimeout(() => write(snap()), 80); };
  // true = done (applied, or already what was saved); false = the control is not there yet (or has no such option yet)
  function applyOne(it, v){
    const e = el(it); if(!e) return false;
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
    const s = read(); if(!s) return;
    let pending = items.filter(it => it.key in s), tries = 0;
    const step = () => {
      restoring = true;
      try{ pending = pending.filter(it => !applyOne(it, s[it.key])); } finally { restoring = false; }
      if(pending.length && ++tries < 12) setTimeout(step, 300);
      else saveSoon();
    };
    step();
  }
  ['click', 'change', 'input'].forEach(ev => document.addEventListener(ev, saveSoon, true));
  window.FilterMemory = { load:read, save:write, attach(list){ items = list; }, restore };
})();

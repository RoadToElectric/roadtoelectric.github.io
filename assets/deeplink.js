// Deep links (e.g. manufacturers.html#map-card, or the 🔗 button of a graph): scroll to the section once the page has drawn and flash it.
// Loaded in <head> so the hash is read before any script rewrites the URL; retries because the charts are drawn (and the filters of a shared link put back) after load.
(function(){
  const id = decodeURIComponent((location.hash || '').replace('#', ''));
  if(!id) return;
  let flashed = false, stop = false;
  ['wheel', 'touchstart', 'keydown'].forEach(ev => window.addEventListener(ev, () => { stop = true; }, { once:true, passive:true }));   // the reader took over: no more automatic scrolling
  const go = () => {
    if(stop) return; const el = document.getElementById(id); if(!el || !el.offsetHeight) return;
    el.style.scrollMarginTop = '72px'; el.scrollIntoView({ block:'start' });
    if(!flashed){ flashed = true; el.classList.add('rte-sec-flash'); setTimeout(() => el.classList.remove('rte-sec-flash'), 2400); }
  };
  window.addEventListener('load', () => { go(); [400, 1000, 2000, 3500].forEach(ms => setTimeout(go, ms)); });
})();

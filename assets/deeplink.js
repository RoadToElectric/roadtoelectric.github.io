// Deep links from the Home cards (e.g. manufacturers.html#map-card): scroll to the section once the page has drawn.
// Loaded in <head> so the hash is read before any script rewrites the URL; retries because the charts are drawn after load.
(function(){
  const id = decodeURIComponent((location.hash || '').replace('#', ''));
  if(!id) return;
  const go = () => { const el = document.getElementById(id); if(!el) return; el.style.scrollMarginTop = '72px'; el.scrollIntoView({ block:'start' }); };
  window.addEventListener('load', () => { go(); setTimeout(go, 600); setTimeout(go, 1600); });
})();

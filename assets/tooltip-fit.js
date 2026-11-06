/* Road to Electric -- keeps every hover tooltip readable.
   A tooltip that would start above the top of the window (or run past a side) is shifted back inside with the CSS `translate` property, which stacks on top of each page's own positioning.
   A tooltip taller than about half the window is first made wider; if it is still taller than the window it is capped to the window height with its top kept visible.
   Covers .tooltip (Mix, Country, Population & Energy, World Car Sales) and the tooltips of Manufacturers (.bw-tip), EV Trucking (.tk-tip), World Oil (.wo-tip), World Population (.wp-tip) and EV Charging (.ch-tip). */
(function(){
  'use strict';
  var SEL = '.tooltip, .bw-tip, .tk-tip, .wo-tip, .wp-tip, .ch-tip', M = 8, CFG = { attributes: true, attributeFilter: ['style'], childList: true, subtree: true };
  function fit(t){
    var o = t.__ttObs; if(o) o.disconnect();
    try{
      if(t.__ttSet){ t.style.maxWidth = ''; t.style.maxHeight = ''; t.style.overflow = ''; t.__ttSet = false; }
      t.style.translate = '';
      if(!t.getClientRects().length) return;                      // display:none
      var vh = window.innerHeight, vw = window.innerWidth, r = t.getBoundingClientRect();
      if(r.height > vh * 0.55){ t.style.maxWidth = 'min(460px, 94vw)'; t.__ttSet = true; r = t.getBoundingClientRect(); }      // long text: wider, so it needs fewer lines
      if(r.height > vh - 2 * M){ t.style.maxHeight = (vh - 2 * M) + 'px'; t.style.overflow = 'hidden'; t.__ttSet = true; r = t.getBoundingClientRect(); }
      var dx = 0, dy = 0;
      if(r.top < M) dy = M - r.top; else if(r.bottom > vh - M) dy = (vh - M) - r.bottom;
      if(r.left < M) dx = M - r.left; else if(r.right > vw - M) dx = (vw - M) - r.right;
      if(dx || dy) t.style.translate = Math.round(dx) + 'px ' + Math.round(dy) + 'px';
    }finally{ if(o) o.observe(t, CFG); }
  }
  function attach(t){
    if(t.__ttObs) return;
    t.__ttObs = new MutationObserver(function(){ fit(t); });
    t.__ttObs.observe(t, CFG);
  }
  function scan(root){
    if(root.nodeType !== 1) return;
    if(root.matches && root.matches(SEL)) attach(root);
    var all = root.querySelectorAll ? root.querySelectorAll(SEL) : [], i;
    for(i = 0; i < all.length; i++) attach(all[i]);
  }
  function start(){
    scan(document.body);
    new MutationObserver(function(list){ for(var i = 0; i < list.length; i++) for(var j = 0; j < list[i].addedNodes.length; j++) scan(list[i].addedNodes[j]); }).observe(document.body, { childList: true, subtree: true });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();

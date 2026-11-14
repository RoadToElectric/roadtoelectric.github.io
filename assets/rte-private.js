/* Local-only data overlay hook. On the public site this does nothing. On localhost / 127.0.0.1 / file:// it loads assets/private/me-bscb.js
   (git-ignored; the BestSellingCarsBlog-exclusive Middle East data kept for personal use, see the population log 2026-11-14) which merges itself into the page constants.
   Pages call RTEPrivate.merge() again after a lazily loaded data asset arrives, and RTEPrivate.mixTop / mixNotes from the Mix page's inline script. */
(function(){
  var h = location.hostname, local = location.protocol === 'file:' || h === 'localhost' || h === '127.0.0.1' || h === '[::1]';
  var R = window.RTEPrivate = window.RTEPrivate || {};
  R.local = local;
  R.merge = R.merge || function(){}; R.mixTop = R.mixTop || function(){}; R.mixNotes = R.mixNotes || function(){};
  if(!local) return;
  document.write('<script src="assets/private/me-bscb.js"><\/script>');
})();

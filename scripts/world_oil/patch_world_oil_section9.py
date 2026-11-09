"""One-off patch of world-oil.html (2026-11-09): section 9 (oil burned by country, a replica of section 6 with a timeline bar), an "only" button in the country
lists of sections 6 and 9, "all other producers / consumers" off by default, and "% of world" measured against the world total even when the others are hidden.
Run once from the repo root: python scripts/world_oil/patch_world_oil_section9.py   (asserts every anchor exists exactly once)."""
import os, re, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'world-oil.html')
raw = open(P, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in raw[:20000] else '\n'
s = raw.replace('\r\n', '\n')


def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)


# ---------------------------------------------------------------- CSS
sub("""  .wo-mini:hover{ border-color:var(--accent); color:var(--accent); }
""", """  .wo-mini:hover{ border-color:var(--accent); color:var(--accent); }
  .wo-list .nm{ flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; }
  .wo-list .wo-only{ appearance:none; flex:none; margin-left:auto; border:1px solid var(--border); background:var(--surface); color:var(--accent); border-radius:6px; padding:0 7px; font:inherit; font-size:11px; font-weight:800; line-height:18px; cursor:pointer; opacity:.55; }
  .wo-list label:hover .wo-only, .wo-list .wo-only:hover, .wo-list .wo-only:focus-visible{ opacity:1; border-color:var(--accent); }
  .wo-tl{ margin:14px 0 6px; }
  .wo-tl .tl-svg{ width:100%; height:auto; display:block; touch-action:none; user-select:none; cursor:grab; overflow:visible; }
  .wo-tl .tl-svg text{ fill:var(--text-muted); font-size:10.5px; font-weight:700; }
  .wo-tl-dec{ display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin-top:8px; }
  .wo-tl-lbl{ font-size:11px; font-weight:800; letter-spacing:.09em; text-transform:uppercase; color:var(--text-muted); margin-right:2px; }
""")

# ---------------------------------------------------------------- section 6: "all other producers" unchecked by default
sub('<input type="checkbox" id="pr-others" checked> Show “all other producers”', '<input type="checkbox" id="pr-others"> Show “all other producers”')
sub("let prMode = 'abs', prY0 = 1960, prY1 = 2025, prOthers = true, prQuery = '';", "let prMode = 'abs', prY0 = 1960, prY1 = 2025, prOthers = false, prQuery = '';")

# ---------------------------------------------------------------- stackedArea: "% of world" against a denominator (works with the others hidden)
sub("""  const rows = years.map((y, i) => { const r = { year:y, i }; series.forEach(s => r[s.key] = s.vals[i] || 0); return r; });
  const stack = d3.stack().keys(series.map(s => s.key)).offset(o.pct ? d3.stackOffsetExpand : d3.stackOffsetNone)(rows);""",
    """  const dn = o.pct && o.denom ? o.denom : null;            // % of a total (world): the stack is value / total, so hidden series simply leave a gap
  const rows = years.map((y, i) => { const r = { year:y, i }; series.forEach(s => r[s.key] = dn ? (dn[i] ? (s.vals[i] || 0) / dn[i] : 0) : (s.vals[i] || 0)); return r; });
  const stack = d3.stack().keys(series.map(s => s.key)).offset(o.pct && !dn ? d3.stackOffsetExpand : d3.stackOffsetNone)(rows);""")
sub("  const ymax = o.pct ? 1 : d3.max(stack[stack.length - 1], d => d[1]) * 1.05;",
    "  const ymax = o.pct && !dn ? 1 : dn ? Math.min(1, d3.max(stack[stack.length - 1], d => d[1]) * 1.05) : d3.max(stack[stack.length - 1], d => d[1]) * 1.05;")
sub("""const tipRows = (r, series, pct) =>""", """const tipRowsW = (r, series, denom) => series.slice().reverse().map(s => `<div class="r"><span><i style="background:${s.color}"></i>${s.label}</span><b>${(100 * s.vals[r.i] / denom[r.i]).toFixed(1)}%</b></div>`).join('');
const tipRows = (r, series, pct) =>""")

# ---------------------------------------------------------------- section 6: % of world with the others hidden, "only" button, list markup
sub("""  stackedArea(document.getElementById('pr-chart'), yrs, series, { pct:prMode === 'pct', h:430,
    tip:(r, ss) => `<b>${r.year}</b><div class="r"><span>World production</span><b>${fmt1(O.worldProd[i0 + r.i])} mb/d</b></div>${tipRows(r, ss.filter(s => s.vals[r.i] > 0.0005), prMode === 'pct')}` });""",
    """  const Wp = O.worldProd.slice(i0, i1 + 1);
  stackedArea(document.getElementById('pr-chart'), yrs, series, { pct:prMode === 'pct', denom:Wp, h:430,
    tip:(r, ss) => `<b>${r.year}</b><div class="r"><span>World production</span><b>${fmt1(Wp[r.i])} mb/d</b></div>${prMode === 'pct' ? tipRowsW(r, ss.filter(s => s.vals[r.i] > 0.0005), Wp) : tipRows(r, ss.filter(s => s.vals[r.i] > 0.0005), false)}` });""")
sub("“all other producers” keeps the stack equal to world production.", "tick “all other producers” to make the stack equal world production. The “only” button next to a country shows that country alone.")
sub("""<i style="background:${c.color}"></i>${c.n.replace(' (USSR before 1985)', '*')}</label>`).join('');""",
    """<i style="background:${c.color}"></i><span class="nm">${c.n.replace(' (USSR before 1985)', '*')}</span><button type="button" class="wo-only" data-n="${c.n.replace(/"/g, '&quot;')}" title="Show only ${c.n.replace(' (USSR before 1985)', '').replace(/"/g, '&quot;')}">only</button></label>`).join('');""")
sub("  document.querySelectorAll('[data-top]').forEach(b => b.onclick = () => {", "  document.getElementById('pr-list').addEventListener('click', e => { const b = e.target.closest('.wo-only'); if(!b) return; e.preventDefault(); const c = COUNTRIES.find(x => x.n === b.dataset.n); if(!c) return;\n    prSel.clear(); prSel.add(c.n); regOn.add(c.region); document.querySelectorAll('#pr-regions .wo-chip').forEach(x => x.classList.toggle('off', !regOn.has(x.dataset.r))); drawList(); drawProd(); });\n  document.querySelectorAll('#pr-f [data-top]').forEach(b => b.onclick = () => {")

# ---------------------------------------------------------------- section 9 HTML
SEC9_HTML = r'''      <div class="card chart-card" id="cs-card">
        <h2>9 · Oil burned by country, 1950–2025</h2>
        <p class="wo-note" id="cs-note"></p>
        <div class="wo-filters" id="cs-f">
          <button type="button" class="wo-ftoggle" aria-expanded="true"><span>Filters</span><span class="wo-fsum" id="cs-fsum"></span><i class="wo-car">▾</i></button>
          <div class="wo-fbody">
            <div class="wo-frow"><label class="wo-fl">Show</label>
              <div class="wo-seg" id="cs-mode"><button type="button" data-v="abs" class="active">Million barrels / day</button><button type="button" data-v="pct">% of world</button></div>
              <label class="wo-chip" style="cursor:pointer"><input type="checkbox" id="cs-others"> Show “all other consumers”</label>
            </div>
            <div class="wo-frow"><label class="wo-fl">Regions</label><div class="wo-legend" id="cs-regions" style="margin:0"></div></div>
            <div class="wo-frow"><label class="wo-fl">Countries</label>
              <input type="search" class="wo-search" id="cs-search" placeholder="Search a country…">
              <button type="button" class="wo-mini" data-ctop="5">Top 5</button><button type="button" class="wo-mini" data-ctop="12">Top 12</button><button type="button" class="wo-mini" data-ctop="25">Top 25</button><button type="button" class="wo-mini" id="cs-none">None</button><button type="button" class="wo-mini" id="cs-all">All</button>
              <div class="wo-list" id="cs-list"></div>
            </div>
            <div class="wo-frow"><label class="wo-fl">Years</label>
              <div class="wo-range"><span id="cs-y0l">1950</span><input type="range" id="cs-y0" min="1950" max="2021" value="1950"></div>
              <div class="wo-range"><input type="range" id="cs-y1" min="1954" max="2025" value="2025"><span id="cs-y1l">2025</span></div>
            </div>
          </div>
        </div>
        <div class="wo-tl" id="cs-tl">
          <svg class="tl-svg" id="cs-tl-svg" role="img" aria-label="Timeline of world oil consumption 1950 to 2025 with the selected years framed"></svg>
          <div class="wo-tl-dec" id="cs-dec"></div>
          <p class="wo-note" style="margin:6px 0 0">Timeline: drag the frame to move the years shown, drag its edges to widen or narrow it, click outside it to jump there, or pick a decade. The curve is world oil consumption; the dashed lines mark the big shocks.</p>
        </div>
        <div class="wo-chart" id="cs-chart"></div>
      </div>

'''
sub('      <details class="wo-method" id="method" open>', SEC9_HTML + '      <details class="wo-method" id="method" open>')

# ---------------------------------------------------------------- section 9 JS
SEC9_JS = r'''// ---------- 9. who burned it, country by country, 1950-2025: the filters of section 6 on the consumption data, plus a timeline bar ----------
const CSY = []; for(let y = CO.y0; y <= CO.y1; y++) CSY.push(y);
const CCOUNTRIES = CO.rows.map(r => ({ n:r.n + (r.h ? '*' : ''), region:r.g || 'Other', v:r.v.map(x => x == null ? 0 : x) }))
  .sort((a, b) => b.v[b.v.length - 1] - a.v[a.v.length - 1] || d3.max(b.v) - d3.max(a.v));
CCOUNTRIES.forEach((c, i) => c.color = PAL[i % PAL.length]);
const CREGIONS = REGIONS.filter(r => CCOUNTRIES.some(c => c.region === r));
const csSel = new Set(CCOUNTRIES.slice(0, 12).map(c => c.n)), csReg = new Set(CREGIONS);
let csMode = 'abs', csY0 = CO.y0, csY1 = CO.y1, csOthers = false, csQuery = '';
const CS_MIN = 4;                                         // narrowest window the timeline / sliders allow (years)
const TL_EVENTS = [[1973, 'Oil embargo'], [1979, 'Iranian revolution'], [1986, 'Price collapse'], [2008, 'Financial crisis'], [2020, 'COVID-19']];
const TL_DEC = [['All', CO.y0, CO.y1], ['1950s', 1950, 1959], ['1960s', 1960, 1969], ['1970s', 1970, 1979], ['1980s', 1980, 1989], ['1990s', 1990, 1999], ['2000s', 2000, 2009], ['2010s', 2010, 2019], ['2020s', 2020, 2025]];
function drawCS(){
  const i0 = csY0 - CO.y0, i1 = csY1 - CO.y0, yrs = CSY.slice(i0, i1 + 1), Wd = CO.world.slice(i0, i1 + 1);
  const chosen = CCOUNTRIES.filter(c => csSel.has(c.n) && csReg.has(c.region));
  const series = chosen.map(c => ({ key:c.n, label:c.n, color:c.color, vals:c.v.slice(i0, i1 + 1) }));
  if(csOthers) series.push({ key:'__others', label:'All other consumers', color:'#cbd5e1', vals:yrs.map((_, i) => Math.max(0, Wd[i] - chosen.reduce((s, c) => s + c.v[i0 + i], 0))) });
  document.getElementById('cs-fsum').textContent = `${chosen.length} countries · ${csMode === 'abs' ? 'mb/d' : '% of world'} · ${csY0}–${csY1}`;
  stackedArea(document.getElementById('cs-chart'), yrs, series, { pct:csMode === 'pct', denom:Wd, h:430, est:yy => yy <= CO.bcTo,
    tip:(r, ss) => `<b>${r.year}</b> ${r.year <= CO.bcTo ? '<span class="est">estimate</span>' : '<span style="color:var(--text-muted)">Energy Institute</span>'}<div class="r"><span>World consumption</span><b>${fmt1(Wd[r.i])} mb/d</b></div>${csMode === 'pct' ? tipRowsW(r, ss.filter(s => s.vals[r.i] > 0.0005), Wd) : tipRows(r, ss.filter(s => s.vals[r.i] > 0.0005), false)}` });
  document.getElementById('cs-note').innerHTML = `Oil burned or used as raw material in each country, million barrels a day (international shipping and aviation fuel and refinery fuel included). Tick or untick countries and regions in the filters; tick “all other consumers” to make the stack equal world consumption. The “only” button next to a country shows that country alone. *Russia includes the Soviet Union before 1985. <b>Hatched years (1950–64) are estimates</b>: the Energy Institute series starts in 1965 (see section 8). World consumption reached ${fmt1(CO.world[CO.world.length - 1])} mb/d in 2025 (${fmt1(CO.world[0])} in 1950).`;
  drawTL();
}
function csSetWindow(a, b){
  a = Math.max(CO.y0, Math.min(a, CO.y1 - CS_MIN)); b = Math.min(CO.y1, Math.max(b, a + CS_MIN));
  csY0 = a; csY1 = b;
  document.getElementById('cs-y0').value = a; document.getElementById('cs-y1').value = b;
  document.getElementById('cs-y0l').textContent = a; document.getElementById('cs-y1l').textContent = b;
  drawCS();
}
let tlX = null, tlW = 900;
function drawTL(){
  const host = document.getElementById('cs-tl'), el = document.getElementById('cs-tl-svg');
  const W = tlW = Math.max(520, host.clientWidth || 900), H = 88, m = { l:46, r:14, t:6, b:22 };
  const x = tlX = d3.scaleLinear().domain([CO.y0, CO.y1]).range([m.l, W - m.r]);
  const yv = d3.scaleLinear().domain([0, d3.max(CO.world) * 1.05]).range([H - m.b, m.t + 16]);
  const svg = d3.select(el); svg.selectAll('*').remove(); svg.attr('viewBox', `0 0 ${W} ${H}`);
  const pts = CSY.map((y, i) => [y, CO.world[i]]);
  svg.append('path').attr('d', d3.area().x(d => x(d[0])).y0(H - m.b).y1(d => yv(d[1])).curve(d3.curveMonotoneX)(pts)).attr('fill', 'var(--accent)').attr('fill-opacity', .2);
  svg.append('path').attr('d', d3.line().x(d => x(d[0])).y(d => yv(d[1])).curve(d3.curveMonotoneX)(pts)).attr('fill', 'none').attr('stroke', 'var(--accent)').attr('stroke-width', 1.6);
  svg.append('rect').attr('x', x(CO.y0)).attr('width', x(CO.bcTo) - x(CO.y0)).attr('y', H - m.b - 4).attr('height', 4).attr('fill', '#d97706').attr('fill-opacity', .8);   // estimate years
  d3.range(1950, 2026, 10).forEach(t => svg.append('text').attr('x', x(t)).attr('y', H - 6).attr('text-anchor', 'middle').text(t));
  TL_EVENTS.forEach(([y, lb]) => { svg.append('line').attr('x1', x(y)).attr('x2', x(y)).attr('y1', m.t + 12).attr('y2', H - m.b).attr('stroke', 'var(--text)').attr('stroke-opacity', .45).attr('stroke-dasharray', '3 3');
    svg.append('text').attr('x', x(y) + 3).attr('y', m.t + 10).text(`${lb} ${y}`).style('fill', 'var(--text)'); });
  const xa = x(csY0), xb = x(csY1), top = m.t, hh = H - m.b - m.t;
  svg.append('rect').attr('x', x(CO.y0)).attr('width', Math.max(0, xa - x(CO.y0))).attr('y', top).attr('height', hh).attr('fill', 'var(--surface)').attr('fill-opacity', .66);
  svg.append('rect').attr('x', xb).attr('width', Math.max(0, x(CO.y1) - xb)).attr('y', top).attr('height', hh).attr('fill', 'var(--surface)').attr('fill-opacity', .66);
  svg.append('rect').attr('x', xa).attr('width', Math.max(2, xb - xa)).attr('y', top).attr('height', hh).attr('fill', 'none').attr('stroke', 'var(--accent)').attr('stroke-width', 2).attr('rx', 3);
  [xa, xb].forEach(h => svg.append('rect').attr('x', h - 3.5).attr('width', 7).attr('y', top + hh / 2 - 12).attr('height', 24).attr('rx', 3).attr('fill', 'var(--accent)').style('cursor', 'ew-resize'));
  svg.append('text').attr('x', xa + 4).attr('y', top + hh - 5).text(csY0).style('fill', 'var(--accent)').style('font-weight', 800);
  svg.append('text').attr('x', xb - 4).attr('y', top + hh - 5).attr('text-anchor', 'end').text(csY1).style('fill', 'var(--accent)').style('font-weight', 800);
  document.querySelectorAll('#cs-dec .wo-yr').forEach(b => b.classList.toggle('on', +b.dataset.a === csY0 && +b.dataset.b === csY1));
}
(function initCS(){
  const rg = document.getElementById('cs-regions');
  rg.innerHTML = CREGIONS.map(r => `<button type="button" class="wo-chip" data-r="${r}"><i style="background:var(--accent)"></i>${r}</button>`).join('');
  rg.title = 'Click: add / remove all the countries of a region. Shift-click: hide / show the region.';
  rg.addEventListener('click', e => { const b = e.target.closest('.wo-chip'); if(!b) return; const r = b.dataset.r;
    if(e.shiftKey || e.altKey){ if(csReg.has(r)) csReg.delete(r); else csReg.add(r); }
    else { const all = CCOUNTRIES.filter(c => c.region === r); const allOn = all.every(c => csSel.has(c.n)); all.forEach(c => allOn ? csSel.delete(c.n) : csSel.add(c.n)); csReg.add(r); }
    rg.querySelectorAll('.wo-chip').forEach(x => x.classList.toggle('off', !csReg.has(x.dataset.r))); csDrawList(); drawCS(); });
  const list = document.getElementById('cs-list');
  list.addEventListener('change', e => { const cb = e.target; if(cb.type !== 'checkbox') return; if(cb.checked) csSel.add(cb.dataset.n); else csSel.delete(cb.dataset.n); drawCS(); });
  list.addEventListener('click', e => { const b = e.target.closest('.wo-only'); if(!b) return; e.preventDefault(); const c = CCOUNTRIES.find(x => x.n === b.dataset.n); if(!c) return;
    csSel.clear(); csSel.add(c.n); csReg.add(c.region); rg.querySelectorAll('.wo-chip').forEach(x => x.classList.toggle('off', !csReg.has(x.dataset.r))); csDrawList(); drawCS(); });
  document.getElementById('cs-search').addEventListener('input', e => { csQuery = e.target.value; csDrawList(); });
  document.querySelectorAll('#cs-f [data-ctop]').forEach(b => b.onclick = () => { csSel.clear(); CCOUNTRIES.slice(0, +b.dataset.ctop).forEach(c => csSel.add(c.n)); csDrawList(); drawCS(); });
  document.getElementById('cs-none').onclick = () => { csSel.clear(); csDrawList(); drawCS(); };
  document.getElementById('cs-all').onclick = () => { CCOUNTRIES.forEach(c => csSel.add(c.n)); csDrawList(); drawCS(); };
  document.getElementById('cs-others').onchange = e => { csOthers = e.target.checked; drawCS(); };
  seg('cs-mode', v => { csMode = v; drawCS(); });
  const a = document.getElementById('cs-y0'), b = document.getElementById('cs-y1');
  a.oninput = () => csSetWindow(+a.value, Math.max(csY1, +a.value + CS_MIN));
  b.oninput = () => csSetWindow(Math.min(csY0, +b.value - CS_MIN), +b.value);
  // decade chips
  const dec = document.getElementById('cs-dec');
  dec.innerHTML = '<span class="wo-tl-lbl">Years</span>' + TL_DEC.map(([l, p, q]) => `<button type="button" class="wo-yr" data-a="${p}" data-b="${q}">${l}</button>`).join('');
  dec.addEventListener('click', e => { const bt = e.target.closest('.wo-yr'); if(bt) csSetWindow(+bt.dataset.a, +bt.dataset.b); });
  // timeline bar: drag the frame, its edges, or click outside it to jump there
  const el = document.getElementById('cs-tl-svg'); let drag = null;
  const yearAt = ev => { const r = el.getBoundingClientRect(); return tlX.invert((ev.clientX - r.left) * (tlW / r.width)); };
  const pxAt = ev => { const r = el.getBoundingClientRect(); return (ev.clientX - r.left) * (tlW / r.width); };
  el.addEventListener('pointerdown', ev => {
    if(!tlX) return; const px = pxAt(ev), yr = yearAt(ev), near = v => Math.abs(px - tlX(v)) < 10;
    if(near(csY0)) drag = { m:'l' }; else if(near(csY1)) drag = { m:'r' };
    else { const w = csY1 - csY0; if(yr > csY0 && yr < csY1) drag = { m:'pan', off:yr - csY0, w }; else { csSetWindow(Math.round(yr - w / 2), Math.round(yr - w / 2) + w); drag = { m:'pan', off:w / 2, w }; } }
    el.setPointerCapture(ev.pointerId); el.style.cursor = 'grabbing'; ev.preventDefault();
  });
  el.addEventListener('pointermove', ev => {
    if(!drag){ if(tlX){ const px = pxAt(ev), near = v => Math.abs(px - tlX(v)) < 10; el.style.cursor = near(csY0) || near(csY1) ? 'ew-resize' : 'grab'; } return; }
    const yr = Math.round(yearAt(ev));
    if(drag.m === 'l') csSetWindow(Math.min(yr, csY1 - CS_MIN), csY1);
    else if(drag.m === 'r') csSetWindow(csY0, Math.max(yr, csY0 + CS_MIN));
    else { const s = Math.max(CO.y0, Math.min(CO.y1 - drag.w, Math.round(yearAt(ev) - drag.off))); csSetWindow(s, s + drag.w); }
  });
  const end = () => { drag = null; el.style.cursor = 'grab'; };
  el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
  csDrawList(); drawCS();
})();
function csDrawList(){
  const q = csQuery.toLowerCase(), esc = t => t.replace(/"/g, '&quot;');
  document.getElementById('cs-list').innerHTML = CCOUNTRIES.filter(c => c.n.toLowerCase().includes(q)).map(c => `<label title="${c.region}"><input type="checkbox" data-n="${esc(c.n)}" ${csSel.has(c.n) ? 'checked' : ''}><i style="background:${c.color}"></i><span class="nm">${c.n}</span><button type="button" class="wo-only" data-n="${esc(c.n)}" title="Show only ${esc(c.n.replace('*', ''))}">only</button></label>`).join('');
}

'''
sub("// ---------- method table ----------", SEC9_JS + "// ---------- method table ----------")

# resize + share links + method text
sub("rzT = setTimeout(() => { drawUse(); drawTransport(); drawUS(); drawProd(); }, 150);", "rzT = setTimeout(() => { drawUse(); drawTransport(); drawUS(); drawProd(); drawCS(); }, 150);")
sub("FilterMemory.auto({ exclude:['co-chips'], extra: [", """FilterMemory.auto({ exclude:['co-chips', 'cs-dec'], extra: [
  { key:'csc', type:'fn', get:() => CCOUNTRIES.map((c, i) => csSel.has(c.n) ? i : -1).filter(i => i >= 0).join(','), set:v => { csSel.clear(); v.split(',').filter(Boolean).forEach(i => { if(CCOUNTRIES[+i]) csSel.add(CCOUNTRIES[+i].n); }); csDrawList(); drawCS(); return true; } },
  { key:'csr', type:'fn', get:() => CREGIONS.map((r, i) => csReg.has(r) ? i : -1).filter(i => i >= 0).join(','), set:v => { csReg.clear(); v.split(',').filter(Boolean).forEach(i => { if(CREGIONS[+i]) csReg.add(CREGIONS[+i]); }); document.querySelectorAll('#cs-regions .wo-chip').forEach(x => x.classList.toggle('off', !csReg.has(x.dataset.r))); csDrawList(); drawCS(); return true; } },""")
sub("<li><b>Who burns it, by country (section 8).</b>", "<li><b>Who burns it, by country (sections 8 and 9).</b>")

open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
print('patched world-oil.html')

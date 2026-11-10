"""One-off patch of world-oil.html (2026-11-10): the 2026 bridge (see bridge_2026.py). Sections 6-7 reach 2026 (January-June, IEA converted), the what-if section keeps the pre-war 2026
baseline (O.wi2026), notes and method say where 2026 comes from. Run once from the repo root; asserts every anchor."""
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'world-oil.html')
raw = open(P, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in raw[:20000] else '\n'
s = raw.replace('\r\n', '\n')


def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:100])
    s = s.replace(old, new)


# ---- section 6 / 7: reach 2026
sub('<h2>6 · Oil produced by country, 1960–2025</h2>', '<h2>6 · Oil produced by country, 1960–2026</h2>')
sub('<input type="range" id="pr-y1" min="1970" max="2025" value="2025"><span id="pr-y1l">2025</span>', '<input type="range" id="pr-y1" min="1970" max="2026" value="2026"><span id="pr-y1l">2026</span>')
sub("let prMode = 'abs', prY0 = 1960, prY1 = 2025, prOthers = false, prQuery = '';", "let prMode = 'abs', prY0 = 1960, prY1 = 2026, prOthers = false, prQuery = '';")
sub("const COUNTRIES = Object.entries(O.countries).map(([n, c]) => ({ n, region:c.region, mbd:c.mbd })).sort((a, b) => b.mbd[b.mbd.length - 1] - a.mbd[a.mbd.length - 1] || d3.max(b.mbd) - d3.max(a.mbd));",
    "const I25 = O.prodYears.indexOf(2025);                    // the last Energy Institute year; 2026 (IEA, converted) is the one point after it\nconst COUNTRIES = Object.entries(O.countries).map(([n, c]) => ({ n, region:c.region, mbd:c.mbd })).sort((a, b) => b.mbd[I25] - a.mbd[I25] || d3.max(b.mbd) - d3.max(a.mbd));")
sub("p = O.prodYears.length - 1;", "p = O.prodYears.indexOf(2025);")
sub("World production reached ${fmt1(O.worldProd[PY.length - 1])} mb/d in 2025 (${fmt1(O.worldProd[0])} in 1960).`;",
    "World production reached ${fmt1(O.worldProd[I25])} mb/d in 2025 (${fmt1(O.worldProd[0])} in 1960). <b>2026 (hatched) is not Energy Institute data yet</b>: it is the January–June 2026 average of the IEA Oil Market Reports (May and July), converted to this basis with each country's own 2025 ratio between the two sources; it shows the Strait of Hormuz crisis. The Energy Institute publishes 2026 in June 2027 and will replace it.`;")
sub("""  stackedArea(document.getElementById('pr-chart'), yrs, series, { pct:prMode === 'pct', denom:Wp, h:430,
    tip:(r, ss) => `<b>${r.year}</b><div class="r"><span>World production</span>""", """  stackedArea(document.getElementById('pr-chart'), yrs, series, { pct:prMode === 'pct', denom:Wp, h:430, est:yy => yy >= 2025,
    tip:(r, ss) => `<b>${r.year}</b>${r.year === 2026 ? ' <span class="est">Jan–Jun · IEA converted</span>' : ''}<div class="r"><span>World production</span>""")
sub('id="rk-year" min="1960" max="2025" value="2025"', 'id="rk-year" min="1960" max="2026" value="2025"')
sub("if(+sl.value >= 2025) sl.value = 1960; pb.textContent = '❚❚'; rkTimer = setInterval(() => { sl.value = +sl.value + 1; drawRanking(); if(+sl.value >= 2025) stopRk(); }, 260);",
    "if(+sl.value >= 2026) sl.value = 1960; pb.textContent = '❚❚'; rkTimer = setInterval(() => { sl.value = +sl.value + 1; drawRanking(); if(+sl.value >= 2026) stopRk(); }, 260);")
sub("<div class=\"wo-note\">World: ${fmt1(W)} mb/d in ${yr}.</div>`;", "<div class=\"wo-note\">World: ${fmt1(W)} mb/d in ${yr}${yr === 2026 ? ' (January–June, IEA data converted to the Energy Institute basis)' : ''}.</div>`;")

# ---- what-if: starts from the pre-war 2026 level, not from the 2026 crisis year
sub("  const U = k => useVal(k, 2026), tg = S.target, out = {};", "  const U = k => O.wi2026[k], tg = S.target, out = {};                // the pre-war 2026 level: scenarios start from a normal year, not from the 2026 crisis year of section 1")
sub("WI_YEARS.map(y => y <= 2026 ? useVal(c.k, y) : run[y][c.k])", "WI_YEARS.map(y => y < 2026 ? useVal(c.k, y) : y === 2026 ? O.wi2026[c.k] : run[y][c.k])")
sub("const totS = WI_YEARS.map(y => y <= 2026 ? tot(y) : run[y].total), totB = WI_YEARS.map(y => y <= 2026 ? tot(y) : base[y].total);",
    "const wiTot = y => y < 2026 ? tot(y) : y === 2026 ? O.wi2026.total : null, totS = WI_YEARS.map(y => y <= 2026 ? wiTot(y) : run[y].total), totB = WI_YEARS.map(y => y <= 2026 ? wiTot(y) : base[y].total);")
sub("ref:{ val:tot(2026), from:2026, color:'#111827', label:`Flat at today's ${fmt1(tot(2026))} mb/d` }, mark:[[2026, 'Today'], [tg, 'Target ' + tg]],",
    "ref:{ val:O.wi2026.total, from:2026, color:'#111827', label:`Flat at the pre-war ${fmt1(O.wi2026.total)} mb/d` }, mark:[[2026, 'Start'], [tg, 'Target ' + tg]],")
sub("dotted flat line = <b>today's level</b>, to see whether demand ends above or below it. The chart is a simple fleet model, not a forecast:",
    "dotted flat line = <b>the starting level</b>, to see whether demand ends above or below it. The scenarios start from the pre-war 2026 level (97.1 mb/d), not from the lower 2026 of section 1 (the Strait of Hormuz crisis, forecast by the IEA at 94.0 mb/d on this page's basis), because a crisis year is not a base for a 2060 path. The chart is a simple fleet model, not a forecast:")
sub("run a simple fleet model from the 2026 estimate;", "run a simple fleet model from the pre-war 2026 level;")

# ---- wording of 2026 in sections 1-3 and the method list
sub("const estTag = y => y <= 1970 ? 'split estimated' : y <= 2025 ? 'split estimated · total is real' : 'forecast';",
    "const estTag = y => y <= 1970 ? 'split estimated' : y <= 2025 ? 'split estimated · total is real' : 'IEA forecast, converted';")
sub("The total oil for 2020–25 is real Energy Institute data; only 2026 is a forecast.", "The total oil for 2020–25 is real Energy Institute data. 2026 is the IEA's October 2026 forecast (demand 102.4 mb/d, down 2.6) converted to the Energy Institute basis; the Energy Institute publishes 2026 in June 2027.")
sub("<b>2026 is a forecast</b> (the year is not over).",
    "<b>2026 is the IEA's forecast, converted:</b> the IEA Oil Market Report of 14 October 2026 puts 2026 demand at 102.4 mb/d, 2.6 below 2025 (105.0 on its basis); we apply that ratio (0.975) to the Energy Institute's 2025 total (96.4 mb/d), giving 94.0 mb/d, and share the cut across purposes in proportion. The IEA says diesel, petrochemical feedstocks and jet fuel carried most of it, so the split of 2026 is a rough guide.")
sub("          <li><b>What-if scenarios (section 4)</b>", """          <li><b>Bridging 2026 until the Energy Institute publishes it (June 2027).</b> The Energy Institute has one release a year. For 2026 we use the IEA Oil Market Reports and convert them with the ratio between the two sources in 2025, the last year both exist: world demand (section 1) from the October 2026 report; oil produced by country (sections 6 and 7) as the January–June 2026 average of the 1Q26 figure of the May report and the 2Q26 figure of the July report (the later reports are not yet public as full tables), each country times its own Energy Institute / IEA ratio of 2025 (the IEA counts crude, condensate and NGL together, the Energy Institute series differs by country, so a country's ratio can be well above or below 1). Countries the IEA does not list are kept at their 2025 level. World production uses the IEA supply without biofuels and refinery gains. Script <code>scripts/world_oil/bridge_2026.py</code>; replace it when the Energy Institute 2026 data arrives.</li>
          <li><b>What-if scenarios (section 4)</b>""")
open(P, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
print('patched world-oil.html')

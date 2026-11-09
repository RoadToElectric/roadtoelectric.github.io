"""Builds assets/world-oil-consumers.js (WORLD_OIL_CONS): oil consumed by country, 1950-2025, plus population, for the two "who burns it" rankings of world-oil.html
(total, and per person).

Inputs (.scratch/oil and .scratch/pop, not in git):
  oil-consumption-by-country.csv   OWID, Energy Institute Statistical Review (TWh), 1965-2025. Converted at 579 TWh per mb/d, like the rest of the page.
  owid-co2-data.csv                OWID CO2 dataset (Global Carbon Project; https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv), column oil_co2 =
                                   CO2 from oil by country since 1750. Its 1950-1964 values rest on the UN Energy Statistics (the UN database starts in 1950).
  world_population_full.npz + world_population_meta.json   UN WPP 2024 single-age population (built by scripts/world_population/build_world_population.py)

Method
 - 1965-2025: the Energy Institute value as published ("ei").
 - 1950-1964: back-cast ("bc") = the country's 1965-69 Energy Institute volume / its 1965-69 oil CO2, times the oil CO2 of each earlier year. The energy-institute series start in 1965,
   so nothing better is free; the chain-link keeps the same basis (bunkers and refinery fuel included) as the later years. An entity whose back-cast jumps by more than 2.5x between two
   consecutive years is dropped for 1950-64 (the UN-based series of small oil exporters is erratic: Saudi Arabia, Kuwait ...).
 - USSR: the Energy Institute has "USSR" to 1984 and "Russia" from 1985; the row is "Russia" with the name USSR up to 1984. Its back-cast and its population are the 15 republics added up before 1985.
 - Per person = barrels a year = mb/d x 365.25 x 1e6 / population (UN WPP, 1 July).
Checks printed at the end: the countries added up against the world series, and the United States against the EIA (US petroleum products supplied: 1950 6.46, 1955 8.46, 1960 9.80 mb/d).
Run:  python scripts/world_oil/build_world_oil_consumers.py   (from the repo root)"""
import csv, collections, json, os
import sys as _sys, os as _os; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from oil_regions import REGION_OF
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OIL = os.path.join(ROOT, '.scratch', 'oil'); POP = os.path.join(ROOT, '.scratch', 'pop')
TWH_PER_MBD = 579.0
Y0, Y1 = 1950, 2025
YEARS = list(range(Y0, Y1 + 1))
SOV = ['RUS', 'UKR', 'BLR', 'MDA', 'EST', 'LVA', 'LTU', 'GEO', 'ARM', 'AZE', 'KAZ', 'UZB', 'TKM', 'KGZ', 'TJK']
JUMP = 2.5

ei = collections.defaultdict(dict); code_of = {}
for r in csv.DictReader(open(os.path.join(OIL, 'oil-consumption-by-country.csv'), encoding='utf8')):
    ei[r['entity']][int(r['year'])] = float(r['oil_consumption_twh']) / TWH_PER_MBD; code_of[r['entity']] = r['code']
co2 = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(OIL, 'owid-co2-data.csv'), encoding='utf8')):
    if r['oil_co2'] != '' and r['iso_code']:
        co2[r['iso_code']][int(r['year'])] = float(r['oil_co2'])
z = np.load(os.path.join(POP, 'world_population_full.npz')); meta = json.load(open(os.path.join(POP, 'world_population_meta.json'), encoding='utf8'))
ids = [int(i) for i in z['ids']]; popt = {i: z['data'][k].sum(axis=1) for k, i in enumerate(ids)}      # persons, 1950..2100
iso2loc = {meta[str(i)]['iso3']: i for i in ids if meta[str(i)].get('iso3')}
pop_of = lambda iso, y: float(popt[iso2loc[iso]][y - 1950])


def backcast(series, co):
    a = [y for y in range(1965, 1970) if y in series and co.get(y, 0) > 0]
    if len(a) < 3:
        return {}
    k = sum(series[y] for y in a) / sum(co[y] for y in a)
    return {y: k * co[y] for y in range(1950, 1965) if co.get(y, 0) > 0}


rows, dropped, world_ei = [], [], ei['World']
for ent, s in ei.items():
    iso = code_of[ent]
    if ent == 'World' or ent == 'USSR' or not iso or iso.startswith('OWID_') or iso not in iso2loc:
        continue
    ser = {y: v for y, v in s.items() if y <= Y1}; hist = None
    if ent == 'Russia':
        ussr = ei['USSR']; ser.update({y: v for y, v in ussr.items() if y <= 1984}); hist = {'to': 1984, 'n': 'USSR'}
        sov = collections.defaultdict(float)
        for c in SOV:
            for y, v in co2[c].items(): sov[y] += v
        co = sov
    else:
        co = co2.get(iso, {})
    bc = backcast(ser, co)
    if bc:
        chain = {**bc, **{y: ser[y] for y in range(1965, 1970) if y in ser}}
        ys = sorted(chain)
        if any(chain[b] / chain[a] > JUMP or chain[b] / chain[a] < 1 / JUMP for a, b in zip(ys, ys[1:]) if b == a + 1 and chain[a] > 0):
            dropped.append(ent); bc = {}
    ser.update(bc)
    if max(ser.values(), default=0) < 0.01:
        continue
    p = [round((sum(pop_of(c, y) for c in SOV) if hist and y <= 1984 else pop_of(iso, y)) / 1000) for y in YEARS]
    row = {'n': ent, 'c': iso, 'v': [round(ser[y], 4) if y in ser else None for y in YEARS], 'p': p, 'g': REGION_OF.get(iso, 'Other')}
    if hist: row['h'] = hist
    rows.append(row)
rows.sort(key=lambda r: -(r['v'][-1] or 0))
world = [round(world_ei[y], 4) for y in YEARS]
out = {'y0': Y0, 'y1': Y1, 'bcTo': 1964, 'world': world, 'rows': rows}
js = ('// Oil consumed by country, 1950-2025 (mb/d): Energy Institute 1965+, back-cast 1950-64 from the Global Carbon Project oil-CO2 series; UN WPP 2024 population (thousands). '
      'Built by scripts/world_oil/build_world_oil_consumers.py\nconst WORLD_OIL_CONS = ' + json.dumps(out, separators=(',', ':'), ensure_ascii=True) + ';\n')
op = os.path.join(ROOT, 'assets', 'world-oil-consumers.js'); open(op, 'w', encoding='utf8', newline='\n').write(js)
print(f'wrote assets/world-oil-consumers.js  {os.path.getsize(op) / 1e3:.0f} KB, {len(rows)} countries; back-cast dropped (erratic): {dropped}')
for y in (1950, 1955, 1960, 1964, 1965, 1970):
    s = sum(r['v'][y - Y0] or 0 for r in rows)
    print(f'  {y}: countries added up {s:6.2f} mb/d vs world {world_ei[y]:6.2f}  ({100 * (s / world_ei[y] - 1):+.1f}%)')
us = next(r for r in rows if r['c'] == 'USA')
print('  United States back-cast', {y: us['v'][y - Y0] for y in (1950, 1955, 1960, 1964, 1965)}, ' (EIA: 1950 6.46, 1955 8.46, 1960 9.80)')


def top(y, per, minpop=1e6, n=8):
    L = []
    for r in rows:
        v, p = r['v'][y - Y0], r['p'][y - Y0] * 1000
        if v is None or p < minpop: continue
        L.append((r['n'] if not (r.get('h') and y <= r['h']['to']) else r['h']['n'], v * 1e6 * 365.25 / p if per else v))
    L.sort(key=lambda t: -t[1]); return [(a, round(b, 1 if per else 2)) for a, b in L[:n]]


for y in (1950, 1960, 1970, 2025):
    print(y, 'total', top(y, False)); print(y, 'per person (bbl/yr)', top(y, True))

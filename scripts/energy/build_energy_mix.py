#!/usr/bin/env python3
"""Builds assets/energy-mix-data.js from the IEA Energy Statistics Data Browser (public API, licence CC BY 4.0).
Inputs (downloaded once, kept next to this script):  all_TESbySource.json, all_TFCbySource.json, all_ElecGenByFuel.json
  curl -s "https://api.iea.org/stats/indicator/TESbySource" -o all_TESbySource.json     (same for TFCbySource, ElecGenByFuel; no key needed; add ?countries=WORLD for one area)
Country names / ISO2 codes come from assets/world-population-data.js (UN names, the same spelling as the rest of the site).
Output: const ENERGY_MIX = { y0, y1, tes:[{k,label,color}], tfc:[...], el:[...], areas:[{id (IEA code), iso3, n, k:'world'|'region'|'country', iso2, last, pop:[persons per year] (world + countries), tes:{key:[per year]}, tfc:{...}, el:{...}}] }
  supply and final consumption in PJ (1 PJ = 1000 TJ), electricity in TWh; null = not published for that year.
Usage: python scripts/energy/build_energy_mix.py"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent.parent
Y0, Y1 = 1990, 2025
NY = Y1 - Y0 + 1

TES_MAP = {'COAL': 'coal', 'MTOTOIL': 'oil', 'NATGAS': 'gas', 'NUCLEAR': 'nuclear', 'HYDRO': 'hydro', 'COMRENEW': 'bio', 'GEOTHERM': 'swo'}
TFC_MAP = {'COAL': 'coal', 'TOTPRODS': 'oil', 'CRNGFEED': 'oil', 'NATGAS': 'gas', 'COMRENEW': 'bio', 'GEOTHERM': 'swo', 'ELECTR': 'elec', 'HEAT': 'heat'}
EL_MAP = {'EHCOAL': 'coal', 'EHOIL': 'oil', 'EHNATGAS': 'gas', 'EHNUCLEAR': 'nuclear', 'EHYDRO': 'hydro', 'EWIND': 'wind', 'ESOLARPV': 'solar', 'EHSOLARTH': 'solar',
          'EHBIOMASS': 'bio', 'EHWASTE': 'bio', 'EHGEOTHERM': 'geo', 'ETIDE': 'geo', 'EHOTHER': 'oth'}
TES_KEYS = [('coal', 'Coal', '#59606a'), ('oil', 'Oil', '#111111'), ('gas', 'Natural gas', '#b87333'), ('nuclear', 'Nuclear', '#a855f7'),
            ('hydro', 'Hydropower', '#0ea5e9'), ('bio', 'Biofuels and waste', '#7a4a21'), ('swo', 'Solar, wind and other renewables', '#22c55e')]
TFC_KEYS = [('coal', 'Coal', '#59606a'), ('oil', 'Oil products', '#111111'), ('gas', 'Natural gas', '#b87333'), ('bio', 'Biofuels and waste', '#7a4a21'),
            ('swo', 'Solar, wind and other renewables', '#22c55e'), ('heat', 'Heat', '#ef4444'), ('elec', 'Electricity', '#0a80d0')]
EL_KEYS = [('coal', 'Coal', '#59606a'), ('oil', 'Oil', '#111111'), ('gas', 'Natural gas', '#b87333'), ('nuclear', 'Nuclear', '#a855f7'), ('hydro', 'Hydropower', '#0ea5e9'),
           ('wind', 'Wind', '#14b8a6'), ('solar', 'Solar', '#facc15'), ('bio', 'Bioenergy and waste', '#7a4a21'), ('geo', 'Geothermal and ocean', '#fb7185'), ('oth', 'Other sources', '#9ca3af')]
REGIONS = {'WORLD': 'World', 'OECDTOT': 'OECD', 'NONOECDTOT': 'Non-OECD', 'EU27_2020': 'European Union (27)', 'AFRICA': 'Africa', 'ASIA': 'Asia (excl. China)', 'EURASIA': 'Eurasia',
           'LATINAMERI': 'Latin America', 'MIDDLEEAST': 'Middle East', 'OECDAM': 'OECD Americas', 'OECDEUR': 'OECD Europe', 'OECDAO': 'OECD Asia Oceania'}
EXTRA_NAMES = {'XKX': 'Kosovo', 'UNK': 'Kosovo', 'CUW': 'Curaçao', 'GIB': 'Gibraltar', 'HKG': 'Hong Kong', 'TWN': 'Taiwan', 'SSD': 'South Sudan', 'COD': 'Democratic Republic of the Congo',
               'COG': 'Congo', 'KOR': 'South Korea', 'PRK': 'North Korea', 'CIV': "Côte d'Ivoire", 'MKD': 'North Macedonia', 'CZE': 'Czechia', 'RUS': 'Russian Federation', 'TUR': 'Turkey',
               'USA': 'United States', 'GBR': 'United Kingdom', 'IRN': 'Iran', 'VNM': 'Vietnam', 'SYR': 'Syria', 'MDA': 'Moldova', 'BOL': 'Bolivia', 'VEN': 'Venezuela', 'TZA': 'Tanzania',
               'LAO': 'Laos', 'BRN': 'Brunei', 'SWZ': 'Eswatini', 'BIH': 'Bosnia-Herzegovina', 'ARE': 'United Arab Emirates'}

wp = (ROOT / 'assets' / 'world-population-data.js').read_text(encoding='utf-8')
wp = json.loads(wp[wp.index('{'):wp.rindex('}') + 1])
names = {l['iso3']: (l['n'], l.get('iso2')) for l in wp['locs'] if l['k'] == 'country' and l.get('iso3')}
# population (persons, 1 July, UN WPP 2024; 2024+ are projections) for per-capita figures: countries by ISO3 (Kosovo is not a separate UN series) and the world
POP = {l['iso3']: l['p'] for l in wp['locs'] if l['k'] == 'country' and l.get('iso3')}
POP['WORLD'] = next(l['p'] for l in wp['locs'] if l['k'] == 'world')


def load(fn): return json.loads((HERE / fn).read_text(encoding='utf-8'))


def series(rows, mapping, keys, labelkey):
    out = {}
    for r in rows:
        k = mapping.get(r[labelkey])
        if not k: continue
        a = out.setdefault(r['short'], {}).setdefault(k, [None] * NY)
        y = int(r['year'])
        if Y0 <= y <= Y1 and r['value'] is not None: a[y - Y0] = (a[y - Y0] or 0) + r['value']
    return out


tes = series(load('all_TESbySource.json'), TES_MAP, TES_KEYS, 'product')
tfc = series(load('all_TFCbySource.json'), TFC_MAP, TFC_KEYS, 'product')
el = series(load('all_ElecGenByFuel.json'), EL_MAP, EL_KEYS, 'flow')
meta = {}
for r in load('all_TESbySource.json'): meta[r['short']] = r['country']


def pack(d, keys, div, nd):
    return {k: [None if v is None else round(v / div, nd) for v in d[k]] for k, _, _ in keys if k in d}


areas = []
for code in sorted(tes):
    iso3 = meta[code]
    if code in REGIONS: kind, name, iso2 = ('world' if code == 'WORLD' else 'region'), REGIONS[code], None
    elif len(iso3) == 3 and iso3 == iso3.upper() and code not in ('CHINAREG', 'GUYANA'):
        nm = EXTRA_NAMES.get(iso3) or (names.get(iso3) or (None, None))[0]
        if not nm: print('no name for', code, iso3); continue
        kind, name, iso2 = 'country', nm, (names.get(iso3) or (None, None))[1]
        if iso3 == 'TWN': iso2 = 'tw'
        if iso3 == 'HKG': iso2 = 'hk'
        if iso3 == 'UNK': iso2 = 'xk'
        if iso3 == 'CUW': iso2 = 'cw'
        if iso3 == 'GIB': iso2 = 'gi'
    else:
        continue
    a = {'id': code, 'iso3': iso3 if kind == 'country' else None, 'n': name, 'k': kind, 'iso2': iso2}
    t = tes[code]; last = max((i for i in range(NY) if any(t[k][i] is not None for k in t)), default=None)
    a['last'] = None if last is None else Y0 + last
    pk = 'WORLD' if kind == 'world' else iso3 if kind == 'country' else None
    if pk in POP: a['pop'] = POP[pk][Y0 - wp['y0']:Y1 - wp['y0'] + 1]
    a['tes'] = pack(t, TES_KEYS, 1000, 1)
    if code in tfc: a['tfc'] = pack(tfc[code], TFC_KEYS, 1000, 1)
    if code in el: a['el'] = pack(el[code], EL_KEYS, 1000, 2)
    areas.append(a)

order = {'world': 0, 'region': 1, 'country': 2}
areas.sort(key=lambda a: (order[a['k']], a['n']))
out = {'y0': Y0, 'y1': Y1, 'source': 'IEA Energy Statistics Data Browser (World Energy Balances, Electricity Information), CC BY 4.0, downloaded 2026-11-10',
       'units': {'tes': 'PJ', 'tfc': 'PJ', 'el': 'TWh'},
       'tes': [dict(k=k, label=l, color=c) for k, l, c in TES_KEYS], 'tfc': [dict(k=k, label=l, color=c) for k, l, c in TFC_KEYS], 'el': [dict(k=k, label=l, color=c) for k, l, c in EL_KEYS], 'areas': areas}
dst = ROOT / 'assets' / 'energy-mix-data.js'
dst.write_text('// IEA energy mix 1990-2025: supply (PJ), final consumption (PJ), electricity generation (TWh) by source, %d areas. Built by scripts/energy/build_energy_mix.py\nconst ENERGY_MIX = %s;\n' % (len(areas), json.dumps(out, separators=(',', ':'), ensure_ascii=False)), encoding='utf-8')
print('wrote', dst, len(areas), 'areas', dst.stat().st_size // 1024, 'KB; countries', sum(1 for a in areas if a['k'] == 'country'))

"""Builds assets/world-oil-data.js (WORLD_OIL) for world-oil.html.

Inputs (downloaded earlier to .scratch/oil, see the world-oil-data-sources memory):
  oil-production-by-country.csv / oil-consumption-by-country.csv   OWID, Energy Institute Statistical Review (TWh)
  iea_oil_tfc_by_sector_ej.json   IEA Key World Energy Statistics 2021, p. 39 "Oil total final consumption by sector 1971-2019 (EJ)":
                                  the 8 stacked-area polygons digitised from the PDF's vector chart (values reproduce the printed 1973 / 2019 pies)
  mer_T03.05 / T03.07A-C.csv      US EIA Monthly Energy Review (kb/d): US petroleum by sector and by product 1949-2025
  IEA Oil 2025 p. 15 (world oil demand by product 2019-2030): typed below (growth of each product used for 2020-2026)

Usage categories (mb/d):  road_passenger, road_goods, aviation, navigation, rail, industry, nonenergy, residential, other, nonfinal
 - 1971-2019  IEA final consumption by sector, EJ -> mb/d at 2.1 EJ per mb/d; "road" split passenger / goods with a share anchored on IEA 2017 (trucks ~17 mb/d)
 - 1950-1970  no IEA series: sector shares and the final-consumption / total ratio held at their 1971 values (flagged estimate)
 - 2020-2026  each sector follows the IEA Oil 2025 product it burns (gasoline, diesel, jet, residual fuel, LPG+naphtha), scaled to the same final/total ratio (flagged estimate)
 - nonfinal   total oil consumption (Energy Institute) minus the final-consumption sectors: power generation, refinery fuel, other transformation, statistical differences
Run:  python scripts/world_oil/build_world_oil.py   (from the repo root)"""
import csv, json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OIL = os.path.join(ROOT, '.scratch', 'oil')
TWH_PER_MBD = 579.0          # 1 mb/d of oil = 49.8 Mt/yr x 11.63 TWh/Mt (Energy Institute conversion)
EJ_PER_MBD = 2.1             # average energy content of the oil products consumed (about 5.8 GJ per barrel)

def load_csv(name, col):
    d = {}
    for r in csv.DictReader(open(os.path.join(OIL, name), encoding='utf8')):
        d.setdefault(r['entity'], {})[int(r['year'])] = float(r[col]) / TWH_PER_MBD
    return d

cons = load_csv('oil-consumption-by-country.csv', 'oil_consumption_twh')
prod = load_csv('oil-production-by-country.csv', 'oil_production_twh')
codes = {r['entity']: r['code'] for r in csv.DictReader(open(os.path.join(OIL, 'oil-production-by-country.csv'), encoding='utf8'))}
D = cons['World']
YEARS = list(range(1950, 2027))
# IEA Oil 2025, world oil demand by product (mb/d): 2019..2026
IEA = {'lpg': [13.2, 13.3, 13.6, 14.2, 14.6, 15.1, 15.4, 15.6], 'naphtha': [6.7, 6.6, 7.0, 6.8, 7.1, 7.3, 7.5, 7.8], 'gasoline': [26.9, 23.9, 26.0, 26.6, 27.1, 27.2, 27.4, 27.3],
       'jet': [7.9, 4.6, 5.2, 6.1, 7.2, 7.6, 7.7, 7.8], 'diesel': [28.7, 26.7, 28.2, 28.7, 28.4, 28.3, 28.3, 28.4], 'resid': [6.2, 5.8, 6.3, 6.5, 6.5, 6.5, 6.5, 6.5], 'other': [11.1, 10.8, 10.9, 11.2, 11.2, 11.0, 11.0, 11.0],
       'total': [100.7, 91.7, 97.4, 100.0, 102.2, 103.0, 103.8, 104.5]}
iea = json.load(open(os.path.join(ROOT, 'scripts', 'world_oil', 'data', 'iea_oil_tfc_by_sector_ej.json')))
iy = iea['years']; ej = iea['ej']

# world total oil consumption (mb/d); 2026 = 2025 x IEA's 2026 / 2025 growth
total = {y: D[y] for y in YEARS if y in D}
total[2026] = round(D[2025] * IEA['total'][7] / IEA['total'][6], 3)

CAT = ['road_passenger', 'road_goods', 'aviation', 'navigation', 'rail', 'industry', 'nonenergy', 'residential', 'other']
def sectors_ej(y):
    i = iy.index(y)
    return {'road': ej['road'][i], 'aviation': ej['aviation'][i], 'navigation': ej['navigation'][i], 'rail': ej['rail'][i], 'industry': ej['industry'][i],
            'nonenergy': ej['nonenergy'][i], 'residential': ej['residential'][i], 'other': ej['other'][i]}

def goods_share(y):          # share of road oil used by trucks / vans / buses: 25% in 1971 (assumed) rising to 44% in 2017 (IEA, The Future of Trucks: ~17 mb/d of ~38), flat after
    y0, y1 = 1971, 2017
    return 0.25 + (0.44 - 0.25) * (min(max(y, y0), y1) - y0) / (y1 - y0)

mbd = {}      # year -> {cat: mb/d}
kind = {}
for y in range(1971, 2020):
    s = {k: v / EJ_PER_MBD for k, v in sectors_ej(y).items()}
    mbd[y] = s; kind[y] = 'iea'
# 2020-2026: product indices relative to 2019
def idx(p, y): return IEA[p][y - 2019] / IEA[p][0]
base = mbd[2019]
for y in range(2020, 2027):
    g = goods_share(2019)
    road_p = base['road'] * (1 - g) * idx('gasoline', y); road_g = base['road'] * g * idx('diesel', y)
    s = {'road': road_p + road_g, 'aviation': base['aviation'] * idx('jet', y), 'navigation': base['navigation'] * idx('resid', y), 'rail': base['rail'] * idx('diesel', y),
         'industry': base['industry'] * (0.5 * idx('diesel', y) + 0.5 * idx('resid', y)), 'nonenergy': base['nonenergy'] * ((IEA['lpg'][y - 2019] + IEA['naphtha'][y - 2019]) / (IEA['lpg'][0] + IEA['naphtha'][0])),
         'residential': base['residential'] * idx('lpg', y), 'other': base['other'] * idx('diesel', y)}
    mbd[y] = s; kind[y] = 'est_fwd'
# scale the 2020-2026 sectors so that final / total keeps its 2019 value
ratio2019 = sum(base.values()) / total[2019]
for y in range(2020, 2027):
    f = ratio2019 * total[y] / sum(mbd[y].values())
    mbd[y] = {k: v * f for k, v in mbd[y].items()}
# 1950-1970: shares and final / total ratio at their 1971 values
r71 = sum(mbd[1971].values()) / total[1971]
for y in range(1950, 1971):
    f = r71 * total[y] / sum(mbd[1971].values())
    mbd[y] = {k: v * f for k, v in mbd[1971].items()}; kind[y] = 'est_back'

use = {c: [] for c in CAT + ['nonfinal']}
for y in YEARS:
    s = mbd[y]; g = goods_share(y)
    parts = {'road_passenger': s['road'] * (1 - g), 'road_goods': s['road'] * g, 'aviation': s['aviation'], 'navigation': s['navigation'], 'rail': s['rail'], 'industry': s['industry'],
             'nonenergy': s['nonenergy'], 'residential': s['residential'], 'other': s['other']}
    parts['nonfinal'] = max(0.0, total[y] - sum(parts.values()))
    for k, v in parts.items():
        use[k].append(round(v, 3))

# ---- US (EIA) by sector and by transport product, kb/d -> mb/d
def eia(file, msn):
    d = {}
    for r in csv.DictReader(open(os.path.join(OIL, file))):
        if r['MSN'] == msn and r['YYYYMM'].endswith('13'):
            try: d[int(r['YYYYMM'][:4])] = float(r['Value']) / 1000
            except ValueError: pass
    return d
us = {'transport': eia('mer_T03.07C.csv', 'PAACPUS'), 'industrial': eia('mer_T03.07B.csv', 'PAICPUS'), 'residential': eia('mer_T03.07A.csv', 'PARCPUS'), 'commercial': eia('mer_T03.07A.csv', 'PACCPUS'),
      'power': eia('mer_T03.07C.csv', 'PAEIZUS'), 'gasoline': eia('mer_T03.07C.csv', 'MGACPUS'), 'distillate': eia('mer_T03.07C.csv', 'DFACPUS'), 'jet': eia('mer_T03.07C.csv', 'JFACPUS'), 'residual': eia('mer_T03.07C.csv', 'RFACPUS')}
uy = list(range(1950, 2026))
us_out = {k: [round(v.get(y, 0.0), 3) for y in uy] for k, v in us.items()}

# ---- production by country, 1960-2025 (mb/d); USSR + Russia combined
REGION = {}
for r, lst in {
    'North America': ['United States', 'Canada', 'Mexico'],
    'South & Central America': ['Brazil', 'Venezuela', 'Colombia', 'Argentina', 'Ecuador', 'Trinidad and Tobago', 'Peru', 'Bolivia', 'Guyana', 'Chile', 'Cuba', 'Suriname'],
    'Europe': ['Norway', 'United Kingdom', 'Italy', 'Denmark', 'Romania', 'Germany', 'Netherlands', 'Poland', 'Austria', 'France', 'Hungary', 'Albania', 'Turkey', 'Croatia', 'Serbia', 'Bulgaria', 'Greece'],
    'CIS': ['Russia', 'Kazakhstan', 'Azerbaijan', 'Turkmenistan', 'Uzbekistan', 'Ukraine', 'Belarus'],
    'Middle East': ['Saudi Arabia', 'Iran', 'Iraq', 'United Arab Emirates', 'Kuwait', 'Qatar', 'Oman', 'Syria', 'Yemen', 'Bahrain', 'Israel', 'Neutral zone'],
    'Africa': ['Nigeria', 'Angola', 'Libya', 'Algeria', 'Egypt', 'Gabon', 'Congo', 'Equatorial Guinea', 'Sudan', 'South Sudan', 'Chad', 'Cameroon', 'Ghana', 'Tunisia', 'Democratic Republic of Congo', 'Morocco', 'Ivory Coast', 'South Africa', 'Niger', 'Mauritania'],
    'Asia Pacific': ['China', 'India', 'Indonesia', 'Malaysia', 'Australia', 'Brunei', 'Thailand', 'Vietnam', 'Pakistan', 'Myanmar', 'Papua New Guinea', 'Japan', 'New Zealand', 'Bangladesh', 'Philippines', 'Taiwan', 'South Korea', 'Timor', 'East Timor']}.items():
    for c in lst: REGION[c] = r
PY = list(range(1960, 2026))
countries = {}
for ent, series in prod.items():
    code = codes.get(ent, '')
    if ent == 'USSR': continue
    if not code or code.startswith('OWID'): continue
    vals = [series.get(y, 0.0) for y in PY]
    if ent == 'Russia':
        ussr = prod['USSR']; vals = [ussr.get(y, 0.0) if y <= 1984 else series.get(y, 0.0) for y in PY]
        ent = 'Russia (USSR before 1985)'
    if max(vals) < 0.02: continue
    countries[ent] = {'region': REGION.get(ent.replace(' (USSR before 1985)', ''), 'Other'), 'mbd': [round(v, 3) for v in vals]}
world_prod = [round(prod['World'].get(y, 0.0), 3) for y in PY]

# ---- consumption by country, 2025 and 2000 for a small "who burns it" table
cons_out = {}
for ent, series in cons.items():
    code = codes.get(ent, '') or ''
    if ent in ('World',): continue
    if ent in {r['entity'] for r in []}: continue
cons_codes = {r['entity']: r['code'] for r in csv.DictReader(open(os.path.join(OIL, 'oil-consumption-by-country.csv'), encoding='utf8'))}
for ent, series in cons.items():
    code = cons_codes.get(ent, '')
    if not code or code.startswith('OWID') or ent == 'World': continue
    if series.get(2025, 0) >= 0.05: cons_out[ent] = {y: round(series.get(y, 0.0), 3) for y in (1990, 2000, 2010, 2019, 2025) if y in series}

out = {'years': YEARS, 'total': [round(total[y], 3) for y in YEARS], 'kind': [kind.get(y, 'est_back') for y in YEARS], 'use': use, 'goodsShare': [round(goods_share(y), 3) for y in YEARS],
       'us': {'years': uy, **us_out}, 'prodYears': PY, 'worldProd': world_prod, 'countries': countries, 'consumption': cons_out,
       'iea2025': {'years': list(range(2019, 2027)), **IEA}, 'ejPerMbd': EJ_PER_MBD}
js = '// World oil: consumption by usage 1950-2026 (IEA final-consumption series 1971-2019 digitised, estimates before / after), production by country 1960-2025, US EIA sectors. Built by scripts/world_oil/build_world_oil.py\nconst WORLD_OIL = ' + json.dumps(out, separators=(',', ':'), ensure_ascii=True) + ';\n'
open(os.path.join(ROOT, 'assets', 'world-oil-data.js'), 'w', encoding='utf8', newline='\n').write(js)
print(len(js) // 1024, 'KB;', len(countries), 'producing countries')
for y in (1950, 1973, 2000, 2019, 2024, 2026):
    i = YEARS.index(y); tr = sum(use[k][i] for k in ('road_passenger', 'road_goods', 'aviation', 'navigation', 'rail'))
    print(y, 'total', round(total[y], 1), 'transport', round(tr, 1), '=', round(100 * tr / total[y]), '% of all oil;', 'final', round(sum(use[k][i] for k in CAT), 1), 'nonfinal', use['nonfinal'][i], {k: round(use[k][i], 1) for k in ('road_passenger', 'road_goods', 'aviation', 'navigation', 'nonenergy')})

"""Electricity & Gas costs page data (gas-electricity-costs.html), built 2026-11-14.

Inputs (scripts/gas_elec/src/):
  statcan_18100001_regular_self_2026.csv   Statistics Canada 18-10-0001-01, regular self-service, cents/L, per city, Jan-Sep 2026
  eia/*.xls                                 EIA monthly retail regular gasoline (EMM_EPMR_PTE_<area>_DPG), USD/gal, Jan-Oct 2026:
                                            US, PADD subregions, 9 states with their own series
  aaa_state_regular_2026_readings.json      AAA state averages, regular, USD/gal: 21 readings (about twice a month) Jan-Nov 2026, from
                                            Internet Archive copies of gasprices.aaa.com/state-gas-price-averages + a live reading 14 Nov 2026
  aaa_2026-11-14.json                       (the live 14 Nov 2026 reading on its own, kept for reference)
  eia_res_electricity_2026_jan_aug.csv      EIA Electric Power Monthly table 5.6.B, residential, Jan-Aug 2026 YTD, USD/kWh
  cer_residential_1000kwh.json              CER market snapshot (2026-03-04), cents/kWh at 1,000 kWh/month, before tax
  boc_fxusdcad_2026.json                    Bank of Canada Valet FXUSDCAD daily, 2026
  electricity_sales_tax.json                sales tax on a residential electricity bill per province / state (compiled 2026-11-14)
  ne50_admin1_us_ca.geojson                 Natural Earth 1:50m admin-1, US + Canada only

Gasoline method
  Canada: the province = plain average of its StatCan cities (ON: Toronto, Ottawa, Thunder Bay; QC: Montreal, Quebec;
          AB/SK/BC: 2 cities; others 1). Territories YT/NT from Whitehorse/Yellowknife. Nunavut has no StatCan city -> blank.
  US:     9 states = own EIA series. The other 41 = average of the AAA state readings over the EIA months (Jan-Oct 2026),
          x one calibration factor (median EIA / AAA over the 9 EIA states, ~0.975: AAA reads ~2.5% above EIA's survey).
          The 9 EIA states are run through the same formula as a check (printed; within about +/-2%).
          (Until 2026-11-16 the 41 states were estimated from one AAA day and the EIA region average: off by up to +12%.)

usage (repo root): python -I scripts/gas_elec/build_gas_elec.py   -> assets/gas-elec-data.js, assets/na-admin1-geo.js
"""
import csv, json, os, math
import xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
ROOT = os.path.dirname(os.path.dirname(HERE))
GAL = 3.785411784

# ---------- FX ----------
fx = json.load(open(os.path.join(SRC, 'boc_fxusdcad_2026.json')))['observations']
fxv = [float(o['FXUSDCAD']['v']) for o in fx]
CAD_PER_USD = round(sum(fxv) / len(fxv), 4)
FX_PERIOD = '%s to %s' % (fx[0]['d'], fx[-1]['d'])

# ---------- Canada gasoline ----------
CITY_PROV = {
    "St. John's, Newfoundland and Labrador": 'NL', 'Charlottetown and Summerside, Prince Edward Island': 'PE',
    'Halifax, Nova Scotia': 'NS', 'Saint John, New Brunswick': 'NB', 'Montréal, Quebec': 'QC', 'Québec, Quebec': 'QC',
    'Ottawa-Gatineau, Ontario part, Ontario/Quebec': 'ON', 'Toronto, Ontario': 'ON', 'Thunder Bay, Ontario': 'ON',
    'Winnipeg, Manitoba': 'MB', 'Regina, Saskatchewan': 'SK', 'Saskatoon, Saskatchewan': 'SK',
    'Calgary, Alberta': 'AB', 'Edmonton, Alberta': 'AB', 'Vancouver, British Columbia': 'BC', 'Victoria, British Columbia': 'BC',
    'Whitehorse, Yukon': 'YT', 'Yellowknife, Northwest Territories': 'NT',
}
city = {}
months_ca = set()
for r in csv.DictReader(open(os.path.join(SRC, 'statcan_18100001_regular_self_2026.csv'), encoding='utf-8')):
    if r['GEO'] in CITY_PROV and r['VALUE']:
        city.setdefault(r['GEO'], []).append(float(r['VALUE']))
        months_ca.add(r['REF_DATE'])
ca_gas, ca_cities = {}, {}
for c, vals in city.items():
    p = CITY_PROV[c]
    ca_cities.setdefault(p, []).append((c.split(',')[0], sum(vals) / len(vals)))
for p, cs in ca_cities.items():
    ca_gas[p] = sum(v for _, v in cs) / len(cs) / 100          # CAD per litre
months_ca = sorted(months_ca)
CA_GAS_PERIOD = '%s to %s 2026' % (['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(months_ca[0][5:]) - 1],
                                   ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(months_ca[-1][5:]) - 1])

# ---------- US gasoline ----------
def eia_2026(area):
    b = xlrd.open_workbook(os.path.join(SRC, 'eia', area + '.xls'))
    s = b.sheet_by_name('Data 1')
    v = []
    for r in range(3, s.nrows):
        d = xlrd.xldate_as_tuple(s.cell_value(r, 0), b.datemode)
        if d[0] == 2026 and s.cell_value(r, 1) != '':
            v.append((d[1], float(s.cell_value(r, 1))))
    return sum(x for _, x in v) / len(v), max(m for m, _ in v)

eia = {a: eia_2026(a) for a in ['NUS', 'R1X', 'R1Y', 'R1Z', 'R20', 'R30', 'R40', 'R5XCA', 'SCA', 'SCO', 'SFL', 'SMA', 'SMN', 'SNY', 'SOH', 'STX', 'SWA']}
US_LAST_M = eia['NUS'][1]
US_GAS_PERIOD = 'Jan to %s 2026' % ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][US_LAST_M - 1]
ST_SERIES = {'CA': 'SCA', 'CO': 'SCO', 'FL': 'SFL', 'MA': 'SMA', 'MN': 'SMN', 'NY': 'SNY', 'OH': 'SOH', 'TX': 'STX', 'WA': 'SWA'}
REGION = {
    'R1X': ['CT', 'ME', 'MA', 'NH', 'RI', 'VT'],
    'R1Y': ['DE', 'DC', 'MD', 'NJ', 'NY', 'PA'],
    'R1Z': ['FL', 'GA', 'NC', 'SC', 'VA', 'WV'],
    'R20': ['IL', 'IN', 'IA', 'KS', 'KY', 'MI', 'MN', 'MO', 'NE', 'ND', 'OH', 'OK', 'SD', 'TN', 'WI'],
    'R30': ['AL', 'AR', 'LA', 'MS', 'NM', 'TX'],
    'R40': ['CO', 'ID', 'MT', 'UT', 'WY'],
    'R5XCA': ['AK', 'AZ', 'HI', 'NV', 'OR', 'WA'],
}
REGION_NAME = {'R1X': 'New England', 'R1Y': 'Central Atlantic', 'R1Z': 'Lower Atlantic', 'R20': 'Midwest', 'R30': 'Gulf Coast',
               'R40': 'Rocky Mountain', 'R5XCA': 'West Coast (excl. California)'}
US_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon',
    'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}
# AAA state averages read about twice a month in 2026 (archived copies of gasprices.aaa.com + one live reading), averaged over the same
# months as the EIA series (Jan-Oct), then put on EIA's level with one factor = median of EIA / AAA over the 9 states EIA publishes
import statistics
AAA_R = json.load(open(os.path.join(SRC, 'aaa_state_regular_2026_readings.json')))['readings']
last_eia = '2026-%02d-31' % US_LAST_M
aaa_win = {d: v for d, v in AAA_R.items() if d <= last_eia}
aaa_avg = {s: sum(v[s] for v in aaa_win.values()) / len(aaa_win) for s in US_NAMES}
AAA_CALIB = statistics.median(eia[ST_SERIES[s]][0] / aaa_avg[s] for s in ST_SERIES)
AAA_N, AAA_FIRST, AAA_LAST = len(aaa_win), min(aaa_win), max(aaa_win)
us_gas, us_gas_src, us_region = {}, {}, {}
print('AAA %d readings %s..%s, calibration to EIA x%.4f; check on the 9 EIA states (AAA x calib vs EIA):' % (AAA_N, AAA_FIRST, AAA_LAST, AAA_CALIB))
for reg, sts in REGION.items():
    for s in sts:
        us_region[s] = reg
        est = aaa_avg[s] * AAA_CALIB
        if s in ST_SERIES:
            act = eia[ST_SERIES[s]][0]
            print('  %s  AAA %.3f  EIA %.3f  diff %+.1f%%' % (s, est, act, (est / act - 1) * 100))
            us_gas[s], us_gas_src[s] = act, 'eia'
        else:
            us_gas[s], us_gas_src[s] = est, 'aaa'
us_gas['CA'], us_gas_src['CA'], us_region['CA'] = eia['SCA'][0], 'eia', 'R50'

# ---------- electricity ----------
us_el = {}
name_to_ab = {n: ab for ab, n in US_NAMES.items()}
for r in csv.DictReader(open(os.path.join(SRC, 'eia_res_electricity_2026_jan_aug.csv'), encoding='utf-8')):
    us_el[name_to_ab[r['state']]] = float(r['usd_per_kwh'])
cer = json.load(open(os.path.join(SRC, 'cer_residential_1000kwh.json')))
CA_NAMES = {'NL': 'Newfoundland and Labrador', 'PE': 'Prince Edward Island', 'NS': 'Nova Scotia', 'NB': 'New Brunswick', 'QC': 'Quebec',
            'ON': 'Ontario', 'MB': 'Manitoba', 'SK': 'Saskatchewan', 'AB': 'Alberta', 'BC': 'British Columbia', 'YT': 'Yukon',
            'NT': 'Northwest Territories', 'NU': 'Nunavut'}

rows = []
for ab, n in CA_NAMES.items():
    rows.append({'id': 'CA-' + ab, 'c': 'CA', 'ab': ab, 'n': n,
                 'g': round(ca_gas[ab], 4) if ab in ca_gas else None, 'gs': 'statcan' if ab in ca_gas else None,
                 'gc': ', '.join(c for c, _ in sorted(ca_cities.get(ab, []))),
                 'e': round(cer[ab] / 100, 4), 'es': 'cer'})
for ab, n in US_NAMES.items():
    if ab == 'DC':
        continue        # no state-level electricity series in the source file; too small for the map
    rows.append({'id': 'US-' + ab, 'c': 'US', 'ab': ab, 'n': n,
                 'g': round(us_gas[ab] / GAL, 4), 'gs': us_gas_src[ab], 'gr': REGION_NAME.get(us_region[ab], 'West Coast'),
                 'e': round(us_el[ab], 4), 'es': 'eia'})

# sales tax on the residential electricity bill (src/electricity_sales_tax.json): 'e' stays before tax, 't' = rate, 'tn' = what it is
tax = json.load(open(os.path.join(SRC, 'electricity_sales_tax.json'), encoding='utf-8'))
for r in rows:
    rate, note = tax[r['c']][r['ab']]
    r['t'], r['tn'] = round(rate / 100, 5), note

data = {
    'built': '2026-11-14',
    'cadPerUsd': CAD_PER_USD, 'fxPeriod': FX_PERIOD,
    'periods': {'caGas': CA_GAS_PERIOD, 'usGas': US_GAS_PERIOD, 'usEl': 'Jan to Aug 2026', 'caEl': 'rates as of Nov 2025'},
    'usAvg': {'gasGal': round(eia['NUS'][0], 3)},
    'aaa': {'n': AAA_N, 'first': AAA_FIRST, 'last': AAA_LAST, 'calib': round(AAA_CALIB, 4)},
    'rows': rows,
}
out = os.path.join(ROOT, 'assets', 'gas-elec-data.js')
open(out, 'w', encoding='utf-8', newline='\n').write(
    '// Built by scripts/gas_elec/build_gas_elec.py - do not edit by hand.\n'
    '// Gasoline: local currency per litre (CAD for Canada, USD for US). Electricity: local currency per kWh.\n'
    'const GAS_ELEC = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('wrote', out, len(rows), 'rows; CAD/USD', CAD_PER_USD, FX_PERIOD, '| CA gas', CA_GAS_PERIOD, '| US gas', US_GAS_PERIOD)

# ---------- geometry ----------
def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + b[0] * a[1] - b[1] * a[0]) / L
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [a, b]

def ring_area(r):
    return abs(sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1))) / 2

geo = json.load(open(os.path.join(SRC, 'ne50_admin1_us_ca.geojson'), encoding='utf-8'))
feats = []
for f in geo['features']:
    p = f['properties']
    cc = 'CA' if p['adm0_a3'] == 'CAN' else 'US'
    g = f['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    arctic = p['postal'] in ('NU', 'NT', 'YT', 'AK')
    eps = 0.06 if arctic else 0.02
    minA = 0.6 if arctic else 0.01            # square degrees: drop small Arctic islands, keep small states' islands
    keep = []
    for poly in polys:
        outer = poly[0]
        if ring_area(outer) < minA and len(polys) > 1:
            continue
        if p['postal'] == 'HI' and min(x for x, _ in outer) < -160.6:     # Northwestern Hawaiian Islands: tiny, and they would shrink the inset
            continue
        rings = []
        for ring in poly[:1]:                 # outer ring only (no holes needed at this scale)
            h = len(ring) // 2                # closed ring: first == last, so simplify the two halves separately
            s = rdp(ring[:h + 1], eps)[:-1] + rdp(ring[h:], eps)
            s = [[round(x, 2), round(y, 2)] for x, y in s]
            if len(s) >= 4:
                rings.append(s)
        if rings:
            keep.append(rings)
    feats.append({'type': 'Feature', 'id': cc + '-' + p['postal'],
                  'geometry': {'type': 'MultiPolygon', 'coordinates': keep}})
gout = os.path.join(ROOT, 'assets', 'na-admin1-geo.js')
open(gout, 'w', encoding='utf-8', newline='\n').write(
    '// Natural Earth 1:50m admin-1 (public domain), US states + Canadian provinces/territories, simplified by scripts/gas_elec/build_gas_elec.py\n'
    'const NA_ADMIN1 = ' + json.dumps({'type': 'FeatureCollection', 'features': feats}, separators=(',', ':')) + ';\n')
print('wrote', gout, os.path.getsize(gout) // 1024, 'KB')

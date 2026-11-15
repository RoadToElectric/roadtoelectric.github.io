"""Gas-car list for the EV vs ICE cost comparator (gas-electricity-costs.html, section 2), built 2026-11-14.

Input: scripts/gas_elec/src/epa_gas_my2024plus.csv - EPA fueleconomy.gov vehicles.csv (file of 2026-11-04), gasoline cars and
       gasoline hybrids (atvType '' / Hybrid / FFV), model years 2024+. Diesel and plug-in hybrids are left out (the page has no diesel price,
       and a plug-in hybrid's cost depends on how much of it is driven on electricity).
       Refresh: download https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip, unzip, then
         python -I scripts/gas_elec/build_ice_models.py --from-full path/to/vehicles.csv
Output: assets/ice-models-data.js  [make, model, year, L/100 km (combined), engine, drive, hybrid 0/1, premium 0/1, class]

Per model family (EPA baseModel) only the newest model year is kept; one entry per make + model + engine + drive + hybrid
(several transmissions of one version are averaged, rounded to 0.1 L/100 km).
Combined MPG (comb08) -> L/100 km = 235.215 / MPG.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src', 'epa_gas_my2024plus.csv')
ROOT = os.path.dirname(os.path.dirname(HERE))
KEEP = ['year', 'make', 'model', 'baseModel', 'VClass', 'drive', 'trany', 'displ', 'cylinders', 'comb08', 'atvType', 'fuelType1']

if '--from-full' in sys.argv:
    full = sys.argv[sys.argv.index('--from-full') + 1]
    w = csv.writer(open(SRC, 'w', newline='', encoding='utf-8')); w.writerow(KEEP); n = 0
    for x in csv.DictReader(open(full, encoding='utf-8', errors='ignore')):
        if int(x['year']) >= 2024 and x['fuelType1'] in ('Regular Gasoline', 'Premium Gasoline', 'Midgrade Gasoline') and x['atvType'] in ('', 'Hybrid', 'FFV'):
            w.writerow([x[k] for k in KEEP]); n += 1
    print('wrote', SRC, n, 'rows')

rows = [r for r in csv.DictReader(open(SRC, encoding='utf-8')) if r['comb08'] and float(r['comb08']) > 0]
fam_y = {}
for r in rows:
    k = (r['make'], r['baseModel'])
    fam_y[k] = max(fam_y.get(k, 0), int(r['year']))
rows = [r for r in rows if int(r['year']) == fam_y[(r['make'], r['baseModel'])]]

DRV = {'Front-Wheel Drive': 'FWD', 'Rear-Wheel Drive': 'RWD', 'All-Wheel Drive': 'AWD', '4-Wheel Drive': '4WD', '4-Wheel or All-Wheel Drive': '4WD',
       'Part-time 4-Wheel Drive': '4WD', '2-Wheel Drive': '2WD'}
groups = {}
for r in rows:
    eng = ('%.1fL %s-cyl' % (float(r['displ']), r['cylinders'])) if r['displ'] and r['cylinders'] else ''
    hyb = 1 if r['atvType'] == 'Hybrid' else 0
    key = (r['make'], r['model'], eng, DRV.get(r['drive'], r['drive']), hyb)
    groups.setdefault(key, []).append(r)
out = []
for (mk, md, eng, drv, hyb), rs in groups.items():
    lp = sum(235.214583 / float(r['comb08']) for r in rs) / len(rs)
    prem = 1 if sum(r['fuelType1'] == 'Premium Gasoline' for r in rs) * 2 > len(rs) else 0     # most variants need premium (Civic 1.5L: only the Si does)
    out.append([mk, md, int(rs[0]['year']), round(lp, 1), eng, drv, hyb, prem, rs[0]['VClass']])
out.sort(key=lambda e: (e[0].lower(), e[1].lower(), e[4], e[5]))
open(os.path.join(ROOT, 'assets', 'ice-models-data.js'), 'w', encoding='utf-8', newline='\n').write(
    '// Built by scripts/gas_elec/build_ice_models.py - do not edit by hand. EPA fueleconomy.gov (2026-11-04), gasoline + hybrid, newest model year per model.\n'
    '// [make, model, model year, L/100 km combined, engine, drive, hybrid 0/1, premium fuel 0/1, class]\n'
    'const ICE_MODELS = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(len(out), 'versions,', sum(e[6] for e in out), 'hybrids,', sum(e[7] for e in out), 'premium; L/100 km %.1f-%.1f' % (min(e[3] for e in out), max(e[3] for e in out)))

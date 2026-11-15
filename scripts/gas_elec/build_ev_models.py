"""EV efficiency list for the Electricity & Gas Costs page (EV drop-down), built 2026-11-14.

Inputs (scripts/gas_elec/src/):
  epa_ev_my2024plus.csv     fueleconomy.gov vehicles.csv (EPA, file of 2026-11-04), battery-electric only, model years 2024+
                            combE = combined kWh/100 miles, measured from the wall (charging losses included); range in miles
  nrcan_bev_my2024plus.csv  NRCan Fuel consumption ratings, battery-electric vehicles 2012-2026 (open.canada.ca, 2026-09-29), MY 2024+
                            Combined (kWh/100 km), same 5-cycle method as the EPA; range in km

One entry per make + model name, newest model year kept (a model dropped after 2024 still appears with its last year).
US entries come from the EPA list; a model that NRCan also lists (same make + model, letters and digits only) is flagged Canada too;
models only NRCan lists are added as Canada-only.

usage (repo root): python -I scripts/gas_elec/build_ev_models.py  -> assets/ev-models-data.js
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
ROOT = os.path.dirname(os.path.dirname(HERE))
MI = 1.609344
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())

def newest(rows, key):
    out = {}
    for r in rows:
        k = key(r)
        if k not in out or r['_y'] > out[k]['_y']:
            out[k] = r
    return out

epa = []
for r in csv.DictReader(open(os.path.join(SRC, 'epa_ev_my2024plus.csv'), encoding='utf-8')):
    if not r['combE'] or float(r['combE']) <= 0:
        continue
    r['_y'] = int(r['year'])
    epa.append(r)
# per model family (EPA baseModel, e.g. "Ioniq 5"): only the newest model year's versions, so a renamed version from an older year does not repeat
fam_y = {}
for r in epa:
    k = (r['make'].strip(), r['baseModel'].strip())
    fam_y[k] = max(fam_y.get(k, 0), r['_y'])
epa = [r for r in epa if r['_y'] == fam_y[(r['make'].strip(), r['baseModel'].strip())]]
epa = newest(epa, lambda r: (r['make'].strip(), r['model'].strip()))

nr = []
for r in csv.DictReader(open(os.path.join(SRC, 'nrcan_bev_my2024plus.csv'), encoding='utf-8')):
    r = {k.strip(): v.strip() for k, v in r.items() if k}
    if not r.get('Combined (kWh/100 km)'):
        continue
    r['_y'] = int(r['Model year'])
    nr.append(r)
nr = newest(nr, lambda r: (r['Make'], r['Model']))

out = []
for (make, model), r in epa.items():
    out.append({'mk': make, 'md': model, 'fam': norm(r['baseModel']), 'y': r['_y'], 'k': round(float(r['combE']) / MI, 1),
                'km': round(float(r['range']) * MI) if r['range'] not in ('', '0') else None, 'ca': False, 'cl': r['VClass']})
by_make = {}
for e in out:
    by_make.setdefault(norm(e['mk']), []).append(e)

# Canada: NRCan names the versions differently (e.g. "IONIQ 5 Long Range AWD (19\" Wheels)"), so a Canadian version is matched to the
# EPA version of the same make whose family name it contains, with the same kWh/100 km (+/- 0.2). Matched EPA versions are flagged Canada.
# A NRCan model whose family the EPA list does not have at all is a Canada-only model: kept, newest year of that family only.
ca_only = {}
for (make, model), r in nr.items():
    k = float(r['Combined (kWh/100 km)'])
    cands = [e for e in by_make.get(norm(make), []) if e['fam'] and e['fam'] in norm(model)]
    if not cands and model.split():         # fallback: same first word of the model name (Audi "Q4 45 e-tron" vs EPA family "Q4 e-tron")
        w = norm(model.split()[0])
        cands = [e for e in by_make.get(norm(make), []) if norm(e['md'].split()[0]) == w]
    if cands:
        hit = [e for e in cands if abs(e['k'] - k) <= 0.2]
        for e in hit:
            e['ca'] = True
        continue
    fam = norm(model.split()[0]) if model.split() else norm(model)
    rng = r.get('Range (km)') or ''
    ca_only.setdefault((norm(make), fam), []).append({'mk': make, 'md': model, 'fam': fam, 'y': r['_y'], 'k': round(k, 1),
                                                      'km': int(float(rng)) if rng else None, 'ca': True, 'us': False, 'cl': r.get('Vehicle class', '')})
for rows in ca_only.values():
    y = max(e['y'] for e in rows)
    out += [e for e in rows if e['y'] == y]

final = [[e['mk'], e['md'], e['y'], e['k'], e['km'], ('US+CA' if e['ca'] else 'US') if e.get('us', True) else 'CA', e['cl']] for e in out]
final.sort(key=lambda e: (e[0].lower(), e[1].lower()))

open(os.path.join(ROOT, 'assets', 'ev-models-data.js'), 'w', encoding='utf-8', newline='\n').write(
    '// Built by scripts/gas_elec/build_ev_models.py - do not edit by hand. EPA fueleconomy.gov (2026-11-04) + NRCan fuel consumption ratings (2026-09-29).\n'
    '// [make, model, model year, kWh/100 km (combined, from the wall), range km, market US | CA | US+CA, class]\n'
    'const EV_MODELS = ' + json.dumps(final, ensure_ascii=False, separators=(',', ':')) + ';\n')
from collections import Counter
print(len(final), 'models;', Counter(e[5] for e in final), '| makes', len({e[0] for e in final}),
      '| kWh/100 km min %.1f max %.1f' % (min(e[3] for e in final), max(e[3] for e in final)))

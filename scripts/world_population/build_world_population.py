"""Builds the data behind world-population.html from the UN World Population Prospects 2024 (medium variant).

Inputs (downloaded to .scratch/pop -- 130 MB, not in git):
  est_1950_2023.csv.gz    WPP2024_PopulationBySingleAgeSex_Medium_1950-2023.csv.gz   (estimates)
  proj_2024_2100.csv.gz   WPP2024_PopulationBySingleAgeSex_Medium_2024-2100.csv.gz   (projections)
  both from https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/<file name>
  Columns used: LocID, ISO3_code, ISO2_code, LocTypeName, ParentID, Location, Time, AgeGrp (0..99, "100+"), PopTotal (thousands, 1 July).

Outputs:
  assets/world-population-data.js      WORLD_POP summary for every location, 1950-2050 (the page's horizon): total + the number of
                                       people aged >= 15..22, >= 65 and >= 80 (everything the page needs is derived from these:
                                       under 16 = total - ge16, 16-64 = ge16 - ge65, people reaching age N in a year = geN - ge(N+1))
  assets/world-population-older.js     WORLD_POP_OLDER: people at every single year of age 60..100+ for every location, 1950-2050, loaded on demand by the
                                       "stop driving at" slider of the potential-drivers card (ge60..ge100 are built from it). Values are persons / s, with s a power of
                                       ten chosen per location so that the largest cell stays under 20,000 (about 5 significant digits for the big cells)
  assets/population/<LocID>.json       every single year of age (0..100+) x every year 1950-2050 for one location, loaded on demand
  .scratch/pop/world_population_full.npz   the full 1950-2100 array, read by load_to_supabase.py

Locations kept: the world, the 6 continental regions (Africa, Asia, Europe, Latin America and the Caribbean, Northern America,
Oceania), the 21 UN subregions and the 237 countries/areas. Persons = thousands x 1000 (the UN publishes 3 decimals).
Run:  python scripts/world_population/build_world_population.py   (from the repo root)"""
import csv, gzip, json, os, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, '.scratch', 'pop')
FILES = ['est_1950_2023.csv.gz', 'proj_2024_2100.csv.gz']
Y0, Y1, PAGE_Y1 = 1950, 2100, 2050          # full data / the page's horizon
PROJ_FROM = 2024                             # first projected year in WPP 2024
REGIONS = {903: 'Africa', 935: 'Asia', 908: 'Europe', 904: 'Latin America and the Caribbean', 905: 'Northern America', 909: 'Oceania'}
GE = [15, 16, 17, 18, 19, 20, 21, 22, 65, 80, 81]  # "aged >= N" series kept for the page (81 = people leaving at the default stop-driving age of 80)
OLD_A0, OLD_A1 = 60, 100                     # single-year ages kept in the lazy 'older' asset
# UN names -> the names the rest of this site uses
RENAME = {
    'United States of America': 'United States', 'Türkiye': 'Turkey', 'Republic of Korea': 'South Korea',
    "Dem. People's Republic of Korea": 'North Korea', 'Viet Nam': 'Vietnam', 'United Republic of Tanzania': 'Tanzania',
    'Bolivia (Plurinational State of)': 'Bolivia', 'Venezuela (Bolivarian Republic of)': 'Venezuela',
    'Iran (Islamic Republic of)': 'Iran', "Lao People's Democratic Republic": 'Laos', 'Republic of Moldova': 'Moldova',
    'Syrian Arab Republic': 'Syria', 'China, Taiwan Province of China': 'Taiwan', 'China, Hong Kong SAR': 'Hong Kong',
    'China, Macao SAR': 'Macao', 'State of Palestine': 'Palestine', 'Brunei Darussalam': 'Brunei',
    'Micronesia (Fed. States of)': 'Micronesia', 'Russian Federation': 'Russia', 'Czechia': 'Czechia',
    'Netherlands (Kingdom of the)': 'Netherlands', 'Côte d\'Ivoire': "Côte d'Ivoire", 'Cabo Verde': 'Cape Verde',
}

def read_locations_and_data():
    meta = {}
    data = {}                                   # LocID -> int64 [years][101 ages], persons
    ny = Y1 - Y0 + 1
    for fn in FILES:
        print('reading', fn, flush=True)
        with gzip.open(os.path.join(SRC, fn), 'rt', encoding='utf-8-sig', newline='') as fh:
            rd = csv.reader(fh); head = next(rd); ix = {c: i for i, c in enumerate(head)}
            iL, iT, iP, iN, i3, i2, iY, iA, iPop = (ix[c] for c in ('LocID', 'LocTypeName', 'ParentID', 'Location', 'ISO3_code', 'ISO2_code', 'Time', 'AgeGrp', 'PopTotal'))
            for r in rd:
                t = r[iT]
                if t not in ('World', 'Geographic region', 'Subregion', 'Country/Area'):
                    continue
                loc = int(r[iL])
                if t == 'Geographic region' and loc not in REGIONS:
                    continue                    # skip "Americas" (= Latin America and the Caribbean + Northern America)
                if loc not in meta:
                    meta[loc] = dict(id=loc, un=r[iN], type=t, parent=int(r[iP]) if r[iP] else 0, iso3=r[i3], iso2=r[i2].lower())
                    data[loc] = np.zeros((ny, 101), dtype=np.int64)
                a = 100 if r[iA] == '100+' else int(r[iA])
                data[loc][int(r[iY]) - Y0, a] = round(float(r[iPop]) * 1000)
    return meta, data

def main():
    meta, data = read_locations_and_data()
    ids = sorted(meta)
    kinds = {}
    for loc in ids:
        m = meta[loc]
        m['kind'] = {'World': 'world', 'Geographic region': 'region', 'Subregion': 'subregion', 'Country/Area': 'country'}[m['type']]
        m['name'] = RENAME.get(m['un'], m['un'])
        kinds[m['kind']] = kinds.get(m['kind'], 0) + 1
    print('locations by kind:', kinds)
    # hierarchy: country -> subregion (parent) -> region ; the 5 Northern America countries hang off a non-typed parent, so they sit
    # directly under the Northern America region, which then also acts as its own subregion
    for loc in ids:
        m = meta[loc]
        if m['kind'] == 'country':
            p = m['parent']
            m['sub'] = p if p in meta and meta[p]['kind'] == 'subregion' else 905
            m['reg'] = meta[m['sub']]['parent'] if meta[m['sub']]['kind'] == 'subregion' else 905
        elif m['kind'] == 'subregion':
            m['sub'] = loc; m['reg'] = m['parent']
        elif m['kind'] == 'region':
            m['sub'] = loc if loc == 905 else 0; m['reg'] = loc
        else:
            m['sub'] = 0; m['reg'] = 0

    # ---- checks: the aggregates must equal the sum of their members (all years, all ages)
    tot = {loc: data[loc].sum(axis=1) for loc in ids}
    def members(kind_field, key):
        return [l for l in ids if meta[l]['kind'] == 'country' and meta[l][kind_field] == key]
    worst = 0.0
    for reg in REGIONS:
        diff = np.abs(data[reg].sum(axis=0).sum() - sum(data[c].sum() for c in members('reg', reg))) / data[reg].sum()
        worst = max(worst, diff)
    wdiff = abs(data[900].sum() - sum(data[c].sum() for c in ids if meta[c]['kind'] == 'country')) / data[900].sum()
    print(f'check: region totals vs sum of their countries, worst relative gap {worst:.2e};  world vs sum of all countries {wdiff:.2e}')
    for sub in [l for l in ids if meta[l]['kind'] == 'subregion']:
        d = abs(data[sub].sum() - sum(data[c].sum() for c in members('sub', sub))) / data[sub].sum()
        if d > 1e-3: print('  subregion mismatch', meta[sub]['name'], d)
    print('check: world population 1950 / 2023 / 2026 / 2050:', *(f"{tot[900][y - Y0] / 1e9:.3f}B" for y in (1950, 2023, 2026, 2050)))
    for nm in ('India', 'China', 'United States', 'Nigeria'):
        loc = next(l for l in ids if meta[l]['name'] == nm); print(f"  {nm:14} 2026: {tot[loc][2026 - Y0] / 1e6:8.1f}M   2050: {tot[loc][2050 - Y0] / 1e6:8.1f}M")

    # ---- summary asset (1950..2050)
    ny = PAGE_Y1 - Y0 + 1
    def ge_series(arr, n):                      # people aged >= n, per year
        return arr[:ny, n:].sum(axis=1)
    out_locs = []
    for loc in ids:
        m = meta[loc]; arr = data[loc]
        rec = dict(id=loc, n=m['name'], k=m['kind'], reg=m['reg'], sub=m['sub'], p=[int(v) for v in tot[loc][:ny]],
                   g=[[int(v) for v in ge_series(arr, n)] for n in GE])
        if m['kind'] == 'country':
            rec['iso3'] = m['iso3']; rec['iso2'] = m['iso2']
        out_locs.append(rec)
    summary = dict(source='United Nations, Department of Economic and Social Affairs, Population Division: World Population Prospects 2024, medium variant',
                   unit='persons (1 July)', y0=Y0, y1=PAGE_Y1, projFrom=PROJ_FROM, ge=GE, locs=out_locs)
    p = os.path.join(ROOT, 'assets', 'world-population-data.js')
    open(p, 'w', encoding='utf-8', newline='\n').write('const WORLD_POP = ' + json.dumps(summary, separators=(',', ':'), ensure_ascii=False) + ';\n')
    print(f'wrote assets/world-population-data.js  {os.path.getsize(p) / 1e6:.2f} MB  ({len(out_locs)} locations)')

    # ---- single-year ages 60..100+ for the 'stop driving at' slider (lazy asset)
    older = {}
    for loc in ids:
        blk = data[loc][:ny, OLD_A0:OLD_A1 + 1]               # years x ages
        step = 1
        while blk.max() / step > 20000:
            step *= 10
        older[str(loc)] = dict(s=step, d=[int(round(v / step)) for v in blk.T.reshape(-1)])   # age-major, year-minor
    op = os.path.join(ROOT, 'assets', 'world-population-older.js')
    open(op, 'w', encoding='utf-8', newline='\n').write('const WORLD_POP_OLDER = ' + json.dumps(dict(a0=OLD_A0, a1=OLD_A1, y0=Y0, y1=PAGE_Y1, locs=older), separators=(',', ':')) + ';\n')
    print(f'wrote assets/world-population-older.js  {os.path.getsize(op) / 1e6:.2f} MB')

    # ---- per-location exact-age files (1950..2050)
    odir = os.path.join(ROOT, 'assets', 'population'); os.makedirs(odir, exist_ok=True)
    size = 0
    for loc in ids:
        m = meta[loc]
        body = dict(id=loc, n=m['name'], y0=Y0, y1=PAGE_Y1, d=[[int(v) for v in row] for row in data[loc][:ny]])
        fp = os.path.join(odir, f'{loc}.json')
        open(fp, 'w', encoding='utf-8', newline='\n').write(json.dumps(body, separators=(',', ':'), ensure_ascii=False))
        size += os.path.getsize(fp)
    print(f'wrote {len(ids)} files to assets/population/  {size / 1e6:.1f} MB total, {size / len(ids) / 1e3:.0f} KB average')

    # ---- full 1950..2100 array for the database loader
    np.savez_compressed(os.path.join(SRC, 'world_population_full.npz'), ids=np.array(ids), data=np.stack([data[l] for l in ids]))
    json.dump({str(l): {k: meta[l][k] for k in ('id', 'name', 'un', 'kind', 'iso3', 'iso2', 'reg', 'sub')} for l in ids}, open(os.path.join(SRC, 'world_population_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('saved the full 1950-2100 array to .scratch/pop/world_population_full.npz')

if __name__ == '__main__':
    main()

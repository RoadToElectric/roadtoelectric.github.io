"""Loads world_population_by_age (one row per location x year, one column per single year of age) from the array written by
build_world_population.py (.scratch/pop/world_population_full.npz, 1950-2100). Idempotent upsert on (loc_id, year, variant).
Usage:  python scripts/world_population/load_to_supabase.py [--limit N]     (N = only the first N rows, for a test)"""
import json, os, re, sys, time, urllib.request
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, '.scratch', 'pop')
txt = open(os.path.join(ROOT, 'scripts', 'refresh_manufacturer_monthly_data.py'), encoding='utf-8').read()
KEY = ''.join(re.findall(r'"([^"]+)"', re.search(r'ANON_KEY = \((.*?)\)', txt, re.S).group(1)))
URL = 'https://rtmlxvjpjxcvjdykrkvm.supabase.co/rest/v1/world_population_by_age?on_conflict=loc_id,year,variant'
Y0, PROJ_FROM, BATCH = 1950, 2024, 150

z = np.load(os.path.join(SRC, 'world_population_full.npz')); ids, data = z['ids'], z['data']
meta = json.load(open(os.path.join(SRC, 'world_population_meta.json'), encoding='utf-8'))
limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else None
rows = []
for i, loc in enumerate(ids):
    m = meta[str(int(loc))]
    for yi in range(data.shape[1]):
        year = Y0 + yi; ages = data[i, yi]
        r = dict(loc_id=int(loc), iso3=m['iso3'] or None, location=m['name'], loc_type=m['kind'], region_id=m['reg'] or None, subregion_id=m['sub'] or None,
                 year=year, is_projection=year >= PROJ_FROM, variant='Medium', total=int(ages.sum()))
        r.update({f'age_{a}': int(ages[a]) for a in range(101)})
        rows.append(r)
        if limit and len(rows) >= limit: break
    if limit and len(rows) >= limit: break
print(f'{len(rows):,} rows to send in batches of {BATCH}')
t0 = time.time()
for s in range(0, len(rows), BATCH):
    body = json.dumps(rows[s:s + BATCH]).encode()
    req = urllib.request.Request(URL, data=body, method='POST', headers={'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'Prefer': 'resolution=merge-duplicates,return=minimal'})
    for attempt in range(4):
        try:
            urllib.request.urlopen(req, timeout=120).read(); break
        except Exception as e:
            if attempt == 3: raise
            print('  retry', s, repr(e)[:150]); time.sleep(2 + attempt * 3)
    if (s // BATCH) % 20 == 0: print(f'  {min(s + BATCH, len(rows)):,}/{len(rows):,}  {time.time() - t0:.0f}s', flush=True)
print(f'done in {time.time() - t0:.0f}s')

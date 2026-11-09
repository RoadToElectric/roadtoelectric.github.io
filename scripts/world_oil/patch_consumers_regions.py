"""Adds the field `g` (region) to every row of assets/world-oil-consumers.js without rebuilding it (the build script now writes it too). Idempotent."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from oil_regions import REGION_OF

p = os.path.join(HERE, '..', '..', 'assets', 'world-oil-consumers.js')
t = open(p, encoding='utf-8', newline='').read()
m = re.search(r'^(.*?const WORLD_OIL_CONS = )(\{.*\});(\s*)$', t, re.S)
d = json.loads(m.group(2))
miss = [r['c'] + '=' + r['n'] for r in d['rows'] if r['c'] not in REGION_OF]
assert not miss, miss
for r in d['rows']:
    r['g'] = REGION_OF[r['c']]
open(p, 'w', encoding='utf-8', newline='').write(m.group(1) + json.dumps(d, separators=(',', ':'), ensure_ascii=True) + ';' + m.group(3))
print('regions added to', len(d['rows']), 'rows')

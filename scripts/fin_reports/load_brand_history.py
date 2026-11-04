"""Upserts every row of brand_history_data.ROWS into Supabase table manufacturer_brand_sales_history (idempotent on group_name, brand, year, period_type).
Usage:  python scripts/fin_reports/load_brand_history.py [--group "Toyota Motor Corporation"]   (default: all groups)"""
import json, os, re, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from brand_history_data import ROWS
txt = open(os.path.join(ROOT, 'scripts', 'refresh_manufacturer_monthly_data.py'), encoding='utf-8').read()
KEY = ''.join(re.findall(r'"([^"]+)"', re.search(r'ANON_KEY = \((.*?)\)', txt, re.S).group(1)))
URL = 'https://rtmlxvjpjxcvjdykrkvm.supabase.co/rest/v1/manufacturer_brand_sales_history?on_conflict=group_name,brand,year,period_type'
only = sys.argv[sys.argv.index('--group') + 1] if '--group' in sys.argv else None
out = []
for g, b, y, pt, u, basis, conf, src, url, scope, notes in ROWS:
    if only and g != only:
        continue
    s, e = {'CY': (f'{y}-01-01', f'{y}-12-31'), 'FY': (f'{y}-04-01', f'{y + 1}-03-31'), '9M': (f'{y}-01-01', f'{y}-09-30'), 'H1': (f'{y}-01-01', f'{y}-06-30')}[pt]
    out.append(dict(group_name=g, brand=b, year=y, period_type=pt, start_date=s, end_date=e, units=u, basis=basis, confidence=conf, source_doc=src, source_url=url or None, scope=scope or None, notes=notes or None))
for i in range(0, len(out), 100):
    req = urllib.request.Request(URL, data=json.dumps(out[i:i + 100]).encode(), method='POST',
                                 headers={'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'Prefer': 'resolution=merge-duplicates,return=minimal'})
    urllib.request.urlopen(req, timeout=120).read()
print(f'upserted {len(out)} rows')

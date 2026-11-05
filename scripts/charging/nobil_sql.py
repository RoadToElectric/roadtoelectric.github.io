"""Writes scripts/charging/out/charging_4_nobil.sql: updates the charging_country_snapshot row and replaces the charging_country_brand rows of the NOBIL countries (Norway, Sweden)
with the values of assets/charging-data.js.  Run after build_charging.py (repo root):  python -I scripts/charging/nobil_sql.py"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from charging_sql import q  # noqa: E402

D = json.loads(re.search(r'const CHARGING = (\{.*\});', open(os.path.join(ROOT, 'assets', 'charging-data.js'), encoding='utf8').read(), re.S).group(1))
snap = D['meta']['snapshot']
out = ["alter table public.charging_country_snapshot add column if not exists listing_source text not null default 'Open Charge Map';",
       "comment on column public.charging_country_snapshot.listing_source is 'Register behind the ocm_* columns: Open Charge Map, or NOBIL (nobil.no, CC BY 4.0) for Norway and Sweden since 2026-11-05';"]
for c in D['countries']:
    if c.get('src') != 'nobil':
        continue
    o = c['ocm']
    b = o['bands']
    fs = o['fs']
    sh = c['sh']
    out.append("update public.charging_country_snapshot set listing_source='NOBIL', ocm_stations=%s, ocm_ports=%s, ocm_ports_lt12=%s, ocm_ports_12_49=%s, ocm_ports_50_149=%s, ocm_ports_150_349=%s, ocm_ports_350plus=%s, "
               "ocm_fast_stations=%s, ocm_fast_ports=%s, share_12_22_of_le22=%s, share_22_49_of_22_149=%s where iso2=%s and snapshot_date=%s;" %
               (o['st'], o['po'], b[0], b[1], b[2], b[3], b[4], fs[0], fs[1], sh[0], sh[1], q(c['iso']), q(snap)))
    out.append("delete from public.charging_country_brand where iso2=%s and snapshot_date=%s;" % (q(c['iso']), q(snap)))
    rows = ','.join('(%s)' % ','.join(q(v) for v in (c['n'], c['iso'], snap, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], 'NOBIL')) for r in o['brands'])
    out.append("insert into public.charging_country_brand (country,iso2,snapshot_date,brand,stations,ports,ports_lt12,ports_12_49,ports_50_149,ports_150_349,ports_350plus,source) values %s;" % rows)
open(os.path.join(HERE, 'out', 'charging_4_nobil.sql'), 'w', encoding='utf8').write('\n'.join(out) + '\n')
print(len(out), 'statements')

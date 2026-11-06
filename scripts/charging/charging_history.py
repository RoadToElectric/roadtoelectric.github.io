"""Charging history: the fast-port snapshot table (public.charging_fast_history) and the "added in the last 6 months" figures of the charging page.

Rows are long format, one per (country, date, source):  stations, ports_all, fast_ports (>= 50 kW), ultra_ports (>= 150 kW).
  basis 'snapshot'                       the numbers of this build (call it every month after fetching the data: the future 6-month change of every country comes from these rows)
  basis 'reconstructed'  month-end values rebuilt from the opening date of each station / site in the files we already hold (existing sites only: closures are not dated,
                                         so older months are a slight undercount): Tesla (supercharge.info dateOpened), US DOE AFDC (open_date, US and Canada), NOBIL (Created, Norway and Sweden)
Sources: 'Tesla Superchargers' (supercharge.info), 'US DOE AFDC', 'NOBIL', 'Open Charge Map' (listing of every other country; coverage varies, so its changes are not clean openings).
Outputs:  scripts/charging/out/charging_6_history_*.sql  (DDL + inserts, apply as a Supabase migration)  and  assets/charging-added-data.js  (CHARGING_ADDED for the page).
usage (repo root):  python -I scripts/charging/charging_history.py [--snapshot-only]      (run build_charging.py first)"""
import datetime, json, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import build_charging as bc  # noqa: E402
import nobil_lib  # noqa: E402
from charging_sources import COUNTRIES  # noqa: E402

CACHE = os.path.join(ROOT, '.scratch', 'chg')
TESLA, AFDC, NOBIL, OCM = 'Tesla Superchargers', 'US DOE AFDC', 'NOBIL', 'Open Charge Map'
SNAP = bc.SNAPSHOT                      # date of the supercharge.info, AFDC and Open Charge Map caches
NOBIL_SNAP = bc.NOBIL_SNAPSHOT
MONTH_ENDS = ['2026-03-31', '2026-04-30', '2026-05-31', '2026-06-30', '2026-07-31', '2026-08-31', '2026-09-30']
SNAPSHOT_ONLY = '--snapshot-only' in sys.argv
NAME = {iso: v[0] for iso, v in COUNTRIES.items()}


def minus_months(d, k):
    y, m = divmod(d.year * 12 + d.month - 1 - k, 12)
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m])
    return datetime.date(y, m + 1, day)


rows = {}          # (iso, as_of, source) -> dict


def put(iso, as_of, source, basis, stations, ports_all, fast, ultra, notes=None):
    rows[(iso, as_of, source)] = dict(iso=iso, country=NAME.get(iso, iso), as_of=as_of, source=source, basis=basis, stations=stations, ports_all=ports_all, fast=fast, ultra=ultra, notes=notes)


# ---------- Tesla Superchargers ----------
tname = {v[2]: iso for iso, v in COUNTRIES.items() if v[2]}
sites = [s for s in json.load(open(os.path.join(CACHE, 'supercharge_all.json'), encoding='utf-8')) if s['status'] == 'OPEN']


def tesla_at(day):           # per iso: [sites, stalls, stalls at >= 150 kW], for sites opened on or before day (None = no date filter)
    out = defaultdict(lambda: [0, 0, 0])
    for s in sites:
        iso = tname.get(s['address']['country'])
        if not iso or (day and not (s.get('dateOpened') and s['dateOpened'] <= day)):
            continue
        e = out[iso]; e[0] += 1; e[1] += s['stallCount']; e[2] += s['stallCount'] if (s.get('powerKilowatt') or 0) >= 150 else 0
    return out


for iso, v in tesla_at(None).items():
    put(iso, SNAP, TESLA, 'snapshot', v[0], v[1], v[1], v[2])
if not SNAPSHOT_ONLY:
    big = {iso for iso, v in tesla_at(None).items() if v[1] >= 100}      # month-end history only for the countries with 100+ Supercharger stalls
    for me in MONTH_ENDS:
        for iso, v in tesla_at(me).items():
            if iso in big:
                put(iso, me, TESLA, 'reconstructed', v[0], v[1], v[1], v[2])

# ---------- US DOE AFDC (US, Canada) ----------
afdc = {}
for iso, fn in (('US', 'afdc_us.json'), ('CA', 'afdc_ca.json')):
    afdc[iso] = [s for s in json.load(open(os.path.join(CACHE, 'qc', fn), encoding='utf-8'))['fuel_stations'] if s.get('status_code') == 'E' and s.get('access_code') == 'public']


def afdc_at(iso, day):       # [stations with a DC fast port, all public ports, DC fast ports]
    st = po = fa = 0
    for s in afdc[iso]:
        if day and not (s.get('open_date') and s['open_date'] <= day):
            continue
        f = s.get('ev_dc_fast_num') or 0
        p = f + (s.get('ev_level2_evse_num') or 0) + (s.get('ev_level1_evse_num') or 0)
        if p:
            st += 1; po += p; fa += f
    return st, po, fa


for iso in afdc:
    st, po, fa = afdc_at(iso, None)
    put(iso, SNAP, AFDC, 'snapshot', st, po, fa, None, 'stations = public EV stations of any speed; fast = DC fast ports; the AFDC gives no per-port power')
    if not SNAPSHOT_ONLY:
        for me in MONTH_ENDS:
            st, po, fa = afdc_at(iso, me)
            put(iso, me, AFDC, 'reconstructed', st, po, fa, None)

# ---------- NOBIL (Norway, Sweden) ----------
nob = {iso: nobil_lib.stations(code) for iso, code in bc.NOBIL.items()}


def nobil_at(iso, day):      # [stations, ports, ports >= 50 kW, ports >= 150 kW]
    st = po = fa = ul = 0
    for s in nob[iso] or []:
        if day and not (s['created'] and s['created'] <= day):
            continue
        st += 1; po += len(s['kw']); fa += sum(1 for k in s['kw'] if (k or 0) >= 50); ul += sum(1 for k in s['kw'] if (k or 0) >= 150)
    return st, po, fa, ul


for iso in nob:
    if nob[iso] is None:
        continue
    put(iso, NOBIL_SNAP, NOBIL, 'snapshot', *nobil_at(iso, None))
    if not SNAPSHOT_ONLY:
        for me in MONTH_ENDS:
            put(iso, me, NOBIL, 'reconstructed', *nobil_at(iso, me),
                'bulk registration of ~2,200 fast ports in Oct 2026' if iso == 'SE' else None)

# ---------- Open Charge Map (every other country): the listing of the build ----------
chg = json.loads(re.search(r'const CHARGING = (\{.*\});', open(os.path.join(ROOT, 'assets', 'charging-data.js'), encoding='utf8').read(), re.S).group(1))
for c in chg['countries']:
    if c.get('src') == 'nobil' or c['iso'] == 'CN' or not c.get('ocm'):
        continue
    o = c['ocm']; b = o['bands']
    put(c['iso'], SNAP, OCM, 'snapshot', o['st'], o['po'], b[2] + b[3] + b[4], b[3] + b[4])

# ---------- "added in the last 6 months" for the page ----------
def added(src_rows_fn, end):
    return minus_months(datetime.date.fromisoformat(end), 6).isoformat(), end


t_start, t_end = added(None, SNAP)
n_start, n_end = added(None, NOBIL_SNAP)
tesla_add, tw = {}, [0, 0]
for s in sites:
    iso = tname.get(s['address']['country'])
    d = s.get('dateOpened') or ''
    if iso and t_start < d <= t_end:
        e = tesla_add.setdefault(iso, [0, 0]); e[0] += s['stallCount']; e[1] += 1
        tw[0] += s['stallCount']; tw[1] += 1
all_add = {}
for iso in afdc:
    f0 = afdc_at(iso, t_start)[2]; f1 = afdc_at(iso, t_end)[2]
    all_add[iso] = dict(n=f1 - f0, base=f0, src='US DOE AFDC', win=[t_start, t_end])
f0 = nobil_at('NO', n_start)[2]; f1 = nobil_at('NO', n_end)[2]
all_add['NO'] = dict(n=f1 - f0, base=f0, src='NOBIL', win=[n_start, n_end])
meta = dict(months=6, tesla=[t_start, t_end], afdc=[t_start, t_end], nobil=[n_start, n_end],
            note='Fast = 50 kW and more. Counted from the opening date of each site now in the files (closures are not dated, so this is gross openings of sites still open); NOBIL: the registration date of the station.')
js = ('// Fast ports (50+ kW) added in the last 6 months, from dated sources: Tesla (supercharge.info dateOpened, [stalls, sites] per country), US DOE AFDC (US, Canada: open_date) and NOBIL (Norway: registration date).\n'
      '// Built by scripts/charging/charging_history.py; the full month-end history is in Supabase table charging_fast_history.\n'
      'const CHARGING_ADDED = ' + json.dumps(dict(meta=meta, tesla=tesla_add, teslaWorld=tw, all=all_add), separators=(',', ':'), ensure_ascii=False) + ';\n')
if not SNAPSHOT_ONLY:
    open(os.path.join(ROOT, 'assets', 'charging-added-data.js'), 'w', encoding='utf-8').write(js)

# ---------- SQL ----------
DDL = """create table if not exists public.charging_fast_history (
  iso2 text not null, country text not null, as_of date not null, source text not null,
  basis text not null check (basis in ('snapshot', 'reconstructed')),
  stations integer, ports_all integer, fast_ports integer, ultra_ports integer, notes text,
  created_at timestamptz not null default now(),
  primary key (iso2, as_of, source));
comment on table public.charging_fast_history is 'Charging stations and ports (all speeds, 50+ kW, 150+ kW) per country, date and source. basis snapshot = values of a monthly build; reconstructed = month-end values rebuilt from the opening date of each station now in the file (Tesla Superchargers from supercharge.info, US DOE AFDC, NOBIL; sites since closed are missing, so older months are a slight undercount). Fast ports added over 6 months = difference between two dates of the same source. Open Charge Map is a partial, crowd-sourced listing: its change mixes openings and new records. Built by scripts/charging/charging_history.py.';
alter table public.charging_fast_history enable row level security;
"""


def q(v):
    return 'null' if v is None else str(v) if isinstance(v, (int, float)) else "'" + str(v).replace("'", "''") + "'"


vals = [r for r in sorted(rows.values(), key=lambda r: (r['source'], r['iso'], r['as_of']))]
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
for f in os.listdir(os.path.join(HERE, 'out')):
    if f.startswith('charging_6_history'):
        os.remove(os.path.join(HERE, 'out', f))
chunks = [vals[i:i + 600] for i in range(0, len(vals), 600)]
for i, ch in enumerate(chunks):
    body = ',\n'.join('(%s)' % ','.join(q(v) for v in (r['iso'], r['country'], r['as_of'], r['source'], r['basis'], r['stations'], r['ports_all'], r['fast'], r['ultra'], r['notes'])) for r in ch)
    sql = ('' if SNAPSHOT_ONLY or i else DDL) + 'insert into public.charging_fast_history (iso2,country,as_of,source,basis,stations,ports_all,fast_ports,ultra_ports,notes) values\n' + body + \
          '\non conflict (iso2, as_of, source) do update set country=excluded.country, basis=excluded.basis, stations=excluded.stations, ports_all=excluded.ports_all, fast_ports=excluded.fast_ports, ultra_ports=excluded.ultra_ports, notes=excluded.notes;\n'
    open(os.path.join(HERE, 'out', 'charging_6_history_%d.sql' % (i + 1)), 'w', encoding='utf-8').write(sql)
print(len(vals), 'rows in', len(chunks), 'sql file(s)')
print('window Tesla/AFDC', t_start, t_end, '| NOBIL', n_start, n_end)
print('Tesla added', tw, 'top', sorted(tesla_add.items(), key=lambda kv: -kv[1][0])[:6])
print('all-operator added', {k: (v['n'], v['base']) for k, v in all_add.items()})

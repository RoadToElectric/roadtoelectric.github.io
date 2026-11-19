"""Monthly electric-truck tracker: pulls new truck registrations by fuel from official monthly sources and writes
assets/ev-trucks-monthly.js (EVTM) for the "Monthly tracker" card of ev-trucking.html.

Sources (all free, no key, re-run any time; each one only adds months, nothing is estimated):
  Denmark      Statistics Denmark StatBank BIL53 (api.statbank.dk): new lorries + road tractors by propellant, monthly 2018+
               ("Electricity" = battery-electric). DST publishes about 6-8 weeks after the month.
  Norway       Statistics Norway table 14020 (data.ssb.no): first-time registered NEW lorries (Lastebiler) by fuel,
               "Electric/zero-emission" (battery + hydrogen). Published ~1st week of the next month.
  Sweden       Mobility Sweden monthly report xlsx ("Manadsrapport Nyregistreringar <month> <year>.xlsx", sheet
               "LB - Vikt & Drivmedel"): trucks by gross-weight group and fuel, month + same month last year.
               Heavy = 16 t and over; medium = 3.5-16 t. "EL" = battery-electric. Published 1st working day.
  Finland      Traficom PxWeb 040_ensirek_tau_104 (trafi2.stat.fi): first registrations, Lorries > 3.5 t, by driving power
               (Electricity + Hydrogen). Published ~1st week.
  Germany      KBA FZ28 monthly xlsx (new vehicles with alternative drive): semi-tractors (Sattelzugmaschinen) only,
               battery-electric + fuel cell; heavy view only (KBA's truck row includes vans). Row exists from May 2026.
  Netherlands  RDW open data (SODA m9d7-ebf2 registry + 8ys7-d773 fuel): EU category N2 (3.5-12 t) and N3 (> 12 t),
               first registration in NL in the month AND first admission no earlier than the previous month (= new,
               not a used import). Electric = only fuel "Elektriciteit". The registry only holds vehicles still
               registered, so trucks exported since are missing: older months read a little low.
Hand-entered (scripts/ev_trucks/data/monthly/manual.json): China heavy-truck new-energy share (press reports of
compulsory-insurance registrations), ACEA EU year-to-date shares and the ACEA Q1-Q3 country table.

Run from the repo root:  python scripts/ev_trucks/fetch_monthly.py            (all sources, ~3-5 min, NL is the slow one)
                         python scripts/ev_trucks/fetch_monthly.py --skip nl   (reuse the saved NL pull)
                         python scripts/ev_trucks/fetch_monthly.py --build     (no download, rebuild the asset only)
"""
import json, os, re, sys, io, collections, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
DATA = os.path.join(HERE, 'data', 'monthly')
START = '2024-01'
UA = {'User-Agent': 'Mozilla/5.0 (RoadToElectric data refresh)'}
os.makedirs(DATA, exist_ok=True)


def get(url, data=None, headers=None, timeout=120):
    h = dict(UA); h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    return urllib.request.urlopen(req, timeout=timeout).read()


def ym(y, m):
    return '%04d-%02d' % (y, m)


def save(name, rows):
    json.dump(dict(sorted(rows.items())), open(os.path.join(DATA, name + '.json'), 'w'), indent=0)
    ks = sorted(rows)
    print(f'{name}: {len(ks)} months, {ks[0]} .. {ks[-1]}')


# ---------- Denmark ----------
def fetch_dk():
    body = {"table": "BIL53", "format": "BULK", "lang": "en", "variables": [
        {"code": "OMRÅDE", "values": ["000"]}, {"code": "BILTYPE", "values": ["4000103000", "4000103030"]},
        {"code": "BRUG", "values": ["1000"]}, {"code": "DRIV", "values": ["20200", "20225", "20231"]}, {"code": "Tid", "values": ["*"]}]}
    txt = get('https://api.statbank.dk/v1/data', json.dumps(body).encode(), {'Content-Type': 'application/json'}).decode('utf-8-sig')
    out = collections.defaultdict(lambda: {'total': 0, 'el': 0, 'heavy_total': 0, 'heavy_el': 0})
    for line in txt.splitlines()[1:]:
        reg, typ, use, fuel, t, v = line.split(';')
        k = t[:4] + '-' + t[5:7]
        if k < START or v in ('', '..'):
            continue
        v = int(v); tractor = typ.startswith('Road tractors')
        f = 'total' if fuel.startswith('Total') else 'el'
        out[k][f] += v
        if tractor:
            out[k]['heavy_' + f] += v
    save('dk', out)


# ---------- Norway ----------
def fetch_no():
    q = {"query": [{"code": "TypeRegistrering", "selection": {"filter": "item", "values": ["N"]}},
                   {"code": "DrivstoffType", "selection": {"filter": "item", "values": ["19", "20", "21", "6"]}},
                   {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Lastebiler"]}},
                   {"code": "Tid", "selection": {"filter": "all", "values": ["*"]}}], "response": {"format": "json-stat2"}}
    d = json.loads(get('https://data.ssb.no/api/v0/en/table/14020', json.dumps(q).encode()))
    t = list(d['dimension']['Tid']['category']['index']); f = list(d['dimension']['DrivstoffType']['category']['index'])
    n = len(t); v = d['value']; out = {}
    for j, tt in enumerate(t):
        k = tt[:4] + '-' + tt[5:7]
        if k < START:
            continue
        vals = {ff: (v[i * n + j] or 0) for i, ff in enumerate(f)}
        out[k] = {'total': sum(vals.values()), 'el': vals['19']}
    save('no', out)


# ---------- Finland ----------
def fetch_fi():
    q = {"query": [{"code": "Maakunta", "selection": {"filter": "item", "values": ["MA1"]}},
                   {"code": "Ajoneuvoluokka", "selection": {"filter": "item", "values": ["03"]}},
                   {"code": "Käyttövoima", "selection": {"filter": "item", "values": ["YH", "04", "05"]}},
                   {"code": "Kuukausi", "selection": {"filter": "all", "values": ["*"]}}], "response": {"format": "json-stat2"}}
    d = json.loads(get('https://trafi2.stat.fi/PXWeb/api/v1/en/TraFi/Ensirekisteroinnit/040_ensirek_tau_104.px', json.dumps(q).encode()))
    t = list(d['dimension']['Kuukausi']['category']['index']); n = len(t); v = d['value']; out = {}
    for j, tt in enumerate(t):
        k = tt[:4] + '-' + tt[5:7]
        if k < START:
            continue
        out[k] = {'total': v[j] or 0, 'el': (v[n + j] or 0) + (v[2 * n + j] or 0)}
    save('fi', out)


# ---------- Sweden ----------
SE_MON = {'januari': 1, 'februari': 2, 'mars': 3, 'april': 4, 'maj': 5, 'juni': 6, 'juli': 7, 'augusti': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12}


def se_parse(blob):
    import openpyxl
    ws = openpyxl.load_workbook(io.BytesIO(blob), data_only=True)['LB - Vikt & Drivmedel']
    rows = list(ws.iter_rows(values_only=True))
    title = next(v for r in rows[:4] for v in r if isinstance(v, str) and 'Nyregistreringar' in v)
    m = re.search(r'Nyregistreringar (\w+) (\d{4})', title); mo, yr = SE_MON[m.group(1).lower()], int(m.group(2))
    d = {}; grp = None
    for r in rows[8:]:
        if len(r) < 12:
            continue
        if r[5]:
            grp = str(r[5])
        if not r[6] or grp is None:
            continue
        if r[6] == 'Totalt':
            break
        if 'Högst' in grp:          # vans up to 3.5 t
            continue
        heavy = 'Över' in grp
        f = 'el' if r[6] == 'EL' else ('total' if r[6] == 'Total' else None)
        if not f:
            continue
        for y, col in ((yr, 10), (yr - 1, 11)):
            e = d.setdefault(ym(y, mo), {'total': 0, 'el': 0, 'heavy_total': 0, 'heavy_el': 0})
            e[f] += r[col] or 0
            if heavy:
                e['heavy_' + f] += r[col] or 0
    return (yr, mo), d


def fetch_se():
    base = 'https://mobilitysweden.se/statistik/Nyregistreringar_per_manad_1'
    listing = get(base).decode('utf8', 'ignore')
    pages = sorted(set(re.findall(base + r'/nyregistreringar-20\d\d[^"]*', listing)))
    prev = json.load(open(os.path.join(DATA, 'se.json'))) if os.path.exists(os.path.join(DATA, 'se.json')) else {}
    own = {}   # values a month's own report gives (preferred over the next year's "same month last year" column)
    sply = {}
    for p in pages:
        y = int(re.search(r'nyregistreringar-(20\d\d)', p).group(1))
        if y < int(START[:4]):
            continue
        try:
            html = get(p).decode('utf8', 'ignore')
            x = re.search(r'/storage/[^"]+\.xlsx', html)
            if not x:
                continue
            (yr, mo), d = se_parse(get('https://mobilitysweden.se' + x.group(0)))
        except Exception as e:
            print('  se: skipped', p, e); continue
        k = ym(yr, mo)
        own[k] = d[k]
        for kk, v in d.items():
            if kk != k:
                sply[kk] = v
    out = dict(prev); out.update(sply); out.update(own)
    save('se', {k: v for k, v in out.items() if k >= START})


# ---------- Netherlands ----------
def fetch_nl():
    B = 'https://opendata.rdw.nl/resource/'
    q = lambda ds, p: json.loads(get(B + ds + '.json?' + urllib.parse.urlencode(p), timeout=180))
    rows, off = [], 0
    while True:
        r = q('m9d7-ebf2', {'$select': 'kenteken,europese_voertuigcategorie,datum_eerste_toelating,datum_eerste_tenaamstelling_in_nederland',
                            '$where': "europese_voertuigcategorie in('N2','N3') AND datum_eerste_tenaamstelling_in_nederland>='%s01'" % START.replace('-', ''),
                            '$limit': 50000, '$offset': off, '$order': 'kenteken'})
        rows += r; off += len(r)
        if len(r) < 50000:
            break
    fuel = {}
    ks = [x['kenteken'] for x in rows]
    for i in range(0, len(ks), 300):
        for x in q('8ys7-d773', {'$select': 'kenteken,brandstof_omschrijving', '$where': 'kenteken in(' + ','.join("'%s'" % k for k in ks[i:i + 300]) + ')', '$limit': 5000}):
            fuel.setdefault(x['kenteken'], set()).add(x['brandstof_omschrijving'])
    out = collections.defaultdict(lambda: {'total': 0, 'el': 0, 'heavy_total': 0, 'heavy_el': 0})
    for x in rows:
        t, a = x['datum_eerste_tenaamstelling_in_nederland'], x['datum_eerste_toelating']
        y, m = int(t[:4]), int(t[4:6]); py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
        if a < '%04d%02d01' % (py, pm):
            continue   # used import
        el = fuel.get(x['kenteken'], set()) == {'Elektriciteit'}
        e = out[ym(y, m)]; e['total'] += 1; e['el'] += el
        if x['europese_voertuigcategorie'] == 'N3':
            e['heavy_total'] += 1; e['heavy_el'] += el
    save('nl', out)


# ---------- Germany ----------
def de_parse(blob):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(blob), data_only=True)
    ws = wb[next(n for n in wb.sheetnames if n.replace(' ', '').startswith('FZ28.1'))]
    rows = [[v for v in r if v not in (None, '')] for r in ws.iter_rows(values_only=True)]
    num = lambda v: v if isinstance(v, (int, float)) else 0
    sat = [r for r in rows if r and str(r[0]).startswith('darunter Sattel')]
    if len(sat) < 2:
        return None
    # columns after the label: total, alternative total, share, electric total, share, BEV, fuel cell, PHEV, ...
    f = lambda r: {'total': int(num(r[1])), 'el': int(num(r[6]) + num(r[7]))}
    return f(sat[0]), f(sat[1])


def fetch_de():
    """KBA FZ28 'Neuzulassungen von Kraftfahrzeugen mit alternativem Antrieb' (monthly xlsx). Only the semi-tractor row
    (Sattelzugmaschinen, heavy) is used: its 'Lastkraftwagen' row includes vans up to 3.5 t. The semi-tractor row exists
    from the May 2026 file on; the latest file's year-to-date row is kept as `ytd`."""
    import datetime
    f = os.path.join(DATA, 'de.json')
    prev = json.load(open(f)) if os.path.exists(f) else {}
    out = {k: v for k, v in prev.items() if k != 'ytd'}; ytd = prev.get('ytd')
    t = datetime.date.today(); y, m = 2026, 5
    while (y, m) < (t.year, t.month):
        k = ym(y, m)
        if k not in out:
            try:
                r = de_parse(get(f'https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ28/fz28_{y}_{m:02d}.xlsx?__blob=publicationFile'))
            except Exception:
                r = None    # not published yet (KBA serves an HTML 404 page)
            if r:
                out[k] = {'heavy_total': r[0]['total'], 'heavy_el': r[0]['el']}
                ytd = {'to': k, 'heavy_total': r[1]['total'], 'heavy_el': r[1]['el']}
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    if ytd:
        out['ytd'] = ytd
    save('de', out)


# ---------- build ----------
def build():
    import datetime
    today = datetime.date.today(); cur = ym(today.year, today.month)
    meta = json.load(open(os.path.join(DATA, 'manual.json'), encoding='utf8'))
    countries = {}
    for code, info in meta['countries'].items():
        f = os.path.join(DATA, code + '.json')
        if not os.path.exists(f):
            continue
        raw = json.load(open(f)); ytd = raw.pop('ytd', None)
        rows = {k: v for k, v in raw.items() if k < cur and (v.get('total') or v.get('heavy_total'))}   # drop the running month
        countries[code] = dict(info, rows=rows, last=max(rows))
        if ytd:
            countries[code]['ytd'] = ytd
    months = sorted({k for c in countries.values() for k in c['rows']})
    out = {'built': today.isoformat(), 'months': months, 'countries': countries,
           'china': meta['china'], 'eu': meta['eu'], 'aceaQ3': meta['aceaQ3']}
    js = ('// Monthly electric-truck tracker: official monthly registrations by fuel (DK/NO/SE/FI/NL), China press readings, ACEA EU.\n'
          '// Built by scripts/ev_trucks/fetch_monthly.py - do not edit by hand.\nconst EVTM = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
    open(os.path.join(ROOT, 'assets', 'ev-trucks-monthly.js'), 'w', encoding='utf8').write(js)
    print('asset:', len(months), 'months', months[0], '..', months[-1], '|', ', '.join(f"{k} to {v['last']}" for k, v in countries.items()))


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--build' not in args:
        skip = set(args[args.index('--skip') + 1].split(',')) if '--skip' in args else set()
        for code, fn in (('de', fetch_de), ('dk', fetch_dk), ('no', fetch_no), ('fi', fetch_fi), ('se', fetch_se), ('nl', fetch_nl)):
            if code in skip:
                continue
            try:
                fn()
            except Exception as e:
                print(f'{code}: FAILED ({e}) - keeping the saved file')
    build()

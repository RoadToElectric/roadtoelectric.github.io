"""Monthly electric-truck tracker: pulls new truck registrations by fuel from official monthly sources and writes
assets/ev-trucks-monthly.js (EVTM) for the "Monthly tracker" card of ev-trucking.html.

Each row holds total/el (trucks over 3.5 t), heavy_*, van_* and bus_* where the source has them. "Heavy" is NOT the same class everywhere:
semi-tractors only in DE, DK and CH (manual.json heavyDef = tractor: shown dashed, never ranked), N3 in NL and ES, 16 t+ in SE, over 12 t in IN.

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
  Switzerland  BFS monthly SDMX (disseminate.stats.swiss, DF_IVS_0_GENERAL_M): new Lastwagen + semi-tractors by fuel; heavy = semi-tractors.
  Spain        DGT monthly registration microdata (export_mensual_mat_YYYYMM.zip): new N2/N3; heavy = N3.
  Netherlands  RDW open data (SODA m9d7-ebf2 registry + 8ys7-d773 fuel): EU category N2 (3.5-12 t) and N3 (> 12 t),
               first registration in NL in the month AND first admission no earlier than the previous month (= new,
               not a used import). Electric = only fuel "Elektriciteit". The registry only holds vehicles still
               registered, so trucks exported since are missing: older months read a little low.
India (BROWSER STEP, not downloaded by this script): the VAHAN dashboard JSON answers only from a page on its own
  origin (curl gets 401). Open https://analytics.parivahan.gov.in/analytics/publicdashboard/vahan?lang=en in a browser,
  run IN_BROWSER_JS below in the page (devtools console / javascript tool), and save the JSON string it returns as
  scripts/ev_trucks/data/monthly/in.json (replace the file: it re-pulls 2024 to today, and the live register keeps
  adding late registrations to recent months). Goods Vehicle group, sub-categories MEDIUM GOODS VEHICLE (7.5-12 t) +
  HEAVY GOODS VEHICLE (over 12 t); electric = PURE EV + ELECTRIC(BOV) + FUEL CELL HYDROGEN; heavy = HGV.
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
UA = {'User-Agent': 'Mozilla/5.0'}
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
        {"code": "OMRÅDE", "values": ["000"]}, {"code": "BILTYPE", "values": ["4000102000", "4000103000", "4000103030"]},
        {"code": "BRUG", "values": ["1000"]}, {"code": "DRIV", "values": ["20200", "20225", "20231"]}, {"code": "Tid", "values": ["*"]}]}
    txt = get('https://api.statbank.dk/v1/data', json.dumps(body).encode(), {'Content-Type': 'application/json'}).decode('utf-8-sig')
    out = collections.defaultdict(lambda: {'total': 0, 'el': 0, 'heavy_total': 0, 'heavy_el': 0})
    for line in txt.splitlines()[1:]:
        reg, typ, use, fuel, t, v = line.split(';')
        k = t[:4] + '-' + t[5:7]
        if k < START or v in ('', '..'):
            continue
        v = int(v); f = 'total' if fuel.startswith('Total') else 'el'
        if typ.startswith('Vans'):
            out[k]['van_' + f] = out[k].get('van_' + f, 0) + v; continue
        out[k][f] += v
        if typ.startswith('Road tractors'):
            out[k]['heavy_' + f] += v
    save('dk', out)


# ---------- Norway ----------
def fetch_no():
    q = {"query": [{"code": "TypeRegistrering", "selection": {"filter": "item", "values": ["N"]}},
                   {"code": "DrivstoffType", "selection": {"filter": "item", "values": ["19", "20", "21", "6"]}},
                   {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Lastebiler", "VareCampBiler", "Busser"]}},
                   {"code": "Tid", "selection": {"filter": "all", "values": ["*"]}}], "response": {"format": "json-stat2"}}
    d = json.loads(get('https://data.ssb.no/api/v0/en/table/14020', json.dumps(q).encode()))
    t = list(d['dimension']['Tid']['category']['index']); f = list(d['dimension']['DrivstoffType']['category']['index'])
    cont = list(d['dimension']['ContentsCode']['category']['index']); n, nc = len(t), len(cont); v = d['value']; out = {}
    for j, tt in enumerate(t):
        k = tt[:4] + '-' + tt[5:7]
        if k < START:
            continue
        out[k] = {}
        for c, pre in (('Lastebiler', ''), ('VareCampBiler', 'van_'), ('Busser', 'bus_')):
            vals = {ff: (v[(i * nc + cont.index(c)) * n + j] or 0) for i, ff in enumerate(f)}
            out[k][pre + 'total'] = sum(vals.values()); out[k][pre + 'el'] = vals['19']
    save('no', out)


# ---------- Finland ----------
def fetch_fi():
    q = {"query": [{"code": "Maakunta", "selection": {"filter": "item", "values": ["MA1"]}},
                   {"code": "Ajoneuvoluokka", "selection": {"filter": "item", "values": ["02", "03", "04"]}},
                   {"code": "Käyttövoima", "selection": {"filter": "item", "values": ["YH", "04", "05"]}},
                   {"code": "Kuukausi", "selection": {"filter": "all", "values": ["*"]}}], "response": {"format": "json-stat2"}}
    d = json.loads(get('https://trafi2.stat.fi/PXWeb/api/v1/en/TraFi/Ensirekisteroinnit/040_ensirek_tau_104.px', json.dumps(q).encode()))
    t = list(d['dimension']['Kuukausi']['category']['index']); n = len(t); v = d['value']; out = {}
    for j, tt in enumerate(t):
        k = tt[:4] + '-' + tt[5:7]
        if k < START:
            continue
        out[k] = {}
        for c, pre in enumerate(('van_', '', 'bus_')):      # classes 02, 03, 04; fuels total, electricity, hydrogen
            g = lambda fu: v[(c * 3 + fu) * n + j] or 0
            out[k][pre + 'total'] = g(0); out[k][pre + 'el'] = g(1) + g(2)
    save('fi', out)


# ---------- Sweden ----------
SE_MON = {'januari': 1, 'februari': 2, 'mars': 3, 'april': 4, 'maj': 5, 'juni': 6, 'juli': 7, 'augusti': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12}


def se_parse(blob):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(blob), data_only=True)
    ws = wb['LB - Vikt & Drivmedel']
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
        f = 'el' if r[6] == 'EL' else ('total' if r[6] == 'Total' else None)
        if not f:
            continue
        if 'Högst' in grp:          # vans up to 3.5 t
            for y, c in ((yr, 10), (yr - 1, 11)):
                e = d.setdefault(ym(y, mo), {'total': 0, 'el': 0, 'heavy_total': 0, 'heavy_el': 0})
                e['van_' + f] = r[c] or 0
            continue
        heavy = 'Över' in grp
        for y, col in ((yr, 10), (yr - 1, 11)):
            e = d.setdefault(ym(y, mo), {'total': 0, 'el': 0, 'heavy_total': 0, 'heavy_el': 0})
            e[f] += r[col] or 0
            if heavy:
                e['heavy_' + f] += r[col] or 0
    for e in d.values():
        e.setdefault('van_total', 0); e.setdefault('van_el', 0)
    # buses (over 3.5 t): first table of the bus sheet, down to its 'Totalt' row
    if 'Buss - Vikt & Drivmedel' in wb.sheetnames:
        br = list(wb['Buss - Vikt & Drivmedel'].iter_rows(values_only=True))
        h = next(i for i, r in enumerate(br) if any(str(x).strip() == 'Antal' for x in r if x))
        c0 = next(j for j, x in enumerate(br[h]) if x and str(x).strip() == 'Antal')
        c1 = next(j for j, x in enumerate(br[h]) if x and str(x).strip() == 'SPLY')
        cf = next(j for r in br[:h] for j, x in enumerate(r) if x == 'Drivmedel')
        bus = {c0: [0, 0], c1: [0, 0]}
        for r in br[h + 1:]:
            if r[cf] == 'Totalt':
                for c in bus:
                    bus[c][0] = r[c] or 0
                break
            if r[cf] == 'EL':
                for c in bus:
                    bus[c][1] += r[c] or 0
        for y, c in ((yr, c0), (yr - 1, c1)):
            if ym(y, mo) in d:
                d[ym(y, mo)].update(bus_total=bus[c][0], bus_el=bus[c][1])
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
    # vans (N1) and buses (M2 + M3): about 5,000 vans a month, so after the first full pull only the last three stored months on are refreshed
    from concurrent.futures import ThreadPoolExecutor
    f = os.path.join(DATA, 'nl.json'); prev = json.load(open(f)) if os.path.exists(f) else {}
    have = sorted(k for k, v in prev.items() if 'van_total' in v)
    frm = have[-3] if len(have) > 3 else START
    rows, off = [], 0
    while True:
        r = q('m9d7-ebf2', {'$select': 'kenteken,europese_voertuigcategorie,datum_eerste_toelating,datum_eerste_tenaamstelling_in_nederland',
                            '$where': "europese_voertuigcategorie in('N1','M2','M3') AND datum_eerste_tenaamstelling_in_nederland>='%s01'" % frm.replace('-', ''),
                            '$limit': 50000, '$offset': off, '$order': 'kenteken'})
        rows += r; off += len(r)
        if len(r) < 50000:
            break
    new = []
    for x in rows:
        t, a = x['datum_eerste_tenaamstelling_in_nederland'], x['datum_eerste_toelating']
        y, m = int(t[:4]), int(t[4:6]); py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
        if a >= '%04d%02d01' % (py, pm):
            new.append((x['kenteken'], ym(y, m), 'van_' if x['europese_voertuigcategorie'] == 'N1' else 'bus_'))
    fuel, ks = {}, [z[0] for z in new]

    def batch(b):
        return q('8ys7-d773', {'$select': 'kenteken,brandstof_omschrijving', '$where': 'kenteken in(' + ','.join("'%s'" % k for k in b) + ')', '$limit': 5000})
    with ThreadPoolExecutor(3) as ex:
        for res in ex.map(batch, [ks[i:i + 300] for i in range(0, len(ks), 300)]):
            for x in res:
                fuel.setdefault(x['kenteken'], set()).add(x['brandstof_omschrijving'])
    vb = collections.defaultdict(lambda: {'van_total': 0, 'van_el': 0, 'bus_total': 0, 'bus_el': 0})
    for k, mth, pre in new:
        vb[mth][pre + 'total'] += 1; vb[mth][pre + 'el'] += bool(fuel.get(k)) and fuel[k] <= {'Elektriciteit', 'Waterstof'}
    for mth in out:
        out[mth].update(vb[mth] if mth >= frm else {k: v for k, v in prev.get(mth, {}).items() if k[:4] in ('van_', 'bus_')})
    save('nl', out)


# ---------- India (run in a browser on analytics.parivahan.gov.in, see the docstring) ----------
IN_BROWSER_JS = r"""
const B='/analytics/publicdashboard/vahandashboard/durationWiseRegistrationTable?';
const M={January:1,February:2,March:3,April:4,May:5,June:6,July:7,August:8,September:9,October:10,November:11,December:12};
const EL='PURE EV,ELECTRIC(BOV),FUEL CELL HYDROGEN'; const out={}; const Y=new Date().getFullYear();
const G=[['h',{vehicleCategoryGroup:'Goods Vehicle',vehicleSubCategories:'HEAVY GOODS VEHICLE'}],['m',{vehicleCategoryGroup:'Goods Vehicle',vehicleSubCategories:'MEDIUM GOODS VEHICLE'}],
  ['v',{vehicleCategoryGroup:'Goods Vehicle',vehicleSubCategories:'LIGHT GOODS VEHICLE'}],['b',{vehicleCategoryGroup:'Bus'}]];
for (let y=2024; y<=Y; y++) for (const [key,g] of G) for (const [f,fk] of [[null,'t'],[EL,'e']]) {
  const p=Object.assign({fromYear:y,toYear:y,calendarType:3},g); if(f) p.vehicleFuels=f;
  const j=await (await fetch(B+new URLSearchParams(p))).json();
  for (const x of j){ const [yy,mn]=x.yearAsString.split('-'); const k=yy+'-'+String(M[mn]).padStart(2,'0'); (out[k]=out[k]||{})[key+fk]=x.registeredVehicleCount; } }
const res={}; Object.keys(out).sort().forEach(k=>{const v=out[k],z=c=>v[c]||0; res[k]={total:z('ht')+z('mt'),el:z('he')+z('me'),heavy_total:z('ht'),heavy_el:z('he'),van_total:z('vt'),van_el:z('ve'),bus_total:z('bt'),bus_el:z('be')};});
JSON.stringify(res)
"""


# ---------- Germany ----------
def de_parse(blob):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(blob), data_only=True)
    ws = wb[next(n for n in wb.sheetnames if n.replace(' ', '').startswith('FZ28.1'))]
    rows = [[v for v in r if v not in (None, '')] for r in ws.iter_rows(values_only=True)]
    num = lambda v: v if isinstance(v, (int, float)) else 0
    sat = [r for r in rows if r and str(r[0]).startswith('darunter Sattel')]
    # columns after the label: total, alternative total, share, electric total, share, BEV, fuel cell, PHEV, ...
    f = lambda r: {'total': int(num(r[1])), 'el': int(num(r[6]) + num(r[7]))}
    bus = [r for r in rows if r and str(r[0]) == 'Kraftomnibusse' and len(r) > 7]
    return f(sat[0]) if sat else None, f(sat[1]) if len(sat) > 1 else None, f(bus[0]) if bus else None


def fetch_de():
    """KBA FZ28 'Neuzulassungen von Kraftfahrzeugen mit alternativem Antrieb' (monthly xlsx). Only the semi-tractor row
    (Sattelzugmaschinen, heavy) is used: its 'Lastkraftwagen' row includes vans up to 3.5 t. The semi-tractor row exists
    from the May 2026 file on; the latest file's year-to-date row is kept as `ytd`."""
    import datetime
    f = os.path.join(DATA, 'de.json')
    prev = json.load(open(f)) if os.path.exists(f) else {}
    out = {k: v for k, v in prev.items() if k != 'ytd'}; ytd = prev.get('ytd')
    t = datetime.date.today(); y, m = int(START[:4]), int(START[5:])
    while (y, m) < (t.year, t.month):
        k = ym(y, m)
        if 'bus_total' not in out.get(k, {}):
            try:
                r = de_parse(get(f'https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ28/fz28_{y}_{m:02d}.xlsx?__blob=publicationFile'))
            except Exception as ex:      # not published yet (KBA serves an HTML 404 page) or unreadable
                print('  de', k, 'not read:', str(ex)[:60]); r = None
            if r:
                e = out.setdefault(k, {})
                if r[0]:
                    e.update(heavy_total=r[0]['total'], heavy_el=r[0]['el'])
                if r[1] and (not ytd or k >= ytd['to']):
                    ytd = {'to': k, 'heavy_total': r[1]['total'], 'heavy_el': r[1]['el']}
                if r[2]:
                    e.update(bus_total=r[2]['total'], bus_el=r[2]['el'])
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    if ytd:
        out['ytd'] = ytd
    save('de', out)


# ---------- Switzerland ----------
def fetch_ch():
    """BFS new registrations of road vehicles, monthly SDMX (dataflow CH1.MFZ_IVS / DF_IVS_0_GENERAL_M on
    disseminate.stats.swiss). Key = canton.owner.registration.vehicle_type.fuel.freq; N = new vehicles;
    035 Lastwagen (trucks over 3.5 t), 036 Sattelmotorfahrzeug, 038 Sattelschlepper (semi-tractors, = heavy);
    EL = battery-electric, FC = fuel cell. Figures for recent months are provisional and get small revisions."""
    import csv
    url = ('https://disseminate.stats.swiss/rest/data/CH1.MFZ_IVS,DF_IVS_0_GENERAL_M/_T._T.N.035+036+038+030+020+021+022._T+EL+FC.M'
           f'?startPeriod={START}&dimensionAtObservation=AllDimensions')
    txt = get(url, headers={'Accept': 'application/vnd.sdmx.data+csv;version=1.0.0'}).decode('utf-8-sig')
    out = collections.defaultdict(lambda: {'total': 0, 'el': 0, 'heavy_total': 0, 'heavy_el': 0})
    for x in csv.DictReader(io.StringIO(txt)):
        k, typ, fuel = x['TIME_PERIOD'], x['UV_RV_VEHICLE_GROUP_AND_TYPE'], x['UV_RV_FUEL']
        if k < START or not x['OBS_VALUE']:
            continue
        v = int(float(x['OBS_VALUE'])); f = 'total' if fuel == '_T' else 'el'
        pre = 'van_' if typ == '030' else ('bus_' if typ in ('020', '021', '022') else '')
        if pre:
            out[k][pre + f] = out[k].get(pre + f, 0) + v; continue
        out[k][f] += v
        if typ == '038':
            out[k]['heavy_' + f] += v
    save('ch', out)


# ---------- Spain ----------
ES_LEN = [8, 1, 8, 30, 22, 1, 21, 2, 1, 5, 6, 6, 6, 3, 2, 2, 2, 2, 24, 2, 2, 1, 8, 5, 8, 1, 1, 9, 3, 5, 30, 7, 3, 5, 1, 1, 1, 1, 1, 1, 11, 25, 25, 35, 70, 6, 6, 4, 4, 3, 8, 4, 4, 4, 6]


def fetch_es(start='2025-01'):
    """DGT monthly registration microdata (MATRABA, fixed width, ~17 MB zip / 130 MB text a month). Field layout:
    dgt.es .../matraba/MATRICULACIONES_MATRABA.pdf. New vehicle = IND_NUEVO_USADO (field 26) 'N'; EU category (field 48)
    N2/N3; electric = propulsion code (field 9) '2' or electric category (field 54) BEV/FCEV. Heavy = N3.
    Only months not yet in es.json are downloaded (each file is published mid-next-month)."""
    import datetime, zipfile
    off = [0]
    for n in ES_LEN:
        off.append(off[-1] + n)
    F = lambda s, i: s[off[i - 1]:off[i]].strip()
    f = os.path.join(DATA, 'es.json')
    out = json.load(open(f)) if os.path.exists(f) else {}
    t = datetime.date.today(); y, m = int(start[:4]), int(start[5:])
    while (y, m) < (t.year, t.month):
        k = ym(y, m)
        if 'van_total' not in out.get(k, {}):
            try:
                blob = get(f'https://www.dgt.es/microdatos/salida/{y}/{m}/vehiculos/matriculaciones/export_mensual_mat_{y}{m:02d}.zip', timeout=600)
                z = zipfile.ZipFile(io.BytesIO(blob))
            except Exception:
                z = None    # not published yet
            if z:
                e = {x + y_: 0 for x in ('', 'heavy_', 'van_', 'bus_') for y_ in ('total', 'el')}
                with z.open(z.namelist()[0]) as fh:
                    for line in io.TextIOWrapper(fh, encoding='latin1'):
                        cat = line[off[47]:off[48]].strip()[:2]      # N1G, N3G, M3G... = off-road versions of the same class
                        if cat not in ('N1', 'N2', 'N3', 'M2', 'M3') or F(line, 26) != 'N':
                            continue
                        el = F(line, 9) == '2' or F(line, 54) in ('BEV', 'FCEV')
                        if cat in ('N1', 'M2', 'M3'):
                            pre = 'van_' if cat == 'N1' else 'bus_'
                            e[pre + 'total'] += 1; e[pre + 'el'] += el; continue
                        e['total'] += 1; e['el'] += el
                        if cat == 'N3':
                            e['heavy_total'] += 1; e['heavy_el'] += el
                out[k] = e
                print('  es', k, e)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    save('es', out)


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
        rows = {k: v for k, v in raw.items() if k < cur and any(v.get(x) for x in ('total', 'heavy_total', 'van_total', 'bus_total'))}   # drop the running month
        for pre in info.get('hide', []):      # classes a source does not cover well enough to show (reason in manual.json)
            for v in rows.values():
                v.pop(pre + 'total', None); v.pop(pre + 'el', None)
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
        for code, fn in (('de', fetch_de), ('ch', fetch_ch), ('es', fetch_es), ('dk', fetch_dk), ('no', fetch_no), ('fi', fetch_fi), ('se', fetch_se), ('nl', fetch_nl)):
            if code in skip:
                continue
            try:
                fn()
            except Exception as e:
                print(f'{code}: FAILED ({e}) - keeping the saved file')
    build()

"""Builds the per-brand site layers of the charging map: assets/brand-sites/<slug>.js (one file per brand, loaded on demand)
and assets/charging-brand-index.js (BRAND_INDEX: brand, file, sites, ports, fast ports, countries, per-source counts).

Positions come from the best public source available for each place:
  * AFDC / NRCan station locator API (United States + Canada; public, operating stations only), cached as .scratch/chg/qc/afdc_us.json / afdc_ca.json
      curl -G "https://developer.nlr.gov/api/alt-fuel-stations/v1.json" -d api_key=DEMO_KEY -d fuel_type=ELEC -d country=US -d limit=all
  * Open Charge Map (every other country, and any US/Canada site of a brand that the AFDC feed does not list within 120 m), cached in .scratch/chg/ocm/
  * OpenStreetMap (.scratch/chg/ck/ck_osm_all.json, one Overpass query per tag, fetched by .scratch/chg/ck/osm_fetch.py) for the Circle K / Couche-Tard layer only
  * Tesla Superchargers are not here: they have their own layer (supercharge.info, exact sites and stalls).
Circle K and Couche-Tard are one company (Alimentation Couche-Tard): the layer 'Couche-Tard / Circle K' is the chargers that sit on a Circle K or Couche-Tard site, whoever runs them
(AFDC station names in any network, e.g. the IONNA hubs at Circle K; Open Charge Map operator or station names; OpenStreetMap operator / brand / name tags).
Rows: [lat, lon, ports, fast ports (>= 50 kW)]. A site found by both sources is kept once (AFDC wins in the US/Canada).
Run from the repo root after build_charging.py:  python scripts/charging/build_brand_sites.py
"""
import json, math, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import build_charging as bc  # noqa: E402
from ocm_names import name_brand  # noqa: E402
from charging_sources import COUNTRIES  # noqa: E402

CACHE = os.path.join(ROOT, '.scratch', 'chg')
OUT = os.path.join(ROOT, 'assets', 'brand-sites')
TOP_N = 200
FORCE = ['Couche-Tard / Circle K']      # small networks the map should always offer
SKIP = {bc.UNKNOWN, bc.SELF, 'Other brands', 'Other operators', 'Tesla', 'Non-Networked', 'Unknown operator'}
HOST = 'Couche-Tard / Circle K'
HOST_RX = re.compile(r'circle ?k|couche[- ]?tard', re.I)
OSM_FILE = os.path.join(CACHE, 'ck', 'ck_osm_all.json')
BBOX = {'NO': (57.9, 71.3, 4.4, 31.5), 'SE': (55.1, 69.1, 10.9, 24.2), 'DK': (54.5, 57.8, 8.0, 15.2), 'FI': (59.7, 70.1, 20.5, 31.6), 'IE': (51.3, 55.5, -10.7, -5.9), 'EE': (57.5, 59.7, 21.7, 28.2),
        'LV': (55.6, 58.1, 20.9, 28.3), 'LT': (53.9, 56.5, 20.9, 26.9), 'PL': (49.0, 54.9, 14.1, 24.2), 'DE': (47.2, 55.1, 5.8, 15.1), 'NL': (50.7, 53.6, 3.3, 7.3), 'BE': (49.5, 51.5, 2.5, 6.4),
        'GB': (49.8, 60.9, -8.7, 1.8), 'US': (24, 50, -125, -66), 'CA': (41.6, 60, -141, -52)}
EXTRA_ALIASES = [(r'couche|circle ?k', 'Couche-Tard / Circle K'), (r'^red e$|^red e ', 'Red E Charge'), (r'^evoke', 'EVoke Systems'), (r'^chargelab', 'ChargeLab')]


def brand_name(title):
    t = bc.norm(title or '')
    for rx, name in EXTRA_ALIASES:
        if re.search(rx, t):
            return name
    return bc.brand_of(title)


def slug(b):
    return re.sub(r'[^a-z0-9]+', '-', bc.norm(b)).strip('-')


class Sites:
    """sites of one brand: records within about 120 m are one site (ports added when they come from the same source)"""
    def __init__(self):
        self.cells = {}
        self.rows = []

    def key(self, lat, lon):
        return int(math.floor(lat / 0.0011)), int(math.floor(lon * max(0.2, math.cos(math.radians(lat))) / 0.0011))

    def find(self, lat, lon):
        ky, kx = self.key(lat, lon)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                i = self.cells.get((ky + dy, kx + dx))
                if i is not None:
                    return i
        return None

    def add(self, lat, lon, ports, fast, src, iso=None):
        i = self.find(lat, lon)
        if i is not None:
            r = self.rows[i]
            if r[4] == src:          # same source at the same spot (several units of one site): add the ports, keep one dot
                r[2] += max(1, int(round(ports)))
                r[3] += int(round(min(fast, max(1, ports))))
            return False             # other source: it is the same site, the first source wins
        self.cells[self.key(lat, lon)] = len(self.rows)
        self.rows.append([round(lat, 5), round(lon, 5), max(1, int(round(ports))), int(round(min(fast, max(1, ports)))), src, iso])
        return True


def load_afdc():
    """AFDC rows per brand: (lat, lon, ports, fast)"""
    out = defaultdict(list)
    for fn in ('afdc_us.json', 'afdc_ca.json'):
        for s in json.load(open(os.path.join(CACHE, 'qc', fn), encoding='utf8'))['fuel_stations']:
            if s.get('status_code') != 'E' or s.get('latitude') is None or s.get('access_code') != 'public':
                continue
            net = (s.get('ev_network') or '').replace('_', ' ')
            f = s.get('ev_dc_fast_num') or 0
            p = f + (s.get('ev_level2_evse_num') or 0) + (s.get('ev_level1_evse_num') or 0)
            bs = []
            if net and net != 'Non-Networked':
                bs.append(brand_name(net))
            if HOST_RX.search(s.get('station_name') or '') and HOST not in bs:      # a charger on a Circle K / Couche-Tard site, in whatever network
                bs.append(HOST)
            for b in bs:
                out[b].append((s['latitude'], s['longitude'], p, f, s.get('country')))
    return out


def osm_ports(tg):
    """(ports, fast ports >= 50 kW) of an OpenStreetMap charging_station: capacity tag, else the sum of the socket:* counts; outputs from socket:*:output"""
    socks, fast = 0, 0
    for k, v in tg.items():
        m = re.match(r'^socket:([a-z0-9_]+)$', k)
        if not m or not str(v).strip().isdigit():
            continue
        c = int(v); socks += c
        kw = [float(x) for x in re.findall(r'[\d.]+', (tg.get(k + ':output') or '').replace(',', '.'))]
        if kw and max(kw) >= 50:
            fast += c
    cap = str(tg.get('capacity') or '').strip()
    ports = int(cap) if cap.isdigit() and int(cap) > 0 else max(1, socks)
    return ports, min(ports, fast)


def osm_iso(lat, lon, tg, cells):
    """country of an OpenStreetMap site: addr:country tag, else the nearest Open Charge Map station within 5 km, else a bounding box"""
    c = (tg.get('addr:country') or '').upper()
    if len(c) == 2:
        return c
    best, bd = None, 0.05 ** 2
    ky, kx = int(lat * 10), int(lon * 10)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            for la, lo, iso in cells.get((ky + dy, kx + dx), ()):
                d = (la - lat) ** 2 + ((lo - lon) * math.cos(math.radians(lat))) ** 2
                if d < bd:
                    best, bd = iso, d
    if best:
        return best
    for iso, (a, b, x, y) in BBOX.items():
        if a <= lat <= b and x <= lon <= y:
            return iso
    return None


def main():
    ref = json.load(open(os.path.join(CACHE, 'refdata.json')))
    ops = {o['ID']: o['Title'] for o in ref['Operators']}
    usage = {u['ID']: u['Title'] for u in ref['UsageTypes']}
    chg = json.loads(re.search(r'const CHARGING = (\{.*\});', open(os.path.join(ROOT, 'assets', 'charging-data.js'), encoding='utf8').read(), re.S).group(1))
    # brand ranking: world ports as on the page, plus the AFDC networks of the US / Canada
    rank = defaultdict(int)
    for w in chg['worldBrands']:
        rank[brand_name(w['b'])] += sum((v[1] or 0) for v in w['c'].values())
    afdc = load_afdc()
    for b, rows in afdc.items():
        rank[b] = max(rank[b], sum(r[2] for r in rows))
    brands = [b for b, _ in sorted(rank.items(), key=lambda kv: -kv[1]) if b not in SKIP][:TOP_N]
    brands += [b for b in FORCE if b not in brands]
    want = set(brands)
    sites = {b: Sites() for b in brands}
    ctry = {b: defaultdict(int) for b in brands}
    # 1. AFDC first (US + Canada)
    for b in brands:
        for lat, lon, p, f, iso in afdc.get(b, []):
            sites[b].add(lat, lon, p, f, 'a', iso)
    # 2. Open Charge Map everywhere
    cells = defaultdict(list)
    for iso in COUNTRIES:
        f = os.path.join(CACHE, 'ocm', iso + '.json')
        if not os.path.exists(f):
            continue
        for p in json.load(open(f, encoding='utf8')):
            if p.get('StatusTypeID') in (100, 150, 200, 210) or 'Private' in usage.get(p.get('UsageTypeID'), ''):
                continue
            b = brand_name(ops.get(p.get('OperatorID')))
            if b == bc.UNKNOWN:
                b = name_brand(iso, p.get('ID')) or b
            ai = p.get('AddressInfo') or {}
            if ai.get('Latitude') is None or ai.get('Longitude') is None:
                continue
            cells[(int(ai['Latitude'] * 10), int(ai['Longitude'] * 10))].append((ai['Latitude'], ai['Longitude'], iso))
            bs = [b] if b in want else []
            if HOST in want and HOST not in bs and HOST_RX.search(' '.join(str(x or '') for x in (ops.get(p.get('OperatorID')), ai.get('Title'), ai.get('AddressLine1'), ai.get('RelatedURL')))):
                bs.append(HOST)                                  # a charger on a Circle K / Couche-Tard site run by someone else
            if not bs:
                continue
            conns = p.get('Connections') or []
            q = sum((c.get('Quantity') or 1) for c in conns) or 1
            n = p.get('NumberOfPoints') or q
            fast = sum((c.get('Quantity') or 1) for c in conns if (c.get('PowerKW') or 0) >= 50) * n / q
            for b in bs:
                sites[b].add(ai['Latitude'], ai['Longitude'], n, fast, 'o', iso)
    # 3. OpenStreetMap: Circle K / Couche-Tard sites only (operator, brand, name, description or network tag)
    if HOST in want and os.path.exists(OSM_FILE):
        for e in json.load(open(OSM_FILE, encoding='utf8')):
            lat, lon = (e.get('lat'), e.get('lon')) if e['type'] == 'node' else (e['center']['lat'], e['center']['lon'])
            tg = e.get('tags') or {}
            if tg.get('access') in ('private', 'no', 'customers'):
                continue
            ports, fast = osm_ports(tg)
            sites[HOST].add(lat, lon, ports, fast, 'm', osm_iso(lat, lon, tg, cells))
    os.makedirs(OUT, exist_ok=True)
    for fn in os.listdir(OUT):
        os.remove(os.path.join(OUT, fn))
    index = []
    for b in brands:
        rows = sites[b].rows
        if not rows:
            continue
        rows.sort(key=lambda r: (r[0], r[1]))
        n_a = sum(1 for r in rows if r[4] == 'a')
        n_m = sum(1 for r in rows if r[4] == 'm')
        data = [r[:4] for r in rows]
        sl = slug(b)
        open(os.path.join(OUT, sl + '.js'), 'w', encoding='utf8').write(
            '(window.BRAND_SITES = window.BRAND_SITES || {})[%s] = %s;\n' % (json.dumps(b, ensure_ascii=False), json.dumps(data, separators=(',', ':'))))
        index.append({'b': b, 'f': sl, 'n': len(rows), 'p': sum(r[2] for r in rows), 'fp': sum(r[3] for r in rows), 'a': n_a, 'o': len(rows) - n_a - n_m, 'm': n_m,
                      'rep': round(rank[b]), 'c': dict(sorted(Counter(r[5] for r in rows if r[5]).items(), key=lambda kv: -kv[1]))})
    open(os.path.join(ROOT, 'assets', 'charging-brand-index.js'), 'w', encoding='utf8').write(
        '// Brands with a site layer on the charging map (assets/brand-sites/<f>.js): n sites, p ports, fp fast ports (50+ kW), a = sites from AFDC, o = from Open Charge Map, m = from OpenStreetMap (Circle K / Couche-Tard only), rep = ports reported for the brand on this page\n'
        'const BRAND_INDEX = ' + json.dumps(index, ensure_ascii=False, separators=(',', ':')) + ';\n')
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(len(index), 'brands,', sum(i['n'] for i in index), 'sites,', tot // 1024, 'KB')
    for i in index[:60]:
        print('%-34s sites %6d ports %7d (afdc %6d, ocm %6d, osm %5d) reported %7d  cov %3d%%' % (i['b'], i['n'], i['p'], i['a'], i['o'], i.get('m', 0), i['rep'], 100 * i['p'] / max(1, i['rep'])))


if __name__ == '__main__':
    main()

"""Reads the NOBIL data dumps (.scratch/chg/nobil/<NOR|SWE>.json, fetched by fetch_nobil.py): the Nordic register of charging stations, licence CC BY 4.0 (attribution: NOBIL.no).
One record per station; each connector entry of a station is one charging point (port).  A station is kept when it is existing (Station_status 1) and open to the public
('Public', or 'Visitors' = customers of a shop / hotel; 'Employees', 'Residents' and 'By appointment' are left out); a point is kept when its energy carrier is electricity
and it is not for boats.  Power comes from the "Charging capacity" text ("22 kW - 400V 3-phase max 32A", "150 kW DC", "7,4 kW - 230V ...")."""
import html, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DIR = os.path.join(ROOT, '.scratch', 'chg', 'nobil')
OPEN_TO = ('Public', 'Visitors')
_KW = re.compile(r'(\d+(?:[.,]\d+)?)\s*kw', re.I)


def kw_of(txt):
    m = _KW.search(txt or '')
    return float(m.group(1).replace(',', '.')) if m else None


def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(s or '')).strip()


def stations(code):
    """[{id, name, lat, lon, op, owner, kw: [kW or None per point]}] for the public stations of one country (NOR, SWE), None if the dump is missing"""
    f = os.path.join(DIR, code + '.json')
    if not os.path.exists(f):
        return None
    out = []
    for s in json.load(open(f, encoding='utf-8'))['chargerstations']:
        m = s['csmd']
        if m.get('Station_status') != 1 or (s['attr']['st'].get('2') or {}).get('trans') not in OPEN_TO:
            continue
        kws = []
        for c in s['attr']['conn'].values():
            if (c.get('26') or {}).get('trans', 'Electricity') != 'Electricity' or 'boat' in ((c.get('17') or {}).get('trans') or '').lower():
                continue
            kws.append(kw_of((c.get('5') or {}).get('trans')))
        if not kws:
            continue
        try:
            lat, lon = (float(x) for x in re.findall(r'-?\d+\.?\d*', m['Position'])[:2])
        except Exception:
            continue
        out.append({'id': m['id'], 'name': clean(m.get('name')), 'lat': lat, 'lon': lon, 'op': clean(m.get('Operator')) or clean(m.get('Owned_by')), 'owner': clean(m.get('Owned_by')),
                    'addr': clean(' '.join(str(m.get(k) or '') for k in ('Street', 'Description_of_location'))), 'kw': kws})
    return out

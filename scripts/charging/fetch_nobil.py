"""Downloads the NOBIL (nobil.no, Nordic charging-station register, CC BY 4.0) full data dump per country into .scratch/chg/nobil/<CODE>.json.
The API key is read from .scratch/chg/nobil.key (git-ignored, one line) and is only sent to nobil.no.
usage (repo root): python -I scripts/charging/fetch_nobil.py [NOR SWE DNK FIN ISL]"""
import json, os, sys, time, urllib.parse, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
KEYFILE = os.path.join(ROOT, '.scratch', 'chg', 'nobil.key')
OUT = os.path.join(ROOT, '.scratch', 'chg', 'nobil')


def fetch(code, key):
    url = 'https://nobil.no/api/server/datadump.php?' + urllib.parse.urlencode({'apikey': key, 'countrycode': code, 'format': 'json', 'file': 'false'})
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 RoadToElectric/1.0'})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main():
    key = open(KEYFILE, encoding='utf-8').read().strip()
    os.makedirs(OUT, exist_ok=True)
    for code in (sys.argv[1:] or ['NOR', 'SWE', 'DNK', 'FIN', 'ISL']):
        try:
            raw = fetch(code, key)
        except Exception as e:
            print(code, 'failed:', str(e).replace(key, '***')[:200])
            continue
        try:
            d = json.loads(raw)
        except Exception:
            print(code, 'not JSON:', raw[:200].decode('utf-8', 'replace').replace(key, '***'))
            continue
        n = len(d.get('chargerstations') or [])
        open(os.path.join(OUT, code + '.json'), 'wb').write(raw)
        print(code, len(raw) // 1024, 'KB', n, 'stations')
        time.sleep(1)


if __name__ == '__main__':
    main()

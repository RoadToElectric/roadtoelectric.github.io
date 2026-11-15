"""Pulls the EEA new-car CO2 data (2025 provisional) aggregated per make + commercial name, through the discodata SQL endpoint.
POST form only: GET requests with bracketed column names are refused by the EEA firewall. Row-level sanity filters drop registry typos.
usage: python -I scripts/gas_elec/src/europe/eea_pull.py"""
import json, os, urllib.request, urllib.parse, sys
T = '[CO2Emission].[latest].[co2cars_2025Pv31]'
Q = {
 'ev':  f"SELECT Mk AS mk, Cn AS cn, COUNT(*) AS n, AVG(CAST([Z (Wh/km)] AS FLOAT)) AS z, AVG(CAST([Ep (KW)] AS FLOAT)) AS kw FROM {T} WHERE Ft = 'electric' AND [Z (Wh/km)] BETWEEN 100 AND 320 GROUP BY Mk, Cn HAVING COUNT(*) >= 100 ORDER BY n DESC",
 'gas': f"SELECT Mk AS mk, Cn AS cn, Fm AS fm, COUNT(*) AS n, AVG(CAST(Fc AS FLOAT)) AS fc, AVG(CAST([Ec (cm3)] AS FLOAT)) AS cc FROM {T} WHERE Ft = 'petrol' AND Fc BETWEEN 3 AND 20 GROUP BY Mk, Cn, Fm HAVING COUNT(*) >= 200 ORDER BY n DESC",
 'tot': f"SELECT Ft AS ft, Fm AS fm, COUNT(*) AS n FROM {T} GROUP BY Ft, Fm ORDER BY n DESC",
}
for k, q in Q.items():
    out, p = [], 1
    while True:
        req = urllib.request.Request('https://discodata.eea.europa.eu/sql', data=urllib.parse.urlencode({'query': q, 'p': p, 'nrOfHits': 1000}).encode(),
                                     headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'})
        r = json.loads(urllib.request.urlopen(req, timeout=600).read())
        if 'results' not in r: print(k, r); break
        out += r['results']
        if len(r['results']) < 1000: break
        p += 1
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'eea_2025_{k}.json'), 'w'), ensure_ascii=False)
    print(k, len(out), out[:3])

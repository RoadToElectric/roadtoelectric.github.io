"""Bridge 2026: the Energy Institute (our base of sections 1-3 and 6-9) publishes once a year (June); its 2026 numbers come in June 2027. Until then 2026 is taken from the
IEA Oil Market Reports and CONVERTED to the Energy Institute basis by the ratio of the two sources in 2025 (the last year both exist).

 * World oil demand 2026 (sections 1-4): IEA October 2026 report (14 Oct 2026, summary page): 2026 = 102.4 mb/d, -2.6 mb/d y-o-y  ->  EI-basis 2026 = EI 2025 x 102.4 / 105.0.
   The split by purpose keeps the shares of the previous 2026 estimate (the cut is shared in proportion). The previous (pre-war) 2026 split is kept as `wi2026` for the what-if section,
   which must start from a normal year, not from the Hormuz-crisis year.
 * Oil produced by country (sections 6-7): January-June 2026 average = (1Q26 from the May report + 2Q26 from the July report) / 2, per country, times the country's own EI/IEA ratio of 2025.
   World = EI 2025 world x (IEA crude + NGL supply H1 2026 / 2025). Countries the IEA does not list stay at 2025. Run after build_world_oil.py (it edits assets/world-oil-data.js in place; idempotent).
Inputs: the two PDFs in .scratch/oil/omr (free from iea.org; editions older than about 3 months are open) and the numbers typed below."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from omr_tables import read_table

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OMR = os.path.join(ROOT, '.scratch', 'oil', 'omr')
MAY, JUL = os.path.join(OMR, 'omr_2026-05.pdf'), os.path.join(OMR, 'omr_2026-07.pdf')
P_ASSET = os.path.join(ROOT, 'assets', 'world-oil-data.js')

# IEA October 2026 report, summary page (https://www.iea.org/reports/oil-market-report-october-2026): demand 2026 = 102.4 mb/d after a 2.6 mb/d fall -> 2025 = 105.0
IEA_DEM_2025, IEA_DEM_2026 = 105.0, 102.4
# IEA supply for H1 2026 (crude + NGL + other, i.e. total supply minus biofuels and processing gains) and for 2025: Table 1 of the May (1Q26) and July (2Q26, 2025) reports
IEA_SUP = {'2025': 106.25 - 3.35 - 2.43, '1Q26': 103.6 - 3.1 - 2.4, '2Q26': 96.24 - 3.60 - 2.26}
IEA_SUP['H1'] = (IEA_SUP['1Q26'] + IEA_SUP['2Q26']) / 2

NAME = {'Saudi Arabia': 'Saudi Arabia', 'Iran': 'Iran', 'Iraq': 'Iraq', 'Kuwait': 'Kuwait', 'Nigeria': 'Nigeria', 'Libya': 'Libya', 'Algeria': 'Algeria', 'Congo': 'Congo', 'Gabon': 'Gabon',
        'Equatorial Guinea': 'Equatorial Guinea', 'Venezuela': 'Venezuela', 'United States': 'United States', 'Mexico': 'Mexico', 'Canada': 'Canada', 'UK': 'United Kingdom', 'Norway': 'Norway',
        'Australia': 'Australia', 'Russia': 'Russia (USSR before 1985)', 'Azerbaijan': 'Azerbaijan', 'Kazakhstan': 'Kazakhstan', 'China': 'China', 'Malaysia': 'Malaysia', 'India': 'India',
        'Indonesia': 'Indonesia', 'Brazil': 'Brazil', 'Argentina': 'Argentina', 'Colombia': 'Colombia', 'Ecuador': 'Ecuador', 'Oman': 'Oman', 'Qatar': 'Qatar', 'UAE': 'United Arab Emirates',
        'Angola': 'Angola', 'Egypt': 'Egypt'}


def bridge():
    may = read_table(MAY, 76)                            # Table 3 only: 3a / 3b repeat country names on other bases (OECD detail, OPEC+ crude)
    jul = read_table(JUL, 68)
    s = open(P_ASSET, encoding='utf-8').read()
    m = re.search(r'^(.*?const WORLD_OIL = )(\{.*\});(\s*)$', s, re.S)
    d = json.loads(m.group(2))
    PY = d['prodYears']; i25 = PY.index(2025)
    rows, ratios = {}, {}
    for k, ours in NAME.items():
        c = d['countries'].get(ours)
        if not c:
            print('not in our countries:', ours); continue
        mv, jv = may.get(k, {}), jul.get(k, {})
        iea25 = jv.get('2025') if jv.get('2025') is not None else mv.get('2025')
        q1, q2 = mv.get('1Q26'), jv.get('2Q26')
        if k == 'UAE':                                   # crude only in May (OPEC), all liquids in July (non-OPEC from 1 May): bring 1Q26 to the July basis with the 2025 ratio
            q1 = q1 * jv['2025'] / mv['2025'] if q1 and mv.get('2025') else None
        if iea25 and q1 is not None and q2 is not None:
            h1 = (q1 + q2) / 2
            rows[ours] = (c['mbd'][i25], iea25, h1, c['mbd'][i25] * h1 / iea25)
    return d, m, rows


def main():
    d, m, rows = bridge()
    PY = d['prodYears']; i25 = PY.index(2025)
    print(f"{'country':28s} {'EI 2025':>8s} {'IEA 2025':>9s} {'IEA H1-26':>10s} {'EI-basis H1-26':>15s}")
    for n, (e, i, h, v) in sorted(rows.items(), key=lambda kv: -kv[1][0]):
        print(f'{n:28s} {e:8.2f} {i:9.2f} {h:10.2f} {v:15.2f}')
    # ---- world production, EI basis
    w25 = d['worldProd'][i25]; w26 = w25 * IEA_SUP['H1'] / IEA_SUP['2025']
    c26 = {n: (rows[n][3] if n in rows else c['mbd'][i25]) for n, c in d['countries'].items()}
    print('world prod EI 2025 %.3f -> H1-2026 %.3f (IEA supply ratio %.4f); sum of countries %.3f' % (w25, w26, IEA_SUP['H1'] / IEA_SUP['2025'], sum(c26.values())))
    # ---- world demand 2026 (full-year IEA forecast), EI basis
    Y = d['years']; i25y, i26 = Y.index(2025), Y.index(2026)
    if 'wi2026' not in d:                                # keep the pre-war 2026 once: the what-if section starts from a normal year
        d['wi2026'] = {'total': d['total'][i26], **{k: v[i26] for k, v in d['use'].items()}}
    f = (d['total'][i25y] * IEA_DEM_2026 / IEA_DEM_2025) / d['wi2026']['total']
    d['total'][i26] = round(d['wi2026']['total'] * f, 3)
    for k in d['use']:
        d['use'][k][i26] = round(d['wi2026'][k] * f, 3)
    print('world demand 2026 EI basis: %.3f (was %.3f), EI 2025 %.3f' % (d['total'][i26], d['wi2026']['total'], d['total'][i25y]))
    # ---- production 2026 (H1) appended to prodYears / countries / worldProd
    if PY[-1] != 2026:
        PY.append(2026)
        for n, c in d['countries'].items():
            c['mbd'].append(0)
        d['worldProd'].append(0)
    for n, c in d['countries'].items():
        c['mbd'][-1] = round(c26[n], 3)
    d['worldProd'][-1] = round(w26, 3)
    d['bridge'] = {'prodLabel': 'January-June 2026 average', 'prodSource': 'IEA Oil Market Reports May 2026 (1Q26) and July 2026 (2Q26), converted to the Energy Institute basis by each country\'s own 2025 ratio',
                   'demandSource': 'IEA Oil Market Report October 2026: 2026 demand 102.4 mb/d (-2.6 mb/d), converted by EI 2025 / IEA 2025 (105.0)', 'ieaDemand': [IEA_DEM_2025, IEA_DEM_2026]}
    if '--apply' in sys.argv:
        open(P_ASSET, 'w', encoding='utf-8', newline='').write(m.group(1) + json.dumps(d, separators=(',', ':'), ensure_ascii=False) + ';' + m.group(3))
        print('written', P_ASSET)
    else:
        print('(dry run, add --apply)')


if __name__ == '__main__':
    main()

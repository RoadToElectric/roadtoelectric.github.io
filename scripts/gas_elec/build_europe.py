"""Europe data for the EV vs ICE cost comparator (ev-vs-ice-cost.html), built 2026-11-15.

Inputs (scripts/gas_elec/src/europe/):
  eurostat_nrg_pc_204_2025S1-2026S1.json   Eurostat nrg_pc_204, household electricity, 2,500-4,999 kWh/yr band, all taxes and levies, EUR/kWh.
                                           2026-S1 used (2025-S2 if a country has no 2026-S1). API:
                                           https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_204?format=JSON&unit=KWH&currency=EUR&tax=I_TAX&nrg_cons=KWH2500-4999&sinceTimePeriod=2025-S1
  national_electricity.json                UK (Ofgem cap), Switzerland (ElCom), Ukraine (regulated tariff): not in Eurostat
  oil_bulletin_euro95_with_taxes_2026.csv  EU Weekly Oil Bulletin, Euro-super 95 with taxes, EUR per 1,000 L, every week of 2026 (EU27)
  gpp_gasoline_2026-11-09.json (+ _extra)  globalpetrolprices.com, Octane-95, USD/L, one reading 9 Nov 2026 - only for countries outside the EU
  boc_fx*_2026.json                        Bank of Canada daily FX (EUR, GBP, CHF and USD against CAD)
  eea_2025_ev.json / eea_2025_gas.json     EEA CO2 monitoring of new cars, 2025 provisional (table co2cars_2025Pv31, EU27 + Iceland + Norway),
                                           aggregated by eea_pull.py: per make + commercial name, registrations and average WLTP consumption
                                           (electric: Wh/km at the plug; petrol: L/100 km, mono-fuel and hybrid separately). EVs with 100+ and
                                           petrol versions with 200+ registrations.

Gasoline outside the EU: the globalpetrolprices reading is converted to EUR at the 9 Nov 2026 rate, then scaled
  (1) to the 2026 average: x (EU average Jan-Nov 2026 / EU price on 9 Nov 2026), and
  (2) to the Oil Bulletin's level: x median over EU countries of (Oil Bulletin 9 Nov / globalpetrolprices 9 Nov in EUR), because that site
      reads ~10% above the official bulletin for the same EU countries and week.
Liechtenstein uses the Swiss gasoline price (same market). Kosovo: no gasoline price found.

usage (repo root): python -I scripts/gas_elec/build_europe.py  -> assets/europe-cost-data.js
"""
import csv, datetime, json, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src', 'europe')
ROOT = os.path.dirname(os.path.dirname(HERE))
J = lambda f: json.load(open(os.path.join(SRC, f), encoding='utf-8'))

NAMES = {'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia', 'CY': 'Cyprus', 'CZ': 'Czechia', 'DK': 'Denmark', 'EE': 'Estonia',
         'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'EL': 'Greece', 'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia',
         'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania',
         'SK': 'Slovakia', 'SI': 'Slovenia', 'ES': 'Spain', 'SE': 'Sweden',
         'IS': 'Iceland', 'LI': 'Liechtenstein', 'NO': 'Norway', 'CH': 'Switzerland', 'UK': 'United Kingdom', 'AL': 'Albania',
         'BA': 'Bosnia and Herzegovina', 'GE': 'Georgia', 'XK': 'Kosovo', 'MD': 'Moldova', 'ME': 'Montenegro', 'MK': 'North Macedonia',
         'RS': 'Serbia', 'TR': 'Türkiye', 'UA': 'Ukraine'}
EU27 = set(list(NAMES)[:27])
WOB = {'EL': 'GR'}                                         # Oil Bulletin code where it differs from Eurostat's
GPP = {'IS': 'Iceland', 'NO': 'Norway', 'CH': 'Switzerland', 'UK': 'United-Kingdom', 'AL': 'Albania', 'BA': 'Bosnia-and-Herzegovina',
       'MD': 'Moldova', 'ME': 'Montenegro', 'MK': 'Macedonia', 'RS': 'Serbia', 'TR': 'Turkey', 'UA': 'Ukraine'}

# ---------- FX ----------
def fx(f, k):
    o = J(f)['observations']
    return {x['d']: float(x[k]['v']) for x in o}
eurcad, usdcad = fx('boc_fxeurcad_2026.json', 'FXEURCAD'), fx('../boc_fxusdcad_2026.json', 'FXUSDCAD')
gbpcad, chfcad = fx('boc_fxgbpcad_2026.json', 'FXGBPCAD'), fx('boc_fxchfcad_2026.json', 'FXCHFCAD')
avg = lambda d: sum(d.values()) / len(d)
EUR_PER = {'EUR': 1, 'GBP': avg(gbpcad) / avg(eurcad), 'CHF': avg(chfcad) / avg(eurcad)}
EURUSD_NOV9 = eurcad['2026-11-09'] / usdcad['2026-11-09']          # USD per EUR on the day of the globalpetrolprices reading

# ---------- electricity ----------
es = J('eurostat_nrg_pc_204_2025S1-2026S1.json')
gidx, tidx = es['dimension']['geo']['category']['index'], es['dimension']['time']['category']['index']
nt = len(tidx)
elec = {}
for g, i in gidx.items():
    if g not in NAMES:
        continue
    for per in ('2026-S1', '2025-S2'):
        v = es['value'].get(str(i * nt + tidx[per]))
        if v is not None:
            elec[g] = (v, 'eurostat', per); break
nat = J('national_electricity.json')
for g in ('UK', 'CH', 'UA'):
    n = nat[g]
    eur = n['v'] / nat['UAH_per_EUR_2026'] if n['cur'] == 'UAH' else n['v'] * EUR_PER[n['cur']]
    elec[g] = (round(eur, 4), 'national', n['src'])

# ---------- gasoline ----------
wob = list(csv.DictReader(open(os.path.join(SRC, 'oil_bulletin_euro95_with_taxes_2026.csv'), encoding='utf-8')))
wob_avg = {c: sum(float(r[c]) for r in wob if r[c]) / sum(1 for r in wob if r[c]) / 1000 for c in wob[0] if c != 'date' and any(r[c] for r in wob)}
nov9 = next(r for r in wob if r['date'] == '2026-11-09')
WOB_PERIOD = '%s to %s' % (min(r['date'] for r in wob), max(r['date'] for r in wob))
gpp = J('gpp_gasoline_2026-11-09.json')['prices']
gpp.update({'Georgia': J('gpp_gasoline_extra.json')['GE']['usd_per_l']})
GPP['GE'] = 'Georgia'
EUGPP = {'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia', 'CY': 'Cyprus', 'CZ': 'Czech-Republic', 'DK': 'Denmark', 'EE': 'Estonia',
         'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'EL': 'Greece', 'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'LV': 'Latvia',
         'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania',
         'SK': 'Slovakia', 'SI': 'Slovenia', 'ES': 'Spain', 'SE': 'Sweden'}
# Non-EU countries: every 2026 archived copy of globalpetrolprices' Europe page (gpp_gasoline_2026_readings.json) + the live 9 Nov reading.
# For each reading date t: price in EUR at that day's rate; k_t = median over the EU countries of (Oil Bulletin week of t / reading),
# which puts that reading on the bulletin's level; the country's level relative to the EU average that week = reading x k_t / bulletin EU(t).
# The 2026 price = mean of those relative levels x the bulletin's EU 2026 average. Readings are sparse (8), so relative levels are used
# rather than plain averages: they cancel the timing of the readings (a country missing from early copies is not biased by the season).
GPP_R = J('gpp_gasoline_2026_readings.json')['readings']
GPP_R.setdefault('2026-11-09', {})['Georgia'] = J('gpp_gasoline_extra.json')['GE']['usd_per_l']
GPP['GE'] = 'Georgia'
def on_or_before(series, d):
    ks = sorted(k for k in series if k <= d)
    return series[ks[-1]] if ks else series[min(series)]
def eur_per_usd(d):
    return on_or_before(usdcad, d) / on_or_before(eurcad, d)
def wob_week(d):
    return min(wob, key=lambda r: abs((datetime.date.fromisoformat(r['date']) - datetime.date.fromisoformat(d)).days))
rel, kt = {}, {}
for d, rd in GPP_R.items():
    w, e = wob_week(d), eur_per_usd(d)
    pairs = [(float(w[WOB.get(c, c)]) / 1000, rd[n] * e) for c, n in EUGPP.items() if n in rd and w.get(WOB.get(c, c))]
    k = statistics.median(a / b for a, b in pairs)
    kt[d] = k
    eu_t = float(w['EU']) / 1000
    for n, v in rd.items():
        rel.setdefault(n, []).append(v * e * k / eu_t)
gpp_year = {n: statistics.mean(v) * wob_avg['EU'] for n, v in rel.items()}
chk = sorted((gpp_year[n] / wob_avg[WOB.get(c, c)] - 1, c) for c, n in EUGPP.items() if n in gpp_year)
GPP_CHECK = max(abs(x) for x, _ in chk)
print('globalpetrolprices: %d readings %s..%s, k_t %s' % (len(GPP_R), min(GPP_R), max(GPP_R), ' '.join('%.3f' % k for k in kt.values())))
print('  check on the 27 EU countries (method vs Oil Bulletin 2026 average): median abs %.1f%%, max %.1f%% (%s)' %
      (100 * statistics.median(abs(x) for x, _ in chk), 100 * GPP_CHECK, max(chk, key=lambda z: abs(z[0]))[1]))
gas = {}
for c in NAMES:
    if c in EU27:
        gas[c] = (round(wob_avg[WOB.get(c, c)], 4), 'wob')
    elif c in GPP and GPP[c] in gpp_year:
        gas[c] = (round(gpp_year[GPP[c]], 4), 'gpp')
gas['LI'] = (gas['CH'][0], 'gpp-ch')
GPP_N = {c: len(rel[GPP[c]]) for c in GPP if GPP[c] in rel}

rows = []
for c, n in NAMES.items():
    e = elec.get(c)
    g = gas.get(c)
    rows.append({'id': 'EU-' + c, 'c': 'EU', 'ab': c, 'n': n, 'cur': 'EUR',
                 'e': e[0] if e else None, 'es': e[1] if e else None, 'ep': e[2] if e else None,
                 'g': g[0] if g else None, 'gs': g[1] if g else None, 'eu27': c in EU27})

# ---------- car lists (EEA, WLTP) ----------
MAKE = {'MERCEDES-BENZ': 'Mercedes-Benz', 'MERCEDES BENZ': 'Mercedes-Benz', 'ROLLS-ROYCE': 'Rolls-Royce', 'ALFA ROMEO': 'Alfa Romeo', 'LAND ROVER': 'Land Rover',
        'LYNK & CO': 'Lynk & Co', 'XPENG': 'XPeng', 'LEAPMOTOR': 'Leapmotor', 'DS': 'DS', 'BMW': 'BMW', 'BYD': 'BYD', 'MG': 'MG', 'KGM': 'KGM', 'GWM': 'GWM',
        'NIO': 'NIO', 'MINI': 'Mini', 'SEAT': 'SEAT', 'SKODA': 'Škoda', 'CITROEN': 'Citroën', 'CUPRA': 'Cupra', 'JAECOO': 'Jaecoo', 'OMODA': 'Omoda',
        'BMW I': 'BMW', 'VW': 'Volkswagen', 'DONGFENG': 'Dongfeng', 'DONG FENG': 'Dongfeng', 'DS AUTOMOBILES': 'DS', 'GREAT WALL MOTOR CO. LTD.': 'GWM',
        'GREAT WALL': 'GWM', 'HYUNDAI, GENESIS': 'Genesis', 'GENESIS': 'Genesis', 'KG MOBILITY': 'KGM', 'SSANGYONG': 'KGM', 'LYNK&CO': 'Lynk & Co',
        'VOLKSWAGEN, VW': 'Volkswagen', 'DFSK': 'DFSK', 'FAW': 'FAW', 'JAC': 'JAC', 'LUCID MOTORS': 'Lucid', 'LUCID': 'Lucid', 'VINFAST': 'VinFast',
        'AUTOMOBILI LAMBORGHINI': 'Lamborghini', 'MERCEDES-AMG': 'Mercedes-Benz', 'MG- ROEWE': 'MG', 'MG-ROEWE': 'MG', 'OPEL - VAUXHALL': 'Opel',
        'VOLKSWAGEN VW': 'Volkswagen', 'VOLKSWAGEN-VW': 'Volkswagen', 'CHERY-EBRO': 'Ebro', 'BAIC': 'BAIC', 'SWM': 'SWM'}
KEEP_UP = {'ID', 'GT', 'GTI', 'GTE', 'GTS', 'GTX', 'RS', 'SUV', 'EV', 'AMG', 'EQ', 'II', 'III', 'IV', 'XL', 'LR', 'SR', 'AWD', 'RWD', 'FWD', 'TFSI', 'TSI',
           'HEV', 'MHEV', 'PHEV', 'DM', 'DM-I', 'ST', 'GR', 'BEV', 'SE', 'LX', 'GS', 'EX', 'UX', 'NX', 'RX', 'RZ', 'LBX', 'ES', 'CX', 'MX', 'HR-V', 'ZR-V',
           'CR-V', 'BZ', 'BZ4X', 'C-HR', 'T-ROC', 'T-CROSS', 'E-208', 'E-2008', 'XC40', 'EX30', 'EX40', 'EC40', 'MG4', 'MG5', 'ZS', 'HS', 'EZS', 'DS', 'XEV'}
def title(s):
    out = []
    for w in s.replace('"', '').split():
        if any(ch.isdigit() for ch in w) or w in KEEP_UP or (w.endswith('.') and len(w) <= 3) or (len(w) <= 2 and w.isalpha() and w not in ('DE', 'LA', 'LE', 'DI')):
            out.append(w)
        else:
            out.append('-'.join(p[:1] + p[1:].lower() for p in w.split('-')))
    return ' '.join(out)
def mk_name(mk):
    mk = re.sub(r'\s+', ' ', mk.strip().upper())
    return MAKE.get(mk, title(mk))
def clean_model(mk, cn):
    m = re.sub(r'\s+', ' ', (cn or '').replace('"', '').strip().upper())
    m = re.sub(r'(\d)\s*KW\b', r'\1 KW', m)                      # "250KW" and "250 KW" are one version
    for pre in {mk.upper(), mk.upper().replace('-', ' '), mk_name(mk).upper()}:
        if m.startswith(pre + ' '):
            m = m[len(pre) + 1:]
    m = re.sub(r'\bE[- ]?TECH ELECTRIC\b', 'E-TECH ELECTRIC', m)
    return title(m) if m else '?'
def merge(items, key, valk):
    out = {}
    for it in items:
        k = key(it)
        o = out.setdefault(k, {'n': 0, 'sum': 0.0})
        o['n'] += it['n']; o['sum'] += it[valk] * it['n']
    return out

# registry rows with an implausible value (e.g. "RENAULT 5" at 388 Wh/km: a petrol figure or a typo) are dropped:
# EVs outside 100-320 Wh/km, petrol cars outside 3-20 L/100 km
evraw = J("eea_2025_ev.json")          # rows already filtered to 100-320 Wh/km in eea_pull.py
# commercial names cut short in the registry ("4 E-TECH ELECTRI") are folded into the full name of the same make
full = {}
for r in evraw:
    full.setdefault(mk_name(r['mk']), set()).add(clean_model(r['mk'], r['cn']))
def unclip(mk, md):
    longer = [x for x in full[mk] if x != md and x.startswith(md) and len(x) - len(md) <= 3 and x[len(md)] != ' ']   # a cut word, not a shorter name
    return max(longer, key=len) if longer else md
ev = merge(evraw, lambda r: (mk_name(r['mk']), unclip(mk_name(r['mk']), clean_model(r['mk'], r['cn']))), 'z')
ev_list = sorted([[mk, md, round(o['sum'] / o['n'] / 10, 1), o['n']] for (mk, md), o in ev.items() if o['n'] >= 100],
                 key=lambda e: (e[0].lower(), e[1].lower()))
# a small entry far above its brand's median is a mislabelled one ("Renault 5" at 31 kWh/100 km next to "5 E-Tech Electric" at 14.9)
med = {mk: statistics.median(e[2] for e in ev_list if e[0] == mk) for mk in {e[0] for e in ev_list}}
ev_list = [e for e in ev_list if not (e[2] > 1.7 * med[e[0]] and e[3] < 2000)]
gs = merge([r for r in J('eea_2025_gas.json') if 3 <= r['fc'] <= 20], lambda r: (mk_name(r['mk']), clean_model(r['mk'], r['cn']), 1 if r['fm'] == 'H' else 0), 'fc')
gas_list = sorted([[mk, md, round(o['sum'] / o['n'], 1), o['n'], h] for (mk, md, h), o in gs.items() if o['n'] >= 200],
                  key=lambda e: (e[0].lower(), e[1].lower(), e[4]))
tot = J('eea_2025_tot.json')
reg_ev = sum(t['n'] for t in tot if t['ft'] == 'electric')
cover_ev = sum(e[3] for e in ev_list) / reg_ev

data = {'built': '2026-11-15', 'eurPerUsd': round(1 / (avg(eurcad) / avg(usdcad)), 5), 'fx': {k: round(v, 5) for k, v in EUR_PER.items()},
        'periods': {'elec': 'Eurostat 2026 first half (household, 2,500-4,999 kWh/yr, all taxes)', 'gas': 'EU Weekly Oil Bulletin, ' + WOB_PERIOD,
                    'gasOther': 'globalpetrolprices.com, %d readings %s to %s, put on the Oil Bulletin level' % (len(GPP_R), min(GPP_R), max(GPP_R))},
        'gpp': {'n': len(GPP_R), 'first': min(GPP_R), 'last': max(GPP_R), 'check': round(GPP_CHECK, 4), 'perCountry': GPP_N},
        'rows': rows, 'ev': ev_list, 'ice': gas_list, 'evCover': round(cover_ev, 3)}
open(os.path.join(ROOT, 'assets', 'europe-cost-data.js'), 'w', encoding='utf-8', newline='\n').write(
    '// Built by scripts/gas_elec/build_europe.py - do not edit by hand. Prices in EUR. ev: [make, model, kWh/100 km WLTP, 2025 registrations];\n'
    '// ice: [make, model, L/100 km WLTP, 2025 registrations, hybrid 0/1]. Sources: Eurostat, EU Weekly Oil Bulletin, Ofgem, ElCom, EEA, globalpetrolprices.com (outside the EU).\n'
    'const EUROPE = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(len(rows), 'countries;', sum(1 for r in rows if r['e'] is None), 'without electricity,', sum(1 for r in rows if r['g'] is None), 'without gasoline')
print(len(ev_list), 'EV models (%.0f%% of 2025 EV registrations),' % (cover_ev * 100), len(gas_list), 'petrol/hybrid versions')
for r in rows:
    print('  %-24s elec %s (%s)  gas %s (%s)' % (r['n'], r['e'], r['es'], r['g'], r['gs']))

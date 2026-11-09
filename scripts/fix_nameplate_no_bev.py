"""Removes BEV units from model rows of nameplates that have NO battery-electric version.

Why: in countries without per-model fuel data the model rows are built by spreading each brand's estimated BEV/PHEV mass over its nameplates, so a
Ford Ranger could show "Ranger BEV" rows (Philippines, Thailand, South Africa, Chile, Georgia...) although the Ranger is only sold with ICE and PHEV
powertrains. The BEV units of such a row are moved into the SAME model's ICE row (model totals do not change, the model's real sales stay); the brand and
country rows are not touched (their BEV is the brand-level estimate, which can now exceed the BEV of the model rows).

NO_BEV below is a curated list (brand, nameplate), lower case, as of Nov 2026. Add a nameplate only when you are sure no BEV version is sold anywhere.
(Toyota Hilux is NOT in the list: a Hilux BEV exists. Hyundai Creta, Kia Carens, Isuzu D-Max are not either: BEV versions exist.)
Usage: python scripts/fix_nameplate_no_bev.py [--apply]   (dry run by default; idempotent)"""
import json, os, re, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FILES = [('manufacturer-model-monthly-data.js', 'year_month'), ('manufacturer-model-yearly-data.js', 'year')]
SUF = re.compile(r'\s+(BEV|PHEV|ICE|HEV)$')
NO_BEV = {
    ('ford', 'ranger'), ('ford', 'new ranger'), ('ford', 'everest'), ('ford', 'fusion'), ('ford', 'escape'),
    ('toyota', 'fortuner'), ('toyota', 'vios'), ('toyota', 'avanza'), ('toyota', 'raize'), ('toyota', 'voxy'), ('toyota', 'noah'), ('toyota', 'aqua'),
    ('mitsubishi', 'xpander'), ('mitsubishi', 'mirage g4'), ('mitsubishi', 'l200'), ('mitsubishi', 'triton'), ('mitsubishi', 'pajero sport'),
    ('isuzu', 'mu-x'), ('honda', 'vezel'), ('nissan', 'serena'), ('hyundai', 'grand i10'), ('kia', 'sonet'), ('volkswagen', 'virtus'),
    ('chevrolet', 'onix'), ('chevrolet', 'colorado'),
}
FUELS = ('bev', 'phev', 'hev', 'petrol', 'diesel', 'others')


def base(model):
    return SUF.sub('', model).strip().lower()


def fix_country(rows, key):
    """returns (new rows, moved units, rows changed)"""
    groups = collections.defaultdict(list)
    for i, r in enumerate(rows):
        if r['bev'] > 0 and (r['brand'].lower(), base(r['model'])) in NO_BEV:
            groups[(r[key], r['brand'], base(r['model']))].append(i)
    if not groups:
        return rows, 0, 0
    drop, moved, changed = set(), 0, 0
    for (per, brand, b), idxs in groups.items():
        sib = [r for r in rows if r[key] == per and r['brand'] == brand and base(r['model']) == b and r['bev'] == 0 and (r['petrol'] + r['diesel'] + r['others']) > 0 and r['phev'] == 0 and r['hev'] == 0]
        for i in idxs:
            r = rows[i]
            u = r['bev']
            if sib:
                t = sib[0]
                ice = t['petrol'] + t['diesel']
                if ice > 0:
                    dp = round(u * t['petrol'] / ice)
                    t['petrol'] += dp; t['diesel'] += u - dp
                else:
                    t['petrol'] += u
                t['total'] += u
                drop.add(i)
            else:                                    # no ICE row to merge into: this row becomes the ICE row
                r['model'] = SUF.sub('', r['model']) + ' ICE' if r['model'].endswith(' BEV') else r['model']
                r['petrol'] += u; r['bev'] = 0
            moved += u; changed += 1
    return [r for i, r in enumerate(rows) if i not in drop], moved, changed


def main():
    apply = '--apply' in sys.argv
    for fn, key in FILES:
        path = os.path.join(ROOT, 'assets', fn)
        text = open(path, encoding='utf-8', newline='').read()
        m = re.search(r'^(const [A-Z_]+ = )(\{.*\});(\s*)$', text, re.S | re.M)
        data = json.loads(m.group(2))
        tot_before = {c: sum(r['total'] for r in rows) for c, rows in data.items()}
        moved_all, per_country = 0, {}
        for c in list(data):
            new, moved, changed = fix_country(data[c], key)
            if moved:
                data[c] = new; per_country[c] = (moved, changed); moved_all += moved
        assert all(tot_before[c] == sum(r['total'] for r in data[c]) for c in data), 'model totals changed'
        print(fn, 'BEV units moved to ICE:', moved_all, {c: v for c, v in sorted(per_country.items(), key=lambda kv: -kv[1][0])})
        if apply and moved_all:
            open(path, 'w', encoding='utf-8', newline='').write(text[:m.start()] + m.group(1) + json.dumps(data, separators=(',', ':'), ensure_ascii=False) + ';' + m.group(3))
            print('  written')
    if not apply:
        print('(dry run -- nothing written; add --apply)')


if __name__ == '__main__':
    main()

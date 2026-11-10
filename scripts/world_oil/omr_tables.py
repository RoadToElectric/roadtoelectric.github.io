"""Reads the tables of an IEA Oil Market Report PDF by word position (columns are matched to the header by x), so blank cells (OPEC forecasts) stay blank.
read_table(pdf, page) -> {row name: {column label: value}}   (row names that repeat, e.g. 'Others', get a numeric suffix)"""
import re
import pymupdf

NUM = re.compile(r'^-?\d+(\.\d+)?$')
MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')


def read_table(pdf, page):
    d = pymupdf.open(pdf)
    words = d[page - 1].get_text('words')
    lines = {}
    for x0, y0, x1, y1, w, *_ in words:
        lines.setdefault(round(y0 / 3), []).append(((x0 + x1) / 2, x0, w))
    keys = sorted(lines)
    header = None
    for k in keys:                                       # the header line holds 2025 and 2026
        toks = [w for _, _, w in sorted(lines[k])]
        if '2025' in toks and '2026' in toks:
            header = k
            break
    cols = []                                            # (x center, label)
    toks = sorted(lines[header])
    i = 0
    while i < len(toks):
        xc, x0, w = toks[i]
        if w in MONTHS and i + 1 < len(toks) and toks[i + 1][2].isdigit():
            cols.append(((xc + toks[i + 1][0]) / 2, f'{w} {toks[i + 1][2]}')); i += 2
        else:
            cols.append((xc, w)); i += 1
    out, seen = {}, {}
    for k in keys:
        if k <= header:
            continue
        toks = sorted(lines[k])
        first = next((j for j, (_, _, w) in enumerate(toks) if NUM.match(w)), None)
        if first is None:
            continue
        name = ' '.join(w for _, _, w in toks[:first]).strip()
        if not name:
            continue
        vals = {}
        for xc, _, w in toks[first:]:
            if NUM.match(w):
                lab = min(cols, key=lambda c: abs(c[0] - xc))
                if abs(lab[0] - xc) < 22:
                    vals[lab[1]] = float(w)
        seen[name] = seen.get(name, 0) + 1
        out[name if seen[name] == 1 else f'{name}#{seen[name]}'] = vals
    return out


if __name__ == '__main__':
    import sys, json
    t = read_table(sys.argv[1], int(sys.argv[2]))
    for k, v in t.items():
        print(f'{k:28s}', v)

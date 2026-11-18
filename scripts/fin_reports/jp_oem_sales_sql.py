"""Builds compact upsert SQL for Supabase manufacturer_region_sales_history from scripts/fin_reports/jp_oem_sales.csv
(Japanese OEMs: Toyota, Honda, Nissan, Mazda, Subaru; company-reported sales by region). Output: scripts/fin_reports/out/jp_oem_sales_<n>.sql,
each loaded with a named migration (apply_migration). Repeated text (group, brand, basis, confidence, source, url, notes) is factored into a per-chunk CTE.
Period types: CY, FY (April of `year` to March of year+1), FYH1 (April-September of `year`), 9M (Jan-Sep)."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, 'jp_oem_sales.csv'), encoding='utf-8')))
q = lambda s: 'null' if s in ('', None) else "'" + str(s).replace("'", "''") + "'"
META = ('group_name', 'brand', 'basis', 'confidence', 'source_doc', 'source_url', 'notes')
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
CH = 1100
for n in range(0, len(rows), CH):
    part = rows[n:n + CH]; ids = {}
    for r in part:
        ids.setdefault(tuple(r[k] for k in META), len(ids) + 1)
    src = ',\n'.join(f"({i},{','.join(q(v) for v in k)})" for k, i in ids.items())
    val = ','.join(f"({ids[tuple(r[k] for k in META)]},{q(r['region'])},{q(r['powertrain'])},{r['year']},{q(r['period_type'])},{r['units']})" for r in part)
    sql = (f"with s(sid,{','.join(META)}) as (values\n{src}),\nv(sid,region,powertrain,year,period_type,units) as (values\n{val})\n"
           "insert into public.manufacturer_region_sales_history (group_name,brand,region,powertrain,year,period_type,start_date,end_date,units,basis,confidence,source_doc,source_url,notes)\n"
           "select s.group_name,s.brand,v.region,v.powertrain,v.year,v.period_type,\n"
           " case v.period_type when 'CY' then make_date(v.year,1,1) when '9M' then make_date(v.year,1,1) else make_date(v.year,4,1) end,\n"
           " case v.period_type when 'CY' then make_date(v.year,12,31) when 'FY' then make_date(v.year+1,3,31) else make_date(v.year,9,30) end,\n"
           " v.units,s.basis,s.confidence,s.source_doc,s.source_url,s.notes from v join s using (sid)\n"
           "on conflict (group_name,brand,region,powertrain,year,period_type,basis) do update set units=excluded.units,start_date=excluded.start_date,end_date=excluded.end_date,"
           "confidence=excluded.confidence,source_doc=excluded.source_doc,source_url=excluded.source_url,notes=excluded.notes,date_updated=now();")
    p = os.path.join(HERE, 'out', f'jp_oem_sales_{n // CH + 1}.sql'); open(p, 'w', encoding='utf-8').write(sql); print(p, len(sql), len(ids), 'sources')

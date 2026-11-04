"""Brand-level worldwide sales as REPORTED BY THE HOLDINGS (company results, annual reports, sales releases), calendar year 2000 -> latest.

Task 5 of the user's list (2026-11-04): "search in ALL holdings sales reports and financial reports sales numbers for each brand, from 2026 going
backward to 2000", one group at a time (Toyota, VW Group, Stellantis, Ford, GM, Nissan, Honda, Subaru, Kia, Renault, BMW, Mercedes).
Companion of fin_report_data.py (that file = one world total per entity for the "Unclassified" rows of the Manufacturers page; this file = the brand split
and the long history). Supabase table manufacturer_brand_sales_history mirrors it; `python scripts/fin_reports/brand_history_data.py` prints the upsert SQL.

add(group, brand, year, period_type, units, basis, confidence, source_doc, source_url, scope, notes)
  period_type  CY (calendar year) | FY (fiscal year, year = the year the FY starts) | 9M (Jan-Sep of the year, a partial year)
  basis        what the company counts: 'sales' = the company's own "sales" definition (Toyota: Japan registrations + notifications, outside Japan the local
               definition, retail or wholesale by country), 'retail', 'wholesale', 'deliveries', 'derived' = computed here from published series
  confidence   filing | press_release | company_data | derived | media     (company_data = the company's own downloadable data file)
Never mix bases across groups without saying so: Toyota 'sales' is not Ford 'wholesale' or VW 'deliveries'.
"""
ROWS = []


def add(group, brand, year, ptype, units, basis, conf, src, url='', scope='', notes=''):
    ROWS.append((group, brand, year, ptype, int(units), basis, conf, src, url, scope, notes))


# =====================================================================================================================
# 1 - TOYOTA   (Toyota Motor Corporation; consolidated group = Toyota incl. Lexus + Daihatsu + Hino)
G_T = 'Toyota Motor Corporation'
PSF = 'https://global.toyota/pages/global_toyota/company/profile/production-sales-figures/'
X24 = PSF + 'production_sales_figures_en_202412.xls'
X25 = PSF + 'production_sales_figures_en_202512.xlsx'
X26 = PSF + 'production_sales_figures_202609.xlsx'
S_X = 'Toyota "Sales, Production, and Export Results" detailed data (Excel), sheet Sales'
S_L = 'Toyota "Sales, Production, and Export Results" detailed data (Excel), sheet Sales of Lexus'
FILES = ' (2007-2023: file of Dec 2024; 2024-2025: file of Dec 2025)'
T_CY = {2007: 8429268, 2008: 7996102, 2009: 6979552, 2010: 7527738, 2011: 7096853, 2012: 8717314, 2013: 8947756, 2014: 9147342, 2015: 9188559, 2016: 9223727, 2017: 9383780,
        2018: 9541748, 2019: 9714253, 2020: 8692168, 2021: 9615157, 2022: 9567184, 2023: 10307395, 2024: 10159336, 2025: 10536807}
D_CY = {2007: 830788, 2008: 866196, 2009: 754406, 2010: 783292, 2011: 730498, 2012: 875662, 2013: 869875, 2014: 915239, 2015: 793760, 2016: 780384, 2017: 816997,
        2018: 848182, 2019: 837990, 2020: 693977, 2021: 725180, 2022: 766091, 2023: 790441, 2024: 536588, 2025: 675285}
H_CY = {2007: 106463, 2008: 109535, 2009: 79242, 2010: 107104, 2011: 121606, 2012: 154795, 2013: 162460, 2014: 168348, 2015: 168764, 2016: 170469, 2017: 185125,
        2018: 203768, 2019: 189879, 2020: 142293, 2021: 155212, 2022: 149972, 2023: 135203, 2024: 125556, 2025: 110483}
L_CY = {2007: 518257, 2008: 434725, 2009: 367029, 2010: 410107, 2011: 403935, 2012: 476568, 2013: 523265, 2014: 582615, 2015: 652453, 2016: 677615, 2017: 668523,
        2018: 698329, 2019: 765330, 2020: 718715, 2021: 760012, 2022: 625392, 2023: 824258, 2024: 851214, 2025: 882231}
TT_CY = {y: T_CY[y] + D_CY[y] + H_CY[y] for y in T_CY}          # = the "Total" line of the Toyota file (checked year by year)
for y, v in T_CY.items():
    add(G_T, 'Toyota (incl. Lexus)', y, 'CY', v, 'sales', 'company_data', S_X + FILES, X24 if y <= 2023 else X25,
        scope='worldwide sales, Toyota + Lexus brands, excl. Daihatsu and Hino', notes='Japan = registrations + notifications (incl. overseas-built models); outside Japan the local definition of sales')
for y, v in L_CY.items():
    add(G_T, 'Lexus', y, 'CY', v, 'sales', 'company_data', S_L + ' (2007-2015: file of Dec 2024; 2016-2025: file of Dec 2025)', X24 if y <= 2015 else X25,
        scope='worldwide, Lexus brand (included in the Toyota (incl. Lexus) line)')
    add(G_T, 'Toyota (excl. Lexus)', y, 'CY', T_CY[y] - v, 'derived', 'derived', 'Toyota (incl. Lexus) minus Lexus, same Toyota Excel files', X24 if y <= 2015 else X25,
        scope='worldwide, Toyota brand only')
for y, v in D_CY.items():
    add(G_T, 'Daihatsu', y, 'CY', v, 'sales', 'company_data', S_X + FILES, X24 if y <= 2023 else X25, scope='worldwide, Daihatsu (kei + small cars + overseas)',
        notes='2024 fell after the Dec 2023 certification-scandal shipment halt' if y == 2024 else '')
for y, v in H_CY.items():
    add(G_T, 'Hino', y, 'CY', v, 'sales', 'company_data', S_X + FILES, X24 if y <= 2023 else X25, scope='worldwide, Hino trucks and buses')
for y, v in TT_CY.items():
    add(G_T, 'Toyota group total (Toyota + Lexus + Daihatsu + Hino)', y, 'CY', v, 'sales', 'company_data', S_X + FILES, X24 if y <= 2023 else X25,
        scope='consolidated group worldwide sales')
# 2026: January-September, from Toyota's own Excel of the Oct 29 2026 release
HINO26 = 'Hino left the Toyota group in April 2026 (merger into ARCHION): a part-year figure, not comparable with earlier years'
for brand, v, nt in [('Toyota (incl. Lexus)', 7515873, ''), ('Lexus', 594218, 'included in Toyota (incl. Lexus)'), ('Toyota (excl. Lexus)', 7515873 - 594218, 'Toyota incl. Lexus minus Lexus'),
                     ('Daihatsu', 513873, ''), ('Hino', 27886, HINO26), ('Toyota group total (Toyota + Lexus + Daihatsu + Hino)', 8057632, 'includes Hino for part of the period only')]:
    der = 'excl.' in brand
    add(G_T, brand, 2026, '9M', v, 'derived' if der else 'sales', 'derived' if der else 'company_data',
        'Toyota "Sales, Production, and Export Results" Excel of the Oct 29 2026 release, column "2026 Cumulative Total" (Jan-Sep)', X26, scope='January-September 2026', notes=nt)
# 2000-2006: Toyota brand incl. Lexus = Japan sales + overseas sales, both from Toyota's own 75-Year History data (the 2007-2011 overlap with the Excel files agrees to within 100 vehicles)
JAPAN = {2000: 1771661, 2001: 1715152, 2002: 1680479, 2003: 1715908, 2004: 1759624, 2005: 1714205, 2006: 1692253}                      # vehicles
OVERSEAS_K = {2000: 3382.6, 2001: 3546.7, 2002: 3838.3, 2003: 4354.5, 2004: 4948.8, 2005: 5554.1, 2006: 6229.3}                          # thousand vehicles
H75 = 'https://www.toyota-global.com/company/history_of_toyota/75years/data/automotive_business/sales/sales_volume/'
for y in JAPAN:
    add(G_T, 'Toyota (incl. Lexus)', y, 'CY', JAPAN[y] + round(OVERSEAS_K[y] * 1000), 'derived', 'derived',
        'Toyota 75-Year History data: "Sales Volume in Japan" (1991-2011 table, Toyota + Lexus) + "Sales Overseas by Region" (TOYOTA IN THE WORLD, Toyota + Lexus, thousand vehicles)',
        H75 + 'overseas/region.html', scope='worldwide, Toyota + Lexus, excl. Daihatsu and Hino',
        notes=f'Japan {JAPAN[y]:,} ({H75}japan/1950.html) + overseas {OVERSEAS_K[y]:,.1f} thousand (rounded to 100 vehicles); Lexus not split out before 2007; Daihatsu and Hino worldwide sales for 2000-2006 not found')

if __name__ == '__main__':
    q = lambda s: "'" + str(s).replace("'", "''") + "'"
    vals = []
    for g, b, y, pt, u, basis, conf, src, url, scope, notes in ROWS:
        s, e = {'CY': (f'{y}-01-01', f'{y}-12-31'), 'FY': (f'{y}-04-01', f'{y + 1}-03-31'), '9M': (f'{y}-01-01', f'{y}-09-30')}[pt]
        vals.append(f"({q(g)},{q(b)},{y},{q(pt)},'{s}','{e}',{u},{q(basis)},{q(conf)},{q(src)},{q(url)},{q(scope)},{q(notes)})")
    print("insert into public.manufacturer_brand_sales_history (group_name,brand,year,period_type,start_date,end_date,units,basis,confidence,source_doc,source_url,scope,notes) values\n"
          + ",\n".join(vals) + "\non conflict (group_name,brand,year,period_type) do update set units=excluded.units,basis=excluded.basis,confidence=excluded.confidence,"
          "source_doc=excluded.source_doc,source_url=excluded.source_url,scope=excluded.scope,notes=excluded.notes;")

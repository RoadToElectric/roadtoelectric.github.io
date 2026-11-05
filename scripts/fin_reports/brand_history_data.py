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

# =====================================================================================================================
# 2 - VOLKSWAGEN GROUP   (Volkswagen AG; deliveries to customers worldwide, incl. the equity-accounted Chinese joint ventures)
# Basis 'deliveries'. Every row records the annual report it was read in. Rule: the figure from the year's own report when read, otherwise the restated
# prior-year figure of the next report ("updated to reflect subsequent statistical trends"). Brand rows exactly as the report lists them.
G_V = 'Volkswagen Group'
WAY = 'http://web.archive.org/web/'
AR = {   # report -> (label, url)
    2025: ('Annual Report 2025, Deliveries', 'https://annualreport2025.volkswagen-group.com/group-management-report/business-development/deliveries.html'),
    2023: ('Annual Report 2023, Deliveries', 'https://annualreport2023.volkswagen-group.com/group-management-report/business-development/deliveries.html'),
    2021: ('Annual Report 2021, Deliveries', 'https://annualreport2021.volkswagenag.com/group-management-report/business-development/deliveries.html'),
    2019: ('Annual Report 2019, Deliveries', 'https://annualreport2019.volkswagenag.com/group-management-report/business-development/deliveries.html'),
    2017: ('Annual Report 2017, Deliveries', 'https://annualreport2017.volkswagenag.com/group-management-report/business-development/deliveries.html'),
    2015: ('Annual Report 2015, Deliveries (printed pp. 96-98)', WAY + '20160504050407/http://annualreport2015.volkswagenag.com:80/group-management-report/business-development/deliveries.html'),
    2014: ('Annual Report 2014, Deliveries', WAY + '20150323221502/http://annualreport2014.volkswagenag.com/group-management-report/business-development/deliveries.html'),
    2013: ('Annual Report 2013, Deliveries', WAY + '20140903072229/http://annualreport2013.volkswagenag.com/group-management-report/business-development/deliveries.html'),
    2012: ('Annual Report 2012, Deliveries', WAY + '20230610141648/https://annualreport2012.volkswagenag.com/managementreport/businessdevelopment/deliveries.html'),
    2011: ('Annual Report 2011, Deliveries', WAY + '20240713184559/https://annualreport2011.volkswagenag.com/managementreport/businessdevelopment/deliveries.html'),
    2010: ('Annual Report 2010, Deliveries', WAY + '20170801213546/http://annualreport2010.volkswagenag.com:80/managementreport/businessdevelopment/deliveries.html'),
    2009: ('Annual Report 2009, Deliveries', WAY + '20170929055731/http://annualreport2009.volkswagenag.com:80/managementreport/businessdevelopment/deliveries.html'),
    2008: ('Annual Report 2008, Deliveries', WAY + '20100918075403/http://annualreport2008.volkswagenag.com:80/managementreport/businessdevelopment/deliveries.html'),
}
SEAT = 'SEAT (incl. CUPRA)'
# year -> (report year, {brand: units}, passenger cars + LCV total or None, commercial vehicles total or None, group total or None, note)
VW = {
    2025: (2025, {'Volkswagen Passenger Cars': 4730574, 'Audi': 1623551, 'ŠKODA': 1043938, SEAT: 586251, 'Bentley': 10131, 'Lamborghini': 10747, 'Porsche': 279449, 'Volkswagen Commercial Vehicles': 393693,
                  'Scania': 94091, 'MAN': 101632, 'International (Navistar)': 63732, 'Volkswagen Truck & Bus': 46111}, 8678334, 305566, 8983900, ''),
    2024: (2025, {'Volkswagen Passenger Cars': 4796192, 'Audi': 1671218, 'ŠKODA': 926567, SEAT: 558159, 'Bentley': 10643, 'Lamborghini': 10687, 'Porsche': 310718, 'Volkswagen Commercial Vehicles': 408281,
                  'Scania': 102120, 'MAN': 95705, 'International (Navistar)': 90562, 'Volkswagen Truck & Bus': 45829}, 8692465, 334216, 9026681, 'restated in the 2025 report'),
    2023: (2023, {'Volkswagen Passenger Cars': 4866803, 'Audi': 1895240, 'ŠKODA': 866820, SEAT: 519176, 'Bentley': 13560, 'Lamborghini': 10112, 'Porsche': 320221, 'Volkswagen Commercial Vehicles': 409406,
                  'Scania': 96568, 'MAN': 115653, 'International (Navistar)': 88880, 'Volkswagen Truck & Bus': 37073}, 8901338, 338174, 9239512, ''),
    2022: (2023, {'Volkswagen Passenger Cars': 4563327, 'Audi': 1614231, 'ŠKODA': 731262, SEAT: 385591, 'Bentley': 15174, 'Lamborghini': 9233, 'Porsche': 309884, 'Volkswagen Commercial Vehicles': 328572,
                  'Scania': 85232, 'MAN': 84372, 'International (Navistar)': 81892, 'Volkswagen Truck & Bus': 53991}, 7957274, 305487, 8262761, 'restated in the 2023 report'),
    2021: (2021, {'Volkswagen Passenger Cars': 4896914, 'Audi': 1680512, 'ŠKODA': 878202, SEAT: 470531, 'Bentley': 14659, 'Lamborghini': 8405, 'Porsche': 301915, 'Bugatti': 63, 'Volkswagen Commercial Vehicles': 359546,
                  'Scania': 90366, 'MAN': 150968, 'International (Navistar)': 29876}, 8610747, 271210, 8881957, 'Navistar included from July 1 2021; Bugatti only until October 31 2021'),
    2020: (2021, {'Volkswagen Passenger Cars': 5328090, 'Audi': 1692773, 'ŠKODA': 1004816, SEAT: 426641, 'Bentley': 11206, 'Lamborghini': 7430, 'Porsche': 272162, 'Bugatti': 77, 'Volkswagen Commercial Vehicles': 371609,
                  'Scania': 72085, 'MAN': 118102}, 9114804, 190187, 9304991, 'restated in the 2021 report'),
    2019: (2019, {'Volkswagen Passenger Cars': 6278345, 'Audi': 1845573, 'ŠKODA': 1242767, SEAT: 574078, 'Bentley': 11006, 'Lamborghini': 8205, 'Porsche': 280800, 'Bugatti': 82, 'Volkswagen Commercial Vehicles': 491559,
                  'Scania': 99457, 'MAN': 142764}, 10732415, 242221, 10974636, 'Volkswagen Commercial Vehicles reported inside Passenger Cars from January 1 2019 (earlier years restated this way)'),
    2018: (2019, {'Volkswagen Passenger Cars': 6244888, 'Audi': 1812485, 'ŠKODA': 1253741, SEAT: 517627, 'Bentley': 10494, 'Lamborghini': 5750, 'Porsche': 256255, 'Bugatti': 76, 'Volkswagen Commercial Vehicles': 499698,
                  'Scania': 96477, 'MAN': 136517}, 10601014, 232994, 10834008, 'restated in the 2019 report (incl. the new segment structure)'),
    2017: (2017, {'Volkswagen Passenger Cars': 6230229, 'Audi': 1878105, 'ŠKODA': 1200535, SEAT: 468431, 'Bentley': 11089, 'Lamborghini': 3815, 'Porsche': 246375, 'Bugatti': 71, 'Volkswagen Commercial Vehicles': 497894,
                  'Scania': 90777, 'MAN': 114134}, None, None, 10741455, 'passenger cars 10,038,650 (without Volkswagen Commercial Vehicles) + commercial vehicles 702,805 (incl. Volkswagen Commercial Vehicles) in the 2017 structure'),
    2016: (2017, {'Volkswagen Passenger Cars': 5980309, 'Audi': 1867738, 'ŠKODA': 1126477, SEAT: 408703, 'Bentley': 11023, 'Lamborghini': 3457, 'Porsche': 237778, 'Bugatti': 1, 'Volkswagen Commercial Vehicles': 477974,
                  'Scania': 81346, 'MAN': 102235}, None, None, 10297041, 'restated in the 2017 report; passenger cars 9,635,486 (without Volkswagen Commercial Vehicles) + commercial vehicles 661,555'),
    2015: (2015, {'Volkswagen Passenger Cars': 5823408, 'Audi': 1803246, 'ŠKODA': 1055501, SEAT: 400037, 'Bentley': 10100, 'Lamborghini': 3245, 'Porsche': 225121, 'Bugatti': 23, 'Volkswagen Commercial Vehicles': 430801,
                  'Scania': 76561, 'MAN': 102474}, None, None, 9930517, 'passenger cars 9,320,681 + commercial vehicles 609,836 (incl. Volkswagen Commercial Vehicles) in the 2015 structure'),
    2014: (2015, {'Volkswagen Passenger Cars': 6118654, 'Audi': 1741129, 'ŠKODA': 1037226, SEAT: 390505, 'Bentley': 11020, 'Lamborghini': 2530, 'Porsche': 189849, 'Bugatti': 45, 'Volkswagen Commercial Vehicles': 446616,
                  'Scania': 79782, 'MAN': 120088}, None, None, 10137444, 'restated in the 2015 report; passenger cars 9,490,958 + commercial vehicles 646,486'),
    2013: (2014, {'Volkswagen Passenger Cars': 6021750, 'Audi': 1575480, 'ŠKODA': 920750, SEAT: 355004, 'Bentley': 10120, 'Lamborghini': 2121, 'Porsche': 162145, 'Bugatti': 47, 'Volkswagen Commercial Vehicles': 462373,
                  'Scania': 80464, 'MAN': 140333}, None, None, None, 'restated in the 2014 report (Saveiro moved into Volkswagen Passenger Cars from January 1 2013; the 2013 report itself shows Volkswagen Passenger Cars 5,932,308 and Volkswagen Commercial Vehicles 551,908)'),
    2012: (2013, {'Volkswagen Passenger Cars': 5738417, 'Audi': 1455123, 'ŠKODA': 939202, SEAT: 321002, 'Bentley': 8510, 'Lamborghini': 2083, 'Porsche': 59513, 'Bugatti': 31, 'Volkswagen Commercial Vehicles': 550156,
                  'Scania': 67401, 'MAN': 134245}, None, None, 9275909, 'restated in the 2013 report; Porsche counted from August 1 2012 only; group total 9,275,909 is the 2012 report figure (9,074,283 passenger cars + LCV + 201,626 trucks and buses)'),
    2011: (2012, {'Volkswagen Passenger Cars': 5091035, 'Audi': 1302659, 'ŠKODA': 879184, SEAT: 350009, 'Bentley': 7003, 'Lamborghini': 1602, 'Bugatti': 38, 'Volkswagen Commercial Vehicles': 528878,
                  'Scania': 80108, 'MAN': 24750}, None, None, None, 'restated in the 2012 report; MAN consolidated from November 9 2011 (partial year); passenger cars + LCV 8,160,408'),
    2010: (2011, {'Volkswagen Passenger Cars': 4502832, 'Audi': 1092411, 'ŠKODA': 762600, SEAT: 339501, 'Bentley': 5117, 'Lamborghini': 1302, 'Bugatti': 40, 'Volkswagen Commercial Vehicles': 435669,
                  'Scania': 63712}, 7139472, None, None, 'restated in the 2011 report'),
    2009: (2010, {'Volkswagen Passenger Cars': 3954551, 'Audi': 949729, 'ŠKODA': 684226, SEAT: 336683, 'Bentley': 4616, 'Lamborghini': 1515, 'Bugatti': 50, 'Volkswagen Commercial Vehicles': 361506,
                  'Scania': 43443}, 6336319, None, None, 'restated in the 2010 report; the report\'s worldwide total (6,336,319) includes Scania'),
    2008: (2009, {'Volkswagen Passenger Cars': 3667843, 'Audi': 1003469, 'ŠKODA': 674530, SEAT: 368104, 'Bentley': 7604, 'Lamborghini': 2430, 'Bugatti': 71, 'Volkswagen Commercial Vehicles': 502265,
                  'Scania': 30527}, 6256843, None, None, 'restated in the 2009 report; Scania only from its consolidation in 2008 (part-year); the report\'s worldwide total (6,256,843) includes Scania'),
    2007: (2008, {'Volkswagen Passenger Cars': 3663154, 'Audi': 964151, 'ŠKODA': 630032, SEAT: 431024, 'Bentley': 10014, 'Lamborghini': 2406, 'Bugatti': 81, 'Volkswagen Commercial Vehicles': 488726}, 6189588, None, None,
                  'restated in the 2008 report; Scania and MAN not yet in the Group'),
}
for y, (rep, brands, pc, cv, tot, note) in VW.items():
    label, url = AR[rep]
    scope = 'deliveries to customers worldwide, incl. equity-accounted Chinese joint ventures'
    for b, u in brands.items():
        add(G_V, b, y, 'CY', u, 'deliveries', 'filing', f'Volkswagen Group {label}', url, scope=scope, notes=note)
    if tot:
        add(G_V, 'Volkswagen Group total', y, 'CY', tot, 'deliveries', 'filing', f'Volkswagen Group {label}', url, scope='all brands, passenger cars + LCV + commercial vehicles', notes=note)
    if pc:
        add(G_V, 'Passenger cars and light commercial vehicles (Group)', y, 'CY', pc, 'deliveries', 'filing', f'Volkswagen Group {label}', url, scope=scope, notes=note)
    if cv:
        add(G_V, 'Commercial vehicles (Group)', y, 'CY', cv, 'deliveries', 'filing', f'Volkswagen Group {label}', url, scope='Scania, MAN, International, Volkswagen Truck & Bus', notes=note)
# check: where the report gives a passenger car + LCV total, the passenger-car brand rows (incl. Volkswagen Commercial Vehicles) must add up to it
_PCB = ('Volkswagen Passenger Cars', 'Audi', 'ŠKODA', SEAT, 'Bentley', 'Lamborghini', 'Porsche', 'Bugatti', 'Volkswagen Commercial Vehicles')
for y, (rep, brands, pc, cv, tot, note) in VW.items():
    if pc:
        s = sum(v for b, v in brands.items() if b in _PCB) + (brands['Scania'] if y in (2008, 2009) else 0)   # the 2009 and 2010 reports' "Worldwide" row still contained Scania
        assert s == pc, (y, s, pc)

# --- Volkswagen Group 2000-2006: the annual reports of that time give deliveries by BRAND GROUP (and, in 2000, 2001 and the 2007 report's 2006 column, by brand).
# Volkswagen brand group = Volkswagen Passenger Cars + Škoda + Bentley + Bugatti; Audi brand group = Audi + SEAT + Lamborghini; Commercial Vehicles = Volkswagen Commercial Vehicles
# (the 2001 figures add up: Audi 726,134 + SEAT 487,617 + Lamborghini 297 = 1,214,048 against the Audi brand group's 1,214,047 in the 2002 report).
UAB = 'https://ddd.uab.cat/pub/infanu/146223/iaVOLKSWAGENa%dieng.pdf'
VW_SCOPE_OLD = 'deliveries to customers worldwide; Volkswagen brand group = Volkswagen Passenger Cars + Škoda + Bentley + Bugatti, Audi brand group = Audi + SEAT + Lamborghini, Commercial Vehicles = Volkswagen Commercial Vehicles'
# year: (report, pdf page, note, {Volkswagen brand group, Audi brand group, Commercial Vehicles, total})
VW_BG = {
    2001: (2002, 20, 'restated in the 2002 report', (3566235, 1214047, 299805, 5080087)),
    2002: (2003, 35, 'restated in the 2003 report', (3500630, 1202579, 280385, 4983594)),
    2003: (2004, 109, 'restated in the 2004 report', (3525553, 1231349, 258825, 5015727)),
    2004: (2005, 56, 'restated in the 2005 report', (3521694, 1223121, 333820, 5078635)),
    2005: (2006, 60, 'restated in the 2006 report', (3588690, 1252955, 401562, 5243207)),
    2006: (2006, 60, '', (3954526, 1337393, 441681, 5733600)),
}
for y, (rep, pg, note, vals) in VW_BG.items():
    assert sum(vals[:3]) == vals[3], (y, sum(vals[:3]), vals[3])
    src = f'Volkswagen AG Annual Report {rep}, deliveries to customers by market (PDF p. {pg})'
    for b, u in zip(('Volkswagen brand group', 'Audi brand group', 'Commercial Vehicles (Volkswagen Commercial Vehicles)'), vals[:3]):
        add(G_V, b, y, 'CY', u, 'deliveries', 'filing', src, UAB % rep, scope=VW_SCOPE_OLD, notes=note)
    add(G_V, 'Volkswagen Group total', y, 'CY', vals[3], 'deliveries', 'filing', src, UAB % rep, scope='all brands (the "Worldwide" row)', notes=note)
# by brand: 2000 and 2001 (own reports), 2006 (the 2007 report's restated prior-year column)
VW_BR = {
    2000: (2000, 22, '', {'Volkswagen Passenger Cars': 3127471, 'Volkswagen Commercial Vehicles': 328798, 'Audi': 653377, SEAT: 514976, 'ŠKODA': 435403, 'Bentley (reported as Rolls-Royce/Bentley)': 1822, 'Lamborghini': 296}, 5062143),
    2001: (2001, 26, '', {'Volkswagen Passenger Cars': 3105673, 'Volkswagen Commercial Vehicles': 299706, 'Audi': 726134, SEAT: 487617, 'ŠKODA': 462321, 'Bentley (reported as Rolls-Royce/Bentley)': 1799, 'Lamborghini': 297}, 5083547),
    2006: (2007, 122, 'restated in the 2007 report', {'Volkswagen Passenger Cars': 3396098, 'Audi': 905188, 'ŠKODA': 549667, SEAT: 429355, 'Bentley': 9387, 'Lamborghini': 2095, 'Volkswagen Commercial Vehicles': 441457, 'Bugatti': 45}, 5733292),
}
for y, (rep, pg, note, brands, tot) in VW_BR.items():
    assert sum(brands.values()) == tot, (y, sum(brands.values()), tot)
    src = f'Volkswagen AG Annual Report {rep}, deliveries by brand (PDF p. {pg})'
    for b, u in brands.items():
        add(G_V, b, y, 'CY', u, 'deliveries', 'filing', src, UAB % rep, scope='deliveries to customers worldwide', notes=note)
    if y == 2000:
        add(G_V, 'Volkswagen Group total', y, 'CY', tot, 'deliveries', 'filing', src, UAB % rep, scope='all brands (the "Worldwide" row)', notes='')
        # brand groups of 2000 are derived from the brand figures (the 2000 report has no brand-group table)
        for b, parts in (('Volkswagen brand group', ('Volkswagen Passenger Cars', 'ŠKODA', 'Bentley (reported as Rolls-Royce/Bentley)')), ('Audi brand group', ('Audi', SEAT, 'Lamborghini')),
                         ('Commercial Vehicles (Volkswagen Commercial Vehicles)', ('Volkswagen Commercial Vehicles',))):
            add(G_V, b, y, 'CY', sum(brands[p] for p in parts), 'derived', 'derived', src + ': sum of the brands in the group', UAB % rep, scope=VW_SCOPE_OLD, notes='derived from the brand figures')

# =====================================================================================================================
# 3 - STELLANTIS (FCA 2012-2020 + PSA 2018-2020, Stellantis from 2021).  Shipments by segment as reported in the Forms 20-F / annual reports (thousand units -> units).
# The holdings' filings do NOT give a brand table for the Group: only the Maserati segment (and Ferrari 2012-2014) are brands. PSA's brand groups
# (Peugeot-Citroën-DS and Opel/Vauxhall) appear for 2018-2020 in the Stellantis FY2020 Form 20-F ("About this report": PSA information).
G_S = 'Stellantis N.V. (FCA / PSA)'
SEC = 'https://www.sec.gov/Archives/edgar/data/1605484/'
STLA = 'https://www.stellantis.com/content/dam/stellantis-corporate/investors/financial-reports/Stellantis-NV-%s1231-Annual-Report.pdf'
S_SRC = {   # report -> (label, url)
    'FY2014': ('FCA Form 20-F FY2014, shipments by segment', SEC + '000160548415000011/fca2014123120f.htm'),
    'FY2017': ('FCA Form 20-F FY2017, shipments by segment', SEC + '000160548418000008/fca2017123120f.htm'),
    'FY2019': ('FCA Form 20-F FY2019, shipments by segment', SEC + '000160548420000011/fca20191231annualreportand.htm'),
    'FY2020': ('Stellantis Form 20-F FY2020 (FCA), shipments by segment', SEC + '000160548421000032/stellantis-20201231.htm'),
    'AR2022': ('Stellantis Annual Report 2022, consolidated shipments by segment', STLA % '2022'),
    'AR2023': ('Stellantis Annual Report 2023, consolidated shipments by segment', STLA % '2023'),
    'AR2025': ('Stellantis Annual Report 2025, consolidated shipments by segment', STLA % '2025'),
}
# FCA segments 2012-2020: year -> (report, NAFTA, LATAM, APAC, EMEA, Ferrari, Maserati, total consolidated, JV or None, combined or None)   thousand units
FCA_SEG = {
    2012: ('FY2014', 2115, 979, 103, 1012, 7, 6, 4223, None, None, 'Ferrari still consolidated'),
    2013: ('FY2014', 2238, 950, 163, 979, 7, 15, 4352, None, None, 'Ferrari still consolidated'),
    2014: ('FY2014', 2493, 827, 220, 1024, 7, 36, 4608, None, None, 'Ferrari still consolidated'),
    2015: ('FY2017', 2726, 553, 149, 1142, 0, 32, 4602, 136, 4738, 'as restated in the FY2017 filing (Ferrari excluded)'),
    2016: ('FY2017', 2587, 456, 91, 1306, 0, 42, 4482, 238, 4720, ''),
    2017: ('FY2017', 2401, 521, 85, 1365, 0, 51, 4423, 317, 4740, ''),
    2018: ('FY2019', 2633, 585, 84, 1318, 0, 35, 4655, 187, 4842, ''),
    2019: ('FY2019', 2401, 577, 76, 1199, 0, 19, 4272, 146, 4418, ''),
    2020: ('FY2020', 1842, 475, 62, 858, 0, 17, 3254, 181, 3435, ''),
}
for y, (rep, na, la, ap, em, fe, ma, tot, jv, comb, note) in FCA_SEG.items():
    assert abs(na + la + ap + em + fe + ma - tot) <= 2, (y, na + la + ap + em + fe + ma, tot)
    lab, url = S_SRC[rep]
    sc = 'consolidated shipments (vehicles shipped to dealers/distributors by consolidated subsidiaries), thousand units rounded in the filing'
    for b, v in (('North America (NAFTA until 2020)', na), ('LATAM (FCA segment 2012-2020; South America from 2021)', la), ('APAC (FCA segment 2012-2020)', ap), ('EMEA (FCA segment 2012-2020)', em), ('Maserati', ma), ('Ferrari', fe)):
        if b == 'Ferrari' and not fe:
            continue
        add(G_S, b, y, 'CY', v * 1000, 'shipments', 'filing', lab, url, scope=sc, notes=note)
    add(G_S, 'Total consolidated shipments', y, 'CY', tot * 1000, 'shipments', 'filing', lab, url, scope=sc, notes=note)
    if jv is not None:
        add(G_S, 'Joint venture shipments', y, 'CY', jv * 1000, 'shipments', 'filing', lab, url, scope='shipments by unconsolidated joint ventures (China, Turkey, Italy...)', notes=note)
        add(G_S, 'Total combined shipments', y, 'CY', comb * 1000, 'shipments', 'filing', lab, url, scope='consolidated + joint venture shipments', notes=note)
# Stellantis 2021-2025: year -> (report, North America, South America, China/India/APAC, Enlarged Europe, Middle East & Africa, Maserati, total, JV, combined)
STLA_SEG = {
    2021: ('AR2022', 1764, 811, 118, 2847, 272, 24, 5836, 213, 6049),
    2022: ('AR2023', 1861, 859, 127, 2626, 283, 26, 5782, 221, 6003),
    2023: ('AR2023', 1903, 879, 102, 2814, 443, 27, 6168, 225, 6393),
    2024: ('AR2025', 1432, 912, 61, 2576, 423, 11, 5415, 111, 5526),
    2025: ('AR2025', 1472, 1000, 61, 2490, 453, 8, 5484, 89, 5573),
}
for y, (rep, na, sa, ci, ee, mea, ma, tot, jv, comb) in STLA_SEG.items():
    assert abs(na + sa + ci + ee + mea + ma - tot) <= 2, (y, na + sa + ci + ee + mea + ma, tot)
    lab, url = S_SRC[rep]
    sc = 'consolidated shipments, thousand units rounded in the report'
    for b, v in (('North America (NAFTA until 2020)', na), ('LATAM (FCA segment 2012-2020; South America from 2021)', sa), ('China and India & Asia Pacific (Stellantis segment)', ci), ('Enlarged Europe (Stellantis segment)', ee),
                 ('Middle East & Africa (Stellantis segment)', mea), ('Maserati', ma)):
        add(G_S, b, y, 'CY', v * 1000, 'shipments', 'filing', lab, url, scope=sc, notes='segment structure of Stellantis (Enlarged Europe and Middle East & Africa replace FCA EMEA)' if y == 2021 else '')
    add(G_S, 'Total consolidated shipments', y, 'CY', tot * 1000, 'shipments', 'filing', lab, url, scope=sc)
    add(G_S, 'Joint venture shipments', y, 'CY', jv * 1000, 'shipments', 'filing', lab, url, scope='shipments by joint ventures')
    add(G_S, 'Total combined shipments', y, 'CY', comb * 1000, 'shipments', 'filing', lab, url, scope='consolidated + joint venture shipments')
# PSA brand groups 2018-2020 (vehicle sales, passenger cars + LCV, incl. CKD kits; 2018 includes about 144,000 vehicles sold in Iran by Iran Khodro and IKAP, 141,000 of them under a Peugeot licence)
PSA = {2020: (1879788, 632687, 2512475), 2019: (2505665, 973431, 3479096), 2018: (2839708, 1038057, 3877765)}
for y, (pcd, ov, tot) in PSA.items():
    assert pcd + ov == tot, (y, pcd + ov, tot)
    lab, url = S_SRC['FY2020'][0].replace('shipments by segment', 'PSA vehicle sales by region'), S_SRC['FY2020'][1]
    sc = 'PSA vehicle sales worldwide, passenger cars + LCV, including CKD kits'
    nt = 'includes about 144,000 vehicles sold in Iran by Iran Khodro and IKAP (141,000 under a Peugeot licence)' if y == 2018 else ''
    add(G_S, 'Peugeot, Citroën and DS (PCD, PSA)', y, 'CY', pcd, 'sales', 'filing', lab, url, scope=sc, notes=nt)
    add(G_S, 'PSA Group total', y, 'CY', tot, 'sales', 'filing', lab, url, scope=sc, notes=nt)   # Opel/Vauxhall (OV) is loaded by brand in PSA_BR below

# PSA brand tables 2001-2020, "Ventes mondiales consolidees" / "Worldwide sales" (passenger cars + light commercial vehicles, assembled vehicles + CKD kits).
# Sources: PSA Documents de reference (2001-2008), PSA sales press releases filed with the AMF (BusinessWire regulated news, 2009-2020).
DR = 'https://www.bnains.org/archives/communiques/Peugeot/%s_Document_de_reference_%s_Peugeot.pdf'
AMF = 'https://echanges.dila.gouv.fr/OPENDATA/AMF/BWR/%s/%s/FCBWR%s_%s.pdf'
PSA_SRC = {
    'DR2003': ('PSA Peugeot Citroen Rapport annuel / Document de reference 2003, Ventes mondiales consolidees (p. 155)', DR % ('20040427', '2003')),
    'DR2005': ('PSA Peugeot Citroen Document de reference 2005, Ventes mondiales consolidees (p. 130)', DR % ('20060424', '2005')),
    'DR2006': ('PSA Peugeot Citroen Document de reference 2006, Ventes mondiales consolidees (p. 138)', DR % ('20070423', '2006')),
    'DR2008': ('PSA Peugeot Citroen Document de reference 2008, Ventes mondiales consolidees (6.1.4)', DR % ('20090424', '2008')),
    'PR2010': ('PSA Peugeot Citroen press release 13 Jan 2011, Worldwide sales 2009 and 2010 (AMF regulated news)', AMF % ('2011', '01', '064133', '20110113')),
    'PR2011': ('PSA Peugeot Citroen press release 12 Jan 2012, Worldwide sales 2010 and 2011 (AMF regulated news)', AMF % ('2012', '01', '074102', '20120112')),
    'PR2012': ('PSA Peugeot Citroen press release 9 Jan 2013, Worldwide sales 2012 versus 2011 (AMF regulated news)', AMF % ('2013', '01', '086824', '20130109')),
    'PR2014': ('PSA Peugeot Citroen press release 14 Jan 2015, Worldwide automobile sales 2013 and 2014 (AMF regulated news)', AMF % ('2015', '01', '082695', '20150114')),
    'PR2015': ('PSA Peugeot Citroen press release 12 Jan 2016, Worldwide sales 2014 and 2015 (AMF regulated news)', AMF % ('2016', '01', '090305', '20160112')),
    'PR2016': ('Groupe PSA press release 11 Jan 2017, Ventes mondiales consolidees 2015 and 2016 (AMF regulated news)', AMF % ('2017', '01', '098023', '20170111')),
    'PR2018': ('Groupe PSA press release 15 Jan 2019, Consolidated world sales 2017 and 2018 (AMF regulated news)', AMF % ('2019', '01', '115005', '20190115')),
    'PR2019': ('Groupe PSA press release 16 Jan 2020, Total consolidated world sales 2018 and 2019 (AMF regulated news)', AMF % ('2020', '01', '122981', '20200116')),
    'PR2020': ('Groupe PSA press release 14 Jan 2021, Total consolidated world sales 2019 and 2020 (AMF regulated news)', AMF % ('2021', '01', '131012', '20210114')),
}
# year -> (source key, Peugeot, Citroen, DS or None, Opel/Vauxhall or None, PSA total, note)
PSA_BR = {
    2001: ('DR2003', 1899200, 1233600, None, None, 3132800, ''),
    2002: ('DR2003', 1955400, 1312100, None, None, 3267500, ''),
    2003: ('DR2003', 1913600, 1372500, None, None, 3286100, ''),
    2004: ('DR2005', 2027200, 1348100, None, None, 3375300, ''),
    2005: ('DR2005', 1995500, 1394500, None, None, 3390000, ''),
    2006: ('DR2006', 1959800, 1406100, None, None, 3365900, ''),
    2007: ('DR2008', 1967100, 1461300, None, None, 3428400, ''),
    2008: ('DR2008', 1904100, 1356300, None, None, 3260400, ''),
    2009: ('PR2010', 1841500, 1346400, None, None, 3187900, ''),
    2010: ('PR2011', 2141790, 1460373, None, None, 3602163, ''),
    2011: ('PR2011', 2113728, 1435688, None, None, 3549416, ''),
    2012: ('PR2012', 1700000, 1265000, None, None, 2965000, 'rounded to thousands in the release'),
    2013: ('PR2014', 1552675, 1143326, 122694, None, 2818695, 'DS shown separately from Citroen as restated in the 2014 release (the 2013 release gave Citroen incl. DS: 1,266,000)'),
    2014: ('PR2014', 1635193, 1185234, 118472, None, 2938899, ''),
    2015: ('PR2015', 1709723, 1160941, 102335, None, 2972999, ''),
    2016: ('PR2016', 1919460, 1140941, 85981, None, 3146382, 'includes 233,000 vehicles produced in Iran under Peugeot licence'),
    2017: ('PR2018', 2119845, 1055676, 52860, 403933, 3632314, 'Opel/Vauxhall consolidated by PSA from 1 August 2017 only (5 months)'),
    2018: ('PR2018', 1740214, 1046229, 53265, 1038057, 3877765, 'Peugeot includes about 144,000 vehicles sold in Iran by Iran Khodro / IKAP (1,596,216 excluding Iran)'),
    2019: ('PR2020', 1453823, 989853, 61989, 973431, 3479096, 'as restated in the 2020 release (the 2019 release gave 1,456,463 / 992,825 / 62,512 / 977,130 = 3,488,930)'),
    2020: ('PR2020', 1118912, 717190, 43686, 632687, 2512475, ''),
}
for y, (sk, pe, ci, ds, ov, tot, nt) in PSA_BR.items():
    assert pe + ci + (ds or 0) + (ov or 0) == tot, (y, pe + ci + (ds or 0) + (ov or 0), tot)
    lab, url = PSA_SRC[sk]
    sc = 'PSA worldwide sales, passenger cars + light commercial vehicles, assembled vehicles + CKD kits'
    ci_nt = '; '.join(x for x in (nt, 'Citroen includes the DS line (DS3/DS4/DS5, Citroen DS) until 2013' if y <= 2012 else '') if x)
    add(G_S, 'Peugeot', y, 'CY', pe, 'sales', 'filing', lab, url, scope=sc, notes='' if y == 2013 else nt)
    add(G_S, 'Citroën', y, 'CY', ci, 'sales', 'filing', lab, url, scope=sc, notes=ci_nt if y <= 2013 else '')
    if ds:
        add(G_S, 'DS Automobiles', y, 'CY', ds, 'sales', 'filing', lab, url, scope=sc, notes='DS was a Citroen sub-line before 2014 and a separate brand from 2015' if y <= 2014 else '')
    if ov:
        add(G_S, 'Opel/Vauxhall', y, 'CY', ov, 'sales', 'filing', lab, url, scope=sc, notes='Opel/Vauxhall belonged to General Motors until 31 July 2017' if y == 2017 else '')
    if y < 2018:
        add(G_S, 'PSA Group total', y, 'CY', tot, 'sales', 'filing', lab, url, scope=sc, notes='' if y != 2017 else 'includes Opel/Vauxhall from 1 August 2017')

if __name__ == '__main__':
    q = lambda s: "'" + str(s).replace("'", "''") + "'"
    vals = []
    for g, b, y, pt, u, basis, conf, src, url, scope, notes in ROWS:
        s, e = {'CY': (f'{y}-01-01', f'{y}-12-31'), 'FY': (f'{y}-04-01', f'{y + 1}-03-31'), '9M': (f'{y}-01-01', f'{y}-09-30')}[pt]
        vals.append(f"({q(g)},{q(b)},{y},{q(pt)},'{s}','{e}',{u},{q(basis)},{q(conf)},{q(src)},{q(url)},{q(scope)},{q(notes)})")
    print("insert into public.manufacturer_brand_sales_history (group_name,brand,year,period_type,start_date,end_date,units,basis,confidence,source_doc,source_url,scope,notes) values\n"
          + ",\n".join(vals) + "\non conflict (group_name,brand,year,period_type) do update set units=excluded.units,basis=excluded.basis,confidence=excluded.confidence,"
          "source_doc=excluded.source_doc,source_url=excluded.source_url,scope=excluded.scope,notes=excluded.notes;")

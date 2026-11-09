"""Region of each country of assets/world-oil-consumers.js (ISO3 -> the region labels of section 6 of world-oil.html, without 'Other').
Used by build_world_oil_consumers.py (field `g` of every row) and by patch_consumers_regions.py (adds it to the existing asset without a rebuild)."""
REG = {
    'North America': 'USA CAN MEX',
    'South & Central America': 'BRA ARG COL CHL VEN ECU PER TTO ABW BHS BRB BOL CRI CUB DOM SLV GLP GTM GUY HTI HND JAM MTQ NIC PAN PRY PRI SUR URY VIR',
    'Europe': 'DEU FRA GBR ESP TUR ITA NLD POL BEL GRC SWE ROU AUT PRT CZE CHE NOR HUN FIN IRL DNK BGR HRV SVK LTU CYP SVN LUX LVA EST MKD ISL ALB BIH GIB MLT SRB',
    'CIS': 'RUS KAZ UKR BLR TKM UZB AZE ARM GEO KGZ MDA TJK',
    'Middle East': 'SAU IRN ARE IRQ KWT QAT OMN ISR BHR JOR LBN PSE SYR YEM',
    'Africa': 'EGY ZAF DZA MAR AGO BEN BWA BFA CMR TCD COG CIV COD DJI GNQ ETH GAB GHA GIN KEN LBR LBY MDG MWI MLI MRT MUS MOZ NAM NER NGA REU SEN SLE SOM SSD SDN TZA TGO TUN UGA ZMB ZWE',
    'Asia Pacific': 'JPN KOR CHN IND IDN SGP THA AUS MYS TWN VNM PHL PAK HKG BGD NZL LKA AFG BRN KHM FJI GUM LAO MAC MDV MNG MMR NPL NCL PRK PNG',
}
REGION_OF = {iso: reg for reg, codes in REG.items() for iso in codes.split()}

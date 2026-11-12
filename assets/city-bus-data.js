// City buses: zero-emission share of new city bus registrations. Read by ev-trucking.html (card "City buses") and social.html (bus drafts).
// To add a new edition: replace `edition`, `asOf`, `dataYear`, `eu` and `countries` (and keep the old ones in `previous`), then the page and the draft follow.
const CITY_BUS = {
  edition: 'te-2026-02',                       // unique id of this release: the draft key of social.html is 'bus|' + edition
  dataYear: 2025,                              // the year the country table describes
  asOf: '2026-02-19',                          // publication date of the release
  label: 'Transport & Environment, Feb 2026',
  short: 'T&E / DVV Media, Feb 2026',                 // short form for posts
  basedOn: 'DVV Media, Alternative Drivelines for City Buses 2025',
  url: 'https://www.sustainable-bus.com/news/electric-buses-city-2025-europe-transport-environment/',   // press summary with the charts (the T&E release itself is on transportenvironment.org)
  // EU27 zero-emission share of new city buses (battery-electric + hydrogen), per cent: actual years, then T&E's projection at the 2023-25 growth rate
  eu: { years:[2019, 2020, 2021, 2022, 2023, 2024, 2025], values:[12, 15, 20, 27, 37, 49, 60], projection:[[2026, 76], [2027, 97], [2028, 100]] },
  // [country, battery-electric, hydrogen fuel cell, hybrid, diesel, gas, 1 = a thin sliver (<= 4 points) not labelled in the source chart and read off its bars]
  countries: [
    ['Bulgaria', 100, 0, 0, 0, 0], ['Denmark', 100, 0, 0, 0, 0], ['Estonia', 100, 0, 0, 0, 0], ['Latvia', 100, 0, 0, 0, 0], ['Slovenia', 33, 67, 0, 0, 0],
    ['Netherlands', 96, 4, 0, 0, 0], ['Norway', 97, 0, 0, 3, 0, 1], ['Luxembourg', 93, 3, 0, 4, 0, 1], ['Finland', 91, 4, 0, 5, 0], ['Belgium', 94, 0, 6, 0, 0],
    ['Lithuania', 93, 0, 0, 7, 0], ['Romania', 91, 0, 0, 9, 0], ['Portugal', 80, 7, 0, 7, 6], ['Sweden', 87, 0, 0, 11, 2, 1], ['Iceland', 85, 0, 0, 15, 0],
    ['Switzerland', 77, 1, 14, 8, 0, 1], ['United Kingdom', 74, 1, 0, 25, 0, 1], ['Austria', 61, 4, 12, 23, 0], ['Italy', 62, 3, 6, 6, 23, 1], ['EU27', 56, 4, 9, 24, 7],
    ['Spain', 56, 0, 17, 19, 8], ['Germany', 41, 9, 20, 30, 0], ['Poland', 43, 6, 12, 35, 5], ['France', 38, 4, 9, 26, 23, 1], ['Ireland', 40, 0, 0, 60, 0],
    ['Czechia', 20, 5, 0, 67, 7], ['Croatia', 20, 0, 30, 50, 0], ['Greece', 19, 0, 0, 60, 20], ['Hungary', 10, 0, 0, 90, 0], ['Slovakia', 0, 0, 0, 100, 0]
  ],
  // facts stated in the release text (not in the charts)
  facts: { ukZeBuses:'over 2,500', germanyShareOfEuFuelCellCityBuses:62, euAllBusesAndCoachesElectricShare:'nearly a quarter (ACEA)', zeroEmissionBy:2028, cvdTarget2035:true },
  previous: []                                  // older editions: [{ edition, dataYear, asOf, eu, countries }]
};

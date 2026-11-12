// Europe's buses in 2026 so far: three sources that count different things. Read by ev-buses.html (card "2026 so far") and social.html (bus draft 2).
// To update: replace the values (and `edition`, `asOf`) when DVV Media / ACEA / ICCT publish a new quarter; the page and the draft follow.
const BUS_2026 = {
  edition: 'h1-2026',                       // the draft key of social.html is 'bus26|' + edition
  asOf: '2026-11-12',                       // when this block was last read from the sources
  // DVV Media Group, European Bus Data Q2 2026 (via Sustainable Bus): registrations of buses above 8 t, EU27 + UK + Iceland + Norway + Switzerland, trolleybuses excluded
  dvv: {
    label: 'DVV Media Group, Q2 2026 European Bus Data (via Sustainable Bus)',
    url: 'https://www.sustainable-bus.com/news/electric-bus-market-europe-first-half-2026/',
    bevH1: { 2025: 5477, 2026: 8141 },
    bevYear: { 2022: 4152, 2023: 6354, 2024: 7843, 2025: 11819 },        // 2025 revised from 11,607 to 11,819 in the Q2 2026 report
    cityBevShareH1: { 2022: 29.0, 2023: 36.1, 2024: 49.6, 2025: 57.9, 2026: 61.2 },   // battery-electric share of H1 city bus registrations, per cent
    cityH1: { 2026: [7480, 12215], 2025: [4953, 8548], 2024: [3636, 7326] },          // [battery-electric city buses, all city buses]
    alt: { bev: [8141, 5477], hybrid: [1449, 1348], cng: [1328, 1195], fuelCell: [397, 272] },   // [H1 2026, H1 2025]
    countries: [['Italy', 1559, 369], ['United Kingdom', 1075, 1299], ['Poland', 1060, 148], ['Norway', 660, null], ['Germany', 553, null], ['Netherlands', 510, null], ['Portugal', 473, null],
      ['Romania', 343, 161], ['France', 337, null], ['Sweden', 326, null], ['Spain', 223, null], ['Denmark', 208, 161]],                // [country, battery-electric H1 2026, H1 2025]
    makers: [['Yutong', 1636, 'China'], ['Iveco / Heuliez', 1156, 'Italy'], ['Solaris', 1022, 'Poland'], ['BYD', 681, 'China'], ['MAN', 584, 'Germany'], ['Mercedes', 553, 'Germany'], ['Wrightbus', 542, 'United Kingdom'],
      ['Karsan', 321, 'Turkey'], ['VDL', 202, 'Netherlands'], ['Alexander Dennis', 157, 'United Kingdom'], ['Volvo', 153, 'Sweden']],   // [maker, battery-electric registrations H1 2026, home country (bar colour = its continent)]
    solarisFuelCell: 256
  },
  // ACEA commercial vehicle registrations, EU27: all buses and coaches, "electrically-chargeable" = battery-electric + plug-in hybrid + fuel cell
  acea: {
    h1: { date: '2026-07-29', total: 22590, growth: 22.7, chargeableGrowth: 56.8, share: 27.7, shareYearAgo: 21.6, diesel: 58.2, hybrid: 6.1, url: 'https://www.acea.auto/cv-registrations/new-commercial-vehicle-registrations-vans-1-9-trucks-9-8-buses-22-7-in-h1-2026/' },
    q3: { date: '2026-10-28', total: 32695, growth: 15.2, chargeableGrowth: 37.6, share: 26.4, shareYearAgo: 22.1, diesel: 58.4, hybrid: 6.9, hybridGrowth: 24, url: 'https://www.acea.auto/cv-registrations/new-commercial-vehicle-registrations-vans-0-trucks-7-5-buses-15-2-in-q1-q3-2026/' }
  },
  // ICCT, European heavy-duty vehicle market development quarterly, Q1-Q2 2026 (July 2026): EU zero-emission buses and coaches
  icct: { label: 'ICCT, European HDV market spotlight, Q1–Q2 2026', url: 'https://theicct.org/wp-content/uploads/2026/07/ID-680-%E2%80%93-EU-HDVs-Q1%E2%80%93Q2-2026_market-spotlight_final.pdf',
    zeUnits: [6400, 4300], zeShare: [28.3, 22.7], cityBusElectricQ2Above: 60 }      // [Q1-Q2 2026, Q1-Q2 2025]; the report's text gives 28.3% in the summary and 28.6% further on
};

// Central catalog of every stat page on the site.
// Add a new entry here whenever a new stat page is published — the
// Home page search box and browse grid are both driven from this list.
// QUESTIONS_CATALOG (below) drives the "Ask the data" cards: a question a visitor might ask, one verified fact, and the page that answers it.
const STATS_CATALOG = [
  {
    title: "Powertrain Mix by Country",
    subject: "World · Powertrain",
    keywords: ["ev", "electric", "bev", "phev", "hev", "hybrid", "petrol", "diesel", "powertrain", "fuel type", "europe", "asia", "americas", "country", "market share", "map", "monthly", "norway", "china", "germany"],
    description: "New-car registrations by powertrain in about 80 markets: battery-electric, plug-in hybrid, hybrid, petrol and diesel shares, a zoomable map, monthly trends, brands and models. Updated monthly — September 2026 is complete, October is rolling in.",
    tag: "Sep–Oct 2026",
    url: "powertrain-mix-by-country.html"
  },
  {
    title: "Manufacturers",
    subject: "World · Brands, groups & models",
    keywords: ["manufacturer", "brand", "model", "toyota", "tesla", "byd", "volkswagen", "group", "ranking", "top 50", "market share", "world sales", "country", "growth", "model y", "china", "us", "united states"],
    description: "Who sells what, country by country: pick a brand, a parent group or a model and see its sales on a map, its world sales since 2000, the top 50 models, and which countries grow or shrink fastest. Head-to-head mode included.",
    tag: "2008–2026",
    url: "manufacturers.html"
  },
  {
    title: "World Car Sales",
    subject: "World · Light vehicles",
    keywords: ["world", "global", "sales", "light vehicles", "cars on the road", "fleet", "bev", "ice", "electric share", "since 2000", "projection", "pickups", "vans"],
    description: "How many light vehicles the world sells and drives: new sales since 2000, the battery-electric versus combustion split, an estimate of the fleet on the road, and a 2026 projection.",
    tag: "2000–2026",
    url: "world-car-sales.html"
  },
  {
    title: "EV Charging",
    subject: "World · Charging infrastructure",
    keywords: ["charging", "charger", "stations", "ports", "ev charging", "supercharger", "tesla", "ionity", "fast charging", "kw", "operators", "brands", "per capita", "per ev", "quebec", "map"],
    description: "Public charging ports, stations and speeds country by country — slow, fast and ultra-fast — per 100,000 people and per electric car, by network, on a map that zooms to street level.",
    tag: "2019–2026",
    url: "charging-stations.html"
  },
  {
    title: "EV Trucking",
    subject: "World · Electric trucks, vans & buses",
    keywords: ["truck", "trucks", "ev trucks", "electric trucks", "trucking", "freight", "heavy-duty", "diesel", "vans", "buses", "china", "europe", "oil", "iea", "semi", "logistics", "fleet"],
    description: "How many electric trucks, vans and buses each country sells and keeps on the road, their share of new sales, an animated race, trucks versus cars, a 2026 projection, and what electric trucks keep out of the diesel tank.",
    tag: "2012–2026",
    url: "ev-trucking.html"
  },
  {
    title: "World Oil Consumption",
    subject: "World · Oil use and production",
    keywords: ["oil", "petroleum", "crude", "barrels", "consumption", "production", "transport", "cars", "trucks", "aviation", "shipping", "plastics", "petrochemicals", "opec", "saudi", "russia", "mb/d", "iea", "eia", "pie"],
    description: "How much oil the world burns each day since 1950 and for what — cars, trucks, planes, ships, plastics, industry, homes — with three pies to compare any years, and who pumps it, country by country since 1960.",
    tag: "1950–2026",
    url: "world-oil.html"
  },
  {
    title: "Population & Energy",
    subject: "World · Per-capita ratios",
    keywords: ["population", "per capita", "car ownership", "cars per person", "fleet", "oil per person", "energy", "sales per capita", "country", "ratio"],
    description: "Three per-person ratios side by side: new-car sales, the car fleet and oil consumption per capita — which countries drive the most, and which depend most on oil.",
    tag: "Latest year",
    url: "population-energy.html"
  },
  {
    title: "Biggest Movers",
    subject: "World · Rankings",
    keywords: ["growth", "fastest", "movers", "ranking", "year over year", "month over month", "bev", "ev sales", "increase", "country"],
    description: "Which markets grow their battery-electric sales fastest: year-over-year %, month-over-month %, and the raw number of extra electric cars sold.",
    tag: "Monthly",
    url: "biggest-movers.html"
  }
];

const QUESTIONS_CATALOG = [
  { q: "Which countries are closest to going fully electric?", fact: "Norway: 98.8% of new cars sold in October 2026 were battery-electric. See who follows.", url: "powertrain-mix-by-country.html", keywords: ["norway", "electric share", "bev", "leader", "country"] },
  { q: "Is China's car market bigger than America's?", fact: "Yes: about 23.7 million cars in China against 16.2 million in the United States in 2025. The “30 million” headline counts exports and trucks.", url: "manufacturers.html", keywords: ["china", "united states", "market size", "30 million", "exports"] },
  { q: "How much of the world's oil goes to cars, trucks, planes and ships?", fact: "Transport burns about 55% of all oil: around 52 million barrels a day in 2024, of which cars use 22 and trucks 17.", url: "world-oil.html#use-card", keywords: ["oil", "transport", "cars", "trucks", "aviation", "shipping"] },
  { q: "Which carmaker sells the most vehicles in the world?", fact: "Toyota Motor Corporation: about 11.3 million vehicles in 2025. Compare any group or brand since 2000.", url: "manufacturers.html", keywords: ["toyota", "biggest", "carmaker", "world sales", "group", "brand"] },
  { q: "How many Tesla Model Y does the world buy?", fact: "Roughly one million a year (about 1.1 million in 2025, an estimate), more than any other electric car.", url: "manufacturers.html", keywords: ["tesla", "model y", "model 3", "best-selling"] },
  { q: "How many cars does the world sell — and how many are electric?", fact: "About 85 million light vehicles in 2025, of which roughly 14 million were battery-electric.", url: "world-car-sales.html", keywords: ["world sales", "light vehicles", "electric share", "global"] },
  { q: "Which markets are growing electric-car sales fastest?", fact: "Ranked by year-over-year growth, month-over-month change and the raw number of extra electric cars.", url: "biggest-movers.html", keywords: ["growth", "fastest", "movers", "bev"] },
  { q: "Are electric trucks finally taking off?", fact: "About 440,000 electric trucks were sold worldwide in 2025 — roughly 9% of truck sales, around 400,000 of them in China.", url: "ev-trucking.html", keywords: ["electric trucks", "china", "freight", "diesel"] },
  { q: "Where can I charge — and how fast?", fact: "Charging ports per 100,000 people and per electric car, slow versus ultra-fast, by country and by network.", url: "charging-stations.html", keywords: ["charging", "fast", "ports", "network", "supercharger"] },
  { q: "Who pumps the most oil?", fact: "The United States (17.9 million barrels a day in 2025), then Saudi Arabia (10.8) and Russia (10.5).", url: "world-oil.html#pr-card", keywords: ["oil production", "saudi", "russia", "united states", "opec"] },
  { q: "Which countries own the most cars per person?", fact: "Cars per person, new-car sales per person and oil per person, side by side for every country.", url: "population-energy.html", keywords: ["car ownership", "per capita", "population", "fleet"] }
];

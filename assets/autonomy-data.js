/* Autonomy vehicles (private page autonomy-vehicles.html): robotaxi cities, Tesla FSD availability, the EU vote, company figures.
   First compiled 2026-11-13. Every figure carries its source and date. Source tiers:
     P = the company or the regulator itself (filing, release, official page)
     C = reported by the company through the press or an earnings call (we read it second-hand)
     T = a third-party tracker or news article that cites its own sources
   Nothing here is estimated by us. When two sources disagree both are kept in the note. */
const AUTONOMY = {
  asOf: '2026-11-13',

  // ---------- headline numbers (the cards at the top of the page) ----------
  kpis: [
    { id:'fsd-miles', label:'Tesla FSD (Supervised) miles', value:'17 billion+', sub:'cumulative, 2 Nov 2026 · 6.76 B on city streets', tier:'C', src:'driveteslacanada.ca, quoting Tesla’s FSD (Supervised) Vehicle Safety Report', url:'https://driveteslacanada.ca/news/tesla-fsd-surpasses-17-billion-miles-driven/' },
    { id:'fsd-cust', label:'Paid FSD customers', value:'1.7 million+', sub:'worldwide, Q3 2026 call (21 Oct) · over half now on subscription', tier:'C', src:'Tesla Q3 2026 earnings call', url:'https://evwire.com/p/tesla-tsla-q3-2026-earnings-call-full-transcript' },
    { id:'tesla-rt', label:'Tesla Robotaxi miles with nobody driving', value:'3.1 million', sub:'to 18 Oct 2026 · Tesla’s Robotaxi Vehicle Safety Report (6 cities)', tier:'C', src:'Not a Tesla App, reading Tesla’s Robotaxi Vehicle Safety Report', url:'https://notateslaapp.com/news/4860/tesla-names-next-robotaxi-cities-shares-miles-driven-safety-data' },
    { id:'waymo-miles', label:'Waymo rider-only miles', value:'271.3 million', sub:'through June 2026 · Waymo Safety Impact hub', tier:'P', src:'waymo.com/safety/impact (read 13 Nov 2026)', url:'https://waymo.com/safety/impact/' },
    { id:'waymo-rides', label:'Waymo paid rides per week', value:'500,000+', sub:'last figure given by Alphabet’s CEO, 29 Apr 2026 · target 1 million by end of 2026', tier:'C', src:'Alphabet Q1 2026 call, as reported (no weekly figure found for Q3)', url:'https://insideevs.com/news/791245/waymo-rides-per-week-2026-doubled/' },
    { id:'apollo', label:'Baidu Apollo Go driverless km', value:'240 million+', sub:'fully driverless, to 18 Aug 2026 · 28 cities · 23 M+ rides (call)', tier:'P', src:'Baidu Q2 2026 results release (read 13 Nov 2026)', url:'https://baidu.gcs-web.com/news-releases/news-release-details/baidu-announces-second-quarter-2026-results' }
  ],

  // ---------- robotaxi cities ----------
  // status of one operator in one city:
  //   paid    = driverless (nobody on board to drive or monitor) and the public can book and pay
  //   limited = driverless, but invite-only, waitlist, free, employees only, or a fixed pilot route
  //   driver  = a safety driver or monitor is on board (passengers ride, sometimes for a fare)
  //   next    = announced / named as coming, no riders yet
  statuses: {
    paid:    { label:'Driverless, open to the public', color:'#1b9e3f' },
    limited: { label:'Driverless, restricted (invite, waitlist, free, staff)', color:'#e8a317' },
    driver:  { label:'Safety driver or monitor on board', color:'#0a80d0' },
    next:    { label:'Announced / coming next', color:'#8a96a6' }
  },
  operators: ['Waymo','Tesla','Zoox','Apollo Go','Pony.ai','WeRide','Wayve','Other'],
  cities: [
    // ---- United States ----
    { n:'Phoenix', c:'United States', lat:33.45, lon:-112.07, rows:[
      ['Waymo','paid','2020','Waymo; MapAtlas tracker, 2 Oct 2026'], ['Tesla','next','','Named as coming in Tesla’s Robotaxi Safety Report, 21 Oct 2026; no date'] ] },
    { n:'San Francisco Bay Area', c:'United States', lat:37.62, lon:-122.2, rows:[
      ['Waymo','paid','Jun 2024 (open to all)','MapAtlas tracker; waymo.com/updates'], ['Tesla','driver','','Safety monitors on board; California DMV gives Tesla only a testing permit that needs a driver (Not a Tesla App, 5 Nov 2026); 1,098 sq mi zone'],
      ['Zoox','limited','','Free rides, no fare yet; service area being quadrupled (Zoox, Mar 2026; TechCrunch)'], ['Other','next','2026 (planned)','Nuro / Lucid / Uber: testing on public roads, first service targeted for the Bay Area in 2026 (Nuro)'] ] },
    { n:'Los Angeles', c:'United States', lat:34.05, lon:-118.24, rows:[ ['Waymo','paid','Nov 2024','MapAtlas tracker; waymo.com/updates'] ] },
    { n:'Austin', c:'United States', lat:30.27, lon:-97.74, rows:[
      ['Waymo','paid','Mar 2025 (via Uber)','MapAtlas tracker; waymo.com/updates'],
      ['Tesla','paid','Jun 2025 launch · Tesla’s unsupervised-miles report starts 22 Jan 2026','Largest Tesla fleet; Cybercabs (300+, Tesla Q3 call) alongside Model Y; zone 272 sq mi, 443 sq mi after 9 Nov expansion (Not a Tesla App; Electrek)'],
      ['Zoox','limited','2026','Employees, friends and family only (TechCrunch, Mar 2026)'] ] },
    { n:'Atlanta', c:'United States', lat:33.75, lon:-84.39, rows:[ ['Waymo','paid','Jun 2025 (via Uber)','MapAtlas tracker; waymo.com/updates'] ] },
    { n:'Miami', c:'United States', lat:25.76, lon:-80.19, rows:[
      ['Waymo','paid','22 Jan 2026','CNBC, 22 Jan 2026'], ['Tesla','paid','2026','Unsupervised Model Y, 30.8 sq mi (Not a Tesla App, 5 Nov 2026)'], ['Zoox','limited','23 Apr 2026','Employees, friends and family only'] ] },
    { n:'Orlando', c:'United States', lat:28.54, lon:-81.38, rows:[ ['Waymo','paid','Apr 2026','MapAtlas tracker'], ['Tesla','paid','Jul 2026','Unsupervised, 26.2 sq mi (Not a Tesla App)'] ] },
    { n:'Tampa', c:'United States', lat:27.95, lon:-82.46, rows:[ ['Waymo','limited','Rolling invitations since 1 Sep 2026','MapAtlas tracker; waymo.com lists it as serving riders'], ['Tesla','paid','Jul 2026','Unsupervised, 23.6 sq mi (Not a Tesla App)'] ] },
    { n:'Nashville', c:'United States', lat:36.16, lon:-86.78, rows:[ ['Waymo','paid','Jun 2026 (via Lyft)','MapAtlas tracker'] ] },
    { n:'Dallas', c:'United States', lat:32.78, lon:-96.8, rows:[ ['Waymo','paid','Aug 2026','MapAtlas tracker'], ['Tesla','paid','2026','Unsupervised Model Y, 81 sq mi; Cybercab rides planned for Nov 2026 (Tesla Q3 call)'] ] },
    { n:'Houston', c:'United States', lat:29.76, lon:-95.37, rows:[ ['Waymo','paid','Aug 2026','MapAtlas tracker'], ['Tesla','paid','2026','Unsupervised; zone grew from 25 to 254 sq mi in late Oct 2026 (Not a Tesla App)'] ] },
    { n:'Fort Worth', c:'United States', lat:32.75, lon:-97.33, rows:[ ['Tesla','paid','2 Nov 2026','143 sq mi, unsupervised Model Y (Not a Tesla App)'] ] },
    { n:'San Antonio', c:'United States', lat:29.42, lon:-98.49, rows:[ ['Waymo','limited','Waitlist; restarted Sep 2026 after a five-month pause','MapAtlas tracker'], ['Tesla','paid','9 Nov 2026','About 274 sq mi on paper; Electrek notes app tests in Austin worked in only about 59% of the posted map'] ] },
    { n:'Las Vegas', c:'United States', lat:36.17, lon:-115.14, rows:[ ['Zoox','paid','10 Aug 2026','First paid Zoox rides (Las Vegas Sun, 6 Aug 2026)'], ['Waymo','limited','Rolling invitations (2026)','waymo.com lists it as serving riders; MapAtlas tracker'], ['Tesla','next','','Named as coming; Nevada approval obtained Aug 2026'] ] },
    { n:'Denver', c:'United States', lat:39.74, lon:-104.99, rows:[ ['Waymo','limited','Rolling invitations since 1 Sep 2026','MapAtlas tracker; waymo.com'] ] },
    { n:'San Diego', c:'United States', lat:32.72, lon:-117.16, rows:[ ['Waymo','limited','Rolling invitations since 1 Sep 2026','MapAtlas tracker; waymo.com'] ] },
    { n:'Jacksonville', c:'United States', lat:30.33, lon:-81.66, rows:[ ['Tesla','next','','Named as coming in Tesla’s Robotaxi Safety Report, 21 Oct 2026'] ] },
    // Waymo's "Up next" list (waymo.com/updates, read 13 Nov 2026)
    { n:'Washington, DC', c:'United States', lat:38.91, lon:-77.04, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Baltimore', c:'United States', lat:39.29, lon:-76.61, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Philadelphia', c:'United States', lat:39.95, lon:-75.17, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'New York', c:'United States', lat:40.71, lon:-74.01, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Boston', c:'United States', lat:42.36, lon:-71.06, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Pittsburgh', c:'United States', lat:40.44, lon:-79.99, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Charlotte', c:'United States', lat:35.23, lon:-80.84, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Detroit', c:'United States', lat:42.33, lon:-83.05, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Chicago', c:'United States', lat:41.88, lon:-87.63, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Minneapolis', c:'United States', lat:44.98, lon:-93.27, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'St. Louis', c:'United States', lat:38.63, lon:-90.2, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'New Orleans', c:'United States', lat:29.95, lon:-90.07, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Portland', c:'United States', lat:45.52, lon:-122.68, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Sacramento', c:'United States', lat:38.58, lon:-121.49, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Seattle', c:'United States', lat:47.61, lon:-122.33, rows:[ ['Waymo','next','','waymo.com/updates "Up next"'] ] },
    { n:'Toronto', c:'Canada', lat:43.65, lon:-79.38, rows:[ ['Waymo','next','','Waymo blog post "Hello Toronto! Waymo is En Route", Oct 2026 (title only read; no date for rides)'] ] },
    // ---- China ----
    { n:'Beijing', c:'China', lat:39.9, lon:116.4, rows:[ ['Pony.ai','paid','Feb 2025','MapAtlas tracker (company releases)'], ['WeRide','paid','Feb 2025','MapAtlas tracker (company releases)'] ] },
    { n:'Shanghai (Pudong)', c:'China', lat:31.23, lon:121.5, rows:[ ['Pony.ai','paid','Aug 2025','MapAtlas tracker'] ] },
    { n:'Guangzhou', c:'China', lat:23.13, lon:113.26, rows:[ ['Pony.ai','paid','2025','MapAtlas tracker'], ['WeRide','paid','2025','MapAtlas tracker'] ] },
    { n:'Shenzhen', c:'China', lat:22.54, lon:114.06, rows:[ ['Pony.ai','paid','Jun 2023','MapAtlas tracker'], ['Apollo Go','paid','2025','Nanshan, Bao’an and Pingshan districts (tracker)'] ] },
    { n:'Wuhan', c:'China', lat:30.59, lon:114.31, rows:[ ['Apollo Go','limited','Free trial rides in 3 districts since Aug 2026','Many robotaxis stalled on 31 Mar 2026; service stopped, new permits frozen, restarted city by city from July (MapAtlas tracker)'] ] },
    { n:'Hong Kong', c:'China', lat:22.31, lon:114.17, rows:[ ['Apollo Go','driver','Jul 2026','First HK permits for fully driverless testing, Airport Island; selected riders (Baidu Q2 2026 release)'] ] },
    // ---- Middle East ----
    { n:'Abu Dhabi', c:'United Arab Emirates', lat:24.47, lon:54.37, rows:[ ['WeRide','paid','Nov 2025 (via Uber)','MapAtlas tracker'], ['Apollo Go','paid','Nov 2025','MapAtlas tracker'] ] },
    { n:'Dubai', c:'United Arab Emirates', lat:25.2, lon:55.27, rows:[ ['Apollo Go','paid','30 Mar 2026','Fully driverless commercial operation, also on Uber (Baidu Q2 2026 release)'], ['WeRide','paid','Mar 2026 (via Uber)','MapAtlas tracker'], ['Pony.ai','limited','Driverless tests since Apr 2026','Public fare-charging launch expected later in 2026 (Pony.ai)'] ] },
    { n:'Riyadh', c:'Saudi Arabia', lat:24.71, lon:46.68, rows:[ ['WeRide','driver','Oct 2025 (via Uber)','MapAtlas tracker'] ] },
    { n:'Doha', c:'Qatar', lat:25.29, lon:51.53, rows:[ ['Pony.ai','driver','Dec 2025','Paid commercial pilot with Mowasalat (MapAtlas tracker)'] ] },
    // ---- Asia / Pacific ----
    { n:'Singapore', c:'Singapore', lat:1.35, lon:103.82, rows:[ ['WeRide','driver','Apr 2026 (Grab)','Punggol shuttle routes (MapAtlas tracker)'], ['Pony.ai','driver','Apr 2026 (ComfortDelGro)','Punggol; public via the Zig app (Pony.ai Q2 2026)'] ] },
    { n:'Seoul', c:'South Korea', lat:37.57, lon:126.98, rows:[ ['Other','driver','','SWM on Kakao T, late-night service in Gangnam (MapAtlas tracker)'] ] },
    { n:'Yokohama', c:'Japan', lat:35.45, lon:139.64, rows:[ ['Other','driver','1 Oct to 18 Dec 2026','Nissan trial in Minato Mirai, 10 cars (MapAtlas tracker)'] ] },
    { n:'Tokyo', c:'Japan', lat:35.68, lon:139.69, rows:[ ['Waymo','next','2027','waymo.com/updates "Up next"'] ] },
    // ---- Europe ----
    { n:'London', c:'United Kingdom', lat:51.51, lon:-0.13, rows:[ ['Wayve','driver','3 Sep 2026 (via Uber)','Normal Uber fares, safety driver, fewer than 20 cars (MapAtlas tracker; Bloomberg on the TfL licence)'], ['Apollo Go','driver','2026','Open-road testing with Uber and Lyft (Baidu Q2 2026 release)'], ['Waymo','next','2027','waymo.com/updates "Up next"'] ] },
    { n:'Hamburg', c:'Germany', lat:53.55, lon:9.99, rows:[ ['Other','driver','15 Jul 2026','MOIA (VW): free, registered residents, up to 10 vehicles (MapAtlas tracker)'] ] },
    { n:'Darmstadt / Langen', c:'Germany', lat:49.87, lon:8.65, rows:[ ['Other','driver','2026','KIRA (RMV, Deutsche Bahn): free shuttle for registered test users (MapAtlas tracker)'] ] },
    { n:'Zagreb', c:'Croatia', lat:45.81, lon:15.98, rows:[ ['Pony.ai','limited','Paid with an operator since 8 Apr 2026; driverless invited riders since 10 Sep 2026','Verne with Pony.ai and Uber, one 22 km route (MapAtlas tracker)'] ] },
    { n:'Madrid', c:'Spain', lat:40.42, lon:-3.7, rows:[ ['WeRide','next','H1 2027','Spain’s first L4 robotaxi licence; public service expected H1 2027 (WeRide)'], ['Waymo','next','','Waymo blog post "¡Llegamos a Madrid!", Oct 2026 (title only read)'] ] }
  ],

  // ---------- Tesla FSD (Supervised): where it is allowed ----------
  // status: avail = on sale / usable; review = a national review is open; none = not approved (or not applied)
  fsdOther: [
    { n:'United States', iso:'US', s:'avail', note:'North America runs the V14 build (Basenor)' },
    { n:'Canada', iso:'CA', s:'avail', note:'' },
    { n:'Mexico', iso:'MX', s:'avail', note:'' },
    { n:'Puerto Rico', iso:'PR', s:'avail', note:'US territory' },
    { n:'China', iso:'CN', s:'avail', note:'Confirmed 21 May 2026; localised, limited build; one-time price 64,000 CNY; nationwide rollout pending final clearance (Basenor, citing Tesla and GlobalChinaEV)' },
    { n:'South Korea', iso:'KR', s:'avail', note:'' },
    { n:'Australia', iso:'AU', s:'avail', note:'' },
    { n:'New Zealand', iso:'NZ', s:'avail', note:'' },
    { n:'Norway', iso:'NO', s:'none', note:'Not an EU member. Statens vegvesen (29 Oct 2026): no national shortcut while the system does not meet UN R171; demos for customers not allowed' },
    { n:'Switzerland', iso:'CH', s:'none', note:'FEDRO (28 Oct 2026): Tesla has filed no application' }
  ],
  fsdOtherSource: { label:'Basenor, "FSD (Supervised) now live in 17 countries", 16 Oct 2026, citing Tesla Newswire; Engadget; TechNode', url:'https://www.basenor.com/blogs/news/tesla-fsd-supervised-now-live-in-17-countries-across-4-continents', tier:'T' },
  // Cumulative FSD (Supervised) miles, from Tesla's vehicle safety report as quoted by the press. ap = approximate date.
  fsdMilestones: [
    { d:'2025-12-28', b:7,  ap:true },
    { d:'2026-02-18', b:8 },
    { d:'2026-04-05', b:9,  ap:true },
    { d:'2026-05-03', b:10 },
    { d:'2026-08-03', b:13 },
    { d:'2026-08-27', b:14 },
    { d:'2026-09-29', b:15 },
    { d:'2026-11-02', b:17 }
  ],
  fsdMilesSource: { label:'Drive Tesla Canada, 2 Nov 2026 (Tesla FSD Supervised Vehicle Safety Report); milestone dates from Drive Tesla Canada / Basenor / Sawyer Merritt posts', url:'https://driveteslacanada.ca/news/tesla-fsd-surpasses-17-billion-miles-driven/', tier:'C' },

  // EU vote: moved to assets/eu-fsd-vote-data.js (public page eu-fsd-vote.html); the draft page sets AUTONOMY.eu = EU_FSD

  // ---------- company table ----------
  companies: [
    { n:'Waymo (Alphabet)', where:'15 US cities with riders (waymo.com, 13 Nov 2026); 17 more listed as next incl. London and Tokyo; Madrid and Toronto announced Oct 2026',
      fleet:'Not disclosed. Press estimates: about 3,000 (Dec 2025) to about 4,000 (2026)', rides:'500,000+ paid rides a week (Apr 2026); about 15 million paid rides in 2025; target 1 million a week by end 2026',
      miles:'271.3 million rider-only miles through June 2026 (LA 67.1, Bay Area 82.4, Phoenix 92.1, Austin 21.1, Atlanta 8.6)',
      other:'95% fewer serious-injury crashes and 82% fewer injury crashes than the human benchmark, Waymo’s own analysis. $16 B equity round at a $126 B valuation (2026); $5 B term loan closed Oct 2026. Alphabet Other Bets Q3 2026 revenue $372 M.',
      tier:'P/C', src:'waymo.com/safety/impact, waymo.com/updates (read 13 Nov 2026) = company; weekly rides, 2025 rides, fleet and Alphabet figures = press', url:'https://waymo.com/safety/impact/' },
    { n:'Tesla Robotaxi', where:'Unsupervised in 8 cities (Austin, Dallas, Houston, Fort Worth, Miami, Orlando, Tampa, San Antonio) plus the Bay Area with monitors; Las Vegas, Phoenix, Jacksonville named as next',
      fleet:'300+ Cybercabs in Austin (Q3 call); total robotaxi fleet not disclosed', rides:'Not disclosed. Austin hours 6 am to 2 am; 24/7 service stated as a goal for end 2026',
      miles:'3.1 million unsupervised miles to 18 Oct 2026: Austin 2.12 M, Dallas 0.61 M, Houston 0.23 M, Orlando 61 k, Tampa 53 k, Miami 46 k. Tesla says about 2 million at 30 Sep, up 8x in the quarter',
      other:'Tesla reports no injuries, airbag deployments or pedestrian hits over those miles (its own report). NHTSA is reviewing claims of robotaxis speeding in school zones. Unsupervised FSD for customer cars: Q2 2027 (V15).',
      tier:'C', src:'Tesla Q3 2026 call (21 Oct); Tesla Robotaxi Vehicle Safety Report via Not a Tesla App; Electrek', url:'https://notateslaapp.com/news/4860/tesla-names-next-robotaxi-cities-shares-miles-driven-safety-data' },
    { n:'Zoox (Amazon)', where:'Las Vegas (paid since 10 Aug 2026), San Francisco (free), Austin and Miami (staff, friends and family)',
      fleet:'About 100 vehicles, Sep 2026 (TechCrunch; not confirmed by Zoox)', rides:'Not disclosed', miles:'Not found',
      other:'Plans paid service in up to 10 more cities (Seattle, Austin, Dallas, Houston, San Diego, Los Angeles...), no dates.',
      tier:'T', src:'Las Vegas Sun, 6 Aug 2026; TechCrunch', url:'https://lasvegassun.com/news/2026/aug/06/free-rides-no-more-zoox-robotaxi-service-to-begin/' },
    { n:'Baidu Apollo Go', where:'28 cities worldwide (Baidu does not publish the list). Verified: Wuhan, Shenzhen, Hong Kong, Abu Dhabi, Dubai; testing in London and Switzerland',
      fleet:'Not given in the Q2 release', rides:'Over 23 million cumulative rides; about 1 million fully driverless rides in Q2 2026 (earnings call, second-hand). Wuhan stopped after a mass stall on 31 Mar 2026 and restarted from August.',
      miles:'Over 350 million autonomous km, of which over 240 million fully driverless (Baidu Q2 2026 release)',
      other:'Dubai: fully driverless commercial since 30 Mar 2026, also on Uber. London: open-road testing with Uber and Lyft. MoU with Kazakhstan’s Turlov.',
      tier:'P', src:'Baidu Q2 2026 results (18 Aug 2026)', url:'https://baidu.gcs-web.com/news-releases/news-release-details/baidu-announces-second-quarter-2026-results' },
    { n:'Pony.ai', where:'Beijing, Shanghai, Guangzhou, Shenzhen; Singapore, Doha, Dubai (tests), Zagreb with Verne; Luxembourg progress in Q2',
      fleet:'1,975 robotaxis at 30 Jun 2026; target over 3,500 by end 2026', rides:'Not disclosed', miles:'Over 100 million km of autonomous driving (Global Times, Aug 2026)',
      other:'Q2 2026 robotaxi revenue $12.1 M (+691% year on year), total revenue $36.2 M. Over 4,000 deployments in the pipeline outside China.',
      tier:'C', src:'Pony.ai Q2 2026 results as reported (Pulse 2.0, MarketBeat)', url:'https://pulse2.com/pony-ai-robotaxi-revenue-jumps-691-while-operating-expenses-rise-just-11/' },
    { n:'WeRide', where:'Beijing, Guangzhou; Abu Dhabi and Dubai (driverless commercial); Riyadh and Singapore (safety driver); Madrid licence; autonomous businesses in 60+ cities, 13 countries',
      fleet:'1,800+ robotaxis and about 3,400 L4 vehicles in all at 31 Jul 2026; about 400 robotaxis in the Middle East; plan 2,600 robotaxis by end 2026', rides:'Not disclosed', miles:'Not found',
      other:'Q2 2026 revenue about RMB 232 M (+82%), overseas revenue +164%. Uber is the main partner outside China.',
      tier:'C', src:'WeRide Q2 2026 results as reported (ChinaEVHome, Nasdaq)', url:'https://chinaevhome.com/2026/08/13/weride-q2-revenue-jumps-82-as-overseas-markets-drive-growth/' },
    { n:'Wayve + Uber', where:'London, safety driver, since 3 Sep 2026', fleet:'Fewer than 20 cars', rides:'Not published', miles:'—',
      other:'Full driverless operation not expected within the year; more UK approvals needed.', tier:'T', src:'MapAtlas tracker; Bloomberg, 5 Aug 2026', url:'https://mapatlas.eu/blog/robotaxi-cities' }
  ],

  // ---------- where the data comes from ----------
  sources: [
    { t:'P', label:'Waymo Safety Impact hub (miles, crash rates)', url:'https://waymo.com/safety/impact/' },
    { t:'P', label:'Waymo updates (cities serving riders / up next)', url:'https://waymo.com/updates/' },
    { t:'P', label:'Baidu Q2 2026 results release', url:'https://baidu.gcs-web.com/news-releases/news-release-details/baidu-announces-second-quarter-2026-results' },
    { t:'C', label:'Tesla Q3 2026 earnings call transcript', url:'https://evwire.com/p/tesla-tsla-q3-2026-earnings-call-full-transcript' },
    { t:'C', label:'Tesla Robotaxi Vehicle Safety Report, read by Not a Tesla App', url:'https://notateslaapp.com/news/4860/tesla-names-next-robotaxi-cities-shares-miles-driven-safety-data' },
    { t:'C', label:'Tesla Robotaxi markets and zone sizes (Not a Tesla App, 5 Nov 2026)', url:'https://www.notateslaapp.com/news/4748/teslas-active-robotaxi-markets-and-their-sizes' },
    { t:'T', label:'Tesla Robotaxi in San Antonio (Electrek, 9 Nov 2026)', url:'https://electrek.co/2026/11/09/tesla-robotaxi-san-antonio-launch-geofence/' },
    { t:'C', label:'FSD (Supervised) 17 billion miles (Drive Tesla Canada, 2 Nov 2026)', url:'https://driveteslacanada.ca/news/tesla-fsd-surpasses-17-billion-miles-driven/' },
    { t:'T', label:'FSD Europe tracker, EU approvals and vote simulator (CC BY 4.0)', url:'https://fsd-eu-tracker.de/en/' },
    { t:'T', label:'Germany confirms December EU vote (Not a Tesla App)', url:'https://www.notateslaapp.com/news/4749/germany-says-it-is-open-to-tesla-fsd-approval-confirms-eu-wide-vote-in-december' },
    { t:'T', label:'EU delays the Tesla FSD vote to December (Electrek, 25 Sep 2026)', url:'https://electrek.co/2026/09/25/eu-delays-tesla-fsd-vote-december-tcmv-agenda/' },
    { t:'T', label:'Dutch approval of FSD (Supervised) (electrive, 13 Apr 2026)', url:'https://www.electrive.com/2026/04/13/tesla-secures-first-european-approval-for-fsd-supervised-driver-assistance-system/' },
    { t:'T', label:'Robotaxi tracker, every city (MapAtlas, 2 Oct 2026, CC BY 4.0; one source per row)', url:'https://mapatlas.eu/blog/robotaxi-cities' },
    { t:'T', label:'Zoox paid rides in Las Vegas (Las Vegas Sun, 6 Aug 2026)', url:'https://lasvegassun.com/news/2026/aug/06/free-rides-no-more-zoox-robotaxi-service-to-begin/' },
    { t:'C', label:'Pony.ai Q2 2026 results (Pulse 2.0)', url:'https://pulse2.com/pony-ai-robotaxi-revenue-jumps-691-while-operating-expenses-rise-just-11/' },
    { t:'C', label:'WeRide Q2 2026 results (ChinaEVHome)', url:'https://chinaevhome.com/2026/08/13/weride-q2-revenue-jumps-82-as-overseas-markets-drive-growth/' },
    { t:'T', label:'FSD countries list (Basenor, 16 Oct 2026, citing Tesla Newswire)', url:'https://www.basenor.com/blogs/news/tesla-fsd-supervised-now-live-in-17-countries-across-4-continents' }
  ],

  // ---------- known gaps ----------
  gaps: [
    'The exact day of the December EU committee (TCMV) meeting is not published anywhere we could find, and a vote is "envisaged", not confirmed.',
    'Tesla’s own pages (tesla.com support and the Robotaxi safety report) block automatic reading: Tesla figures come second-hand, mostly from Not a Tesla App, Electrek and Drive Tesla Canada. Check them against tesla.com before publishing.',
    'Baidu names 28 cities but publishes no list: only the ones with a recent source are on the map. Chongqing, Chengdu, Hefei and others are left out until a source is found.',
    'Waymo’s weekly paid rides: the last figure from the company is 500,000+ (April). Press reports of more in October are not confirmed.',
    'Fleet sizes of Waymo, Tesla and Zoox are not disclosed by the companies; the figures here are press estimates, flagged as such.',
    'Not yet researched: May Mobility, Avride, Motional, Mobileye / VW ID Buzz, Nuro in detail, Wayve outside London, Zurich (WeRide / Uber), Luxembourg (Pony.ai), India, Japan robotaxi pilots beyond Yokohama.',
    'Japan, the UK, the UAE and Switzerland: no FSD approval found. Norway: waiting for the EU decision.'
  ]
};

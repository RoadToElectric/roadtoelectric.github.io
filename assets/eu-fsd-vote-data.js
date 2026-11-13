/* EU vote on Tesla FSD (Supervised): page eu-fsd-vote.html (the draft autonomy-vehicles-draft.html reads it too).
   Compiled 2026-11-13 from public sources, each state with the authority or outlet that announced it. Source tiers:
     P = the regulator or ministry itself, C = a company statement read second-hand, T = a tracker or a news article citing its own sources.
   Populations are in millions, as used by the FSD-EU-Tracker (CC BY 4.0). Nothing here is estimated by us. */
const EU_FSD = {
  asOf: '2026-11-11',                 // last event in the data (Finland, announced 11 Nov)
  checked: '2026-11-13',
  source: { label:'FSD-EU-Tracker.de (CC BY 4.0); each approval cites a national authority or news item', url:'https://fsd-eu-tracker.de/en/', tier:'T' },
  needStates: 15, needPop: 65,        // qualified majority: 15 of 27 states AND 65% of the EU population; 4 states with more than 35% block
  // [iso, name, population M, status (approved | review | none), approved since, who announced it / note]
  states: [
    ['NL','Netherlands',17.9,'approved','2026-04-10','RDW (the type approval everyone else recognises)'],
    ['LT','Lithuania',2.9,'approved','2026-05-20','ETSC'],
    ['EE','Estonia',1.4,'approved','2026-05-29','Estonian World'],
    ['DK','Denmark',6.0,'approved','2026-06-09','Electrek'],
    ['BE','Belgium',11.7,'approved','2026-06-10','evxl.co'],
    ['SI','Slovenia',2.1,'approved','2026-09-07','GOV.SI (AVP)'],
    ['CZ','Czechia',10.9,'approved','2026-09-21','Ministry of Transport (md.gov.cz)'],
    ['HR','Croatia',3.9,'approved','2026-09-29','N1 (HINA)'],
    ['SK','Slovakia',5.4,'approved','2026-10-16','Ministry of Transport (MD SR)'],
    ['LV','Latvia',1.9,'approved','2026-10-26','CSDD (via LETA)'],
    ['FI','Finland',5.6,'approved','2026-11-10','Traficom (says its recognition does not bind Finland in the EU vote)'],
    ['DE','Germany',83.4,'review','','Transport ministry, 6 Oct 2026: open to approval, wants a name change and the speed offset capped at +10%'],
    ['FR','France',68.3,'review','','Reuters'],
    ['IT','Italy',59.0,'review','','Review open since July; Salvini backs a swift EU approval (29 Oct 2026), no national decision'],
    ['ES','Spain',48.6,'review','','Minister Hereu'],
    ['GR','Greece',10.4,'review','','ETSC'],
    ['SE','Sweden',10.6,'review','','Trafikverket recommended the EU reject it while the system can exceed speed limits (June 2026)'],
    ['IE','Ireland',5.4,'review','','Electrek'],
    ['PL','Poland',36.6,'none','',''],
    ['RO','Romania',19.1,'none','',''],
    ['PT','Portugal',10.6,'none','',''],
    ['HU','Hungary',9.6,'none','',''],
    ['AT','Austria',9.2,'none','',''],
    ['BG','Bulgaria',6.5,'none','',''],
    ['LU','Luxembourg',0.7,'none','',''],
    ['CY','Cyprus',0.9,'none','',''],
    ['MT','Malta',0.5,'none','','']
  ],
  timeline: [
    ['2026-04-10','The Dutch road authority RDW gives Tesla FSD (Supervised) a provisional type approval, valid in the Netherlands for at least 36 months (electrive, Reuters). Other EU states can recognise it one by one.'],
    ['2026-06-30','118th meeting of the EU technical committee (TCMV): the Netherlands presents the case, no vote. The minutes cite 40 million km driven on FSD (Supervised) (EU Commission register, via the tracker).'],
    ['2026-09-25','The EU leaves the Tesla item off the 6 October vote: discussion only (Electrek, electrive).'],
    ['2026-10-06','119th TCMV meeting: discussion, no vote. A majority of approval authorities signalled they were not ready to vote (Norway’s road authority). Germany sets its conditions: a rename and a +10% speed margin cap.'],
    ['2026-10-21','Tesla’s Q3 call: Musk hopes for EU-wide approval within a few months and says he would be surprised if it took longer than Q1 2027 (Not a Tesla App recap of the call).'],
    ['2026-10-29','Italy’s transport minister Salvini backs a swift EU approval, without recognising the Dutch approval nationally.'],
    ['2026-11-10','Finland recognises the Dutch approval: the eleventh EU country. In Europe the system is now branded "Tesla Assisted Driving".'],
    ['December','Next scheduled TCMV meeting. Germany’s ministry says a vote is "envisaged"; the RDW says the procedure is still running and a vote is expected at that meeting at the earliest, not confirmed. We could not find the exact day.']
  ],
  sources: [
    { t:'T', label:'FSD-EU-Tracker.de: approvals by country, vote simulator (CC BY 4.0)', url:'https://fsd-eu-tracker.de/en/' },
    { t:'T', label:'EU delays the Tesla FSD vote to December (Electrek, 25 Sep 2026)', url:'https://electrek.co/2026/09/25/eu-delays-tesla-fsd-vote-december-tcmv-agenda/' },
    { t:'T', label:'Germany confirms a December EU vote (Not a Tesla App)', url:'https://www.notateslaapp.com/news/4749/germany-says-it-is-open-to-tesla-fsd-approval-confirms-eu-wide-vote-in-december' },
    { t:'T', label:'Dutch approval of FSD (Supervised) (electrive, 13 Apr 2026)', url:'https://www.electrive.com/2026/04/13/tesla-secures-first-european-approval-for-fsd-supervised-driver-assistance-system/' },
    { t:'C', label:'Tesla Q3 2026 earnings call (transcript)', url:'https://evwire.com/p/tesla-tsla-q3-2026-earnings-call-full-transcript' }
  ]
};

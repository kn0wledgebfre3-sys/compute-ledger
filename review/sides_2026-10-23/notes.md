# Notes: company statements moved from record to claim

Inputs: `entries_before.json` (21 entries) and `company_in_record.csv` (77 figures). Output: `entries_after.json`. Only `record`, `claim`, `record_sources`, `claim_sources` and `gap` were edited.

Summary: 19 entries changed. 71 of the 77 listed figures moved to the claim. 6 figures in 2 entries (Dominion and Stockholm Exergi) were left in the record because they come from statutory filings.

## How the edits were made

- **What moved with each figure.** Each figure moved together with the words that say what it measures and its qualifiers (unit, scope, period, condition). Other information in the same sentence that still made sense without the figure stayed in the record. This covers who built something, the supply route, the fuel mix, a permit, a timing or a funding source. Where a removal broke a sentence, the repair was one or two words: "and", "phase", "is a", "water", "cited". Each repair is listed under its entry.
- **Claim text.** Existing claim text is unchanged word for word. Each moved clause was added in full, naming who says it, and placed next to the related claim sentence. The one exception is a single full stop added to the Batam claim, which had no closing full stop.
- **Sources.** One company document now supported only the claim, so it moved from `record_sources` to `claim_sources`: TNB's AGM presentation. Several record sources now support both sides, because the record still uses them for other text and the claim now cites them for the moved figures. Those sources stay in `record_sources`, and an identical copy of each was added to `claim_sources` where it was not already there. This follows the existing Fortum entry, which lists its release on both sides. No source object was altered or dropped.
- **Gap.** The gap was changed in 5 entries, only where it stated a moved figure as a recorded fact. The change only adds who states the figure.

## Per entry

### fi-espoo-kirkkonummi-microsoft-fortum-heat
- **Moved:** all eight figures from Fortum's 6 May 2026 release: 72 water-to-water heat pumps, up to 180 MW, 40 air-to-water heat pumps, 200 MW (electric boilers), 20,000 m3, 800 MWh, about EUR 225 million and about 250,000 heat users. The claim gains a sentence beginning "Fortum's press release (6 May 2026) states: ...".
- **Kept in the record (not figures):** heat production started; "investment with NextGenerationEU and Finnish state support" (the funding source, which may later be matched to a state-aid record); recovery starts in phases in 2027.
- **Sources:** the Fortum release still supports the record and was already in claim_sources.
- **Gap:** unchanged.

### fi-hamina-google-heat-seawater
- **Moved:** EUR 1 billion and about 80%, attributed to Google's announcement as recorded by Business Finland; about 70-75% and 2,000 apartments, attributed to CapMan Infra, the owner of Haminan Energia.
- **Why the Business Finland figures moved:** Business Finland is a state funding agency, not a regulator. Its item reports Google's announcement and does not present the figures as its own findings.
- **Repairs:** "recorded a Hamina expansion with recovered heat contributing by late 2025"; "...supplied first heat in Q4 2025 and was inaugurated 12 May 2026".
- **Sources:** the Business Finland and CapMan items still support the record. Copies were added to claim_sources.
- **Gap:** unchanged. It already attributes 70-75% to the owner and 80% to Google.
- **Still in the record, not listed:** "Google states the site uses seawater to cool its servers." This is a company statement with no figure, kept under rule 2.

### ca-ab-aeso-large-load-byog-greenlight
- **Moved:** 932 MW, 2× (Siemens SGT6-8000H), C$4.6B and ~150 MMcf/d. The claim gains "Pembina's FID release (2026-07-02) gives...".
- **Repair:** "Pembina took FID on 2026-07-02 on the first phase, Sturgeon County, COD second half 2030, long-term tolling to an unnamed data center customer."
- **Sources:** the Pembina release still supports the record (FID date, COD, tolling). A copy was added to claim_sources.
- **Gap:** "approved 932 MW plant" became "approved plant's first 932 MW (Pembina's figure)". The AUC approved 1,864 MW and gives no per-phase MW, so 932 MW is now only Pembina's figure.

### us-va-dominion-datacenter-demand-filed-2026: left in place
- **Not moved:** 28% and 26% (datacenters' share of Virginia Power electricity sales, 2025 and 2024).
- **Why:** the source is Dominion's Form 10-K, a statutory filing with the SEC that the officers certify. Rule 6 names statutory filings as an example to leave in the record. The claim already states the same two figures ("Dominion's 10-K: ... 28% ... (26% in 2024)"), so moving them would only have deleted them from the record.
- **For the editor:** the record and the gap still label the 10-K figure "(company statement)". That wording was left untouched under rules 2 and 5. Whoever owns the entry should settle the label one way or the other.

### sg-imda-green-dc-roadmap-pue
- **Moved:** up to 40% (GovTech), 7% (BDx), 2-3% and 4.5 MW (Digital Realty), attributed to each operator "as republished by IMDA".
- **Why moved although IMDA is a regulator:** IMDA republishes these as the operators' own results, not as IMDA findings. The existing claim already says they are self-reported.
- **Kept in the record:** "IMDA reports GovTech moved supply air from 24°C to 26°C." This is the action, not a listed figure.
- **Sources:** the IMDA page still supports the record and was already in claim_sources.
- **Gap:** "documented adopter results" became "adopter results reported by the operators".

### my-tnb-esa-5-9gw
- **Moved:** the whole TNB AGM sentence, carrying 5.9 GW, 38 data-centre projects, 18 projects, 1.9 GW, ~1.3 GW, 5 projects and 2.7GW. Every part of it is figures and their qualifiers.
- **Why moved although TNB runs the grid:** TNB is also Peninsular Malaysia's grid utility. But this document is an investor presentation at the AGM, not a filing with the Energy Commission or a system-operator publication, and 1.3 GW and 2.7GW are targets.
- **Sources:** TNB's AGM presentation now supports only the claim and moved from record_sources to claim_sources. The record keeps only the ISEAS source.
- **Gap:** "Contracted maximum demand (5.9 GW)" became "Contracted maximum demand as stated by TNB (5.9 GW)".

### id-batam-nongsa-power
- **Moved:** 2 x 150 MW. The CSV lists this value twice, once for unit capacity and once for unit count. It is now in the claim, attributed to the Batam city government release. The claim gains a full stop after its original text.
- **Why moved:** the document is a city press release reporting a contract signing, not a regulator's finding.
- **Kept in the record:** "(gas/steam combined cycle)". This plant type supports the gap's "gas-fired".
- **Sources:** the city release still supports the record (the signing and the Firmansyah statements). A copy was added to claim_sources.
- **Gap:** unchanged.

### in-telangana-aws-future-city
- **Moved:** over US$21bn (India-wide, 2026-2030), attributed to Amazon's release. The record now ends "Amazon's release gives no site investment, acreage, building count or MW."
- **Sources:** the Amazon release still supports the record and was already in claim_sources.
- **Gap:** unchanged.

### se-stockholm-exergi-heat: left in place
- **Not moved:** 117 GWh, 50% by Stockholms stad, 50% by Ankhiale and 98%.
- **Why:** all four come from Stockholm Exergi's Årsredovisning 2023. This is the statutory annual report required under the Swedish Annual Accounts Act, filed with Bolagsverket and covered by an auditor's report. Rule 6 names statutory filings as an example to leave in the record. The record_sources entry and the gap already present it as a statutory annual report. Moving all four would have emptied the record.
- **Caveats for the editor:**
  - The CSV notes that 117 GWh is not separately assured and includes non-datacentre Öppen Fjärrvärme sources. The gap already says both.
  - The 98% renewable/recovered figure is the item closest to a company sustainability claim inside the statutory report.

### us-az-tsmc-phoenix-water
- **Moved:** 4.75 million gallons/day, attributed to TSMC Arizona's Water Resource Center engineers (24 August 2026). It was placed first in the claim, ahead of the 65% recycling figure.
- **Repair:** one word. The record now says the engineers "stated the site uses water supplied through the City of Phoenix portfolio (mostly reclaimed wastewater with a small groundwater share), under a City of Phoenix industrial pretreatment discharge permit". The supply route and permit are not the listed figure, so they stay.
- **Sources:** AZFamily still supports the record and was already in claim_sources.
- **Gap:** "about 3.6 times today's" became "about 3.6 times today's use as stated by TSMC". The ratio also holds against the EA's 4.755 MGD for Phase 1.

### kr-samsung-fabs-water
- **Moved:** all ten figures from the Water Stewardship disclosure: 344,000 t/day, 51.038 Mt/yr, 22.450 Mt/yr, 46.909 Mt/yr, +9.931 Mt, 4.985 Mt/yr, 17.601 Mt, 10.190 Mt, 235,000 t and 45,000 t/day. The 45,000 t/day figure is the Osan Stream discharge agreement as Samsung reports it. All were added to the claim as one sentence attributed to Samsung.
- **Record now reads:** "No percentage reuse rate is stated. No separate Korean Ministry of Environment withdrawal record was located." Rule 2 kept the first sentence word for word, but it now refers to Samsung's disclosure, which is described only in the claim.
- **Sources:** the Samsung document stays in record_sources because that sentence describes it. It was already in claim_sources. The editor may prefer to move the sentence and the source together.
- **Gap:** unchanged ("Company data only").

### us-hyperscaler-server-lifespan-circularity
- **Moved:**
  - 28,285 t: "Microsoft's 2025 Environmental Data Fact Sheet reports diverted waste of 28,285 t for FY24".
  - 84%: "Google reports 84% of data-center operational waste diverted (2024)".
- **Why 28,285 t moved despite assurance:** the figure is inside Deloitte's limited-assurance scope, but it is Microsoft's own figure in Microsoft's document. Limited assurance is not an auditor's finding of the number. The assurance itself stays in the record ("...shows Deloitte & Touche LLP limited assurance on Section 1 ... for FY24."), and the gap still notes it. This was the closest call. If the ledger counts auditor-assured company tables as records, restore this one figure.
- **Repair:** "Google reports UL 2799 Zero-Waste validation at two data centers and one warehouse."
- **Sources:** the Microsoft fact sheet still supports the record (the assurance scope). A copy was added to claim_sources. Google's circularity page was already on both sides.
- **Gap:** unchanged.

### uy-canelones-google-water
- **Moved:** 3,800 m³/day, as "Google (March 2023): first-stage peak potable water use of 3,800 m³/day." It was placed first in the claim, ahead of Google's Nov 2023 and 2025 statements.
- **Kept in the record:** the Ministry-released 7,600 m³/day and the context of the water crisis.
- **Sources:** El Observador (12 Mar 2023) still supports the record. A copy was added to claim_sources.
- **Gap:** unchanged.

### ar-stargate-argentina-rigi
- **Moved:** US$25 bn ("up to"), attributed to the Oficina del Presidente's X post (10 Oct 2025).
- **Kept in the record:** "...as an investment structured under RIGI, with up to 500 MW reported [press]". The RIGI framing has no figure, and 500 MW is not listed in the CSV.
- **Sources:** W.Media still supports the record and was already in claim_sources.
- **Gap:** unchanged. It already attributes US$25 bn and RIGI to the Presidency's post.

### ae-abudhabi-uae-us-ai-campus-5gw
- **Moved:**
  - 5 GW, attributed to the US Department of Commerce release (15 May 2025). This is a government announcement, not a finding.
  - 1 GW and 200 MW, attributed to G42 (Oct 2025).
- **Record now reads:** "Unveiled 15 May 2025: AI data-center capacity built by G42; ..." and "Stargate UAE is being built by Khazna (G42, Oct 2025)."
- **Sources:** the Commerce release still supports the record (unveiling, compute-access terms, fuel wording). A copy was added to claim_sources. Gulf Business was already on both sides.
- **Gap:** unchanged.

### sa-humain-pif-datacenters
- **Moved:** 211 land plots and ~6 GW, as "Humain confirmed to DCD (Mar 2026) 211 land plots nationwide and ~6 GW planned over a decade."
- **Repair:** "Humain is a PIF subsidiary, launched May 2025."
- **Sources:** DCD (press) remains in record_sources and was already in claim_sources.
- **Gap:** "Public record consists of capacity targets and a grid cooperation agreement" became "Public record consists of a grid cooperation agreement, with capacity targets stated by Humain".

### za-teraco-solar-wheeling-diesel
- **Moved:** 186 MW, Isando 70, Bredell 64, Cape Town 50, Durban 2, around 15% (CEO), 120 MW and >338,000 MWh/yr. All are attributed to Teraco or its CEO and placed first in the claim.
- **Repair:** "CEO Jan Hnizdo cited diesel spend of 'millions of rands in a month'." The diesel-spend phrase has no digits and is not listed, so it stays.
- **Kept in the record:** "In Feb 2024 Teraco announced a Free State solar PV plant to be wheeled ...".
- **Sources:** Techpoint still supports the record and was already in claim_sources.
- **Gap:** unchanged.
- **Still in the record, not listed:** the CEO's diesel-spend quote and Teraco's own statements about the plant's status. These are company statements without listed figures, kept under rule 2.

### ke-olkaria-ecocloud-geothermal
- **Moved:** 342 ha, as "KenGen's release of 31 Aug 2023 gives the Green Energy Park's area as 342 ha." KenGen is a state-owned generating company, not a regulator or grid operator.
- **Sources:** the KenGen release still supports the record. A copy was added to claim_sources.
- **Gap:** unchanged.

### ke-olkaria-microsoft-g42-stalled
- **Moved:**
  - US$1 bn, 342 ha, 100% ('100% renewable geothermal') and 24 months, as a sentence quoting KenGen's 23 May 2024 release.
  - 1,000 megawatts and 3,000 megawatts, attributed to President Ruto (29 Apr 2026, as reported by The Star). This is a head-of-state statement.
- **Repairs:** "KenGen release (23 May 2024): campus at the Green Energy Park, groundbreaking planned Q3 2024; DCD records an initial 100 MW." "President Ruto said that switching it on 'would have meant switching off half of Kenya' ...".
- **Why the claim repeats 100% and 24 months:** the existing claim already gives both figures as a paraphrase. They appear again because the moved clause was added in full, as rule 3 requires.
- **Sources:** the KenGen release was already on both sides. The Star still supports the record. A copy was added to claim_sources.
- **Gap:** unchanged.

### ng-lagos-diesel-gas-dependence
- **Moved:**
  - 12 MW expansion, about 25 MW and 180–200 MW, attributed to Rack Centre's CEO (28 Oct 2025).
  - 12 MW LGS2, attributed to Rack Centre's March 2025 briefing.
  - 40%, attributed to MTN via Connecting Africa, with no primary source.
- **Repairs:**
  - "...tied to a new expansion."
  - "describes its LGS2 as running on ...". The fuel mix restored in the third verification pass stays.
  - "...cites a Mordor Intelligence estimate of ~136.7 MW for 2025, and says gas gensets are the most common alternative (unnamed research)."
- **Sources:** Connecting Africa and the Techpoint brand-press post still support the record. Copies were added to claim_sources. TechCabal was already on both sides.
- **Gap:** unchanged. It already attributes the ~25 MW figure to the CEO.

### ma-naver-500mw-taqa-renewable
- **Moved:** 500 MW of green energy, as "TAQA Morocco's FY2025 results presentation (1 Apr 2026) gives the MoU a target of 500 MW of green energy supplied by TAQA Morocco." The whole target clause moved, because removing only the number would have turned the target into a statement that TAQA supplies the energy.
- **Why moved:** the results presentation is a listed issuer's press-conference deck, not a statutory filing.
- **Sources:** the TAQA deck still supports the record (the MoU, its development phase, northern Morocco, partners). A copy was added to claim_sources.
- **Gap:** unchanged.
- **Still in the record, not listed:** "Announced June 2025: up to 500 MW AI data center; phase 1 40 MW ..." (press).

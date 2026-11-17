# UK records on datacentres, read twice (17 November 2026)

**What was read.** Three first readers looked for the UK's public records on datacentres (briefs in `briefs/`):

- **A, permits and the grid:** the Environment Agency's decision documents on environmental permits for datacentre standby generators (49 documents, about 45 installations), Natural Resources Wales's list of permits, SEPA's guidance, and the documents on the West London electricity constraint (Greater London Authority, the utilities' letter to the Mayor, the West London Local Area Energy Plan, SSEN's plan for the Iver grid supply point, the London Assembly's report);
- **B, planning:** decisions of the Secretary of State on appeals, council officer reports and committee decisions, and directions into the development consent route, 2023 to 2026;
- **C, energy, water and money:** NESO's Future Energy Scenarios and other estimates, Ofgem's consultations on the demand connection queue, Parliament's research briefing, the Climate Change Agreement for the datacentre sector, water companies' plans, and the National Audit Office's report and government announcements on public money for AI compute.

They recorded 814 items from 170 documents (`readers/first_reading_*.csv`).

**How it was checked.** 710 of the items (all but stack heights, fuel storage and per-generator ratings) were split by document among four second readers. Each was given the document, the site or subject, and what to look for, but not the first reading's value (`readers/second_reading_tasks_*.csv`), and wrote down what the document states (`readers/second_reading_*.csv`). The two readings were compared item by item (`readers/comparison.csv`): 620 agree as printed; 87 differ, most only in wording ("twelve" against 12, a date written two ways, a decision described in other words); 3 were not found or could not be opened.

**What entered the ledger.** 322 figures, each where the two readings agree (or, for 12 items, where both readings give the same number in different words; each is noted in `check_result.csv`). They are in `sites/topics/uk/figures.csv`, with the line each was read from, and the 67 UK sites they are about are in `sites/topics/uk/sites.csv`. The seven entries in `registry/europe.json` that describe them (permits, West London, planning decisions, national estimates, the Climate Change Agreement, water companies' plans, public money) cite only items read twice.

**Left out, with the reason in `check_result.csv`:** items the readings disagree on; a testing figure that is the operator's proposal rather than a permit limit; a document with two different testing limits; three items whose source is an automated third-party summary of a council agenda; the claimants' solicitors' capacity figure for Woodlands Park; and a floor area printed as "more than 1.5 million".

**Reading the figures.**

- A permit's figure is the aggregate **rated thermal input** of the standby generators (fuel in, MWth), not electrical output and not IT load.
- Hour limits are the permit's caps. Emergency running is usually 500 hours a year for the whole installation; testing is per generator or per stack, as each figure's detail says.
- Applicants' and appellants' jobs and investment are claims, even when a decision repeats them.
- NESO's and Ofgem's figures are estimates and queue data, not metered demand.

**Limits.**

- Both readers read the documents through a text-extraction step, because the publishers' servers refused direct downloads, so page numbers can be off by one.
- Several planning decisions are known from the press only, because the councils' reports could not be reached; their figures are marked press reports.
- When this round was read, no UK site was placed on the map. 43 were placed afterwards from their grid references, read twice (`review/uk_locations_2026-11-17/`).

# Organisations: identifiers and group links, read twice (17 November 2026)

**What was read.** Two things the organisation pages need, each from a register or another document:

- **Identifiers** for the largest groups in the site register: Legal Entity Identifiers (LEIs), SEC Central Index Keys (CIKs) and Wikidata items (`briefs/BRIEF_identifiers.md`, `readers/tasks_identifiers.csv`).
- **Group links** for the companies named at the ledger's sites: which group a project company or national subsidiary belongs to, acts for or was renamed as (`briefs/BRIEF_groups.md`; US and Irish companies in `readers/tasks_groups.csv`, UK companies in `readers/tasks_groups_uk.csv`). The readers preferred a register record (Companies House's register of people with significant control, an LEI record), then a regulator's document, then the group's own filing (a subsidiaries list, an annual report), and a press report only where nothing else was found.

**How it was checked.** A second reader was given each page or document and the pair of names, but not what the first reader found, and wrote down what the document states (`briefs/BRIEF_identifiers_second.md`, `briefs/BRIEF_groups_second.md`; `readers/second_*.csv`; `readers/map_groups_*_second.csv` says which first-reading row each second-reading task checks). An identifier or link enters the ledger only where the two readings agree.

**What entered the ledger.**

- **78 identifiers for 47 organisations** (37 LEIs, 41 SEC CIKs) in `sites/organisations/identifiers.csv`. No Wikidata item entered: the second reader could not open wikidata.org. Three identifiers on which the readings differ were left out.
- **47 group links** in `sites/chain/edges.csv` (leg `ownership`), from 45 of the 47 pairs read twice. Of these, 18 rest on register records, 15 on the group's own subsidiary lists in its 10-K, 10 on other filings (annual reports, an 8-K, a 20-F, an S-3, a filing in a Louisiana Public Service Commission proceeding, an application in a Nevada state agency's board packet), and 6 on press reports or directories. 17 organisations named only by these links were added to `sites/entity_register.csv`.
- Each link keeps the line it was read from and what both readers noted: a share less than all (TSMC holds about 73% of JASM and 70% of ESMC), a list from an older year (Digital Reston, LLC appears in Digital Realty's list filed in 2008 but not in those for 2017 to 2019), a later sale (Cyxtera's assets were sold in bankruptcy in 2023), a register band ("75% or more", which does not say all).

**Left out, with the reason in `check_result.csv`:**

- two pairs the documents call only an "affiliate" (Vitesse, LLC of Facebook; Montauk Innovations LLC of Google);
- 32 first-reading rows not read a second time: 14 where no document stating the link was found; 12 where the document states another relation or no ownership (a person registered as the controlling party, two registered controllers, a successor in interest, a merger); and 6 where the same link was read from another document, or the document names a trading name rather than the company.

**Limits.**

- The register pages were read through a text-extraction step. A Companies House quote joins the fields of one entry with "...".
- LEI parents are accounting consolidation, not a stated share.
- Some subsidiary lists name only "the Registrant"; for those, the parent rests on who filed the list.
- A group link says which company owns another. It does not say that the parent operates the site.

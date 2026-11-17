# Check of the graph's links against their documents (17 November 2026)

**What was checked.** Whether the links the graph draws are what the documents say: that a figure is about the site or organisation it is attached to, that the document behind a site names the organisation the site is linked to, and as what, that a site is where the graph places it, that a document says what a chain link says, and that a document is published by the organisation it is linked to. 52 links were drawn at random from `data/graph/links.csv` by kind (`reader/key_graph_check.csv`): 14 figures, 14 operators (four of them from the UK sites, the newest names), 6 places, 13 chain links and 5 publishers. Ownership links are not in the sample: each was read twice in its own round (`review/organisation_identity_2026-11-17/`).

**How.** A reader who had not built the graph was given each document, the subject and a question, but not what the ledger holds (`reader/BRIEF_graph_check.md`, `reader/tasks_graph_check.csv`), and answered from the document alone (`reader/result_graph_check.csv`). The reader could open only 6 of the 38 documents (7 links). For 13 more links, the ledger's maintainer opened the documents and read them the same way. The other 32 links were not checked; most are figures and places resting on data services and long permit lists that could not be opened here.

**What was found** (`check_result.csv`):

- 16 links are as the documents state them, and one in part: Virginia's list of permits names the facility "Compass IAD Datacenter", not the company; the company comes from the permit itself.
- Natural Resources Wales names MSFT MCIO Limited as the **applicant** for a permit at Imperial Park, Newport, not as its operator. The role in `sites/organisations/operator_names.csv` now says so.
- The two planning decisions on Woodlands Park, Iver, name the appellant company differently: "Altrad Limited" in 2023 and "Altrad UK Limited" in 2025. The site is listed from the 2025 decision. The role now records both names. Under the ledger's rules the two names stay apart until a document says they are the same company.
- One publisher rests on where the document is hosted: the "xAi Project Quick Facts" sheet names no publisher and is on MLGW's site.

**Also checked, by script.** Every name the ledger maps to an organisation (405 operator names, 204 entry links, 84 publisher names) was compared with the organisation's name. Seventeen operator names, 5 publisher names and 17 entry links share no word with it, apart from legal forms. Each was read by hand, and each is a brand the rules map to its group (Google, TSMC, AWS) or a name the listing gives with another (a project company named with its group). None was wrong.

**Limits.** The 32 links not checked are to be read in the next check. The sample is small; repeat it whenever a new feed adds links.

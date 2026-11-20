# Scotland's datacentre directions and applications, read twice (20 November 2026)

**What was read.** The Scottish Government's two directions for datacentres over 50MW (notification, in force 17 August 2026; environmental impact assessment, in force 17 September 2026), the Parliament's motion S7M-01177 on hyperscale datacentres and its votes of 16 September 2026, the Minister for Public Finance's letter to the Climate Action Committee of 8 October 2026, and the records of five proposals: Chapelcross near Annan, Auchtertool in Fife, Wester Hermiston in Edinburgh, Larbert in Falkirk and Hurlford in East Ayrshire. South Gyle, already in the ledger, was read again.

**How.** A first reader found the documents and took 105 items (`BRIEF_first.md`, `readers/first_reading.csv`). Two second readers were given each item's document and question, not the first reader's value (`BRIEF_second.md`, `readers/second_reading_tasks.csv`), and read them independently (`readers/second_reading_result.csv`). The two readings were then compared item by item (`check_result.csv`).

**Result.** 77 items agree and are used; 21 agree but are not used (the reason is given for each); 5 differ and are not used; one document could not be opened by the second reader (a press report on Larbert), and one case page could not be read by either (the Wester Hermiston EIA decision).

**What entered the ledger.**
- A new entry, `uk-scotland-datacentre-directions-2026` (`registry/europe.json`): the directions, the Parliament's resolution and the Minister's letter as records; the applicants' and developers' figures as claims.
- Five sites in `sites/topics/uk/sites.csv`. Wester Hermiston is placed from the grid reference on its screening request (X 316900, Y 670000, given to the nearest 100 m). The other four are not placed: their documents give an address or a place, not coordinates.
- 17 figures in `sites/topics/uk/figures.csv`. Three are records: the Chapelcross site's area and its 132kv grid supply point from the council's framework, and Larbert's 300MW in the council's notice of the application. The rest are claims: capacity, investment, jobs and areas as applicants describe them, in the press or as SPICe gives them.

**Reading them.**
- The Parliament's motion is a resolution, and the Minister's letter states an expectation. Neither is a legal bar on decisions.
- The proposals state capacity in different terms ("data capacity", "demand utility capacity", "badged as"), so they are not added together.
- Chapelcross's application and EIA Report are known from press only.
- Third parties' figures from submissions to the Climate Action Committee (backup generators at Chapelcross, Ravenscraig and the Lanarkshire AI Growth Zone) were read twice and agree, but are not used. They describe documents the readers did not open.

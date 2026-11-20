# Datacentre counts in a commercial directory, read twice (20 November 2026)

**What was read.** Data Center Map's list of datacentres by country (https://www.datacentermap.com/datacenters.html), for the 50 countries with a page in the ledger, and its worldwide total. Two readers read the page independently on 20 November 2026 (`BRIEF_directory.md`, `readers/`). All 51 counts agree (`check_result.csv`).

**What entered the ledger.** The counts are in `sites/topics/directory/figures.csv`. They are claims, not records: the directory says its listings "are primarily submitted and maintained directly by the operators". They belong to the entry `global-datacentre-counts-directory-and-records`, which sets them beside the sites the ledger names from public records. Each country's page shows both numbers under "How many datacentres".

**Reading them.**
- The directory counts buildings that operators list. It gives no size, and does not say what runs in them.
- It changes daily, so each count is dated.
- It lists Hong Kong and Macau apart from China, and the Republic of the Congo apart from the Democratic Republic of the Congo. The ledger takes each country's own line.

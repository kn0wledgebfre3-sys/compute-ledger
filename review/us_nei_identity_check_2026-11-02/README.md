# Check: what and where the inventory's datacenter facilities are (2 November 2026)

EPA's emissions inventory (pulled 26 October 2026) lists 71 facilities outside Virginia that states classed under NAICS 518210. The figures are EPA's; what a script cannot check is what each facility is and where. Three readers, working separately from each other and from the ledger, each took a group of states with `BRIEF.md` and their list (`readers/facilities_A.csv`: Oregon and Nevada; `_B`: Illinois, Pennsylvania and Texas; `_C`: the other eight states) and wrote `readers/result_*.csv`, as written except that wording about the search tools was replaced.

Their search time ran out before every facility was searched: 31 facilities were identified from a regulator's or other public body's document, 16 from company or press material only, and 24 not yet (for six of these the finding is that the inventory's street address is an owner's mailing address). Texas was not searched by its reader; the four Texas facilities were matched to the ledger's Texas sites by EPA's own facility registry (one record lists the inventory id, the others the same street address).

How the results were applied (`check_result.csv`, one row per facility, and `sites/metered/us_nei_facilities.csv`):

- Every facility stays in, as the inventory classifies it, with a note saying what else was found. Three are typed as buildings that contain a datacenter, where the documents describe offices.
- A facility is placed on a site the ledger already lists only where a document says it is the same site: nine (four in Texas, five Google sites). Other nearby listed sites are named in the note and kept apart.
- The operator is filled in only where a record names the holder or operator.
- The figures have not been re-queried: they are first readings by script (`second_read` = no).

# System check before publication, 24 October 2026

A dedicated check of the whole ledger before it was sent out, by reviewers who had not seen it built, followed by corrections. Each folder holds the reviewer's brief (`BRIEF.md`) and findings (`result.csv`); `COMMON.md` is the rules every reviewer worked to.

| Folder | What was checked | Findings |
|---|---|---|
| `A` | Every number and factual statement in the brief, the READMEs, the ledger page's themes and the outgoing emails, traced to the data | 10 errors, 18 inconsistencies (6 of them stale totals), 24 weak, 3 style |
| `B1`, `B2` | A fresh random sample of 65 figures and 15 supply links, none covered by an earlier check, re-read against their documents (`figures_*.csv`, `edges_*.csv`) | figures: 49 found, 3 found different, 7 not in the document, 6 unreachable (three read in other copies); links: 14 found, 1 found different |
| `C1`, `C2` | All 202 registry entries: records vs claims, sources, internal consistency, contradictions between entries, tone | 146 and 70 problems |
| `V1`, `V2` | A second reading against the primary documents of the 40 entries that had never had one | 13 verified, 19 partial, 6 not found, 2 contradicted |
| `P1`, `P2` | Every figure with a press or NGO basis shown on the record side (376), classified | 163 kept as reports of records, 111 moved to claim, 93 unattributed, 9 wrong basis |
| `F` | After the corrections: the outward text (ledger themes, standards note, brief, READMEs, package notes, emails) against the corrected entries | 43 places changed: 14 errors, 7 inconsistencies, 22 weak |

A mechanical sweep of the repository ran alongside (ids, references, dates, URLs, units, duplicate sites, local paths, every page opened at phone width).

## What changed

- **Records and claims.** Company statements, government announcements, plans and forecasts, and press reports of them, were moved from `record` to `claim`, with their measurement rows; the record or claim text of 142 of the 202 entries changed. Press reports of records stay in `record`, marked `[press: …]`; NGO and study findings are marked `[NGO: …]` and `[study: …]`. Entries with no record behind them now say "No record found yet". The rules are in `CONTRIBUTING.md`.
- **Errors corrected**, among them: Virginia's large-load rate class comes from the SCC's biennial review order (PUR-2025-00058), at 25 MW or more, not from the Chesterfield order; Korea's 162 metro applications is 176; the Irish CRU decision's terms rest on a law firm's briefing, not the decision paper; Amsterdam's title said the opposite of its record; figures not in their cited documents were removed or re-sourced (ERCOT, Thames Water, The Dalles, Middenmeer); the xAI Memphis permit is now named (No. 01156-01PC).
- **Status.** Every entry now has a verification status: 70 verified, 103 partial, 29 not found. Confidence follows the rule in `CONTRIBUTING.md`: 69 high, 108 medium, 25 low.
- **The measurements table**: 2,750 figures, 650 of them claims. Computed sums are basis `derived` with their formula; source links and dates are well formed and enforced by the builder; site ids that turned out to name one site twice are retired to `site_id_aliases.csv`.
- **Outward text**: the brief, READMEs, the ledger page's themes and the emails were corrected where the review found an error or an overstatement.

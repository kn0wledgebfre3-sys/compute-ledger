# The three views, checked twice by two checkers (20 November 2026)

**What was checked.** The three pages added on 20 November 2026: `records-and-claims.html` (records beside claims), `coverage.html` (what the public record holds, country by country and topic by topic) and `timeline.html` (the documents over time).

**How.** Two checkers who did not build the pages worked side by side, and each checked twice: once on the first build, and again after the fixes.
- **Accuracy.** Recomputed every number from the ledger's tables without using the code that builds the pages. That covered all 520 coverage cells, also compared with each country's own page and replayed through Explore's filters; the 72 rows and every pair on the records page, with 11 pairs' figures confirmed in their source documents; and every one of the 923 timeline rows (date, side, countries, link), the per-year counts, and agreement with the 1,063 document pages and the document list. Files: `checkers/accuracy_first.csv`, `checkers/accuracy_second.csv`, and the random samples of timeline rows.
- **Browser.** Opened each page at desktop and phone widths in light and dark, and tested:
  - errors and sideways overflow;
  - every link;
  - every filter option, with its count checked against the rows drawn;
  - the chart by mouse, keyboard and tap, and under 89 filter settings;
  - sorting;
  - tabbing through every cell;
  - contrast.

  Files: `checkers/browser_first.csv`, `checkers/browser_second.csv` (screenshots were not kept).

**Result.** All counts were right at the first check. 28 problems were found across the two checks, in notes, labels, layout and behaviour; `check_result.csv` lists each with how it was resolved. Two concern figures already in the ledger and are on the roadmap rather than changed without a second reading: the Morowali figure's description ("initial count"), and the source address of Meta's 2024 assured figures, which now serves the 2025 report. The pairs concerned were taken off the page.

**What changed beyond the three pages.**
- Every country page's grid now says when a topic holds only figures the ledger computed from records.
- Document pages and the document list now date a document by the latest date recorded for it, give the range where there are several, and tag a document read as often for records as for claims as both.
- One-day periods are written as one date on every page.

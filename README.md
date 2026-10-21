# Compute Ledger

A public ledger of what records say about the physical, social and economic footprint of AI compute, site by site, worldwide. Permits, grid filings, court records, statistical offices, audits and trade data, laid beside what operators and governments say in public. Every number links to the document it came from. Good cases are entries too.

**117 entries · 40 countries · 397 linked documents · 71 open datasets · 3 receipts** (as of 2026-10-20)

The ledger is built on one rule: a company's statement is a claim, and a document from a regulator, court, grid operator, statistical office, auditor or customs authority is a record. The ledger shows both and states the gap in one line without adjectives.

## What is here

| Folder | What it holds |
|---|---|
| `registry/` | The entries, one JSON file per region plus `sources.json` (the open-data catalogue) and `guide.json` (the guided themes on the page). This is the dataset. |
| `receipts/` | Cases worked all the way down: the claim, a dated timeline of documents, the gap, the limits. Markdown for reading, JSON for the page. |
| `scrapers/` | Scripts that pull structured public files (US grid queues, federal plant data, UK register, Climate TRACE) so numbers come from a file, not from anyone's reading. See its README. |
| `research_notes/` | The working notes behind each region's entries, with the gaps that were found. |
| `site/` | `build_page.py` turns the registry, guide and receipts into one self-contained `index.html`. |
| `data/` | Dated outputs of each monthly scraper run (created by the workflow). |

## Entry schema

```json
{
  "id": "nl-middenmeer-microsoft-water",
  "country": "Netherlands", "region": "Hollands Kroon",
  "site_or_subject": "...", "operator": "...", "lat": 52.8, "lon": 4.98,
  "category": "water",
  "record": "What the public record says, with numbers and dates.",
  "record_sources": [{"title": "", "url": "", "publisher": "", "date": ""}],
  "claim": "What the operator or government says in public, or 'none found'.",
  "claim_sources": [...],
  "gap": "One neutral line, or 'none documented', or 'positive example: ...'",
  "confidence": "high | medium | low",
  "verification_status": "verified | partial | not_found",
  "verification_note": "What was checked against the original document and what could not be.",
  "receipt": "optional slug of a receipt in receipts/",
  "last_checked": "YYYY-MM-DD"
}
```

Categories: `power fuel water heat_reuse moratorium grid_policy minerals fab ewaste land_biodiversity community public_money labor circularity`.

Confidence: **high** means the primary document was read directly; **medium** means the figure comes from a press report of the document; **low** means second-hand or older. A second pass re-checked every medium and low entry against its original; the result is in `verification_status`.

## Contributing a correction or an entry

The correct response to an entry is a newer document, not a rebuttal.

1. Open a pull request that edits the entry in `registry/`. Put the document first in `record_sources`, update `record`, `gap` and `last_checked`, and say in the PR what the document shows.
2. For a new entry, use the schema above. No entry merges without a URL to a record. Company press releases are claims, not records. Mirrors of an actual document (a law firm's copy of a regulator decision, a library copy of a UN report) count as the document.
3. Validation runs on every PR: the registry must parse, ids must be unique, every entry needs a record URL, and the page must build.

Corrections submitted on the published page go to its shared store and are reviewed into the registry by hand.

## Running the scrapers

See `scrapers/README.md`. They need a machine with ordinary internet access and, for the generation series, a free EIA API key in `EIA_API_KEY`. The monthly workflow in `.github/workflows/monthly-scrape.yml` runs them on the 3rd of each month and commits dated outputs under `data/`. Until the first live run, every scraper output in this repository is from fixture files and is labelled as such.

## Method

**What counts as a record.** A document produced by a regulator, court, grid operator, statistical office, auditor, UN body, customs authority, or a legally bound corporate filing. A sustainability report is a claim unless a figure is third-party assured and the assurance statement is public, in which case the assured figure is a record and the rest remains a claim.

**What a gap means.** Where the record and the claim differ, in one line. "None documented" means they agree or no claim was found. "Positive example" means the record shows a practice worth copying.

**What is excluded.** Estimates, modelled footprints, advocacy press releases cited on their own, and anything without a URL to the underlying document.

**What a receipt is.** One case worked to the point where it cannot be waved away: every figure tied to a page of a document, the timeline reconstructed from dated documents, a short quote at most, no adjectives. Figures confirmed only through press are marked [press]; figures computed from two documented figures are marked [arithmetic].

**Tone.** Entries are descriptions of documents, not findings of fact about any company. Coordinates mark the county or region, not an address.

## Licence

Data (`registry/`, `receipts/`, `research_notes/`, `data/`): CC BY 4.0. Code (`scrapers/`, `site/`): MIT. Climate TRACE data used by `climate_trace_match.py` is CC BY 4.0 from the Climate TRACE coalition.

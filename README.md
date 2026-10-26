# Compute Ledger

A public ledger of what records say about the physical, social and economic footprint of AI compute, site by site, worldwide. Permits, grid filings, court records, statistical offices, audits and trade data, laid beside what operators and governments say in public. Every number links to the document it came from. Good cases are entries too.

**202 entries · 44 countries and territories, plus EU-wide and global entries · 718 distinct linked documents · 2,984 figures in one validated table · 853 sites, one page each · 207 documented links in the chain from smelter to site · 71 open datasets · 3 receipts · 182 Virginia permits read twice · 129 Texas facilities from regulator records · metered electricity for Ireland's 11 licensed datacentres, two years, from the regulator** (as of 2026-10-24)

Live pages (GitHub Pages, served from `docs/`): the ledger at https://kn0wledgebfre3-sys.github.io/compute-ledger/ and the Climate TRACE brief at https://kn0wledgebfre3-sys.github.io/compute-ledger/brief.html. The handover package is in `data/climate_trace_seed/`.

The ledger is built on one rule: a company's statement is a claim, and a document from a regulator, court, grid operator, statistical office, auditor or customs authority is a record. The ledger shows both and states the gap in one line without adjectives.

## What is here

| Folder | What it holds |
|---|---|
| `registry/` | The entries, one JSON file per region plus `sources.json` (the open-data catalogue) and `guide.json` (the guided themes on the page). This is the dataset. |
| `sites/` | Site lists in seed form (not ledger entries): the worldwide seed list, Ireland's 40 sites from EPA records, the register backlog, the 43-row dedicated-supply column, the Texas site joins, Climate TRACE's schema notes, and `sites/metered/`, the transcriptions of the Irish annual environmental reports, the EPA emissions-inventory records and the public-utility documents, each row with its document URL. `sites/build/` holds the scripts that rebuild the seed and Ireland lists from their embedded, sourced values. |
| `pipeline/` | The Virginia and Texas permit extraction. `run_all.sh` reads the DEQ list and every permit PDF, extracts generator inventories and geocodes (run live 2026-10-21; the DEQ site blocks scripted PDF downloads, so PDFs are fetched by browser and passed with `--pdf-dir`). The extractor was fixed on 2026-10-22 after an independent second read and now agrees with it on 178 of 182 permits (`tests/`). `tx_fetch.py` rebuilds Texas from issued authorizations; `build_handover_assets.py` writes the handover's Climate TRACE asset files from the reviewed data; `build_metered.py` writes the metered-load files (unit conversions only). CI runs all of them on fixtures. |
| `receipts/` | Cases worked all the way down: the claim, a dated timeline of documents, the gap, the limits. Markdown for reading, JSON for the page. |
| `scrapers/` | Scripts that pull structured public files (US grid queues, federal plant data, UK register, Climate TRACE) so numbers come from a file, not from anyone's reading. See its README. |
| `research_notes/` | The working notes behind each region's entries, with the gaps that were found. |
| `site/` | `build_page.py` turns the registry, guide and receipts into one self-contained `index.html`. |
| `docs/` | The built ledger page (`index.html`) and the brief (`brief.html`), copied there by `site/build_page.py` so GitHub Pages can serve them. Do not edit by hand. |
| `data/` | `climate_trace_seed/` is the handover package (sites in Climate TRACE's asset schema, Ireland, the supply column, Virginia extraction, the Climate TRACE plant match, the metered figures from regulators and public utilities, the method, and the hostile reviews). Monthly scraper runs land in dated subfolders. |
| `documents/` | Browser-downloaded copies of public records whose hosts refuse automated access (the Wisconsin PSC final decisions for Oak Creek and Paris), with their original URLs. |
| `CONTRIBUTING.md`, `JURISDICTION_TEMPLATE.md` | How a figure enters the ledger, the two-reading rule, id and correction rules; the checklist for adding a country or state. |
| `ci_local.sh` | Runs the same checks as CI before you push. |
| `ROADMAP.md` | What is open in the package, the legs of the chain not yet traced (refiners, fabs, chips in motion, metered site power, the paper layer of certificates and offsets), the record each would rest on, and the three-week schedule after the Climate TRACE emails. |
| `review/` | The hostile reviews (handover, final package, ledger page), unedited except that local file paths and the names of the fetch and search tools were replaced, with their findings applied in the current files; the Virginia second reading (`va_reread/`); the Texas check; and `BROWSER_FETCH_LIST.csv`, the documents that need a person with a browser. |

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

Categories: `power fuel water heat_reuse moratorium grid_policy minerals fab ewaste land_biodiversity community public_money labor circularity accounting`.

Confidence: **high**: the record rests on record holders' documents that were read; **medium**: on press reports of records or partly read documents (company statements at most medium); **low**: mainly on press, NGO or company material. A second pass re-checked every medium and low entry against its original; the result is in `verification_status`.

## Contributing a correction or an entry

The correct response to an entry is a newer document, not a rebuttal.

1. Open a pull request that edits the entry in `registry/`. Put the document first in `record_sources`, update `record`, `gap` and `last_checked`, and say in the PR what the document shows.
2. For a new entry, use the schema above. No entry merges without a URL to a record. Company press releases are claims, not records. Mirrors of an actual document (a law firm's copy of a regulator decision, a library copy of a UN report) count as the document.
3. Validation runs on every PR: the registry must parse, ids must be unique, every entry needs a record URL, and the page must build.

Corrections sent from the page open a GitHub issue with the entry's id; they are reviewed into the registry by hand.

## Running the scrapers

See `scrapers/README.md`. They need a machine with ordinary internet access and, for the generation series, a free EIA API key in `EIA_API_KEY`. The monthly workflow in `.github/workflows/monthly-scrape.yml` runs them on the 3rd of each month and commits dated outputs under `data/`. Until the first live run, every scraper output in this repository is from fixture files and is labelled as such.

## Method

**What counts as a record.** A document produced by a regulator, court, grid operator, public utility, statistical office, auditor, UN body, registry or customs authority. A company's own statements are claims wherever they are published, including the narrative of its SEC filings; a sustainability figure becomes a record only where an independent assurance statement covers it and is public. A press report of a record is kept as such and marked; a press report of what a company or government says is that party's claim. Findings of NGOs and peer-reviewed studies are marked with their basis so they can be told apart from records.

**What a gap means.** Where the record and the claim differ, in one line. "None documented" means they agree or no claim was found. "Positive example" means the record shows a practice worth copying.

**What is excluded.** Third-party estimates and modelled footprints with no record behind them, advocacy press releases cited on their own, and anything without a URL to the underlying document. Figures the ledger computes itself (sums, shares, emissions from metered energy) are kept, with basis `derived` and their formula; estimates a record holder publishes (a regulator's forecast, a market monitor's counterfactual) are kept as that record holder's estimates.

**What a receipt is.** One case worked to the point where it cannot be waved away: every figure tied to a page of a document, the timeline reconstructed from dated documents, a short quote at most, no adjectives. Figures confirmed only through press are marked [press]; figures computed from two documented figures are marked [arithmetic].

**Tone.** Entries are descriptions of documents, not findings of fact about any company. In the ledger, an entry's coordinates mark the county or region, not an address; the site files (`sites/`, and the handover's asset files) carry document-level coordinates where a record gives them.

## Licence

Data (`registry/`, `sites/`, `receipts/`, `research_notes/`, `data/`, `review/`): CC BY 4.0. Code (`scrapers/`, `pipeline/`, `site/`): MIT. Climate TRACE data used by `climate_trace_match.py` is CC BY 4.0 from the Climate TRACE coalition.

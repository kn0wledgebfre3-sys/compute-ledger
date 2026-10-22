# Dedicated-supply column for the Climate TRACE handover: categories and the α rule

Built 2026-10-20. Outputs: `/home/claude/registry/dedicated_supply.json` (array, 43 rows) and `/home/claude/registry/dedicated_supply.csv` (same rows). Build script with every value embedded: `/tmp/claude-0/-home-claude/bd7e6ebd-b0e6-53fb-80f0-fee6cd3e5e1b/scratchpad/build_supply.py`.

## Why this column exists

Satellites can locate a data center, estimate its building volume, and (with a grid model) estimate the emissions of the electricity it draws. They cannot see *the contract*: whether a 2,262 MW gas plant was built and paid for to serve one campus, whether the nuclear next door is actually behind the meter, or whether "100% renewable" means a direct-supply line or an annual certificate purchase. That is the one field in a Scope 2 attribution that only the public record (regulator dockets, court rulings, grid-operator filings) can supply. This column collects it for every ledger site or cluster where such a record exists.

## Scope and rules of evidence

- Input: every entry in `north_america.json`, `europe.json`, `asia_pacific.json`, `latam_mena_africa.json`, `people_land_money.json` (99 entries; `minerals_ewaste.json` excluded). No sites were added.
- A row was written only where the entry's `record` or `claim` documents *how electricity is supplied*: a named plant, contract, tariff, policy obligation, metered grid share, or an explicit operator supply claim set against a regulator record. Entries that document water, heat reuse, noise, land, tax, labor, a moratorium, or a connection queue with nothing connected were left out (list of the 57 omitted ids is printed by the validation step; four of them are duplicates merged into another row and named in that row's `documented_by`).
- `documented_by` and `document_url` always point to a source already in the ledger entry. Two details were re-confirmed by fetching ledger-linked pages (FERC Susquehanna order 2-1, 300 -> 480 MW; Nevada CTT approval with NV Energy as physical deliverer). Nothing was added from outside the ledger.
- Where the only document is press or an operator statement, the row says so in `documented_by` and `confidence` is `low`.
- One ledger entry produced two rows (`ca-ab-aeso-large-load-byog-greenlight`: the AESO bring-your-own policy and the Greenlight plant are different arrangements for different loads). Every other entry maps to at most one row.

## Categories (`supply_type`)

| Category | Meaning in this column | Rows |
|---|---|---|
| `dedicated_fossil` | A gas (or diesel/gas) plant built, permitted, contracted or tolled for a named data center load, or the only capacity addition a utility documents for a data-center-driven need. The operator's renewable claim, if any, goes in `operator_claim` and does not change the category. | 9 |
| `dedicated_clean_firm` | A specific firm low-carbon resource contracted or allocated to the load: geothermal, nuclear PPA, hydro allocation, regulator-approved clean tariff. | 5 |
| `bring_your_own` | A policy that makes the load supply its own dispatchable capacity as a condition of connection (CRU Ireland; AESO BYOG). The fuel is not yet documented per site. | 2 |
| `grid_only` | Grid connection documented, nothing beyond it. Includes sites with large permitted diesel backup fleets (Loudoun, Alto Jahuel): backup is Scope 1, not supply. | 17 |
| `certificates_only` | Operator claims renewable supply with no physical arrangement in the record (I-RECs, guarantees of origin, balance-sheet renewable statutes, an unexplained "100% renewable"). | 4 |
| `on_site_fossil_unpermitted` | Documented generation before a permit existed (xAI Memphis). | 1 |
| `wheeled_renewable` | Contracted renewable energy delivered across a grid or by a direct-supply line (Teraco, Zhongwei, Morocco MoU). | 3 |
| `mixed` | Several resource types named for one load without shares (Georgia Power's certified portfolio; UAE campus "nuclear, solar and gas"). | 2 |

Strictness applied: a renewable certificate purchase is `certificates_only`; a gas plant approved to serve a named data center is `dedicated_fossil` even when the operator says "100% renewable"; a claim of "new dedicated plants" with no plant named stays `grid_only` with the claim recorded (Pecém).

## The α rule

For a site with annual electricity E (MWh), Scope 2 is attributed as

    E_site = α · EF_dedicated · E + (1 − α) · EF_grid(hourly, region) · E

where **α is the share of the site's electricity for which the public record documents a physical, named-load supply from a specific resource**, and EF_dedicated is that resource's emissions factor. On-site combustion (dedicated gas turbines, diesel run-hours) is additionally Scope 1 of the site and must not be double counted against the grid term.

How α is set, by category:

1. `dedicated_fossil` / `dedicated_clean_firm`, plant sized at or above the load and contracted or permitted to it (Hyperion, Homer City, Southaven, Susquehanna behind-the-meter tranche): **α = 1**.
2. Same categories, plant smaller than the load (Google/Fervo 115 MW): **α = min(1, MW_dedicated × CF_dedicated / (MW_site × CF_site))**.
3. Utility system plants that a regulator approved because of data-center load but did not tie to a named customer (Chesterfield, Georgia Power, Batam; Wisconsin partly): **α = 0 at the site**, because retail customers draw from the grid; the row carries an *incremental-load* α for cluster analyses, where the data-center-driven capacity is counted against the data-center load growth it was built for. Both values are in `alpha_note` so the handover can choose a method consistently.
4. `bring_your_own`: α is not knowable from the policy. Under CRU/2025236 the on-site plant must be separately metered and bid into markets, so it is a grid generator and the site's α stays 0 until metered self-supply hours are published; under AESO's gas-only bridging pool α = 1 on a gas EF for any admitted site.
5. `grid_only`: **α = 0**; use the regional hourly factor. Backup diesel is Scope 1 from run-hours.
6. `certificates_only`: **α = 0**. Annual certificates and balance-sheet renewable shares do not change physical supply. The claimed share is kept in `share_of_load` as a disclosure field only.
7. `wheeled_renewable`: α = 0 on a physical basis. If the attribution method chooses to credit contracted, grid-delivered renewables, α = contracted MWh / site MWh (Teraco ≈ 0.3 once commissioned; Zhongwei 0.65 per the stated target), and the choice must be applied uniformly, with hourly matching preferred where a counterparty publishes it.
8. `mixed`: α = 0 until shares are documented; the regional grid factor already blends the named fuels in the UAE case.
9. Front-of-meter PPAs with an existing, non-additional plant (Susquehanna after spring 2027): α = 1 only if the method credits firm bilateral PPAs hourly; otherwise 0. The row carries both.

Confidence (`high`/`medium`/`low`) reflects the document, not the α: `high` = regulator, court, grid operator or statutory text retrieved; `medium` = such a document exists but a key figure rests on press; `low` = press or operator statement only.

## Counts

43 rows across 42 ledger entries: grid_only 17, dedicated_fossil 9, dedicated_clean_firm 5, certificates_only 4, wheeled_renewable 3, mixed 2, bring_your_own 2, on_site_fossil_unpermitted 1. Confidence: high 18, medium 14, low 11.

Dedicated fossil capacity with a regulator or permit document behind it (α = 1 rows): Hyperion 2,262 MW, Homer City 4,678 MW, Southaven 1,200 MW, Greenlight 932 MW (customer unnamed), Memphis 247 MW permitted (100-421 MW unpermitted before). Dedicated clean firm with a document: Susquehanna up to 1,920 MW, Fervo 115 MW, Hydro-Québec 187 MW peak.

## Known weaknesses to fix on the next pass

- Four `dedicated_fossil` / `dedicated_clean_firm` rows rest on press or company statements only (Batam PPA, Lagos gensets, EcoCloud tariff, KenGen release); their α values are placeholders flagged in `alpha_note`.
- The Southaven 1.2 GW permit and the Wisconsin Paris/Red Oak Ridge terms were not retrieved from the regulator; figures are press-sourced inside otherwise documented rows.
- No row has an hourly-matching record. Every α above 0 is a capacity-and-contract judgement, not a metered share.
- `mw` mixes plant MW, contracted MW, connected MW and metered load; the `resource` string says which. Do not sum the column.


## Revision after two hostile reviews (2026-10-21)

Categories now: {'system_fossil_dc_driven': 3, 'grid_only': 19, 'on_site_fossil_unpermitted': 1, 'dedicated_fossil': 3, 'mixed': 2, 'dedicated_clean_firm': 5, 'bring_your_own': 2, 'dedicated_fossil_unnamed_load': 1, 'certificates_only': 4, 'wheeled_renewable': 3}. Added `system_fossil_dc_driven` (a utility system plant approved with datacenter load as the stated driver; alpha=0 at site level) and `dedicated_fossil_unnamed_load` (a merchant plant contracted to a datacenter customer the record does not name). Six rows were reclassified because the category rested on press or inference under this note's own strictness rule; each carries a `review_note`. Of the five `dedicated_clean_firm` rows, two rest on a regulator or filing (Susquehanna, Hydro-Québec) and three on press or company statements (Nevada, EcoCloud, Microsoft/G42 Olkaria) and are confidence low; the honest count of documented clean-firm supply is two.

# Attributing electricity emissions to a datacenter site

A method note to accompany the seed list. Written for Climate TRACE's methodology reviewers, in their terms.

## The problem

A datacenter emits almost nothing on site. Its footprint is the generation that serves it, which may be a plant next door, a plant three states away, or a mix that changes every hour. Climate TRACE already estimates the plant side. What does not exist is the consumer side: a facility-level estimate of the emissions a datacenter's load causes, from signals the operator does not control.

## What can be observed without the operator

1. **Site existence, footprint and growth.** Sentinel-2 and Landsat time series show the building envelope and its expansion. ECOSTRESS and Landsat thermal bands show a persistent heat signature. This is the same detection step Climate TRACE uses for other facility types.
2. **Capacity.** Air permits for backup generators are public in most jurisdictions and are sized to carry the full site load. Permitted generator MW is a floor on site capacity, often published before any announcement. Interconnection filings and utility commission orders give contracted MW. Statutory registers (EU EED, Germany's register) give reported IT load where operators comply.
3. **Load.** Not observable directly, but bounded. IT load × PUE ≈ facility load. PUE is bounded by climate and cooling type (regulators now publish caps: Singapore 1.3, China 1.25 for large sites, Germany 1.2 for new builds). Utilisation of connected capacity is reported in aggregate by some grid operators (AEMO: 27%; Ireland's CSO meters the national share). A site's load can be estimated as a range from permitted capacity, published utilisation statistics, and the thermal signature's intensity, with the range widening where only one of the three exists.
4. **Grid carbon intensity.** Hourly or sub-hourly marginal and average emissions factors by balancing area already exist for the US (EPA eGRID and real-time sources), Europe (ENTSO-E), Australia (AEMO) and others. Where a site has a documented dedicated supply (a regulator-approved geothermal tariff, an existing nuclear PPA restructured front-of-meter, a gas plant certified for the load), that supply replaces the grid factor for the contracted share.

## The estimate

For site *s* in balancing area *b* over period *t*:

```
E(s,t) = Σ_h  L(s,h) × [ α(s) × EF_dedicated(s,h) + (1 − α(s)) × EF_grid(b,h) ]
```

where `L(s,h)` is estimated hourly load (a range, not a point), `α(s)` is the share of load under a documented dedicated supply (0 where none), `EF_dedicated` is that supply's emissions factor (zero for geothermal, hydro or nuclear; the plant's Climate TRACE estimate for a dedicated gas plant), and `EF_grid` is the balancing-area factor. Datacenter load is flat, so for most sites the hourly sum collapses to annual load × annual average factor, with the hourly form mattering only where dedicated supply is intermittent.

Report the result as a range with a confidence rating, in Climate TRACE's existing style: the range from the load bounds, the confidence from how many of the three capacity signals (permit, filing, register) agree.

## What this is not

- It is not a claim about what the operator bought on paper. Annual renewable certificates do not change `EF_grid`. That is the point: the method measures physical supply, and a site that has contracted real dedicated clean supply gets credit for it through `α` and nothing else does.
- It is not precise. The honest output for most sites today is a factor-of-two range. The value is that it is independent, comparable across sites, and improves as registers fill.
- It does not cover embodied emissions (chips, construction) or water. Those belong to other facility types and other datasets; the ledger tracks them separately.

## What Climate TRACE already has, and what this adds

Climate TRACE's co-founder said in April 2026 that its database holds "the world's data centers" and that a hyperscaler dataset would be public soon; as of release 5.11.0 it is not. Release 5.11.0 also began reporting facility-level Scope 2 for oil and gas, aluminium and pulp and paper, using regional grid factors. So both the site inventory and the purchased-electricity pattern exist inside the coalition. The formula above is their existing Scope 2 approach applied to one more facility type; it is not a new method.

What the ledger adds is the part satellites cannot see:

- **Permitted capacity from air permits**, the earliest and most reliable public floor on site size, per site with the permit URL.
- **Dedicated-supply documentation** (`α` and `EF_dedicated` above): which sites have a regulator-approved geothermal tariff, a nuclear PPA, or a gas plant certified for their load. This is in utility-commission dockets, not imagery, and it is what separates a site with real clean supply from one with certificates.
- **The claim column**: what each operator says the site uses, next to the estimate, so the inventory can show the gap.
- **Water, land, public money and labor** for the same sites, which Climate TRACE does not track and would not need to, but which share the asset ids.

## Why Climate TRACE is the right home

- The detection step is theirs already. A datacenter is a large, flat-roofed, persistently warm building with a backup generator yard; the classifier exists.
- The plant-side factor is theirs already. Every dedicated gas plant in the ledger will have a Climate TRACE estimate once operating.
- The ownership file is theirs already. Operator, parent and ownership share are the fields that make a datacenter asset useful.
- The inputs they lack are permit-derived capacity, dedicated-supply contracts and operator claims per site, which the ledger produces in their asset schema (source_id, source_name, source_type, iso3_country, lat, lon, capacity, capacity_units, with the permit in `other1`/`other1_def` and the ownership file's `source_operator` and `parent_name` filled from public records).

## Minimum viable first release

Not a global estimate. One balancing area where every input exists: PJM (Northern Virginia). Permitted generator MW from Virginia DEQ's air-permit list for ~177 sites; contracted MW from Dominion's filings; hourly PJM emissions factors; Sentinel time series for footprint growth since 2019. Publish the range per site, the method, and the confidence. If it holds up under review for one region, extend to Dublin (CSO-metered share as a check), Singapore (IMDA-awarded capacity), and Johor.

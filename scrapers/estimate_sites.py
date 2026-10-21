#!/usr/bin/env python3
"""Worked-example estimator: site electricity emissions as a RANGE, in Climate TRACE's output shape.

Implements receipts/attribution_method.md:
  E(s) = L(s) x [ alpha(s) x EF_dedicated(s) + (1 - alpha(s)) x EF_grid(b) ]
with L(s) a range derived from the best available capacity signal, not a point.

Grid factors: EPA eGRID2023 Table 1 "Subregion Output Emission Rates" (produced 2025-03-27),
  https://www.epa.gov/system/files/documents/2025-06/summary_tables_rev2.pdf  (CO2e lb/MWh)
  SRVC 596.3 | RFCE 599.2 | RFCW 916.1 | ERCT 736.6 | US 770.9
  Converted to tCO2e/MWh by x 0.000453592.
  These are annual average, not marginal, factors. The method note says why that is acceptable for
  flat loads and where it is not.

Load range rules (documented in method note; all inputs must carry a URL):
  - If a REGISTER or FILING gives IT load (MW):       L = IT x PUE x util x 8760
        PUE range [1.15, 1.40] (bounded by published caps: DE 1.2 new, SG 1.3, CN 1.25, EU avg 1.36)
        util range [0.55, 0.85] for operating hyperscale (AEMO reports 27% of CONNECTED capacity across a
        pipeline with many idle connections; for an operating site the metered share is higher; the
        range is deliberately wide and stated)
  - If only a PERMIT gives backup generator MW:      facility load <= generator MW (generators are sized
        to carry full load); L = gen_MW x [0.35, 0.75] x 8760, the lower bound reflecting N+1 redundancy
        and the upper bound the site at high utilisation.
  - If only CONTRACTED MW from a utility filing:     L = contracted x [0.30, 0.80] x 8760 (contracted
        capacity leads real load by years; AEMO/TNB data show large gaps).
  Confidence: high if two independent signals agree within 30%; medium if one signal; low if only an
  operator statement.

Output: Climate TRACE asset-emissions rows with emissions_quantity = midpoint, plus other slots for
low/high, alpha, EF, inputs and confidence, so the range is never hidden behind the point.

Run: python3 estimate_sites.py --out out/     (uses the worked-example site table below)
"""
import argparse, csv, json, os, datetime

LB_TO_T = 0.000453592
EGRID = {"SRVC":596.3,"RFCE":599.2,"RFCW":916.1,"ERCT":736.6,"US":770.9}
EGRID_SRC = "EPA eGRID2023 Table 1, https://www.epa.gov/system/files/documents/2025-06/summary_tables_rev2.pdf"

# Five worked examples. Every input has a URL. These are the sites the ledger already documents best.
SITES = [
 {"source_id":"ledger-dc-us-va-chesterfield-load","source_name":"Data center load served by Chesterfield Energy Reliability Center (Dominion), Virginia",
  "iso3":"USA","lat":37.38,"lon":-77.38,"subregion":"SRVC",
  "signal":"contracted","mw":944,"mw_src":"Virginia SCC Final Order PUR-2025-00037 (2025-11-25): 944 MW gas peaker approved citing data center load; https://scc.virginia.gov/",
  "alpha":0.0,"ef_dedicated_lb":1135.0,"ded_note":"System plant, not site-dedicated: the 944 MW peaker serves Dominion's whole system with data center load as the stated justification (SCC order). Site-level alpha=0 (grid factor applies); the INCREMENTAL attribution is reported separately in other7 as the range at alpha=1 with AP-42 simple-cycle EF. See dedicated_supply.json alpha_note.",
  "claim":"Dominion reports ~40 GW of contracted data center capacity; operators in the cluster claim 100% renewable matching via certificates.",
  "ledger":"us-va-chesterfield-dominion-cerc-gas"},
 {"source_id":"ledger-dc-us-tn-memphis-xai-colossus","source_name":"xAI Colossus, South Memphis, Tennessee",
  "iso3":"USA","lat":35.05,"lon":-90.14,"subregion":"SRVC",
  "signal":"permit","mw":247,"mw_src":"Shelby County Health Dept permit 2025-07-02: 15 turbines, 247 MW; https://www.shelbytnhealth.com/",
  "alpha":0.5,"ef_dedicated_lb":1135.0,"ded_note":"On-site gas turbines ran ~1 year before permitting (100-421 MW per filings); alpha=0.5 as a documented partial self-supply, EF_dedicated = EPA AP-42 simple-cycle gas turbine ~1,135 lb CO2/MWh (https://www.epa.gov/air-emissions-factors-and-quantification/ap-42-compilation-air-emissions-factors, Ch. 3.1). Range widened accordingly.",
  "claim":"Operator describes turbines as temporary and being removed; regulator schedule allows some to run to 2027.",
  "ledger":"us-tn-memphis-xai-colossus-turbines"},
 {"source_id":"ledger-dc-us-nv-google-storey","source_name":"Google data centers, Storey County, Nevada (Clean Transition Tariff)",
  "iso3":"USA","lat":39.55,"lon":-119.45,"subregion":"US",
  "signal":"contracted","mw":115,"mw_src":"PUCN Docket 24-06014 ESA filed 2024-06-10: 115 MW from Fervo Corsac Station enhanced geothermal; https://puc.nv.gov/",
  "alpha":1.0,"ef_dedicated_lb":0.0,"ded_note":"Dedicated clean firm: regulator-approved geothermal supply for the contracted 115 MW; alpha=1 for that share, EF_dedicated=0. Site load beyond 115 MW (not documented) would take the NV grid factor (WECC NWPP/CAMX; US average used here as placeholder, flagged).",
  "claim":"Google: 24/7 carbon-free energy goal; this tariff is cited as firm clean supply.",
  "ledger":"us-nv-google-nv-energy-clean-transition-tariff"},
 {"source_id":"ledger-dc-us-pa-susquehanna-aws","source_name":"AWS campus at Susquehanna nuclear plant, Pennsylvania",
  "iso3":"USA","lat":41.09,"lon":-76.15,"subregion":"RFCE",
  "signal":"contracted","mw":1920,"mw_src":"Talen Energy FY2025 10-K: amended PPA up to 1,920 MW through 2042, front-of-meter from 2026; https://www.sec.gov/edgar",
  "alpha":1.0,"ef_dedicated_lb":0.0,"ded_note":"Dedicated clean firm: existing nuclear under PPA. alpha=1, EF_dedicated=0 for contracted volume. Note the attribution question (existing plant redirected, not new) is a policy debate; physically the supply is carbon-free. Front-of-meter structure means grid charges are paid.",
  "claim":"AWS: carbon-free nuclear supply for the campus.",
  "ledger":"us-pa-susquehanna-talen-aws-colocation"},
 {"source_id":"ledger-dc-us-wi-mount-pleasant-microsoft","source_name":"Microsoft Mount Pleasant, Wisconsin (We Energies gas build)",
  "iso3":"USA","lat":42.72,"lon":-87.89,"subregion":"RFCW",
  "signal":"contracted","mw":1100,"mw_src":"PSC Wisconsin docket 6630-CE-317: up to 1,100 MW simple-cycle gas, $1.205B, for large-load growth; https://apps.psc.wi.gov/",
  "alpha":0.0,"ef_dedicated_lb":1135.0,"ded_note":"System plant, not site-dedicated: PSC-approved 1,100 MW of simple-cycle gas for We Energies' system with Microsoft load as the stated driver. Site-level alpha=0 (RFCW grid factor, which is already gas/coal-heavy); INCREMENTAL attribution at alpha=1 with AP-42 EF reported in other7. See dedicated_supply.json alpha_note.",
  "claim":"Microsoft: closed-loop water pilot; 100% renewable matching via PPAs/certificates.",
  "ledger":"us-wi-mount-pleasant-microsoft-we-energies"},
]

def load_range(signal, mw):
    if signal=="register":  lo,hi = mw*1.15*0.55*8760, mw*1.40*0.85*8760
    elif signal=="permit":  lo,hi = mw*0.35*8760, mw*0.75*8760
    else:                   lo,hi = mw*0.30*8760, mw*0.80*8760
    return lo,hi

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="out"); a=ap.parse_args(); os.makedirs(a.out,exist_ok=True)
    today=datetime.date.today().isoformat(); rows=[]
    for s in SITES:
        lo,hi=load_range(s["signal"],s["mw"])
        ef_grid=EGRID[s["subregion"]]*LB_TO_T
        ef_ded=(s["ef_dedicated_lb"] if s["ef_dedicated_lb"] is not None else EGRID[s["subregion"]])*LB_TO_T
        ef=s["alpha"]*ef_ded+(1-s["alpha"])*ef_grid
        e_lo,e_hi=lo*ef,hi*ef; mid=(e_lo+e_hi)/2
        conf="medium" if s["signal"] in("contracted","permit") else "low"
        rows.append({"source_id":s["source_id"],"source_name":s["source_name"],"source_type":"datacenter","iso3_country":s["iso3"],
            "sector":"power","subsector":"electricity-consumption-datacenters (proposed)","start_time":"2025-01-01","end_time":"2025-12-31",
            "lat":s["lat"],"lon":s["lon"],"gas":"co2e_100yr","emissions_quantity":round(mid),"temporal_granularity":"annual",
            "activity":round((lo+hi)/2),"activity_units":"MWh (midpoint of range)","emissions_factor":round(ef,4),"emissions_factor_units":"tCO2e/MWh (blended)",
            "capacity":s["mw"],"capacity_units":f"MW ({s['signal']})","capacity_factor":"","capacity_factor_units":"",
            "other1":round(e_lo),"other1_def":"Emissions low bound tCO2e (load low bound x EF)",
            "other2":round(e_hi),"other2_def":"Emissions high bound tCO2e (load high bound x EF)",
            "other3":s["alpha"],"other3_def":"alpha: share of load under documented dedicated supply",
            "other4":round(ef_ded,4),"other4_def":"EF_dedicated tCO2e/MWh (0 for clean firm; AP-42 for dedicated gas; grid factor as floor if plant not yet in inventory)",
            "other5":round(ef_grid,4),"other5_def":f"EF_grid tCO2e/MWh, eGRID2023 subregion {s['subregion']}; {EGRID_SRC}",
            "other6":s["mw_src"],"other6_def":"Capacity signal and its document",
            "other7":s["ded_note"]+(f" Incremental (alpha=1) range: {round(lo*ef_ded):,}-{round(hi*ef_ded):,} tCO2e/yr." if s["alpha"]==0 and s["ef_dedicated_lb"] else ""),"other7_def":"Dedicated-supply documentation, how alpha/EF_dedicated were set, and the incremental range where a system plant was justified by this load",
            "other8":s["claim"],"other8_def":"Operator's public claim about this site's supply",
            "other9":conf,"other9_def":"Confidence: high=two independent capacity signals agree; medium=one regulator/permit signal; low=operator statement only",
            "other10":s["ledger"],"other10_def":"Compute Ledger entry id with full sources",
            "created_date":today,"modified_date":today})
    cols=list(rows[0].keys())
    with open(os.path.join(a.out,"worked_example_estimates.csv"),"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
    json.dump({"method":"receipts/attribution_method.md","grid_factors":EGRID,"grid_factor_source":EGRID_SRC,"rows":rows},open(os.path.join(a.out,"worked_example_estimates.json"),"w"),indent=1)
    for r in rows: print(f"{r['source_name'][:60]:60s}  {r['other1']:>10,} – {r['other2']:>10,} tCO2e/yr  alpha={r['other3']}  conf={r['other9']}")
    print(f"wrote {a.out}/worked_example_estimates.csv ({len(rows)} rows)")

if __name__=="__main__": main()

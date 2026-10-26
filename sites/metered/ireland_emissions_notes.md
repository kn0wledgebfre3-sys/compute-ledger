# Emissions computed for Ireland's licensed datacentres

The eleven EPA-licensed datacentres report metered electricity and the fuel they burned in their Annual Environmental Reports (`ireland_aer_transcribed.csv`). The reports give energy, not emissions. The ledger computes emissions from them with published factors (`ireland_emission_factors.csv`): SEAI's for grid electricity, and the EPA's own factors for EU ETS reports for fuel. The rows are in `measurements.csv` with basis `derived`, feed `sites/metered/ireland_emission_factors.csv`, and the formula in `metric_detail`.

**Location-based Scope 2** = metered electricity (GJ) / 3.6 x SEAI's greenhouse gas emissions per kWh of electricity consumed in Ireland that year (225.13 gCO2e/kWh for 2024, 199.29 for 2025). SEAI publishes the factor as each fuel's contribution; the ledger sums them and checks the sum on every build. This is the national average applied to each site's meter. It says nothing about any contract, certificate or supplier mix, which is what a market-based figure would reflect.

**CO2 from fuel burned on site** = gas oil (GJ) x 73.30 t CO2/TJ + natural gas (GJ) x the EPA's factor for that year (56.602 t CO2/TJ for 2024, 56.62 for 2025). The EPA's factors are on a net calorific value basis, and the reports do not say whether their gas GJ are gross or net, so gas gives a range: the high end takes the GJ as net, the low end takes them as gross and applies the EPA's gross-to-net multiplier (0.9026 for 2024, 0.9028 for 2025). The reports head the diesel row 'Light Fuel Oil'; the generators' GHG permits name gas oil, so the gas oil factor is used (the EPA's light fuel oil factor, 76.00, is about 4% higher). HVO is biogenic and counted as zero CO2. This is the fuel part of Scope 1 only: refrigerant losses, methane and nitrous oxide are not included.

| Year | Sites | Location-based Scope 2 (t CO2e) | CO2 from fuel (t) |
|---|---|---|---|
| 2024 | 11 (Drogheda from 8 August) | 807,024 | 27,261 to 30,076, of which Equinix DB5 26,417 to 29,232 |
| 2025 | 11 | 818,855 | 1,216 to 1,273 |

Equinix DB5's 2024 fuel CO2 is larger than its Scope 2 that year (18,999 t): its 2024 report says that, with full grid capacity delayed, the site operated its generators "as prime from February 2024 to November 2024 to support the IT load".

## Limits

- SEAI labels its 2025 factors provisional and revises its figures.
- SEAI's electricity factor is a national statistical average. An operator's own Scope 2 reporting may use other factors.
- Next check: several of these sites hold EU ETS greenhouse gas permits, so their verified CO2 emissions are in the EU Union Registry. Comparing the fuel figures here with those verified figures is the obvious test (ROADMAP).

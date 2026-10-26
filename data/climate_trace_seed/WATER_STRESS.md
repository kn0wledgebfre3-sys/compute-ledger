# Baseline water stress beside each located site

`water_stress.csv` gives, for each of the 305 sites in `site_register.csv` that have coordinates, the World Resources Institute's Aqueduct 4.0 **baseline water stress** for the sub-basin the point falls in: WRI's own fields `pfaf_id` (the HydroBASINS level 6 sub-basin), `bws_raw`, `bws_score` (0 to 5), `bws_cat` and `bws_label`. Each site's page shows the label.

**How.** WRI's data file (`aqueduct-4-0-water-risk-data.zip`, from https://www.wri.org/data/aqueduct-global-maps-40-data) was downloaded on 2026-10-24 and every site's point was joined to the `baseline_annual` polygons of its geodatabase with `pipeline/water_stress.py` (a point-in-polygon join, WGS84). Result: 304 of 305 sites have a value: 29 Extremely High (>80%), 99 High (40-80%), 40 Medium-High (20-40%), 38 Low-Medium (10-20%), 94 Low (<10%), 4 Arid and Low Water Use. One point (Pecém, Brazil) falls in no polygon at the coordinate's precision and has no value.

**Second reading.** Before the file was available, 97 of these sites had been looked up separately through an online copy of Aqueduct 4.0 (Esri Living Atlas, layer "Baseline Annual"). All 97 agree with the join on both sub-basin and category.

**What it is and is not.** Baseline water stress is the ratio of total water withdrawals to available renewable supply in the sub-basin, a property of the place, not of the site. It says nothing about what a datacenter itself withdraws; where a record gives a site's water use, it is in `measurements.csv`. For seven sites WRI's raw value is 9999, a code rather than a ratio; the category and label shown are WRI's.

**Licence and citation.** Aqueduct 4.0 is CC BY 4.0. Kuzma, S., M.F.P. Bierkens, S. Lakshman, T. Luo, L. Saccoccia, E.H. Sutanudjaja and R. Van Beek. 2023. "Aqueduct 4.0: Updated decision-relevant global water risk indicators." Technical Note. Washington, DC: World Resources Institute. https://doi.org/10.46830/writn.23.00061

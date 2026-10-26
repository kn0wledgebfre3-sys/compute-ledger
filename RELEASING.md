# Releasing a citable version

Each GitHub release is archived by Zenodo with its own DOI, and one concept DOI always points to the latest version. Zenodo reads `.zenodo.json` for the record; `CITATION.cff` gives the "Cite this repository" button on GitHub. Keep `version` the same in both.

## First time (about ten minutes)

1. Sign in at https://zenodo.org with the GitHub account that owns the repository (Log in, then "Sign in with GitHub").
2. Open https://zenodo.org/account/settings/github/, find `kn0wledgebfre3-sys/compute-ledger` and switch it on. If it is not listed, press "Sync now".
3. On GitHub: Releases, "Draft a new release", tag `v1.0.0` on `main`, title `Compute Ledger 1.0.0`, and paste the notes below. Publish.
4. Within a few minutes the record appears under Zenodo's GitHub page with a DOI badge. Copy the concept DOI (the one that says "Cite all versions").
5. Add the badge to the top of `README.md` and `doi:` to `CITATION.cff`, commit and push. That push does not need a new release.

## Later versions

Bump `version` in `CITATION.cff` and `.zenodo.json`, then publish a release tagged `vX.Y.Z`. Zenodo makes a new version under the same concept DOI.

## Notes for v1.0.0

First citable release of the Compute Ledger: public records on the physical, social and economic footprint of AI compute, site by site. Records are kept apart from claims; every figure links to the document it came from and says what kind of document that is.

What is in it:
- the registry of entries with their record and claim sources, and the guide and themes behind the public page;
- `measurements.csv`, one validated table of figures with unit, period, basis and the line each was read from, and `site_register.csv`;
- Virginia's datacenter air permits read twice, EPA inventory emissions, and the minimum generator hours they imply;
- Ireland's licensed datacentres: metered electricity, water and fuel from their annual reports, and the emissions computed from them with SEAI factors;
- the chain table of documented links from mine and refiner to site, power, fuel, water and tenant;
- topic feeds (crypto mining, nuclear, refiners, fabs, trade, hardware life, fuel and water, Singapore);
- the pipeline and checks that rebuild every output from its sources.

Counts for this version are at the top of `README.md`. Open items are in `ROADMAP.md`.

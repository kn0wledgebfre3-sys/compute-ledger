# Brief: fresh-eyes usability review (2 November 2026)

You have never seen this repository. Read only; change nothing.

The Compute Ledger is a ledger of public records (permits, regulator decisions, grid filings, statistics, audited reports) about datacenters and the AI compute supply chain, with company statements kept separate as claims. The website is built from `docs/`; data is CC BY 4.0, code MIT.

Question: is this good enough for other people to use, work with and build upon, and if not, what specifically stops them? Judge it as each of four people would, arriving cold from a link:

1. A data analyst at a climate NGO who wants to load the figures into their own pipeline.
2. A journalist who wants one checkable number with its source.
3. A researcher who wants to cite the dataset and reproduce a figure.
4. A developer or volunteer who wants to add a new jurisdiction or fix a figure.

For each, walk the path they would take from `README.md` and the website, and note every point of friction: which file is the data, column meanings, units, stable ids, versions and citation, how to run the build, how to contribute, folder names, stale files, and whether the README's counts and paths match what is there. Run the build in a copy if useful.

Report: a verdict per person; the 10 to 15 most important problems ranked by how much each blocks real use, each with the files, what goes wrong and a concrete fix, blockers separated from polish; and what is already good. Usability, structure and documentation only, not the subject matter.

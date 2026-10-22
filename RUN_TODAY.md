# Run sheet: 21 October 2026 (historical)

> Kept as the record of the 21 October run. Do not repeat step 5: the handover's asset files are now built from the reviewed data by `pipeline/build_handover_assets.py`, and Virginia's figures are the resolved second reading (`data/climate_trace_seed/VIRGINIA.md`).

One zip to download: **compute-ledger-repo.zip**. Everything is inside it, including the handover package. Budget: about two hours, most of it waiting.

You need: a laptop with normal internet, Python 3.10 or newer, and a terminal. Mac or Linux terminal commands are shown; on Windows use PowerShell and replace `./run_all.sh` with `bash run_all.sh` (Git Bash) or run the five Python files in order as listed in `run_all.sh`.

---

## Step 0. Unpack and prove it works offline (10 min)

```
unzip compute-ledger-repo.zip
cd repo
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r pipeline/requirements.txt -r scrapers/requirements.txt
cd pipeline
./run_all.sh --fixture
```

Last two lines must read `all outputs valid` and `== done.` If `pip` complains about pandas, run `pip install "pandas<3"` and retry. If `./run_all.sh` says permission denied: `chmod +x run_all.sh`.

## Step 1. Smoke test, live, ten permits (5 min)

```
./run_all.sh --limit 10
```

This fetches the real Virginia DEQ page, tries to locate and read the first ten permits, geocodes, merges. Watch for the line `rows with links`. Open `out/va_permits.csv`: if several rows have a generator count and MW, the live path works. Go to step 2.

If most rows say `pdf: not located`, the DEQ page is not exposing its PDF links to the script. Fix: open https://www.deq.virginia.gov/news-info/shortcuts/permits/air/issued-air-permits-for-data-centers in a browser, right-click five or six permit links, copy them (they look like `deq.virginia.gov/home/showpublisheddocument/25843/6386...`), and add a row for each to `fixtures/va_known_documents.csv` with the registration number from the page. Rerun step 1. It resumes and skips what it already has. If that works, a longer session of copying links is the main manual effort today; each one you add is a permit-grade capacity figure.

## Step 2. Full Virginia and Texas run (30–60 min)

```
./run_all.sh
```

Go make coffee. It pauses politely between downloads. Texas will mostly report `none` with a reason; that is expected. When it ends, open `out/handover_summary.json` and note `by_state.Virginia.with_coordinates_and_generator_mw`. That number goes in the email.

## Step 3. Spot-check ten rows (20 min)

Open `out/va_permits.csv`. Pick ten rows at random that have MW. For each, open the permit PDF (URL in the row) and check generator count and total MW match. Known traps (from the eight already checked): the first address on the cover is often the mailing address, not the site; the permittee can differ from the list name; a posted PDF can be older than the list date. Put anything wrong in the `review_note` column.

## Step 4. The strongest single row (5 min)

Download Climate TRACE's power package: https://climatetrace.org/downloads → Power → latest (a ZIP, about 100 MB). Then:

```
cd ../scrapers
python3 climate_trace_match.py --power-zip ~/Downloads/power.zip --out ../data/climate_trace_seed/
```

Open `../data/climate_trace_seed/climate_trace_matches.csv`. Any row with `method = name` is their own emissions estimate for a plant that a regulator's order ties to datacenter load. If Chesterfield or Oak Creek matched by name, that is one sentence in the email.

## Step 5. Assemble the package (5 min)

```
cd ..
cp pipeline/out/climate_trace/*.csv data/climate_trace_seed/
cp pipeline/out/handover_summary.json data/climate_trace_seed/virginia_extraction_summary.json
cp pipeline/out/va_permits.csv data/climate_trace_seed/
zip -j climate-trace-handover.zip data/climate_trace_seed/*
```

## Step 6. Push the repository (10 min)

Create an empty repository on GitHub (any name; public). Then from the `repo` folder:

```
git add -A
git commit -m "Live Virginia extraction $(date +%F)"
git remote add origin https://github.com/<you>/<name>.git
git branch -M main
git push -u origin main
```

Optional today: Settings → Secrets → add `EIA_API_KEY` (free key from https://www.eia.gov/opendata/register.php) so the monthly job can pull generation data.

## Step 7. Share the brief, then send (10 min)

1. Open the brief page (the "Datacenters for Climate TRACE" artifact), use its Share menu, make it viewable by link. Copy the link.
2. Email to Gavin McCormick (gavin@ClimateTRACE.org). Use the short draft. Fill in: your name and one line about you; the brief link; the repository link; the Virginia number from step 2 in the sentence about the backlog ("X Virginia permits extracted so far, generator count and MW per site"); the Climate TRACE match sentence from step 4 if you got one. Attach `climate-trace-handover.zip`.
3. Same day, the longer "pilot" draft to coalition@climatetrace.org with the same attachment and links, so the formal route is covered.

In both emails, these two sentences must be present, because the package says them: "Under N+1 the metered total bounds utilisation of permitted capacity at roughly 0.54–0.71; under 2N it imposes no bound" and "We had the package reviewed hostilely before sending; the review and our changes are included."

## If step 1 or 2 fails and you cannot fix it

Send anyway, today. Skip the Virginia number, keep the sentence "the extraction pipeline is tested on eight real permits and ready to run." Ireland, the supply column, the method and the review are the argument. Virginia is the offer.

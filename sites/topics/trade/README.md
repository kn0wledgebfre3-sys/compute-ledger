# Chips and servers across borders

Customs statistics for accelerators, servers and their parts, by product code, partner and period.

**The record.** Taiwan Ministry of Finance monthly trade statistics (exports by destination); US Census Bureau USA Trade Online (imports by port of entry); UN Comtrade for others. Product codes: HS 8471.50 and 8471.80 (servers and units), 8473.30 (parts), 8542.31 (processors), 8542.32 (memory).

**Figures here.** `trade_value` (money, as published, currency in `unit`) and `trade_quantity` (count or mass). Put the HS code, partner and direction in `metric_detail` ("exports, HS 8471.50, Taiwan to United States"). Subject is an entry (`entry_id`), not a site.

**The limit, stated as a finding.** The series ends at the country and the port. No public record links a shipment to the site it runs in; the ledger lays the series beside the permit series and says so.

**Status.** Waiting: see `review/INTAKE.csv`.

## How rows enter

`pipeline/build_measurements.py` reads every folder in `sites/topics/`: `sites.csv` rows join the site register with their `kind`, and `figures.csv` rows become measurements. Columns, vocabulary and rules are those of `sites/topics/crypto/` (see `CONTRIBUTING.md`): `value_as_published` must appear inside `quoted_line` exactly; `basis` `company_statement` makes the row a claim; every row needs the document's URL. Links between parties (who supplies whom) go in `sites/chain/edges.csv`, not here. A row added here is a first reading until `second_read` is `yes`.

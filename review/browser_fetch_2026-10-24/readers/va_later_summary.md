# Virginia DEQ: the 13 later permits, read and compared (2026-10-24)

Files: `fetched/fetched/from_downloads/` (listed per registration below). Each was read two ways: `pdftotext -layout` for every page, and page images (110 dpi) for every equipment-list page and the NOx-limit pages. No page lacked a text layer, so no OCR was run. Where the OCR'd text layers disagreed with the images (52629, 73370, 73717), the image was followed. Proposed rows are in `va_later_permits.csv` (same columns as `va_permits_resolved.csv`) and the unit groups are in `va_later_units.csv`.

## 1. Is each file the later permit?

| Reg. | File | First page shows | DEQ list date | Verdict |
|---|---|---|---|---|
| 52629 | 52629_DC_Permit (1).pdf | Reg. 52629, permit 2019-06-27, supersedes 2018-07-03 | 2019-06-27 | Later permit |
| 71804 | 7180404_DC_Permit.pdf | Reg. 71804, permit 2016-11-09 | 2016-11-09 | Later permit (new engines replace the 2009 set) |
| 73200 | 7320003_DC_Permit.pdf | Reg. 73200, letter 2007-10-18 + amended page 6 | 2007-10-18 | Minor amendment (opacity only), not a full permit |
| 73240 | 73240_DC_Permit (1).pdf | Reg. 73240, permit **2024-09-20** | 2024-09-24 | Date differs from the list. This is the permit the ledger already read (same date, same inventory). |
| 73370 | 7337016_DC_Permit.pdf | Reg. 73370, permit 2017-08-23, **ACC10 only** (Gazelle Ventures LLC) | 2017-08-23 | Later permit. It adds to the 2013 permits and does not supersede them. |
| 73643 | 7364305_DC_Permit.pdf | Reg. 73643, **letter** 2011-10-13 | 2011-10-13 | **Not a permit.** DEQ declined an emission-factor amendment. No inventory. |
| 73670 | 7367014_DC_Permit.pdf | Reg. 73670, renewal **Title V** permit, effective 2025-03-14 | 2025-03-14 | Later permit (Title V operating permit) |
| 73717 | 7371703_DC_Permit.pdf | Reg. 73717, permit 2019-05-29 (Zayo Group) | 2019-05-29 | Later permit. Covers new EG5-EG7 only. |
| 73977 | 7397702_DC_Permit.pdf | Reg. 73977, admin amendment 2013-08-19 (pages 1, 6, 10) | 2013-08-19 | Amendment, not a full permit |
| 74079 | 74079_DC_Permit (1).pdf | Reg. 74079, permit **2021-04-28** | 2025-08-21 | **Wrong file.** This is the 2021 permit already read. The 2025-08-21 permit is still unread. |
| 74156 | 74156_DC_Permit (1).pdf | Reg. 74156, permit 2018-11-08 | 2018-11-08 | Later permit. The ledger's "2018-09-10" is this letter's completeness date, so it is probably the same document. |
| 74190 | 74190_DC_Permit (1).pdf | Reg. 74190, permit 2020-07-16, supersedes 2020-02-19 | 2020-07-16 | Later permit. The ledger's "2020-02-19" is this permit's supersession date, so it is probably the same document. |
| 74265 | 742653_DC_Permit (1).pdf | Reg. 74265, permit 2026-08-13, supersedes 2024-10-22 | 2026-08-13 | Later permit. The ledger's row already matches it exactly, so it is probably the same document. |

Several of the "earlier" dates in `va_permits_resolved.csv` came from automatic extraction and are not the permit dates. For 74156 the extracted date is the completeness date. For 74190 and 74265 it is the date the permit supersedes. For 73670 it is an original-permit date; `va_permit_unit_rates.csv` gives the permit read as 2017-10-04. For these registrations the "not the latest" flag was mostly an artefact of those dates.

## 2. Earlier vs later, per registration

"Later alone" means the units listed in the later document. "Registration after" is what the ledger row should hold once the later document is applied (this is what `va_later_permits.csv` carries).

| Reg. | Earlier (ledger): date / units / MW | Later doc: date | Later alone: units / MW | Registration after: units / MW | Δ units | Δ MW | NOx limits in va_permit_unit_rates.csv |
|---|---|---|---|---|---|---|---|
| 52629 | 2018-07-03 / 92 / 272.0 | 2019-06-27 | 92 / 272.0 | 92 / 272.0 | 0 | 0 | not in file |
| 71804 | 2009-02-27 / 8 / 7.35 | 2016-11-09 | 8 / 8.595 | 8 / 8.595 | 0 | +1.245 | not in file |
| 73200 | 2006-10-19 / 7 / 14.0 | 2007-10-18 (amendment) | inventory not restated (EGU1-EGU7) | 7 / 14.0 | 0 | 0 | not in file |
| 73240 | 2024-09-20 / 12 / 24.0 | 2024-09-20 (same permit) | 12 / 24.0 | 12 / 24.0 | 0 | 0 | not in file |
| 73370 | 2013-08-27 / 147 / 316.98 | 2017-08-23 (ACC10) | 18 / 40.5 | 165 / 357.48 | +18 | +40.5 | Existing ACC2-ACC7 limits unchanged. ACC10 adds 18 units at 5.1 lb/hr (SCR) / 7.3 lb/hr (no SCR), which the file lacks |
| 73643 | 2007-12-19 / 22 / 55.0 | 2011-10-13 (letter) | none | 22 / 55.0 (carried) | 0 | 0 | not in file |
| 73670 | 2017-10-04 mNSR (ledger date "2014-01-29") / 143 / 283.175 | 2025-03-14 (Title V) | 139 / 274.675 | 139 / 274.675 | −4 | −8.5 | Per-unit limits unchanged. Counts change: Gen2.5 CAT 19→18, Gen 1-45 (45)→Gen 1-44 (44), Building D 11→9 |
| 73717 | 2009-01-15 / 5 / 4.275 | 2019-05-29 | 3 / 6.75 | 8 / 11.025 (additive, medium) | +3 | +6.75 | not in file |
| 73977 | 2012-04-09 / 4 / 10.0 | 2013-08-19 (amendment) | inventory not restated (G-1..G-4) | 4 / 10.0 | 0 | 0 | not in file |
| 74079 | 2021-04-28 / 17 / 38.25 | 2021-04-28 (wrong file) | 17 / 38.25 | 17 / 38.25 | 0 | 0 | not in file |
| 74156 | "2018-09-10" / 24 / 66.0 | 2018-11-08 | 24 / 66.0 | 24 / 66.0 | 0 | 0 | not in file |
| 74190 | "2020-02-19" / 17 / 46.5 | 2020-07-16 | 17 / 46.5 | 17 / 46.5 | 0 | 0 | not in file |
| 74265 | "2024-10-22" / 121 / 272.25 | 2026-08-13 | 121 / 272.25 | 121 / 272.25 | 0 | 0 | not in file |

What changed, in brief:
- **71804**: All eight engines were replaced. Five Cummins 900 ekW and three 1,365 ekW units take the place of five 750 kW Cummins and three 1,200 kW Waukesha. The permittee is now Meridian Science 7990, LLC.
- **73370**: ACC10 at 21744 Sir Timothy Drive adds 18 CAT 3516C units at 2,250 ekW (prime rating). The ACC2-ACC7 figures (2013) still stand.
- **73670**: The Title V lists 139 units, four fewer than the 2017 mNSR permit: Gen 45, Gen2.5-19, and two Building D units are missing. Conditions 6 and 7 say "fifty-three 2,000 kW" (Gen1-44, 46-54) and "twenty-one 2,500 kW" (Gen2.5-1..18, 20-22). The permit gives no reason. A Title V lists units that operate, so the four were probably never built or have been removed, while the 2017 mNSR permit is still the underlying construction permit.
- **73717**: The site has passed from Visa to Zayo at 1764A Old Meadow Lane. The 2019 permit lists only the new EG5-EG7 (3 × 2,250 ekW) and does not mention EG1-EG4 or LS1. I treated those units as still permitted because the numbering continues at EG5.
- **52629**: Units and MW are unchanged. EG57-EG92 now have SCR, and the permit adds hour limits of 100 h (maintenance and testing) and 500 h (all purposes) per unit, plus a 1,070,750 gal/yr fuel cap for all units.

## 3. Statewide totals

I summed `va_permits_resolved.csv` the way VIRGINIA.md describes: the registrations with a resolved MW, which excludes the '5' row and 74331. The result is **182 permits, 13,973 units, 33,692.737 MW**, which confirms the published figures. Excluding transitory units it is 13,922 units and 33,586.787 MW.

Net change from applying the later documents as proposed:

| | Permits | Units | MW | Units excl. transitory | MW excl. transitory |
|---|---|---|---|---|---|
| Current | 182 | 13,973 | 33,692.737 | 13,922 | 33,586.787 |
| Change | 0 | **+17** | **+39.995** | +17 | +39.995 |
| Proposed | 182 | 13,990 | 33,732.732 (≈33,733) | 13,939 | 33,626.782 |

The change is 71804 +1.245 MW; 73370 +18 units and +40.5 MW; 73670 −4 units and −8.5 MW; 73717 +3 units and +6.75 MW. None of the later documents lists transitory or non-emergency units.

Sensitivity to the choices above:
- If the 2009 units at 73717 were removed, the change is +12 units and +35.72 MW (13,985 / 33,728.457).
- If 73670 is kept at the mNSR figures (143 / 283.175), the change is +21 units and +48.495 MW (13,994 / 33,741.232).
- If the 73370 ACC10 permit were wrongly treated as replacing ACC2-ACC7, the total would drop by 129 units and 276.48 MW. It should not be applied that way.

The headline rounds to **≈33.73 GW**. That sits inside the stated band of 33.4 to 33.9 GW.

## 4. Effect on the metered files (per-engine NOx limits)

- **73670** (`va_permit_unit_rates.csv` rows and `va_generator_hours.csv`): the per-unit NOx limits are unchanged (48.1, 38.86, 4.47, 11.58, 38.61, 7.83, 4.99 lb/hr), and so are the building-group annual limits (86.7 + 80.4 = 167.1 tpy). If the Title V counts are adopted, three unit_count values change: Gen2.5 CAT 19 → 18; "Gen 1 to Gen 45" → Gen 1 to Gen 44 (44); Building D 11 → 9. The summed rate falls from 5,475.95 to 5,311.77 lb/hr. Minimum full-load-equivalent hours rise from 2.51 to 2.59 h (2020) and from 6.24 to 6.43 h (2023), and the facility limit becomes 62.9 h instead of 61. The NEI years (2020, 2023) fall before the 2025 Title V, so it is not known whether the four missing units existed then.
- **73370**: the ACC2-ACC7 limits are unchanged. ACC10 is missing from the unit-rates file. Its limits as written are 5.1 lb/hr with SCR and 7.3 lb/hr without SCR (0.0292 and 0.136 lb/gal), with 12.4 tpy for all 18 combined. Adding 18 × 7.3 lb/hr gives 7,570.88 lb/hr, and the hours become 5.14 h (2020) and 12.61 h (2023) instead of 5.23 and 12.83. However, the NEI addresses match ACC2-ACC5, and ACC10 is at a different street, so it is probably best left out of the NEI match. Note also that the lb/hr and lb/gal values in the ACC10 table do not match each other at the fuel rate implied by the SCR pair: 0.136 lb/gal × about 175 gal/hr is about 24 lb/hr, not 7.3. I have recorded the 7.3 as written.
- None of the other 11 registrations is in `va_permit_unit_rates.csv` or `va_generator_hours.csv`.

## 5. Open items

1. **74079**: the 2025-08-21 permit is still needed; the downloaded file is the 2021 permit.
2. **73643**: the later item is a letter. The governing permit is the NSR permit dated 2009-08-28 (amended 2010-04-29), and neither it nor the 2010 amendment has been read. The ledger's 22 × 2,500 ekW come from the 2007 permit, so I lowered confidence to medium.
3. **73717**: it is not confirmed whether EG1-EG4 and LS1 (Visa, 2009) are still permitted. Confidence is medium.
4. **73670**: choose between the Title V figure (139 / 274.675) and the mNSR figure (143 / 283.175). This is a convention choice.
5. **73240**: the DEQ list date (2024-09-24) does not match the document date (2024-09-20). There may be a second item on the list for that registration.
6. **52629**: the EG57-EG92 rating cell is blank in the 2019 table. I took 3,000 ekW from the same model in the row above, as the 2018 reading did.
7. **73200 and 73977**: these are partial amendments, so the inventories are carried from the earlier permits and not re-read from a full permit.

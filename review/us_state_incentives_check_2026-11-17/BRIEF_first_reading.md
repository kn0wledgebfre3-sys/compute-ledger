# Brief: what US states give up for datacenters, and what they get, from official evaluations

You are a reader for a public ledger built only from public documents. It keeps **records** (documents from regulators, auditors, courts, statistics offices, legislatures and their evaluation offices) apart from **claims** (what companies, industry groups and politicians say). This task is records: official evaluations and statutory reports on state tax incentives for datacenters.

The ledger already holds Virginia's JLARC evaluation (2024), Georgia's Department of Audits and Accounts evaluation (December 2025, revised January 2026) and a Texas State Auditor audit of JETI agreements. Do **not** redo those.

Look for, in this order of priority: Texas (the Comptroller's reporting on the data center sales tax exemption, Tax Code 151.359, and any Legislative Budget Board or Comptroller evaluation), Washington (JLARC tax preference review of the data center sales and use tax exemption), Arizona (Joint Legislative Budget Committee or Department of Revenue reporting on the computer data center program), Illinois (the Department of Commerce's annual report on the Data Center Investment program, which lists certified datacenters), Ohio (Tax Credit Authority datacenter sales tax exemptions, or a state evaluation), Minnesota (Department of Revenue tax expenditure report or Office of the Legislative Auditor on the datacenter exemption), Nevada (GOED abatement reports for datacenter projects), Indiana, Iowa, Oregon (enterprise zone or Strategic Investment Program reports naming datacenters), Nebraska, Mississippi, Utah, and any other state where an auditor or legislative evaluation office has evaluated a datacenter incentive.

For each document you find, record each of these that it states, with the page or table and a short verbatim quote (at most 15 words):
- forgone revenue: amount, period (fiscal year or years), and whether state, local or both;
- number of datacenters, companies or projects that qualified;
- jobs: and say exactly which kind the document means (direct permanent jobs at datacenters, construction jobs, or jobs "supported" in the wider economy by a model), with the period;
- capital investment stated;
- the evaluator's own assessment of return (for example revenue returned per dollar forgone, or whether the incentive changed location decisions), quoted;
- for site-level lists (Illinois, Nevada, Oregon), the number of sites listed and two or three example rows (company, site, investment, jobs), and the document's URL.

Rules: official documents only (an auditor's or evaluation office's report, a revenue department's report, an agency's statutory report). A news article may lead you to the document but is not the source. Quote at most a short phrase. Neutral wording: no adjectives about companies, states or the incentives. If a figure is not stated, write "not stated"; do not compute or estimate. Pace yourself: about 80 web searches in all.

Write the result with Python's csv module to `result_money.csv` in this folder, one row per figure, columns:
`state, document_title, publisher, document_date, url, figure (forgone_revenue|qualifying_count|jobs_direct|jobs_construction|jobs_supported|capital_investment|return_assessment|site_list), value_as_published, period, scope (state|local|both|n/a), page_or_table, short_quote, notes`

Then reply with a short summary: which states have an official evaluation or report, the headline figures, and which states you looked for and found nothing official.

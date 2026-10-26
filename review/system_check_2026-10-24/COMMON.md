# Pre-publication check of the Compute Ledger: common rules for every reviewer

You are one of several independent reviewers. You have not seen how this work was built. Your job is to find faults before it is published; assume there are some. Report what you find; do not fix anything.

- Today is 2026-10-24. Do not write a later date. Anything dated after today in the data is itself a fault.
- Do not modify the repository or the package drafts. Write only into your own output folder.
- Fetch documents from their links (read long ones to the end), and search only to find a document's current location.
- The project: a public ledger of AI compute's physical, social and economic footprint, built only from public documents. Rules are in CONTRIBUTING.md; read it first. In short:
  - A **record** is a document from a regulator, court, grid operator, public utility, statistics office, auditor (an auditor-assured company figure counts), registry or customs. A **claim** is what a company or government says in its own voice (press releases, sustainability reports without assurance, SEC narrative), and press reports are neither unless they quote a record.
  - Every figure keeps the text it was read from; the period, unit and the thing it is attached to (site, unit, party) must match the document, not just the number.
  - Figures the ledger computes are basis `derived` and show their formula.
  - The tone is neutral: nobody is villainised, nothing is speculated, gaps are stated as "no record found yet", not as wrongdoing.
- Severity for each problem: `error` (a wrong fact, number, attachment, date, link or classification that a reader would rely on), `inconsistency` (two places in the project disagree), `weak` (true but overstated, unclear, or a source weaker than presented), `style` (tone, wording, typo).
- Be concrete: quote the exact text in the project and, where relevant, the exact text in the document. A problem without a quote is not useful.

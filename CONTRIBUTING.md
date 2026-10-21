# Contributing

## Where help matters most

In order:

1. **Fetch the originals in Asia.** 28 entries have `verification_status: not_found`. Most are in Johor, India, Korea, Taiwan and China's western hubs, where the government document exists but is not online in a form a browser can reach. If you can obtain the actual Johor approvals, the Indian parliamentary reply, the Korean grid-impact decisions or the Taipower notice, open a PR with the document (or a stable link to it) and the corrected entry.
2. **Thin regions.** Vietnam, Thailand, the Philippines, Colombia, Poland and Switzerland have no entries. Seed from `registry/sources.json`, not from press.
3. **Receipts.** Candidates already in the registry with the documents half-gathered: Chesterfield (Virginia gas peaker), Memphis (xAI turbines), Johor (water rejections), Aragón (Amazon approvals vs regional consumption). Follow the structure of an existing receipt exactly.
4. **Run the scrapers live** and report what broke. Column names and URLs move; the scripts fail loudly and say what they found.
5. **Read it as an expert.** A grid engineer, a water-rights lawyer, a journalist who has filed FOI requests. Open an issue for anything that is wrong, overstated, or missing a known document.

## Rules

- A record needs a URL to the document. A press report of a document is medium confidence and says so.
- Quote at most a short phrase; paraphrase the rest.
- No adjectives in `gap`. No accusations anywhere. If a company responded in good faith, that response is part of the record.
- Never remove an entry. If a record is superseded, add the newer document and update the entry.
- Never change an `id`.
- Set `last_checked` on every entry you touch.

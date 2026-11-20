"""What changed, from CHANGELOG.md: docs/changes.html and docs/feed.xml (Atom).

The changelog is the one source. Each release is a `## <version> (<date>)` heading, or `## Unreleased`; within one, each
round is a `### <day> <month> <year>` heading; each change is one line starting `- **<title>.**`. A change with no round
heading takes its release's date. Both files are built from those lines alone, so they change only when the changelog
does, and CI compares them with the committed copies.

Called by site/build_graph_pages.py (build(gp)).
"""
from __future__ import annotations

import csv
import datetime as dt
import html
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
TAG = "tag:kn0wledgebfre3-sys.github.io,2026:compute-ledger"

CSS = """
/* what changed */
.chg h2{font-size:clamp(19px,2.2vw,23px);margin-top:36px}
.chg article{border-top:1px solid var(--rule);padding:14px 0 4px;max-width:80ch}
.chg article h3{font-family:var(--display);font-stretch:90%;font-size:18px;margin:0 0 6px;line-height:1.25}
.chg article h3 a{color:var(--ink);text-decoration:none}
.chg article h3 a:hover,.chg article h3 a:focus-visible{text-decoration:underline}
.chg article p{font-size:16px;margin:0 0 8px}
.chg code{font-family:var(--mono);font-size:.86em;overflow-wrap:anywhere}
.feedline{font-family:var(--mono);font-size:13px;color:var(--ink-2)}
.chg article:target{background:var(--paper-2);box-shadow:-10px 0 0 var(--paper-2),10px 0 0 var(--paper-2);border-left:3px solid var(--accent);padding-left:10px}
.chg .relsum p{font-size:16px;color:var(--ink-2);max-width:80ch}
"""


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70].strip("-")


SUMMARIES: dict = {}  # a release's own paragraphs (its summary), by release date; filled by parse()


def parse() -> list[dict]:
    """Every change, newest first: {date, release, title, text, anchor}. A release's paragraphs before its changes are its summary."""
    out, release, rel_date, day = [], "", "", ""
    SUMMARIES.clear()
    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\S+)(?: \((\d{4}-\d{2}-\d{2})\))?\s*$", line)
        if m:
            release, rel_date, day = m.group(1), m.group(2) or "", ""
            continue
        if release and rel_date and line.strip() and not line.startswith(("-", "#")):
            SUMMARIES.setdefault(rel_date, (release, []))[1].append(line.strip())
            continue
        m = re.match(r"^### (\d{1,2} [A-Z][a-z]+ \d{4})\s*$", line)
        if m:
            day = dt.datetime.strptime(m.group(1), "%d %B %Y").date().isoformat()
            continue
        if line.startswith("### "):
            raise SystemExit(f"CHANGELOG.md: a round heading must be a date such as '### 20 November 2026', not {line!r}")
        m = re.match(r"^- \*\*(.+?)\*\*\s*(.*)$", line)
        if m and release:
            date = day or rel_date
            if not date:
                raise SystemExit(f"CHANGELOG.md: {m.group(1)!r} is under {release} with no date: put it under a '### <date>' heading")
            out.append({"date": date, "release": release, "title": m.group(1).rstrip(".").strip(), "text": m.group(2).strip()})
        elif line.startswith("- ") and release:
            raise SystemExit(f"CHANGELOG.md: a change must start '- **<title>.**': {line[:60]!r}")
    seen = set()
    for c in out:
        a = f"{c['date']}-{slug(c['title'])}"
        if a in seen:
            raise SystemExit(f"CHANGELOG.md: two changes on {c['date']} have the same title {c['title']!r}")
        seen.add(a)
        c["anchor"] = a
    return sorted(out, key=lambda c: c["date"], reverse=True)  # stable: within a day, the changelog's own order


@lru_cache(maxsize=1)
def entry_ids() -> frozenset:
    with open(ROOT / "data" / "climate_trace_seed" / "entries.csv", newline="", encoding="utf-8") as f:
        return frozenset(r["id"] for r in csv.DictReader(f))


def inline(text: str, site_url: str, repo: str) -> str:
    """The changelog's markdown, as HTML: `code` (linked when it names a file or page that exists) and **bold**."""
    def code(m):
        s = m.group(1)
        p = s.rstrip("/")
        if s in entry_ids():
            return f'<a href="index.html#{html.escape(s)}"><code>{html.escape(s)}</code></a>'
        if re.fullmatch(r"[\w./-]+", s) and not s.startswith("docs/") and (ROOT / "docs" / s).is_file():
            return f'<a href="{html.escape(s)}"><code>{html.escape(s)}</code></a>'
        if re.fullmatch(r"[\w.-]+\.\w+", s) and (ROOT / s).is_file():
            return f'<a href="{repo}/blob/main/{html.escape(s)}"><code>{html.escape(s)}</code></a>'
        if "/" in s and re.fullmatch(r"[\w./-]+", s) and (ROOT / p).exists():
            if p.startswith("docs/") and (ROOT / p).is_file() and p.endswith(".html"):
                href = p[5:]
            else:
                href = f"{repo}/{'tree' if (ROOT / p).is_dir() else 'blob'}/main/{p}"
            return f'<a href="{html.escape(href)}"><code>{html.escape(s)}</code></a>'
        return f"<code>{html.escape(s)}</code>"
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for x in parts:
        if x.startswith("`") and x.endswith("`") and len(x) > 1:
            out.append(code(re.match(r"`(.+)`", x)))
        else:
            out.append(re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(x, quote=False)))
    return "".join(out)


def long_date(d: str) -> str:
    x = dt.date.fromisoformat(d)
    return f"{x.day} {x.strftime('%B %Y')}"


def page(changes: list[dict], gp) -> str:
    e = gp.e
    P = ""
    body = [gp.nav(P, ["What changed"], ""),
            f'<p class="eyebrow">{len(changes)} changes, from the first citable release (1.0.0) on</p><h1>What changed</h1>',
            '<p class="lede">Each round of work on the ledger, newest first: what was added, corrected or checked, and where to find it. '
            'The same list is in <a href="https://github.com/kn0wledgebfre3-sys/compute-ledger/blob/main/CHANGELOG.md">the changelog</a>, '
            'which this page is built from.</p>',
            '<p class="feedline">Follow it in a feed reader: <a href="feed.xml">feed.xml</a> (Atom). Every corrected figure keeps its old link, '
            'which leads to the figure that replaced it. Within a day, changes follow the changelog, which groups them by subject, not by the hour.</p>', '<div class="chg">']
    day = None
    for c in changes:
        if c["date"] != day:
            day = c["date"]
            rel = f" · version {c['release']}" if c["release"] != "Unreleased" else ""
            body.append(f'<h2 id="d-{day}">{e(long_date(day))}<span class="m">{e(rel)}</span></h2>')
            if day in SUMMARIES:
                body.append('<div class="relsum">' + "".join(f"<p>{inline(x, gp.bs.SITE_URL, gp.REPO)}</p>" for x in SUMMARIES[day][1]) + "</div>")
        body.append(f'<article id="{e(c["anchor"])}"><h3><a href="#{e(c["anchor"])}">{e(c["title"])}</a></h3>'
                    f'<p>{inline(c["text"], gp.bs.SITE_URL, gp.REPO)}</p></article>')
    body.append("</div>")
    desc = "Each round of work on the Compute Ledger, newest first: what was added, corrected or checked."
    return gp.head("What changed · Compute Ledger", desc, P, path="changes.html") + "\n".join(body) + "\n" + gp.foot(P, lines=False, path="changes.html", name="what changed", about=False)


def feed(changes: list[dict], gp) -> str:
    site = gp.bs.SITE_URL
    x = lambda s: html.escape(s, quote=True)  # noqa: E731
    out = ['<?xml version="1.0" encoding="utf-8"?>', '<feed xmlns="http://www.w3.org/2005/Atom">',
           "<title>Compute Ledger: what changed</title>",
           "<subtitle>Each round of work on a public ledger of AI compute's footprint, built from public records.</subtitle>",
           f'<link rel="self" type="application/atom+xml" href="{site}feed.xml"/>', f'<link rel="alternate" type="text/html" href="{site}changes.html"/>',
           f"<id>{site}feed.xml</id>", f"<updated>{changes[0]['date']}T00:00:00Z</updated>",
           "<author><name>Compute Ledger contributors</name></author>", "<rights>CC BY 4.0</rights>"]
    rel_entries = [{"date": d, "title": f"Version {r}, released", "anchor": f"d-{d}",
                    "text": " ".join(x for x in ps if not x.endswith(":")) + f" The changes it brought are listed under {long_date(d)}."}  # a line that leads into the list stays on the page
                   for d, (r, ps) in SUMMARIES.items()]
    for c in sorted(changes + rel_entries, key=lambda c: c["date"], reverse=True):
        content = inline(c["text"], site, gp.REPO)
        content = re.sub(r'href="(?!https?://)([^"]+)"', lambda m: f'href="{site}{m.group(1)}"', content)  # a feed reader has no page to resolve from
        out += ["<entry>", f"<title>{x(c['title'])}</title>", f'<link rel="alternate" type="text/html" href="{site}changes.html#{x(c["anchor"])}"/>',
                f"<id>{TAG}:{x(c['anchor'])}</id>", f"<updated>{c['date']}T00:00:00Z</updated>",
                f'<content type="html">{x("<p>" + content + "</p>")}</content>', "</entry>"]
    out.append("</feed>")
    return "\n".join(out) + "\n"


def build(gp) -> dict:
    changes = parse()
    if not changes:
        raise SystemExit("CHANGELOG.md: no changes found")
    return {"changes.html": page(changes, gp), "feed.xml": feed(changes, gp)}

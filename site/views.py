"""Three views across the whole ledger, built from its tables alone: records beside claims, coverage by country and topic,
and the timeline of the documents behind it.

  records-and-claims.html  the quantities a record and a claim both state (sites/views/same_quantity.csv, chosen by hand),
                           then every subject where both sides give the same kind of figure
  coverage.html            one row per country, one cell per topic: a figure from a record, only claims, or nothing found,
                           counted exactly as each country's own page counts it
  timeline.html            every dated document, by the date the ledger records for it, with a chart of documents per year

Called by site/build_graph_pages.py (build(ctx, gp)), which writes the files and checks them in CI.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAIRS = ROOT / "sites" / "views" / "same_quantity.csv"
ALIASES = ROOT / "data" / "climate_trace_seed" / "measurement_id_aliases.csv"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SHORT_TOPIC = {"Electricity used": "Electricity used", "Grid connection and capacity": "Grid and capacity",
               "Clean-energy purchases and certificates": "Clean-energy purchases", "Greenhouse gases": "Greenhouse gases",
               "Generators, fuel and air pollution": "Generators and air", "Water": "Water", "Money, jobs and prices": "Money and jobs",
               "Land, buildings and number of sites": "Land and buildings", "Minerals, fuel supply, hardware and waste": "Minerals and waste",
               "Other counts, shares and durations": "Other"}
FIRST_YEAR = 2015  # the timeline's chart puts documents dated before this year in one column

CSS = """
/* views: records beside claims, coverage, timeline */
:root{--c-rec:#00806A;--c-claim:#BF4A1A;--c-both:#6A5FC1}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--c-rec:#2FA38C;--c-claim:#D9703F;--c-both:#8C85E0}}
:root[data-theme="dark"]{--c-rec:#2FA38C;--c-claim:#D9703F;--c-both:#8C85E0}
.vw-note{background:var(--paper-2);padding:10px 14px;margin:14px 0 0;font-size:15px;max-width:80ch}
.vw table td{font-size:14.5px;overflow-wrap:break-word}
.vw table td.m,.vw table td .m{font-size:12.5px}
.vw .side{min-width:220px}
.vw td.about{min-width:8em}
.vw .empty{margin:10px 0 0}
.vw tr[hidden],.cov tr[hidden]{display:none!important}
.vw .fv strong{font-family:var(--display);font-size:17px}
.vw .fv .cv{font-family:var(--mono);font-size:12px;color:var(--ink-2);margin-left:6px}
.vw ul.fl{list-style:none;padding:0;margin:0}
.vw ul.fl li{padding:0 0 8px;margin:0 0 8px;border-bottom:1px dashed var(--rule)}
.vw ul.fl li:last-child{border-bottom:0;margin-bottom:0;padding-bottom:0}
.vw th.rh,.vw td.rh{border-left:3px solid var(--rec);padding-left:8px}
.vw th.ch,.vw td.ch{border-left:3px solid var(--claim);padding-left:8px}
.vw .count{margin:6px 0 0}
.cov{border-collapse:separate;border-spacing:2px;width:auto;min-width:100%}
.cov th{white-space:normal;vertical-align:bottom;font-size:11px;line-height:1.25;padding:4px 3px 6px;min-width:64px;max-width:84px}
.cov th.cn,.cov td.cn{position:sticky;left:0;background:var(--paper);z-index:1;min-width:130px;max-width:170px;text-align:left}
.cov td{padding:0;border:0;vertical-align:middle;text-align:center;font-family:var(--mono);font-size:12.5px}
.cov td.cn{padding:6px 8px 6px 0;font-family:var(--body);font-size:14.5px;border-bottom:1px solid var(--rule)}
.cov td.cl a,.cov td.cl span{display:block;padding:9px 4px;min-height:36px;text-decoration:none;color:var(--ink)}
.cov td.k-rec{background:color-mix(in srgb,var(--c-rec) 22%,var(--paper))}
.cov td.k-claim{background:color-mix(in srgb,var(--c-claim) 16%,var(--paper));box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--c-claim) 45%,var(--paper))}
.cov td.k-calc a{white-space:nowrap;font-size:11.5px}
.tag.both{color:var(--c-both);border-color:var(--c-both)}
.tl td.v{white-space:nowrap}
#tl-counts td.v{min-width:0}
.cov td.k-calc{background:color-mix(in srgb,var(--calc) 16%,var(--paper));box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--calc) 45%,var(--paper))}
.cov td.k-none{background:var(--paper-2);color:var(--ink-2)}
.cov td.k-none span{color:var(--ink-2)}
.cov td.cl a:hover,.cov td.cl a:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.cov td.n{font-family:var(--mono);font-size:12px;padding:6px 4px;border-bottom:1px solid var(--rule)}
.cov tfoot td{font-family:var(--mono);font-size:12px;color:var(--ink-2);padding:8px 4px;border-top:1px solid var(--rule)}
.cov th button{all:unset;cursor:pointer;display:block;text-align:center;width:100%}
.cov th button::after{content:" ↕";opacity:.45}
.cov td.cl a{scroll-margin-left:140px}
.cov th button:focus-visible{outline:2px solid var(--accent)}
.cov th[aria-sort] button::after{content:" ↓";color:var(--accent);opacity:1}
.vw-key{display:flex;flex-wrap:wrap;gap:6px 18px;margin:12px 0 0;font-family:var(--mono);font-size:12.5px;color:var(--ink-2)}
.vw-key i{display:inline-block;width:14px;height:14px;vertical-align:-2px;margin-right:6px;border-radius:2px}
.vw-key i.r{background:color-mix(in srgb,var(--c-rec) 22%,var(--paper));border:1px solid var(--c-rec)}
.vw-key i.c{background:color-mix(in srgb,var(--c-claim) 16%,var(--paper));border:1px solid var(--c-claim)}
.vw-key i.n{background:var(--paper-2);border:1px solid var(--rule)}
.vw-key i.k{background:color-mix(in srgb,var(--calc) 16%,var(--paper));border:1px solid var(--calc)}
.vw-key i.be{background:var(--c-both)}
.tl-chart .b-both{fill:var(--c-both)}
.vw-key i.br{background:var(--c-rec)} .vw-key i.bc{background:var(--c-claim)}
.tl-chart{position:relative;margin:14px 0 0;border:1px solid var(--rule);background:var(--paper);padding:8px 0 0}
.tl-chart svg{display:block;width:100%;height:230px}
.tl td.doc{min-width:11em}
.tl-chart text{font-family:var(--mono);font-size:11px;fill:var(--ink-2)}
.tl-chart .grid line{stroke:var(--rule);stroke-width:1}
.tl-chart .b-rec{fill:var(--c-rec)} .tl-chart .b-claim{fill:var(--c-claim)}
.tl-chart g.col{cursor:pointer;outline:none}
.tl-chart g.col:hover path.bar,.tl-chart g.col:focus-visible path.bar{filter:brightness(1.15)}
.tl-chart g.col.on .hit{fill:color-mix(in srgb,var(--accent) 12%,transparent)}
.tl-chart g.col:focus-visible .hit{stroke:var(--accent);stroke-width:2}
.tl-tip{position:absolute;pointer-events:none;background:var(--paper);border:1px solid var(--rule);padding:6px 9px;font-family:var(--mono);font-size:12px;color:var(--ink);box-shadow:0 2px 8px rgba(0,0,0,.12);white-space:nowrap;z-index:3}
.tl-tip b{font-size:14px} .tl-tip .k{display:inline-block;width:12px;height:2px;vertical-align:3px;margin-right:6px}
.tl tr.yr th{font-family:var(--display);font-size:19px;color:var(--ink);padding-top:22px;border-bottom:2px solid var(--ink)}
.tl td.d{white-space:nowrap;font-family:var(--mono);font-size:12.5px;color:var(--ink-2)}
@media (max-width:640px){.cov th.cn,.cov td.cn{min-width:118px;max-width:130px}.cov th{min-width:64px}.cov td.cl a{scroll-margin-left:126px}
 .vw table.cards thead{display:none}.vw table.cards,.vw table.cards tbody,.vw table.cards tr,.vw table.cards td{display:block;width:auto;min-width:0}
 .vw table.cards tr{border-bottom:1px solid var(--rule);padding:10px 0}.vw table.cards td{border:0;padding:3px 0}
 .vw table.cards td.side{padding-left:10px;margin-top:6px}.vw table.cards td[data-label]::before{content:attr(data-label);display:block;font-family:var(--mono);font-size:11.5px;color:var(--ink-2)}
 .vw table.cards tr.yr th{display:block}.vw table.tl.cards td.d,.vw table.tl.cards td.tg{display:inline-block;margin-right:10px}}
"""


def build(ctx, gp) -> dict:
    """The three pages, keyed by their path under docs/."""
    return {"records-and-claims.html": records_and_claims(ctx, gp), "coverage.html": coverage(ctx, gp), "timeline.html": timeline(ctx, gp)}


# --------------------------------------------------------------------------------------------------- shared

def subject_countries(ctx, r) -> list[str]:
    """The countries a figure's subject is in, as the subject's own page gives them."""
    nid = {"site": "site:", "entity": "org:", "entry": "entry:"}[r["subject_type"]] + r["subject_id"]
    return [c for c in ctx.g.nodes.get(nid, {}).get("country", "").split(";") if c]


def country_name(ctx, gp, cc) -> str:
    n = ctx.g.nodes.get(f"country:{cc}")
    return n["name"] if n else gp.bs.COUNTRY.get(cc, cc)


def fmt_num(v) -> str:
    x = float(v)
    s = f"{x:,.3f}".rstrip("0").rstrip(".")
    return s


def fmt_date(d: str) -> str:
    p = d.split("-")
    if len(p) == 3:
        return f"{int(p[2])} {MONTHS[int(p[1]) - 1]} {p[0]}"
    if len(p) == 2:
        return f"{MONTHS[int(p[1]) - 1]} {p[0]}"
    return d


NUMBER_WORDS = {"million", "billion", "thousand", "trillion", "bn", "mn", "m", "k", "about", "approximately", "approx", "around", "up", "to",
                "over", "under", "more", "than", "less", "nearly", "almost", "some", "roughly", "at", "least", "most", "c", "ca", "circa", "and"}
UNIT_WORDS = {"gal": "gallons", "Mgal": "million gallons", "Mgal/yr": "million gallons a year", "MGD": "million gallons a day", "gpd": "gallons a day",
              "L": "litres", "ML": "megalitres", "GL": "gigalitres", "GL/yr": "gigalitres a year", "MLD": "megalitres a day", "L/day": "litres a day",
              "m3": "m³", "m3/day": "m³ a day", "m3/yr": "m³ a year", "m3/s": "m³ a second", "hm3": "cubic hectometres", "t": "tonnes", "kt": "thousand tonnes",
              "Mt": "million tonnes", "ha": "hectares", "acre": "acres", "km2": "km²", "m2": "m²", "m2_land": "m² of land", "sqft": "square feet",
              "short_ton": "short tons", "h": "hours", "days": "days", "months": "months", "years": "years"}


def names_unit(shown: str) -> bool:
    """whether a value as printed names its unit: anything left once the digits, signs and number words are taken out"""
    rest = [w for w in re.sub(r"[\d.,~≈<>+\-–()]+", " ", shown).lower().split() if w not in NUMBER_WORDS]
    return bool(rest)


def unit_words(u: str) -> str:
    return UNIT_WORDS.get(u, u.replace("_", " "))


def figure_cell(ctx, gp, r, P, conv=""):
    e = gp.e
    did = ctx.url_doc.get(r["source_url"])
    title = gp.gk.short(r["source_title"] or r["source_url"], 90)
    doc = f'<a href="{P}doc/{did}.html">{e(title)}</a>' if did else e(title)
    what = "computed from records" if r["basis"] == "derived" else r["basis"].replace("_", " ")
    twice = " · read twice" if r["second_read"] == "yes" else ""
    shown = gp.bs.as_published(r)
    if not conv and r["value"] and r["unit"] not in ("count", "pct", "other", "other_currency", "money_per_unit") and not names_unit(shown):
        conv = f"{fmt_num(r['value'])} {unit_words(r['unit'])}"  # the printed value names no unit: give the ledger's
    cv = f'<span class="cv">= {e(conv)}</span>' if conv else ""
    return (f'<div class="fv"><strong>{e(shown)}</strong>{cv}</div><div>{e(r["metric_detail"])}</div>'
            f'<div class="m">{e(gp.bs.period(r))} · {e(what)}{twice}</div>'
            f'<div class="m">{doc} · {e(r["source_publisher"])} · <a href="{P}explore.html#{e(r["measurement_id"])}">the figure</a></div>')


FILTER_JS = """<script>
(()=>{const tb=document.getElementById('%(tbody)s'),q=document.getElementById('%(q)s'),n=document.getElementById('%(n)s'),
sels=[...document.querySelectorAll('select[data-for="%(tbody)s"]')],rows=[...tb.querySelectorAll('tr[data-row]')];
function f(){const t=q.value.trim().toLowerCase();let v=0;
rows.forEach(r=>{const ok=sels.every(s=>!s.value||(' '+(r.dataset[s.dataset.f]||'')+' ').includes(' '+s.value+' '))&&(!t||r.textContent.toLowerCase().includes(t));r.hidden=!ok;if(ok)v++;});
n.textContent=v.toLocaleString()+' of '+rows.length.toLocaleString()+' shown';const z=document.getElementById('%(tbody)s-none');if(z)z.hidden=v>0;}
[q,...sels].forEach(x=>x.addEventListener('input',f));f();})();
</script>"""


def select(gp, tbody, f, label, opts):
    e = gp.e
    name = re.sub(r"^(Every|Any) ", "", label)  # the control's name, not its first option ('Every country' -> 'Country')
    return (f'<select data-for="{tbody}" data-f="{f}" aria-label="{e(name[:1].upper() + name[1:])}"><option value="">{e(label)}</option>'
            + "".join(f'<option value="{e(v)}">{e(t)}</option>' for v, t in opts) + "</select>")


# --------------------------------------------------------------------------------------------------- records beside claims

def load_pairs(ctx):
    meas = {r["measurement_id"]: r for r in ctx.meas}
    alias = {}
    if ALIASES.exists():
        with open(ALIASES, newline="", encoding="utf-8") as f:
            alias = {r["retired_measurement_id"]: r["measurement_id"] for r in csv.DictReader(f)}

    def get(i):
        seen = set()
        while i not in meas and i in alias and i not in seen:
            seen.add(i)
            i = alias[i]
        if i not in meas:
            raise SystemExit(f"{PAIRS.relative_to(ROOT)}: no figure has the id {i}")
        return meas[i]

    out = []
    with open(PAIRS, newline="", encoding="utf-8") as f:
        for k, p in enumerate(csv.DictReader(f), 2):
            where = f"{PAIRS.relative_to(ROOT)} row {k}"
            if None in p or None in p.values():
                raise SystemExit(f"{where}: not four fields (a field with a comma must be in quotes)")
            a, b = get(p["record_id"]), get(p["claim_id"])
            if a["side"] != "record":
                raise SystemExit(f"{where}: {a['measurement_id']} is on the {a['side']} side, not a record")
            if b["side"] != "claim":
                raise SystemExit(f"{where}: {b['measurement_id']} is on the {b['side']} side, not a claim")
            if (a["subject_type"], a["subject_id"], a["metric"]) != (b["subject_type"], b["subject_id"], b["metric"]):
                raise SystemExit(f"{where}: the two figures are not about the same subject and metric")
            if not p["both_describe"].strip():
                raise SystemExit(f"{where}: both_describe is empty")
            out.append((a, b, p["both_describe"].strip(), p["note"].strip()))
    return out


def periods(gp, a, b):
    pa, pb = gp.bs.period(a), gp.bs.period(b)
    if pa == pb and pa != "not stated":
        return "same", f"both {pa}"
    if pa == "not stated" or pb == "not stated":
        return "unstated", f"record {pa} · claim {pb}"
    return "different", f"record {pa} · claim {pb}"


def records_and_claims(ctx, gp):
    e, P = gp.e, ""
    pairs = load_pairs(ctx)
    groups = defaultdict(lambda: {"rec": [], "claim": []})
    for r in ctx.meas:
        groups[(r["subject_type"], r["subject_id"], r["metric"])]["claim" if r["side"] == "claim" else "rec"].append(r)
    both = {k: v for k, v in groups.items() if v["rec"] and v["claim"]}
    subjects = {(t, i) for t, i, _ in both}
    # the hand-picked pairs
    prow = []
    for a, b, what, note in sorted(pairs, key=lambda x: (periods(gp, x[0], x[1])[0] != "same", ctx.g.nodes.get({"site": "site:", "entity": "org:", "entry": "entry:"}[x[0]["subject_type"]] + x[0]["subject_id"], {}).get("name", "").lower())):
        conv_a = conv_b = ""
        if a["unit"] != b["unit"] and a["canonical_unit"] and a["canonical_unit"] == b["canonical_unit"] and a["value_canonical"] and b["value_canonical"]:
            u = unit_words(a["canonical_unit"])
            conv_a = f"{fmt_num(a['value_canonical'])} {u}".strip() if a["unit"] != a["canonical_unit"] else ""
            conv_b = f"{fmt_num(b['value_canonical'])} {u}".strip() if b["unit"] != b["canonical_unit"] else ""
        kind, ptxt = periods(gp, a, b)
        cs = " ".join(subject_countries(ctx, a))
        prow.append(f'<tr data-row data-p="{kind}" data-c="{e(cs)}"><td class="about">{ctx.subject(a["subject_type"], a["subject_id"], P)}'
                    f'<div class="m">{e(", ".join(country_name(ctx, gp, c) for c in cs.split()))}</div></td>'
                    f'<td><strong>{e(gp.bs.metric_label(a["metric"]))}</strong><div>{e(what)}</div><div class="m">{e(ptxt)}</div>'
                    + (f'<div class="m">{e(note)}</div>' if note else "") + "</td>"
                    f'<td class="side rh" data-label="Record">{figure_cell(ctx, gp, a, P, conv_a)}</td><td class="side ch" data-label="Claim">{figure_cell(ctx, gp, b, P, conv_b)}</td></tr>')
    n_same = sum(1 for a, b, _, _ in pairs if periods(gp, a, b)[0] == "same")
    pair_tbl = ('<div class="filters">' + '<input id="pq" type="search" placeholder="Filter these pairs" aria-label="Filter these pairs">'
                + select(gp, "prows", "p", "Any period", [("same", "The same period"), ("different", "Different periods"), ("unstated", "A period not stated")])
                + '</div><p class="m count" id="pn" aria-live="polite"></p>'
                '<div class="tw"><table class="cards"><thead><tr><th>About</th><th>What both describe</th><th class="rh">Record</th><th class="ch">Claim</th></tr></thead>'
                f'<tbody id="prows">{"".join(prow)}</tbody></table></div><p class="none empty" id="prows-none" hidden>Nothing matches these filters.</p>'
                + FILTER_JS % {"tbody": "prows", "q": "pq", "n": "pn"})
    # every subject where both sides give the same kind of figure
    grow = []
    topics_used, countries_used = Counter(), Counter()

    def gkey(k):
        t, i, m = k
        nm = ctx.g.nodes.get({"site": "site:", "entity": "org:", "entry": "entry:"}[t] + i, {}).get("name", i)
        return (nm.lower(), gp.TOPIC_OF.get(m, gp.LAST_TOPIC), m)

    for k in sorted(both, key=gkey):
        t, i, m = k
        v = both[k]
        ti = gp.TOPIC_OF.get(m, gp.LAST_TOPIC)
        cs = subject_countries(ctx, v["rec"][0])
        topics_used[ti] += 1
        for c in cs:
            countries_used[c] += 1
        order = lambda rs: sorted(rs, key=lambda r: (-(int((r["period_end"] or r["period_start"] or "0")[:4] or 0)), r["measurement_id"]))  # noqa: E731
        rl = "".join(f"<li>{figure_cell(ctx, gp, r, P)}</li>" for r in order(v["rec"]))
        cl = "".join(f"<li>{figure_cell(ctx, gp, r, P)}</li>" for r in order(v["claim"]))
        grow.append(f'<tr data-row data-c="{e(" ".join(cs))}" data-t="{ti}"><td class="about">{ctx.subject(t, i, P)}'
                    f'<div class="m">{e(", ".join(country_name(ctx, gp, c) for c in cs))}</div></td>'
                    f'<td><strong>{e(gp.bs.metric_label(m))}</strong><div class="m">{e(gp.TOPICS[ti][0])}</div>'
                    f'<div class="m">{len(v["rec"])} on the record side, {len(v["claim"])} claimed</div></td>'
                    f'<td class="side rh" data-label="On the record side"><ul class="fl">{rl}</ul></td><td class="side ch" data-label="Claimed"><ul class="fl">{cl}</ul></td></tr>')
    c_opts = sorted(((c, country_name(ctx, gp, c)) for c in countries_used), key=lambda x: x[1].lower())
    t_opts = [(str(ti), gp.TOPICS[ti][0]) for ti in sorted(topics_used)]
    group_tbl = ('<div class="filters"><input id="gq" type="search" placeholder="Filter: a company, a site, a word" aria-label="Filter this list">'
                 + select(gp, "grows", "c", "Every country", c_opts) + select(gp, "grows", "t", "Every topic", t_opts)
                 + '</div><p class="m count" id="gn" aria-live="polite"></p>'
                 '<div class="tw"><table class="cards"><thead><tr><th>About</th><th>Kind of figure</th><th class="rh">On the record side</th><th class="ch">Claimed</th></tr></thead>'
                 f'<tbody id="grows">{"".join(grow)}</tbody></table></div><p class="none empty" id="grows-none" hidden>Nothing matches these filters.</p>'
                 + FILTER_JS % {"tbody": "grows", "q": "gq", "n": "gn"})
    body = [gp.nav(P, ["Records and claims"], "records-and-claims.html"), '<div class="vw">',
            f'<p class="eyebrow">Records and claims · {gp.plural(len(pairs), "pair")} of the same quantity · {len(both)} rows with both sides</p>',
            '<h1>Records beside claims</h1>',
            '<p class="lede">The ledger keeps what records show apart from what companies and governments say. This page puts the two side by side, '
            'each figure with its document. On the left, the record side: figures read from a record, such as a regulator’s decision, a permit, a filing, '
            'an assured report or an official statistic, from a report of one, or computed by the ledger from records. On the right, claims. '
            'The ledger does not say which is right, and a difference is not a finding that anything is wrong.</p>',
            gp.section("The same quantity, from both sides", "rec",
                       f"Pairs in which a record and a claim state the same thing, chosen by hand and checked: {n_same} for the same period, "
                       f"{len(pairs) - n_same} for different periods or with a period not stated, which the row says. "
                       f'Where the two print different units, both are also given in one unit. The list is in <a href="{gp.REPO}/blob/main/sites/views/same_quantity.csv">sites/views/same_quantity.csv</a>.',
                       pair_tbl),
            gp.section("Every subject where both sides give the same kind of figure", "",
                       f"{len(both)} rows, one for each subject and kind of figure ({gp.plural(len(subjects), 'subject')}, {gp.plural(len({k[2] for k in both}), 'kind of figure', 'kinds of figure')}): "
                       "a site, an organisation or an entry with at least one figure on the record side and at least one claim of the same kind.",
                       '<p class="vw-note">Figures in the same row share a subject and a kind of figure, not always a meaning: a row of shares can hold the share of '
                       'sites in a region on one side and the share of requests approved on the other. Read each line before comparing.</p>' + group_tbl),
            "</div>"]
    return (gp.head("Records beside claims · Compute Ledger", "Where a record and a claim state the same kind of figure about the same subject, side by side, each with its document.", P,
                    path="records-and-claims.html")
            + "\n".join(body) + "\n" + gp.foot(P, lines=False, path="records-and-claims.html", name="records beside claims", about=False))


# --------------------------------------------------------------------------------------------------- coverage

def coverage(ctx, gp):
    e, P = gp.e, ""
    ccs = sorted((n["node_id"][8:] for n in ctx.g.nodes.values() if n["type"] == "country"), key=lambda c: country_name(ctx, gp, c).lower())
    nt = len(gp.TOPICS)
    rows, col_rec, col_cl, col_calc, n_any = [], Counter(), Counter(), Counter(), 0
    for cc in ccs:
        name = country_name(ctx, gp, cc)
        sites, _, _, _, figs = gp.country_scope(ctx, cc)
        by = gp.topic_counts(figs)
        cells, n_with = [], 0
        for i, (t, _) in enumerate(gp.TOPICS):
            c = by.get(i, Counter())
            rec, calc, cl = c["record"], c["computed"], c["claim"]
            href = f'{P}explore.html?country={e(cc)}&amp;topic={i}'
            if rec:
                href += '&amp;what=record'
                n_with += 1
                col_rec[i] += 1
                extra = (f", {calc:,} computed" if calc else "") + (f", {cl:,} claimed" if cl else "")
                tip = f"{name} · {t}: {gp.plural(rec, 'figure')} from records{extra}"
                cells.append(f'<td class="cl k-rec" data-v="{rec}"><a href="{href}" title="{e(tip)}" aria-label="{e(tip)}">{rec:,}</a></td>')
            elif calc and not cl:
                col_calc[i] += 1
                tip = f"{name} · {t}: {gp.plural(calc, 'figure')} computed by the ledger from records; none read directly from a record yet"
                cells.append(f'<td class="cl k-calc" data-v="0"><a href="{href}" title="{e(tip)}" aria-label="{e(tip)}">computed</a></td>')
            elif cl or calc:
                col_cl[i] += 1
                tip = f"{name} · {t}: only {gp.plural(cl + calc, 'figure')} {'claimed' if cl and not calc else 'claimed or computed'}; no record found yet"
                cells.append(f'<td class="cl k-claim" data-v="0"><a href="{href}" title="{e(tip)}" aria-label="{e(tip)}">claim</a></td>')
            else:
                tip = f"{name} · {t}: no public record found yet"
                cells.append(f'<td class="cl k-none" data-v="-1"><span title="{e(tip)}" aria-label="{e(tip)}">·</span></td>')
        placed = sum(1 for s in sites if s["lat"])
        n_any += 1 if n_with else 0
        rows.append(f'<tr data-row data-name="{e(name.lower())}" data-n="{n_with}"><td class="cn"><a href="{P}country/{e(cc)}.html">{e(name)}</a></td>'
                    + "".join(cells) + f'<td class="n" data-v="{n_with}">{n_with} of {nt}</td><td class="n" data-v="{len(sites)}">{len(sites):,}'
                    + (f' <span class="m">({placed:,} on the map)</span>' if sites else "") + "</td></tr>")
    head_cells = "".join(f'<th scope="col" title="{e(t)}"><button type="button" data-col="{i + 1}">{e(SHORT_TOPIC.get(t, t))}</button></th>'
                         for i, (t, _) in enumerate(gp.TOPICS))
    foot_cells = "".join(f'<td>{col_rec[i]} with a record' + (f'<br>{col_calc[i]} computed only' if col_calc[i] else "") + (f'<br>{col_cl[i]} with only claims' if col_cl[i] else "") + '</td>' for i in range(nt))
    zero = len(ccs) - n_any
    js = """<script>
(()=>{const t=document.getElementById('cov'),tb=t.tBodies[0],q=document.getElementById('cq'),n=document.getElementById('cn'),srt=document.getElementById('cs');
const rows=[...tb.rows];let col=0,prev='name';
function val(r,c){return c?+r.cells[c].dataset.v:0}
function order(){const s=srt.value;let rs=rows.slice();
 if(col){rs.sort((a,b)=>val(b,col)-val(a,col)||a.dataset.name.localeCompare(b.dataset.name));}
 else if(s==='most'){rs.sort((a,b)=>b.dataset.n-a.dataset.n||a.dataset.name.localeCompare(b.dataset.name));}
 else if(s==='fewest'){rs.sort((a,b)=>a.dataset.n-b.dataset.n||a.dataset.name.localeCompare(b.dataset.name));}
 else rs.sort((a,b)=>a.dataset.name.localeCompare(b.dataset.name));
 rs.forEach(r=>tb.appendChild(r));
 t.querySelectorAll('thead th').forEach((h,i)=>{if(i&&col===i)h.setAttribute('aria-sort','descending');else if(i)h.removeAttribute('aria-sort');});}
function filt(){const v=q.value.trim().toLowerCase();let k=0;rows.forEach(r=>{const ok=!v||r.cells[0].textContent.toLowerCase().includes(v);r.hidden=!ok;if(ok)k++;});
 n.textContent=k+' of '+rows.length+' shown';document.getElementById('cov-none').hidden=k>0;}
t.querySelectorAll('thead button').forEach(b=>b.addEventListener('click',()=>{const c=+b.dataset.col;col=(col===c)?0:c;srt.value=col?'topic':prev;order();}));
srt.addEventListener('input',()=>{col=0;prev=srt.value;order();});q.addEventListener('input',filt);order();filt();
const tw=t.parentElement;t.addEventListener('focusin',ev=>{const c=ev.target.closest('td');if(!c||c.classList.contains('cn'))return;const pin=t.querySelector('th.cn').getBoundingClientRect().width+6,br=tw.getBoundingClientRect(),cr=c.getBoundingClientRect();if(cr.right>br.right)tw.scrollLeft+=cr.right-br.right+6;else if(cr.left<br.left+pin)tw.scrollLeft-=br.left+pin-cr.left;});})();
</script>"""
    body = [gp.nav(P, ["Coverage"], "coverage.html"), '<div class="vw">',
            f'<p class="eyebrow">Coverage · {len(ccs)} countries and groupings · {nt} topics</p>',
            '<h1>What the public record holds, country by country</h1>',
            '<p class="lede">One row per country, one cell per topic, counted exactly as each country’s own page counts it: its sites, the organisations '
            'based there and the entries about it. A number is the count of figures from records; “computed” means only figures the ledger computed from records; '
            '“claim” means only claimed figures (or claimed and computed) have been found; a dot means nothing has been found yet. A gap means the ledger has not found or read a public record, not that none exists.</p>',
            '<div class="vw-key"><span><i class="r"></i>figures from records (the number)</span><span><i class="c"></i>only claims</span>'
            '<span><i class="k"></i>computed from records only</span><span><i class="n"></i>nothing found yet</span></div>',
            f'<p class="m" style="margin-top:10px">{n_any} of {len(ccs)} have at least one figure from a record'
            + (f"; {zero} have none yet." if zero else ".") + " Select a number, a “computed” or a “claim” for those figures in Explore, or a topic’s name to sort by it.</p>",
            '<div class="filters"><input id="cq" type="search" placeholder="Find a country" aria-label="Find a country">'
            '<select id="cs" aria-label="Order"><option value="name">A to Z</option><option value="most">Most topics with a record</option>'
            '<option value="fewest">Fewest topics with a record</option><option value="topic" disabled>By the topic chosen above the table</option></select></div>'
            '<p class="m count" id="cn" aria-live="polite"></p>',
            '<div class="tw"><table class="cov" id="cov"><thead><tr><th scope="col" class="cn">Country</th>' + head_cells
            + '<th scope="col">Topics with a record</th><th scope="col">Sites</th></tr></thead><tbody>' + "".join(rows) + "</tbody>"
            + f'<tfoot><tr><td class="cn">Countries</td>{foot_cells}<td></td><td></td></tr></tfoot></table></div><p class="none empty" id="cov-none" hidden>Nothing matches this search.</p>',
            js, "</div>"]
    return (gp.head("Coverage · Compute Ledger", "What public records the ledger holds for each country, topic by topic: from records, only claims, or nothing found yet.", P,
                    path="coverage.html")
            + "\n".join(body) + "\n" + gp.foot(P, lines=False, path="coverage.html", name="coverage", about=False))


# --------------------------------------------------------------------------------------------------- timeline

def doc_facts(ctx, gp):
    """One row per dated document: its date (the latest recorded for it), publisher and side as its own page gives them, and the
    countries and topics of what it supports."""
    by_url = defaultdict(list)
    for r in ctx.meas:
        by_url[r["source_url"]].append(r)
    esrc = defaultdict(list)
    for r in ctx.esrc:
        esrc[r["url"]].append(r)
    by_doc_links = defaultdict(list)
    for l in ctx.g.links:
        if l["document_id"]:
            by_doc_links[l["document_id"]].append(l)
    top = lambda c: sorted(((-v, k) for k, v in c.items() if k))[0][1] if any(k for k in c) else ""  # noqa: E731
    out, undated = [], 0
    for n in ctx.g.nodes.values():
        if n["type"] != "doc":
            continue
        did, url = n["node_id"][4:], n["detail"]
        m = ctx.doc_meta[url]
        date, first, ndates = gp.doc_dates(m)
        if not date:
            undated += 1
            continue
        cs, ts = set(), set()
        for r in by_url.get(url, []):
            cs.update(subject_countries(ctx, r))
            ts.add(gp.TOPIC_OF.get(r["metric"], gp.LAST_TOPIC))
        for r in esrc.get(url, []):
            cs.update(c for c in ctx.g.nodes.get("entry:" + r["entry_id"], {}).get("country", "").split(";") if c)
        for l in by_doc_links.get(did, []):
            for x in (l["from_id"], l["to_id"]):
                cs.update(c for c in ctx.g.nodes.get(x, {}).get("country", "").split(";") if c)
        out.append({"did": did, "name": n["name"], "date": date, "first": first, "ndates": ndates, "pub": top(m["pubs"]), "side": gp.doc_side(m),
                    "countries": sorted(cs), "topics": sorted(ts), "bases": sorted(k for k in m["bases"] if k), "nfig": len(by_url.get(url, []))})
    out.sort(key=lambda d: ((d["date"] + "-00-00")[:10], d["name"].lower(), d["did"]), reverse=True)
    return out, undated


SIDES = [("record", "mostly records", "b-rec"), ("both", "records and claims equally", "b-both"), ("claim", "mostly claims", "b-claim")]


def timeline(ctx, gp):
    e, P = gp.e, ""
    docs, undated = doc_facts(ctx, gp)
    years = sorted({int(d["date"][:4]) for d in docs})
    last = years[-1]
    buckets = ["before"] + [str(y) for y in range(FIRST_YEAR, last + 1)]
    bucket = lambda y: "before" if int(y) < FIRST_YEAR else y  # noqa: E731
    counts = {b: Counter() for b in buckets}
    rows, cur = [], None
    cset, bset, tset = Counter(), Counter(), Counter()
    for d in docs:
        y = d["date"][:4]
        b = bucket(y)
        counts[b][d["side"]] += 1
        if y != cur:
            rows.append(f'<tr class="yr" data-y="{e(y)}"><th colspan="5" scope="rowgroup">{e(y)}</th></tr>')
            cur = y
        for c in d["countries"]:
            cset[c] += 1
        for x in d["bases"]:
            bset[x] += 1
        for tp in d["topics"]:
            tset[tp] += 1
        place = ", ".join(country_name(ctx, gp, c) for c in d["countries"])
        many = (f'<div class="m">the latest of {d["ndates"]} dates recorded for it, from {e(fmt_date(d["first"]))}</div>' if d["ndates"] > 1 else "")
        rows.append(f'<tr data-row data-y="{e(y)}" data-b="{e(b)}" data-s="{e(d["side"])}" data-c="{e(" ".join(d["countries"]))}" '
                    f'data-t="{" ".join(str(x) for x in d["topics"])}" data-k="{e(" ".join(d["bases"]))}">'
                    f'<td class="d">{e(fmt_date(d["date"]))}</td><td class="doc"><a href="{P}doc/{e(d["did"])}.html">{e(gp.gk.short(d["name"], 130))}</a>'
                    f'<div class="m">{e(d["pub"])}</div>{many}</td><td class="tg">{gp.SIDE_TAG.get(d["side"], "")}</td><td class="m">{e(place)}</td>'
                    f'<td class="v m">{gp.plural(d["nfig"], "figure") if d["nfig"] else "cited, no figure"}</td></tr>')
    label = {"before": f"before {FIRST_YEAR}"}
    counts_rows = "".join(f'<tr><td>{e(label.get(b, b))}</td>' + "".join(f'<td class="v">{counts[b][s]:,}</td>' for s, _, _ in SIDES)
                          + f'<td class="v">{sum(counts[b].values()):,}</td></tr>' for b in buckets)
    n_side = Counter(d["side"] for d in docs)
    c_opts = sorted(((c, country_name(ctx, gp, c)) for c in cset), key=lambda x: x[1].lower())
    t_opts = [(str(x), gp.TOPICS[x][0]) for x in sorted(tset)]
    b_opts = sorted(((b, "computed by the ledger" if b == "derived" else b.replace("_", " ")) for b in bset), key=lambda x: x[1])
    y_opts = [(b, label.get(b, b)) for b in reversed(buckets)]
    data = {"buckets": buckets, "labels": {b: label.get(b, b) for b in buckets}, "sides": [[s, w, c] for s, w, c in SIDES], "first": FIRST_YEAR}
    js = """<script>
(()=>{const D=%s,tb=document.getElementById('trows'),rows=[...tb.querySelectorAll('tr[data-row]')],heads=[...tb.querySelectorAll('tr.yr')],
q=document.getElementById('tq'),n=document.getElementById('tn'),sels=[...document.querySelectorAll('select[data-for="trows"]')],ysel=document.getElementById('ty'),
box=document.getElementById('tl-chart'),tip=document.getElementById('tl-tip'),ct=document.getElementById('tl-counts'),none=document.getElementById('trows-none');
const NS='http://www.w3.org/2000/svg',S=D.sides.map(x=>x[0]);let C=null,keep='';
function el(t,a){const x=document.createElementNS(NS,t);for(const k in a)x.setAttribute(k,a[k]);return x;}
function step(m){if(m<=4)return 1;const raw=m/4,p=Math.pow(10,Math.floor(Math.log10(raw))),f=raw/p;return (f<=1?1:f<=2?2:f<=2.5?2.5:f<=5?5:10)*p;}
function tot(c,b){return S.reduce((a,s)=>a+c[b][s],0);}
function draw(){const c=C;if(!c)return;box.querySelector('svg')?.remove();tip.hidden=true;
 const W=Math.max(300,Math.round(box.clientWidth)),H=230,L=40,R=10,T=22,B=30,bw=(W-L-R)/D.buckets.length,mw=Math.min(24,bw*0.62);
 let mx=0,maxb=D.buckets[0];for(const b of D.buckets){const v=tot(c,b);if(v>mx){mx=v;maxb=b;}}
 let st=step(mx);if(!Number.isInteger(st))st=Math.ceil(st);const top=st*4;
 const s=el('svg',{viewBox:`0 0 ${W} ${H}`,width:W,height:H,role:'group','aria-label':'Documents per year, by whether they are read mostly for records, mostly for claims, or for both equally'});
 const g=el('g',{class:'grid'});for(let i=0;i<=4;i++){const v=st*i,y=T+(H-T-B)*(1-i/4);g.appendChild(el('line',{x1:L,x2:W-R,y1:y,y2:y}));
  const tx=el('text',{x:L-6,y:y+4,'text-anchor':'end'});tx.textContent=v.toLocaleString();g.appendChild(tx);}s.appendChild(g);
 const sc=v=>(H-T-B)*v/top,every=bw<34?2:1,shows={};
 D.buckets.forEach((b,i)=>{const x=L+i*bw+(bw-mw)/2,all=tot(c,b),on=ysel.value===b;
  const col=el('g',{class:'col'+(on?' on':''),tabindex:0,role:'button','aria-pressed':on?'true':'false','data-b':b,
   'aria-label':`${D.labels[b]}: ${all} documents, `+D.sides.map(([k,w])=>`${c[b][k]} ${w}`).join(', ')+(on?'. Shown alone; select again to show every year.':'. Select to show only these.')});
  col.appendChild(el('rect',{class:'hit',x:L+i*bw+1,y:T-4,width:Math.max(1,bw-2),height:H-T-B+4,fill:'transparent'}));
  const segs=D.sides.filter(([k])=>c[b][k]).map(([k,,cls])=>[Math.max(1.5,sc(c[b][k])),cls]);let y0=H-B;
  segs.forEach(([h,cls],j)=>{const last=j===segs.length-1,gap=j?2:0,hh=Math.max(0.5,h-gap),y=y0-h,rr=last?Math.min(4,hh,mw/2):0;
   const d=`M${x},${y+hh}V${y+rr}`+(rr?`Q${x},${y} ${x+rr},${y}H${x+mw-rr}Q${x+mw},${y} ${x+mw},${y+rr}`:`H${x+mw}`)+`V${y+hh}Z`;
   col.appendChild(el('path',{d,class:'bar '+cls}));y0=y;});
  if(all&&(b===maxb||i===D.buckets.length-1)){const tx=el('text',{x:x+mw/2,y:H-B-sc(all)-6,'text-anchor':'middle'});tx.textContent=all.toLocaleString();col.appendChild(tx);}
  const lab=el('text',{x:x+mw/2,y:H-B+16,'text-anchor':'middle'});
  lab.textContent=b==='before'?(bw<34?"<'"+String(D.first).slice(2):'earlier'):((i===D.buckets.length-1||(D.buckets.length-1-i)%%every===0)?(bw<34?"'"+b.slice(2):b):'');col.appendChild(lab);
  const show=()=>{tip.hidden=false;tip.replaceChildren();const h=document.createElement('div');const bb=document.createElement('b');bb.textContent=all.toLocaleString();h.append(bb,' documents · '+D.labels[b]);tip.append(h);
   for(const [k,w] of D.sides){const d=document.createElement('div');const sw=document.createElement('span');sw.className='k';sw.style.background='var(--c-'+(k==='record'?'rec':k)+')';d.append(sw,c[b][k].toLocaleString()+' '+w);tip.append(d);}
   const tw=tip.offsetWidth;let px=x+mw/2+8;if(px+tw>W-4)px=x+mw/2-tw-8;tip.style.left=Math.max(4,px)+'px';tip.style.top='8px';};
  shows[b]=show;
  col.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse')show();});col.addEventListener('focus',show);
  col.addEventListener('pointerleave',e=>{if(e.pointerType==='mouse')tip.hidden=true;});col.addEventListener('blur',()=>tip.hidden=true);
  const pick=kb=>{ysel.value=ysel.value===b?'':b;keep=b;f(kb);};
  col.addEventListener('click',e=>pick(e.detail===0));col.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();pick(true);}});
  s.appendChild(col);});
 box.insertBefore(s,tip);return shows;}
function f(kb){const t=q.value.trim().toLowerCase();let v=0;const c={};for(const b of D.buckets){c[b]={};for(const k of S)c[b][k]=0;}const seen=new Set();
 rows.forEach(r=>{const okBut=sels.every(s=>s===ysel||!s.value||(' '+(r.dataset[s.dataset.f]||'')+' ').includes(' '+s.value+' '))&&(!t||r.textContent.toLowerCase().includes(t));
  if(okBut&&S.includes(r.dataset.s))c[r.dataset.b][r.dataset.s]++;
  const ok=okBut&&(!ysel.value||r.dataset.b===ysel.value);r.hidden=!ok;if(ok){v++;seen.add(r.dataset.y);}});
 heads.forEach(h=>h.hidden=!seen.has(h.dataset.y));none.hidden=v>0;
 n.textContent=v.toLocaleString()+' of '+rows.length.toLocaleString()+' documents shown';
 ct.replaceChildren(...D.buckets.map(b=>{const tr=document.createElement('tr');const cells=[[D.labels[b],'']].concat(S.map(k=>[c[b][k],'v']),[[tot(c,b),'v']]);
  for(const [x,cls] of cells){const td=document.createElement('td');if(cls)td.className=cls;td.textContent=typeof x==='number'?x.toLocaleString():x;tr.append(td);}return tr;}));
 C=c;const shows=draw();
 if(keep){const g=box.querySelector('g.col[data-b="'+keep+'"]');if(g){if(kb===true)g.focus();else if(shows&&shows[keep])shows[keep]();}keep='';}}
[q,...sels].forEach(x=>x.addEventListener('input',()=>f()));f();
document.addEventListener('pointerdown',ev=>{if(!box.contains(ev.target))tip.hidden=true;});
let rw=box.clientWidth;new ResizeObserver(()=>{if(Math.abs(box.clientWidth-rw)>2){rw=box.clientWidth;draw();}}).observe(box);})();
</script>""" % json.dumps(data, ensure_ascii=False)
    body = [gp.nav(P, ["Timeline"], "timeline.html"), '<div class="vw">',
            f'<p class="eyebrow">Timeline · {len(docs):,} dated documents</p>',
            '<h1>The record over time</h1>',
            f'<p class="lede">Every document behind the ledger that has a date, newest first: {n_side["record"]:,} read mostly for records, {n_side["claim"]:,} mostly for claims '
            f'and {n_side["both"]:,} as often for each. Filter by country, topic or kind of document; select a year in the chart to show only its documents. '
            'A document’s countries and topics are those of the figures, entries and links it supports.</p>',
            '<div class="filters"><input id="tq" type="search" placeholder="Filter: a publisher, a title, a word" aria-label="Filter the documents">'
            + select(gp, "trows", "c", "Every country", c_opts) + select(gp, "trows", "t", "Every topic", t_opts)
            + select(gp, "trows", "s", "Records and claims", [("record", "Mostly records"), ("claim", "Mostly claims"), ("both", "Records and claims equally")])
            + select(gp, "trows", "k", "Every kind of document", b_opts)
            + '<select id="ty" data-for="trows" data-f="b" aria-label="Every year"><option value="">Every year</option>'
            + "".join(f'<option value="{e(v)}">{e(x)}</option>' for v, x in y_opts) + "</select></div>",
            '<div class="vw-key"><span><i class="br"></i>mostly records</span><span><i class="be"></i>records and claims equally</span><span><i class="bc"></i>mostly claims</span>'
            '<span>documents per year, for the filters chosen</span></div>',
            '<div class="tl-chart" id="tl-chart"><div class="tl-tip" id="tl-tip" hidden></div></div>',
            '<details style="margin-top:8px"><summary class="m">The counts as a table</summary><div class="tw"><table><thead><tr><th>Year</th><th>Mostly records</th>'
            f'<th>Equally</th><th>Mostly claims</th><th>All</th></tr></thead><tbody id="tl-counts">{counts_rows}</tbody></table></div></details>',
            '<p class="m count" id="tn" aria-live="polite"></p>',
            '<div class="tw"><table class="tl cards"><thead><tr><th>Date</th><th>Document</th><th>Read for</th><th>Countries</th><th>Figures</th></tr></thead>'
            f'<tbody id="trows">{"".join(rows)}</tbody></table></div><p class="none empty" id="trows-none" hidden>Nothing matches these filters.</p>',
            '<p class="m" style="margin-top:10px">A document is placed at the latest date the ledger records for it, as on its own page; where several dates are recorded for it, such as a register read over time, the row gives their range. '
            'It is read mostly for records or mostly for claims by the side of the figures, entries and links that cite it most often. '
            f'{undated:,} documents have no date recorded and are not shown; they are in the <a href="{P}doc/index.html">list of documents</a>.</p>',
            js, "</div>"]
    return (gp.head("Timeline · Compute Ledger", "Every dated document behind the Compute Ledger, newest first, with a chart of documents per year.", P,
                    path="timeline.html")
            + "\n".join(body) + "\n" + gp.foot(P, lines=False, path="timeline.html", name="the timeline", about=False))

"""Totals that cannot mislead: docs/totals.html.

The ledger adds figures together only where it can say exactly what the sum is. A figure is added when it is:
  - about a site (a figure for a country, a company or an entry may already include the sites, so it is never added to them);
  - read from a record (a claim, a figure the ledger computed, or one known only through a press report is not added);
  - exact (not approximate, a lower or upper bound, or a range) and given in the ledger's standard unit;
  - for a stated span of time, the same span for every figure (a count or limit as of a date is a stock, not a flow, and is not added);
  - the same kind of figure with the same definition (metric and metric_detail word for word) and in the same country;
  - the only such figure for its site (where a site has two, neither is added: they may count the same thing twice).
A total is shown when at least two sites' figures are added. Every figure with the same kind, unit, period and country that
was left out is listed with the reason. A total is the sum of what the records the ledger holds give, never a total for
the country: the page says how many of the country's sites in the ledger it covers.

Called by site/build_graph_pages.py (build(ctx, gp)), which writes the file and checks it in CI.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from decimal import Decimal

MIN_SITES = 2
REASON = {  # why a figure that shares a total's kind, unit, period and country is not in it
    "claim": "a claim: totals add records only",
    "derived": "computed by the ledger: totals add only figures read from records",
    "press_report": "known only through a press report of the record",
    "approximate": "an approximate value",
    "lower_bound": "a lower bound ('at least')",
    "upper_bound": "an upper bound ('up to')",
    "range": "a range",
    "no_value": "no value in the ledger's standard unit",
    "twice": "the site has two or more such figures; none is added, since they may count the same thing twice",
    "estimated": "the filing says estimated values were used",
    "part_meter": "the filing flags that the meter has less than 12 full months of data",
    "partly_estimate": "partly an estimate, as the document says",
    "not_site_entity": "about a company as a whole (its figure may cover every country it works in), not a site (rule 1)",
    "not_site_entry": "about a ledger entry (a country, a region or a programme), not a site (rule 1)",
    "year_unconfirmed": "the ledger's notes say the filing's year may not be the year of the data",
    "construction": "includes water used for construction, as the document says",
}
# What a document says about its own figure, in the figure's notes, that makes it not exact for the whole period (rules 3 and 4)
FLAGS = [("estimated", "Used Estimated Energy Values=True", ""), ("part_meter", "less than 12 full calendar months of data=Possible Issue", ""),
         ("year_unconfirmed", "whether it is the calendar year of the metered data was not confirmed", ""),
         ("year_unconfirmed", "REPORTINGYEAR semantics unconfirmed", ""),
         ("year_unconfirmed", "REPORTINGYEAR is calendar year of data or year of submission was not confirmed", ""),
         ("year_unconfirmed", "year semantics unconfirmed", ""),
         ("year_unconfirmed", "benchmark_year is the compliance year label", ""),
         ("construction", "also currently used for construction purposes", "water_withdrawn"),
         ("partly_estimate", "Total Water Used 21,617 is partly an estimate", "water_withdrawn")]  # a metric names the one figure a shared note is about
FIELDS = {"largestpropertyusetype": "the filing's 'largest property use type'", "beudo_property_type": "the filing's property type",
          "propertytype": "the filing's property type", "primary_property_type": "the filing's primary property type"}
KINDS = {"datacenter": "datacenters", "telecom_exchange": "telephone exchanges filed as datacenters",
         "mixed_building_with_datacenter": "buildings that contain a datacenter", "smelter_refiner": "smelters and refiners",
         "fab": "chip fabs and packaging plants", "crypto_mining": "crypto mining sites",
         "crypto_to_ai_conversion": "crypto mining sites moving to AI or hosting", "nuclear_plant": "nuclear plants"}
THE = {"USA", "GBR", "NLD", "PHL", "ARE", "CZE"}  # country names written with 'the' in a sentence
UNIT = {"MWh": "MWh", "t": "tonnes", "m3": "m³", "h": "hours", "count": "", "MWth": "MW thermal", "MW": "MW", "m2": "m²",
        "ha": "hectares", "USD": "US dollars", "GBP": "pounds", "EUR": "euros", "pct": "%"}

CSS = """
/* totals */
.tot td.sum{font-family:var(--display);font-size:19px;font-weight:700;white-space:nowrap}
.tot td.sum .m{font-family:var(--mono);font-weight:400;display:block;white-space:normal}
.tot details{margin:2px 0 0}
.tot summary{cursor:pointer;font-family:var(--mono);font-size:12.5px;color:var(--accent)}
.tot details ul{list-style:none;padding:0;margin:8px 0 0;max-height:420px;overflow:auto;border-top:1px solid var(--rule)}
.tot details li{font-size:14px;padding:5px 0;border-bottom:1px dashed var(--rule);display:flex;gap:4px 12px;flex-wrap:wrap;justify-content:space-between}
.tot details li .v{font-family:var(--mono);font-size:13px;white-space:nowrap}
.tot h4{font-family:var(--mono);font-size:12px;font-weight:500;color:var(--ink-2);margin:12px 0 0}
.tot ol.rules{max-width:80ch;font-size:16px;padding-left:22px}
.tot ol.rules li{margin:0 0 6px}
.tot .warn{border-left:3px solid var(--gap);padding:2px 0 2px 8px;margin:6px 0 0;font-size:14px}
@media (max-width:640px){.tot details li .v{white-space:normal}.tot td.sum{white-space:normal}}
"""


def dec(s: str) -> Decimal:
    return Decimal(s.replace(",", ""))


def show(x: Decimal) -> str:
    """A sum, to the precision that reads cleanly: whole numbers from 100 up, then two significant decimals."""
    if abs(x) >= 100:
        return f"{x.quantize(Decimal(1)):,}"
    if abs(x) >= 1:
        return f"{x.quantize(Decimal('0.01')):,}".rstrip("0").rstrip(".")
    return f"{x:.3g}"


def friendly(x: Decimal, unit: str) -> str:
    if unit == "MWh" and x >= 1_000_000:
        return f"{x / Decimal(1_000_000):,.2f} TWh"
    if unit == "MWh" and x >= 1_000:
        return f"{x / Decimal(1_000):,.1f} GWh"
    if unit == "m3" and x >= 1_000_000:
        return f"{x / Decimal(1_000_000):,.2f} million m³"
    return ""


def why_not(r: dict) -> str:
    if r["side"] != "record":
        return "claim"
    if r["basis"] == "derived":
        return "derived"
    if r["basis"] == "press_report":
        return "press_report"
    if r["qualifier"] in ("approximate", "lower_bound", "upper_bound"):
        return r["qualifier"]
    if r["value_high_canonical"]:
        return "range"
    if not r["value_canonical"]:
        return "no_value"
    for k, s, metric in FLAGS:
        if s in r["notes"] and (not metric or r["metric"] == metric):
            return k
    return ""


def plain(detail: str) -> str:
    """A definition as the page shows it: a filing's raw field name (field=value) in words; the data keep the original."""
    def f(m):
        return f"({FIELDS.get(m.group(1).lower(), 'the filing' + chr(39) + 's field ' + m.group(1).replace('_', ' '))}: {m.group(2)})"
    return re.sub(r"\(([A-Za-z_]+)=([^()]+)\)", f, detail)


def overlaps(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


def compute(ctx) -> list[dict]:
    buckets = defaultdict(list)
    for r in ctx.meas:
        if r["subject_type"] != "site":
            continue
        ps, pe = r["period_start"], r["period_end"]
        if not (ps and pe and ps < pe):
            continue
        cc = ctx.sites[r["subject_id"]]["country"]
        buckets[(cc, r["metric"], r["canonical_unit"], ps, pe)].append(r)
    totals = []
    for key, rows in buckets.items():
        by_def = defaultdict(list)
        for r in rows:
            by_def[r["metric_detail"]].append(r)
        made = {}
        for d, rs in by_def.items():
            reasons = {r["measurement_id"]: why_not(r) for r in rs}
            ok = [r for r in rs if not reasons[r["measurement_id"]]]
            n_site = Counter(r["subject_id"] for r in ok)
            for r in ok:
                if n_site[r["subject_id"]] > 1:
                    reasons[r["measurement_id"]] = "twice"
            inc = [r for r in rs if not reasons[r["measurement_id"]]]
            if len({r["subject_id"] for r in inc}) >= MIN_SITES:
                made[d] = {"key": key, "detail": d, "added": inc,
                           "left": [(r, REASON[reasons[r["measurement_id"]]]) for r in rs if reasons[r["measurement_id"]]],
                           "sum": sum((dec(r["value_canonical"]) for r in inc), Decimal(0))}
        for d, t in made.items():
            other = Counter(x for x in by_def if x != d for _ in by_def[x])
            t["other_defs"] = sorted(((x, n, x in made) for x, n in other.items()), key=lambda z: (-z[1], z[0]))
            totals.append(t)
    return totals


def build(ctx, gp) -> dict:
    e = gp.e
    P = ""
    totals = compute(ctx)
    cname = lambda cc: gp.bs.COUNTRY.get(cc, cc)  # noqa: E731
    in_country = defaultdict(Counter)
    for s in ctx.sites.values():
        in_country[s["country"]][s["kind"]] += 1

    def order(t):
        cc, m, u, ps, pe = t["key"]
        return (cname(cc).lower(), gp.TOPIC_OF.get(m, gp.LAST_TOPIC), gp.bs.metric_label(m).lower(), -int(pe[:4]), ps, pe,
                -len({r["subject_id"] for r in t["added"]}), t["detail"].lower())

    def kinds_phrase(kinds):
        order_ = list(KINDS)
        w = [KINDS.get(k, k.replace("_", " ")) for k in sorted(kinds, key=lambda k: (order_.index(k) if k in order_ else 99, k))]
        return w[0] if len(w) == 1 else ", ".join(w[:-1]) + " and " + w[-1]

    totals.sort(key=order)
    # what else shares a total's kind, unit and country: other periods of the same definition, and figures not about a site
    names = {v: k for k, v in {**gp.bs.COUNTRY, **gp.bx.EXTRA_COUNTRY}.items()}
    names["European Union"] = "EUU"
    same_def = defaultdict(Counter)
    not_site = defaultdict(list)
    for r in ctx.meas:
        if r["subject_type"] == "site" and r["side"] == "record":
            same_def[(ctx.sites[r["subject_id"]]["country"], r["metric"], r["canonical_unit"], r["metric_detail"])][(r["period_start"], r["period_end"])] += 1
        elif r["subject_type"] in ("entry", "entity"):
            if r["subject_type"] == "entry":
                ccs = gp.bx.entry_countries(ctx.entries[r["subject_id"]]["country"], names) if r["subject_id"] in ctx.entries else []
            else:
                ccs = [ctx.ents[r["subject_id"]]["country"]] if r["subject_id"] in ctx.ents else []
            for c in ccs:
                not_site[(c, r["metric"], r["canonical_unit"], r["period_start"], r["period_end"])].append(r)
    spans = defaultdict(list)
    for t in totals:
        cc, m, u, ps, pe = t["key"]
        spans[(cc, m, u, t["detail"])].append((ps, pe))
    rows, countries, topics = [], Counter(), Counter()
    for i, t in enumerate(totals):
        cc, m, u, ps, pe = t["key"]
        ti = gp.TOPIC_OF.get(m, gp.LAST_TOPIC)
        countries[cc] += 1
        topics[ti] += 1
        added = sorted(t["added"], key=lambda r: ctx.sites[r["subject_id"]]["name"].lower())
        sites = {r["subject_id"] for r in added}
        kinds = Counter(ctx.sites[s]["kind"] for s in sites)
        same_kind = sum(in_country[cc][k] for k in kinds)
        kind_words = kinds_phrase(kinds)
        where = ("the " if cc in THE else "") + cname(cc)
        pubs = Counter(r["source_publisher"] for r in added)
        pub_line = "; ".join(f"{p} ({n})" if n > 1 else p for p, n in sorted(pubs.items(), key=lambda x: (-x[1], x[0])))
        period = gp.bs.period(added[0])
        unit = UNIT.get(u, u.replace("_", " "))
        fr = friendly(t["sum"], u)
        left = list(t["left"]) + [(r, ("a claim, and " if r["side"] == "claim" else "") + REASON["not_site_" + r["subject_type"]]) for r in not_site.get(t["key"], [])]

        def who(r):
            return ctx.ref(("site:" if r["subject_type"] == "site" else "entry:" if r["subject_type"] == "entry" else "org:") + r["subject_id"], P)

        add_li = "".join(
            f'<li><span>{who(r)}</span><span class="v">{e(gp.bs.as_published(r))}'
            + (f' = {e(show(dec(r["value_canonical"])))} {e(unit)}' if r["unit"] != r["canonical_unit"] else "")
            + f' · <a href="{P}explore.html#{e(r["measurement_id"])}">the figure</a></span></li>' for r in added)
        left_li = "".join(
            f'<li><span>{who(r)} <span class="m">{e(why)}</span></span><span class="v">{e(gp.bs.as_published(r))}'
            f' · <a href="{P}explore.html#{e(r["measurement_id"])}">the figure</a></span></li>'
            for r, why in sorted(left, key=lambda x: (x[1], x[0]["subject_id"])))
        defs = "".join(f'<li><span>{e(plain(d))}</span><span class="v">{gp.plural(n, "figure")}' + (" · its own total" if own else "") + "</span></li>"
                       for d, n, own in t["other_defs"])
        others = sorted(((k, n) for k, n in same_def[(cc, m, u, t["detail"])].items() if k != (ps, pe)), key=lambda x: (x[0][1], x[0][0]), reverse=True)
        oth_li = "".join(f'<li><span>{e(gp.bs.period({"period_start": a, "period_end": b}))}</span><span class="v">{gp.plural(n, "figure")}'
                         + (" · its own total" if (a, b) in spans[(cc, m, u, t["detail"])] else "") + "</span></li>" for (a, b), n in others)
        n_def = sum(n for _, n, _ in t["other_defs"])
        n_oth = sum(n for _, n in others)
        summary = (f"{gp.plural(len(added), 'figure')} added · " + (f"{len(left):,} left out" if left else "none left out")
                   + (f" · {n_def:,} with another definition" if n_def else "") + (f" · {n_oth:,} for another period" if n_oth else ""))
        detail = (f'<details><summary>{e(summary)}</summary><h4>Added</h4><ul>{add_li}</ul>'
                  + (f"<h4>Left out ({len(left):,}): the same kind of figure, in the same unit, for the same period, about a site in this country, the country, "
                     f"or a company registered there</h4><ul>{left_li}</ul>" if left else "")
                  + (f"<h4>The same kind of figure with another definition, counted apart</h4><ul>{defs}</ul>" if defs else "")
                  + (f"<h4>The same definition for another period, not added to this one</h4><ul>{oth_li}</ul>" if oth_li else "")
                  + "</details>")
        over = [s for s in spans[(cc, m, u, t["detail"])] if s != (ps, pe) and overlaps(s, (ps, pe))]
        part = not (ps[5:] == "01-01" and pe[5:] == "12-31" and ps[:4] == pe[:4])
        warn = ""
        if over:
            warn = (f'<p class="warn">Part of a year. Another total covers an overlapping span ({e("; ".join(gp.bs.period({"period_start": a, "period_end": b}) for a, b in over))}), '
                    "for other sites: the two are not to be added together.</p>")
        elif part:
            warn = '<p class="warn">Part of a year: the documents cover only this span.</p>'
        ex = f"{P}explore.html?country={e(cc)}&amp;metric={e(m)}&amp;what=record&amp;year={e(pe[:4])}"
        rows.append(
            f'<tr data-row data-c="{e(cc)}" data-t="{ti}" id="t{i + 1}"><td data-label="Where">{ctx.ref("country:" + cc, P)}</td>'
            f'<td data-label="What is added"><strong>{e(gp.bs.metric_label(m))}</strong><div>{e(plain(t["detail"]))}</div><div class="m">{e(period)}</div>{warn}</td>'
            f'<td class="sum" data-label="Sum">{e(show(t["sum"]))} {e(unit)}' + (f'<span class="m">{e(fr)}</span>' if fr else "") + "</td>"
            f'<td data-label="What it covers"><div>{len(sites):,} of the {same_kind:,} {e(kind_words)} the ledger lists in {e(where)}, '
            f'each with this figure from a record. Not a total for {e(where)}.</div>'
            f'<div class="m">From: {e(pub_line)}</div><div class="m"><a href="{ex}">Records of this kind for {e(where)} in {e(pe[:4])}, in Explore</a> '
            '(a wider view than this row: any figure from a record ending that year)</div>' + detail + "</td></tr>")
    c_opts = sorted(((c, cname(c)) for c in countries), key=lambda x: x[1].lower())
    t_opts = [(str(ti), gp.TOPICS[ti][0]) for ti in sorted(topics)]
    tbl = ('<div class="filters"><input id="tq" type="search" placeholder="Filter: a site, a word, a year" aria-label="Filter the totals">'
           + gp.views.select(gp, "trows", "c", "Every country", c_opts) + gp.views.select(gp, "trows", "t", "Every topic", t_opts)
           + '</div><p class="m count" id="tn" aria-live="polite"></p>'
           '<div class="tw"><table class="cards"><thead><tr><th>Where</th><th>What is added</th><th>Sum</th><th>What it covers</th></tr></thead>'
           f'<tbody id="trows">{"".join(rows)}</tbody></table></div><p class="none empty" id="trows-none" hidden>Nothing matches these filters.</p>'
           + gp.views.FILTER_JS % {"tbody": "trows", "q": "tq", "n": "tn"}
           + """<script>
(()=>{const q=document.getElementById('tq'),sel=f=>document.querySelector('select[data-for="trows"][data-f="'+f+'"]');
const p=new URLSearchParams(location.search);let any=false;
for(const k of ['c','t']){const v=p.get(k),s=sel(k);if(v&&s&&[...s.options].some(o=>o.value===v)){s.value=v;any=true;}}
if(p.get('q')){q.value=p.get('q');any=true;}
function keep(){const u=new URLSearchParams();for(const k of ['c','t']){const s=sel(k);if(s&&s.value)u.set(k,s.value);}if(q.value.trim())u.set('q',q.value.trim());
const s=u.toString();history.replaceState(null,'',location.pathname+(s?'?'+s:''));
const w=q.value.trim().toLowerCase();
for(const r of document.querySelectorAll('#trows tr[data-row]')){const d=r.querySelector('details');if(!d)continue;
const out=[...r.cells].map(c=>{const x=c.cloneNode(true);x.querySelectorAll('details').forEach(n=>n.remove());return x.textContent.toLowerCase();}).join(' ');
const by=w&&!r.hidden&&!out.includes(w);if(by){d.open=true;d.dataset.bysearch='1';}else if(d.dataset.bysearch){d.open=false;delete d.dataset.bysearch;}}}
document.querySelectorAll('#trows details').forEach(d=>d.addEventListener('toggle',()=>{if(!d.open)delete d.dataset.bysearch;}));
[q,sel('c'),sel('t')].forEach(x=>x&&x.addEventListener('input',keep));
if(any)q.dispatchEvent(new Event('input'));})();
</script>""")
    rules = ("<ol class=\"rules\">"
             "<li><b>Sites only.</b> A figure for a country, a company or an entry may already include the sites, so it is never added to them.</li>"
             "<li><b>Records only.</b> A claim is not added, nor a figure the ledger computed, nor one known only through a press report.</li>"
             "<li><b>Exact values in one unit.</b> An approximate value, a lower or upper bound, a range, or a value its document says is partly or wholly estimated is not added; values are added in the ledger's standard unit, and each figure as printed is in the list.</li>"
             "<li><b>The same span of time.</b> Every figure covers the same stated period, and none is flagged by its document as covering less of it. A count or limit as of a date is not added.</li>"
             "<li><b>The same definition.</b> The same kind of figure, described in the same words, in the same country. "
             "Figures described differently are kept apart, even where the difference may be only wording.</li>"
             f"<li><b>One figure per site.</b> Where a site has two such figures, neither is added. A total needs at least {MIN_SITES} sites.</li></ol>")
    body = [gp.nav(P, ["Totals"], "totals.html"), '<div class="vw tot">',
            f'<p class="eyebrow">Totals · {gp.plural(len(totals), "total")} in {gp.plural(len(countries), "country", "countries")}</p>',
            "<h1>Totals that can be added</h1>",
            '<p class="lede">Adding figures from different documents can mislead: a national figure counted again with its own sites, '
            'two years mixed, a claim added to a record, the same site counted twice. The ledger adds figures only where it can say exactly '
            'what the sum is. Under each total it lists the figures added and every figure of the same kind, unit and period it left out (about a site in the country, '
            'the country, or a company registered there, records and claims alike), '
            'with the reason, and counts the figures with another definition or for another period. Each total is the sum of what the records the ledger holds '
            'give for those sites. It is not a total for the country, and the row says how many of the country\'s sites in the ledger it covers.</p>',
            gp.section("The rules", "", "A figure is added to a total only when all six hold.", rules),
            gp.section("The totals", "rec", f"{gp.plural(len(totals), 'total')}, each with the figures added and those left out. "
                       "Open a row's list to see every figure, as its document printed it.", tbl),
            "</div>"]
    desc = "Sums of the ledger's figures only where they can be added: records, the same definition and period, one figure per site, with what was left out and why."
    return {"totals.html": gp.head("Totals · Compute Ledger", desc, P, path="totals.html") + "\n".join(body) + "\n"
            + gp.foot(P, lines=False, path="totals.html", name="the totals", about=False)}

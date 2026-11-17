#!/usr/bin/env python3
"""Pages built from the graph: one per organisation, country and document, the chain, and the search index.

Every page of a kind carries the same sections in the same order, and a section with nothing in it says so, so the
same question gets the same place on every page:

  organisation  facts and identifiers · tiles · what the public record holds (one cell per topic) · figures about it ·
                its sites · its group and companies acting for it · the chain · documents it published · entries that
                name it · not found yet
  country       facts · tiles · what the public record holds · regions · sites · organisations listed there · the chain ·
                who keeps the records · entries · not found yet
  document      facts · tiles · figures read from it · links it states · entries that cite it · checks · also by this publisher

Writes docs/org/, docs/country/, docs/doc/ (each with an index.html), docs/chain.html, docs/data/search.json and
docs/assets/graph.css and graph.js. Reads data/graph/ (pipeline/build_graph.py) and data/climate_trace_seed/.
Output is deterministic; --check compares with the committed files and exits 1 on a difference.

    python3 site/build_graph_pages.py [--check]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_explore as bx  # noqa: E402
import build_sites as bs  # noqa: E402
import graphkit as gk  # noqa: E402
from graphdata import CHAIN_RELATIONS, GROUP_RELATIONS, graph  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "data" / "climate_trace_seed"
DOCS = ROOT / "docs"
REPO = bs.REPO_URL
e = bs.e
TOPICS = bx.TOPICS
TOPIC_OF = {m: i for i, (_, ms) in enumerate(TOPICS) for m in ms}
LAST_TOPIC = len(TOPICS) - 1
SIDE_TAG = {"record": '<span class="tag rec">record</span>', "claim": '<span class="tag claim">claim</span>'}


def read(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def plural(n, one, many=None):
    return f"{n:,} {one if n == 1 else (many or one + 's')}"


# --------------------------------------------------------------------------------------------------- page frame

def head(title, desc, prefix, jsonld=None):
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")).replace("</", "<" + chr(92) + "/")}</script>\n' if jsonld else ""
    return ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{e(title)}</title>\n<meta name="description" content="{e(desc)}">\n' + bx.FONTS
            + f'<link rel="stylesheet" href="{prefix}sites/site.css">\n<link rel="stylesheet" href="{prefix}assets/graph.css">\n' + ld
            + '<body>\n<div class="wrap">\n')


def nav(prefix, crumbs, current=""):
    links = bs.NAV
    cur = ' aria-current="page"'
    out = "".join(f'<a href="{prefix}{h}"' + (cur if h == current else "") + f'>{t}</a>' for h, t in links)
    return (f'<nav class="top"><span><a href="{prefix}index.html">Compute Ledger</a>' + "".join(f" / {c}" for c in crumbs)
            + f'</span><span class="links">{out}</span></nav>\n'
            f'<div class="gsearch" data-base="{prefix}"><input type="search" placeholder="Search sites, organisations, countries, documents" '
            'aria-label="Search the ledger" autocomplete="off"><ul role="listbox"></ul></div>\n')


def foot(prefix):
    return ('<footer><p>Records are documents from regulators, courts, grid operators, statistics offices, auditors, registries or customs. '
            'Claims are what companies and governments say. A gap means the ledger has not found or read a public record yet, not that none '
            'exists or that anything is wrong. A line between two names is drawn only where a document states the link.</p>'
            f'<p>Data CC BY 4.0. <a href="{prefix}explore.html#get-the-data">Get the data</a> · <a href="{REPO}/tree/main/data/graph">The graph as data</a> · '
            f'<a href="{REPO}#how-to-cite">Cite</a> · <a href="{REPO}/issues/new/choose">Report an error or a missing record</a> · '
            f'<a href="{prefix}index.html">The ledger</a></p></footer>\n</div>\n'
            f'<script src="{prefix}assets/graph.js" defer></script>\n</body>\n</html>\n')


def cite_line(cite, kind, ident, iri):
    v = f", version {cite['version']}" if cite.get("version") else ""
    doi = f" https://doi.org/{cite['doi']}" if cite.get("doi") else ""
    return f"{cite['authors']} ({cite['year']}). {cite['title']}{v}, {kind} {ident}. {iri}{doi}"


# --------------------------------------------------------------------------------------------------- shared blocks

def topic_grid(rows, explore_base, prefix):
    by = defaultdict(Counter)
    for r in rows:
        t = TOPIC_OF.get(r["metric"], LAST_TOPIC)
        by[t]["computed" if r["basis"] == "derived" else r["side"]] += 1
    out = ['<ul class="q">']
    for i, (t, _) in enumerate(TOPICS):
        c = by.get(i, Counter())
        n_rec, n_calc, n_cl = c["record"], c["computed"], c["claim"]
        href = f'{prefix}explore.html?{explore_base}&amp;topic={i}'
        if n_rec:
            txt = f'<a href="{href}">{plural(n_rec, "figure")} from records</a>' + (f", {n_calc:,} computed" if n_calc else "") + (f", {n_cl:,} claimed" if n_cl else "")
            out.append(f"<li><b>{e(t)}</b><span>{txt}</span></li>")
        elif n_cl or n_calc:
            out.append(f'<li class="no"><b>{e(t)}</b><span>Only <a href="{href}">{plural(n_cl + n_calc, "figure")}</a> '
                       f'{"claimed" if n_cl and not n_calc else "claimed or computed"}; no record found yet</span></li>')
        else:
            out.append(f'<li class="no"><b>{e(t)}</b><span>No public record found yet</span></li>')
    out.append("</ul>")
    return "".join(out)


def fig_table(rows, ctx, prefix, limit=60, more_href="", show_doc=True):
    if not rows:
        return ""
    many = len({(r["subject_type"], r["subject_id"]) for r in rows}) > 1
    out = ['<div class="tw"><table><thead><tr>' + ("<th>About</th>" if many else "") + '<th>Figure</th><th>As published</th><th>Kind</th>'
           + ("<th>Document</th>" if show_doc else "") + '</tr></thead><tbody>']
    for r in rows[:limit]:
        subj = f'<td>{ctx.subject(r["subject_type"], r["subject_id"], prefix)}</td>' if many else ""
        did = ctx.url_doc.get(r["source_url"])
        docl = (f'<a href="{prefix}doc/{did}.html">{e(gk.short(r["source_title"] or r["source_url"], 70))}</a>' if did else e(r["source_title"]))
        src = f' · <a href="{e(r["source_url"])}" rel="noopener">source</a>' if r["source_url"].startswith("http") else ""
        what = "computed" if r["basis"] == "derived" else r["side"]
        tag = SIDE_TAG.get(what, f'<span class="tag">{e(what)}</span>')
        twice = ' <span class="tag" title="read a second time, independently">read twice</span>' if r["second_read"] == "yes" else ""
        out.append(f'<tr>{subj}<td><strong>{e(bs.metric_label(r["metric"]))}</strong><div class="m">{e(r["metric_detail"])}</div></td>'
                   f'<td class="v">{e(bs.as_published(r))}<div class="m">{e(bs.period(r))}</div>{twice}</td>'
                   f'<td>{tag}<div class="m">{e(r["basis"].replace("_", " "))}</div></td>'
                   + (f'<td>{docl}<div class="m">{e(" · ".join(x for x in (r["source_publisher"], r["source_date"]) if x))}{src}</div></td>' if show_doc else "")
                   + '</tr>')
    out.append("</tbody></table></div>")
    if len(rows) > limit:
        out.append(f'<p class="m" style="margin-top:8px">Showing {limit} of {len(rows):,}. <a href="{more_href}">All {len(rows):,} in Explore, to filter, download and cite →</a></p>')
    return "".join(out)


def link_table(ls, ctx, prefix, show_doc=True):
    if not ls:
        return ""
    out = ['<div class="tw"><table><thead><tr><th>Link</th><th>Period</th><th>Kind</th>' + ("<th>Document and the line that states it</th>" if show_doc else "<th>The line that states it</th>")
           + "</tr></thead><tbody>"]
    for l in sorted(ls, key=lambda l: (l["relation"], ctx.g.nodes[l["from_id"]]["name"], ctx.g.nodes[l["to_id"]]["name"], l["link_id"])):
        a, b = ctx.ref(l["from_id"], prefix), ctx.ref(l["to_id"], prefix)
        d = ctx.g.nodes.get("doc:" + l["document_id"]) if l["document_id"] else None
        doc = (f'<a href="{prefix}{d["page"]}">{e(gk.short(d["name"], 100))}</a> · <a href="{e(d["detail"])}" rel="noopener">source</a>' if d and show_doc else "")
        per = " to ".join(x for x in (l["period_start"], l["period_end"]) if x) or "not stated"
        out.append(f'<tr><td>{a} {e(gk.REL_TEXT.get(l["relation"], l["relation"].replace("_", " ")))} {b}</td><td class="m">{e(per)}</td>'
                   f'<td>{SIDE_TAG.get(l["side"], "")}<div class="m">{e(l["basis"].replace("_", " "))}</div></td>'
                   f'<td>{doc}<blockquote>“{e(l["quoted_line"])}”</blockquote></td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


def chain_block(ls, ctx, prefix, gid, focus, note=""):
    """A drawing of the chain links, its detail panel, and the links as a table."""
    if not ls:
        return '<p class="none">No link in the chain is documented for it yet.</p>' + (f'<div class="gapbox">{note}</div>' if note else "")
    svg, data = gk.chain_drawing(ls, ctx.cnodes, ctx.docnodes, gid, gap=False, focus=focus)
    svg = svg.replace('<svg class="lg"', f'<svg data-base="{prefix}" class="lg"', 1)
    return (f'<div class="lglegend"><span><i></i>record</span><span><i class="c"></i>claim</span><span>arrows point the way metal, chips, power or water go</span>'
            '<span>select a box or a line for its details</span></div>'
            f'<div class="lgwrap">{svg}</div>{gk.data_script(gid, data)}<div class="lgpanel" id="{gid}-panel" aria-live="polite"></div>'
            + (f'<div class="gapbox">{note}</div>' if note else "")
            + f'<details style="margin-top:10px"><summary class="m">The {plural(len(ls), "link")} as a table</summary>{link_table(ls, ctx, prefix)}</details>')


def gaps_box(items):
    if not items:
        return '<p class="none">Nothing listed as missing.</p>'
    return '<div class="gapbox"><span class="tag gap">not found yet</span><ul>' + "".join(f"<li>{x}</li>" for x in items) + "</ul></div>"


def tiles(items):
    return '<div class="tiles">' + "".join(f'<div class="tile"><b>{e(n)}</b><span>{t}</span></div>' for n, t in items) + "</div>"


def section(title, cls, lede, body, anchor=""):
    a = f' id="{anchor}"' if anchor else ""
    return f'<h2 class="{cls}"{a}>{e(title)}</h2>' + (f'<p class="lede">{lede}</p>' if lede else "") + body


# --------------------------------------------------------------------------------------------------- context

class Ctx:
    def __init__(self):
        self.g = graph()
        g = self.g
        self.cite = bx.citation_meta()
        self.vocab = json.loads((ROOT / "pipeline" / "measurement_vocab.json").read_text(encoding="utf-8"))
        self.sites = {s["site_id"]: s for s in read(PKG / "site_register.csv")}
        self.ents = {x["entity_id"]: x for x in read(ROOT / "sites" / "entity_register.csv")}
        self.entries = {x["id"]: x for x in read(PKG / "entries.csv")}
        self.meas = read(PKG / "measurements.csv")
        self.esrc = read(PKG / "entry_sources.csv")
        self.checks = {c["check_id"]: c for c in read(PKG / "checks.csv")}
        self.findings = read(PKG / "findings.csv")
        idp = ROOT / "sites" / "organisations" / "identifiers.csv"
        self.idents = defaultdict(list)
        for r in (read(idp) if idp.exists() else []):
            self.idents[r["entity_id"]].append(r)
        self.url_doc = {n["detail"]: n["node_id"][4:] for n in g.nodes.values() if n["type"] == "doc"}
        self.by_subject = defaultdict(list)
        for r in self.meas:
            t = {"site": "site", "entity": "org", "entry": "entry"}[r["subject_type"]]
            self.by_subject[f"{t}:{r['subject_id']}"].append(r)
        # document facts
        self.doc_meta = defaultdict(lambda: {"titles": Counter(), "pubs": Counter(), "dates": Counter(), "bases": Counter(), "sides": Counter()})
        for r in self.meas:
            m = self.doc_meta[r["source_url"]]
            m["titles"][r["source_title"]] += 1; m["pubs"][r["source_publisher"]] += 1; m["dates"][r["source_date"]] += 1
            m["bases"][r["basis"]] += 1; m["sides"][r["side"]] += 1
        for r in self.esrc:
            m = self.doc_meta[r["url"]]
            m["titles"][r["title"]] += 1; m["pubs"][r["publisher"]] += 1; m["dates"][r["date"]] += 1; m["sides"][r["side"]] += 1
        for l in read(ROOT / "data" / "chain" / "edges.csv"):
            m = self.doc_meta[l["document_url"]]
            m["titles"][l["document_title"]] += 1; m["pubs"][l["publisher"]] += 1; m["dates"][l["document_date"]] += 1
            m["bases"][l["basis"]] += 1; m["sides"][l["side"]] += 1
        # nodes as the drawings read them (pages relative to the site root)
        self.cnodes = {}
        for nid, n in g.nodes.items():
            d = {"type": n["type"], "name": n["name"], "page": n["page"], "kind": n["kind"], "country": n["country"]}
            if n["type"] == "site":
                s = self.sites[nid[5:]]
                d["place"] = ", ".join(x for x in (s["locality"], s["admin_region"], bs.COUNTRY.get(s["country"], s["country"])) if x)
            self.cnodes[nid] = d
        self.docnodes = {n["node_id"][4:]: n for n in g.nodes.values() if n["type"] == "doc"}

    def subject(self, t, i, prefix):
        nid = {"site": "site:", "entity": "org:", "entry": "entry:"}[t] + i
        return self.ref(nid, prefix)

    def ref(self, nid, prefix):
        n = self.g.nodes.get(nid)
        if not n:
            return e(nid)
        if n["page"] and n["type"] != "party":
            return f'<a href="{prefix}{n["page"]}">{e(n["name"])}</a>'
        return f"<strong>{e(n['name'])}</strong>"

    def topic_of(self, r):
        return TOPIC_OF.get(r["metric"], LAST_TOPIC)


def order_figs(rows):
    return sorted(rows, key=lambda r: (0 if r["side"] == "record" and r["basis"] != "derived" else 1 if r["basis"] == "derived" else 2,
                                       TOPIC_OF.get(r["metric"], LAST_TOPIC), r["metric"], -int((r["period_end"] or r["period_start"] or "0")[:4] or 0),
                                       r["measurement_id"]))


def ring_item(ctx, nid, prefix, side="", count=None, name=None, page=None, typ=None):
    n = ctx.g.nodes.get(nid, {})
    return {"id": nid, "name": name or n.get("name", nid), "type": typ or n.get("type", ""), "side": side, "count": count,
            "page": page if page is not None else ((prefix + n["page"]) if n.get("page") and n.get("type") != "party" else "")}


# --------------------------------------------------------------------------------------------------- organisation pages

def org_page(ctx, oid):
    g = ctx.g
    nid = f"org:{oid}"
    n = g.nodes[nid]
    ent = ctx.ents[oid]
    P = "../"
    sites = g.org_sites(nid)
    site_ids = sorted({s for s, _, _ in sites})
    group = g.org_group(nid)
    subjects = set(g.org_subjects(nid))
    figs = [r for s in sorted(subjects) for r in ctx.by_subject.get(s, [])]
    own_entries = g.org_entries(nid)
    own = order_figs(ctx.by_subject.get(nid, []) + [r for x in own_entries for r in ctx.by_subject.get(x, [])])
    countries = sorted({ctx.sites[s[5:]]["country"] for s in site_ids})
    chain = []
    for x in [nid] + site_ids:
        chain += g.chain_links(x)
    chain = list({l["link_id"]: l for l in chain}.values())
    grp = g.group_links(nid)
    names_listed = sorted({l["note"].split("listed as “", 1)[1].split("”", 1)[0] for _, l, via in sites if via == nid and "listed as “" in l["note"]})
    entries = sorted({l["from_id"] for l in g.rel_in(nid, "names")}, key=lambda x: g.nodes[x]["name"].lower())
    published = sorted({l["from_id"] for l in g.rel_in(nid, "published_by")}, key=lambda x: g.nodes[x]["name"].lower())
    n_rec = sum(1 for r in figs if r["side"] == "record" and r["basis"] != "derived")
    n_cl = sum(1 for r in figs if r["side"] == "claim")
    idents = ctx.idents.get(oid, [])
    is_maker = any(l["to_id"] == nid and l["relation"] in gk.UPSTREAM_LEGS for l in chain)
    dc_sites = [s for s in site_ids if ctx.sites[s[5:]]["kind"] in ("datacenter", "crypto_to_ai_conversion", "mixed_building_with_datacenter")]

    kind = ent["kind"] or "organisation"
    country = bs.COUNTRY.get(ent["country"], bx.EXTRA_COUNTRY.get(ent["country"], "")) if ent["country"] else ""
    lede = (f"{e(kind[:1].upper() + kind[1:])}. The ledger lists it at {plural(len(site_ids), 'site')}"
            + (f" in {plural(len(countries), 'country', 'countries')}" if countries else "")
            + f", holds {plural(len(figs), 'figure')} about it and its sites ({n_rec:,} from records, {n_cl:,} claimed) and "
            + f"{plural(len(chain) + len(grp), 'documented link')}.")
    facts = [("Kind", e(kind)),
             ("Country", (f'<a href="{P}country/{e(ent["country"])}.html">{e(country)}</a> <span class="m">as the register gives it</span>' if country else "not recorded")),
             ("Names it is listed under", ("; ".join(f"“{e(x)}”" for x in names_listed) if names_listed else "<span class=\"m\">none at a site</span>")),
             ("Identifiers", (" · ".join(f'{e({"wikidata": "Wikidata", "lei": "LEI", "sec_cik": "SEC CIK"}.get(i["scheme"], i["scheme"]))} <a href="{e(i["source_url"])}" rel="noopener">{e(i["identifier"])}</a>' for i in idents)
                              if idents else '<span class="m">none recorded yet</span>'))]
    if ent["notes"]:
        facts.append(("Notes", e(ent["notes"])))

    body = [nav(P, [f'<a href="index.html">Organisations</a>'], "org/"),
            f'<p class="eyebrow">Organisation · {e(oid)}</p><h1>{e(n["name"])}</h1><p class="lede">{lede}</p>',
            '<div class="cols2"><main>',
            '<dl class="facts">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts) + "</dl>",
            tiles([(f"{len(site_ids):,}", "sites listed with it" + (" or its group" if len(group) > 1 else "")),
                   (f"{len(countries):,}", "countries its sites are in"),
                   (f"{len(figs):,}", f"figures: {n_rec:,} from records, {n_cl:,} claims"),
                   (f"{len(chain) + len(grp):,}", "documented links (chain and group)")])]
    eb = f"org={e(oid)}"
    body.append(section("What the public record holds", "gapc", "For it and the sites listed with it: one cell per topic, the same on every organisation's page.",
                        topic_grid(figs, eb, P)))
    body.append(section("Figures about the organisation itself", "rec", "Company-wide figures, and figures in ledger entries that concern it alone: records first, then what was computed, then claims.",
                        fig_table(own, ctx, P, 40, f"{P}explore.html?subject={e(oid)}") or '<p class="none">No figure about the organisation as a whole yet.</p>'))
    if site_ids:
        rows = []
        for s, l, via in sorted(sites, key=lambda x: (ctx.sites[x[0][5:]]["country"], g.nodes[x[0]]["name"].lower())):
            sr = ctx.sites[s[5:]]
            sf = ctx.by_subject.get(s, [])
            rec = sum(1 for r in sf if r["side"] == "record" and r["basis"] != "derived")
            cl = sum(1 for r in sf if r["side"] == "claim")
            role = l["note"].split(";", 1)[0]
            how = e(role) + (f' <span class="m">through {ctx.ref(via, P)}</span>' if via != nid else "")
            rows.append(f'<tr><td>{ctx.ref(s, P)}<div class="m">{e(bs.KIND.get(sr["kind"], sr["kind"]))}</div></td>'
                        f'<td class="m">{e(", ".join(x for x in (sr["locality"], sr["admin_region"], bs.COUNTRY.get(sr["country"], "")) if x))}</td>'
                        f'<td class="m">{how}</td><td class="v">{rec or ""}</td><td class="v">{cl or ""}</td></tr>')
        body.append(section("Its sites", "rec", f"{plural(len(site_ids), 'site')} in the register where it is named, from the list each site came from. "
                            f'<a href="{P}map.html?org={e(oid)}">On the map</a>' if False else
                            f"{plural(len(site_ids), 'site')} in the register where it is named, as the list each site came from names it.",
                            '<div class="tw"><table><thead><tr><th>Site</th><th>Where</th><th>How it is named</th><th>Records</th><th>Claims</th></tr></thead><tbody>'
                            + "".join(rows) + "</tbody></table></div>", "sites"))
    else:
        body.append(section("Its sites", "rec", "", '<p class="none">No site in the register is listed with it.</p>', "sites"))
    body.append(section("Its group, and companies acting for it", "rec",
                        "Parents, subsidiaries, project companies and earlier names, only where a document states the link.",
                        link_table(grp, ctx, P) or '<p class="none">No document read yet states its parent, its subsidiaries or a company acting for it.</p>'))
    gap_note = ""
    if is_maker:
        gap_note = "No public record read yet names a datacenter that runs its chips: the chain stops at the chip maker."
    elif dc_sites:
        gap_note = "No public record read yet names the chips running at its sites: the chain stops before the datacenter."
    body.append(section("The chain", "rec", "Who supplies it and its sites, and whom they supply, as documents state it.",
                        chain_block(chain, ctx, P, "ch-org", {nid, *site_ids}, gap_note)))
    if published:
        pl = "".join(f'<li>{ctx.ref(d, P)} <span class="m">{e(g.nodes[d]["kind"].replace("_", " "))}</span></li>' for d in published[:30])
        more = f'<p class="m">and {len(published) - 30} more</p>' if len(published) > 30 else ""
        body.append(section("Documents it published", "claim", "Read by the ledger. What a company publishes about itself is a claim unless an auditor or regulator stands behind it.",
                            f"<ul>{pl}</ul>{more}"))
    else:
        body.append(section("Documents it published", "claim", "", '<p class="none">None read by the ledger.</p>'))
    if entries:
        body.append(section("Entries that name it", "", "Ledger entries whose subject names it.",
                            "<ul>" + "".join(f'<li>{ctx.ref(x, P)} <span class="m">{e(g.nodes[x]["country"].replace(";", ", "))}</span></li>' for x in entries) + "</ul>"))
    else:
        body.append(section("Entries that name it", "", "", '<p class="none">No entry names it.</p>'))
    missing = []
    by = defaultdict(Counter)
    for r in figs:
        by[TOPIC_OF.get(r["metric"], LAST_TOPIC)][r["side"]] += 1
    for i, (t, _) in enumerate(TOPICS[:3] + TOPICS[5:6]):
        ti = [x[0] for x in TOPICS].index(t)
        if not by.get(ti, Counter())["record"]:
            missing.append(f"{e(t)}: no figure from a record")
    if not grp and len(site_ids) and oid.startswith("org-"):
        missing.append("Its parent company: no document read yet")
    if gap_note:
        missing.append(gap_note)
    if not idents:
        missing.append("Identifiers (Wikidata, LEI, national register): not recorded yet")
    body.append(section("Not found yet", "gapc", "", gaps_box(missing)))
    body.append("</main>")
    body.append(side_panel(ctx, nid, P, org_ring(ctx, nid, sites, grp, chain, entries, countries, P), "organisation", oid,
                           [(f"{P}explore.html?{eb}", f"Its {len(figs):,} figures in Explore"), (f"{REPO}/blob/main/data/graph/links.csv", "Every link (CSV)")]))
    body.append("</div>")
    jl = {"@context": "https://schema.org", "@type": "Organization", "@id": n["iri"], "name": n["name"], "url": bx.SITE_URL + n["page"]}
    same = [f"http://www.wikidata.org/entity/{i['identifier']}" for i in idents if i["scheme"] == "wikidata"]
    if same:
        jl["sameAs"] = same
    desc = f"{n['name']}: what public records show about it and its sites, with its own statements kept apart. From the Compute Ledger."
    return head(f"{n['name']} · Compute Ledger", desc, P, jl) + "\n".join(body) + "\n" + foot(P)


def org_ring(ctx, nid, sites, grp, chain, entries, countries, P):
    g = ctx.g
    items, seen = [], set()
    for l in grp:
        o = l["to_id"] if l["from_id"] == nid else l["from_id"]
        if o not in seen:
            seen.add(o); items.append(ring_item(ctx, o, P, l["side"]))
    cps = Counter()
    side_of = {}
    for l in chain:
        for o in (l["from_id"], l["to_id"]):
            if o != nid and not o.startswith("site:") or (o.startswith("site:") and g.nodes[o]["kind"] in ("nuclear_plant",)):
                if o != nid:
                    cps[o] += 1; side_of[o] = l["side"]
    refiners = [o for o in cps if g.nodes[o]["type"] == "site" and g.nodes[o]["kind"] == "smelter_refiner"]
    for o, _ in sorted(cps.items(), key=lambda x: (-x[1], g.nodes[x[0]]["name"])):
        if o in refiners or o in seen:
            continue
        seen.add(o); items.append(ring_item(ctx, o, P, side_of[o]))
    if refiners:
        items.append({"id": "refiners", "name": f"{len(refiners)} smelters and refiners", "type": "sites", "count": len(refiners), "side": "claim", "page": "#ch-org"})
    colisted = Counter()
    site_set = {s for s, _, _ in sites}
    for s in site_set:
        for l in g.rel_out(s, "listed_operator"):
            if l["to_id"] != nid and l["to_id"] not in seen and l["to_id"] not in g.org_group(nid):
                colisted[l["to_id"]] += 1
    for o, _ in sorted(colisted.items(), key=lambda x: (-x[1], g.nodes[x[0]]["name"]))[:3]:
        seen.add(o); items.append(ring_item(ctx, o, P, ""))
    if site_set:
        if len(site_set) <= 3:
            for s in sorted(site_set):
                items.append(ring_item(ctx, s, P, ""))
        else:
            items.append({"id": "sites", "name": f"{len(site_set)} sites", "type": "sites", "count": len(site_set), "side": "", "page": "#sites"})
    for c in countries[:3]:
        items.append(ring_item(ctx, f"country:{c}", P, ""))
    if len(countries) > 3:
        items.append({"id": "countries", "name": f"{len(countries) - 3} more countries", "type": "country", "side": "", "page": "#sites"})
    if entries:
        items.append({"id": "entries", "name": f"{len(entries)} entries", "type": "entry", "count": len(entries), "side": "", "page": ""})
    return items[:14]


def side_panel(ctx, nid, P, ring, kind_word, ident, downloads):
    n = ctx.g.nodes[nid]
    center = {"name": n["name"]}
    svg = gk.ego_drawing(center, ring, f"eg-{kind_word[:3]}") if ring else ""
    return ('<aside class="side">'
            + (f'<div class="panel"><h3>Neighbourhood</h3>{svg}<div class="lglegend"><span>○ organisation</span><span>□ site</span><span>■ sites, entries</span>'
               '<span>◇ country</span><span><i></i>record</span><span><i class="c"></i>claim</span><span><i class="l"></i>in the ledger’s tables</span></div>'
               '<p class="m" style="margin:8px 0 0">Select a name to go to its page.</p></div>' if svg else "")
            + f'<div class="panel"><h3>Cite this page</h3><p class="m" style="margin:0">{e(cite_line(ctx.cite, kind_word, ident, n["iri"]))}</p></div>'
            + '<div class="panel"><h3>Download</h3><p class="m" style="margin:0">' + " · ".join(f'<a href="{h}">{e(t)}</a>' for h, t in downloads)
            + f' · <a href="{REPO}/blob/main/data/graph/graph.jsonld">The whole graph (JSON-LD)</a></p></div></aside>')


# --------------------------------------------------------------------------------------------------- country pages

def country_page(ctx, cc, region_rows):
    g = ctx.g
    nid = f"country:{cc}"
    n = g.nodes[nid]
    P = "../"
    sites = sorted([s for s in ctx.sites.values() if s["country"] == cc], key=lambda s: s["name"].lower())
    site_nids = [f"site:{s['site_id']}" for s in sites]
    ents_here = [x for x in ctx.ents.values() if x["country"] == cc]
    entries = sorted([nid_ for nid_, nn in g.nodes.items() if nn["type"] == "entry" and cc in nn["country"].split(";")], key=lambda x: g.nodes[x]["name"].lower())
    figs = []
    for s in site_nids:
        figs += ctx.by_subject.get(s, [])
    for x in entries:
        figs += ctx.by_subject.get(x, [])
    for x in ents_here:
        figs += ctx.by_subject.get(f"org:{x['entity_id']}", [])
    n_rec = sum(1 for r in figs if r["side"] == "record" and r["basis"] != "derived")
    n_cl = sum(1 for r in figs if r["side"] == "claim")
    placed = sum(1 for s in sites if s["lat"])
    orgs = Counter()
    for s in site_nids:
        for l in g.rel_out(s, "listed_operator"):
            orgs[l["to_id"]] += 1
    chain = []
    for s in site_nids:
        chain += g.chain_links(s)
    chain = list({l["link_id"]: l for l in chain}.values())
    docs_used = Counter()
    pubs = Counter()
    for r in figs:
        docs_used[r["source_url"]] += 1
        if r["side"] == "record" and r["basis"] != "derived":
            pubs[r["source_publisher"]] += 1
    name = n["name"]
    lede = (f"The ledger holds {plural(len(sites), 'site')} in {e(name)} ({placed:,} placed on the map), {plural(len(figs), 'figure')} about them, "
            f"about organisations based there and about the country as a whole ({n_rec:,} from records, {n_cl:,} claimed), and "
            f"{plural(len(entries), 'entry', 'entries')}.")
    body = [nav(P, ['<a href="index.html">Countries</a>'], "country/"),
            f'<p class="eyebrow">Country · {e(cc)}</p><h1>{e(name)}</h1><p class="lede">{lede}</p>', '<div class="cols2"><main>',
            tiles([(f"{len(sites):,}", f"sites, {placed:,} placed"), (f"{len(orgs):,}", "organisations listed at its sites"),
                   (f"{len(figs):,}", f"figures: {n_rec:,} from records, {n_cl:,} claims"), (f"{len(docs_used):,}", "documents behind them")])]
    eb = f"country={e(cc)}"
    body.append(section("What the public record holds", "gapc", "For its sites and for the country as a whole: one cell per topic, the same on every country's page.",
                        topic_grid(figs, eb, P)))
    if region_rows:
        rows = "".join(f'<tr id="r-{e(rid)}"><td>{e(rn)}</td><td class="v">{ns:,}</td><td class="v">{nr or ""}</td><td class="v">{nc or ""}</td></tr>'
                       for rid, rn, ns, nr, nc in region_rows)
        body.append(section("Regions", "", "States, provinces and counties as the site lists give them.",
                            '<div class="tw"><table><thead><tr><th>Region</th><th>Sites</th><th>Records</th><th>Claims</th></tr></thead><tbody>' + rows + "</tbody></table></div>"))
    else:
        body.append(section("Regions", "", "", '<p class="none">No site here names its region.</p>'))
    if sites:
        kinds = Counter(bs.KIND.get(s["kind"], s["kind"]) for s in sites)
        top = sorted(sites, key=lambda s: (-len(ctx.by_subject.get(f"site:{s['site_id']}", [])), s["name"].lower()))[:25]
        rows = []
        for s in top:
            sf = ctx.by_subject.get(f"site:{s['site_id']}", [])
            rec = sum(1 for r in sf if r["side"] == "record" and r["basis"] != "derived")
            cl = sum(1 for r in sf if r["side"] == "claim")
            rows.append(f'<tr><td>{ctx.ref("site:" + s["site_id"], P)}<div class="m">{e(s["operator"])}</div></td><td class="m">{e(bs.KIND.get(s["kind"], s["kind"]))}</td>'
                        f'<td class="m">{e(s["admin_region"])}</td><td class="v">{rec or ""}</td><td class="v">{cl or ""}</td></tr>')
        body.append(section("Sites", "rec", " · ".join(f"{v:,} {e(k.lower())}" for k, v in kinds.most_common())
                            + f'. <a href="{P}sites/index.html">All sites</a> · <a href="{P}map.html?country={e(cc)}">On the map</a>',
                            '<div class="tw"><table><thead><tr><th>Site</th><th>Kind</th><th>Region</th><th>Records</th><th>Claims</th></tr></thead><tbody>'
                            + "".join(rows) + "</tbody></table></div>"
                            + (f'<p class="m" style="margin-top:8px">The {min(25, len(sites))} with the most figures, of {len(sites):,}.</p>' if len(sites) > 25 else "")))
    else:
        body.append(section("Sites", "rec", "", '<p class="none">No site in the register here yet.</p>'))
    if orgs:
        rows = "".join(f'<li>{ctx.ref(o, P)} <span class="m">{plural(c, "site")}</span></li>' for o, c in sorted(orgs.items(), key=lambda x: (-x[1], g.nodes[x[0]]["name"].lower()))[:40])
        based = ""
        if ents_here:
            based = '<p class="m" style="margin-top:10px">Based here, as the register gives it: ' + ", ".join(ctx.ref(f"org:{x['entity_id']}", P) for x in sorted(ents_here, key=lambda x: x["name"].lower())[:30]) + "</p>"
        body.append(section("Organisations listed at its sites", "", "By the number of sites each is named at.",
                            f'<ul class="cols">{rows}</ul>' + (f'<p class="m">and {len(orgs) - 40} more</p>' if len(orgs) > 40 else "") + based))
    else:
        body.append(section("Organisations listed at its sites", "", "", '<p class="none">None named.</p>'))
    body.append(section("The chain", "rec", "Links that touch a site here, as documents state them.",
                        chain_block(chain, ctx, P, "ch-cty", set())))
    if pubs:
        rows = "".join(f'<li>{e(p or "publisher not recorded")} <span class="m">{plural(c, "figure")}</span></li>' for p, c in pubs.most_common(15))
        body.append(section("Who keeps the records", "rec", "Publishers of the record-side figures above: regulators, grid operators, utilities, statistics offices and others.",
                            f"<ul>{rows}</ul>"))
    else:
        body.append(section("Who keeps the records", "rec", "", '<p class="none">No figure from a record yet.</p>'))
    if entries:
        body.append(section("Entries", "", "Ledger entries about the country or a place in it.",
                            "<ul>" + "".join(f"<li>{ctx.ref(x, P)}</li>" for x in entries) + "</ul>"))
    else:
        body.append(section("Entries", "", "", '<p class="none">No entry yet.</p>'))
    missing = []
    by = defaultdict(Counter)
    for r in figs:
        by[TOPIC_OF.get(r["metric"], LAST_TOPIC)][r["side"]] += 1
    for t in ("Electricity used", "Grid connection and capacity", "Water", "Generators, fuel and air pollution", "Money, jobs and prices"):
        ti = [x[0] for x in TOPICS].index(t)
        if not by.get(ti, Counter())["record"]:
            missing.append(f"{e(t)}: no figure from a record")
    if sites and not placed:
        missing.append("No site placed on the map")
    if not chain:
        missing.append("No documented supply link at a site here")
    body.append(section("Not found yet", "gapc", "", gaps_box(missing)))
    body.append("</main>")
    ring = [ring_item(ctx, f"region:{cc}/{rid}", P, "", None, rn, f"#r-{rid}", "country") for rid, rn, *_ in sorted(region_rows, key=lambda x: -x[2])[:6]]
    ring += [ring_item(ctx, o, P, "") for o, _ in sorted(orgs.items(), key=lambda x: (-x[1], g.nodes[x[0]]["name"].lower()))[:6]]
    if entries:
        ring.append({"id": "entries", "name": f"{len(entries)} entries", "type": "entry", "count": len(entries), "side": "", "page": ""})
    body.append(side_panel(ctx, nid, P, ring, "country", cc, [(f"{P}explore.html?{eb}", f"Its {len(figs):,} figures in Explore"),
                                                              (f"{P}map.html?country={e(cc)}", "Its sites on the map")]))
    body.append("</div>")
    jl = {"@context": "https://schema.org", "@type": "Country", "@id": n["iri"], "name": name, "identifier": cc}
    return head(f"{name} · Compute Ledger", f"{name}: what public records show about compute's footprint there. From the Compute Ledger.", P, jl) + "\n".join(body) + "\n" + foot(P)


# --------------------------------------------------------------------------------------------------- document pages

def doc_page(ctx, did, by_pub):
    g = ctx.g
    nid = f"doc:{did}"
    n = g.nodes[nid]
    P = "../"
    url = n["detail"]
    m = ctx.doc_meta[url]
    top = lambda c: sorted(((-v, k) for k, v in c.items() if k))[0][1] if any(k for k in c) else ""  # noqa: E731
    pub, date = top(m["pubs"]), top(m["dates"])
    figs = order_figs([r for r in ctx.meas if r["source_url"] == url])
    states = [l for l in g.inn.get(nid, []) if False] + [l for l in g.links if l["document_id"] == did and (l["relation"] in CHAIN_RELATIONS or l["relation"] in GROUP_RELATIONS)]
    cites = [l for l in g.rel_in(nid, "cites")]
    pub_org = [l["to_id"] for l in g.rel_out(nid, "published_by")]
    sides = Counter(r["side"] for r in figs) + Counter(l["side"] for l in states) + Counter(l["side"] for l in cites)
    kind_side = "record" if sides and sides.most_common(1)[0][0] == "record" else "claim" if sides else ""
    bases = [b for b, _ in m["bases"].most_common()]
    other_titles = [t for t in m["titles"] if t and t != n["name"]]
    checks = sorted({l["from_id"][6:] for l in g.rel_in(nid, "read_again")})
    facts = [("Published by", (ctx.ref(pub_org[0], P) + f' <span class="m">as recorded: {e(pub)}</span>') if pub_org else (e(pub) or "not recorded")),
             ("Date", e(date) or "not recorded"),
             ("Kind of document", (SIDE_TAG.get(kind_side, "") + " " + e(", ".join(b.replace("_", " ") for b in bases))) if bases or kind_side else "not recorded"),
             ("Where to read it", f'<a href="{e(url)}" rel="noopener">{e(gk.short(url, 110))}</a>')]
    if other_titles:
        facts.append(("Also cited as", "; ".join(e(t) for t in sorted(other_titles)[:6])))
    lede = f"{plural(len(figs), 'figure')} read from it, {plural(len(states), 'link')} it states, and {plural(len({l['from_id'] for l in cites}), 'entry', 'entries')} that cite it."
    body = [nav(P, ['<a href="index.html">Documents</a>'], "doc/"),
            f'<p class="eyebrow">Document · {e(did)}</p><h1>{e(n["name"])}</h1><p class="lede">{lede}</p>', '<div class="cols2"><main>',
            '<dl class="facts">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts) + "</dl>",
            tiles([(f"{len(figs):,}", "figures read from it"), (f"{len(states):,}", "links it states"),
                   (f"{len({l['from_id'] for l in cites}):,}", "entries that cite it"), (f"{sum(1 for r in figs if r['second_read'] == 'yes'):,}", "figures read twice")])]
    body.append(section("Figures read from it", "rec", "Each as the document printed it.",
                        fig_table(figs, ctx, P, 80, f"{P}explore.html?doc={e(did)}", show_doc=False) or '<p class="none">No figure is read from it; it is cited for what it says.</p>'))
    body.append(section("Links it states", "rec", "Supply, ownership and other links in the chain, with the line that states each.",
                        link_table(states, ctx, P, show_doc=False) or '<p class="none">It states no link the ledger records.</p>'))
    if cites:
        rows = "".join(f'<li>{ctx.ref(l["from_id"], P)} <span class="m">on its {e(l["side"])} side</span></li>'
                       for l in sorted(cites, key=lambda l: g.nodes[l["from_id"]]["name"].lower()))
        body.append(section("Entries that cite it", "", "", f"<ul>{rows}</ul>"))
    else:
        body.append(section("Entries that cite it", "", "", '<p class="none">No entry cites it directly.</p>'))
    if checks:
        body.append(section("Checks that name it", "calc", "", "<ul>" + "".join(f'<li>{e(ctx.checks[c]["name"])} <span class="m">{e(ctx.checks[c]["date"])}</span></li>' for c in checks if c in ctx.checks) + "</ul>"))
    else:
        body.append(section("Checks that name it", "calc", "", '<p class="none">No check of the ledger names it.</p>'))
    same = [d for d in by_pub.get(pub, []) if d != did][:12] if pub else []
    if same:
        body.append(section("Also by this publisher", "", f"As the ledger records the publisher: {e(pub)}.",
                            "<ul>" + "".join(f'<li>{ctx.ref("doc:" + d, P)} <span class="m">{e(top(ctx.doc_meta[g.nodes["doc:" + d]["detail"]]["dates"]))}</span></li>' for d in same) + "</ul>"))
    else:
        body.append(section("Also by this publisher", "", "", '<p class="none">No other document by this publisher in the ledger.</p>'))
    body.append("</main>")
    ring = []
    for o in pub_org:
        ring.append(ring_item(ctx, o, P, ""))
    subj = Counter()
    for r in figs:
        subj[{"site": "site:", "entity": "org:", "entry": "entry:"}[r["subject_type"]] + r["subject_id"]] += 1
    for s, _ in subj.most_common(5):
        ring.append(ring_item(ctx, s, P, "record" if kind_side == "record" else "claim"))
    for l in states[:4]:
        for o in (l["from_id"], l["to_id"]):
            if o not in {x["id"] for x in ring}:
                ring.append(ring_item(ctx, o, P, l["side"]))
    for l in cites[:3]:
        if l["from_id"] not in {x["id"] for x in ring}:
            ring.append(ring_item(ctx, l["from_id"], P, l["side"]))
    body.append(side_panel(ctx, nid, P, ring[:12], "document", did, [(f"{P}explore.html?doc={e(did)}", f"Its {len(figs):,} figures in Explore")]))
    body.append("</div>")
    jl = {"@context": "https://schema.org", "@type": "CreativeWork", "@id": n["iri"], "name": n["name"], "url": url}
    if pub:
        jl["publisher"] = {"@type": "Organization", "name": pub}
    if date:
        jl["datePublished"] = date
    return head(f"{gk.short(n['name'], 80)} · Compute Ledger", f"What the Compute Ledger read from: {n['name']}.", P, jl) + "\n".join(body) + "\n" + foot(P)


# --------------------------------------------------------------------------------------------------- indexes, chain, search

def index_page(title, eyebrow, intro, cols, rows, prefix, crumb, current, filters=""):
    th = "".join(f"<th>{c}</th>" for c in cols)
    script = """<script>
(()=>{const q=document.getElementById('q'),n=document.getElementById('n'),sels=[...document.querySelectorAll('select[data-f]')];
const rows=[...document.querySelectorAll('#rows tr')];
function f(){const t=q.value.trim().toLowerCase();let v=0;
rows.forEach(r=>{const ok=sels.every(s=>!s.value||r.dataset[s.dataset.f]===s.value)&&(!t||r.textContent.toLowerCase().includes(t));r.hidden=!ok;if(ok)v++;});
n.textContent=v.toLocaleString()+' of '+rows.length.toLocaleString();}
[q,...sels].forEach(x=>x.addEventListener('input',f));f();})();
</script>"""
    return (head(f"{title} · Compute Ledger", intro, prefix) + nav(prefix, [crumb], current)
            + f'<p class="eyebrow">{eyebrow}</p><h1>{e(title)}</h1><p>{intro}</p>'
            + f'<div class="filters"><input id="q" type="search" placeholder="Filter this list" aria-label="Filter this list">{filters}</div><p class="m" id="n" aria-live="polite"></p>'
            + f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody id="rows">' + "".join(rows) + "</tbody></table></div>"
            + script + foot(prefix))


def chain_page(ctx):
    g = ctx.g
    ls = [l for l in g.links if l["relation"] in CHAIN_RELATIONS or (l["relation"] in GROUP_RELATIONS and l["source"].startswith("chain:"))]
    svg, data = gk.chain_drawing(ls, ctx.cnodes, ctx.docnodes, "chain", gap=True)
    svg = svg.replace('<svg class="lg"', '<svg data-base="" class="lg"', 1)
    follow = sorted({k for k in data["nodes"]}, key=lambda k: (data["nodes"][k]["type"] != "org", data["nodes"][k]["name"].lower()))
    opts = "".join(f'<option value="{e(k)}">{e(data["nodes"][k]["name"])}</option>' for k in follow)
    by_rel = Counter(l["relation"] for l in ls)
    sides = Counter(l["side"] for l in ls)
    parties = sorted([n for n in g.nodes.values() if n["type"] == "party"], key=lambda n: n["name"].lower())
    legs = json.loads((ROOT / "data" / "chain" / "summary.json").read_text(encoding="utf-8"))
    empty = ", ".join(x.replace("_", " ") for x in legs["legs_without_edges"])
    body = [nav("", ["The chain"], "chain.html"),
            f'<p class="eyebrow">The chain · {plural(len(ls), "documented link")}</p><h1>From refiner to datacenter</h1>',
            f'<p class="lede">Each line is a link a document states: {sides["record"]:,} from records, {sides["claim"]:,} from companies’ own filings and statements. '
            'Upstream, the links come from the chip makers’ own reports to the SEC; at the sites, from utilities, regulators and licence reports. '
            'Between the chip maker and the datacenter, no public record has been found yet.</p>',
            '<div class="lgcontrols"><label>Follow <select id="chain-follow"><option value="">nothing selected</option>' + opts + "</select></label>"
            '<label><input type="checkbox" checked data-hide="record" data-for="chain"> records</label>'
            '<label><input type="checkbox" checked data-hide="claim" data-for="chain"> claims</label>'
            '<label><input type="checkbox" checked data-hide="gap" data-for="chain"> the gap</label></div>',
            '<div class="lglegend"><span><i></i>record</span><span><i class="c"></i>claim (a company’s own filing or statement)</span><span><i class="g"></i>gap: no record found yet</span>'
            '<span>a number on a line counts the links it stands for</span><span>arrows point the way metal, chips, power or water go</span></div>',
            f'<div class="lgwrap">{svg}</div>', gk.data_script("chain", data), '<div class="lgpanel" id="chain-panel" aria-live="polite"></div>',
            f'<p class="m" style="margin-top:10px">Legs with no documented link yet: {e(empty)}. Ownership links are drawn where both ends are on the drawing; all are in the table below.</p>',
            '<h2 class="rec">Every link, as a table</h2><p class="lede">With the document and the line that states it.</p>',
            link_table(ls, ctx, ""),
            '<h2>Parties named in a document but not yet in a register</h2>',
            '<ul>' + "".join(f'<li id="party-{e(p["node_id"][6:])}">{e(p["name"])}</li>' for p in parties) + "</ul>"]
    return head("The chain · Compute Ledger", "Every documented link from refiner to datacenter, with the document behind each.", "") + "\n".join(body) + "\n" + foot("")


def vocab_page():
    """docs/vocab.html: the ledger's own terms, so that every term's IRI (…/vocab#…) opens its definition."""
    v = json.loads((ROOT / "data" / "graph" / "vocabulary.jsonld").read_text(encoding="utf-8"))
    base = bx.SITE_URL + "vocab#"
    groups = defaultdict(list)
    for t in v["@graph"]:
        frag = t["@id"].replace(base, "")
        if t["@type"] == "rdfs:Class":
            groups["Classes"].append((frag, t["rdfs:label"], t["rdfs:comment"], t.get("rdfs:subClassOf", {}).get("@id", "")))
        elif t["@type"] == "rdf:Property":
            groups["Properties"].append((frag, t["rdfs:label"], t["rdfs:comment"], ""))
        elif t["@type"] == "skos:Concept":
            groups[t["skos:inScheme"]["@id"].replace(base, "")].append((frag, t["skos:prefLabel"], t.get("skos:definition", ""), t.get("skos:closeMatch", {}).get("@id", "")))
    titles = {"Classes": "Classes", "Properties": "Properties of links and figures", "relations": "Relations", "bases": "Kinds of document",
              "metrics": "Metrics", "sitekind": "Kinds of site"}
    body = [nav("", ["Vocabulary"], ""), '<p class="eyebrow">Vocabulary</p><h1>The ledger’s terms</h1>',
            '<p class="lede">Every class, relation and controlled list the ledger’s graph uses, with the standard term it matches where one exists '
            '(schema.org, PROV-O, QUDT). Each term’s address is this page with its name after #. '
            f'Machine-readable: <a href="{REPO}/blob/main/data/graph/vocabulary.jsonld">vocabulary.jsonld</a>.</p>']
    for g in ("Classes", "Properties", "relations", "bases", "sitekind", "metrics"):
        rows = "".join(f'<tr id="{e(f)}"><td><code>{e(f)}</code></td><td><strong>{e(lab)}</strong><div class="m">{e(d)}</div></td><td class="m">{e(m)}</td></tr>'
                       for f, lab, d, m in sorted(groups.get(g, [])))
        body.append(f'<h2 id="{e(g)}">{e(titles[g])}</h2><div class="tw"><table><thead><tr><th>Term</th><th>Meaning</th><th>Matches</th></tr></thead><tbody>{rows}</tbody></table></div>')
    return head("Vocabulary · Compute Ledger", "The classes, relations and controlled lists of the Compute Ledger's graph.", "") + "\n".join(body) + "\n" + foot("")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    ctx = Ctx()
    g = ctx.g
    files: dict[str, str] = {}
    # organisations
    org_rows = []
    for oid in sorted(ctx.ents):
        files[f"org/{oid}.html"] = org_page(ctx, oid)
        nid = f"org:{oid}"
        sites = {s for s, _, _ in g.org_sites(nid)}
        figs = sum(len(ctx.by_subject.get(s, [])) for s in g.org_subjects(nid))
        x = ctx.ents[oid]
        cc = bs.COUNTRY.get(x["country"], "") if x["country"] else ""
        org_rows.append((x["name"].lower(), f'<tr data-k="{e(x["kind"])}"><td><a href="{e(oid)}.html">{e(x["name"])}</a></td><td class="m">{e(x["kind"])}</td>'
                         f'<td class="m">{e(cc)}</td><td class="v">{len(sites) or ""}</td><td class="v">{figs or ""}</td>'
                         f'<td class="v">{len(g.chain_links(nid)) + len(g.group_links(nid)) or ""}</td></tr>'))
    kinds = sorted({x["kind"] for x in ctx.ents.values() if x["kind"]})
    files["org/index.html"] = index_page(
        "Organisations", f"{len(ctx.ents):,} companies, utilities and public bodies",
        "Every organisation the ledger names: as operator, permit holder or applicant at a site, as a party to a documented link, or as the subject of figures. "
        "Each has one page, with the same sections in the same order.",
        ["Organisation", "Kind", "Country", "Sites", "Figures", "Links"], [r for _, r in sorted(org_rows)], "../", "Organisations", "org/",
        '<select data-f="k" aria-label="Kind"><option value="">Every kind</option>' + "".join(f"<option>{e(k)}</option>" for k in kinds) + "</select>")
    # countries
    c_rows = []
    for cc in sorted(n["node_id"][8:] for n in g.nodes.values() if n["type"] == "country"):
        regs = defaultdict(lambda: [0, 0, 0, ""])
        for s in ctx.sites.values():
            if s["country"] == cc and s["admin_region"]:
                rid = bs_slug(s["admin_region"])
                sf = ctx.by_subject.get(f"site:{s['site_id']}", [])
                r = regs[rid]
                r[0] += 1; r[1] += sum(1 for x in sf if x["side"] == "record" and x["basis"] != "derived"); r[2] += sum(1 for x in sf if x["side"] == "claim"); r[3] = s["admin_region"]
        region_rows = sorted(((rid, v[3], v[0], v[1], v[2]) for rid, v in regs.items()), key=lambda x: x[1].lower())
        files[f"country/{cc}.html"] = country_page(ctx, cc, region_rows)
        ns = sum(1 for s in ctx.sites.values() if s["country"] == cc)
        nf = len(re.findall(r"", "")) and 0
        c_rows.append((g.nodes[f"country:{cc}"]["name"], f'<tr><td><a href="{e(cc)}.html">{e(g.nodes["country:" + cc]["name"])}</a></td><td class="m">{e(cc)}</td>'
                       f'<td class="v">{ns or ""}</td><td class="v">{len(region_rows) or ""}</td></tr>'))
    files["country/index.html"] = index_page("Countries", f"{len(c_rows)} countries and groupings",
                                             "Every country the ledger holds a site, an organisation or an entry for. Each page has the same sections in the same order.",
                                             ["Country", "Code", "Sites", "Regions"], [r for _, r in sorted(c_rows)], "../", "Countries", "country/")
    # documents
    by_pub = defaultdict(list)
    for n in sorted(g.nodes.values(), key=lambda n: n["name"].lower()):
        if n["type"] == "doc":
            m = ctx.doc_meta[n["detail"]]
            pub = sorted(((-v, k) for k, v in m["pubs"].items() if k))[0][1] if any(k for k in m["pubs"]) else ""
            if pub:
                by_pub[pub].append(n["node_id"][4:])
    d_rows = []
    for n in sorted((n for n in g.nodes.values() if n["type"] == "doc"), key=lambda n: n["node_id"]):
        did = n["node_id"][4:]
        files[f"doc/{did}.html"] = doc_page(ctx, did, by_pub)
        m = ctx.doc_meta[n["detail"]]
        pub = sorted(((-v, k) for k, v in m["pubs"].items() if k))[0][1] if any(k for k in m["pubs"]) else ""
        date = sorted(((-v, k) for k, v in m["dates"].items() if k))[0][1] if any(k for k in m["dates"]) else ""
        side = m["sides"].most_common(1)[0][0] if m["sides"] else ""
        nfig = sum(m["bases"].values()) if False else sum(1 for r in ctx.meas if r["source_url"] == n["detail"])
        d_rows.append((n["name"].lower(), f'<tr data-s="{e(side)}"><td><a href="{e(did)}.html">{e(gk.short(n["name"], 120))}</a></td><td class="m">{e(pub)}</td>'
                       f'<td class="m">{e(date)}</td><td>{SIDE_TAG.get(side, "")}</td><td class="v">{nfig or ""}</td></tr>'))
    files["doc/index.html"] = index_page("Documents", f"{len(d_rows):,} documents read",
                                         "Every document the ledger cites: for a figure, for an entry, or for a link in the chain.",
                                         ["Document", "Publisher", "Date", "Mostly", "Figures"], [r for _, r in sorted(d_rows)], "../", "Documents", "doc/",
                                         '<select data-f="s" aria-label="Record or claim"><option value="">Records and claims</option><option value="record">Mostly records</option><option value="claim">Mostly claims</option></select>')
    files["chain.html"] = chain_page(ctx)
    files["vocab.html"] = vocab_page()
    # search index
    items = []
    for n in sorted(g.nodes.values(), key=lambda n: n["node_id"]):
        t = n["type"]
        if t not in ("org", "site", "country", "doc", "entry"):
            continue
        sub = {"org": n["kind"], "site": ctx.cnodes[n["node_id"]].get("place", ""), "country": n["node_id"][8:], "doc": "",
               "entry": n["country"].replace(";", ", ")}[t]
        extra = n["detail"] if t in ("site", "entry") else ""
        text = " ".join((n["name"], sub, extra, n["node_id"].split(":", 1)[1])).lower()
        items.append([t, n["name"], n["page"], sub, text])
    files["data/search.json"] = json.dumps({"about": "Names and pages of every site, organisation, country, document and entry in the Compute Ledger, for the search box.",
                                            "items": items}, ensure_ascii=False, separators=(",", ":")) + "\n"
    files["assets/graph.css"] = gk.CSS.lstrip()
    files["assets/graph.js"] = gk.JS.lstrip()

    if a.check:
        bad = [p for p, t in files.items() if not (DOCS / p).exists() or (DOCS / p).read_text(encoding="utf-8") != t]
        stale = [p for d in ("org", "country", "doc") for p in (f"{d}/{x.name}" for x in (DOCS / d).glob("*.html")) if p not in files]
        if bad or stale:
            print(f"docs/ graph pages are stale ({len(bad)} differ, {len(stale)} extra, e.g. {(bad + stale)[:3]}): run python3 site/build_graph_pages.py and commit")
            return 1
        print(f"graph pages up to date ({len(files)} files)")
        return 0
    for p, t in files.items():
        out = DOCS / p
        out.parent.mkdir(parents=True, exist_ok=True)
        if not out.exists() or out.read_text(encoding="utf-8") != t:
            out.write_text(t, encoding="utf-8")
    removed = 0
    for d in ("org", "country", "doc"):
        for x in (DOCS / d).glob("*.html"):
            if f"{d}/{x.name}" not in files:
                x.unlink(); removed += 1
    print(f"wrote {sum(1 for p in files if p.startswith('org/')) - 1} organisation, {sum(1 for p in files if p.startswith('country/')) - 1} country and "
          f"{sum(1 for p in files if p.startswith('doc/')) - 1} document pages, the chain and the search index" + (f"; removed {removed} stale pages" if removed else ""))
    return 0


def bs_slug(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


if __name__ == "__main__":
    raise SystemExit(main())

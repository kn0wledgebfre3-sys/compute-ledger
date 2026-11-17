#!/usr/bin/env python3
"""The ledger as a graph: typed nodes, and links that each say where they come from.

Reads the ledger's own tables and writes data/graph/:
  nodes.csv      one row per node: organisations, sites, countries, regions, documents, entries, checks, figures and
                 the parties a document names that are in no register yet
  links.csv      one row per link, with the document that states it (and the line it was read from) or the table
                 of the ledger that holds it
  graph.jsonld   the same, as JSON-LD (schema.org, PROV-O, QUDT, SKOS), with permanent IRIs on the ledger's site
  vocabulary.jsonld  the ledger's classes, relations and concept schemes (relations, kinds of document, metrics)
  summary.json   counts, and the names the ledger has not matched to an organisation yet

A link exists only where a table of the ledger holds it. Nothing is inferred from a name: a site is linked to an
organisation through sites/organisations/operator_names.csv (each name as the listing printed it, matched by hand),
an organisation to another only through a chain link with a document (sites/chain/edges.csv, leg "ownership").

Checks (any failure exits 1): every link's ends are nodes; every link a document states has the document and the
line; every curated table names ids that exist; no link repeats. Output is deterministic.

    python3 pipeline/build_graph.py [--out DIR]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "data" / "climate_trace_seed"
ORGS = ROOT / "sites" / "organisations"
SITE = "https://kn0wledgebfre3-sys.github.io/compute-ledger/"
REPO = "https://github.com/kn0wledgebfre3-sys/compute-ledger"
sys.path.insert(0, str(ROOT / "site"))
from build_sites import COUNTRY, KIND, metric_label  # noqa: E402

EXTRA_COUNTRY = {"COD": "Democratic Republic of the Congo", "GHA": "Ghana", "MAR": "Morocco", "MMR": "Myanmar",
                 "RUS": "Russia", "EUU": "European Union (EU-wide)", "WLD": "Global"}
COUNTRIES = {**COUNTRY, **EXTRA_COUNTRY}

# the graph's own relations, beyond the chain's (pipeline/measurement_vocab.json "relations")
GRAPH_RELATIONS = {
    "located_in": "a site lies in a region or country, or a region in a country, as the site register gives it",
    "listed_operator": "a site was listed with this organisation as its operator, permit holder, applicant or occupant (the role is in the link's note)",
    "based_in": "an organisation's country as the ledger's register gives it (registration or headquarters)",
    "names": "a ledger entry names this organisation among those it concerns",
    "cites": "a ledger entry cites this document, on its record side or its claim side",
    "about": "a figure is about this site, organisation or entry",
    "read_from": "a figure was read from this document, or computed from documents it names",
    "published_by": "a document was published by this organisation, as the ledger records its publisher",
    "examined": "a check of the ledger examined this site, organisation or entry",
    "read_again": "a check of the ledger read this document again (it is named in the check's findings)",
}
LINK_COLS = ["link_id", "from_id", "relation", "to_id", "side", "basis", "document_id", "quoted_line", "period_start",
             "period_end", "source", "note"]
NODE_COLS = ["node_id", "type", "name", "iri", "page", "country", "kind", "detail"]
UNITS_QUDT = {"t": "unit:TONNE", "MWh": "unit:MegaW-HR", "MW": "unit:MegaW", "count": "unit:NUM", "pct": "unit:PERCENT",
              "m3": "unit:M3", "h": "unit:HR", "m3/day": "unit:M3-PER-DAY", "ha": "unit:HA", "m2": "unit:M2", "km": "unit:KiloM",
              "MVA": "unit:MegaV-A", "USD": "cur:USD", "GBP": "cur:GBP", "EUR": "cur:EUR"}


def read(p: Path) -> list[dict]:
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


def doc_id(url: str) -> str:
    return "d-" + hashlib.sha1(url.strip().encode("utf-8")).hexdigest()[:10]


def iri_page(t: str, i: str) -> tuple[str, str]:
    """(IRI, page path relative to the site root) for a node."""
    if t == "org":
        return SITE + f"org/{i}", f"org/{i}.html"
    if t == "site":
        return SITE + f"sites/{i}", f"sites/{i}.html"
    if t == "country":
        return SITE + f"country/{i}", f"country/{i}.html"
    if t == "region":
        c, r = i.split("/", 1)
        return SITE + f"country/{c}#r-{r}", f"country/{c}.html#r-{r}"
    if t == "doc":
        return SITE + f"doc/{i}", f"doc/{i}.html"
    if t == "entry":
        return SITE + f"index.html#{i}", f"index.html#{i}"
    if t == "figure":
        return SITE + f"explore.html#{i}", f"explore.html#{i}"
    if t == "party":
        return SITE + f"chain.html#party-{i}", f"chain.html#party-{i}"
    if t == "check":
        return SITE + f"index.html#check-{i}", ""
    raise ValueError(t)


def entry_countries(text: str) -> list[str]:
    names = {v: k for k, v in COUNTRIES.items()}
    names["European Union"] = "EUU"
    t = text.strip()
    m = re.fullmatch(r"Multiple \((.*)\)", t)
    out = []
    for p in (m.group(1) if m else t).split(";"):
        p = p.strip()
        code = names.get(p) or ("WLD" if p.startswith("Global") else "EUU" if p in ("EU",) else "USA" if re.match(r"US[- ]", p) else None)
        if code and code not in out:
            out.append(code)
    return out


def build():
    problems: list[str] = []
    vocab = json.loads((ROOT / "pipeline" / "measurement_vocab.json").read_text(encoding="utf-8"))
    chain_rel = {k: v for k, v in vocab["relations"].items() if not k.startswith("_")}
    sites = read(PKG / "site_register.csv")
    ents = read(ROOT / "sites" / "entity_register.csv")
    entries = read(PKG / "entries.csv")
    esrc = read(PKG / "entry_sources.csv")
    meas = read(PKG / "measurements.csv")
    chain = read(ROOT / "data" / "chain" / "edges.csv")
    checks = read(PKG / "checks.csv")
    findings = read(PKG / "findings.csv")
    opn = read(ORGS / "operator_names.csv")
    named = {r["name_as_written"]: r for r in read(ORGS / "named_parties.csv")}
    entry_orgs = read(ORGS / "entry_organisations.csv")
    pubs = {r["publisher_as_written"]: r["entity_id"] for r in read(ORGS / "publisher_names.csv")}
    idents = read(ORGS / "identifiers.csv") if (ORGS / "identifiers.csv").exists() else []

    nodes: dict[str, dict] = {}
    links: dict[str, dict] = {}

    def node(t, i, name, country="", kind="", detail=""):
        nid = f"{t}:{i}"
        if nid not in nodes:
            iri, page = iri_page(t, i)
            nodes[nid] = {"node_id": nid, "type": t, "name": name, "iri": iri, "page": page, "country": country, "kind": kind, "detail": detail}
        return nid

    def link(frm, rel, to, side="", basis="", doc="", quote="", ps="", pe="", source="", note=""):
        for end in (frm, to):
            if end not in nodes:
                problems.append(f"link {frm} {rel} {to} ({source}): {end} is not a node")
                return
        key = "|".join((frm, rel, to, doc, source))
        lid = "l-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]
        if lid in links:
            problems.append(f"link repeats: {frm} {rel} {to} ({source})")
            return
        links[lid] = {"link_id": lid, "from_id": frm, "relation": rel, "to_id": to, "side": side, "basis": basis, "document_id": doc,
                      "quoted_line": quote, "period_start": ps, "period_end": pe, "source": source, "note": note}

    # --- places
    used_cc = {s["country"] for s in sites} | {e["country"] for e in ents if e["country"]}
    for e in entries:
        used_cc |= set(entry_countries(e["country"]))
    for c in sorted(used_cc):
        if c not in COUNTRIES:
            problems.append(f"no country name for {c}")
            continue
        node("country", c, COUNTRIES[c])
    regions = {}
    for s in sites:
        if s["admin_region"]:
            rid = f"{s['country']}/{slug(s['admin_region'])}"
            regions[rid] = (s["admin_region"], s["country"])
    for rid, (name, cc) in sorted(regions.items()):
        r = node("region", rid, name, cc)
        link(r, "located_in", f"country:{cc}", basis="register", source="site_register")

    # --- organisations
    ent_ids = set()
    for e in sorted(ents, key=lambda x: x["entity_id"]):
        ent_ids.add(e["entity_id"])
        o = node("org", e["entity_id"], e["name"], e["country"], e["kind"], e["notes"])
        if e["country"]:
            link(o, "based_in", f"country:{e['country']}", basis="register", source="entity_register")

    # --- documents: every URL a figure, an entry or a chain link cites
    uses = defaultdict(lambda: {"title": Counter(), "publisher": Counter(), "date": Counter(), "basis": Counter(), "side": Counter()})
    for r in meas:
        u = uses[r["source_url"]]
        u["title"][r["source_title"]] += 1; u["publisher"][r["source_publisher"]] += 1; u["date"][r["source_date"]] += 1
        u["basis"][r["basis"]] += 1; u["side"][r["side"]] += 1
    for r in esrc:
        u = uses[r["url"]]
        u["title"][r["title"]] += 1; u["publisher"][r["publisher"]] += 1; u["date"][r["date"]] += 1; u["side"][r["side"]] += 1
    for r in chain:
        u = uses[r["document_url"]]
        u["title"][r["document_title"]] += 1; u["publisher"][r["publisher"]] += 1; u["date"][r["document_date"]] += 1
        u["basis"][r["basis"]] += 1; u["side"][r["side"]] += 1
    top = lambda c: sorted(((-n, k) for k, n in c.items() if k), key=lambda x: (x[0], x[1]))[0][1] if any(c) and any(k for k in c) else ""  # noqa: E731
    docs = {}
    for url in sorted(uses):
        if not url:
            continue
        u = uses[url]
        d = doc_id(url)
        docs[url] = d
        title = top(u["title"]) or url
        node("doc", d, title, kind=top(u["basis"]), detail=url)
        pub = top(u["publisher"])
        if pub in pubs:
            link(f"doc:{d}", "published_by", f"org:{pubs[pub]}", basis="register", source="publisher_names", note=pub)
    for p, i in pubs.items():
        if i not in ent_ids:
            problems.append(f"publisher_names.csv: {p!r} -> {i} is not in sites/entity_register.csv")

    # --- sites
    site_ids = set()
    by_name = defaultdict(list)
    for r in opn:
        by_name[r["name_as_listed"]].append(r)
        if r["entity_id"] and r["entity_id"] not in ent_ids:
            problems.append(f"operator_names.csv: {r['name_as_listed']!r} -> {r['entity_id']} is not in sites/entity_register.csv")
    unmatched = Counter()
    for s in sorted(sites, key=lambda x: x["site_id"]):
        sid = node("site", s["site_id"], s["name"], s["country"], s["kind"], s["operator"])
        site_ids.add(s["site_id"])
        where = f"region:{s['country']}/{slug(s['admin_region'])}" if s["admin_region"] else f"country:{s['country']}"
        link(sid, "located_in", where, basis="register", source="site_register")
        if s["operator"]:
            if s["operator"] not in by_name:
                unmatched[s["operator"]] += 1
            m = re.search(r"https?://\S+", s["register_source"])
            for r in by_name.get(s["operator"], []):
                if r["entity_id"]:
                    link(sid, "listed_operator", f"org:{r['entity_id']}", basis="register", doc=docs.get(m.group(0), "") if m else "",
                         source="site_register", note=f"{r['role']}; listed as “{s['operator']}” in: {s['register_source']}")

    # --- entries
    entry_ids = set()
    for e in entries:
        cc = entry_countries(e["country"])
        eid = node("entry", e["id"], e["site_or_subject"], ";".join(cc), e["category"], e["operator"])
        entry_ids.add(e["id"])
    for r in esrc:
        if r["url"] in docs and r["entry_id"] in entry_ids:
            lk = f"entry:{r['entry_id']}", "cites", f"doc:{docs[r['url']]}"
            key = "|".join(lk + (docs[r["url"]], f"entry_sources:{r['side']}"))
            if "l-" + hashlib.sha1(key.encode()).hexdigest()[:10] not in links:
                link(*lk, side=r["side"], basis="register", doc=docs[r["url"]], source=f"entry_sources:{r['side']}")
    for r in entry_orgs:
        if r["entry_id"] not in entry_ids or r["entity_id"] not in ent_ids:
            problems.append(f"entry_organisations.csv: {r['entry_id']} -> {r['entity_id']}: unknown id")
            continue
        link(f"entry:{r['entry_id']}", "names", f"org:{r['entity_id']}", basis="register", source="entry_organisations",
             note=f"named as “{r['name_as_written']}”")

    # --- chain links (each with its document and quoted line)
    def end(r, side):
        t, i, name = r[f"{side}_type"], r[f"{side}_id"], r[f"{side}_name"]
        if t == "site":
            return f"site:{i}"
        if t == "entity":
            return f"org:{i}"
        if t == "entry":
            return f"entry:{i}"
        m = named.get(name)
        if m and m["entity_id"]:
            if m["entity_id"] not in ent_ids:
                problems.append(f"named_parties.csv: {name!r} -> {m['entity_id']} is not in the register")
            return f"org:{m['entity_id']}"
        return node("party", slug(name)[:80], name)

    for r in chain:
        if not r["quoted_line"] or r["document_url"] not in docs:
            problems.append(f"chain {r['edge_id']}: no document or quoted line")
            continue
        a, b = end(r, "from"), end(r, "to")
        note = "; ".join(x for x in (f"named as “{r['from_name']}”" if r["from_type"] != "named" else "",
                                     f"“{r['to_name']}”" if r["to_type"] != "named" else "", r["leg"].replace("_", " ")) if x)
        link(a, r["relation"], b, side=r["side"], basis=r["basis"], doc=docs[r["document_url"]], quote=r["quoted_line"],
             ps=r["period_start"], pe=r["period_end"], source=f"chain:{r['edge_id']}", note=r["leg"])

    # --- figures
    for r in meas:
        subj = {"site": "site", "entity": "org", "entry": "entry"}[r["subject_type"]]
        val = r["value_as_published"]
        f = node("figure", r["measurement_id"], f"{metric_label(r['metric'])}: {val}", kind=r["metric"], detail=r["side"])
        link(f, "about", f"{subj}:{r['subject_id']}", side=r["side"], basis=r["basis"], source="measurements")
        if r["source_url"] in docs:
            link(f, "read_from", f"doc:{docs[r['source_url']]}", side=r["side"], basis=r["basis"], doc=docs[r["source_url"]], source="measurements")

    # --- checks
    subj_seen = set()
    for c in checks:
        node("check", c["check_id"], c["name"], kind="check", detail=c["date"])
    for f in findings:
        t = {"site": "site", "entity": "org", "entry": "entry"}.get(f["subject_type"])
        if not t or not f["subject_id"]:
            continue
        k = (f["check_id"], t, f["subject_id"])
        if k in subj_seen or f"{t}:{f['subject_id']}" not in nodes:
            continue
        subj_seen.add(k)
        link(f"check:{f['check_id']}", "examined", f"{t}:{f['subject_id']}", basis="register", source="findings")

    for c in checks:
        seen_docs = set()
        for fp in c["findings_file"].split(";"):
            fp = ROOT / fp.strip()
            if fp.suffix != ".csv" or not fp.exists():
                continue
            for row in read(fp):
                for k, v in row.items():
                    if not k or not v or not ("url" in k.lower() or "evidence" in k.lower() or "source" in k.lower()):
                        continue
                    for u in re.findall(r"https?://[^\s;,|]+", v):
                        u = u.rstrip(").")
                        if u in docs and u not in seen_docs:
                            seen_docs.add(u)
                            link(f"check:{c['check_id']}", "read_again", f"doc:{docs[u]}", basis="register", doc=docs[u], source="findings_file")

    # --- identifiers (Wikidata, LEI, national registers), each from the page it was read on
    for r in idents:
        if r["entity_id"] not in ent_ids:
            problems.append(f"identifiers.csv: {r['entity_id']} is not in the register")
        if not r["source_url"].startswith("http"):
            problems.append(f"identifiers.csv: {r['entity_id']} {r['scheme']}: no source URL")

    rel_ok = set(GRAPH_RELATIONS) | set(chain_rel)
    for l in links.values():
        if l["relation"] not in rel_ok:
            problems.append(f"{l['link_id']}: relation {l['relation']} is not in the vocabulary")
    return nodes, links, docs, problems, unmatched, vocab, idents


def jsonld(nodes, links, meas_rows, vocab, idents):
    ctx = {"schema": "https://schema.org/", "prov": "http://www.w3.org/ns/prov#", "skos": "http://www.w3.org/2004/02/skos/core#",
           "qudt": "http://qudt.org/schema/qudt/", "unit": "http://qudt.org/vocab/unit/", "cur": "http://qudt.org/vocab/currency/",
           "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "owl": "http://www.w3.org/2002/07/owl#", "cl": SITE + "vocab#",
           "xsd": "http://www.w3.org/2001/XMLSchema#",
           "name": "schema:name", "url": {"@id": "schema:url", "@type": "@id"},
           "containedInPlace": {"@id": "schema:containedInPlace", "@type": "@id"},
           "from": {"@id": "cl:from", "@type": "@id"}, "to": {"@id": "cl:to", "@type": "@id"},
           "relation": {"@id": "cl:relation", "@type": "@id"}, "side": "cl:side", "basis": {"@id": "cl:basis", "@type": "@id"},
           "wasDerivedFrom": {"@id": "prov:wasDerivedFrom", "@type": "@id"}, "quotedLine": "cl:quotedLine",
           "about": {"@id": "cl:about", "@type": "@id"}, "metric": {"@id": "cl:metric", "@type": "@id"},
           "valueAsPublished": "cl:valueAsPublished", "numericValue": {"@id": "qudt:numericValue", "@type": "xsd:decimal"},
           "hasUnit": {"@id": "qudt:unit", "@type": "@id"}, "unitText": "cl:unitText", "periodStart": "cl:periodStart", "periodEnd": "cl:periodEnd",
           "identifier": "schema:identifier", "latitude": "schema:latitude", "longitude": "schema:longitude", "kind": "cl:kind",
           "sameAs": {"@id": "schema:sameAs", "@type": "@id"}}
    TYPES = {"org": ["schema:Organization", "cl:Organisation"], "site": ["schema:Place", "cl:Site"], "country": ["schema:Country"],
             "region": ["schema:AdministrativeArea"], "doc": ["schema:CreativeWork", "prov:Entity", "cl:Document"],
             "entry": ["schema:CreativeWork", "cl:Entry"], "check": ["prov:Activity", "cl:Check"], "party": ["cl:NamedParty"],
             "figure": ["cl:Figure", "qudt:QuantityValue"]}
    iri = {n["node_id"]: n["iri"] for n in nodes.values()}
    fig = {r["measurement_id"]: r for r in meas_rows}
    site_geo = {r["site_id"]: r for r in read(PKG / "site_register.csv")}
    same = defaultdict(list)
    for r in idents:
        if r["scheme"] == "wikidata":
            same[r["entity_id"]].append("http://www.wikidata.org/entity/" + r["identifier"])
        elif r["scheme"] == "lei":
            same[r["entity_id"]].append("https://search.gleif.org/#/record/" + r["identifier"])
    graph = []
    for n in sorted(nodes.values(), key=lambda x: x["node_id"]):
        t, i = n["type"], n["node_id"].split(":", 1)[1]
        o = {"@id": n["iri"], "@type": TYPES[t], "name": n["name"]}
        if t == "country":
            o["identifier"] = i
        if t == "site":
            g = site_geo[i]
            if g["lat"] and g["lon"]:
                o["latitude"], o["longitude"] = float(g["lat"]), float(g["lon"])
            o["kind"] = {"@id": f"cl:sitekind/{g['kind']}"}
        if t == "org":
            if n["kind"]:
                o["kind"] = n["kind"]
            if same.get(i):
                o["sameAs"] = sorted(same[i])
        if t == "doc":
            o["url"] = n["detail"]
        if t == "figure":
            r = fig[i]
            o["metric"] = f"cl:metric/{r['metric']}"
            o["valueAsPublished"] = r["value_as_published"]
            if r["value_canonical"]:
                o["numericValue"] = r["value_canonical"]
                u = UNITS_QUDT.get(r["canonical_unit"])
                if u:
                    o["hasUnit"] = u
                else:
                    o["unitText"] = r["canonical_unit"]
            for k, c in (("period_start", "periodStart"), ("period_end", "periodEnd")):
                if r[k]:
                    o[c] = r[k]
            o["side"] = r["side"]
            o["basis"] = f"cl:basis/{r['basis']}"
        graph.append(o)
    for l in sorted(links.values(), key=lambda x: x["link_id"]):
        o = {"@id": SITE + "graph#" + l["link_id"], "@type": "cl:Link", "from": iri[l["from_id"]], "relation": f"cl:relation/{l['relation']}",
             "to": iri[l["to_id"]]}
        if l["side"]:
            o["side"] = l["side"]
        if l["basis"] and l["basis"] != "register":
            o["basis"] = f"cl:basis/{l['basis']}"
        if l["document_id"]:
            o["wasDerivedFrom"] = iri["doc:" + l["document_id"]]
        if l["quoted_line"]:
            o["quotedLine"] = l["quoted_line"]
        for k, c in (("period_start", "periodStart"), ("period_end", "periodEnd")):
            if l[k]:
                o[c] = l[k]
        graph.append(o)
    # containedInPlace stated directly on sites and regions
    byid = {g["@id"]: g for g in graph}
    for l in links.values():
        if l["relation"] == "located_in":
            byid[iri[l["from_id"]]]["containedInPlace"] = iri[l["to_id"]]
    return {"@context": ctx, "@graph": graph}


def vocabulary(vocab):
    V = SITE + "vocab#"
    g = []
    cls = {"Organisation": ("schema:Organization", "A company, utility, public body or other organisation the ledger names."),
           "Site": ("schema:Place", "A datacenter, fab, smelter or refiner, mining site or power plant in the site register."),
           "Document": ("schema:CreativeWork", "A document the ledger read: a record (regulator, court, grid operator, statistics office, auditor, registry, customs) or a claim (what a company or government says)."),
           "Entry": ("schema:CreativeWork", "A ledger entry: what the records show about one subject, what is claimed, and what is missing."),
           "Figure": ("qudt:QuantityValue", "One number as a document published it, with its period, the document, and whether it is a record or a claim."),
           "Link": ("prov:Entity", "A statement that one node relates to another, with the document that states it and the line it was read from."),
           "Check": ("prov:Activity", "A check of the ledger: what was read again, how, and what was found."),
           "NamedParty": ("schema:Thing", "A party a document names that is in no register of the ledger yet.")}
    for k, (sup, d) in cls.items():
        g.append({"@id": V + k, "@type": "rdfs:Class", "rdfs:label": k, "rdfs:comment": d, "rdfs:subClassOf": {"@id": sup}})
    props = {"from": "The node a link starts from.", "to": "The node a link points to.", "relation": "What the link says (a concept in cl:relations).",
             "side": "record or claim: whether the document that states it is a record or a claim.", "basis": "The kind of document (a concept in cl:bases).",
             "quotedLine": "The words in the document that state the link, copied exactly.", "about": "What a figure is about.",
             "metric": "What a figure measures (a concept in cl:metrics).", "valueAsPublished": "The value as the document printed it.",
             "unitText": "The unit, where no QUDT unit is given.", "periodStart": "Start of the period a figure or link covers.",
             "periodEnd": "End of the period.", "kind": "The kind of site or organisation."}
    for k, d in props.items():
        g.append({"@id": V + k, "@type": "rdf:Property", "rdfs:label": k, "rdfs:comment": d})
    schemes = {"relations": {**{k: v for k, v in vocab["relations"].items() if not k.startswith("_")}, **GRAPH_RELATIONS},
               "bases": {k: v for k, v in vocab["bases"].items() if not k.startswith("_")},
               "metrics": {k: v for k, v in vocab["metrics"].items() if not k.startswith("_")},
               "sitekind": KIND}
    for s, items in schemes.items():
        g.append({"@id": V + s, "@type": "skos:ConceptScheme", "skos:prefLabel": s})
        for k, d in sorted(items.items()):
            c = {"@id": V + f"{s[:-1] if s.endswith('s') else s}/{k}" if s != "sitekind" else V + f"sitekind/{k}", "@type": "skos:Concept",
                 "skos:inScheme": {"@id": V + s}, "skos:prefLabel": k.replace("_", " ")}
            if s == "relations":
                c["@id"] = V + f"relation/{k}"
            elif s == "bases":
                c["@id"] = V + f"basis/{k}"
            elif s == "metrics":
                c["@id"] = V + f"metric/{k}"
                c["skos:prefLabel"] = metric_label(k)
            c["skos:definition"] = d if isinstance(d, str) else json.dumps(d, ensure_ascii=False)
            g.append(c)
    close = {"relation/located_in": "schema:containedInPlace", "relation/published_by": "schema:publisher", "relation/cites": "schema:citation",
             "relation/read_from": "prov:wasDerivedFrom", "relation/owns": "schema:subOrganization", "relation/about": "schema:about"}
    for c in g:
        k = c["@id"].replace(V, "")
        if k in close:
            c["skos:closeMatch"] = {"@id": close[k]}
    return {"@context": {"rdfs": "http://www.w3.org/2000/01/rdf-schema#", "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                         "skos": "http://www.w3.org/2004/02/skos/core#", "schema": "https://schema.org/", "prov": "http://www.w3.org/ns/prov#",
                         "qudt": "http://qudt.org/schema/qudt/"}, "@graph": g}


def write_csv(p: Path, cols, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "data" / "graph"))
    a = ap.parse_args()
    nodes, links, docs, problems, unmatched, vocab, idents = build()
    for p in problems[:60]:
        print(p)
    if problems:
        print(f"{len(problems)} problems")
        return 1
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    write_csv(od / "nodes.csv", NODE_COLS, sorted(nodes.values(), key=lambda n: n["node_id"]))
    write_csv(od / "links.csv", LINK_COLS, sorted(links.values(), key=lambda l: (l["from_id"], l["relation"], l["to_id"], l["link_id"])))
    meas = read(PKG / "measurements.csv")
    jl = jsonld(nodes, links, meas, vocab, idents)
    known = {o["@id"] for o in jl["@graph"]}
    dangling = [(o["@id"], k) for o in jl["@graph"] for k in ("from", "to", "wasDerivedFrom", "containedInPlace") if o.get(k) and o[k] not in known]
    if dangling:
        print(f"graph.jsonld: {len(dangling)} references to nodes it does not hold, e.g. {dangling[:3]}")
        return 1
    (od / "graph.jsonld").write_text(json.dumps(jl, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    (od / "vocabulary.jsonld").write_text(json.dumps(vocabulary(vocab), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    summary = {"nodes": len(nodes), "links": len(links),
               "nodes_by_type": dict(sorted(Counter(n["type"] for n in nodes.values()).items())),
               "links_by_relation": dict(sorted(Counter(l["relation"] for l in links.values()).items())),
               "links_by_side": dict(sorted(Counter(l["side"] or "ledger table" for l in links.values()).items())),
               "operator_names_not_matched": dict(sorted(unmatched.items()))}
    (od / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"0 problems: {len(nodes)} nodes, {len(links)} links" + (f"; {len(unmatched)} operator names not matched yet" if unmatched else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""The graph as the pages read it: data/graph/nodes.csv and links.csv, indexed.

Shared by site/build_graph_pages.py (the organisation, country, document and chain pages), site/build_sites.py (the
site pages) and site/build_explore.py (which filters figures by organisation and document), so every page counts
the same way.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "data" / "graph"
CHAIN_RELATIONS = {"mines_for", "refines_for", "fabricates_for", "supplies_memory_to", "packages_for", "assembles_for", "ships_to",
                   "supplies_power_to", "contracts_power_from", "supplies_water_to", "supplies_fuel_to", "hosts_compute_for",
                   "leases_site_to", "receives_end_of_life_from"}
GROUP_RELATIONS = {"owns", "operates", "acts_for", "renamed_as"}


def _read(p: Path) -> list[dict]:
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Graph:
    def __init__(self):
        self.nodes = {n["node_id"]: n for n in _read(GRAPH / "nodes.csv")}
        self.links = _read(GRAPH / "links.csv")
        self.out = defaultdict(list)
        self.inn = defaultdict(list)
        for l in self.links:
            self.out[l["from_id"]].append(l)
            self.inn[l["to_id"]].append(l)

    def rel_out(self, nid, rel):
        return [l for l in self.out.get(nid, []) if l["relation"] == rel]

    def rel_in(self, nid, rel):
        return [l for l in self.inn.get(nid, []) if l["relation"] == rel]

    def chain_links(self, nid):
        return [l for l in self.out.get(nid, []) + self.inn.get(nid, []) if l["relation"] in CHAIN_RELATIONS]

    def group_links(self, nid):
        return [l for l in self.out.get(nid, []) + self.inn.get(nid, []) if l["relation"] in GROUP_RELATIONS]

    def org_group(self, oid):
        """Organisations whose sites count toward oid's: those it owns (as a document states, any depth) and those a
        document says act for it or are it under another name."""
        seen, todo = {oid}, [oid]
        while todo:
            a = todo.pop()
            for l in self.out.get(a, []):
                if l["relation"] == "owns" and l["to_id"].startswith("org:") and l["to_id"] not in seen:
                    seen.add(l["to_id"]); todo.append(l["to_id"])
            for l in self.inn.get(a, []):
                if l["relation"] in ("acts_for", "renamed_as") and l["from_id"].startswith("org:") and l["from_id"] not in seen:
                    seen.add(l["from_id"]); todo.append(l["from_id"])
        return seen

    def org_sites(self, oid):
        """[(site node id, listed_operator link, via org id)] for the organisation and its documented group."""
        out = []
        for g in sorted(self.org_group(oid)):
            for l in self.rel_in(g, "listed_operator"):
                out.append((l["from_id"], l, g))
        return out

    def org_entries(self, oid):
        """Entries that name the organisation, or companies of its documented group, and no other organisation."""
        grp = self.org_group(oid)
        out = []
        for l in self.links:
            if l["relation"] == "names" and l["to_id"] in grp:
                named = {x["to_id"] for x in self.rel_out(l["from_id"], "names")}
                if named <= grp:
                    out.append(l["from_id"])
        return sorted(set(out))

    def org_subjects(self, oid):
        """Node ids whose figures the organisation's page counts: itself, its group, their listed sites, and the
        entries that concern only it."""
        return sorted({oid} | self.org_group(oid) | {s for s, _, _ in self.org_sites(oid)} | set(self.org_entries(oid)))


@lru_cache(maxsize=1)
def graph() -> Graph:
    return Graph()

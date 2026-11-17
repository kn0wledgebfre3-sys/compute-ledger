"""Drawing the ledger's graph: the chain as columns, and one node's neighbourhood as a ring.

Both are drawn here, at build time, as SVG with every node and link carrying data attributes; docs/assets/graph.js
adds the behaviour (highlight on hover, details on click, filters, follow a company) and docs/assets/graph.css the
look. A drawing shows only links the graph holds, so each line on it has a document behind it.
"""
from __future__ import annotations

import html
import json
import math
import re
from collections import defaultdict

ARROW_AT_FROM = {"contracts_power_from"}  # arrows point the way goods, power or water go
UPSTREAM_LEGS = {"refines_for": (0, 2), "fabricates_for": (1, 2), "supplies_memory_to": (1, 2), "packages_for": (1, 2),
                 "assembles_for": (1, 2), "mines_for": (0, 0)}
COL_TITLES = ["Refiners · fab suppliers", "Fabs · memory · assembly", "Chip and system makers", "Sites · contract holders", "Power · fuel · water · tenants"]
REL_TEXT = {"refines_for": "refines metal for", "fabricates_for": "fabricates chips for", "supplies_memory_to": "supplies memory to",
            "packages_for": "packages chips for", "assembles_for": "assembles for", "supplies_power_to": "supplies power to",
            "contracts_power_from": "contracts power from", "supplies_water_to": "supplies water to", "supplies_fuel_to": "supplies fuel to",
            "leases_site_to": "leases the site to", "owns": "owns", "acts_for": "acts for", "renamed_as": "was renamed",
            "operates": "operates", "hosts_compute_for": "hosts computing for", "mines_for": "mines for", "ships_to": "ships to",
            "receives_end_of_life_from": "takes retired hardware from"}


def e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def short(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1].rstrip(" ,;(") + "…"


def column_of(link: dict, nodes: dict, end: str) -> int | None:
    """Which column a link's end sits in, from what the link is."""
    rel = link["relation"]
    if rel in UPSTREAM_LEGS:
        return UPSTREAM_LEGS[rel][0 if end == "from" else 1]
    other = link["to_id"] if end == "from" else link["from_id"]
    me = link["from_id"] if end == "from" else link["to_id"]
    if rel in ("supplies_power_to", "supplies_water_to", "supplies_fuel_to"):
        site = nodes.get(link["to_id"], {})
        upstream = site.get("kind") == "fab"
        if end == "to":
            return 1 if upstream else 3
        return 0 if upstream else 4
    if rel == "contracts_power_from":
        return 3 if end == "from" else 4
    if rel in ("leases_site_to", "hosts_compute_for"):
        return 3 if end == "from" else 4
    return None  # ownership and the rest: drawn only between nodes already placed


def chain_drawing(links: list[dict], nodes: dict, docs: dict, gid: str, gap: bool = True, width: int = 1180,
                  group_refiners: bool = True, focus: set | None = None) -> tuple[str, dict]:
    """The chain as five columns. Returns (svg, data for the page's script)."""
    focus = focus or set()
    inst: dict[tuple, dict] = {}          # (node_id, col) -> instance
    groups: dict[str, list] = defaultdict(list)  # refiner group key -> refiner node ids
    edges = []

    def key_for(nid, col):
        n = nodes[nid]
        if group_refiners and col == 0 and n["type"] == "site" and n.get("kind") == "smelter_refiner":
            g = f"grp:refiners:{n['country']}"
            if nid not in groups[g]:
                groups[g].append(nid)
            return (g, 0)
        return (nid, col)

    placed = []
    for l in links:
        cf, ct = column_of(l, nodes, "from"), column_of(l, nodes, "to")
        if cf is None or ct is None:
            continue
        a, b = key_for(l["from_id"], cf), key_for(l["to_id"], ct)
        for k in (a, b):
            inst.setdefault(k, {"key": k})
        placed.append((a, b, l))
    # ownership and other links between instances already drawn
    ids_placed = defaultdict(list)
    for k in inst:
        ids_placed[k[0]].append(k)
    for l in links:
        if column_of(l, nodes, "from") is not None:
            continue
        if l["from_id"] in ids_placed and l["to_id"] in ids_placed:
            placed.append((ids_placed[l["from_id"]][0], ids_placed[l["to_id"]][0], l))

    # aggregate parallel links between the same two instances with the same relation and side
    agg: dict[tuple, list] = defaultdict(list)
    for a, b, l in placed:
        agg[(a, b, l["relation"], l["side"])].append(l)

    cols = defaultdict(list)
    for k in inst:
        cols[k[1]].append(k)
    if not inst:
        return "", {}
    # order within columns: name first, then two passes of barycentres against the neighbouring columns
    def label(k):
        nid = k[0]
        if nid.startswith("grp:refiners:"):
            return nodes.get("country:" + nid.split(":")[2], {}).get("name", nid)
        return nodes[nid]["name"]
    for c in cols:
        cols[c].sort(key=lambda k: (label(k).lower(), k[0]))
    nb = defaultdict(list)
    for (a, b, _, _), ls in agg.items():
        nb[a].append(b); nb[b].append(a)
    for _ in range(3):
        for c in sorted(cols):
            pos = {k: i for cc in cols for i, k in enumerate(cols[cc])}
            def bary(k):
                ns = [pos[x] for x in nb[k] if x[1] != c]
                return sum(ns) / len(ns) if ns else pos[k]
            cols[c].sort(key=lambda k: (round(bary(k), 3), label(k).lower(), k[0]))

    used_cols = sorted(cols)
    if not gap:  # a strip on a page: only the columns it uses, side by side
        width = max(560, 250 * len(used_cols))
    slot = {c: (c if gap else i) for i, c in enumerate(used_cols)}
    ncol = 5 if gap else len(used_cols)
    colw = width / ncol
    boxw = min(200, colw - 34)
    rowh, boxh, top = 46, 36, 50
    height = top + max(len(cols[c]) for c in cols) * rowh + 30
    xy = {}
    for c in cols:
        n = len(cols[c])
        offset = (height - top - 30 - n * rowh) / 2
        for i, k in enumerate(cols[c]):
            x = slot[c] * colw + (colw - boxw) / 2
            y = top + offset + i * rowh
            xy[k] = (x, y)

    data = {"nodes": {}, "edges": {}}
    out = [f'<svg class="lg{" big" if gap else ""}" id="{e(gid)}" viewBox="0 0 {width} {int(height)}" width="100%" role="img" '
           f'aria-label="The chain: {len(inst)} parties and sites, {sum(len(v) for v in agg.values())} documented links">']
    out.append('<defs>' + "".join(
        f'<marker id="{gid}-a{s}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 z" class="ah ah-{s}"/></marker>' for s in ("record", "claim")) + "</defs>")
    for c in used_cols:
        out.append(f'<text class="colt" x="{slot[c] * colw + colw / 2:.0f}" y="22" text-anchor="middle">{e(COL_TITLES[c].upper())}</text>')
    out.append(f'<line class="rule" x1="0" y1="34" x2="{width}" y2="34"/>')
    if gap and 2 in cols and 3 in cols:
        gx = 3 * colw - 12
        out.append(f'<g class="gapband"><line x1="{gx:.0f}" y1="44" x2="{gx:.0f}" y2="{height - 12:.0f}"/>'
                   f'<text x="{gx - 8:.0f}" y="{height / 2:.0f}" text-anchor="middle" transform="rotate(-90 {gx - 8:.0f} {height / 2:.0f})">'
                   'no record found yet links a chip to a site</text></g>')
    # edges
    out.append('<g class="edges">')
    for i, ((a, b, rel, side), ls) in enumerate(sorted(agg.items(), key=lambda kv: (kv[0][0][1], kv[0][1][1], label(kv[0][0]), label(kv[0][1]), kv[0][2]))):
        (xa, ya), (xb, yb) = xy[a], xy[b]
        ya += boxh / 2; yb += boxh / 2
        if a[1] < b[1]:
            x1, x2 = xa + boxw, xb
        elif a[1] > b[1]:
            x1, x2 = xa, xb + boxw
        else:
            x1, x2 = xa + boxw, xb + boxw
        dx = (x2 - x1) * 0.45 if a[1] != b[1] else 40
        d = f"M{x1:.1f} {ya:.1f} C {x1 + dx:.1f} {ya:.1f}, {x2 - dx:.1f} {yb:.1f}, {x2:.1f} {yb:.1f}"
        eid = f"{gid}-e{i}"
        n = len(ls)
        w = 1.4 + min(3.2, math.log2(n)) if n > 1 else 1.4
        mk = f' marker-start="url(#{gid}-a{side})"' if rel in ARROW_AT_FROM else f' marker-end="url(#{gid}-a{side})"'
        ends = " ".join(sorted({a[0], b[0]} | {l["from_id"] for l in ls} | {l["to_id"] for l in ls}))
        up, dn = (b[0], a[0]) if rel in ARROW_AT_FROM else (a[0], b[0])  # the way metal, chips, power or water go
        out.append(f'<path class="ed s-{e(side)}" id="{eid}" d="{d}" style="stroke-width:{w:.1f}" data-ends="{e(ends)}" data-up="{e(up)}" data-dn="{e(dn)}" data-side="{e(side)}"'
                   f' tabindex="0" role="button" aria-label="{e(label(a))} {e(REL_TEXT.get(rel, rel))} {e(label(b))}, {n} link{"s" if n > 1 else ""}, {side}"{mk}/>')
        items = []
        for l in sorted(ls, key=lambda l: (nodes[l["from_id"]]["name"], nodes[l["to_id"]]["name"])):
            d_ = docs.get(l["document_id"], {})
            items.append({"f": nodes[l["from_id"]]["name"], "fp": nodes[l["from_id"]].get("page", ""), "t": nodes[l["to_id"]]["name"],
                          "tp": nodes[l["to_id"]].get("page", ""), "q": l["quoted_line"], "doc": d_.get("name", ""), "dp": d_.get("page", ""),
                          "u": d_.get("detail", ""), "b": l["basis"], "p": " to ".join(x for x in (l["period_start"], l["period_end"]) if x)})
        data["edges"][eid] = {"rel": REL_TEXT.get(rel, rel), "side": side, "a": label(a), "b": label(b), "items": items}
        if n > 1:
            mx, my = (x1 + x2) / 2, (ya + yb) / 2
            out.append(f'<text class="en" x="{mx:.0f}" y="{my - 4:.0f}" text-anchor="middle">{n}</text>')
    out.append("</g><g class=\"nodes\">")
    for k, (x, y) in sorted(xy.items(), key=lambda kv: (kv[0][1], kv[1][1])):
        nid = k[0]
        if nid.startswith("grp:refiners:"):
            members = groups[nid]
            cc = nid.split(":")[2]
            name = nodes.get("country:" + cc, {}).get("name", cc)
            sub = f"{len(members)} smelter{'s' if len(members) > 1 else ''} and refiner{'s' if len(members) > 1 else ''}"
            page = ""
            kind = "group"
            data["nodes"][nid] = {"name": f"Smelters and refiners in {name}", "type": "group",
                                  "members": [[nodes[m]["name"], nodes[m].get("page", "")] for m in sorted(members, key=lambda m: nodes[m]["name"])]}
        else:
            n = nodes[nid]
            name, page, kind = n["name"], n.get("page", ""), n["type"]
            sub = {"org": n.get("kind") or "organisation", "site": (n.get("kind") or "site").replace("_", " "), "party": "named in a document",
                   "entry": "ledger entry"}.get(kind, kind)
            if kind == "site" and n.get("place"):
                sub = n["place"]
            data["nodes"][nid] = {"name": name, "type": kind, "page": page, "sub": sub}
        cls = f"nd t-{kind}" + (" focus" if nid in focus else "")
        out.append(f'<g class="{cls}" data-id="{e(nid)}" tabindex="0" role="button" aria-label="{e(name)}, {e(sub)}">'
                   f'<rect x="{x:.1f}" y="{y:.1f}" width="{boxw:.0f}" height="{boxh}"/>'
                   f'<text class="nm" x="{x + 9:.1f}" y="{y + 15:.1f}">{e(short(name, int(boxw / 7.6)))}</text>'
                   f'<text class="sb" x="{x + 9:.1f}" y="{y + 29:.1f}">{e(short(sub, int(boxw / 6.4)))}</text></g>')
    out.append("</g></svg>")
    return "".join(out), data


def ego_drawing(center: dict, ring: list[dict], gid: str, size: int = 330) -> str:
    """One node and its neighbours on a ring. ring items: {id, name, page, type, side, count, sub}."""
    c = size / 2
    r = size / 2 - 56
    out = [f'<svg class="lg ego" id="{e(gid)}" viewBox="0 0 {size} {size}" width="100%" role="img" '
           f'aria-label="{e(center["name"])} and {len(ring)} neighbours">']
    n = max(1, len(ring))
    pts = []
    for i, it in enumerate(ring):
        a = -math.pi / 2 + 2 * math.pi * i / n
        pts.append((c + r * math.cos(a), c + r * math.sin(a), it))
    out.append('<g class="edges">')
    for x, y, it in pts:
        out.append(f'<line class="ed s-{e(it.get("side") or "ledger")}" x1="{c:.1f}" y1="{c:.1f}" x2="{x:.1f}" y2="{y:.1f}" data-ends="{e(it["id"])}"/>')
    out.append("</g>")
    out.append(f'<g class="ctr"><circle cx="{c}" cy="{c}" r="38"/>'
               + "".join(f'<text x="{c}" y="{c + 4 + 11 * j - 5.5 * (len(lines) - 1):.0f}" text-anchor="middle">{e(t)}</text>'
                         for lines in [wrap(center["name"], 13, 4)] for j, t in enumerate(lines)) + "</g>")
    for x, y, it in pts:
        shape = {"org": f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9"/>',
                 "site": f'<rect x="{x - 9:.1f}" y="{y - 9:.1f}" width="18" height="18"/>',
                 "sites": f'<rect x="{x - 13:.1f}" y="{y - 11:.1f}" width="26" height="22" class="fill"/>',
                 "country": f'<path d="M{x:.1f} {y - 11:.1f} l11 11 l-11 11 l-11 -11 z"/>',
                 "doc": f'<rect x="{x - 8:.1f}" y="{y - 10:.1f}" width="16" height="20" class="doc"/>',
                 "entry": f'<rect x="{x - 9:.1f}" y="{y - 9:.1f}" width="18" height="18" class="fill"/>',
                 "party": f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" class="party"/>'}.get(it["type"], f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8"/>')
        cnt = f'<text class="cnt" x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle">{it["count"]}</text>' if it.get("count") else ""
        ty = y + 24 if y >= c - 2 else y - 16
        lab = "".join(f'<tspan x="{x:.1f}" dy="{0 if j == 0 else 11}">{e(t)}</tspan>' for j, t in enumerate(wrap(it["name"], 18, 2)))
        if y < c - 2 and len(wrap(it["name"], 18, 2)) > 1:
            ty -= 11
        inner = f'{shape}{cnt}<text class="lb" x="{x:.1f}" y="{ty:.1f}" text-anchor="middle">{lab}</text>'
        if it.get("page"):
            out.append(f'<a class="nd t-{e(it["type"])}" data-id="{e(it["id"])}" href="{e(it["page"])}" aria-label="{e(it["name"])}">{inner}</a>')
        else:
            out.append(f'<g class="nd t-{e(it["type"])}" data-id="{e(it["id"])}">{inner}</g>')
    out.append("</svg>")
    return "".join(out)


def wrap(s: str, w: int, lines: int) -> list[str]:
    words, out, cur = (s or "").split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + (1 if cur else 0) <= w:
            cur = (cur + " " + wd).strip()
        else:
            if cur:
                out.append(cur)
            cur = wd
        if len(out) == lines:
            break
    if cur and len(out) < lines:
        out.append(cur)
    if len(out) == lines and " ".join(out) != " ".join(words):
        out[-1] = short(out[-1] + " …", w)
    return [short(x, w + 2) for x in out] or [""]


def data_script(gid: str, data: dict) -> str:
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<" + chr(92) + "/")
    return f'<script type="application/json" id="{e(gid)}-data">{js}</script>'


CSS = """
.lgwrap{position:relative;overflow-x:auto;background:var(--paper);border:1px solid var(--rule);margin:12px 0 0}
.lgwrap svg.lg{min-width:540px;display:block} .lgwrap svg.lg.big{min-width:1000px}
svg.lg text{font-family:var(--mono);fill:var(--ink-2)}
svg.lg .colt{font-size:11px;letter-spacing:.06em}
svg.lg .rule{stroke:var(--rule)}
svg.lg .nd rect,svg.lg .nd circle,svg.lg .nd path{fill:var(--paper);stroke:var(--ink);stroke-width:1.2}
svg.lg .nd.t-site rect{stroke:var(--rec);stroke-width:1.5}
svg.lg .nd.t-party rect,svg.lg .nd .party{stroke-dasharray:3 2;stroke:var(--ink-2)}
svg.lg .nd.t-group rect{fill:var(--paper-2)}
svg.lg .nd.focus rect{fill:var(--ink)} svg.lg .nd.focus .nm,svg.lg .nd.focus .sb{fill:var(--paper)}
svg.lg .nd .nm{font-family:var(--body);font-size:13.5px;font-weight:600;fill:var(--ink)}
svg.lg .nd .sb{font-size:10.5px}
svg.lg .nd{cursor:pointer;outline:none}
svg.lg .nd:focus-visible rect,svg.lg .nd:focus-visible circle{stroke:var(--accent);stroke-width:3}
svg.lg .ed{fill:none;stroke-width:1.5;cursor:pointer;outline:none}
svg.lg .ed.s-record{stroke:var(--rec)} svg.lg .ed.s-claim{stroke:var(--claim);stroke-dasharray:6 4}
svg.lg .ed.s-ledger{stroke:var(--rule);stroke-width:1.2}
svg.lg .ah-record{fill:var(--rec)} svg.lg .ah-claim{fill:var(--claim)}
svg.lg .ed:hover,svg.lg .ed:focus-visible,svg.lg .ed.on{stroke-width:3.4!important}
svg.lg .en{font-size:10.5px;fill:var(--ink-2);paint-order:stroke;stroke:var(--paper);stroke-width:3px}
svg.lg .gapband line{stroke:var(--gap);stroke-width:1.5;stroke-dasharray:2 4}
svg.lg .gapband text{font-size:11px;fill:var(--gap)}
svg.lg.dim .ed:not(.on){opacity:.12} svg.lg.dim .nd:not(.on){opacity:.3} svg.lg.dim .en{opacity:.2}
svg.lg.no-record .ed.s-record,svg.lg.no-claim .ed.s-claim{display:none}
svg.lg.no-gap .gapband{display:none}
svg.ego .ctr circle{fill:var(--ink)} svg.ego .ctr text{fill:var(--paper);font-size:9.5px}
svg.ego .lb{font-size:10px;fill:var(--ink)} svg.ego .cnt{font-size:10px;fill:var(--paper)}
svg.ego .nd .fill{fill:var(--rec);stroke:var(--rec)} svg.ego .nd .doc{fill:var(--paper-2)}
svg.ego a.nd:hover .lb,svg.ego a.nd:focus .lb{text-decoration:underline}
.lgpanel{border:1px solid var(--rule);background:var(--paper-2);padding:12px 14px;margin:10px 0 0;font-size:15px}
.lgpanel:empty{display:none}
.lgpanel h3{font-family:var(--mono);font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-2);margin:0 0 6px}
.lgpanel blockquote{margin:4px 0 6px}
.lgpanel ul{margin:6px 0 0;padding-left:18px;max-height:340px;overflow:auto}
.lgcontrols{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;margin:16px 0 0;font-family:var(--mono);font-size:13px;color:var(--ink-2)}
.lgcontrols select{font:inherit;padding:6px 8px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);width:340px;max-width:100%;min-width:0}
.lgcontrols label{display:flex;gap:6px;align-items:center;max-width:100%;min-width:0}
.lgcontrols input{accent-color:var(--accent);width:16px;height:16px;margin:0}
.lglegend{display:flex;flex-wrap:wrap;gap:4px 16px;font-family:var(--mono);font-size:12px;color:var(--ink-2);margin:8px 0 0}
.lglegend span{display:flex;align-items:center;gap:6px}
.lglegend i{display:inline-block;width:24px;border-top:2px solid var(--rec)}
.lglegend i.c{border-top:2px dashed var(--claim)} .lglegend i.g{border-top:2px dotted var(--gap)} .lglegend i.l{border-top:1.5px solid var(--rule)}
.cols2{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:36px;align-items:start}
.side{position:sticky;top:16px}
.panel{border:1px solid var(--rule);background:var(--paper);padding:14px;margin:0 0 14px}
.panel h3{font-family:var(--mono);font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-2);margin:0 0 8px}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:22px 0 0}
.tile{background:var(--paper-2);padding:12px 14px}
.tile b{display:block;font-family:var(--display);font-size:28px;line-height:1.1}
.tile span{font-family:var(--mono);font-size:12px;color:var(--ink-2)}
.gapbox{border:1.5px dashed var(--gap);padding:10px 14px;margin:10px 0 0}
.gapbox ul{margin:6px 0 0;padding-left:18px}
.none{color:var(--ink-2);font-style:italic;margin:8px 0 0}
.gsearch{position:relative;margin:16px 0 0;max-width:640px}
.gsearch input{width:100%;font:inherit;font-size:15px;padding:9px 12px;border:1px solid var(--rule);background:var(--paper);color:var(--ink)}
.gsearch ul{position:absolute;z-index:5;left:0;right:0;top:100%;list-style:none;margin:2px 0 0;padding:0;background:var(--paper);border:1px solid var(--rule);max-height:420px;overflow:auto;box-shadow:0 6px 18px rgba(0,0,0,.12)}
.gsearch ul:empty{display:none}
.gsearch li a{display:block;padding:7px 12px;text-decoration:none;color:var(--ink)}
.gsearch li a:hover,.gsearch li a:focus,.gsearch li a.sel{background:var(--paper-2)}
.gsearch li .m{display:block}
.tag{white-space:nowrap}
.cols2 td,.cols2 .m{overflow-wrap:break-word}
.tag.rec{color:var(--rec);border-color:currentColor} .tag.claim{color:var(--claim);border-color:currentColor} .tag.gap{color:var(--gap);border-color:currentColor}
@media (max-width:860px){ .cols2{grid-template-columns:minmax(0,1fr)} .side{position:static} .tiles{grid-template-columns:repeat(2,minmax(0,1fr))} }
"""

JS = r"""
(()=>{
const $$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function setup(svg){
  const dataEl=document.getElementById(svg.id+'-data');const D=dataEl?JSON.parse(dataEl.textContent):{nodes:{},edges:{}};
  const panel=document.getElementById(svg.id+'-panel');const base=svg.dataset.base||'';
  const edges=$$('.ed',svg),nodes=$$('.nd',svg);
  function light(ids){if(!ids){svg.classList.remove('dim');edges.forEach(x=>x.classList.remove('on'));nodes.forEach(x=>x.classList.remove('on'));return;}
    svg.classList.add('dim');edges.forEach(x=>{const on=x.dataset.ends.split(' ').some(i=>ids.has(i));x.classList.toggle('on',on);});
    const lit=new Set(ids);edges.forEach(x=>{if(x.classList.contains('on'))x.dataset.ends.split(' ').forEach(i=>lit.add(i));});
    nodes.forEach(x=>x.classList.toggle('on',lit.has(x.dataset.id)));}
  function showNode(id){if(!panel)return;const n=D.nodes[id];if(!n)return;
    let h='<h3>'+esc(n.type==='group'?'Group':n.type==='org'?'Organisation':n.type==='site'?'Site':n.type==='party'?'Named in a document':n.type)+'</h3><p><b>'+esc(n.name)+'</b>'+(n.sub?' <span class="m">'+esc(n.sub)+'</span>':'')+'</p>';
    if(n.page)h+='<p><a href="'+esc(base+n.page)+'">Open its page →</a></p>';
    if(n.members)h+='<ul>'+n.members.map(m=>'<li>'+(m[1]?'<a href="'+esc(base+m[1])+'">'+esc(m[0])+'</a>':esc(m[0]))+'</li>').join('')+'</ul>';
    const mine=edges.filter(x=>x.dataset.ends.split(' ').includes(id));h+='<p class="m">'+mine.length+' line'+(mine.length===1?'':'s')+' on this drawing. Select a line to see the document behind it.</p>';
    panel.innerHTML=h;}
  function showEdge(eid){if(!panel)return;const d=D.edges[eid];if(!d)return;
    let h='<h3>'+(d.side==='record'?'Record':'Claim')+' · '+d.items.length+' link'+(d.items.length===1?'':'s')+'</h3><p><b>'+esc(d.a)+'</b> '+esc(d.rel)+' <b>'+esc(d.b)+'</b></p><ul>';
    h+=d.items.slice(0,200).map(it=>'<li>'+(d.items.length>1?'<b>'+esc(it.f)+'</b> → '+esc(it.t)+': ':'')+(it.q?'<blockquote>“'+esc(it.q)+'”</blockquote>':'')
      +'<span class="m">'+(it.dp?'<a href="'+esc(base+it.dp)+'">'+esc(it.doc)+'</a>':esc(it.doc))+(it.u?' · <a href="'+esc(it.u)+'" rel="noopener">source</a>':'')+(it.b?' · '+esc(it.b.replace(/_/g,' ')):'')+(it.p?' · '+esc(it.p):'')+'</span></li>').join('')+'</ul>';
    if(d.items.length>200)h+='<p class="m">and '+(d.items.length-200)+' more in the table below.</p>';panel.innerHTML=h;}
  nodes.forEach(n=>{const id=n.dataset.id;
    n.addEventListener('mouseenter',()=>light(new Set([id])));n.addEventListener('mouseleave',()=>{if(!svg.dataset.follow)light(null);else follow(svg.dataset.follow);});
    n.addEventListener('focus',()=>light(new Set([id])));
    if(n.tagName.toLowerCase()!=='a'){n.addEventListener('click',()=>{showNode(id);light(new Set([id]));});
      n.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();showNode(id);}});}});
  edges.forEach(x=>{x.addEventListener('click',()=>showEdge(x.id));x.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();showEdge(x.id);}});});
  function follow(id){if(!id){delete svg.dataset.follow;light(null);return;}svg.dataset.follow=id;
    // what reaches it (upstream) and what it reaches (downstream), along the way goods, power or water go
    const fw={},bw={};edges.forEach(x=>{const u=x.dataset.up,d=x.dataset.dn;if(!u||!d)return;(fw[u]=fw[u]||[]).push(x);(bw[d]=bw[d]||[]).push(x);});
    const on=new Set(),lit=new Set([id]);
    for(const [adj,next] of [[fw,'dn'],[bw,'up']]){const seen=new Set([id]);const q=[id];
      while(q.length){const a=q.shift();for(const x of (adj[a]||[])){on.add(x);const b=x.dataset[next];lit.add(b);if(!seen.has(b)){seen.add(b);q.push(b);}}}}
    svg.classList.add('dim');edges.forEach(x=>x.classList.toggle('on',on.has(x)));nodes.forEach(x=>x.classList.toggle('on',lit.has(x.dataset.id)));}
  const fsel=document.getElementById(svg.id+'-follow');if(fsel)fsel.addEventListener('change',()=>{follow(fsel.value);if(fsel.value)showNode(fsel.value);else if(panel)panel.innerHTML='';});
  $$('input[data-hide]').filter(i=>i.dataset.for===svg.id).forEach(i=>i.addEventListener('change',()=>svg.classList.toggle('no-'+i.dataset.hide,!i.checked)));
}
$$('svg.lg[id]').forEach(setup);
// one search box for sites, organisations, countries, documents and entries
$$('.gsearch').forEach(box=>{const inp=box.querySelector('input'),ul=box.querySelector('ul'),base=box.dataset.base||'';let IDX=null,sel=-1;
  const T={site:'Site',org:'Organisation',country:'Country',doc:'Document',entry:'Entry'};
  async function load(){if(IDX)return IDX;try{const r=await fetch(base+'data/search.json');IDX=(await r.json()).items;}catch(e){IDX=[];}return IDX;}
  async function run(){const t=inp.value.trim().toLowerCase();if(t.length<2){ul.innerHTML='';return;}const ws=t.split(/\s+/);const idx=await load();
    const hits=[];for(const it of idx){const s=it[4];if(ws.every(w=>s.includes(w))){hits.push(it);if(hits.length>=40)break;}}
    hits.sort((a,b)=>(a[1].toLowerCase().startsWith(t)?0:1)-(b[1].toLowerCase().startsWith(t)?0:1));
    sel=-1;ul.innerHTML=hits.slice(0,14).map(it=>'<li><a href="'+esc(base+it[2])+'">'+esc(it[1])+'<span class="m">'+esc(T[it[0]]||it[0])+(it[3]?' · '+esc(it[3]):'')+'</span></a></li>').join('')
      +(hits.length?'':'<li><span class="m" style="padding:7px 12px;display:block">Nothing found</span></li>');}
  inp.addEventListener('input',run);inp.addEventListener('focus',load);
  inp.addEventListener('keydown',ev=>{const as=[...ul.querySelectorAll('a')];if(!as.length)return;
    if(ev.key==='ArrowDown'){ev.preventDefault();sel=Math.min(as.length-1,sel+1);}else if(ev.key==='ArrowUp'){ev.preventDefault();sel=Math.max(0,sel-1);}
    else if(ev.key==='Enter'&&sel>=0){ev.preventDefault();location.href=as[sel].href;return;}else if(ev.key==='Escape'){ul.innerHTML='';return;}else return;
    as.forEach((a,i)=>a.classList.toggle('sel',i===sel));});
  document.addEventListener('click',ev=>{if(!box.contains(ev.target))ul.innerHTML='';});});
})();
"""

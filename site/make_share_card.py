#!/usr/bin/env python3
"""The picture a link to the ledger shows when it is shared: docs/assets/share.png (1200 x 630).

It holds no figures, so it does not go stale when the data changes; rebuild it only when the wording or the look changes.
Needs Playwright with Chromium (pip install playwright; playwright install chromium) and Pillow. Not part of rebuild.sh or CI.

    python3 site/make_share_card.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "share.png"

CARD = """<!doctype html><html><head><meta charset="utf-8"><style>
:root{--paper:#F4F6F3;--paper-2:#E9EDE8;--ink:#17211E;--ink-2:#4B5955;--rule:#C9D1CC;--rec:#1C6B5F;--claim:#B2481F}
*{box-sizing:border-box;margin:0}
html,body{width:1200px;height:630px}
body{background:var(--paper);color:var(--ink);font-family:"Gelasio","Crimson Text",Georgia,serif;position:relative;overflow:hidden}
.rules{position:absolute;left:0;right:0;bottom:0;height:46px;background:repeating-linear-gradient(to bottom,transparent 0 37px,var(--rule) 37px 38px);opacity:.7}
.margin{position:absolute;top:0;bottom:0;left:72px;width:2px;background:var(--claim);opacity:.35}
.wrap{position:absolute;left:112px;right:84px;top:64px;bottom:46px;display:flex;flex-direction:column}
.eyebrow{font-family:"DejaVu Sans Mono",monospace;font-size:22px;letter-spacing:.12em;color:var(--ink-2);text-transform:uppercase}
h1{font-family:"Archivo Black","Archivo",sans-serif;font-weight:900;font-size:104px;line-height:1;letter-spacing:-.02em;margin-top:22px;white-space:nowrap}
.sub{font-size:35px;line-height:1.28;color:var(--ink-2);margin-top:20px;max-width:960px}
.sides{display:flex;gap:28px;margin-top:auto}
.side{flex:1;background:var(--paper);border:2px solid var(--rule);border-left-width:10px;padding:14px 20px}
.side b{display:block;font-family:"Archivo Black",sans-serif;font-size:30px;letter-spacing:.01em}
.side span{display:block;font-size:23px;line-height:1.3;color:var(--ink-2);margin-top:4px}
.rec{border-left-color:var(--rec)} .rec b{color:var(--rec)}
.claim{border-left-color:var(--claim)} .claim b{color:var(--claim)}
.foot{display:flex;justify-content:space-between;font-family:"DejaVu Sans Mono",monospace;font-size:19px;color:var(--ink-2);margin-top:18px}
</style></head><body><div class="rules"></div><div class="margin"></div><div class="wrap">
<div class="eyebrow">A public ledger · built from public records</div>
<h1>Compute Ledger</h1>
<p class="sub">The physical, social and economic footprint of AI compute, as the documents record it.</p>
<div class="sides"><div class="side rec"><b>Records</b><span>regulators, courts, grid operators, statistics offices, registries</span></div>
<div class="side claim"><b>Claims</b><span>what companies and governments say, kept apart</span></div></div>
<div class="foot"><span>kn0wledgebfre3-sys.github.io/compute-ledger</span><span>Open data · CC BY 4.0</span></div>
</div></body></html>"""


def main():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=2)  # drawn at twice the size, then reduced: no hairlines
        pg.set_content(CARD)
        pg.wait_for_timeout(300)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        big = pg.screenshot(clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        b.close()
    import io
    from PIL import Image
    Image.open(io.BytesIO(big)).convert("RGB").resize((1200, 630), Image.LANCZOS).save(OUT, optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

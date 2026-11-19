#!/usr/bin/env python3
"""Render social-card PNGs (1200x675) from the SVG post thumbnails.

Facebook, LinkedIn, X and Slack ignore SVG for og:image, so every post that
uses an SVG hero needs a PNG twin at static/images/og/<slug>.png. build.py
picks it up automatically (and warns when one is missing). Run this after
adding or changing a thumbnail, then commit the PNGs:

    python3 -m venv --without-pip v && curl -sSL https://bootstrap.pypa.io/get-pip.py | v/bin/python
    v/bin/python -m pip install resvg-py pillow
    v/bin/python scripts/make_og_images.py

Not a build dependency: Cloudflare only ever reads the committed PNGs.
"""
import re
import sys
from pathlib import Path

import resvg_py

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "images" / "og"
OUT.mkdir(parents=True, exist_ok=True)

wanted = set()
for md in sorted((ROOT / "content" / "blog").glob("*.md")):
    m = re.search(r"^image:\s*(\S+)", md.read_text(encoding="utf-8"), re.M)
    if m and m.group(1).endswith(".svg"):
        wanted.add(Path(m.group(1)).stem)

for stem in sorted(wanted):
    svg = ROOT / "static" / "images" / "thumbnails" / f"{stem}.svg"
    if not svg.exists():
        print("MISSING SVG", svg, file=sys.stderr)
        continue
    png = bytes(resvg_py.svg_to_bytes(svg_path=str(svg), width=1200))
    (OUT / f"{stem}.png").write_bytes(png)
    print("wrote", f"static/images/og/{stem}.png", len(png) // 1024, "KB")

# Square site card for pages without a hero (home, blog list, about, docs).
try:
    from PIL import Image
    Image.open(ROOT / "static" / "images" / "avatar.png").convert("RGB").save(OUT / "site.png", optimize=True)
    print("wrote static/images/og/site.png")
except ImportError:
    print("pillow not installed; skipped site.png", file=sys.stderr)

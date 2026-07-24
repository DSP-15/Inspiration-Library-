#!/usr/bin/env python3
"""
Build the Inspiration Library page from library/library.json.

    python3 build.py

Reads the entries, resizes and embeds each image as a data URI, validates every
vocabulary term against the controlled lists below, and writes
preview/inspiration-library.html.

Images live in library/images/ and are referenced by filename. Nothing is
fetched over the network, so the output is a single self-contained file.
"""

import base64
import hashlib
import io
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required.  pip install Pillow")

ROOT = Path(__file__).parent
LIBRARY = ROOT / "library" / "library.json"
IMAGES = ROOT / "library" / "images"
TEMPLATE = ROOT / "preview" / "_library-template.html"
OUTPUT = ROOT / "preview" / "inspiration-library.html"

# Controlled vocabulary. Must stay in sync with TYPES / AXES in the template.
TYPES = [
    "Portfolio", "Studio / Agency", "E-commerce", "Product / SaaS",
    "Editorial", "Landing Page", "App Interface", "Brand / Campaign",
]
AXES = {
    "layout": [
        "asymmetric grid", "editorial columns", "full-bleed imagery", "bento grid",
        "masonry", "centred composition", "split screen", "dense index",
        "product grid", "generous whitespace",
    ],
    "typography": [
        "oversized display", "serif display", "grotesk display", "monospace accents",
        "tight tracking", "type as image", "small caps labels",
    ],
    "colour": [
        "monochrome", "single saturated accent", "warm neutral ground",
        "cool neutral ground", "dark ground", "high contrast", "duotone", "muted palette",
    ],
    "imagery": [
        "editorial photography", "product photography", "3D render",
        "illustration", "archival grain", "motion or video", "no imagery",
    ],
}
ALL_TERMS = {t for terms in AXES.values() for t in terms}

# Total embedded payload past which browsers and the artifact host start to
# struggle. Images are downscaled further rather than failing the build.
BUDGET_BYTES = 4_500_000
WIDTHS = [1500, 1280, 1100, 900, 760]
QUALITY = {1500: 86, 1280: 84, 1100: 82, 900: 80, 760: 78}


def encode(path: Path, width: int) -> str:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    if w > width:
        img = img.resize((width, round(h * width / w)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=QUALITY[width], optimize=True, subsampling=0)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def main() -> int:
    if not LIBRARY.exists():
        sys.exit(f"Missing {LIBRARY}")
    if not TEMPLATE.exists():
        sys.exit(f"Missing {TEMPLATE}")

    data = json.loads(LIBRARY.read_text())
    entries = data.get("entries", [])
    if not entries:
        sys.exit("library.json has no entries")

    problems, seen_ids = [], set()
    for i, e in enumerate(entries):
        where = f"entry {i} ({e.get('title', 'untitled')})"
        for field in ("id", "title", "image", "type", "vocab"):
            if not e.get(field):
                problems.append(f"{where}: missing '{field}'")
        if e.get("id") in seen_ids:
            problems.append(f"{where}: duplicate id '{e['id']}'")
        seen_ids.add(e.get("id"))
        if e.get("type") and e["type"] not in TYPES:
            problems.append(f"{where}: unknown type '{e['type']}'")
        for term in e.get("vocab", []):
            if term not in ALL_TERMS:
                problems.append(f"{where}: unknown vocabulary term '{term}'")
        if e.get("image") and not (IMAGES / e["image"]).exists():
            problems.append(f"{where}: image not found, library/images/{e['image']}")
    if problems:
        print("Build failed:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1

    # Encode at the largest width that fits the budget.
    for width in WIDTHS:
        cards, total = [], 0
        for order, e in enumerate(entries):
            uri = encode(IMAGES / e["image"], width)
            total += len(uri)
            cards.append({
                "id": e["id"],
                "added": order + 1,
                "title": e["title"],
                "image": uri,
                "sourceUrl": e.get("sourceUrl", ""),
                "type": e["type"],
                "vocab": e["vocab"],
                "brief": e.get("brief", ""),
            })
        if total <= BUDGET_BYTES or width == WIDTHS[-1]:
            break
        print(f"  {len(entries)} images at {width}px = {total//1024}KB, over budget, retrying smaller")

    payload = json.dumps(cards, ensure_ascii=False)
    build_id = hashlib.sha256(payload.encode()).hexdigest()[:12]

    html = TEMPLATE.read_text()
    for token in ("__LIBRARY_DATA__", "__BUILD_ID__"):
        if token not in html:
            sys.exit(f"Template is missing the {token} placeholder")
    html = html.replace("__LIBRARY_DATA__", payload).replace("__BUILD_ID__", build_id)

    OUTPUT.write_text(html)
    print(f"Built {OUTPUT.relative_to(ROOT)}")
    print(f"  {len(cards)} references, images at {width}px, {len(html)//1024}KB total")
    print(f"  build {build_id}")
    if total > BUDGET_BYTES:
        print("  WARNING: over the size budget even at the smallest width.")
        print("  Consider splitting the library or trimming older entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

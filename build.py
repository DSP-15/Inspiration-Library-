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
FONTS = ROOT / "assets" / "fonts"
OUTPUT = ROOT / "preview" / "inspiration-library.html"

# Controlled vocabulary. Must stay in sync with TYPES / AXES in the template.
TYPES = [
    "Portfolio", "Studio / Agency", "E-commerce", "Product / SaaS",
    "Editorial", "Landing Page", "App Interface", "Brand / Campaign",
]
AXES = {
    "layout": [
        "full-bleed imagery", "split screen", "centred composition",
        "asymmetric grid", "card grid", "generous whitespace",
    ],
    "typography": [
        "oversized display", "grotesk display", "serif display",
        "geometric sans", "monospace accents",
    ],
    "colour": [
        "dark ground", "cool neutral ground", "warm neutral ground",
        "high contrast", "muted palette", "single saturated accent",
        "gradient ground", "multi-colour palette", "monochrome",
    ],
    "imagery": [
        "editorial photography", "product photography", "3D render",
        "archival grain", "generative graphics", "line icons",
    ],
}
ALL_TERMS = {t for terms in AXES.values() for t in terms}

# Total embedded payload past which browsers and the artifact host start to
# struggle. Images are downscaled further rather than failing the build.
BUDGET_BYTES = 4_500_000
WIDTHS = [1500, 1280, 1100, 900, 760]
QUALITY = {1500: 86, 1280: 84, 1100: 82, 900: 80, 760: 78}


CARD_RATIO = 3 / 2


def edge_colour(img: Image.Image) -> tuple:
    """Median colour of the image border, used to pad without a visible seam."""
    w, h = img.size
    px = img.load()
    step = max(1, min(w, h) // 60)
    samples = []
    for x in range(0, w, step):
        samples.append(px[x, 0])
        samples.append(px[x, h - 1])
    for y in range(0, h, step):
        samples.append(px[0, y])
        samples.append(px[w - 1, y])
    return tuple(sorted(c[i] for c in samples)[len(samples) // 2] for i in range(3))


def encode(path: Path, width: int) -> str:
    img = Image.open(path).convert("RGB")

    # Screenshots arrive at whatever ratio the browser window was. Cropping them
    # to the card would cut off headlines and edge content, which is the part
    # worth referencing, so pad to the card ratio in the screenshot's own edge
    # colour instead. The grid stays uniform and no composition is lost.
    w, h = img.size
    ratio = w / h
    if abs(ratio - CARD_RATIO) > 0.01:
        if ratio > CARD_RATIO:
            canvas_w, canvas_h = w, round(w / CARD_RATIO)
        else:
            canvas_w, canvas_h = round(h * CARD_RATIO), h
        canvas = Image.new("RGB", (canvas_w, canvas_h), edge_colour(img))
        canvas.paste(img, ((canvas_w - w) // 2, (canvas_h - h) // 2))
        img = canvas

    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
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

    # Fonts are embedded rather than linked: the artifact host blocks font CDNs,
    # and a silent fallback is what made earlier builds render badly.
    font_bytes = 0
    for token, filename in (
        ("__FONT_LB_REGULAR__", "lb-regular.woff2"),
        ("__FONT_WS_REGULAR__", "ws-regular.woff2"),
        ("__FONT_WS_BOLD__", "ws-bold.woff2"),
    ):
        path = FONTS / filename
        if not path.exists():
            sys.exit(f"Missing font {path}")
        raw = path.read_bytes()
        font_bytes += len(raw)
        html = html.replace(token, base64.b64encode(raw).decode("ascii"))

    OUTPUT.write_text(html)
    print(f"Built {OUTPUT.relative_to(ROOT)}")
    print(f"  {len(cards)} references, images at {width}px, {len(html)//1024}KB total")
    print(f"  fonts embedded, {font_bytes//1024}KB")
    print(f"  build {build_id}")
    if total > BUDGET_BYTES:
        print("  WARNING: over the size budget even at the smallest width.")
        print("  Consider splitting the library or trimming older entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

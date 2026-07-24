# Inspiration Library — Style Preview

Pick one of five visual directions for the design library, then that style becomes the real site.

## Viewing

Open `index.html` in any browser. No build step, no server needed — it is a single
self-contained file with the seed images embedded as data URIs.

## The five styles

| Style | Character |
|---|---|
| **Print-Tech Paper** | Warm archival paper, black grotesk, mono tag labels, rust accent |
| **Contact Sheet** | Darkroom black, metadata over the image on a scrim, signal red |
| **Gallery Plaque** | Putty ground, serif display, sepia imagery, museum wall-label captions |
| **Swatch Deck** | Paper ground, cards on rotating flat colour mats, heavy ink borders |
| **Terminal Ledger** | Near-black, monospace throughout, bracket-notation tags, amber accent |

## What works right now

- Filter by design type and design vocabulary; chips carry live counts and are multi-select
- Click any card for the focused view: full screenshot, tags, source link, editable brief
- **Copy prompt** copies the brief text; **Copy image** puts the actual bitmap on the clipboard
- **+ Add screenshot** takes an image, title, URL, type, and vocabulary tags, and the new
  tags register in the filter bar automatically
- Everything persists to `localStorage`; **Reset seed data** restores the three starting cards

## Files

- `index.html` — the built, self-contained preview
- `_template.html` — source template with `__*_B64__` placeholders instead of image data
- `seed/` — the three seed screenshots as ordinary jpgs

## Rebuilding after editing the template

Edit `_template.html`, then substitute the base64 payloads back in:

```python
import base64, pathlib
html = pathlib.Path("_template.html").read_text()
for token, name in {
    "__CRAFTING_CULTURE_B64__": "crafting-culture.jpg",
    "__OUTFIT_B64__": "outfit.jpg",
    "__OUR_PROJECTS_B64__": "our-projects.jpg",
}.items():
    html = html.replace(token, base64.b64encode(pathlib.Path("seed", name).read_bytes()).decode())
pathlib.Path("index.html").write_text(html)
```

## Adding more seed screenshots

Upload them to this repo through the GitHub web UI. That path is confirmed working and is
how the three current seeds arrived.

---

# Gallery Plaque — Three Iterations

`gallery-iterations.html` narrows the five styles down to the chosen Gallery Plaque
direction and offers three refinements of it. Source template: `_gallery-template.html`.

| Iteration | Display face | Palette | Structure |
|---|---|---|---|
| **A · Wall Label** | Didot / Bodoni class, high contrast | Cool gallery putty, olive accent | Three-up, light sepia, letterspaced Gill Sans captions |
| **B · Archive Press** | Palatino / Iowan Old Style, humanist | Warm manila, ink-blue accent | Two-up so plates run large, monospace captions |
| **C · Modern Plaque** | Optima / Gill Sans, humanist sans | Cool stone, clay accent | Three-up tighter, near-neutral imagery in a hairline frame |

## Font caveat

The Artifact content policy blocks external font CDNs, and this build environment has no
network access to download and embed font files. All three iterations therefore use system
font stacks. Didot, Palatino, Optima, and Gill Sans all ship with macOS and will render as
intended there; on Windows or Linux each stack falls back to its next entry, so the
iterations will look closer to one another than they do on a Mac.

Once a direction is chosen, the intended faces can be self-hosted as `@font-face` data URIs
so they render identically everywhere.

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

---

# Modern Plaque — Three Iterations (round 2)

`modern-iterations.html`. Built from Iteration C, with the requested changes applied to
all three: card titles in the Archive Press serif, boxed rounded filter buttons, larger
type throughout, no colour grading on the images, and a different hover treatment each.

| Iteration | Hover | Palette | Controls |
|---|---|---|---|
| **D · Lift** | Frame rises 6px on a tinted shadow, hairline darkens | Cool stone, clay accent | Pill |
| **E · Rule** | Underline draws beneath the title, frame hairline turns accent, nothing moves | Pale cool grey, ink blue accent | 8px rounded |
| **F · Plate** | Caption bar slides up over the image, surfacing the source link | Warm stone, near-black accent so screenshots carry the only colour | Pill |

Seed images were re-encoded at 1500px wide, quality 86, no chroma subsampling
(previously 1000px / 78 / 4:2:0), which is what the earlier softness came from.
Sepia and saturation filters were removed entirely.

---

# Inspiration Library (Rule) — the chosen direction

`inspiration-library.html`, built from `_library-template.html`.

## Tagging

Free-text tags were the reason the filter bar fragmented into one-off terms like
"filterable tag navigation". Replaced with a **controlled vocabulary**: one design type
from a fixed list, plus terms drawn from four axes (Layout, Typography, Colour, Imagery).
Because everyone picks from the same list, tags accumulate counts and the filters find
real patterns.

The **Colour axis is read off the image**. On upload the page samples the screenshot on a
64x64 canvas and measures average lightness, saturation, lightness spread, and hue
distribution, then pre-selects colour terms. Measured, not guessed, and deliberately
conservative: a term that fires on everything stops discriminating. Current behaviour on
the seeds:

- Crafting Culture -> cool neutral ground, high contrast
- Outfit -> single saturated accent
- Our Projects -> muted palette

The **brief writes itself** from the type and selected vocabulary, and stays editable.

## Filter fine-tuning

Below 6 references every tag shows, because the bar would otherwise be empty. Past 6,
only tags carried by two or more references stay in the bar; one-off tags remain on their
card and move behind a "Show N one-off tags" toggle.

## What is not AI

A published Artifact is a static page. Its only runtime capabilities are `downloads` and
`mcp`; there is no model-inference capability, so the page cannot send a screenshot to
Claude for tagging. The controlled vocabulary plus pixel-read colour is what is achievable
client-side. True vision tagging needs a server, see below.

## Path to real AI tagging

A small backend endpoint that accepts the image and returns structured JSON constrained to
the same vocabulary in this file:

    POST /api/tag  ->  { type, vocab[], brief }

Anthropic's API with a JSON schema over the `TYPES` and `AXES` constants keeps the model on
the controlled vocabulary rather than inventing terms. The front end changes only in the add
flow: call the endpoint, pre-select what comes back, leave every term editable.

In the meantime the same result is available by pushing screenshots to this repository and
asking for them to be tagged directly.

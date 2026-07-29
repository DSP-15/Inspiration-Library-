# Inspiration Library

A filterable design reference library. The repository is the source of truth; the
published page is a build artifact.

## Adding references

1. Upload screenshots to `library/images/` on GitHub (Add file, then Upload files).
2. Ask Claude in this repo's session to add them.
3. Claude looks at each screenshot, writes the design type, vocabulary, and brief,
   updates `library/library.json`, rebuilds, and pushes.

You never have to name the design vocabulary yourself. That is the point of routing
it through the conversation: the tagging happens where something can actually see
the image.

Include the source URL if you have it, and it becomes a "Visit site" link on the card.

## Building

```
pip install Pillow
python3 build.py
```

Reads `library/library.json`, embeds each image from `library/images/` as a data URI,
and writes `preview/inspiration-library.html` as one self-contained file. No network
access is needed to build or to view.

The build **fails** on any vocabulary term or design type outside the controlled lists
in `build.py`. That guard is deliberate: free-text tags are what caused the filter bar
to fragment into one-off entries that grouped nothing.

## Layout

```
library/
  library.json     entries: title, type, vocab, brief, sourceUrl, image filename
  images/          source screenshots at full resolution
build.py           validates, encodes, and writes the page
preview/
  _library-template.html   the app, with __LIBRARY_DATA__ and __BUILD_ID__ placeholders
  inspiration-library.html generated, do not hand-edit
```

Earlier design explorations are kept in `preview/` and described in `preview/README.md`.

## Controlled vocabulary

One design type per entry, plus terms from four axes. `build.py` holds the canonical
lists and the template mirrors them.

| Axis | Terms |
|---|---|
| Layout | full-bleed imagery, split screen, centred composition, asymmetric grid, card grid, generous whitespace |
| Typography | oversized display, grotesk display, serif display, geometric sans, monospace accents |
| Colour | dark ground, cool neutral ground, warm neutral ground, high contrast, muted palette, single saturated accent, gradient ground, multi-colour palette, monochrome |
| Imagery | editorial photography, product photography, 3D render, archival grain, generative graphics, line icons |

The lists are curated to what the library actually contains. Terms nothing used were
removed rather than left sitting in the picker; terms the references needed were added.
Keeping them earned rather than aspirational is what stops the filter bar filling with
options that match nothing.

Terms are worth adding as the library grows, but add them to both lists and prefer
extending an axis over inventing one-off descriptions.

## Filters

Below 5 references every tag shows, because otherwise the bar mirrors the cards and
tells you nothing. Past that, only tags carried by two or more references stay in the
bar; one-off tags stay on their card and collapse behind a toggle.

## Builds and local edits

Each build carries an id. The page keeps your library in `localStorage` so inline brief
edits and quick additions survive a reload, but when a newer build is published it
replaces the cached copy. Export first if you have local additions worth keeping.

`Restore from repo` resets to the shipped build at any time.

## Fonts

Titles are set in **Libre Baskerville**, the interface in **Work Sans**. Both are SIL
Open Font License 1.1; the licences ship in `assets/fonts/`.

They are **embedded in the page** as subset woff2 data URIs, not linked. The artifact host
blocks font CDNs, and the previous build relied on Palatino and Optima being installed
locally, so anywhere but macOS silently fell back and rendered badly. Embedding costs 40KB
for all three faces and renders identically on every machine.

Subsetting is to Latin plus the punctuation the interface uses. If you add copy needing
other characters, regenerate with `fontTools.subset` and widen the character set.

## Screenshot ratios

Screenshots arrive at whatever ratio the browser window happened to be. Rather than crop
them to the card and cut off headlines, `build.py` pads each one to 3:2 in its own
median edge colour, so the grid stays uniform and no composition is lost.

## Copying from a card

Open any card. `Copy prompt` copies the brief. `Copy image` puts the screenshot itself on
the clipboard as a PNG, ready to paste into a prompt or a document.

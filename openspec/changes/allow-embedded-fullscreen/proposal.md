## Why

The pilot wants every simulation on machinome.org viewable full screen, like
a video player (24 September 2026). The viewer gains a full-screen button and
the `f` key (machinome-viewer change `go-fullscreen`), shown only where the
browser permits full screen. An `<iframe>` permits it only when it carries
`allowfullscreen`. The `.. machinome::` directive emits its iframe without
that attribute, so every model embedded in the Machinome manual — the ten
tutorial and example pages machinome.org hosts — would hide the button and
ignore `f`.

## What Changes

- The directive's HTML iframe carries `allowfullscreen`, so an embedded model
  may go full screen when the reader asks.
- Nothing else: no directive option, no change to the export or the document.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sphinx-embedding`: the iframe permits full screen.

## Impact

`machinome/sphinx.py` (`visit_machinome_iframe`) and `tests/test_sphinx_ext.py`.
The Machinome manual is rebuilt for the site afterwards; no viewer or project
source changes here.

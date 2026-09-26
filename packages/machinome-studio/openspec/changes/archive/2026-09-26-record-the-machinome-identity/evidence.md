# Evidence: record-the-machinome-identity

This change records behaviour already on `main`; its evidence is the
cycle that put it there and the pilot's live assessments.

## The merged commits (studio `main`, 26 September 2026)

- `b90747a` Apply the Machinome visual identity to the studio: lockup,
  favicon links, fonts, tokens, identity release intact, NOTICE, tests.
- `47657e3` Keep the design's amber accent under the identity, after the
  pilot assessed the orange accent live: "I don't like the contrast with
  the new orange, it's harsh. The old colors were smooth. The logo
  application is nice."
- `e43ec03` Give the studio a white favicon on a black plate, after the
  pilot asked for a white favicon to tell the studio apart from
  machinome.org; a white symbol on a transparent canvas was shown on mock
  light and dark tab strips to vanish on light chrome.

## Tests that hold the behaviour

- `tests/test_product_identity.py`: favicon links, the intact release
  against its manifest, the fonts with their notices, the faces and the
  lockup in the source, the favicon's verbatim symbol path on its plate.
- `tests/test_shop_lifecycle_e2e.py::test_the_hub_wears_the_machinome_identity`:
  the wordmark painted at 180px inside a link named `Machinome Studio`
  with a `Studio` qualifier, both faces actually loaded (via
  `document.fonts.load`, which also caught a cyclic `--mono` token during
  the cycle), the favicon links and the served favicon.
- On the rebased branch before the fast-forward: 469 unit tests OK (one
  pre-existing skip), 23 browser e2e tests OK.

## This change

Records only. `openspec validate --strict` valid; the product-identity and
documentation test modules green after the design-reference edit.

# Evidence

- Red: `tests/test_sphinx_ext.py::DirectiveTest::test_emits_iframe_and_copies_export`
  failed with `AssertionError: 'allowfullscreen' not found` (the iframe was
  `<iframe src="_machinome/spinner_export/index.html" style="..." loading="lazy"></iframe>`).
- Green: `tests/test_sphinx_ext.py` 13 passed; with the docs structure, docs
  exports and viewer-documentation-link tests, 32 passed, 98 subtests.
- The manual's reference page and the sharing tutorial's iframe example now
  say the embed allows full screen.

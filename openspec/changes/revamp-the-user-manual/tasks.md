## 1. Red-first evidence

- [ ] 1.1 Replace the docs tests that pin the old chapters and the three
  sibling examples with tests for the new structure: navigation sections,
  one live model per example page, three example exports built by both
  builders, tutorial embeds committed, no publication caveat outside the
  status page. Confirm they fail against the unchanged manual.
- [ ] 1.2 Add `tests/test_tutorial_counter.py`, which imports, assembles and
  builds every tutorial chapter and runs the companion tests through
  `machinome test`. Confirm it fails while the tutorial project is absent.

## 2. The tutorial machine

- [ ] 2.1 Create `docs/tutorial/` (manifest, `counter/` package, digit artwork
  generator and artwork) with one self-contained module per chapter and
  companion tests for the fit, scenario, running and clocked chapters.
- [ ] 2.2 Export the chapters that embed a model into `docs/_exports/` and
  commit them; remove the retired tutorial exports.

## 3. The pages

- [ ] 3.1 Write the entry pages: why, install, first machine, index.
- [ ] 3.2 Write the ten tutorial chapters against the chapter modules.
- [ ] 3.3 Write the how-to guides from the existing leaf, fusion, markings,
  flexible, declaring, animation, CLI and testing material.
- [ ] 3.4 Write the concept pages from the existing declaring, driving,
  scenarios, node-tree, testing and embedding material.
- [ ] 3.5 Write the examples index and three example pages; remove the V8 and
  Clock 01 pages and submodules; add the Pascaline and Curta submodules;
  update `.readthedocs.yaml` and the Actions docs job.
- [ ] 3.6 Write the reference and project pages: CLI, API, Sphinx directive,
  sibling manuals, status, changelog, release notes, upgrading, contributing;
  define the version substitutions in `conf.py`; update `README.rst` and
  `context7.json`.

## 4. Validation

- [ ] 4.1 Strict Sphinx build (`-E -W --keep-going`) with all three examples
  exported from their pinned revisions; docs and tutorial tests green; a
  browser check of the landing, tutorial and example pages with screenshots.
- [ ] 4.2 Record the evidence in `validation.md`, sync the spec delta,
  archive the change and commit the completed state.

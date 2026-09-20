## Why

The user manual grew out of the solid-node documentation, whose thesis was
modelling parts in several backends and animating them against a looping
timeline. Machinome 0.7, released on 2026-09-20, is a framework for machines
with declared inputs, joints, relations, stops and memory, and the manual
still teaches the old perspective: drivers arrive in chapter seven of nine,
five unrelated demonstration models compete for one tutorial, two thousand
lines of contract-grade prose sit under tutorial titles, the navigation mixes
stubs and internal change records with guides, and release-preparation caveats
are repeated on eight pages. The pilot asked for a coherent narrative on the
release day, keeping only what is good.

## What Changes

- Reorganise the manual by reader intent: a why page, a start section,
  one tutorial, how-to guides, concept pages ("how it works"), examples,
  reference and project pages. Every page has one stated purpose.
- Replace the disc-pointer-pin clock tutorial, the box-with-hole backend tour,
  the knob and the plotter with ONE framework-owned tutorial machine, a
  hand-cranked tally counter, built chapter by chapter from a part to a driven,
  related, tested, running, remembering and shared machine. Its chapter
  modules are real source under `docs/tutorial/` that the framework suite
  builds and tests, and its embeds are committed exports.
- Move the contract-grade content of the driving, scenarios, declaring,
  testing and leaf-node pages into concept and how-to pages, rewritten for
  lookup rather than for learning, and drop what was an internal record
  (the expression-graphs page, the flexible-parts stub, the 0.7 development
  record's place in the manual, the duplicated viewer JavaScript API).
- Feature three example machines, one per execution model: Metamaquina 2
  (posed), the Pascaline module (running) and the Curta Type I (clocked).
  The V8 engine and Clock 01 pages and submodules leave the manual.
  **BREAKING** for the documentation builders: the export steps change.
- State the release facts once: version and publication facts become Sphinx
  substitutions and live on the status page; tutorial and guide pages carry
  no publication caveat. The manual describes 0.7.0 as released.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: the narrative is driver-first; one tutorial machine
  carries the learning path and is built by the suite; the manual is organised
  by reader intent with publication facts stated once; worked examples cover
  the three execution models; the declarative, kernel and viewer/embedding
  requirements name the new pages and defer the browser API to the viewer
  manual.

## Impact

`docs/` (all user pages, `conf.py`, `index.rst`, `_exports/`, new
`tutorial/` project), `.gitmodules` and `docs/examples/` (two submodules
removed, two added), `.readthedocs.yaml` and the `docs` job of
`.github/workflows/python-app.yml`, `tests/test_docs_exports.py` and a new
`tests/test_tutorial_counter.py`, `README.rst`'s learning-path paragraph and
`context7.json`. No framework runtime, API or dependency changes. No ADR: the
architecture is untouched. Publication of the two new example repositories on
the machinome organisation is a prerequisite for a fresh public documentation
build and is the pilot's action.

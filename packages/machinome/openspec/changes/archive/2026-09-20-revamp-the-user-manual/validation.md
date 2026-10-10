# Validation record

Standalone documentation cycle on the release day of Machinome 0.7.0.
Base: framework primary `main` at `9fb5127fad62e6c66067b34e7d02dd389471fa2d`.
Worktree: `machinome/WTs/docs-revamp`, branch `docs-revamp`, slot 11.
Planning commit: `19e71d9`. Integration target: framework `main`, which
needs the pilot's separate authority. Ratification: the pilot approved the
navigation tree and the tutorial machine on 2026-09-20 ("Start building")
and stated that 0.7 releases that day.

## Red first

Against the unchanged manual, the replaced and new tests failed as intended:
`tests/test_docs_exports.py` (the one-per-execution-model examples, the
committed tutorial embeds), `tests/test_docs_structure.py` (navigation
sections, chapter pages and modules, retired internal records, release
substitutions, no publication caveat outside the status page: 56 failures
across the old pages) and `tests/test_tutorial_counter.py` (no tutorial
project). All pass after the change.

## The tutorial machine

`docs/tutorial/` is a Machinome project: eleven named models (the first
machine, chapters one to nine, and chapter four's ratio variant), companion
tests for chapters six to nine, a seven-segment digit artwork generator and
its SVG. Measured in the workspace environment:

- `machinome build --all`: eleven models built, 53 s cold.
- `machinome test --all`: 11 tests, 0 failed, 5 s warm.
- The scenario chapter's crash tick (70, crank at 252 degrees) was measured
  independently before it was written into the test.
- Chapter six's red runs were captured from real `--set` overrides:
  `post_offset=22` fails interference with 69.27 mm³ shared, and
  `clearance=1.0` fails the capture contract; the guard promoted in chapter
  six then refuses `post_offset=22` before building.
- Running: ten `Turn once` requests leave the units drum at 360 and the
  tens drum at 36; `Back a bit` is blocked at zero; thirty forward then a
  hundred back admits exactly minus thirty.
- Clocked: twelve strokes in one request commit twelve events (units 2,
  tens 1); 99 plus one carries to 00 in one event; `trigger` returns a
  request with its commit at fraction 1.0; a reverse stroke admits zero
  naming `handle.turn`.
- Six committed exports under `docs/_exports/counter-*` at document versions
  2, 2, 4, 4, 5 and 8; the browser renderer shows the digit markings in the
  expected decreasing order, unmirrored.

## The manual

48 pages, 6,923 lines of reStructuredText (the previous manual: 30 pages,
about 14,000 lines including the 1,851-line development record and the
duplicated viewer API). Sections: Start (2), Tutorial (10), How-to (11),
How it works (9), Examples (4), Reference (5), Project (4), plus the why
page and the release note.

Retired from the manual: the disc-pointer-pin clock tutorial and its twenty
committed exports, the knob and plotter, the box-with-hole backend tour, the
expression-graphs record, the flexible-parts stub, the V8 and Clock 01
example pages and submodules, the duplicated viewer JavaScript API, and the
publication caveats on eight pages. The 0.7 development record and the
docs-0.7 validation record moved to `workflow/archive/docs-0-7-2026-09-19/`.

Release facts are Sphinx substitutions in `conf.py` (`release_date`,
`viewer_version`, `viewer_api`, `document_versions`, `mechanics_version`)
and the status page is the one page that discusses publication state.

## Examples

Three submodules, one per execution model, pinned at the workspace clones:

| Example | Model | Pinned revision | Export |
| --- | --- | --- | --- |
| Metamaquina 2 | posed | `c916f9b5f09ba27faaab9225fff0cdf6342fc00c` | 5 min 1 s cold, 36 MB, needs OpenSCAD |
| Pascaline module | running | `576dc6b` | 2 min 20 s cold, 5.0 MB, version 5 |
| Curta Type I (clocked_curta) | clocked | `0db199f` (branch `direct-operation`) | 2 min 0 s cold at `c13c308`, 28 s warm at `0db199f`, 29 MB, version 8 |

Both documentation builders (`.readthedocs.yaml`, the Actions `docs` job)
export exactly these three, and `tests/test_docs_exports.py` holds them to
the directives. The submodules point at the **Machinome Foundry**
organisation (`github.com/machinome-foundry`), where the pilot keeps the
simulations of open-source machines; the manual names the organisation on
the index, why, examples, status, contributing and sibling-manuals pages
and invites the reader to browse it, and `tests/test_docs_structure.py`
holds every submodule and example page to that organisation. The example
pages state the licences the Foundry's licensing policy
(`machinome-studio/docs/foundry-licensing-policy.md`, 2026-09-20) selects:
Foundry simulation software under AGPL-3.0-or-later, the Metamaquina 2
design GPL-3.0-or-later per its headers, the Pascaline's meshes under the
unversioned CC BY the listing records, and the Curta's original and adapted
CAD and design-derived corrections, and every export containing them,
under CC-BY-NC-SA-4.0. The Pascaline repository commits no source geometry; its own
`scripts/download_sources.py` (pinned Printables files, no login, standard
library only, 7 s) and `scripts/prepare_sources.py` run before its export
in both builders, as they did here. The times above are measured from the
worktree's submodule clones with the workspace environment. The design
record's mention of markings on the Pascaline was a slip: the Curta's number
rolls carry the markings, the Pascaline's do not, and the pages say so. At validation the Foundry's `Metamaquina2` main was at the pinned
revision; its `Curta-Type-I-3x` main (`60979ad`) and `direct-operation`
(`fe02911`) did not yet hold `0db199f`; and no `Pascaline-module`
repository existed in the organisation. Publishing those two pinned
revisions is the pilot's action and a prerequisite for a fresh public
build.

## Build and browser

`python -m sphinx -E -b html -W --keep-going docs docs/_build/html` builds
48 pages with no warnings in 7 s, all three example exports and the six
tutorial exports embedded, the widget-less exports completed by the
installed viewer.

`pytest tests/test_docs_exports.py tests/test_docs_structure.py
tests/test_sphinx_ext.py tests/test_tutorial_counter.py
tests/test_machinome_identity.py tests/test_export.py`: 60 passed, 97
subtests, 76 s, the tutorial's eleven models built and its eleven companion
tests run inside that. The one warning is a framework fixture's intentional
legacy-render path. `README.rst` parses with docutils at warning-as-error
severity; `openspec validate --specs --strict` passes 34 items; `git diff
--check` is clean.

Headless Chromium over the built HTML, served locally: the landing page,
the why, install, examples and status pages, tutorial chapters two, four,
eight and nine, the execution-models concept page, the fast-tests guide,
the API reference and the three example pages, with no page or console
error. Each tutorial embed and each example page mounts exactly one viewer.
The counter's chapter-eight embed exposes `Back a bit`, `Turn once`, the
running nudge inputs and the run/step transport; chapter nine exposes the
`tens` and `units` readouts, the `Turn once` button and `Reset`.
Metamaquina 2 exposes `CenterX`, `HomeZ`, `PresentBed`, `Rest` and the
three axis sliders; the Pascaline `Add hundred`, `Add one`, `Add ten`,
`Back one`, its three entry inputs and the transport; the Curta its
twenty-three request inputs, the result and turns readouts, `Turn crank`
and `Reset`. The digit markings are visible on the counter's drums and the
Curta's rolls. Screenshots stay in the session's scratch directory.

## Rebase onto main 9016f00

The branch was rebased on 2026-09-21 onto framework main `9016f00`, eight
commits past the recorded base `9fb5127`. Main had edited four pages this
change deletes (`animation`, `driving`, `scenarios`, `api-reference`); the
deletions were taken and the edits folded into the pages that replace them:

- ADR-133 retained time-driven motion: `concepts/running`, `publishing`,
  `howto/timeline`, `reference/api`, `changelog` (folded before the rebase).
- ADR-134 ancestor joint constraints: `concepts/joints` gains the section
  `Constraints from an ancestor` under the label the API reference already
  pointed at; `concepts/running` and `concepts/clocked` say how the added
  range stops and clips; the changelog bullet came with the merge.
- ADR-135 contact attribution and ADR-136 relative crossings: the running
  stops section states first-contact attribution, its two remaining limits,
  moving-threshold landings and certified following contact; one changelog
  bullet, `Moving-contact stops`.

The viewer repository had moved to API 23, reading document versions 1 to
10 and executing time drives, so `conf.py` now substitutes those numbers,
and the changelog, release page, publishing page, chapter ten and
`context7.json` no longer describe version-10 viewer support as
outstanding. One stale sentence in `docs/architecture.md` saying the
viewer refuses version 10 was corrected. Framework version strings
(`pyproject.toml`, `machinome/__init__.py`, `conf.py`) already read 0.7.0.

After the rebase: strict Sphinx build clean, 16 documentation tests with
98 subtests pass, the tutorial suite builds and tests all nine chapter
models on the rebased framework in 71 s, `git diff --check` clean.

## Foundry pins after licence adequation

On 2026-09-21 the Foundry repositories carried licence-adequated heads
whose histories do not contain the revisions pinned above. The pins moved
to the pushed heads: Pascaline-module `dc8bc5e` (the pilot's `ae7efbe`
plus one commit making the README and two script docstrings state
AGPL-3.0-or-later with the full copyright name, as pyproject, NOTICE and
CREDITS already did), Metamaquina2 `4cc1da7` (model package renamed
`simulation`, mechanics-based belts, licence split recorded in NOTICE and
CREDITS). Both re-exported from the new heads with the builders' steps:
the Pascaline publishes version 5 with instructions Add hundred, Add one,
Add ten and Back one, drivers hundreds_entry, tens_entry and units_entry
and six dial controls; Metamaquina 2 publishes version 4 with drivers x,
y, z, instructions CenterX, HomeZ, PresentBed and Rest, 99 pieces. The
example pages' licence sections now follow each repository's NOTICE:
Metamaquina 2's helpers AGPL-3.0-or-later and its design-integrating
modules GPL-3.0-only beside the design's own GPL grants; the Pascaline's
generated rings and cam keep the source's attribution terms. Strict
build clean, docs tests 16 passed with 98 subtests, staged whitespace
clean. Curta stays pinned at `0db199f`, an ancestor of the local
project's head but absent from the Foundry remote, whose licence
adequation has not started.

## Not claimed

No framework runtime, API or dependency changed; no ADR is needed. The
example pages describe the pinned revisions' surfaces from their published
documents; this record does not certify the examples' complete mechanical
test suites. Nothing was pushed, tagged, published or integrated.

## Mechanics companion pass (2026-09-22)

The mechanics manual was brought to the released state in its own
repository (OpenSpec change `release-mechanics-with-0-7`). This manual
said "twelve" helpers on the API, install, manuals and upgrading pages
and told readers to follow source installation "while publication is
pending"; corrected to the twenty-four helpers in nine families and the
index install. Strict `-E -W --keep-going` build clean.

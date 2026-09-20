## Context

Standalone maintainer documentation work on the release day of Machinome
0.7.0 (2026-09-20). Base is framework primary `main` at
`9fb5127fad62e6c66067b34e7d02dd389471fa2d`, clean. The shop opened
`machinome/WTs/docs-revamp` on branch `docs-revamp` with `scripts/dev-env`
(slot 11). Integration target is framework `main` under separate pilot
authority. The pilot ratified the navigation tree and the tutorial machine on
2026-09-20 ("Start building") and stated that 0.7 is released today.

The existing manual is accurate. Its faults are structural: the spine is the
pre-0.6 timeline animation; the driving and scenarios pages are specs in
tutorial clothing; navigation kinds are mixed; publication caveats are spread
over eight pages; the examples show the timeline surface, not the machine
surface. The ratified `user-documentation` spec and `tests/test_docs_exports.py`
pin the old chapter names and the three sibling examples, so this is a
spec-changing cycle, not an adjustment.

## Goals / Non-Goals

**Goals:**

- A manual whose learning path teaches the machine surface in the order the
  framework thinks: a part, an input moving a body through a joint, shared
  dimensions, relations and laws, buttons, fit tests, stepped scenarios, a
  running machine with stops, a machine with memory, sharing.
- One tutorial machine that the suite builds and tests so the lessons cannot
  rot; every embed a committed export.
- Contract-grade content preserved, moved to concept and how-to pages, and
  rewritten for lookup.
- Examples that show the three execution models on real machines.
- Publication facts stated once and easy to change.

**Non-Goals:**

- Changing framework behaviour, the CLI, the scaffold `machinome new` writes,
  or any dependency.
- Documenting the viewer's browser API or the mechanics helpers beyond links:
  those manuals exist and own that content.
- Publishing repositories, pushing, tagging or integrating.

## Decisions

- **Organise by reader intent** (start, tutorial, how-to, how it works,
  examples, reference, project), following the tutorial / how-to /
  explanation / reference split. Alternative: keep one linear book. Rejected
  because the same page cannot serve a learner and a reader looking up a
  refusal, which is exactly what the driving page tries to do today.

- **One tutorial machine, a hand-cranked tally counter**, framework-owned
  under Apache-2.0, exact parts only (CadQuery) so the tutorial needs no
  OpenSCAD. It has a base with a reading post, a crank, and two digit drums
  driven by a windowed law: the units drum advances one digit during the last
  sixty degrees of a crank turn and the tens drum during the last thirty-six
  degrees of the units drum's turn. It exercises a driver, a revolute joint,
  a relation, a ratio and a law of the author's own, parameters, absolute
  instructions, fit contracts, a stepped scenario, a ratchet stop under
  `Time.running()` with controls on the part, and `State` with committing
  relations. The spike proved every stage builds, poses, runs (ten turns
  advance the tens drum one digit; a reverse move is blocked at the last
  tooth) and counts (twelve strokes commit twelve events; 99 plus one carries
  to 00). Alternatives: keep the clock (no input, no memory), the plotter
  (drivers and instructions only). Rejected as unable to carry the story.

- **Each chapter is a self-contained module** under `docs/tutorial/counter/`
  (`c01_part.py` ... `c09_clocked.py`) with companion tests where the chapter
  writes tests, a `pyproject.toml` declaring every chapter as a named model,
  and a generator for the digit artwork. Pages include code with
  `literalinclude`, so prose cannot drift from source. A suite test imports,
  assembles and builds every chapter and runs the companion tests through
  `machinome test`. Alternative: one evolving module and inline snippets.
  Rejected because snippets rot and intermediate stages could not be built.

- **Contract content moves, it is not deleted.** Joint frames and
  composition, relation solving and refusals, running mechanics (integration,
  jumps, self-reads, blocks, `Play`, stops), clocked mechanics (events,
  commits, bounds, the clock), the kernels and the quantum, the assertion
  catalogue, the leaf recipes, the caching rules: each gets a concept or
  how-to page written for lookup, with the "why the framework refuses this"
  explanations kept.

- **Examples are one per execution model**: Metamaquina 2 (posed; drivers,
  instructions, flexible parts, an OpenSCAD design read in place), the
  Pascaline module (running; ratchet stops, controls on the parts, markings)
  and the Curta Type I clocked model (clocked; states, commits, interlocks,
  digits). Each page embeds exactly one live model built at documentation
  build time from a pinned submodule, as today. The V8 and Clock 01 pages and
  submodules are removed. Measured locally: the Pascaline export takes about
  two minutes; the Curta's is measured in the validation record. The two new
  submodules point at `https://github.com/machinome/Pascaline-module.git` and
  `https://github.com/machinome/Curta-Type-I-3x.git`, which the pilot must
  publish at the pinned revisions before a fresh public build works; local
  validation uses the workspace clones.

- **Publication facts are substitutions.** `conf.py` defines the framework
  version, release date, viewer version, API and document versions, and the
  mechanics version; pages use `|release|`-style substitutions. The status
  page is the one page that discusses publication state. Tutorial, how-to
  and concept pages carry no version-gate prose.

- **The embedding page keeps what the framework owns** (what an export
  contains, document versions, the Sphinx directive) and links to the viewer
  manual for the browser API.

- **Docs tests follow the structure**: the export-coverage tests stay; the
  tests pinning the old chapters and the three siblings are replaced by tests
  for one live model per example page, the three example exports, the
  tutorial's committed exports, the navigation sections and the absence of
  publication caveats outside the status page.

## Risks / Trade-offs

- [Read the Docs build time grows with the Curta] → measure the export
  locally and record it; keep the existing per-example build steps so a slow
  example is one step to remove.
- [New example repositories are not yet public] → record the prerequisite in
  the validation record and the status page; the pinned gitlinks identify the
  validated revisions exactly.
- [A ten-chapter tutorial is long] → each chapter ends with a working
  machine the reader can drive; a reader may stop after chapter five with a
  complete posed machine.
- [Rewriting contract prose can drop a fact] → every existing page is
  reviewed against the new one before deletion; the suite's API-name check
  (`machinome.simulation` exports) stays.

## Migration Plan

Nothing deploys. On integration the hosted manual rebuilds from the new
builders; until the two example repositories are public that build fails on
the export steps, as the validation record states.

## Open Questions

None for this cycle. Whether `machinome new` should scaffold an exact leaf so
the first-run path needs no OpenSCAD is a separate, behavioural question for
the pilot.

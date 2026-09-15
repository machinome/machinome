## Why

solid-node's ADR-121 gave a law the one thing every law it admitted
before was forbidden: the coordinate the law DRIVES may now appear among
its sources, and what the law reads there is the value that coordinate
RETAINS. The mechanism behind it is the Curta's clearing rack — a ring
carrying nine-tooth racks sweeps past the register dials, and a rack
turns a dial only while its teeth reach it AND the dial is not already
standing in its missing-tooth gap. The gap is what lets the ring go on
sweeping past a finished dial while it still clears the dials beyond it,
so the law that moves the dial has to read where the dial stands.

A program carrying such a law is published as a **version 6** document.
No key was added for it: the self-read is a law edge whose `needs`
intersects its own `gives`. The version moved because a version 5
consumer evaluates a law edge as `f(end) − f(start)`, which with the
read at BOTH ends freezes the branch the gate selects and moves the part
by a different mechanism in silence — measured on the producer's side at
`evidence.md` §2 of the framework's own change, where a 500° rack sweep
from a dial standing at 108° left it at 608° and a second sweep at 1108°,
with no crossing located at all.

This viewer renders versions 1–5 and refuses a version 6 document by
name, which is correct (ADR-034) and is now the only thing between the
Curta and a browser:

```text
…/viewer.json declares document version 6, which this viewer does not
render; it renders versions 1, 2, 3, 4, 5. The document is written to a
schema this build cannot read: refusing it rather than rendering part of
a machine it does not understand.
```

The framework's own requirement note item 8 — "replay that document
through the independent viewer's running engine" — is discharged HERE,
in this repository, by this cycle. ADR-110/111 is the standing shape: one
published program, one conformance corpus, two runtimes that are one
algorithm.

**The corpus gap, measured on this base.** The committed copy at
`solid_node_viewer/widget/src/running-corpus.json` is stale by TWO
framework regenerations, and this cycle closes both:

1. `publish-only-what-runs` (framework, 2026-09-14), whose viewer refresh
   never happened. It changes the two `Train` scenarios' DOCUMENT only:
   `program.intermediates` loses `wheel.turn` and `program.sources`
   loses its `"wheel.turn": []` entry. The program `identity` is
   unchanged, and **both `Train` scenarios replay green on this base
   against the new file** — so this half of the gap is a stale document
   and not a drifted engine.
2. `read-the-driven-coordinate` (framework, 2026-09-15), which adds three
   scenarios over two machines: `Clearing` at `dt = 0.05` (24 ticks) and
   at `dt = 0.1` (12 ticks), and `StoppedClearing` at `dt = 0.05`
   (16 ticks).

The framework's file copied byte for byte over the committed one, on this
base, fails exactly four tests and no others:

```text
× the running corpus > is the framework's own fixture, unedited
  → expected [ …(17) ] to have a length of 14 but got 17
× replays Clearing at dt=0.05 (scenario 14)
  → Clearing at dt=0.05, tick 8, bank wheel.turn: expected 359.5 within
    1e-9 relative, got 408
× replays Clearing at dt=0.1 (scenario 15)
  → Clearing at dt=0.1, tick 2, bank wheel.turn: expected 359.5 within
    1e-9 relative, got 488
× replays StoppedClearing at dt=0.05 (scenario 16)
  → StoppedClearing at dt=0.05, tick 3, bank ring: expected
    341.1428571428571 within 1e-9 relative, got 336.73469387755097
```

Thirteen of the fourteen existing scenarios and the width guard pass
untouched. `408` against `359.5` is the gate frozen open: the dial ran
through its gap because the engine read the self-read at both ends,
exactly as the framework measured on its own side before ADR-121.

## What Changes

- **The loader recognises a self-read edge.** A law edge whose `needs`
  intersects its `gives` reads the coordinate it drives. `loadProgram`
  derives, per driven end, the two-layer reading of that end's jump
  plan — which of its jump nodes DEPEND on the driven coordinate (its
  qualified id among the free names of the node's published level
  quantity, CLOSED OVER the document's bindings table, transitively
  through the placeholders of dependent inner nodes), the independent
  subset as a plan of its own, and the skeleton's affinity READ off the
  edge's published `affine` flag rather than recomputed. Nothing further
  is published for it and the viewer requires nothing further.
- **The step executes such an edge PIECE BY PIECE.** ADR-107's partition
  is built first over the independent nodes alone, unchanged, its
  branches read at its midpoints; inside each of its pieces the
  dependent nodes are WALKED, their branches read at the piece's LEFT
  END with the driven coordinate at its retained value and every other
  source at that fraction; the piece is cut at the FIRST surface any
  dependent level reaches strictly inside it; and after a cut the driven
  coordinate is placed at the nearest representable value on the FAR
  SIDE of the surface, bracketed by doubling from one ulp and bisected in
  ordinal float space. A law with no self-read takes ADR-107's path with
  nothing rebuilt at all — one array test before it.
- **The run COMMITS the landing.** A self-read edge reports, beside its
  increment, the absolute value a driven end whose walk took at least one
  cut holds at the tick's end; the step applies it where it already
  writes an absolute value for a stop, BEFORE the stops are located, so a
  stop on the same coordinate in the same segment wins.
- **Two new refusals, both of the tick and neither of the document.** A
  node flipped twice at a piece's left end is a sliding mode and refuses
  the tick as an unsupported law; a cut that places the coordinate
  nowhere within 200 doublings of a ulp raises a broken-invariant refusal
  of its own, rather than committing the one value the design says is
  never committed.
- **A self-read crossing is not a stop**: it stops no input, retires no
  command, and is recorded as a crossing.
- **`documentVersions` becomes `[1, 2, 3, 4, 5, 6]`** and the declared
  widget API version rises **14 → 15**: executing a version 6 document is
  a capability a host may require before it mounts a bundle that would
  refuse the Curta by name. `bundle.py`'s `RELEASED_DOCUMENT_VERSIONS`
  does not move — it is what a viewer that predates the declaration is
  entitled to be assumed to read, and 0.1.0 read `[1, 2, 3, 4]`.
- **The committed conformance corpus is replaced by the framework's
  regenerated one** — 17 scenarios over 14 machines, 328 ticks — and
  replayed green; the widget's width guard gains the producer's three new
  required features, so a narrower corpus copied in is loud here without
  anyone running the generator.
- **The Curta's clearing interface runs in a real page.** The framework's
  own `tests/clearing_project/machine.py:CurtaInterface` — six dials, two
  rows, one ring, and a `clamp01` station window that makes every
  self-read crossing a SEARCHED one — is exported and committed as
  `tests/fixtures/clearing/`, mounted in Chromium, swept, and read back
  at six band edges; a second sweep moves nothing.
- **Not** a change to the document's shape, to the framework, or to the
  contract between the two packages: the self-read is `needs ∩ gives`,
  and nothing of the viewer's code moves into solid-node.

## Capabilities

### New Capabilities

None. This cycle widens capabilities the viewer already has.

### Modified Capabilities

- `viewer-package`: **ADDED** — "The worker executes a law that reads the
  coordinate it drives": the recognition, the derived reading, the
  two-layer walk, the far-side landing, the committed value and the two
  tick refusals. **MODIFIED** — "One loader reads either published
  document" (the rendered version list becomes 1–6, and what a version 6
  document carries); "The viewer declares its API version" (15); "The
  step reproduces the producer's own integration" (a law's contribution
  is no longer always ADR-107's partition, and a step may commit an
  absolute value for a coordinate no bound stopped); "A program the
  viewer cannot execute is refused by name" (the three self-read shapes
  refused at load); "The two runtimes agree on a conformance corpus" (the
  three features the producer's generator now requires).

## Impact

- `solid_node_viewer/widget/src/run/program.ts` — the self-read
  recognition, the derived two-layer reading per driven end, and the
  three load-time refusals; `RefusalKind` gains `landing`.
- `solid_node_viewer/widget/src/run/jumps.ts` — `_Retained` and `_Walk`
  mirrored: the dependence split, the left-end branch decision with its
  flip and chattering refusal, the first-cut solve and search, the
  far-side landing, and the float-ordinal helpers JavaScript has no
  `Math.nextafter` or `Math.ulp` for.
- `solid_node_viewer/widget/src/run/edges.ts` — `edgeIncrements` reports
  landings and `edgeCuts` routes through the reading.
- `solid_node_viewer/widget/src/run/run.ts` — the landings map per
  segment, applied where a stop's bound is applied and before the stops
  are located; the new refusal caught with the other four.
- `solid_node_viewer/widget/src/viewer.ts` — `RENDERED_VERSIONS`, and the
  program gate that today reads `document.version === 5`.
- `solid_node_viewer/widget/package.json` —
  `solidNodeViewerApi`, `solidNodeDocumentVersions`;
  `src/version.test.ts`.
- `solid_node_viewer/capture.py` — `carries_program`, which today tests
  `version == 5`.
- `solid_node_viewer/widget/src/running-corpus.json` — replaced by the
  producer's regenerated copy; `src/run/running-corpus.test.ts` — the
  census and the width guard; `src/run/cost.test.ts` — what a self-read
  tick costs.
- `tests/fixtures/clearing/` (new), `tests/support.py`, and a new
  Playwright acceptance beside `tests/test_lock_document.py`.
- `CHANGELOG.md` under `0.2.0 — unreleased`, `README.md`'s version table;
  `docs/adrs/EXPORT/ADR-057`, extracted after implementation, and
  `docs/adrs/README.md`.
- Nothing in the framework, nothing in another checkout, and nothing of
  the document's shape.

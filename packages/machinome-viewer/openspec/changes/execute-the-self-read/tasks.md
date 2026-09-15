## 0. Before anything else

- [ ] 0.1 Confirm the base: this worktree is `execute-the-self-read` off
      viewer main `28dfc79`, package `0.2.0` unreleased, declared API
      version `14`, `solidNodeDocumentVersions == [1, 2, 3, 4, 5]`, the
      highest ADR `056` in `docs/adrs/EXPORT`. Never `npm install` or
      `npm ci` here: `solid_node_viewer/widget/node_modules` is a symlink
      to the primary checkout's.
- [ ] 0.2 Record the baseline in
      `openspec/changes/execute-the-self-read/evidence.md`, measured on
      this base and pasted verbatim. These are the numbers measured while
      proposing; re-measure and paste rather than copying them:
      - `npm run typecheck` — clean, exit 0;
      - `npm test` — **36 test files, 806 tests, 0 failed**, ~20 s;
      - `npm run build` — writes `dist/solid-widget.js`, 685.7 kb
        (702 107 bytes on disk);
      - `PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest -q`
        — **114 passed, 0 skipped**, ~107 s. Name every skip if any
        appears; this environment has Playwright, Chromium and Pillow, so
        there were none.
      - the four cost measurements `src/run/cost.test.ts` prints on this
        base: `Train, no constraint` 73 188 ticks/s; `Captured, blocking
        ticks` 60 339 ticks/s; `the lock, idle` 8 488 ticks/s; `the lock,
        advancing the key` 132 ticks/s; `the Pascaline at dt = 1/240`
        32 942 ticks/s.
- [ ] 0.3 Record the CORPUS GAP on the base, before changing anything.
      Copy framework main `8e15791`'s `tests/running-corpus.json` over
      `solid_node_viewer/widget/src/running-corpus.json`, run
      `npx vitest run src/run/running-corpus.test.ts`, paste the result,
      and restore the committed file. It must be exactly this and nothing
      else:
      - `is the framework's own fixture, unedited` — 17 machines, not 14;
      - `replays Clearing at dt=0.05 (scenario 14)` — tick 8, bank
        `wheel.turn`: expected `359.5`, got `408`;
      - `replays Clearing at dt=0.1 (scenario 15)` — tick 2, bank
        `wheel.turn`: expected `359.5`, got `488`;
      - `replays StoppedClearing at dt=0.05 (scenario 16)` — tick 3, bank
        `ring`: expected `341.1428571428571`, got `336.73469387755097`;
      - and the other thirteen scenarios plus both width-guard cases
        GREEN — including both `Train` scenarios, whose documents differ
        from the committed copy (`program.intermediates` loses
        `wheel.turn`, `program.sources` loses `"wheel.turn": []`, the
        `identity` unchanged). A failure anywhere else means the copy was
        not byte-identical, and is a stop condition to report.
- [ ] 0.4 Read, and keep open, the framework's own record at
      `/home/asa/devel/libresolid-studio/solid-node` (READ ONLY — never
      write, stage or commit there):
      `docs/adrs/NODE/ADR-121-a-law-may-read-the-coordinate-it-drives.md`;
      `openspec/changes/archive/2026-09-15-read-the-driven-coordinate/design.md`
      §3, §4, §6 and the whole of its dated "Implementation notes";
      `openspec/specs/simulation/spec.md` "A law may read the coordinate
      it drives"; `openspec/specs/export/spec.md` "A running root's
      document publishes the compiled program" and "The two runtimes
      share a conformance corpus"; and the implementation this cycle
      mirrors — `solid_node/simulation/program.py` (`_dependence`,
      `_on_surface`, `_ordinal`, `_from_ordinal`, `_chattering`,
      `_unlanded`, `LandingInvariantError`, `_Retained`, `_Walk`,
      `Edge.retained`, `Edge._retained_ends`, `Edge.increments`,
      `Edge.cuts`) and `solid_node/simulation/run.py` (`_landed`,
      `_pass`, `integrate`). Where this cycle and ADR-121 disagree,
      ADR-121 is right; where the TypeScript and `program.py` disagree,
      `program.py` is right.
- [ ] 0.5 Confirm the refusal this cycle removes is real, and paste it:
      load one of the framework corpus's version 6 documents (the
      `Clearing` machine's) through `assertRenderable` on this base and
      capture the message naming version 6 and the versions this viewer
      renders.

## 1. The corpus, red first

- [ ] 1.1 Replace `solid_node_viewer/widget/src/running-corpus.json` with
      framework main `8e15791`'s `tests/running-corpus.json`, **byte for
      byte** — 17 scenarios over 14 machines (`Captured`, `CarryLead`,
      `Clearing`, `Clutch`, `Ratchet`, `Remainder`, `StopAndJump`,
      `StoppedClearing`, `Swept`, `Throwing`, `Train`, `TwoStops`,
      `Window`, `Wrapped`), 328 ticks, tolerance `{"float": 1e-9}`.
      Verify with a digest of both files and paste it. Nothing here edits
      it and nothing here regenerates it.
- [ ] 1.2 Update the census in `src/run/running-corpus.test.ts`: 17
      machines entries, 14 distinct names, 328 ticks.
- [ ] 1.3 Red: `npm test -- running-corpus` fails on `Clearing` (both
      step sizes) and `StoppedClearing` and on nothing else. Paste it
      verbatim; it is 0.3's list minus the census assertion.
- [ ] 1.4 Widen the width guard's `REQUIRED` to the producer's list
      (design D7), computed the way
      `tools/generate_running_corpus.py`'s `uncovered_features` computes
      it, over the committed fixture only:
      - `'a law that reads the coordinate it drives'` — a law edge with
        `needs ∩ gives` non-empty;
      - `'a self-read coordinate holding at its gate while its input
        moves on'` — such an id whose bank value is unchanged from the
        previous tick (or from `program.coordinates[...].initial` on tick
        one) while at least one id of `program.sources[<that id>]` that
        is itself in the bank changed;
      - `'a tick carrying both a self-read crossing and a stop'` — a tick
        with a non-empty `stops` list one of whose `crossings` names a
        self-read coordinate.
      Extend the "narrowed corpus is refused" case to name one of the
      three.

## 2. Reading the self-read (`src/run/program.ts`, design D1)

- [ ] 2.1 Red, in `src/run/program.test.ts`: a hand-written version 6
      document whose law edge names its one driven end among its `needs`
      loads today with `retained` absent, and its band gate — whose level
      reaches the driven id ONLY through a bindings entry — is not
      recognised as dependent. Both must hold once 2.2 lands.
- [ ] 2.2 Add `retained: (RetainedReading | null)[]` to `ProgramEdge`,
      derived in `loadProgram` and parallel to `gives`; `[]` — not an
      array of nulls — where no driven end reads itself, so the one test
      downstream is `edge.retained.length > 0`. Each entry carries
      `own`, `dependent`, `outer` (`{ skeleton, jumps: <independent> }`)
      and `affine`, where `affine` is **read from `edge.affine[index]`**
      and never recomputed: for a plan-bearing law the producer's
      per-end flag IS `_affine_in_sources(plan.skeleton)`
      (`Edge._affine_ends`). Assert that equality in a test against the
      corpus's `Clearing` document rather than asserting it in a comment.
- [ ] 2.3 Dependence: a jump depends on the driven id when that id is
      among `namesOf(jump.level)` — the EXISTING bindings closure
      `loadProgram` already owns — or when that set holds the placeholder
      of a jump already found dependent, propagated in the plan's own
      (postorder) jump order. Tests: `Clearing`'s `_j2`/`_j3` are
      dependent and `_j0`/`_j1` are not, reached only through `_b3`; a
      plan with no dependent node at all yields `outer === the whole
      plan` and an empty `dependent`; a nested dependent node makes its
      enclosing node dependent.
- [ ] 2.4 The three load-time refusals (design D1), each red first, each
      naming the edge, the coordinate and the document:
      a self-read edge with more than one `gives`, or more than one id in
      `needs ∩ gives`; a self-read whose driven id is a published
      computed value rather than a bank coordinate; a self-read whose
      plan skeleton's free names, closed over the bindings table, still
      hold the driven id.
- [ ] 2.5 Tests for what is NOT refused: a version 6 document whose
      program carries no self-read edge loads and runs exactly as a
      version 5 one; a version 5 document is never given a reading,
      because the test is `needs ∩ gives` and not the version number.

## 3. The float primitives (`src/run/jumps.ts`, design D3)

- [ ] 3.1 Red, then write `ordinalOf`, `fromOrdinal`, `ulpOf`,
      `nextAfter` and `copySign` over a `Float64Array`/`BigInt64Array`
      view, with `BigInt` ordinals. Mirror `_ordinal`/`_from_ordinal`
      exactly, including the negative branch `-(2n**63n) - bits`.
- [ ] 3.2 Tests against values the producer's own functions answer:
      `ordinalOf(+0) === ordinalOf(-0) === 0n`; adjacent floats differ by
      `1n` at `1.0`, at `1e300` and at the smallest subnormal;
      `fromOrdinal(ordinalOf(x)) === x` over a spread including
      negatives and a binade boundary; `nextAfter(x, x) === x`;
      `nextAfter(0, 1) === 5e-324` and `nextAfter(0, -1) === -5e-324`;
      `ulpOf(1) === 2.220446049250313e-16`; `copySign(1, -0) === -1`.

## 4. The walk (`src/run/jumps.ts`, design D2)

Each of these mirrors a named piece of `_Walk` and is red before it is
green. They reuse `partition`, `branchesAt`, `levelAt`, `surfacesOf`,
`branchOf` and `bisect` — no second copy of any of them.

- [ ] 4.1 `retainedIncrement(program, reading, start, delta, described,
      coordinate, crossings, tick)` returning `{ increment, landing }`,
      and `retainedCuts(...)` returning the breakpoints, mirroring
      `_Retained.increment`/`_Retained.cuts`.
- [ ] 4.2 The walk's constructor zeroes the driven coordinate's own
      delta (`delta[own] = 0`). Give this its own test: a tick in which
      the same coordinate is ALSO driven by another edge (the corpus's
      `StoppedClearing` shape) must not advance `own` along the path.
- [ ] 4.3 The zero-source early return: a tick in which no source but the
      driven coordinate itself has a nonzero delta contributes `0`,
      reports no landing, and evaluates nothing.
- [ ] 4.4 Layer one: `partition` over `reading.outer`, its crossings
      recorded and its branches read at midpoints; `[0, 1]` and no
      evaluation where the independent subset is empty.
- [ ] 4.5 Layer two `decide`: branches in plan order with the driven
      coordinate at `ownLeft` and every other source at the piece's left
      end; the on-surface set from `_on_surface`'s rules (zero for `sign`
      and a comparison; a non-finite level is not on a surface; `%` at
      zero is not on a surface; otherwise `level === Math.floor(level)`);
      the probe as the first differing sample; the flip to
      `branchOf(jump, nextAfter(surface, probe))` and NEVER to the branch
      at the probe; the second flip of one node refusing the tick as
      chattering with the producer's message.
- [ ] 4.6 `firstCut`: the solved path where `jump.affine &&
      reading.affine`, taking the EARLIEST surface only (not all of them,
      which is where this differs from `crossingsOf`); the searched path
      with the three corrections — a sub-interval whose level does not
      move is skipped; a surface EQUAL to the left sample's level is not
      a crossing of that sub-interval; the surface reached first is the
      one NEAREST the left sample, and a right sample exactly on a
      surface is the crossing there. Every crossing with `where > t` is
      returned, one a hair inside the left end included.
- [ ] 4.7 Tests for 4.6 written as the three defects the framework's
      implementation found, each red first: the phantom crossing that
      jumps a whole surface on a gate that changes the RATE rather than
      holding the part; the flip to a branch the piece never enters on
      the same gate; the genuine crossing of order `1e-16` inside a left
      end, dropped, driving the part through its gap.
- [ ] 4.8 `land`/`farSide`: nothing to walk where the piece did not move
      the coordinate; otherwise the bracket sought in BOTH directions
      with the stride doubling from one ulp (`5e-324` where `own*` is
      zero), bisected in ordinal space until adjacent, the far one taken;
      the crossed nodes walked in plan order, each judged with the others
      at the piece's near-side branches. Two nodes crossing within
      `crossingTolerance` of one fraction are ONE cut.
- [ ] 4.9 `LandingInvariantError` where no bracket is found within 200
      doublings, naming the relation, the coordinate and the primitive,
      and saying the tick committed nothing. Note in the code that no
      test reaches it by construction, as `program.py` does.
- [ ] 4.10 `maxCrossings` refuses the walk with the existing `tooMany`
      message and count.

## 5. Reporting and committing (`src/run/edges.ts`, `src/run/run.ts`, design D4, D5)

- [ ] 5.1 `edgeIncrements` gains a `landings: Record<string, number> |
      null` output and dispatches on `edge.retained.length > 0`;
      `edgeCuts` routes through `retainedCuts`. `Run.along` keeps passing
      `null`, exactly as `Run._along` drops the report.
- [ ] 5.2 `Run.pass` threads `landings`; `Run.integrate` applies them to
      `committed` in BOTH places it builds one — after the full-stretch
      pass and after the segment pass — and BEFORE `reachedBounds` and
      before the stop loop, so a numeric stop on the same coordinate
      overwrites the landing. Red-first test for each of the two places.
- [ ] 5.3 `RefusalKind` gains `'landing'`; `refusalKind` maps the new
      class; `Run.integrate`'s catch lists it beside the other four, so a
      tick that fails AFTER a cut commits nothing — not the landing, not
      the crossing, not the bank. Test it directly with a conflict staged
      after a cut.
- [ ] 5.4 A self-read crossing is recorded as a crossing and never as a
      stop, and stops no input: test over the corpus's `StoppedClearing`
      shape, where `sim.stops` names only the ranged coordinates.

## 6. The framework's own numbers, mirrored (`src/run/run.test.ts`)

Each of these is a `bench()` document reproducing the framework fixture
in `tests/running_project/machine.py`, and each number is that
repository's own suite.

- [ ] 6.1 The `Clearing` bench, taken from the corpus's own copy of the
      document: inputs `setter` and `ring` (both rest `0`), `wheel.turn`
      rest `108`, one law edge with `needs ["setter", "ring",
      "wheel.turn"]` and `gives ["wheel.turn"]`, `GAP = 0.5`,
      `STATION = (100, 500)`.
- [ ] 6.2 The dial clears to its gap and the ring runs on: a sweep long
      enough to reach the band leaves `wheel.turn` within `0.5` of `360`
      on the disengaged side, the ring completing its whole travel, one
      crossing recorded and no stop.
- [ ] 6.3 A second and a third sweep move the dial by NOTHING — the same
      float, bit for bit (`Object.is`), not within a tolerance — and
      every command completes.
- [ ] 6.4 Swept backward from inside the station, the dial ends on the
      band's UPPER edge and does not move on a further backward sweep.
- [ ] 6.5 A dial standing exactly at a band edge holds in the direction
      that would take it deeper and turns in the direction that leaves —
      rule (c) from the outside.
- [ ] 6.6 The same sweep at one tick, twelve and two hundred and forty
      agrees within the run's agreement window, with no stop and no
      blocked command.
- [ ] 6.7 A run state taken after a partial sweep and restored resumes
      from the same float and reaches the same band edge.
- [ ] 6.8 The `StoppedClearing` bench: one segment reports both a landing
      and a bound on `wheel.turn`, and the BOUND wins — `wheel.turn`
      exactly `400`, its stop recorded, and the gauge's own stop at its
      own fraction of the same tick.

## 7. The corpus, green

- [ ] 7.1 `npm test -- running-corpus` passes: all 17 scenarios, 328
      ticks, exactly for discrete state and within `1e-9` relative for
      floats. Paste the count.
- [ ] 7.2 The width guard passes on the new corpus and fails on a
      narrowed copy naming one of the three new features.

## 8. Versions (design D6)

- [ ] 8.1 Red, then `solidNodeDocumentVersions` → `[1, 2, 3, 4, 5, 6]`
      and `RENDERED_VERSIONS` in `viewer.ts` with it;
      `src/version.test.ts` keeps pinning the two to each other and to
      `package.json`.
- [ ] 8.2 Red, then `solidNodeViewerApi` `14 → 15`, with the comment in
      `version.test.ts` written in that file's voice: why executing a
      version 6 document is a capability a host may require, and why 13
      stays skipped.
- [ ] 8.3 `viewer.ts`'s program gate `document.version === 5 ||
      (document as RunDocument).program !== undefined` becomes
      `>= 5`. Red first: a version 6 document with a `program` key
      already loads through the second clause, so the red test is a
      version 6 document whose `program` key is ABSENT, which must be
      refused as "a document declaring the running version must carry
      one" rather than loaded as a treeful document with no program.
- [ ] 8.4 `solid_node_viewer/capture.py`'s `carries_program` — today
      `document.get("version") == 5` — becomes `>= 5`, red first in the
      Python suite.
- [ ] 8.5 `bundle.py`'s `RELEASED_DOCUMENT_VERSIONS` does NOT move; add
      or extend a test asserting it is still `[1, 2, 3, 4]` and that
      `describe()['documentVersions']` is the package's new list.
- [ ] 8.6 `README.md`'s version table row → `| 0.2.0 | 15 | 1, 2, 3, 4,
      5, 6 |`, leaving the parenthetical about 13 as it is. Change
      nothing else in `README.md` unless a statement is actually false.
- [ ] 8.7 `CHANGELOG.md`: amend the existing API-8 bullet's last clause,
      which says "A version 6 document is refused by name and by list",
      to name version 7 — the smallest true edit, because within one
      unreleased release that sentence cannot stand beside 9.1's bullet.

## 9. The Curta, in a real browser (design D9)

- [ ] 9.1 Produce `tests/fixtures/clearing/viewer.json` from a
      **throwaway copy** of a solid-node checkout at main `8e15791`
      (never the pilot's checkout), with the workspace environment:
      `PYTHONPATH="$PWD" solid export
      tests/clearing_project/machine.py:CurtaInterface -o <dir>
      --no-widget`. Commit `viewer.json` **verbatim** and record its byte
      count, its declared version (6), its driver (`clearing`), its six
      coordinates and its six law edges, each with `needs ∩ gives`
      non-empty.
- [ ] 9.2 Stand the geometry in: each distinct model path the document
      names holds a copy of the 684-byte binary unit cube
      `tests/fixtures/pascaline/vendor/` already carries. Write
      `tests/fixtures/clearing/README.md` in that fixture's voice, saying
      exactly what is verbatim, what is a stand-in, and which framework
      commit it came from. Add `CLEARING = FIXTURES / 'clearing'` to
      `tests/support.py` and a plain test that every model path resolves,
      so a missing mesh fails as a missing mesh.
- [ ] 9.3 A vitest case loading the fixture through `Engine.load`: it
      does not throw; six edges carry a non-empty `retained`; each
      reading's `dependent` holds the band's `floor` and comparison and
      its `outer` holds the station's nodes; every reading's `affine` is
      `false`, which is the `clamp01` window making the skeleton
      non-affine and every crossing a searched one.
- [ ] 9.4 The browser acceptance, beside `tests/test_lock_document.py`'s
      and in its shape (`needs_playwright`, `needs_bundle`,
      `serve_directory`, `page.evaluate` over the mounted handle):
      - the document MOUNTS — no refusal, a run exists, no tick taken,
        the bank at the published rest values;
      - one full sweep of `clearing` leaves each of the six dials within
        `GAP` of a multiple of `360` in the sweep's direction, at a value
        the published gate reads DISENGAGED;
      - a SECOND sweep moves no dial at all, bit for bit, while
        `clearing` completes its whole travel;
      - no stop is recorded and every crossing names a dial's coordinate.
      Verify each number against the framework's own fixture before
      asserting it, and paste the measured banks into evidence rather
      than only the assertions.
- [ ] 9.5 Two inspected screenshots written to `tests/_shots/`, as the
      lock and Pascaline acceptances write their own: the six dials at
      rest, and the six dials cleared. Pixels are evidence.

## 10. What it costs (design D8)

- [ ] 10.1 Extend `src/run/cost.test.ts` with two printed measurements,
      each floored an order of magnitude below the bench as that file
      already does: the corpus's `Clearing` machine (solved crossings)
      and the committed Curta fixture (searched crossings, six dials).
- [ ] 10.2 Assert the other way too: `Train`'s existing measurement does
      not move. A document with no self-read edge pays one array-length
      test per edge per tick and nothing else.
- [ ] 10.3 Record both in evidence beside the framework's own numbers
      (`Clearing` 1 349 ticks/s and `CurtaInterface` 24.4 ticks/s in
      Python, `Train` 80 graph evaluations over ten ticks before and
      after) and beside this viewer's own base numbers from 0.2. State
      plainly whether the Curta fixture runs at the viewer's default step
      of `1/240 s`. **A shortfall is REPORTED to the pilot as a
      finding** — never mended by widening a tolerance, coarsening the
      step size or skipping a sample.

## 11. The whole suite, and the build

- [ ] 11.1 `npm run typecheck` clean, `npm test` green with its new
      count, `npm run build` writes `dist/solid-widget.js`. Paste all
      three.
- [ ] 11.2 The Python suite green with the rebuilt bundle, naming every
      skip. Paste it.
- [ ] 11.3 `acceptance.test.ts` — the Pascaline module — is unchanged to
      the digit: `tens.drum.turn` still `65.54` after ten `Add one`. A
      document with no self-read edge does not move.
- [ ] 11.4 `test_lock_document.py` unchanged: a version 5 document with
      constraints runs exactly as it did.

## 12. The record

- [ ] 12.1 `CHANGELOG.md`, a new bullet under `0.2.0 — unreleased`: the
      worker executes a law that reads the coordinate it drives; the
      Curta's own clearing interface mounts and clears six dials in a
      browser; the corpus is the producer's regenerated one (17
      scenarios, 328 ticks); `documentVersions` becomes
      `[1, 2, 3, 4, 5, 6]` and the API version rises to 15.
- [ ] 12.2 `docs/adrs/EXPORT/ADR-057-a-self-read-edge-is-executed-from-the-retained-value.md`,
      extracted AFTER implementation from what was decided and measured:
      the self-read is recognised as `needs ∩ gives` and its two-layer
      reading derived at load; the walk reads its branches at a piece's
      left end from the retained value; the landing is the nearest
      representable value on the far side, found in ordinal float space;
      the corpus is what holds the two runtimes to one algorithm. Cites
      ADR-045, ADR-047, ADR-054 and the framework's ADR-121. Take **057**
      and leave 055 free for the in-flight `slide-and-turn-parts` cycle.
      Update `docs/adrs/README.md` in its chronological order.
- [ ] 12.3 `openspec validate execute-the-self-read --strict` clean, the
      delta specs synchronized into
      `openspec/specs/viewer-package/spec.md`, and the change archived as
      `openspec/changes/archive/<date>-execute-the-self-read` with its
      evidence.
- [ ] 12.4 Report to the pilot, as findings rather than fixes: whether
      the Curta fixture runs at `1/240 s` (10.3); anything the framework
      and this engine disagreed on that was resolved in `program.py`'s
      favour; and the note that `src/partControls.ts` contains literal
      NUL bytes (its `${kind}\0${part}` key), so `grep` treats it as a
      binary file and needs `-a` — harmless, pre-existing, and a trap for
      anyone searching this tree.

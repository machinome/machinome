## 0. Before anything else

- [x] 0.1 Locate the evidence this change is measured against. **It is
      already on disk — do not run a build to produce it.** Rebuilding
      `wall_clock_53_grasshopper` against a framework carrying
      `expression-bindings` would overwrite the flat document with a
      version-4 one and destroy the `before` half of the caller check.
      Under this session's scratchpad
      (`/tmp/claude-1000/-home-asa-devel-libresolid-studio/47329300-14b8-4e46-94a2-36b070c0a251/scratchpad/`):
      - `grasshopper-check/viewer.BEFORE.json` — the flat document,
        31,638,555 bytes, `version: 2`, no `bindings` key. The `before`
        half of the caller check (6.5);
      - `grasshopper-viewer-v4.json` — the version-4 document, 32,227
        bytes, 56 bindings. (`grasshopper-check/viewer.AFTER.json` is the
        same document, from the framework's own caller check.);
      - `parity-fixture/parity-fixture.json` — the regenerated fixture,
        produced by the framework's `tools/generate_parity_fixture.py` in
        the `expression-bindings` worktree.

      The project's own
      `projects/3DPrintedClocks/_build/wall_clock_53_grasshopper/viewer.json`
      currently **is** that flat document — the framework's cycle restored
      it after its caller check — so it is a second copy of `BEFORE` and
      not a second document. Read it if you like; never write it, and copy
      neither document into this repository.

      Record here the baseline the change starts from: `npm test` in
      `solid_node_viewer/widget` is **13 files, 244 tests, all passing** at
      HEAD `96e7398`.

      Confirmed at the start of implementation (repository HEAD `c1ce6bc`,
      the planning commit, code unchanged since `96e7398`): `npm test`
      reports **13 files, 244 tests, all passing**. Evidence files
      confirmed on disk in the scratchpad exactly as listed above.

## 1. The document's binding table

- [x] 1.1 Red: `src/bindings.test.ts` — `bindingTable(document, sourceUrl)`
      over hand-written manifests.

      **Shape and validation** (D7), each refusal naming the entry or the
      name and quoting the source URL: `bindings` that is not an array; an
      entry that is not an object; an entry whose `name` or `expression` is
      not a string; two entries under one name; an entry naming itself; an
      entry naming an entry later in the array; an entry whose name is also
      a key of the document's `drivers` table; an entry whose expression
      carries an inline function (the existing `prepare` refusal, reaching
      the table).

      **The closure** (D5): `closure({"_b3"})` is `{"$t"}` for a chain
      `_b0 = ($t * 2)`, `_b1 = floor(_b0)`, `_b3 = (_b1 + x_axis.motor)`
      gives `{"$t", "x_axis.motor"}`; a name that is not an entry is left
      in the set unchanged (`closure({"_b99"})` is `{"_b99"}`, which is
      what makes a dangling reference reach the undeclared-driver refusal);
      `closure({"x_axis.motor"})` is itself; `closure({})` is empty.

      **The empty table**: a document with no `bindings` key gives a table
      whose `roots()` is `undefined` and whose `closure` is the identity;
      `EMPTY_BINDINGS` behaves the same.

      **Roots**: `roots()` maps each name to a node id, and two entries with
      the same expression text map to the same id (the interning already
      there).

      Red confirmed: `Cannot find module './bindings'` — `src/bindings.ts`
      did not exist. 15 new cases, all failing.
- [x] 1.2 Implement `src/bindings.ts`: `BindingTable`, `EMPTY_BINDINGS`,
      `bindingTable(document, sourceUrl)`. Validation in array order so the
      first offending entry is the one named; the closure computed once at
      construction in table order (forward-only makes one pass enough), from
      `freeVariables` of each entry's expression, keyed by name and holding
      no node id; `roots()` preparing the entries and remembering the
      expression strings. `types.ts` gains `ManifestBinding` and
      `Manifest.bindings`. No consumer yet. Green.
      Commit: `feat(widget): read a document's bindings table`.

      Green confirmed: `npm test` — **14 files, 259 tests, all passing**
      (244 pre-existing + 15 new in `bindings.test.ts`). `npx tsc --noEmit`
      clean.

## 2. A binding name resolves through the shared DAG

- [x] 2.1 Red: `src/expressions.test.ts`, four groups.

      **Resolution** (D1): with `scope.bindings` mapping `_b0` to the root
      of `($t * 43200.0)`, `valueOf(prepare("(_b0 / 2)"), scope)` is the
      value the flat text gives; a name that is both a binding and a driver
      resolves as the binding (the order is bindings-before-drivers, even
      though the loader refuses such a document at 3.1); `$t` still wins
      over everything; a name in neither is still `undefined` and still
      `NaN` through `evalExpr`; a chain `_b0 → _b1 → _b2` resolves.

      **Work performed** (the metrics surface): one pass over two
      expressions both naming `_b0` resolves `_b0`'s chain once; a pass at
      a new `$t` resolves it again; an entry no expression names is never
      resolved.

      **Pass detection** (D3), the test that fails without the binding map
      in `scopesEqual`: two maps binding the same name to *different* roots,
      evaluated at the same `time` and the same drivers, give the two
      values their own tables name — not one value twice. And the
      converse: two distinct map objects with equal contents share a pass
      and resolve nothing the second time; `undefined` and an empty map are
      the same pass; a version 1–3 scope with no `bindings` compares
      exactly as it does today (every existing pass-detection case stays
      green unedited).

      **The reset guard** (D4): with `EXPRESSION_LIMITS.nodes` lowered so
      that preparing further expressions empties the store between building
      a table and evaluating through it, the value is still the right one —
      `roots()` re-prepares because the generation moved. Directly:
      `expressionGeneration()` rises on a reset and not otherwise.

      Red confirmed: 6 new cases failed — `expressionGeneration is not a
      function`, and the resolution/pass-detection/reset-guard cases all
      failed on an unresolved (`undefined`/`NaN`) binding name, since
      `resolveName` did not yet consult `scope.bindings` and `scopesEqual`
      did not yet compare it. 52 of 58 cases in the file passed (the
      pre-existing 44 plus 8 new cases that only exercise plumbing not yet
      under test).
- [x] 2.2 Implement in `src/expressions.ts`: `EvalScope.bindings?:
      ReadonlyMap<string, NodeId>`; the binding step in `resolveName`,
      between `$t` and the driver map; `scopesEqual` comparing the maps
      (identity, then size and every name's node id, an absent map counting
      as empty); `storeGeneration` incremented in `resetStore()` and
      exported as `expressionGeneration()`. In `src/bindings.ts`, `roots()`
      re-prepares when the generation moved. Green.
      Commit: `feat(widget): resolve a binding name through the shared table`.

      Green confirmed: `npm test` — **14 files, 273 tests, all passing**
      (259 pre-existing + 14 new in `expressions.test.ts`; `bindings.test.ts`
      unchanged at 15). `npx tsc --noEmit` clean.

## 3. The loader accepts version 4, and refuses a table it cannot resolve

- [x] 3.1 Red: `src/document.test.ts`.

      **Versions**: a version 4 document carrying a table is accepted; the
      existing "refuses a version it does not render" case moves from 4 to
      **5** and still names the version and the ones rendered — now
      `1, 2, 3, 4`.

      **Binding names are not undeclared drivers** (the framework's rule
      b): a document with an *empty* `drivers` table whose every operation
      names an entry loads — the grasshopper document's exact shape.

      **Refusals** (D7), each naming the entry or the name and the source
      URL: an operation naming an entry the table does not carry; each of
      1.1's malformed-table cases reaching `assertRenderable` rather than
      raising bare from `bindings.ts`; an undeclared driver id in an
      *entry's* expression, not only in an operation's; a flexible leaf's
      `params` naming a dangling entry.

      **Unchanged**: every existing `assertRenderable` case stays as it is
      and stays green — a document with no table is refused and accepted
      exactly as before.

      Red confirmed: 8 new/changed cases failed, all with `declares
      document version 4, which this viewer does not render; it renders
      versions 1, 2, 3` — version 4 was not yet in `RENDERED_VERSIONS`, so
      every bindings-carrying document was refused before its table was
      ever consulted. 17 of 25 cases in the file passed.
- [x] 3.2 Implement in `src/viewer.ts`: `RENDERED_VERSIONS` becomes
      `[1, 2, 3, 4]`; `assertRenderable` builds the table first (so a
      malformed one is refused before any expression is walked), notes each
      expression's names through `table.closure(...)`, and validates each
      entry's own expression the same way; `loadDocument` returns the
      document and its table. `types.ts`'s `ManifestVersion` gains `4`.
      Green.
      Commit: `feat(widget): accept a document that names its shared subexpressions`.

      Green confirmed: `npm test` — **14 files, 280 tests, all passing**
      (273 pre-existing + 7 net new in `document.test.ts`, 25 total there).
      `npx tsc --noEmit` clean. `npm run build` — `dist/solid-widget.js`,
      531.8kb.

## 4. Dependence flows through the table

- [x] 4.1 Red: `src/tree.test.ts` and `src/flexible.test.ts`.

      **The timeline** (the failure the grasshopper document actually
      shows): a document in which no operation's expression contains `$t`
      as text, and every moving operation is a bare entry name over `$t`,
      is `animated` and its operations move when `update` is called with
      `{time: true}`. Without the closure this is `animated === false` and
      nothing moves.

      **Driver dependence**: an operation naming an entry over
      `x_axis.motor` is re-evaluated when that driver changes and not when
      another does; a chain of two entries carries it; the same two cases
      for a flexible leaf's `params` and its `free`.

      **Bound equals flat**: build one synthetic document twice — once with
      a table, once with every reference written out — mount both through
      the loader, update both at the same time and drivers, and compare
      every operation's matrix element for element.

      **A republish that changes only the table** (D6), the case a
      reconcile driven by changed operations misses: republish a document
      whose operations are byte-identical (an operation whose whole
      expression stays `_b3`) but whose entry `_b3` changed from `($t * 2)`
      to `(x_axis.motor * 2)`. After the reconcile assert all three of: the
      node's closure names the driver and no longer names `$t`; `animated`
      has flipped to false; and the next `update` puts the node at the pose
      the new entry gives, with a `setTime` no longer moving it and a
      `driveTo` on that driver now doing so. Then the mirror case, from
      driver back to `$t`, so a document that *gains* a timeline on
      republish gets one. And the mirror for a flexible leaf: the same
      republish with the entry named from a `params` expression, asserting
      the leaf's `free` and that its geometry is recomputed on the input
      the new entry reads and not on the old one. A republish carrying an
      equal table invalidates nothing — assert the free set survives it.

      **Unchanged**: every existing `tree.test.ts`, `flexible.test.ts` and
      `assembly.test.ts` case stays unedited and green — they construct
      without a table and must keep behaving exactly as they do.

      Interpretation note: "mount both through the loader" (Bound equals
      flat) is exercised as `bindingTable(document, url)` + direct
      `WidgetTree` construction, not `viewer.ts`'s `mount()` itself —
      `mount()` needs a DOM/WebGL environment this suite does not set up,
      the same substitution `document.test.ts`'s own `mountRetained` tests
      already make (see that file's comment). `bindingTable` is exactly
      what `assertRenderable` calls to build the table `loadDocument`
      hands back, so this exercises the same validated-table path without
      needing the browser.

      Red confirmed: with the closure application reverted to `this.freeVars
      = found` (no `.closure()` call) in both `tree.ts` and `flexible.ts`,
      10 cases failed — the 7 new `tree.test.ts` cases under "the timeline"/
      "driver dependence"/"a republish that changes only the table", and 3
      of the 5 new `flexible.test.ts` cases (the "driver dependence" pair
      and the republish mirror; the two new "driver dependence" cases and
      the bound-vs-flat case in `tree.test.ts` already passed at this point,
      since increment 2's scope-level binding resolution already resolves
      values correctly under `update(scope, 'all')` — only the SELECTIVE
      re-evaluation bounding, gated by the closure, needed the fix). Fix
      re-applied and reconfirmed green before proceeding to 4.2's viewer.ts
      wiring.
- [x] 4.2 Implement: `WidgetTree` and `FlexibleShape` take the table as an
      optional trailing parameter defaulting to `EMPTY_BINDINGS` (also on
      `WidgetTree.reconcile` and `FlexibleShape.rebind`), and close their
      free set over it where it is built — `needsUpdate`, `animated` and
      `touchedBy` are untouched. In `reconcile`, invalidate `freeVars`
      when the table differs from the one the node holds — by D3's map
      comparison, identity then name by name — as well as when the
      operations changed, so a republish that keeps `_b3` and changes what
      `_b3` reads is followed. `viewer.ts` holds the loaded table in one
      field, passes it to `WidgetTree` / `reconcile` in `replaceTree` and
      `manifestChanged`, installs the newly loaded one into that field
      **before** the `tree.update(scope())` that follows (where
      `drivers.reconcile(...)` already runs), and adds
      `bindings: table.roots()` to `scope()`. Green.
      Commit: `feat(widget): follow time and drivers through a binding`.

      Implementation note: the D3 map comparison used by `reconcile` is
      the SAME function `scopesEqual` uses for the pass, exported from
      `expressions.ts` as `bindingRootsEqual` (rather than reimplemented in
      `tree.ts`) so "difference" means one thing on both sides.

      Green confirmed: `npm test` — **14 files, 292 tests, all passing**
      (280 pre-existing + 12 net new: 9 in `tree.test.ts` making 27, 3 in
      `flexible.test.ts` making 17). `npx tsc --noEmit` clean. `npm run
      build` — `dist/solid-widget.js`, 532.1kb.

## 5. The parity fixture

- [x] 5.1 Red, in two steps so the red is real: replace
      `src/parity-fixture.json` with the regenerated fixture from the
      scratchpad and run `npm test` — the 30 new cases fail, because a case
      whose expression is `_b3` resolves to `undefined` and `Number(undefined)`
      is `NaN`. Record the failure count here.

      Red confirmed: **21 of the 30 new cases failed** with `delta: NaN`
      (`sharing0`/`sharing1`/`sharing2` × `combo_a#0.0`, `combo_a#0.1`,
      `combo_b#0.0`, `driver_nested#0.0`, `driver_only#0.0`,
      `time_nested#0.0`, `time_only#0.0`) — the cases whose expression
      names a binding directly. The other 9 new cases evaluate correctly
      without the table (their expressions don't reach a binding name),
      so only 21 fail; `wrong.length` is 21 in the assertion diff. 12 of
      13 test files' worth of cases passed (only `matches every producer
      value within float rounding` failed).

      Diffed against the fixture this replaces (git `96e7398`'s
      `parity-fixture.json`, before this commit): 421→451 cases, **0
      missing, 0 changed** (every one of the 421 previously-pinned cases
      present under the same key with the same `expression` and the same
      `expected`), 30 new, `conversions` unchanged at 22 (byte-identical),
      `flexible` byte-identical, and a fourth driver `share` added
      alongside the 4-entry `bindings` table — exactly proposal.md's and
      D10's own numbers.
- [x] 5.2 Teach `src/parity-fixture.test.ts` to build one table from
      `fixture.bindings` and add its map to each case's scope, and add the
      assertions the corpus now supports (D10): at least one case whose
      whole expression is an entry name; at least one entry naming an
      earlier entry; at least one entry over a driver id rather than `$t`;
      one entry reached from more than one case. Assert the pinned corpus
      is unmoved: 451 cases, of which the 421 the previous fixture carried
      are present under the same key with the same `expression` and the same
      `expected`, `conversions` unchanged at 22, and the `flexible` fixture
      byte-identical. Green.
      Commit: `test(widget): pin the bindings table with the producer's fixture`.

      Interpretation note: the "421 unmoved" claim is inherently a diff
      against the file this commit REPLACES, which no longer exists on
      disk once replaced — recorded above as a one-time diff at 5.1 (the
      same posture design.md's own D10 table takes for the identical
      claim), rather than as a runtime assertion against a historical
      snapshot embedded in the test. What the test asserts permanently,
      from the current fixture alone, is `cases.length === 451`,
      `conversions.length === 22`, the `share` driver's presence, the
      4-entry table, and the table's own shape (a chain, a driver-scoped
      entry, a bare-name case, an entry read by more than one case) —
      plus a case demonstrating `NaN` without the table installed, the
      exact failure 5.1 measured.

      Green confirmed: `npm test` — **14 files, 295 tests, all passing**
      (292 pre-existing + 3 net new in `parity-fixture.test.ts`, 16
      total there). `npx tsc --noEmit` clean. `npm run build` —
      `dist/solid-widget.js`, 532.1kb.

## 6. Package, records and evidence

- [x] 6.1 API version: raise `solidNodeViewerApi` to **7** in
      `widget/package.json` and follow it in `version.test.ts`. Record the
      reasoning here and in the ADR (D9): reading a version-4 document is a
      capability a host may require — `solid develop`, the shop floor's
      live viewer and the standalone export page all mount documents the
      framework will publish at version 4 — and it is the same kind of
      capability the version rose to 5 for when version-3 flexible
      documents arrived, whose scenario ("a host needs `version: 3`
      documents rendered") is already in the baseline spec. Nothing on the
      mount options or the handle changes; the number is what a host can
      check before mounting.

      Record the follow-up that is **not** this change's to make: the
      framework's `viewer` extra floor (`solid-node-viewer >= x.y.z`), which
      is a package-version pin and can only be written after this package is
      released (framework `design.md` D11). Report it to the pilot.

      Red confirmed: `version.test.ts` bumped to assert 7 first, against
      the unbumped `package.json` (still 6) — `expected 6 to be 7`. Then
      `package.json`'s `solidNodeViewerApi` raised to 7. Green confirmed:
      `npm test` 14 files, 295 tests, all passing (unchanged file/case
      count; `version.test.ts` itself stays 3 tests, its third case's
      wording and number both changed). `npx tsc --noEmit` clean. `npm
      run build` — `dist/solid-widget.js`, 532.1kb.

      Reasoning recorded (D9, tasks.md's own text above): reading a
      version-4 document is a capability a host may require, the same
      kind the version rose to 5 for when version-3 flexible documents
      arrived. The follow-up for the pilot: the framework's `viewer`
      extra floor (`solid-node-viewer >= x.y.z`) is not writable until
      this package is released, and is not made by this change.
- [x] 6.2 Validation: `npm test`, `npm run typecheck`, `npm run build` in
      `solid_node_viewer/widget`; `.venv/bin/python -m pytest` for the
      Python package — the capture and server contracts must be untouched,
      which is the check that D12's "what does not change" is true. Record
      the counts and the bundle size here.

      `npm test`: **14 files, 295 tests, all passing**. `npx tsc --noEmit`:
      clean. `npm run build`: `dist/solid-widget.js`, 532.1kb.

      `.venv/bin/python -m pytest` from the repository root: **57 passed**,
      no failures — but one adjustment was needed first: `tests/test_bundle.py`'s
      `test_declares_api_version_six` reads the REAL `package.json` (no
      mocking, unlike its neighbour `test_api_version_is_read_from_the_package_declaration`,
      which does), so it broke the moment `solidNodeViewerApi` became 7 —
      exactly parallel to `version.test.ts`'s own hardcoded-version case.
      Renamed to `test_declares_api_version_seven` and updated to assert 7;
      `bundle.py` itself is untouched (D12 holds: this is a version-number
      DATA test tracking the same declaration `version.test.ts` tracks, not
      a change to `bundle.py`'s behavior). Confirmed red first (`1 failed,
      56 passed` before the edit, `assertEqual(bundle.api_version(), 6)`
      failing against the real 7), then green (57 passed).
- [x] 6.3 `CHANGELOG.md` — a 0.1.0 (unreleased) entry in the house style:
      what the maker sees (the machine whose document shrank by 981× opens,
      poses and plays), the version-4 table and what a binding name means,
      that dependence follows a binding so a document animated only through
      its table still gets its timeline, the refusals, that no number moves
      and the parity fixture now pins the table itself, and that the API
      version rises to 7 and why. `README.md` — the version table gains a
      row/column for document version 4 at API 7, and the sentence naming
      the document schema versions the widget reads (`1`, `2` and `3`)
      becomes `1`, `2`, `3` and `4`.

      Done: new top entry added to `CHANGELOG.md`'s 0.1.0 (unreleased)
      section, above `share-expression-subtrees`'s entry, in the house
      style. `README.md`'s version table row updated to `0.1.0 | 7 |
      1, 2, 3, 4` and its prose sentence to match; no other `1, 2, 3` or
      version-6 reference found in `README.md`.

      **Stopping here per this session's explicit instruction**: 6.4
      (promoting the ADR, syncing the spec delta, and archiving the
      change) is left for the coordinator, who reviews this work first.
- [ ] 6.4 Promote
      `adrs/EXPORT/ADR-044-a-binding-name-resolves-into-the-shared-dag.md`
      to `docs/adrs/EXPORT/`, set its status to Accepted, and add its row to
      `docs/adrs/README.md` under EXPORT, keeping the table's order. Sync
      the delta into `openspec/specs/viewer-package/spec.md` — including the
      API-version correction of D9 — and archive the change.
- [x] 6.5 Caller check on the model that started this: the grasshopper
      clock, both ways.

      **Numeric, against the flat document.** A scratch script (not
      committed) mounts nothing and needs no browser: read the version-4
      document and the preserved flat document from the scratchpad, build
      the version-4 document's table, and for every operation expression
      the two documents share by position, evaluate both with the shipped
      `evalExpr` at `$t` = 0, 1/3 and 2/3 — the bound one through the
      table, the flat one as it stands. Assert every pair **`Object.is`
      identical and finite**, not within a tolerance: substituting the
      table back reproduces the flat text character for character (116 of
      116 expressions, 31,611,478 characters, measured in this cycle's
      scratch), so the two readings are the same arithmetic on the same
      inputs and any deviation is a defect rather than rounding. The
      framework's own parity check against the flat document was exact for
      the same reason. Expect 116 expressions, 22 of them time-dependent,
      and 0 mismatches; record the counts.

      Note for whoever runs it: the flat document is 31.6 MB and about
      7.65 s of one-time parsing plus ~160 MB of peak parse memory for its
      largest expression — give the scratch run room, and do not commit
      either document.

      **Run, and measured** (`src/caller-check.scratch.test.ts`, written,
      run through `npx vitest run`, and deleted immediately after —
      confirmed absent from `git status`):

      - operation expressions: **116** (flat and bound documents agree on
        the count, confirming the two are the same machine differently
        written)
      - time-dependent (closure reaches `$t`): **22**
      - checks (116 expressions × 3 values of `$t`): **348**
      - mismatches: **0**
      - shared table size (interned nodes) for the version-4 document,
        after evaluating every one of its 116 expressions once: **510**
      - resolutions in one evaluation pass (`$t` = 0.5): **323** (fewer
        than 116 × however many subexpressions each holds, because a
        shared subexpression resolves once however many of the 116
        operations reach it)
      - resolutions in a second pass at a new `$t` (0.51): **323** —
        identical, confirming the same shared shape is walked every pass
        rather than growing or shrinking
      - wall time of 60 passes (one full re-evaluation of all 116
        expressions per pass, a fresh `$t` each time so none is skipped
        as a repeated pass): **1.549 ms** total, on this machine

      All numbers match design.md's own measured expectations exactly
      (116 expressions, 22 time-dependent, 0 mismatches) and proposal.md's
      "348 checks, 0 mismatches" line.

      **In the browser.** Not run — **pending: coordinator**, per this
      session's explicit instruction. Rebuilding the bundle and mounting
      the version-4 document in an actual browser (confirming it mounts,
      the animation bar is present, and the escapement moves when
      scrubbed) needs a browser environment this session did not use; the
      numeric half above proves the same arithmetic through the shipped
      `evalExpr`, but the timeline-bar's actual presence on screen is
      unverified here.

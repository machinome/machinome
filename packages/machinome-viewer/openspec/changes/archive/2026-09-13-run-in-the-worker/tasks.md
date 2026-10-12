## 0. Before anything else

- [x] 0.1 Record the baseline this change starts from, in this file: the
      worktree HEAD, `npm test` in `solid_node_viewer/widget` (files, tests,
      all passing), `npm run typecheck`, and the Python suite with the
      workspace venv
      (`PYTHONPATH=<worktree> /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest`,
      naming what it skips). The worktree has no `dist/` yet, so every
      `@needs_bundle` test skips until task 12.1 builds one; say so.
- [x] 0.2 Copy the framework's committed corpus into the widget source,
      **byte for byte**, as `src/running-corpus.json`, from
      `solid-node/WTs/open-run-simulation/tests/running-corpus.json`.
      Never regenerate it here: the numbers in it are the framework's.
      Record its size, its `generated_by`, its thirteen scenarios over
      eleven machines and its 260 ticks.
- [x] 0.3 Copy the acceptance document into
      `tests/fixtures/pascaline/viewer.json`, **verbatim**, from
      `projects/Calculators/Pascaline-module/WTs/open-run-simulation/_build/viewer.json`,
      and write a tiny stand-in binary STL (a unit cube) at each of the
      fifteen model paths it names, so the fixture is about 35 kB instead
      of 1.5 MB. Add `tests/fixtures/pascaline/README.md` saying exactly
      that: the document is the module's published build verbatim, the
      geometry is a stand-in, because this repository tests a run and not a
      mesh. Read the project; write nothing there.

## 1. The corpus, red before anything can pass it

- [x] 1.1 Red: `src/run/running-corpus.test.ts` — the whole conformance
      suite, written against the engine that does not exist yet, so it
      fails to resolve `./engine` and every scenario is red. For each of
      the corpus's scenarios: build the engine from the fixture's
      `document` (`format`, `version`, `drivers`, `instructions`,
      `bindings` when present, `program` — and no `root`, `pieces` or
      `animation`) at the fixture's `dt` with a record ring covering the
      whole run; for `tick = 1 … steps`, apply the script entries naming
      that tick in array order (`move` with `by`/`to` and `duration`,
      `rate`, `trigger` binding one handle per issued command in order,
      `snapshot`, `restore`), integrate one tick, and compare the fixture's
      entry.

      Comparison rules, stated once in the suite and used everywhere:
      EXACT (`Object.is`) for the tick number, every status word, every
      coordinate, relation, primitive, bound side and input name, every
      crossing `level`, and the ORDER of `crossings`, `stops`, `inputs`
      and `commands`; RELATIVE for every bank value, every `t`, every
      `admitted` and every stop `value`, as
      `|a − b| <= tolerance.float * max(1, |a|, |b|)` with
      `tolerance.float` read from the fixture, never from a constant here.
      A failure names the scenario, its `dt`, the tick and the key.
- [x] 1.2 Red: in the same file, the width guard — a mirror of the
      generator's `uncovered_features` over the committed fixture: the five
      jump primitives and a comparison, a multi-source law, a stop located
      inside a tick, a bound stated as an expression, a command retired
      `blocked`, a rate, a snapshot, a restore, both instruction forms, and
      a tick carrying both a crossing and a stop. It reads the fixture
      only, so it is red only if the fixture is narrowed — run it against a
      deliberately trimmed copy to prove it fails, then against the real
      one.

## 2. The evaluation scope

- [x] 2.1 Red: `src/run/scope.test.ts` — `nest({'units.drum.turn': 7})` is
      `{units: {drum: {turn: 7}}}`, and `evalExpr('(-1 * units.drum.turn)',
      {time: 0, drivers: nest(...)})` is `-7`. Include the shipped
      failure as its own case: the value through today's
      `DriverStore.scope()` is `NaN`.
- [x] 2.2 Green: `src/run/scope.ts` — `nest(flat)` nesting at every
      segment, and `assertNestable(ids)` refusing an id that is a strict
      prefix of another, naming both.
- [x] 2.3 Red then green: `src/drivers.test.ts` gains a three-segment
      driver id whose scope resolves; `DriverStore.scope()` delegates to
      `nest`. Prove the existing driver and instruction tests are
      unchanged.
- [x] 2.4 Red then green: `src/expressions.test.ts` — `sign` at negative
      zero resolves as the framework's `(x > 0) − (x < 0)` does, not as
      `Math.sign` does; `context.sign` takes the framework's formula.
      Re-run `parity-fixture.test.ts` unedited and record that every case
      still passes.

## 3. The program, loaded and refused

- [x] 3.1 Red: `src/run/program.test.ts` over hand-written programs — every
      refusal of design §4, each naming the thing and quoting the source:
      no `program` on a version 5 document; a missing published key; an
      unknown coordinate `kind`; a non-finite `initial`; inputs
      disagreeing with the `drivers` table either way; an id set that
      cannot be nested; a `clock` colliding with an id; an unknown edge
      `kind`; a law whose `expressions`/`affine`/`plans` are not aligned
      with `gives`; a `check` with a non-empty `gives`; a formula without
      `slot`/`factors`/`constant`; a `needs` or `gives` naming an unknown
      value; a jump `primitive` outside the ten; two plans sharing a
      placeholder; an expression whose free names are not among its edge's
      `needs` plus that plan's placeholders; a bound reading anything but
      its own coordinate; a span over an unbanked coordinate; a missing or
      non-finite limit; a `sources` entry naming an unknown id; and a
      computed value the document READS that no edge gives.
- [x] 3.2 Red: the same file — what loading a **good** program yields: the
      coordinate order verbatim, `kinds`/`units`/`domains`/`initial`, the
      intermediates, the edges in published order with one prepared
      `NodeId` per expression, the spans, the sources, the limits, the
      clock, the identity, and the derived `determiner` map. Load the
      acceptance document's program from the committed fixture and assert
      its shape: 12 coordinates with the three inputs first, 6
      intermediates, 9 edges, 3 plans with one `floor` jump each, no spans,
      `limits.agreement === 1e-9`.
- [x] 3.3 Green: `src/run/program.ts`.
- [x] 3.4 Red then green: the held node ids are generation-guarded (design
      D12) — lower `EXPRESSION_LIMITS.nodes` in a test, force a store
      reset after a program is loaded, and assert the program still
      evaluates to the same numbers because it re-prepared from the
      expression strings it keeps, exactly as `bindings.ts` does.

## 4. The edges

- [x] 4.1 Red: `src/run/edges.test.ts` — `values`, `increments`, `cuts`,
      `linear` and `predicts` against hand-built edges: a law that is the
      difference of two evaluations; a constant law (`expressions: [null]`)
      contributing zero; a wiring's `source × factor` and
      `Δsource × factor`; a formula forward (`constant + Σ needs·factors`);
      a formula backward (slot first with factor `0.0`, the solved-for term
      last with its own coefficient, value
      `(slot − constant − Σ other·factor) ÷ own`); an increment being the
      same arithmetic with the constant replaced by zero; a check
      predicting over every need but the slot. Pin the accumulation ORDER
      by a case whose re-association changes the last bits.
- [x] 4.2 Green: `src/run/edges.ts`.
- [x] 4.3 Red then green: every evaluation gets a FRESH scope object
      (design D11). Evaluate one expression at two source values through a
      single mutated scope object and through two fresh ones, and assert
      the mutated pair returns the stale memoized value while the fresh
      pair does not — then assert no module under `src/run/` ever writes
      into a scope it has passed to the evaluator.

## 5. The jump plan

- [x] 5.1 Red: `src/run/jumps.test.ts` — `branchOf` for each of the ten
      primitives (`floor`, `ceil`, `sign` by the framework's formula, `%`
      as the truncated quotient, each comparison against zero);
      `surfaces` between two level values, exclusive and inclusive, with
      `%` skipping the zero surface, with the non-finite refusal and with
      the `max_crossings` refusal; `deduplicated` folding a crossing
      located twice from either side; `merged` folding two cuts closer than
      the tolerance and ending at exactly `1`.
- [x] 5.2 Red: the partition and the increment — postorder over the jump
      nodes, an affine level quantity solving every surface between two
      endpoint values, a non-affine one sampled at `subdivisions`, bracketed
      and bisected to `crossing_tolerance` in at most `bisection_rounds`,
      the branch read at each piece's MIDPOINT, and the increment as the
      plain sum over the pieces. A zero-length path contributes zero
      without evaluating anything. The crossings list is sorted by fraction
      then postorder index.
- [x] 5.3 Green: `src/run/jumps.ts`.

## 6. Commands

- [x] 6.1 Red: `src/run/commands.test.ts` — `admits` as a pure function of
      the tick count since the start: a zero-duration move landing entirely
      at the tick it was requested on and nothing after; a ramped move
      admitting `value_at(k) − value_at(k−1)` with the integer
      distribution `start + floor(delta·k / ticks)` (including a NEGATIVE
      delta, where floor and truncation differ); a rate admitting
      `cumulative(k) − cumulative(k−1)` with `cumulative` truncated toward
      zero for an integer input; `finished`; `requested`/`admitted`/
      `remaining`/`rate` in design units through the declaration's scale;
      `cancel` on an active and on a retired command.
- [x] 6.2 Red: the refusals — exactly one of `by`/`to`; a duration that is
      not a whole number of ticks, naming the duration and the step size;
      an input that is not a declared one, listing the declared ones; a
      second command on an owned input, naming the owner; `rate(input, 0)`
      completing an active rate and being a no-op otherwise.
- [x] 6.3 Green: `src/run/commands.ts`, reusing `toNative` from
      `drivers.ts` for the design→native conversion.

## 7. The run

- [x] 7.1 Red: `src/run/run.test.ts` — one pass over the edges in program
      order: increments propagated, a value no edge determines holding, a
      conflict between two determinations, a check whose prediction
      disagrees, each refusing with a message naming the relation as
      written and the class that stated it.
- [x] 7.2 Red: the stop machinery — `reached` (outside a bound AND further
      outside than it began, with the "already at the bound and moving
      away is free" case), `event` (the earliest, with everything within
      the crossing tolerance of it as one event), `locate` in its three
      cases (affine with no cuts: one division; affine with cuts: solved
      inside the bracketing piece; anything else: sampled, bracketed,
      bisected), `group` (the published sources filtered by whether the
      candidate's own admission alone gives the coordinate a nonzero
      increment), `block`, and the stop-invariant refusal.
- [x] 7.3 Red: the segment loop and atomicity — a tick with two stops at
      two fractions; a tick whose crossing fractions are mapped back to the
      fraction of the TICK across a segment boundary; a tick that refuses
      in its second segment committing nothing at all, with the bank, the
      tick count and the records standing and the commands that moved
      retired `refused`.
- [x] 7.4 Red: state — `snapshot` carrying identity, `dt`, tick, bank and
      command records; `restore` refusing a different identity or a
      different `dt` before touching anything, cancelling live handles,
      rebuilding the command table and clearing the rings; `reset` as a
      restore of the initial; the three bounded rings.
- [x] 7.5 Green: `src/run/run.ts`.

## 8. The engine, and the corpus turning green

- [x] 8.1 Green: `src/run/engine.ts` — the façade tasks 1.1 and 1.2 were
      written against: build from the program-bearing keys, `move`, `rate`,
      `trigger`, `cancel`, `advance(n)`, `snapshot`, `restore`, `reset`,
      `state()`, `tick`, `clock`, and `ticksFor(seconds)` reproducing
      `Sim._ticks`.
- [x] 8.2 Run the corpus suite. Every one of the thirteen scenarios, all
      260 ticks, must pass under the corpus's own tolerance. Record here,
      scenario by scenario, that it does. **A divergence is a bug in this
      engine: fix the engine. Do not widen a tolerance, do not skip a
      scenario, and do not edit the fixture.**
- [x] 8.3 Record the cost: ticks per second for `CarryLead` (affine plans,
      solved) and for a searched plan, in node, so a later regression is a
      number rather than an impression.

## 9. The document admits version 5

- [x] 9.1 Red: `src/document.test.ts` — `RENDERED_VERSIONS` is
      `[1, 2, 3, 4, 5]`; a version 5 document loads; a version 6 document
      is refused naming 6 and the five it renders; a version 5 document
      whose program is malformed is refused by the §4 messages; the
      declared-name set is widened to the clock, the coordinates, the
      intermediates and each plan's own placeholders, and a name outside
      all of those is still refused naming it.
- [x] 9.2 Red: the same file — every existing version 1 to 4 case passes
      **unedited**, including the bindings-table refusals and the
      undeclared-driver refusal. Record that the file's pre-existing cases
      were not touched.
- [x] 9.3 Green: `viewer.ts`'s `RENDERED_VERSIONS` and `assertRenderable`,
      returning the loaded program beside the binding table.

## 10. The worker and its protocol

- [x] 10.1 Red: `src/run/protocol.test.ts` — the request/reply pairing, the
      positional bank against the `order` from `ready`, `moved` as indices,
      and the encoding of a refusal and of an error.
- [x] 10.2 Red: `src/run/runtime.test.ts` in plain node against a fake
      message port: one advance in flight (a second frame while one is
      outstanding sends nothing and accumulates its elapsed time); the
      wall-time debt capped at four frames' worth; the fractional tick
      remainder carried across frames so a slow speed never stalls at zero
      ticks; commands queued in order while an advance is outstanding; a
      refusal pausing the run rather than retrying; a `Worker` constructor
      that throws falling back in-thread with `runsInWorker === false`.
- [x] 10.3 Green: `src/run/protocol.ts`, `src/run/worker.ts`,
      `src/run/runtime.ts`.
- [x] 10.4 Green: `build.mjs` — the first pass bundling `src/run/worker.ts`
      to a string, injected as `__WORKER_SOURCE__`; still exactly one
      published file, `dist/solid-widget.js`. Prove it: the built bundle
      contains the worker source and `dist/` holds one `.js`.

## 11. Posing, and the handle

- [x] 11.1 Red: `src/run/pose.test.ts` — the scope a committed bank makes
      (`time: 0`, the bank and the clock name nested in `drivers`, the
      bindings roots), and the `Changed` set from a frame's `moved`
      indices. A node reading only an idle coordinate is not re-evaluated.
- [x] 11.2 Green: `viewer.ts` — a version 5 document starts a runtime,
      poses at the published rest bank before the first tick, and poses
      each committed bank in the animation loop through
      `tree.update(scope, {time: false, drivers: moved})`; the rendering
      loop never advances the run; `dispose()` tears the runtime down.
- [x] 11.3 Green: the `run()` handle of design §7, with `runsInWorker`, and
      `run()` returning `null` for a document with no program.
- [x] 11.4 Red then green: `src/options.test.ts` — the
      `run: {dt, record, autostart}` mount option, its defaults (`1/240`,
      600 ticks, not started), and the refusal of a non-finite or
      non-positive `dt` naming the value.
- [x] 11.5 Red then green: a mounted run is stopped (design D13) — mounting
      takes no tick, leaves the elapsed clock at zero and poses the rest
      bank; `run: {autostart: true}` starts it. Assert the capture's own
      mount options (`animation: 'external'`) take no tick either, which is
      what gives the still its rest pose for nothing.

## 12. The versions this build declares

- [x] 12.1 Red then green: `package.json` — `solidNodeViewerApi` 7 → 8 and
      a new `solidNodeDocumentVersions: [1, 2, 3, 4, 5]`; `build.mjs`
      injects `__DOCUMENT_VERSIONS__`; `src/version.ts` exports it;
      `src/version.test.ts` pins that the bundle's list and
      `RENDERED_VERSIONS` are the same array, so the number the viewer
      reports and the versions it refuses by cannot drift apart. Build the
      bundle (`npm run build`) so the Python suite stops skipping.
- [x] 12.2 Red then green: `tests/test_bundle.py` and `tests/test_cli.py` —
      `describe()` and `solid-node-viewer describe` carry
      `documentVersions`, read from the widget's `package.json`, beside the
      existing keys. Leave `/_viewer` and the development server alone: its
      consumer mounts the bundle and lets it refuse, and the consumer that
      must ask before publishing asks the entry point.
- [x] 12.3 Green: `tests/test_widget_e2e.py` — the mounted handle and the
      global report API version 8.

## 13. The acceptance: the Pascaline module in a real browser

- [x] 13.1 Red: `tests/test_running_document.py`, a Playwright test on the
      committed fixture of task 0.3, in the harness-page shape
      `ViewerMountApiTest` already uses. Mount `viewer.json`; assert the
      handle's `run()` is not null and its `identity` is the document's;
      assert the rest pose (`state()['tens.drum.turn'] === 0`). Then
      `trigger('Add one')` and `step(240)` ten times over, awaiting each
      outcome, and assert `state()['units_entry'] === 10`,
      `state()['units.drum.turn'] === 360` and
      `state()['tens.drum.turn']` equal to **65.54** within `1e-9`
      relative — the framework's own number for ten `Add one`, which the
      module's `test_the_second_carry_is_cumulative` pins as `CARRY_THROW`.
      Assert the units drum mesh's world matrix differs from the one it had
      at rest, so the bank is provably reaching the geometry, and that the
      page logged no error.
- [x] 13.2 A screenshot of the fixture at rest and after the ten
      instructions, taken the way `WidgetE2ETest` takes one, inspected by
      eye and recorded here — pixels are evidence, and a green suite is
      not an inspection.
- [x] 13.3 Record whether the run used the worker (`runsInWorker`) in that
      page, and the wall time the ten instructions took.

## 14. The whole suite, the docs and the records

- [x] 14.1 `npm run typecheck` and `npm test` in `solid_node_viewer/widget`
      — record files, tests and that every pre-existing test passes
      unedited except the ones tasks 2.3, 2.4, 9.1 and 12.1 deliberately
      changed. `npm run build`. The Python suite with the workspace venv —
      record what it skips and why.
- [x] 14.2 `README.md`: the version table gains `0.2.0 | 8 | 1, 2, 3, 4, 5`;
      the opening list says the widget runs a document that carries a
      program, in a worker; "Working on the viewer" is unchanged.
- [x] 14.3 `CHANGELOG.md`: a new `## 0.2.0 — unreleased` section above
      0.1.0, which is left exactly as it is. Say what is true: the viewer
      reads version 5 and runs the machine; the numbers are pinned against
      the framework's corpus; there is no on-screen control for a running
      document yet, and that is the next change. Do not describe 0.1.0 or
      0.2.0 as released.
- [x] 14.4 Write the three ADRs design §14 names, as
      `docs/adrs/EXPORT/ADR-045-…`, `ADR-046-…`, `ADR-047-…`, and add them
      to `docs/adrs/README.md`'s index in order, with status `Accepted`.
- [x] 14.5 Record in this file the findings of design §15 that the
      framework side may want to act on, so the report to the pilot and
      this change's record say the same thing.
- [x] 14.6 `openspec validate run-in-the-worker --strict` passes;
      `openspec archive run-in-the-worker` only when the pilot says so.


## Record

Every task above is done. The full evidence -- the RED text of every test
before the production code that turned it green, the corpus result
scenario by scenario, the cost measurements, the acceptance numbers, the
two inspected screenshots, the suite counts, the findings for the
framework side and the deviations from `design.md` -- is in
[`evidence.md`](evidence.md) beside this file.

Summary of the numbers the tasks ask to be recorded here:

- **Baseline** (0.1): HEAD `3ee1236`, widget 14 files / 298 tests all
  passing, typecheck clean, Python 1 failed / 38 passed / 20 skipped --
  the failure and every skip being the absent `dist/` bundle.
- **The corpus** (0.2, 8.2): `tests/running-corpus.json` copied byte for
  byte, 170,449 bytes, `generated_by` `tools/generate_running_corpus.py`,
  13 scenarios over 11 machines, 260 ticks. Every scenario passes under
  the corpus's own `tolerance.float` of `1e-9`; nothing was widened,
  skipped or edited.
- **The acceptance fixture** (0.3): the Pascaline module's `viewer.json`
  verbatim, 32,994 bytes, with fifteen 684-byte stand-in unit-cube STLs
  (43 kB in all, against 1.5 MB of real geometry).
- **The cost** (8.3): 88,356 ticks/s for CarryLead's affine plans,
  13,242 ticks/s with the same plans forced to search, 24,623 ticks/s for
  the Pascaline at `dt = 1/240` -- about a hundred times real time.
- **The acceptance** (13.1 to 13.3): `runsInWorker` true, 258 ms of wall
  time for 2400 ticks, `tens.drum.turn` 65.53999999999998 against the
  framework's CARRY_THROW of 65.54.
- **The whole suite** (14.1): widget 26 files / 482 tests, typecheck
  clean, one published `dist/solid-widget.js` of 631.6 kb; Python 62
  passed / 1 skipped (the React development app, unbuilt and untouched).
- **The findings** (14.5): six, three of them design §15's and three
  found here about the corpus's width. All in `evidence.md`.

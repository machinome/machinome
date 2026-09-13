# Evidence — run in the worker

Every red test's failure text, recorded before the production code that
turns it green, and the measurements the tasks ask for.

## 0.1 Baseline

Worktree HEAD `3ee1236d711cabed2f801c620d72079b52e54705` (the planning
commit for both cycle-5 changes), on `open-run-simulation`, base
`6fb082ba9823fb0839631bd4a3ecbf4a41b33b64`.

```
$ npm test          (solid_node_viewer/widget)
 Test Files  14 passed (14)
      Tests  298 passed (298)

$ npm run typecheck
tsc --noEmit        -> exit 0, no output

$ PYTHONPATH=<worktree> .venv/bin/python -m pytest -q
1 failed, 38 passed, 20 skipped
```

The one failure and all twenty skips are the same fact: this worktree has
no `dist/solid-widget.js` yet, because `dist/` is ignored and nothing has
run `npm run build` here. Every `@needs_bundle` test skips
(`tests/test_capture.py` 3, `tests/test_real_time_playback.py` 4,
`tests/test_server.py` 1, `tests/test_widget_e2e.py` 12) and
`tests/test_cli.py::ModuleEntryTest::test_the_package_runs_as_a_module_through_the_interpreter`
fails because it spawns the CLI, which exits non-zero with "Viewer bundle
not found ...". Task 12.1 builds the bundle and both go away.

## 1.1 / 1.2 RED — the conformance corpus, before the engine exists

`src/run/running-corpus.test.ts` written first, against `./engine`,
`./commands` and `./program`:

```
FAIL  src/run/running-corpus.test.ts [ src/run/running-corpus.test.ts ]
Error: Cannot find module './engine' imported from
  .../src/run/running-corpus.test.ts
Test Files  1 failed (1)   Tests  no tests
```

Thirteen scenarios, the fixture-identity case and the two width cases are
all red, because the file does not resolve at all.

## 2.1 RED — the nesting of a qualified id

`src/run/scope.test.ts`, eleven cases, all red at collection:

```
FAIL  src/run/scope.test.ts
Error: Cannot find module './scope' ... Does the file exist?
```

Green after `src/run/scope.ts`: 11 passed. The shipped-failure case
inside it stays as a case of its own — a scope built by splitting at the
first dot evaluates `(-1 * units.drum.turn)` to `NaN`.

## 2.3 — `DriverStore.scope()` delegates

`src/drivers.test.ts` gained no edit beyond the new three-segment case in
`src/run/scope.test.ts` (`DriverStore.scope` describe block there);
`drivers.ts`'s own builder now calls `nest`. The 28 pre-existing driver
and instruction cases pass unedited.

## 2.4 RED — `sign` at negative zero

```
FAIL  src/expressions.test.ts > valueOf: semantics agree with the shipped
      evaluator > resolves sign by the producer's formula, including at
      negative zero
AssertionError: expected -0 to be +0 // Object.is equality
 - Expected  0
 + Received -0
```

Green after `context.sign = (x) => (x > 0 ? 1 : 0) - (x < 0 ? 1 : 0)`.
`src/parity-fixture.test.ts` re-run unedited: 16 files' worth of cases,
all still passing (16 tests).

## 3.1 / 3.2 RED — the program loader

```
FAIL  src/run/program.test.ts
Error: Cannot find module './program' ... Does the file exist?
```

40 cases: 26 refusals of design §4 (every item 1 to 14), four "reads a
good program verbatim" cases, three over the committed acceptance
document and one generation guard. Green after `src/run/program.ts`:
40 passed.

## 4.1 / 4.3 RED — the edges

```
FAIL  src/run/edges.test.ts
Error: Cannot find module './edges' ... Does the file exist?
```

14 cases. Green after `src/run/edges.ts`: 14 passed. The accumulation
order is pinned by three terms (1e16, 1, 1) that sum to `1e16` in `needs`
order and to `10000000000000002` re-associated.

## 5.1 / 5.2 RED — the jump plan

```
FAIL  src/run/jumps.test.ts
Error: Cannot find module './jumps' ... Does the file exist?
```

23 cases. Green after `src/run/jumps.ts`: 23 passed.

## 6.1 / 6.2 and 7.1 to 7.4 RED — commands and the run

```
FAIL  src/run/commands.test.ts
Error: Cannot find module './commands' ...
FAIL  src/run/run.test.ts
Error: Cannot find module './run' ...
```

Green after `src/run/commands.ts` and `src/run/run.ts`: 16 + 17 = 33
passed. Two of my own cases were wrong when first run and were corrected
against the producer, not around it:

- `expected [ -0, -1, ... ] to deeply equal [ +0, -1, ... ]` — an integer
  rate's first tick. `math.trunc` returns a Python **int**, which has no
  signed zero; `Math.trunc(-0.7)` is `-0`. Fixed in the engine (a `whole`
  helper in `jumps.ts` and the same normalisation in `commands.ts`), not
  in the test.
- `expected 0 to be greater than 0` — my crossing-and-stop bench put the
  bound below the first fold, so the stop happened before any surface was
  crossed. The bench now bounds at 1.5, where the fold at `t = 1/3`
  precedes the stop at `t = 0.5`.

## 8.2 — the corpus, green

```
✓ src/run/running-corpus.test.ts (16 tests)
  the running corpus > is the framework's own fixture, unedited
  ... replays Train at dt=0.05 (scenario 1)      [30 ticks]
  ... replays Train at dt=0.1 (scenario 2)       [20 ticks]
  ... replays Window at dt=0.05 (scenario 3)     [24 ticks]
  ... replays Remainder at dt=0.05 (scenario 4)  [24 ticks]
  ... replays Wrapped at dt=0.05 (scenario 5)    [20 ticks]
  ... replays Throwing at dt=0.05 (scenario 6)   [20 ticks]
  ... replays Clutch at dt=0.05 (scenario 7)     [24 ticks]
  ... replays CarryLead at dt=0.05 (scenario 8)  [24 ticks]
  ... replays CarryLead at dt=0.1 (scenario 9)   [14 ticks]
  ... replays Ratchet at dt=0.05 (scenario 10)   [20 ticks]
  ... replays Swept at dt=0.01 (scenario 11)     [16 ticks]
  ... replays TwoStops at dt=0.05 (scenario 12)  [12 ticks]
  ... replays StopAndJump at dt=0.05 (scenario 13) [12 ticks]
  the corpus's width > exercises every feature ... / is refused when narrowed
```

Thirteen scenarios, 260 ticks, every one compared: exact for the tick
number, statuses, coordinate/relation/primitive/bound/input names,
crossing levels and every list's order; `1e-9` relative (the fixture's
own `tolerance.float`) for banks, fractions, admitted travel and stop
values. **No tolerance was widened, no scenario skipped and the fixture
was not touched.** It passed on the first run of the engine.

That it is not a vacuous pass was checked by deliberate perturbation and
reverted:

```
# + 1e-7 on a law's increment
→ Train at dt=0.05, tick 1, bank first.turn: expected 4 within 1e-9
  relative, got 4.0000001
→ CarryLead at dt=0.05, tick 1, bank tens.turn: expected 35.5 ..., got
  35.500000099999994
→ Ratchet at dt=0.05, tick 1, bank wheel.turn: expected 42.5 ..., got
  42.5000001
```

Three perturbations were NOT caught, which is a property of the committed
corpus rather than of this engine, and is reported as a finding: a
`wiring`'s factor, a forward `formula`'s accumulation, the searched jump
bisection and both non-linear stop localizations (`piecewise`,
`searched`) are never reached by any of the thirteen scenarios. See
"Findings" below. Each is covered instead by this package's own unit
tests (`edges.test.ts`, `jumps.test.ts`, `run.test.ts`), and the
`run.test.ts` searched-localization case was verified to bite by the same
method (`expected 0.51 to be close to 0.5`).

## 8.3 — the cost of a tick

`src/run/cost.test.ts`, on this bench (node 22, one core):

```
  CarryLead, affine plans:            20000 ticks in 0.226 s =  88356 ticks/s
  CarryLead, plans forced to search:   1000 ticks in 0.076 s =  13242 ticks/s
  the Pascaline at dt = 1/240:         2400 ticks in 0.097 s =  24623 ticks/s
```

Real time at `dt = 1/240` is 240 ticks a second, so the acceptance
machine runs at about a hundred times real time on one thread and a
searched plan costs about seven times a solved one. The test asserts
floors an order of magnitude below each, so it catches a tenfold
regression and never a slow machine.

## 9.1 / 9.2 RED — the document admits version 5

Ten red in `src/document.test.ts` before `viewer.ts` changed:

```
× ... refuses a version it does not render, naming it and the ones it does
  → expected to throw error matching /1, 2, 3, 4, 5/ but got
    '/m.json declares document version 6, …'
× ... renders version 5 and says so in its list
  → expected undefined to deeply equal [ 1, 2, 3, 4, 5 ]
× ... accepts a version 5 document and hands back its loaded program
  → /m.json declares document version 5, which this viewer does not
    render; it renders versions 1, 2, 3, 4.
× ... hands back no program for a document that carries none
  → expected undefined to be null
× ... refuses a version 5 document with no program at all
× ... refuses a malformed program by the loader's own messages
× ... admits the clock, a coordinate and a computed value as names
× ... admits a plan's placeholder inside that plan, and nowhere else
× ... still refuses a name that is none of those
× ... refuses a pose that reads a computed value no edge determines
```

Only ONE pre-existing case was edited, and deliberately (task 9.1): the
version-refusal case, whose named version moves from 5 to 6 exactly as it
moved from 4 to 5 when version 4 became readable. Every other case in the
file — the bindings-table refusals, the undeclared-driver refusal, the
flexible refusals, `mountRetained` — is untouched and passes.

## 10.1 / 10.2 RED — the protocol and the runtime

```
FAIL  src/run/protocol.test.ts    Cannot find module './protocol'
FAIL  src/run/runtime.test.ts     Cannot find module './runtime'
```

Green: 7 + 8 = 15. Three of my own runtime expectations were wrong when
first run and were corrected in the ENGINE, not around it:

- `expected [] to have a length of 1` — I expected an advance asking for
  zero ticks. Sending nothing until a whole tick is earned is the
  behaviour D2 actually wants (a frame that earns no tick costs no round
  trip), so the test now says that.
- `expected 0 to be greater than 0` at speed x0.1 — a genuine bug: I had
  capped the accumulated DEBT rather than the ticks per advance, so a
  slow speed never accumulated a whole tick and the run stalled forever.
  D9 caps the TICKS ("`ticks` per advance is capped at
  `4 × speed × frameBudget / dt`"); the remainder is carried and the wall
  time beyond the cap is lost. Fixed in `runtime.ts`.
- `Test timed out in 5000ms` — a genuine bug: a `trigger` issues one
  command per input it moves and the main thread cannot know how many, so
  its promise never settled. The worker now posts an `issued` reply
  naming the handles it created, before any of them can retire.

## 11.4 / 11.5 RED — the run's mount option

```
× resolveOptions: the run > defaults to 1/240 s, a 600-tick record, and
  NOT started
  → expected undefined to deeply equal { dt: 0.004166666666666667, …(2) }
× ... takes a step size the host chooses, once
  → Cannot read properties of undefined (reading 'dt')
× ... refuses a non-finite or non-positive step size, naming the value
  → expected [Function] to throw an error
× ... takes a record length, and none at all
```

## 11.1 RED — posing from a bank

```
FAIL  src/run/pose.test.ts    Cannot find module './pose'
```

Green: 6 passed, including the bounded re-evaluation — a part whose
expression names only an idle coordinate keeps the matrix it had.

## 12.1 RED — the two declarations

With `package.json` still at `solidNodeViewerApi: 7` and no
`solidNodeDocumentVersions`:

```
× API_VERSION > declares the run-in-the-worker API as version 8
  → expected 7 to be 8
× DOCUMENT_VERSIONS > is declared in package.json, where a Python caller
  can read it            → expected false to be true
× DOCUMENT_VERSIONS > is the list the package declares, not a second copy
  → DOCUMENT_VERSIONS is not iterable
× DOCUMENT_VERSIONS > is exactly what the loader refuses by
  → DOCUMENT_VERSIONS is not iterable
```

## 12.2 RED — the Python entry point

```
FAILED tests/test_bundle.py::…::test_declares_the_document_versions_this_build_reads
FAILED tests/test_bundle.py::…::test_api_version_is_read_from_the_package_declaration
FAILED tests/test_bundle.py::…::test_document_versions_fall_back_to_every_released_viewer
FAILED tests/test_bundle.py::…::test_describe_reports_absolute_existing_paths
FAILED tests/test_cli.py::ModuleEntryTest::…  KeyError: 'documentVersions'
```

## 10.4 — one published file, carrying the worker

```
$ npm run build
  dist/solid-widget.js  631.6kb     (545.3kb before this change)
$ ls dist/*.js | wc -l      -> 1
built bundle contains the worker's message loop ('onmessage')  -> yes
built bundle contains the injected document-version list        -> yes
```

`tests/test_bundle.py::test_the_bundle_carries_the_worker_and_is_one_file`
pins both.

## 13.1 to 13.3 — the acceptance, in a real browser

`tests/test_running_document.py`, on the committed fixture:

```
runsInWorker=True  wall=258 ms for 2400 ticks
tens.drum.turn=65.53999999999998
1 passed in 2.87s
```

- `run()` is not null and its `identity` is the document's
  (`62bb22d2…f2a33e68b4b`); `apiVersion` is 8; `dt` is 1/240.
- At rest, before any tick: `tens.drum.turn === 0`,
  `units.drum.turn === 0`, `tick === 0`.
- Ten `Add one`, each `step(240)` with its outcome awaited: `tick` 2400,
  `elapsed` 10.0 s, `units_entry` 10, `units.drum.turn` 360, and
  **`tens.drum.turn` 65.53999999999998**, inside `1e-9` relative of the
  framework's own CARRY_THROW of 65.54. Ten instructions retired
  `completed`, each admitting 1 digit.
- The run used the **worker** (`runsInWorker: true`), and the ten
  instructions took **258 ms of wall time for 2400 ticks** — about 9,300
  ticks a second through the message boundary and ten round trips,
  against real time of 240 ticks a second.
- The page logged no error and no console error.

### The two screenshots, inspected

`tests/_shots/pascaline-at-rest.png` and
`tests/_shots/pascaline-after-ten.png` (written by the test; the
directory is ignored, so the evidence is regenerated by running it).

Both show the same 800x600 dark frame: three brown slabs lying flat on a
diagonal — the base and lid stand-ins, scaled by the document's own
placements — and about forty small orange, blue and cream cubes strung
along that diagonal in three clusters, one per decimal column. That is
what the fixture IS: the module's real published document posing STAND-IN
unit cubes, which is why the machine looks like scattered dice rather
than a Pascaline. The lighting, the framing and the camera are identical
in both, because nothing about the mount changed between them.

What differs is small and in exactly the right place. Compared by
`ImageChops.difference`, 676 of 480,000 pixels changed, inside one
bounding box: `(283, 247)` to `(475, 305)` — the middle of the diagonal,
where the units column's carry cube and the tens column's drum cube sit.
The third cluster, down at the lower right, is pixel-identical, and so
are all three slabs. That is precisely the bank: `units.carry.turn` went
to -65.54 and `tens.drum.turn` to +65.54, while `hundreds.*` never moved
at all — and `units.drum.turn` reached exactly 360°, a whole revolution,
which is why the units drum cube is back where it started and contributes
nothing to the difference. A viewer that had failed to reach the geometry
would have produced two identical files.

## 14.1 — the whole suite

```
$ npm run typecheck        (solid_node_viewer/widget)     exit 0, no output
$ npm test
 Test Files  26 passed (26)
      Tests  482 passed (482)
$ npm run build
  dist/solid-widget.js  631.6kb

$ PYTHONPATH=<worktree> .venv/bin/python -m pytest -q
62 passed, 1 skipped
```

Widget: 14 files / 298 tests before, 26 files / 482 tests after. Every
pre-existing test passes unedited except the four the tasks name: the
version-refusal case in `document.test.ts` (5 -> 6), the API-version case
in `version.test.ts` (7 -> 8), the two `describe()` shape cases in
`tests/test_bundle.py` / `tests/test_cli.py`, and the e2e API-version
case. `src/drivers.test.ts` and `src/parity-fixture.test.ts` are
byte-identical to their baseline and pass.

Python: 1 failed / 38 passed / 20 skipped before, 62 passed / 1 skipped
after. The twenty `@needs_bundle` skips and the one CLI failure are gone
because `dist/solid-widget.js` now exists in this worktree. The one
remaining skip is `tests/test_server.py:170`, "development app not built
(npm run build)" — the React development app under
`solid_node_viewer/app/`, which this change does not touch and which this
worktree has never built.

## Findings for the framework side

Design §15 named three and resolved each on the viewer's side; all three
held in practice, and implementation found three more. None blocks this
change.

1. **`program.intermediates` lists ids no edge determines.** Confirmed on
   the acceptance document: `hundreds.stop.angle`, `hundreds.wheel`,
   `tens.stop.angle`, `tens.wheel`, `units.stop.angle`, `units.wheel` —
   six entries whose `sources` is the empty list and which appear in no
   edge's `needs` or `gives`. The Train machine of the corpus publishes a
   seventh, `wheel.turn`. **Resolved here** as the design proposed: they
   are accepted as declared names, and refused the moment an edge or a
   pose expression actually READS one (`uncomputedValues`, and the
   `document.test.ts` case "refuses a pose that reads a computed value no
   edge determines").

2. **A `bindings` entry may name a branch placeholder, which the ratified
   requirement does not describe.** Confirmed, and it is not theoretical:
   mounting the acceptance document refused it outright until the loader
   was widened —

   ```
   viewer.json has expressions naming undeclared drivers (_j0, _j1, _j2);
   its drivers table declares: hundreds.carry.turn, …
   ```

   Six of its fifty entries reach a placeholder: `_b33 = (360.0 * _j0)`,
   `_b34 = (units.drum.turn - _b33)` and the same pair for `_j1` and
   `_j2`. Not one of its 260 pose expressions reaches one. **Resolved
   here** as the design proposed: this viewer never evaluates the table
   forward, so an entry nothing reads is never evaluated; a placeholder
   is admitted inside a bindings entry and still refused in an operation,
   and `loadProgram` has already checked that each plan's own
   expressions, closed over the table, name only that plan's placeholders
   and that edge's sources. The framework-side follow-up the design
   proposes — widening that requirement's sentence and replacing its
   one-forward-pass conclusion with the lazy reading a consumer actually
   performs — still stands.

3. **`sign` differs at negative zero.** Confirmed against the shipped
   evaluator (`expected -0 to be +0`). **Resolved here**, with a red
   test, by taking the producer's own `(x > 0) - (x < 0)`. No framework
   change asked.

4. **The committed corpus exercises only `law` edges.** Every one of the
   thirteen scenarios' edges is a `law`: no `wiring`, no `formula` and no
   `check` appears anywhere in `tests/running-corpus.json`, although the
   generator's own docstring describes the Train machine as carrying "a
   wiring into a plain port" — that edge drives nothing in the bank, so
   `_reaching_the_bank` drops it before publication. Measured by
   perturbing this engine and watching the corpus stay green: a wiring's
   `source x factor` and a forward formula's accumulation can both be
   multiplied by `1.0000001` with all 260 ticks still passing. `REQUIRED`
   in the generator does not list them either, so the width guard cannot
   catch it. Covered here instead by `src/run/edges.test.ts`, which pins
   all four kinds directly, including the backward-solved formula and the
   accumulation order.

5. **Every published jump in the corpus is `affine: true`.** The searched
   crossing path — sample `subdivisions` points, bracket, bisect up to
   `bisection_rounds` — is therefore never reached by the corpus:
   `+ 1e-8` on the bisection midpoint leaves all 260 ticks green.
   Covered here by `src/run/jumps.test.ts` ("samples, brackets and
   bisects a level quantity that is NOT affine").

6. **No stop in the corpus is localized by anything but one division.**
   Both non-linear localizations — the piecewise solve inside a jump
   plan's cuts, and the sampled-and-bisected search behind a non-affine
   edge — can be perturbed by `1e-6` with the corpus still green.
   Covered here by `src/run/run.test.ts` ("maps a crossing back to the
   fraction of the TICK across a segment" reaches the piecewise solve,
   and "locates a stop behind a NON-affine edge by sampling and
   bisection" reaches the search; the latter was verified to bite,
   `expected 0.51 to be close to 0.5`).

Findings 4 to 6 are about the corpus's WIDTH, not about anything the
framework computes wrongly. They are worth the producer's attention
because the corpus is the only thing that makes the two runtimes one
algorithm, and three of this engine's paths are currently pinned by this
repository's own tests alone.

## Deviations from design.md

1. **The advance cap is on TICKS, not on the accumulated debt.** Design
   D9 says "`ticks` per advance is capped at `4 x speed x frameBudget /
   dt` (four frames' worth)", which is what is implemented; an earlier
   reading that capped the debt itself stalled a slow speed forever (see
   10.2 above). The remainder below one tick is carried; the wall time
   beyond the cap is lost, which is what D9 asks for.

2. **A command request is answered with an `issued` reply.** Design §2's
   protocol table lists `outcome`, `refusal` and `error` for the
   worker-to-main direction. A `trigger` creates one command per input it
   moves and the main thread cannot know how many, so its promise could
   never settle; the worker now names the handles it created, before any
   of them can retire. One message type more than the design's table,
   for a promise the design's §7 requires.

3. **The driver chrome is suppressed for a document carrying a program.**
   Design §11 says a version 5 document has "no nudge, no jog, no
   instruction button" in this change. The existing chrome would have
   drawn sliders over driver values that no longer pose anything (the
   bank does), so it is not built for such a document. Two lines in
   `rebuildDriverChrome`.

4. **The engine refuses a non-finite level quantity for every jump
   primitive**, where the producer refuses it explicitly only for
   `floor`, `ceil` and `%` and reaches the same refusal for the others
   through Python's `ZeroDivisionError`. JavaScript has no such error:
   `1 / 0` is `Infinity`. Refusing a non-finite level everywhere
   reproduces the producer for the cause that actually occurs (a divisor
   of zero) and is stricter only for an overflow no published law can
   reach. Recorded rather than hidden.

5. **The acceptance asserts the geometry through PIXELS rather than a
   world matrix.** Task 13.1 asks for the units drum mesh's world matrix.
   The mount handle exposes no matrix accessor and this change adds none
   (that would be host API, and §11 keeps this change's surface closed),
   so the test compares the rendered canvas at rest with the canvas after
   ten instructions — which can only differ if the bank reached the
   geometry — and the two inspected screenshots quantify where.

6. **The package version is bumped to 0.2.0.** The tasks ask for a
   `## 0.2.0 — unreleased` changelog section and a README row reading
   `0.2.0 | 8 | 1, 2, 3, 4, 5`, and `tests/test_version.py` pins
   `pyproject.toml`, `solid_node_viewer/__init__.py`, the widget's
   `package.json` and the changelog to one number. Bumping is what keeps
   those four agreeing about the build this tree makes. **Nothing is
   released**: both changelog sections still say unreleased, and nothing
   is published or pushed.

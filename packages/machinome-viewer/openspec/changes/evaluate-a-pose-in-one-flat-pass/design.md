## Context

`expressions.ts` interns every expression into one page-wide hash-consed graph (ADR-043) and evaluates it by `valueOf`: a node whose stamp is the current pass's returns its memo, otherwise `compute` recurses into its children, and a name goes through `resolveName` (`$t`, then `profileOverlap` when the scope carries profiles, then the scope's binding table, whose entry is walked into by `valueOf(root)` (ADR-044), then the driver map by `in`, then the OpenSCAD context, else `undefined`, with jokenizer's `readMember` for every further part). A pass is a set of scope values (`ensurePass`, `scopesEqual`), so one pose costs each distinct node it reaches once.

On the Enigma I page that is the whole graph: 518,888 of the 546,768 nodes depend on `operation.press` and about 507,000 on the press, the key, the stage and the three rotors together, so a moved key recomputes about 540,000 nodes, about 100 ms of script. The bindings are 214,278 small steps over `max`, `abs`, `sqrt`, `min`, arithmetic and 2,757 comparisons used as gates, with no ternary, `&&` or `||` (evidence file). The second prototype compiled the graph reached from the binding roots into a flat program, ran it before `WidgetTree.update` and `admit`, and let `valueOf` read it: 433,678 nodes covered, 419,864 entries over 14 inputs, compiled in about 310 ms, a run about 4.3 ms, no mismatch in 30.6 million comparisons. Its limits are the evidence file's: one document, one browser, single runs, a self-check that took a boolean as its number.

A census of every committed document the widget's suite reads (`tests/fixtures/**`, `clocked-corpus.json`, `running-corpus.json`, `time-drive-corpus.json`, `parity-fixture.json`, `run/*.json`), every string holding an operator or a parenthesis parsed with the bench's jokenizer during this proposal, found no ternary, no `&&`, `||`, `===` or `!==`, no index, no generic member, no string or boolean literal, and only unary `-`; it found `==` and `!=` (calculator, clocked and running corpora), `%`, the four comparisons, `^`, and calls of `abs`, `acos`, `asin`, `atan`, `atan2`, `ceil`, `cos`, `floor`, `max`, `min`, `sign`, `sin`, `sqrt`, `tan` and, in `run/profile-overlap-v13.json` (no table), `profileOverlap`.

What must stay true: every requirement of `viewer-package` about evaluation and its lifetime (two are restated by this change's delta, see Decision 10), ADR-043 and ADR-044 with their amendments, every refusal a pose makes today with the same message, and the numerical results of every committed corpus and fixture.

## Goals / Non-Goals

**Goals:**

- A pose of a large bound document computes its formulas in one flat pass, with every value it hands out identical (`Object.is`, type included) to the walk's, and the walk for everything the pass does not cover.
- The pass cannot throw, and every throw a pose makes today is made at the same point with the same message.
- A pose's work is proportional to what its moved inputs feed; a document with no table, or a small one, compiles nothing.
- Lifetime, memory and counts are stated, tested, and tied to the store's existing reclamation points.

**Non-Goals:**

- Generated code (`new Function`, `eval`) in any form; parsing; the graph's structure; what a document may contain; the framework's way of writing piecewise laws; the rebuild of flexible parts; the renderer; anything that lowers a part's resolution or sampling; any project's source.
- Routing the clocked machine's solving, a run's ticks, `PathValue`, `ExpressionPath` or validation through the pass (Decision 6).
- Reading the scope's `bindings` once per pass. The first prototype measured it apart, without a flat pass; with one, a binding name a pose reads is answered from the program and does not reach `resolveName`, so what it would save is not known and is not this change.
- Viewer API (stays 30) and document versions (stay 1 to 14): verified in `widget/package.json`. `src/widget.ts` exports nothing from `expressions.ts`.

## Decisions

### 1. What is compiled, and what is covered (point 1)

The unit is a binding table: the `ReadonlyMap<string, NodeId>` a scope carries as `bindings`, which `bindingTable().roots()` returns as one object per store generation. Its program is the part of the graph reached from its roots, in table order, by an iterative postorder (no recursion, so no depth limit), where a node's children are a unary's target, a binary's two operands, a call's arguments (the callee is examined, not walked), and, for a single-part name that is an entry of the table, that entry's root. A child found still on the stack (a cycle) leaves its parent uncovered; the loader refuses a table with a cycle, so this is a guard, not a case.

A node is **covered** when its kind is in the table below and every child is covered. Everything else stays with the walk, and so does everything above it.

| Node | Covered when | Flat value |
| --- | --- | --- |
| literal | its value is a number | that number |
| `$t` | the name has one part | `scope.time` |
| binding name | one part, an entry of the table, not `$t` or `profileOverlap` (which resolve first) | the root's slot itself: no entry, same value and kind. Every entry's own name node that exists in the store gets this slot, whether or not another entry reads it, so an operation that names an entry reads it without a resolution; the lookup uses the intern table's key and mints nothing |
| other name | its first part is not `$t`, not `profileOverlap`, not an entry; if it is `in` the OpenSCAD context (its prototype included, so `constructor` is), the context holds a number there (`PI`) | an **input**, read each run (Decision 4) |
| unary | operator `-` | `-1 * v` |
| binary | `+ - * / %` | the same operator on the two values |
| binary | `< <= > >= == !=` | the same comparison; kind boolean, held as 1 or 0 |
| call | callee a one-part name in the list below, not an entry of the table | the very function the context holds, called with the arguments in order |

The listed functions are the context's own `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `sign`, `ln`, `log`, `mod` and Math's `abs`, `ceil`, `exp`, `floor`, `max`, `min`, `pow`, `round`, `sqrt`, taken as the objects `context` holds at module load (`context` is module-private and written only there). Each applies ToNumber to every argument before anything else (the language's definition of every Math function; the wrappers do arithmetic or comparisons on theirs), never throws on numbers, returns a number and keeps no state. Every other name of the context stays with the walk: `random` (a new value per call: a program that skips unchanged entries would freeze it), any function a browser adds to `Math` (`sumPrecise` throws on a number), the remaining Math functions until a document needs them.

Not covered, and so walked exactly as today: `!`, `+` and `~`; `&&`, `||` (lazy on their right side); `===`, `!==`; `| ^ & << >> >>>`; a ternary (lazy on its untaken branch); a generic member, an index, an array, an object; a literal that is a string, a boolean or `null`; a multi-part name whose first part is `$t` or an entry; `profileOverlap` as a name or a callee; a call of anything not listed, including a function or a driver used as a callee; a name of the context whose value is a function (`max + 1`). None of the uncovered forms occurs in a committed document or in the Enigma's table except `profileOverlap` (no table).

### 2. Values, and why each covered value is the walk's (point 1)

A program holds one `Float64Array` of **slots** and one `Uint8Array` of kinds (number or boolean), fixed per slot at compile: a comparison is boolean, everything else is number. `valueOf` hands a covered node out as `slot !== 0` when its kind is boolean and as the double otherwise, so a walked parent, `evalExpr`, `evaluateExpression` and every other caller receive what they receive today, `true` or `false` included. No consumer needs to be argued about: `===` and `!==` in a walked parent, a colour condition, a value returned to a caller all see the boolean.

Inside the program an operand is a number or a boolean held as 1 or 0, and every covered operator gives the same result for `true`/`false` as for 1/0:

- `+ - * / %` and unary `-` (`-1 * v`, jokenizer's rule, verbatim): neither operand is a string or an object, so ToPrimitive leaves them and ToNumeric(`true`) is 1 and ToNumeric(`false`) is 0.
- `< <= > >=`: IsLessThan takes ToPrimitive, finds no string, and compares ToNumeric values.
- `== !=`: two booleans or two numbers compare by IsStrictlyEqual, which for 1/0 gives what it gives for `true`/`false`; a boolean against a number is IsLooselyEqual of ToNumber(boolean) and the number.
- a listed call: ToNumber of every argument first.

A `Float64Array` holds every double as it is: `-0` stays `-0`, `NaN` stays `NaN` (its payload is not observable to `Object.is`), 1 and 0 are exact. A literal's slot is written at compile. `$t` and inputs are read by the walk's own steps (Decision 4), and accepted only when they are numbers. A binding name shares its root's slot, so it is the root's value by construction. A listed call calls the same function object `resolveName` would return for its callee, because the callee cannot resolve to anything else: not `$t` or `profileOverlap` (not listed), not an entry (checked at compile, the table is fixed), not a driver (checked every run, Decision 4), and the context is not written after load. Every covered computation is a pure function of its slots, so an entry whose inputs did not change keeps a value equal to recomputing it.

### 3. Nothing the flat pass does can throw (point 2)

The walk is lazy and the pass is eager, so the pass is built to have no operation that can throw, and to stay out of every place the walk can:

| What throws in the walk | Where it stays |
| --- | --- |
| `in` on a truthy primitive owner (`readMember`): a dotted name over a number, a generic member | a multi-part `$t` or entry name and a generic member are not covered; a dotted input whose owner is a primitive makes the run decline (Decision 4) before any `in`, and the walk throws it |
| calling a value that is not a function | a covered call's callee is a listed function by Decisions 1 and 4; anything else is walked |
| a called function's own error: `profileOverlap`, a function that throws on numbers | not covered |
| `Unknown unary operator`, `Unknown binary operator` | the operator is not covered |
| anything under the untaken side of `&&`, `||` or a ternary | the node is not covered, so the walk decides what it visits; its covered children cannot throw |
| a scope getter: `scope.bindings` (`roots()`) | read once at the pose's start, where `ensurePass` already reads it for the pose's first `valueOf`; after load its preparations repeat parses that succeeded |
| the pose's own refusals on a value (`evaluated to NaN`, a non-composable transform, a colour condition) | unchanged: the values are the walk's |
| `RangeError` from the depth of the recursion | see below |

Covered operations are arithmetic, comparisons and listed calls on numbers, which do not throw. The compile and the run are therefore total by construction; a throw inside either is a defect or an allocation failure. It is caught, the table is marked unserved for the store generation, `flatPassMetrics().failures` counts it, and the pose continues on the walk. Outside the source-only self-check of Decision 10, a pose never throws from the pass, so every throw happens in the walk, at the point and with the message it has today. The parity proof asserts zero failures.

One difference is not a refusal: the recursive walk can exceed the engine's stack on a deep enough graph, an error whose depth depends on the browser and whose message the viewer does not own. A pose served by the pass reads covered nodes without recursing, so such a graph may pose where the walk overflowed. No committed document, and not the Enigma, overflows today.

### 4. Inputs and scopes (point 5)

An input is a name node (Decision 1). Each run reads every input of the program as `resolveName` would: the first part from the driver map when it is `in` it, else from the context, else `undefined`; then each further part as `readMember` does, except that a truthy owner that is not an object or a function **declines** instead of evaluating `in`. A nested driver map is therefore read through its owners exactly as the walk reads it, and an input set that differs from any earlier scope is read afresh each run. `$t` is `scope.time`.

A run is **two-phase**. First, with nothing written: every input is read into a scratch array and must be a number; `scope.time` must be a number when the program reads `$t`; and no listed callee name the program calls may be `in` the scope's driver map (a driver named `max` makes `resolveName` return it, and the walk then throws its own `TypeError`). If any check fails, the run **declines**: `flatPassMetrics().declined` counts it, nothing of the program changes, the pass is not served, and the walk computes every node of that pass as today. Only then are the changed inputs found (by `Object.is` against the values of the program's last completed run, so `-0` and `0` differ and `NaN` equals `NaN`), stored, and their segments run (Decision 5). The prototype wrote inputs before declining, so a later pass compared against values its program had never computed with and kept stale results; S8 of the tests is that case.

A scope missing one input declines the whole pass rather than the input's cone: no committed document or the Enigma is known to pose with a missing input, the parity proof counts declines per document, and a document that always declines is posed by the walk, correctly and as slowly as today.

The set of inputs a program depends on has no width limit: masks are arrays of 32-bit words sized to the program's input count (point 5's last case). An input read through the context (`PI`) is an input like any other and never changes unless a driver of that name appears.

### 5. Work in proportion to what moved (point 6)

At compile every covered node gets a **class**, the set of inputs it depends on: its own for an input, the union of its children's otherwise (structural, over both operands of everything covered), with class ids interned and unions memoized so compilation stays linear. Entries (one per covered node that computes: unary, binary, call; never a literal, an input or a binding name) are laid out in **segments**, one per class, the classes ordered by the number of inputs they hold and each segment keeping the postorder. A child's class is a subset of its parent's, so it lies in an earlier segment or earlier in the same one: the layout is a dependency order. A segment also stores its first entry, its end and its mask.

A run tests each segment's mask against the changed mask and runs the entries of those that meet it. The first run after a compile runs every segment, the class with no input included, which is never run again. A pose therefore costs the number of inputs, the number of segments, and the entries whose inputs moved: a flap frame on the Enigma runs the flap's segments and tests the others' masks, where the prototype tested 420,000 entry masks (1.4 ms). Prediction, resting on the evidence table's dependency counts and not on a count of the Enigma's classes: the run of a flap frame falls well below the prototype's 1.4 ms and a Press's run is not above its 4.3 ms. `flatPassMetrics()` reports segments and entries so the reviewer reads both on the page.

A table smaller than `FLAT_PASS.minimumBindings` entries (default 1,000; a knob value), or no table, compiles nothing: the pose is the walk, byte for byte the base's path apart from one comparison. The default keeps every small committed fixture (1 to 50 entries) and every corpus table on the walk in production and puts the source-timing Curta exports (4,227 to 9,809), the Voron-2 (232,347) and the Enigma (214,278) on the pass. The parity proof lowers it to 0.

The first pose of a table in a store generation pays its compile and a full run, inside that pose: on a mount, the `next.update(scope())` that follows `startRuntime`; on a republish, the `update` in the tree's reconcile or the `tree.update(scope())` after `settlement.installed()`; in both cases before the first picture of the document. Prediction, resting on the prototype's 310 ms for 419,864 entries, of which the binding names (up to 214,278) are not entries here (Decision 1): 0.2 to 0.4 s on the Enigma, added to a load measured in seconds.

### 6. Who enters it, and who reads it (point 3)

One function, `prepareFlatPass(scope)`, called first inside `WidgetTree.update`'s and `WidgetTree.admit`'s `withExpressions`. It reads `scope.bindings` once; returns at once without a table or below the minimum; otherwise calls `ensurePass(scope)`, returns if this pass is already served, finds or compiles the table's program, runs it, and on success records the program and the pass it serves.

`valueOf` is unchanged except for one test after the memo test: when the recorded pass is the current one and the node has a slot, it returns the slot's value. No other evaluator calls `prepareFlatPass`:

| Evaluator | Routed | Cost |
| --- | --- | --- |
| `WidgetTree.update`, `admit` (every pose: viewer, clocked pose hook, drawn frames, running poses), and inside them transforms, colour conditions, flexible parameters | yes | Decision 5 |
| `operationsMatrix` for part controls, `admitPresentation` in reconcile | no | the walk; a scope equal to a served pose's is the same pass and reads its slots, which are that pass's values |
| clocked solving and bounds (`clocked/bounds.ts`, `machine.ts`, `events.ts`, `commit.ts`, `document.ts`) | no | the walk, one integer comparison more per memo miss |
| a running program's ticks: `evaluateExpression` (a fresh scope per call), `kinkLevel`, `run/jumps.ts`, `trajectory.ts`, `edges.ts` | no | same |
| `PathValue`, `ExpressionPath` | no | they do not call `valueOf`; unchanged |
| validation (`assertRenderable`, `inspectProfileExpression`, `freeVariables`) | no | unchanged |

They evaluate few nodes under many scopes, where a run would cost its input reads and segment tests per scope on top of the nodes, so none is routed. `src/run/cost.test.ts` and `src/clocked/cost.test.ts` pose no tree: the only change on their path is the comparison in `valueOf`'s miss path, false whenever no pose has been served in the pass. Prediction: within their noise; tasks 5.3 runs both files on the base and on the implementation and records their figures.

`prepareFlatPass` calls `ensurePass` even for a pose that then evaluates nothing (an empty change set), where today such a pose does not move the pass; a later call under the previous scope then recomputes what it would have read from the memo. Only a resolution count of that later call can tell.

### 7. Lifetime (point 4)

Programs live in a `WeakMap` keyed by the table's map object, created and replaced by `resetStore()` together with every other node-keyed array (ADR-043, D8); `resetStore()` also forgets the served program and pass. A program records the store generation and the node count at its compile.

- **A store reset** (a load's start, a refused load's end, a settlement, any viewer's disposal and the last one's, and `EXPRESSION_LIMITS.everyOperation` in tests) drops every program. No program or slot index survives it, so a node id reused after it cannot reach an old value. A table re-prepares its roots after a reset into a new map, which compiles anew at its first pose.
- **Nodes interned after a compile** have ids at or above the recorded node count and no slot. They cannot be reached from the compiled roots, because a node's children exist before it and never change.
- **Two documents on one page, operated alternately:** two tables, two programs, both retained; no recompilation on a switch. Each run compares inputs with its own program's last run, so a switch costs what moved since that document's last pose. Pass equality includes the table (D3), so a slot is never read under another table's pass.
- **A republish** builds a new `bindingTable`, so a new map and a new program at its first pose, the same table content or not. The old program goes with the old map, or at the next reset, whichever comes first; a load of a store above 125,000 nodes starts with a reset.
- **The last viewer's disposal** resets the store: nothing remains.
- **`everyOperation`**: every outermost operation resets, so every pose compiles. Test-only.

Nothing outside `expressions.ts` holds a program, a slot or a class; no reference crosses an operation except through a table, which already re-prepares by generation.

### 8. Memory (point 7)

Per program: a slot index by node id (`Int32Array`, the store's node count at compile), the slots (`Float64Array`) and their kinds (`Uint8Array`), per entry an operator code (`Uint8Array`) and two operand slots (`Int32Array` each), an argument pool for calls of more than two arguments, the inputs with their parts, the segments with their masks, and the listed callee names. Compile temporaries (class per node, the postorder, the class table and union memo) are released when the compile returns.

Prediction for the Enigma, resting on the prototype's counts (546,768 nodes, 433,678 covered, 419,864 entries over 14 inputs) and on the assumption that most of the 214,278 binding names were among its entries, which here share their root's slot: about 200,000 to 420,000 entries and slots; about 2.2 MB of slot index, 1.8 to 3.4 MB of slots, 0.2 to 0.4 MB of kinds, 1.8 to 3.8 MB of entries; 6 to 10 MB per program, beside a store of 115.6 MB resident (ADR-043's reclamation-point amendment). Two alternating documents hold two. It is released at the next store reset or when its table is no longer reachable.

### 9. Counted work and the existing tests (point 8)

`expressionMetrics().resolutions` keeps its definition: values computed by the recursive walk. A covered node read from a served pass costs no resolution; the pose's resolutions are the uncovered nodes it computes. `flatPassMetrics()` returns `compiles`, `runs`, `declined`, `failures`, `entries` (entries computed by runs), `compared` (values checked by `FLAT_PASS.verify`), and the last compiled program's `programEntries`, `segments` and `inputs`; `resetExpressionMetrics()` zeroes its counters. The work a pose performs is `resolutions` plus `entries`. Neither is on the mount handle.

Every test that asserts a resolution count calls `evalExpr`, `valueOf`, `evaluateExpression` or `PathValue` directly and poses no tree: `expressions.test.ts` (D6/D9 counts, pass detection, binding work, the binding map in the pass, `PathValue`), `evaluator.test.ts` (one pass for two operations), `run/jumps.test.ts` (274), `run/cost.test.ts`, `run/run.test.ts`, `run/kink-probe-cache.test.ts`. None of them enters the pass, so each holds as written and `resolutions` means there what it means today. The tests that pose trees under pressure (`expression-reuse.test.ts`, `expression-lifetime.test.ts`, `validation-pressure.test.ts`, `document.test.ts`) assert node counts, peaks, generations and binding preparations; the pass mints no node and prepares nothing. One may see one more binding preparation: a pose that evaluates nothing after a reset now reads `scope.bindings`; the applier reports such a test rather than changing it. Their large wide tables cross the default minimum, so they now also compile; under `everyOperation` that is one compile per pose.

### 10. Self-check, parity proof, spec and records (point 9)

`FLAT_PASS.verify` (source-only, false by default): after a run, every covered node is evaluated by the walk with slot reads suspended and compared with its slot's handed-out value by `Object.is`; a difference throws naming the node, its kind and operator and both values. The walk of a covered node visits only covered nodes and inputs the run has just read, so it cannot throw.

The parity proof, `src/flat-pass-parity.test.ts`, sets the minimum to 0 and the switch on, and for every committed document with a table poses what the document poses: `tests/fixtures/` calculator, lock, touched, pascaline, carriage, clearing, astrarium, pose-admission, direct-motion/columns and the four source-timing exports; the 17 tables of the clocked corpus, the 18 of the running corpus, the time-drive corpus and `run/follow-wrapped-v12.json`; and the parity fixture's cases through its table. A clocked document is driven by `clockedMachine` with a `pose` hook that poses every bank it commits by `clockedScope`, over the corpus script or every declared instruction; a running one by `Engine` tick by tick, posing `poseScope` of each state; a posed one at its defaults, its range ends and a seeded sweep; the parity cases at their own scopes. At every pose it also evaluates every operation, flexible parameter and colour condition of the document by `evalExpr` with the pass served and again under an equal scope with the pass off, and compares them by `Object.is`. Per document it asserts at least one compile and one run, no failure, `compared` above zero, and reports `declined`; a document with a table that never runs is a finding to report, not a test to relax. Of point 1's constructs these documents carry comparisons, `==`, `!=`, `%`, `^` and `sign` at `-0` (the parity fixture); none carries a ternary, `&&`, `||`, `===`, `!==`, a generic member or index read, a non-numeric literal, an undefined name, an owner map or function as a value, `profileOverlap` in a table, or a driver named like a function. Those are proved only by the edge tests. The state-colour fixtures carry no table and prove only that nothing compiles.

Spec: "A repeated subexpression is evaluated once per pass" and "A named binding is resolved where it is used" are restated with every scenario. The second says "An entry SHALL be evaluated only when something reads it", and its scenario "An entry nobody reads costs nothing" expects an entry no operation reaches not to be evaluated when its driver moves. A flat pass computes a covered entry whenever an input it reads moves, whether or not the pose reads it, so the requirement is qualified for poses served by the pass: such an evaluation never throws, changes no value and is counted apart. A new requirement, "A pose evaluates a large document's formulas in one flat pass", carries the rest.

Records: ADR-044's consequence "an entry is evaluated only when something reads it" gets a pointer amendment, and ADR-043 a dated amendment, after the reviewer's measurement.

## Tests

In `src/flat-pass.test.ts` (new), each its own test. Unless a test says otherwise it sets `FLAT_PASS.minimumBindings` to 0 in a `beforeEach` that tolerates the export's absence, so the base reaches the assertion, and builds its scope by hand with `bindings` from `bindingTable` or a `Map`. "Served" is asserted through the probe `flatPassServes(id)` and `flatPassMetrics()`; on the base both are absent and the test fails at the call. The value assertions hold on the base by construction (the base is the reference); what makes them bite is the mutations of tasks 4.2.

- **Work.** W1, through `WidgetTree.update` on a document of 1,200 entries (above the default minimum, no limit set): a balanced tree of sums whose leaves read `a` (depth about ten, so the walk stays far from the stack) and one entry over `b`, the operation adding the tree's root and that entry; after a first pose, a pose moving only `b` performs at most four resolutions plus entries (the operation's sum and its literal, and `(b + 1)`), where the base performs 3,004 resolutions (measured on this bench during the proposal); red on the base on the resolution count. W2: a new scope object with equal values computes nothing. W3: the first pose after a compile computes every entry once and the class with no input is not computed again. W4: two independent inputs, each moved alone, compute only their own segments.
- **Exactness.** E1 a comparison read by a walked `=== true` and E2 by `!== false` give the walk's booleans; E3 `(c + c)`, `(c == 1)` and `max(c, 0)` over a comparison `c`; E4 `-0` through unary minus of a zero input, `sign(-0)`, `1 / -0`; E5 `NaN` through `sqrt(-1)`, compared, and an input that stays `NaN` across passes; E6 `(a && t)` and `(a || t)` where `t` calls a driver as a function: not covered, no throw while the walk does not reach `t`, the walk's `TypeError` when it does; E7 a ternary whose untaken branch would throw; E8 a generic member and an index; E9 a name nothing resolves; E10 an owner map used as a value; E11 a context function used as a value (`max + 1`); E12 `profileOverlap` in an entry with profiles in the scope; E13 `random()` in an entry: not covered, a new value each pass as on the base; E14 a call of an unlisted function (`hypot`); E15 a string, a boolean and `null` literal; E16 a pose refused for a non-finite transform with the base's message.
- **Scopes.** S1 an input missing; S2 an input that is a string, a boolean, an owner map; S3 a dotted input over a truthy number: the run declines and the pose throws the walk's `TypeError`; S4 a nested driver map; S5 `$t`; S6 a driver named `max` beside `max(a, 1)`: declined, the walk's `TypeError`; S7 seventy inputs, moving the sixty-fifth computes only its cone; S8 a pass declined between two served ones leaves nothing stale; S9 an extra driver nothing reads does not decline.
- **Lifetime.** L1 a reset between poses recompiles, with node ids reused for different nodes; L2 two tables binding one name to different roots, posed alternately six times: two compiles, each its own values; L3 a node interned after the compile reads covered values; L4 the last release drops the program; L5 `everyOperation` compiles at every pose with the values unchanged and the generation risen; L6 a table below the minimum and a scope with no table compile nothing.

In `src/tree.test.ts`: T1 `update` and `admit` each serve a pose (runs rise, one compile across both); T2 a pose evaluating no operation still leaves the matrices the base leaves.

`src/flat-pass-parity.test.ts` as Decision 10.

## Departures from the prototype

- Booleans leave the program as booleans; the prototype handed out 1 or 0, which a walked `===` reads differently, and its self-check converted the walk's boolean to a number before comparing, so it could not see it.
- `&&`, `||`, unary `+` and `!` stay with the walk: no committed document or the Enigma carries them, and the first two are lazy.
- Calls are limited to twenty named total, pure functions; the prototype took any context function, which freezes `random` after its first run and would call a browser's `Math.sumPrecise` eagerly.
- A driver named like a called function is checked every run; the prototype checked the compile scope only.
- Inputs are classified by the table and the context, not by the compile scope's drivers, and read by `resolveName`'s own steps every run.
- A declined run writes nothing; the prototype's wrote the inputs it had read and left stale values for the next pass.
- Binding names share their root's slot instead of copying it; segments by class replace a test of every entry's mask; masks have no width limit where the prototype saturated to "all" past 64 inputs.
- One program per table is retained; the prototype compiled again whenever the table changed, so two alternating documents would recompile at every switch.
- Small and absent tables compile nothing; a compile or run failure falls back to the walk; validity is a pass number cleared by `resetStore`; reading the scope's bindings once per pass, on by default in the prototype, is not part of this change.

## Alternatives considered

- **Generated code.** Out of scope, and refused under a strict Content-Security-Policy (ADR-043).
- **Keep a value whose inputs did not change, inside the walk** (prototype 1). Measured: correct, and slower on the Enigma, because almost every node depends on what moves.
- **Test every entry's mask** (prototype 2 as it is). Pays for the whole program on every pose: 1.4 ms to find a flap's twenty entries.
- **A list of entries per input.** Memory is the sum of the cones, which on the Enigma is several times the program (about seven inputs feed about 507,000 nodes each), and a pose moving several inputs must merge them.
- **Compile from the tree's own expressions rather than the table.** A program per tree that changes on every republish, and it would not make "evaluated only when something reads it" hold either: a pose re-evaluates only the operations its change set touches, while a moved input's cone is computed whatever the change set says.
- **Cover `&&`, `||` and the ternary eagerly.** Exact under Decision 3's totality, since an untaken covered side cannot throw; but nothing carries them, and it would put an eager evaluation of an untaken side into every pose of such a document.
- **Hand booleans out as 1 or 0 and prove no consumer can tell.** A walked `===` can; the kind array is cheaper than the proof.
- **Route ticks, clocked solving and path values through a program.** They evaluate few nodes under many scopes; a run per scope adds input reads and segment tests to the same nodes.
- **Decline only the cone of a missing input.** No evidence of a scope that lacks an input; it adds a per-slot class read to every flat read.
- **Compile at the second pose of a table.** Moves the compile from the load to the first key press.

## Risks / Trade-offs

- [The pass computes entries a pose does not read, when their inputs move] → bounded by the program; counted; the spec says so.
- [A deep graph that overflowed the walk's stack may now pose] → stated in Decision 3; not a refusal the viewer makes.
- [A document whose scopes always lack an input never gets the pass] → correct and as slow as today; the parity proof reports declines per document.
- [6 to 10 MB per large table, predicted] → released with the store; the reviewer reads the heap on the Enigma.
- [The first pose of a large table pays a compile, predicted 0.2 to 0.4 s on the Enigma] → inside the load, before its first picture.
- [A second numeric path to hold in parity with the walk] → the walk stays the reference: every covered kind is argued from its source, the self-check compares every value, and the parity proof runs every committed document through both.

## Open Questions

- Whether the qualification of "An entry SHALL be evaluated only when something reads it" for poses is acceptable as a reviewed spec change or is the pilot's to accept.

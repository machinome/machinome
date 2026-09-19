# Evidence: bounds-read-other-coordinates

Every command below is run from the cycle worktree
`solid-node/WTs/bounds-read-other-coordinates` with

    PYTHONPATH="$PWD" .venv/bin/python -m pytest <files> -q

against the workspace venv at `/home/asa/devel/libresolid-studio/.venv`.

## Baseline at the planning commit (dbb0740)

    tests/test_running_stops.py tests/test_running_simulation.py
    tests/test_running_jumps.py tests/test_running_document.py
    tests/test_running_corpus.py tests/test_joints.py
    -> 342 passed, 1 skipped, 3 warnings, 701 subtests passed in 31.30s

The one skip is `DeferredBoundTest` (`tests/test_running_stops.py:584`),
ADR-109's pinned deferral, which this cycle replaces.

## Task group 1: the declaration and the untimed reading -- RED

### 1.4 `Bound` does not exist

With the fixtures of 1.1 added to `tests/running_project/machine.py`
(and the `Pin` leaf to `tests/running_project/parts.py`), the whole
fixture module refuses to import:

    tests/running_project/machine.py:40: in <module>
        from solid_node.motion.joints import Bound, Free, Prismatic, Revolute
    E   ImportError: cannot import name 'Bound' from
        'solid_node.motion.joints'
    ERROR tests/test_running_stops.py
    !!!! Interrupted: 1 error during collection !!!!
    1 error in 0.28s

## Task group 2: declaration, resolution, enumeration-close judgement -- GREEN

    tests/test_joints.py -> 166 passed, 255 subtests passed in 4.03s

The six-file set plus `tests/test_couplings.py`:

    -> 530 passed, 1 skipped, 3 warnings, 875 subtests passed in 32.29s

The remaining skip is still `DeferredBoundTest`, replaced in group 3.

Two fixture facts found while implementing and recorded here:

- task 1.1 states the pins as `p1 = Slide(lift=Prismatic(...))`. A site
  joint under a NEW name ADDS a coordinate rather than replacing
  `Slide.travel`, so such a pin carries an undriven `travel` and
  `Sim` refuses the machine at construction ("the rest render leaves
  p1.travel unbound"). The fixtures therefore use a new `Pin` leaf in
  `tests/running_project/parts.py` declaring `lift` alone -- which is
  also the shape both delta specs name (`p1 = Pin()`).
- the "read the bounded coordinate itself" refusal cannot be written as
  a joint's own `range=` in one statement (the joint is not in scope
  while its own arguments are evaluated), so the test states it as
  `spin.range = (0, Bound(..., reads=(spin,)))` on the next line of the
  same body, which is the same class-definition moment.

## Task group 3: the running reading -- RED

    tests/test_running_stops.py
    -> 18 failed, 36 passed, 25 subtests passed in 2.57s

Every constraint test fails at `Sim` construction, in the compiler, by
the very refusal this change removes:

    solid_node.simulation.program.UnsupportedLaw: Arbor.turn: its upper
    bound -- the range of the coordinate 'plug.turn' -- resolved to
    <Bound a bound reading (p1.lift, p2.lift)>, which is neither a
    number nor a callable of the joint's own coordinate.

`DeferredBoundTest.test_a_bound_may_name_a_second_coordinate` -- the
skip ADR-109 left pinned open, now a real test -- fails the same way,
and the `Train` cost probe fails because it has no number yet
(`80 != 40`, the placeholder; the measured figure is recorded below).

Two fixture renames forced by an existing framework rule, recorded as a
finding rather than worked around silently: `set_state` records a joint
COORDINATE's id under its bare name beside the drivers, so a running
root declaring a driver `turn` while a child declares a joint `turn`
makes the bare name ambiguous and `Sim` construction fails with

    ValueError: ambiguous driver name in set_state: 'turn' could mean
    plug.turn, turn.

The simulation delta names the plug's input `turn` and the pawl's
`lift`; the export delta names the published id `plug.turn`. The
published ids are the half the corpus and the viewer are held to, so the
fixtures keep `plug.turn` and `pawl.lift` and rename the INPUTS to
`twist` and `hoist`. The pin tumbler lock's own migration (group 6) has
the same collision between its `turn` driver and `plug.turn`.

## Task group 4: compile and run -- GREEN

    tests/test_running_stops.py tests/test_running_simulation.py
    tests/test_running_jumps.py tests/test_running_document.py
    tests/test_running_corpus.py tests/test_joints.py
    -> 371 passed, 3 warnings, 705 subtests passed in 32.40s

No skips remain: `DeferredBoundTest` is a real test now.

### Measurements

Both probes evaluate `solid_node.simulation.program._evaluated` through
a counting wrapper and take the best of several timed runs on this
machine. The BASE figures come from the base commit 33d8bf5, unpacked
read-only with `git archive` into a scratch directory and probed there
with the identical script, so the comparison is producer to producer.

`Train` -- a machine declaring no bound that reads other coordinates:

| probe                          | base 33d8bf5 | this change |
|--------------------------------|--------------|-------------|
| graph evaluations over 10 ticks| 80           | 80          |
| ms/tick (best of 5 x 1000)     | 0.4383       | 0.4387      |

The deterministic count is unchanged, exactly. The wall time is 0.1%
apart, well inside noise, and both are comfortably under ADR-108's
recorded 1.065 ms/tick -- that figure was taken on different hardware;
what this cycle is answerable for is that the number does not MOVE, and
it does not.

`Gate` -- the two-pin constraint machine, whose plug's bound reads two
coordinates and whose sub-program is four edges:

| tick                                        | ms/tick | graph evals |
|---------------------------------------------|---------|-------------|
| quiet (nothing the bound depends on moves)  | 0.3601  | 8           |
| active (`feed` moves, nothing stops)        | 5.3845  | 528         |
| blocking (the plug is stopped at `t* = 0`)  | 3.3203  | 328         |

A quiet tick pays exactly what the machine paid before the constraint
existed: the level is not evaluated at all. An active tick pays the
sampled search -- 65 level samples over a four-edge sub-program, 8 graph
evaluations each -- whether or not it stops; that is design.md decision
9's stated price for looking inside the stretch. A blocking tick pays
fewer, because the search stops at the first sample carried outward
(here the first of the 64) and then bisects; its 328 evaluations are 40
levels plus the tick's own pass.

### The representative caller: the Pascaline module

Run from `projects/Calculators/Pascaline-module` with `PYTHONPATH`
leading with this worktree. Nothing in the project was edited; the only
writes were into its own ignored `_build/`.

    solid test --faceted simulation/test_pascaline.py
    -> Ran 37 tests in 81.65 seconds: 37 passed, 0 failed
       (faceted kernel, volume epsilon 0 mm3)

    solid build && pytest tests/test_document.py
    -> 3 passed, 6 subtests passed

The published program identity, before and after:

    b6c0543d4c901338d8ac290ffe685084771fd275f02bb7c170ad161d3c172504

which is the identity `docs/decimal-carry-correction.md` records. A
one-argument callable bound keeps its code path and its published span,
exactly as the migration plan says, and the module's own document test
still finds no second coordinate in any span.

## Task group 5: publication and the corpus

### 5.1 Publication -- RED at the group-3 point, GREEN now

`test_a_bound_reading_other_coordinates_names_them` and
`test_a_capture_bound_publishes_the_coordinate_it_reads` could not run
at all before group 4: publishing a `Gate` document means compiling its
program, which was refused by `UnsupportedLaw` above. With the compiler
in place they pass with no change to `published()` or
`_published_bound` -- design.md decision 7's claim that the span's shape
is unchanged, confirmed rather than asserted.

One factual slip in the ratified export delta, corrected in place (see
the cycle report): the scenario said the published expression's free
names ARE `plug.turn`, `plug.p1.lift` and `plug.p2.lift`. The fixture
the scenario itself states -- `lambda turn, a, b: 90 * (abs(a) <= 0.05)
* (abs(b) <= 0.05)` -- never mentions its own coordinate, so the graph's
free names are the two reads. What the compiler CHECKS is
`names <= {own} | reads`; what the graph CARRIES is what the author
wrote. The scenario and task 5.1 now say that.

### 5.3 The generator's two new refusals -- RED

    tests/test_running_corpus.py -k CoverageGuard
    -> 2 failed, 3 passed in 0.27s

    E AssertionError: 'a bound reading another coordinate' not found in
      [...]
    E AssertionError: 'a stop reached by the motion of what a bound
      reads' not found in ['a stop located inside a tick', 'a tick
      carrying both a crossing and a stop']

### 5.4-5.5 The regenerated corpus -- GREEN

    PYTHONPATH="$PWD" python tools/generate_running_corpus.py
    -> tests/running-corpus.json: 14 scenarios over 12 machines
       (Captured, CarryLead, Clutch, Ratchet, Remainder, StopAndJump,
        Swept, Throwing, Train, TwoStops, Window, Wrapped),
       276 ticks, 185576 bytes

    tests/test_running_corpus.py -> 8 passed, 42 subtests passed

The `Captured` scenario's own tick 6 is the second new feature, in the
fixture, by its own numbers:

    stops: [{'coordinate': 'key.travel', 'bound': 'low', 'value': 20.0,
             't': 0.0, 'inputs': ['feed']}]
    bank:  {'feed': 20.0, 'key.travel': 20.0, 'p1.lift': 0.0,
            'p2.lift': 0.0, 'plug.turn': 30.0, 'twist': 30.0}

-- a stop whose coordinate holds exactly the value it held before the
tick, because what carried the constraint outward was the key's own
withdrawal against a plug that stood turned.

## Whole suite

    tests/test_running_stops.py tests/test_running_simulation.py
    tests/test_running_jumps.py tests/test_running_document.py
    tests/test_running_corpus.py tests/test_joints.py
    -> 375 passed, 3 warnings, 710 subtests passed in 32.04s

    tests/
    -> 2546 passed, 4 skipped, 50 warnings, 1420 subtests passed
       in 374.28s

The four remaining skips are environmental and pre-existing: the
installed-viewer e2e photograph, the absent `jscad` CLI, and two vendor
STEP fixtures that are not checked out.

## Adversarial review before sync and archive (2026-09-14)

Probes run against the implemented worktree from a scratch package
(`probe_review.py`), beyond the ratified scenarios:

- a `rate` on the `twist` input while a pin crosses the shear line
  retires `blocked` with `0.0` admitted and releases the input;
- a snapshot taken before the reciprocal stop restores and replays the
  same stop (`key.travel`, `t = 0.0`, `('feed',)`) with the same admitted
  travel;
- standing at a constraint stop (the key at `17.950000000000728`, inside
  the window by the crossing tolerance): a further withdrawal is blocked
  at `t = 0` with `0` admitted, an insertion of `1.0` completes;
- a site joint whose `Bound` reads the DECLARING class's own joint (an
  `OwnRef`, `reads=(turn,)`): compiles, and the capture blocks at once;
- the untimed impossible pose (`twist=30, feed=0` on `GateBody`) is
  refused naming `plug.turn`, `30.0`, the evaluated bound and both reads.

Two gaps found and closed red-first:

1. **A `Bound` whose expression returns a NUMBER** was compiled to a
   float span AND registered as a constraint, so the first active tick
   raised `AttributeError: 'float' object has no attribute 'evaluate'`.
   Red: `test_a_bound_returning_a_number_is_refused_at_construction`
   → `AssertionError: ValueError not raised`. Fix: refused at
   construction — "declares reads=(p1.lift) and returns the number 45,
   so it never reads what it declares".
2. **A declared read the expression never uses** was accepted, giving a
   constraint sampled along every active tick for nothing. Red:
   `test_a_read_the_expression_never_uses_is_refused_at_construction`
   → `AssertionError: ValueError not raised`. Fix: refused at
   construction naming the unused read — "declares reads=(p1.lift,
   p2.lift) but its expression never reads p2.lift".

Also guarded: an unbound DRIVER read at the enumeration's close is
skipped like an unbound slot rather than raising `AttributeError` out
of `refuse_bounds`.

After the fixes: the six-file set → 377 passed, 710 subtests.

## The originating project

The pin tumbler lock
(`projects/Locks/Pin_tumbler_lock`, its own repository, its own OpenSpec change
`2026-09-14-run-the-lock`, archived) was migrated to `Time.running()` against
this worktree's working tree. Nothing is committed there; every command below
runs from the project directory with

    PYTHONPATH="<this worktree>:$PWD" .venv/bin/python ...

### What it declares

`Plug` declares its five key pins, then the turn that reads them, then the key
whose own travel reads the turn:

    turn = Revolute(
        axis=(0, 0, 1), unit="deg",
        range=(Bound(plug_limit(-1),
                     reads=(p1.lift, p2.lift, p3.lift, p4.lift, p5.lift)),
               Bound(plug_limit(1),
                     reads=(p1.lift, p2.lift, p3.lift, p4.lift, p5.lift))))

    key = Key(..., insert=Prismatic(
        axis=(0, 0, 1), unit="mm",
        range=(Bound(capture, reads=(turn,)), 0.0)))

with `plug_limit(sense)` returning `sense * 90 * clear(l1) * … * clear(l5)`,
`clear(l) = (l >= -0.15) * (l <= 0.05)`, and `capture(insert, turn) = -60 +
60 * (abs(turn) > 0)`. The SAME five reads on both sides of one pair are
accepted without comment, and so is a site joint's bound reading the declaring
class's own joint. Each key pin's lift is `piecewise(insert, knots)` over the
exact breakpoints of the project's own contact envelope (8 to 26 knots per pin,
agreeing with the reference to 1.24e-12 mm at 601 stations for each of four
keys). `tools/check.py` is green under `--faceted` and `--exact`: 7 + 1 + 24 +
2 + 3 solid tests and 4 unittests, 41 in all.

### Blocked positions and admitted travel (dt = 0.05 s)

| Asked | Answer |
|---|---|
| turn +90° at insertion −60, −40, −20, −10, −5, −1 mm | `blocked`, `0.0` admitted, `plug.turn` `high` `0.0` at `t = 0`, inputs `('rotation',)` |
| turn ±90° seated, too-deep key (pin 2 at −0.85) | `blocked`, `0.0` admitted, `plug.turn` at `0.0` |
| turn ±90° seated, too-shallow key (pin 2 at +0.65) | `blocked`, `0.0` admitted |
| turn +90° seated, matching key | `completed`, `90.0`; return `completed`, `-90.0`; no stop |
| withdraw 60 mm with the plug at 90° | `blocked`, `0.0` admitted, `plug.key.insert` `low` `0.0` at `t = 0`, inputs `('insertion',)` |

### The derived reciprocal

With the capture removed (`simulation/probes.py:UncapturedLock`, a subclass of
the plug declaring an ordinary `range=(-60.0, 0.0)` on the key), the same
withdrawal is still stopped, by the plug's own bound, with the plug standing:

    handle.status   'blocked'
    handle.admitted -0.23883259990270744
    plug.key.insert -0.23883259990270744
    plug.turn        90.0   (unmoved)
    stop             Stop(tick=1, coordinate='plug.turn', bound='high',
                          value=90.0, t=0.19106607992216595,
                          inputs=('insertion',))
    lifts            [0.04999835, 0.04999784, 0.04999701, 0.05, 0.04999875]

`t*` is exact: the project computes the crossing from its own committed knots
as `-0.23883259990277672` (pin 4's split reaching `+0.05`), and the run stops
`6.9e-14` mm inside it. At `dt = 0.025` the admitted travel and the committed
position are identical to twelve places and `t = 0.3821321598443319` of the
half-size tick — the same place, twice the fraction. Every pin is INSIDE the
window at the committed state, never outside.

### Spring limits reached by no legal key

`DriverPin.lift` declares `range=(-6.9, 6.1)` from the source's 24 mm free
length and 11 mm compressed reference through `height = 17.9 - lift`. The
refusal reads:

    pin: joint 'lift' declares the range -6.9 to 6.1 mm, and 6.11 is outside
    it. A range refuses the binding rather than clamping it, because a pose
    outside the joint's travel is a mistake in what drives it.

The observed driver envelope over all four prepared keys is −4.719873 to
+5.591003 mm, so no legal key comes within a millimetre of either limit; the
project keeps a one-pin stand (`DriverPinSample`) so the refusal can be seen at
all. Recorded in the project as a VISUALIZATION limit the source states, not
coil bind and not a material limit.

### Published spans and identity

`solid build` publishes a version 5 document, no `errors.json`, identity

    b45402a563493d03462a51b456059300c74c75c61f74bc206a7f38cc7746c867

with 16 coordinates, two inputs, five intermediates (`s1.height`…`s5.height`)
and the spans

    plug.turn        low  {"expression": "(((((-90.0 * _b10) * _b13) * _b16) * _b19) * _b22)"}
                     high {"expression": "(((((90.0 * _b10) * _b13) * _b16) * _b19) * _b22)"}
    plug.key.insert  low  {"expression": "(-60.0 - (-60.0 * (abs(plug.turn) > 0)))"}
                     high 0.0
    d1.lift … d5.lift     -6.9 to 6.1

The five reads reach the plug's bound through the document's binding table:
`_b10 = (_b8 * _b9)`, `_b8 = (plug.p1.lift >= -0.15)`,
`_b9 = (plug.p1.lift <= 0.05)`, and so on to `_b22` for pin 5. Checked against
the shipped viewer: `solid_node_viewer/widget/src/run/program.ts` ends its
program reader with `check(bound.expression, new Set([id]))` per span side, so
this document is refused BY NAME, as decision 8 says it should be.

### What a tick costs

`Sim` over the lock, `dt = 0.05` s, best of three, this machine:

| Tick | ms/tick |
|---|---:|
| nothing moves | 2.97 |
| the key advances (the bound's reads move) | 193.3 |
| the plug turns, seated (the bound's own coordinate moves) | 195.5 |
| a turn blocked at `t = 0` at −20 mm insertion | 8.1 |

An active tick is about 65 idle ticks, which is `_SUBDIVISIONS` samples each
costing about what a whole ordinary program pass costs. Decision 9 estimated
"on the order of 450 edge evaluations"; the lock's sub-program is far larger
than the five edges the design assumed, because the plug's bound reads the five
pin lifts and those are determined by five `piecewise` laws of 8 to 24 knots —
about 150 expression nodes each. Two observations for the cycle:

- the price is paid whenever the bound's OWN coordinate moves, even when
  nothing it reads is moving. Turning the seated plug re-evaluates all five
  lift laws 64 times per tick to learn what the last committed bank already
  says. A cheap pre-test — sample only what actually moves over the stretch —
  would make this the one case it is not;
- a blocking tick is CHEAP (8.1 ms), because `g(0) > 0` gives `t* = 0` before
  the search runs. The cost is entirely in ticks that do not stop.

### Framework findings

1. **The test runner's operation checkpoints double a leaf child's joint
   displacement under a running root.** `solid_node/manager/test.py:327`
   snapshots each ROOT CHILD's `operations` before every test and
   `:368`/`:383` restores them after; from the SECOND test on, the binding
   `node.set_keyframe(instant)` runs at `:344` appends the joint displacement a
   second time. The lock's five driver pins then stand 0.1 mm deeper than their
   own coordinate says (`d1.lift` reads `0.10000020307669977`, the mesh sits at
   `x = 12.46` instead of `12.56`), and nothing a test can call puts them back —
   `_prepare()`, `render()` and a `set_state` round trip all leave the fifth
   operation in place. Minimal reproduction, on the lock but not on the runner:

       a = load_node('simulation/lock.py:PinTumblerLock')
       a.set_keyframe(0); a._prepare(); a.build_stls()
       for _ in range(2):
           saved = {c: list(c.operations) for c in a.children}
           a.set_keyframe(0)
           for c, ops in saved.items(): c.operations[:] = list(ops)
       a.set_keyframe(0)          # -> d1 has 5 operations, not 4

   The SAME tree under the project's previous UNTIMED model does not do it
   (the driver pin keeps 4 operations through any number of cycles), so this is
   specific to a running root's binding. Children of a sub-assembly are
   unaffected, because the runner only checkpoints the root's own children.
   Cost to the project: `assertNoSolidInterference` failed with
   `core should not interfere with d2 (intersection volume 0.10313749602963482)`
   at ±90°, and the geometry tests now build a lock of their own, with the
   reason written where they build it.

2. **`solid build` refuses a coordinate bound by a CHILD-declared relation and
   read by a ROOT-declared one, as doubly bound.** With
   `key.insert.drives(p1.lift, law=…)` in `Plug`'s body and
   `plug.p1.lift.drives(d1.lift, ratio=-1)` in the root's, the symbolic
   publication pass (`core/serializer.py:240` → `qualified.py:311` →
   `couplings.py:1898`) raises

       DoublyBound: plug.p1.lift would be bound by the relation
       key.insert drives p1.lift and by the relation plug.p1.lift drives
       d1.lift. A coordinate has exactly one binder in one enumeration of the
       tree ...

   The second relation does not bind `plug.p1.lift`; it READS it. The message
   names a relation's SOURCE as a binder, which sent the project looking for a
   double binding that does not exist. Every untimed pose, every `Sim` and the
   whole test suite accept the same declarations; only the publication pass
   refuses them, evidently by solving the root's relation backwards.
   Worked around by declaring all five lift relations in the ROOT's body, which
   publishes.

3. **A `.repeat()` child's PORT cannot be published under a running root.**
   Decision 2 says "the springs stay `.repeat(5)`, because a port is not
   banked". A port is not banked, but it IS an intermediate of the published
   program, and `Program.published` refuses it:

       UnsupportedLaw: the program names 'PenSpring.height', which is a
       FALLBACK derived from a class name rather than an instance path: the
       node it belongs to is not linked under the root ... Hold the node on
       its own attribute of its parent.

   The lock's five springs therefore became `s1`…`s5` too, with a one-source
   law in place of the broadcast. The migration plan's second step should say
   so: under a running root, a repeated child is publishable only if it owns
   neither a joint nor a port that the program names.

4. **A running root's drivers are not bound by construction.**
   `PinTumblerLock().assemble()` raises `AttributeError: driver 'insertion' of
   PinTumblerLock is not bound; bind it with set_state(insertion=...)` even
   though the driver declares a default; a `Sim`, a `set_state` or the loader's
   `set_keyframe` is what applies it. Reasonable, and it cost one test a
   confusing failure; worth a sentence in the running spec.

5. **The naming clash decision 1 of the migration plan predicts is real, and
   its message is good.** With the root driver named `turn` beside the three
   joints called `turn`:

       ValueError: ambiguous driver name in set_state: 'turn' could mean
       plug.core.turn, plug.key.turn, plug.turn, turn. Address the instance
       you mean by its qualified id, e.g. set_state(**{'plug.core.turn': ...}).

   The input is named `rotation`.

6. **The reciprocal fires in both directions, which is right and worth
   noticing.** The capture `-60 + 60 * (abs(turn) > 0)` says a turned plug
   holds the key seated, so asking a PARTLY inserted lock to turn produces TWO
   stops — `plug.turn` `high` `0.0` and `plug.key.insert` `low` `-60.0`, both
   at `t = 0`, both naming `('rotation',)`. The turn is refused twice over by
   two statements that agree, which is exactly decision 4's "an input moving a
   read coordinate so as to make a STANDING position invalid is stopped".

## Review after the originating project (2026-09-14)

The lock's evidence above measured 193–195 ms on ANY active tick, the
seated plug's turning ticks included, although nothing the plug's bound
reads moves while it turns. Red-first in the framework:
`ConstraintCostTest.test_a_tick_moving_only_the_bounded_coordinate_is_not_sampled`
→ `assertLessEqual(turning, idle + 2)` failed. Fix (`Run._reached`): on a
stretch in which no READ of a constraint moves, the bound is the number
its expression gives at the tick's committed own value and the reads'
standing values, and the coordinate takes the exact self-only path —
solved, snapped, one evaluation. Semantically a special case of the
ratified rule (own committed, reads along a path on which they do not
move); recorded in the spec delta, ADR-113 and the architecture overview.

After the fix, six-file set → 378 passed, 710 subtests; the corpus
regenerates unchanged; the lock's running scenarios (`LockRunTest`,
`WrongKeyRunTest`) → 7 passed against the updated worktree, and the lock's
tick costs, best of three at `dt = 0.05`:

| Tick | before | after |
|---|---:|---:|
| nothing moves | 2.97 ms | 2.91 ms |
| the seated plug turns (own moves, reads static) | 195.5 ms | 4.68 ms |
| the key advances (reads move) | 193.3 ms | 44.9 ms |

The remaining cost of an insertion tick is the sampled search over five
`piecewise` laws, `f(start)` recomputed per sample; the follow-ups are in
`workflow/warts.md` under the lock's 2026-09-14 entry, with the runner
checkpoint, publication and `.repeat()`-port findings the lock surfaced.

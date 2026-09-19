## Context

The requirement and the project that owes it are in `proposal.md`. Four
records bind this design, and nothing here re-opens a decision any of them
took:

- **The ratified clocked discipline.** `openspec/changes/archive/2026-09-17-
  declare-the-state` (**ADR-125**), `.../2026-09-17-a-bound-stops-the-request`
  (**ADR-126**) and `.../2026-09-17-time-without-running` (**ADR-127**),
  together with the baseline specs they synced. They are AUTHORITY.
- **The version ladder.** **ADR-110** (EXPORT), and the three archived cycles
  that added rungs to it: `2026-09-13-publish-the-mechanical-program`
  (version 5), `2026-09-15-read-the-driven-coordinate` (version 6) and
  `2026-09-15-select-the-source` with `2026-09-16-pin-the-block-order`
  (version 7). Their rule is the one this cycle obeys: **a version is a
  property of the document, a bump is emitted only where the content or the
  root's declaration needs it, and a bump that is not additive must make a
  lower consumer REFUSE rather than render a wrong pose.**
- **The conformance-corpus pattern.** `2026-09-13-publish-the-mechanical-
  program`'s own corpus half (**ADR-111**'s pattern), as
  `tools/generate_running_corpus.py`, `tests/running-corpus.json` and
  `tests/test_running_corpus.py` implement it.
- **The requirement note**, `workflow/docs/clocked-machine.md`. SUPERSEDED
  history with four marked corrections; it is evidence, never authority.

One constraint stands above the rest: **nothing about document versions 5, 6
and 7, about `tests/running-corpus.json`, or about `Time.running()` moves.**
A running root cannot declare a `State` (refused where declared defaults are
bound), so `program` and `clocked` can never appear in one document, and the
two ladders never meet.

## Goals / Non-Goals

**Goals:**

1. A clocked machine has a document, and that document carries everything a
   second runtime needs to reach the SAME bank, the SAME events and the SAME
   stops the framework's own executor reaches.
2. A consumer that cannot read it refuses it by name rather than animating it
   wrongly — ADR-110's rule, which is the whole reason the gate exists.
3. A model that declares no `State` is unchanged in behaviour, in published
   bytes and in cost, structurally rather than hopefully.
4. Everything published is what COMPILE TIME decided. Nothing is published
   that a consumer can compute from what is already there, and nothing is
   left for a consumer to re-derive that the framework decided by refusing.

**Non-Goals:**

Listed in `proposal.md`; section 20 gives each its reason and the shape a
later cycle takes.

## Decisions

### 1. Version 8, and it is a property of the ROOT'S DECLARATION

A tree in which anything declares a `State` publishes `version: 8`, whatever
its tree content.

This is version 5's rung, not version 3's or 4's. `document_version`'s
docstring already draws that distinction
(`solid_node/core/serializer.py:446-484`): flexible leaves and shared
subexpressions are properties of the TREE and are read off the finished
document, while a compiled program is a property of the ROOT'S DECLARATION,
"and a running root with a trivial program is still a machine a version 4
consumer would animate wrongly". A clocked root with one state and no
flexible leaf is exactly that machine.

**Why it is not additive.** A clocked tree's pose expressions read its states
as FREE NAMES. That is not a proposal: it is what the producer does today,
verified on this worktree by serializing `tests/clocked_project/register.py`
with the gate bypassed — its three wheels publish
`(36.0 * w0.digit)`, `(36.0 * w1.digit)` and `(36.0 * w2.digit)`, and the
`drivers` table holds `crank`, `operand`, `ring` and nothing else. A version 7
consumer handed that document resolves `w0.digit` to nothing. Publishing the
states as their INITIAL VALUES instead was rejected outright by ADR-125 and is
not reopened: the geometry would be right only at the initial state and then
silently stop following the machine.

**Eight dominates.** A clocked document is a clocked document whatever else it
holds — a flexible leaf, a non-empty `bindings` table. The ladder is
therefore: clocked wins, else program wins (7 over 6 over 5), else bindings,
else the tree's own content.

**Where the rule is stated.** In its OWN requirement, not by restating
"Manifest contract". That is the precedent versions 6 and 7 set: the export
capability's "Manifest contract" still names the ladder up to 5, and each
later rung lives in the requirement that owns its object. Following it keeps
this delta honest about what actually changed.

### 2. The gate is re-aimed, not deleted

`document_body` is the one function `solid build`, `solid develop`, `solid
export` and `solid snapshot --renderer web` all pass through, and ADR-125 put
the refusal there for a reason a browser-rendered snapshot proves: a capture
BAKES one instant and never enters `symbolic_document`, so a gate on the
symbolic walk would leave that producer publishing
(`solid_node/core/serializer.py:658-667`).

`document_body` gains a `clocked=` parameter beside `program=`, and
`_refuse_a_clocked_model` becomes `_refuse_an_uncompiled_clocked_model`: it
asks `tree_declares_states(node)` exactly as it does today, and raises when
the answer is yes and no compiled machine was passed. That refusal is a
PRODUCER error — "this producer published a clocked model without compiling
it" — and it is what stops a fifth producer, added later, from reaching a
version 7 document by a route nobody re-checked. The structural walk, its
cost and the "a stateless model is answered by one walk that renders
nothing" property are all unchanged.

`ClockedDocumentError` keeps its name and its module; only its message and its
meaning move.

### 3. `drivers` stays the handles; `states` joins it

A `State` takes exactly `Driver`'s five fields with exactly their meanings
(`solid_node/simulation/state.py:41-93`), so the document publishes them
through exactly `drivers_table`'s rules
(`solid_node/core/serializer.py:352-376`): `default` NATIVE, `range` in
DESIGN units and never a clamp, `dtype` by name because a document is JSON,
`unit` and `scale` verbatim, keys sorted.

They are TWO tables and not one, and the split IS the handle rule. Every key
of `drivers` is an input a person may move — `sim.move(id, by=)` takes one,
and a control or an instruction targets one. No key of `states` ever is: a
state is written by the machine at an event, `set_state` refuses one by name,
and `move` naming one is refused by name
(`solid_node/simulation/clocked.py:1806-1812`). A consumer that offered a
state as a slider would be offering a handle the framework refuses, and one
table with a `kind` field would make that mistake one field-read away.

The two tables SHALL name disjoint id sets, which the framework already
guarantees at a lower level: `drive_tree` refuses a qualified id claimed by
both a `State` and a `Driver`, at the walk
(`solid_node/node/qualified.py:404-413`).

### 4. There is no `coordinates` table, and that is the point

`program.coordinates` exists because a running bank holds JOINT COORDINATES
whose `initial` values come from the rest render — the one number a consumer
cannot compute without running the CAD tree (`program.py:2688-2695`).

**A clocked bank holds no joint coordinate.** It is every declared driver at
its declared default, every declared state at its declared default, and — under
`Time.elapsed()` — the clock at `0.0` (`clocked.py:1457-1468`). Every one of
those numbers is already in the document: the two tables publish the defaults,
and `clocked.clock` says the third. So the bank is derivable, a `coordinates`
table would repeat five fields the tables already carry, and repeating them is
what the running requirement explicitly forbids ("An input entry SHALL NOT
repeat `unit`, `dtype`, `scale`, `range` or `default`").

This is the one place the clocked object departs from the program's shape. It
departs because the question the program answers here does not exist for a
clocked root, and inventing an answer would be publishing something a
consumer must then be told to ignore.

*Consequence, stated rather than hidden:* `Sim(model, state={...})` is session
setup and is NOT published. A document says where the machine RESTS; where a
particular session opened it is not a property of the model.

### 5. The `clocked` object

Top-level, beside `drivers`, `states`, `instructions` and `bindings`, and
ahead of `root` — `program`'s position, for `program`'s reason.

```
clocked: {
  "identity":  "<sha256 hex>",
  "clock":     "time" | null,
  "own":       "_own",
  "commits":   [ ... ],
  "bounds":    [ ... ],
  "limits":    {"crossing_tolerance": 1e-12, "max_crossings": 1000}
}
```

Ordered deterministically for a given tree, every key in a fixed order, so
republishing an unchanged model is byte-identical — the rule
`published_controls` and `published` already state for themselves
(`program.py:2598-2609`).

**Every expression slot holds a NATIVE GRAPH, not text**, exactly as
`Program.published` leaves its own (`program.py:2696-2705`), so
`bind_document` compiles them in the SAME pass as the tree's and a
subexpression a commit law shares with the geometry that displays it is
published ONCE. `_collect_clocked_slots` joins `_collect_slots` and
`_collect_program_slots`; `bind_document` is given the union of the two
tables' keys, the clock and the own-name, so a minted `_b0` can never collide
with anything a published expression reads
(`serializer.py:599-628`, and the collision rule at `expressions.py:242`).

### 6. `commits`: one entry per committing relation, in tree order

```
{ "sources":     ["crank", "w0.digit", "w1.digit"],
  "targets":     ["w0.digit", "w1.digit"],
  "at":          {"primitive": "floor", "level": <expression>},
  "law":         [<expression>, <expression>],
  "shapes":      {"crank": "affine"},
  "description": "(crank, w0.digit, w1.digit) commits (w0.digit, w1.digit)",
  "stated_by":   "Register" }
```

- **`sources` is in WRITTEN ORDER**, because that is the order the law's
  positional arguments are in (`clocked.py:232-242`), and a consumer
  evaluating the published expression reads them by NAME anyway — the order
  is published so a reader of the document sees the relation as written.
- **`at` is ONE jump node and its LEVEL QUANTITY**, which is `Committing`'s
  own `primitive` and `level` (`clocked.py:442-443`, built by `_event_level`
  at `clocked.py:449-487`). `primitive` is `floor`, `ceil`, `sign` or one of
  the six comparisons — `%` is refused in an `at` and cannot appear. The level
  carries NO jump inside it: `_event_level` refuses more than one jump node,
  so `_argument_graph` returns a jump-free graph. The SURFACES and the BRANCH
  are the ones the published jump vocabulary already defines and a version 5
  consumer already implements (`program.py:659-688`): integers for
  `floor`/`ceil`, zero for `sign` and a comparison. **No key is added for
  them**, exactly as the running document adds none.
- **`law` is one expression per target**, aligned with `targets` — the law
  applied ONCE to a symbolic token per source, which is the graph
  `_checked_law` already builds and today throws away
  (`clocked.py:490-542`: it calls `record.law(*tokens)`, checks the shape and
  returns the CALLABLE). Retaining that graph is the whole of what the
  simulation layer owes this cycle. A law returning a plain number publishes a
  numeric literal and never `null`: a commit's law IS the value written, so a
  constant is a real answer and not an absent one — which is the asymmetry
  with a running law edge, whose `null` means "contributes no increment".
  A `dtype=int` target is rounded ONCE, at the commit, and the document
  states HOW rather than leaving a consumer to choose. `State.committed` is
  `round(value)` (`state.py:84-93`): Python's round, which takes the nearest
  whole number and an exact half to the EVEN one, and which returns an `int`.
  Nothing else happens to a committed value — `scale` is design units per
  native unit and a commit law already speaks native units, so NO scaling is
  applied at a commit and none is published for one. A consumer must not reach
  for its own rounding: JavaScript's `Math.round` takes a half toward
  +infinity and OpenSCAD's `round` takes it away from zero, which is exactly
  why `solid_node.math` refuses to emit `round` at all
  (`solid_node/math.py:53-56`) — three runtimes, three answers. The consumer
  reads `dtype` from the `states` table and no key is added for it; the RULE
  is stated in the export requirement, and the corpus carries a machine whose
  law lands on an exact half (section 16) so a second runtime cannot pass it
  by accident.
- **A `%` in a published law is DESUGARED**, because the framework's executor
  does not evaluate the law graph at all: it calls the project's callable, and
  Python's `%` is not the document's. Section 16 states the rule, the
  verification behind it, and the wart it exposes.
- **`shapes` is what compile time decided, per input that can move the
  level.** `Committing.jumps` is a dict keyed by the moving input, each entry
  carrying `_shape_of(_standing_except(level, input))`
  (`clocked.py:409-425`) — `affine` or `kinked`; `None` is REFUSED at
  simulation construction and therefore never reaches a document. An input
  ABSENT from `shapes` cannot move this level at all, which is exactly
  `moves_with` (`clocked.py:127-130`): the consumer does not examine the
  relation for it and it costs nothing.

  *Why publish a classification a consumer could re-derive.* Because ADR-126's
  own principle is ONE AUTHORITY, and the corpus is exact: a consumer that
  classified a level differently would cut a kinked path differently and land
  on a different float. `_shape_of` is a hundred lines of structural rules
  (`program.py:3867-3881`); asking a second runtime to reproduce it exactly
  buys nothing and risks everything, and the running document already
  publishes `affine` for the same reason. The KINK BREAKPOINTS are NOT
  published: they are `abs`, `min` and `max` in the expression, which a
  consumer already re-derives — the running corpus's own `_kinked_laws` does
  it from the published text (`tools/generate_running_corpus.py:503-521`).
- **`description` and `stated_by`** are a law edge's two, for a law edge's
  reason: a consumer's refusal must name what a reader can find in the model.
  `record.described()` and the declaring class are both already held
  (`clocked.py:115`, `clocked.py:798-800`).
- **Order** is `_records_of`'s tree order (`clocked.py:352-373`), which walks
  `_rest_children` — the linked rest structure every qualified pass descends,
  deterministic for a given tree.

### 7. `bounds`: one entry per compiled constraint

ADR-126 compiles one constraint per (bounded coordinate, SIDE), and that is
the unit published — not a `spans`-style `{low, high}` pair, because the two
sides carry different chains only by accident and different PLANS in general,
and because a `Stop` is reported per side (`clocked.py:896-928`).

```
{ "coordinate":  "knob.travel",
  "side":        "high",
  "unit":        "mm",
  "value":       <expression over bank ids>,
  "bound":       <expression over bank ids and the own-name>,
  "plan":        {"skeleton": <expr>, "jumps": [{"name": "_j0",
                   "primitive": "floor", "level": <expr>}]} | null,
  "shapes":      {"crank": {"level": "affine", "jumps": ["affine"]}},
  "node":        "Knob",
  "joint":       "slide",
  "description": "the high bound of 'knob.travel'" }
```

- **`value` is the CHAIN** — `Bounded.chain`, the one expression graph over the
  bank's ids that ADR-126 composes by SUBSTITUTION down to declared drivers
  and states, traversing intermediate ports and never simplifying
  (`clocked.py:653-669`, `_Chains.of` at `722-732`). It is published VERBATIM,
  `%` included and un-desugared, and section 16 says why: a chain, a bound and
  a level are `GraphValue`s the framework EVALUATES through the graph — every
  threshold, clip and judgement calls `.evaluate` (`clocked.py:986-1015`),
  whose `%` is `math.fmod` (`scad_expression.py:59`) — so the published graph
  already says exactly what the clip computed. A commit law is the opposite
  case and gets the opposite treatment.
- **`bound` is the compiled bound**, with its own coordinate read under the
  own-name (section 8) and every `reads=` coordinate already substituted by
  its own chain (`clocked.py:1171-1178`). A NUMERIC bound publishes a number
  literal.
- **The LEVEL is the consumer's own subtraction.** `Bounded.level` is
  `value − bound` on the high side and `bound − value` on the low side
  (`clocked.py:1179-1182`), and publishing it as well would publish `bound`
  twice. `side` is what says which subtraction, and the consumer forms it.
- **`plan` is the level's JUMP PLAN**, `null` where the level carries none.
  ADR-109 admits jumps in a bound — a `floor` for a tooth, a comparison for a
  gate — and ADR-126 partitions the path at the level's own jump surfaces
  before solving each piece (`clocked.py:1020-1073`, `_plan_of` at
  `clocked.py:1185`). The published shape is EXACTLY the running document's
  jump plan, through the same `_published_plan` and the same `_renamed`
  (`program.py:4305-4322`), and the placeholders are minted across the whole
  document by the same `_placeholder_prefix` rule
  (`program.py:2781-2799`, `4294-4302`), because two plans naming their first
  jump alike would let the binding pass share one subtree between two
  different jump nodes.
- **`shapes`, per input that can move the level**, carries the SKELETON's shape
  and each jump's, aligned with `plan.jumps` (`clocked.py:1195-1209`). An
  absent input cannot move the level and is not examined for it — `moves_with`
  again (`clocked.py:980-984`). A CURVED level is refused at construction and
  never reaches a document.
- **`node` and `joint`** are what a `Stop` and a `JointRangeError` name
  (`clocked.py:1290-1300`); publishing them is what lets a consumer's stop
  report name what a reader can find in the model.

A declared range that reaches NOTHING still appears: ADR-126 admits a
DECORATIVE range as a constant chain, and it publishes as a `value` that is a
number literal with an empty `shapes`. It costs one small entry and it is
honest — the machine really does declare that range.

### 8. `$own` cannot be published, and a minted name replaces it

`_OWN` is the free name a constraint level reads its own coordinate under —
the value it held when the REQUEST STARTED, ADR-109's committed-state rule
with the request in the tick's place (`clocked.py:589-594`). Its spelling is
`'$own'`, chosen so `_shape_of` reads it as a constant and so it cannot
collide with a qualified id.

**It cannot travel.** The document's expression language admits exactly ONE
`$`-name: `_NAME_RE = re.compile(r'\$t|[A-Za-z_][A-Za-z0-9_]*...')`
(`solid_node/core/expressions.py:25`), and `bind_expressions` validates every
leaf as `$t`, a declared id or an earlier binding (`expressions.py:261-269`).
`$own` would not even tokenize.

Widening the shared regex was rejected: it changes the expression language
every document and every consumer shares, for one producer's private
convention.

**Chosen: mint the name, and DECLARE it.** `clocked.own` publishes the name —
`_own`, lengthened by a leading underscore for as long as any published id
equals it, which is `_placeholder_prefix`'s own rule for `_j` with the
digit-suffix match replaced by equality, there being one own-name and not a
series (`program.py:4294-4302`) — and every `bound` expression reads the
coordinate's start-of-request value under it. A consumer evaluates each
bound's `value` over the bank at the request's start, binds the result to
that name, and holds it for the whole request. The name is in the set
`bind_document` is given, so nothing can mint over it.

This is `program.clock`'s pattern exactly: one reserved free name, published
as a string, rather than a convention a consumer has to know.

### 9. `limits`: the one tolerance a clocked path reaches, published

ADR-125 and ADR-127 claim the clocked path introduces NO tolerance, and the
claim is true: `Committing.next_event` solves by division through
`JumpPlan._solved`, which uses none (`program.py:560-587`), and ADR-127
asserts `_CROSSING_TOLERANCE` appears nowhere in `clocked.py`.

**But it is REACHED, and the design says so.** A KINKED event level is cut at
its breakpoints and the crossings found on adjacent pieces are merged by
`_deduplicated`, which calls two crossings one when they are within
`_CROSSING_TOLERANCE` (`clocked.py:204`, `program.py:705-715`); a jumped
constraint level is partitioned by `JumpPlan.cuts`, whose `_merged` folds cuts
by the same constant (`program.py:717-730`). "Introduces no NEW use" and
"reaches none" are different claims, and only the first is true.

So `clocked.limits` publishes `crossing_tolerance` and `max_crossings`, as
numbers, for the running document's own stated reason: so a consumer cannot
silently differ from the producer. `subdivisions`, `bisection_rounds` and
`agreement` are NOT published — a clocked path never searches, never bisects
and never compares two increments, so publishing them would state a contract
this discipline does not have.

### 10. The clock, and what `$t` means in a version 8 document

**Under `Time.elapsed()` the document carries the free name `time`.** That is
version 5's rule (`export/spec.md:1086-1103`) applied to the base it was
written for, and it is necessary: the viewer poses a clocked machine at its
banked instant, and `$t` is a 0..1 animation variable, not seconds.
`symbolic_document` gains one line in the clocked branch — the line the
running branch already has, `target._states[CLOCK_NAME] = symbol(CLOCK_NAME)`
(`serializer.py:258`) — and `clocked.clock` publishes `"time"`. `read_time`
reads each node's own snapshot entry first, so the delivery is per visited
assembly, exactly as ADR-127 states for the posed case.

**Under a clocked root with NO time base, `$t` is untouched and means what it
has always meant.** ADR-125 is explicit that `time` is not in the bank, that a
clocked pose leaves `self.time` the untimed symbolic `$t` through ADR-008's
fallback, and that "nothing about `time` changes, and that is the point". So
the `animation` object is the one an undeclared root publishes — `fps` and
`frames`, no `loop`, byte for byte (`serializer.py:422-443`; a clocked root
declares no base, or an elapsed one whose `loop` is `None`) — and a geometry
that is a formula of `$t` animates on that timeline while the bank stands.

**What the preview shows** is therefore stated plainly and is not a new
behaviour: the INITIAL BANK posed — every driver and every state at its
declared default — with `$t` sweeping whatever formula-of-time geometry the
model has. `clocked.clock` is `null` there, which is a consumer's signal that
this machine has no clock to advance.

### 11. The tree half of version 8 needs nothing, and that is measured

Serializing `tests/clocked_project/register.py` on this worktree with the gate
bypassed publishes `(36.0 * w0.digit)`, `(36.0 * w1.digit)` and
`(36.0 * w2.digit)`, with a `bindings` table of `[]` and a `drivers` table of
`crank`, `operand`, `ring`.

That works because `drive_tree` binds a declared STATE through the same
`resolve` callback it binds a driver through, in the same pass
(`solid_node/node/qualified.py:401-416`), so `symbolic_document`'s own
`symbolic` resolver already mints `DriverToken(state_id)` for a state — while
the table it RETURNS holds drivers only (`qualified.py:391-393`). And
`tree_declares_drivers` already answers True for a tree that declares a state
and no driver (`enumeration.py:285-289`), so `symbolic_document`'s early
return does not skip one — verified on `pendulum.ClockAlone`, an elapsed
clocked root with no driver at all.

So the changes to `symbolic_document` are exactly two: the elapsed clock
binding of section 10, and nothing else. The control refusal stays where it is
(`serializer.py:250-253`) and goes on refusing a control under a clocked root,
which is correct and is section 14.

**No coordinate delivery.** The running branch binds every joint coordinate
symbolically because a running bank HOLDS them; a clocked bank holds none, so
a joint's placement publishes as the expression over drivers and states the
untimed enumeration produces — which is the untimed publication path,
unchanged, and is what the measurement above shows.

### 12. Compiling for publication: `clocked_of`, on `program_of`'s shape

```python
def compiled_clocked(node):            # serializer.py, beside compiled_program
    if not tree_declares_states(node):
        return None, None
    from solid_node.simulation.clocked import clocked_of
    return clocked_of(node)
```

`clocked_of(root)` mirrors `program_of` (`program.py:4508-4536`): it takes
`_snapshots(root)`, constructs `Sim(root)` — a clocked `Sim`, which takes no
`dt` — reads the compiled machine and `dict(sim.initial.values)` off it, and
restores every node's snapshot and re-renders in a `finally`, so a caller
that held a posed tree still holds one. There is no `release_tree`: a clocked
simulation does not own the tree the way a run does, and `Sim.__init__`'s
clocked branch returns before any binder is installed
(`sim.py:203-217`).

Two properties this buys, both of them the running one's:

- **The published machine is the simulation's BY CONSTRUCTION**, not by two
  implementations agreeing. The compile is `compile_clocked` and
  `compile_bounds` as `Clocked.__init__` calls them (`clocked.py:1450-1456`),
  and every refusal they make is made before a document exists.
- **The browser-snapshot capture works.** That producer poses the tree at
  `--drive` values and bakes one instant; `program_of` already re-poses and
  restores in exactly that path, and this does the same.

The import is deferred, HERE and nowhere else in the producers, so a model
that declares no `State` loads no clocked module — the rule
`compiled_program` already states for the running compiler
(`serializer.py:631-643`, capability `cli-startup-cost`).

`clocked_block(compiled, initial) = compiled.published(initial)`, mirroring
`program_block` (`serializer.py:646-650`).

### 13. `identity`

A sha256 over a canonical listing — the root class, each input and state with
its `dtype` and `scale`, each committing relation's sources, targets,
primitive and law text, and each compiled constraint's coordinate, side and
level text — exactly `Program.described()`'s shape and purpose
(`program.py:2424-2425`, `2478-2498`): **a bank taken against one machine is
refused against another.** A consumer that persists a bank across a reload —
which is what cycle 5 will do — needs it, and a digest is four lines.

A changed RANGE changes the identity, as it does for a run, so a snapshot
cannot be restored into a machine whose stops have moved.

### 14. `instructions` and `controls` under a clocked root — the brief was wrong

This cycle's brief says "an instruction under a clocked root is refused
today; keep it". **It is not.** `compile_clocked` refuses an instruction only
where its target is a STATE (`clocked.py:338-347`); an instruction targeting a
DRIVER is admitted. Probed on this worktree: a clocked root declaring
`instructions = {'Park': Instruction({'crank': 360.0}, duration=0.5),
'Advance': Instruction(by={'crank': 10.0}, duration=0.5)}` constructs a
clocked `Sim` with both in `sim.instructions`, and only `sim.trigger('Park')`
is refused by name. `workflow/warts.md:3033-3038` says the same thing.

An instruction targeting a STATE never reaches a document, and structurally
rather than by a filter in the table: the refusal is made by `compile_clocked`
at simulation construction, and every producer compiles the machine before it
publishes (section 12) while the re-aimed gate refuses a clocked tree
published without one (section 2). There is no route to a document that
skips the refusal.

**Decision: a version 8 document publishes EVERY declared instruction, in the
version 5 shape** — each entry carrying exactly one of `targets` and `by`,
both keyed by qualified driver id and both in design units, beside
`duration`. `instructions_table`'s `running=` flag does not mean "running": it
means "the document is version 5 or above", and the reason it was introduced
is stated in its own docstring — a RELATIVE instruction is omitted below
version 5 because the shipped viewer reads `targets` off every entry
(`serializer.py:379-419`). A version 8 consumer is a new consumer and has that
problem nowhere. Publishing `{}` instead, or silently dropping the relative
ones, would be a producer discarding a declaration for a reason that does not
apply. The parameter is renamed to say what it means; its three non-test call
sites — `core/builder.py:664`, `core/export.py:158` and
`tools/generate_running_corpus.py:307` — and the framework's own tests pass
exactly what they pass today, so no stateless document moves.

**This cycle gives the table no runtime meaning.** A clocked simulation has no
command surface and `trigger` stays refused by name. Whether a clocked
consumer may turn an instruction into a `move` request is cycle 6's question,
and `workflow/warts.md:3033-3038` already records it.

**A control stays REFUSED**, in both places, unchanged: the publication walk
refuses one under a non-running root by name
(`serializer.py:250-253`, `309-322`) and `Sim.__init__` makes the same refusal
(`sim.py:200-202`). A version 8 document therefore never carries a `controls`
key, and `compiled_controls(None, None)` returns `{}` regardless
(`serializer.py:741-754`).

### 15. The producers, and how the framework knows the viewer cannot read it

**Nothing new is needed.** The `solid_node.viewer` entry point's `describe`
report already carries `documentVersions`, and `bundle.unreadable_document(8)`
already returns the three facts as one sentence or `None`
(`solid_node/viewers/bundle.py:101-136`). Version 8 is simply not in the list
the installed viewer reports until the viewer's own cycle adds it — and a
viewer reporting no `documentVersions` at all is read as `[1, 2, 3, 4]`
(`bundle.py:94-98`), so an older viewer is described truthfully rather than
guessed at.

Each producer therefore behaves as it already does for a version it cannot
read, and each behaviour is already the right one:

| producer | today, for an unreadable version | with version 8 |
| --- | --- | --- |
| `solid build` / `solid develop` | `_warn_unreadable`, publish anyway (`core/builder.py:37-53`) | warns, publishes; the build, the STLs, the tests and `--no-web` are unaffected |
| `solid export` | `_warn_unreadable`, write anyway (`core/export.py:203-210`) | warns, writes; an export is an artifact a LATER viewer may open |
| `solid snapshot --renderer web` | `refuse_unreadable` BEFORE the browser starts (`viewers/browser.py:102`, `137-155`) | refused by name, no browser, no image, no staging directory, and never a silent fall back to OpenSCAD |
| `solid snapshot --renderer openscad` | untouched | untouched: renders the tree as posed — the INITIAL BANK, with `--drive` posing drivers and `set_state` refusing a state by name |

Each producer gains the same two lines: `compiled_clocked(node)` beside
`compiled_program(node)`, and the block passed to `document_body`. The capture
path additionally publishes the two tables off the compiled machine's own
inputs and states, mirroring its running branch
(`browser.py:98-101`).

The shop's hub preview calls these same producers and is the shop's own
repository; it is out of scope and named so.

### 16. The corpus, and why it is EXACT

`tools/generate_clocked_corpus.py` writes `tests/clocked-corpus.json` from the
framework's OWN clocked executor; `tests/test_clocked_corpus.py` replays it;
the viewer commits a copy and replays it against the browser (cycle 5). Every
expected value in it is a value the executor PRODUCED and never one recomputed
a second way — ADR-111's pattern, unchanged.

**Agreement is BIT FOR BIT, and that is the one substantive difference from
the running corpus.** The running corpus compares floats within `1e-9`
relative, which is the run's own `_TOLERANCE` — "the window inside which the
run itself declines to distinguish two increments"
(`tests/test_running_corpus.py:14-19`). A clocked executor has no such window:

- there is no `dt`, so nothing is an increment;
- every event is SOLVED by division, never searched (ADR-125);
- **two relations are one event exactly when their landings are the SAME
  float** (`clocked.py:1761-1787`), and a consumer within `1e-9` of the
  landing would merge events this framework keeps apart, or split events it
  joins — the corpus's `ties` fixture is built precisely on surfaces one ulp
  apart.

A tolerance would therefore not merely be slack; it would admit a consumer
that is WRONG about the thing this discipline exists to be right about. JSON
round-trips a Python float exactly (shortest round-trip `repr`), and a JS
double IS a Python float, so exactness is reachable. The corpus carries
`"tolerance": {"float": 0.0}` so the claim is a field of the file and not a
convention of the reader.

**What the claim RESTS ON**, stated rather than assumed. Every value the
corpus records — a bank value, an event landing, a clipped fraction, a
threshold — is produced by operations that are exact or identically rounded in
both runtimes:

- IEEE `+`, `-`, `*`, `/` and `sqrt`, which the standard requires to be
  correctly rounded, so one double in gives one double out in either runtime;
- `fmod`, which is exact by construction, and the floored remainder built from
  it below, whose correction is ONE addition and therefore one rounding;
- `floor`, `ceil`, `abs`, `sign`, `min`, `max` and the six comparisons, which
  select rather than round;
- the FAR-SIDE WALK, `far_side_of` (`program.py:1578-1634`) — the bisection
  every landing passes through — which runs in float ORDINAL space through
  `_ordinal`/`_from_ordinal` (`program.py:1029-1041`): a reinterpretation of a
  double's 64 bits as a signed integer, which a second runtime reproduces with
  one `ArrayBuffer` viewed as a `Float64Array` and a `BigInt64Array`, and
  never with arithmetic. A consumer that walked by a small epsilon instead
  would land on a different float at exactly the surfaces this corpus is built
  on, and cycle 5 owes that bit walk.

**What it does NOT rest on**, as a stated limitation. A TRANSCENDENTAL —
`sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2` of
`solid_node.math.SYMBOLIC_BUILTINS`, all of them in DEGREES — and `^`
(`operator.pow` against JavaScript's `**`) are not correctly rounded by IEEE,
so libm and V8 need not agree in the last bit. The claim therefore covers no
machine that uses one in a COMMIT LAW, an EVENT LEVEL, a CONSTRAINT LEVEL or a
CHAIN, and no corpus machine does: `pendulum`'s `sin` is in the POSE
(`self.bob.swing = A * sin(...)`, `pendulum.py:166`), which the corpus does not
record at all, and its one `floor(sin(time))` level belongs to a CURVED-level
fixture the framework refuses at construction (`pendulum.py:93-95`). The
generator REFUSES a machine that carries one in a published `clocked`
expression, so the limitation is enforced rather than remembered. If a project
ever needs a transcendental commit law, the shape of the follow-up is a
per-machine tolerance FIELD beside the file's own `"tolerance": {"float":
0.0}` — one machine opting out by name — and not a window the whole file
relaxes into.

#### `%` means two things, and the document says which

The `%` hazard is real, but it is NOT Python-versus-JavaScript. Verified on
this worktree:

- **the DOCUMENT's `%` is truncated in both runtimes.** The framework's two
  evaluators spell it `math.fmod` (`GraphValue.evaluate`,
  `scad_expression.py:59`; the path evaluator, `program.py:806`), and the
  viewer's is JavaScript's native `%` (`solid_node_viewer/widget/src/
  expressions.ts:632`), which is truncated too. The two runtimes AGREE on the
  document's `%`.
- **the CLOCKED EXECUTOR does not evaluate the law graph.** It calls the
  project's Python callable with the bank's numbers (`clocked.py:222-242`,
  ADR-125), and Python's float `%` is FLOORED. So `(-1) % 10` is `9` in the
  bank the framework produces and `-1` in a graph published verbatim.

The breach is therefore INSIDE the framework, and a law graph published as
written would not mean what the executor computed. `solid_node.math` already
knows the difference and says so where it refuses to emit a `mod` function:
"Python's `%` takes the sign of the divisor where OpenSCAD's and JavaScript's
take the sign of the dividend" (`solid_node/math.py:57-60`).

**Decision: a `%` node in a published commit LAW is DESUGARED to the floored
remainder.** CPython's `float_rem` (`Objects/floatobject.c`) is
`mod = fmod(a, b); if (mod) { if ((b < 0) != (mod < 0)) mod += b; }
else mod = copysign(0.0, b);` — `fmod` is exact and the correction is a single
IEEE addition, so the document's own vocabulary reproduces it, with the same
one rounding, as

    r + b * ((r != 0) * ((r < 0) != (b < 0)))      where r is the document's a % b

**Verified empirically on this worktree** with the workspace venv: 500 000
random double pairs — uniform small, uniform wide, sub-ulp, and random finite
bit patterns, both signs — reproduced Python's `a % b` with ZERO value
mismatches, as did the hand cases `-1 % 10 = 9`, `1 % -10 = -9`,
`-7 % -3 = -1`, `5.5 % -2 = -0.5`, `-5.5 % 2 = 0.5` and `1e308 % -3 = -1`. The
ONE divergence is the sign of a ZERO result under a negative divisor —
Python's `copysign(0.0, b)` gives `-0.0` where the desugaring gives `+0.0` —
which compares equal as a number in both runtimes (`-0.0 == 0.0`, `-0 === 0`)
and which nothing in the published vocabulary distinguishes.

**The rewrite applies to a LAW GRAPH and to nothing else.**

- An `at` cannot carry a `%` anywhere, in any position: `%` is a JUMP operator
  (`program.py:79`, `_is_jump` at `645-647`), and `_event_level` admits exactly
  ONE jump node which must be a `floor`, `ceil`, `sign` or comparison
  (`clocked.py:474-487`), so a level holding a remainder is already refused by
  name.
- A CHAIN, a BOUND and a constraint LEVEL keep the document's `%`, because the
  framework evaluates THOSE through the graph — they are `GraphValue`s and
  every threshold, clip, `at` and judgement calls `.evaluate`
  (`clocked.py:986-1015`), which is `fmod`. Publishing them verbatim says
  exactly what the clip computed; desugaring them would make the document
  disagree with the framework.

**The wart this exposes, recorded and not fixed here.** The split is not
Python-versus-JavaScript, it is CALLABLE-versus-GRAPH, and the framework is on
both sides of it:

- a COMMIT law is CALLED with numbers → floored;
- a chain, a bound, a constraint level and a RUNNING law edge (ADR-106) are
  EVALUATED as graphs → `fmod`;
- and a POSE calls the callable (`couplings.py:1640-1650` hands the law its
  numbers at realization) while the PUBLISHED pose expression is that same law
  applied to symbols — so a `drives(law=)` taking `%` of a negative already
  poses one way in Python and publishes another, in every document version
  from 2 upward.

This cycle publishes the truth of each place it publishes FROM, fixes only
what it publishes for the FIRST time — a commit law, where no existing
document moves — and records the other two in `workflow/warts.md`: the
CROSS-MODE divergence (the same law text means floored under a clocked root
and `fmod` under a running one) and the POSE-versus-GRAPH divergence, which is
framework-wide, pre-existing, and unfixable inside a cycle that must leave
versions 5, 6 and 7 byte-identical.

**`% 0`.** Python raises `ZeroDivisionError` for `a % 0.0`; the document's
`fmod(a, 0)` is NaN and the desugaring leaves it NaN. A law that raises raises
inside `relation.commit`, which the request runs over `working =
dict(self.bank)` (`clocked.py:1660`) and whose result reaches `self.bank` only
after the pose is accepted (`_posed`, `clocked.py:1561-1590`) — so the request
is refused WHOLE and commits nothing, ADR-125's atomicity, unchanged. The
corpus records such a step the way it records every refusal: by KIND
(`ZeroDivisionError`) and by the names its message carries. The document
cannot express a raise, so a consumer that computes a NON-FINITE commit value
refuses the request rather than banking it.

The parity fixture (`tools/generate_parity_fixture.py`, ADR-022) stays what it
is: the pin on the symbolic vocabulary function for function across the
runtimes. It pins the DOCUMENT's `%`, which is what a chain and a bound carry;
the desugared form above is what a commit law carries, and the corpus is what
pins it.

#### The fixture itself

**Shape**, following the running corpus file for file
(`tools/generate_running_corpus.py:670-696`):

```
{ "generated_by": "tools/generate_clocked_corpus.py",
  "corpus":       "tests/clocked_project/",
  "tolerance":    {"float": 0.0},
  "machines": [
    { "name": "Calculator",
      "document": {format, version, drivers, states, instructions,
                   bindings, clocked},
      "script":   [ {"move": {...}} | {"snapshot": "a"} | {"restore": "a"}
                    | {"reset": true} , ... ],
      "requests": [ ... one entry per script step ... ] } ] }
```

Documents are deduplicated by machine name and embedded VERBATIM, exactly as
the running corpus embeds its program-bearing keys
(`generate_running_corpus.py:298-309`, `671-684`), and a framework test
asserts each machine's REAL published document reproduces the fixture's copy,
so the fixture cannot drift from the producer it claims to come from.

Each `requests` entry carries the whole bank after the step, the admitted
travel, the commits in path order (each with its relations, fraction, the
input's value and the targets written) and the stops (each with coordinate,
side, bound, value, input and fraction) — and, for a step the executor
REFUSED, the exception KIND and the qualified names the message must contain,
with the bank after proving that nothing was committed. The kind and the names
are pinned and the prose is not: a message is edited for clarity and a corpus
that pinned it would make every such edit a regeneration, while the KIND and
the NAMES are the contract a second runtime must reproduce.

**`uncovered_features` refuses a narrow corpus**, mirroring
`generate_running_corpus.uncovered_features` (`:369-500`) and
`generate_parity_fixture.uncovered_builtins`. The inventory is stated in the
tool rather than inferred, so adding a machine cannot narrow the corpus by
accident and removing one cannot narrow it at all — it refuses to write
instead — and the framework's own suite tests that refusal directly, so the
width is visible without running the generator. The inventory:

the four `at` primitives (`floor`, `ceil`, `sign`, a comparison); a law using
`%` over a NEGATIVE operand; a multi-source commit law; a multi-target commit;
an integer state rounded once; an integer state whose law lands on an exact
HALF; a scaled state; a RISING step that fires; a
FALLING step that fires nothing; a kinked event level cut at its breakpoints;
two relations landing on ONE float; two surfaces one ulp apart as two events;
a conflict refusing the request; an `at` that reads the state it commits; one
state written by two relations on two inputs; a request clipped at a numeric
bound; a request clipped at an expression bound; a bound reading ANOTHER
coordinate; a bound reading its OWN coordinate (the ratchet); a FREEZE, both
bounds reading the own coordinate; a jumped constraint level partitioned at
its own surfaces; a kinked constraint level; ZERO travel admitted; a
decorative range nothing binds; a bank standing OUTSIDE a bound moving back
in; an end-of-request judgement refusing a commit; a chain through an
INTERMEDIATE PORT; a snapshot; a restore; a reset; the clock in the bank; an
event on the clock; a time request refused BACKWARDS; a time request no bound
clips; and a request refused for too many events.

Two of those items are new here and are what findings 1 and 3 of the review
asked for. The NEGATIVE remainder needs no new fixture and no edited one:
`register`'s own stroke law is `total % 10` over `d0 + 10*d1 + 100*d2 +
operand`, and `operand` is a declared driver whose `range=(0, 9)` is
presentation and clamps nothing (ADR-125), so a script that moves it to a
negative value drives `total` negative and asks the question. The EXACT HALF
needs a law that lands on `x.5` for an `int` state — one relation on the
Curta-shaped fixture of section 17, whose expected value is computed by hand
from the half-to-even rule and not from the implementation — so a consumer
reaching for `Math.round` fails on it instead of passing by luck.

**Machines:** the existing clocked fixtures — `counter`, `register`,
`clearing`, `pawl`, `lock`, `freeze`, `gate`, `ties`, `pendulum`, `outside`,
`decorative`, `units` — plus the Curta-shaped one below. The existing
fixtures are not edited: the corpus SCRIPTS them, and a fixture edited to suit
a corpus is a fixture that no longer means what its own cycle's tests say it
means.

### 17. The Curta-shaped fixture

`tests/clocked_project/register.py` is already half the shape: three wheels of
ONE class, one stroke relation over all three digits and an operand, and three
clearing relations each reading its own digit — two writers per digit, on two
inputs. What no fixture carries is all of it AT ONCE, and the corpus's
interesting cases are the interactions: a clip and a commit in one request, a
clearing surface that moves with the state it writes while an interlock holds,
a chain that has to traverse an intermediate port to reach a bound.

`tests/clocked_project/calculator.py` adds a `Calculator` root:

- FOUR dials of one class (`register.py`'s three plus one, so a carry
  propagates twice), each `digit = State(default=0, range=(0, 9), dtype=int)`;
- a `crank` driver and a `ring` clearing driver;
- a `setting` selector driven through a plain `Port` into the knob's joint —
  `setting.drives(knob.travel, ratio=6)` — because the Curta's selectors are
  wired that way and ADR-126 traverses an intermediate port for exactly that
  reason (`clocked.py:660-664`);
- the STROKE relation, `at = floor(crank / 360)`, law the four-digit add;
- one CLEARING relation per dial, `at = ring >= start + pitch * (10 - digit)`,
  reading the digit it writes — the spike's finding 2, where the note's own
  sketch writes a constant the measured geometry does not admit;
- the RATCHET, a one-argument `Bound` on the crank's own joint reading its own
  coordinate (`pawl.py`'s shape);
- the FREEZE, both bounds of the selector's joint reading the own coordinate
  so the knob may not move while the crank is off rest (`freeze.py`'s shape,
  which is ADR-126's own acceptance fixture);
- and one relation whose law lands an `int` state on an EXACT HALF — a
  `dtype=int` total divided by two, say — so the corpus carries the
  half-to-even rounding of section 6 as a machine and not as a sentence. Its
  expected value is computed by hand from that rule.

Geometry is one box per part, from `tests/clocked_project/parts.py`. Four
dials rather than seventeen is a corpus-size choice and is stated as one: the
seventeenth dial exercises nothing the fourth does not, and every scenario is
replayed by a second runtime.

### 18. What is asserted unchanged, structurally

- **Every stateless document is byte-identical**, compared literally against
  the same fixture published at the cycle's base commit — the assertion
  ADR-125 already pins for its own change, extended to this one.
- **`tests/running-corpus.json` and every `tests/running_project` fixture are
  untouched**, by hash, and no line of `simulation/run.py` changes.
  `simulation/program.py` gains nothing but what section 6, 7 and 12 REUSE.
- **No clocked code path is entered for a stateless tree**: the
  `simulation.clocked` counter (`clocked.py:75-89`) reads ZERO across a
  stateless model's construction, pose, stepping AND publication — the
  assertion ADR-125 and ADR-127 both make, now covering the producer.
- **`document_body` asks one structural question for a stateless tree** and
  renders nothing, exactly as today.

### 19. Risks

- **Bit-for-bit is a strong claim.** Section 16 states it, states why a weaker
  one would be wrong, and states what it rests on operation by operation. The
  one operation that would have broken it — `%` — is resolved by publishing
  the floored remainder the executor actually computes, verified against
  CPython's `float_rem` and over 500 000 random double pairs. What remains is
  named and bounded: the sign of a zero under a negative divisor (equal as a
  number in both runtimes), a `% 0` the document cannot express as a raise,
  and the transcendentals and `^` the claim excludes and the generator
  refuses. The corpus exercises the negative remainder and the exact-half
  rounding deliberately.
- **A composed chain can be long.** ADR-126 measured 1 to 3 nodes and levels 3
  to 18 on its own fixtures, so nothing this framework can write today
  approaches a size that would make a published chain unwieldy. The
  Curta-shaped fixture's selector chain, through a port and a ratio, is the
  longest this cycle produces and its size is recorded.
- **`identity` is new surface.** It is a digest of a canonical listing and
  nothing consumes it in this cycle; if cycle 5 wants a different granularity
  the listing is the only thing that moves.
- **A producer added later could forget the compile.** That is precisely what
  section 2's re-aimed gate refuses, and the refusal is tested from each of
  the four producers rather than from `document_body` alone.

### 20. Non-goals, each with its reason and its shape

- **The viewer's execution of a version 8 document** (cycle 5) and **the
  browser's clock and clip** (cycle 6). Both are `solid-node-viewer`'s own
  repository, under its own OpenSpec records; a change that spans both
  packages is one change in each. Nothing here touches that repository, and
  the contract between them is this document plus the corpus.
- **Any change to versions 5, 6 or 7, to the running corpus, or to
  `Time.running()`.** A running root cannot declare a state, so the two
  ladders cannot meet; asserted by diff and by hash.
- **An `Instruction` or a control acquiring meaning under a clocked root.**
  Section 14 publishes the declarations that exist and gives them no runtime
  meaning; what a clocked consumer may do with one is cycle 6's, and the wart
  is already recorded.
- **The Curta project's migration** to the published document, and the shop's
  hub preview. Both belong to their own repositories.
- **A `State` under `Time.running()`**, still defined and not implemented
  (ADR-125), and **a clip in time with a chain that follows the clock**, still
  ADR-127's single open item. Neither is reached by a document cycle.
- **A structural pre-check for two writers at one event** (ADR-125's recorded
  follow-up). The conflict is a property of the bank and the path; publishing
  it would mean publishing a claim the framework does not make.
- **The framework's OWN two meanings of `%`** (section 16). This cycle makes
  the published commit law say what the executor computed and records the rest
  as warts: the same law text means floored under a clocked root and `fmod`
  under a running one, and a `drives(law=)` taking `%` of a negative poses one
  way in Python and publishes another in every version from 2 upward.
  Reconciling them means changing what a published pose expression or a
  running law edge MEANS, which moves versions 5, 6 and 7 — the one thing this
  cycle may not do. It is a wart with a named owner and not a silence.

### 21. Planned proof

- **Red first, per behaviour.** The lifted gate's own refusal test is
  INVERTED — the existing test that asserts a clocked model is refused becomes
  the test that asserts it publishes — and every new behaviour gets a test
  that fails for its stated reason first.
- **Golden documents.** The version 8 documents of `counter`, `register`,
  `pawl`, `pendulum` and `calculator` are pinned as committed fixture files and
  compared literally, which is what the running cycles did for their programs;
  a structural assertion would let a key change without a test failing.
- **The ladder.** `document_version` is tested at each rung, including that a
  clocked tree with a flexible leaf and a non-empty `bindings` table still
  declares 8, and that a stateless tree never does.
- **Byte identity**, by literal comparison against documents published at the
  cycle's base commit, for every stateless fixture and for the running
  fixtures.
- **The corpus**, three ways: the framework reproduces it exactly; the
  generator refuses a corpus missing each listed feature (tested directly);
  and each machine's real published document equals the fixture's copy.
- **The four producers**, each separately: a build publishes 8 and warns, an
  export writes 8 and warns, a web snapshot is refused before the browser
  starts with no staging directory left behind, and an OpenSCAD snapshot
  renders the initial bank.
- **The counter** asserted zero across a stateless model's whole lifecycle,
  publication included.

### 22. Closure 1: two landings the shared locator had no answer for

This cycle's corpus is what found them, so this cycle closes them. Neither
is a new behaviour: each is a place where the SHARED locator, which cycles 1
and 2 compiled against and this cycle publishes, refused or lost a request
the ratified rules already describe. Both are corrections of ADR-125 and
ADR-126 rather than additions to them, and both are stated as corpus
contract so the viewer's own cycle inherits them.

**(a) A crossing belongs to the request whose path CONTAINS its landing.**
ADR-125 stated the containment by FRACTION — "the right end is INCLUSIVE and
the left end exclusive" — and that reading loses an event. `ties.Strict`
states `at = crank > 100`; `move('crank', to=100.0)` solves its crossing at
fraction 1.0, but the landing, the nearest representable value on the far
side of a STRICT surface, is the first float ABOVE 100.0 — beyond the
request's own endpoint. The request committed the value anyway and then
resumed from a point past its target, so the remaining travel was NEGATIVE
and the same surface was re-solved backwards; the walk, asked for a far side
in the direction it had just come from, found none and raised
`LandingInvariantError`. And the next request, resuming from 100.0, excluded
its own left end BY FRACTION, so the surface at fraction 0 was skipped and
the event was lost by both.

The rule, stated by LANDING in both directions:

- A landing ON the endpoint is this request's — a request that ends exactly
  on a NON-STRICT surface has reached it, which is ADR-125's stroke.
- A landing one representable value BEYOND the endpoint is NOT this
  request's. It belongs to the next request, whose path from that endpoint
  contains it.
- Therefore the left end is excluded by LANDING and not by fraction: a
  crossing solved at fraction 0 whose far side lies AHEAD inside the path IS
  this request's first event, and a request resuming from its own landing
  still fires nothing, because there the landing IS the value it starts
  from.

`_solved` keeps excluding a piece's left end, which is right for an interior
breakpoint — the sub-piece before it reached that surface — so the path's own
OPENING surface is added by `Committing._located`, read with the shared
`_on_surface` off the level the path starts at. `next_event` then reads the
branch AT THE START (there is no piece behind the opening to take a midpoint
of) and the branch at the next representable value the path reaches: equal
means the machine already stands on the far side and the surface is not
this request's; different means the landing is that value. A landing beyond
the endpoint is skipped, in the direction of travel.

The correction fires one event the framework previously LOST outside the
strict case as well: a `sign` level standing at zero and moved off it takes
TWO rising steps, `-1 → 0` at the centre and `0 → +1` at the float above it,
and the corpus's `Signed` machine now records both.

**(b) The landing walk's first step is sized by the SEGMENT, never by the
ulp of zero.** `far_side_of` took `step = math.ulp(own_star) if own_star
else 5e-324`, so a walk starting from a coordinate value of exactly `0.0`
doubled a denormal: two hundred doublings reach about 1e-263, which is no
distance at all on a segment a millimetre long, and the bracket was never
found. `calculator.Standing` rests with `slide.travel` at 0 and its low
bound at 3 — a bank standing OUTSIDE its bound — and `move('feed', by=-1.0)`
raised instead of stopping, where the HIGH-bound mirror `outside.Outside`
admits zero travel and reports its stop. The walk now takes
`math.ulp(max(abs(own_star), abs(scale)))`, `scale` being the larger
magnitude of the path's two ends, passed by the two CLOCKED callers. A
caller that passes no `scale` gets the value's own ulp exactly as before,
which is what `_Walk._far_side` does: **no running landing moves, and
`tests/running-corpus.json` is byte-identical.** The running walk therefore
keeps the ulp-of-zero step, unfixed and unmeasured, and that is recorded in
`workflow/warts.md` rather than changed here.

The stop itself is then said off the CROSSING and not left to the walk. A
level already AT its limit and pushed further admits ZERO travel — design
section 9 — and `Bounded.clip` now returns `(0.0, start)` as soon as the
crossing is solved at fraction 0. Left to the walk, the low side would admit
half an ulp OF THE LEVEL of travel — `-2.22e-16` for `Standing`, measured —
because the input's own float grid near zero is finer than the level's,
while the high side of the same bound admits exactly nothing; the bound's
two sides would then differ only because the coordinate happens to stand
near zero. Zero travel on both sides is the ratified behaviour and the one a
second runtime can reproduce.

**What this does not touch.** `_Walk._far_side`, `simulation/run.py`,
`tests/running-corpus.json` and every running document are unchanged;
`moves_with`, the clip's threshold, the judgement and the commit are
unchanged; and no tolerance is introduced anywhere.

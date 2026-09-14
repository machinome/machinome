## Why

ADR-109 let a joint's range bound be an expression, and deferred one
thing by name: a bound may not read a SECOND coordinate, because a
joint is class metadata resolved before any qualified id exists, so a
class body has no namespace to name another coordinate in. The
deferral cost the Pascaline nothing. It costs the pin tumbler lock its
whole mechanism.

The originating project is `projects/Locks/Pin_tumbler_lock`. Its
source is a five-pin lock: a key slides into a plug, five key pins ride
the key's cuts and rise and drop over them as the key advances, five
driver pins ride on the key pins under five springs, and the plug turns
only when every one of the five splits lies at the shear line — and
once the plug is turned, the key is captured until the plug returns.
Today the project is a POSE model: `insertion`, `turn` and five
independent `lift_n` drivers, with the contact computed by a Python
module (`simulation/contact.py`) and the interlocks — the guarded turn,
the capture — enforced by a state machine that lives in that module and
again, line for line, in a browser controller under `web/`. Nothing in
the framework says the plug may not turn, and nothing says the key may
not leave: the pose model admits every impossible pose and the project
polices the possible ones itself, twice.

Migrated to `Time.running()`, the pins become coordinates driven by the
key's travel through a law each, and the two interlocks become what
they are: declared ranges. But each is a range whose bound depends on
OTHER coordinates — the plug's turn is bounded by the five lifts, the
key's travel is bounded by the plug's turn — and that is exactly the
form ADR-109 deferred. A gated law does not do it: `turn * aligned(...)`
into the plug leaves the plug still while the `turn` INPUT advances and
its command reports `completed`, which is not a lock that will not
turn; a physical stop is a bound on the plug's coordinate that stops
the input pushing it (ADR-108), and only a bound can say that.

The pilot's brief for this change sets its terms: resolve the semantics
before the syntax — how a bound names what it reads, especially on a
joint declared where a child is placed; how insertion and turning in
one tick stay valid, since freezing a cross-coordinate bound at the
tick's start is not enough; what happens when what a bound reads moves
so as to make a standing position invalid, with no teleport, no clamp
and no penetration; which commands stop, what they report and how a
retry works with no backlog; and what a bound means untimed, at
construction, on restore and in the browser. Use the lock as the
empirical acceptance case, preserve the Pascaline's behaviour, and do
not assume `Bound` is enough because its syntax is small.

## What Changes

- **A range bound may read other coordinates.** Either bound of a
  joint's `(lo, hi)` `range` MAY be `Bound(expression, reads=(...))`:
  a callable applied to the joint's own coordinate and then to each
  coordinate it names, in order, returning a number or an expression in
  `solid_node.math`'s vocabulary. `reads` names coordinates exactly as a
  relation's ends do — a joint or port the declaring class body owns, a
  path through child declarations, a driver of the declaring class —
  checked at class definition and resolved against the joint's
  DECLARER: the node itself for a class-declared joint, the declaring
  parent for a site-declared one. A one-argument callable keeps meaning
  what ADR-109 made it mean.
- **Under a running root a bound that reads other coordinates is a
  CONSTRAINT between the coordinate and what it reads, evaluated ALONG
  the tick's path** rather than frozen at the tick's start: the joint's
  own value in the expression is the committed one (ADR-109's rule, the
  ratchet's tooth), and every other coordinate it reads takes the value
  it has along the path. The stop is located where the constraint is
  first carried outward, by the same search a jump crossing uses, on
  the sub-program that determines what the bound reads, so the committed
  state at the stop satisfies the bound by the same arithmetic that
  located it.
- **The group a constraint stops is every input whose own motion carries
  it outward — through the bounded coordinate OR through what the bound
  reads.** A dependency that moves so as to make a standing position
  invalid is stopped where the constraint becomes active, and the
  standing coordinate does not move: the key captured by the turned
  plug follows from the plug's own bound, with no second declaration.
  Commands on stopped inputs retire `blocked` with the travel they
  admitted, exactly as ADR-108 states; nothing resumes and nothing is
  remembered.
- **Untimed, a bound that reads other coordinates is judged when the
  enumeration closes**, over the values then bound, and an impossible
  pose is refused by name — the joint, the value, the evaluated bound
  and every coordinate it read with its value. It is not judged at the
  moment of binding, because the coordinates it reads are bound in an
  order the author does not control. A coordinate a running simulation
  owns is not judged by the enumeration: the run judged it.
- **The published program carries the bound as it is**: its expression
  names the ids it reads, the identity changes with them, and no
  document version is added. The conformance corpus gains two required
  features — a bound reading another coordinate, and a stop reached by
  the motion of what a bound reads — so the browser worker's cycle in
  the viewer repository has a fixture to be held to; until that cycle
  lands the shipped worker refuses such a document by name.
- **Nothing existing changes meaning.** A number bound, a callable of
  one argument, `None`, `Program.spans`' shape, `Stop`'s shape and every
  command status are untouched; the Pascaline module's ratchet runs
  exactly as it does today.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `joints`: "Joint arguments resolve against the instance at
  realization" admits `Bound(expression, reads=...)` as a range bound
  and states how its reads are named, checked and resolved; "A declared
  range refuses a binding outside it" states when such a bound is
  judged untimed and what its refusal names.
- `simulation`: "A declared range is a physical stop located inside the
  tick" is restated for a bound that reads other coordinates — the
  along-path evaluation, the constraint level, the group that includes
  the inputs moving what the bound reads, the localization and the
  commit; a new requirement states how such a bound is compiled, what
  it may read and what is refused.
- `export`: "A running root's document publishes the compiled program"
  drops the restriction that a span's expression reads its own id
  alone; "The two runtimes share a conformance corpus" adds the two
  features the corpus must exercise.

## Impact

- `solid_node/motion/joints.py`: `Bound`, carried through `_span`
  unevaluated; the bind-time check defers a `Bound` side and records the
  binding for the enumeration's close.
- `solid_node/node/phase.py`, `solid_node/node/assembly.py`,
  `solid_node/motion/couplings.py`: the enumeration records bound-bearing
  bindings and judges them at `_finish_enumeration`, resolving `reads`
  against the declarer through the same path references a relation
  resolves.
- `solid_node/node/declarative.py`: `ChildDeclaration.__set_name__`
  checks a SITE-declared joint's reads against the declaring parent,
  beside the wiring check it already makes there — the one moment that
  class is known, since `_specialize` fires the site joint's own
  `__set_name__` against the specialized child class instead.
- `solid_node/simulation/program.py`: `_compiled_spans` resolves reads to
  qualified ids and compiles the graph over them; the program carries,
  per such bound, the read ids, the sub-program that determines them and
  the candidate inputs; `described()` and therefore `identity` change
  for any root declaring one.
- `solid_node/simulation/run.py`: constraint evaluation along the path,
  detection at each stretch's end, searched localization over the
  sub-program, the generalized pushing test, the commit rule.
- `tools/generate_running_corpus.py`, `tests/running-corpus.json`: two
  required features and a fixture machine that exercises both.
- `tests/running_project/machine.py`, `tests/test_running_stops.py`,
  `tests/test_joints.py`, `tests/test_running_document.py`,
  `tests/test_running_corpus.py`: the red-first suite listed in
  `tasks.md`.
- `docs/architecture.md`, `docs/adrs/`: one ADR after implementation;
  ADR-109's deferral consequence amended; the "a range bound may not
  name a second coordinate" gap removed from the overview.
- Originating project `projects/Locks/Pin_tumbler_lock` (its own
  repository, its own cycle): migrated to `Time.running()` against this
  worktree as the empirical acceptance; the migration plan is in
  `design.md`.
- `solid-node-viewer` (its own repository, its own cycle, after this
  one): the worker's bound check and evaluation, held to the regenerated
  corpus.

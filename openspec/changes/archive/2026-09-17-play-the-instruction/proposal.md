## Why

**A clocked stroke cannot be WATCHED.** The originating project is
`projects/Calculators/Curta-Type-I-3x` (branch `direct-operation`, HEAD
`9fb725f`), whose third sibling `simulation/clocked.py:ClockedCurta` builds at
`_build/clocked_curta/viewer.json` as a version 8 document and declares, on
line 95, exactly what its `Time.running()` sibling declares on line 83:

```python
instructions = {'Turn crank': Instruction(by={'crank_rotation': 360}, duration=2)}
```

The pilot's requirement, verbatim: *"I need it to be animated fast between
states with smooth transition just like the fast_curta, but holding state."*
The `fast_curta` sibling (`simulation/curta.py:33-42`, seven instructions with
durations) gets that because a POSED document's instruction is played by the
viewer as a ramp of its drivers over `duration`, one pose per frame
(`solid-node-viewer`, `solid_node_viewer/widget/src/drivers.ts:64-85`,
`Ramp.valueAt`). The clocked sibling does not, because ADR-128
§"Instructions are published in the version 5 shape, with no meaning"
publishes the table and gives it none:
`sim.trigger` is refused BY NAME on a clocked `Sim`
(`solid_node/simulation/sim.py:523`, through `_not_clocked`,
probed on this worktree), and the viewer lists the buttons disabled. The
project's own record says it in one line: *"The instruction remains disabled
metadata under the current clocked contract"*
(`simulation/docs/clocked-curta-2026-09-17.md`, "Limits").

So the ONLY way to turn that crank today is `sim.move('crank_rotation',
by=360)`: one request, the crank jumps a whole turn, every tooth and carry
fires, the tree poses ONCE at the end, and nothing is seen moving. The machine
is fast enough to be watched and cannot be — the same record measures
**0.07875 s** for a complete clocked stroke in Python (median of 20) and
**36.95 ms** in
Chromium — and the gap is recorded as the open wart *"the instruction's
meaning under a clocked root"* (`workflow/warts.md:3285-3292`, "Open, waiting
on the viewer cycles"). This cycle closes it.

The same record measures the alternative and rules it out: one stroke **split
into 20 requests/poses** costs **1.56363 s** in Python and **647.7 ms** in the
browser, against 0.07875 s and 36.95 ms for the one request that does the same
work. Slicing an instruction into per-frame requests puts the machine in the
frame loop, which is the running Curta's structure and the thing the clocked
discipline exists to replace.

## What Changes

- **An instruction under a clocked root MEANS one request.** `sim.trigger(name)`
  stops being refused and becomes the one verb of that refused list with a
  meaning: `by={id: travel}` makes `move(id, by=travel)` and `targets={id:
  value}` makes `move(id, to=value)`, in design units, through the same
  `_instruction` and `_driver` resolution every other base uses and the same
  unknown-name message. It RETURNS the request, so a caller that pressed a
  button holds exactly what a caller that moved the input holds.
- **An instruction under a clocked root names EXACTLY ONE driver**, refused at
  the machine's compile — beside the existing refusal of one naming a State
  (`solid_node/simulation/clocked.py:421-430`) — by name, naming the
  instruction, the inputs and the rule. This is not a new rule: a request
  names exactly one moving input (the ratified requirement "A clocked
  simulation solves a request path event by event"), and `Instruction`'s own
  docstring already says sequencing "is the beginning of a program, and that
  is the G-code layer's job — faking it here would have to be unfaked later"
  (`solid_node/simulation/instruction.py:20-24`). The consequence is worth
  stating plainly: every instruction a version 8 document carries is one a
  consumer can PLAY.
- **`duration` is carried and means nothing to the machine.** A request is a
  path, not an interval. The framework keeps validating it as it does today
  (finite, non-negative, `instruction.py:53-58`), publishes it as ADR-128
  already publishes it, and reads it nowhere. What it says is how long a
  CONSUMER draws the transition.
- **A `Request` reports BOTH ENDS of the path it travelled.** Today
  `Request(input, by, to, commits, admitted, stops)`
  (`clocked.py:1589-1616`) does not carry where the input STOOD: `to` is
  `None` for a `by=` request, `by` is the ASK and in DESIGN units, and the
  start is only in a bank the caller may not have kept. Probed on this
  worktree: `move('crank', by=740.0)` over the `Calculator` fixture returns
  `{'input': 'crank', 'by': 740.0, 'to': None, 'admitted': 740.0, ...}` with
  commits at `360.0` and `720.0` and nothing saying the path began at `0`. Two
  fields are added, `origin` and `end`, taken VERBATIM from the bank and
  therefore in the input's NATIVE units — the units every `Commit.value`
  already speaks. Nothing else is added: `Commit` already carries the landing,
  the target ids, the values written and the firing order
  (`clocked.py:1552-1585`), which is everything a drawer needs and was checked
  rather than assumed.
- **The document changes NOTHING.** No field, no key, no version bump, no
  producer change. Version 8 already carries `instructions` in the version 5
  shape and `clocked.commits`; the meaning is stated by the simulation
  capability and executed by the machine the document already publishes. The
  export requirement's sentence "This version SHALL give a published
  instruction NO execution meaning" is the one thing that moves, and the
  scenario that pins it becomes "the document is byte for byte the one that
  root published when an instruction had no execution meaning".
- **The corpus records a `trigger` step**, so the viewer's replay pins what an
  instruction MEANS and not merely that a button exists. No clocked fixture
  declares an instruction today except the refusal fixture
  (`tests/clocked_project/unsupported.py:156-166`), so the Curta-shaped
  `Calculator` gains two — `'Stroke': Instruction(by={'crank': 360.0},
  duration=2.0)` and `'Set four': Instruction({'operand': 4}, duration=0.5)` —
  and the generator's inventory gains both forms. The corpus stays EXACT,
  `"tolerance": {"float": 0.0}`. `tests/clocked-corpus.json` and
  `tests/clocked_documents/calculator.json` are regenerated; the viewer
  consumes the regenerated file in ITS own cycle, in its own repository.

## Capabilities

### New Capabilities

None. An existing declaration gets a meaning under a third base, an existing
value object gets two fields, and an existing conformance corpus gets a fourth
script verb.

### Modified Capabilities

- `simulation`: TWO MODIFIED requirements — "Instructions carry design-unit
  targets" (what triggering means under a clocked root, the one-input rule,
  the duration's silence) and "A clocked simulation solves a request path
  event by event" (`trigger` leaves the refused cadence list; `move`'s value
  object reports both ends of its path).
- `export`: TWO MODIFIED requirements — "A clocked root's document publishes
  its compiled machine" (a published instruction now MEANS one request; the
  document does not change; an instruction naming none or several drivers
  reaches no document) and "The two runtimes share a clocked conformance
  corpus" (the `trigger` script verb, the recorded path ends, the two new
  inventory entries).

## Impact

- `solid_node/simulation/clocked.py`: `Request` gains `origin` and `end`
  in `__slots__` and `__init__`; `Clocked.move` passes the two floats it
  already holds (`origin` at line 2063, the clipped `target` at line 2090,
  returned at line 2145);
  `compile_clocked`'s instruction loop gains the arity refusal beside the
  State one.
- `solid_node/simulation/sim.py`: `trigger()` drops `_not_clocked` and
  dispatches to the clocked executor exactly as `move()` does, keeping
  `_instruction` and `_driver` as the resolvers so every message shape is the
  one the running and untimed paths already give.
- `tools/generate_clocked_corpus.py`: a `trigger` script verb recorded through
  the same `apply_step` shape, `origin`/`end` in a recorded request, two
  `REQUIRED` entries.
- `tests/clocked_project/calculator.py` (two instructions),
  `tests/clocked_project/unsupported.py` (a two-driver instruction),
  `tests/clocked-corpus.json` and `tests/clocked_documents/calculator.json`
  regenerated; tests in `tests/test_clocked_sim.py`,
  `tests/test_clocked_refusals.py`, `tests/test_clocked_corpus.py`,
  `tests/test_clocked_document.py`.
- `docs/scenarios.rst` (the clocked sections: `trigger` leaves "What a clocked
  model refuses today", and an instruction's meaning is stated),
  `docs/api-reference.rst`, `HISTORY.rst`.
- One ADR, candidate **ADR-129** (NODE), extracted after implementation, which
  AMENDS ADR-128 §"Instructions are published in the version 5 shape, with no
  meaning" and closes the wart at `workflow/warts.md:3285-3292`.

### Non-goals

Each is named in `design.md` with its reason.

- **The viewer.** Playing a returned request over the instruction's duration,
  one pose per frame, with no machine work in the frame loop, is
  `solid-node-viewer`'s own repository and its own cycle. Nothing here touches
  it, and nothing here states what a frame is.
- **Any frame, tick, cadence or clock in the framework.** The framework never
  learns what a frame is.
- **Slicing an instruction into per-frame requests.** Rejected by the pilot and
  measured against above.
- **Sequencing several inputs from one instruction**, under any base. Refused
  here rather than designed, because no project has written one.
- **`Time.elapsed()`, `Time.running()`, the running instruction path, document
  versions 1..7, the running corpus, `controls`.** Untouched, asserted by diff
  and by fixture.
- **The Curta's own edits.** The project drops its unneeded `Time.elapsed()`
  line and wires its button itself, in its own repository.

## Why

An assembly's `children` list is empty inside its own `render()` and, on
the first pass over a tree, inside its own `simulate()`; a loop over it
there does nothing, and nothing says so. Originating project:
`projects/Robots/AlbertPro` (branch `frames-and-mates`). Finding,
`workflow/warts.md`, "AlbertPro (2026-09-07, simulate the Albert
quadruped)", first Framework entry:

> **`self.children` is empty during `simulate()`, and iterating it fails
> silently.** `LowerLeg.simulate()` was written as `for piece in
> self.children: piece.rotate(self.knee.value, AXIS)`. The port was
> bound and correct, the list was empty, the loop applied nothing, and
> nothing raised — the shin simply never turned about its knee, and the
> published model was a robot whose knees did not bend. Every contract
> passed, because a test calls `set_state` before measuring and by then
> the children are linked; only a snapshot showed it. The workaround is
> to address the declared attributes (`self.near`, `self.far`), which
> works in both phases, and that is what
> `projects/Robots/AlbertPro/simulation/leg.py` does. A documented
> empty-during-simulate contract, or a `.children` that raises there
> rather than reading as empty, would turn a silent wrong model into an
> error. This is the one worth filing.

The 2026-09-14 standing triage planned it as this change, never started.

**Reproduced on the bench `fix-warts-3` at `d21f6c6`** (design.md,
Context). A declarative assembly declaring two cubes and a `knee` driver,
whose `simulate()` rotates each of `self.children` by `self.knee`: after
`set_state(knee=30.0)` its `simulate()` saw 0 children and neither cube
carries a rotation; the same class looping over `(self.near, self.far)`
rotates both by 30. A second `set_state(knee=45.0)` still saw 0. After
`assemble()`, `set_state(knee=60.0)` saw 2 and rotated the cube by 60: the
read's answer depends on whether something has presented the node
already, which is why a test passes and the published document, made by a
walk that never presents, does not move. `InternalNode.present()` and
`materialize()` are the only framework code that assigns `children`
(`machinome/node/internal.py`); every phase of a pass runs before either.

**A second, silent sighting in the catalogue.** Every `self.children`
read in project model code (outside tests and tools) is in
`projects/3DPrintedClocks/simulation/wall_clock_*/clock.py`, inside
`render()` or a property `render()` calls, setting `part.color` on each
child. Measured against the bench through the loader's own default
binding and one enumeration: 18 reads in eight clocks (12, 25, 28, 32,
36, 37, 39, 40) are reached, every one inside a `render()` phase, and
every one sees an empty tuple. Clock 12's reads a child's list
(`self.numerals.children` inside `Dial.render()`); the other seventeen
read the assembly's own. (Of the nineteen own-list reads the campaign's
survey counted, the two not reached are clock 17's `islands` property,
read only by its test after assembly, and clock 36's `WindingKey`, a
class its tree never instantiates.) In seven of the eight clocks no
colour the loop meant reaches its parts (60 dial islands in clock 12;
dial supports, pulley parts, winding-key parts, standoffs or raised
detail in 25, 28, 32, 36, 37 and 39 — 40 parts), and the bench's
serialized document carries
`color: None` for each, as the project's published `viewer.json` of
10 September already did. In clock 40 the colours reach the parts only
because its part classes also declare the same colour as a class
attribute; its three loops are dead code. A render-phase read can never
see the children: `render()` is what decides them. That is why the
render read never works, and why the simulate read works only on a pass
after something has presented the node.

## What Changes

- **A read of an internal node's `children` inside a lifecycle phase,
  before anything has assigned them, is refused by name.**
  `InternalNode.children` becomes a property over the value
  `present()`/`materialize()` assign. When nothing has been assigned and
  an assembly's `render()` or `simulate()` phase is running, the read
  raises `StructureError` — the error `omit()` already raises in
  `simulate()` — naming the assembly whose phase is running, the phase,
  what it read (`self.children` or `<child>.children`), why the list is
  not there yet, and what to address instead: the declared children by
  their attributes (`self.near, self.far, ...`), or, for a node that
  declares none, its own `render()`, which builds them.
- **Unchanged:** a read after the node has been presented or prepared,
  in any phase or none (AlbertPro's own tests read `node.children` after
  `set_state`, outside any phase); a read outside any phase before
  linking, which still answers `()`; a leaf's `children`, which stays the
  base class's empty tuple; `InternalNode.brep`'s own refusal outside a
  phase; the assignment sites and what they assign.
- `docs/concepts/rest-and-motion.rst` says that `render()` and
  `simulate()` address children by their declared attributes and that
  reading `children` in either is refused; `docs/architecture.md`'s
  declarative-internal-node paragraph records the refusal beside
  `omit()`'s; one changelog bullet under `Unreleased`.

**Deliberately out**, with the reason:

- populating `children` earlier. For `render()` it is impossible —
  `render()` is what decides the children — so the render-phase read
  must be refused whatever happens to the simulate-phase one. Populating
  them before `simulate()` as well (in `_run_phase`, after the link it
  already makes) would let AlbertPro's original loop work, but it is the
  larger change — the refusal is needed anyway, plus a second assignment
  site and a new guarantee every walker would then rely on — and it
  would give `simulate()` and `render()` two different answers to the
  same question. design.md, Decision 1, measures both;
- a read outside any phase before linking (a test reading
  `Node().children` before assembling it): no phase is running to name,
  and the finding, the catalogue and the brief concern lifecycle reads.
  It keeps answering `()`;
- a legacy render (one that reads a driver, re-run per binding): a
  `simulate()` read after the node was presented sees the last
  presentation's list, as today;
- the projects. AlbertPro already addresses its attributes and is run,
  not changed. The eight clocks are run, not changed; with this change
  each of them is refused at load until its reads are rewritten to
  address declared attributes (design.md, Open Question 1).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `node-model`: one requirement added, "An internal node's children are
  refused before they are linked" — a read of an internal node's
  `children` inside an assembly's `render()` or `simulate()` before the
  node's children have been assigned by preparation or presentation is
  refused naming the assembly, the phase, the read and the declared
  attributes; every read after that assignment, and every read outside
  any phase, answers as before. Four scenarios.

## Impact

- Code: `machinome/node/internal.py` (`InternalNode.children` property
  and setter; one private message helper). Nothing else changes:
  `present()` and `materialize()` keep their `self.children = children`,
  which the setter stores where it is stored today, and
  `machinome/model.py`'s production assignment likewise.
- Tests: a new `tests/test_children_reads.py`. The full suite on the
  unmodified bench with the refusal installed from outside refused
  nothing (4623 passed, 4 skipped, 6611 subtests; design.md, Context): no
  framework code a test reaches reads `children` inside a phase before
  linking, and no existing test is edited.
- Projects: AlbertPro unchanged (its `leg.py` addresses attributes; its
  tests read `children` outside any phase). Eight 3DPrintedClocks models
  (12, 25, 28, 32, 36, 37, 39, 40) are refused at load by this change
  until their 18 reached reads are rewritten; that rewrite is a project
  change outside this cycle, valid against both today's framework and
  this one (design.md, Open Question 1).
- Documents, published artifacts, bank ids: unchanged for every model
  that loads.
- Manual: `docs/concepts/rest-and-motion.rst`; `docs/architecture.md`;
  `docs/project/changelog.rst`.
- No ADR (design.md, Decision 4).

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 3, `children-refuse-early-reads`,
validated in AlbertPro, with the 3DPrintedClocks clocks as the second
sighting. Whether the refusal may make eight clock models fail at load
until the project is rewritten is recorded as design.md's Open Question 1
for the orchestrator's review, with a recommendation; the artifacts
deliver the recommended option.

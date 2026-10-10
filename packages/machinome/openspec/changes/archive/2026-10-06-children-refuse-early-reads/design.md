## Context

### Where `children` is set, and which phases run before it

`AbstractBaseNode` declares the class attribute `children = tuple()`
(`machinome/node/base.py:531`). Exactly three places assign the instance
attribute, each AFTER the walk it belongs to:

- `InternalNode.present(children)` (`machinome/node/internal.py:129`),
  called by `assemble()`'s presentation, after it has assembled every
  child (`internal.py:147`);
- `InternalNode.materialize(children)` (`internal.py:162`), called by
  native preparation (`_prepare`), after it has prepared every child
  (`internal.py:170`);
- `machinome/model.py:476`, the production consumer's `prepare`, from the
  rest structure a rigid consumer already validated.

The lifecycle every walker reaches through `render()`
(`machinome/node/assembly.py`) runs before any of them:

- `_rest` (`assembly.py:40`) pushes a RENDER phase (`machinome/node/phase.py`)
  and runs the author's `render()` once per instance; on a declarative
  class the wrapper `_declarative_render` (`internal.py:14`) turns its
  `None` into the declared children AFTER the author's code returns. The
  children do not exist as a list while `render()` runs: `render()` is
  what decides them.
- `_run_phase` (`assembly.py:90`) calls `_rest`, then
  `assembly._link_children(...)` — which sets each child's `_parent` and
  name and assigns nothing on the assembly — then pushes a SIMULATE phase
  and runs `simulate()`.
- `_rest_children` (`assembly.py:220`), the rest-only walk `set_state`,
  `clear_state` and `qualified.drive_tree` take, runs `_rest` (a RENDER
  phase) and links; it assigns nothing either.

So on a declarative node and on a hand-written `render()` node alike, a
read of `self.children` inside `render()` always answers the class's
`()`, and inside `simulate()` answers `()` on every pass until something
has run `present()` or `materialize()` on the node; after that it
answers the list that call assigned. The loader's default binding
(`simulation.enumeration.qualified_drivers` → `drive_tree`), the
serializer's symbolic pass (`serializer.symbolic_document` → `drive_tree`)
and `set_state` all enumerate before anything presents, which is why a
published document carries no motion from such a loop while a test that
assembled first sees it. `InternalNode.brep` (`internal.py:121`) already
refuses, outside any phase, to answer before the children are linked.

### Reproduction at `d21f6c6`

Probes in the campaign scratchpad
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle3/`),
each run with the bench first on `PYTHONPATH`; `machinome.__file__`
printed `/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.
The scratchpad is not durable: `evidence.md` carries the probes' sources
(tasks §1.3).

**The finding** — `repro_project/repro.py`, run from `repro_project/`
(its `pyproject.toml` gives the fixture classes a project root), with
`tests.meta_project.parts.Cube` as the part. `LowerLeg` declares
`knee = Driver(default=0.0, range=(-90.0, 90.0), unit='deg')`,
`near = Cube()`, `far = Cube()`, and `simulate()` rotates each of
`self.children` by `self.knee` about x; `AddressedLowerLeg` is the same
class looping over `(self.near, self.far)`:

| Step | `simulate()` saw | `near` rotations |
|---|---|---|
| `LowerLeg()`, `set_state(knee=30.0)` | 0 children | `[]` (`far`: `[]`) |
| `AddressedLowerLeg()`, `set_state(knee=30.0)` | — | `[['r', '30.0', [1, 0, 0]]]` (`far` the same) |
| the `LowerLeg`, `set_state(knee=45.0)` | 0 children | `[]` |
| the `LowerLeg`, `assemble()`, then `set_state(knee=60.0)` | 2 children | `[['r', '60.0', [1, 0, 0]]]` |

Nothing raised in any step. Running the same script with the proposed
refusal installed from outside (`refuse_probe.py`, below; `repro.py
--refuse`) raises at the first step: `StructureError: LowerLeg
'LowerLeg': children read during simulate() of LowerLeg 'LowerLeg' before
they are linked` (the probe's provisional wording; Decision 3 has the
proposed one).

**The catalogue's reads** — `probe_children.py`, run from
`projects/3DPrintedClocks` with `PYTHONPATH=<bench>:<project>` over the
eight clocks the campaign's survey names and clock 12. It replaces
`AbstractBaseNode.children` by a logging data descriptor that answers
exactly what the plain attribute answers (the instance's assigned value
or the class's `()`), instantiates the root, runs the loader's default
binding (`qualified_drivers(root)`: every driver at its default, the
rest-only walk, one enumeration), then one more `root.render()`, and
records every `children` read made from project code or made from
anywhere while a phase is running. Output `probe-summary.txt`:

| Clock | Read (`clock.py` line) | Phase | Saw | Children after | Colour reached |
|---|---|---|---|---|---|
| 12 | 104, `self.numerals.children` in `Dial.render()` | render (Dial's) | 0 | 60 islands | 0 of 60 (`DIAL_DETAIL`) |
| 25 | 121 (`RaisedDetail.parts`), 135, 282, 291 | render (own) | 0 | 4, 4, 3, 2 | 0 of 13 |
| 28 | 232, 242 | render (own) | 0 | 3, 1 | 0 of 4 |
| 32 | 120 | render (own) | 0 | 4 | 0 of 4 |
| 36 | 81, 234 | render (own) | 0 | 2, 3 | 0 of 5 |
| 37 | 115, 267, 276 | render (own) | 0 | 4, 3, 2 | 0 of 9 |
| 39 | 224, 232 | render (own) | 0 | 3, 2 | 0 of 5 |
| 40 | 99, 272, 281 | render (own) | 0 | 4, 3, 2 | 9 of 9, all through a class-level `color` on the part class |
| 17 | — | — | — | — | (its `islands` property, `clock.py:138`, is read only by `test_clock.py` after assembly) |

No read in the second enumeration and no framework read inside a phase
was recorded in any clock. Clock 36's third read (`clock.py:243`) is in a
`WindingKey` class its tree never instantiates.

`probe_document.py` serializes a root through
`machinome.core.serializer.serialize_node` — the walk a build's viewer
document is made of — after the same default binding, with node names in
place of model references (nothing built, nothing written to the
project). Against the bench, clock 25's `raised_detail/detail_*`,
`dial/supports/support_*`, `winding_knob/{body,handle}` and
`movement/pulley/{wheel,holder_back,holder_front}` all carry
`color: None`, while its `standoffs/*`, whose `render()` addresses
attributes, carry `#b08d2d`; the project's published
`_build/wall_clock_25/viewer.json` (10 September) reads the same.
Clock 40's same parts carry `#4a4d50`, `#111111` and `#9be300`: its
`DialSupportPart`, `PulleyPart` and `WindingKeyPart` declare those
colours as class attributes (`wall_clock_40/parts.py:59`, `:72`, `:87`).

**The framework's own lifecycle reads** — `refuse_probe.py`, loaded as a
pytest plugin (`-p refuse_probe`), installs the proposed refusal on
`InternalNode.children` from outside the bench and logs every refusal.


### Suite under the probe

The full suite on the unmodified bench with the refusal installed
(`pytest -p refuse_probe -q -p no:cacheprovider` at the bench root,
`PYTHONPATH=<bench>:<scratch>`): **4623 passed, 4 skipped, 6611 subtests
passed in 663.57 s; nothing refused, `refusals.log` never created.** A
check in the same interpreter confirmed `InternalNode.__dict__['children']`
is the probe's `property` while pytest runs. So no framework test, and no
framework code any test reaches in-process, reads an internal node's
`children` inside a phase before linking. (A build a test runs in a
subprocess does not carry the probe; the suite's in-process paths are
what it measures.)

### The projects under the probe

- AlbertPro, against the bench, unmodified: `machinome test --mesh
  simulation/albert.py` — 35 passed in 11.85 s (mesh engine, volume
  epsilon 0 mm³), 14.9 s wall; `python -m pytest -q -p no:cacheprovider
  simulation/test_frames.py` — 12 passed in 3.65 s. With the refusal
  installed (`import refuse_probe` before `machinome.cli.manage()`, which
  runs the tests in-process, and `-p refuse_probe` for pytest): 35 passed
  in 10.84 s and 12 passed in 3.30 s, nothing refused. `git status
  --short` empty before and after.
- The clocks, loaded with the refusal installed (`probe_document.py`
  after `import refuse_probe`): clock 17 loads; each of 12, 25, 28, 32,
  36, 37, 39 and 40 is refused at its first render-phase read
  (`wall_clock_12/clock.py:104` in `Dial.render()` on `numerals`;
  `wall_clock_25/clock.py:121`; `28:242`; `32:120`; `36:81`; `37:115`;
  `39:232`; `40:99`), each inside `render()`. `git status --short` of the
  project unchanged (` M screenshots/wall_clock_03.png`, pre-existing).

### The originating project at `d21f6c6`

`projects/Robots/AlbertPro`, branch `frames-and-mates`, `2c34ebf`, clean
tree. `simulation/leg.py` places the shin through mates and addresses
its declared attributes; nothing in `simulation/` reads `children`
outside the tests (`test_frames.py:112`, `test_albert.py:122`, `:135`),
which walk the tree after `assemble()` or the test runner's preparation,
outside any phase. Its two documented runs are green against the bench
with and without the refusal installed ("The projects under the probe").

## Goals / Non-Goals

**Goals:** a read of an internal node's `children` that can only answer
"none yet" — inside a `render()` or `simulate()` phase, before anything
has assigned them — is refused by name, at the read, saying what to
address instead; every other read answers exactly as today.

**Non-goals:** populating `children` earlier; reads outside any phase;
legacy renders' staleness; the projects; any new public name.

## Decisions

### 1. Refuse; do not populate earlier

Two remedies were weighed against the measurements.

- **Refuse (taken).** One property on `InternalNode` refuses the read in
  both phases while nothing has been assigned.
- **Populate before `simulate()`.** `_run_phase` already holds the rest
  children and links them before `simulate()`; assigning
  `assembly.children` there would make AlbertPro's original loop work.
  It cannot help `render()`: inside `render()` there is no list to assign
  — `render()` decides it, a declarative wrapper computes it from the
  omission marks after the author's code returns, and a hand-written
  `render()` returns a list nobody has yet. The render-phase reads are the
  ones the catalogue actually has (eight clocks, every read), so the
  refusal is needed whichever way the simulate-phase read goes. Populating
  as well adds a second assignment site, a guarantee every walker between
  `_run_phase` and presentation would come to rely on (`InternalNode.brep`
  would answer where it refuses today), and a contract in which
  `self.children` means the list in `simulate()` and nothing in
  `render()`. It is safe as far as measured, and it is not the smaller
  change.

Under the refusal, a `simulate()` that reads `self.children` raises on the
first pass of every entry point — the loader, the serializer,
`set_state`, `assemble()` — because each enumerates before anything
presents; the author meets it at once, in the place the published model
was silently wrong.

### 2. Where: `InternalNode.children`, a property over the assigned value

In `machinome/node/internal.py`:

```python
@property
def children(self):
    """The children preparation or presentation last linked under this
    node: what present() or materialize() assigned. ..."""
    linked = self.__dict__.get('children')
    if linked is not None:
        return linked
    current = _phase.current()
    if current is None:
        return ()
    raise _early_read(self, current)

@children.setter
def children(self, children):
    self.__dict__['children'] = children
```

with `from . import phase as _phase` (the module imports nothing from the
node layer, as its own docstring says, so no cycle).

- The setter stores the value under the instance-dictionary key it is
  stored under today, so `present()`, `materialize()` and
  `machinome/model.py:476` are unchanged, and `_child_name_index`'s skip
  of the `children` key (`base.py:1256`) still applies.
- The class attribute `children = tuple()` on `AbstractBaseNode` stays:
  a leaf's `children` is not an `InternalNode`'s and keeps answering `()`
  in every phase (a walker reaching a leaf inside a phase must not be
  refused).
- The condition is "a phase is running", any assembly's, not "this
  node's own phase": clock 12 reads a child's list inside the parent's
  `render()`, which is the same silent read.
- `FusionNode` is an `InternalNode`; it has no phase of its own, so its
  `children` is refused only when read inside an enclosing assembly's
  phase before linking, which is the same defect.

### 3. The error: `StructureError`, naming the read and what to address

`StructureError` (`machinome/node/declarative.py`, a `RuntimeError`) is the
error `omit()` raises in `simulate()` (`base.py:781`) and a render that
changes its structure raises; it is not new vocabulary. Not
`AttributeError`: `getattr(node, 'children', ())` and `hasattr` would
swallow it and answer the silent `()` this change removes.

A private module function `_early_read(node, phase)` in `internal.py`
builds it. With `owner = phase.assembly`, `spelled` = `self.children` when
`node is owner` and `{node.name}.children` otherwise, and `prefix`
likewise `self` or `node.name`:

```text
{Owner} '{owner.name}' read {spelled} in {phase.kind}(): the framework
links an assembly's children after the tree's render() and simulate()
have run, so here the list is not there yet and a loop over it does
nothing. {instead}
```

`{instead}`:

- when `declared_children(type(node))` is not empty: `Address the
  children by the attributes that declare them: {prefix}.{a}, {prefix}.{b}.`
  in declaration order (a repeated or listed declaration is named by its
  attribute, which holds the list);
- otherwise: `{Node} declares no children: they are the list its own
  render() returns, and it is there that they are addressed.`

AlbertPro's original loop then reads: `LowerLegFL 'lower' read
self.children in simulate(): the framework links an assembly's children
after the tree's render() and simulate() have run, so here the list is
not there yet and a loop over it does nothing. Address the children by
the attributes that declare them: self.near, self.far, self.knee_servo.`
Clock 40's `DialSupports` reads `... read self.children in render(): ...
self.support_0, self.support_1, self.support_2, self.support_3.`; clock
12's `Dial` reads `... read numerals.children in render(): ... DialDetail
declares no children: they are the list its own render() returns, ...`.

### 4. No ADR

A refusal of a read that can only answer wrongly, inside the lifecycle
ADR-002, ADR-023 and ADR-066 already define, in the shape of `omit()`'s
`StructureError` in `simulate()` (ADR-066, "Structure stays at rest") and
`InternalNode.brep`'s refusal before linking. It adds no mechanism and
moves no responsibility.

### 5. Spec: one requirement added to `node-model`

"An internal node's children are refused before they are linked", with
four scenarios: the simulate-phase read (the finding), the render-phase
read (the clocks), a read after linking and a read outside any phase
(unchanged). No existing requirement is modified; "Template-method render
lifecycle" and "Tree naming from parent attributes" stand as written.

### 6. Manual and changelog

- `docs/concepts/rest-and-motion.rst`, after the `simulate()` paragraph
  and before the code block: two sentences — both methods reach a child
  through the attribute that declares it (`self.crank`, `self.caps`), as
  the example does; `children` is the framework's linked list, linked
  after both have run, and reading it inside either is refused naming
  the attributes to use.
- `docs/architecture.md`, the declarative-internal-node paragraph that
  says "`omit()` raises in `simulate()`": one sentence, a read of an
  internal node's `children` inside a phase before `present()` or
  `materialize()` has assigned it raises `StructureError` naming the
  declared attributes.
- `docs/project/changelog.rst`: one bullet under `Unreleased` naming
  `children-refuse-early-reads`.

## Proof plan

- **Red** (tests/test_children_reads.py, tasks §2): the simulate-phase
  read (AlbertPro's shape) and the render-phase reads (the clocks' two
  shapes: an own list, and a child's list inside the parent's
  `render()`) raise `StructureError` naming the owner, the read, the phase
  and the attributes. On the unmodified bench each runs without raising
  and the loop applies nothing.
- **Guards** (green before and after): the attribute-addressed loop
  rotates both parts; a read after `assemble()`, inside a later phase and
  outside any, answers the linked list; a never-linked node read outside
  any phase answers `()`; a leaf's `children` inside a phase answers
  `()`; `InternalNode.brep` outside a phase before linking keeps its
  `RuntimeError`.
- **Framework reads**: the full suite, which under the outside probe
  measured the framework's own lifecycle reads (Context).
- **Originating project**: AlbertPro's two documented runs before and
  after, at their counts, its tree unchanged.
- **Second sighting**: the eight clocks loaded before (load, colours as
  in Context) and after (each refused at load, naming its assembly, the
  phase and the attributes); clock 17 loads unchanged after.

## Risks / Trade-offs

- **Eight catalogue models stop loading.** Clocks 12, 25, 28, 32, 36, 37,
  39 and 40 read `children` in `render()`; with this change each is
  refused at its first load until its reads are rewritten. Seven of them
  publish uncoloured parts today because of those reads; clock 40's are
  dead code. Open Question 1.
- **A project read this cycle cannot see.** A read inside a phase reached
  only by a model, branch or parameter set the probe did not load would
  now raise where it silently did nothing. Every such read was a no-op:
  the refusal fires only where the answer was `()` on an `InternalNode`
  inside a phase. The campaign's closing load of every catalogue model
  (`scripts/load-projects`) is where any other is found.
- **A walker reading `children` inside a phase.** The full suite under
  the probe refused nothing (Context); a framework read inside a phase
  before linking that no test reaches would be refused too, and could
  only have been reading the silent `()`.

## Migration Plan

A model that reads `children` inside `render()` or `simulate()` replaces
the read with the declared attributes, as the error names them —
`for part in (self.wheel, self.holder_back, self.holder_front)` in place
of `for part in self.children`. The rewrite is valid against the
framework before this change too, so a project can make it first.

## Open Questions

1. **The refusal in `render()` makes eight clock models fail at load.**
   Answered by the orchestrator under the mandate, or deferred to the
   pilot. The choices, each of which closes AlbertPro's finding:
   - (a) **refuse in both phases** (delivered here). The clocks' 18 reads
     become errors naming the attributes; the clocks need a companion
     change in `projects/3DPrintedClocks` (each loop over the declared
     attributes; for clock 12, the islands coloured where `DialDetail`
     builds them, or by a class-level colour on its island class), made
     in that repository under its own records. That rewrite also gives
     40 parts in seven clocks the colour their author wrote, a visible
     change to those published models. Because it is valid against
     today's main, it can land first; this change should not reach
     local `main` before it, or eight models fail to load there.
   - (b) **refuse in `simulate()` only.** No project changes; the
     render-phase reads, the only ones the catalogue has, stay silent and
     the 40 parts stay uncoloured.
   - (c) **populate before `simulate()`, refuse in `render()`.** Same
     project impact as (a); larger (Decision 1).
   - (d) **refuse in `simulate()`, warn in `render()`** (a
     `FutureWarning` per class, as a legacy render is warned). The clocks
     keep loading, uncoloured, and print a warning; a compatibility path
     with a later step to an error.

   Recommendation: (a), with the companion clocks change authorized as
   a separate project cycle. The render read is the one that is always
   wrong, and the measurement shows it costing real output in seven
   published models; a warning leaves those models wrong.

   Answered by the orchestrator at review (6 October 2026): (a). The
   companion change is made in this cycle as direct project work, on a
   branch `children-reads` of `projects/3DPrintedClocks` in a worktree
   of that repository (tasks §4.3), so the project's checkout does not
   move and the pilot decides its merge; until that branch is merged,
   the eight clocks refuse to load against this framework, which the
   campaign note records under "Deferred to the pilot". As applied, the
   branch carries clocks 12, 25 and 28 (`58ff90e`); the edits of the other
   five were refused by the harness and are not made (evidence.md, §4.3).
2. **Reads outside any phase stay silent.** A helper walking
   `node.children` on a root nobody has assembled reads an empty tree
   and passes vacuously. No measured case (AlbertPro's and the clocks'
   test walkers run after assembly); left as today, and recorded in
   `warts.md` for triage (tasks §7).

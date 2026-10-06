Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Every framework command runs as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`;
every project command as
`env -C <project> PYTHONPATH=<bench>:<project> /home/asa/devel/machinome/.venv/bin/<tool> ...`
with `<Albert>` = `/home/asa/devel/machinome/projects/Robots/AlbertPro`
and `<Clocks>` = `/home/asa/devel/machinome/projects/3DPrintedClocks`.
`<scratch>` is the campaign scratchpad's `cycle3/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle3/`):
`repro_project/` (`pyproject.toml`, `repro.py`), `probe_children.py`,
`probe_document.py`, `summarize.py` and `refuse_probe.py`. `repro.py` runs
from `<scratch>/repro_project` with `PYTHONPATH=<bench>:<scratch>`;
`probe_children.py` and `probe_document.py` run from `<Clocks>`. One test
run of ours at a time (they share `tests/_build`). Every test marked RED
in section 2 is run and seen red, for the reason it names, before the
code that turns it green. Edit nothing in any project. Record every
command and its result in `evidence.md` as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench).
- [ ] 1.2 Run `tests/test_declarative_render.py tests/test_animator_tag.py
  tests/test_node_naming.py tests/test_traversal_naming.py` with `pytest
  -q -p no:cacheprovider`; record counts and wall time.
- [ ] 1.3 Run `<scratch>/repro_project/repro.py` (expect design.md's
  Context table: 0, 0, 2 children seen; no rotation until after
  `assemble()`; nothing raised) and `probe_children.py <scratch>
  simulation.wall_clock_40.clock:WallClock40` followed by clocks 12, 17,
  25, 28, 32, 36, 37 and 39 (each `simulation.wall_clock_NN.clock:WallClockNN`),
  then `summarize.py <scratch> -v` (expect design.md's catalogue table).
  Run `probe_document.py <scratch>/document-wall_clock_25.json
  simulation.wall_clock_25.clock:WallClock25` and the same for clock 40;
  record the colours of `raised_detail`, `dial/supports`, `winding_knob`,
  `movement/pulley` and `standoffs`. Copy every probe's source, and
  `refuse_probe.py`'s, into `evidence.md` (the scratchpad is not
  durable).
- [ ] 1.4 Run, each alone, recording counts and wall time:
  `machinome test --mesh simulation/albert.py` and `python -m pytest -q
  -p no:cacheprovider simulation/test_frames.py` in `<Albert>` (Stage P:
  35 passed in 11.85 s; 12 passed in 3.65 s). `git -C
  <Albert> status --short` and `git -C <Clocks> status --short` before and
  after: no change to either project (`<Clocks>` carries a pre-existing
  ` M screenshots/wall_clock_03.png`, not ours).

## 2. Red tests

All in a new `tests/test_children_reads.py` (a `BaseNodeTest`; fixture
classes in the module, `tests.meta_project.parts.Cube` as the part,
`machinome.simulation.Driver` for the knee):

- [ ] 2.1 RED, the node-model scenario "A simulate-phase read is refused":
  `LowerLeg` (design.md, Context: `knee` driver, `near`, `far`,
  `simulate()` rotating each of `self.children` by `self.knee` about x);
  `LowerLeg().set_state(knee=30.0)` raises `StructureError` whose message
  contains `LowerLeg`, `read self.children in simulate()`, `self.near` and
  `self.far`. The same from a fresh instance's `render()` and from
  `assemble()`. Red today: nothing raises, `near.operations` holds no
  rotation.
- [ ] 2.2 RED, "A render-phase read is refused", own list: `Tinted`
  declaring `a = Cube()`, `b = Cube()`, whose `render()` sets
  `part.color = '#ff0000'` for each of `self.children`;
  `Tinted().render()` raises `StructureError` containing `Tinted`, `read
  self.children in render()`, `self.a` and `self.b`. Red today: nothing
  raises and `a.color` is not `'#ff0000'`.
- [ ] 2.3 RED, same scenario, a child's list (clock 12's shape): `Islands`,
  an assembly declaring no children whose `render()` returns `[Cube(),
  Cube()]`, held as `islands = Islands()` by `Face`, whose `render()`
  colours each of `self.islands.children`; `Face().render()` raises
  `StructureError` containing `Face`, `read islands.children in render()`
  and `Islands declares no children`. Red today: nothing raises.
- [ ] 2.4 GUARD, "The same loop over the declared attributes works":
  `AddressedLowerLeg` (`simulate()` over `(self.near, self.far)`),
  `set_state(knee=30.0)`: both carry `['r', '30.0', [1, 0, 0]]`; nothing
  raised. Green before and after.
- [ ] 2.5 GUARD, "A read after linking, or outside any phase, is
  unchanged": (a) `AddressedLowerLeg().children == ()` before anything
  links it; (b) after `assemble()`, `node.children` lists `near` and `far`
  in order; (c) a `Peeking` root holding `inner = Inner()` (an assembly
  declaring one `Cube`), whose `simulate()` records `self.inner.children`
  only when the test has set `node._peek = True`: `assemble()` with the
  flag off, then the flag on and `node.render()` records the linked list
  of one cube; (d) a leaf's `children` read inside a phase (a `simulate()`
  recording `self.near.children`) is `()`; (e) `InternalNode.brep` on a
  never-linked `AddressedLowerLeg` outside any phase raises `RuntimeError`
  containing `cannot say whether it is a B-rep`. Green before and after.
- [ ] 2.6 Run 2.1-2.5 on the unmodified tree; record 2.4 and 2.5 green and
  the failure lines of 2.1-2.3.

## 3. The change

- [ ] 3.1 `machinome/node/internal.py`: `from . import phase as _phase`;
  `InternalNode.children` property and setter (design.md, Decision 2);
  `_early_read(node, phase)` building the `StructureError` (Decision 3),
  `declared_children` imported beside `declared_child_nodes`. The
  property's docstring says what it answers and when it refuses.
  `AbstractBaseNode.children = tuple()` stays.
- [ ] 3.2 Run section 2: 2.1-2.3 green with the messages asserted; 2.4 and
  2.5 still green. Run 1.2's files: counts unchanged.
- [ ] 3.3 Run `<scratch>/repro_project/repro.py` (without `--refuse`):
  the first step raises the Decision 3 message naming `self.near` and
  `self.far`; record it.

## 4. Validation in the projects

- [ ] 4.1 AlbertPro: 1.4's two runs again, alone; counts equal to 1.4's.
  `git -C <Albert> status --short` unchanged.
- [ ] 4.2 The clocks: `probe_document.py` for each of clocks 12, 25, 28,
  32, 36, 37, 39 and 40: each now raises `StructureError` at load, naming
  its assembly, `render()`, the read and the attributes (record each
  message's first line); clock 17 serializes as before. `git -C <Clocks>
  status --short` unchanged. This is the expected outcome on the
  unchanged project (design.md, Open Question 1), not a regression of
  this change; record it as such.
- [ ] 4.3 The companion change in 3DPrintedClocks (design.md, Open
  Question 1, answered: option (a)), as direct project work in that
  repository: `git -C <Clocks> worktree add WTs/children-reads -b
  children-reads` from the project's current HEAD (`ec2a05d` on
  `solid-node-simulation`; its pre-existing ` M screenshots/wall_clock_03.png`
  is not ours and stays), and in that worktree rewrite the 18 reads of
  clocks 12, 25, 28, 32, 36, 37, 39 and 40 to loop over the declared
  attributes (clock 12: colour the islands where `DialDetail` builds
  them, or a class-level colour on the island class; clock 40: delete
  the three dead loops or make them equivalent, say which). Edit only
  with Read/Edit/Write, only inside that worktree. Then, against the
  bench: `probe_document.py` for each of the eight clocks serializes
  (no refusal) and the previously `color: None` parts (60 islands, 40
  others) carry their colours; each clock's documented test command
  (the project's README) at its count on `solid-node-simulation` and on
  the branch; one `machinome snapshot` of one coloured clock (clock 25)
  looked at with the Read tool, saying the colours are visible. Commit
  on that branch in the project repository (`git -C <worktree>
  rev-parse --show-toplevel` must print the project; a message in the
  project's own style; the attribution trailer `Co-Authored-By: Claude
  Fable 5.1 <noreply@anthropic.com>`), nothing merged, the project's
  main checkout untouched; leave the worktree in place and record its
  path and the commit in evidence.md. If a clock's test command needs
  more than ~15 minutes, run the clock's own module test only and say so.

## 5. Manual and changelog

- [ ] 5.1 `docs/concepts/rest-and-motion.rst`: the two sentences of
  design.md, Decision 6, after the `simulate()` paragraph.
- [ ] 5.2 `docs/architecture.md`: the one sentence of Decision 6 in the
  declarative-internal-node paragraph beside "`omit()` raises in
  `simulate()`".
- [ ] 5.3 `docs/project/changelog.rst`: one bullet under the existing
  `Unreleased` section naming `children-refuse-early-reads` — a read of
  an internal node's `children` inside `render()` or `simulate()` before
  the framework has linked them is refused naming the declared attributes,
  where it answered an empty list and a loop over it did nothing.
- [ ] 5.4 Grep `docs/` for `self.children` and `.children` and confirm no
  page tells a reader to read `children` in `render()` or `simulate()`.

## 6. Checks

- [ ] 6.1 `black --check` and `flake8 --max-line-length=89` on
  `machinome/node/internal.py` and `tests/test_children_reads.py`.
- [ ] 6.2 The full suite once, alone (`pytest -q -p no:cacheprovider` at
  the bench root); record counts and wall time. Expect design.md's
  "Suite under the probe" (4623 passed, 4 skipped, 6611 subtests on the
  unmodified bench) plus section 2's new tests; any other failure is a
  framework read the probe did not see, and is recorded and stopped on,
  not worked around.

## 7. Warts

- [ ] 7.1 Move the AlbertPro entry "**`self.children` is empty during
  `simulate()`, and iterating it fails silently.**" verbatim from
  `workflow/warts.md` to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
  under a heading naming `children-refuse-early-reads`, with a "What
  shipped" paragraph (the refusal, both phases, the clocks' second
  sighting and Open Question 1's outcome as recorded at the time), and
  delete it from `warts.md`; delete the standing triage's "Planned, never
  done" bullet naming this cycle.
- [ ] 7.2 Add to `warts.md`, under a heading "Findings from the framework
  cycle `children-refuse-early-reads` (2026-10-06)": the eight clocks'
  render-phase colour loops (refused at load until rewritten; 40 parts
  uncoloured before; clock 40's dead loops) unless the companion project
  change has already landed; and design.md's Open Question 2 (a read
  outside any phase before linking still answers `()`). Each
  **Recorded.**

## 8. Sync and archive

- [ ] 8.1 Sync the delta into `openspec/specs/node-model/spec.md` (the
  requirement added after "Tree naming from parent attributes" or at the
  end of the requirements; no existing requirement edited).
- [ ] 8.2 Archive the change to
  `openspec/changes/archive/2026-10-06-children-refuse-early-reads/`;
  `openspec validate --specs` (or `openspec validate node-model`) passes.
- [ ] 8.3 Run section 2's file and 1.2's files once more; record. Leave
  everything uncommitted.

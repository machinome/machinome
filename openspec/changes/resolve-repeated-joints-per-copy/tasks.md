Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`.

- Every framework command runs as
  `env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`.
- The project command runs as
  `env -C <Prusa> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/machinome test --mesh simulation/prusa_i3.py`,
  where `<Prusa>` = `/home/asa/devel/machinome/projects/3D-Printers/Prusa3-vanilla`.
  The project's README says `--faceted`, which is now `--mesh`.
- `<scratch>` is the campaign scratchpad's `cycle4/` directory
  (`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle4/`).
  It holds `pyproject.toml`, `repro_repeat_index.py` and `seed_probe.py`.

Rules for the whole cycle:

- Run one test run of ours at a time, since runs share `tests/_build`.
- Every test marked RED in section 2 is run and seen red, for the reason
  it names, before the code that turns it green.
- Edit nothing in any project, and do not run hangprinter or OpenCycloid.
- Record every command and its result in `evidence.md` as you go, in the
  shape of `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check: `python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench.
- [ ] 1.2 Run `<scratch>/repro_repeat_index.py`, once plain and once with
  `PROBE_SEED=1`. Expect design.md's Context table, the six rows in both
  columns. Copy the script's source and `seed_probe.py`'s into
  `evidence.md`, because the scratchpad is not durable.
- [ ] 1.3 Run `tests/test_declarative_nodes.py tests/test_joints.py
  tests/test_frames.py` with `pytest -q -p no:cacheprovider`, and record
  the counts and wall time.
- [ ] 1.4 Run Prusa3-vanilla's command, alone, and record the count, the
  two failing tests' names and the wall time. Expect 19 tests: 17
  passed, 2 failed, those being `test_the_gear_pair_drives_at_every_feed`
  and `test_x_home_meets_the_switch` (design.md, Context; about 170 s).
  Record `git -C <Prusa> status --short` before and after: it is empty,
  and stays empty.

## 2. Tests

All the tests go in `tests/test_declarative_nodes.py`, in a new class
`RepeatIndexDuringConstructionTest` placed after `RepeatIndexTest`, with
fixture classes at module level beside `Bead`/`Ranked`/`Half`. Each leaf
is a `Solid2Node` returning `cube(1, center=True)`. Joint arguments are
read with `declared_joints(type(copy))[<name>].arguments(copy)`, and
frames with `machinome.node.frames.resolved_frames`.

- [ ] 2.1 RED, the scenario "Each copy resolves and places its own
  joint". `Guide` declares
  `turn = Revolute(axis=lambda node: (0, 0, 1 if node.index == 0 else -1), at=lambda node: (10.0 * node.index, 0, 0), range=lambda node: (0, 90 + node.index), unit='deg')`
  and `GuidePair(AssemblyNode)` declares `guides = Guide().repeat(2)`.
  Assert:
  - copy 0's arguments are `((0, 0, 1), (0.0, 0.0, 0.0), (0, 90))`;
  - copy 1's arguments are `((0, 0, -1), (10.0, 0.0, 0.0), (0, 91))`;
  - after `copy.turn = 30` on each copy,
    `copy.__dict__['_joint_motion']['turn']` serializes to
    `[['r', '30', [0, 0, 1]]]` for copy 0 and to
    `[['t', ['-10.0', '-0.0', '-0.0']], ['r', '30', [0, 0, -1]], ['t', ['10.0', '0.0', '0.0']]]`
    for copy 1;
  - both copies share one `uniq_id`.

  Red today: `GuidePair()` raises `ParameterError` containing
  `Guide.turn: axis` and `no attribute 'index'`.
- [ ] 2.2 RED, the scenario "An orbit's carried point reads the copy's
  position". `Roller` declares
  `spin = Orbit(axis=(0, 0, 1), carries=lambda node: (5.0 + node.index, 0, 0), unit='deg')`,
  repeated twice. The resolved arguments' index 3 is `(5.0, 0.0, 0.0)`
  and `(6.0, 0.0, 0.0)`. Red today: `Roller.spin: carries -- ... no
  attribute 'index'`.
- [ ] 2.3 RED, the scenario "A frame argument and a check read the
  copy's position", in two tests:
  - `Seated` declares `seat = Frame(at=lambda node: (0, 0, 3.0 *
    node.index))`, repeated twice. `resolved_frames(copy)['seat'].at`
    is `(0.0, 0.0, 0.0)` and `(0.0, 0.0, 3.0)`. Red today:
    `Seated.seat: frame argument at -- ... no attribute 'index'`.
  - `Checked` declares `size = Length(1.0, min=0)` and a `check()` that
    stores `self.seen = self.index`, repeated twice. The copies'
    `seen` is `[0, 1]`. Red today: `AttributeError: 'Checked' object has
    no attribute 'index'`.
- [ ] 2.4 GUARD, the scenario "A function failing for another reason is
  refused as before". Both refusals raise `ParameterError`:
  - (a) a repeated class whose `turn` has `axis=lambda node:
    node.no_such_thing`. The message contains the class name, `turn`,
    `axis`, `AttributeError` and `no_such_thing`.
  - (b) `Guide` declared as one plain child (`guide = Guide()`) of an
    assembly. The message contains `Guide.turn`, `axis`, `AttributeError`
    and `index`.

  Both are green before and after.
- [ ] 2.5 GUARD, the scenario "What other functions are handed is
  unchanged". The site case is the existing
  `SiteJointCallableTest.test_a_copys_index_is_not_reachable_from_a_site_callable`
  (do not duplicate it). Add two tests:
  - (a) a legacy `Stubborn(Solid2Node)` whose `__init__(self,
    name=None)` assigns `self.index = -1` and then calls
    `super().__init__(name=name)`, held as `items = Stubborn().repeat(2)`.
    The copies read `index` `[0, 1]`.
  - (b) `guards = Guard(thickness=2.0).repeat(2)` (`Guard` from
    `tests/declarative_project/parts.py`, a legacy class). The copies are
    named `guards-0` and `guards-1`, read `thickness` `2.0`, and read
    `index` `[0, 1]`.

  Both are green before and after.
- [ ] 2.6 Run section 2 on the unmodified tree. Record 2.4 and 2.5 green,
  and the failure line of each test in 2.1 to 2.3.

## 3. The change

- [ ] 3.1 In `machinome/node/declarative.py`, make Decision 2's shape:
  - `ChildDeclaration.realize(self, values, owner, index=None)`, its
    docstring saying what `index` is and who passes it;
  - `ChildDeclaration._construct(self, args, kwargs, index)`, which
    replaces the plain call at `:543`;
  - `RepeatDeclaration.realize` passing `index=index` and keeping its
    stamp, with the comment at `:710-716` replaced by Decision 2's.
- [ ] 3.2 Revise the docstring of
  `SiteJointCallableTest.test_a_copys_index_is_not_reachable_from_a_site_callable`.
  Its reason becomes that a site callable is handed the declaring parent,
  so there is no copy in scope to read `index` off. The old reason,
  "stamped ... AFTER the copy's construction", is removed. The test's
  code and assertions stay as they are.
- [ ] 3.3 Run section 2: 2.1 to 2.3 are green, and 2.4 and 2.5 are still
  green. Run 1.3's files, and the counts are 1.3's plus the new tests.
  Run `repro_repeat_index.py` without `PROBE_SEED`: its output equals
  the probe column of design.md's table.

## 4. Validation in the originating project

- [ ] 4.1 Run Prusa3-vanilla's command again, alone. Expect the same
  count and the same two failing tests as 1.4. `git -C <Prusa> status
  --short` is unchanged. Record the wall time.

## 5. Manual, ADR and changelog

- [ ] 5.1 In `docs/concepts/joints.rst`, "Arguments", replace the
  sentence quoted in design.md, Decision 6, with the sentence given
  there.
- [ ] 5.2 In `docs/architecture.md`, make the two edits of Decision 6
  (`:877` and `:1150`).
- [ ] 5.3 Add to
  `docs/adrs/NODE/ADR-096-a-relation-broadcasts-over-a-repeated-child.md`
  a final section "## Amendment (2026-10-06, change
  `resolve-repeated-joints-per-copy`)" saying the three things of
  Decision 4. In `docs/adrs/README.md`, ADR-096's line ends
  `— **Accepted**, extends 089, depends on 061/063/093, amended 2026-10-06`.
  (Open Question 1, recommendation (a).)
- [ ] 5.4 Add to `docs/project/changelog.rst` the bullet of Decision 6
  under the existing `Unreleased` section.
- [ ] 5.5 Grep `docs/`, excluding `adrs/` and `releases/`, for `index`
  near "not yet", "does not exist" and "AFTER construction". No page may
  still say a copy's `index` is missing during its construction.

## 6. Checks

- [ ] 6.1 Run `black --check` and `flake8 --max-line-length=89` on
  `machinome/node/declarative.py` and `tests/test_declarative_nodes.py`.
- [ ] 6.2 Run the full suite once, alone (`pytest -q -p no:cacheprovider`
  at the bench root), and record the counts and wall time. Expect
  design.md's "Suite under the probe" plus section 2's new tests. Any
  other failure is recorded and stopped on, not worked around.

## 7. Warts

- [ ] 7.1 Move the second entry of `workflow/warts.md`'s section
  "joint-frame-follows-declarer (2026-09-10)" verbatim, from "**A
  `.repeat()` copy's `index` does not exist yet when a joint's own
  `axis`/`at`/`carries` resolves" to "since a relation's `law=`/`ratio=`
  resolves later, after `index` exists.". Its destination is
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, under a heading
  `## \`resolve-repeated-joints-per-copy\``, with a "What shipped"
  paragraph covering:
  - the copy seeded before construction;
  - joint arguments, frame arguments and `check()` reading it;
  - resolution not moved;
  - the ADR-096 amendment.

  Delete the entry from `warts.md`. The section keeps its first entry.
  Also delete the standing triage's "Planned, never done" bullet "**A
  `.repeat()` copy's joint arguments resolve before `index` exists**".

## 8. Sync and archive

- [ ] 8.1 Sync the delta into `openspec/specs/declarative-nodes/spec.md`.
  The requirement is added after "Class-body child declarations", and no
  existing requirement is edited.
- [ ] 8.2 Archive the change to
  `openspec/changes/archive/2026-10-06-resolve-repeated-joints-per-copy/`.
  Then `openspec validate --specs` (or `openspec validate
  declarative-nodes`) passes.
- [ ] 8.3 Run section 2's tests and 1.3's files once more, and record
  the result. Leave everything uncommitted.

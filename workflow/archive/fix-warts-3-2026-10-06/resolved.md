# Fix-warts 3: the entries it resolved

Each entry below left `../../warts.md` in the cycle that closed it, with its
text as it stood there and a paragraph saying what shipped. The campaign's
plan and progress are in `../../ongoing/fix-warts-3.md`; each cycle's
archived OpenSpec change is the authority for what it did.

## `snap-keeps-the-triad-unit`

From "Findings from the SO-ARM100 project's migration onto mates
(2026-09-26)":

- **A snapped triad component leaves the triad non-unit.** `frames.py`
  normalizes a declared direction and then snaps each component within
  `_SNAP = 1e-9` of 0, 1 or -1 onto that value, one component at a time
  and without renormalizing. A URDF rpy of `1.57079` gives
  `z = (0, -0.99999999998, 6.33e-6)`: the second component snaps to
  exactly `-1` while the third stays, and the resolved `z` has length
  `1 + 2e-11`; `3.14158` gives `1 + 8e-11`, on `z` and `x` both. Four of
  the SO-100's six fixed frames resolve so. No pose shows it (the mate's
  axis-angle extraction goes through `atan2`) and the placement is within
  1e-10, but the documented read promises a unit triad, and the project's
  test had to compare resolved directions at 1e-9 rather than 1e-12. The
  snap should keep the triad orthonormal: snap a component only when the
  snapped vector is still unit to `_SNAP` (the other components within
  the snap of 0), or renormalize after snapping. A small fix in
  `frames.py`; the joint's own `_SNAP` shares the rule and should be
  checked with it. **Recorded.**

  **Remaining (2026-10-04):** `explicit-frame-direction-precision`
  (`fabfc3d`) no longer snaps a frame stated with both `x` and `z`; with
  `x` omitted, `frames.py` still snaps each component without
  renormalizing, and the joint's `_snapped` axis does too.

**What shipped.** `explicit-frame-direction-precision` (`fabfc3d`) had
closed it for a frame stating both directions, which is how all four of
the SO-100's off-axis fixed frames are written. `snap-keeps-the-triad-unit`
(`openspec/changes/archive/2026-10-06-snap-keeps-the-triad-unit/`) closed
the rest: on a frame's snapped path, which a non-unit direction reaches
only with `z` omitted and `x` stated (the path the note above calls "`x`
omitted"; an omitted `x` needs `z` on a principal axis, which snaps to
exact integers), and on every joint's axis. One helper,
`machinome.motion.joints._snapped_direction`, now used by `Joint.resolve`
and `Frame.resolve` alike, snaps a direction to a principal axis only as a
whole: exactly that axis in integers when every component is within `1e-9`
of `0`, `1` or `-1`, otherwise only its components within `1e-9` of `0`
made `0`. Every resolved direction is unit to `1e-12`, and a mate stating no
axis turns its child about exactly the moving frame's resolved `z`. In the
SO-100, against the bench, every one of its twelve resolved frame
directions and six joint axes is unit within `2.22e-16`, and its frames,
joint axes and every link's operations in its five documented poses are
identical before and after the change. Its guard's `1e-9` tolerance is the
project's own to tighten. The two per-component snaps the change left, a
site-declared joint's carried axes and a mate's rest-rotation axis, are
recorded as a new entry in the same section of `../../warts.md`.

## `build-settles-on-a-grown-source-set`

From "Findings from the framework cycle `lean-install` (3 October 2026)",
the addendum to the entry that begins "**A `machinome build` in a fresh
project worktree hung for three hours.**" (the entry itself stays in
`../../warts.md`, with a note on what is left of it):

  *4 October 2026, the framework cycle `mesh-engine`:* a `machinome build`
  in a project whose sources were written moments earlier restarts every
  second without end: each build generation, a fresh spawned interpreter,
  ends `SOURCE_CHANGED` (11), and `machinome build` starts the next,
  printing `START` once a second. In a temporary project of `StlNode` parts,
  outside any import finder, `timeout 60 machinome build
  mfixture/parts.py:Shelf` exited 124 after 50 `START` lines; with every
  source dated an hour back, the same build printed one `START` and exited
  0. (Here a child is spawned every second; the hang above saw none, so the
  two may yet differ in their last step.) Evidence:
  `openspec/changes/archive/2026-10-04-mesh-engine/evidence.md`, §2.
  **Reproduced, mechanism found; untriaged.**

**What shipped.** A builder remembered the largest mtime of the sources its
classes were loaded from and, after assembly had added every part's own
sources to the set, stood down when the grown set's largest mtime differed;
a mesh dated even a millisecond after its module made them differ with no
file changed, and every fresh generation saw the same. A git checkout writes
files in path order, so a fresh clone or worktree leaves meshes newer than
their modules. `build-settles-on-a-grown-source-set`
(`openspec/changes/archive/2026-10-06-build-settles-on-a-grown-source-set/`)
keeps that comparison only for a builder without a source generation, a
path no real build takes; with one, every contributor, those joining during
assembly included, is compared with its own observation by the assembly
phase's closing check and every later boundary (ADR-084), so an edit after
the build observed a source still stands it down. Against the bench, the
fixture's `native.py:StlBench` and `machine.py:Machine` build with one
`START` and exit 0 (before: 9 and 8 `START` lines in 30 s, still
restarting); a scratch project whose mesh is 1 ms or 1 s newer than its
module builds in one generation (before: 36 and 37 `START` lines in 45 s);
and a fresh worktree of Robots/hexapod_spiderbot_model builds with one
`START` in 8.2 s (before: 33 `START` lines in 120 s). The seven
`tests/test_scad_presentation.py` tests the cycle `snap-keeps-the-triad-unit`
had to deselect pass on the checkout's own timestamps.

## `name-what-is-refused`

Three entries, one change: each refusal kept its verdict and named, in its
message, something the author could not act on. The change is archived at
`openspec/changes/archive/2026-10-06-name-what-is-refused/`.

From "Findings from the framework cycle `slide-by-mate` (2026-09-26)" (the
section's only entry; the section went with it):

- **The axis-less refusal names a `Revolute` for any kind.**
  `Joint.__set_name__`'s `axisless_refusal` was written when only a
  `Revolute` could lack an axis; a `Prismatic(axis=None)` written in a
  class body, or as a mate's freedom, is refused by it with "is a
  Revolute without an axis ... where the moving frame supplies it",
  which is wrong on both counts for a `Prismatic` (a `Prismatic` freedom
  states its axis, ADR-151). Found in the orchestrator's review of
  `slide-by-mate`; the cycle left the wording alone because widening it
  was struck with the axis-less `Prismatic`. A one-line wording fix
  naming the kind and, for a `Prismatic`, saying the axis is required
  everywhere. **Recorded.**

**What shipped.** `axisless_refusal` takes the joint's kind and the words
naming the declaration. A `Revolute`'s text is unchanged; any other kind is
named as itself, its axis said to be required everywhere (for a `Prismatic`,
"a mate's freedom included"), and only a `Revolute` said to leave its axis
out, as a mate's freedom. A joint a mate installed from an axis-less
freedom is refused naming the mate on the assembly that states it
(`Palm.grip: the mate's freedom is a Prismatic without an axis. ...`)
rather than the moving child's class, and the declaration-site check
covers `Prismatic` and `Orbit` beside `Revolute`, so a site
`Prismatic(axis=None)` names the declaring class (`Rail: the joint 'travel'
passed where Slider is declared is a Prismatic without an axis. ...`)
rather than `Slider.travel`. No project declares an axis-less `Prismatic`;
the proof is `tests/test_joints.py::AxislessKindTest` and
`tests/test_mates.py::SlidingMateTest::test_a_prismatic_freedom_written_axis_none_names_the_mate`.

From "Findings from the OpenMANIPULATOR-X project's migration onto mates
(2026-09-26)", the section's last entry (its other findings had left it in
the warts hygiene of 4 October 2026); the section went with it, its
introduction kept here:

> The validation of `slide-by-mate` (ADR-151) in its originating project:
> the four revolutes and the two prismatic finger joints of
> OpenMANIPULATOR-X stated as mates referencing the URDF transcription
> (branch `frames-and-mates`, commits `597e18c`, `5548c4b`, `eb8ec16`;
> framework `6f11aba`), `capture_poses.py compare` at maximum deviation 0
> (unrounded 0.0) over 23 poses and 43 leaves, the documented suites at
> their `main` counts with no test edited, `machinome export` identical
> but for mtimes, `Rest`/`Present` snapshots byte-identical. Nothing
> refused; the `Prismatic` freedom, its translational coordinate and the
> mimic as a relation between two mates expressed the URDF with nothing
> left over. The workspace's `capture_poses.py compare` silently skips
> ports whose names move between nodes, which every mate migration does;
> the matrices carry the proof, and the tool could say what it skipped.
> Three findings, all consequences, recorded for the pilot's triage.

- **`JointRangeError` names the child's installed joint, not the mate's
  coordinate.** `set_state(grip=21)` is refused as
  `...link5.left_finger: joint 'left_travel' declares the range -11.0
  to 20.0 mm`, naming the joint the mate installed on the finger, while
  the only place it can be bound is `Link5Assembly.left_travel`; the
  names match, so a reader finds it, but the message points at the
  node a reader cannot bind. A wording candidate for the next mates
  cycle. **Recorded.**

**What shipped.** One helper, `machinome.motion.joints._binding_site`,
says where a joint's coordinate is bound: for a joint a mate installed, the
assembly that states the mate (the child's linked parent) and `mate
'<name>'`; for any other joint, the node and `joint '<name>'` as before.
Every range refusal that can judge a mate's joint takes its head from it:
the binding-time refusals in `joints.py`, the judgement of a `Bound` that
reads other coordinates when the enumeration closes (`couplings.py`), and
the clocked simulation's construction and commit refusals
(`simulation/clocked.py`), which still quote the coordinate's bank id. In
OpenMANIPULATOR-X, against the bench, `set_state(grip=21)` is now refused
as `arm.link2.link3.link4.link5: mate 'left_travel' declares the range
-11.0 to 20.0 mm, and 21 is outside it. ...`, and a binding on a
`Link5Assembly` of its own as `Link5Assembly (Link5Assembly): mate
'left_travel' ...`; its documented suites (11 and 4) and OpenArm's (10),
whose guards assert the mate's name, pass unchanged. A joint given at a
declaration site keeps naming the child, where it is bound. The
constraint-intersection refusals, which name a bank id, were left as they
are and recorded in `../../warts.md`.

From "read-the-driven-coordinate (2026-09-15, found while fixing)", whose
other entries stay in `../../warts.md`:

- **`a.drives(a)`, one to one, still deadlocks into `UnreachedCoordinate`
  instead of naming itself.** ADR-100 declined to widen its shared-coordinate
  refusal to the one-to-one shape and ADR-121 does not either: recognition is
  scoped to a relation naming SEVERAL ends, which is the only shape that is
  forward-only, so `a.drives(a)` is not checked at class definition at all.
  Measured on this worktree (`evidence.md` §1 E): it raises
  `UnreachedCoordinate: wheel.turn drives wheel.turn: nothing bound either
  end` at the close of the enumeration, which says nothing about the shape. A
  one-to-one self-read has no second source to carry slope, so the skeleton
  test would refuse every such law anyway — the message, not the verdict, is
  what is wrong.

**What shipped.** `relate` compares a relation's one source with its one
driven end after both ends' own checks, the comparison the several-ends
self-read already made, with the node standing for its one joint expanded,
and refuses a match at class definition with a `TypeError`: `wheel.turn
drives wheel.turn: the relation's one source, wheel.turn, is its own driven
end, wheel.turn. ...`, pointing to `(source & wheel.turn).drives(wheel.turn,
law=...)` under a running root as the way a law reads the coordinate it
drives. Every spelling probed is caught: a written path, with or without a
`law=`, a port of the class, the node standing for its one joint
(`wheel.drives(wheel.turn)`) and a reused-joint mate's handle
(`mount.drives(body.turn)`). No machine that could be posed before is
refused now: each shape was refused at its first enumeration, as
`UnreachedCoordinate` or `DoublyBound`, and is now refused when the class is
defined. A driver or a
repeat named at both ends keeps its own end refusal. No class in the
catalogue writes the shape (a literal scan of 4238 `.drives(` lines in 552
files under `projects/`).

## `children-refuse-early-reads`

From "AlbertPro (2026-09-07, simulate the Albert quadruped)", "Framework":

- **`self.children` is empty during `simulate()`, and iterating it fails
  silently.** `LowerLeg.simulate()` was written as `for piece in
  self.children: piece.rotate(self.knee.value, AXIS)`. The port was
  bound and correct, the list was empty, the loop applied nothing, and
  nothing raised — the shin simply never turned about its knee, and the
  published model was a robot whose knees did not bend. Every contract
  passed, because a test calls `set_state` before measuring and by then
  the children are linked; only a snapshot showed it. The workaround is
  to address the declared attributes (`self.near`, `self.far`), which
  works in both phases, and that is what
  `projects/Robots/AlbertPro/simulation/leg.py` does. A documented
  empty-during-simulate contract, or a `.children` that raises there
  rather than reading as empty, would turn a silent wrong model into an
  error. This is the one worth filing.

**What shipped.** `children-refuse-early-reads`
(`openspec/changes/archive/2026-10-06-children-refuse-early-reads/`) made
`InternalNode.children` a property over the list `present()` and
`materialize()` assign. Inside an assembly's `render()` or `simulate()`,
a read of an internal node's `children` before anything has assigned them
raises `StructureError` naming the assembly, the phase, the read
(`self.children` or `<child>.children`) and the declared attributes to
address instead, or, for a node declaring none, that its own `render()`
builds them. A read after linking, or outside any phase, answers as
before. The refusal covers both phases: in `render()` the list can never
be there, since `render()` is what decides it, and in `simulate()` it is
there only on a pass after something has presented the node, which is why
AlbertPro's tests passed while its published document did not move.
AlbertPro's two documented runs (35 and 12) are unchanged. The search
for other readers found a second, silent sighting: eighteen reads in
3DPrintedClocks wall clocks 12, 25, 28, 32, 36, 37, 39 and 40, each a
colour loop in `render()` that saw an empty list, so sixty dial islands
and forty other parts in seven of those clocks were published uncoloured
(clock 40's three loops were dead code beside a class-level colour).
Each of the eight is now refused at load until its loops address the
declared attributes. The orchestrator chose to refuse in both phases and
to make the companion rewrite in the project on its branch
`children-reads`; at the time of this cycle clocks 12, 25 and 28 were
rewritten there (`58ff90e`) and the other five were not, and the merge is the
pilot's (`../../ongoing/fix-warts-3.md`, "Deferred to the pilot"). What
remains is recorded under "Findings from the framework cycle
`children-refuse-early-reads` (2026-10-06)" in `../../warts.md`.

## `resolve-repeated-joints-per-copy`

From "joint-frame-follows-declarer (2026-09-10)":

- **A `.repeat()` copy's `index` does not exist yet when a joint's own
  `axis`/`at`/`carries` resolves, so "a callable of the copy's index"
  is not actually a working bridge for a JOINT argument.** Found
  applying decision 4's Bridge A to Prusa3-vanilla's `XGuide`/`YGuide`,
  hangprinter's `RollerBearing`, and OpenCycloid's `RadialBearing`/`Pin`
  in this cycle's own pose overlay: `axis=lambda node: (0, 0, 1 if
  node.index == 0 else -1)` on a `.repeat(2)` class raises
  `AttributeError: '<Class>' object has no attribute 'index'` at
  REALIZATION, every time, because `resolve_declared_joints` runs
  inside the copy's own `__init__` (ADR-088) while
  `RepeatDeclaration.realize()` assigns `child.__dict__['index'] =
  index` on the line AFTER that construction returns
  (`machinome/node/declarative.py:391`, whose own comment already says
  "no sighting needs `index` during construction" — true for a LAW
  resolved later, false for a joint argument resolved eagerly).
  `MotionWorksPart`'s existing `at=lambda node: ... node.index ...`
  works today only because `index` there is a DECLARED PARAMETER
  (`Count(min=0, max=2)`, passed as a constructor kwarg), not a
  `.repeat()`-assigned attribute — the working and the broken case look
  identical at the call site and are easy to conflate, which the
  overlay did once. Worked around, three times over, by deriving the
  axis from the copy's ACTUAL placement in the PARENT's `render()`
  instead of a class-body callable — the overlay's own
  `derive_helper.axis_from_placement`, `_carry`'s own arithmetic reused
  for one run. Candidate fix: resolve a REPEATED class's joint
  arguments once per copy, after `index` is assigned, rather than
  inside the copy's own `__init__` — or let `resolve_declared_joints`
  defer a `NameError`/`AttributeError` from a callable and retry once
  the realization path can say why, naming which attribute was missing
  rather than failing opaquely. This closes the axis half of decision 4
  as WRITTEN (Bridge A does not work as stated for the five axes); the
  parent-supplies-the-sign bridge (Thor's own `ratio=`) is unaffected,
  since a relation's `law=`/`ratio=` resolves later, after `index`
  exists.

**What shipped.** `resolve-repeated-joints-per-copy`
(`openspec/changes/archive/2026-10-06-resolve-repeated-joints-per-copy/`)
gives a copy its `index` before its construction rather than after.
`RepeatDeclaration.realize` hands each copy's position to
`ChildDeclaration.realize`, whose `_construct` allocates the copy, writes
`index` into the copy's own instance dictionary and only then runs the
copy's constructor; the stamp after construction stays, so a copy whose
constructor assigned an `index` of its own still ends with its position.
So the copy's `check()`, the functions given as its class-declared joint
arguments (`axis`, `at`, `range`, `carries`) and the functions given as
its frame arguments all read `node.index`, and each copy resolves and is
placed by its own arguments while the copies keep one `uniq_id`.
Resolution did not move: joint and frame arguments still resolve inside
the copy's constructor, after `check()` and before any child is realized
(ADR-088), so a refused copy has still realized nothing, and a function
that fails for another reason is refused as before, naming the attribute
it could not read. A function given where the child is declared is still
handed the parent (ADR-098). ADR-096, whose decision said the stamp was
made after construction, carries a dated amendment saying so. The finding's
form now works as written; Prusa3-vanilla, hangprinter and OpenCycloid keep
their site-declared or placement-derived workarounds, and moving back to
the class form is each project's own choice. Prusa3-vanilla's documented
run is unchanged (19 tests: 17 passed, the same 2 failing before and after).

## `tooling-paths-and-flags`

From "Expression math and mechanisms (2026-09-06)", "Framework":

9. **`tools/generate_parity_fixture.py` cannot run from a worktree.** Its
   default output path resolves to `ROOT/../machinome-viewer/...`, which
   from `machinome/WTs/<name>/` is a directory that does not exist. Resolve
   through the Git common directory, as the shop contract prescribes for
   workspace paths, or require the output argument. Evidence:
   `expression-math` task 5.4.

From "Internal-Cycloidal-Actuator (2026-09-06, project refactor pass)":

14. **`machinome snapshot --preview` passes a bare `--preview` to OpenSCAD
    2021.01**, which rejects it with a usage dump
    (`OpenScadRenderer.build_command` emits it unconditionally). Seen in
    3DPrintedClocks.

From "Voron-2 — native contact measurements and snapshot arguments (5
October 2026)":

### A negative-leading camera vector is rejected at the viewer subprocess boundary

- **Symptom/evidence.** `machinome snapshot --renderer web --autocenter
  --viewall --imgsize 1400x1100 --camera 0,0,0,65,0,35,1400` fails with
  `argument --up: expected one argument`. The tested framework's
  `viewers/browser.py` emits `--up` and its comma tuple as separate tokens.
  This camera produces `(-0.242403876506104, 0.34618861305875415,
  0.9063077870366499)`; the negative-leading tuple is rejected by the viewer
  argument parser. The same construction is used for `--view`.
- **Workaround and limits.** Omitting the requested camera passes parsing,
  but that separate capture then reports `Failed to fetch`; it is not a
  successful replacement snapshot. OpenSCAD rendered the requested views.
  Commands, errors and inspected images are recorded in the project's
  `docs/evidence/resumed-snapshots.json`.
- **Triage.** Framework subprocess argument construction, not a new camera
  API. No fix implemented. The separate static-export browser stall belongs
  in the viewer's `workflow/warts.md`.

The same project also reproduced existing **item 14**, the bare OpenSCAD
`--preview` consuming the following filename. No duplicate wart is opened:
Voron's argument trace and successful captures without the optional flag
are additional evidence for that existing finding.

**What shipped.** `tooling-paths-and-flags`
(`openspec/changes/archive/2026-10-06-tooling-paths-and-flags/`) makes three
commands the framework composes ones their tools accept. Given no output
path, `tools/generate_parity_fixture.py` asks Git for the common directory
of the checkout it sits in, takes the primary checkout as that directory's
parent and writes `machinome_viewer/widget/src/parity-fixture.json` in the
`machinome-viewer` checkout beside it, so the primary checkout and every
worktree under `WTs/` name the same file; when Git cannot answer or no such
viewer directory exists, it refuses before building anything, naming where
it looked and the output argument. An argument is used as given, as before.
The OpenSCAD renderer passes `--preview=throwntogether` for `machinome
snapshot --preview`, one token OpenSCAD 2021.01 reads as its ThrownTogether
previewer, so the bare option no longer takes the `.scad` path as its value;
3DPrintedClocks' wall clock 11 with `--preview` writes its image. The web
renderer hands the viewer's capture `--view=<eye,target>` and
`--up=<x,y,z>` as one token each, so a camera whose resolved eye or up
direction begins with a negative component reaches the viewer intact;
Voron-2's camera, run on the framework's own snapshot fixture, writes its
image. The separate static-export stall Voron-2 saw without a camera stays
the viewer's.

## `name-solids-by-path`

From "3DPrintedClocks (2026-09-07, shared simulation package)":

- No public way to give a declared child an instance-specific tree name.
  Mantel clock 34's `TrainArbor` (one class, six instances) set
  `part.name` and the private `_explicit_name` on its `wheel` and `rod`
  children so the viewer tree and interference failures said which wheel
  was which. The refactor dropped the private and relies on the hierarchy
  (`train.centre.wheel`); an interference failure still names the leaf
  only (`wheel should not interfere with wheel`). A public per-instance
  name, or failure messages that print the qualified path, would close
  it.

From "Robots/Thor (2026-09-07, full simulation with fasteners)", the last
paragraph of its second entry (the interference inventory, which stays
open in `../../warts.md`):

  Related: neither the assertion nor the pair helpers can name a solid by
  its path. `seats.qualified_names()` walks the tree to build
  `{id(node): 'shoulder.art2.art3.art4.art56.gt2x40_pulley_1'}`, because
  `solid.name` is `gt2x40_pulley_1` and this machine has two. Same gap as
  the 3DPrintedClocks entry above, from the other side.

**What shipped.** `name-solids-by-path`
(`openspec/changes/archive/2026-10-06-name-solids-by-path/`) closes it with
the second remedy the clock entry names: failure messages print the path.
Every assertion of `machinome.test` that names a node names it by its path
below the node under test, the dotted linked child names the serialized
document publishes and a qualified driver id is built from (ADR-056), so
`wheel should not interfere with wheel` reads `centre.wheel should not
interfere with third.wheel`. One internal helper, `path_name` in
`machinome/node/qualified.py`, beside `instance_path` and reading the same
segments, builds every name and never raises: the node under test, a node
linked under nothing and the support assertion's floor keep their bare
names, a node outside the node under test is named below the top of its
own tree, and a message naming only direct children is unchanged. No
public per-instance name was added. Mantel clock 34's documented run stays
at 20 tests, 15 passed and the same 5 failed, its failures now reading
`movement.pendulum.bob.shell should not interfere with
movement.pendulum.bob.lid_screw_right` and `case.plates.edging should be
one connected body, ...`; a scratch script pulling the fourth arbor onto
the third reads `movement.train.third.wheel should not intersect
movement.train.fourth.wheel`, and the whole train's sweep now shows that
the first pair it meets is the centre arbor's lantern wheel against the
fourth (`movement.train.centre.wheel.wheel should not interfere with
movement.train.fourth.wheel`), which the old message printed as `wheel`
twice. On Thor, `path_name` gives each of the 438 printed solids the string
`seats.qualified_names()` builds by hand, so the project's walk may be
dropped by the project. The labels the engines put in their own errors
still print a bare name; that residue is filed in `../../warts.md`.

## `keep-the-corpus-cursor-honest`

From "Corpus record cursor across restore (2026-09-20)":

**Status: observed while validating Curta; deferred, no external issue filed.**
`tools/generate_running_corpus.py::run_machine` and the matching test replay
helper retain their record-list cursors across a scripted `restore`, while
the real run clears its record rings. If the same script step immediately
creates a new stop, the old cursor can omit it from that step's corpus record.
Direct runtime snapshot tests still compare the actual stop correctly.

The periodic-contact corpus restores on its own recorded step before the
next request, so both stops are present. No general corpus cursor repair is
included in that cycle. A future repair should be red-first for restore plus
an immediate same-step stop, and check crossings as well as stops; it should
  not change machine state or command semantics to repair evidence collection.

**What shipped.** `keep-the-corpus-cursor-honest`
(`openspec/changes/archive/2026-10-06-keep-the-corpus-cursor-honest/`)
closes it in evidence collection only. `run_machine` and the suite's
replay, `CorpusReplayTest.replay` in `tests/test_running_corpus.py`, now
start both counters, `crossings_seen` and `stops_seen`, at `0` after a
script action that restores, so a step's record is counted from the rings
`Run.restore` has just cleared, as `tools/generate_time_drive_corpus.py`
already did. Two tests were red first on the corpus machine `StopAndJump`,
whose single tick carries a `wrap` crossing and a stop: a script that
snapshots and moves in step 1, then restores and repeats the move in
step 2. The generator's record of step 2 had neither the crossing nor the
stop the run held, and now equals step 1's record and a one-step run's;
the replay refused the honest entry (`0 != 1 : StopAndJump tick 1`) and
accepted one with that crossing and stop removed, and now does the
reverse. The run, its commands and every machine are unchanged. No
committed corpus changed: a regeneration of the running corpus into the
scratchpad is byte-identical to the regeneration before the change, and
`tests/running-corpus.json`, `tests/clocked-corpus.json` and
`tests/time-drive-corpus.json` were not written. The viewer's replay keeps
the old counting; it still passes, since no committed scenario restores
and records in one step. The rings' bound in entries rather than ticks is
filed in `../../warts.md`.

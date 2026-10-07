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

## `snapshot-the-follow-prefix`

From "Review of the cycles landed after the 0.7.0 fold (2026-09-23)":

- **The Follow prefix cache stores mapping proxies where a propagation
  used to flow.** `Run._constraint_level` in `machinome/simulation/run.py`
  memoises a successful law-to-Follow prefix as
  `(MappingProxyType(dict(deltas)), MappingProxyType(dict(landings)))`.
  On a hit the rest of the method receives a plain read-only mapping, not
  the `Propagation` object the first walk produced, so `motions`,
  `untraced`, `follow_cuts` and `follow_closures` are absent. Today only
  item access follows the prefix, so it is correct; the first later change
  that reads a path attribute after the prefix will work on a miss and fail
  on a hit, and the focused tests would not necessarily catch it.
  **Deferred:** when that method is next touched, either snapshot the
  propagation itself (frozen) or assert the shape at the hit.

**What shipped.** `snapshot-the-follow-prefix`
(`openspec/changes/archive/2026-10-07-snapshot-the-follow-prefix/`) stores
the prefix as a `FrozenPropagation`, a new subclass of `Propagation` in
`machinome/simulation/trajectory.py` that carries the walk's displacements
and every attribute of the walk, dictionaries as read-only mappings and
sets as frozen sets, and refuses item and attribute changes with
`TypeError`. The walk that publishes the prefix continues with the stored
pair, so a hit and a miss hand the rest of `_constraint_level` one shape.
A test on `TwoSurfaces`, `test_a_reused_prefix_is_the_propagation_its_walk_produced`
in `tests/test_follow_prefix_cache.py`, was red first (`mappingproxy({...})
is not an instance of <class 'machinome.simulation.trajectory.Propagation'>`)
and is green. On the Curta (`projects/Calculators/Curta-Type-I-3x`, head
`1f3dc22`, run from outside the project, nothing written there) forty
crank ticks commit the same banks bit for bit before and after (SHA-256
`167ea1cd…8b18b1fcf`), in 177.45 s before and 176.59 s after; its
radial-ball module passes 4 of 4 in 263.49 s before and 260.63 s after,
and `test_mechanistic.py`'s subtraction test passes in 210.38 s before and
206.80 s after. No corpus changed.

## `clocked-snapshot-identity`

From "Three findings from filming the clocked Curta (1 October 2026, found by Videomaker's curta-video campaign)", item 4:

4. **The framework's clocked snapshot carries no identity, the viewer's does.**
   `ClockedSnapshot` holds `model` (the bare class name with the sorted bank
   ids) and `values`, and `Clocked.restore` compares `model` only, so the
   framework restores a snapshot from a machine whose law or range changed
   under the same ids, or from a same-named class in another module; the
   export spec says the identity exists precisely to refuse that, and a
   running `RunSnapshot` does carry and check `program.identity`. Found by
   `sim-identity` (its `evidence.md`, finding 1).

**What shipped.** `clocked-snapshot-identity`
(`openspec/changes/archive/2026-10-07-clocked-snapshot-identity/`) gives
`ClockedSnapshot` a third slot, `identity`, which `Clocked.snapshot()` and
`sim.initial` fill with the machine's identity, the string `sim.identity`
returns and an export publishes as `clocked.identity`. `Clocked.restore`
compares that identity instead of `model`, and refuses a snapshot whose
identity differs with a `ValueError` naming both models and both
identities, before touching the bank, the tree or the record. In
`tests/test_clocked_identity.py`, three tests were red first: a snapshot
and `sim.initial` carry `sim.identity` (`AttributeError: 'ClockedSnapshot'
object has no attribute 'identity'`), and a snapshot of the register
counter is refused by a same-named counter whose units dial stops at 360
instead of 324 degrees, and by one whose commit law advances by two
(each `ValueError not raised`); a fourth, the snapshot restoring into a
fresh simulation of the same machine, was green before and after. On the
Curta (`projects/Calculators/Curta-Type-I-3x`, head `1f3dc22`, run from
outside the project, nothing written there) a snapshot after 7 x 2 is
restored into three simulations: before the change all three are
accepted; after it, the same machine is accepted with result digits
`[4, 1, 0, 0]`, and the machine whose `crank_lift` stops at 8 mm and the
unchanged class under another module are refused. Its
`EventDrivenOperationsTest`, which snapshots and restores the Curta in
two tests, passes 11 tests and 57 subtests before (35.33 s) and after
(35.70 s). No document, identity or corpus changed. That a declared
`Driver` or `State` range is not part of the identity is filed in
`../../warts.md`.

## `production-reads-once`

From "Findings from the adversarial review of the framework cycle `production-layer` (4 October 2026)", items 1 and 2:

- **Defect: binding a production after a build doubles the placements of
  children positioned in a rigid internal node's `render()`.** The
  `model-consumption` spec's scenario "Read an advanced machine" promises
  that structural reading leaves established operation values unchanged.
  It holds when the facade reads first and fails when the lifecycle ran
  first: `ModelSnapshot.occurrences` (`machinome/model.py:354-365`) calls
  `render()` on every non-assembly internal node unless its own
  `_production_rest` cache exists, and a node already rendered by
  `_prepare()` or `assemble()` has no such cache, so the author's `render()`
  runs a second time and re-applies every `translate`/`rotate` to the same
  declared children. The doubled structure is then cached and returned by
  every later `render()` (`machinome/node/internal.py:39-42`); nothing
  raises. Measured: child operations 1 in the facade-only, lifecycle-only
  and facade-then-lifecycle orders, 2 in the lifecycle-then-facade order,
  also with the fusion inside a prepared assembly; a regeneration after the
  doubling fused a different solid (content id `f966a273…` became
  `c49003bd…`). The cycle's test
  `test_rigid_rest_placements_reused_by_normal_lifecycle` covers the
  facade-first order only, and the Curta slice prints leaves, so neither
  could meet it. Exposed by any process that builds, snapshots or serves a
  model and then binds a `Production` to the same instance. Remedy shape:
  the walk reuses the node's `_prepared_rendered` when the lifecycle
  already rendered it and renders once otherwise, pinned by a red test in
  the lifecycle-first order that compares operations and the regenerated
  content id. **Untriaged.**
- **A missing input file at binding escapes `Production(model)` as the
  facade's own error.** A node whose `files` names a path that does not
  exist makes the constructor raise
  `machinome.model.ModelInputChangedError("input observation failed: …")`:
  `Production.__init__` (`machinome/production/profile.py:281-288`) wraps
  only `OSError`, so the production error taxonomy is bypassed, and the
  message says a file changed when it never existed. **Untriaged.**

**What shipped.** `production-reads-once`
(`openspec/changes/archive/2026-10-07-production-reads-once/`) changes two
functions of `machinome/model.py` and one branch of
`machinome/production/profile.py`. The structural walk of
`ModelSnapshot.occurrences` reads a rigid internal node that preparation
already rendered (by `trigger_stl()` or `assemble()`) from preparation's
own render, `_prepared_rendered`, and renders, once, only a node that
preparation never rendered; the author's `render()` therefore runs at most
once per instance in either order. `ModelSnapshot(model)` refuses a source
a node names that does not exist when it is constructed with
`FileNotFoundError`, whose message names the node (`Nut 'nut' names an
input file that does not exist`) and whose `filename` is the path, and
`Production(model)` refuses it with `ProductionExportError`
(`RootProduction cannot bind: Nut 'nut' names an input file that does not
exist: <path>`); a source observed and later changed or deleted is still
`ModelInputChangedError`. Four tests were red first: in
`tests/test_model_consumption.py`,
`test_binding_after_a_build_keeps_rest_placements` for a faceted
`FusionNode` of two self-materializing boxes, one translated in
`render()`, alone and inside an assembly (each "Left contains one more
item: <machinome.node.operations.Translation …>"), and
`test_missing_source_is_refused_at_construction` (`ModelInputChangedError:
input observation failed`); in `tests/test_production.py`,
`test_missing_model_source_is_refused_at_binding` (the same error); the
guard `test_source_deleted_after_binding_is_still_a_change` was green
before and after. The reproduction gave two operations on the translated
child and a regenerated fused STL `fd3b003d…` in place of the built
`f435a10c…` in the lifecycle-then-facade order before the change, and one
operation with `f435a10c…` in all four orders after it; `assemble()` then
the facade went from 1 -> 2 operations to 1 -> 1. The originating Curta
production slice (`projects/Calculators/Curta-Type-I-3x`, worktree
`WTs/production-layer-3x`, `7c9121e`) prints leaves and binds files that
exist, so it validates that nothing regresses. Its own README command
cannot collect against the 0.8 framework (its test imports `AssemblyNode`
and `StepNode` from the root of `machinome.node`), so it ran as a copy of
its `production/` package in the scratchpad with that one import rewritten,
over the Curta's `main` (`1f3dc22`), nothing written in the project: 6
passed in 117.56 s before and 117.04 s after. That a missing source on a
child only `render()` creates, and a source changed between a verified load
and binding, still read as changed inputs is filed in `../../warts.md`.

## `production-reports-in-scope`

From "Findings from the adversarial review of the framework cycle `production-layer` (4 October 2026)", the items on the Markdown gate, the overlap scope and the declaration paths:

- **The Markdown gate refuses text that is not a dependency.** `_markdown`
  (`profile.py:143-181`) rejected `if a<b then c>d ok` and a code span
  containing a tag as an "unsupported HTML dependency". Version 1 was meant
  to refuse dependencies a bundle cannot carry, not inequalities or quoted
  markup. **Untriaged.**
- **An overlap anywhere in the root blocks an unambiguous child's reports.**
  With an overlap under `right`, `production.left.bom` raises
  `ProductionConflictError`: `_read` (`profile.py:361-374`) checks every
  overlap finding of the shared root, not the ones inside the queried
  scope. The design refuses ambiguous totals; the child's totals are not
  ambiguous. **Untriaged.**
- **Declaration paths change shape with the repetition count.** A
  one-member repeated child binding is named `kids/arbitrary_name` and a
  two-member one `kids-0/arbitrary_name` (`profile.py:1083-1085`), although
  the binding is a tuple in both cases, as the spec requires. A consumer
  test pinning a declaration path breaks when a count parameter moves from
  one to two. **Untriaged.**

**What shipped.** `production-reports-in-scope`
(`openspec/changes/archive/2026-10-07-production-reports-in-scope/`)
changes `machinome/production/profile.py` only. The Markdown gate first
reduces an instruction to what a CommonMark renderer reads, by a line scan:
fenced code blocks are dropped, code spans become a space, an HTML block is
kept whole; wherever the scan could differ from CommonMark it keeps more
text. It then refuses an HTML tag only when its element embeds, loads or
executes content (`img`, `script`, `link`, `iframe`, `object`, `style`,
`svg`, …) or it carries an attribute that names a resource (`src`, `href`,
`data`, `srcset`, `style`, `xlink:href`, …), so `if a<b then c>d ok`,
`<kbd>Ctrl</kbd>` and markup quoted in code are accepted, while
`<img src>`, `<a href>` (an HTTPS one included), `<link>` and `<script>`
are refused as before; a reference whose only definition is inside fenced
code is now refused as unresolved. A binding's reports are refused with
`ProductionConflictError` only for an overlap that names an occurrence
within its own scope, the test `findings` already used; the root's scope
holds every occurrence, so it still refuses on any overlap. A repeated or
tuple child binding names its members by index at every count, so a
one-member repetition's member is `kids-0`, in every declaration path and
in the draft manifest; a single reference is still named without one. In
`tests/test_production.py`, 18 cases were red first: 13 accepted Markdown
cases (`unsupported HTML dependency`, or `unsupported local or URL
dependency` for a link or definition in code), the fenced-definition
refusal (DID NOT RAISE), an inequality read through `steps` and `export`,
`left.bom` beside an overlap under `right`, `right.bom` beside a parent
Item reaching into `left`, and a one-member repetition's
`['kids/arbitrary_name'] != ['kids-0/arbitrary_name']`; 23 guards were
green before and after. The reproduction refused every gate case, every
report of `left`, `right` and the root, and named a one-member member
`kids` before the change; after it, the non-dependencies are accepted,
`left` reads `[2]` and `right` (in the second fixture) `[3]` while the
overlapping child and the root still refuse, and the manifest's `bindings`
are `['', 'kids-0']` at one member. The originating Curta production slice
(`projects/Calculators/Curta-Type-I-3x`, worktree `WTs/production-layer-3x`,
`7c9121e`) has twelve Markdown files with no `<` or `>`, declares no
overlap, and binds its two `springs` tuples of ten and five members,
already indexed, so it validates that nothing regresses; its test pins no
declaration path, and no project edit is needed. Its own README command
cannot collect against the 0.8 framework (its test imports `AssemblyNode`
and `StepNode` from the root of `machinome.node`), so it ran as a copy of
its `production/` package in the scratchpad with that one import rewritten,
over the Curta's `main` (`1f3dc22`), nothing written in the project: 6
passed in 118.81 s before and 119.63 s after, with the same 417 findings
and 21 binding paths.

## `refuse-the-undeclared-file-by-name`

From "name-the-missing-file (2026-09-15, found while fixing)", the whole
section:

Findings outside that cycle's ratified scope, from
`openspec/changes/name-the-missing-file/proposal.md` ("Out of scope") and
`design.md` (reviewer's note 1); **status: filed here; triage open**. No
framework code changed for either.

- **The four adapters refuse a missing DECLARATION inconsistently.**
  `StlNode` and `StepNode` raise `ValueError` naming the class
  (`stl.py:162`, `step.py:476`). `JScadNode` raises a bare `Exception`
  that names only `"OpenJScadNode subclass"`, never the actual subclass
  (`jscad.py:28-30`). `OpenScadNode` has no check at all: an
  undeclared `scad_source` reaches `os.path.join(basedir, None)` and
  raises `TypeError: join() argument must be str, bytes, or os.PathLike
  object, not 'NoneType'` (`openscad.py:40`), naming neither the class nor
  the attribute. This cycle adds a fourth failure family — a *declared but
  absent* file — that IS consistent across all four (`FileNotFoundError`
  or `ValueError`, always naming the class); the pre-existing
  *undeclared* family above it is not touched.
- **The builder's own wrapper text reads as broken English and names the
  model, not the node.** `Builder._start()` wraps a load-time failure as
  `f'{self.path}: failed to {stage} project: {exc}'` (`builder.py:356`,
  stage `'load'` or `'inspect initial sources'`), e.g. `parts:MissingStl:
  failed to load project: ...` — "failed to load project" reads oddly for
  a single model reference, and `self.path` is the CLI's model argument,
  not the node whose declaration was wrong; for a leaf nested inside an
  assembly the wrapper still names only the root (`evidence.md`,
  measurement 4/"After"). This cycle's own message, inside `exc`, does
  name the node; the wrapper around it is untouched.

**What shipped.** `refuse-the-undeclared-file-by-name`
(`openspec/changes/archive/2026-10-07-refuse-the-undeclared-file-by-name/`)
makes the refusal in `require_source_file` (`machinome/node/sources.py`):
a declared value that names no file, `None` or empty, is refused first,
before anything is resolved, with `ValueError` naming the class, the
attribute and the module that defines the class (`BareStl does not declare
stl_source. Set stl_source in <module> to the path of the file its part is
read from, relative to that module's directory or absolute.`; for an empty
value, `EmptyScad declares scad_source = '', which names no file. Set
...`). Its `path` argument became optional: given the declared value
alone, it resolves it beside the defining module, as the adapters did, and
it returns the path it judged in both forms. `StlNode`, `StepNode`,
`JScadNode` and `OpenScadNode` dropped their own guards and joins and take
their source from one call, and the leaf-contract stand-in `MeshPart` does
the same, so a leaf written outside the core in that form gets the refusal
unchanged; the leaf contract stays at version 3. The builder's line on a
failed launch reads `The model <reference> could not be loaded: <message>`,
`The sources of the model <reference> could not be read: ...` or `The
model <reference> could not be assembled: ...`, by stage; the inner
message, which names the leaf's class, stands as it is, and `errors.json`
and the reload path are unchanged. Red first: 14 failures, the eight
adapter subtests (`StlNode` and `StepNode` lacked the module and the new
words, `JScadNode` raised `Exception`, `OpenScadNode` `TypeError` or "is
not a file"), `MeshPart`'s `TypeError`, the missing fourth argument, the
three builder lines (`model.py: failed to load project: broken model`, and
the inspect and assemble lines alike) and `machinome build assembly:Rig`
in a scratch project (`assembly:Rig: failed to load project: BareStl is an
StlNode and must declare ...`); every existing test of
`tests/test_missing_source_file.py` and both
`test_a_missing_declaration_fails_naming_the_class` stayed green unedited.
On the probe project, all nine undeclared or empty leaves (the four
adapters twice and `BareMesh`) were refused in four shapes before and in
the one shape after; a marking's `Svg('')` is now refused as naming no
file and `Svg(None)` still fails in `Svg.resolve`'s own join, outside this
change; the six builds exit 1 before and after, with the new line. A scan
of the 16 791 Python files under `projects/` finds no test or code that
asserts on, matches or catches an old text (11 hits, all `"project: "` in
unrelated fields and docstrings), so no project was run or edited.

## `report-the-instant`

From "honour-skip-and-xfail (2026-09-15, found while fixing)", the whole
section:

Findings outside that cycle's ratified scope, from
`openspec/changes/honour-skip-and-xfail/proposal.md` ("Out of scope") and
`design.md` ("Reviewer's notes (ratification, 2026-09-15)", note 1);
**status: filed here; triage open**. No framework code changed for any of
these.

- **The runner keeps the LAST failing instant's traceback, not the
  first.** `run_test`'s `error` is rebound on every raising instant
  (`manager/test.py`) and only the last is printed, so a method that
  fails at instant 0 and again, differently, at instant 2 reports
  instant 2's traceback. This change only stopped a SKIP from becoming
  that traceback (`error` is now set in the `except Exception` arm
  alone); which real failure is reported when several instants fail is
  left exactly as it was.
- **No failure report names the instant it happened at.** `FAIL!`'s
  traceback shows where in the method's own source the assertion raised,
  never which declared instant (`0`, `0.5`, `1`, ...) it raised at under
  `@testing_steps`/`@testing_instant`. A maker reproducing a sweep
  failure has to re-run the method by hand to find the instant.
- **A non-skip exception from `setUp`, or any exception from
  `setUpClass`, aborts the run without a verdict.** `run_test` now
  catches `unittest.SkipTest` from `setUp` and reports the method
  skipped; any OTHER exception `setUp` raises still escapes `run_test`
  uncaught, as does anything `setUpClass` raises, and `handle` catches
  only `StopTestRun` — so the run stops with a bare traceback, no
  summary line, and no verdict for the tests that would have followed.
  `unittest` itself reports these as ERRORS, distinct from failures, and
  keeps running the rest of the suite; `machinome test` has no error
  classification at all, for a set-up exception or any other.

**What shipped.** `report-the-instant`
(`openspec/changes/archive/2026-10-07-report-the-instant/`) changes
`machinome test`'s runner alone (`machinome/manager/test.py`). A failing
method prints the traceback of its first failing instant, the later ones
counted and not printed; a method that declares its instants names that
instant after `FAIL!`, written so that `@testing_instant` given it runs
the same value (`FAIL! at instant 0.020833333333333332`), and a sweep adds
`(K of N instants failed)`, or `(--failfast stopped the sweep at instant P
of N)`; a method declaring no instant reads `FAIL!` as before. An
exception other than a skip from `setUp` is an ERROR of that method
(`ERROR! (setUp raised)`, the traceback, no instant run, no `tearDown`),
and from `setUpClass` an ERROR of each of the class's methods (`ERROR!
(setUpClass raised)`, the traceback once, no method run, no
`tearDownClass`); the run goes on, the summary line gains `, E errors`
after `F failed` when there are any, the run exits 1, and `--failfast`
stops on an error. A `unittest.SkipTest` from `setUpClass` skips the
class's methods with its reason, as the class decoration does. A debugger
quit in set-up still ends the run, and an expected-failure marking does
not turn a set-up error into an expected failure. Exceptions from a
method's own body stay failures, and `tearDown`/`tearDownClass`
exceptions still escape (filed in `warts.md` under this change's name).
Red first: 14 tests of `tests/test_manager_test.py` (the last instant's
message printed and no instant named; `RuntimeError` and `SkipTest`
escaping `run_class_tests`, `run_tests` and `handle`; no error count in
the summary), with two guards green both ways; the pin
`test_a_non_skip_setup_error_still_propagates` replaced. On
3DPrintedClocks' mantel clock 34 (`ec2a05d`, `--mesh --volume-epsilon
0.001`), nothing written in the project: 20 tests, 15 passed, 5 failed
before and after, the same `AssertionError` lines, and the five `FAIL!`
lines now read `at instant 0.0 (8 of 8 instants failed)`, `(48 of 48 ...)`,
`at instant 0`, `at instant 0` and `at instant 0.0 (32 of 32 instants
failed)`. A provoked sweep over the minute hand's travel printed the
centroid read at the last instant, `(47.837, -83.031, 45.609)`, before,
and `FAIL! at instant 0.0 (4 of 4 instants failed)` with the first
instant's centroid, `(65.434, -65.434, 70.495)`, after.

## `key-the-shape-on-its-observation` (found already fixed)

From "`cached_shape` keys a loaded BREP on `(path, float mtime)`
(2026-09-29, found while designing persistent-verdict-memo)":

**Status (as filed): recorded; triage open.**

`machinome.exact.cached_shape` keeps one imported CadQuery shape per
`(brep path, os.path.getmtime(...))`, a float mtime, and `shape_identity`
hands that key to every exact-path cache: the bounding boxes, the face
boxes, the placements and the in-process verdict memo. Every other artifact
cache has since moved to the full `ArtifactObservation` (realpath, device,
inode, size, mtime_ns, ctime_ns) -- `cached_base_mesh`, the Manifold and
bounds caches, `currency._file_key` -- because `_atomic_export` stamps every
artifact with its SOURCE's mtime: a rebuild not caused by a source edit
(a changed producer recipe, a deleted artifact, a framework or kernel
upgrade that exports differently) reproduces the old mtime while its bytes
may differ. Under the float key such a rebuild inside one long-lived
process keeps serving the old shape, and every exact cache keyed on it.

`persistent-verdict-memo` (ADR-156) did not change this key; it was a
non-goal. The persistent tier guards itself instead: `cached_shape` now
records the observation it loaded from (observed before and after
`importBrep`), and a persisted identity is the digest of THOSE bytes, or
none when the file has changed since. The in-process gap is unchanged:
within one process a same-mtime rebuild still reads as current. Candidate
fix: key `cached_shape` on the load observation, as the mesh caches key on
theirs. Evidence: design.md "Non-Goals" and §3 of the
`persistent-verdict-memo` change; no project has reported a wrong verdict
from it.

**What shipped:** nothing in this campaign. `leaf-contract` (3 October
2026, ADR-164) had already keyed `machinome.brep_cache.cached_shape` on
`(path, (device, inode, size, mtime_ns, ctime_ns))` from one stat, with
the scenario "A replacement under an unchanged source mtime is not served
stale" in the `brep-geometry` spec and `tests/test_shape_cache_observation.py`
pinning it; the entry was never closed. Reproduced at `904f2a6` on
7 October 2026: a same-stamp replacement (renamed into place, rewritten
in place, or rewritten in place at the same size) is served new. The
case ADR-164 accepts, an in-place same-size rewrite within one ctime tick
by a writer other than the core, remains as that ADR records it (208 of
300 such rewrites served stale on ext4); adding the realpath through
`observe_artifact` per request (ADR-164's rejected option 5) would cost
about 100 µs against 3 µs per request, 2 to 5 % of wall clock 02's warm
run, and would not close it. Wall clock 02 (`--brep`, scratch build
directory): 16 passed, 6 failed, its own, cold 1152 s, warm 23.7 s. The
`_verdict_key` docstring and ADR-156's consequence, which still said
`(path, float mtime)`, were corrected with this closure.

## `strict-manual-build`

From "Three findings from filming the clocked Curta (1 October 2026, found by Videomaker's curta-video campaign)", items 5 and 6:

5. **The strict manual build is not a gate.** `sphinx -W` fails on `main` with
   five warnings in untouched lines (`docs/reference/api.rst` 23, 35, 76 and
   the `Sim.initial` and `Sim.state` docstrings). Found by `sim-identity`.
6. **A stale known gap in `docs/architecture.md`:** "A clocked model is
   published but not yet VIEWED" predates viewer 0.7.0, which reads document
   versions 1 to 13. Found by `sim-identity`.

From "Inmoov-sim (2026-09-10, stage B on ADR-098)":

- **A site joint's value is the line in the parent's frame where the
  child FINALLY rests, after every rest operation the parent applies to
  it — and when one of those is conditional, a plain value is silently
  wrong for the other branch.** `Forearm` places its wrist `axle` with
  `_in_wrist` and then, when `presented` is true, `present()`'s turn;
  the site joint `Bolt(turn=Revolute(axis=..., at=...))` written as the
  plain pre-presentation numbers reproduced the reference poses only
  with `presented=False`, and with the project's own default missed by
  622 mm³ of palm/axle interference at rest and 14.2 mm at full wrist
  travel, with no refusal. Correct: a callable of the realized parent
  (`_presented(vector)` rotating the value through `PRESENTATION` when
  `forearm.presented`), which is the ADR-098 contract working as
  designed — the parent's frame is where the child ends up — but nothing
  in the docs says a plain site value should be treated as suspect
  whenever the parent's own rest placement of that child is conditional.
  Triage: one sentence in `docs/driving.rst`'s site paragraph and in the
  shop craft skill; no framework change.

  **Remaining (2026-10-04):** not done. `docs/driving.rst` no longer exists;
  the site paragraph is now in `docs/concepts/joints.rst`, which says
  nothing about a conditional placement.

**What shipped.** `strict-manual-build`
(`openspec/changes/archive/2026-10-07-strict-manual-build/`). CI's docs job
(`python -m sphinx -b html -W docs docs/_build`) and Read the Docs
(`fail_on_warning: true`) were green because neither built nitpicky: Sphinx
reports an unresolved cross-reference only under `-n`, and the five
warnings appeared only in the stricter build the manual's procedure names.
`docs/conf.py` now sets `nitpicky = True`, so both builds, unchanged, refuse
a reference to nothing; `tests/test_docs_exports.py`'s `StrictBuildTest`
pins the setting (red first: `docs/conf.py does not set nitpicky`) and
Read the Docs' `fail_on_warning`. With the setting alone, the CI command
failed in an environment holding `docs/requirements.txt` alone with the
five warnings: two `api.rst` references naming `AssemblyNode` without its
module (`api.rst:193` and `:205` at the bench commit), the
`OpenScadNode.__init__` docstring's `name keyword argument:` line, which
napoleon read as a parameter `argument` of type `name keyword` (attributed
to `api.rst:236`), and the `Sim.initial` and `Sim.state` docstrings, whose
first lines napoleon read as `Type: description` and rendered as a bogus
"Type:" field. Each was fixed where it is written: the two references name
`machinome.node.assembly.AssemblyNode` with their rendered text kept and
now link, the three docstrings render as written (`initial` and `state`
with no "Type:" field, the parameter called `name`). The CI command then
built with no warning, and so did `-n -W --keep-going -E`. In
`docs/architecture.md`'s "Known gaps and tensions", four entries closed by
named work were deleted: the clocked model "not yet VIEWED" (viewer
ADR-062 and ADR-063, accepted, execute a clocked machine, and the released
viewer reads document versions 1 to 13), Create React App (viewer ADR-052
supersedes ADR-013), `declared_ports` not memoised (commit `6ff98062`,
22 September 2026, caches each completed class's ports on the class) and
the viewer's whole-graph walk (viewer ADR-060); the manual-build entry was
rewritten to the one fact still true, that the CI browser-snapshot job
installs the viewer from Git; and the self-read gate entry's dead
`docs/scenarios.rst` became `docs/concepts/running.rst`. The joints page's
site-declaration paragraph (`docs/concepts/joints.rst`) gained the one
sentence: a site joint's values are read where the child finally rests,
after every rest operation the parent applies to it, so when one is
conditional a plain value is right for one branch only and the argument is
written as a callable of the realized parent; `tests/test_mate_contract_docs.py`
pins it (red first: `'finally rests' not found`). The entry's other half,
the same sentence in the studio's craft skill
(`machinome-studio/shop-skills/machinome/SKILL.md`), is the studio
repository's and is recorded in the campaign note's outside-the-framework
step.

## `release-metadata-and-vestiges`

From "import-the-artifact-by-path (2026-09-15, found while fixing)", both
entries. The section's introduction read: "Findings outside that cycle's
ratified scope, measured in
`openspec/changes/import-the-artifact-by-path/evidence.md` ("Noticed and
left out of scope"); **status: filed here; triage open**. No framework
code changed for either." With both entries closed the section was empty,
and its heading and introduction left `warts.md` with them.

- **A rigid leaf's own `.scad` stops describing its geometry after the
  first build: it becomes a self-import of the STL it exists to
  regenerate.** Build 1 writes it as the leaf's own geometry (e.g.
  `cube(size = [10, 10, 10]);`); once the STL is current, `assemble()`'s
  up-to-date branch sets `self.model = self.artifact_import(self.local_stl)`
  (`base.py:862-863`) and then calls `generate_scad()`, so the file that is
  supposed to be able to rebuild the STL from scratch merely imports it.
  It resolves (same directory), so it is not this change's bug.
  `FusionNode`'s own `.scad` is written the same self-importing way, but
  harmlessly: its STL is produced natively (OCCT or manifold3d), never by
  OpenSCAD from that `.scad`.

**What shipped.** `release-metadata-and-vestiges`
(`openspec/changes/archive/2026-10-07-release-metadata-and-vestiges/`).
Measured at `184b069` before the change: since `scad-presentation`
(4 October 2026) `assemble()` writes no `.scad`, so `machinome build` run
twice left a `Solid2Node`'s own `.scad` as its geometry (`$fn = 24;` then
`cylinder(h = 8, r = 3);`, same inode and stamp), and no build writes a
fusion's `.scad` at all. The up-to-date branch still set the model to the
import of the leaf's own STL, though, and that is what the leaf's
`scad_code` and `generate_scad()` wrote: `machinome snapshot --renderer
openscad` of a current `FineCylinder` (`tests/scad_where_read_project`)
rewrote its kept `.scad` as `import(file =
"machine-FineCylinder-2111f2f9079a.stl", ...)` under a new inode, and a
fresh `OpenScadNode` assembled with its STL current gave `scad_code` ending
in that import instead of its module call. The branch now asks the node
for its presentation of a current artifact through one private hook,
`_current_artifact_presentation()`, beside `_require_model()`: the base
answers with the import of its STL, as before, and `ScadLeafNode`, the
OpenSCAD family's leaf base, answers None, so the model is rendered on
demand from the leaf's own geometry. After the change the same snapshot
left the file's bytes, inode and stamp as the build wrote them, and both
fresh `scad_code`s equal their built files.
`tests/test_scad_presentation.py` pins both
(`test_a_current_leafs_scad_code_is_its_geometry`,
`test_a_current_scad_authored_root_keeps_its_scad_as_built`, red first);
the presentation golden stays at 0 differences. Nodes outside the family
keep the import as their up-to-date presentation.

- **`self.mesh_scad_file` / `self.mesh_stl_file` are vestigial.** Nothing
  in `machinome/` writes or reads them beyond the assignment at
  `base.py:711-712`.

**What shipped.** `release-metadata-and-vestiges`. `mesh_scad_file` had
already gone with `openscad-out` (4 October 2026). `mesh_stl_file` was
still assigned in `AbstractBaseNode.__init__` and listed in
`parameters._RESERVED`; no reader in `machinome/`, `tests/`, `docs/` or the
catalogue's 14,618 Python files, and no `.mesh.stl` named anywhere. Both
went. Removing the reserved name is a loosening: a parameter, flag,
marking, frame or mate may now be named `mesh_stl_file`, as it may be
named anything else a node does not carry. `tests/test_declarative_nodes.py`
pins the absence (`test_a_node_carries_no_mesh_stl_file`, red first) and
that every name `_RESERVED` lists is an attribute a node carries
(`test_every_reserved_name_is_an_attribute_a_node_carries`). No changelog
bullet: the attribute was never in the manual.

The third entry the cycle measured, "The `viewer` extra carries no version
floor", stays in `warts.md`: which viewer the extra should install is the
pilot's decision, recorded in the campaign note under "Deferred to the
pilot".

## The exact-geometry flake (found already fixed)

From "Expression math and mechanisms (2026-09-06)", Framework item 10:

10. **Non-reproducible flake in `tests/test_exact_geometry.py`.**
    `ExactArtifactTest::test_a_shape_without_file_identity_is_not_cached`
    failed once in a full run and passed alone and in two further full
    runs. It asserts `assertIsNot` on two `placed_shape` results, so an
    object-identity or GC-recycling assumption is the likely cause. Seen
    once during `mechanisms`.

**What shipped:** nothing in this campaign. The mechanism was found by
investigation 3 of fix-warts-3 (7 October 2026, report in its
scratchpad, reproduced on the bench at `87a5864`): `brep_cache._shape_keys`
is keyed on `id(shape)`, safe only while `_shape_cache` keeps the shape
alive; the class's `setUp` then cleared only `_shape_cache`, leaving
stale ids behind, and when CPython reused such an address for the test's
new shape it inherited an old file's identity, the second placement was
a cache hit, and `assertIsNot` failed. Commit `8d6bfedd` (8 September
2026, finding AR-01 of the performance due diligence) added
`clear_exact_shape_caches` (now `tests/brep_test_support.py`) and the
regression test `tests/test_brep_test_isolation.py`; the entry was never
closed. The test now lives in `tests/test_brep_geometry.py` and calls
`cached_placement`. Provoked on demand: with the old fixture pollution
and the old reset, 18 of 50 runs fail with the original
`unexpectedly identical` error; with the current reset, 0 of 50, under
garbage-collection pressure and ten hash seeds alike.

## `count-bodies-without-repair`

From "YouCanBuildDog", whose other two entries stay in `warts.md`:

- **`networkx` is an undeclared need of the mesh path.**
  `assertNoDisconnectedSolids` now takes the exact path for an exact solid
  (`_routes_exact`), which closed the first half of this finding. Its mesh
  path (`split(only_watertight=False)`) can still reach trimesh's
  `fill_holes`, which imports `networkx`, and `networkx` is not among the
  package's declared dependencies: the workspace venv has it only because
  it was installed by hand on 2026-09-07. Whether trimesh's split still
  reaches `fill_holes` is unverified. Condensed 2026-10-04.

**What shipped.** `count-bodies-without-repair`
(`openspec/changes/archive/2026-10-07-count-bodies-without-repair/`). It
did reach it: both connectivity assertions counted bodies with
`split(only_watertight=False)`, whose default `repair=True` sends every
component that is not watertight through `fill_holes`, and `fill_holes`
needs `networkx`, which trimesh requires only for its `easy` extra and
machinome did not declare. With `networkx` refused on import, the four of
six STL fixtures that are not watertight raised `ModuleNotFoundError` in
`assertNoDisconnectedSolids` and in `assertJoined`'s mesh count,
`_body_count`. The repair's result was never read: trimesh 4.4.9 builds
the list of components before it repairs any and returns that same list,
so filling a hole cannot change the count, and over the 465 STL files of
the four catalogue projects that combine `require_watertight = False` with
`assertNoDisconnectedSolids` (SO-ARM100, roboto_origin,
hexapod_spiderbot_model, mechanical-multiplier; 157 not watertight) the
count at `repair=True` and at `repair=False` is the same for every file.
`_body_count` now splits with `repair=False`, as `node/stl.py:_bodies`
already did, and `assertNoDisconnectedSolids` counts through it; no
dependency was added. `Robotic-Arms/SO-ARM100`'s three `machinome test
--mesh` suites, run read-only against the bench with `networkx` refused in
every process, went from 3 passed 1 failed, 5 passed, and 11 passed 1
failed (both failures `ModuleNotFoundError`, in
`test_each_selected_body_is_connected` and `test_solid_integrity`) to 4, 5
and 12 passed, the counts they reach with `networkx` present, before and
after. `tests/test_connectivity.py` pins it:
`CountWithoutRepairTest.test_open_meshes_are_counted_where_networkx_is_absent`
(red first, in a subprocess where `networkx` cannot be imported), a guard
over the six fixtures' counts and verdicts, and a comparison with the
repairing split that runs wherever `networkx` is installed.

## `a-witness-is-interior-in-its-neighbourhood`

From "OpenAstroMount — a scenario test refused by the exact common guard (3 October 2026)":

Found validating the framework change `exact-engine` on a branch of the
project. `OpenAstroMountScenarioTest.test_every_instruction_reaches_its_documented_end_state`
fails on the project's `master` against the unmodified framework (feb23f2)
and against the change alike, with `ExactCommonInconsistency`: the exact
common of `housing` and `rolamento_uc206_valor_predeterminado_1` is empty
while a point near (-2.02, 265.56, 442.98) classifies strictly inside both
solids beyond their face tolerances. Same pair, same witness to the last
digit before and after the change, so it is not the engine's doing. Either
the housing and the bearing genuinely overlap at that pose, or the guard
witnesses a false empty on a valid common. Not triaged; the project's other
eight tests pass. Evidence: `openspec/changes/archive/2026-10-03-exact-engine/evidence.md`, §6.

**What shipped.** `a-witness-is-interior-in-its-neighbourhood`
(`openspec/changes/archive/2026-10-07-a-witness-is-interior-in-its-neighbourhood/`,
ADR-142 amended 2026-10-07). The guard witnessed a false empty on a valid
common. The polar frame's F206 housing and the right ascension body's UC206
insert, both valid vendor STEP solids, meet on two concentric spheres of
radius 31.000 mm, a contact of zero volume at every right ascension angle,
so OCCT's empty common is right; the witness lay 31.1357 mm from the
spheres' centre, outside the insert, whose zero-tolerance classifier
answered IN there alone (OUT at its neighbours 10⁻⁴ mm away; a 0.01 mm ball
there has no common with the insert; 40,000 samples found no point inside
both). The first amendment's face-tolerance test passed it, at 0.0999563 and
0.135651 mm from the two solids' faces. In `machinome/engine/brep.py`,
`_resolved_interior` now returns a candidate's margin, its smallest face
distance, or `None` within a face's tolerance, and `_false_empty_witness`
counts a candidate resolved in both solids only when its six axis
neighbours at half the smaller margin are classified IN both as well; no
face lies within the margin, so a neighbour read OUT proves a reading
wrong, and such a candidate is skipped while the search goes on. No
tolerance, mesh verdict, volume or second Boolean enters; the stencil is
unchanged. `tests/test_witness_neighbourhood.py` pins it: the lone false IN
between two touching boxes (red with `BrepCommonInconsistency`), the margin,
an undecided neighbour refusing verification, and a 0.4 mm slab of shared
interior still refused; the two guard test files pass unedited. The project
(branch `exact-engine-validation`, `58e46cd`, read only with a scratch build
directory) went from 8 passed, 1 failed in 575 s to 9 passed in 1274 s, the
difference being the Target and Present overlap inventories the refusal had
cut short; the pair alone is returned empty in 37.5 s where it was refused
in 28.5 s. ADR-142's originating Curta positioning-ball pairs at ±0.2 mm are
still refused at the same witnesses. Voron-2's thread-seat refusals, genuine
false empties, were not re-run, the project being paused; the re-run is
recorded as owed in `../../warts.md`, with the shallow sphere dent the
stencil misses before and after the change.

## `follow-a-sibling-packages-init`

From "3DPrintedClocks":

- **Generated-artifact freshness is not dependable for source-bound CAD
  leaves.** While changing Wall Clock 22's source-derived hanging-weight
  datum, `machinome test wall_clock_22 --faceted` continued to compare an older
  generated assembly pose. Removing only that model's ignored
  `_build/wall_clock_22` cache was needed to force regeneration; the next
  run also tried to reuse a deleted `clock-Pillars...stl` artifact and raised
  `FileNotFoundError`. The artifact identity appears not to include every
  source adapter dependency, and the test artifact index can retain paths
  that the producer no longer restores. A project should never need cache
  deletion for a source edit to reach a spatial assertion. Candidate
  framework work: make dependency fingerprints complete and make the test
  artifact index self-healing when an artifact is absent. Evidence:
  `projects/3DPrintedClocks`, Wall Clock 22, 2026-09-10. Deferred for a
  framework agent; no framework workaround is part of the clock model.

**What shipped.** `follow-a-sibling-packages-init`
(`openspec/changes/archive/2026-10-07-follow-a-sibling-packages-init/`,
ADR-033 amended 2026-10-07). An investigation on 7 October 2026 ran the
entry again on a byte-identical scratch copy of the project (`ec2a05d1`)
and found one of its three halves still standing. The stale pose does not
reproduce: an assembly's placement is computed on every run, so an edit to
the weight datum moves the weight at once (an edit lowering the weight's
top by 40 mm moved `wound_position` and the weight shell's world
translation from -92.94 to -132.94 with no artifact rewritten).
The retained path does not reproduce: the `FileNotFoundError` came from
the OpenSCAD-era assembly `.scad` files, an artifact kind removed by
`748d6d94`, and deleting a leaf's STL or the whole model build directory
now rebuilds cleanly. What remained was that a leaf did not track all the
code it runs. `machinome/node/sources.py` dropped every `__init__.py` the
import walk reached, and Wall Clock 22 builds its movement through
`from clocks import ...`, where `clocks/__init__.py` re-exports eighteen
modules, so its leaves tracked 3 of the 30 `clocks/` modules they execute;
an edit to the bottom-pillar radius in `clocks/plates.py` left the pillar's
STL and BREP at 31.1 mm while the live render was 37.1 mm, nothing was
rewritten and nothing warned, and deleting the STL by hand regenerated it
while its BREP kept the old shape. `_project_file` now drops an
`__init__.py` only when its package directory contains the importing file,
the case ADR-033's reason covers (a root assembly or sub-assembly above the
importer); a sibling package's `__init__.py` is followed with what it
imports. `tests/test_source_set.py` pins it with a library facade in the
fixture: `test_a_module_behind_a_sibling_package_init_is_tracked` and
`test_editing_a_module_behind_a_sibling_package_init_invalidates_the_artifact`
were red first (the leaf tracked only its own file, and reported its STL
current after the library module was rewritten), and
`test_the_importers_own_package_init_is_not_tracked` guards a `from .
import` leaf against a rule following every `__init__.py` (a probe with
that rule put the whole project in such a leaf's set). On the scratch copy
with the change, the pillar tracks 43 files, 30 of them under `clocks/`,
the ancestor `simulation/__init__.py` and `simulation/wall_clock_22/__init__.py`
stay untracked, and the pillar edit re-derived every leaf (288 files) with
both pillar artifacts at 37.096/37.1 mm; reverted, the documented
`machinome test wall_clock_22 --mesh --volume-epsilon 0.001 --set facing=0`
gave 25 tests, 19 passed, 6 failed (the clock's own NotManifold weight
shell and multi-body bow ties), and a warm rerun rewrote nothing. The
unchanged project, read only with a scratch build directory, gave 25/19/6
before and after; its first run after the change re-derived the model once
(288 files, 43.45 s) and the next rewrote nothing (22.35 s, against
22.52 s before). Projects whose nodes import through a sibling package
rebuild once; in the catalogue that is every 3DPrintedClocks model,
Curta-Type-I-3x and openflexure-microscope.

## Wall clock 02's six failures (diagnosed: the project's, not the framework's)

From "3DPrintedClocks wall clock 02 (2026-09-29, verdict memo across
runs)":

The memo finding is fixed (`persistent-verdict-memo`, ADR-156). Not a
framework fix, recorded for the project: the six `wall_clock_02` failures
measured there (collet against hinge_screw 14.58 mm³, holder body against
the beat crinkle washer 1.58 mm³, `standoffs` two bodies, the weight screw
not meeting its nut), undiagnosed.

**What shipped:** nothing; investigation 5 of fix-warts-3 (7 October
2026, bench `fc26c61`, project `ec2a05d` on `solid-node-simulation`,
read only with a scratch build directory: `--brep` cold 1182.8 s and
warm 31.1 s, 16 passed, 6 failed, the same volumes as on 29 September)
diagnosed every failure as the project's. The B-rep engine, the mesh
engine and an independent CadQuery common agree on each pair to nine
digits. The three sweeps fail at every instant on the collet against
its hinge screw, 14.578953 mm³ = π(1.5² − 1.25²) × 6.75 mm to fifteen
digits: the M3 screw drawn at 3 mm in the author's 2.5 mm tap-drill
hole, visible since `590189b` split the fused holder into fastener
leaves and present in about twenty clocks. `standoffs` is the upstream
preview group of two separately printed parts 275 mm apart (wall clock
36 already splits it; clocks 01 and 02 predate the split). The body
inventory adds the crinkle washer in its 0.16 mm slot (1.578 mm³, the
author's room for a squashed washer, drawn flat) and the bob shell's
three self-tapping nubs per lid screw (1.727 mm³). The weight screw and
its nut touch on coincident 3 mm cylinders with zero shared volume
since `4ac9b7e` bored the nut to the screw's diameter, while the test
still asserts a positive overlap. Side findings for the project: the
README's mesh check refuses the SlidingWeightShell STL as non-manifold
and its paragraph on nudging the shell is stale; the beat screw shows a
0.0025 mm³ mesh-only sliver. How the project represents an intended
overlap (a tapped hole, a nub, a squashed washer) is the pilot's
choice, recorded in the campaign note.

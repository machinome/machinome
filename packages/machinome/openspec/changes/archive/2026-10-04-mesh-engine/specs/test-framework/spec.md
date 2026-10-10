## MODIFIED Requirements

### Requirement: Accelerated intersection evaluation

All intersection-volume assertions (`assertNotIntersecting`,
`assertIntersecting`, `assertIntersectVolumeAbove`,
`assertIntersectVolumeBelow`, the perturbation assertions, and the pairwise
sweep) SHALL route through one shared `(is_empty, volume)` helper.

The helper SHALL select its evaluation path from the compared nodes and from
the run's comparison kernel:

- When the run's kernel is exact and BOTH nodes are exact, it SHALL use the
  EXACT path: each node's
  `shape()` is placed by its composed matrix and the two are intersected by
  the boundary-representation kernel. The result is empty when it contains no
  solid — boundary contact between coincident faces yields no solid and is
  therefore exactly empty with zero volume — and otherwise its volume is the
  summed volume of the solids it contains. A kernel failure raises under the
  `exact-geometry` capability rather than falling back.
- Otherwise, when both nodes expose an `stl_file`, it SHALL use the faceted
  fast path, unchanged. Under the faceted kernel this is the path every pair
  of built solids takes, exact or not: a node's `shape()` is never read, and
  the exact-geometry stack is not imported by the test framework.
- Otherwise (e.g. test doubles implementing only `.mesh`) it falls back to
  intersecting the two `.mesh` geometries through the mesh engine, after
  trimesh's own check that each is a volume and with trimesh's own message
  when one is not, reading emptiness and volume off the resulting mesh as
  trimesh reads them, with identical verdict semantics. It SHALL NOT call
  `trimesh.boolean`, whose backend is the mesh engine's kernel reached outside
  the mesh engine.

The AABB broad-phase SHALL run ahead of every path: each part's local
bounding-box corners are transformed by its composed world matrix into a
conservative world AABB, and if the two boxes are disjoint the intersection is
reported as exactly empty without running any boolean. This is an
exact-negative shortcut that never changes a verdict, and it is what keeps the
exact path's cost proportional to interacting pairs.

For a pair of EXACT solids a SECOND exact-negative tier MAY run after that
broad phase and before any boolean: a FACE-BOX tier with a containment guard.
It SHALL report the pair exactly empty with zero volume, on the exact path,
only when both of the following hold:

- no bounding box of any face of either solid meets any bounding box of any
  face of the other, the two solids' face boxes being compared in one common
  frame, boxes that touch without overlapping counting as meeting rather than
  as separated; and
- one representative point of EVERY solid of each shape is classified strictly
  OUTSIDE every solid of the other shape's placed geometry, each classification
  being of one point against one solid rather than against a shape as a whole.

Each face's bounding box SHALL enclose that face's exact surface, and a box
carried into the common frame MAY be enlarged by a fixed absolute margin
absorbing the arithmetic of that frame change; enlargement SHALL only make the
tier decline, never make it decide. Both classification directions SHALL be
required, because two closed solids whose boundaries do not meet are either
disjoint or one lies wholly inside the other, and only the representative
points of the CONTAINED shape reveal containment. A shape carrying no faces or
no solids, a solid carrying no representative point, a non-finite relative
placement, and any classification that is not strictly outside — inside, on
the boundary, unknown, or refused by the classifier — SHALL each make the tier
DECLINE, and a declined pair SHALL be settled by the boolean exactly as it is
without the tier. The tier SHALL therefore be capable of removing boolean
work only, and SHALL NOT change any verdict, volume, message, or epsilon
semantics: a flush contact's face boxes touch, so it reaches the kernel and
still returns non-empty at exactly 0.0 mm³; a solid wholly inside another is
caught by the containment guard and reaches the kernel; a solid inside another
solid's cavity shares no material with it and is reported empty, which is the
verdict the kernel reports for it too. The tier SHALL run inside the memoized
computation, so its verdict is cached and served under the same identity any
boolean verdict is. The margin, the comparison frame and any internal chunking
of the comparison are internal tuning values and SHALL NOT be exposed as an
assertion argument, flag, or environment variable. The faceted path SHALL NOT
have this tier: a faceted verdict is read from the mesh engine's cached
solids, which carry no faces, and a faceted run reads no solid's exact
geometry at all.

The per-STL cache SHALL be split by what each part of it needs:

- a solid's local bounding box is read from the same cached base mesh the
  `mesh` property uses, keyed by `(stl_file, mtime)` with stale entries
  evicted on rebuild, whenever a solid is selected. This half SHALL NOT
  require the mesh engine and SHALL NOT judge the mesh: selecting a solid,
  placing it in the broad phase, or comparing it on the exact kernel never
  raises for the state of its mesh;
- one mesh-engine solid per `(stl_file, mtime)` (module-level, stale
  entries evicted on rebuild) is built by the mesh engine from that same
  cached base mesh at the FIRST comparison that actually reads it, and never
  for a solid whose every comparison is decided by the boundary-representation
  kernel. The core SHALL hold the solid as an opaque handle and ask the mesh
  engine for every operation on it. Repeated reads SHALL reuse the one cached
  solid, so deferring construction SHALL NOT increase the number of solids
  built for any assembly. The mesh engine's own judgement of the solid it
  built is the admissibility verdict: a solid the engine does not admit SHALL
  raise a `ValueError` naming the STL file and the engine's own word for the
  fault, with trimesh's watertightness verdict as a diagnostic, and SHALL NOT
  be cached; a mesh the engine accepts is compared whatever trimesh says of
  it. A flexible leaf's solid, built from its evaluated mesh at the current
  binding, is judged the same way and the error names the node.

The faceted fast path SHALL then place the cached solids by the mesh
engine's placement, which re-meshes and re-judges nothing, and intersect them
directly through the engine, reading the engine's emptiness and volume off the
result with no conversion back to trimesh, reading the volume only when
non-empty.

Under the faceted kernel the helper SHALL apply the run's volume epsilon to
every verdict it returns, on either faceted path: a result whose volume does
not exceed the epsilon is reported as empty with zero volume. At the default
epsilon of 0.0 this changes nothing.

Verdict semantics on the FACETED path SHALL be preserved exactly: `is_empty`
is the boolean engine's own emptiness — a non-empty result with exactly
0.0 mm³ volume (real flush contact) still counts as fouling at the strict
`volume_epsilon=0` default, and only a `volume_epsilon > 0` comparison may
treat it as clear (the volume-epsilon contract of ADR-025 depends on this;
folding zero volume into emptiness is explicitly rejected — ADR-029). On the
EXACT path that construction does not arise: flush contact produces no solid
and is genuinely empty, so there is no float-noise sliver for an epsilon to
absorb.

The bounding boxes the broad phase transforms SHALL come from the cached base
mesh for every solid, exact or faceted. The candidate pairs a given assembly
emits SHALL NOT depend on whether its solids carry exact geometry.

#### Scenario: Distant parts skip the boolean

- **WHEN** `assertNoPairwiseIntersections` sweeps an assembly where most
  leaf pairs are far apart
- **THEN** disjoint-box pairs are culled without any exact boolean and the
  verdicts are identical to the unculled computation

#### Scenario: Flush contact still strict

- **WHEN** two FACETED parts share a flush face producing a non-empty,
  zero-volume intersection and `volume_epsilon` is 0
- **THEN** the assertion reports a foul, forcing an explicit
  `volume_epsilon` opt-in

#### Scenario: Non-watertight part

- **WHEN** a faceted fast-path assertion reads an STL from which the mesh
  engine builds a solid it does not admit (a box missing a triangle, say)
- **THEN** it raises a `ValueError` naming that STL file and the engine's own
  word for the fault (`NotManifold` from the provider this framework
  resolves), and the solid is not cached

#### Scenario: A mesh trimesh doubts and the engine accepts

- **WHEN** a faceted fast-path assertion reads an STL whose edges are shared
  by four faces, so trimesh reports it non-watertight, and the mesh engine
  admits the solid it builds from it
- **THEN** the assertion compares the part and reaches the engine's verdict,
  with no error

#### Scenario: An exact run never judges a mesh

- **WHEN** the run's kernel is exact, two exact solids are compared, and one
  of them has an STL the mesh engine would refuse
- **THEN** the verdict is the boundary-representation kernel's, no
  mesh-engine solid is built, and the STL's state raises nothing

#### Scenario: The broad phase does not judge a mesh

- **WHEN** `assertNoSolidInterference` selects a solid whose STL the mesh
  engine would refuse and no candidate pair compares it faceted
- **THEN** the sweep completes with the kernel's verdicts and the solid's
  bounding box culls its pairs as any other's does

#### Scenario: An exact tight fit is not interference

- **WHEN** two exact solids meet on coincident cylindrical faces at zero
  nominal clearance, and one is rotated relative to the other
- **THEN** the exact intersection contains no solid, the helper reports empty
  with zero volume, and the facet phase of either part is irrelevant to the
  verdict

#### Scenario: A mixed pair uses the faceted path

- **WHEN** one compared node is exact and the other is not
- **THEN** the helper uses the faceted path and its verdict semantics are
  those of that path

#### Scenario: An exact assembly builds no Manifold

- **WHEN** `assertNoSolidInterference` verifies an assembly whose every selected
  solid is exact
- **THEN** no mesh-engine solid is constructed for any of those solids, and
  the verdict is the one the kernel reaches

#### Scenario: A mixed assembly builds a Manifold only for the solids it compares faceted

- **WHEN** an assembly's selected solids include exact and faceted parts and only
  some candidate pairs route faceted
- **THEN** a mesh-engine solid is built for each solid a faceted comparison
  reads, once each, and for no other solid

#### Scenario: A faceted run compares exact parts on their meshes

- **WHEN** the run's kernel is faceted and both compared nodes are exact
- **THEN** the helper uses the faceted fast path over the nodes' built STLs,
  reads neither node's `shape()`, and the verdict semantics are those of the
  faceted path

#### Scenario: The run's epsilon absorbs tessellation contact

- **WHEN** the run's kernel is faceted with a volume epsilon of 0.5 mm³ and
  two parts' meshes share 0.2 mm³ where their exact solids only touch
- **THEN** the helper reports the pair empty with zero volume, and
  `assertNotIntersecting` passes

#### Scenario: A real overlap survives the run's epsilon

- **WHEN** the run's kernel is faceted with a volume epsilon of 0.5 mm³ and
  two parts share 12 mm³
- **THEN** the helper reports the measured volume and the assertion fails as
  it does on the exact kernel

#### Scenario: An enclosed exact pair skips the boolean

- **WHEN** two exact solids' whole-solid bounds overlap — one solid lying
  inside the region the other spans — while no face of either comes near any
  face of the other
- **THEN** the helper reports the pair empty with zero volume on the exact
  path without running any boolean

#### Scenario: Containment is not mistaken for separation

- **WHEN** one exact solid lies wholly inside another, so their boundaries do
  not meet at all
- **THEN** the containment guard finds a representative point inside the
  partner, the boolean runs, and the helper reports the positive intersection
  volume

#### Scenario: A solid in a cavity is empty

- **WHEN** one exact solid lies wholly inside a cavity of another, touching no
  face of it
- **THEN** the helper reports the pair empty with zero volume, the same
  verdict the boundary-representation kernel reports for it

#### Scenario: Flush contact still reaches the kernel

- **WHEN** two exact solids meet on a coincident face, their touching face
  boxes overlapping
- **THEN** the face-box tier declines, the boolean runs, and the verdict is
  the kernel's own — empty with zero volume for coincident exact faces, as it
  is without the tier

#### Scenario: A compound whose components straddle the partner

- **WHEN** one exact shape is a compound of two solids, one of them wholly
  inside the other shape and one wholly outside it, and no boundaries meet
- **THEN** the per-solid containment guard, classifying each shape's solids
  against each solid of the other, finds the inside component, the boolean
  runs, and the pair is reported with its positive volume

#### Scenario: A shape the tier cannot represent falls through

- **WHEN** an exact shape presented to the tier carries no faces, or a solid
  of it carries no representative point, or the pair's relative placement is
  not finite
- **THEN** the tier decides nothing and the pair is settled by the boolean
  exactly as it is without the tier

#### Scenario: A faceted pair has no face-box tier

- **WHEN** a pair is evaluated on the faceted path, whether because a solid is
  faceted or because the run's kernel is faceted
- **THEN** no face bounding box is computed, no solid's exact geometry is
  read, and the verdict is the mesh engine's own, read off its cached
  solids

#### Scenario: Mesh-only nodes are intersected through the mesh engine

- **WHEN** two test doubles that expose only `.mesh` are compared
- **THEN** their meshes are intersected by the mesh engine, emptiness and
  volume are those trimesh reads off the resulting mesh, exactly the values
  `trimesh.boolean.intersection` returned for them, and `trimesh.boolean` is
  not called

### Requirement: A decided verdict is kept between runs of a project

When a run's comparison policy has the verdict store on and the project under
test has a resolvable build root, the shared `(is_empty, volume)` helper SHALL
keep every verdict it computes in a verdict store, the directory `.verdicts` at
the top of that build root. A LATER process asking the same question of the
same state SHALL be served that verdict without running a boolean. The store
SHALL be consulted only for a comparison the run's own per-run cache has not
already decided. A process with no resolvable project build root SHALL keep no
store and SHALL behave as it does without one.

A project SHALL have one store. Every declared model of the project SHALL
share it, whether a run tests one model or every model with `--all`: a
verdict kept by a run of one declared model SHALL be served to a run of
another declared model of the same project that asks the same question.

A question kept across runs SHALL be identified by state, never by location or
time:

- a rigid solid by the CONTENT of the artifact its compared geometry was read
  from: its exact-geometry artifact on the exact path, its mesh artifact on the
  faceted path. An artifact rewritten with identical content is still the same
  question, and so is a project moved or copied together with its build
  directory. An artifact whose content changed is a different question even
  when its modification time and size are unchanged;
- a flexible leaf by its state, as the per-run cache identifies it;
- the evaluation path, the run's placement quantum and the quantised relative
  placement, exactly as the per-run cache identifies them.

No filesystem path and no timestamp SHALL be part of what identifies a kept
question. Every kept verdict SHALL also be bound to the framework's own source
code, to the installed versions of the geometry kernels and the flexible
evaluator on the verdict path, and to the platform. A verdict kept under any
other framework source, kernel or evaluator version, or platform SHALL NOT be
served.

A verdict decided on the faceted path SHALL also be bound to the identity,
name and version, that the mesh engine resolved for the process reports of
itself; a verdict decided on the exact path SHALL NOT be bound to the mesh
engine. A faceted question whose mesh engine cannot be resolved, or reports no
version, SHALL be computed without being kept or served. What binds every
verdict SHALL be computed without importing a kernel; only a faceted
question SHALL ask the mesh engine for its identity.

The store SHALL hold the kernel's raw verdict (emptiness, volume, and whether
the exact kernel produced it) and no geometry. The run's volume epsilon SHALL
be applied after a kept verdict is read, exactly as after a per-run hit. A
served verdict SHALL therefore be identical to the verdict the kernel produced
for the same question, including flush contact's non-empty 0.0 mm³, and SHALL
NOT change any assertion's outcome, message or epsilon semantics. This is a
recomputation shortcut of the same kind as the per-run cache, not a tolerance.

The store SHALL NOT keep a verdict:

- for a comparison the per-run cache does not cache: a node without a stable
  identity, or a relative placement with a non-finite entry;
- for a comparison whose computation raised;
- for a solid whose artifact changed after its geometry was read.

Such comparisons SHALL be computed exactly as they are without the store.

The store SHALL never make a run fail and SHALL never print. A store that is
corrupt, truncated, written under another framework or kernel version,
unreadable or unwritable SHALL be ignored, and the run SHALL compute whatever
it cannot serve, with the output and exit status it has without a store.

Two runs of one project in progress at once SHALL both complete without
error, and a later run SHALL be served the verdicts either of them kept. A
run whose reading of the store overlaps one reorganisation of it by another
process SHALL still be served every verdict the store held when that run
began, other than a verdict that reorganisation discards under the store's
bound.

The store SHALL be bounded by a fixed internal number of verdicts. When full,
it SHALL discard first the verdicts kept under another framework source,
kernel or evaluator version or platform, and then the verdicts least recently
used. The bound SHALL NOT be exposed as a flag or an environment variable.
Deleting the store SHALL always be safe: the next run SHALL compute what it
is no longer served, and SHALL reach the same verdicts.

Keeping the store SHALL require neither the mesh engine nor the exact-geometry
stack. A run that does not import them without the store SHALL NOT import them
with it.

#### Scenario: A second run is served from the store

- **WHEN** a project is tested, and then tested again by a new process with
  nothing changed
- **THEN** the second run runs no boolean for any comparison the first run
  decided, and reports the same outcome for every test

#### Scenario: An artifact rewritten with identical content is still served

- **WHEN** between two runs a solid's artifact is replaced by a file with
  identical content, under a new modification time
- **THEN** the second run serves that solid's comparisons from the store

#### Scenario: A moved project is still served

- **WHEN** a project directory is moved together with its build directory
  between two runs
- **THEN** the second run, in the new location, serves its comparisons from
  the store

#### Scenario: A content change under a preserved timestamp is recomputed

- **WHEN** between two runs a solid's artifact content changes while its
  modification time and size are restored to their previous values
- **THEN** every comparison involving that solid is recomputed, and its
  verdict is the one for the new content

#### Scenario: A framework or kernel change invalidates kept verdicts

- **WHEN** the framework's source code, or the installed version of a kernel
  or evaluator on the verdict path, differs from the one under which a
  verdict was kept
- **THEN** that verdict is not served and the comparison is computed

#### Scenario: A mesh engine upgrade invalidates faceted verdicts only

- **WHEN** a project's store holds faceted and exact verdicts kept under one
  version of the mesh engine, and a later run's mesh engine reports another
  version, everything else unchanged
- **THEN** the later run computes every faceted comparison again and is served
  every exact one

#### Scenario: A flexible pair is served at an equal state and recomputed at another

- **WHEN** a flexible leaf is compared with a part at one binding in one run,
  and a later run compares them at the same binding and relative placement
  and then at a different binding
- **THEN** the later run serves the equal binding from the store and computes
  the different binding

#### Scenario: A different placement quantum is a different question

- **WHEN** a verdict is kept under one placement quantum, and a later run asks
  the same pair under another quantum whose quantised relative placement
  coincides with the kept one
- **THEN** the kept verdict is not served

#### Scenario: Uncacheable comparisons are never kept

- **WHEN** a run compares a node exposing only `.mesh`, a pair whose relative
  placement has a non-finite entry, or a pair whose computation raises
- **THEN** nothing is kept for them, and a later run computes them again

#### Scenario: A flush contact survives the store

- **WHEN** a flush abutment that reports non-empty with exactly 0.0 mm³ is
  decided in one run and asked again in a later run
- **THEN** the later run reports non-empty with 0.0 mm³, and the strict
  `volume_epsilon=0` default still reports the foul

#### Scenario: A corrupt store is ignored

- **WHEN** the store holds a truncated, garbled or foreign file, or the store
  location cannot be written
- **THEN** the run completes with the verdicts, output and exit status it has
  without a store, and nothing from the store raises

#### Scenario: Two concurrent runs keep both their verdicts

- **WHEN** two processes testing one project keep verdicts in the store at
  the same time
- **THEN** neither fails, and a later run is served every verdict either of
  them decided

#### Scenario: A run that starts while the store is reorganised is still served

- **WHEN** a run begins reading a store within its bound while another
  process is merging the store's files and removing the ones it merged
- **THEN** the run is served every verdict the store held when it began, and
  neither process fails

#### Scenario: An interrupted run leaves a readable store

- **WHEN** a run is killed while it keeps verdicts
- **THEN** the next run reads the store without error, computes what it
  cannot serve, and reaches the same verdicts

#### Scenario: No project build root, no store

- **WHEN** assertions run in a process that has no resolvable project build
  root
- **THEN** no store is created, and comparisons are cached within the run
  only

#### Scenario: Declared models of one project share one store

- **WHEN** a run of one declared model keeps a verdict, and a later run of
  another declared model of the same project asks the same question, of two
  parts both models build identically at the same relative placement
- **THEN** the later run is served that verdict without running a boolean,
  whether each run tests one model or every model with `--all`

#### Scenario: A faceted run of an exact project still never reaches the exact stack

- **WHEN** an all-exact project whose build is current is tested under the
  faceted kernel, in a fresh interpreter, with the store on
- **THEN** the test framework imports no `cadquery`, and reads no node's
  `shape()`

#### Scenario: An all-exact project keeps its store without the mesh engine

- **WHEN** an all-exact project is tested twice, with the store on, on a
  machine where the mesh engine is absent, neither `manifold3d` nor
  `machinome.manifold` being importable
- **THEN** both runs complete as they do without the store, the second is
  served from it, and neither asks for the mesh engine

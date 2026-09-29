## ADDED Requirements

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
  machine where `manifold3d` cannot be imported
- **THEN** both runs complete as they do without the store, and the second is
  served from it

## MODIFIED Requirements

### Requirement: An intersection verdict is computed once per run

The shared `(is_empty, volume)` helper SHALL answer from a per-run cache when
it is asked a comparison it has already decided, and SHALL compute a verdict
only for a comparison it has not.

A comparison's cache key SHALL identify everything the verdict depends on and
nothing else:

- the identity of each compared solid's geometry. A rigid solid has the
  identity the per-artifact caches already use, so a rebuilt part is a
  different key rather than a stale hit. A stock flexible leaf has its STATE:
  its technology, its defining module, the content of its tracked sources,
  its full structural identity, its exact bound values and a full digest of
  its serialized shape specification;
- the pair's RELATIVE placement — one node's composed world matrix inverted
  and applied to the other's — QUANTISED to the run's placement quantum;
- the run's placement quantum itself, so entries made under two different
  quanta in one process can never serve one another;
- the evaluation path taken (exact, faceted, or the `.mesh` fallback), so a
  pair is never served an exact answer from a faceted entry or the reverse.

The relative placement is sufficient because intersection emptiness and volume
are invariant under a common rigid transform: two solids moved together share
exactly the volume they shared before. A repeated key is therefore provably
the same verdict, and reusing it SHALL NOT change any assertion's outcome,
message, or epsilon semantics. This is a recomputation shortcut of the same
kind as the AABB broad phase, not a new tolerance on any assertion.

The quantised placement SHALL be built from the INTEGER cell indices of the
relative matrix — each entry divided by the quantum and rounded to the nearest
integer — and SHALL NOT be built from rounded floating-point values, so that
`-0.0` and `0.0` fall in one cell and two placements are one question exactly
when their integers are equal. A quantum of `0` SHALL restore the exact bytes
of the relative matrix as the placement term, keying the memo precisely as it
was keyed before the quantum existed. A relative matrix carrying a non-finite
entry SHALL yield no key, and its comparison SHALL be computed as an
uncacheable one.

Quantisation SHALL merge only placements that are indistinguishable at the
scale the run models: two relative matrices sharing a cell differ per entry by
less than the quantum `q`, so for a part of extent `L` from its own origin
every point of one solid in the other's frame moves by at most `3qL + √3 q`.
At the default quantum that bound is nanometres at metre scale. The failure
direction SHALL be a miss: two placements that straddle a cell boundary key
differently and are recomputed, exactly as they are today, so quantisation can
only add cache hits and never widens a verdict at a boundary.

Quantisation SHALL apply ONLY to the verdict key. The geometry a comparison is
handed SHALL still be placed by its own exact matrix, the exact placement and
bounding-box caches SHALL keep their exact keys, and the world-AABB broad phase
SHALL keep reading the real matrices.

The cache SHALL be keyed independently of which assertion asked, so the
animation sweep, the pairwise sweep, the whole-assembly interference
assertion and the perturbation assertions share one another's answers for the
same pair in the same relative placement.

A flexible leaf's identity SHALL be taken from the same evaluation that
supplies the geometry being compared. Two comparisons SHALL therefore share a
key only when their flexible geometry is the same geometry, in the same
relative placement. That is why a flexible part at a new binding is a new
question, and a flexible part at a binding already asked is not.

A node whose geometry has no stable identity SHALL NOT be cached, and its
comparisons SHALL be computed exactly as they are today. Such nodes are: a
test double exposing only `.mesh`; a flexible leaf whose class overrides the
stock evaluation seam the comparison reads (`base_mesh` on the faceted path,
`shape` on the exact path); and a flexible leaf whose tracked sources cannot
be read.

Beneath this per-run cache, the verdict store of "A decided verdict is kept
between runs of a project" MAY serve a comparison the run has not yet decided.

#### Scenario: A repeated comparison is not recomputed

- **WHEN** an assertion compares the same two solids in the same relative
  placement a second time within one run
- **THEN** the verdict returned equals the first verdict exactly, and no
  boolean is run by either kernel

#### Scenario: A moved pair is recomputed

- **WHEN** two solids are compared, then one is placed differently relative
  to the other, and they are compared again
- **THEN** the second comparison runs its boolean and returns the verdict for
  the new placement

#### Scenario: A pair moved together is not recomputed

- **WHEN** two solids are compared, then BOTH are placed by the same
  additional rigid transform and compared again
- **THEN** the verdict is served from the cache and equals the first verdict

#### Scenario: A pair carried together through a parent is not recomputed

- **WHEN** two solids are compared, then both are carried by the same parent
  rotation composed so that their relative matrix differs from the first by
  float noise far below the run's placement quantum, and they are compared
  again
- **THEN** the verdict is served from the cache and no boolean is run

#### Scenario: A pair displaced by more than the quantum is recomputed

- **WHEN** two solids are compared, then one is displaced relative to the
  other by more than the run's placement quantum, and they are compared again
- **THEN** the second comparison runs its boolean and returns the verdict for
  the new placement

#### Scenario: A zero quantum restores the exact key

- **WHEN** a run's placement quantum is `0` and two solids are compared, then
  carried together so that their relative matrix differs only by float noise,
  and compared again
- **THEN** the second comparison runs its boolean, as it does under the
  exact-bytes key

#### Scenario: Signed zero does not split a cell

- **WHEN** two comparisons of the same pair produce relative matrices whose
  corresponding entries are `-0.0` and `0.0`, with a nonzero quantum
- **THEN** the second comparison is served from the cache

#### Scenario: The exact kernel quantises too

- **WHEN** an exact run compares a pair of exact solids twice at relative
  placements that differ by less than the placement quantum
- **THEN** the second comparison is served from the cache and no OCCT boolean
  is run

#### Scenario: A rebuilt part invalidates its entries

- **WHEN** a solid's geometry file is rebuilt and a comparison that involved
  it is repeated
- **THEN** the comparison is recomputed against the new geometry

#### Scenario: Flush contact keeps its verdict through the cache

- **WHEN** a flush abutment that reports non-empty with exactly 0.0 mm³ is
  compared twice
- **THEN** both comparisons report non-empty with 0.0 mm³, and the strict
  `volume_epsilon=0` default still reports the foul

#### Scenario: A flexible pair at one binding is not recomputed

- **WHEN** a stock flexible leaf is compared with a part, then compared again
  in the same run at the same binding and the same relative placement
- **THEN** the second comparison is served from the cache, no boolean is run,
  and its verdict equals the first

#### Scenario: A flexible pair at a new binding is recomputed

- **WHEN** a stock flexible leaf is compared with a part, then rebound to
  different port values and compared again at the same relative placement
- **THEN** the second comparison runs its boolean and returns the verdict for
  the new geometry

#### Scenario: A flexible leaf with a custom evaluation seam is not cached

- **WHEN** a comparison involves a flexible leaf whose class overrides
  `base_mesh` (faceted path) or `shape` (exact path)
- **THEN** the comparison is computed as it is today, and no cache entry
  serves a later comparison in its place

#### Scenario: A node without stable geometry identity is not cached

- **WHEN** a comparison involves a node exposing only `.mesh`
- **THEN** the comparison is computed as it is today and no cache entry
  serves a later comparison in its place

#### Scenario: The placed geometry is not quantised

- **WHEN** the same solid is compared at two relative placements differing by
  less than the placement quantum
- **THEN** each comparison that runs is handed geometry placed by its own
  exact matrix, and the exact placement cache keys those placements on their
  exact matrix bytes

### Requirement: Run-level comparison kernel

The test framework SHALL hold, for each run, one comparison kernel (`exact`
or `faceted`), one volume epsilon in mm³, one placement quantum in mm and one
verdict-store switch (on or off). Together these are the run's comparison
policy. The kernel is a property of the run,
never of the model: a node's `exact` attribute SHALL keep reporting whether
its geometry is exact, and neither the build nor any artifact SHALL depend on
the kernel a test run selects.

`machinome test` SHALL resolve the kernel from the mutually exclusive `--exact` /
`--faceted` flags, else from the `SOLID_TEST_KERNEL` environment variable
(`exact` or `faceted`; any other value is an error naming the variable), else
`exact`. It SHALL resolve the epsilon from `--volume-epsilon`, else from
`SOLID_TEST_VOLUME_EPSILON`, else `0.0`; a negative value is an error. The
epsilon exists only for the faceted kernel: `--volume-epsilon` together with
an exact run is an error saying the exact kernel has nothing to absorb, and
`SOLID_TEST_VOLUME_EPSILON` is not read under the exact kernel. The
environment is the project's, loaded through the CLI's `.env` rule, so a
setting in an ignored checkout-local `.env` selects the kernel for every run
in that checkout and nowhere else.

It SHALL resolve the placement quantum from `--placement-quantum`, else from
`SOLID_TEST_PLACEMENT_QUANTUM`, else the framework's default of `1e-9` mm. A
negative or non-finite value is an error naming the flag or the variable; an
environment value that is not a number is an error naming
`SOLID_TEST_PLACEMENT_QUANTUM` and saying it is a length in mm. Unlike the
volume epsilon, the placement quantum SHALL apply under BOTH kernels and
SHALL be accepted by the exact kernel, because it identifies a question and
not a quantity of material, and both kernels' verdicts pass through the same
memo. A quantum of `0` SHALL be accepted and SHALL mean the exact-bytes key.

It SHALL resolve the verdict-store switch from `--verdict-store` /
`--no-verdict-store`, else from `SOLID_TEST_VERDICT_STORE`, else on. The
variable's value SHALL be `on` or `off`. Any other non-empty value is an
error naming the variable and the two accepted values, raised before any
node is built. Like the placement quantum, the switch SHALL apply under BOTH
kernels. With the switch off, a run SHALL neither read nor write the verdict
store; its per-run cache is unaffected.

Outside `machinome test` — a `ScenarioTest` under pytest, an assertion driven
directly — the framework SHALL resolve the same policy from the environment
at the first comparison of the process, with the same defaults and the same
errors.

Under the exact kernel every assertion behaves as specified elsewhere in
this capability. Under the faceted kernel every intersection, containment,
connectivity and weld question SHALL be answered from the compared nodes'
meshes exactly as it is answered today for a node that is not exact, and the
verdicts of the shared intersection helper SHALL have the run's epsilon
applied before any assertion reads them.

A run at the default placement quantum SHALL produce exactly the output it
produces today: no announcement, and no change to the summary line. A run at
any other placement quantum SHALL name it on the summary line, after the
preserved summary prefix and beside the faceted label when both apply.

A run with the verdict store on SHALL produce exactly the output it produces
without the store, whether or not any verdict was served from it. A run with
the store off SHALL say so on the summary line, after the preserved summary
prefix, in the same parenthesis as the faceted label and a non-default
quantum when those apply.

#### Scenario: The default run is the exact run

- **WHEN** `machinome test` runs with no kernel flag and no `SOLID_TEST_KERNEL`
- **THEN** every comparison of two exact nodes uses the boundary-representation
  kernel and the run's output is unchanged

#### Scenario: A checkout selects the faceted kernel once

- **WHEN** the project's `.env` contains `SOLID_TEST_KERNEL=faceted` and
  `machinome test` runs without a kernel flag
- **THEN** every comparison uses the faceted path and the run says so

#### Scenario: A flag overrides the environment

- **WHEN** `SOLID_TEST_KERNEL=faceted` is set and `machinome test --exact` runs
- **THEN** the run uses the exact kernel and prints no kernel line

#### Scenario: An epsilon offered to the exact kernel is refused

- **WHEN** `machinome test --exact --volume-epsilon 0.5` or
  `machinome test --volume-epsilon 0.5` with no faceted selection is run
- **THEN** the command exits with an error saying the exact kernel has nothing
  for an epsilon to absorb, before any node is built

#### Scenario: An unknown kernel name is refused

- **WHEN** `SOLID_TEST_KERNEL=fast` is set
- **THEN** `machinome test` exits with an error naming the variable and the two
  accepted values

#### Scenario: The default placement quantum needs no selection

- **WHEN** `machinome test` runs with no `--placement-quantum` and no
  `SOLID_TEST_PLACEMENT_QUANTUM`
- **THEN** the run's policy carries the framework's default quantum and the
  run's output is byte-for-byte what it is without this option

#### Scenario: A quantum offered to the exact kernel is accepted

- **WHEN** `machinome test --exact --placement-quantum 1e-6` runs
- **THEN** the run compares on the exact kernel with that quantum, and no
  error is raised

#### Scenario: A checkout selects a placement quantum

- **WHEN** the project's `.env` contains `SOLID_TEST_PLACEMENT_QUANTUM=1e-6`
  and `machinome test` runs without the flag
- **THEN** the run's policy carries `1e-6` mm

#### Scenario: The quantum flag beats the environment

- **WHEN** `SOLID_TEST_PLACEMENT_QUANTUM=1e-6` is set and
  `machinome test --placement-quantum 0` runs
- **THEN** the run's policy carries `0` and the memo keys on exact matrix
  bytes

#### Scenario: A negative or non-finite quantum is refused

- **WHEN** `machinome test --placement-quantum -1` runs, or
  `SOLID_TEST_PLACEMENT_QUANTUM=-1` is set, or `machinome test
  --placement-quantum inf` runs, or `SOLID_TEST_PLACEMENT_QUANTUM=nan` is set
- **THEN** the command exits with an error naming the flag or the variable,
  before any node is built

#### Scenario: A non-numeric quantum in the environment is refused

- **WHEN** `SOLID_TEST_PLACEMENT_QUANTUM=tight` is set
- **THEN** `machinome test` exits with an error naming the variable and saying the
  value is a length in mm

#### Scenario: A non-default quantum is named on the summary line

- **WHEN** a run uses a placement quantum other than the default
- **THEN** the summary line keeps its prefix verbatim and names the quantum,
  beside the faceted label and volume epsilon when the run is faceted

#### Scenario: The verdict store is on by default

- **WHEN** `machinome test` runs with no verdict-store flag and no
  `SOLID_TEST_VERDICT_STORE`
- **THEN** the run's policy has the store on, and the run's output is
  byte-for-byte what it is without this option

#### Scenario: A checkout turns the verdict store off

- **WHEN** the project's `.env` contains `SOLID_TEST_VERDICT_STORE=off` and
  `machinome test` runs without a verdict-store flag
- **THEN** the run neither reads nor writes the store, and its summary line
  says the store is off

#### Scenario: The verdict-store flag beats the environment

- **WHEN** `SOLID_TEST_VERDICT_STORE=off` is set and
  `machinome test --verdict-store` runs, or `SOLID_TEST_VERDICT_STORE=on` is
  set and `machinome test --no-verdict-store` runs
- **THEN** the flag decides the run's switch

#### Scenario: An unknown verdict-store value is refused

- **WHEN** `SOLID_TEST_VERDICT_STORE=sometimes` is set
- **THEN** `machinome test` exits with an error naming the variable and the
  two accepted values, before any node is built

#### Scenario: A run without the store says so beside the other notes

- **WHEN** `machinome test --faceted --volume-epsilon 0.5 --no-verdict-store`
  runs
- **THEN** the summary line keeps its prefix verbatim and names the faceted
  kernel, the epsilon and the store being off, in one parenthesis

#### Scenario: A faceted run of an exact project never reaches the exact stack

- **WHEN** an all-exact project is tested under the faceted kernel in a fresh
  interpreter and its build is current
- **THEN** the test framework imports no `cadquery` and reads no node's
  `shape()`, and the verdicts are those of the faceted path

#### Scenario: The model is unaware of the kernel

- **WHEN** a test reads `node.exact` under the faceted kernel
- **THEN** it reports the geometry's exactness as it does under the exact
  kernel

#### Scenario: A scenario test under pytest reads the environment

- **WHEN** a `ScenarioTest` runs under plain pytest with
  `SOLID_TEST_KERNEL=faceted` in the environment
- **THEN** its geometric assertions use the faceted path with the
  environment's epsilon

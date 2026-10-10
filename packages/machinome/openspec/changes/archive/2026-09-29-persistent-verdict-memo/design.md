## Context

The finding is recorded in `workflow/warts.md` under "3DPrintedClocks wall
clock 02 and strandbeest (2026-09-29, verdict memo across runs)". At
framework `main` bf24687, a probe ran each suite twice inside one
interpreter, first with the ADR-070 memo cold and then with it warm. The
probe wrapped `_memoized`, `intersect_shapes` and `Shape.importBrep`.

| Suite | Cold | Of which in misses | Warm (every ask served) |
|---|---:|---:|---:|
| 3DPrintedClocks `wall_clock_02` (22 tests, exact) | 1348.9 s | 1280.6 s (95%), 643 booleans | 18.35 s |
| strandbeest walking demo (3 tests, exact) | 246.9 s | 228.1 s (92%), 1055 booleans | 11.97 s |

The verdicts were identical in both passes: 16 passed and 6 failed for the
clock, and 3 passed for strandbeest. Neither suite asked a single
uncacheable question: in both, no flexible pair reached the memo.

ADR-070 did measure flexible cost, on the v8-engine root suite and on the
exact kernel (ADR-073's faceted kernel came later). Of the 1622.8 s left
after its memo, 1499 s went to flexible comparisons: about 50 ms evaluating
the spring and 380 ms in the kernel, each. ADR-073 cites the same 430 ms
per exact spring comparison, against about 14 ms on the spring's own mesh.

At the project's checked-out commit (branch `declarative-api`, fdf624b; its
`master` predates the springs and asks no spring pair), two tests put a
molejo valve spring into a pair:

- `v8_engine/test_v8_engine.py`,
  `EngineTest.test_valve_springs_clear_head_stem_and_retainer_on_exact_solids`,
  at t = 0.125: each of the 16 springs against its valve, its retainer and
  its bank's head, 48 pairs;
- `v8_engine/valvetrain/test_valve_motion.py`,
  `ValveMotionTest.test_fully_compressed_spring_clears_the_stack_on_exact_solids`,
  at the lobe's peak: one stack's spring against its valve and its
  retainer, 2 pairs.

The `assertNoPairwiseIntersections` sweeps of `test_v8_engine.py` and
`valvetrain/test_bank_valvetrain.py` also walk the springs as leaves. The
other spring tests read mesh bounds and vertices and ask no pair. The
checkout's `.env` sets `SOLID_TEST_KERNEL=faceted`, so a bare
`machinome test` there compares the springs on the faceted path, and
`--exact` compares them on solids. Both paths leave the pair unkeyed today,
as the next section shows.

### What the memo is today

All spatial verdicts pass through `_memoized(key, compute)` in
`machinome/test.py`. The key is built in one of two places:

- `_verdict_key`, from `_engine_intersection_stats`, which serves the
  pairwise, perturbation and weld assertions;
- `_record_key`, from `_placed_intersection`, which serves
  `assertNoSolidInterference` and `assertAssemblySupported`.

Either way it is `(identity₁, identity₂, path, quantum, cells)`: two solid
identities, `'exact'` or `'faceted'`, and the run's placement quantum with
the integer cells of `inv(M₁) @ M₂` (ADR-090; at quantum 0, the exact bytes
of the relative matrix). `_settled` applies the run's volume epsilon after
the memo is read, so the memo holds raw `IntersectionStats`. The memo is a
module dict bounded at 8192 entries. ADR-070 recorded that "nothing
survives the process".

The solid identities are:

- **Exact:** `shape_identity(shape)`, which is `(brep path, float mtime)`
  from `cached_shape` in `machinome/exact.py`.
- **Faceted:** `(stl path, ArtifactObservation)` from
  `_geometry_identity`. The observation is the full observable state of the
  file: realpath, device, inode, size, mtime_ns and ctime_ns.
- **Flexible, faceted path:** `None`. `_fast_geometry` returns it
  deliberately, even though `_flexible_manifold` has just computed the
  leaf's full state identity through `FlexibleNode._faceted_cache_snapshot()`
  to key its own Manifold cache.
- **Flexible, exact path:** also `None`. A molejo leaf is exact, and its
  `shape()` is evaluated rather than loaded, so `shape_identity` finds
  nothing. The framework's default kernel is exact, so a project's springs
  take this path unless its checkout selects the faceted kernel. v8-engine's
  checkout does: a bare run there takes the faceted path above, and
  `--exact` takes this one. The evidence measures both (tasks 1.2 and 9.3).

None of these identities can outlive the process. Paths are absolute, and
an mtime or an inode changes on a rebuild that reproduces identical bytes,
on a move and on a copy.

### Constraints this design inherits

- **The memo must never change a verdict.** This is ADR-070's first driver,
  carried by ADR-090 and ADR-092. Flush contact must still come back
  non-empty at exactly 0.0 mm³ (ADR-025/029).
- **The run policy has a fixed shape.** ADR-073 and ADR-090 established a
  field on `ComparisonPolicy`, a `machinome test` flag, and a `SOLID_TEST_*`
  variable read through the CLI's `.env` rule. The flag beats the
  environment, which beats the default. A run at the defaults prints exactly
  what it printed before, and a non-default choice is named in the summary
  line's parenthesis.
- **Imports stay light.** A faceted run of an all-exact project imports no
  `cadquery`, and an all-exact run needs no `manifold3d` (ADR-052 and the
  `mesh-engine-dependency` and `cli-startup-cost` capabilities). Nothing the
  store needs may import either. `machinome/core/builder.py` is imported at
  module level by the `build`, `develop`, `export` and `snapshot` commands,
  so the sweep's exemption may not bring the store module, or anything it
  reads, onto their path (§5, §6).
- **The builder's sweep deletes unknown files.** It removes every file in
  the build directory it does not name (`kept` in
  `machinome/core/builder.py`), after every successful publication,
  including the ones `machinome develop` triggers.
- **Two writers are normal.** The studio floor spawns `machinome test` as a
  subprocess, and a pilot or a second agent may run the same project's suite
  at the same moment. On bf24687 `machinome develop` holds no verdict memo:
  `machinome/manager/develop.py` never imports `machinome.test`. What
  develop contributes is a concurrent *sweeper*, not a concurrent writer.
- **The filesystem is not a local disk.** Projects on the pilot's machine
  live on virtiofs. SQLite's documentation warns that its locking, and the
  shared-memory index behind WAL mode, are unreliable on network and shared
  filesystems.

### How this differs from ADR-140's rejection

ADR-140 rejected "cross-path, cross-run or unbounded memoization" of bind
results "without a measured need", because a longer lifetime "raises graph
ownership and stale-state questions". Both halves differ here:

- **The need is measured.** The table above shows 95% and 92% of the wall
  time.
- **The key has no mutable owner.** It is a pure function of file bytes, of
  a flexible leaf's serialized state and of a relative placement. A
  `_PathValue` entry depends on live graph state, which nothing stable can
  name.

### How this sits with ADR-006 and ADR-060

ADR-006 rejected content hashing as a *replacement* for mtime currency on
cost. ADR-060 then confined hashing to the case where a render would
otherwise run. This design confines it in the same way: an artifact is
digested only at an in-process memo miss with the store enabled. That is
exactly the point at which an OCCT boolean (about 2 s here) or a Manifold
boolean would otherwise run, and the digest is memoised per observation.

## Goals / Non-Goals

**Goals:**

- A second process testing an unchanged project answers every spatial
  question it asked before from the store, with no boolean. On the two
  originating suites the second process should approach the measured warm
  floor.
- Verdicts are keyed on state: artifact content, flexible state and
  relative placement. No absolute path and no timestamp is persisted.
- A framework change, a kernel upgrade or a store-format change invalidates
  the store with no maintainer action.
- No verdict, message or epsilon semantics change. Every uncertainty
  resolves to a miss.
- The default run's output is unchanged. The switch is visible and
  removable.
- Two concurrent runs of one project neither error nor lose each other's
  records.

**Non-Goals:**

- **Caching geometry across runs.** BREP imports (0.08 s for 53 files on the
  clock), Manifold construction and flexible evaluation stay per process. In
  the pilot's words, "we don't want cache for geometries".
- **Skipping flexible evaluation on a hit.** A flexible leaf's geometry is
  still evaluated before its key is formed, as a rigid shape is still loaded
  (§4). Deferring evaluation until a miss is a possible follow-up if the
  v8-engine measurement shows that evaluation dominates what is left.
- **Sharing or committing the store.** It is local build state, as `.brep`
  artifacts are. There is no remote cache.
- **Canonicalising pair order.** `(A, B)` and `(B, A)` stay two questions,
  as in the in-process memo.
- **Strengthening `cached_shape`'s in-process key.** It stays
  `(path, float mtime)`, weaker than every other artifact cache. The
  persistent tier guards itself against that gap (§3), and the gap is
  recorded as a wart for its own triage rather than changed here.
- **Any change to an assertion,** the broad phases, the face-box tier, the
  volume epsilon or the placement quantum.
- **Extra user surface.** There is no read-only mode, no statistics line
  and no `machinome` subcommand to clear the store. Deleting the directory
  clears it, and no finding asks for more.

## Decisions

### 1. A tier beneath `_memoized`, consulted only at an in-process miss

`_memoized(key, compute)` keeps its contract and gains one step:

1. If `key` is `None`, compute and cache nothing, exactly as today.
2. If the in-process memo holds the key, return the verdict. Nothing else is
   touched.
3. On an in-process miss, if the run's policy has the store on and the
   project has a build root, derive the **persisted key** (§2). This is the
   first point at which content digests are computed. If the key derives
   and the store holds it, the stored verdict is entered into the in-process
   memo, a last-use touch is queued (§7), and the verdict is returned.
4. Otherwise compute. If that returns, the verdict enters the in-process
   memo and, when a persisted key derived, is queued for the store. If it
   raises, nothing is stored anywhere.

`_settled` stays where it is, after `_memoized`, in both
`_intersection_stats` and `_placed_intersection`. The store therefore holds
raw engine verdicts, and the same store serves any volume epsilon.

Two alternatives were considered and rejected:

- **A store beside the memo, consulted before it.** A store read would then
  precede every in-process hit, doing work the in-process memo already
  makes unnecessary.
- **Replacing the in-process memo with the store.** An in-process hit costs
  one dict lookup, and a store hit also costs a digest derivation the first
  time.

### 2. The persisted key: state, hashed, carrying the stamp (point 1)

The persisted key is the SHA-256 of a canonical, length-prefixed encoding of
these fields, in this order:

1. the store format version;
2. the stamp digest (§5);
3. the evaluation path, `exact` or `faceted`;
4. the placement quantum's IEEE-754 bytes;
5. the persistent identity of solid 1 (§3, §4);
6. the persistent identity of solid 2;
7. the placement term: the integer cell bytes of ADR-090, or at quantum 0
   the relative matrix's exact bytes.

Fields 3, 4 and 7 are exactly the in-process key's fields. Only the two
identities are replaced, and the stamp is added. Order is kept, so `(A, B)`
and `(B, A)` stay distinct, as they are in process.

The store maps that 32-byte digest to the raw verdict:

- `is_empty`;
- `exact`;
- `volume`, as the exact IEEE-754 bits the engine returned, so a negative, a
  non-finite and the flush contact's `0.0` all come back bit for bit;
- a last-use time for eviction.

No geometry, path, name, matrix or identity is stored.

Hashing the key is a design choice, not a tolerance:

- **What it relies on.** A collision of SHA-256 over well-formed encodings.
  The artifact digests that feed it already rely on SHA-256, as ADR-060's
  source digests do. At the store's bound of 2¹⁸ records the chance of a
  collision is below 2⁻²¹⁹.
- **What it buys.** Fixed-width records, which make truncation and
  corruption trivially detectable (§7). Nothing about the project leaves the
  key but its digest.

Alternatives considered and rejected:

- **Persist the key tuple verbatim.** Records become variable-width and carry
  nested structures, with nothing gained.
- **Persist under the in-process identities.** Paths and mtimes are exactly
  what the finding shows do not survive a rebuild that reproduces identical
  bytes, a move or a copy.
- **Key on world matrices.** ADR-070 already rejected this: it misses every
  pair a parent carries together.

### 3. Rigid identity is a content digest bound to the loaded bytes (point 2)

The persistent identity of a rigid solid is `('artifact', kind, sha256 of
the artifact's bytes)`. The kind is the BREP for the exact path and the STL
for the faceted path, the file whose bytes the compared geometry was read
from. A mixed pair decided on meshes uses both solids' STL digests, because
that is what it compares.

The digest must name **the bytes the compared geometry came from**, not
whatever the path holds now. Otherwise a stale in-process shape could be
filed under new content. So it is bound through the observation:

- **Faceted.** The in-process identity already carries the
  `ArtifactObservation` that keyed the Manifold and the bounds, and
  `cached_base_mesh` reads the bytes through an `ArtifactSnapshot` checked
  against that observation.
- **Exact.** `cached_shape` gains a record of the observation it loaded
  from. It observes the file before and after `importBrep`. If the two
  observations differ, it records none, and that shape has no persistent
  identity. Its in-process key stays `(path, float mtime)`, and eviction
  clears the record with the shape.
- **The digest itself** is read through an `ArtifactSnapshot` of the path.
  If the snapshot's observation is not the recorded one, meaning the file
  has changed since the geometry was read, there is no persistent identity:
  the pair is computed as today and kept in process only.

The digest is **computed lazily**, only in step 3 of §1. It is **memoised in
process on the full `ArtifactObservation`**: realpath, device, inode, size,
mtime_ns and ctime_ns. When a path's observation changes, its older entry is
evicted. This is `currency._file_key`'s discipline, and deliberately not
`(path, mtime_ns, size)`. ADR-060's text says per-file digests are cached on
`(path, mtime, size)`, but the code has since moved to the full identity,
because "a same-size rewrite followed by an mtime restoration must evict".
For artifacts that case is ordinary, not exotic: `_atomic_export` stamps
every artifact with its *source's* mtime. Any rebuild not caused by a source
edit therefore reproduces the old mtime, and it may reproduce the size too,
while its bytes may differ. Such rebuilds include a changed producer recipe,
a deleted artifact, and a framework or kernel upgrade that exports
differently. The observation's realpath is used only as an in-process key
and is never persisted.

Alternatives considered and rejected:

- **Digest at decode or import.** The STL bytes are already in memory in
  `cached_base_mesh`. This would pay hashing on every load even with the
  store off or every ask served in process, and for a BREP it means reading
  the bytes twice or importing from memory.
- **Key on mtime and size.** The mtime is preserved across a rebuild by
  design, as above.
- **Reuse the currency sidecar's source digest.** It names the node's
  *sources*, not the artifact. Adapter code, tessellation precision, kernel
  export behaviour and the recipe sit between the two, and a sidecar may be
  absent or swept. The artifact's own bytes are the state the verdict is a
  function of.

### 4. Flexible leaves are keyed on their state, in both tiers (point 3)

A stock `FlexibleNode` gets a state identity. `('flexible', sha256 of a
canonical encoding of)`:

- `tech`;
- `type(node).__module__`;
- `source_digest`: project-relative, and the content proof;
- the full `_flexible_structural_identity`: the canonical serialization
  `uniq_id` is shortened from;
- the sorted `(name, repr(value))` of `bound_values()`;
- the SHA-256 of the canonically serialized spec.

This is the identity `_faceted_cache_snapshot` already computes, with two
components dropped:

- **`os.path.realpath(self.src)`** is absolute and would defeat a moved
  project. It is also redundant: the source digest names every tracked
  source by its project-relative path, and the module names the defining
  module.
- **`source_fingerprint`** is metadata (device, inode, ctime) that changes
  on a move, a clone or a touch. ADR-081 made it a guard *in front of* the
  digest. The digest is the content claim the fingerprint stands in for, and
  it is kept.

The Manifold cache keeps its own key unchanged. The evaluator's version
(molejo) is in the stamp (§5), not in this identity.

The same identity is used by the in-process memo. A flexible pair therefore
becomes cacheable within a run as well as across runs, and
`test_flexible_verdicts_are_not_memoized_after_geometry_reuse` is inverted.

**Coherence rule.** The identity must name the geometry actually compared.
One private snapshot seam returns `(identity, rendered, values)` from a
single `current_shape()` and serves both paths:

- **Faceted.** `_flexible_manifold` already keys its Manifold on the
  snapshot and builds a miss from the same `rendered`. It also returns the
  verdict identity, and `_fast_geometry` stops returning `None` for a stock
  leaf.
- **Exact.** `_exact_solid` records, beside the `(shape, tolerance)` it
  builds, the identity of the snapshot it built from. The exact branch of
  `_engine_intersection_stats` asks the flexible node for the identity
  recorded with the shape its `shape()` just returned, instead of calling
  `shape_identity`. The per-instance last-binding memo keeps its behaviour:
  one entry per instance, replaced on a new binding. If a shortened
  `binding_hash` collision ever serves an older binding's solid, the
  identity it carries is that older binding's too. The key then still names
  the geometry compared, so it stays true.

**What stays uncached, as today:**

- **A subclass that overrides a stock evaluation seam.** On the faceted path
  that seam is `base_mesh`, which is today's rule. On the exact path it is
  `shape`, the analogous public seam. The override's geometry is not proven
  to be a function of the serialized spec.
- **A leaf whose source digest cannot be read.** The snapshot identity is
  then `None`, a coherent miss, as it is for the Manifold cache.

**The amendment to ADR-070, stated plainly.** ADR-070's consequence "Flexible
parts are uncacheable by construction and stay that way" (restated by
ADR-090) rests on the spike's name-keyed census. Two instants at one relative
placement are different questions when the flexible part's binding differs,
so a *name* is not an identity. That argument is right about names and does
not reach state. A key that contains the bound values and the spec digest
separates exactly the cases the census conflated. Two comparisons with equal
keys have the same spec, the same values, the same evaluator (stamp) and the
same relative placement, and so the same geometry in the same relative pose.
The ADR this cycle produces says so and amends ADR-070 accordingly.

Alternatives considered and rejected:

- **Key flexible pairs on their per-binding snapshot STL.** Those files
  exist only on the SCAD path. They are named by a shortened hash, and the
  sweep deletes them per binding.
- **Keep flexible pairs uncached.** The pilot directed otherwise, and
  v8-engine's 1499 s is the measured cost.

### 5. The invalidation stamp covers the whole package (point 4)

The stamp is one SHA-256 over a canonical encoding of these parts, computed
once per process at the first store use:

- the store format version;
- `machinome.__version__`;
- a digest of **every `.py` file of the imported `machinome` package**, by
  package-relative path and bytes. At bf24687 that is 97 files, 1.9 MB,
  hashed in 21 ms cold on the pilot's virtiofs;
- the installed distribution versions of `cadquery-ocp` and `cadquery` (the
  exact path), `manifold3d` and `trimesh` (the faceted path: trimesh decodes
  the STL the Manifold is built from) and `molejo` (the flexible evaluator on
  both paths);
- `sys.platform`, `platform.machine()` and
  `sys.implementation.cache_tag`. These name the binary the native kernels
  were built as.

Versions are read from distribution metadata (`importlib.metadata`). **No
package is imported to read its version**, so neither ADR-052 nor the
faceted run's refusal to import `cadquery` is disturbed. For a distribution
with no metadata the token depends on the module:

- if `importlib.util.find_spec` locates the module, the token is its origin
  file's size and mtime_ns (this covers, for instance, a conda-built OCP);
- if it does not, the token is `absent`. A module that is absent contributes
  nothing to any verdict.

**Everything the stamp reads is read inside the stamp function, at the first
store use, never at import.** That covers `importlib.metadata`,
`importlib.util.find_spec`, `platform`, the `sys.implementation` read, and
the walk and digest of the package sources. The store module's top-level
imports are cheap standard-library modules only (`os`, `struct`, `hashlib`,
`time`, `logging` and the like) and `machinome._artifact`, which itself
imports only the standard library. The store module imports no kernel or
evaluator (`cadquery`, `OCP`, `manifold3d`, `trimesh`, `molejo`) at any
time: versions come from metadata, and `find_spec` locates a top-level
module without importing it. Importing the store module therefore loads no
metadata, platform or kernel module, and a process that never consults the
store never pays for the stamp. A fresh-interpreter probe proves it
(task 6.7).

The stamp is included in every persisted key (§2), so correctness never
depends on segment filtering. It is also written in every segment's header
(§7), so foreign segments are never read.

**Why the whole package and not a list.** The minimum list is `test.py`,
`exact.py`, `mesh_engine.py` and `node/flexible.py`. To it one would have to
add `node/adapters/molejo.py`, whose `_snapshot_mesh` and `_snapshot_shape`
turn a spec into geometry, and `node/base.py`, whose `cached_base_mesh`
decodes the STL. Any list is a maintenance obligation that fails silently:
the next exact-negative tier, the next decode change or the next adapter
hook lands in a module nobody added. That discipline is exactly what the
stamp exists to remove. The whole package costs about 20 ms once per
process. Its only price is that a framework developer's edit anywhere in the
package makes their next project run cold. Released users pay nothing extra,
because the version changes at every release anyway.

Alternatives considered and rejected:

- **The minimum module list.** It needs the maintenance described above.
- **The version string alone.** An editable install does not move it. The
  workspace venv's metadata reads 0.7.0 while the bench's
  `machinome.__version__` reads 0.7.1, and neither moves between commits.
- **Per-path stamps**, so a mesh-engine upgrade would not invalidate exact
  records. That is a refinement with no finding behind it: an upgrade costs
  one cold run.

### 6. Where the store lives and what protects it (point 5, location)

The store is the directory `<build root>/.verdicts/`. The build root is the
one `project_build_root()` resolves in the testing process:

- the anchored root under `machinome test`. A run that tests one declared
  model and a run of every model with `--all` both anchor on the project's
  root (`anchor_build_dir` keeps the root beside the model's directory), so
  every declared model of a project shares one store. A verdict kept by a
  run of one model is served to a run of another that asks the same
  question: two parts both models build to identical artifacts, at the same
  relative placement;
- else an absolute `SOLID_BUILD_DIR`;
- else `SOLID_BUILD_DIR` (default `_build`) under the project root found
  above the working directory.

If none of these exists (no manifest, nothing anchored), there is no store
and the run keeps the in-process memo only. The resolver must *not* use
`project_build_root`'s bare-relative fallback, which would create `_build/`
in whatever directory a pytest happens to run.

Correctness does not depend on location, because keys are content. Two
projects sharing an absolute `SOLID_BUILD_DIR` share a store safely.
Location decides only who shares hits.

The name cannot collide with a declared model's directory: `MODEL_NAME`
(`^[A-Za-z_][A-Za-z0-9_-]*$`) forbids a leading dot. The builder already
keeps the build path out of Git.

**The sweep.** `_sweep_unreferenced_artifacts` prunes `.verdicts` from its
`os.walk` at the top of the directory it sweeps, by the same mechanism that
already skips declared model directories. That covers two cases:

- **the root build's sweep**, where the store normally lives;
- **a model's sweep**, for a fresh interpreter started after
  `anchor_build_dir`. Such a process sees `SOLID_BUILD_DIR` set to the
  model's directory and resolves that as its build root.

The directory name lives in one constant, in `machinome/_artifact.py`. The
builder already imports that module, for `ArtifactChanged`, and takes the
name from there; so does the store module. The exemption therefore adds no
module to the command path of `build`, `develop`, `export` or `snapshot`,
and the store module is loaded only by the test framework. `_artifact` is
also where the observations and snapshots the store's digests are bound
through (§3) already live. A fresh-interpreter probe proves it: a
`machinome build` dispatch loads no store module, and no metadata, platform
or kernel module beyond what it loads at bf24687. At bf24687 that is
`importlib.metadata` and `platform`, and no kernel (tasks 1.4 and 6.7).

Alternatives considered and rejected:

- **The name in the store module, imported by the builder.** It puts the
  store module on every builder user's command path. Its import discipline
  (§5) would keep that cheap, but only for as long as every later edit to
  the store module keeps it so. Hosted in `_artifact`, the builder's cost is
  zero by construction.
- **A user cache directory** (`~/.cache/machinome/<project hash>`). It
  splits a project's state from its build directory, needs a project hash
  (an absolute path, which defeats moves) and outlives a deleted project.
- **Naming individual files in `kept`.** Pruning one directory is simpler,
  and it spares temporaries and segments alike.

### 7. Immutable segments, lock-free, merged on read (point 5, format)

**Layout.** The store is a directory of **segment files**. A segment is
immutable once published and consists of:

- a header: magic bytes, the store format version, the full stamp digest and
  a record count;
- fixed-width records: key digest, verdict flags, volume bits and last-use
  seconds;
- a trailing SHA-256 over everything before it.

Segments are named
`<stamp prefix>-<pid>-<time_ns>-<random>.seg`, so a listing tells the
current stamp's segments apart from foreign ones without opening any.

**Write.** A process never modifies a file. A flush writes the pending
records to a temporary file in the store directory and publishes it with
`os.replace`. That is atomic on POSIX and on Windows. An interrupted write
leaves at most an unpublished temporary, which nothing reads.

**Read.** At its first store consultation a process lists the current
stamp's segments, reads each one whole and validates it: magic, version,
stamp, length equal to count × width, and checksum. It merges the valid ones
into an in-memory index; for a key seen twice, the latest last-use wins. A
segment that fails validation is skipped.

A listed segment that is gone when it is opened has almost always been
merged and deleted by a concurrent compaction, and one compaction deletes up
to 64 inputs. Skipping them would leave the reader nearly cold for its whole
run. So when a listed segment vanishes, the reader lists the directory once
more and reads every current-stamp segment of the second listing that it has
not read yet. Compaction publishes its merged segment before it deletes any
input (below), so the second listing holds every record the vanished
segments held. Only a segment that vanishes again, from the second listing,
is skipped. A load re-lists at most once.

After its load a process never lists again. Verdicts other processes record
afterwards are served from the next process on. A skipped segment costs
misses, never an error.

**Flush.** Pending records are the new verdicts, plus one touch per key
first served from the store in this process. They are flushed:

- when at least 10 s have passed since the last flush and a record is
  pending (checked when a record is queued);
- at the end of a `machinome test` run, in the runner's `finally`, so
  `--failfast` and a model failure under `--all` flush too;
- at interpreter exit.

A process killed without exit handlers therefore loses at most the last
10 s of decided verdicts, and it leaves the store valid.

A warm run writes too. Its touches, about one per key it was served (about
1.1 k for a clock 2 run), go out as one segment per flush, and a warm clock 2
run of about 18 s flushes once or twice. The current stamp's segment count
therefore grows by one or two per run until a load finds more than 64 and
compacts them. That is intended: touches are how last use reaches
eviction, and compaction bounds the count.

**Compaction.** It runs at load, when the current stamp has more than 64
segments or the store holds more records than its limit:

1. Merge the current stamp's valid records, one per key with the latest
   last-use, into one new segment, and publish it.
2. Then delete exactly the segments that were merged.
3. Delete segments that failed validation, and temporaries older than one
   hour.

Step 1 precedes step 2 on purpose. At every instant, each current-stamp
record is in at least one published segment, and that is what lets a reader
that finds an input gone recover it by listing once more (Read, above).

Two concurrent compactors may each publish a merged segment. The duplicates
carry identical verdicts for identical keys and are merged next time. A
segment published by another process after the listing is not deleted,
because only merged inputs are. A file that cannot be removed, such as one
open on Windows, is left for a later compaction.

**Bound and eviction.** The store holds at most 2¹⁸ records in total, across
stamps: about 12 MiB on disk. The in-memory index is several times larger
than the file, because it is a Python dict of 32-byte keys and small verdict
tuples. At the full bound it is about 60 MiB: a dict of 2¹⁸ such entries
measured 57 to 59 MiB. A smaller store costs proportionally less. The bound
is an internal value, not a flag or a variable, in the manner of ADR-092's
margins. When a compaction finds the store over the limit, it evicts:

1. **Foreign-stamp segments first**, oldest file first.
2. **Then the current stamp's least recently used records**, until three
   quarters of the limit remain.

"Used" means written or touched at a flush, so the unit is the run. Clock 2
decides about 1.1 k keys per full run, so the limit keeps on the order of a
hundred edit-runs of history before anything current is evicted.

**Failure.** The store must never raise into an assertion. An `OSError`, a
malformed file, a `.verdicts` that is a regular file, or a read-only build
directory disables the store for the rest of the process. The failure is
logged at debug level, the pending records are dropped, and the run carries
on with the in-process memo. The default run's output is unchanged whether
or not the store works.

**Why not SQLite in WAL mode.** It is stdlib, indexed and transactional.
But:

- its correctness rests on POSIX advisory locks and, in WAL mode, on a
  memory-mapped `-shm` index, which SQLite documents as unreliable on
  network and shared filesystems. The pilot's projects are on virtiofs;
- its `-wal`, `-shm` and `-journal` sidecars would all need sparing;
- a corrupt database needs detection and recreation, so its failure modes
  would be the filesystem's.

Segments need only atomic rename, which every target filesystem provides.
A full store is about 12 MiB. Reading and checksumming one whole and
merging it into a dict took about 0.15 s in a measurement made for this
plan, off virtiofs. A project's usual store is far smaller. Per-key
lookups are dictionary lookups after the load.

Alternatives also rejected:

- **One file per verdict.** Tens of thousands of directory entries, and an
  open per lookup on a filesystem where opens are not cheap.
- **Appending to one shared file.** It needs a lock to prevent torn,
  interleaved appends.

### 8. Run policy: `verdict_store`, default on (point 6)

`ComparisonPolicy` becomes `'kernel volume_epsilon placement_quantum
verdict_store'`, declared with
`defaults=(DEFAULT_PLACEMENT_QUANTUM, True)`. Every existing two- and
three-argument construction therefore keeps meaning "at the default quantum,
store on". As in ADR-090, EQUALITY with a shorter tuple breaks, and the
assertions in `ComparisonKernelSelectionTest` are widened. That is the
intended, visible break.

`resolve_comparison_policy(..., verdict_store=None, environ=None)` resolves
the switch before the kernel is branched on, because both kernels carry it:

- an explicit value (the flag) wins;
- else `SOLID_TEST_VERDICT_STORE`, which must be `on` or `off`. Any other
  non-empty value is an error naming the variable and both values, raised
  before any node is built. The empty string counts as unset, as it does for
  the other `SOLID_TEST_*` variables;
- else on.

`machinome test` adds `--verdict-store` / `--no-verdict-store`
(`argparse.BooleanOptionalAction`, default `None`), outside the kernel
group. The positive flag lets a single run override a checkout's
`SOLID_TEST_VERDICT_STORE=off`. Outside `machinome test` (a `ScenarioTest`
under pytest, an assertion driven directly) the same policy is resolved
from the environment at the first comparison, as ADR-073 specified.

With the store on, output does not change: no pre-build line and no
summary change. With it off, `verdict store off` joins the summary's
parenthesis after the faceted label and epsilon and the non-default
quantum, for example
`(faceted kernel, volume epsilon 0.5 mm³, verdict store off)`.

Nothing announces hits. A served verdict is the verdict the same key
produced, so a store-served run is not a different kind of run the way a
faceted one is. The manual says how to force a cold run.

Alternatives considered and rejected:

- **Default off.** The floor would never benefit, because it runs
  `machinome test` without extra flags, and the finding is exactly that
  every floor run is cold.
- **A three-valued switch** (`on`, `off`, `read-only`). No finding asks for
  read-only.

### 9. What is never persisted (point 7)

Exactly what the in-process memo refuses, plus one case of its own:

- **A node with no identity.** Mesh-only test doubles take the
  `trimesh.boolean` fallback, which never reaches `_memoized`. The virtual
  floor is a record of length ≤ 6, for which `_record_key` returns `None`.
  Also a shape with no `shape_identity` (composed for one comparison, or
  from a non-current artifact), a flexible leaf with an overridden seam or
  an unreadable source, and a faceted artifact that `_geometry_identity`
  cannot observe.
- **A relative matrix with a non-finite entry.** `_verdict_key` returns
  `None`.
- **A computation that raised.** That covers an OCCT failure
  (`RuntimeError`), a refused false-empty common (`ExactCommonInconsistency`,
  `ExactCommonVerificationError`), a missing mesh engine
  (`MeshEngineUnavailable`) and an engine refusal of a mesh (`ValueError`).
  `_memoized` stores only on return, and the store queues only what
  `_memoized` stores.
- **New:** a pair whose persistent identity cannot be established, because
  the artifact changed since its geometry was read (§3) or it carries no
  load observation. Such a pair is still cached in process under its
  in-process key, exactly as today.

### 10. Why the persistent tier cannot change a verdict (point 8)

The in-process memo's premise is already accepted in ADR-070 and extended
by ADR-090 and ADR-092: a pair's verdict is a function of its two
geometries, the evaluation path and its relative placement, and the key
names all of them. This tier serves a stored verdict only when every field
of that premise is equal:

- **Geometry.** The persistent identities are SHA-256 digests of the very
  bytes the compared geometry was read from (§3), or of the full serialized
  state a flexible leaf is evaluated from (§4). Equal digests mean equal
  bytes or equal state, under the collision resistance ADR-060's source
  digests already rely on. That is strictly stronger than the in-process
  memo's `(path, mtime)` for exact shapes.
- **Placement and path.** These are the same cells, quantum and path
  ADR-090 specified, unchanged. ADR-090's bound on what a cell merges
  (`3qL + √3 q`) is unchanged.
- **The function itself.** The in-process memo assumes that one process's
  code and kernels are the same at the first and the second ask. That is
  trivially true within a process. Across processes it is what the stamp
  asserts: the same framework source byte for byte, the same kernel and
  evaluator distributions, the same platform and interpreter ABI.

So the tier adds one assumption to ADR-070's, **stability across
processes**, and the stamp makes it explicit. It never loosens a key, adds a
tolerance or folds zero volume into emptiness. The raw verdict is stored bit
for bit and `_settled` runs after it, exactly as today.

**The failure direction is a miss.** Each of these computes, exactly as
today:

- a missing, changed or unreadable artifact;
- a missing load observation;
- an unreadable source;
- a foreign stamp;
- a corrupt, truncated or unknown segment;
- an unwritable directory;
- a disabled switch.

Nothing in the tier can turn a question the kernel would have computed into
a different answer. It can only return an answer the kernel already gave
for an identical key, or decline.

**The one honest extension.** For the computed answer (not the
mathematical question), invariance under a common rigid transform holds up
to the kernel's float behaviour. OCCT's boolean runs with
`SetRunParallel(True)`, and the same relative pose at two world poses can in
principle differ in the last bits of a volume. The in-process memo already
serves the answer from whichever pose asked first *in the run*. Persistence
serves the answer from whichever pose asked first *under the stamp*,
possibly in an earlier run. It is the same assumption with a longer reach,
and it is stated here as ADR-070 stated it, not hidden.

### 11. The framework's own suite runs with the store off

`tests/base.py` sets an absolute `SOLID_BUILD_DIR`, and `tests/test_meta.py`
spawns `machinome test` with one. With the default on, test runs would
serve one another's verdicts, and the boolean-counting tests
(`test_intersection_memo.py`, `test_flexible_cache_performance.py`,
`test_exact_placement_cache.py`, `test_broad_phase_culling.py`) would lose
their meaning between runs. The suite's existing `tests/conftest.py` is
therefore extended, not replaced. It keeps what it does today:
`collect_ignore = ['meta_project', 'vet_projects']`, which keeps the fixture
projects' deliberately failing `test_*.py` files out of pytest's collection.
It gains a session-wide `SOLID_TEST_VERDICT_STORE=off`, which subprocesses
inherit.
The store's own tests enable it explicitly, on a temporary build root, and
reset the process state between cases.

### 12. How tests and evidence observe the store without new output

Proof is by count, not timing. The default output may not change, so:

- **In-process tests** read private counters on the store module (served,
  queued, flushed) and patch `intersect_shapes` and `_faceted_verdict` to
  count computations. These are the seams the existing memo tests use.
- **Cross-process tests and the evidence runs** run the CLI through a small
  child probe. The probe imports `machinome.test`, wraps the verdict
  computations and the store's lookup, calls `machinome.cli.manage()` and
  writes one JSON line of counts to stderr at exit. This is the technique of
  the originating measurement. It adds no product surface.

## Risks / Trade-offs

- **[A locally rebuilt kernel binary keeps its distribution version]**
  → The stamp names distributions, not binary bytes. A hand-rebuilt OCP
  with an unchanged version string would not be detected. The manual says
  `--no-verdict-store`, or deleting `.verdicts`, forces a cold run. The
  stamp's platform and ABI tokens cover the ordinary way binaries differ.
- **[Project test code patches framework functions at run time]**
  → A verdict computed under a monkeypatched kernel would be stored. The
  framework's suite is pinned off (§11), and a project doing this is outside
  the assertion contract. The manual names the switch for such experiments.
- **[Kernel non-determinism]** → Covered by §10's extension, which is an
  assumption the in-process memo has made since ADR-070. A disagreement
  between two records for one key is kept as whichever is newer. It is not
  detected, because detecting it would need two computations of one key,
  which is the cost this change removes.
- **[Disk and memory]** → The bound is 2¹⁸ records: about 12 MiB on disk
  and about 60 MiB of index in memory at the full bound (§7), with the
  eviction rule stated. Deleting the directory is always safe.
- **[A framework developer's edits make every project run cold]**
  → By design (§5). Correctness over hit rate, and no worse than today.
- **[An older framework sweeping a newer project's build directory deletes
  `.verdicts`]** → Losing the store costs one cold run. There is no other
  effect.
- **[The measured win falls short of the warm floor]** → Load, stamp and
  digest costs sit on top of the 12–18 s floor. The evidence task records
  whatever the numbers are, as ADR-070's and ADR-090's precedents require,
  and no key is widened to chase them.
- **[Two processes compute the same fresh pair at once]** → Both pay for it
  once. Records for a key are identical, and neither process errors.
  Cross-process deduplication of in-flight work is not a goal.
- **[A load overlaps a compaction]** → The reader re-lists once and reads
  the merged segment (§7). Only a second compaction, deleting that merged
  segment between the re-listing and the open, costs it misses for that
  run.

## Migration Plan

None is required. The change is additive and on by default, and the
default output is unchanged. A project gains a `.verdicts/` directory under
its build root on its next test run. To roll back, run with
`--no-verdict-store` or `SOLID_TEST_VERDICT_STORE=off`, or delete the
directory. An older framework ignores the directory, and its sweep deletes
it.

## Open Questions

None is blocking. These judgement calls were made without asking the
pilot and are recorded so they can be overturned cheaply:

1. The names `--verdict-store` / `--no-verdict-store`,
   `SOLID_TEST_VERDICT_STORE` (`on`/`off`) and the policy field
   `verdict_store` (§8).
2. Default on (§8).
3. The whole-package source digest in the stamp, rather than a module list
   (§5).
4. `molejo` in the global stamp rather than in the flexible identity (§5):
   one rule, at the cost that a molejo upgrade makes rigid pairs cold once.
5. Digests are memoised on the full `ArtifactObservation`, not on
   `(path, mtime_ns, size)` (§3).
6. The flexible identity drops the absolute source path and the metadata
   fingerprint, and keeps module, source digest, structural identity,
   values and spec digest (§4).
7. The flexible identity is used in both tiers and on both paths, and the
   exact-path override rule is "overrides `shape`" (§4).
8. The store lives at `<build root>/.verdicts/`, and the sweep prunes it by
   directory. The directory's name is hosted in `machinome/_artifact.py`,
   not in the store module, so the builder imports nothing new (§6).
9. The format is immutable checksummed segments, not SQLite (§7).
10. The internal constants: a flush every 10 s, compaction above 64
    segments, a limit of 2¹⁸ records, eviction to three quarters, foreign
    stamps first, and temporaries older than one hour removed (§7).
11. Nothing announces hits, and only "store off" is named (§8).
12. The framework suite pins the store off in its existing
    `tests/conftest.py` (§11).

## The ADR this cycle produces (outline for the implementer)

The ADR is `docs/adrs/TEST-FRAMEWORK/ADR-156-a-decided-verdict-outlives-the-run.md`,
using the next free number (156 at bf24687). It is **Accepted**, *Amends*
ADR-070, and is *Related to* ADR-090, ADR-073, ADR-029, ADR-092, NODE/ADR-060,
NODE/ADR-071, NODE/ADR-140, and BUILD/ADR-038 and ADR-119 (per-artifact
publication with its sweep, and per-model build directories). It is written after
implementation, with the measured numbers.

- **Context:** the table above, cited to `workflow/warts.md`. The floor's
  fresh process per run. The identities that die with the process. The
  flexible pairs that `_fast_geometry` and the exact branch leave unkeyed.
- **Decision drivers:**
  - never change a verdict (ADR-070, in force);
  - the default output is unchanged (ADR-073/090);
  - invalidation needs no maintainer;
  - two writers are normal;
  - no dependency or import is added to a path that avoids one.
- **Considered options:**
  1. a persistent content-keyed tier beneath the memo, with segments and a
     stamp [chosen];
  2. SQLite WAL [rejected: locking and shm on shared filesystems];
  3. key on the in-process identities [rejected: paths and mtimes];
  4. a hand-maintained module list in the stamp [rejected: silent
     maintenance];
  5. keep flexible uncached [rejected: state keys have no collision; the
     v8-engine measurement].
- **Decision outcome:** §§1–9 in brief.
- **The amendment to ADR-070:** "nothing survives the process" gives way to
  a persistent tier under a stamp. "Flexible parts are uncacheable by
  construction" was right about names and does not reach state (§4). Note
  that ADR-090's restatement of the latter is superseded with it.
- **Why this cannot serve a wrong verdict:** §10, reproduced with its one
  honest extension.
- **Consequences:**
  - the cold and warm process numbers for `wall_clock_02`, strandbeest and
    the v8-engine slice under both kernels, from `evidence.md`;
  - the default output is unchanged;
  - the framework's suite runs with the store off;
  - `cached_shape`'s `(path, mtime)` in-process key is left as a recorded
    wart.
- **References:**
  - `machinome/test.py` (`_memoized`, `ComparisonPolicy`,
    `resolve_comparison_policy`);
  - the store module;
  - `machinome/_artifact.py` (the store's directory name);
  - `machinome/exact.py` (`cached_shape`);
  - `machinome/node/flexible.py`;
  - `machinome/core/builder.py` (the sweep);
  - `machinome/manager/test.py`;
  - the tests;
  - `workflow/warts.md`;
  - this change.

# ADR-156: A Decided Verdict Outlives the Run

**Status:** Accepted; the in-process shape key its consequences left weaker was replaced 2026-10-03 by [ADR-164](../NODE/ADR-164-the-loaded-shape-cache-keys-on-the-artifacts-observation.md); the mesh engine's binding amended 2026-10-04 by [ADR-176](ADR-176-the-mesh-engine-is-a-provider-behind-the-seam-installed-by-an-extra.md)
**Date:** 2026-09-29
**Amends:**
- [ADR-070: Relative Placement as the Identity of an Intersection Question](./ADR-070-relative-placement-as-the-identity-of-an-intersection-question.md)
  (and, with it, ADR-090's restatement that flexible parts stay uncacheable)

**Related to:**
- [ADR-090: The Placement Quantum Is a Property of the Test Run](./ADR-090-the-placement-quantum-is-a-property-of-the-test-run.md)
- [ADR-073: The Comparison Kernel Is a Property of the Test Run](./ADR-073-the-comparison-kernel-is-a-property-of-the-test-run.md)
- [ADR-029: Manifold Cache and AABB Broad Phase for Assertions](./ADR-029-manifold-cache-and-aabb-broad-phase-for-assertions.md)
- [ADR-092: Face Boxes Decide an Enclosed Pair Without a Boolean](./ADR-092-face-boxes-decide-an-enclosed-pair-without-a-boolean.md)
- [NODE/ADR-060: Content-Verified Currency Beneath the Mtime Rule](../NODE/ADR-060-content-verified-currency-beneath-the-mtime-rule.md)
- [NODE/ADR-071: Node-Scoped Content Currency](../NODE/ADR-071-node-scoped-content-currency.md)
- [NODE/ADR-140: A Path Reuses Only Its Own Identical Successful Bind](../NODE/ADR-140-a-path-reuses-only-its-own-identical-successful-bind.md)
- [BUILD/ADR-038: Per-Artifact Atomic Build Publication](../BUILD/ADR-038-per-artifact-atomic-build-publication.md)
- [BUILD/ADR-119: Named Project Models and Per-Model Build Directories](../BUILD/ADR-119-named-project-models-and-per-model-build-directories.md)

## Context and Problem Statement

Every spatial assertion routes through the verdict memo, `_memoized` in
`machinome/test.py`, keyed on two solid identities, the evaluation path and
the quantised relative placement (ADR-070, ADR-090). ADR-070 kept it per
run: "nothing survives the process". The studio floor starts a fresh
`machinome test` process for every run, so every floor run starts cold.

Measured at framework `main` bf24687 (`workflow/warts.md`, "3DPrintedClocks
wall clock 02 and strandbeest (2026-09-29, verdict memo across runs)"), by
running each suite twice in one interpreter:

| Suite | Cold | Of which in misses | Warm (every ask served) |
|---|---:|---:|---:|
| 3DPrintedClocks `wall_clock_02` (22 tests, exact) | 1348.9 s | 1280.6 s (95%), 643 booleans | 18.35 s |
| strandbeest walking demo (3 tests, exact) | 246.9 s | 228.1 s (92%), 1055 booleans | 11.97 s |

The identities the memo keys on die with the process: an exact shape is
`(brep path, float mtime)`, a faceted solid is the STL's full
`ArtifactObservation`. Both are absolute and both change on a rebuild that
reproduces identical bytes, on a move and on a copy. And flexible pairs were
not keyed at all: `_fast_geometry` returned `None` for a flexible leaf,
although `FlexibleNode._faceted_cache_snapshot` had just computed its full
state to key the Manifold cache, and an evaluated molejo solid has no
`shape_identity` on the exact path. ADR-070 measured 1499 s of the v8-engine
root suite's 1622.8 s in exactly those pairs.

## Decision Drivers

- The memo must never change a verdict (ADR-070, in force).
- The default run's output is unchanged (ADR-073, ADR-090).
- Invalidation needs no maintainer.
- Two writers are normal: the floor's subprocess and a pilot or a second
  agent may test one project at once.
- No dependency or import is added to a path that avoids one (ADR-052, the
  faceted run's refusal to import `cadquery`, the CLI's startup cost).

## Considered Options

1. **A persistent, content-keyed tier beneath the memo, stored as
   immutable segments and bound to a stamp** (chosen)
2. SQLite in WAL mode
3. Persist under the in-process identities
4. A hand-maintained module list in the stamp
5. Keep flexible pairs uncached

## Decision Outcome

Chosen: **option 1.**

- **A tier beneath `_memoized`, consulted only at an in-process miss.** With
  the run's store switch on and a project build root, the in-process key is
  made persistent and looked up; a served verdict enters the in-process
  memo. A computed verdict enters both tiers; a computation that raises is
  kept in neither. `_settled` still applies the run's epsilon after the
  memo, so the store holds raw engine verdicts: emptiness, the volume's
  IEEE-754 bits and which kernel decided it.
- **The persisted key is state.** The SHA-256 of a canonical encoding of the
  format version, the stamp, the evaluation path, the quantum's bytes, two
  persistent identities and ADR-090's placement cells, in the in-process
  key's order. A rigid solid's persistent identity is the SHA-256 of the
  bytes its compared geometry was READ from: the STL whose observation
  keyed its Manifold, or the BREP whose load `cached_shape` now records by
  observing the file before and after `importBrep`. If the file has changed
  since, there is no persistent identity and the pair is kept in process
  only. Digests are memoised per process on the full `ArtifactObservation`,
  because `_atomic_export` stamps artifacts with their source's mtime and a
  rebuild may reproduce the old mtime and size with new bytes.
- **A flexible leaf is keyed on its state in both tiers.** One coherent
  snapshot, from one `current_shape()`, yields the Manifold key and the
  STATE identity: technology, defining module, project-relative source
  digest, full structural identity, bound values and spec digest -- the
  Manifold key without its absolute source path and its fingerprint. On the
  exact path the leaf records that identity beside the solid its
  last-binding memo built. A leaf whose class overrides `base_mesh`
  (faceted) or `shape` (exact), or whose sources cannot be read, stays
  uncached.
- **The stamp covers the whole package.** The format version,
  `machinome.__version__`, a digest of every `.py` of the running package,
  the installed versions of `cadquery-ocp`, `cadquery`, `manifold3d`,
  `trimesh` and `molejo` read from distribution metadata (or the origin
  file's size and mtime, or `absent`), and the platform and interpreter
  ABI. All read inside the stamp function at the first store use; no kernel
  is ever imported to read a version.
- **Where it lives.** `<build root>/.verdicts`, the build root the testing
  process resolves: the anchored root, which every declared model of a
  project shares; else an absolute `SOLID_BUILD_DIR`; else `SOLID_BUILD_DIR`
  under the project root above the working directory; with none of these,
  no store. The builder's sweep prunes the directory by name, a constant in
  `machinome/_artifact.py`, so the builder imports nothing new.
- **Immutable segments, merged on read.** A segment is a header (magic,
  format version, full stamp, count), fixed-width records and a trailing
  SHA-256, published by `os.replace` and never modified. A reader validates
  and merges every current-stamp segment; when a listed segment has
  vanished it lists once more, because a compaction publishes its merged
  segment before deleting its inputs. Compaction runs at load above 64
  current-stamp segments or 2^18 records, evicting foreign stamps first,
  oldest first, then the least recently used records down to three
  quarters of the limit; a touch per served key is how last use reaches
  eviction. Pending records flush every 10 s, at the end of a
  `machinome test` run and at exit.
- **Any failure disables the tier for the process**, logged at debug level
  and never raised or printed.
- **The switch.** `ComparisonPolicy.verdict_store`, defaulting on,
  `--verdict-store` / `--no-verdict-store`, `SOLID_TEST_VERDICT_STORE`
  (`on`/`off`) read through the CLI's `.env` rule; the flag beats the
  environment, which beats the default. A run with the store on prints what
  it printed before; a run with it off says `verdict store off` in the
  summary parenthesis, after the faceted label and a non-default quantum.

### The amendment to ADR-070

"Nothing survives the process" gives way to a persistent tier under a stamp.
"Flexible parts are uncacheable by construction and stay that way", and
ADR-090's restatement of it, are superseded: the argument was right about
NAMES -- two instants at one relative placement are different questions
when the flexible part's binding differs -- and does not reach STATE. A key
that contains the bound values and the spec digest separates exactly the
cases a name-keyed census conflated.

### Why this cannot serve a wrong verdict

A stored verdict is served only when every field of the in-process memo's
premise is equal: the geometry (SHA-256 of the very bytes it was read from,
or the full serialized state a flexible leaf is evaluated from -- strictly
stronger than the in-process `(path, mtime)` for exact shapes), the path,
the quantum and the placement cells (ADR-090's bound `3qL + sqrt(3) q`
unchanged), and the function itself: the stamp asserts the same framework
source byte for byte, the same kernel and evaluator distributions, and the
same platform and ABI. The tier adds one assumption to ADR-070's, stability
across processes, and makes it explicit. It never loosens a key, adds a
tolerance or folds zero volume into emptiness; the raw verdict is stored
bit for bit and `_settled` runs after it.

The one honest extension: invariance under a common rigid transform holds
for the computed answer only up to the kernel's float behaviour (OCCT runs
its boolean with `SetRunParallel(True)`). The in-process memo already serves
the answer from whichever pose asked first in the run; persistence serves it
from whichever pose asked first under the stamp. It is the same assumption
with a longer reach, stated as ADR-070 stated it.

The failure direction is a miss: a missing, changed or unreadable artifact,
a missing load observation, an unreadable source, a foreign stamp, a
corrupt or truncated segment, an unwritable directory or a disabled switch
all compute exactly as a run with no store.

### Why not SQLite (option 2)

Its correctness rests on POSIX advisory locks and, in WAL mode, on a
memory-mapped `-shm` index, which SQLite documents as unreliable on network
and shared filesystems; the pilot's projects are on virtiofs. Its sidecars
would all need sparing, and a corrupt database needs detection and
recreation. Segments need only atomic rename.

### Why not the in-process identities (option 3)

Paths and mtimes are exactly what the finding shows do not survive a
rebuild that reproduces identical bytes, a move or a copy.

### Why not a module list (option 4)

The minimum list (`test.py`, `exact.py`, `mesh_engine.py`,
`node/flexible.py`, `node/adapters/molejo.py`, `node/base.py`) is a
maintenance obligation that fails silently the day the next tier, decode
change or adapter hook lands elsewhere. The whole package costs about 20 ms
once per process; a framework developer's edit anywhere makes their next
project run cold, which released users never pay.

### Why not keep flexible pairs uncached (option 5)

State keys have no collision, the pilot directed otherwise, and v8-engine's
1499 s is the measured cost.

## Consequences

- Measured one fresh `machinome test` process after another, the store
  deleted before each cold process (full counts, raw lines and the probe in
  `evidence.md` of the `persistent-verdict-memo` OpenSpec change):

  | Suite | Process | Wall | Computations | Booleans | Store hits | Verdicts |
  |---|---|---:|---:|---:|---:|---|
  | 3DPrintedClocks `wall_clock_02` (exact) | cold | 1255.93 s | 1138 | 643 | 0 | 16 passed, 6 failed |
  | | warm | 27.81 s | 0 | 0 | 1138 | 16 passed, 6 failed |
  | strandbeest walking demo (exact) | cold | 163.51 s | 1510 | 1055 | 0 | 3 passed |
  | | warm | 10.63 s | 0 | 0 | 1510 | 3 passed |
  | | `--no-verdict-store` | 166.36 s | 1510 | 1055 | 0 | 3 passed |
  | v8-engine valve-motion slice (faceted) | cold | 2.17 s | 2 | 2 faceted | 0 | 8 passed |
  | | warm | 2.13 s | 0 | 0 | 2 | 8 passed |
  | v8-engine valve-motion slice (`--exact`) | cold | 2.91 s | 2 | 1 | 0 | 8 passed |
  | | warm | 2.26 s | 0 | 0 | 2 | 8 passed |

  The verdicts, and the clock's six failure messages with their volumes,
  are identical cold, warm and store-off, and identical to the baselines.
  The v8-engine slice's two spring pairs were uncacheable on both kernels
  before this change and are keyed now.
- The clock's warm process sits 9.46 s above ADR-070's in-interpreter warm
  floor of 18.35 s. The store's own work in a warm process was timed
  directly at about 0.1 s (stamp 0.02 s, load 0.02 s, key derivation with
  digests 0.06 s, lookups under 0.01 s); the rest is per-process work
  outside the memo that a second pass in one interpreter did not repeat.
  strandbeest's warm process, 10.63 s, is at its 11.97 s floor within the
  day's machine variance (its cold process was also faster than the
  baseline's, with identical counts). No key was widened to chase either.

- The default run's output is unchanged, byte for byte (the manager tests'
  exact-string assertions; `tests/test_verdict_store_cli.py` compares a
  first and a second process's stdout apart from the timing figure).
- The framework's own suite runs with the store off: `tests/conftest.py`
  sets `SOLID_TEST_VERDICT_STORE=off` for every subprocess and suspends the
  store in the pytest process, whose positionally constructed policies
  default on. The store's tests switch it on explicitly on temporary build
  roots. The three `FacetedKernelMetaTest` cases that pin what a run at the
  defaults prints run their subprocesses at the store's default, in a
  throwaway build directory.
- `ComparisonPolicy`'s fourth field is declared with a default, so every
  two- and three-argument construction keeps meaning "store on"; policy
  EQUALITY with a shorter tuple breaks, and
  `ComparisonKernelSelectionTest` was widened to 4-tuples.
- `cached_shape`'s in-process key stays `(path, float mtime)`, weaker than
  every other artifact cache; the persistent tier guards itself against it
  through the recorded load observation, and the gap is recorded in
  `workflow/warts.md` for its own triage. (Closed on 3 October 2026 by
  [ADR-164](../NODE/ADR-164-the-loaded-shape-cache-keys-on-the-artifacts-observation.md),
  which keys the shape on the artifact's stat observation; the entry
  left `warts.md` on 7 October 2026.)
- A flexible leaf's geometry is still evaluated before its key is formed,
  as a rigid shape is still loaded; deferring evaluation to a miss is a
  possible follow-up.

## References

- `machinome/test.py` -- `_memoized`, `_persisted_key`,
  `_persistent_identity`, `_exact_identity`, `_flexible_geometry`,
  `ComparisonPolicy`, `resolve_comparison_policy`
- `machinome/_verdict_store.py` -- the stamp, the digest memo, the
  persisted key, segments, load, compaction and eviction, the switch-off on
  failure
- `machinome/_artifact.py` -- `VERDICT_STORE_DIRECTORY`
- `machinome/exact.py` -- `cached_shape`, `shape_load_observation`
- `machinome/node/flexible.py` -- `_snapshot`, `_state_snapshot`,
  `_exact_state_identity`
- `machinome/core/builder.py` -- the sweep's exemption
- `machinome/manager/test.py` -- the flags, the summary note, the flush
- `tests/test_verdict_store.py`, `tests/test_flexible_verdict_identity.py`,
  `tests/test_verdict_store_cli.py`, `tests/verdict_probe.py`,
  `tests/verdict_store_workers.py`
- `workflow/warts.md` -- "3DPrintedClocks wall clock 02 and strandbeest
  (2026-09-29, verdict memo across runs)"
- OpenSpec change `persistent-verdict-memo` and its `evidence.md`,
  capabilities `test-framework`, `flexible-parts`, `cli`, `build-pipeline`,
  `user-documentation`

## Amendment (2026-10-04)

[ADR-176](ADR-176-the-mesh-engine-is-a-provider-behind-the-seam-installed-by-an-extra.md) removes `manifold3d` from the stamp's distributions
(`KERNELS`): the stamp is computed in every run, all-exact ones included,
and the mesh engine is resolved only where a faceted question is asked. A
faceted verdict's persisted key carries instead the identity, name and
version, the resolved engine reports of itself (`persisted_key`'s
`engine`); an exact verdict's carries none. A faceted question whose engine
is absent or reports no version is computed without being kept. A
manifold3d upgrade therefore starts the faceted verdicts afresh and keeps
the exact ones; the record and segment layouts, and `FORMAT_VERSION`, are
unchanged.

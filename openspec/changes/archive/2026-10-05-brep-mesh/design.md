## Context

The second cycle of the phase "The next phase: the architecture ready for the
split" (`workflow/ongoing/lean-core.md`, pilot, 4 October 2026), cut from the
line `v0.8-split` at faf1c80 ("lean-core plan: openscad-out integrated; next
brep-mesh"), on the bench `machinome/WTs/v0.8-split-brep-mesh`. It carries out
the pilot's lock of the same day ("Locked at the session's close", "The
engines are `brep` and `mesh`"): the engines are named for the representation
each consumes, a boundary representation of parametric surfaces and a
polyhedral triangle mesh, not for a claim ("exact") or a quality
("faceted"); the providers are `machinome.engine.brep` and
`machinome.engine.mesh`, the module carrying the role so that one engine per
role is installed at a time; the same two words replace `exact`, `faceted` and
the providers' technology names wherever the code uses them for this split;
artifact extensions stay. The plan's entry for the cycle adds the engine
package whose `__init__` holds both seams and extends its path with portions
as `machinome/node/` does, the extras `brep` and `mesh` (ADR-167), the
verdict recompute without migration code, and the table `brep-mesh.toml`.

Precedents, all under `openspec/changes/archive/`: `2026-10-03-exact-engine`
(ADR-160 to 165: the seam, the provider, the contract integer, the leaf
bases), `2026-10-03-lean-install` (ADR-167 to 169: an extra named by the last
component of the module that needs it, three doors, no alias),
`2026-10-04-mesh-engine` (ADR-176: the mesh provider behind its seam) and
`2026-10-04-openscad-out` (ADR-177 to 179: the token gate, the declared
capability set whose `exact` member this cycle renames, removed capabilities
by `git rm` after archive). Also ADR-047, ADR-052, ADR-073 (the comparison
kernel is a property of the run; this change names it the run's engine,
Open Question 2), ADR-156 (the verdict store) and ADR-172.

Facts below were read on the bench at faf1c80, unless marked *inferred*; the
scans ran under Python 3.11 and the workspace venv's 3.12.3 alike (the gate's
count is 548 under both). Probes ran under the session scratchpad; the gate's
prototype is this change's `gate-prototype.py`.

### What carries the words today

| today | what | readers |
|---|---|---|
| `machinome/exact_engine.py` | the B-rep seam: `exact_engine()`, `require_exact_engine()`, `ExactEngineUnavailable`, `ExactEngineIncompatible`, `ExactCommonInconsistency`, `ExactCommonVerificationError`, `CONTRACT = 1` (line 34), `PROVIDER = 'machinome.occt.engine'` (37), four Protocols and `ExactShape` | `exact_cache.py:28`, `exact_artifacts.py:21`, `test.py:21`, `node/exact_leaf.py:7`, `node/fusion.py:10`, `node/cadquery.py:6`, `node/step.py:77`, `node/build123d.py:22`, `occt/engine.py:59` |
| `machinome/mesh_engine.py` | the mesh seam: `mesh_engine()`, `require_mesh_engine()`, `MeshEngineUnavailable`, `MeshEngineIncompatible`, `CONTRACT = 1` (45), `PROVIDER = 'machinome.manifold.engine'` (48), five Protocols and `MeshSolid` | `test.py:22`, `node/fusion.py:11`, `manager/test.py:21` |
| `machinome/occt/engine.py` (+ `__init__.py`) | the B-rep provider, 13 operations, `CONTRACT = 1` (63), refusing by `require_extra('occt', ...)` (32) | the seam; projects (`intersect_shapes`, `fuse_shapes`, `placed_shape`, `solid_count`, `solid_volume`, exact-engine.toml) |
| `machinome/manifold/engine.py` (+ `__init__.py`) | the mesh provider, ten operations, `CONTRACT = 1`, refusing by `require_extra('manifold', ...)` (30) | the seam only |
| `machinome/exact_cache.py`, `machinome/exact_artifacts.py` | the memos over B-rep handles; `.brep`/`.stl` publication | leaf base, fusion, test framework, `manager/test.py:20`, `node/leaf.py:178` |
| `machinome/node/exact_leaf.py` | `ExactLeafNode`, its `exact` property (64-66) | `node/cadquery.py:9`, `build123d.py:24`, `step.py:79`, `sheet_leaf.py:5` |
| `node/base.py:1138`, `node/internal.py:122`, `node/molejo.py:69`, `node/leaf.py` | the declared capability `exact` (ADR-178), `CONTRACT = 2` (leaf.py:24) | `test.py:236`, `core/builder.py:725`, `node/fusion.py:38-104` |
| `machinome/test.py` | `KERNELS = ('exact', 'faceted')` (124), `ComparisonPolicy`'s field `kernel` (119-122), `resolve_comparison_policy(kernel=None, ...)` and `SOLID_TEST_KERNEL` (132-196), the policy and its errors (190-216), `_routes_exact` (234) and `_engine_reason` (239), which read `.kernel` (236, 242), the verdict paths `'exact'`/`'faceted'` (1099, 1111, 1785-1811, 1953, 1963), `IntersectionStats.exact` (71) | `manager/test.py`, assertions |
| `machinome/manager/test.py` | `--exact`, `--faceted` (66-74) in the group `kernel` with `dest='kernel'` (64-71), `getattr(args, 'kernel', None)` (102), `self.policy.kernel` (110) and `policy.kernel` (329), the mesh run's line and summary note (110-123, 327-332) | the CLI |
| `machinome/_verdict_store.py` | `_EXACT = 2` (82), `record(..., exact)` (571) | `test.py:_memoized` |
| `machinome/node/fusion.py` | recipes `'exact-fusion-occt-v1'` (39), `'faceted-fusion-manifold-v1:'` (42) | the currency check (`node/base.py:1373-1376`) |
| `pyproject.toml` | extras `occt` (90), `manifold` (99); `cadquery`, `build123d`, `step`, `molejo` include `machinome[occt]`; `all` names both | pip |

### The counts

- **The gate's red count on faf1c80: 30 modules, 548 occurrences**
  (Decision 9's table): `faceted` 97, `exact` in identifiers and paths 174,
  `exact` in text naming the split 196, `occt`/`manifold` outside the zones
  81.
- **Specs.** 38 of the 45 baseline specs contain the word `exact` or
  `faceted` (`grep -lic`); 22 use them, or a provider's technology, for the
  split: 18 are modified here and four renamed. The other 16 use `exact` only
  as the ordinary adjective (`simulation`'s exact landings, `export`'s
  bit-exact parity, `mates`' exact half turns, ...) and get no delta. The
  plan's "39 of 46" and "eight spec names" were taken on 57928eb: since
  then `openscad-out` removed `openscad-engine` and `scad-engine-dependency`;
  `openscad-dependency` names the OpenSCAD binary, not the split, and
  `mesh-engine-dependency` already carries the lock's word. Four names
  change: `exact-engine-dependency`, `exact-geometry`, `occt-engine`,
  `manifold-engine`.
- **Tests.** 77 test files name a moved name (grep of `tests/` for the moved
  modules, classes, members, flags, extras and values); the run-policy rename
  (Open Question 2) adds one, `tests/test_tutorial_counter.py:27`, which
  clears `SOLID_TEST_KERNEL` and names no other moved name: 78. The ten
  files that pass `kernel=`, read `.kernel` or set `SOLID_TEST_KERNEL`
  (`test_manager_test.py`, `test_verdict_store.py`, `test_meta.py`,
  `test_flexible_verdict_identity.py`, `test_markings.py`,
  `test_mesh_engine_dependency.py`, `test_exact_placement_cache.py`,
  `test_assembly_integrity.py`, `mesh_engine_golden.py`,
  `test_tutorial_counter.py`) are among them.
- **Projects** (from the plan; this cycle may not grep `projects/`): three
  files of 3DPrintedClocks spell `--faceted`; the Curta's tools use `faceted`
  as their own parameter names, which stay. Imports of `machinome.occt.engine`
  and subclasses of `ExactLeafNode` exist (exact-engine.toml; the lock's
  "every `ExactLeafNode` subclass"), uncounted.

### A probe that settles the seams' names

A package whose `__init__` defines a function `brep()` and which has a
submodule `brep.py` loses the function the first time the submodule is
imported: the import system binds the submodule as the package's attribute
`brep`. Probe (scratchpad package `pkg.engine`, Python 3.11): before,
`type(pkg.engine.brep)` is `function`; after `pkg.engine.brep()` imports
`pkg.engine.brep`, it is `module`, and a second call raises `TypeError:
'module' object is not callable`. The seam resolving
`machinome.engine.brep` from `machinome/engine/__init__.py` would destroy
itself on first use. The seams therefore cannot be called `brep()` and
`mesh()` (Decision 2).

## Goals / Non-Goals

**Goals:**

- The gate passes: no `faceted`, no `exact` for the split, no `occt` or
  `manifold` outside the provider modules and the OCCT-built node modules.
- One engine package, `machinome.engine`, holding both seams in its
  `__init__` and admitting provider portions; the providers at
  `machinome.engine.brep` and `machinome.engine.mesh`, unchanged in behaviour.
- Every name of the split renamed once, with no alias: the leaf base, the
  capability, the memos, the test framework's paths, flags, values and
  messages, the recipe identities, the extras, the spec names; and the
  run-policy word `kernel`, which becomes `engine` (the pilot's ruling at
  ratification, Open Question 2).
- Every verdict's answer (emptiness, volume) byte-identical with the path word
  changed; every artifact byte-identical; the goldens unchanged.

**Non-Goals:**

- Rewriting the projects (the root cleanup's single pass), `jscad` and `stl`
  as packages, the viewer seam, cutting a distribution, the licence.
- The word `kernel` where it names the third-party library an engine wraps
  (OCCT, manifold3d): the `kernel-extras` capability, `machinome/extras.py`,
  the node modules, the providers, `machinome._verdict_store.KERNELS` (the
  library distributions the store's stamp reads, `_verdict_store.py:115`),
  `tests/test_core_kernel_free.py`. Only the run's choice is renamed
  (Decision 6).
- The library names: `OCP`, `cadquery-ocp`, `manifold3d`, molejo's own
  `molejo[brep]`; the artifact extensions `.brep`, `.stl`, `brep_file`; the
  verdict store's artifact kinds `('artifact', 'brep' | 'stl', digest)`.
- The ordinary adjective: `exactly`, exact IEEE-754 values, exact matrix
  bytes, the `exact-negative` shortcut (ADR-090: a negative answer that is
  never wrong), OpenSCAD's `$fn`.
- The studio's `machinome_test` tool and skills, the workspace's skills
  (follow-ups, Migration Plan).
- Fixture projects of the suite whose names are keys of a golden's data or
  part of an artifact's path (Decision 12).

## Decisions

### 1. The vocabulary, and how the two senses of `exact` are told apart

In identifiers, values, flags, extras, module names and spec names the words
are `brep` and `mesh`; in prose, "B-rep" (boundary representation) and
"mesh"; an engine is "the B-rep engine" or "the mesh engine", and a run that
compares on one is "a run on the B-rep engine" (`--brep`, the default) or "a
run on the mesh engine" (`--mesh`). A node, leaf, fusion, part or solid whose
`brep` is true is "a B-rep node" (leaf, fusion, ...); one whose `brep` is
false is "a mesh node" (leaf, fusion, ...): the lock's two words, not "non-B-rep".
"Has B-rep geometry" replaces the predicate "is exact".

`exact` keeps its ordinary sense where it has one, and that sense stays:
`exactly`; exact IEEE-754 values and matrix bytes; the exact-bytes verdict key
(ADR-070); the `exact-negative` shortcut (ADR-090, a negative answer that is
never wrong, used on both paths: `test.py:1913-1916` is the AABB cull of the
mesh fast path); exact fractions in `simulation/profile.py`; the snapped
`exact` 0, 1, -1 of `node/frames.py` and `motion/joints.py`. Decision 9's gate
draws the line mechanically and lists the ordinary uses it admits.

Rejected: "B-rep" and "mesh" only in prose, with identifiers left
(`ExactLeafNode`, `exact`, `'faceted'`): the lock names the identifiers. The
word `kernel` for a run's choice becomes `engine` (Decision 6; Open Question
2, ruled by the pilot): a run compares on an engine, and `kernel` keeps only
its library sense.

### 2. The engine package: `machinome/engine/__init__.py` holds both seams

`machinome/engine/__init__.py` is today's two seam modules joined, each keeping
its shape (ADR-161, 162, 176: a known provider address, resolved once per
process by `functools.lru_cache`, absence read from the provider's
`ExtraUnavailable` or its own `ModuleNotFoundError`, an integer contract
checked by equality, `require_*(needed_by, reason)` refusing with one
actionable error). It imports only `functools`, `importlib`, `typing`,
`machinome.extras` and `machinome._namespace_portions`, and ends, as
`machinome/node/__init__.py:62` does, with
`__path__ = _namespace_portions(__path__, __name__)`, so a distribution cut
from the core later installs `machinome/engine/brep.py` or
`machinome/engine/mesh.py` without the package's `__init__` and the seam finds
it. It imports neither provider.

The names, the pilot's words and no other (with "engine", the package's own
word):

| B-rep seam | mesh seam |
|---|---|
| `brep_engine()` | `mesh_engine()` |
| `require_brep_engine(needed_by, reason)` | `require_mesh_engine(needed_by, reason)` |
| `BrepEngineUnavailable` | `MeshEngineUnavailable` |
| `BrepEngineIncompatible` | `MeshEngineIncompatible` |
| `BrepCommonInconsistency`, `BrepCommonVerificationError` | — |
| `BREP_CONTRACT = 2` | `MESH_CONTRACT = 1` |
| `BREP_PROVIDER = 'machinome.engine.brep'` | `MESH_PROVIDER = 'machinome.engine.mesh'` |
| `BrepShape`; `BrepCurrency`, `BrepComposition`, `BrepComparison`, `BrepEngine` | `MeshSolid`; `MeshSolids`, `MeshComposition`, `MeshComparison`, `MeshIdentity`, `MeshEngine` |
| `_brep_absent(error)`: `ExtraUnavailable` with `extra == 'brep'`, or `ModuleNotFoundError` named `BREP_PROVIDER` | `_mesh_absent(error)`: the same with `'mesh'` and `MESH_PROVIDER` |

No seam name is a provider module's name, so resolving a provider (which
binds `machinome.engine.brep` or `.mesh` to the module) never rebinds a seam:
the probe of "Context". The mesh seam's names are today's, only their
module moves; `from machinome.engine import brep` gives the provider module, a
natural spelling for the project calls of `intersect_shapes` and its peers.
`machinome/exact_engine.py`, `machinome/mesh_engine.py`, `machinome/occt/`
and `machinome/manifold/` are deleted; nothing re-exports or aliases them
(ADR-169), so their imports fail with Python's own `ModuleNotFoundError`, as
`exact-engine`, `expression-type` and `openscad-out` did. A checkout that
pulls the deletion keeps `machinome/occt/__pycache__` and
`machinome/manifold/__pycache__`, which Python imports as empty namespace
packages: `git clean -fdX machinome/occt machinome/manifold` once (the plan's
"Update at the eighth cycle's integration"; task 3.2).

Rejected: `brep()` and `mesh()` (the probe: the first resolution replaces the
function by the module); two seam submodules `machinome/engine/brep_seam.py`
and `mesh_seam.py` (the plan puts the seams in the package's `__init__`; a
submodule beside the providers would make one namespace hold core modules and
provider modules alike, and every cut would have to tell them apart);

one parametrised seam `engine('brep')` (two contracts, two Protocol sets and
two error families do not share a signature, and every caller names its role
anyway); keeping `machinome.exact_engine` and `machinome.mesh_engine` beside
the package (two addresses for one seam, the shape ADR-169 forbids).

### 3. The providers move; the B-rep contract is 2, the mesh contract stays 1

`machinome/occt/engine.py` becomes `machinome/engine/brep.py` and
`machinome/manifold/engine.py` becomes `machinome/engine/mesh.py`, their code
unchanged but for: the refusal, `require_extra('brep', 'the B-rep engine
(machinome.engine.brep)', 'OCP')` and `require_extra('mesh', 'the mesh engine
(machinome.engine.mesh)', 'manifold3d')`; the B-rep provider's import of its
error types from `machinome.engine`; its messages (Decision 13); and its
`CONTRACT`. The two `__init__.py` files of `occt/` and `manifold/` go: the
providers are modules of the engine package, which exports the seams and no
operation.

`BREP_CONTRACT` and the provider's `CONTRACT` become 2: the contract names the
error types `intersect_shapes` raises, and they are renamed, which ADR-162's
rule ("a contract change bumps both") and ADR-165's reading of it (a renamed
declared member changes the number) make a change. Nothing the mesh contract
names is renamed (its operations, `MeshSolid` and its Protocols keep their
names), so `MESH_CONTRACT` and the mesh provider's `CONTRACT` stay 1. Inside
one distribution the two numbers cannot disagree; the bump is the record a cut
provider reads (Open Question 3).

Rejected: both stay 1 (a provider written against the old error names would
pass the check and fail at its import of `machinome.exact_engine`, a worse
refusal than ADR-162's); both become 2 (the mesh contract did not change).

### 4. The B-rep leaf base: `BrepLeafNode` at `machinome.node.brep_leaf`; the capability `brep`; leaf contract 3

`machinome/node/exact_leaf.py` becomes `machinome/node/brep_leaf.py` and
`ExactLeafNode` becomes `BrepLeafNode`, beside `sheet_leaf.py`'s
`SheetLeafNode`, which now subclasses it. The declared capability of ADR-178,
the property `exact`, becomes `brep` on the node base (`node/base.py:1138`,
`False`), `InternalNode` (all children's), `BrepLeafNode` and `MolejoNode`
(`True`); `FlexibleNode`'s private B-rep memo (`_exact_binding`,
`_exact_result`, `_exact_identity`, `_exact_solid`, `_exact_state_identity`)
and its `_faceted_cache_snapshot` become `_brep_*` and `_mesh_cache_snapshot`.
`brep` collides with no attribute of any node (grep of `machinome/` and
`tests/` for `.brep\b` and `brep =` finds only the artifact extension and
molejo's own `molejo.brep` module); it sits beside `brep_file`, the artifact
path, which keeps its name.

`machinome.node.leaf.CONTRACT` becomes **3** (ADR-165: the version changes
with a removed or renamed declared member; ADR-178 set 2), and its comment
records what 3 changed: `exact` is `brep`, `ExactLeafNode` is `BrepLeafNode`.
A class declaring `leaf_contract = 2` is refused at creation naming 2, 3 and
`machinome.node.leaf`, unchanged in wording. machinome-freecad's
`lean-core-validation` branch declares 1 under `ExactLeafNode` and is refused
already since `openscad-out` (its proposal.md, "Sibling packages"), as ADR-165
intends; its retarget subclasses `BrepLeafNode` and declares 3.

Rejected: `BRepLeafNode` (OCCT's spelling, a technology's; `brep_file`,
`.brep` and the lock's `brep` are lower case); `ExactLeafNode` kept as an alias
(ADR-169); the capability as `has_brep` (the lock names the flag `brep`).

### 5. The memos and the publication: `machinome.brep_cache`, `machinome.brep_artifacts`

`machinome/exact_cache.py` and `machinome/exact_artifacts.py` are renamed in
place, their functions unchanged in name (`cached_shape`,
`cached_bounding_box`, `cached_face_boxes`, `cached_placement`,
`shape_identity`, `shape_load_observation`, `_reset_placement_cache`;
`write_brep`, `write_stl`, `deflections`, `_atomic_export`).

Rejected: moving them under `machinome/engine/` (they are core memos over
opaque handles, exact-engine Decision 9, and the engine package is the
providers' namespace: a portion-ready package holding only the seams keeps a
cut's question simple, "which providers are installed"); leaving
`exact_cache` (the lock names "everywhere the code uses them").

### 6. The test framework: paths, flags, values

- The run-policy word `kernel` is `engine` (Open Question 2, the pilot's
  ruling): `ENGINES = ('brep', 'mesh')` replaces `KERNELS` (`test.py:124`);
  `ComparisonPolicy`'s field `kernel` is `engine` (`test.py:119-122`) and
  takes those values; the default is `'brep'`; `resolve_comparison_policy`'s
  first argument `kernel=None` is `engine=None` (`test.py:132`), and
  `_routes_brep` and `_engine_reason` read `comparison_policy().engine`
  (`test.py:236, 242`). `SOLID_TEST_ENGINE` replaces `SOLID_TEST_KERNEL`
  (`test.py:190`): it accepts `brep` or `mesh`, reads an empty value as
  unset as today, and refuses anything else (R7, Decision 13), the former
  values included; an explicit `engine` outside `ENGINES` is refused with
  R31.
- **The former variable is refused, not ignored.** When `SOLID_TEST_KERNEL`
  is set to a non-empty value, `resolve_comparison_policy` raises R30 before
  it reads the engine, whatever that value and whether or not a flag or
  `SOLID_TEST_ENGINE` is given; its value is never read. Reason: a renamed
  module fails with Python's `ModuleNotFoundError`, a renamed flag with
  argparse's exit 2, a renamed extra with pip's warning, but an environment
  variable nobody reads fails with nothing: ignored, a checkout whose `.env`
  says `SOLID_TEST_KERNEL=faceted` would silently compare on the B-rep
  engine, slower, needing the `brep` extra, at another precision, with its
  `SOLID_TEST_VOLUME_EPSILON` silently unread (the B-rep engine does not
  read it). Refusing it whatever the flag finds a stale `.env` line at the
  checkout's first run instead of at its first run without a flag. It is a
  refusal and not an alias (ADR-169): nothing is translated, and the message
  names the variable to set. The check names `SOLID_TEST_KERNEL` in
  `machinome/test.py`, which the gate allows (Decision 9: `kernel` is not
  scanned).
- `machinome test --brep` and `--mesh` replace `--exact` and `--faceted`, a
  mutually exclusive pair as now; argparse refuses the former flags as
  unrecognised arguments (exit 2).
- The verdict paths passed to `_verdict_key`/`_record_key` and read by
  `_persistent_identity` and `_engine_identity` are `'brep'` and `'mesh'`.
- `IntersectionStats.exact` becomes `.brep` (which representation supplied the
  verdict); the private names become `_brep_engine`, `_routes_brep`,
  `_brep_verdict`, `_mesh_verdict`, `_brep_identity`, `_BREP_NEEDED_BY`,
  `_BREP_REASON`, `_MESH_NEEDED_BY`, `_MESH_REASON`; `_place_solid`'s
  `faceted_identity` parameter becomes `mesh_identity`.
- `manager/test.py`: the flags, their help, the start-of-run refusal and line,
  and the summary note (Decision 13); the mutually exclusive group's variable
  `kernel` (64-71) is `engine`, both flags store into `dest='engine'`,
  `handle` passes `getattr(args, 'engine', None)` (102), and the run's line
  and the summary note test `self.policy.engine` (110) and `policy.engine`
  (329), whose fallback is `ComparisonPolicy('brep', 0.0)` (327).

Rejected: accepting the former values or flags with a warning (the no-alias
rule, ADR-169, and the pilot's "no migration code"); reading
`SOLID_TEST_KERNEL` as an alias of `SOLID_TEST_ENGINE` (ADR-169); ignoring it
(the silent switch above); keeping the policy's `kernel` (the pilot's ruling,
Open Question 2).

### 7. The verdict store recomputes once; no migration code

`_verdict_store.py` keys every record on `persisted_key(path, quantum,
identity1, identity2, placement, engine)` under a stamp holding
`_package_digest()`, a digest of every Python source of the running package
(`_verdict_store.py:163, 171-196`). This change alters both: the path words
are new, and the package's sources change. A record under another stamp is
never served (ADR-156), and a full store evicts foreign-stamp segments first,
so every project's store recomputes once and then serves again; nothing reads
or converts an old record. In the module itself only names change: `_EXACT`
becomes `_BREP`, the same bit (2), so the record layout and `FORMAT_VERSION`
(1) are unchanged; `record(key, is_empty, volume, brep)` and the index tuple
`(is_empty, volume, brep, last_use)`; the docstrings say "the B-rep path" and
"a mesh verdict". The recompute happens anyway at every framework edit (the
stamp); the path words make it certain rather than incidental.

Rejected: a migration rewriting old records' keys (the pilot ratified none;
ADR-156 makes a miss the safe direction).

### 8. The recipe identities: `brep-fusion-v1` and `mesh-fusion-v1`

`FusionNode.geometry_recipe` returns `'brep-fusion-v1'` for a B-rep fusion and
`'mesh-fusion-v1:' + sha256(children's recipes)` for a mesh fusion. What
rebuilds, read in the code:

- A mesh fusion's STL records its recipe (`_artifact_recipe`,
  `fusion.py:45-48`; `node/base.py:1373-1376` refuses currency when the
  recorded recipe differs): **every mesh fusion's STL rebuilds once**, to the
  same bytes, since the union is the same engine call on the same meshes.
- A B-rep fusion's artifacts record no recipe (`exact_artifacts._atomic_export`
  takes none; `_artifact_recipe` returns `None` for them): **no B-rep fusion
  artifact rebuilds**. Its identity is read only as an ingredient of an
  enclosing mesh fusion, which rebuilds anyway.
- Leaves' `geometry_recipe` is `'<module>.<qualname>:native-v1'`, of the
  project's own class: unchanged.

The identities drop the technology (`occt`, `manifold`), which the gate's W4
forbids in `node/fusion.py` and the lock removes from the identities. The
consequence for a second mesh engine is in Risks.

Rejected: keeping the technology (`mesh-fusion-manifold-v1`; the lock);
reading the engine's identity into the recipe (`engine.identity()`): it would
resolve the mesh engine on every currency check of a current fusion, which
`mesh-engine-dependency` forbids ("Current fusion does not resolve its
engine").

### 9. The gate: one scan, written red first, kept in the suite

`tests/test_core_names_no_split_words.py`, permanent, in the shape of
`tests/test_core_names_no_scad.py`. It reads every `machinome/**/*.py` of the
checkout (the project templates included) by token, `NAME` (identifiers,
attribute names), `STRING` (strings, docstrings) and `COMMENT`, plus each
module's own path, and parses each module with `ast.parse` so a module that
does not parse fails rather than being skipped. An f-string is read whole, as
one string, from its `FSTRING_START` to its `FSTRING_END` where the running
Python splits it (3.12), as 3.11 yields it: otherwise `f'it is the exact
{artifact} artifact'` offends on 3.11 and not on 3.12, and the count differs
by one (measured: 548 and 547). The rule, per word:


- **W1, `faceted`**: every case-insensitive occurrence offends, in any token
  and any path. No zone.
- **W2, `exact` in an identifier, attribute name or path**: offends when
  `exact` or `exactness` is a component of it, split at `_`, `/`, `.` and a
  lower-to-upper camel-case boundary (`ExactLeafNode`, `exact_cache`,
  `_routes_exact`, `node.exact`, `machinome/exact_engine.py`), except these
  ordinary-sense identifiers, by module: `simulation/profile.py` `exact`
  (exact fractions), `node/frames.py` `exact` and `motion/joints.py` `exact`
  (the snapped 0, 1, -1), `simulation/trajectory.py` `exact_lines`,
  `exact_source_lines`, `exact_end`, `authored_exact`.
- **W3, `exact` in a string, docstring or comment**, as a word (no letter
  before it; nothing after it but `ness` or a non-letter): offends when the
  token's whole text is the word (the path word `'exact'`); when it is written
  as a flag or a setting (`--exact`, `=exact`); when it is back-quoted as a
  member (`` `exact` ``); when it is `exactness`; or when the next word,
  across spaces, back-quotes, asterisks, braces, `_`, `-` and `.`, is one of
  the split's nouns: `engine(s)`, `kernel(s)`, `geometry`, `leaf`, `leaves`,
  `node(s)`, `shape(s)`, `solid(s)`, `common`, `cache`, `artifact(s)`,
  `path(s)`, `verdict(s)`, `fusion`, `adapter(s)`, `layer`, `backend`,
  `contract`, `branch`, `record(s)`, `identity`, `stack`, `part(s)`,
  `comparison(s)`, `placement(s)`, `composition`, `operation(s)`,
  `module(s)`, `surface(s)`, `children`, `route`, `project(s)`, `model(s)`,
  `run`, `test`, `side`, `currency`, `memo(s)`, `state`, `result`, `binding`,
  `only`, `needed`, `reason`, `base(s)`. Except four phrases in which the
  adjective is ordinary before such a noun, matched by module on the text from
  the word, whitespace collapsed: `node/sources.py` "exact path to watch",
  `simulation/driver.py` "exact comparison rather", `manager/test.py` "exact
  operations list", `node/base.py` "Exact artifact equality".
- **W4, `occt` and `manifold`**: every case-insensitive occurrence offends,
  in any token and any path, outside the zones: the two provider modules
  `machinome/engine/brep.py` and `machinome/engine/mesh.py`, which may name
  their libraries, and the four node-type modules whose own kernels are built
  on OCCT and which describe that kernel's behaviour,
  `machinome/node/cadquery.py`, `build123d.py`, `step.py` and `molejo.py`
  (these are node packages under "Every node type is a package"; W1 to W3
  apply to them in full).
- **What it reports**: every offending module with its count and its first
  offending tokens with their line numbers.

The rule's own unit cases (as in the SCAD gate): `ExactLeafNode`,
`exact_cache`, `'exact'`, `--faceted`, `the exact engine`, `exact-geometry`,
`` `exact` ``, `machinome/occt/engine.py` offend; `exactly`, `exact IEEE-754`,
`exact matrix bytes`, `exact-negative`, `exact-bytes`, `the exact set` pass;
the ordinary identifiers pass only in their own module.

Prototyped as `gate-prototype.py` in this change (any Python 3.11+, `python3
gate-prototype.py <checkout>`). **Red on faf1c80: 30 modules, 548
occurrences** (W1 97, W2 174, W3 196, W4 81):

| module | W1 | W2 | W3 | W4 | total |
|---|---|---|---|---|---|
| `test.py` | 59 | 52 | 54 | 3 | 168 |
| `exact_engine.py` | 0 | 37 | 20 | 8 | 65 |
| `occt/engine.py` | 1 | 5 | 14 | 18 | 38 |
| `node/flexible.py` | 5 | 14 | 13 | 0 | 32 |
| `manifold/engine.py` | 0 | 0 | 0 | 27 | 27 |
| `node/exact_leaf.py` | 0 | 8 | 16 | 2 | 26 |
| `node/fusion.py` | 6 | 10 | 7 | 3 | 26 |
| `manager/test.py` | 11 | 2 | 9 | 0 | 22 |
| `_verdict_store.py` | 6 | 10 | 3 | 0 | 19 |
| `mesh_engine.py` | 8 | 0 | 4 | 7 | 19 |
| `node/build123d.py` | 0 | 6 | 8 | 0 | 14 |
| `node/step.py` | 0 | 6 | 8 | 0 | 14 |
| `exact_cache.py` | 0 | 4 | 7 | 1 | 12 |
| `exact_artifacts.py` | 0 | 4 | 5 | 1 | 10 |
| `node/cadquery.py` | 0 | 6 | 4 | 0 | 10 |
| `node/leaf.py` | 0 | 2 | 5 | 0 | 7 |
| `occt/__init__.py` | 0 | 0 | 4 | 3 | 7 |
| `manifold/__init__.py` | 0 | 0 | 0 | 4 | 4 |
| `node/__init__.py` | 0 | 0 | 4 | 0 | 4 |
| `node/base.py` | 1 | 1 | 2 | 0 | 4 |
| `node/sheet_leaf.py` | 0 | 3 | 1 | 0 | 4 |
| `extras.py` | 0 | 0 | 2 | 1 | 3 |
| `node/internal.py` | 0 | 2 | 1 | 0 | 3 |
| `core/processes.py` | 0 | 0 | 0 | 2 | 2 |
| `node/molejo.py` | 0 | 1 | 1 | 0 | 2 |
| `simulation/__init__.py` | 0 | 0 | 2 | 0 | 2 |
| `core/builder.py` | 0 | 1 | 0 | 0 | 1 |
| `manager/import_step.py` | 0 | 0 | 0 | 1 | 1 |
| `motion/couplings.py` | 0 | 0 | 1 | 0 | 1 |
| `motion/joints.py` | 0 | 0 | 1 | 0 | 1 |

(The W4 counts for `occt/engine.py` and `manifold/engine.py` are paths and
text that become zones once the modules move; their W1 to W3 counts move with
them and must be cleared there.)

**What the gate does not see**, and how it is covered: `exact` as a
predicate or before a word outside the noun list in prose ("this leaf is
exact", "not both exact", "exact or faceted", "an exact one", "how exact").
The rule cannot tell those from the ordinary sense without reading meaning; the
rename table (Decision 17) and the refusal texts (Decision 13) name each such
message, and task 7.2 has the applier list every remaining word `exact` in
`machinome/` after the gate is green, with each one's reading recorded in
`evidence.md`. On faf1c80 the word stands 312 times in the core's text
(strings, docstrings, comments; `exactly` and `exactness` not counted), 196 of
them caught by W3; of the 116 others most are ordinary ("the exact set",
"exact matrix bytes", "exact flush contact") and a minority are the split's
predicates, which the applier rewrites from the rename table.

Rejected: the brief's example "`exact` preceded by `the`" (measured: 93
occurrences of "the exact" in the core's text, 25 of them ordinary by W3's
reading, in 16 modules:
 "the exact set", "the exact IEEE-754 values", "the exact stamp",
"the exact pinned artifact bytes", "the exact 0, 1 or -1", ...); renaming the
ordinary identifiers so that W2 needs no exceptions (the lock renames the
split's words and nothing else); an AST-only scan (misses comments, where
much of the word lives).

Not scanned, and stated: `pyproject.toml`, `requirements.txt`, `setup.cfg`,
`machinome/vet/universe.toml` (data; changed by tasks 6.1 and 6.2),
`docs/`, `tests/`.

The gate does not scan the word `kernel`: it keeps its library sense in
`kernel-extras`, `machinome/extras.py`, the node modules, the providers and
`_verdict_store.KERNELS`, and the run's `kernel`, renamed by Decision 6, is
held by the tests of Decision 15, item 6.

### 10. The extras: `brep` and `mesh`

`pyproject.toml`: `occt = ["cadquery-ocp>=7.8.1,<7.9"]` becomes `brep = [...]`
and `manifold = ["manifold3d"]` becomes `mesh = [...]`, their comments naming
`machinome.engine.brep` and `machinome.engine.mesh` (ADR-167: an extra is
named by the last component of the address of the module that needs it);
`cadquery`, `build123d`, `step` and `molejo` include `machinome[brep]`
instead of `machinome[occt]`; no node extra includes `mesh`, as no node
extra includes `manifold` today; `all = ["machinome[cadquery,build123d,step,
molejo,brep,mesh,openscad,solid2]"]`; `dev` takes `all` (unchanged). The
dependencies' comment (`pyproject.toml:28`) names the OCCT binding and
manifold3d as the extras `brep` and `mesh`. `requirements.txt` keeps the
concrete requirements (CI installs them) and its comment names `brep`, `mesh`.
`setup.cfg`'s per-file E402 ignore moves from `machinome/occt/engine.py` to
`machinome/engine/brep.py` and adds `machinome/engine/mesh.py`, which imports
`numpy` and `manifold3d` after its refusal and is not listed today (an
omission found here). `machinome/extras.py` keeps holding no table; its
docstring's example becomes "`machinome[brep]` for the B-rep engine's module".
`machinome/vet/universe.toml` keeps `manifold3d` and `OCP` in its kernel tier
(library names).

Rejected: keeping `occt` and `manifold` (the lock; ADR-167's rule names the
extra after the module, which is now `brep`/`mesh`); declaring the former
extras as empty aliases (ADR-169; pip's own warning for an unknown extra is
the refusal).

### 11. Specs: four renamed, eighteen modified, titles and purposes after archive

**Renamed capabilities.** OpenSpec 1.6.0 cannot rename a capability through a
delta, and a delta removing every requirement of a capability aborts the
archive (`dist/core/archive.js:350`, "Validate every rebuilt spec before
writing any of them"; `dist/core/schemas/spec.schema.js:8`, `.min(1,
SPEC_NO_REQUIREMENTS)`), as `openscad-out` found (its design.md Decision 12).
So, on that model: this change founds `brep-engine-dependency`,
`brep-geometry`, `brep-engine` and `mesh-engine` as new capabilities whose
deltas ADD every requirement of `exact-engine-dependency`, `exact-geometry`,
`occt-engine` and `manifold-engine`, each scenario's content kept and its words
and addresses rewritten (the provider specs' first requirement rewritten for
a module of the engine package; `brep-engine-dependency` and
`mesh-engine-dependency` gain the scenario "Resolving the provider leaves the
seam callable"); and the archive task deletes the four old directories with
`git rm` after `openspec archive`, checking that no spec names them.

**Modified capabilities.** Eighteen: `backend-neutral-materialization`,
`build-pipeline`, `cli`, `cli-startup-cost`, `flexible-parts`,
`kernel-extras`, `leaf-contract`, `markings`, `mesh-engine-dependency`,
`node-model`, `openscad-dependency`, `openscad-node`, `step-import`,
`stl-import`, `test-framework`, `user-documentation`, `vet`, `web-snapshot`.
Every requirement whose text uses the split's words, or `kernel` for the
run's choice (Open Question 2), is MODIFIED in full;
requirement names carrying them are RENAMED (OpenSpec supports it:
`specs-apply.js:170-195`, RENAMED before MODIFIED, MODIFIED naming the new
header): among them `test-framework`'s "Run-level comparison kernel" →
"Run-level comparison engine" and `user-documentation`'s "The comparison
kernels are documented" → "The comparison engines are documented". The
library sense of `kernel` (the Boolean kernel a flush contact reaches, an
installed kernel's version in the store's stamp, a node type's kernel) is
not touched. `kernel-extras` ADDS "The engine providers are modules of one engine
package that admits portions"; `cli` adds the scenario "The former selectors
are not accepted". `export`'s "exactness" is bit-exact parity between two
runtimes, the ordinary sense, and gets no delta.

**Scenario titles.** A MODIFIED requirement must keep every scenario name of
the baseline (`specs-apply.js:219`, `findMissingCurrentScenarios`: "Refresh the
change spec before archiving to avoid dropping scenarios"), so the deltas keep
the 74 scenario titles that carry the words (71 for the split, three for the
run's `kernel`: "An unknown kernel name is refused", "The model is unaware
of the kernel", `cli`'s "A developer runs the fast kernel by flag"), and the
archive task renames
them in `openspec/specs/` from this change's `scenario-titles.tsv` (spec, old
title, new title; a title that occurs twice in one spec is renamed at each
occurrence), then runs `openspec validate --specs --strict`. Rejected:
REMOVED and re-ADDED requirements under new names (OpenSpec refuses one name
in both sections, `specs-apply.js:113-116`; a new name for every requirement
whose only offence is a scenario title would rename what the pilot did not
ask, and moves each to the end of its spec).

**Dry run.** In a scratchpad copy of this bench's `openspec/` (4 October
2026, before the ratification's amendment), `openspec archive brep-mesh
--yes` applies cleanly (+ 33 added, ~ 70 modified, → 8 renamed
requirements); after the four `git rm`s (there `rm`) and the 71 title
renames of `scenario-titles.tsv` (none missing), `openspec validate --specs
--strict` passes 45 of 45 specs, and no spec names a removed capability. The
amendment (Open Question 2) adds two RENAMED requirements (→ 10) and three
title rows (74); `openspec validate brep-mesh --strict` passes on the amended
change, and the archive task's own run (task 12.2) is the dry run's
repetition. What remains of the words there is intended: the
library names (OCCT, OCP, manifold3d) in `brep-engine`, `kernel-extras` and
the node types' own lines; the former names in `kernel-extras`' and `cli`'s
scenarios that refuse them; `FacetedBox`, a fixture class of the OpenSCAD
dependency tests named for its facets; and the Purposes below, until
rewritten.


**Purposes**, which no delta reaches, are rewritten by the archive task:

- `brep-engine-dependency`: "The B-rep engine as a conditional, versioned
  dependency of the core: which paths resolve it, that the core holds no
  kernel code and treats B-rep shapes as opaque handles, the actionable
  refusal naming `machinome[brep]` when the engine is absent, the contract
  version check, and the one place, the engine package's `__init__`, where
  the core names its provider `machinome.engine.brep`. Encodes ADR-161,
  ADR-162 and ADR-180."
- `brep-geometry`: "B-rep geometry: the node's `brep` capability, the
  `shape()` accessor and its one currency, B-rep fusion, persistence and
  reload of `.brep` artifacts, Boolean failures never masked, declared
  tessellation precision, admission of a render by its kernel object, and
  independence from CAD front ends. Encodes ADR-044, ADR-045, ADR-077,
  ADR-164 and ADR-180."
- `brep-engine`: "The OCCT B-rep engine, `machinome.engine.brep`: its
  currency, the operations it performs on B-rep shapes, the operations a
  project calls directly, the contract version it declares (2), and what it
  imports. It governs behaviour that leaves the core with the engine's package
  at the cut. Encodes ADR-160 and ADR-180."
- `mesh-engine`: "The manifold3d mesh engine, `machinome.engine.mesh`: the
  provider the core's mesh engine seam resolves, the contract version it
  declares, what it imports and how it refuses an absent `manifold3d`, and
  each operation it performs on a mesh solid. It governs behaviour that leaves
  the core with the engine's package at the cut. Encodes ADR-176 and ADR-180."
- `kernel-extras`: its code list names `machinome/engine/brep.py` and
  `machinome/engine/mesh.py`, and its encodings add ADR-180.
- `leaf-contract`: "what a mesh, a B-rep, a sheet and a flexible leaf
  provides".
- `mesh-engine-dependency`: "at the start of a mesh run naming
  `machinome[mesh]`, how the seam in `machinome.engine` resolves its one
  provider"; encodes ADR-180 too.
- `step-import`: "how a STEP document becomes a B-rep part ... and its
  `brep` capability".
- `test-framework`: "ADR-073 (the comparison engine, which it called the
  kernel, as a property of the test run)", and its encodings add ADR-180.

### 12. The tests: renamed modules, fixtures that keep their names, goldens not re-recorded

78 test files name a moved name (grep of faf1c80: 77 for the split's
words, and `test_tutorial_counter.py` for `SOLID_TEST_KERNEL`). They are
repointed by the rename table; the helpers that clear the run's variable
from a subprocess's environment (`mesh_engine_golden.py:161`,
`test_tutorial_counter.py:27`) clear `SOLID_TEST_ENGINE`, and the calls
that pass `kernel=` pass `engine=`. Besides:

- **Test modules and helpers named for the split are renamed** with `git mv`
  (history kept), their content repointed: `test_exact_common_guard.py` →
  `test_brep_common_guard.py`, `test_exact_currency.py` →
  `test_brep_currency.py`, `test_exact_engine_dependency.py` →
  `test_brep_engine_dependency.py`, `test_exact_engine_seam.py` →
  `test_brep_engine_seam.py`, `test_exact_geometry.py` →
  `test_brep_geometry.py`, `test_exact_input_copies.py` →
  `test_brep_input_copies.py`, `test_exact_placement_cache.py` →
  `test_brep_placement_cache.py`, `test_exact_test_isolation.py` →
  `test_brep_test_isolation.py`, `test_front_end_free_exact.py` →
  `test_front_end_free_brep.py`, `test_leaf_contract_exact.py` →
  `test_leaf_contract_brep.py`, `test_leaf_contract_faceted.py` →
  `test_leaf_contract_mesh.py`, `test_manifold_cache.py` →
  `test_mesh_cache.py`, `test_manifold_engine.py` → `test_mesh_engine.py`,
  `test_occt_engine.py` → `test_brep_engine.py`,
  `test_resolved_exact_witness.py` → `test_resolved_brep_witness.py`,
  `exact_engine_absent.py` → `brep_engine_absent.py`, `exact_engine_golden.py`
  → `brep_engine_golden.py` (and `tests/data/exact_engine_golden.json` →
  `tests/data/brep_engine_golden.json`, bytes unchanged),
  `exact_test_support.py` → `brep_test_support.py`.
- **Fixture projects keep their names**: `tests/meta_project/` (its fixture
  names are the keys of `tests/data/mesh_engine_golden.json`:
  `exact_clearance`, `occt_only`, ...), `tests/contract_package/`
  (`exact_project.py`, `faceted_stand_in.py`, ...) and
  `tests/vet_projects/exact_engine_internals/`: projects the suite builds,
  tests or vets, whose module paths name their artifacts, their test runs and
  their findings. Their content is repointed (an import, a declared
  `leaf_contract = 3`); their file names are data.

- **The finder helpers.** `brep_engine_absent.py` refuses
  `machinome.engine.brep` (and `OCP` when asked) by default and renames its
  environment variables `EXACT_ENGINE_ABSENT` and `EXACT_ENGINE_ABSENT_LOG` to
  `BREP_ENGINE_ABSENT` and `BREP_ENGINE_ABSENT_LOG`, with its module;
  `mesh_engine_absent.py` keeps its name and its variables
  `MESH_ENGINE_ABSENT` and `MESH_ENGINE_ABSENT_LOG`, and refuses
  `machinome.engine.mesh` and `manifold3d`. A finder refusing
  `machinome.engine.brep` must not refuse `machinome.engine` (the seams): the
  helpers match a root and what lies beneath it, never a prefix of it.
- **The goldens.** `leaf_contract_golden.py`, `scad_presentation_golden.py`,
  `expression_type_golden.py` and `brep_engine_golden.py` are repointed
  (imports only) and must `--check` with no difference: no byte, uniq id,
  record or measurement moves. `mesh_engine_golden.py` records verdict tuples
  `(path, is_empty, volume.hex())`, runs `machinome test --faceted`/`--exact`
  keyed by kernel, and records the summary note and the mesh fusion's refusal
  text: its kernel loop runs `--mesh`/`--brep` and reads the recorded
  `'faceted'`/`'exact'` keys and path words through a second table of
  expected differences, `BREP_MESH_EXPECTED` (path words `faceted` → `mesh`,
  `exact` → `brep`; `faceted kernel, volume epsilon` → `mesh engine, volume
  epsilon`; `faceted fusion` → `mesh fusion`), beside the mesh-engine cycle's
  `EXPECTED`. No golden's JSON is re-recorded.
- **New:** `test_core_names_no_split_words.py` (the gate),
  `test_engine_package.py` (Decision 2's names, portions and shadowing).

Rejected: keeping every test file's name (the suite would go on teaching the
former words in its module names, which a reader of a failure sees first);
renaming the fixture projects (it would re-key the mesh-engine golden's data,
which the golden exists to keep, and move the fixtures' artifacts).


### 13. The refusal and message texts, verbatim before and after

`{...}` is filled per call. Behaviour, exception type and exit status are
unchanged for every row; only the words and install lines move. R30 is the
one new refusal: a `ValueError` from `resolve_comparison_policy`, as R7 is,
so `machinome test` exits 1 with it before any node is built and an entry
outside `machinome test` raises it at its first comparison.

| | where | before | after |
|---|---|---|---|
| R1 | `BrepEngineUnavailable` (was `ExactEngineUnavailable`) | `{needed_by} requires the exact engine because {reason}; install it with 'pip install "machinome[occt]"'. A model with no exact node never needs it` | `{needed_by} requires the B-rep engine because {reason}; install it with 'pip install "machinome[brep]"'. A model with no B-rep node never needs it` |
| R2 | `BrepEngineIncompatible` | `The exact engine machinome.occt.engine {stated}, but this machinome speaks exact engine contract version 1; install the engine released with this machinome` | `The B-rep engine machinome.engine.brep {stated}, but this machinome speaks B-rep engine contract version 2; install the engine released with this machinome` |
| R3 | `MeshEngineUnavailable` | `{needed_by} requires the mesh engine because {reason}; install it with 'pip install "machinome[manifold]"'. Exact geometry does not need it: a model whose every compared part is exact is decided by the boundary-representation kernel` | `{needed_by} requires the mesh engine because {reason}; install it with 'pip install "machinome[mesh]"'. B-rep geometry does not need it: a model whose every compared part has B-rep geometry is decided by the B-rep engine` |
| R4 | `MeshEngineIncompatible` | `The mesh engine machinome.manifold.engine {stated}, but this machinome speaks mesh engine contract version 1; install the engine released with this machinome` | `The mesh engine machinome.engine.mesh {stated}, but this machinome speaks mesh engine contract version 1; install the engine released with this machinome` |
| R5 | importing the B-rep provider without `OCP` | `the exact engine (machinome.occt.engine) needs OCP, which is not installed; install it with 'pip install "machinome[occt]"'` | `the B-rep engine (machinome.engine.brep) needs OCP, which is not installed; install it with 'pip install "machinome[brep]"'` |
| R6 | importing the mesh provider without `manifold3d` | `the mesh engine (machinome.manifold.engine) needs manifold3d, which is not installed; install it with 'pip install "machinome[manifold]"'` | `the mesh engine (machinome.engine.mesh) needs manifold3d, which is not installed; install it with 'pip install "machinome[mesh]"'` |
| R7 | `SOLID_TEST_ENGINE` (was `SOLID_TEST_KERNEL`) out of range | `SOLID_TEST_KERNEL must be 'exact' or 'faceted', not {kernel!r}` | `SOLID_TEST_ENGINE must be 'brep' or 'mesh', not {engine!r}` |
| R8 | an epsilon on a B-rep run | `the exact kernel has nothing for a volume epsilon to absorb: drop --volume-epsilon or select --faceted` | `the B-rep engine has nothing for a volume epsilon to absorb: drop --volume-epsilon or select --mesh` |
| R9 | a mesh run without the mesh engine, at its start: `needed_by` | `machinome test on the faceted kernel` | `machinome test on the mesh engine` |
| R10 | `_engine_reason` under a mesh run | `the run compares on the faceted kernel` | `the run compares on the mesh engine` |
| R11 | the mesh run's line, standard output | `Comparing on the faceted kernel (volume epsilon {e:g} mm³): verdicts are at tessellation precision, not exact.` | `Comparing on the mesh engine (volume epsilon {e:g} mm³): verdicts are at tessellation precision, not the B-rep engine's.` |
| R12 | the summary's note | `faceted kernel, volume epsilon {e:g} mm³` | `mesh engine, volume epsilon {e:g} mm³` |
| R13 | `_MESH_NEEDED_BY`, `_MESH_REASON` | `Comparing faceted geometry`; `a part without exact geometry is compared through its mesh` | `Comparing mesh geometry`; `a part without B-rep geometry is compared through its mesh` |
| R14 | `_BREP_NEEDED_BY`, `_BREP_REASON` | `Comparing exact geometry`; `two exact parts are compared on the boundary-representation kernel` | `Comparing B-rep geometry`; `two B-rep parts are compared on the B-rep engine` |
| R15 | `_STATICS_REASON` | `... from meshed intersections for every body, exact solids included, and stands the assembly on a meshed virtual floor` | `... from meshed intersections for every body, B-rep solids included, and stands the assembly on a meshed virtual floor` |
| R16 | the ignored-epsilon warning | `{assertion} ignored volume_epsilon={e} because every comparison used exact geometry` | `{assertion} ignored volume_epsilon={e} because every comparison used B-rep geometry` |
| R17 | `assertNoDisconnectedSolids`' source word | `exact geometry` | `B-rep geometry` |
| R18 | `assertNoSolidInterference`'s reason | `one of the two solids in a candidate pair has no exact geometry, so the pair is compared through their meshes` | `one of the two solids in a candidate pair has no B-rep geometry, so the pair is compared through their meshes` |
| R19 | fusion's `needed_by` and reasons | `exact fusion {name}`; `fusing its exact children`; `writing its fused exact artifacts`; `faceted fusion {name}` | `B-rep fusion {name}`; `fusing its B-rep children`; `writing its fused B-rep artifacts`; `mesh fusion {name}` |
| R20 | a mesh fusion's admission and union failures | `faceted fusion {name} cannot admit child {child}: {engine} reported {fault}`; `faceted fusion {name} failed: {engine} reported {fault}` | `mesh fusion {name} cannot admit child {child}: {engine} reported {fault}`; `mesh fusion {name} failed: {engine} reported {fault}` |
| R21 | the leaves' `needed_by` and reasons (`brep_leaf`, `cadquery`, `step`, `build123d`) | `exact leaf {name}`; `its render result becomes exact geometry`; `its STEP product becomes exact geometry` | `B-rep leaf {name}`; `its render result becomes B-rep geometry`; `its STEP product becomes B-rep geometry` |
| R22 | the conversion hook's refusal | `{name} ({qualname}) rendered a {kind}, which its conversion hook shape_from_rendered cannot turn into exact geometry: {error}` | `{name} ({qualname}) rendered a {kind}, which its conversion hook shape_from_rendered cannot turn into B-rep geometry: {error}` |
| R23 | `shape()` on a node without B-rep geometry | `{name} does not expose exact geometry` | `{name} does not expose B-rep geometry` |
| R24 | `brep` read on an unassembled internal node | `{name} exactness is unavailable before its children are linked by assemble()` | `{name} cannot say whether it is a B-rep before its children are linked by assemble()` |
| R25 | the memos' and publication's `needed_by`/reason | `reading exact geometry`; `writing {path}` / `it is the exact {artifact} artifact` | `reading B-rep geometry`; `writing {path}` / `it is a B-rep node's {artifact} artifact` |
| R26 | the provider's admission | `The OCCT exact engine takes an OCP.TopoDS.TopoDS_Shape, or an object carrying one as .wrapped, not {type}` | `The OCCT B-rep engine takes an OCP.TopoDS.TopoDS_Shape, or an object carrying one as .wrapped, not {type}` |
| R27 | the provider's Booleans | `Exact {operation} failed for {a} and {b}: {error}`; `Exact common of {a} and {b} was empty, but its independent native-interior check failed: {error}`; `Exact common of {a} and {b} was empty despite a point strictly inside both native solids: {witness}. No overlap volume was inferred.` | `B-rep {operation} failed for {a} and {b}: {error}`; `B-rep common of {a} and {b} was empty, but its independent native-interior check failed: {error}`; `B-rep common of {a} and {b} was empty despite a point strictly inside both native solids: {witness}. No overlap volume was inferred.` |
| R28 | `machinome test` help | `--exact`: `Compare exact parts on the boundary-representation kernel (the default, and what SOLID_TEST_KERNEL=exact selects).`; `--faceted`: `... selected for a checkout by SOLID_TEST_KERNEL=faceted in its .env.`; `--volume-epsilon`: `Under --faceted, report ... The exact kernel refuses it.`; `--placement-quantum`: `... Accepted by both kernels; 0 restores the exact-bytes key.` | `--brep`: `Compare B-rep parts on the B-rep engine (the default, and what SOLID_TEST_ENGINE=brep selects).`; `--mesh`: `... selected for a checkout by SOLID_TEST_ENGINE=mesh in its .env.`; `--volume-epsilon`: `Under --mesh, report ... The B-rep engine refuses it.`; `--placement-quantum`: `... Accepted by both engines; 0 restores the exact-bytes key.` |
| R29 | the leaf contract's refusal (ADR-165) | wording unchanged; it names 2 as the version the core speaks | wording unchanged; it names 3 |
| R30 | `SOLID_TEST_KERNEL` set to a non-empty value (Decision 6), whatever the flags | (none: the variable is the one read) | `SOLID_TEST_KERNEL is not read: the run's engine is set by SOLID_TEST_ENGINE, 'brep' or 'mesh'; rename the variable where it is set (a checkout's .env)` |
| R31 | an explicit engine outside `ENGINES` (`resolve_comparison_policy(engine=...)`) | `unknown comparison kernel {kernel!r}` | `unknown comparison engine {engine!r}` |

The `ExtraUnavailable` refusals of the node modules (`machinome[cadquery]`,
`[build123d]`, `[step]`, `[molejo]`) and of the OpenSCAD family are unchanged.

### 14. The docs

Under `skills/write-the-manual/SKILL.md` (the workspace's), the pages a reader
is sent to: `docs/architecture.md` (72 occurrences: the engine package, the
two seams and providers, the leaf base, the capability, the test framework's
engines, `SOLID_TEST_ENGINE` and the run's engine (2314), the source map),
`docs/start/install.rst` (the extras `brep`,
`mesh`), `docs/howto/fast-tests.rst` (`--mesh`, `--brep`,
`SOLID_TEST_ENGINE=mesh` in `.env`, the run's engine where it says the
kernel, the run's line and note),
`docs/howto/backends.rst`, `docs/howto/fusion.rst`,
`docs/howto/imported-parts.rst`, `docs/howto/flexible-parts.rst`,
`docs/howto/markings.rst`, `docs/howto/sheet-parts.rst`,
`docs/reference/cli.rst` (the flags, and `SOLID_TEST_ENGINE` in the
environment table, 159 and 570), `docs/reference/api.rst` (the engine
package, `BrepLeafNode`, `brep`), `docs/reference/assertions.rst`,
`docs/concepts/node-tree.rst`, `docs/concepts/publishing.rst`,
`docs/start/first-machine.rst`, `docs/tutorial/01-part.rst`, `06-fit.rst`,
`09-clocked.rst`, `docs/why.rst`, `README.rst`, and
`docs/project/upgrading.rst` (the flags, the variable `SOLID_TEST_ENGINE`
and the refusal of `SOLID_TEST_KERNEL`, the extras, the moved names, the
verdict recompute, the mesh fusion rebuild, the `__pycache__` cleaning).
The changelog's Unreleased section gains this cycle's bullet, written in this
cycle (the pilot's ruling of 29 September 2026), and its earlier Unreleased
bullets that name the renamed addresses, extras and flags are revised to the
names 0.8 will ship (Open Question 5). The ADRs, `docs/releases/` and
`docs/performance-improvement.md` (a dated report) are history and keep their
words; the ADR index gains ADR-180 and the amended status lines, ADR-073's
among them (Open Question 2).

### 15. Proof, red first

Each red assertion and why it is red on faf1c80:

1. The gate (Decision 9): 30 modules, 548 occurrences offend.
2. `tests/test_engine_package.py`: `machinome.engine` imports and defines
   `brep_engine`, `require_brep_engine`, `BrepEngineUnavailable`,
   `BrepEngineIncompatible`, `BrepCommonInconsistency`,
   `BrepCommonVerificationError`, `BREP_CONTRACT == 2`, `BREP_PROVIDER ==
   'machinome.engine.brep'`, and the mesh seam's names with `MESH_CONTRACT ==
   1`, `MESH_PROVIDER == 'machinome.engine.mesh'`; importing it leaves neither
   provider, `OCP` nor `manifold3d` in `sys.modules`; after `brep_engine()` and
   `mesh_engine()` resolve, `machinome.engine.brep_engine` and
   `.mesh_engine` are still the functions and return the same providers; a
   directory on `sys.path` holding `machinome/engine/probe.py` with no
   `__init__.py` is importable as `machinome.engine.probe`, and one holding its
   own `machinome/__init__.py` and `machinome/engine/__init__.py` is not;
   `import machinome.exact_engine`, `machinome.mesh_engine`, `machinome.occt`,
   `machinome.manifold` each raise `ModuleNotFoundError`; the package holds no
   operation (`intersect_shapes`, `intersect_solids`). Red: no package, the
   former modules exist.
3. The three doors for each engine, with the finder helpers: importing
   `machinome.engine.brep` with `OCP` refused raises `ExtraUnavailable` with
   R5, `extra == 'brep'`; `brep_engine()` answers `None` and
   `require_brep_engine(...)` raises R1; building a stale B-rep fusion raises R1
   naming `B-rep fusion {name}` (the B-rep engine's command door is the point of
   use: no command needs it at its start); likewise `machinome.engine.mesh` with
   `manifold3d` refused raises R6, `mesh_engine()` answers `None`, and
   `machinome test --mesh` exits 1 with R3 naming `machinome test on the mesh
   engine` before building. Red: no such modules; today's texts name `occt`
   and `manifold`.
4. The metadata (`test_kernel_extras.py`): extras `brep` and `mesh` declared
   with today's ranges; `occt` and `manifold` absent; `cadquery`, `build123d`,
   `step`, `molejo` include `machinome[brep]`; none includes `mesh`; `all`
   names `brep` and `mesh`. Red: the extras are `occt` and `manifold`.
5. The leaf base and the capability (`test_leaf_capability_set.py`,
   `test_leaf_contract_version.py`): `machinome.node.brep_leaf.BrepLeafNode`
   exists, `SheetLeafNode`, `CadQueryNode`, `Build123dNode`, `StepNode`
   subclass it; `brep` answers `True` on a `CadQueryNode`, `False` on an
   `StlNode`, all-children on a `FusionNode`; no node class defines `exact`;
   `machinome.node.leaf.CONTRACT == 3`; `leaf_contract = 2` is refused naming 2
   and 3; `import machinome.node.exact_leaf` raises `ModuleNotFoundError`;
   R24 for an unassembled internal node. Red: `ExactLeafNode`, `exact`, 2.
6. The test framework (`test_manager_test.py`, the comparison-policy tests):
   `machinome.test.ENGINES == ('brep', 'mesh')` and `machinome.test` has no
   `KERNELS`; `ComparisonPolicy._fields` starts with `'engine'` and has no
   `kernel`; the default policy's engine is `'brep'`;
   `resolve_comparison_policy(engine='mesh')` gives a mesh policy and
   `resolve_comparison_policy(kernel='mesh')` raises `TypeError`;
   `--brep`/`--mesh` parse into `args.engine` and are mutually exclusive;
   `--faceted` and `--exact` are unrecognised (exit 2);
   `SOLID_TEST_ENGINE=mesh` selects the mesh engine;
   `SOLID_TEST_ENGINE=faceted` and `=exact` are refused with R7; the former
   variable, `SOLID_TEST_KERNEL` set to `mesh`, to `faceted` or to `brep`,
   is refused with R30, with no flag and with `--brep` or `--mesh` given, and
   `machinome test` exits 1 with R30 before building; an explicit
   `engine='fast'` is refused with R31; R8 under `--brep --volume-epsilon
   0.5`; R11 and R12 under `--mesh`; `IntersectionStats` has `brep` and no
   `exact`. Red: today's flags, values and names.
7. The verdict paths (`test_verdict_store.py`): a B-rep comparison's in-process
   key carries `'brep'` and a mesh comparison's `'mesh'`; a record kept with
   `brep=True` reads back with the bit `_BREP`; a store written by the
   former key words is not served after the change (a stub record under
   `'exact'` misses). Red: the words are `'exact'`/`'faceted'`.
8. The recipe identities (`test_backend_neutral_materialization.py`): a B-rep
   fusion's `geometry_recipe == 'brep-fusion-v1'`; a mesh fusion's starts with
   `'mesh-fusion-v1:'` and its STL's recorded recipe equals it; a mesh fusion
   whose STL records the former recipe is not current and rebuilds to the same
   bytes; a B-rep fusion whose artifacts are current stays current. Red: the
   former identities.
9. The memos and publication: `machinome.brep_cache` and
   `machinome.brep_artifacts` import and `machinome.exact_cache`,
   `machinome.exact_artifacts` do not. Red: the former modules exist.
10. Vet (`test_vet_universe.py`): the universe denies `machinome.brep_cache`,
    `machinome.brep_artifacts`, `machinome.engine.brep.read_brep`,
    `.write_brep`, `.write_stl`, and passes `machinome.engine`,
    `machinome.engine.brep.intersect_shapes`. Red: the denylist names the
    former addresses.

### 16. Empirical validation (the orchestrator runs every leg)

Run against the bench after the suite, one project at a time (virtiofs),
before (the line at faf1c80) and after, in fresh build directories, with the
orchestrator's verdict recorder (each verdict's key path word, emptiness,
volume as `float.hex`, the engine's identity):

- **Deep, `Locks/Pin_tumbler_lock`** (OpenSCAD-authored parts, a flexible
  spring, mesh comparisons): `machinome test --faceted` before, `machinome
  test --mesh` after, `--no-verdict-store` both: 24 tests with the same
  outcomes; 2573 verdicts, identical in order, emptiness, volume and engine
  identity, the path word `faceted` before and `mesh` after; the run's line
  and summary note per R11 and R12. Then `machinome test --mesh` twice with
  the store on: the first run's store serves nothing kept before the change
  (the recompute), the second serves every verdict the first kept.
- **Deep, `3D-Printers/Prusa3-vanilla`** (the heaviest mesh user): 16
  passed, 3 failed (pre-existing) before and after, its 15935 verdicts
  identical but for the path word.
- **Deep, OpenAstroMount** (CadQuery and STEP only, every part a B-rep):
  `machinome test --exact` before, `machinome test --brep` after: the same
  outcomes (8/9, the known B-rep common wart), every verdict identical but for
  the path word `exact` → `brep`; with the mesh engine made unfindable by
  `tests/mesh_engine_absent.py` (the provider and `manifold3d`), before and
  after reach the same outcomes and the after-run asks for
  `machinome.engine.mesh` exactly where the before-run asked for
  `machinome.manifold.engine`; `machinome build` after the change rebuilds no
  artifact (90 STL, 90 BREP: same inodes and records).

- **Deep, one project with a mesh `FusionNode`** (the orchestrator's grep
  picks it; failing one in the universe, `tests/mesh_engine_golden.py`'s
  `Fused` fixture is the leg): after the change the fused STL rebuilds once,
  byte-identical (SHA-256) to the before-build's, its recorded recipe now
  `mesh-fusion-v1:<same digest>`; a second build reuses it. A B-rep fusion in
  the same or another project is not rebuilt.
- **The goldens**, each in a fresh process: `leaf_contract_golden.py
  --check`, `scad_presentation_golden.py --check`,
  `expression_type_golden.py --check`, `brep_engine_golden.py --check`,
  `mesh_engine_golden.py --check` (with `BREP_MESH_EXPECTED`): no difference.
- **The three doors for each engine** in throwaway processes with the finder
  helpers (Decision 15, item 3), and a stub provider portion
  (`machinome/engine/probe.py` in a temporary directory on `PYTHONPATH`)
  importable as `machinome.engine.probe`.
- **Shallow, the universe**: `scripts/load-projects` with the eight earlier
  tables plus this change's `moved-names.toml` (copied as
  `scripts/load-projects.d/brep-mesh.toml`), 300 s timeout. Expected: no new
  unexpected row (2 unexpected and pre-existing); the rows that were `ok` and
  now fail are `expected`, each explained by a row of `brep-mesh.toml` (an
  import of `machinome.occt.engine`, `machinome.exact_engine`,
  `machinome.node.exact_leaf` or a sibling), their number equal to the
  orchestrator's grep count; 6 no-model.
- **Greps the orchestrator runs over `projects/`** (the proposer may not):
  `ExactLeafNode`, `exact_leaf`, `machinome.occt`, `machinome.manifold`,
  `exact_engine`, `mesh_engine`, `exact_cache`, `exact_artifacts`,
  `ExactCommon`, `IntersectionStats`, `.exact\b` attribute reads, `--faceted`,
  `--exact`, `SOLID_TEST_KERNEL` in tracked files and in untracked `.env`
  files, `machinome[occt]`, `machinome[manifold]` and `"occt"`/`"manifold"` in
  manifests, `exact-fusion`/`faceted-fusion`; and machinome-freecad's
  validation branch (its `leaf_contract = 1` under `ExactLeafNode` is refused
  already; after this change its import of `machinome.node.exact_leaf` fails
  first).


### 17. The rename table

Every name of the split, today and tomorrow. The messages are Decision 13's
rows; the test modules Decision 12's; `moved-names.toml` holds the importable
rows in the sweep's format.

| kind | today | tomorrow |
|---|---|---|
| package | `machinome.occt` | (removed; the provider is a module of `machinome.engine`) |
| package | `machinome.manifold` | (removed; likewise) |
| package | — | `machinome.engine` (the two seams; path extended with portions) |
| module | `machinome.exact_engine` | `machinome.engine` (`__init__`) |
| module | `machinome.mesh_engine` | `machinome.engine` (`__init__`) |
| module | `machinome.occt.engine` | `machinome.engine.brep` |
| module | `machinome.manifold.engine` | `machinome.engine.mesh` |
| module | `machinome.exact_cache` | `machinome.brep_cache` |
| module | `machinome.exact_artifacts` | `machinome.brep_artifacts` |
| module | `machinome.node.exact_leaf` | `machinome.node.brep_leaf` |
| function | `exact_engine()` | `machinome.engine.brep_engine()` |
| function | `require_exact_engine(needed_by, reason)` | `machinome.engine.require_brep_engine(needed_by, reason)` |
| function | `machinome.mesh_engine.mesh_engine()`, `.require_mesh_engine()` | `machinome.engine.mesh_engine()`, `.require_mesh_engine()` |
| function (private) | `exact_engine._absent`, `mesh_engine._absent` | `machinome.engine._brep_absent`, `._mesh_absent` |
| class | `ExactEngineUnavailable`, `ExactEngineIncompatible` | `BrepEngineUnavailable`, `BrepEngineIncompatible` |
| class | `ExactCommonInconsistency`, `ExactCommonVerificationError` | `BrepCommonInconsistency`, `BrepCommonVerificationError` |
| class | `MeshEngineUnavailable`, `MeshEngineIncompatible` | the same names in `machinome.engine` |
| Protocol | `ExactCurrency`, `ExactComposition`, `ExactComparison`, `ExactEngine` | `BrepCurrency`, `BrepComposition`, `BrepComparison`, `BrepEngine` |
| Protocol | `MeshSolids`, `MeshComposition`, `MeshComparison`, `MeshIdentity`, `MeshEngine` | the same names in `machinome.engine` |
| alias | `ExactShape`, `MeshSolid` | `BrepShape`, `MeshSolid` |
| constant | `machinome.exact_engine.CONTRACT = 1`, `.PROVIDER` | `machinome.engine.BREP_CONTRACT = 2`, `.BREP_PROVIDER = 'machinome.engine.brep'` |
| constant | `machinome.mesh_engine.CONTRACT = 1`, `.PROVIDER` | `machinome.engine.MESH_CONTRACT = 1`, `.MESH_PROVIDER = 'machinome.engine.mesh'` |
| constant | `machinome.occt.engine.CONTRACT = 1` | `machinome.engine.brep.CONTRACT = 2` |
| constant | `machinome.manifold.engine.CONTRACT = 1` | `machinome.engine.mesh.CONTRACT = 1` |
| constant | `machinome.node.leaf.CONTRACT = 2` | `3` |
| class | `ExactLeafNode` | `BrepLeafNode` |
| member | `exact` (property: node base, `InternalNode`, `ExactLeafNode`, `MolejoNode`; declared in `LeafNode`, `FlexibleNode`) | `brep` |
| member (private) | `FlexibleNode._exact_binding`, `_exact_result`, `_exact_identity`, `_exact_solid`, `_exact_state_identity`, `_faceted_cache_snapshot` | `_brep_binding`, `_brep_result`, `_brep_identity`, `_brep_solid`, `_brep_state_identity`, `_mesh_cache_snapshot` |
| member (private) | `FusionNode._generate_faceted_stl` | `_generate_mesh_stl` |
| field | `machinome.test.IntersectionStats.exact` | `.brep` |
| value | `KERNELS = ('exact', 'faceted')`, `ComparisonPolicy.kernel`, the default `'exact'` | `ENGINES = ('brep', 'mesh')`, `ComparisonPolicy.engine`, default `'brep'` |
| constant | `machinome.test.KERNELS` | `machinome.test.ENGINES` |
| member | `machinome.test.ComparisonPolicy.kernel` (the namedtuple's first field) | `.engine` |
| parameter | `resolve_comparison_policy(kernel=None, ...)` | `resolve_comparison_policy(engine=None, ...)` |
| argument | `machinome test`'s mutually exclusive group `kernel`, `dest='kernel'`, `args.kernel`, `self.policy.kernel`, `policy.kernel` (`manager/test.py:64-71, 102, 110, 329`) | the group `engine`, `dest='engine'`, `args.engine`, `self.policy.engine`, `policy.engine` |
| path word | the verdict paths `'exact'`, `'faceted'` (`_verdict_key`, `_record_key`, `_persistent_identity`, `_engine_identity`) | `'brep'`, `'mesh'` |
| function (private) | `machinome.test._exact_engine`, `_routes_exact`, `_exact_verdict`, `_faceted_verdict`, `_exact_identity` | `_brep_engine`, `_routes_brep`, `_brep_verdict`, `_mesh_verdict`, `_brep_identity` |
| constant (private) | `machinome.test._EXACT_NEEDED_BY`, `_EXACT_REASON`, `_FACETED_NEEDED_BY`, `_FACETED_REASON` | `_BREP_NEEDED_BY`, `_BREP_REASON`, `_MESH_NEEDED_BY`, `_MESH_REASON` |
| parameter | `_place_solid(..., faceted_identity)` | `mesh_identity` |
| constant (private) | `machinome._verdict_store._EXACT = 2`; `record(..., exact)` | `_BREP = 2`; `record(..., brep)` |
| flag | `machinome test --exact`, `--faceted` | `--brep`, `--mesh` |
| environment variable | `SOLID_TEST_KERNEL` | `SOLID_TEST_ENGINE` (the former, when set, refused with R30) |
| environment value | `SOLID_TEST_KERNEL=exact`, `=faceted` | `SOLID_TEST_ENGINE=brep`, `=mesh` |
| extra | `occt`, `manifold` (`machinome[occt]`, `machinome[manifold]`) | `brep`, `mesh` |
| identity | `exact-fusion-occt-v1` | `brep-fusion-v1` |
| identity | `faceted-fusion-manifold-v1:<sha256>` | `mesh-fusion-v1:<sha256>` |
| spec | `exact-engine-dependency`, `exact-geometry`, `occt-engine`, `manifold-engine` | `brep-engine-dependency`, `brep-geometry`, `brep-engine`, `mesh-engine` |
| vet denylist | `machinome.exact_cache`, `machinome.exact_artifacts`, `machinome.occt.engine.read_brep`, `.write_brep`, `.write_stl` | `machinome.brep_cache`, `machinome.brep_artifacts`, `machinome.engine.brep.read_brep`, `.write_brep`, `.write_stl` |
| test helper variable | `EXACT_ENGINE_ABSENT`, `EXACT_ENGINE_ABSENT_LOG` | `BREP_ENGINE_ABSENT`, `BREP_ENGINE_ABSENT_LOG` |
| message | Decision 13, R1 to R31 | |
| prose | "the exact engine", "the exact kernel", "the boundary-representation kernel" (a run's), "exact geometry", "an exact leaf/node/fusion/part/solid", "faceted geometry", "a faceted leaf/node/fusion/run", "the faceted kernel", "exactness", "non-exact" | "the B-rep engine", "the B-rep engine", "the B-rep engine", "B-rep geometry", "a B-rep leaf/...", "mesh geometry", "a mesh leaf/...", "the mesh engine", "`brep`", "mesh" |
| prose | "the run's kernel", "the comparison kernel", "both kernels" and "either kernel" (a run's two choices), "a kernel flag", "the kernel line" | "the run's engine", "the comparison engine", "both engines", "either engine", "an engine flag", "the engine line" |

Unchanged, and stated: `.brep` and `.stl`; `brep_file`; the verdict store's
artifact kinds `'brep'` and `'stl'`; `OCP`, `cadquery-ocp`, `manifold3d`,
`molejo[brep]`; `kernel` in its library sense, `machinome._verdict_store.KERNELS`
among it (Non-Goals); every ordinary `exact` (Decision 1).

## SOLID review

The pilot's standing requirement; where the design follows each principle and
where it bends.

- **Single responsibility.** The engine package's `__init__` does one thing:
  declare the two contracts and resolve their providers. Each provider does one
  representation's geometry; the memos and publication stay core modules over
  opaque handles; the test framework orders and asks. The renaming removes a
  responsibility the names had taken on: a name that said "OCCT" or
  "manifold" in the core (a recipe identity, an extra, a seam's provider
  address) described which library a provider wraps today, a fact that is the
  provider's alone; the names now say the role.
- **Open/closed.** A second provider of a role is a package installing
  `machinome/engine/mesh.py` (or `brep.py`) as a portion: the core's package
  path admits it with no edit (Decision 2). A new node type built on a B-rep
  subclasses `BrepLeafNode` and declares nothing about a technology. **Bend,
  by the lock:** one engine per role at a time, so two mesh engines cannot
  coexist; and the mesh fusion's recipe identity does not name the provider,
  so a second mesh engine must make its identity part of the recipe when it
  arrives (Risks).
- **Liskov.** Any provider implementing a contract substitutes for another;
  the contract integers make a mismatch a refusal, not a misbehaviour. Every
  B-rep leaf answers `brep` true and `shape()` with the base's meaning, a
  flexible leaf and a fusion included, so the core reads the flag directly
  (ADR-178) and never asks which class it holds.
- **Interface segregation.** The Protocols stay split by consumer
  (`BrepCurrency`, `BrepComposition`, `BrepComparison`; `MeshSolids`,
  `MeshComposition`, `MeshComparison`, `MeshIdentity`). The engine package
  exposes seams, not operations: a caller that wants an operation resolves a
  provider, and a project calling B-rep operations directly imports
  `machinome.engine.brep`, the one path (exact-engine Decision 6).
- **Dependency inversion.** The core depends on its seams' abstractions (the
  Protocols, the contract integers, the error types); no core module imports a
  provider but through its seam, which the gate (W4) and
  `test_core_kernel_free.py` hold. The B-rep provider depends on the core for
  its error types and the extras check, the direction a cut package keeps
  (its pin on the core). **Bend:** a project calling
  `machinome.engine.brep.intersect_shapes` reaches the provider without the
  seam's contract check, as it reached `machinome.occt.engine` before; inside
  one distribution the two cannot disagree, and at the cut the provider
  package's pin on the core guards it (ADR-161).

## ADRs

Extracted after implementation, under the framework-change skill:

- **ADR-180** (NODE), "The engines are named for the representation each
  consumes: `brep` and `mesh`": the lock's words and how the ordinary `exact`
  is told apart (the gate); the engine package `machinome.engine`, its two
  seams in the `__init__` with their names and why they are not `brep()` and
  `mesh()` (the probe), its path admitting portions; the providers
  `machinome.engine.brep` (contract 2) and `machinome.engine.mesh` (contract
  1); `BrepLeafNode` at `machinome.node.brep_leaf`, the capability `brep`,
  leaf contract 3; `machinome.brep_cache`, `machinome.brep_artifacts`; the
  run values, flags and messages; the recipe identities and what rebuilds; the
  verdict recompute without migration; the extras `brep` and `mesh`; the
  run's engine, `SOLID_TEST_ENGINE`, `ComparisonPolicy.engine` and
  `ENGINES`, the former variable refused. Amends ADR-073 (the run's
  comparison kernel is its comparison engine), ADR-160 (the provider's
  address; the currency unchanged), ADR-161 (the
  seam's address and names), ADR-162 (the constants named per role in one
  module), ADR-163 (the leaf base's name and module), ADR-165 (version 3),
  ADR-167 (the extras), ADR-176 (the mesh provider's address and extra) and
  ADR-178 (the member `exact` is `brep`). Cites ADR-047, ADR-052,
  ADR-090, ADR-156, ADR-169 and ADR-177.

One ADR, as the brief asks: the names, the package and the contracts are one
decision, the lock's, and splitting them would scatter it. ADR-160 stays in
`docs/adrs/OCCT/` (Open Question 6).

## Moved names

`moved-names.toml` in this change, in the earlier cycles' format (`cycle`,
`date`, `[[moved]]` rows with `name`, `to` and optional `also`), holds 103
rows: 93 importable names and members (the four removed modules and
packages, the providers and their operations, the seams' names, the memos and
publication, the leaf base and the capability, the private names of the test
framework and the verdict store, `machinome.test.KERNELS` and
`ComparisonPolicy.kernel`) and ten rows marked `informational = true`
(the two flags, the variable `SOLID_TEST_KERNEL` and its two former values,
the run's values, the two extras, the two recipe identities), which no load
error can name and the root cleanup's rewrite applies to command lines,
`.env` files and manifests.
`scripts/load-projects` reads only `name`, `to` and `also`; the extra key is
ignored.

## Risks / Trade-offs

- [A project imports a moved name] → its load fails with Python's own
  `ModuleNotFoundError` or "cannot import name", which the sweep explains by a
  row of `brep-mesh.toml`; the root cleanup's single pass rewrites it; until
  then the line is unreleased (`main` holds 0.7.1).
- [A project's `.env` sets `SOLID_TEST_KERNEL`, to `faceted` or any value]
  → the run refuses at its start with R30, exit 1, naming `SOLID_TEST_ENGINE`
  and both values, whatever flag it is given (Decision 6); `.env` files are
  untracked, so the root cleanup's rewrite may not see them: the
  orchestrator's grep lists them and the upgrading page says so. A shell or
  CI job that exports the former variable is refused the same way.
- [A checkout keeps `machinome/occt/__pycache__` or
  `machinome/manifold/__pycache__`] → Python imports the deleted package as an
  empty namespace package and the "former addresses are gone" test fails;
  `git clean -fdX machinome/occt machinome/manifold` once in every checkout that
  pulls the change (task 3.2; the primary checkout when the line merges).
- [The studio's `machinome_test` tool passes `--faceted`/`--exact`
  (`machinome-studio/floor/mcp_server.py:978-985`)] → argparse refuses them
  (exit 2) against a framework with this change; the studio runs against the
  workspace venv's primary checkout, which takes the change only when the line
  merges into `main`: a paired studio change then (Open Question 7).
- [The gate misses the split's predicates] → Decision 9's residual review,
  recorded in `evidence.md`.
- [The gate's ordinary tables go stale] → each entry is by module and by
  phrase; a new ordinary use is a reviewed edit of the test, as the SCAD gate's
  zones are.
- [A cold verdict store on a large project] → one cold run per project (the
  store's own example: 1348.9 s cold where the warm memo answered in 18.35 s,
  `_verdict_store.py:8-10`); ADR-156 already accepts it at every framework
  edit, which this change also is.
- [A second mesh engine under the same recipe identity] → a fused STL built by
  one mesh engine would be reused under another; today there is one, and the
  recipe never named its version either; the second engine's arrival makes its
  identity part of the recipe.
- [The delta specs keep 74 scenario titles with the former words] → the
  archive task's table, then `openspec validate --specs --strict`.
- [machinome-freecad's validation branch is refused] → intended (ADR-165);
  its retarget declares 3 and subclasses `BrepLeafNode`.
- [A docs test pins a former text] → the suite names it; the page changes with
  the code (task 9.1).

## Migration Plan

- **Projects** (the root cleanup's script, with this change's table among the
  others): imports of the moved names; `--faceted` → `--mesh` and `--exact`
  → `--brep` (three files of 3DPrintedClocks, per the plan); `.env` lines
  `SOLID_TEST_KERNEL=faceted|exact` → `SOLID_TEST_ENGINE=mesh|brep` (the
  variable and its value); manifests'
  `machinome[occt]` → `machinome[brep]` and `machinome[manifold]` →
  `machinome[mesh]`; `ExactLeafNode` subclasses → `BrepLeafNode`, their
  `leaf_contract` → 3 where declared. The Curta's own `faceted` parameter
  names stay.
- **Persisted state, once, automatically**: every verdict store recomputes on
  its next run (Decision 7); every mesh fusion's STL rebuilds on its next
  build, byte-identical (Decision 8). Nothing to run by hand.
- **Checkouts**: `git clean -fdX machinome/occt machinome/manifold` once.
- **Outside the framework** (findings for the orchestrator, not this cycle's
  edits): machinome-studio's `machinome_test` tool and its test
  (`tests/test_scoped_tools.py:307-313`), its `machinome-api` and `machinome`
  skills (`--faceted`, `--exact`, `SOLID_TEST_KERNEL`, which becomes
  `SOLID_TEST_ENGINE`); the workspace's
  `skills/simulate-project/SKILL.md:232`; `scripts/load-projects.d/` gains
  `brep-mesh.toml`; machinome-freecad's retarget.
- **Rollback**: revert the implementation commit; the stores recompute and
  the mesh fusions rebuild once more.

## Open Questions

1. **The seams' names.** The brief suggests `brep()`, `require_brep()`,
   `mesh()`, `require_mesh()`; the probe of "Context" shows a seam function
   named like its provider module is replaced by the module at its first
   resolution. Recommendation: `brep_engine()`, `require_brep_engine()`,
   `mesh_engine()`, `require_mesh_engine()` (Decision 2), the mesh ones being
   today's names.
2. **The run-policy word `kernel`** (`ComparisonPolicy.kernel`, `KERNELS`,
   `SOLID_TEST_KERNEL`, the `kernel` argument). **Resolved by the pilot at
   ratification (4 October 2026): rename now**, against the recommendation
   to leave it. Reason: in this codebase "kernel" means the third-party
   library an engine wraps (OCCT, manifold3d; the `kernel-extras`
   capability), and after the rename a run's choice, `brep` or `mesh`, is an
   engine. So `SOLID_TEST_KERNEL` is `SOLID_TEST_ENGINE`, the former variable
   refused when set (Decision 6, R30); `ComparisonPolicy.kernel` is
   `.engine`; `KERNELS` is `ENGINES`; the `kernel` argument of
   `resolve_comparison_policy` and of `manager/test.py` is `engine`; every
   message for the run says "the B-rep engine" / "the mesh engine"
   (Decision 13). The gate is not extended to the word (Decision 9), which
   keeps its library sense in `kernel-extras`, `extras.py`, the node modules
   and the providers. ADR-180 amends ADR-073.
3. **`BREP_CONTRACT = 2`.** Recommendation: 2, because the contract names the
   error types it renames (Decision 3); the mesh contract stays 1.
4. **The gate's W4 zones** admit `occt` and `manifold` in the four OCCT-built
   node modules (`cadquery`, `build123d`, `step`, `molejo`), which describe
   their own kernel's behaviour (OCCT's STEP reader, OCCT's mesher), and
   nowhere else in the core: `core/processes.py`'s comment on OCCT's OpenMP
   workers and `manager/import_step.py`'s on OCCT's naming of a root are
   reworded ("the B-rep engine's kernel", "the STEP reader").
   Recommendation: as designed; the alternative, no zone but the providers,
   would reword true statements in node packages about their own kernel.
5. **The changelog's earlier Unreleased bullets** (`docs/project/changelog.rst`,
   Unreleased, lines 16-220) name `machinome.occt.engine`,
   `machinome.exact_engine`, `ExactLeafNode`, `machinome[occt]`,
   `machinome[manifold]` and `--faceted`, none of which 0.8 will ship.
   Recommendation: revise those bullets in place to the shipped names and add
   this cycle's bullet; nothing in Unreleased has been released, and the
   section is read as what the release changes.
6. **ADR-160's directory `docs/adrs/OCCT/`.** Recommendation: keep it (the ADR
   index's rule: historical entries retain the names they used); the cut
   decides the engine package's ADR directory.
7. **The studio's `machinome_test` tool.** Recommendation: a paired studio
   change (accept `brep`/`mesh`, pass `--brep`/`--mesh`, its skills) when the
   line merges into `main`, recorded now as a campaign follow-up; before the
   merge, the studio's framework is the primary checkout and nothing breaks.
8. **The mesh run's line (R11).** "verdicts are at tessellation precision, not
   the B-rep engine's" keeps today's caution without the word.
   Recommendation: as written; the alternative drops the clause.

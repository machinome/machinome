## Context

This is item 1 of the lean-core campaign plan (`workflow/ongoing/lean-core.md`,
"What it takes"), cut second, after the `exact-engine` cycle
(`openspec/changes/archive/2026-10-03-exact-engine/`) because the contract
names the engine's currency. Three items of that cycle's "Deferred" list are
this cycle's: the declared `LeafNode`/`ExactLeafNode` extension contract, the
public form of `shape_from_rendered`, and the public replacement for `_evict`.
The plan's "Import paths", "machinome, the core" and "Empirical validation,
per cycle" govern it. Facts below were read in the bench at 5c163ea on
3 October 2026 unless marked *inferred*.

### The originating evidence: machinome-freecad's exact leaf

`machinome-freecad/machinome_freecad/adapter.py` (main, b5b6233, read-only)
builds one exact leaf class per FreeCAD product in `_leaf_class`:
`class _Solid(_NativeCurrency, ExactLeafNode)`. What it reaches:

1. **The cast.** `namespace = 'cadquery'`; `render()` reads the transferred
   BREP into a bare `TopoDS_Shape` with `BRepTools.Read_s`, then
   `import cadquery as cq` only to return `cq.Shape.cast(shape)` and call
   `.Solids()` and `.isValid()` on it. Since ADR-160 the engine admits the bare
   shape (`occt/engine.py`, `as_shape`), and `isValid` is
   `BRepCheck_Analyzer(self.wrapped).IsValid()` in cadquery 2.7.0 (read in the
   venv), so the cast buys nothing.
2. **The private eviction, inside a `materialize()` override.** The override
   (a) checks the native source generation, (b) copies the `.brep`, `.stl`
   and both source records (`currency.sidecar`) to a temporary directory,
   (c) calls the base's `materialize`, (d) checks the generation again, and on
   `SourceChanged` restores the copies in place with `shutil.copy2` (or
   unlinks new files), calls `machinome.exact._evict(self.brep_file)` and
   re-raises; (e) when `_up_to_date(brep_file)` was false before, calls
   `_evict` again, with the comment "core exact-shape cache keys only
   path+mtime; native recipe changes can replace a BREP while source mtime
   stays equal". `machinome.exact` was removed by the first cycle; the cache is
   now `machinome.exact_cache`, still keyed `(path, os.path.getmtime)`, and
   `_evict` is still private. Its reasons, then: the native recipe can change
   the BREP with no tracked file changing (reason for (e)); and "a failed
   native generation must not leave new certified outputs" (reason for (a),
   (b), (d)), pinned by `tests/test_freshness.py`
   `test_publication_source_race_publishes_no_artifact`, which asserts the
   four files' bytes unchanged after a source mutation injected inside
   `currency.publish`.
3. **The currency overrides.** The `_NativeCurrency` mixin, on the leaf and on
   the adapter's `AssemblyNode` carriers, overrides the private
   `_tracked_fingerprint` and `_tracked_digest` to call
   `_check_native_generation()` and return
   `sha256(str(found) + self._native_recipe)`.
4. **The release pin.** `FreeCADAssemblyNode.__init__` refuses unless
   `importlib.metadata.version('machinome') == '0.7.1'`, and `pyproject.toml`
   pins `machinome==0.7.1`. The bench's `pyproject.toml` and `__version__`
   still say 0.7.1, so against this campaign line the refusal does not fire
   while `machinome.exact` is gone: a release number does not see a contract
   change.

Its carriers also call `AssemblyNode._link_children` and
`source_generation.track_sources`; those are assembly-side and outside a leaf
contract (Deferred).

### The empirical shape: the nine core leaves

What each core leaf overrides, and what it reaches that a package could not,
read from `machinome/node/adapters/*.py`, `sheet_leaf.py` and `flexible.py`.
Rows marked † leave the core at the cut (plan, "Import paths").

| leaf | base | overrides | private or internal reach today |
|---|---|---|---|
| `StlNode` | `LeafNode` | `__init__` (sets `stl_source` before `super()`), `get_source_file`, `render` (returns self), `materialize`, `as_scad`, `namespace = None` | `_ExternalWrapperIdentity`; `currency.publish` and its own stamping in `_write_binary_stl`; `self._up_to_date` |
| `Solid2Node` | `LeafNode` | `namespace = 'solid2'`, `as_scad`, `materialize` (`self.model = rendered; self.generate_scad()`), `as_number` | none (`model`, `generate_scad`, `require_openscad` are public) |
| `OpenScadNode` | `LeafNode` | `__init__`, `get_source_file`, `render`, `as_scad`, `materialize`, `scad_code` | `_ExternalWrapperIdentity`; `_model_for_own_scad()` in `scad_code`; `coherent_read` |
| `JScadNode` | `LeafNode` | `__init__`, `get_source_file`, `render`, `materialize`, `as_scad` | `_ExternalWrapperIdentity`; `currency.publish`; `current_phase().checkpoint`; `self._up_to_date` |
| `CadQueryNode` † | `ExactLeafNode` | `namespace = 'cadquery.cq'`, `shape_from_rendered`, metaclass `CheckCQEditor(NodeMeta)` | none (`require_exact_engine` is the seam's public function) |
| `Build123dNode` † | `ExactLeafNode` | `namespace = 'build123d'`, `shape_from_rendered`, `validate` (calls super) | none |
| `Build123dSheetNode` † | `SheetLeafNode` | `namespace`, `profile`, `_profile_faces`, `_lies_on_xy_plane`, `_extrude`, `_write_dxf` | four private hooks; `exact_artifacts._atomic_export` |
| `StepNode` † | `ExactLeafNode` | `__init__`, `get_source_file`, `render`, `shape_from_rendered`, `color` property, `namespace = 'cadquery.cq'` | `_ExternalWrapperIdentity`; `consumed_source`; `workplane_shape` from the cadquery adapter (a cross-package reach at the cut) |
| `MolejoNode` † | `FlexibleNode` | `namespace = 'molejo'`, `tech`, `exact`, `_shape_parameters`, `_shape_spec`, `_snapshot_mesh`, `_snapshot_stl`, `_snapshot_shape` | five private hooks |

Every row's overrides are the members a leaf of that kind must be able to
write; every entry in the last column of a † row, and every reach of the
FreeCAD leaf, is a private a package would import across a package boundary.
No project under `projects/` subclasses a leaf base directly or overrides any
of the hooks above (grep, 3 October 2026), and none uses `_up_to_date`,
`_tracked_digest`, `_tracked_fingerprint` or `_artifact_recipe`.

## Goals / Non-Goals

**Goals:**

- `LeafNode`, `ExactLeafNode`, `SheetLeafNode` and `FlexibleNode` are declared,
  specified, documented extension points at one path each, and a node package
  written against them reaches no private of the core.
- No subclass ever needs to evict a core cache: the loaded-shape cache keys on
  the artifact's observation.
- The contract is versioned, and a package's declaration is checked when its
  class is created.
- The FreeCAD adapter, migrated by hand on a never-merged branch, runs its
  suite against this bench with no cadquery, no `_evict` and no private
  currency override.
- No core leaf changes behaviour, artifact bytes, source records or identity.

**Non-Goals:**

- No class moves; no node package is cut (items 4 and 5 of the plan).
- No assembly extension contract (Deferred).
- No transactional multi-artifact publication with rollback (Deferred).
- No change to `vet`: a project's contract is unchanged.
- No new capability that no leaf uses today.

## Decisions

### 1. Four bases, not two

The plan's item 1 names `LeafNode` and `ExactLeafNode`. The evidence names
four: `Build123dSheetNode` and `MolejoNode` leave the core at the cut
(machinome-node-build123d, machinome-node-molejo, both settled by the pilot
on 2 October 2026) and subclass `SheetLeafNode` and `FlexibleNode` through
underscore hooks. Declaring only two bases would leave the cut to move four
private hooks and five private hooks across package boundaries, or to design
two contracts inside a move. The two specialised bases are therefore declared
here, by the same rule: what their core subclasses override becomes public.

Rejected: declare only `LeafNode` and `ExactLeafNode` and defer the sheet and
flexible hooks to the cut (the cut would then carry contract design and the
renames inside a code move, and machinome-node-molejo would ship against
private hooks if it were cut first). Put to the pilot with the proposal and
settled on 3 October 2026: four bases.

### 2. The contract, member by member

Declared, by base (the `leaf-contract` spec states each as behaviour):

| member | where | a subclass | the core |
|---|---|---|---|
| `render()` | every base | implements (not on a sheet leaf) | calls once per preparation |
| `validate(rendered)` | `LeafNode` | may extend, calling super | list/None and namespace checks |
| `namespace` | `LeafNode` | may declare a module prefix | checks it at validation |
| `as_scad(rendered)` | `LeafNode` | implements for a SCAD-presented faceted leaf | writes the SCAD; OpenSCAD makes the STL |
| `materialize(rendered)` | every base | implements (faceted, self-producing) or extends calling super | calls it when an artifact is stale |
| `publish_artifact(path, write)` | `LeafNode` | calls to write any artifact of its own | checks currency, stamps, records, replaces atomically |
| `get_source_file()`, `files`, `source_recipe` | `AbstractBaseNode` (inherited) | override / add to / declare | derives stamp, digest, fingerprint |
| `artifact_import(local_path)`, `local_stl`, `basepath`, `scad_file`, `stl_file`, `brep_file`, `model`, `generate_scad()` | inherited | read or call | owns them |
| `shape_from_rendered(rendered)` | `ExactLeafNode` | may override, a rewrap only | calls it where a stale artifact is written or a stale `shape()` read |
| `linear_deflection`, `angular_deflection` | `ExactLeafNode` | may declare | validates at export |
| `exact`, `shape()` | `ExactLeafNode` | neither | true; reloads current `.brep` |
| `profile()`, `profile_faces`, `lies_on_xy_plane`, `extrude`, `write_dxf(face, path)`, `thickness`, `validated_profile()` | `SheetLeafNode` | implements the first five, declares `thickness` | owns `render`, the rules, the DXF publication |
| `tech`, `shape_parameters`, `shape_spec`, `snapshot_mesh`, `snapshot_stl`, `snapshot_shape`, `exact` | `FlexibleNode` | declares / implements / may declare true | owns rigidity, the port surface, snapshots, the document |
| `leaf_contract` | any subclass | may declare | checks it at class creation |
| `NodeMeta` | `machinome.node.declarative` | derives a metaclass from it | — |
| `ExternalSourceIdentity`, `require_source_file`, `source_closure` | `machinome.node.sources` | mixes in / calls | — |
| `consumed_source`, `coherent_read`, `SourceChanged` | `machinome.source_generation` | calls / raises | — |

Not overridable: `assemble`, `shape` on an exact leaf, `render` on a sheet
leaf, `mtime_ns`, `mtime`, `source_digest`, `source_fingerprint`, `uniq_id`,
`children`, `time`, and every underscore member.

The two source-generation helpers and `SourceChanged` are declared for leaves
although `vet` denies `machinome.source_generation` to a project: the leaf
contract and the project contract have different audiences, and a leaf that
reads a foreign file (`StepNode`'s document cache, `OpenScadNode`'s source
text) must tie the read to the source generation. `JScadNode`'s
`current_phase().checkpoint` stays core-internal (Decision 5).

Rejected: declare the contract as `typing.Protocol` classes beside the bases,
as the engine's is. A leaf is a subclass, not a provider object: inheritance
already gives the defaults, and a Protocol would be a second listing of the
same members to keep in step. The listing is the spec, the docstrings and the
agreement test of task 2.4.

### 3. The eviction reach: key the shape cache on the artifact's observation

`exact_cache.cached_shape(brep_file)` keys on `(brep_file,
os.path.getmtime(brep_file))`. Every exact artifact is stamped with the node's
source `mtime_ns` (`exact_artifacts._atomic_export`: `os.utime(temporary,
ns=(time.time_ns(), mtime_ns))`), so a BREP replaced under an unchanged source
is the same key and is served stale.

The key becomes `(brep_file, (st_dev, st_ino, st_size, st_mtime_ns,
st_ctime_ns))` from one `os.stat`, the metadata fields of
`machinome._artifact.ArtifactObservation` and of ADR-081's
`SourceObservation`. A miss loads through the engine exactly as today, after
`_evict(brep_file)` drops every entry for that path (shape, identity,
bounds, face boxes, placements); the full `observe_artifact` is still taken
before and after the read and recorded as the load observation only when the
two agree, as today.

**Why a replacement changes the observation, from the code.** Every artifact
the core publishes goes through `_atomic_export` (exact) or the new
`publish_artifact` (Decision 5), both of which `tempfile.mkstemp` a new file
in the artifact's directory while the previous artifact still exists, write
and stamp it, then `currency.publish` → `os.replace(temporary, artifact)`.
Two files that exist at once never share an inode on one device, so the
replacement's inode differs from that of the file it replaced; the rename
also sets the new inode's ctime. Equality with a cached observation would
need an older generation's freed inode number reused for a later
replacement, with equal size, equal stamped mtime and a ctime falling in the
same tick of the filesystem's timestamp clock as the earlier file's last
metadata change.

**Probe, 3 October 2026,** with the bench's own `_atomic_export` and
`observe_artifact`: two publications of 100 different bytes stamped with the
same `mtime_ns` gave equal `(path, getmtime)` keys and unequal observations
(different inode, different ctime), on the bench's virtiofs and on ext4
under `/tmp`; 200 back-to-back replacement pairs on virtiofs gave 0 equal
observations. An in-place rewrite of the replaced file with `shutil.copy2`
(the FreeCAD adapter's restore) kept the inode and, on ext4, the ctime too:
the observation was equal. Hence the contract publishes only by rename
(`leaf-contract`, "A leaf publishes an artifact through one call").

**Cost.** On the bench's virtiofs, `os.path.getmtime`, which is one
`os.stat`, measured 3.4 µs a call, and the full `observe_artifact` 128.8 µs
(two `realpath` walks of a deep path). The key therefore takes one `stat` and the
full observation only on a miss, unlike `cached_base_mesh`, which pays
`artifact_cache_key` per call.

**`shape_identity` and the verdict memo (ADR-156).** `shape_identity(shape)`
keeps returning the cache key of a held shape, now `(path, metadata)`; the
in-process verdict memo keys on it and is never persisted. The persistent
identity (`test._persistent_identity`) reads `identity[0]` and
`exact_cache.shape_load_observation(identity)` and digests the bytes of that
observation through `_verdict_store.artifact_digest`; neither depends on the
key's second element, so the verdict store's persistent keys are unchanged.
The store's stamp digests the package source and starts afresh once, as after
every source change. `test.py`'s memo eviction by `key[0][0]` is unchanged.
Two tests assert the old key form `(path, 2.0)` and are repointed (task 5.2).

**Is a public call still needed?** For no subclass that keeps to the
contract. The one case the observation cannot see is an in-place rewrite of
an artifact path, by something other than the core's publication, within one
timestamp tick of a load of that same file, with size and mtime equal. The
contract rules that out: artifacts are written only through the core. The
FreeCAD adapter's rollback rewrites in place, but restores bytes no reader
loaded in between (its flow publishes and restores inside one
`materialize`), and under either key a restore of the previous bytes is
served correctly; its first `_evict` is therefore unnecessary and its second
is made unnecessary by this decision. `_evict` stays private.

Rejected: (a) publish `evict(path)` (every subclass that replaces an artifact
would have to know to call it, the Liskov violation of the first cycle's
review made public); (b) stamp artifacts with the publication time (breaks
ADR-006's mtime equality and every artifact's currency); (c) key on a content
digest of the `.brep` (reads every byte per request); (d) key on the full
`observe_artifact` per request (correct, 38 times the cost on virtiofs).

### 4. `shape_from_rendered` is the declared conversion hook; `namespace` is an optional guard

The hook is declared: `ExactLeafNode.shape_from_rendered(rendered)` returns
the engine's currency for a validated render result. The default is
`require_exact_engine(...).as_shape(rendered)`; an override promises a rewrap
of the kernel object the result holds, never a translation (the
`exact-geometry` requirement), as `CadQueryNode`'s `workplane_shape`,
`StepNode`'s and `Build123dNode`'s `build123d_shape` are. The core calls it
only in the two places the first cycle left it: the writing branch of
`materialize` and the stale branch of `shape()`. Where the hook raises
`TypeError` (the engine refusing an object), the core re-raises naming the
node and the type, so a leaf with no namespace is refused as legibly as one
with a namespace (today `as_shape`'s message names the type only).

`namespace` survives, as what it actually is: an optional early refusal by
module, made at validation before any artifact is written. It is the real
discriminator for faceted and front-end leaves (`solid2`, `cadquery.cq`,
`build123d`, `molejo`), whose render result is an object of their library.
For an exact leaf rendering the engine's currency it is a leftover:
`namespace = 'OCP'` names the kernel binding's module, which the engine's
admission rule already judges and which a leaf contract should not make an
author spell. Such a leaf declares none; `OCP` stays valid. The stand-in of
the first cycle (`tests/meta_project/occt_only.py`) keeps its `'OCP'` as the
pin that the old spelling still works; the new stand-in declares none.

Rejected: (a) drop `namespace` (every faceted and front-end leaf loses its
early, legible refusal, and the spec's validation scenarios with it);
(b) make validation call the conversion hook (an `optimize = False` leaf is
validated on every build, so a current exact leaf would resolve the engine,
breaking `exact-engine-dependency`'s "a current exact fusion does not resolve
the engine"); (c) make the hook a free function or a Protocol (it was made a
method by the first cycle exactly so this one could declare it).

### 5. `publish_artifact`: one call for a leaf's own artifacts

Four near-identical private publishers write a leaf's own artifacts today:
`StlNode`'s `_write_binary_stl`, `JScadNode`'s inline code,
`exact_artifacts._atomic_export` (reached by `Build123dSheetNode`), and
`base._atomic_write_bytes` (`FlexibleNode`'s snapshot). Each is: currency
check by `_up_to_date`, `mkstemp` in the directory, write, `os.utime` with the
node's `mtime_ns`, `currency.publish` with the node's digest and fingerprint.
`LeafNode.publish_artifact(path, write)` is that sequence as one declared
call: it returns false without calling `write` when `path` is current, and
otherwise calls `write(temporary)`, stamps, publishes and returns true;
`path` must begin with the node's `basepath` (the core's naming of every
artifact a node owns; the snapshot's `basepath-<hash>.stl` and the DXF's
`basepath.dxf` both do). Its implementation is `_atomic_export` with the
node's own stamp, digest and fingerprint, so bytes and records are those the
private publishers write.

`StlNode`, `SheetLeafNode`'s DXF and `FlexibleNode`'s snapshot move onto it;
`write_dxf(face, path)` then writes to the path it is given and
`build123d_sheet` stops importing `_atomic_export`. `ExactLeafNode`'s own
`.brep`/`.stl` and `FusionNode`'s keep `exact_artifacts.write_brep`/
`write_stl`, which are the core writing for the base, not a subclass.

`JScadNode` keeps its own publication, a bend: its producer is a foreign
process whose silent no-output case returns without publishing (`if not
os.path.exists(temporary): return`) and whose phase checkpoint sits between
production and publication; folding it in would either change that no-output
behaviour into an error or give the call a "wrote nothing" mode no other leaf
needs. A faceted package with a foreign producer calls the checkpoint inside
its `write`.

Rejected: make `_up_to_date` public and declare `currency.publish` (two
members where one suffices, and the stamp and record would be the subclass's
to get right); a context manager yielding the temporary path (the same
semantics with a harder-to-read early return when current).

### 6. `source_recipe`: what decides the artifacts beyond the tracked files

The FreeCAD adapter's recipe is a SHA-256 of the native snapshot: it changes
when FreeCAD's interpretation of the document changes without any tracked
file changing. The core's existing private `_artifact_recipe(path)` is
recorded only by marking publication (`_atomic_write_bytes`), not by
`_atomic_export` or `_publish_scad`, so making it the hook would touch every
publication path.

Instead `AbstractBaseNode` gains `source_recipe`, default `None`, and
`_tracked_digest(files)` and `_tracked_fingerprint(files)` fold it in when it
is not `None` (a digest or fingerprint of `None` stays `None`). Every artifact
of the node — `.scad`, `.stl`, `.brep`, markings, the flexible snapshot and
its state identity — takes its record from those two, so the recipe reaches
all of them with one change; with `None` both return exactly today's values.
It is read at every digest or fingerprint computation, which is where the
adapter calls `_check_native_generation()` today, so the adapter's property
does the same. It sits on `AbstractBaseNode`, not `LeafNode`, because the
adapter's carriers are `AssemblyNode`s with the same need; declaring it there
costs nothing and removes the carriers' private overrides too.

Rejected: declare `_tracked_digest`/`_tracked_fingerprint` overridable under
public names (a subclass would compute currency itself, and every subclass's
hashing would be its own); make `source_digest`/`source_fingerprint`
overridable (same, and they are what `vet`-level tooling and the viewer read).

### 7. The external-file identity mixin becomes public

`_ExternalWrapperIdentity` (`node/sources.py`, ADR-155) is renamed
`ExternalSourceIdentity`, unchanged in behaviour, and the four external-file
leaves mix it in under that name. `require_source_file` and `source_closure`
are already public names there and are declared. The mixin's hook
`_external_identity_origin` stays private: the mixin is the declared member,
not the hook it overrides.

Rejected: apply the wrapper identity automatically whenever
`get_source_file()` is not the defining module (it would change the FreeCAD
leaf's and carriers' `uniq_id`, which override `get_source_file` to return
the wrapper, and so every artifact name they own).

### 8. The sheet and flexible hooks lose their underscore

`_profile_faces`, `_lies_on_xy_plane`, `_extrude`, `_write_dxf` →
`profile_faces`, `lies_on_xy_plane`, `extrude`, `write_dxf(face, path)`;
`_shape_parameters`, `_shape_spec`, `_snapshot_mesh`, `_snapshot_stl`,
`_snapshot_shape` → `shape_parameters`, `shape_spec`, `snapshot_mesh`,
`snapshot_stl`, `snapshot_shape`. One name each, no alias: the one-path rule
and the absence of any project override (grep) make an alias pure cost.
`test.py`'s call of `node._snapshot_mesh` follows. Public method names on a
node can shadow a project's child or parameter of the same name; none of
these nine names is used as an attribute in `projects/` *(inferred from the
grep for definitions above; the universe scan of task 9.2 confirms)*.

### 9. The contract version: a class declaration checked at creation

`machinome/node/leaf.py` declares `CONTRACT = 1`. `LeafNode.__init_subclass__`
reads `leaf_contract` from the new class's own `__dict__` only; when present
and not equal to `CONTRACT` (or not an `int`, `bool` excluded), it raises
`TypeError`: "`<qualname>` declares leaf contract `<n>`; this machinome speaks
leaf contract 1 (`machinome.node.leaf`)". Absent means not checked, so every
project leaf, every core adapter and every subclass of a declaring class is
created as before. `LeafNode` itself carries `leaf_contract = None`, so the
member exists to be documented; `None` in a subclass's own body means "not
declared" and is not checked.

Why this and not the alternatives:

- **ADR-162's pattern, moved to the moment a leaf package meets the core.**
  The engine is resolved through a seam, so its check runs at resolve time. A
  node package is imported by the project (plan, D2): there is no seam, and
  the first moment the core sees the package is when its class is created.
  Equality, not a range, as for the engine (the packages are numbered with
  the framework, D7).
- **The adapter's own pin shows the need and the failure of the obvious
  check.** It refuses any release but 0.7.1 at construction; against this
  bench, which still says 0.7.1, the refusal passes while the module it
  imports is gone. A contract number moves when the contract does.
- **Optional on purpose.** Requiring a declaration of every subclass would
  break 78 CadQuery projects' leaves; requiring it of "packages" needs a
  definition of a package the core cannot make reliably. The dependency pin
  (`machinome~=0.8.0`) remains the install-time guard; the declaration catches
  the editable and source-tree installs that bypass pins, which is how the
  workspace runs.
- **Metadata at the cut.** The package standard (section 1.2) also asks for
  the number in package metadata; as for the engine (ADR-162), that is
  declared when the packages are cut. The core's own adapters declare nothing:
  they ship with the core and cannot differ.

Rejected: metadata only (nothing checks it at runtime, the 0.7.1 failure
again); a module-level `CONTRACT` in the package checked through
`sys.modules[cls.__module__]` (projects' modules would have to be told apart
from packages' modules); nothing (the adapter would go on pinning a release).

### 10. Documentation

The four bases' docstrings say they are declared extension points, name the
`leaf-contract` capability and list their declared members on one line headed
"Declared members:", which the agreement test (task 2.4) reads; the sentences
saying "framework-internal" go, in `leaf.py`, `exact_leaf.py`, `sheet_leaf.py`,
`flexible.py` and the `SheetLeafNode` paragraph. `docs/reference/api.rst`
"Leaf nodes" is the page a reader writing a leaf is sent to: it gains a short
paragraph naming the contract, its version and the spec, and autodoc entries
for the declared members of all four bases, under the workspace's
`skills/write-the-manual/SKILL.md`. No how-to page for writing a leaf exists
(`docs/howto/` has none), and none is written in this cycle: the reference
and the docstrings are enough to use the contract, and its first readers are
the packages this campaign cuts, whose manuals come with them.
`docs/architecture.md`'s leaf-adapter paragraph and its exact-layer cache
description are corrected.

## SOLID review

**Single responsibility.** A base owns the lifecycle, currency and
publication of its kind; a subclass owns only its technology: what it renders,
how its result becomes the kind's geometry, and what its sources are. After
this change no core leaf computes a stamp, a digest or a record itself
(`publish_artifact`, `source_recipe`), and no subclass manages a core cache
(Decision 3). *Bends:* `JScadNode` keeps its own publication (Decision 5,
its no-output case); `OpenScadNode` keeps `scad_code` reaching
`_model_for_own_scad()`, a core leaf presenting a source file verbatim, not a
pattern a package needs.

**Open/closed.** A new leaf kind needs no core change: the stand-in faceted
leaf and the stand-in exact leaf of tasks 2.1 and 2.2 are written outside
`machinome/` against the declared members alone, and the AST scan of task 2.6
proves that they, and the five adapters that leave at the cut, reach no
underscore member and no internal module. *Bend:* a new artifact kind (a
suffix the build's sweep does not know) is still a core change; no leaf
needs one today.

**Liskov substitution.** Every subclass that keeps to the contract is usable
wherever the core expects a leaf of its kind: the tree, fusion, export, the
document and the test framework treat the stand-ins as they treat the core's
adapters (scenarios of `leaf-contract`). The first cycle's named violation,
a subclass that replaces its BREP having to evict a private cache, is closed:
replacement is visible to the cache itself. *Bend:* a subclass that rewrites
an artifact in place, outside `publish_artifact`, steps outside the
guarantee; the FreeCAD adapter's rollback does, harmlessly in its flow, and
is Deferred.

**Interface segregation.** The faceted contract (`render`, `as_scad` or
`materialize` plus `publish_artifact`) carries no exact obligation; the exact
contract adds only the conversion hook and the deflections; sheet and flexible
add only their hooks. Source tracking is a separate interface, the one the
FreeCAD adapter's `_NativeCurrency` mixin shows: it mixes into a leaf and an
assembly alike and touches nothing geometric, so it is declared on
`AbstractBaseNode` as three members (`get_source_file`, `files`,
`source_recipe`) plus the external-file helpers, and the adapter's mixin
shrinks to one property. *Bend:* `publish_artifact` lives on `LeafNode`, so an
exact leaf sees it though its base writes its `.brep` and `.stl` itself; it
is the call a sheet leaf's DXF needs, so it is the exact side's too.

**Dependency inversion.** A node package depends on the declared bases,
the seam module `machinome.exact_engine` (for `require_exact_engine`) and the
engine's currency, and on the declared helpers of `machinome.node.sources` and
`machinome.source_generation`; never on `machinome.currency`,
`machinome.exact_cache`, `machinome.exact_artifacts`, `machinome._artifact` or
an underscore name. *Bends:* `StepNode` will depend on the cadquery node
package's `workplane_shape` at the cut, a package-to-package dependency the
cut decides (Deferred); the FreeCAD adapter's rollback still reaches
`currency.sidecar` (Deferred).

## ADRs

Written after implementation, from what the pilot ratifies; fresh numbers:

- **ADR-163, the leaf bases are declared extension points.** The four bases
  and their members (Decision 2), `publish_artifact`, `source_recipe`, the
  public mixin and hooks; supersedes the "framework-internal base, not a
  declared extension point" sentences of ADR-047, ADR-053 and ADR-057 (marked
  there as superseded in part). Cites ADR-004, ADR-044, ADR-055, ADR-102,
  ADR-155, ADR-160, ADR-161.
- **ADR-164, the loaded-shape cache keys on the artifact's observation.**
  Amends ADR-044's `(path, mtime)` key; cites ADR-006, ADR-028 (the base-mesh
  cache), ADR-081, ADR-156.
- **ADR-165, a leaf package declares the contract version on its class,
  checked at class creation.** Extends ADR-162's pattern to imported
  packages; cites ADR-068.

Not architectural: the hook renames' spellings, the docstring wording, the
test repointing.

## Risks / Trade-offs

- [A project child or parameter named like a newly public hook] → none found
  by grep; the universe scan (task 9.2) loads every root against the bench.
- [`source_recipe` does not reach an internal node composing a recipe-bearing
  leaf: a fusion's digest is over its union of files] → the FreeCAD adapter
  has the same gap today (its override is on the leaf and the carriers, not a
  fusion), no project fuses such a leaf, recorded under Deferred.
- [An in-place artifact rewrite inside one ctime tick is invisible to the
  cache] → the contract publishes by rename only; the probe shows the
  residual case only for in-place rewrites; the same metadata is what the
  base-mesh cache and ADR-081 already trust.
- [`__init_subclass__` refusing a class at import time surprises a
  developer] → the message names the class, both versions and the module;
  only a class that declares a number is ever checked.
- [The verdict store starts afresh once] → its stamp digests the package
  source, as after every framework change.
- [FreeCAD validation needs the FreeCAD runtime] → the validator records the
  environment and any test it could not run; the cycle does not claim a green
  it did not see.

## Migration Plan

One planning commit, one implementation commit, on `v0.8-leaf-contract`;
integration into `v0.8` is the orchestrator's. No artifact rebuild is needed
for a node without a recipe (bytes, records and `uniq_id` unchanged). Rollback
is reverting the implementation commit.

## Deferred, recorded here so it is not lost

- The class-name switch at `node/base.py:1262` (plan item 2).
- Items 4, 5 and 6 of the plan; the markings SVG reducer; the studio's
  `shop-skills/machinome-api/SKILL.md`, updated once, at the cut.
- The contract number in each node package's metadata (package standard
  section 1.2), declared when the packages are cut, as for the engine.
- machinome-freecad's retarget and rename to machinome-node-freecad, in its
  own repository, beyond what its validation branch does.
- **The FreeCAD adapter's publication rollback** (pilot, 3 October 2026:
  deferred to the adapter's retarget). It copies and restores the `.brep`,
  `.stl` and their records in place, reaching `currency.sidecar`, to keep "a
  failed native generation leaves no new output", a stronger promise than
  the core's ("an interrupted publication leaves no record and rebuilds").
  The gap it works around is narrower than transactional publication: the
  adapter's source identity is the worker's native generation, which the
  phase census cannot observe, since the census observes files. `source_recipe`
  covers the digest-time half, a leaf raising `SourceChanged` from it; the
  other half would be a declared boundary hook, so a leaf's own check runs
  where the core's `check_current` runs at the phase boundary, after which
  the core's record ordering already keeps a mid-build change safe. Whether
  "no new output" was ever needed beyond "rebuild, never stale" is the
  retarget cycle's evidence to weigh. On the validation branch the reach is
  recorded, not fixed.
- **An assembly extension contract.** The adapter's carriers call
  `AssemblyNode._link_children` and `source_generation.track_sources`.
- `StepNode`'s use of `workplane_shape` from the cadquery adapter: at the cut,
  machinome-node-step either depends on machinome-node-cadquery or keeps its
  own conversion.
- `source_recipe` folded into an internal node's currency over its subtree,
  when a project fuses a recipe-bearing leaf.
- Teaching the build's sweep an artifact kind a package introduces, when one
  does.

## Open Questions

None. The three put to the pilot were settled on 3 October 2026: four
bases (Decision 1); the public names as proposed (`publish_artifact`,
`source_recipe`, `leaf_contract`, `ExternalSourceIdentity`, the nine hooks
without their underscore); the FreeCAD adapter's rollback stays a recorded
reach until its retarget (Deferred).

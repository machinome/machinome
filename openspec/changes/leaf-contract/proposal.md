## Why

The lean-core campaign (`workflow/ongoing/lean-core.md`, "What it takes",
item 1) moves every kernel-bearing node type into a package of its own:
machinome-node-cadquery, -build123d, -step and -molejo, and later the FreeCAD
adapter as machinome-node-freecad. Each of those packages subclasses a leaf
base of the core. Today those bases say in their own docstrings that they are
framework-internal and not extension points, and the only leaf already
written outside the core shows what that costs:

- **machinome-freecad's exact leaf** (`machinome_freecad/adapter.py`,
  `_leaf_class`) reaches three things the core never promised. It imports
  cadquery only to cast the bare `TopoDS_Shape` it reads from a FreeCAD BREP
  (`cq.Shape.cast`), which the engine has admitted as it is since ADR-160. It
  imports the private `machinome.exact._evict` twice from its `materialize()`
  override, because the loaded-shape cache keys on `(path, float mtime)` and
  every artifact is stamped with its source's mtime, so a BREP the adapter
  replaces under an unchanged source (a changed native recipe) is served stale;
  that module no longer exists, so the adapter is broken against the campaign
  line. And its `_NativeCurrency` mixin overrides the private
  `_tracked_digest` and `_tracked_fingerprint` to fold its native recipe into
  currency. It also guards all of this with a construction-time refusal of
  any machinome other than `0.7.1`, which cannot see a contract change: the
  bench still reports 0.7.1 while the module it imports is gone.
- **The nine core leaves are the shape of the contract.** What they override
  and what they reach is what a package will need: `StepNode` mixes in the
  private `_ExternalWrapperIdentity`; `Build123dSheetNode` overrides four
  private hooks of `SheetLeafNode` and imports the private
  `exact_artifacts._atomic_export`; `MolejoNode` overrides five private hooks
  of `FlexibleNode`; `StlNode` publishes its artifact through the
  framework-internal `machinome.currency.publish` beside `_up_to_date`. Every
  one of these is a reach that becomes a cross-package dependency on a core
  private at the cut.

This cycle declares the contract before the packages are cut, so the cut moves
code and no node package reaches a private of the core.

## What Changes

- **The leaf bases become declared extension points.** `LeafNode`
  (`machinome.node.leaf`), `ExactLeafNode` (`machinome.node.exact_leaf`),
  `SheetLeafNode` (`machinome.node.sheet_leaf`) and `FlexibleNode`
  (`machinome.node.flexible`) are specified by a new capability: what a
  subclass must provide, what it may override and how, what it must not
  override, and what the core guarantees in return. Their docstrings say so
  and point at the spec; the API reference's leaf section documents the
  declared members.
- **One versioned contract.** `machinome.node.leaf.CONTRACT = 1`; a class that
  declares `leaf_contract` in its own body is checked when it is created and
  refused, naming both versions, when the number differs from the core's. A
  class that declares nothing (every project leaf) is not checked. ADR-162's
  pattern, at class creation instead of a seam, because a node package is
  imported, not resolved.
- **The loaded-shape cache keys on the artifact's observation**, the device,
  inode, size, mtime and ctime of the `.brep`, instead of `(path, float
  mtime)`. Every artifact the core publishes replaces the previous one by
  rename from a new file, so a replacement changes the observation even when
  the stamped mtime is equal. Eviction becomes unnecessary for every subclass;
  `_evict` stays private and no public eviction call is added.
- **The conversion hook is declared.** `ExactLeafNode.shape_from_rendered`
  is the contract's one conversion point: a rewrap, never a translation; the
  default admits what the engine admits. A result it cannot convert is
  refused naming the node and the type. `namespace` stays an optional early
  guard on the render result's module; a leaf rendering the engine's currency
  declares none (`namespace = 'OCP'` is no longer the way to say it).
- **A leaf publishes its own artifacts through one call.**
  `LeafNode.publish_artifact(path, write)` writes through a temporary file,
  stamps it, records the node's sources and replaces the artifact atomically,
  and does nothing when the artifact is already current. `StlNode`, the sheet
  base's DXF and the flexible snapshot use it in place of three private
  publishers; bytes and source records are unchanged.
- **A node may declare a source recipe.** `source_recipe`, default `None`,
  states what decides a node's artifacts beyond its tracked files; the core
  folds it into the source digest and fingerprint of every artifact the node
  publishes. With `None` nothing changes. It replaces the FreeCAD adapter's
  overrides of `_tracked_digest` and `_tracked_fingerprint`.
- **The external-file identity mixin is public**:
  `_ExternalWrapperIdentity` becomes `ExternalSourceIdentity` in
  `machinome.node.sources`, beside `require_source_file` and
  `source_closure`, which the contract also declares.
- **BREAKING (for subclasses of the two specialised bases only):** the hooks
  of `SheetLeafNode` (`_profile_faces`, `_lies_on_xy_plane`, `_extrude`,
  `_write_dxf`) and of `FlexibleNode` (`_shape_parameters`, `_shape_spec`,
  `_snapshot_mesh`, `_snapshot_stl`, `_snapshot_shape`) lose their leading
  underscore, and `write_dxf` takes the temporary path the base publishes. No
  project overrides any of them (grep of `projects/`, 3 October 2026); the
  two core adapters are updated.

Not in this cycle, recorded in design.md's "Deferred": the class-name switch
(`node/base.py:1262`, plan item 2); items 4, 5 and 6 of the plan; the markings
reducer; the studio's contract skill; the FreeCAD adapter's retarget and
rename; an assembly extension contract (the adapter's carriers still override
`AssemblyNode` privates); the adapter's publication rollback; the
package-metadata form of the contract declaration (at the cut, as for the
engine).

## Capabilities

### New Capabilities

- `leaf-contract`: the declared leaf extension contract. The four bases and
  their one path each; what a faceted, an exact, a sheet and a flexible leaf
  subclass must provide and may override; the conversion hook and the
  namespace guard; artifact publication through `publish_artifact`; source
  identity (`get_source_file`, `files`, `source_recipe`, the external-file
  identity and its helpers); what a subclass must not override; what the core
  guarantees; the contract version and its check.

### Modified Capabilities

- `exact-geometry`: "Exact geometry is persisted and reloaded" keys the
  loaded shape and its derived measurements on the artifact's observation, so
  a BREP replaced under an unchanged source mtime is never served stale; "An
  exact render is admitted by its kernel object" names the declared
  conversion hook, its refusal naming the node, and the namespace guard's
  optional role for a leaf rendering the engine's currency.
- `node-model`: "Leaf adapters are distinct types" no longer says a shared
  base is not part of the public interface; the shared bases are now the
  declared contract, and type distinctness still holds.

## Impact

- **Code.** `machinome/node/leaf.py` (`CONTRACT`, `__init_subclass__`,
  `publish_artifact`, docstring), `machinome/node/base.py` (`source_recipe`
  folded into `_tracked_digest`/`_tracked_fingerprint`),
  `machinome/node/exact_leaf.py` (docstring, conversion refusal naming the
  node), `machinome/exact_cache.py` (observation key),
  `machinome/node/sheet_leaf.py` and `node/adapters/build123d_sheet.py` (public
  hooks, DXF through `publish_artifact`), `machinome/node/flexible.py`,
  `node/adapters/molejo.py` and `machinome/test.py` (public flexible hooks,
  snapshot through `publish_artifact`), `machinome/node/sources.py`
  (`ExternalSourceIdentity`), `node/adapters/{stl,step,openscad,jscad}.py`
  (the public mixin; `StlNode` through `publish_artifact`),
  `node/adapters/step.py` docstrings naming the cache.
- **Public interface.** New public members: `machinome.node.leaf.CONTRACT`,
  `leaf_contract`, `publish_artifact`, `source_recipe`,
  `machinome.node.sources.ExternalSourceIdentity`; nine hooks renamed public.
  Nothing a project imports changes; no project overrides a renamed hook.
- **Artifacts.** No byte of any artifact or source record changes for a node
  that declares no `source_recipe` (the first cycle's golden fixtures,
  `tests/exact_engine_golden.py --check`, are the pin). Artifact identity
  (`uniq_id`) is unchanged: the mixin keeps its behaviour under its new name.
- **Docs.** `docs/reference/api.rst` "Leaf nodes", `docs/architecture.md`
  (leaf adapters, exact layer cache key), the changelog's Unreleased section.
  No how-to for writing a leaf exists and none is written here.
- **Downstream.** machinome-freecad is validated against this bench on a
  never-merged branch `lean-core-validation` of its own repository: bare
  render, no cadquery in the adapter, no `_evict`, `source_recipe` in place
  of its currency overrides, `leaf_contract = 1` in place of its release pin.
  Its retarget and rename are a later cycle in that repository.

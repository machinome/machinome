# ADR-163: The Leaf Bases Are Declared Extension Points

**Status:** Accepted, declared members amended 2026-10-04 by [ADR-178](ADR-178-a-leaf-declares-its-kind-as-one-set-on-the-leaf-base.md)
**Date:** 2026-10-03
**Change:** [`leaf-contract`](../../../openspec/changes/archive/2026-10-03-leaf-contract/)
**Supersedes in part:**
- [ADR-047: One shared OCCT currency for every exact backend](ADR-047-shared-occt-currency-for-exact-backends.md) — its sentence "`ExactLeafNode` is a framework-internal base, not a declared extension point"
- [ADR-053: Authored profile as a sheet part's source of truth](ADR-053-authored-profile-as-the-sheet-part-source-of-truth.md) — `SheetLeafNode` as "a framework-internal base"
- [ADR-057: The flexible leaf, whose geometry travels as a spec](ADR-057-the-flexible-leaf-and-spec-carried-geometry.md) — `FlexibleNode` as "the framework-internal base"
**Related to:**
- [ADR-004: Multi-CAD backend adapter pattern](ADR-004-multi-cad-backend-adapter-pattern.md) — the adapters these bases serve
- [ADR-044: Derived exact-geometry capability](ADR-044-derived-exact-geometry-capability.md) — the exact contract `ExactLeafNode` holds
- [ADR-055: Wrapper module in the imported part's source set](ADR-055-wrapper-module-in-the-imported-part-source-set.md) — what `files` holds for an external-file leaf
- [ADR-102: Native materialization precedes optional SCAD presentation](ADR-102-native-materialization-precedes-optional-scad-presentation.md) — the `materialize` hook a faceted leaf implements
- [ADR-155: External-file wrapper identity includes the defining source](ADR-155-external-wrapper-identity-includes-defining-source.md) — the mixin made public here
- [OCCT/ADR-160: The OCCT engine's currency is the kernel's own shape](../OCCT/ADR-160-the-occt-engines-currency-is-the-kernels-own-shape.md) — what a conversion hook returns
- [ADR-161: The core holds no kernel code](ADR-161-the-core-holds-no-kernel-code.md) — the seam the exact base resolves
- [ADR-164: The loaded-shape cache keys on the artifact's observation](ADR-164-the-loaded-shape-cache-keys-on-the-artifacts-observation.md), [ADR-165: A leaf package declares the contract version on its class](ADR-165-a-leaf-package-declares-the-contract-version-on-its-class.md) — the two decisions that complete this one

## Context and Problem Statement

The lean-core campaign (`workflow/ongoing/lean-core.md`, item 1) moves every
kernel-bearing node type into a package of its own: CadQuery, build123d,
STEP and molejo leaves, and later the FreeCAD adapter. Each package
subclasses a leaf base of the core. Until this change those bases said in
their docstrings, and ADR-047, ADR-053 and ADR-057 said in their decisions,
that they were framework-internal and not extension points.

The only leaf already written outside the core, machinome-freecad's exact
leaf, shows the cost: it imported cadquery only to cast a bare
`TopoDS_Shape`, called the private `machinome.exact._evict` (removed by the
first campaign cycle) from a `materialize()` override, overrode the private
`_tracked_digest` and `_tracked_fingerprint` to fold its native recipe into
currency, and pinned a machinome release number that could not see any of
these change. The nine core leaves show the rest: `StepNode` mixed in the
private `_ExternalWrapperIdentity`, `Build123dSheetNode` overrode four
private hooks and imported the private `exact_artifacts._atomic_export`,
`MolejoNode` overrode five private hooks, and `StlNode` published through
the framework-internal `currency.publish` beside `_up_to_date`. At the cut
every one of these would become a dependency of one package on another's
private.

## Decision Drivers

- The cut must move code, not design a contract inside a move.
- A leaf written outside the core must reach no underscore name and no
  internal module of the core.
- No core leaf may change behaviour, artifact bytes, source records or
  identity.
- Declare only what a leaf uses today.

## Considered Options

1. **Declare four bases, by what their core subclasses override** (chosen)
2. Declare only `LeafNode` and `ExactLeafNode`, deferring the sheet and
   flexible hooks to the cut
3. Declare the contract as `typing.Protocol` classes beside the bases

## Decision Outcome

Four bases are declared extension points, each at one path, the module that
defines it: `LeafNode` (`machinome.node.leaf`), `ExactLeafNode`
(`machinome.node.exact_leaf`), `SheetLeafNode` (`machinome.node.sheet_leaf`)
and `FlexibleNode` (`machinome.node.flexible`). The `leaf-contract`
capability specifies, member by member, what a subclass must provide, what it
may override and how, what it must not override, and what the core
guarantees in return; each base's docstring lists its declared members on a
"Declared members:" paragraph that a test compares with the spec and with
the API reference.

- **The faceted contract**: `render`, `validate`, `namespace`, `as_scad` for
  a SCAD-presented leaf or `materialize` for one producing its own STL, and
  `publish_artifact(path, write)`, the core's one sequence of temporary
  file, source-mtime stamp, source record and atomic rename, skipped when the
  artifact is current, refused for a path outside the node's `basepath`. It
  replaces `StlNode`'s, the DXF's and the flexible snapshot's private
  publishers with bytes and records unchanged. `JScadNode` keeps its own
  publication: its foreign producer may silently produce nothing, and its
  phase checkpoint sits between production and publication.
- **The exact contract** adds the declared conversion hook
  `shape_from_rendered`, a rewrap and never a translation, whose refusal the
  core re-raises naming the node and the type, and the two tessellation
  precisions. `namespace` stays an optional early guard by module; a leaf
  rendering the engine's currency declares none.
- **The sheet and flexible hooks lose their underscore**: `profile_faces`,
  `lies_on_xy_plane`, `extrude`, `write_dxf(face, path)` (writing to the
  temporary path the base publishes); `shape_parameters`, `shape_spec`,
  `snapshot_mesh`, `snapshot_stl`, `snapshot_shape`. One name each, no alias:
  no project overrides any of them.
- **Source identity** is three members on `AbstractBaseNode`:
  `get_source_file()`, `files`, and the new `source_recipe`, a string stating
  what decides the node's artifacts beyond its tracked files, which the core
  folds into the digest and fingerprint of every artifact the node publishes
  (`None` changes nothing). It sits on the node base, not the leaf base,
  because the FreeCAD adapter's carriers are assemblies with the same need.
  The external-file identity mixin is public as
  `machinome.node.sources.ExternalSourceIdentity`, beside the declared
  `require_source_file` and `source_closure`; `consumed_source`,
  `coherent_read` and `SourceChanged` are declared for leaves although
  `vet` does not offer `machinome.source_generation` to a project.
- **Not overridable**: `assemble`, `shape` on an exact leaf, `render` on a
  sheet leaf, `mtime_ns`, `mtime`, `source_digest`, `source_fingerprint`,
  `uniq_id`, `children`, `time`, and every underscore member.

Option 2 was rejected because the cut would then carry contract design and
nine renames inside a code move, and a molejo package cut first would ship
against private hooks. Option 3 was rejected because a leaf is a subclass,
not a provider object: inheritance already gives the defaults, and a
Protocol would be a second listing of the same members to keep in step.
The pilot settled four bases and the names on 3 October 2026.

## Consequences

- A stand-in faceted leaf and a stand-in exact leaf written outside
  `machinome/` (`tests/contract_package/`) build, fuse and test against the
  declared members alone, and an AST scan proves that they and the five
  adapters that leave at the cut reach no underscore member and no internal
  module, with two listed exceptions: `CadQueryNode`'s metaclass derives from
  the declared `NodeMeta`, and `StepNode` reaches the cadquery adapter's
  `workplane_shape`, which the cut decides.
- BREAKING for a subclass of `SheetLeafNode` or `FlexibleNode` that
  overrides an underscored hook; none exists among the projects.
- Not in this decision: an assembly extension contract (the FreeCAD
  adapter's carriers still call `AssemblyNode._link_children`), the FreeCAD
  adapter's publication rollback, which rewrites artifacts in place and
  reaches `currency.sidecar`, and `source_recipe` reaching an internal node
  that fuses a recipe-bearing leaf.

## References

- `machinome/node/leaf.py`, `exact_leaf.py`, `sheet_leaf.py`, `flexible.py`,
  `base.py` (`source_recipe`), `sources.py` (`ExternalSourceIdentity`)
- `openspec/specs/leaf-contract/spec.md`
- `tests/test_leaf_contract_members.py`, `test_leaf_contract_reach.py`,
  `test_leaf_contract_exact.py`, `test_leaf_contract_faceted.py`,
  `test_leaf_contract_recipe.py`, `tests/contract_package/`

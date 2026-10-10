# ADR-176: The Mesh Engine Is a Provider Behind the Seam, Installed by an Extra

**Status:** Accepted; the mesh provider's address and extra, amended 2026-10-05 by [ADR-180](../NODE/ADR-180-the-engines-are-named-for-the-representation-each-consumes.md)
**Date:** 2026-10-04
**Change:** [`mesh-engine`](../../../openspec/changes/archive/2026-10-04-mesh-engine/)
**Amends:**
- [ADR-052: Conditional mesh-engine dependency](ADR-052-conditional-mesh-engine-dependency.md) — its "packaging is unchanged" and its rejected option "move `manifold3d` to an optional extra"; `trimesh.boolean`'s engine selection no longer reaches the core
- [NODE/ADR-161: The core holds no kernel code](../NODE/ADR-161-the-core-holds-no-kernel-code.md) — now covers the mesh engine, whose seam takes the exact seam's shape, absence rule included
- [ADR-156: A decided verdict outlives the run](ADR-156-a-decided-verdict-outlives-the-run.md) — the stamp no longer carries `manifold3d`; a faceted verdict's key carries the engine's identity
- [NODE/ADR-167: A kernel is an extra, and its module refuses its absence at import](../NODE/ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md) — `manifold3d` is no longer the required exception

**Related to:**
- [ADR-029: Manifold cache and AABB broad phase](ADR-029-manifold-cache-and-aabb-broad-phase-for-assertions.md) — the cache, now of the engine's solids, stays in the core
- [ADR-074: The mesh engine judges its own input](ADR-074-the-mesh-engine-judges-its-own-input.md) — unchanged, through the engine's `fault`
- [ADR-049: Static equilibrium as LP feasibility](ADR-049-static-equilibrium-as-lp-feasibility.md) — the statics program stays in the core
- [NODE/ADR-162: A resolved provider declares the contract version it implements](../NODE/ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md) — the contract check

## Context and Problem Statement

On 4 October 2026 the pilot settled that machinome's core stays Apache-2.0,
and took up next "the extraction of manifold3d behind the mesh seam, for the
architecture alone, by the same shape as the exact engine"
(`workflow/ongoing/lean-core.md`, "Settled by the pilot, 4 October 2026, later
the same day"). The mesh engine was the one kernel the core still called
itself:

- `machinome/mesh_engine.py` imported `manifold3d` and handed its `Manifold`
  and `Mesh` classes to the core; there was no provider module, no contract
  version and no extra, and its refusal said `pip install manifold3d`;
- `machinome/test.py` and `machinome/node/fusion.py` built, judged, placed,
  intersected, united, measured and meshed back manifold3d solids with
  manifold3d's own API;
- `assertJoined`'s union and the `.mesh` fallback reached manifold3d through
  `trimesh.boolean`, whose backend in trimesh 4.4 is manifold3d;
- the verdict store stamped every verdict, exact ones included, with the
  installed `manifold3d`;
- `manifold3d` was a required dependency, the last kernel there since
  ADR-167 by the pilot's ruling of 2 October, which the 4 October decision
  superseded.

## Decision Drivers

- The core holds no kernel code (ADR-161) and names a provider in one place.
- Every verdict, every refusal's status word and every fused STL byte stays
  what it was.
- A plain install carries no kernel, and every path that needs the mesh
  engine refuses by name; a project whose every compared pair is exact never
  resolves it.
- No assertion's meaning changes; no second engine, no WebAssembly surface,
  no package cut in layer 1 (the pilot's scope).

## Considered Options

1. **A provider `machinome.manifold.engine` behind the seam, of the exact
   engine's shape, installed by the `manifold` extra** (chosen)
2. Keep manifold3d inside `machinome.mesh_engine`, the seam and the kernel
   in one module
3. Name the provider by its capability, `machinome.mesh` or
   `machinome.faceted`
4. Resolve the seam ahead of `trimesh.boolean` and leave trimesh to compute
   `assertJoined`'s union and the `.mesh` fallback
5. Bind the engine's identity in the verdict store's process stamp

## Decision Outcome

**The provider.** `machinome.manifold` exports nothing; its one module
`machinome.manifold.engine` (Apache-2.0, as manifold3d is) calls
`require_extra('manifold', 'the mesh engine (machinome.manifold.engine)',
'manifold3d')` before importing its kernel and defines the contract's ten
operations, each the manifold3d call the core made inline: `solid_from_mesh`
(float32 positions, uint32 triangles), `fault` (`None`, or manifold3d's word
such as `NotManifold`), `mesh_arrays`, `centred_box`, `placed_solid` (the
matrix's upper three rows), `unite_solids` (a left fold, not
`batch_boolean`), `intersect_solids`, `is_empty`, `volume` and `identity`
(`('manifold3d', version)` from metadata). It imports numpy, manifold3d and
`machinome.extras` only, reads and writes no file and keeps no state.

**The seam.** `machinome.mesh_engine` keeps its address and its names,
declares `CONTRACT = 1`, `PROVIDER`, `MeshSolid` and four Protocols by
consumer (`MeshSolids`, `MeshComposition`, `MeshComparison`,
`MeshIdentity`, joined in `MeshEngine`). `mesh_engine()` resolves the
provider once per process, answers `None` when the provider or its kernel is
absent (`ModuleNotFoundError` naming `machinome.manifold` or the provider, or
the `manifold` extra's `ExtraUnavailable`), lets any other import error
propagate, and refuses a contract mismatch with `MeshEngineIncompatible`
naming both versions. `require_mesh_engine` returns the provider or raises
`MeshEngineUnavailable` naming `pip install "machinome[manifold]"`.

**The core over the seam.** The core holds the engine's solids as opaque
handles in its caches (renamed: `_mesh_solid_cache`, `_cached_mesh_solid`,
`_flexible_mesh_solid*`, `_DeferredMeshSolid`, `_placed_mesh_solid`,
`_Body.solid`) and asks the engine for every operation, looked up on the
provider at the call. `assertJoined`'s union and the `.mesh` fallback run
trimesh's own steps through the engine (`_mesh_boolean`: trimesh's
`is_volume` precondition and message, one solid per mesh, the Boolean,
`Trimesh(vertices, faces)` with trimesh's processing), so no core module
calls `trimesh.boolean`. The faceted fusion's recipe identity
`faceted-fusion-manifold-v1` is kept.

**The three doors.** The provider refuses at import by its extra; the seam
reads that refusal as absence, so every requiring path raises at its point
of use naming itself, its reason and the extra; and `machinome test` on the
faceted kernel refuses at its start, before any node is built, through
`self.fail` (exit 1).

**The verdict store.** `KERNELS` loses the `manifold3d` row;
`persisted_key` takes an `engine` tuple, the engine's `identity()` for a
faceted key and `()` for an exact one; a faceted question whose engine is
absent or reports no version is computed without being kept.

**Packaging.** `manifold3d` leaves `dependencies` for the `manifold` extra,
unranged as it was; `all` includes it; no node extra does.

**Two wordings change** (design.md Decision 4): a compared part's refusal
says "cannot build a solid" for "cannot build a Manifold", and the faceted
fusion's says `manifold3d reported NotManifold` for `... Error.NotManifold`.

### Why not option 2

The seam and the kernel in one module is what ADR-161 forbids for the exact
engine; the core would go on importing a kernel.

### Why not option 3

A capability name leaves a second mesh engine nowhere to go, the reason D1
gave for `machinome-occt` over `machinome-exact`.

### Why not option 4

The refusal would be the seam's, but the core would still reach manifold3d
outside the provider, and a second engine would not be used there.

### Why not option 5

The stamp is computed at the store's first use in every run, all-exact ones
included; asking the engine there would resolve it in every run.

## Ratification (4 October 2026)

The orchestrator, under the pilot's standing authority, took every
recommendation of design.md's Open Questions: the engine's identity binds
the faceted keys and not the stamp; the two `trimesh.boolean` paths go
through the engine; the faceted fusion's bytes are proven by the golden and
an exact fusion never asks; `machinome/extras.py` gains no table; no
project-facing mesh operation; the privates are renamed; the extra stays
unpinned; the recipe identity is kept; two unchanged `test-framework`
requirements keep "cached Manifolds". The admission operation is named
`fault`, so "refusal" keeps meaning the extras' install refusal.

Accepted at implementation: trimesh asks for `manifold3d` at its import from
two of its modules, `trimesh.boolean` and `trimesh.util` (through
`importlib.util.find_spec`, which does not catch a finder's error), not from
`trimesh.boolean` alone as design.md Decision 11 said. The absent-engine
helper therefore finds nothing rather than raising, and the validation
asserts that every ask of `manifold3d` is one of those two.

## Consequences

- `pip install machinome` no longer installs manifold3d; a project comparing
  a part without exact geometry, running `machinome test --faceted`, calling
  `assertAssemblySupported`, fusing meshes, or importing manifold3d or calling
  `trimesh.boolean` itself installs `machinome[manifold]`. ADR-052's
  objection to an extra, a "silently faceted-broken installation", no longer
  holds: every requiring path refuses by name and the faceted run refuses at
  its start.
- Verdicts are bit-identical: the change's golden (1095 values over every
  meta fixture on both kernels, statics digests, body counts, the fused STL,
  the `.mesh` fallback) and the Pin_tumbler_lock (2573 verdicts) and
  Prusa3-vanilla (15935 verdicts) logs are byte-identical before and after.
- The verdict store starts afresh once (the package digest changed); a
  manifold3d upgrade no longer discards exact verdicts.
- A faceted verdict served from the store resolves the engine at its key,
  the cost of importing one module; manifold3d is already loaded by trimesh.
- `mesh_engine()` no longer swallows a broken manifold3d.
- At the cut the provider becomes the distribution `machinome-manifold` and
  the `manifold-engine` capability moves with it.
- Deferred: the exact path's stamp rows (`cadquery-ocp`, `cadquery`) moving
  into exact keys from an exact engine identity.

## References

- `machinome/manifold/engine.py`, `machinome/mesh_engine.py`,
  `machinome/test.py`, `machinome/node/fusion.py`,
  `machinome/_verdict_store.py`, `machinome/manager/test.py`
- `pyproject.toml`, `requirements.txt`
- `tests/test_mesh_engine_seam.py`, `tests/test_manifold_engine.py`,
  `tests/test_mesh_engine_dependency.py`, `tests/mesh_engine_absent.py`,
  `tests/mesh_engine_golden.py`, `tests/data/mesh_engine_golden.json`
- `openspec/specs/manifold-engine/spec.md`,
  `openspec/specs/mesh-engine-dependency/spec.md`,
  `openspec/specs/kernel-extras/spec.md`,
  `openspec/specs/test-framework/spec.md`

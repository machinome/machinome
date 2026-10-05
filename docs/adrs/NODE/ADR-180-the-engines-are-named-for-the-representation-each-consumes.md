# ADR-180: The Engines Are Named for the Representation Each Consumes: `brep` and `mesh`

**Status:** Accepted
**Date:** 2026-10-05
**Change:** [`brep-mesh`](../../../openspec/changes/archive/2026-10-05-brep-mesh/)
**Amends:**
- [ADR-073: The comparison kernel is a property of the test run](../TEST-FRAMEWORK/ADR-073-the-comparison-kernel-is-a-property-of-the-test-run.md) — the run's comparison kernel is its comparison engine
- [ADR-160: The OCCT engine's currency is the kernel's own shape](../OCCT/ADR-160-the-occt-engines-currency-is-the-kernels-own-shape.md) — the provider's address; the currency unchanged
- [ADR-161: The core holds no kernel code](ADR-161-the-core-holds-no-kernel-code.md) — the seam's address and names
- [ADR-162: A resolved provider declares the contract version it implements](ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md) — the constants named per role in one module; the B-rep contract is 2
- [ADR-163: The leaf bases are declared extension points](ADR-163-the-leaf-bases-are-declared-extension-points.md) — the B-rep leaf base's name and module
- [ADR-165: A leaf package declares the contract version on its class](ADR-165-a-leaf-package-declares-the-contract-version-on-its-class.md) — leaf contract version 3
- [ADR-167: A kernel is an extra, and its module refuses its absence at import](ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md) — the extras `brep` and `mesh`
- [ADR-176: The mesh engine is a provider behind the seam, installed by an extra](../TEST-FRAMEWORK/ADR-176-the-mesh-engine-is-a-provider-behind-the-seam-installed-by-an-extra.md) — the mesh provider's address and extra
- [ADR-178: A leaf declares its kind as one set on the leaf base](ADR-178-a-leaf-declares-its-kind-as-one-set-on-the-leaf-base.md) — the member `exact` is `brep`
**Related to:**
- [ADR-047: Shared OCCT currency for exact backends](ADR-047-shared-occt-currency-for-exact-backends.md)
- [ADR-052: Conditional mesh engine dependency](../TEST-FRAMEWORK/ADR-052-conditional-mesh-engine-dependency.md)
- [ADR-090: The placement quantum is a property of the test run](../TEST-FRAMEWORK/ADR-090-the-placement-quantum-is-a-property-of-the-test-run.md)
- [ADR-156: A decided verdict outlives the run](../TEST-FRAMEWORK/ADR-156-a-decided-verdict-outlives-the-run.md)
- [ADR-169: A leaf type is one module under `machinome.node`](ADR-169-a-leaf-type-is-one-module-under-machinome-node.md)
- [ADR-177: The OpenSCAD family is a node package, and the core names no technology](ADR-177-the-openscad-family-is-a-node-package-and-the-core-names-no-technology.md)

## Context and Problem Statement

The core's two engines were named three ways at once: by a claim, the
*exact* engine; by a quality, the *faceted* kernel; and by the library a
provider happened to wrap, `machinome.occt` and `machinome.manifold`, with
the extras `occt` and `manifold`. A name that says OCCT describes which
library a provider wraps today, a fact that is the provider's alone, and a
name that says "exact" or "faceted" describes a property, not a role: the
word `exact` also stood, in its ordinary sense, beside exact IEEE-754 values,
the exact-bytes verdict key (ADR-070) and the exact-negative shortcut
(ADR-090). The cut that moves each engine into its own distribution needs one
address per role that a second provider of the same role could install
without the core's edit. The pilot locked the words on 4 October 2026: the
engines are named for the representation each consumes, `brep` (a boundary
representation of parametric surfaces) and `mesh` (a polyhedral triangle
mesh), everywhere the code uses them for this split. At ratification the pilot
ruled the run's choice, called its `kernel`, its engine too: `kernel` keeps
only its library sense.

## Considered Options

1. **One engine package, `machinome.engine`, whose `__init__` holds both
   seams and admits portions; the providers its modules `brep` and `mesh`;
   every name of the split renamed once, with no alias** (chosen)
2. The seams named like their providers, `brep()` and `mesh()`
3. Two seam submodules beside the providers (`brep_seam.py`, `mesh_seam.py`)
4. "B-rep" and "mesh" in prose only, the identifiers kept (`ExactLeafNode`,
   `exact`, `'faceted'`)
5. The former names kept beside the new ones as aliases, or the former
   variable read as an alias

## Decision Outcome

**The engine package.** `machinome/engine/__init__.py` is the two former seam
modules joined, each keeping its shape (a known provider address resolved
once per process, absence read from the provider's `ExtraUnavailable` or its
own `ModuleNotFoundError`, an integer contract checked by equality, one
actionable refusal): `brep_engine()`, `require_brep_engine(needed_by,
reason)`, `BrepEngineUnavailable`, `BrepEngineIncompatible`,
`BrepCommonInconsistency`, `BrepCommonVerificationError`, `BREP_CONTRACT = 2`,
`BREP_PROVIDER = 'machinome.engine.brep'`, the Protocols `BrepCurrency`,
`BrepComposition`, `BrepComparison`, `BrepEngine` and the alias `BrepShape`;
and `mesh_engine()`, `require_mesh_engine()`, `MeshEngineUnavailable`,
`MeshEngineIncompatible`, `MESH_CONTRACT = 1`, `MESH_PROVIDER =
'machinome.engine.mesh'` and the mesh Protocols under their former names. It
imports neither provider, exports no operation, and ends with
`__path__ = _namespace_portions(__path__, __name__)`, so a distribution cut
from the core installs `machinome/engine/brep.py` or `mesh.py` without the
package's `__init__` and the seam finds it. No seam is named like its
provider: importing `machinome.engine.brep` binds the module as the
package's attribute `brep`, which would replace a seam function of that name
at its first use (the probe in the change's design).

**The providers.** `machinome.occt.engine` is `machinome.engine.brep` and
`machinome.manifold.engine` is `machinome.engine.mesh`, their code unchanged
but for their refusals (`require_extra('brep', 'the B-rep engine
(machinome.engine.brep)', 'OCP')`, `require_extra('mesh', ...)`), the B-rep
provider's error types and messages, and its `CONTRACT`, now 2: the contract
names the error types `intersect_shapes` raises, and they are renamed. The
mesh contract names nothing renamed and stays 1.

**The leaf base, the capability, the memos.** `ExactLeafNode` is
`BrepLeafNode` at `machinome.node.brep_leaf`; the declared member `exact` is
`brep`; `machinome.node.leaf.CONTRACT` is 3, and a class declaring 2 is
refused naming 2 and 3. `machinome.exact_cache` and
`machinome.exact_artifacts` are `machinome.brep_cache` and
`machinome.brep_artifacts`, their functions unchanged.

**The run's engine.** `machinome test --brep` (the default) and `--mesh`;
`SOLID_TEST_ENGINE`, `brep` or `mesh`; `machinome.test.ENGINES`,
`ComparisonPolicy.engine`, `resolve_comparison_policy(engine=...)`; the run's
line, summary note and refusals say "the B-rep engine" and "the mesh engine".
The former variable `SOLID_TEST_KERNEL`, set to anything, is refused before
the engine is read, naming `SOLID_TEST_ENGINE`: a renamed module, flag and
extra each fail loudly by themselves, but a variable nobody reads would
silently move a checkout's runs to another engine.

**What persists, and what recomputes.** The verdict paths are `'brep'` and
`'mesh'`, and the store's record bit is `_BREP` (the same bit, so
`FORMAT_VERSION` stays 1); every project's store recomputes once, with no
migration code (ADR-156: a miss is the safe direction). The fusion recipes
are `brep-fusion-v1` and `mesh-fusion-v1:<sha256 of the children's
recipes>`; a mesh fusion's STL records its recipe, so it rebuilds once to the
same bytes, and a B-rep fusion's artifacts record none and are reused.

**The extras.** `occt` and `manifold` are `brep` and `mesh`, named by the last
component of the module that needs each (ADR-167); `cadquery`, `build123d`,
`step` and `molejo` include `machinome[brep]`; `all` names both.

**The gate.** A permanent token scan of `machinome/**/*.py`
(`tests/test_core_names_no_split_words.py`) finds no `faceted`; no `exact` as
a component of an identifier or a path, but for the ordinary identifiers it
lists by module; no `exact` in text where it names the split (the path word,
a flag or setting, the back-quoted member, `exactness`, or `exact` before a
closed list of nouns), but for four ordinary phrases by module; and no `occt`
or `manifold` outside the two provider modules and the four node modules
built on OCCT. It was red on 548 occurrences in 30 modules and is at zero.

Nothing aliases a former name (ADR-169): the four removed addresses fail with
Python's own `ModuleNotFoundError`, the former flags with argparse's exit 2,
the former extras with pip's own warning.

## Rejected Options

- **2:** the probe shows the first resolution replaces the function by the
  module, so the seam would destroy itself on first use.
- **3:** one namespace would hold core modules and provider modules alike,
  and every cut would have to tell them apart; the package's `__init__` is
  the one core module of the package.
- **4:** the lock names the identifiers; a reader of `ExactLeafNode` or
  `--faceted` would go on learning the words the lock retired.
- **5:** two addresses for one name is the shape ADR-169 forbids; an alias
  variable would make the rename invisible to a checkout until the alias is
  removed, and then silent.

## Consequences

- A second mesh engine is a package installing `machinome/engine/mesh.py`
  as a portion, with no edit of the core; one engine per role is installed at
  a time. Since the mesh fusion's recipe does not name its provider, that
  engine's arrival makes its identity part of the recipe.
- Every project importing a moved name fails to load until the root cleanup's
  rewrite applies the change's `moved-names.toml`; a checkout's `.env`
  setting `SOLID_TEST_KERNEL` is refused until renamed; a checkout that pulls
  the change runs `git clean -fdX machinome/occt machinome/manifold` once,
  since a directory holding only `__pycache__` imports as an empty namespace
  package.
- Verdicts, artifacts and goldens are bit for bit what they were: the deep
  validation of the lock, Prusa3-vanilla and OpenAstroMount found every
  verdict's answer identical but for its path word.
- machinome-freecad's retarget subclasses `BrepLeafNode` and declares leaf
  contract 3; machinome-studio's `machinome_test` tool and skills move to
  `--brep`/`--mesh` and `SOLID_TEST_ENGINE` when the line merges.
- The word `kernel` keeps its library sense (`kernel-extras`,
  `machinome.extras`, `machinome._verdict_store.KERNELS`), and `exact` its
  ordinary one.

## References

- [`brep-mesh` change](../../../openspec/changes/archive/2026-10-05-brep-mesh/): design Decisions 1 to 17, `moved-names.toml`, `evidence.md`
- `workflow/ongoing/lean-core.md`: "Locked at the session's close (pilot, 4 October 2026)", "The next phase: the architecture ready for the split"

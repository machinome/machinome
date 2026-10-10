## Why

The pilot's domain-modelling lock of 4 October 2026
(`workflow/ongoing/lean-core.md`, "Locked at the session's close", "The
engines are `brep` and `mesh`"): the two engines are named for the
representation each consumes, a boundary representation of parametric
surfaces and a polyhedral triangle mesh, not for a claim ("exact") or a
quality ("faceted"), and not for the library a provider happens to wrap
today (`occt`, `manifold`). The provider module carries the role
(`machinome.engine.brep`, `machinome.engine.mesh`), so one engine per role is
installed at a time and a second mesh engine is another package providing the
same module; the packages will be `machinome-engine-brep` and
`machinome-engine-mesh`. The same two words replace `exact`, `faceted` and the
providers' technology names everywhere the code uses them for this split.

"The next phase: the architecture ready for the split" makes this its second
cycle, after `openscad-out` (integrated 4 October, merge 04809f7; the line's
head is faf1c80), and before `root-cleanup`, whose single rewrite pass over the
projects applies this cycle's table. Counts on faf1c80 (design.md, Context):
the words occur in 30 of the core's Python modules, 548 occurrences by this
change's gate rule; 38 of the 45 baseline specs say `exact` or `faceted`
(the plan's "39 of 46" was taken before `openscad-out` removed two specs), of
which 22 use them for the split (18 changed in place, four renamed) and
four carry the split or a provider
technology in their names (`exact-engine-dependency`, `exact-geometry`,
`occt-engine`, `manifold-engine`); in the projects, three files of
3DPrintedClocks spell `--faceted` (plan, same section).

## What Changes

- **The acceptance gate**, a permanent test written red first: a token scan of
  `machinome/**/*.py` (identifiers, attribute names, strings, docstrings,
  comments, module paths) finding no `faceted` anywhere; no `exact` as a
  component of an identifier or a path, but for seven ordinary-sense
  identifiers listed by module; no `exact` in text where it names the split
  (the path word, a flag or setting, the back-quoted member, `exactness`, or
  `exact` before one of a closed list of nouns: `engine`, `geometry`, `leaf`,
  `cache`, ...), but for four ordinary phrases listed by module; and no
  `occt` or `manifold` outside the two provider modules and the four node
  modules built on OCCT. Red on faf1c80: 30 modules, 548 occurrences
  (design.md, Decision 9; `gate-prototype.py` in this change).
- **The engine package `machinome.engine`**: its `__init__` holds both seams
  and extends its path with portions, as `machinome.node` does. The seams are
  `brep_engine()`, `require_brep_engine()`, `BrepEngineUnavailable`,
  `BrepEngineIncompatible`, `BrepCommonInconsistency`,
  `BrepCommonVerificationError`, `BREP_CONTRACT = 2`, `BREP_PROVIDER`, and
  `mesh_engine()`, `require_mesh_engine()`, `MeshEngineUnavailable`,
  `MeshEngineIncompatible`, `MESH_CONTRACT = 1`, `MESH_PROVIDER`; not
  `brep()` and `mesh()`, because resolving `machinome.engine.brep` binds the
  provider module over a seam function of that name (probe, design.md
  Decision 2).
- **The providers** move unchanged in behaviour to `machinome/engine/brep.py`
  (from `machinome/occt/engine.py`, contract 2) and `machinome/engine/mesh.py`
  (from `machinome/manifold/engine.py`, contract 1).
- **The B-rep leaf base** `ExactLeafNode` (`machinome.node.exact_leaf`) is
  `BrepLeafNode` (`machinome.node.brep_leaf`); the declared capability `exact`
  (ADR-178) is `brep`; the leaf contract goes to **`CONTRACT = 3`** (ADR-165:
  a renamed declared member).
- **The memos and publication** `machinome.exact_cache` and
  `machinome.exact_artifacts` are `machinome.brep_cache` and
  `machinome.brep_artifacts`.
- **The test framework**: the paths and values `'exact'`/`'faceted'` are
  `'brep'`/`'mesh'`; the run's choice is its engine, not its kernel (the
  pilot's ruling at ratification, design.md Open Question 2): `KERNELS` is
  `ENGINES`, `ComparisonPolicy.kernel` is `.engine`, the `kernel` argument of
  `resolve_comparison_policy` and of `machinome test`'s parser is `engine`,
  and `SOLID_TEST_KERNEL` is `SOLID_TEST_ENGINE`; `IntersectionStats.exact`
  is `.brep`; every message says "the B-rep engine" / "the mesh engine"
  (design.md, Decision 13, the refusal texts before and after). The word
  `kernel` keeps its library sense (OCCT, manifold3d; `kernel-extras`).
- **The recipe identities** of fusion are `brep-fusion-v1` and
  `mesh-fusion-v1:<sha256>`.
- **The extras** `occt` and `manifold` are `brep` and `mesh` (ADR-167: an
  extra is named by the last component of the module that needs it);
  `cadquery`, `build123d`, `step` and `molejo` include `machinome[brep]`; `all`
  names `brep` and `mesh`.
- **BREAKING (command line):** `machinome test --exact` and `--faceted` are
  `--brep` and `--mesh`; the environment variable `SOLID_TEST_KERNEL` is
  `SOLID_TEST_ENGINE`, which takes `brep` or `mesh`, and the former values
  are refused naming the variable and the two accepted values;
  `SOLID_TEST_KERNEL`, when set, is refused naming `SOLID_TEST_ENGINE`
  rather than ignored, since an ignored variable would silently move a
  checkout's mesh runs to the B-rep engine (design.md, Decision 6).
- **BREAKING (install):** `machinome[occt]` and `machinome[manifold]` are
  `machinome[brep]` and `machinome[mesh]`; pip warns about an unknown extra and
  installs nothing for it.
- **BREAKING (framework API):** the seams' and providers' addresses, the leaf
  base's name and module, the capability flag, the memo and publication
  modules, the error types; nothing aliases a former name (ADR-169).
  `moved-names.toml` lists all of them.
- **BREAKING (persisted state, once):** every project's verdict store
  recomputes once, because its keys carry the path words and its stamp digests
  the package's sources (ADR-156; no migration code, ratified by the pilot);
  every mesh fusion's STL rebuilds once, byte-identical, because its recorded
  recipe changes. B-rep fusion artifacts and every leaf artifact are reused.

Not in this change: the projects' rewrite (the root cleanup's single pass
applies this table; 3DPrintedClocks' three `--faceted` files; the Curta's own
`faceted` parameter names, which stay theirs), `jscad` and `stl` as packages,
the viewer seam, the package split (no distribution is cut), the licence,
the word `kernel` in its library sense, and anything else the pilot did not
lock. The studio's `machinome_test` tool and skills, and the workspace's
simulate-project skill, still pass `--faceted`/`--exact` (and the studio's
skill spells `SOLID_TEST_KERNEL`): follow-ups recorded in design.md, not
this cycle's edits.

## Capabilities

### New Capabilities

- `brep-engine-dependency`: the B-rep engine as a conditional, versioned
  dependency of the core, through its seam in `machinome.engine`. Takes the
  content of `exact-engine-dependency`, which the archive task removes.
- `brep-geometry`: the node's `brep` capability, `shape()`, B-rep fusion,
  persistence, precision and admission. Takes the content of `exact-geometry`.
- `brep-engine`: the provider `machinome.engine.brep` (OCCT), contract 2.
  Takes the content of `occt-engine`.
- `mesh-engine`: the provider `machinome.engine.mesh` (manifold3d). Takes the
  content of `manifold-engine`.

### Modified Capabilities

- `kernel-extras`: the `brep` and `mesh` extras; the providers as modules of
  one engine package admitting portions (new requirement).
- `mesh-engine-dependency`: the seam in `machinome.engine`, the provider's
  address, the `mesh` extra, the mesh run's words.
- `leaf-contract`: `BrepLeafNode`, the member `brep`, `CONTRACT = 3`.
- `test-framework`: the run's engine (`SOLID_TEST_ENGINE`, the requirement
  "Run-level comparison engine"), its values, flags and messages; the
  former variable refused; the B-rep and mesh paths; the verdict store's
  path words.
- `cli`: `--brep` / `--mesh`, `SOLID_TEST_ENGINE`, the former selectors and
  variable refused.
- `cli-startup-cost`, `build-pipeline`, `backend-neutral-materialization`,
  `node-model`, `flexible-parts`, `markings`, `step-import`, `stl-import`,
  `openscad-dependency`, `openscad-node`, `vet`, `user-documentation`
  (with "The comparison engines are documented"), `web-snapshot`: the words
  and addresses, behaviour unchanged.

Removed (by the archive task, design.md Decision 11): `exact-engine-dependency`,
`exact-geometry`, `occt-engine`, `manifold-engine`.

## Impact

- **Code.** New: `machinome/engine/__init__.py`, `machinome/engine/brep.py`,
  `machinome/engine/mesh.py`, `machinome/node/brep_leaf.py`,
  `machinome/brep_cache.py`, `machinome/brep_artifacts.py`. Removed:
  `machinome/exact_engine.py`, `machinome/mesh_engine.py`, `machinome/occt/`,
  `machinome/manifold/`, `machinome/node/exact_leaf.py`,
  `machinome/exact_cache.py`, `machinome/exact_artifacts.py`. Changed: the 30
  modules of the gate's red count, `machinome/vet/universe.toml`,
  `pyproject.toml`, `requirements.txt`, `setup.cfg`.
- **Tests.** 78 test files name a moved name (grep of faf1c80); the test
  modules whose names carry the words are renamed, the fixture projects keep
  theirs (design.md, Decision 12); the goldens' data are not re-recorded.
- **Projects.** Every project importing a moved name fails to load until the
  root cleanup's rewrite; the universe sweep shows them as `expected`,
  explained by `moved-names.toml`; the orchestrator's grep sizes them.
- **Sibling repositories.** machinome-studio's `machinome_test` tool
  (`floor/mcp_server.py:978-985`) and its two skills, and the workspace's
  `skills/simulate-project/SKILL.md`, spell the former flags (follow-ups).
- **Docs.** `docs/architecture.md`, the install, fast-tests, backends,
  fusion, imported-parts, CLI, API, assertions and upgrading pages (the
  flags, the extras and `SOLID_TEST_ENGINE`),
  `README.rst`, the changelog's Unreleased section, the campaign plan.

Originating evidence: `workflow/ongoing/lean-core.md`, "Locked at the
session's close (pilot, 4 October 2026)", "Every node type is a package"
("Engines are named as engines"), "The next phase: the architecture ready for
the split" (this cycle's entry and its counts) and "State of the campaign"
(the update at the eighth cycle's integration: the `__pycache__` leftover of a
deleted package); the pilot's lock of 4 October 2026.

# ADR-183: An Extension Package Is a Namespace Portion in Its Own Distribution

**Status:** Accepted; a node package refused by its extra's name at its import, amended 2026-10-10 by [ADR-184](../NODE/ADR-184-an-absent-node-package-is-refused-by-its-extra-at-its-import.md); a product of a repository of its own joining as an extension package, amended 2026-10-11 by [ADR-185](../NODE/ADR-185-a-node-type-may-read-a-whole-assembly-through-an-external-program.md)
**Date:** 2026-10-10
**Change:** [`cut-the-engines`](../../../openspec/changes/archive/2026-10-10-cut-the-engines/)
**Amends:**
- [NODE/ADR-167: A kernel is an extra, and its module refuses its absence at import](../NODE/ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md): the `brep` and `mesh` extras name the engines' distributions, which state the kernels
**Related to:**
- [ADR-182: The repository is a monorepo of distributions, each named by its directory](ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md): the layout this one fills with its first extension packages
- [NODE/ADR-180: The engines are named for the representation each consumes](../NODE/ADR-180-the-engines-are-named-for-the-representation-each-consumes.md): the engine package whose path admits a portion; the resolution, ADR-169's and ADR-180's, does not change

## Context and Problem Statement

The plan for Machinome 0.9 (`workflow/ongoing/monorepo-0.9.md` at the
repository root, accepted by the pilot on 10 October 2026) cuts the
framework's modules into extension packages, and its decisions bind how: the
record of an extension package is the framework's, so an extension package
carries its manifest, its source and a README (1); one version for the whole
set, `~=` pins both ways, the contract numbers at the seams the real guard
(2); a uv workspace at the root, every member editable in compat mode (3).

The core's engine seams were written for the cut: `machinome.engine` names
each provider by string, reads its absence as an absent engine refused by
its extra's name, and extends its path with every portion on `sys.path` that
holds no `__init__.py` of its own (`machinome._namespace_portions`). No
distribution had ever shipped a portion, so that path, the editable compat
mode and the pins were untested on a real install.

This decision is BUILD rather than NODE: it decides how a module is
distributed, installed, versioned and checked, beside ADR-130 and ADR-182.

## Considered Options

1. **Each extension package a namespace portion in its own distribution
   under `packages/`, with no `__init__.py` at the levels the core defines**
   (chosen)
2. The engines as regular packages under another import name, the core
   re-exporting them: refused, since the address is the location and the
   plan's rule forbids a second spelling
3. The core shipping every module and the extras only pulling kernels, as in
   0.8: refused by the plan, whose purpose is the cut

## Decision Outcome

**An extension package is a directory with four things.** It is
`packages/<distribution>/`, holding its manifest `pyproject.toml`, a
`README.md` naming its install line and the licence, the root's licence by
the relative links `LICENSE` and `LICENSES`, and its portion at its address:
`packages/machinome-engine-brep/machinome/engine/brep.py`. It holds no
`__init__.py` under `machinome/` or any level the core defines; the core's
are the package, and a portion's own would make it another copy of the core,
which the path extension refuses. Its specs, tests, decision records and
manual pages are the framework's.

**The core's path extension resolves it; the seam refuses its absence.**
Installed from its wheel, the portion's file lands in the core's
`machinome/engine/` directory, owned by its own distribution; installed
editable, its directory is on `sys.path` and the core's `__path__` admits
it. When the distribution is absent the seam answers `None` and refuses
naming the extra that installs it, as it did for an absent kernel.

**One version, pinned both ways, bumped from the root.** It carries the
set's version. The core's extra that installs it requires it as
`~=<version>`, and it requires the core as `~=<version>`; the root's
`.bumpversion.cfg` names every manifest's version and every pin, and
`tests/test_release_records.py` holds them to the core's. Its kernel ranges
are stated in its own manifest: the OCCT range in `machinome-engine-brep`'s
alone.

**The workspace installs it, and `check-dist` proves it.** The root
manifest names it as a workspace source, and the sync installs it editable
in compat mode. `scripts/check-dist` builds it, installs it into a throwaway
environment through the core's extra from the built archives, and smokes it
through the seam: the provider resolved, its file owned by its distribution,
one operation on its kernel, its version the core's, its licence texts.

### Consequences

- Good: every import and install line a project writes is unchanged;
  `pip install "machinome[brep]"` installs the B-rep engine from its own
  distribution.
- Good: the eight node packages of the later cycles take the same shape
  with no new mechanism; the lint and the scans read `packages/machinome-*`.
- Neutral: installed from wheels, the portion's file shares the core's
  directory and is removed with its own distribution, not with the core.
- Neutral: CI installs the set with uv from the lock, which a stale lock
  fails; the requirements files and tox, which could not install the set,
  are retired.
- Neutral (2026-10-10, `cut-the-mesh-nodes`): a portion may be a package
  directory at its address, its own `__init__.py` below the levels the core
  defines, and its manifest's `include` names that package; with the four
  node packages over no B-rep engine every node type of the table is a
  package, and the core imports none.
- Neutral (2026-10-11, `join-freecad`): a product of a repository of its own
  joins as an extension package of the same shape, its history imported to
  its final paths and its record folded into the framework's.
- Bad: an environment whose `PYTHONPATH` names the core's directory alone,
  with no install of the engines, has no engine: the fallback recipe of the
  first cycle no longer runs the whole suite.
- Bad: `pip install "machinome[brep]"` from an index needs
  `machinome-engine-brep` published with the core; the set is released
  together.

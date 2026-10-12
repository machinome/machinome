# ADR-187: The Mechanics Helpers Are a Portion of the Repository at Their Own Version

**Status:** Accepted
**Date:** 2026-10-12
**Change:** [`join-mechanics`](../../../openspec/changes/archive/2026-10-12-join-mechanics/)
**Supersedes:**
- [MATH/ADR-132: Mechanics helpers release independently](../MATH/ADR-132-mechanics-helpers-release-independently.md), in its import path (`machinome_mechanics`) and its repository; its ownership of the formulas, their conventions, tests and specification by the mechanics package, and the framework's independence from them, stand
**Amends:**
- [ADR-182: The repository is a monorepo of distributions, each named by its directory](ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md): a product that joined from a repository of its own and is not an extension package keeps its record in its directory
- [ADR-183: An extension package is a namespace portion in its own distribution](ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md): a member of the repository not numbered with the set, outside `.bumpversion.cfg`, smoked from its own wheel
**Related to:**
- [MATH/ADR-076: Mechanism laws as compositions over expression math](../MATH/ADR-076-mechanism-laws-as-compositions-over-expression-math.md): the formulas' two faces over `machinome.math`, unchanged
- [ADR-149: Vet checks a project against a versioned universe, statically, and the adapters contain their sources](ADR-149-vet-checks-a-project-against-a-versioned-universe.md): the contract tier is `machinome` and `molejo`; the helpers lie beneath `machinome`
- [MATH/ADR-170: The core's symbolic value is its own type](../MATH/ADR-170-the-core-s-symbolic-value-is-its-own-type.md): the framework's own symbolic value, which the helpers' tests read through `machinome.expression_graph`

## Context and Problem Statement

The plan for the joins of Machinome 0.9 (`workflow/ongoing/joins-0.9.md` at
the repository root, set by the pilot on 11 October 2026) brings
machinome-mechanics into the repository as its second join. The package was
published as 0.1.0 on 26 September 2026 from a repository of its own:
twenty-four kinematic formulas in nine family modules over `machinome.math`,
imported as `machinome_mechanics`, with its own Sphinx manual on Read the
Docs, three specs and sixteen archived changes.

On 12 October 2026 the pilot settled three decisions: the import is
`machinome.mechanics`, a portion of the `machinome` namespace as
`machinome.node.freecad` is, with no module of the former name; its manual
folds into the framework's one manual; and it keeps its own version, 0.1.0,
outside the set's one-version rule. The plan adds that a product which is
not an extension package keeps its record in its directory.

On the line's head the product does not run against the framework it joins:
its suite collects with 2 errors and fails 38 tests (design.md of the change,
probe 1), because two tests import `AssemblyNode` from the node root and
every symbolic check takes its time from SolidPython, whose value the core
reads as symbolic only once a node package adopts it. Fourteen import lines
bring its 201 tests green (probe 2), and 195 of them pass on published
Machinome 0.8.0 (probe 3). uv does not check a requirement's specifier
against a workspace member's version (probe 10), and pip, asked for
`machinome-mechanics>=0.1.0` beside the built wheel, chooses the published
wheel of the same version, whose import is the former one (probe 11).

## Considered Options

1. **A portion of the `machinome` namespace at its own version, its record in
   its directory** (chosen)
2. The set's version, 0.8.1 now and renumbered with the set; refused by the
   pilot on 12 October 2026
3. The import `machinome_mechanics` kept; refused by the pilot on 12 October
   2026
4. An extension package whose record folds into the framework's; refused by
   the plan, under which a product keeps its record
5. Installed through the `mechanics` extra by `scripts/check-dist`; refused
   by probe 11, since pip may take the published wheel of the former import

## Decision Outcome

**The package is `machinome.mechanics`.** The distribution
`machinome-mechanics`, at `packages/machinome-mechanics/`, ships the package
directory `machinome/mechanics/` with its own `__init__.py` and the nine
family modules, and none at `machinome/`; the core's path extension admits
it. No module of the former name, and no alias, is provided. Names,
signatures and formulas are unchanged.

**Its record is in its directory.** Beside the package the directory holds
its manifest, README, `CHANGELOG.md`, `MANIFEST.in`, `.gitignore`, the links
`LICENSE` and `LICENSES` to the root's, its `tests/`, its `openspec/` (specs
and archived changes) and its `workflow/`. Its tests run from that directory,
in a step of CI's test job; the core's suite does not collect them. Its
manual is the exception: the reference section `reference/mechanics/` and
the how-to `howto/mechanism-formulas` of the framework's manual, whose
examples the package's tests run.

**It carries its own version.** The manifest states 0.1.0; no table of
`.bumpversion.cfg` names it; `tests/test_release_records.py` holds it to its
changelog's newest release and to the manual's `mechanics_version`. The
package requires `machinome>=0.8.0` and the core's `mechanics` extra
requires `machinome-mechanics>=0.1.0`: floors that the versions in the tree
satisfy, held by that test since uv does not check them.

**The core never imports it.** The boundary test's guard refuses the dotted
address `machinome.mechanics` and every name beneath it, and a positive
control proves the guard refuses an explicit import. The vet universe's
contract is `machinome` and `molejo`: the helpers are inside beneath
`machinome`, and the former name, which no package of the set installs, is
outside.

**It is smoked from its wheel.** `scripts/check-dist` builds it and installs
its wheel by path, then checks its ten modules owned by its distribution
inside the throwaway environment, its version, its requirement, the core's
extra naming it, a numeric pose and a deferred expression from the
framework's animation time, and its licence texts.

### Consequences

- Good: one address, `machinome.mechanics`, one install line,
  `pip install "machinome[mechanics]"`, and one manual whose examples run.
- Good: each module's history reads at its new path back to the founding
  commit of 11 September 2026.
- Bad: the extra's floor admits the published 0.1.0 of the former import
  until a release moves the package's version and the floor past it.
- Bad: uv does not check the two floors; the release-records test and
  `scripts/check-dist` do.
- Bad: twenty-seven project repositories rename an import.
- Neutral: the core never imports the helpers, as before.

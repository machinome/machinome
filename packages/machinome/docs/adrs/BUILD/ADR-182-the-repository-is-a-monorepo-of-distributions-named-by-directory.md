# ADR-182: The Repository Is a Monorepo of Distributions, Each Named by Its Directory

**Status:** Accepted; a product of a repository of its own keeping its record in its directory, amended 2026-10-12 by [ADR-187](ADR-187-the-mechanics-helpers-are-a-portion-of-the-repository-at-their-own-version.md); an npm workspace at the root, amended 2026-10-12 by [ADR-188](ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md); each member's direct dependencies beside it, amended 2026-10-12 by [ADR-191](ADR-191-the-videomaker-is-a-product-of-the-set-its-node-side-installed-by-its-command.md); the Makefile of the repository's steps at the root, amended 2026-10-12 by [ADR-192](ADR-192-the-repository-s-steps-are-the-targets-of-one-makefile.md)
**Date:** 2026-10-10
**Change:** [`monorepo-layout`](../../../openspec/changes/archive/2026-10-10-monorepo-layout/)
**Related to:**
- [ADR-130: Machinome is a clean package and command boundary](ADR-130-machinome-is-a-clean-package-and-command-boundary.md): fixed the distribution, the import package, the command and the repository; this one fixes where in the repository the distribution lives and what the repository's root holds
- [IPC/ADR-018: Lean framework separation](../IPC/ADR-018-lean-framework-separation.md): the viewer a separate distribution reached as a separate process; a later join moves its tree into its own directory, and the boundary stays

## Context and Problem Statement

On 10 October 2026 the pilot set the direction of Machinome 0.9: the
machinome repository becomes a monorepo of several packages, every one under
the one licence the framework carries, and the first step is the cut of the
framework's own modules into the ten extension packages the lean-core
campaign locked (`workflow/ongoing/monorepo-0.9.md` at the repository root).
The plan's four decisions, accepted that day, bind the layout: the record of
an extension package is the framework's (1); one version for the whole set
(2); a uv workspace at the root, setuptools kept, every member installed
editable in compat mode (3); today's tree moves in the first cycle (4).

Until this change the framework's tree was the repository root. There was no
place for a second distribution, and the licence, the history, the CI and
the record of a campaign that spans packages had no home that was not the
framework's.

## Considered Options

1. **The framework under `packages/machinome/`, the root the repository's**
   (chosen)
2. The framework stays at the root and its siblings go under `packages/`: the
   root's record would be the framework's, and a second product's record
   would sit inside it, against the plan's rule "a record lives with what it
   records"
3. One repository per distribution: refused by the plan, since the eleven
   distributions are one product with one release

## Decision Outcome

**A directory per distribution.** Each distribution of the repository lives
in a directory under `packages/` named as the distribution it builds. The
framework, the distribution `machinome`, is `packages/machinome/`, with its
import package, tests, manual, architecture synthesis, decision records,
OpenSpec records and working record. Paths in the framework's records are
relative to that directory unless they name the repository root.

**The root is the repository's.** It holds the licence (`LICENSE`,
`LICENSES/`), the contributor guide, the AI-use statement, the history, the
CI workflow, `scripts/`, `context7.json`, a `README.md` naming each package,
and the record of the campaigns that span products under `workflow/`. Each
product's record is in its directory.

**One licence, stated once.** The licence texts are at the root only. Each
package directory reaches `LICENSE`, `LICENSES`, `HISTORY.rst`,
`CONTRIBUTING.rst` and `AI-USE.md` through relative symbolic links
(`../../<name>`). setuptools carries a linked file into the sdist and the
wheel as a regular file with the target's bytes, so the archives built from
the package directory are the archives built before the layout;
`scripts/check-dist` compares those bytes on every build.

**A uv workspace at the root, virtual.** The root `pyproject.toml` declares
`[tool.uv.workspace] members = ["packages/*"]`, maps each member to the
workspace in `[tool.uv.sources]`, and has no `[project]` table: the root is no
distribution. Every member installs editable in compat mode, set once in the
root's `[tool.uv] config-settings`, because setuptools' lenient editable
finder declares a namespace portion's packages through a path hook that
shadows the core's own package, and uv reads that setting at the workspace
root only. Products no index serves are excluded from the lock by name
(`exclude-dependencies`), since uv locks every extra of every member; each
leaves the list when an index serves it. The default `dev` group names the
core's `dev` extra, so `uv sync` at the root installs every kernel the suite
runs. setuptools stays the build backend, and publishing does not change.

**The archives are proved where CI runs.** `scripts/check-dist` builds every
member outside the repository, checks both archives with `twine check
--strict`, installs the wheels into a throwaway environment and smokes each,
and uploads nothing; the CI's `dist` job runs it after `test` and `docs`.

### Consequences

- Good: a later product joins as a plain move into its own directory, and
  each extension package of the cut is a sibling directory.
- Good: the licence and the history have one copy each, and the archives
  carry them unchanged.
- Neutral: the suite, the lint and the OpenSpec command run from
  `packages/machinome/`; a bench is synced with uv at its root.
- Neutral: Read the Docs reads a configuration path per project; the
  framework's sits beside its manual and names the manual's paths from the
  repository root. The project setting is the pilot's, at release.
- Neutral (2026-10-12, `join-mechanics`): a product of a repository of its
  own may join with its record in its directory and its own version
  (ADR-187).
- Neutral (2026-10-12, `join-viewer`): the browser viewer joined as a
  product numbered with the set; the root holds an npm workspace (ADR-188).
- Neutral (2026-10-12, `join-movie`): the root's `.npmrc` installs each npm
  member's direct dependencies in its own `node_modules` (ADR-191).
- Bad: a clone without symbolic-link support checks the five links out as
  text files; the framework's development is on Linux.
- Bad: the editable lenient mode is unfit for namespace portions, so a
  contributor installing without uv must ask for compat mode once a portion
  exists.

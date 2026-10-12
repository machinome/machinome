# ADR-192: The Repository's Steps Are the Targets of One Makefile at Its Root

**Status:** Accepted
**Date:** 2026-10-12
**Change:** [`release-tooling`](../../../openspec/changes/archive/2026-10-12-release-tooling/)
**Related to:**
- [ADR-182: The repository is a monorepo of distributions, each named by its directory](ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md): amended; the root also holds the `Makefile` of the repository's steps, and the CI runs `scripts/check-dist` through it
- [ADR-183: An extension package is a namespace portion in its own distribution](ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md): amended; the set's version is declared once, as `current_version` of the root's `.bumpversion.cfg`, and `make bump` moves it without committing or tagging
- [ADR-187: The mechanics helpers are a portion of the repository at their own version](ADR-187-the-mechanics-helpers-are-a-portion-of-the-repository-at-their-own-version.md): their own version stays outside the bump
- [ADR-188: The browser viewer is a product of the repository, numbered with the set](ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md): the npm workspace whose lock the bump moves and whose bundle `make widget` builds

## Context and Problem Statement

Machinome 0.8.1 was released by hand on 10 October 2026: the framework's
sdist and wheel built into the framework checkout's `dist/0.8.1-2026-10-10/`,
the viewer's into its own repository's, checked by no script, and the steps a
checklist in the framework's working record (`workflow/ongoing/release-0.8.1.md`).
The repository then held fifteen distributions, sixteen with the movie, and
four products with tests of their own. The commands a contributor runs were
spelled in three places that differed: `CONTRIBUTING.rst`, the framework's
cookiecutter `packages/machinome/Makefile` (whose `release` target built and
ran `twine upload dist/*`) and the CI workflow, each job's commands written
out. The version was stated in twenty files and two locks, read by the
release-records test from the core's manifest, and `.bumpversion.cfg` told
bump2version to commit and tag.

On 12 October 2026 the pilot decided (`workflow/ongoing/release-0.9.md` at
the repository root, decisions 2 and 10) that 0.9.0 is released with one
command per step, declared once: a Makefile at the root, the version declared
in one place and bumped from it, `scripts/check-dist --out dist/vX.Y.Z`
keeping the archives it proved, CI on the same targets, the layout gate
reading the Makefile's package list, no sweep target and no target that
chains the build and the upload.

The change's probes (design.md) found:

- `scripts/check-dist` at 40087800 did not parse: a merge had lost the brace
  that closed the viewer's smoke row (probe 1).
- `scripts/check-dist --out` prototyped on a clean copy kept 30 archives
  flat, all passing `twine check --strict` (probe 2).
- `bumpversion --no-commit --no-tag --new-version 0.9.0 patch`, `npm install
  --package-lock-only` at the root and in a copy of the movie's `js`, and
  `uv lock` moved every copy and lock and committed nothing (probe 3).
- An sdist built from a checkout carries the checkout's ignored build
  directories: the 0.7.1 sdist kept in the framework checkout holds 246
  entries of `tests/_build*` and 10 of `docs/_build/`; built from `git
  archive HEAD` it holds none (probe 9).

## Considered Options

1. **One `Makefile` at the root**, its targets the steps, the packages
   declared in it, CI calling it (chosen)
2. A task runner other than make (`just`, `nox`, `tox`): one more tool to
   install before the first step, where make is on every Linux and macOS
   development machine and on `ubuntu-latest`
3. Scripts under `scripts/`: a file per step and no list of the steps; the
   help, the package list and the guard against chaining would each be
   written again
4. The steps left in the contributor guide: the state that was the
   finding, three spellings that drifted

## Decision Outcome

**The targets.** The root `Makefile` has the targets `help` (the default,
one line per target), `version`, `bump VERSION=`, `sync`, `test [PKG=]`,
`lint`, `docs`, `widget`, `dist`, `upload`, `check` and `clean`, and no
other target with a help line; none runs the universe sweep. It runs one
step at a time under `-j`, finds `uv` and `npm` on the PATH and the
workspace's commands in the root's `.venv/`, so every target runs from a
fresh clone after `make sync` without an activated environment. It declares
the packages once, `PACKAGES`, every directory under `packages/`, and the
packages with tests of their own, `TESTED`, the core and every product; the
layout test holds both to the tree. `make test PKG=` refuses an extension
package, naming the core's suite, which tests it. The framework's
directory holds no Makefile.

**The version, declared once.** `current_version` of `.bumpversion.cfg` is
the declaration; every manifest numbered with the set, every pin, the files
that restate the version and the npm and uv locks are copies the
release-records test holds to it. The cfg's `[bumpversion]` section holds
`current_version` alone. `make bump VERSION=X.Y.Z` refuses an absent or
unchanged version and a tree whose tracked files have changes, then moves
every copy with bump2version (`--no-commit --no-tag`), the root's npm lock
and each npm member's own lock with npm, and `uv.lock` with uv, and lists the
files. It never commits and never tags.

**The archives proved are the archives uploaded.** `scripts/check-dist
--out DIR` refuses a `DIR` that exists and is not an empty folder before it
builds, and copies every sdist and wheel, flat, into `DIR` once every check
and smoke has passed; a failure keeps nothing. `make dist` refuses a
checkout whose `git status` lists a file, then runs it with `--out
dist/v<current_version>` on a copy of the checked-out commit outside the
repository, so no ignored build directory enters an archive. `make upload`
runs `twine upload dist/v<current_version>/*` and nothing else, refusing an
absent or empty folder; it has no prerequisite, no rule depends on `dist` or
`upload`, and no other recipe runs `twine upload`. `make check` runs the
script on the tree and on a clean copy of the tracked files and keeps
nothing. `make clean` removes only what the targets write and Git ignores,
never `.venv/`, an npm install or `dist/`.

**CI on the targets.** Each job keeps its setup steps and runs the targets:
`make lint`; `make widget` and, after Chromium, `make test`; `make widget`
before the browser capture; `make docs`; `make check`; and on a tag, after
checking that the tag is `v` and `make version`'s output, `make dist`,
whose folder is attached to the tag's GitHub release. No job spells a
command a target runs.

### Consequences

- Good: a contributor, CI and the pilot run the same command for each step,
  and the gate fails when the Makefile and the tree disagree.
- Good: the archives a release uploads are the bytes built from its commit,
  checked, installed and smoked, kept in one folder per release.
- Good: the version moves in one command that changes files and nothing
  else.
- Bad: `make check` builds the set twice in CI's slowest job, about seven
  minutes on the development machine.
- Bad: CI no longer reports coverage; it had no threshold and no reader, and
  `coverage` stays in the dev extra.
- Neutral: a contributor without make or uv still has the guide's install
  with pip and pytest from a package's directory.

## References

- `Makefile`, `.bumpversion.cfg`, `scripts/check-dist`,
  `.github/workflows/python-app.yml`, `CONTRIBUTING.rst` at the repository
  root
- `tests/test_repository_layout.py` (`TheMakefileTest`, the CI tests),
  `tests/test_check_dist.py`, `tests/test_release_records.py`,
  `tests/test_docs_exports.py`
- `openspec/specs/release-tooling/spec.md`,
  `openspec/specs/framework-identity/spec.md`

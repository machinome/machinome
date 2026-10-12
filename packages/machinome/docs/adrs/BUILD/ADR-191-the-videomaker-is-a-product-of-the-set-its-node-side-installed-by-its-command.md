# ADR-191: The Videomaker Is a Product of the Set, Its Node Side Inside Its Portion and Installed by Its Command

**Status:** Accepted
**Date:** 2026-10-12
**Change:** [`join-movie`](../../../openspec/changes/archive/2026-10-12-join-movie/)
**Amends:**
- [ADR-182: The repository is a monorepo of distributions, each named by its directory](ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md): the root's npm workspace installs each member's direct dependencies beside it (`.npmrc`, `install-strategy=shallow`)
- [ADR-188: The browser viewer is a product of the repository, numbered with the set](ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md): the npm workspace's second member, which keeps a lock of its own beside the root's
**Related to:**
- [ADR-187: The mechanics helpers are a portion of the repository at their own version](ADR-187-the-mechanics-helpers-are-a-portion-of-the-repository-at-their-own-version.md): the products table; this product keeps its record in its directory
- [ADR-189: A package contributes a command through the group `machinome.commands`](ADR-189-a-package-contributes-a-command-through-the-group-machinome-commands.md): `machinome movie` is the group's first contributor
- [ADR-190: The machinome skills are a package of the set, installed into assistants' directories by a command](ADR-190-the-machinome-skills-are-a-package-of-the-set-installed-by-a-command.md): the second

## Context and Problem Statement

On 12 October 2026 the pilot settled how the videomaker joins the repository
(`workflow/ongoing/release-0.9.md` at the repository root, decisions 1 to 5
and 9): one member, the distribution `machinome-movie` at
`packages/machinome-movie/`, the portion `machinome.movie` with its Node side
inside it at `machinome/movie/js/`, at the set's version pinned `~=` both
ways and installed by `machinome[movie]`, under the set's licence; one
command, `machinome movie`, the first contributor of `machinome.commands`,
with the verbs `list`, `evaluate`, `watch`, `check`, `speech`, `preview`,
`render`, `build`, `live`, `review` and `setup`, no `--viewer` option; Node
22 or newer the user's, found on the `PATH` or named by `MACHINOME_NODE`;
`machinome movie setup` installing the Node dependencies into the package's
own JavaScript directory in the environment that owns it, never into a
cache; distribution by pip alone.

Before the join the videomaker was a private repository with two command
lines, `python -m machinome_movie` and `node bin/videomaker.mjs`, which took
the viewer's bundle by path; its Node side read its packages from its own
`node_modules` (its own ADR-013 names every bundled file by the tool).

The change's probes (design.md) found:

- npm's default layout for the root workspace with the movie as a second
  member (probe 6) splits the movie's packages between the root and its own
  `node_modules`, its esbuild, TypeScript, vitest and jsdom differing in
  major from the widget's: the stage build, which reads React from the
  tool's own directory, and three tests fail on the layout itself.
- A root `.npmrc` with `install-strategy=shallow` (probe 7) keeps every one
  of the viewer's 176 resolutions and puts each member's direct
  dependencies in its own `node_modules`; `npm ci` reproduces it. The Node
  suite runs on it with the movie's records at their new paths (probe 8).
- A member's lock is ignored inside the workspace and read outside it
  (probe 10); `npm ci --omit=dev` refuses without one (probe 11).
- The package built and installed from its wheel (probe 11): 77 entries,
  `setup` installs 14 packages, 81 MB, into the installed package's
  `js/node_modules`; `pip uninstall` leaves them behind.
- The package root's eager imports cost `machinome -h` 63 ms and `machinome
  movie -h` 126 ms; read lazily, 19 ms and 72 ms (probe 14).

## Considered Options

1. **One member at `machinome.movie`, its Node side as package data,
   installed by `machinome movie setup` from a lock of its own into the
   installed package's directory, the repository's checkout installed by
   the root's `npm ci` with each member's direct dependencies beside it**
   (chosen)
2. The Node side a separate npm package: refused by the pilot, pip only
3. The dependencies installed into a cache outside the package: refused by
   the pilot
4. npm's default layout and the tool reading its packages through Node's
   lookup: refused by probe 6, three tests and the bundle's names rewritten
   for an install detail
5. The dependencies vendored into the wheel: refused, 81 MB of other
   people's platform binaries per platform

## Decision Outcome

**The package.** `packages/machinome-movie/` holds its manifest, a README,
its changelog, `MANIFEST.in`, `.gitignore`, the links `LICENSE` and
`LICENSES` to the root's, the package directory `machinome/movie/` (no
`__init__.py` at `machinome/`), `tests/`, `openspec/`, `workflow/` (its own
decision log under `workflow/adrs/`, under its own numbers) and
`experiments/`. It carries the set's version, requires
`machinome~=<version>`, `machinome-viewer~=<version>` and `jsonschema`, is
required by the core's extra `movie` with the same pin, and is named by
`.bumpversion.cfg` with its JavaScript directory's `package.json`. Its wheel
carries the modules, `cli.py`, the schema as a regular file, and the Node
side's manifest, lock, command and sources (`js/bin/`, `js/src/`,
`js/stage/`, `js/player/`, `js/transport/`, `js/schema/`), named in its
`package-data`; the Node suite, its fixtures and scripts travel in the sdist
alone. Its root reads each exported name from its module on first use. No
module `machinome_movie` is provided; the core never imports the package,
and `machinome vet` denies it to a model.

**The command.** `machinome movie` declares `movie =
"machinome.movie.cli:Movie"` in `machinome.commands`; `python -m
machinome.movie` runs the same parser. `list`, `evaluate` and `watch` run in
Python. The film verbs run `js/bin/videomaker.mjs` with the Node named by
`MACHINOME_NODE`, else the `PATH`'s, 22 or newer, the user's working
directory, environment and streams, and exit with its status; a source is
an episode, a movie document, or a project directory and a movie name,
evaluated first; `check`, `preview`, `render`, `build` and `live` give it
the installed viewer's bundle through the `machinome.viewer` entry point, as
`machinome develop` finds it. Every refusal is one line naming the line to
run.

**The Node side's installation.** `setup` runs `npm ci --omit=dev` from the
package's own `js/package-lock.json` into `js/node_modules` of the installed
package, with the npm beside the Node it found, and prints Playwright's
Chromium as the second step; `setup --remove` deletes that directory. Both
refuse in a source checkout, where the JavaScript directory is a member of
the repository's npm workspace, and where a `node_modules` from it upward is
a symbolic link. In the checkout the root's `npm ci` installs it: the root
`package.json` names the movie's `js/` after the widget, and the root
`.npmrc` installs each member's direct dependencies in its own
`node_modules`, so the tool reads its packages where it always has. A test
holds both locks to the member's `package.json`. Playwright is the viewer's
1.63.0, one Chromium for both.

**The proof.** `scripts/check-dist` installs the wheel by path, refuses a
verb before `setup`, runs `setup`, reaches Node with a verb, and removes the
Node side; CI runs the package's Python tests and the Node suite's `pure`
and `stage` projects.

### Consequences

- Good: one install line and one command make a film; the films are
  numbered and licensed with the set and drawn by the viewer installed
  beside the framework.
- Good: one Chromium build serves the viewer's capture and the movie's
  render.
- Bad: Node and npm become the user's prerequisites for the film verbs,
  and `setup` needs the npm registry or npm's cache.
- Bad: `pip uninstall machinome-movie` leaves `js/node_modules` unless
  `setup --remove` ran first; the manual says so.
- Bad: the workspace's layout now depends on the root's `.npmrc`, and the
  movie's packages have two locks, whose transitive resolutions may differ
  by patch releases.
- Bad: CI runs the Node suite's browser and pipeline tests nowhere yet;
  they run in a cycle's evidence and on a contributor's machine.
- Neutral: the core imports nothing of the package, and the tool's internal
  names (`bin/videomaker.mjs`, the stage's `videomaker/stage` specifier)
  stay.

## References

- `packages/machinome-movie/machinome/movie/` (`cli.py`, `__init__.py`,
  `__main__.py`, `js/`), `packages/machinome-movie/pyproject.toml`
- `packages/machinome-movie/tests/test_command.py`,
  `packages/machinome-movie/tests/test_package.py`
- the root's `package.json`, `.npmrc` and `package-lock.json`
- `tests/test_repository_layout.py`, `tests/test_release_records.py`,
  `scripts/check-dist` at the repository root
- `openspec/specs/movie-distribution/spec.md`, `openspec/specs/cli/spec.md`
  ("Movie command")

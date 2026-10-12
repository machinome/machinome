# ADR-193: The Studio Is a Product of the Set, Reached by `machinome studio`

**Status:** Accepted
**Date:** 2026-10-12
**Change:** [`join-studio`](../../../openspec/changes/archive/2026-10-12-join-studio/)
**Amends:**
- [ADR-182: The repository is a monorepo of distributions, each named by its directory](ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md): the npm workspace's third member, the studio's frontend, keeps no lock of its own
- [ADR-188: The browser viewer is a product of the repository, numbered with the set](ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md): the studio's frontend is built from the root beside the widget, and the studio photographs projects through the viewer's capture
- [ADR-189: A package contributes a command through the group `machinome.commands`](ADR-189-a-package-contributes-a-command-through-the-group-machinome-commands.md): `machinome studio` is the group's third contributor
**Related to:**
- [ADR-187: The mechanics helpers are a portion of the repository at their own version](ADR-187-the-mechanics-helpers-are-a-portion-of-the-repository-at-their-own-version.md): the products table; this product keeps its record in its directory
- [ADR-190: The machinome skills are a package of the set, installed into assistants' directories by a command](ADR-190-the-machinome-skills-are-a-package-of-the-set-installed-by-a-command.md): the skills package whose `machinome-simulate` the studio links
- [ADR-191: The videomaker is a product of the set, its Node side inside its portion and installed by its command](ADR-191-the-videomaker-is-a-product-of-the-set-its-node-side-installed-by-its-command.md): the npm workspace's second member and the root's `.npmrc`
- The studio's own decision log, `packages/machinome-studio/workflow/adrs/`: its ADR 0033, the console script `machinome-studio` and the studio configuration file, superseded in its command by this record; the configuration file stands

## Context and Problem Statement

On 12 October 2026 the pilot settled what Machinome 0.9.0 contains
(`workflow/ongoing/release-0.9.md` at the repository root, decisions 1, 2,
3, 4, 6, 7 and 9): Machinome Studio, the project hub and workspace in which
a team of agents builds a machinome project with its maker, kept since
26 September 2026 in a repository of its own, experimental and never
published, joins the repository whole with its record in its directory, as
the distribution `machinome-studio` at `packages/machinome-studio/` and the
portion `machinome.studio`, no module `floor` and no alias; at the set's
version pinned `~=` both ways and under the set's licence; installed by
`machinome[studio]` and reached by `machinome studio`; its manual folded
into the framework's; its frontend the third member of the npm workspace;
its two skills kept and `machinome-simulate` linked from the skills
package; distributed by pip alone, its wheel carrying the built browser
surface.

The change's probes (design.md) found:

- Its manifest's `fastapi>=0.115` cannot resolve beside the core's
  `fastapi==0.111.*`; the studio has run on 0.111.1 in the workspace venv,
  its tests passing (probes 5 and 10).
- Its resources were found from its module's parent directory, which at
  `machinome/studio/` names `machinome/`, and the 0.1.0 wheel shipped only
  the built surface: an installed wheel held neither the profiles nor the
  skills (probe 6). With both inside the package directory and the root its
  own directory, both profiles load from a checkout and from the wheel
  (probes 7 and 8).
- Its package root imported the whole application: `machinome studio -h`
  took 351 ms and `import machinome.studio.cli` loaded 427 modules; with a
  lazy root, 76 ms and 79 modules (probe 9).
- Its profile loader refused a skill reached through `shop-skills/` into
  another package ("must link directly to shop-skills/<skill>").
- Its MCP server ran as `python -m floor.mcp_server` from the resource root
  on `PYTHONPATH`.
- Its test tool still offered the engines' 0.7 names and its skills taught
  seven imports from the node package's root, which the set's gates
  (ADR-180, ADR-181) refuse (probe 3).
- A model importing `machinome.studio` is vetted pure: the package lies
  beneath the contract member `machinome` and no denial names it (probe
  12).

## Considered Options

1. **The studio a product of the set at `machinome.studio`, its resources in
   its package directory, its command contributed through
   `machinome.commands`, the console script dropped** (chosen)
2. The same with the console script `machinome-studio` kept as an alias of
   `machinome studio`: refused, one command; no project names the launcher,
   and the workspace's records move with it
3. The studio's resources beside the package, found from the checkout:
   refused by probe 6, an installed wheel holds no checkout
4. The studio kept outside the set, consuming its packages: refused by the
   pilot

## Decision Outcome

**The package.** `packages/machinome-studio/` holds its manifest, a README,
its changelog, `MANIFEST.in`, `.gitignore`, the links `LICENSE` and
`LICENSES` to the root's, the package directory `machinome/studio/` (no
`__init__.py` at `machinome/`) with its subpackage `backends/`, its
`frontend/`, `profiles/` and `shop-skills/`, and its `scripts/`, `tests/`,
`openspec/` and `workflow/` (its decision log under `workflow/adrs/`, under
its own numbers, its architecture overview, design reference, product
records and spikes). It carries the set's version, requires
`machinome~=<version>`, `machinome-viewer[snapshot]~=<version>`,
`fastapi>=0.111,<1`, `tomlkit`, `uvicorn` and `watchdog`, is required by the
core's extra `studio` with the same pin, and is named by `.bumpversion.cfg`
with its frontend's `package.json`. Its wheel carries the modules, the built
surface `static/`, the profiles and the skills as package data, named by
three globs with `include-package-data` off, and no frontend source; its
sdist carries the frontend's sources and a surface its own hook builds,
and a wheel built from a checkout rebuilds a surface absent or older than a
frontend source, refusing first a symbolic `node_modules` from the frontend
up.

**The address.** The package's root reads `create_app` on first use. The
resource root is the package directory, in a checkout and in an installed
wheel alike. The MCP server runs as `python -m machinome.studio.mcp_server`;
the two backends that start it put on `PYTHONPATH`, and the Codex floor
worker runs from, the directory holding the package's `machinome/`, never
the resource root, which would expose the package's modules as top-level
names. The word floor stays for the product's workspace, its MCP server's
name and tools, its environment variables and the line the command prints.
The studio imports no framework module: it runs `machinome` beside its
interpreter and reads the viewer's bundle from `machinome viewer`'s report.

**The command.** `studio = "machinome.studio.cli:Studio"` in
`machinome.commands`: `--projects-dir PATH`, `--port PORT` and the
launcher's two hidden options; `handle` calls the orchestrator's `run`,
which resolves the folder and the port as the launcher always has (option,
`FLOOR_PORT`, the studio configuration file, 9000), refuses without the
OpenSpec CLI, prints `shop-floor open at http://127.0.0.1:PORT` once the hub
listens, and opens no browser. `python -m machinome.studio.orchestrator` is
the same command, `python -m machinome.studio` the hub without agents. No
console script and no module `floor` are installed.

**The skills.** The studio keeps `shop-skills/machinome` and
`shop-skills/machinome-api`; `shop-skills/machinome-simulate` is a relative
link into the skills package's skill, which the archives carry as files. A
profile's skill link is read one level and must name `shop-skills/<skill>`
of the same shop, whose entry may itself be a link; any other target is
refused. The builder, the designer and the machinist allowlist
`machinome-simulate`. The test tool takes `engine` (`brep`, `mesh`) as
`--brep` or `--mesh`, and the skills import each node name from its module.

**The workspace and the proof.** The frontend, `@machinome/studio`, is the
root npm workspace's third member with no lock of its own, its resolutions
seeded into the root lock unchanged. `machinome vet` denies
`machinome.studio`. `scripts/check-dist` installs the studio's wheel by its
path, loads both profiles from the installed package, opens the hub on a
scratch catalogue and reads its page. The studio's tests run from its
directory, `make test PKG=machinome-studio` after the frontend's typecheck
and build, the OpenSpec CLI on the PATH (CI installs it); its browser tests
run when `MACHINOME_STUDIO_E2E=1` is set.

### Consequences

- Good: one licence, one version, one command and one manual for the set;
  the studio installs by pip from the set, its wheel serving the hub, the
  profiles and the skills with no checkout.
- Good: `machinome -h` pays for the studio only its command class.
- Bad: the studio's floor for fastapi follows the core's pin.
- Bad: its tests need the OpenSpec CLI and the built surface.
- Bad: the wheel carries third-party minified code whose notices it does
  not hold; `CREDITS.md` names the packages, versions and licences.
- Bad: the identity's artwork and favicon pack travel in the package
  without the set's licence, their carve-out stated in `CREDITS.md` and the
  brand README.
- Neutral: the studio still reaches the framework and the viewer only as
  processes.
- Neutral: its branches other than `main` stay in its former repository.

## References

- `packages/machinome-studio/pyproject.toml`, `MANIFEST.in`,
  `machinome/studio/` (`__init__.py`, `cli.py`, `packaging.py`,
  `preparation.py`, `profiles.py`, `mcp_server.py`, `orchestrator.py`,
  `backends/`)
- `packages/machinome-studio/tests/` (`test_packaging.py`,
  `test_floor_entrypoint.py`, `test_runtime_profiles.py`,
  `test_documentation.py`)
- the root's `pyproject.toml`, `package.json`, `package-lock.json`,
  `Makefile`, `.bumpversion.cfg` and `.github/workflows/python-app.yml`
- `tests/test_repository_layout.py`, `tests/test_release_records.py`,
  `tests/test_vet_universe.py`, `scripts/check-dist`
- `openspec/specs/studio-distribution/spec.md`, `openspec/specs/cli/spec.md`
  ("Studio command")

# studio-distribution Specification

## Purpose

Ship Machinome Studio, the package `machinome.studio`, at the set's version
and under its licence, with its built browser surface, its profiles and its
shop skills in its wheel, so an installed studio serves the hub and loads
its profiles with no checkout; reached by `machinome studio`, it runs the
framework's command and reads the viewer's report as processes of its own
(change `join-studio`, ADR-193).

## Requirements
### Requirement: The studio package ships its browser surface, its profiles and its skills

The repository's distribution `machinome-studio`, at
`packages/machinome-studio/`, SHALL ship the package `machinome.studio`, a
portion of the `machinome` namespace, holding its modules and the subpackage
`machinome.studio.backends`, and as package data its built browser surface
`static/`, its runtime profiles `profiles/` and its shop skills
`shop-skills/`: `machinome` and `machinome-api`, its own, and
`machinome-simulate`, which in the repository is a relative symbolic link to
the skills package's skill of that name and which the distributions SHALL
carry as regular files with that skill's bytes, under `shop-skills/` and
under each profile that exposes it. The wheel SHALL carry no source of the
frontend, no `node_modules` and no `machinome/__init__.py`. The source
distribution SHALL carry the frontend's sources and a surface built from them
by the distribution's own hook, so installing either needs no npm; a wheel
built from a checkout SHALL rebuild a surface that is absent or older than a
frontend source. The package SHALL be numbered with the set, require the
framework and `machinome-viewer[snapshot]` with the compatible-release pin
`~=<version>`, declare `studio = "machinome.studio.cli:Studio"` in the
entry-point group `machinome.commands`, declare no console script, and keep
its tests and its record in its directory; the framework SHALL NOT import it.

#### Scenario: The wheel carries what the studio serves

- **WHEN** the package's wheel is built and installed
- **THEN** it holds `machinome/studio/` with its modules, `static/index.html`,
  both profiles and `shop-skills/machinome-simulate/SKILL.md` as a regular
  file, owned by `machinome-studio`, and no file under `frontend/`

#### Scenario: A checkout's surface is stale

- **WHEN** a wheel is built from a checkout whose frontend has a source newer
  than its built surface
- **THEN** the build runs the frontend's build before packaging, refusing
  first when a `node_modules` from the frontend up is a symbolic link

### Requirement: The studio finds its resources in its package directory

The studio SHALL find its profiles, its shop skills and its built surface in
the directory of the package `machinome.studio`, from the module it runs,
never from the working directory, a Git checkout or an environment variable
naming a checkout, so a source checkout and an installed wheel serve the same
resources. Its MCP server SHALL run as `python -m
machinome.studio.mcp_server` from the studio's own interpreter.

#### Scenario: An installed studio loads its profiles

- **WHEN** the studio is installed from its wheel, with no checkout of the
  repository on the machine, and loads the profiles `openspec-builder` and
  `fordesmac`
- **THEN** each loads from the installed package directory with its prompts
  and its allowlisted skills

### Requirement: A profile's skill link names the shop's skill, which may reach the skills package

A profile SHALL expose a shared skill by a symbolic link that names, read
one level, `shop-skills/<skill>` of the same studio; the loader SHALL refuse
a link naming anything else, another profile, a repository `skills/`
directory or a file. The entry `shop-skills/<skill>` SHALL be a directory
holding the skill's `SKILL.md`, or a relative link resolving to one: the
studio's `machinome-simulate` is the skills package's, linked. An agent's
prompt SHALL name each skill it uses in its frontmatter, and the builder of
`openspec-builder` and the designer and the machinist of `fordesmac` SHALL
name `machinome-simulate`.

#### Scenario: The builder loads the linked skill

- **WHEN** the profile `openspec-builder` is loaded from a checkout of the
  repository
- **THEN** the builder's skills are `machinome-api`, `machinome` and
  `machinome-simulate`, the last announcing the skills package's name and
  description

#### Scenario: A profile link that bypasses the shop's skills is refused

- **WHEN** a profile's skill link names a directory other than
  `shop-skills/<skill>`, even one holding a valid skill
- **THEN** loading the profile fails naming the profile and the skill

### Requirement: The studio reaches the framework and the viewer as processes

The studio SHALL import no module of the framework but the `machinome`
package its own package lies under: it SHALL run the `machinome` command
installed beside its interpreter for every build, test and snapshot, and
read the browser viewer's bundle from the report of `machinome viewer`. Its
test tool SHALL pass the comparison engine to `machinome test` with the
framework's own flags, `--brep` or `--mesh`, and SHALL refuse any other
engine naming the two. Its shop skills SHALL import each framework name from
the module that defines it.

#### Scenario: The studio's modules import no framework module

- **WHEN** every absolute import of the package's modules is read
- **THEN** each that names `machinome` names `machinome.studio` or a module
  beneath it, and a test fails naming any other

#### Scenario: An agent runs the tests on meshes

- **WHEN** an agent calls the studio's `machinome_test` tool with `engine`
  `mesh`
- **THEN** the studio runs `machinome test --mesh` in the active project, and
  a call naming `faceted` or `exact` is refused naming `brep` and `mesh`


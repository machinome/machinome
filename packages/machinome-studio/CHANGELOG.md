# Changelog

All notable changes to Machinome Studio. The first section describes the
current source; when a release is cut it becomes that release's section
and a new `Unreleased` section opens above it.

## Unreleased

Machinome Studio, numbered with Machinome, runs against the framework and
the browser viewer of its own release, on Linux, with Claude Code, OpenCode
or qualified Codex as the agent backend.

### Joined to the Machinome repository

- Machinome Studio is part of the Machinome repository,
  <https://github.com/machinome/machinome>, at `packages/machinome-studio/`,
  with its history. Its Python package is `machinome.studio` (formerly
  `floor`), a portion of the `machinome` package, and its command is
  `machinome studio`; the `machinome-studio` command is gone, `python -m
  machinome.studio` serves the hub without agents, and the configuration
  file, its keys and the project's `[tool.machinome-studio]` table are
  unchanged. It is numbered with Machinome, installed by
  `pip install "machinome[studio]"`, and licensed as every package of the
  repository, GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the
  recipient's choice. Its manual is part of Machinome's,
  <https://machinome.readthedocs.io>. Its frontend builds from the
  repository's npm workspace and its wheel carries the built surface, the
  profiles and the skills.
- The profiles' agents may load `machinome-simulate`, the skills package's
  skill for reconstructing an existing design; the builder, the designer
  and the machinist allowlist it.
- The `machinome_test` tool takes `engine` (`brep` or `mesh`), the
  framework's flags since 0.8, in place of `kernel`; the two skills import
  each node name from its module.

### What a maker gets

- **The command `machinome studio`**, a command of `machinome` wherever
  `pip install "machinome[studio]"` installed the studio, starting the same
  hub as `python -m machinome.studio.orchestrator`. A
  studio configuration file, TOML at
  `$XDG_CONFIG_HOME/machinome-studio/config.toml` or
  `$HOME/.config/machinome-studio/config.toml` (or the file
  `MACHINOME_STUDIO_CONFIG` names), supplies the project folder and the
  port once for all three ways of starting the hub; a command-line option
  still overrides it, and a malformed file refuses startup naming the file
  and the key. **Breaking:** a missing project folder, with no
  `--projects-dir` and no configuration file, now exits `1` with an
  `error:` line, as a failed prerequisite, instead of argparse's usage
  error `2`.
- **A project hub** over any folder of projects: one card per project with
  its profile, branch, last commit and a preview of its model; folders of
  projects and multi-model projects entered in place; directories that
  cannot be opened listed with the reason; the agent backends found on the
  machine. A project is created with a name and a profile, from the
  framework's scaffold, as its own Git repository, and opened in the same
  action.
- **The Machinome identity**: the wordmark with its `Studio` qualifier in
  the title bar of the hub and of every workspace, the white Machinome
  symbol on a black plate as the tab's favicon, Space Grotesk for the interface and IBM Plex Mono for code,
  paths and values.
- **A project workspace**: a conversation with the agent who speaks for
  the team; the model in the framework's browser viewer, updated part by
  part as the source changes, with the viewer's own assembly navigator; the
  project's Git-visible files in an editor with revision-checked saves;
  each agent's activity, with its runtime changeable while idle; and the
  distinct printed pieces of the last build on a fixed virtual bed,
  downloadable as one STL per piece with printing instructions.
- **Two profiles**: `openspec-builder`, the shop default, one agent —
  OpenSpec Builder — working directly with the maker and keeping the
  project's design in an OpenSpec record it owns; and `fordesmac`, a
  foreman who speaks with the maker and assigns a designer, a machinist
  and a librarian one increment at a time. **Breaking:** a project
  declaring no profile now opens under `openspec-builder` instead of
  `fordesmac`, and a project declaring the former `builder` or `openspec`
  name is refused, naming its `pyproject.toml` and the value, until its
  declaration names `openspec-builder`; the studio ships no alias and no
  migration path for either old name.
- **Correction:** the Agents area's Session panel reported every profile
  as `delegated`; it now reads the profile's own work mode (`direct` for
  `openspec-builder`, `delegated` for `fordesmac`).
- **Three backends, chosen per agent by the project**: Claude Code,
  OpenCode and qualified Codex, each agent replacing its native tools with the studio's bounded
  operations rooted at the project, holding exactly the capabilities its
  profile declares, and loading the skills its profile allows.
- **Scoped Codex sessions** with a separate Studio login, concurrent
  projects, image tools, active steering and context-preserving recovery
  and idle model changes. Unsupported runtimes fail closed; native tool
  execution is not enabled to make a session work.
- **Project-owned configuration**: the `[tool.machinome-studio]` table
  selects the profile and, per agent, backend, provider, model and
  reasoning level; the studio writes it on creation and on request, and
  touches nothing else.
- **Sessions that keep nothing**: several projects open at once, each
  isolated; a session ends with everything it held, and the project's
  repository is the record.
- **A manual**, part of Machinome's, whose facts are held to the
  package.

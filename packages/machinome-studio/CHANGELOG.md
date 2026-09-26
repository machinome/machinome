# Changelog

All notable changes to Machinome Studio. The first section describes the
current source; when a release is cut it becomes that release's section
and a new `Unreleased` section opens above it.

## Unreleased

Machinome Studio 0.1.0 runs against Machinome 0.7.0 installed with its
`viewer` extra, on Linux, with Claude Code, OpenCode or qualified Codex as the agent
backend.

### What a maker gets

- **A project hub** over any folder of projects: one card per project with
  its profile, branch, last commit and a preview of its model; folders of
  projects and multi-model projects entered in place; directories that
  cannot be opened listed with the reason; the agent backends found on the
  machine. A project is created with a name and a profile, from the
  framework's scaffold, as its own Git repository, and opened in the same
  action.
- **A project workspace**: a conversation with the agent who speaks for
  the team; the model in the framework's browser viewer, updated part by
  part as the source changes, with the viewer's own assembly navigator; the
  project's Git-visible files in an editor with revision-checked saves;
  each agent's activity, with its runtime changeable while idle; and the
  distinct printed pieces of the last build on a fixed virtual bed,
  downloadable as one STL per piece with printing instructions.
- **Two profiles**: `builder`, one agent working directly with the maker
  and keeping the project's design in an OpenSpec record it owns; and
  `fordesmac`, a foreman who speaks with the maker and assigns a designer,
  a machinist and a librarian one increment at a time.
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
- **A manual** under `docs/`, built with Sphinx, whose facts are derived
  from the package.

# ADR-190: The Machinome Skills Are a Package of the Set, Installed into Assistants' Directories by a Command

**Status:** Accepted
**Date:** 2026-10-12
**Change:** [`join-skills`](../../../openspec/changes/archive/2026-10-12-join-skills/)
**Related to:**
- [ADR-183: An extension package is a namespace portion in its own distribution](ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md): one version for the set, `~=` pins both ways, bumped from the root's `.bumpversion.cfg`
- [ADR-187: The mechanics helpers are a portion of the repository at their own version](ADR-187-the-mechanics-helpers-are-a-portion-of-the-repository-at-their-own-version.md): the products table; this is the first product numbered with the set and specified by the framework
- [ADR-189: A package contributes a command through the group `machinome.commands`](ADR-189-a-package-contributes-a-command-through-the-group-machinome-commands.md): `machinome skills` is a contributor of the group

## Context and Problem Statement

On 12 October 2026 the pilot settled what Machinome 0.9.0 contains
(`workflow/ongoing/release-0.9.md` at the repository root, decisions 1, 2, 4
and 6). machinome-skills, the two assistant skills `machinome` and
`machinome-simulate` written in the Agent Skills format and kept since 20
September 2026 in a repository of their own, joins as it is: the
distribution `machinome-skills` at `packages/machinome-skills/`, the portion
`machinome.skills`, at the set's version and under the set's licence,
installed by `machinome[skills]`. Its command, `machinome skills`, a
contributor of `machinome.commands`, installs the skills on the criteria of
OpenSpec's installer: a registry of tools with OpenSpec's ids and
dot-directories plus `agents` for `.agents/skills/`, `install --tools
all|none|a,b,c [path]` with a picker pre-selecting the tools detected in the
project, `update [--force]`, `list`, `--personal`, a marker in each copy,
`agents` the default when no tool is named, and nothing deleted that the
command did not write.

Before the join the product had no command: its README asked a reader to
copy two directories by hand into one of three documented locations, check
for an existing skill of the same name, and keep per-skill licence and
notice files beside them.

The change's probes (design.md) found:

- OpenSpec 1.6.0's installer (probe 1) lists 31 tools with a skills
  directory and one, `agents`, it never offers to `--tools`; detects a tool
  by its dot-directory at the project root (GitHub Copilot by seven paths);
  marks each skill it writes with `metadata.generatedBy` and rewrites a
  tool's skills when that differs from its running version; and removes a
  deselected workflow's skill directories by name, without reading a marker.
- Run in scratch (probe 2), `openspec init --tools all` overwrote a user's
  own `.claude/skills/openspec-propose/SKILL.md`, which carried no marker,
  without a question.
- The clients' documentation (probe 3) names, for Codex, Kilo Code, pi and
  Windsurf (now Devin Desktop), a skills directory other than OpenSpec's
  dot-directory: `.agents/skills/`, `.kilo/skills/`, `.agents/skills/` and
  `.devin/skills/`; OpenSpec's `.codex/skills/` and `.kilocode/skills/` are
  in none of them.
- The command run from the built wheel (probe 8) installs, refuses, updates
  and lists as the decision below says.

## Considered Options

1. **A product of the set at the set's version**, its tests and working
   record in its directory, its specification the framework's, its command
   on OpenSpec's criteria with a marker, a refusal and no deletion (chosen)
2. The skills inside the core's package: refused, the pilot's decision
   names a distribution
3. OpenSpec's behaviour whole, overwriting by name: refused, probe 2 shows it
   overwrote a user's skill
4. Per-tool adapters or slash commands: refused, the skills carry none, so
   one writer serves every tool
5. A picker library: refused, no dependency for one prompt (probe 9)

## Decision Outcome

**The package.** `packages/machinome-skills/` holds its manifest, a README,
`MANIFEST.in`, `.gitignore`, the links `LICENSE` and `LICENSES` to the
root's, the package directory `machinome/skills/` (no `__init__.py` at
`machinome/`), `tests/` and `workflow/`. It has no changelog and no OpenSpec
records of its own: its changes are the set's `HISTORY.rst` bullets and its
specification is the framework's `skills-distribution`. It carries the set's
version, requires `machinome~=<version>`, is required by the core's extra
`skills` with the same pin, is named by `.bumpversion.cfg`, and declares
`skills = "machinome.skills.cli:Skills"` in `machinome.commands`. The core
never imports it.

**The skills as data.** The two skills are package data under
`machinome/skills/agent-skills/<skill>/`, a directory name that is not an
identifier, so setuptools reads none of it as a package; each is `SKILL.md`
and its `references/` file, unchanged in substance, the frontmatter's
`license` the set's expression. They are read through
`importlib.resources`.

**The registry as data.** `tools.toml` lists every OpenSpec id with a
skills directory, spelled as OpenSpec spells it, in its order, after
`agents`: a display name, the detection paths, the project directory, the
personal directory where the tool documents one, and the row's source.
Where the client's documented directory differs from OpenSpec's (Codex,
Kilo Code, pi, Windsurf) the row writes the client's and detects by both.
Fifteen personal directories are OpenSpec's dot-directory under the home,
marked inferred and not verified.

**The copy and its marker.** `install` copies each shipped skill directory
whole into `<destination>/<skill>/` for each chosen tool, a directory shared
by several tools written once, every path printed. The copied `SKILL.md`
gains a `metadata` mapping at the end of its frontmatter,
`installed-by: machinome-skills` and `version: "<the installed version>"`,
written and read as text by the standard library alone. A target whose
`SKILL.md` carries no marker is refused unless `--force`: nothing is written,
each refused target is named with the line to run, exit 1. `--tools` takes
`all`, `none` or ids; an invalid value is a usage error, exit 2, naming the
valid values. Without `--tools`, a numbered prompt when standard input is a
terminal and `CI` is not set, pre-selecting the tools holding a marked copy,
else those detected, else `agents`; otherwise `agents`, said on one line.
`--personal` writes each tool's home directory; a tool with none is
refused.

**Update, list, no deletion.** `update` rewrites the marked copies whose
version is older than the installed one, compared as integers, and reports
the others: current, newer and left, not the command's and left; `--force`
rewrites every marked copy and never an unmarked one. `list` prints the
registry and each copy with the tools that read it and its version. No verb
deletes a file or a directory, and a file the package does not ship is left
as it is.

### Consequences

- Good: one install line and one command give the skills to every
  assistant the registry names.
- Good: the skills are at the set's version and under its licence, and the
  conformance walk of the seam reads a real contributor.
- Bad: the registry's inferred personal directories are unverified, and a
  client that moves its directory needs a release.
- Bad: `update` cannot know of a file a newer version stopped shipping, and
  by the rule above does not remove it.
- Bad: the seam's tests now read the environment's contributors and compute
  their expectations from it.
- Neutral: the core imports nothing of the package.

## References

- `packages/machinome-skills/machinome/skills/` (`cli.py`, `installer.py`,
  `tools.toml`, `agent-skills/`)
- `packages/machinome-skills/tests/test_skill_format.py`,
  `packages/machinome-skills/tests/test_command.py`
- `tests/test_repository_layout.py`, `tests/test_cli_contributed.py`,
  `tests/test_cli_lazy_imports.py`, `scripts/check-dist` at the repository
  root
- `openspec/specs/skills-distribution/spec.md`, `openspec/specs/cli/spec.md`
  ("Skills command")

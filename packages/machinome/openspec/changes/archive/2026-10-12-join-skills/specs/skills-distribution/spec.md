## ADDED Requirements

### Requirement: The skills package ships two skills in the Agent Skills format

The repository's distribution `machinome-skills`, at
`packages/machinome-skills/`, SHALL ship the package `machinome.skills`, a
portion of the `machinome` namespace, holding two skills as package data under
`machinome/skills/agent-skills/`: `machinome` and `machinome-simulate`, each a
directory holding a `SKILL.md` and its `references/` Markdown files, and
nothing else. Each `SKILL.md` SHALL begin with YAML frontmatter whose keys are
exactly `name`, `description` and `license`: the name valid by the Agent
Skills format and equal to its directory, a description of 1 to 1024
characters, and the licence the set's expression,
`GPL-2.0-or-later OR CERN-OHL-S-2.0+`; it SHALL be under 500 lines, every
local link of a skill's files SHALL resolve inside that skill, and every
`references/` file SHALL be linked from its `SKILL.md`. A skill SHALL carry no
licence or notice file of its own. The package SHALL be numbered with the
set, require the framework with the compatible-release pin `~=<version>`,
declare `skills = "machinome.skills.cli:Skills"` in the entry-point group
`machinome.commands`, and keep its tests and its working record in its
directory; the framework SHALL NOT import it.

#### Scenario: The wheel carries the skills

- **WHEN** the package's wheel is built and installed
- **THEN** it holds `machinome/skills/` with its modules, its registry and the
  two skill directories, each `SKILL.md` and its reference file, owned by
  `machinome-skills`, and no `machinome/__init__.py`

#### Scenario: A skill drifts from the format

- **WHEN** a shipped `SKILL.md` gains a frontmatter key, names another
  licence, links a file outside its skill, or a `references/` file is not
  linked from it
- **THEN** the package's format tests fail naming the skill and the fault

### Requirement: The registry names each tool by OpenSpec's id

The package SHALL carry, as data, a registry of the tools whose skills it
installs: every tool id of OpenSpec 1.6.0's installer that has a skills
directory, spelled as OpenSpec spells it, and `agents`, for the
`.agents/skills/` convention. Each entry SHALL state the tool's display name,
the paths whose presence in a project marks the tool detected (among them
OpenSpec's dot-directory for the tool, or OpenSpec's detection paths where it
names them), the skills directory under a project, and the skills directory
under the user's home, or none where the tool documents none. Where the
client's documented directory differs from OpenSpec's, the entry SHALL name
the client's: `.agents/skills/` for `codex` and `pi`, `.kilo/skills/` for
`kilocode`, `.devin/skills/` for `windsurf`.

#### Scenario: An id means the same tool in both installers

- **WHEN** the registry is read beside OpenSpec 1.6.0's list of tools
- **THEN** every OpenSpec id with a skills directory is present, its
  dot-directory is among its detection paths, and `claude`'s project directory
  is `.claude/skills/` and its personal one `~/.claude/skills/`

#### Scenario: Codex reads the Agent Skills directory

- **WHEN** the registry's entry for `codex` is read
- **THEN** its project directory is `.agents/skills/` and its personal one
  `~/.agents/skills/`, and `.codex` marks it detected

### Requirement: Install copies each skill whole with a marker

`machinome skills install [path] [--tools all|none|ID,...] [--personal]
[--force]` SHALL copy each shipped skill directory whole, `SKILL.md` and its
references, into `<destination>/<skill>/` for each tool chosen, the
destination being the tool's project directory under `path` (the current
directory by default) or, with `--personal`, its directory under the user's
home; a directory several chosen tools share SHALL be written once. Each
copied `SKILL.md` SHALL be the shipped one with a `metadata` mapping added to
its frontmatter, `installed-by: machinome-skills` and `version: "<the
installed package's version>"`, its marker; every other file SHALL be
written as shipped. The command SHALL print every path it writes and write
nothing else.

Before writing, a target that exists and whose `SKILL.md` does not carry the
marker SHALL be refused unless `--force` is given: nothing SHALL be written,
each refused target SHALL be named and the line to run with `--force` given,
and the command SHALL exit 1. A target carrying the marker SHALL be rewritten.
`--personal` with a tool that documents no personal directory SHALL be
refused naming the project install, exit 1.

`--tools all` SHALL choose every tool and `--tools none` none, exit 0;
otherwise the ids given, separated by commas; an unknown id, `all` or `none`
beside an id, or an empty value SHALL be a usage error, exit 2, naming the
valid values. Without `--tools`, when standard input is a terminal and `CI` is
not set, the command SHALL show the registry numbered, mark as pre-selected
the tools whose directories under `path` hold a marked copy, else the tools
detected under `path`, else `agents`, and install for the tools the answer
names, Enter taking the marked ones; otherwise it SHALL install for `agents`,
saying so on one line.

#### Scenario: Install for two tools

- **WHEN** a user runs `machinome skills install --tools agents,claude` in a
  project
- **THEN** `.agents/skills/` and `.claude/skills/` each hold `machinome/` and
  `machinome-simulate/` with their `SKILL.md` and reference file, each
  `SKILL.md` carries the marker with the installed version, every path written
  is printed, nothing else in the project changes, and the command exits 0

#### Scenario: A skill the command did not write

- **WHEN** a project's `.cursor/skills/machinome/SKILL.md` has no marker and a
  user runs `machinome skills install --tools cursor`
- **THEN** nothing is written, the target and the line `machinome skills
  install --tools cursor --force <path>` are printed on standard error, and
  the command exits 1; with `--force` the copy replaces it and a file of the
  user's beside it stays

#### Scenario: No tool named and no terminal

- **WHEN** `machinome skills install` runs with standard input not a terminal
- **THEN** it installs for `agents` into `.agents/skills/` and says so

#### Scenario: The prompt pre-selects the detected tools

- **WHEN** a project holds `.claude/` and `.cursor/` and a user runs
  `machinome skills install` at a terminal and presses Enter
- **THEN** the numbered registry marks `claude` and `cursor`, and the skills
  are installed into `.claude/skills/` and `.cursor/skills/`

#### Scenario: A personal install

- **WHEN** a user runs `machinome skills install --personal --tools
  opencode,codex`
- **THEN** the skills are written under `~/.config/opencode/skills/` and
  `~/.agents/skills/`; and `--personal --tools trae` is refused naming the
  project install, exit 1

### Requirement: Update rewrites the copies older than the package

`machinome skills update [path] [--personal] [--force]` SHALL look in every
directory of the registry under `path` (or, with `--personal`, under the
user's home) for each shipped skill, and SHALL rewrite, as install writes it,
each copy whose marker names a version older than the installed package's,
reporting each copy on one line: current, rewritten from its version, newer
and left as it is, or not written by the command and left as it is.
`--force` SHALL rewrite every copy carrying the marker, never one without it.
With no copy found, the command SHALL say how to install and exit 0.

#### Scenario: An older copy is rewritten

- **WHEN** a project holds copies at the installed version and one copy whose
  marker names an older version, and a user runs `machinome skills update`
- **THEN** that copy alone is rewritten and reported with its old and new
  versions, and the others are reported current

#### Scenario: A newer or a foreign copy is left

- **WHEN** a copy's marker names a newer version, or a skill of the same name
  carries no marker
- **THEN** `machinome skills update` leaves it as it is and says so; with
  `--force` the newer copy is rewritten and the unmarked one is not

### Requirement: List shows the registry and the copies

`machinome skills list [path] [--personal]` SHALL print every tool of the
registry with its project and personal directories, then each copy of a
shipped skill under `path` (or the user's home), with the tools that read its
directory and its marker's version compared with the installed package's, or
that the command did not write it, and exit 0.

#### Scenario: Copies are listed by tool

- **WHEN** a project holds the skills under `.agents/skills/` and a user runs
  `machinome skills list`
- **THEN** the registry is printed, and each copy is listed with `agents`,
  `codex` and `pi` and its version

### Requirement: The command never deletes

No verb of `machinome skills` SHALL delete a file or a directory. A file in a
target that the package does not ship SHALL be left as it is by `install` and
`update`, and a file or a skill without the command's marker SHALL never be
written to without `--force`.

#### Scenario: A file of the user's inside a copy

- **WHEN** a marked copy holds a file the package does not ship and a user
  runs `machinome skills install` or `machinome skills update --force`
- **THEN** that file is still there, unchanged, afterwards

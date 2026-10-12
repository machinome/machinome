## Context

A cycle of the joins campaign of Machinome 0.9, cut from the line
`v0.9-joins` at 5af14f71 (the head after `commands-contributed-by-packages`
and the 0.9.0 decisions note) on the bench
`machinome/WTs/v0.9-joins-join-skills`. It runs beside `join-movie`, both
contributors of the command seam. The method of `workflow/ongoing/joins-0.9.md`
holds: a product is imported by rewriting its history directly to its final
paths and merged with `--allow-unrelated-histories` by the orchestrator after
the planning commit; one licence at the join; the original repository stays as
it is. The viewer's join, on another bench, founds the npm workspace and takes
ADR-188; this cycle has no JavaScript and takes ADR-190.

The pilot's decisions of 12 October 2026 (`workflow/ongoing/release-0.9.md`,
decisions 1, 2, 4 and 6), settled and not reopened here:

- **machinome-skills joins as it is**: the two skills `machinome` and
  `machinome-simulate` unchanged in substance, the distribution
  `machinome-skills` at `packages/machinome-skills/`, the portion
  `machinome.skills`, at the set's version (0.8.1 on this line), pinned `~=`
  both ways, installed by a new extra `machinome[skills]`.
- **One licence at the join**: its licence files and the per-skill licence and
  notice files go, the `license` field of each `SKILL.md` frontmatter states
  the set's expression, no record this change writes names the licence it
  carried; `NOTICE`'s provenance, the adaptation from the studio's skills,
  goes to `CREDITS.md`; its check script becomes a test, its evaluation note
  its working record.
- **Its command, `machinome skills`**, the second contributor of the group
  `machinome.commands` (ADR-189), follows OpenSpec's installer: a registry of
  tools with OpenSpec's ids and dot-directories plus `agents` for the
  `.agents/skills/` convention; `install --tools all|none|a,b,c [path]` with a
  picker pre-selecting the tools detected in the project; `update [--force]`;
  `list`; `--personal` for a tool's user-level directory; a marker in each
  installed copy; `agents` the default when no tool is named; nothing deleted
  that the command did not write.
- **The package is separate from the studio**, which keeps its own skills and
  links `machinome-simulate` from the package later. The unification of
  `machinome-simulate` with the workspace's `simulate-project`, and the
  derivation of the studio's API skill from the manual, are deferred.

machinome-skills is one commit, 69e67ff of 20 September 2026, on `main` of
`/home/asa/devel/machinome/machinome-skills` (remote
`git@github.com:machinome/machinome-skills.git`), with no tag and no other
branch; `dist/` (three archives) and `scripts/__pycache__/` are untracked
leavings. Its fifteen tracked files: `README.md` (the two skills, an install
table of three assistants with a project and a personal location each, the
example paths, the runtime requirements, the maintainer's validation and
build commands, the licence and provenance); `LICENSE`; `NOTICE` (the
author's copyright, the licence, and the provenance: "The mechanical workflow
guidance is adapted from the machinome and simulate-project skills in
Machinome Studio, with revisions for independent, cross-harness use and
documentation-based API lookup."); `.gitignore` (`__pycache__/`, `*.pyc`,
`.venv/`, `dist/`); `requirements-dev.txt` (`PyYAML==6.0.3`);
`scripts/check.py` (the format checks under PyYAML, and `--build`, which
writes three deterministic ZIP archives); `docs/evaluation.md` (the static
checks, ten live evaluation cases, and the validation boundary of 20
September 2026); and `skills/machinome/` and `skills/machinome-simulate/`,
each a `SKILL.md` (103 and 127 lines, frontmatter `name`, `description`,
`license`), one `references/` file (`mechanical-contracts.md`, 112 lines;
`source-adaptation.md`, 88 lines), a `LICENSE.txt` equal to the root's
licence and a `NOTICE` equal to the root's.

The licence the product carried is stated in `LICENSE`, the two
`LICENSE.txt`, the three `NOTICE`, the README's last section, `check.py`'s
SPDX line and its licence checks, each `SKILL.md`'s `license` field, and the
subject of its one commit.

The Agent Skills format (<https://agentskills.io/specification>, read on 12
October 2026): a skill is a directory holding `SKILL.md`, YAML frontmatter
then Markdown; `name` (1 to 64 characters, lowercase letters, digits and
single hyphens, matching the directory), `description` (1 to 1024
characters), optional `license` ("license name or reference to a bundled
license file"), `compatibility`, `metadata` ("a map from string keys to
string values... We recommend making your key names reasonably unique") and
`allowed-tools`; optional `scripts/`, `references/`, `assets/`; `SKILL.md`
under 500 lines; references one level deep.

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise. Probes ran in the scratch
directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C5-propose/`
(`<scratch>` below), never in the bench, the product or a project, with the
bench's venv synced from the lock (CPython 3.12.3), uv 0.11.8, git-filter-repo
`ed61b4050b71`, `build` 1.6.1 and the OpenSpec CLI 1.6.0. The prototype the
probes ran is `<scratch>/prototype/` (a manifest, three modules and the
registry); it is evidence for the shape, not the implementation.

### Probes

1. **OpenSpec's installer, read.** `@fission-ai/openspec` 1.6.0,
   `dist/core/config.js`: `AI_TOOLS` lists 32 entries, 31 with a `skillsDir`
   (`amazon-q` `.amazonq`, `antigravity` `.agent`, `auggie` `.augment`, `bob`
   `.bob`, `claude` `.claude`, `cline` `.cline`, `codex` `.codex`,
   `forgecode` `.forge`, `codebuddy` `.codebuddy`, `continue` `.continue`,
   `costrict` `.cospec`, `crush` `.crush`, `cursor` `.cursor`, `factory`
   `.factory`, `gemini` `.gemini`, `github-copilot` `.github`, `iflow`
   `.iflow`, `junie` `.junie`, `kilocode` `.kilocode`, `kimi` `.kimi`, `kiro`
   `.kiro`, `lingma` `.lingma`, `vibe` `.vibe`, `oh-my-pi` `.omp`, `opencode`
   `.opencode`, `pi` `.pi`, `qoder` `.qoder`, `qwen` `.qwen`, `roocode`
   `.roo`, `trae` `.trae`, `windsurf` `.windsurf`) and one, `agents` ("AGENTS.md
   (works with Amp, VS Code, ...)"), `available: false`, with none, so
   `--tools` never accepts it. Only `github-copilot` has `detectionPaths`
   (seven paths under `.github/`); every other tool is detected by its
   dot-directory at the project root (`available-tools.js`). `init.js`:
   `--tools all|none|a,b` (case-folded, deduplicated, `all` and `none` not
   combinable, an unknown id refused naming the valid ones); without it, an
   interactive searchable multi-select (OpenSpec's own prompt over
   `@inquirer/core`) pre-selecting the configured tools, or on a first setup
   the detected ones; non-interactive, the detected tools, else an error.
   Interactive means stdin is a TTY and `CI` is not set
   (`utils/interactive.js`). `skill-generation.js` writes each skill's
   frontmatter with `license`, `compatibility` and `metadata: {author:
   openspec, version: "1.0", generatedBy: "<OpenSpec version>"}`;
   `tool-detection.js` reads `generatedBy` back with a regular expression and
   `update.js` rewrites a tool's skills when it differs from the running
   version (`!==`, not older), `--force` rewriting all; `update.js` removes
   whole skill directories of deselected workflows by name, without reading a
   marker. The cleanup that removes only its markers is the legacy config
   files' (`legacy-cleanup.js`).
2. **OpenSpec's installer, run.** `openspec init --tools all .` in a scratch
   git directory with `HOME` and `XDG_CONFIG_HOME` under `<scratch>/home`
   (`<scratch>/os-init.out`), after placing a user's own
   `.claude/skills/openspec-propose/SKILL.md` without the marker: exit 0; 31
   directories `<dot-dir>/skills/`, 186 `SKILL.md` (six skills each); slash
   commands beside them, and for Codex six prompt files under
   `$HOME/.codex/prompts/`, outside the project; and the user's own
   `openspec-propose/SKILL.md` overwritten without a question ("Refreshed:
   Claude Code"). OpenSpec does not refuse a skill it did not write; the
   pilot's criterion here does.
3. **The clients' documentation** (12 October 2026; Decision 5's table states
   each row's source). Read directly: Claude Code
   (<https://code.claude.com/docs/en/skills>: `~/.claude/skills/`,
   `.claude/skills/` in the start directory and its parents up to the
   repository root); Codex (<https://learn.chatgpt.com/docs/build-skills>:
   `.agents/skills` in every directory from the working directory up to the
   repository root, `$HOME/.agents/skills`; no `.codex/skills`); OpenCode
   (<https://opencode.ai/docs/skills/>: `.opencode/skills/`,
   `~/.config/opencode/skills/`, and the `.claude` and `.agents` locations at
   both levels); Kilo Code (<https://kilo.ai/docs/customize/skills>:
   `.kilo/skills/` and `~/.kilo/skills/`, plus `.agents` and `.claude`; no
   `.kilocode/skills`); pi (`packages/coding-agent/docs/skills.md` of
   `badlogic/pi-mono`: "Pi also supports the Agent Skills locations
   `~/.agents/skills/` and `.agents/skills/`", project ones from the working
   directory through its ancestors). Through a search engine's summary of the
   vendors' pages, not read whole: GitHub Copilot (`.github/skills`,
   `.claude/skills` or `.agents/skills`; `~/.copilot/skills` or
   `~/.agents/skills`); Gemini CLI (`.gemini/skills/` or `.agents/skills/`;
   `~/.gemini/skills/` or `~/.agents/skills/`); Cursor (`.cursor/skills/`,
   `~/.cursor/skills/`); Cline (`.cline/skills/`, `~/.cline/skills/`); Windsurf,
   now documented as Devin Desktop (`.devin/skills/` current and
   `.windsurf/skills/` legacy, still read; `~/.config/devin/skills/` current
   and `~/.codeium/windsurf/skills/` legacy). The same search reported that
   Roo Code shut down on 15 May 2026 (a third-party page; not verified). The
   other rows are the orchestrator's reading of each client's documentation
   on 12 October 2026, not repeated here, or inferred from OpenSpec's
   dot-directory, as the table marks.
4. **The import, rehearsed** on a fresh clone (`<scratch>/skills-rw`) with the
   command of Decision 1 (`<scratch>/filter-repo-command.sh`, its message
   expression `<scratch>/replace-message.txt`): one commit parsed and
   rewritten, `main` at 9a23c9a, its subject "Create portable machinome skills
   package", author and date kept (Luis Fagundes, 2026-09-20 20:15:07
   +0000); its tree the 8 paths of `<scratch>/rehearsal-ls-files.txt`, every
   one under `packages/machinome-skills/`; no tag. Without the message
   expression the subject keeps its last three words, which name the licence
   the product carried (Open Questions 7).
5. **The merge, rehearsed** in a scratch clone of the bench's branch at
   5af14f71 (`<scratch>/merge-rehearsal-2`): `git fetch <scratch>/skills-rw
   main` and `git merge --allow-unrelated-histories`: no conflict, 8 files
   created, 736 insertions (`<scratch>/merge.out`); `git log --follow` on
   `packages/machinome-skills/machinome/skills/agent-skills/machinome/SKILL.md`
   and on `packages/machinome-skills/tests/test_skill_format.py` reaches
   9a23c9ac, and `git blame` attributes the skill's lines to it. The gates on
   the joined tree (an earlier rehearsal, `<scratch>/merge-rehearsal`, the
   same 8 files with the skills under `bundled/`), eight suite modules run
   with the bench's venv from `<scratch>/merge-rehearsal/packages/machinome`
   (`<scratch>/probe-gates-at-join.out`: 17 failed, 129 passed, 1738
   subtests). Red for the join: `test_every_member_is_a_workspace_source`,
   `test_the_members_are_the_package_directories` (no `pyproject.toml`),
   `test_the_readme_links_every_package_and_states_the_licence`,
   `test_every_sibling_is_in_the_table` and
   `test_the_guide_installs_every_member_without_uv`, each naming
   `machinome-skills`. The other twelve are the rehearsal's own (the bench
   venv's editable lines name the bench's directories, so
   `test_each_portion_resolves_from_its_package` and
   `test_each_product_resolves_from_its_directory` read the bench, not the
   clone), as in `join-mechanics`'s probe 6. `test_release_records.py`,
   `test_core_names_no_scad.py`, `test_node_root_exports_nothing.py`,
   `test_docs_structure.py`, `test_machinome_identity.py`,
   `test_kernel_extras.py` and `test_core_names_no_split_words.py` pass on the
   joined tree.
6. **The seam's tests with the package installed.** A throwaway venv
   (`<scratch>/venv-try`, CPython 3.12.3) whose site directory adds the
   bench venv's (a `.pth` calling `site.addsitedir`), the prototype's wheel
   installed into it with `--no-deps`, and `test_cli_contributed.py`,
   `test_cli_lazy_imports.py` and `test_cli.py` run from the rehearsal's
   framework directory (`<scratch>/probe-seam-with-skills.out`): 4 failed, 49
   passed, 1 skipped. `test_a_second_contributor_runs` exits 1, "Error:
   machinome skills is contributed by more than one package: fake-skills
   (machinome_fake_skills:Skills), machinome-skills
   (machinome.skills.cli:Skills)"; `test_help_lists_contributed_commands_after_the_framework`
   finds `skills` unavailable for the same reason;
   `test_a_module_that_cannot_be_imported` expects the choices
   `{...,vet,gone}` and reads `{...,vet,gone,skills}`;
   `test_the_contract_walk_reads_a_fake_distribution` expects the fakes'
   distributions alone and reads `machinome-skills` beside them, with no
   failure. `test_every_contributed_entry_resolves_and_honours_the_contract`
   walks `machinome-skills` and passes. The seam's tests assume no
   contributor is installed; the suite's environment is to install one
   (Decision 10).
7. **The package built** from the rehearsal with the prototype manifest
   (`<scratch>/build.out`): `python -m build` exit 0; with the skills under
   `machinome/skills/bundled/`, setuptools warns three times "Package
   'machinome.skills.bundled...' is absent from the `packages`
   configuration" (`bundled`, `bundled.machinome`,
   `bundled.machinome.references`, the identifier-named directories; not
   `machinome-simulate`); under `machinome/skills/agent-skills/`, none
   (`<scratch>/build-alt.out`). The wheel holds 16 entries: `__init__.py`,
   `cli.py`, `installer.py`, `tools.toml`, the four skill files, the three
   licence files and five metadata files, no `machinome/__init__.py`; the
   sdist 33 entries, `tests/test_skill_format.py` among them and no
   `workflow/`; `twine check --strict` passes both. PyPI answers 404 for
   `machinome-skills` (12 October 2026).
8. **The command from the wheel** (`<scratch>/probe-command.out`,
   `<scratch>/probe-refusals.out`), run as `machinome` from the throwaway venv
   on scratch projects: `machinome -h` lists `skills` after `vet` with its
   docstring; `machinome skills -h` lists the three verbs; `install --tools
   claude,agents <project>` exit 0, eight files written and printed, each
   `SKILL.md` with the marker of Decision 6, nothing else in the project
   changed; the same again, exit 0; `update` "0.8.1, current" for the four
   copies, and after a copy's marker was edited to 0.8.0, "0.8.0 -> 0.8.1"
   for it alone; `list` the registry and the four copies with their versions
   and tools (`.agents/skills` read by `agents`, `codex` and `pi`). A user's
   own `.cursor/skills/machinome/SKILL.md`: `install --tools cursor` exit 1,
   nothing written, the line to run named; with `--force`, overwritten.
   Without `--tools` and no terminal, `agents`. An unknown id refused naming
   the valid ones; `all,claude` refused. `--tools none` exit 0, nothing
   written. With `HOME` under scratch, `--personal --tools opencode,codex`
   wrote `~/.config/opencode/skills/` and `~/.agents/skills/`; `--personal
   --tools trae` refused naming the project install. `--tools all`: 120 files
   in 30 directories (32 ids; `codex` and `pi` share `agents`'s).
9. **The picker** on a pseudo-terminal (`<scratch>/probe_picker.py`,
   `<scratch>/probe-picker.out`), a project holding `.claude/` and `.cursor/`:
   the numbered list marks `claude` (6) and `cursor` (14), Enter installs for
   those two, exit 0; the standard library's `input()` alone.
10. **Cost** (`<scratch>/probe_wall.py`, median of seven, the throwaway
    venv): with the package, `machinome -h` 899 ms, `vet -h` 55 ms, `skills
    -h` 108 ms, `skills list /tmp` 109 ms; without it, 991, 68 and 122 ms (the
    last two an invalid choice), the differences within the noise of the
    runs. `python -X importtime -c "import machinome.skills.cli"`: 1.6 ms of
    its own, 14.8 ms with the core's root.
11. **The lock.** In the rehearsal with the core's extra, the root's source
    and the dev group of Decision 10: `uv lock --offline` "Resolved 189
    packages", "Added machinome-skills v0.8.1" (the base lock 188); the diff
    (`<scratch>/uv-lock.diff`, 63 lines) adds the member, the dev group's
    `machinome[skills]`, the extra and the package's editable source.
12. **The projects.** `grep -rIl -e 'machinome\.skills' -e 'machinome skills'
    -e 'machinome-skills'` over `/home/asa/devel/machinome/projects`
    (excluding `.git`, `.venv`, `node_modules`, `.tools`, `WTs`, `_build*`):
    0 files (`<scratch>/projects-grep.txt`).
13. **The deltas, archived in scratch.** A copy of the bench's `openspec/`
    with this change's planning artifacts and a one-line tasks file
    (`<scratch>/os-probe`, `<scratch>/os-archive.out`): `openspec archive
    join-skills -y` creates `skills-distribution` (+ 6) and applies "+ 1
    added" to `cli` and `user-documentation`, "~ 2 modified" to
    `framework-identity` and "~ 1 modified" to
    `framework-contributor-guidance` (totals + 8, ~ 3); `openspec validate
    --specs --strict` passes 47 of 47. The created spec's Purpose is the
    CLI's placeholder, "TBD - created by archiving change join-skills", for
    the applier to write at the archive.

## Goals / Non-Goals

**Goals:**

- machinome-skills joins at `packages/machinome-skills/` with its history, its
  two skills unchanged in substance, under the set's licence and version.
- `machinome skills install|update|list`, contributed through the seam, writes
  the skills where each assistant documents that it reads them, refuses what
  it did not write, and deletes nothing.
- Its checks are tests run from its directory; the seam's own tests hold
  with a real contributor installed; `scripts/check-dist` proves the wheel.
- A reader of the manual gives an assistant the skills in two lines.

**Non-Goals:**

- Any change to the skills' instructions.
- The unification with the workspace's `simulate-project`, the studio's API
  skill, the studio's link to `machinome-simulate`.
- Slash commands, hooks or per-tool adapters; an uninstall verb; archives.
- A hint for `machinome skills` without the package (Open Questions 9).
- A version bump, an upload, a push.

## Decisions

### 1. The mapping and the import

| at 69e67ff | lands at | reason |
|---|---|---|
| `skills/machinome/SKILL.md`, `skills/machinome/references/mechanical-contracts.md` | `packages/machinome-skills/machinome/skills/agent-skills/machinome/` | package data at its final place (Decision 3); a skill directory whole, so an installed copy is the directory as shipped |
| `skills/machinome-simulate/SKILL.md`, `.../references/source-adaptation.md` | `packages/machinome-skills/machinome/skills/agent-skills/machinome-simulate/` | the same |
| `scripts/check.py` | `packages/machinome-skills/tests/test_skill_format.py` | its format checks become the package's tests, rewritten in place (Decision 11); its history reads at the test |
| `docs/evaluation.md` | `packages/machinome-skills/workflow/evaluation.md` | its working record, brought current in place (Decision 16) |
| `README.md` | `packages/machinome-skills/README.md` | the package's README, rewritten in place to the shape of the ten (Decision 2); its install table, examples and runtime requirements move to the how-to |
| `.gitignore` | `packages/machinome-skills/.gitignore` | edited in place to the package's own leavings (Decision 2) |
| `LICENSE`, `NOTICE` | dropped | one licence at the join; the package links the root's; `NOTICE`'s provenance goes to `CREDITS.md` |
| `skills/*/LICENSE.txt`, `skills/*/NOTICE` (four files) | dropped | an installed copy states the set's licence in its frontmatter, the texts being the repository's (Open Questions 6) |
| `requirements-dev.txt` | dropped | PyYAML, its one line, is in the core's `dev` extra, which the workspace installs; a package of the set keeps no requirements file |

The command, run by the orchestrator in a fresh clone (`git clone
file:///home/asa/devel/machinome/machinome-skills <dir>`), as rehearsed in
probe 4 (`<scratch>/filter-repo-command.sh`; the message expression is a
one-line file `literal: under <the last word of the subject>==>`, written by
the orchestrator from `git log -1 --format=%s`, so no record of this change
spells it):

```
git filter-repo \
  --path LICENSE --path NOTICE --path requirements-dev.txt \
  --path skills/machinome/LICENSE.txt --path skills/machinome/NOTICE \
  --path skills/machinome-simulate/LICENSE.txt --path skills/machinome-simulate/NOTICE \
  --invert-paths \
  --path-rename README.md:packages/machinome-skills/README.md \
  --path-rename .gitignore:packages/machinome-skills/.gitignore \
  --path-rename scripts/check.py:packages/machinome-skills/tests/test_skill_format.py \
  --path-rename docs/evaluation.md:packages/machinome-skills/workflow/evaluation.md \
  --path-rename skills/:packages/machinome-skills/machinome/skills/agent-skills/ \
  --replace-message <scratch>/replace-message.txt \
  --tag-rename ':skills-'
```

The product has no tag; `--tag-rename` is the plan's and renames nothing. The
rewritten commit keeps its author and date. The orchestrator then checks that
`git ls-tree -r --name-only main` lists the 8 paths of
`<scratch>/rehearsal-ls-files.txt`, that the head is 9a23c9a (*inferred*
deterministic: same input, same options) and its subject "Create portable
machinome skills package", fetches `main` into the bench and
merges it with `git merge --allow-unrelated-histories`, one merge commit,
after the planning commit. A move and an edit never share a commit: the
import lands each file where the applier edits it.

### 2. The package's directory

`packages/machinome-skills/` after the cycle holds `pyproject.toml`,
`README.md`, `MANIFEST.in`, `.gitignore`, the links `LICENSE ->
../../LICENSE` and `LICENSES -> ../../LICENSES`, the package directory
`machinome/skills/` (no `__init__.py` at `machinome/`), `tests/` and
`workflow/`. No `CHANGELOG.md`: the package is numbered with the set, and its
changes are the set's `HISTORY.rst` bullets, as an extension package's are.
No `openspec/`: its specification is the framework's `skills-distribution`.

`pyproject.toml`, new (probe 7 built it):

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-skills"
version = "0.8.1"
description = "The machinome skills for assistants that read Agent Skills, and the command machinome skills that installs them"
readme = { file = "README.md", content-type = "text/markdown" }
requires-python = ">=3.11"
license = "GPL-2.0-or-later OR CERN-OHL-S-2.0+"
license-files = ["LICENSE", "LICENSES/*.txt"]
authors = [
    { name = "Luis Fagundes", email = "lhfagundes@gmail.com" },
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
keywords = ["machinome"]
dependencies = [
    # The core whose command reads the group machinome.commands and whose
    # path extension admits this portion, numbered with it.
    "machinome~=0.8.1",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

# `machinome skills`, the second command a package contributes (ADR-189).
[project.entry-points."machinome.commands"]
skills = "machinome.skills.cli:Skills"

[tool.setuptools.packages.find]
# The package directory machinome/skills/, which has its own __init__.py,
# with none at machinome/, so the core's package path admits it.
include = ["machinome.skills"]
namespaces = true

[tool.setuptools.package-data]
# The registry and the skills, shipped as data: agent-skills/ is not an
# identifier, so setuptools reads none of it as a package.
"machinome.skills" = [
    "tools.toml",
    "agent-skills/*/SKILL.md",
    "agent-skills/*/references/*.md",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--import-mode=importlib"
```

`README.md`, replacing the product's, in the shape of the ten:

```markdown
# machinome-skills

The machinome skills for assistants that read
[Agent Skills](https://agentskills.io): `machinome`, for building and
verifying parts and assemblies with
[Machinome](https://github.com/machinome/machinome), and
`machinome-simulate`, for adding a simulation layer to an existing design;
and the command `machinome skills`, which installs them where each
assistant reads its skills.

## Install

    pip install "machinome[skills]"
    machinome skills install

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

`MANIFEST.in`, new: the sdist of a product that keeps its record carries it
(probe 7: without it, `workflow/` is absent):

```
recursive-include tests *.py
recursive-include workflow *.md
```

`.gitignore`, edited in place to the package's own leavings, as
`machinome-mechanics`'s (the root's covers `__pycache__/`, `*.py[cod]`,
`/.venv/`, `build/` and `*.egg-info/` under `packages/*/`):

```
# This package's leavings the root's .gitignore does not name: its own
# test runs and a local build.
.pytest_cache/
dist/
```

### 3. The portion and its data

- `machinome/skills/__init__.py`: the package's docstring (what it ships, the
  command, the specification `skills-distribution`), the SPDX line and the
  copyright of the set's files; it imports nothing.
- `machinome/skills/cli.py`: the class `Skills`, the contributed command
  (Decision 7's verbs); it imports nothing at module scope, so `machinome -h`
  pays for it what probe 10 measured, and `handle` imports the installer.
- `machinome/skills/installer.py`: the registry's reader, detection, the
  copies, the marker, `install`, `update`, `listing`; standard library only
  (`importlib.resources`, `importlib.metadata`, `tomllib`, `pathlib`,
  `re`), no PyYAML: the core does not require it, and the marker is written
  and read as text (Decision 6).
- `machinome/skills/tools.toml`: the registry as data (Decision 5).
- `machinome/skills/agent-skills/<skill>/`: the two skills. The name: not an
  identifier, so setuptools does not read the directories as packages missing
  from its configuration (probe 7: three warnings with `bundled/`, none with
  `agent-skills/`), and it names the format the directories follow. The
  skills are read with `importlib.resources.files('machinome.skills') /
  'agent-skills'`, from the source directory on an editable install and from
  `site-packages` on a wheel's.

The version a copy is marked with is `importlib.metadata.version('machinome-skills')`,
the installed distribution's, stated nowhere in the package's source but the
manifest.

### 4. The skills' content

The applier edits one line of each `SKILL.md`, after the join: `license:`
becomes `license: GPL-2.0-or-later OR CERN-OHL-S-2.0+`, the expression of the
set's manifests, a plain YAML scalar. Nothing else of the two `SKILL.md` and
the two references changes; `git diff <merge commit> -- <the four files>`
shows those two lines and nothing else. The instructions keep naming the
upstream repository and the official documentation as the API authority, and
keep their own words on Context7; whether a sentence would read better now
that the package is the framework's is a change to the skills' substance,
which the pilot's decision excludes.

### 5. The registry

`tools.toml` is an array of `[[tool]]` tables, one per id, in OpenSpec's order
after `agents`: `id`, `name` (OpenSpec's display name; `agents`: "Agent
Skills, the .agents convention"), `detect` (the paths whose presence in a
project marks the tool detected: OpenSpec's dot-directory, its seven
`detectionPaths` for `github-copilot`, and for Kilo Code and Windsurf the
client's current directory beside OpenSpec's), `project` (the skills
directory under a project) and `personal` (under the user's home, written
`~/...`; absent where the tool documents none). Every id of OpenSpec's 31 is
kept, spelled as OpenSpec spells it, so an id names the same tool in both
installers; `agents` is OpenSpec's id for its AGENTS.md entry, which it never
offers to `--tools` (probe 1), so the meaning here, the `.agents/skills/`
convention, takes nothing from it.

| id | detect | project | personal | source |
|---|---|---|---|---|
| `agents` | `.agents` | `.agents/skills/` | `~/.agents/skills/` | the Agent Skills convention, read by Codex, pi, OpenCode, Kilo Code, Gemini CLI and GitHub Copilot (probe 3) |
| `amazon-q` | `.amazonq` | `.amazonq/skills/` | `~/.amazonq/skills/` | OpenSpec; personal inferred |
| `antigravity` | `.agent` | `.agent/skills/` | `~/.agent/skills/` | OpenSpec; personal inferred |
| `auggie` | `.augment` | `.augment/skills/` | `~/.augment/skills/` | OpenSpec; personal inferred |
| `bob` | `.bob` | `.bob/skills/` | `~/.bob/skills/` | OpenSpec; personal inferred |
| `claude` | `.claude` | `.claude/skills/` | `~/.claude/skills/` | OpenSpec; Claude Code's documentation, read |
| `cline` | `.cline` | `.cline/skills/` | `~/.cline/skills/` | OpenSpec; Cline's documentation, search summary |
| `codex` | `.codex` | `.agents/skills/` | `~/.agents/skills/` | Codex's documentation, read; OpenSpec writes `.codex/skills/`, which Codex does not read |
| `forgecode` | `.forge` | `.forge/skills/` | `~/.forge/skills/` | OpenSpec; personal inferred |
| `codebuddy` | `.codebuddy` | `.codebuddy/skills/` | `~/.codebuddy/skills/` | OpenSpec; personal inferred |
| `continue` | `.continue` | `.continue/skills/` | `~/.continue/skills/` | OpenSpec; personal inferred |
| `costrict` | `.cospec` | `.cospec/skills/` | `~/.cospec/skills/` | OpenSpec; personal inferred |
| `crush` | `.crush` | `.crush/skills/` | `~/.crush/skills/` | OpenSpec; personal inferred |
| `cursor` | `.cursor` | `.cursor/skills/` | `~/.cursor/skills/` | OpenSpec; Cursor's documentation, search summary |
| `factory` | `.factory` | `.factory/skills/` | `~/.factory/skills/` | OpenSpec; personal the orchestrator's reading, 12 October 2026 |
| `gemini` | `.gemini` | `.gemini/skills/` | `~/.gemini/skills/` | OpenSpec; Gemini CLI's documentation, search summary |
| `github-copilot` | OpenSpec's seven `.github/...` paths | `.github/skills/` | `~/.copilot/skills/` | OpenSpec; GitHub's documentation, search summary |
| `iflow` | `.iflow` | `.iflow/skills/` | `~/.iflow/skills/` | OpenSpec; personal inferred |
| `junie` | `.junie` | `.junie/skills/` | `~/.junie/skills/` | OpenSpec; personal the orchestrator's reading, 12 October 2026 |
| `kilocode` | `.kilocode`, `.kilo` | `.kilo/skills/` | `~/.kilo/skills/` | Kilo Code's documentation, read; OpenSpec writes `.kilocode/skills/`, which it does not name |
| `kimi` | `.kimi` | `.kimi/skills/` | `~/.kimi/skills/` | OpenSpec; personal inferred |
| `kiro` | `.kiro` | `.kiro/skills/` | `~/.kiro/skills/` | OpenSpec; personal the orchestrator's reading, 12 October 2026 |
| `lingma` | `.lingma` | `.lingma/skills/` | `~/.lingma/skills/` | OpenSpec; personal inferred |
| `vibe` | `.vibe` | `.vibe/skills/` | `~/.vibe/skills/` | OpenSpec; personal the orchestrator's reading, 12 October 2026 |
| `oh-my-pi` | `.omp` | `.omp/skills/` | `~/.omp/skills/` | OpenSpec; personal inferred |
| `opencode` | `.opencode` | `.opencode/skills/` | `~/.config/opencode/skills/` | OpenSpec; OpenCode's documentation, read |
| `pi` | `.pi` | `.agents/skills/` | `~/.agents/skills/` | pi's documentation, read; OpenSpec writes `.pi/skills/` |
| `qoder` | `.qoder` | `.qoder/skills/` | `~/.qoder/skills/` | OpenSpec; personal inferred |
| `qwen` | `.qwen` | `.qwen/skills/` | `~/.qwen/skills/` | OpenSpec; personal inferred |
| `roocode` | `.roo` | `.roo/skills/` | `~/.roo/skills/` | OpenSpec; personal the orchestrator's reading, 12 October 2026 (probe 3's report of its shutdown not verified) |
| `trae` | `.trae` | `.trae/skills/` | none | OpenSpec; no personal directory documented (the orchestrator's reading, 12 October 2026) |
| `windsurf` | `.windsurf`, `.devin` | `.devin/skills/` | `~/.config/devin/skills/` | Devin Desktop's documentation, search summary (`.windsurf/skills/` and `~/.codeium/windsurf/skills/` legacy, still read); OpenSpec writes `.windsurf/skills/` |

Where OpenSpec's directory and the client's current documentation differ
(Codex, Kilo Code, pi, Windsurf), the id writes the client's documented
current directory and detects by both: a copy is useful only where the
assistant reads it, and OpenSpec's directory stays a detection path, so a
project that OpenSpec set up is still recognised (Open Questions 3). Rows
marked "inferred" take `~/<OpenSpec's dot-directory>/skills/`, as the
orchestrator directed, and are not verified; a later finding changes the data, not the
code.

A test holds OpenSpec's 31 ids and dot-directories, written out in the test
from `config.js` of 1.6.0, against the registry: every id present, each
dot-directory among its `detect` paths (for `github-copilot`, its seven
paths), and the four differing rows' `project` as the table states.

### 6. The marker

An installed `SKILL.md` is the shipped one with two lines of `metadata`
added at the end of its frontmatter:

```
---
name: machinome
description: ...
license: GPL-2.0-or-later OR CERN-OHL-S-2.0+
metadata:
  installed-by: machinome-skills
  version: "0.8.1"
---
```

`installed-by` names the package that wrote the copy, `version` its version,
quoted so YAML reads a string, as the format's `metadata` requires. A copy
is the command's when its `SKILL.md` frontmatter holds a `metadata` mapping
whose `installed-by` is `machinome-skills`; its version is that mapping's
`version`. The marker is written and read as text (a regular expression over
the frontmatter, as OpenSpec reads `generatedBy`), so a copy whose
frontmatter was reformatted out of that shape reads as not the command's and
is refused rather than overwritten. The shipped `SKILL.md` carries no
`metadata` (the format tests hold it to its three fields), so the marker is
the only difference between a copy and the package's file. A user who edits a
copy and wants it kept removes the marker; the how-to says so.

### 7. `machinome skills install`

```
machinome skills install [path] [--tools all|none|ID,ID...] [--personal] [--force]
```

- **The destinations.** For each tool chosen, `<path>/<project>`, or with
  `--personal` the tool's `personal` directory under the user's home, `path`
  then ignored; `path` defaults to the current directory and must be a
  directory. Tools sharing a directory (`agents`, `codex` and `pi`) write it
  once.
- **The copy.** Into each destination, each shipped skill as
  `<destination>/<skill>/`, every file the package ships for it at its
  relative path (`SKILL.md` with the marker, `references/<file>`), directories
  created as needed. Every file written is printed, under a line naming the
  destination and the ids it serves:

  ```
  <path>/.claude/skills/ (claude)
    wrote <path>/.claude/skills/machinome/SKILL.md
    wrote <path>/.claude/skills/machinome/references/mechanical-contracts.md
    ...
  ```

  No other file is written, renamed or removed: a file already in a copy and
  not shipped stays as it is.
- **What is refused.** Before anything is written, each target
  `<destination>/<skill>/` that exists and is not the command's (Decision 6)
  is refused, unless `--force`; then nothing is written, each refused target
  is named on one line and the line to run follows, exit 1:

  ```
  Error: <path>/.cursor/skills/machinome holds a skill machinome skills did not write; nothing was written
  To replace it, run: machinome skills install --tools cursor --force <path>
  ```

  A target that is the command's, of any version, is rewritten, its old and
  new versions printed. `--personal` with a tool that has no personal
  directory is refused before anything is written, exit 1: `Error: trae
  documents no personal skills directory; install it into a project:
  machinome skills install --tools trae <project>`. A `path` that is not a
  directory: `Error: <path> is not a directory`, exit 1.
- **`--tools`.** `all`, every id; `none`, no tool, exit 0 with "Nothing
  installed: --tools none"; otherwise ids separated by commas, case-folded and
  deduplicated in order. An unknown id, `all` or `none` beside an id, or an
  empty value is a usage error, exit 2, naming the valid values as OpenSpec
  does: `machinome skills install: error: unknown tool 'x'; use all, none or
  ids from: agents, amazon-q, ...` (or "all and none stand alone").
- **Without `--tools`.** Interactive when standard input is a terminal and
  `CI` is not set (OpenSpec's rule, probe 1): a numbered list of the
  registry, the pre-selected tools marked `*` (the tools whose directories
  under `path` already hold a copy that is the command's; when none does, the
  tools detected under `path`; when none is detected, `agents`), and one
  prompt, `Tools (Enter for the marked ones; numbers or ids separated by
  commas; all; none):`. Enter takes the marked ones; an answer is read as
  `--tools` is, numbers standing for their rows; an invalid answer is named
  and asked again; end of input installs nothing, exit 1. Not interactive:
  `agents`, with one line first, `No --tools given and no terminal to ask:
  installing for agents (.agents/skills/); name others with --tools`.
- **Exit status.** 0 when every chosen destination was written or none was
  chosen; 1 on a refusal; 2 on a usage error.

The picker is the standard library's `input()` over a numbered list (probe
9); no dependency enters the core or the package (Open Questions 4).

### 8. `machinome skills update`

```
machinome skills update [path] [--personal] [--force]
```

For each distinct directory of the registry (`project` under `path`, or
`personal`), each shipped skill's target that exists is reported on one line:

- not the command's: `<target>: not written by machinome skills, left as it
  is`;
- the command's at the installed version: `<target>: 0.8.1, current`;
- at an older version (versions compared as tuples of integers): its files
  rewritten as `install` writes them, printed, then `<target>: 0.8.0 ->
  0.8.1`;
- at a newer version, or one that is not numeric: `<target>: 0.9.0, newer
  than 0.8.1, left as it is`.

`--force` rewrites every copy that is the command's, current or newer, never
one that is not. Nothing is removed. With no target under any directory:
`No copy of the machinome skills under <path>; install them with: machinome
skills install`, exit 0. OpenSpec rewrites on any difference (probe 1); the
pilot's criterion is "older", so a copy left by a newer package installed
elsewhere is not downgraded unasked. `--personal` is on `update` and `list`
as on `install`, since a personal copy is otherwise one no verb could update
or show.

### 9. `machinome skills list`

```
machinome skills list [path] [--personal]
```

Prints the registry, one row per id (`id`, `project`, `personal` or `-`,
`name`), then `Installed under <path>:` (or `Installed in your home:`) and,
for each target that exists, `<target> (<ids>): <version>, current|older
than <installed>|newer than <installed>` or `not written by machinome
skills`; `none` when nothing is there. Exit 0.

### 10. The core and the workspace

- **The extra**, in the core's `pyproject.toml` before `all`:

  ```toml
  # The machinome skills and the command `machinome skills` that installs
  # them into assistants' skill directories (`machinome.skills`), the
  # repository's distribution machinome-skills, numbered with the set.
  skills = [
      "machinome-skills~=0.8.1",
  ]
  ```

  `all` stays the kernels' (`test_all_names_every_kernel_extra`); `dev` does
  not name it either: the core's development extra installs what the core's
  suite runs, and the workspace's group installs the products.
- **The root's `pyproject.toml`**: `machinome-skills = { workspace = true }`
  after `machinome-node-stl`; the dev group `["machinome[dev]",
  "machinome[mechanics]", "machinome[skills]"]`, its comment gaining "and the
  skills package, whose tests run from its directory and whose command the
  suite's conformance walk reads". The package must be installed for its own
  tests (they import it) and for the walk of Decision 12 to read a real
  contributor; a virtual workspace root syncs only its groups' closure.
- The applier runs `uv lock` (expected "Resolved 189 packages", the diff of
  probe 11) and `uv sync --python 3.12` (expected a fourteenth
  `__editable__` `.pth` file naming `packages/machinome-skills`). Then from
  `/tmp`: `<bench>/.venv/bin/machinome skills -h` lists the three verbs, and
  `<bench>/.venv/bin/python -c "import machinome.skills;
  print(machinome.skills.__file__)"` names the bench's package directory.

### 11. The tests at their new place

`packages/machinome-skills/tests/`, run with `python -m pytest` from the
package's directory on the synced workspace, collected by no core run.

- **`test_skill_format.py`**, rewritten in place from `check.py`, each check a
  test over the shipped skills (read from the package directory, not from an
  installed copy): exactly `machinome` and `machinome-simulate` under
  `agent-skills/`; real files, no link; the frontmatter's keys exactly
  `name`, `description`, `license`; the name valid by the format and equal to
  its directory; the description 1 to 1024 characters; the `license` equal to
  the framework's manifest's `license`, the set's expression; `SKILL.md` under 500 lines; every local
  Markdown link of a skill's files resolving inside that skill; every
  `references/` file linked from its `SKILL.md`; each skill holding only
  `SKILL.md` and `references/*.md` (no licence or notice file); every shipped
  file matched by a `package-data` pattern of the manifest. Dropped from
  `check.py`: the package-level file list and its links (the README's links
  are the layout gate's), the root licence text check (the repository's), the
  per-skill licence and notice equality (the files are gone), and the archive
  builder. Red at the join: the module collects no test; after the rewrite,
  the licence test fails on both skills (the field names the licence the
  product carried) until Decision 4's edit.
- **`test_command.py`**, new, through scratch directories (`tempfile`), the
  installer's functions in process and `machinome` in a subprocess where the
  dispatch is under test: the registry against OpenSpec's 31 ids (Decision 5)
  and its four differing rows; `install` writing each skill whole into each
  chosen destination with the marker, printing every path, the tree outside
  the copies unchanged; a shared directory written once; the copies equal to
  the shipped files but for the marker's lines, and the installed frontmatter
  parsing as YAML with `metadata` a map of strings; a user's skill of the same
  name refused with nothing written and exit 1, then overwritten with
  `--force`, a file of its own beside it kept; `--tools none`, `all`, an
  unknown id and `all,claude` (exit 2); no terminal (standard input patched
  not to be one, or `CI` set) installing for `agents`; the prompt with
  standard input a terminal and `input` patched: Enter, a number, ids, an
  invalid answer then a valid one; `--personal` with `HOME` under the scratch
  directory, and refused for `trae`; `update` on an older, a current, a newer
  and a foreign copy, with and without `--force`, nothing removed; `list`
  with and without copies; `machinome -h` listing `skills` with its docstring
  and `machinome skills install --tools claude <dir>` exit 0 through the
  installed entry point. Red before the package's modules exist:
  `ModuleNotFoundError: No module named 'machinome.skills.installer'` at
  collection, and the subprocess `machinome skills` exiting 2 with invalid
  choice.

### 12. The core's tests

- **`tests/test_repository_layout.py`**: `PRODUCTS` gains

  ```python
  'machinome-skills': ('machinome.skills', 'skills',
                       ('.gitignore', 'LICENSE', 'LICENSES', 'MANIFEST.in',
                        'README.md', 'machinome', 'pyproject.toml', 'tests',
                        'workflow')),
  ```

  and its comment says a product keeps its record in its directory, its
  specs there or in the framework's (`join-skills`).
  `test_each_product_keeps_its_tests_and_specs` becomes: every product's
  `tests/` holds a `test_*.py`, and a product listing `openspec` among its
  entries holds `openspec/specs/`. The check that mechanics' `tests/` holds a
  `pyproject.toml` goes from the gate: that file is the `[tool.machinome]`
  table that makes mechanics' integration tests a project, and those tests
  fail without it (*inferred* from its comment; the applier proves it once
  by moving the file aside in a scratch copy).
  `test_the_default_group_is_the_framework_dev_and_mechanics_extras` is
  renamed `test_the_default_group_is_the_framework_dev_and_the_products_extras`
  and expects the three entries. The module's docstring gains the skills.
  Red at the join (probe 5) and until the package exists: the workspace
  source, the members, the README, the table, the guide; then the product's
  entries, manifest, README, resolution, the CI step and the default group.
- **`tests/test_machinome_identity.py`**: the extras' loop gains `('skills',
  'machinome-skills')`. Red: `KeyError: 'skills'`.
- **`tests/test_kernel_extras.py`**: `EXTRAS` gains `'skills':
  {f'machinome-skills~={VERSION}'}`, with the comment "`join-skills`: the
  skills package, a product numbered with the set, not a kernel". Red:
  `KeyError: 'skills'`.
- **`tests/test_docs_structure.py`** (Decision 15): the How-to toctree names
  `howto/assistant-skills`, whose page spells `pip install
  "machinome[skills]"`, `machinome skills install`, `machinome skills
  update`, `machinome skills list`, `--tools` and `--personal`;
  `test_the_installation_page_names_the_extension_distributions` gains
  `machinome-skills`; a test that `reference/cli.rst` has the section
  `machinome skills` naming `install`, `update`, `list`, `--tools`,
  `--personal` and `--force`, and no longer says the skills package is "to
  add" its command. Red: the page, the distribution, the section.
- **The seam's tests** (probe 6). In `tests/contributed_commands.py`, the fake
  `fake-skills` becomes `fake-lessons`, its entry `lessons =
  machinome_fake_lessons:Lessons`, its docstring "Teach a lesson (a fake
  contributed command).", so no fake takes the name of a package of the set
  that the suite installs. In `tests/test_cli_contributed.py`, the choices the
  help and the gone module's test expect are computed: the framework's
  `COMMAND_ORDER`, then the names of the suite's own contributed commands
  (read once from `importlib.metadata.entry_points(group='machinome.commands')`,
  distributions whose name begins `fake-` excepted) together with the test's
  fakes, sorted by name; `test_a_second_contributor_runs` runs `lessons
  install`. In `tests/test_cli_lazy_imports.py`,
  `test_the_contract_walk_reads_a_fake_distribution` compares the failures of
  the fakes' distributions alone. Red: probe 6's four failures, once the sync
  installs the package.
- **What the conformance walk then proves.**
  `test_every_contributed_entry_resolves_and_honours_the_contract`, vacuous
  until now, walks `machinome-skills`'s entry in the suite's environment: its
  name is not a framework command's, its distribution is not `machinome`, no
  other distribution declares `skills`, `machinome.skills.cli:Skills` imports
  and constructs with no argument, carries a docstring, `add_arguments` and
  `handle`, and declares `needs_node` as a boolean. It proves the shipped
  class meets the seam's contract from the source tree; it does not prove the
  verbs (the package's tests) or the built wheel's entry point
  (`scripts/check-dist`). Its red is shown once by a temporary edit
  deleting `needs_node` from `Skills`, one run, reverted, as the seam's own
  cycle showed its guards.

### 13. The version records

`.bumpversion.cfg` gains, after the FreeCAD package's tables:

```
[bumpversion:file(version):packages/machinome-skills/pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file(pins):packages/machinome-skills/pyproject.toml]
search = ~={current_version}"
replace = ~={new_version}"
```

The core's `pins` table already moves `machinome-skills~=0.8.1"`.
`tests/test_release_records.py` holds the rest unchanged: the member numbered
with the core, its pins `~=` both ways, its manifest named by a table. Red
before the tables: `test_the_version_is_bumped_from_the_root` names the
manifest. The applier proves the bump on a copy, as `join-freecad` did:
`bump2version --no-commit --no-tag --new-version 0.9.0 patch` over a scratch
git copy of the root's configuration and the files it names, the skills
manifest's version and pin moving to 0.9.0.

### 14. `scripts/check-dist` and CI

`scripts/check-dist` needs a row, or it fails "machinome-skills has no smoke
in scripts/check-dist". Installed from its wheel by path, like
`machinome-mechanics`'s, not through `machinome[skills]`: no index serves the
name (probe 7, 12 October 2026), and an install through the extra would let pip consult
the index for a name the set does not yet own there; the smoke proves the
extra's requirement from the core's metadata instead. The row, after the
mechanics package's:

```python
    'machinome-skills': {
        # Installed from its wheel by path: the smoke reads the extra's
        # requirement from the core's metadata.
        'extras': [],
        'code': '''
import importlib.metadata as metadata
import subprocess
import tempfile
from pathlib import Path
import machinome.skills as skills
distribution = metadata.distribution('machinome-skills')
version = metadata.version('machinome')
assert distribution.version == version, (distribution.version, version)
files = [str(path) for path in distribution.files]
shipped = sorted(path for path in files if path.startswith('machinome/'))
assert shipped == sorted([
    'machinome/skills/__init__.py', 'machinome/skills/cli.py',
    'machinome/skills/installer.py', 'machinome/skills/tools.toml',
    'machinome/skills/agent-skills/machinome/SKILL.md',
    'machinome/skills/agent-skills/machinome/references/mechanical-contracts.md',
    'machinome/skills/agent-skills/machinome-simulate/SKILL.md',
    'machinome/skills/agent-skills/machinome-simulate/references/source-adaptation.md',
]), shipped
owned = Path(distribution.locate_file('machinome/skills/__init__.py')).resolve()
assert owned == Path(skills.__file__).resolve(), (owned, skills.__file__)
assert owned.is_relative_to(Path(VENV).resolve()), owned
assert f'machinome~={version}' in distribution.requires, distribution.requires
core = metadata.requires('machinome')
assert any(line.startswith(f'machinome-skills~={version}')
           and 'skills' in line.partition(';')[2] for line in core), core
(entry,) = [entry for entry in metadata.entry_points(group='machinome.commands')
            if entry.name == 'skills']
assert entry.value == 'machinome.skills.cli:Skills', entry.value
project = Path(tempfile.mkdtemp())
run = subprocess.run([str(Path(VENV) / 'bin' / 'machinome'), 'skills',
                      'install', '--tools', 'agents,claude', str(project)],
                     capture_output=True, text=True)
assert run.returncode == 0, run.stdout + run.stderr
copies = sorted(path.relative_to(project).as_posix()
                for path in project.rglob('*') if path.is_file())
assert copies == sorted(f'{base}/{name}' for base in
                        ('.agents/skills', '.claude/skills') for name in (
    'machinome/SKILL.md', 'machinome/references/mechanical-contracts.md',
    'machinome-simulate/SKILL.md',
    'machinome-simulate/references/source-adaptation.md')), copies
for copy in project.glob('*/skills/*/SKILL.md'):
    text = copy.read_text()
    assert 'installed-by: machinome-skills' in text, copy
    assert f'version: "{version}"' in text, copy
    assert 'license: GPL-2.0-or-later OR CERN-OHL-S-2.0+' in text, copy
'''
        + LICENCES.substitute(name='machinome-skills')
        + '''
print('machinome-skills', distribution.version, 'installed',
      len(copies), 'files for agents and claude')
''',
        'commands': [['machinome', 'skills', 'list']],
    },
```

Red first: before the row, the script fails naming the package.

CI: the `test` job of `.github/workflows/python-app.yml` gains, after the
mechanics package's step:

```yaml
      # The skills package keeps its tests in its own directory (change
      # `join-skills`); the workspace synced above installs it.
      - name: Run the skills package's tests
        working-directory: packages/machinome-skills
        run: python -m pytest
```

The layout gate's `test_the_test_job_runs_each_product_s_tests` requires it.
Lint already reads `../machinome-*/machinome`.

### 15. The manual

- **A how-to, `howto/assistant-skills.rst`, "Give your assistant the
  machinome skills"**, in How-to guides after `howto/mechanism-formulas`. One
  job: an assistant that reads Agent Skills builds or simulates a machine with
  the skills. Its content, by reader intent, from the product's README:
  what each skill is for, one sentence each; the two install lines `pip
  install "machinome[skills]"` and `machinome skills install` (the prompt and
  its pre-selection; `--tools claude,codex` to name them; `machinome skills
  list` for every tool and where it reads); `--personal` for every project;
  `machinome skills update` after upgrading the package; what the command
  never does (overwrite a skill it did not write without `--force`, delete a
  file) and the marker, with the advice to remove it from a copy to keep
  one's edits; how to ask for a skill (the README's two example requests);
  and what the assistant needs to do the work (file access, command
  execution, image inspection, machinome and the project's CAD tools
  installed). No table of tools: the registry is data that `machinome skills
  list` prints, and a copied table would drift.
- **`start/install.rst`**: "Two more extras exist" becomes "Three more extras
  exist", gaining ``skills`` installs the :doc:`machinome skills
  </howto/assistant-skills>` for assistants and the command ``machinome
  skills`` (the distribution ``machinome-skills``); "Packages and licences"
  names ``machinome-skills`` after ``machinome-mechanics``, under the same
  licence.
- **`reference/cli.rst`**: in "Commands from other packages", the closing
  sentence becomes "The skills package adds ``machinome skills``, below; the
  videomaker (``machinome movie``) and the studio (``machinome studio``) are
  to add theirs."; then a section `machinome skills` with its anchor
  `.. _skills-command:`: the synopsis of the three verbs, each option, the
  exit statuses, the marker in one sentence, and a link to the how-to.
- The framework's `README.rst` is unchanged: its extras paragraph is held to
  its words by `ReadmeTest`, and the root README's table lists the package.
- The build: `sphinx -b html -n -W --keep-going` with `docs/requirements.txt`
  alone, exit 0, and the new page looked at.

### 16. The records

- **`HISTORY.rst`**, at the end of `Unreleased`, after the seam's bullet:

  ```
  * **The machinome skills join the repository, with a command that
    installs them.** machinome-skills, the skills ``machinome`` and
    ``machinome-simulate`` for assistants that read Agent Skills, kept in a
    repository of its own since 20 September 2026, is the package
    ``machinome-skills`` at ``packages/machinome-skills/``, its history kept,
    numbered with the set and installed by ``pip install
    "machinome[skills]"``. Its command, ``machinome skills``, the second a
    package adds to ``machinome``, installs the skills where each assistant
    reads them: ``install`` for the tools named by ``--tools`` (OpenSpec's
    tool ids, and ``agents`` for ``.agents/skills/``) or chosen at a prompt
    that pre-selects the tools found in the project, ``--personal`` for the
    user's own directories, ``update`` and ``list``. A copy carries a marker;
    a skill the command did not write is refused unless ``--force``, and the
    command deletes nothing. The skills are unchanged but for their licence
    field, the set's. Change ``join-skills`` (ADR-190).
  ```

- **`docs/project/changelog.rst`**, at the end of `Unreleased`:

  ```
  * **Give your assistant the machinome skills.** ``pip install
    "machinome[skills]"`` then ``machinome skills install`` copies the
    skills ``machinome`` and ``machinome-simulate`` into the directories your
    assistants read, ``machinome skills update`` keeps them current, and
    ``machinome skills list`` shows where each tool reads
    (:doc:`/howto/assistant-skills`, :ref:`skills-command`).
  ```

- **`CREDITS.md`**: a section after the FreeCAD package's, "### Adapted from
  Machinome Studio, in the skills package": "The package `machinome-skills`
  (`machinome.skills`) ships the skills `machinome` and `machinome-simulate`,
  whose mechanical workflow guidance is adapted from the `machinome` and
  `simulate-project` skills of Machinome Studio
  (<https://github.com/machinome/machinome-studio>), with revisions for
  independent, cross-harness use and documentation-based API lookup.
  Copyright 2026 Luis Henrique Cassis Fagundes, the author of both."; the
  file's last-updated line 2026-10-12. No row in the licence table: the
  adaptation is the same author's work, not a dependency.
- **`docs/architecture.md`**: in "CLI", after the paragraph on contributed
  commands, "The first is `machinome skills`, from the repository's
  distribution `machinome-skills` (ADR-190)."; a section "Skills package (the
  distribution `machinome-skills` · spec `skills-distribution`)": the two
  skills as package data, the registry, the copy with its marker, the
  refusal, no deletion, the package's tests and working record in its
  directory; the Map gains the row "Skills package, the distribution
  `machinome-skills`" | "the repository's `packages/machinome-skills/`
  (`machinome/skills/`: `cli.py`, `installer.py`, `tools.toml`,
  `agent-skills/`; its own `tests/` and `workflow/`)" | `skills-distribution`
  | "187, 189, 190"; the extras sentence gains "`[skills]` for the
  machinome skills".
- **The root `README.md`**: a row after the mechanics helpers':
  ``| [`machinome-skills`](packages/machinome-skills/) | The machinome skills for assistants that read Agent Skills, `machinome` and `machinome-simulate`, and the command `machinome skills` that installs them; installed by `machinome[skills]`. |``
- **`CONTRIBUTING.rst`**: the pip block gains `-e packages/machinome-skills \`
  after the mechanics line; "Running tests" gains "The skills package keeps
  its tests in its own directory: run ``python -m pytest`` from
  ``packages/machinome-skills``." after the mechanics sentence.
- **`context7.json`**: `excludeFolders` gains `packages/machinome-skills/tests`
  and `packages/machinome-skills/workflow`; `rules` gains one: "The machinome
  skills for assistants that read Agent Skills, machinome and
  machinome-simulate, are installed by pip install \"machinome[skills]\" then
  machinome skills install [path] [--tools all|none|ids] [--personal]
  [--force], which copies each skill into the directories the named tools
  read (ids as OpenSpec's, and agents for .agents/skills/); machinome skills
  update rewrites older copies and machinome skills list prints the tools. A
  copy carries metadata installed-by: machinome-skills; a skill without it is
  refused unless --force, and nothing is deleted."
- **`AI-USE.md`**: the paragraph on what is agent-written gains "and the
  machinome skills under `packages/machinome-skills/`, founded in a
  repository of their own after the line and joined here with their history"
  after the mechanics helpers.
- **The product's `workflow/evaluation.md`**, brought current in place: its
  "Mechanical checks" section says the format checks are the package's tests
  (`python -m pytest` from `packages/machinome-skills`), and that a trial
  installs the skills with `machinome skills install --tools <id> <project>`
  into a disposable project instead of extracting an archive; a section
  "Distribution since the join (12 October 2026)" says what the join changed:
  the skills ship in the wheel of `machinome-skills`, installed by
  `machinome[skills]` and copied by the command with a marker; the per-skill
  licence and notice files are gone and each frontmatter states the set's
  licence; no archive is built; the live cases are still not run in any
  harness. Its live cases and its "Initial validation boundary" of 20
  September 2026 stay as written, a record of their day.
- **ADR-190** (recommended, Open Questions 5),
  `docs/adrs/BUILD/ADR-190-the-machinome-skills-are-a-package-of-the-set-installed-by-a-command.md`,
  "The machinome skills are a package of the set, installed into assistants'
  directories by a command", Status Proposed, Change `join-skills`, Related to
  ADR-183 (one version), ADR-187 (the products table; this is the first
  product numbered with the set and specified by the framework) and ADR-189
  (the seam; its second contributor). Context: the pilot's decisions; probes
  1, 2, 3 and 8. Options: (1) a product of the set at the set's version, its
  tests and working record in its directory, its specification the
  framework's, its command on OpenSpec's criteria with a marker, refusal and
  no deletion (chosen); (2) the skills inside the core's package (refused:
  the pilot's decision names a distribution); (3) OpenSpec's behaviour whole,
  overwriting by name (refused: probe 2 shows it overwrote a user's skill);
  (4) per-tool adapters or slash commands (refused: the skills carry none,
  so one writer serves every tool); (5) a picker library (refused: no
  dependency for one prompt, probe 9). Decision: Decisions 2 to 9 and 14.
  Consequences: good, one install line and one command for every assistant,
  the skills at the set's version and licence; bad, the registry's inferred
  personal directories are unverified and a client that moves its directory
  needs a release, `update` cannot know of a file a newer version stopped
  shipping, and the seam's tests now read the environment's contributors;
  neutral, the core imports nothing of the package. Index line under BUILD
  after ADR-189's.
- **The plan's progress** (`workflow/ongoing/joins-0.9.md` or
  `release-0.9.md`, as the orchestrator keeps them): the cycle's entry at its
  close.

### 17. Validation and the originating check

- The whole suite, one process, from the framework's directory on the bench
  venv: no failure, the base's skips, the passed count the base's (4854
  passed, 24 skipped at 5af14f71) with each added test named.
- The package's tests from its directory: no failure; their count.
- The manual with warnings as errors (Decision 15); the new page looked at.
- `scripts/check-dist` on the tree and on a clean copy of the tracked tree:
  fourteen members, 28 archives `twine check --strict`, the skills row's line
  and `machinome skills list`'s exit 0, nothing uploaded.
- The originating check, the job the product's README gave a reader by hand:
  a scratch git project; `machinome skills install --tools agents,claude` from
  the bench venv; the copies at `.agents/skills/<skill>/SKILL.md` and
  `.claude/skills/<skill>/SKILL.md`, the paths Codex's and Claude Code's
  documentation name for discovery (probe 3), each a valid skill by the
  format (`name` equal to its directory) with the marker; where the `claude`
  and `codex` programs are installed on the machine, each asked to list its
  skills in that project and naming both (recorded as not run where a
  program is absent); then one copy's marker edited to an older version and
  `machinome skills update` rewriting it alone; `git -C <project> status
  --short` showing only the two directories.
- **No universe sweep**: no project repository names the package, its
  module or its command (probe 12, 0 files; the applier repeats the grep on
  the final tree's day), the core's modules are unchanged, and the extra installs nothing
  a project's model loads; the sweep would read the base's rows.

### 18. Deferred, and the workspace follow-ups

- **Deferred by the pilot, unchanged here**: the workspace's
  `skills/simulate-project/SKILL.md` (a 326-line repository-agent procedure
  under the workspace's OpenSpec and worktree discipline) and
  `machinome-simulate` (a portable 127-line skill with no workspace path)
  stay two skills; the studio's `shop-skills/machinome/SKILL.md` (919 lines,
  runtime craft served to the floor's agents through its MCP server, not
  through a dot-directory) and `shop-skills/machinome-api/SKILL.md` are
  untouched, and the studio's link to `machinome-simulate` is the studio's
  join's. Nothing of them is read by this package.
- **Workspace follow-ups**, listed for the orchestrator, none done here: the
  operating contract (`AGENTS.md`) names no machinome-skills (12 October 2026, grep, 0
  lines), so a status sentence for the joined package is the consistency
  cycle's; `docs/collaborator-setup.md` lines 31 and 97 to 100 clone the
  original repository, to be replaced by "installed by the workspace's
  sync"; the original repository's archiving on GitHub is the pilot's.

### 19. The spec deltas

- `skills-distribution`: new, six requirements (what ships; the registry;
  install; update; list; nothing deleted).
- `cli`: ADDED "Skills command".
- `framework-identity`: MODIFIED "Extras select independent Machinome
  products" (the `skills` extra; one scenario added) and "The framework is the
  package directory `packages/machinome` of a monorepo" (the skills product,
  numbered with the set, its tests and working record in its directory, its
  smoke from its wheel; three scenarios added, two restated with their titles
  kept).
- `user-documentation`: ADDED "The machinome skills are documented as a
  how-to".
- `framework-contributor-guidance`: MODIFIED "The contributor guide states
  the monorepo's development setup" (the pip command and the tests'
  directory; one scenario restated, one added).

Each MODIFIED requirement is copied whole from its baseline and edited; every
existing scenario keeps its title.

## Risks / Trade-offs

- [A personal directory in the registry is wrong for a tool] → Fifteen rows
  are inferred from OpenSpec's dot-directory and marked so; a wrong one
  writes a directory the tool never reads, which `list` shows; the registry
  is data, corrected by a finding.
- [A client moves its directory, as Windsurf's did] → The id detects both and
  writes the current one; a later move is a data change and a release.
- [`update` cannot remove a file a newer version stops shipping] → By the
  pilot's rule nothing is deleted; `update` meets no such file at 0.8.1 (both
  versions ship the same four), and the risk is recorded in ADR-190.
- [A user edits a marked copy and runs `update` after an upgrade] → The copy
  is rewritten, as OpenSpec's would be; the how-to says to remove the marker
  to keep one's edits.
- [The seam's tests now depend on what the suite's environment installs] →
  They read it once and compute the expectation; the movie's join, beside this
  one, installs `machinome movie` and meets the same assumption with the fake
  `fake-movie` (probe 6's shape), which its own cycle owns.
- [`machinome skills` without the package is argparse's invalid choice] →
  The seam answers only installed contributors (ADR-189, Decision 7); a hint
  naming the extra is a decision for the seam (Open Questions 9).
- [The commit message of the join is rewritten] → The original repository
  keeps the original commit and its hash; only the trailing words naming the
  licence go.
- [The joined history's README, check script and frontmatter state the
  licence the product carried] → Historical contents, as in `join-mechanics`;
  every file this change writes states the set's.

## Migration Plan

In the order of tasks.md: the baseline; the join, by the orchestrator, and
its reds; the red tests; the package; the core, the workspace and the sync;
the seam's tests; the manual; the version records, `check-dist` and CI; the
records; validation and the originating check; the archive. Rollback is a
revert of the implementation commit and of the merge commit, then `uv lock`
and `uv sync`; copies a user installed carry the marker and stay where they
were written.

## Open Questions

1. **The data directory.** `machinome/skills/agent-skills/<skill>/`, or
   `bundled/` as the orchestrator suggested, or the skill directories beside the
   modules. Recommendation: `agent-skills/` (Decision 3): setuptools reads an
   identifier-named data directory as a package missing from its
   configuration and warns three times at every build (probe 7), and a skill
   directory named `machinome` beside the modules would read as a subpackage
   `machinome.skills.machinome`.
2. **The marker's fields.** `installed-by: machinome-skills` and `version:
   "0.8.1"` under `metadata`; or OpenSpec's `author` and `version`; or one key
   `machinome-skills: "0.8.1"`. Recommendation: `installed-by` and `version`:
   two fields like OpenSpec's author and version, as the pilot asked, with a
   key that says what wrote the copy, which `author` would misstate (the
   skills' author is not the package), and reasonably unique as the format
   recommends.
3. **The differing directories.** Codex, Kilo Code, pi and Windsurf write the
   client's current documented directory (`.agents/skills/`,
   `.kilo/skills/`, `.agents/skills/`, `.devin/skills/`) and detect by
   OpenSpec's too; or OpenSpec's directories, so both installers agree.
   Recommendation: the clients' (Decision 5); OpenSpec's `.codex/skills/` and
   `.kilocode/skills/` are not in their clients' documentation, and a copy
   where the assistant does not look installs nothing.
4. **The picker.** A numbered prompt on standard input, OpenSpec's rule for
   when to ask; or a picker library (OpenSpec's is its own prompt over
   `@inquirer/core`; Python's equivalents are third-party). Recommendation:
   the numbered prompt (probe 9); no dependency enters the core or the
   package for one question.
5. **The ADR.** ADR-190, or none (the decisions are the pilot's and the
   seam's ADR-189 covers the command). Recommendation: ADR-190: the join
   makes choices no record holds, the first product numbered with the set and
   specified by the framework, and an installer whose rules (marker, refusal,
   no deletion, the registry's directories) differ from OpenSpec's on
   evidence. If declined, the HISTORY bullet ends "(ADR-189)".
6. **The licence in an installed copy.** The frontmatter's `license` field
   alone, or a notice file beside each copy. Recommendation: the field alone:
   the format allows a licence name there, the texts are the repository's and
   travel with the distribution's metadata, and a notice file in every copy
   multiplies a statement the pilot's rule keeps in one place.
7. **The joined commit's message.** Its subject ends by naming the licence
   the product carried. Rewrite it at the import (`--replace-message`, probe
   4: "Create portable machinome skills package") or keep it as written.
   Recommendation: rewrite: the join writes that commit into the
   repository's history under a new hash, and the common rule is that no new
   text names the licence a product carried; the original repository keeps
   the original.
8. **The dev group.** `machinome[skills]` in the root's default group, which
   puts a real contributor in the suite's environment and needs the seam's
   tests made to read it (Decision 12); or left out, with the package's tests
   run on a separate install. Recommendation: in the group: the package's
   tests need it installed, the CI step reuses the synced workspace, and the
   conformance walk stops being vacuous.
9. **`machinome skills` without the package.** Argparse's invalid choice
   on 12 October 2026, as for any name nothing contributes. A hint naming `pip install
   "machinome[skills]"` would have the core name a product, against the
   seam's decision that it does not, and the movie and the studio would want
   the same. Recommendation: not in this change; a question for the pilot
   about the seam.
10. **The registry's unverified rows.** Fifteen personal directories are
    inferred and Roo Code's service is reported closed. Keep every OpenSpec id
    with its inferred directory, or drop the rows no source confirms.
    Recommendation: keep all 31: an id means the same in both installers, a
    wrong personal directory harms nothing but itself, and `list` shows each.

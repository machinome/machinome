## Why

On 12 October 2026 the pilot settled what Machinome 0.9.0 contains
(`workflow/ongoing/release-0.9.md` at the repository root, decisions 1, 2, 4
and 6): machinome-skills, the two assistant skills `machinome` and
`machinome-simulate` written in the Agent Skills format and kept since
20 September 2026 in a repository of their own, joins the repository as it is,
as the distribution `machinome-skills` at `packages/machinome-skills/`, the
portion `machinome.skills`, at the set's version and under the set's licence,
installed by a new extra `machinome[skills]`; and its command, `machinome
skills`, the second contributor of the group `machinome.commands` (ADR-189),
installs the skills into assistants' skill directories on the criteria of
OpenSpec's installer. On 12 October 2026 the product has no command: its README asks a
reader to copy two directories by hand into one of three documented locations,
check for an existing skill of the same name, and keep per-skill licence and
notice files beside them (design.md, Context). On the line's head,
`machinome skills install` exits 2 with argparse's invalid choice, and the
product's check script validates a licence the set does not carry.

## What Changes

- **The join, by the orchestrator, after the planning commit**: a fresh clone
  of machinome-skills rewritten by `git filter-repo` with the mapping of
  design.md Decision 1 (8 files land under `packages/machinome-skills/`, 7 are
  dropped), its one commit merged with `--allow-unrelated-histories`;
  rehearsed in the scratch directory, where the merge is clean and `git blame`
  reaches the founding commit of 20 September 2026 from the skills' new paths.
- **`machinome-skills` at `packages/machinome-skills/`**, a product that keeps
  its tests and its working record in its directory and its specification in
  the framework's: its manifest at the set's version 0.8.1, requiring
  `machinome~=0.8.1`, under the set's licence, declaring `skills =
  "machinome.skills.cli:Skills"` in `machinome.commands`; the links `LICENSE`
  and `LICENSES`; the package directory `machinome/skills/` with the command,
  the installer, the registry of tools as data (`tools.toml`) and the two
  skills as package data under `machinome/skills/agent-skills/`, each
  `SKILL.md` and its `references/` file unchanged in substance, the `license`
  field of each frontmatter stating the set's expression.
- **The command `machinome skills`** with the verbs `install`, `update` and
  `list` (design.md Decisions 5 to 9): a registry of OpenSpec 1.6.0's 31 tool
  ids with their dot-directories plus `agents` for `.agents/skills/`, each with
  the project directory and the personal directory the tool documents;
  `install --tools all|none|a,b,c [path] [--personal] [--force]` copying each
  skill directory whole with a marker in its frontmatter `metadata`, refusing
  a skill of the same name it did not write unless `--force`, a numbered
  prompt pre-selecting the detected tools when a terminal can answer and
  `agents` when none can, every path written printed; `update [--force]`
  rewriting the copies older than the installed package; `list` printing the
  registry and the copies under a path. It deletes nothing.
- **The tests at their new place**: the product's check script becomes the
  package's format tests (its archive builder dropped), beside the command's
  tests, run from `packages/machinome-skills/` by a step of CI's test job; the
  core's suite does not collect them.
- **The core**: the extra `skills = ["machinome-skills~=0.8.1"]`; the root
  workspace's source and its default `dev` group installing
  `machinome[skills]`; the layout gate's `PRODUCTS` row; the bumpversion
  tables; `scripts/check-dist`'s row, the wheel installed by path and smoked
  by installing into a scratch project and reading the copies back; the
  seam's tests, which assume no contributor is installed, made to read the
  environment's own (design.md probe 6).
- **One licence at the join**: the product's licence file, its notice and the
  per-skill licence and notice files are dropped by the import, and its
  development requirements file with them; the joined commit's message is
  rewritten so it names no licence (Open Questions 7); `NOTICE`'s provenance,
  the adaptation from the studio's skills, goes to `CREDITS.md`.
- **The manual**: a how-to, "Give your assistant the machinome skills"; the
  installation page's row for `machinome[skills]`; the command reference's
  section for `machinome skills`, replacing "are to add theirs" for the
  skills.
- **Records**: `HISTORY.rst`, the manual's changelog, `CREDITS.md`,
  `docs/architecture.md`, the root `README.md`, `CONTRIBUTING.rst`,
  `context7.json`, `AI-USE.md`; the product's `workflow/evaluation.md`
  brought current; ADR-190 (recommended, Open Questions 5).

Not in this change: the unification of `machinome-simulate` with the
workspace's `simulate-project` and anything about the studio's API skill
(deferred by the pilot); the studio's link to `machinome-simulate`; a hint
naming `machinome[skills]` when the package is absent (Open Questions 9); the
workspace follow-ups of design.md Decision 18; any upload, push or version
bump; the other joins.

## Capabilities

### New Capabilities

- `skills-distribution`: what the distribution `machinome-skills` ships (two
  skills in the Agent Skills format, under the set's licence), the registry of
  tools, and the rules of `machinome skills install`, `update` and `list`:
  where a copy is written, its marker, what is refused, what is never
  deleted. The product keeps no specification of its own; this is the
  framework's.

### Modified Capabilities

- `cli`: a requirement for the `skills` command, contributed through the group
  by the installed package and held to the seam's contract by the suite.
- `framework-identity`: the `skills` extra selects the repository's
  distribution at the set's version; the monorepo's products include
  `machinome-skills`, numbered with the set and smoked from its wheel (new
  scenarios, the existing titles kept).
- `user-documentation`: a how-to installs the skills; the installation page
  and the command reference name them.
- `framework-contributor-guidance`: the install without uv names the skills
  directory, and the guide says where its tests run.

`kernel-extras` is unchanged: its requirements list the kernel and node
extras, and none names a product's.

## Impact

- **Tree.** The join adds 8 files. The cycle adds the manifest, `MANIFEST.in`,
  the two licence links, three modules and the registry under
  `machinome/skills/`, the command's test module, the how-to page and ADR-190,
  and the edits of design.md Decisions 2 to 17; it deletes nothing the join
  did not bring.
- **Code.** No module of the core changes. The core's manifest gains one
  extra; the root manifest one source and one dev-group entry.
- **Tests.** Joining: the format tests and the command's tests, run from their
  own directory. Changed in the core's suite: `test_repository_layout.py`,
  `test_machinome_identity.py`, `test_kernel_extras.py`,
  `test_docs_structure.py`, `test_cli_contributed.py`,
  `test_cli_lazy_imports.py` and the helper `contributed_commands.py`.
- **Build and CI.** Fourteen members build from `packages/`; `check-dist`
  gains a row; the test job gains a step; `uv lock` resolves 189 packages.
- **Projects.** None: no project repository imports the skills or runs the
  command, so no universe sweep is owed (design.md Decision 17).

Originating evidence: the pilot's decisions of 12 October 2026, the product's
README and check script (the install it replaces), OpenSpec 1.6.0's installer
read and run in scratch, the clients' documentation read on 12 October 2026,
and the probes recorded in design.md.

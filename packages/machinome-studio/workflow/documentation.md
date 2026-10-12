# Building the studio's pages of the Machinome manual

Since 12 October 2026 (change `join-studio` of the machinome repository)
the studio's manual is part of the Machinome manual, in the repository's
`packages/machinome/docs/`, built with it: three how-to guides,
`howto/open-a-studio-project.rst`, `howto/studio-workspace.rst` and
`howto/studio-agents.rst`, and the reference section `reference/studio/`
(`index.rst`, `command.rst`, `project-configuration.rst`, `profiles.rst`,
`troubleshooting.rst`). The package carries no manual configuration, no
`docs` extra and no Read the Docs configuration of its own.

## Release facts

The facts the pages state about the studio are release facts of the
manual's `docs/conf.py`, written there as literals: `studio_viewer_api`,
`studio_claude_models`, `studio_claude_efforts`, `studio_codex_version`,
`studio_codex_models`, `studio_codex_efforts` and `studio_build_volume`, each
with its substitution (`|studio_viewer_api|` and the others). The manual
reads no file of this package at build time. `tests/test_documentation.py`
holds each literal to the constant of the floor's source it states
(`preparation.py`, `codex_auth.py`, `backends/codex_policy.py`,
`build_package.py`); a change to one of those constants is a change to
`conf.py` in the same commit. The version the pages document is the
manual's `|release|`, the set's.

## Local build

From the repository root:

```sh
make docs
```

or, as the framework's contributor guide says, a venv with
`packages/machinome/docs/requirements.txt` alone and `sphinx -b html -n -W
--keep-going docs docs/_build/html` from `packages/machinome`. The build
imports nothing of the floor and needs no CAD tool or backend.

`tests/test_documentation.py` holds the pages' shape: the pages and their
place in the navigation, the facts, no publication caveat, no project name
or checkout path, every launcher option and configuration key documented,
`machinome studio` and the module forms at `machinome.studio`, no link to a
manual by its URL, and the records kept under `workflow/`. The framework's
`tests/test_docs_structure.py` holds the navigation, the installation
page's `studio` extra and the CLI reference's section `machinome studio`.

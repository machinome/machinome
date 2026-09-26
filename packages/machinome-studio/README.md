# Machinome Studio

Machinome Studio 0.1.0 is a local harness in which a maker builds a
mechanical CAD project with the
[Machinome framework](https://machinome.readthedocs.io/) by talking to
agents in the browser. It opens a project hub over a folder of projects.
Opening a project starts a session of its own: the agents the project's
profile declares, a conversation with the one agent who speaks for the
team, a live view of the model that follows every change to its source,
the project's files, each agent's work as it happens, and the printable
pieces of the last complete build. The agents design, write, test, inspect
and commit inside that project's own Git repository and nowhere else; the
maker remains the authority for the decisions that matter.

The studio runs against Machinome 0.7.0 installed with its `viewer` extra.
The manual is under `docs/`, starting at `docs/index.rst`; where the studio
stands is `docs/project/status.rst`.

## Install

Linux, Python 3.11 or later, Node.js 22 or later with npm, Git, OpenSCAD,
and a logged-in agent backend: Claude Code (`claude`) or OpenCode
(`opencode`). Then:

```text
git clone git@github.com:machinome/machinome-studio.git
cd machinome-studio
scripts/setup
```

The script creates `.venv/`, installs `machinome[viewer]` and
`machinome-viewer[snapshot]` with the Chromium the snapshot renderer needs,
installs the OpenSpec CLI (`@fission-ai/openspec`) when `openspec` is not on
`PATH`, builds the browser surface into `floor/static/`, and installs the
studio editable. It is idempotent.

## Open the hub

```text
source .venv/bin/activate
python -m floor.orchestrator --projects-dir PATH
```

`--projects-dir` is required and names the folder that holds your projects,
exactly as given. The command prints the hub's address and keeps running;
choose or create a project in the browser. `python -m floor` serves the
same hub without agents.

Every project is its own Git repository under that folder. A project
selects its profile and its agents' runtimes in its own `pyproject.toml`,
under `[tool.machinome-studio]`; the manual's reference states the grammar.

## The manual

Build it with the `docs` extra:

```text
.venv/bin/python -m pip install -e '.[docs]'
.venv/bin/python -m sphinx -b html -n -W --keep-going docs docs/_build/html
```

`workflow/documentation.md` records how it is built and checked, and how it
would be hosted.

## Development

```text
.venv/bin/python -m unittest discover -s tests -v
npm --prefix floor/frontend run test
npm --prefix floor/frontend run build
scripts/test-e2e
```

`floor/static/` is generated: rerun the frontend build after changing
`floor/frontend/`. [AGENTS.md](AGENTS.md) is the contract for changing this
repository. The studio is developed from the machinome workspace repository
(<https://github.com/machinome/workspace>), beside the framework and the
other packages of the ecosystem; framework changes and cross-repository
work live there.

## License

Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes.

Machinome Studio is licensed under the GNU Affero General Public License,
version 3 or (at your option) any later version. See [LICENSE](LICENSE).

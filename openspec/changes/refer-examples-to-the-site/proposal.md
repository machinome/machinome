## Why

Read the Docs built the pushed `v0.7.0` tag on 24 September 2026 and stopped
at its 900-second limit (build #34734207): exporting the Metamaquina 2 took
568 s, the Pascaline 146 s, and the Curta never finished; the `latest` build
before it stopped the same way inside the Pascaline export. The manual
exported its three example machines during every documentation build, on
Read the Docs and in the CI docs job, from Foundry submodules, with OpenSCAD,
Node and the mechanics package installed for them. The pilot decided on
25 September 2026: the manual no longer builds or embeds the example
machines, readers are sent to machinome.org, whose Foundry shows the same
machines live, and the documentation build produces nothing.

## What Changes

- The three example pages and their Foundry submodules leave the manual.
  `examples.rst` stays as the one page of its section and sends the reader
  to the Foundry on machinome.org, describing what is there by kind of
  machine and execution model.
- `.readthedocs.yaml` and the CI docs job install `docs/requirements.txt`
  and run Sphinx, nothing else: no export, no apt package, no Node, no
  submodule, no package installed from a repository URL. The requirements
  are Sphinx, its theme and the published `machinome-viewer`, which
  completes the committed tutorial exports with its widget. `conf.py` mocks
  `OCP` beside the other CAD imports so autodoc needs no CAD stack.
- Every page that pointed at an example page points at the site instead;
  the README, the 0.7 changelog bullet, the release note and
  `context7.json` follow.
- `tests/test_docs_exports.py` pins the new rule: every embedded export is
  committed and neither build configuration generates one, installs from a
  repository, needs a system package, Node or a submodule.
  `tests/test_docs_structure.py` pins the examples page's link to the site
  and the absence of example pages and submodules.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: the worked-examples requirement is replaced by the
  examples page that sends readers to machinome.org, and the documentation
  build is required to produce nothing.

## Impact

`.gitmodules`, `docs/examples/*` (removed), `docs/example-*.rst` (removed),
`docs/examples.rst`, `docs/index.rst`, `docs/why.rst`,
`docs/reference/manuals.rst`, `docs/concepts/execution-models.rst`,
`docs/tutorial/10-share.rst`, `docs/project/status.rst`,
`docs/howto/flexible-parts.rst`, `docs/howto/simulate-existing.rst`,
`docs/releases/release-0.7.rst`, `docs/project/changelog.rst`,
`docs/conf.py`, `docs/requirements.txt`, `.readthedocs.yaml`,
`.github/workflows/python-app.yml`, `README.rst`, `context7.json`,
`tests/test_docs_exports.py`, `tests/test_docs_structure.py`.

The 0.7.0 tag moves to the integrated head (the pilot's act; it is pushed
and not on PyPI). The documentation build then depends on `machinome-viewer`
being on PyPI, so the viewer is uploaded before the framework is pushed.
machinome.org's hosted framework manual is rebuilt from the new commit
without supplied inputs.

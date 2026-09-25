## 1. Prove the failure

- [x] 1.1 `tests/test_docs_exports.py`: replace the three-way reconciliation
      with the rule that every directive names a committed export and that
      neither `.readthedocs.yaml` nor the CI docs job exports, installs from a
      repository URL, names an apt package, a Node tool, a `pre_build` job or
      a submodule checkout, and that both install `docs/requirements.txt`.
      Run it red against the current configuration.
- [x] 1.2 `tests/test_docs_structure.py`: the examples page links to the
      Foundry on machinome.org and names the three execution models; no
      `docs/example-*.rst` page and no `.gitmodules` exist. Run it red.

## 2. Remove the builds

- [x] 2.1 Remove the three submodules under `docs/examples/`, `.gitmodules`
      and the three `docs/example-*.rst` pages.
- [x] 2.2 `.readthedocs.yaml`: Python 3.12, `docs/requirements.txt`, Sphinx;
      nothing else. `.github/workflows/python-app.yml` docs job: checkout,
      Python, `pip install -r docs/requirements.txt`, Sphinx with `-W`.
- [x] 2.3 `docs/requirements.txt`: Sphinx, `sphinx_rtd_theme`,
      `machinome-viewer`. `docs/conf.py`: mock `OCP`; drop `examples/**`
      from `exclude_patterns`.

## 3. Point the manual at the site

- [x] 3.1 Rewrite `docs/examples.rst`; update `index`, `why`,
      `reference/manuals`, `concepts/execution-models`, `tutorial/10-share`,
      `project/status`, `howto/flexible-parts`, `howto/simulate-existing`,
      `releases/release-0.7`, `project/changelog`, `README.rst` and
      `context7.json`.

## 4. Build and record

- [x] 4.1 Doc tests green; the manual builds with `-W` in the workspace venv
      and in a fresh venv holding `docs/requirements.txt` alone (viewer wheel
      built from the local tag standing in for PyPI); the built examples and
      tutorial pages read once.
- [x] 4.2 Validate, sync the delta, archive, commit.

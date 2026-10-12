## 1. Red

- [x] 1.1 Add `tests/test_documentation.py` holding the shape of the manual: the pages, the derived release facts, the caveat regex, the project-name and checkout regexes, the launcher options, the sibling-link allowlist, the `docs` extra, the build that imports nothing, the records kept out of `docs/`.
- [x] 1.2 Run it against the current tree and record the failures in `evidence.md`.

## 2. The manual

- [x] 2.1 `docs/conf.py`, `docs/requirements.txt`, `.readthedocs.yaml`, the `docs` extra.
- [x] 2.2 `docs/index.rst`, `installation`, `opening-a-project`, `the-floor`, `working-with-agents`, `troubleshooting`.
- [x] 2.3 `docs/reference/cli`, `project-configuration`, `profiles`; `docs/project/status`.
- [x] 2.4 `README.md` rewritten; `CHANGELOG.md`; the `floor` package docstring.
- [x] 2.5 `workflow/README.md`, `workflow/documentation.md`; move `docs/shop-history.md` and `docs/foreman-listener.md`.

## 3. Green and review

- [x] 3.1 `python -m sphinx -b html -n -W --keep-going docs docs/_build/html` warning-free; read every page in the built HTML as the reader.
- [x] 3.2 Every sibling-manual link opened in the sibling's built HTML.
- [x] 3.3 `tests/test_documentation.py` green; the whole studio suite green.
- [x] 3.4 Record commands and output in `evidence.md`.

## 4. Close

- [x] 4.1 Sync the spec, archive the change, commit the implementation record on the branch; integration is the pilot's.

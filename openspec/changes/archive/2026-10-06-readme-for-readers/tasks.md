## 1. Red first

- [x] 1.1 Add `ReadmeTest` to `tests/test_docs_structure.py`: the seven section titles in order; at most 1500 words; no heading with a digit and no sentence naming a version of Machinome or of its former name; every `.. code-block:: python` block, dedented, a substring of one module under `docs/tutorial/counter/`, and at least one; no block containing `translate(` and one stating a mate with `.on(`. Run the file against the current README and record the red.

## 2. Write

- [x] 2.1 Add `docs/tutorial/counter/readme.py` (design D2) and declare it as the model `readme` in `docs/tutorial/pyproject.toml`; build it beside the chapter's `RatioCounter` and compare the two documents' operations and mesh hashes.
- [x] 2.2 Rewrite `README.rst` in the shape of design D1, the block spliced from the module by a script that reads it (D3), the licence in the exact words of `docs/conf.py`'s `framework_licence`, the viewer's licence before the `viewer` extra, module imports only, no version of Machinome, no former kernel name.
- [x] 2.3 Rewrite `CONTRIBUTING.rst` (design D6).

## 3. Green and checked

- [x] 3.1 Run `tests/test_docs_structure.py`, `tests/test_node_root_exports_nothing.py`, `tests/test_release_records.py`, `tests/test_machinome_identity.py` and `tests/test_docs_exports.py`, then `tests/test_tutorial_counter.py`, which builds the new model, with `-p no:cacheprovider`: green.
- [x] 3.2 Build the distributions into the scratch directory and run `twine check`; render `README.rst` and `CONTRIBUTING.rst` with docutils; check every manual URL and relative link against the tree; read the README once as the reader.
- [x] 3.3 Sync the spec delta into `openspec/specs/user-documentation/spec.md`, record red, green, the document comparison and the checks in `evidence.md`, run `openspec validate readme-for-readers --strict`, archive the change and make the implementation commit.
